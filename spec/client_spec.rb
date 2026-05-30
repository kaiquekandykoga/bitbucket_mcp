# frozen_string_literal: true

RSpec.describe BitbucketMcp::Client do
  let(:base) { described_class::BASE_URL }

  describe "#initialize" do
    it "uses explicit credentials" do
      client = described_class.new(email: "a@b.com", api_token: "tok")
      expect(client.email).to eq("a@b.com")
      expect(client.api_token).to eq("tok")
    end

    it "falls back to environment variables" do
      with_env("BITBUCKET_EMAIL" => "user@example.com", "BITBUCKET_API_TOKEN" => "secret") do
        client = described_class.new
        expect(client.email).to eq("user@example.com")
        expect(client.api_token).to eq("secret")
      end
    end

    it "lets explicit credentials override the environment" do
      with_env("BITBUCKET_EMAIL" => "env@b.com", "BITBUCKET_API_TOKEN" => "env-tok") do
        client = described_class.new(email: "other@b.com", api_token: "other-tok")
        expect(client.email).to eq("other@b.com")
        expect(client.api_token).to eq("other-tok")
      end
    end

    it "raises when the email is missing" do
      with_env("BITBUCKET_EMAIL" => nil, "BITBUCKET_API_TOKEN" => "tok") do
        expect { described_class.new }.to raise_error(BitbucketMcp::ConfigurationError, /BITBUCKET_EMAIL/)
      end
    end

    it "raises when the API token is missing" do
      with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => nil) do
        expect { described_class.new }.to raise_error(BitbucketMcp::ConfigurationError, /BITBUCKET_API_TOKEN/)
      end
    end

    it "defaults timeout and retries" do
      client = described_class.new(email: "a@b.com", api_token: "tok")
      expect(client.timeout).to eq(30.0)
      expect(client.max_retries).to eq(3)
    end

    it "reads timeout and retries from the environment" do
      with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok",
               "BITBUCKET_TIMEOUT" => "12.5", "BITBUCKET_MAX_RETRIES" => "7") do
        client = described_class.new
        expect(client.timeout).to eq(12.5)
        expect(client.max_retries).to eq(7)
      end
    end

    it "lets explicit tuning override the environment" do
      with_env("BITBUCKET_TIMEOUT" => "12.5", "BITBUCKET_MAX_RETRIES" => "7") do
        client = described_class.new(email: "a@b.com", api_token: "tok", timeout: 1.0, max_retries: 0)
        expect(client.timeout).to eq(1.0)
        expect(client.max_retries).to eq(0)
      end
    end

    it "raises on a non-numeric timeout env var" do
      with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok", "BITBUCKET_TIMEOUT" => "soon") do
        expect { described_class.new }.to raise_error(BitbucketMcp::ConfigurationError, /BITBUCKET_TIMEOUT/)
      end
    end

    it "raises on a non-integer max-retries env var" do
      with_env("BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok", "BITBUCKET_MAX_RETRIES" => "lots") do
        expect { described_class.new }.to raise_error(BitbucketMcp::ConfigurationError, /BITBUCKET_MAX_RETRIES/)
      end
    end

    it "raises on a non-positive timeout" do
      expect { described_class.new(email: "a@b.com", api_token: "tok", timeout: 0) }
        .to raise_error(BitbucketMcp::ConfigurationError, /timeout/)
    end

    it "raises on a negative max-retries" do
      expect { described_class.new(email: "a@b.com", api_token: "tok", max_retries: -1) }
        .to raise_error(BitbucketMcp::ConfigurationError, /max_retries/)
    end
  end

  describe "request decoding" do
    it "parses a JSON object body" do
      stub_api(:get, "/repositories/ws/repo/pullrequests/1", body: { "id" => 1, "title" => "PR" })
      expect(build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1))
        .to eq("id" => 1, "title" => "PR")
    end

    it "returns an empty hash for an empty body" do
      stub_api(:get, "/repositories/ws/repo/pullrequests/1", body: "")
      expect(build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)).to eq({})
    end

    it "returns a raw string for text responses" do
      stub_api(:get, "/repositories/ws/repo/pullrequests/1/diff", body: "diff --git a b")
      expect(build_client.get_pull_request_diff(workspace: "ws", repository: "repo", pull_request_id: 1))
        .to eq("diff --git a b")
    end

    it "wraps invalid JSON in a ResponseError" do
      stub_api(:get, "/repositories/ws/repo/pullrequests/1", body: "not json{")
      expect { build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1) }
        .to raise_error(BitbucketMcp::ResponseError, /invalid JSON/)
    end
  end

  describe "request headers" do
    it "sends Basic auth, Accept and a User-Agent" do
      stub_api(:get, "/repositories/ws/repo/pullrequests/1")
      build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)

      expected_auth = "Basic #{Base64.strict_encode64("a@b.com:tok")}"
      expect(a_request(:get, "#{base}/repositories/ws/repo/pullrequests/1").with(headers: {
                                                                                   "Authorization" => expected_auth,
                                                                                   "Accept" => "application/json",
                                                                                   "User-Agent" => "bitbucket-mcp/#{BitbucketMcp::VERSION}",
                                                                                 })).to have_been_made
    end
  end

  describe "query parameters" do
    it "omits nil parameters and keeps provided ones" do
      stub_request(:get, "#{base}/repositories/ws/repo/pullrequests")
        .with(query: { "state" => "OPEN" }).to_return(status: 200, body: "{}")
      build_client.list_pull_requests(workspace: "ws", repository: "repo", state: "OPEN")
      expect(a_request(:get, "#{base}/repositories/ws/repo/pullrequests").with(query: { "state" => "OPEN" }))
        .to have_been_made
    end

    it "serializes array-valued params as repeated keys (doseq)" do
      target = build_client.send(:build_request_target, "/path", { "include" => %w[a b c], "page" => nil })
      expect(target.split("?", 2).last).to eq("include=a&include=b&include=c")
    end

    it "interpolates brace-wrapped UUID path segments without URI errors" do
      target = build_client.send(:build_request_target, "/repositories/ws/repo/pipelines/{abc-123}", {})
      expect(target).to eq("/2.0/repositories/ws/repo/pipelines/{abc-123}")
    end
  end

  describe "error mapping" do
    it "raises AuthenticationError on HTTP 401 without retrying" do
      stub = stub_api(:get, "/repositories/ws/repo/pullrequests/1", status: 401, body: "nope")
      client = build_client(max_retries: 3)
      allow(client).to receive(:sleep)
      expect { client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1) }
        .to raise_error(BitbucketMcp::AuthenticationError, /401/)
      expect(stub).to have_been_made.once
    end

    it "raises ResponseError with the body on other error statuses" do
      stub_api(:get, "/repositories/ws/repo/pullrequests/1", status: 404, body: "missing")
      expect { build_client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1) }
        .to raise_error(BitbucketMcp::ResponseError, /HTTP 404.*missing/m)
    end
  end

  describe "retries" do
    let(:url) { "#{base}/repositories/ws/repo/pullrequests/1" }

    it "retries idempotent GETs on a 503 and returns the eventual success" do
      stub_request(:get, url).to_return({ status: 503, body: "" }, { status: 200, body: '{"ok":true}' })
      client = build_client(max_retries: 2)
      allow(client).to receive(:sleep)
      expect(client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)).to eq("ok" => true)
      expect(a_request(:get, url)).to have_been_made.twice
    end

    it "does not retry non-idempotent POSTs on a 503" do
      stub = stub_request(:post, "#{base}/repositories/ws/repo/pullrequests").to_return(status: 503, body: "boom")
      client = build_client(max_retries: 3)
      allow(client).to receive(:sleep)
      expect do
        client.create_pull_request(workspace: "ws", repository: "repo", title: "t", source_branch: "f")
      end.to raise_error(BitbucketMcp::ResponseError, /503/)
      expect(stub).to have_been_made.once
    end

    it "retries POSTs on a 429 (rate limited, provably not processed)" do
      stub_request(:post, "#{base}/repositories/ws/repo/pullrequests")
        .to_return({ status: 429, body: "" }, { status: 201, body: '{"id":1}' })
      client = build_client(max_retries: 2)
      allow(client).to receive(:sleep)
      result = client.create_pull_request(workspace: "ws", repository: "repo", title: "t", source_branch: "f")
      expect(result).to eq("id" => 1)
    end

    it "honors a numeric Retry-After header" do
      stub_request(:get, url).to_return(
        { status: 429, headers: { "Retry-After" => "5" }, body: "" },
        { status: 200, body: "{}" },
      )
      client = build_client(max_retries: 1)
      allow(client).to receive(:sleep)
      client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
      expect(client).to have_received(:sleep).with(5.0)
    end

    it "gives up after max_retries and raises" do
      stub_request(:get, url).to_return(status: 500, body: "err")
      client = build_client(max_retries: 2)
      allow(client).to receive(:sleep)
      expect { client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1) }
        .to raise_error(BitbucketMcp::ResponseError, /500/)
      expect(a_request(:get, url)).to have_been_made.times(3)
    end
  end

  describe "network errors" do
    let(:url) { "#{base}/repositories/ws/repo/pullrequests/1" }

    it "retries idempotent requests on a timeout then succeeds" do
      stub_request(:get, url).to_timeout.then.to_return(status: 200, body: "{}")
      client = build_client(max_retries: 1)
      allow(client).to receive(:sleep)
      expect(client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)).to eq({})
    end

    it "raises ResponseError when timeouts exhaust the retries" do
      stub_request(:get, url).to_timeout
      client = build_client(max_retries: 1)
      allow(client).to receive(:sleep)
      expect { client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1) }
        .to raise_error(BitbucketMcp::ResponseError, /request failed/)
      expect(a_request(:get, url)).to have_been_made.twice
    end

    it "does not retry non-idempotent requests on a network error" do
      stub_request(:post, "#{base}/repositories/ws/repo/pullrequests").to_timeout
      client = build_client(max_retries: 3)
      allow(client).to receive(:sleep)
      expect do
        client.create_pull_request(workspace: "ws", repository: "repo", title: "t", source_branch: "f")
      end.to raise_error(BitbucketMcp::ResponseError)
      expect(a_request(:post, "#{base}/repositories/ws/repo/pullrequests")).to have_been_made.once
    end
  end

  describe "private helpers" do
    let(:client) { build_client }

    describe "#retry_delay" do
      it "uses capped exponential backoff without a Retry-After" do
        expect(client.send(:retry_delay, 0, nil)).to eq(1.0)
        expect(client.send(:retry_delay, 1, nil)).to eq(2.0)
        expect(client.send(:retry_delay, 2, nil)).to eq(4.0)
      end

      it "caps the backoff at RETRY_MAX_DELAY" do
        expect(client.send(:retry_delay, 20, nil)).to eq(described_class::RETRY_MAX_DELAY)
      end
    end

    describe "#clean" do
      it "drops nil values and keeps falsey non-nil values" do
        expect(client.send(:clean, { "a" => 1, "b" => nil, "c" => false })).to eq("a" => 1, "c" => false)
      end

      it "treats nil params as an empty hash" do
        expect(client.send(:clean, nil)).to eq({})
      end
    end

    describe "#build_multipart" do
      it "builds a multipart body with form fields and file parts" do
        body, content_type = client.send(:build_multipart, [
                                           ["message", nil, "hello"],
                                           ["file.txt", "file.txt", "contents"],
                                         ])
        expect(content_type).to match(%r{\Amultipart/form-data; boundary=BitbucketBoundary\h+\z})
        boundary = content_type.split("boundary=").last
        expect(body).to include("--#{boundary}\r\n")
        expect(body).to include(%(Content-Disposition: form-data; name="message"\r\n\r\nhello\r\n))
        expect(body).to include(%(Content-Disposition: form-data; name="file.txt"; filename="file.txt"\r\n))
        expect(body).to end_with("--#{boundary}--\r\n")
      end
    end

    describe "#basic_auth_header" do
      it "base64-encodes email:token" do
        expect(client.send(:basic_auth_header)).to eq("Basic #{Base64.strict_encode64("a@b.com:tok")}")
      end
    end
  end
end
