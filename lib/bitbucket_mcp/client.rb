# frozen_string_literal: true

require "net/http"
require "uri"
require "json"
require "base64"
require "securerandom"

require_relative "version"
require_relative "errors"

# Endpoint groups. Each file defines a module under BitbucketMcp::Endpoints
# holding the methods for one Bitbucket Cloud API area; Client mixes them all in.
Dir[File.join(__dir__, "endpoints", "*.rb")].sort.each { |file| require file }

module BitbucketMcp
  # A thin, dependency-free client for the Bitbucket Cloud REST API (v2.0).
  #
  # Credentials come from the +BITBUCKET_EMAIL+ / +BITBUCKET_API_TOKEN+
  # environment variables (or constructor arguments). Networking is tunable via
  # +BITBUCKET_TIMEOUT+ and +BITBUCKET_MAX_RETRIES+.
  class Client
    BASE_URL = "https://api.bitbucket.org/2.0"
    BASE_URI = URI.parse(BASE_URL).freeze

    # Networking defaults. Override via the BITBUCKET_TIMEOUT / BITBUCKET_MAX_RETRIES
    # environment variables, or the constructor.
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_MAX_RETRIES = 3
    RETRY_BACKOFF_BASE = 1.0
    RETRY_MAX_DELAY = 60.0
    RETRYABLE_STATUS = [429, 500, 502, 503, 504].freeze
    IDEMPOTENT_METHODS = %w[GET HEAD OPTIONS PUT DELETE].freeze
    USER_AGENT = "bitbucket-mcp/#{VERSION}".freeze

    # Network-level failures worth retrying for idempotent requests.
    NETWORK_ERRORS = [
      Timeout::Error, Net::OpenTimeout, Net::ReadTimeout, EOFError, IOError,
      SocketError, Errno::ECONNREFUSED, Errno::ECONNRESET, Errno::EHOSTUNREACH,
      Errno::ENETUNREACH, Errno::ETIMEDOUT, Errno::EPIPE, OpenSSL::SSL::SSLError
    ].freeze

    REQUEST_CLASSES = {
      "GET" => Net::HTTP::Get,
      "POST" => Net::HTTP::Post,
      "PUT" => Net::HTTP::Put,
      "DELETE" => Net::HTTP::Delete,
    }.freeze

    # Mix in every endpoint group (PullRequests, Repositories, Pipelines, ...).
    Endpoints.constants.sort.each { |name| include Endpoints.const_get(name) }

    def initialize(email: nil, api_token: nil, timeout: nil, max_retries: nil)
      email ||= ENV["BITBUCKET_EMAIL"]
      api_token ||= ENV["BITBUCKET_API_TOKEN"]

      raise ConfigurationError, "BITBUCKET_EMAIL is not set" if email.nil? || email.empty?
      raise ConfigurationError, "BITBUCKET_API_TOKEN is not set" if api_token.nil? || api_token.empty?

      @email = email
      @api_token = api_token
      @timeout = timeout || env_float("BITBUCKET_TIMEOUT", DEFAULT_TIMEOUT)
      @max_retries = max_retries || env_int("BITBUCKET_MAX_RETRIES", DEFAULT_MAX_RETRIES)

      raise ConfigurationError, "timeout must be greater than 0" if @timeout <= 0
      raise ConfigurationError, "max_retries must be 0 or greater" if @max_retries.negative?
    end

    attr_reader :email, :api_token, :timeout, :max_retries

    private

    # Perform a request against the Bitbucket API, with retries, and decode the
    # response. Returns a parsed Hash/Array for JSON, a String when
    # +text_response+ is true, or +{}+ for an empty JSON body.
    def request(method, path, body: nil, body_bytes: nil, body_content_type: nil, params: nil, text_response: false)
      target = build_request_target(path, params)
      net_request = build_net_request(method, target, body, body_bytes, body_content_type)

      attempt = 0
      loop do
        response = network_error = nil
        begin
          response = perform(net_request)
        rescue *NETWORK_ERRORS => e
          network_error = e
        end

        if network_error
          if attempt < @max_retries && idempotent?(method)
            sleep(retry_delay(attempt, nil))
            attempt += 1
            next
          end
          raise ResponseError, "Bitbucket API request failed: #{network_error.message}"
        end

        status = response.code.to_i
        if status == 401
          raise AuthenticationError,
                "Authentication failed (HTTP 401). Check BITBUCKET_EMAIL and BITBUCKET_API_TOKEN."
        end
        return decode(response, text_response) if status.between?(200, 299)

        if attempt < @max_retries && retry_status?(method, status)
          sleep(retry_delay(attempt, response))
          attempt += 1
          next
        end
        raise ResponseError, "Bitbucket API error (HTTP #{status}): #{response.body}"
      end
    end

    # Build the request target (path + query) as a string. Path segments are
    # interpolated verbatim - Bitbucket resource ids are sometimes brace-wrapped
    # UUIDs (e.g. "{uuid}"), which URI.parse would reject, so the path is never
    # round-tripped through URI parsing.
    def build_request_target(path, params)
      target = "#{BASE_URI.path}#{path}"
      cleaned = clean(params)
      target << "?#{URI.encode_www_form(cleaned)}" unless cleaned.empty?
      target
    end

    def build_net_request(method, target, body, body_bytes, body_content_type)
      klass = REQUEST_CLASSES.fetch(method) { raise ArgumentError, "Unsupported method: #{method}" }
      net_request = klass.new(target)
      net_request["Authorization"] = basic_auth_header
      net_request["Accept"] = "application/json"
      net_request["User-Agent"] = USER_AGENT
      if !body.nil?
        net_request["Content-Type"] = "application/json"
        net_request.body = JSON.generate(body)
      elsif !body_bytes.nil?
        net_request["Content-Type"] = body_content_type unless body_content_type.nil?
        net_request.body = body_bytes
      end
      net_request
    end

    def perform(net_request)
      http = Net::HTTP.new(BASE_URI.host, BASE_URI.port)
      http.use_ssl = BASE_URI.scheme == "https"
      http.open_timeout = @timeout
      http.read_timeout = @timeout
      http.write_timeout = @timeout if http.respond_to?(:write_timeout=)
      http.start { |connection| connection.request(net_request) }
    end

    def decode(response, text_response)
      raw = response.body
      return (raw || "").dup.force_encoding(Encoding::UTF_8).scrub if text_response
      return {} if raw.nil? || raw.empty?

      JSON.parse(raw)
    rescue JSON::ParserError => e
      raise ResponseError, "Bitbucket API returned invalid JSON: #{e.message}"
    end

    def basic_auth_header
      "Basic #{Base64.strict_encode64("#{@email}:#{@api_token}")}"
    end

    # Whether a request that failed with +status+ should be retried. Reads (and
    # other idempotent methods) retry on any retryable status; non-idempotent
    # writes only retry on HTTP 429, where the request was rate-limited and
    # provably not processed, so a retry cannot duplicate the side effect.
    def retry_status?(method, status)
      return false unless RETRYABLE_STATUS.include?(status)
      return true if status == 429

      idempotent?(method)
    end

    def idempotent?(method)
      IDEMPOTENT_METHODS.include?(method)
    end

    # Seconds to wait before the next attempt (0-indexed). Honors a numeric
    # Retry-After header, otherwise uses capped exponential backoff.
    def retry_delay(attempt, response)
      retry_after = parse_retry_after(response)
      return [retry_after, RETRY_MAX_DELAY].min unless retry_after.nil?

      [RETRY_MAX_DELAY, RETRY_BACKOFF_BASE * (2**attempt)].min
    end

    def parse_retry_after(response)
      return nil if response.nil?

      value = response["Retry-After"]
      return nil if value.nil?

      value = value.strip
      value.match?(/\A\d+\z/) ? value.to_f : nil
    end

    # Build a multipart/form-data body from +[name, filename, content]+ tuples.
    # A nil filename marks a plain form field; otherwise it is a file part.
    def build_multipart(fields)
      boundary = "BitbucketBoundary#{SecureRandom.hex(16)}"
      body = +"".b
      fields.each do |name, filename, content|
        body << "--#{boundary}\r\n"
        if filename.nil?
          body << %(Content-Disposition: form-data; name="#{name}"\r\n\r\n)
        else
          body << %(Content-Disposition: form-data; name="#{name}"; filename="#{filename}"\r\n)
          body << "Content-Type: application/octet-stream\r\n\r\n"
        end
        body << content.to_s.dup.b
        body << "\r\n"
      end
      body << "--#{boundary}--\r\n"
      [body, "multipart/form-data; boundary=#{boundary}"]
    end

    # Drop keys whose value is nil, mirroring the Python client's parameter handling.
    def clean(params)
      return {} if params.nil?

      params.compact
    end

    def env_float(name, default)
      raw = ENV[name]
      return default if raw.nil? || raw.empty?

      Float(raw)
    rescue ArgumentError
      raise ConfigurationError, "#{name} must be a number, got #{raw.inspect}"
    end

    def env_int(name, default)
      raw = ENV[name]
      return default if raw.nil? || raw.empty?

      Integer(raw, 10)
    rescue ArgumentError
      raise ConfigurationError, "#{name} must be an integer, got #{raw.inspect}"
    end
  end
end
