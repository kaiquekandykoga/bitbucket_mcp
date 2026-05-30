# frozen_string_literal: true

require "bitbucket_mcp"
require "webmock/rspec"

WebMock.disable_net_connect!

# Shared helpers for exercising the client and tools against a stubbed API.
module SpecHelpers
  API = BitbucketMcp::Client::BASE_URL

  # Build a client with fixed credentials. Retries default to 0 so endpoint
  # specs assert exactly one request; retry behavior is covered separately.
  def build_client(**opts)
    BitbucketMcp::Client.new(email: "a@b.com", api_token: "tok", max_retries: 0, **opts)
  end

  # Stub a Bitbucket API endpoint at an exact URL. `body` may be a Hash
  # (JSON-encoded) or a String.
  def stub_api(method, path, status: 200, body: {}, headers: {})
    encoded = body.is_a?(String) ? body : JSON.generate(body)
    stub_request(method, "#{API}#{path}").to_return(status: status, body: encoded, headers: headers)
  end

  # Stub a request to `path` (with or without a query string), returning an
  # empty JSON object. Use together with `a_request(...).with(...)` to assert the
  # method, path, query and body a client method produced.
  def stub_call(method, path, status: 200, body: "{}")
    stub_request(method, /\A#{Regexp.escape("#{API}#{path}")}(\?|\z)/).to_return(status: status, body: body)
  end

  # The full URL for a path, for use in `a_request`/`have_requested` assertions.
  def api_url(path)
    "#{API}#{path}"
  end

  # Run the block with the given environment, restoring the original afterwards.
  def with_env(values)
    original = ENV.to_hash
    values.each { |key, value| value.nil? ? ENV.delete(key) : ENV[key] = value }
    yield
  ensure
    ENV.replace(original)
  end
end

RSpec.configure do |config|
  config.include SpecHelpers

  config.expect_with(:rspec) { |c| c.syntax = :expect }
  config.mock_with(:rspec) { |m| m.verify_partial_doubles = true }
  config.disable_monkey_patching!
  config.shared_context_metadata_behavior = :apply_to_host_groups
  config.order = :random
  Kernel.srand(config.seed)
end
