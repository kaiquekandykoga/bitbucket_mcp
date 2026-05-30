# frozen_string_literal: true

module BitbucketMcp
  # Base class for every error raised by this library.
  class Error < StandardError; end

  # Raised when required configuration (credentials, tuning) is missing or invalid.
  class ConfigurationError < Error; end

  # Raised when Bitbucket rejects the credentials (HTTP 401).
  class AuthenticationError < Error; end

  # Raised when Bitbucket returns an error status or an unexpected response.
  class ResponseError < Error; end
end
