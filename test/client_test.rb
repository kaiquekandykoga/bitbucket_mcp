# frozen_string_literal: true

require_relative "test_helper"

class ClientTest < Test::Unit::TestCase
  include TestHelpers

  def base
    BitbucketMcp::Client::BASE_URL
  end

  def client
    @client ||= build_client
  end

  # ----- #initialize -----

  test "uses explicit credentials" do
    client = BitbucketMcp::Client.new(email: "a@b.com", api_token: "tok")
    assert_equal("a@b.com", client.email)
    assert_equal("tok", client.api_token)
  end

  test "falls back to environment variables" do
    with_env("BITBUCKET_EMAIL" => "user@example.com", "BITBUCKET_API_TOKEN" => "secret") do
      client = BitbucketMcp::Client.new
      assert_equal("user@example.com", client.email)
      assert_equal("secret", client.api_token)
    end
  end

  test "lets explicit credentials override the environment" do
    with_env("BITBUCKET_EMAIL" => "env@b.com", "BITBUCKET_API_TOKEN" => "env-tok") do
      client = BitbucketMcp::Client.new(email: "other@b.com", api_token: "other-tok")
      assert_equal("other@b.com", client.email)
      assert_equal("other-tok", client.api_token)
    end
  end

  test "raises when the email is missing" do
    with_env("BITBUCKET_EMAIL" => nil, "BITBUCKET_API_TOKEN" => "tok") do
      error = assert_raise(BitbucketMcp::ConfigurationError) { BitbucketMcp::Client.new }
      assert_match(/BITBUCKET_EMAIL/, error.message)
    end
  end

  test "raises when the API token is missing" do
    with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => nil) do
      error = assert_raise(BitbucketMcp::ConfigurationError) { BitbucketMcp::Client.new }
      assert_match(/BITBUCKET_API_TOKEN/, error.message)
    end
  end

  test "defaults timeout and retries" do
    client = BitbucketMcp::Client.new(email: "a@b.com", api_token: "tok")
    assert_equal(30.0, client.timeout)
    assert_equal(3, client.max_retries)
  end

  test "reads timeout and retries from the environment" do
    with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok",
             "BITBUCKET_TIMEOUT" => "12.5", "BITBUCKET_MAX_RETRIES" => "7") do
      client = BitbucketMcp::Client.new
      assert_equal(12.5, client.timeout)
      assert_equal(7, client.max_retries)
    end
  end

  test "lets explicit tuning override the environment" do
    with_env("BITBUCKET_TIMEOUT" => "12.5", "BITBUCKET_MAX_RETRIES" => "7") do
      client = BitbucketMcp::Client.new(email: "a@b.com", api_token: "tok", timeout: 1.0, max_retries: 0)
      assert_equal(1.0, client.timeout)
      assert_equal(0, client.max_retries)
    end
  end

  test "raises on a non-numeric timeout env var" do
    with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok", "BITBUCKET_TIMEOUT" => "soon") do
      error = assert_raise(BitbucketMcp::ConfigurationError) { BitbucketMcp::Client.new }
      assert_match(/BITBUCKET_TIMEOUT/, error.message)
    end
  end

  test "raises on a non-integer max-retries env var" do
    with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok", "BITBUCKET_MAX_RETRIES" => "lots") do
      error = assert_raise(BitbucketMcp::ConfigurationError) { BitbucketMcp::Client.new }
      assert_match(/BITBUCKET_MAX_RETRIES/, error.message)
    end
  end

  test "raises on a non-positive timeout" do
    error = assert_raise(BitbucketMcp::ConfigurationError) do
      BitbucketMcp::Client.new(email: "a@b.com", api_token: "tok", timeout: 0)
    end
    assert_match(/timeout/, error.message)
  end

  test "raises on a negative max-retries" do
    error = assert_raise(BitbucketMcp::ConfigurationError) do
      BitbucketMcp::Client.new(email: "a@b.com", api_token: "tok", max_retries: -1)
    end
    assert_match(/max_retries/, error.message)
  end

  # ----- request decoding -----

  test "parses a JSON object body" do
    stub_api(:get, "/repositories/ws/repo/pullrequests/1", body: { "id" => 1, "title" => "PR" })
    assert_equal({ "id" => 1, "title" => "PR" },
                 build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1))
  end

  test "returns an empty hash for an empty body" do
    stub_api(:get, "/repositories/ws/repo/pullrequests/1", body: "")
    assert_equal({}, build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1))
  end

  test "returns a raw string for text responses" do
    stub_api(:get, "/repositories/ws/repo/pullrequests/1/diff", body: "diff --git a b")
    assert_equal("diff --git a b",
                 build_client.get_pull_request_diff(workspace: "ws", repository: "repo", pull_request_id: 1))
  end

  test "wraps invalid JSON in a ResponseError" do
    stub_api(:get, "/repositories/ws/repo/pullrequests/1", body: "not json{")
    error = assert_raise(BitbucketMcp::ResponseError) do
      build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    end
    assert_match(/invalid JSON/, error.message)
  end

  # ----- request headers -----

  test "sends Basic auth, Accept and a User-Agent" do
    stub_api(:get, "/repositories/ws/repo/pullrequests/1")
    build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)

    expected_auth = "Basic #{Base64.strict_encode64("a@b.com:tok")}"
    assert_requested(:get, "#{base}/repositories/ws/repo/pullrequests/1", headers: {
                       "Authorization" => expected_auth,
                       "Accept" => "application/json",
                       "User-Agent" => "bitbucket-mcp/#{BitbucketMcp::VERSION}",
                     })
  end

  # ----- query parameters -----

  test "omits nil parameters and keeps provided ones" do
    stub_request(:get, "#{base}/repositories/ws/repo/pullrequests")
      .with(query: { "state" => "OPEN" }).to_return(status: 200, body: "{}")
    build_client.list_pull_requests(workspace: "ws", repository: "repo", state: "OPEN")
    assert_requested(:get, "#{base}/repositories/ws/repo/pullrequests", query: { "state" => "OPEN" })
  end

  test "serializes array-valued params as repeated keys (doseq)" do
    target = build_client.send(:build_request_target, "/path", { "include" => %w[a b c], "page" => nil })
    assert_equal("include=a&include=b&include=c", target.split("?", 2).last)
  end

  test "interpolates brace-wrapped UUID path segments without URI errors" do
    target = build_client.send(:build_request_target, "/repositories/ws/repo/pipelines/{abc-123}", {})
    assert_equal("/2.0/repositories/ws/repo/pipelines/{abc-123}", target)
  end

  # ----- error mapping -----

  test "raises AuthenticationError on HTTP 401 without retrying" do
    stub = stub_api(:get, "/repositories/ws/repo/pullrequests/1", status: 401, body: "nope")
    client = build_client(max_retries: 3)
    stub_sleep(client)
    error = assert_raise(BitbucketMcp::AuthenticationError) do
      client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    end
    assert_match(/401/, error.message)
    assert_requested(stub, times: 1)
  end

  test "raises ResponseError with the body on other error statuses" do
    stub_api(:get, "/repositories/ws/repo/pullrequests/1", status: 404, body: "missing")
    error = assert_raise(BitbucketMcp::ResponseError) do
      build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    end
    assert_match(/HTTP 404.*missing/m, error.message)
  end

  # ----- retries -----

  test "retries idempotent GETs on a 503 and returns the eventual success" do
    url = "#{base}/repositories/ws/repo/pullrequests/1"
    stub_request(:get, url).to_return({ status: 503, body: "" }, { status: 200, body: '{"ok":true}' })
    client = build_client(max_retries: 2)
    stub_sleep(client)
    assert_equal({ "ok" => true }, client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1))
    assert_requested(:get, url, times: 2)
  end

  test "does not retry non-idempotent POSTs on a 503" do
    stub = stub_request(:post, "#{base}/repositories/ws/repo/pullrequests").to_return(status: 503, body: "boom")
    client = build_client(max_retries: 3)
    stub_sleep(client)
    error = assert_raise(BitbucketMcp::ResponseError) do
      client.create_pull_request(workspace: "ws", repository: "repo", title: "t", source_branch: "f")
    end
    assert_match(/503/, error.message)
    assert_requested(stub, times: 1)
  end

  test "retries POSTs on a 429 (rate limited, provably not processed)" do
    stub_request(:post, "#{base}/repositories/ws/repo/pullrequests")
      .to_return({ status: 429, body: "" }, { status: 201, body: '{"id":1}' })
    client = build_client(max_retries: 2)
    stub_sleep(client)
    result = client.create_pull_request(workspace: "ws", repository: "repo", title: "t", source_branch: "f")
    assert_equal({ "id" => 1 }, result)
  end

  test "honors a numeric Retry-After header" do
    url = "#{base}/repositories/ws/repo/pullrequests/1"
    stub_request(:get, url).to_return(
      { status: 429, headers: { "Retry-After" => "5" }, body: "" },
      { status: 200, body: "{}" },
    )
    client = build_client(max_retries: 1)
    delays = stub_sleep(client)
    client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_equal([5.0], delays)
  end

  test "gives up after max_retries and raises" do
    url = "#{base}/repositories/ws/repo/pullrequests/1"
    stub_request(:get, url).to_return(status: 500, body: "err")
    client = build_client(max_retries: 2)
    stub_sleep(client)
    error = assert_raise(BitbucketMcp::ResponseError) do
      client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    end
    assert_match(/500/, error.message)
    assert_requested(:get, url, times: 3)
  end

  # ----- network errors -----

  test "retries idempotent requests on a timeout then succeeds" do
    url = "#{base}/repositories/ws/repo/pullrequests/1"
    stub_request(:get, url).to_timeout.then.to_return(status: 200, body: "{}")
    client = build_client(max_retries: 1)
    stub_sleep(client)
    assert_equal({}, client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1))
  end

  test "raises ResponseError when timeouts exhaust the retries" do
    url = "#{base}/repositories/ws/repo/pullrequests/1"
    stub_request(:get, url).to_timeout
    client = build_client(max_retries: 1)
    stub_sleep(client)
    error = assert_raise(BitbucketMcp::ResponseError) do
      client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    end
    assert_match(/request failed/, error.message)
    assert_requested(:get, url, times: 2)
  end

  test "does not retry non-idempotent requests on a network error" do
    stub_request(:post, "#{base}/repositories/ws/repo/pullrequests").to_timeout
    client = build_client(max_retries: 3)
    stub_sleep(client)
    assert_raise(BitbucketMcp::ResponseError) do
      client.create_pull_request(workspace: "ws", repository: "repo", title: "t", source_branch: "f")
    end
    assert_requested(:post, "#{base}/repositories/ws/repo/pullrequests", times: 1)
  end

  # ----- private helpers -----

  test "#retry_delay uses capped exponential backoff without a Retry-After" do
    assert_equal(1.0, client.send(:retry_delay, 0, nil))
    assert_equal(2.0, client.send(:retry_delay, 1, nil))
    assert_equal(4.0, client.send(:retry_delay, 2, nil))
  end

  test "#retry_delay caps the backoff at RETRY_MAX_DELAY" do
    assert_equal(BitbucketMcp::Client::RETRY_MAX_DELAY, client.send(:retry_delay, 20, nil))
  end

  test "#clean drops nil values and keeps falsey non-nil values" do
    assert_equal({ "a" => 1, "c" => false }, client.send(:clean, { "a" => 1, "b" => nil, "c" => false }))
  end

  test "#clean treats nil params as an empty hash" do
    assert_equal({}, client.send(:clean, nil))
  end

  test "#build_multipart builds a multipart body with form fields and file parts" do
    body, content_type = client.send(:build_multipart, [
                                       ["message", nil, "hello"],
                                       ["file.txt", "file.txt", "contents"],
                                     ])
    assert_match(%r{\Amultipart/form-data; boundary=BitbucketBoundary\h+\z}, content_type)
    boundary = content_type.split("boundary=").last
    assert_include(body, "--#{boundary}\r\n")
    assert_include(body, %(Content-Disposition: form-data; name="message"\r\n\r\nhello\r\n))
    assert_include(body, %(Content-Disposition: form-data; name="file.txt"; filename="file.txt"\r\n))
    assert(body.end_with?("--#{boundary}--\r\n"), "expected body to end with the closing boundary")
  end

  test "#basic_auth_header base64-encodes email:token" do
    assert_equal("Basic #{Base64.strict_encode64("a@b.com:tok")}", client.send(:basic_auth_header))
  end
end
