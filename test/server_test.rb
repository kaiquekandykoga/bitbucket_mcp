# frozen_string_literal: true

require_relative "test_helper"

class ServerTest < Test::Unit::TestCase
  include TestHelpers

  # Credentials for tool dispatch; retries off so error cases don't sleep.
  def creds
    { "BITBUCKET_EMAIL" => "a@b.com", "BITBUCKET_API_TOKEN" => "tok", "BITBUCKET_MAX_RETRIES" => "0" }
  end

  def find_tool(name)
    BitbucketMcp::Tools.all.find { |tool| tool.name_value == name } or raise "tool #{name} not registered"
  end

  def tools
    BitbucketMcp::Tools.all
  end

  # ----- .build -----

  test ".build builds an MCP server named bitbucket_mcp with every tool" do
    server = BitbucketMcp::Server.build
    assert_kind_of(MCP::Server, server)
    assert_equal("bitbucket_mcp", server.name)
    assert_equal(BitbucketMcp::VERSION, server.version)
    assert_equal(BitbucketMcp::Tools.all.size, server.tools.size)
  end

  # ----- tool registry -----

  test "registers at least the pull request tools" do
    assert_operator(tools.size, :>=, 30)
  end

  test "gives every tool a unique name" do
    names = tools.map(&:name_value)
    assert_equal(names.length, names.uniq.length)
  end

  test "maps every tool to a client method of the same name" do
    client = build_client
    tools.each do |tool|
      assert_respond_to(client, tool.name_value)
    end
  end

  test "produces a valid JSON Schema for every tool" do
    tools.each do |tool|
      schema = tool.input_schema.to_h
      assert_equal("object", schema[:type])
      assert(schema.key?(:properties), "expected schema to declare :properties")
    end
  end

  test "marks read-only tools and destructive tools with annotations" do
    assert_true(find_tool("get_pull_request").annotations_value.read_only_hint)
    assert_true(find_tool("delete_pull_request_comment").annotations_value.destructive_hint)
  end

  test "declares object/array types for structured params so valid input is not rejected" do
    settings = find_tool("set_repository_override_settings").input_schema.to_h.dig(:properties, :settings)
    assert_equal("object", settings[:type])
    assert_false(settings.key?(:additionalProperties))

    groups = find_tool("create_branch_restriction").input_schema.to_h.dig(:properties, :groups)
    assert_equal("array", groups[:type])
    assert_false(groups.key?(:items))
  end

  test "accepts object- and array-valued arguments during schema validation" do
    tool = find_tool("set_repository_override_settings")
    assert_nothing_raised do
      tool.input_schema.validate_arguments("workspace" => "ws", "repository" => "repo", "settings" => { "enabled" => true })
    end
  end

  # ----- tool dispatch -----

  test "forwards arguments to the client and returns JSON text" do
    with_env(creds) do
      stub_call(:get, "/repositories/ws/repo/pullrequests/1", body: '{"id":1,"title":"PR"}')
      response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1)
      assert_kind_of(MCP::Tool::Response, response)
      assert_false(response.error?)
      assert_equal({ "id" => 1, "title" => "PR" }, JSON.parse(response.content.first[:text]))
    end
  end

  test "passes text responses through without JSON-encoding" do
    with_env(creds) do
      stub_call(:get, "/repositories/ws/repo/pullrequests/1/diff", body: "RAW DIFF")
      response = find_tool("get_pull_request_diff").call(workspace: "ws", repository: "repo", pull_request_id: 1)
      assert_equal("RAW DIFF", response.content.first[:text])
    end
  end

  test "ignores an injected server_context argument" do
    with_env(creds) do
      stub_call(:get, "/repositories/ws/repo/pullrequests/1", body: "{}")
      response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1,
                                                    server_context: :ignored)
      assert_false(response.error?)
    end
  end

  test "turns Bitbucket failures into a tool error response" do
    with_env(creds) do
      stub_call(:get, "/repositories/ws/repo/pullrequests/1", status: 500, body: "boom")
      response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1)
      assert_true(response.error?)
      assert_match(/500/, response.content.first[:text])
    end
  end

  test "turns missing credentials into a tool error response" do
    with_env("BITBUCKET_EMAIL" => nil, "BITBUCKET_API_TOKEN" => nil) do
      response = find_tool("get_pull_request").call(workspace: "ws", repository: "repo", pull_request_id: 1)
      assert_true(response.error?)
      assert_match(/BITBUCKET_EMAIL/, response.content.first[:text])
    end
  end

  # ----- end-to-end through the MCP server -----

  test "answers a tools/call JSON-RPC request" do
    with_env(creds) do
      stub_call(:get, "/repositories/ws/repo/pullrequests/1", body: '{"id":1}')
      server = BitbucketMcp::Server.build
      request = {
        jsonrpc: "2.0", id: 1, method: "tools/call",
        params: { name: "get_pull_request", arguments: { workspace: "ws", repository: "repo", pull_request_id: 1 } }
      }
      response = JSON.parse(server.handle_json(JSON.generate(request)))
      assert_false(response.dig("result", "isError"))
      text = response.dig("result", "content", 0, "text")
      assert_equal({ "id" => 1 }, JSON.parse(text))
    end
  end

  test "lists tools over JSON-RPC" do
    server = BitbucketMcp::Server.build
    request = { jsonrpc: "2.0", id: 2, method: "tools/list", params: {} }
    response = JSON.parse(server.handle_json(JSON.generate(request)))
    names = response.dig("result", "tools").map { |t| t["name"] }
    assert_include(names, "get_pull_request")
    assert_include(names, "create_pull_request")
  end

  # ----- .run CLI -----

  test ".run prints the version" do
    assert_equal("#{BitbucketMcp::VERSION}\n", capture_stdout { BitbucketMcp::Server.run(["--version"]) })
  end

  test ".run prints usage help" do
    assert_match(/MCP server for the Bitbucket Cloud REST API/, capture_stdout { BitbucketMcp::Server.run(["--help"]) })
  end
end
