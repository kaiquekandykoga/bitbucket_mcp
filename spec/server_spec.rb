# frozen_string_literal: true

RSpec.describe BitbucketMcp::Server do
  # Credentials for tool dispatch; retries off so error cases don't sleep.
  let(:creds) do
    { "BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok", "BITBUCKET_MAX_RETRIES" => "0" }
  end

  def find_tool(name)
    BitbucketMcp::Tools.all.find { |tool| tool.name_value == name } or raise "tool #{name} not registered"
  end

  describe ".build" do
    it "builds an MCP server named bitbucket_mcp with every tool" do
      server = described_class.build
      expect(server).to be_a(MCP::Server)
      expect(server.name).to eq("bitbucket_mcp")
      expect(server.version).to eq(BitbucketMcp::VERSION)
      expect(server.tools.size).to eq(BitbucketMcp::Tools.all.size)
    end
  end

  describe "tool registry" do
    let(:tools) { BitbucketMcp::Tools.all }

    it "registers at least the pull request tools" do
      expect(tools.size).to be >= 30
    end

    it "gives every tool a unique name" do
      names = tools.map(&:name_value)
      expect(names.uniq.length).to eq(names.length)
    end

    it "maps every tool to a client method of the same name" do
      client = build_client
      tools.each do |tool|
        expect(client).to respond_to(tool.name_value)
      end
    end

    it "produces a valid JSON Schema for every tool" do
      tools.each do |tool|
        schema = tool.input_schema.to_h
        expect(schema[:type]).to eq("object")
        expect(schema).to have_key(:properties)
      end
    end

    it "marks read-only tools and destructive tools with annotations" do
      expect(find_tool("get_pull_request").annotations_value.read_only_hint).to be(true)
      expect(find_tool("delete_pull_request_comment").annotations_value.destructive_hint).to be(true)
    end

    it "declares object/array types for structured params so valid input is not rejected" do
      settings = find_tool("set_repository_override_settings").input_schema.to_h.dig(:properties, :settings)
      expect(settings[:type]).to eq("object")
      expect(settings).not_to have_key(:additionalProperties)

      groups = find_tool("create_branch_restriction").input_schema.to_h.dig(:properties, :groups)
      expect(groups[:type]).to eq("array")
      expect(groups).not_to have_key(:items)
    end

    it "accepts object- and array-valued arguments during schema validation" do
      tool = find_tool("set_repository_override_settings")
      expect do
        tool.input_schema.validate_arguments("workspace" => "ws", "repository" => "repo", "settings" => { "enabled" => true })
      end.not_to raise_error
    end
  end

  describe "tool dispatch" do
    it "forwards arguments to the client and returns JSON text" do
      with_env(creds) do
        stub_call(:get, "/repositories/ws/repo/pullrequests/1", body: '{"id":1,"title":"PR"}')
        response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1)
        expect(response).to be_a(MCP::Tool::Response)
        expect(response.error?).to be(false)
        expect(JSON.parse(response.content.first[:text])).to eq("id" => 1, "title" => "PR")
      end
    end

    it "passes text responses through without JSON-encoding" do
      with_env(creds) do
        stub_call(:get, "/repositories/ws/repo/pullrequests/1/diff", body: "RAW DIFF")
        response = find_tool("get_pull_request_diff").call(workspace: "ws", repository: "repo", pull_request_id: 1)
        expect(response.content.first[:text]).to eq("RAW DIFF")
      end
    end

    it "ignores an injected server_context argument" do
      with_env(creds) do
        stub_call(:get, "/repositories/ws/repo/pullrequests/1", body: "{}")
        response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1, server_context: :ignored)
        expect(response.error?).to be(false)
      end
    end

    it "turns Bitbucket failures into a tool error response" do
      with_env(creds) do
        stub_call(:get, "/repositories/ws/repo/pullrequests/1", status: 500, body: "boom")
        response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1)
        expect(response.error?).to be(true)
        expect(response.content.first[:text]).to match(/500/)
      end
    end

    it "turns missing credentials into a tool error response" do
      with_env("BITBUCKET_EMAIL" => nil, "BITBUCKET_API_TOKEN" => nil) do
        response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1)
        expect(response.error?).to be(true)
        expect(response.content.first[:text]).to match(/BITBUCKET_EMAIL/)
      end
    end
  end

  describe "end-to-end through the MCP server" do
    it "answers a tools/call JSON-RPC request" do
      with_env(creds) do
        stub_call(:get, "/repositories/ws/repo/pullrequests/1", body: '{"id":1}')
        server = described_class.build
        request = {
          jsonrpc: "2.0", id: 1, method: "tools/call",
          params: { name: "get_pull_request", arguments: { workspace: "ws", repository: "repo", pull_request_id: 1 } }
        }
        response = JSON.parse(server.handle_json(JSON.generate(request)))
        expect(response.dig("result", "isError")).to be(false)
        text = response.dig("result", "content", 0, "text")
        expect(JSON.parse(text)).to eq("id" => 1)
      end
    end

    it "lists tools over JSON-RPC" do
      server = described_class.build
      request = { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }
      response = JSON.parse(server.handle_json(JSON.generate(request)))
      names = response.dig("result", "tools").map { |t| t["name"] }
      expect(names).to include("get_pull_request", "create_pull_request")
    end
  end

  describe ".run CLI" do
    it "prints the version" do
      expect { described_class.run(["--version"]) }.to output("#{BitbucketMcp::VERSION}\n").to_stdout
    end

    it "prints usage help" do
      expect { described_class.run(["--help"]) }.to output(/MCP server for the Bitbucket Cloud REST API/).to_stdout
    end
  end
end
