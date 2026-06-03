# frozen_string_literal: true

require_relative "../test_helper"

class RefsSearchTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists refs with filters" do
    stub_call(:get, "#{repo}/refs")
    client.list_refs(workspace: "ws", repository: "repo", q: "x", sort: "name", page: 2)
    assert_requested(:get, api_url("#{repo}/refs"), query: { "q" => "x", "sort" => "name", "page" => "2" })
  end

  test "lists branches with filters" do
    stub_call(:get, "#{repo}/refs/branches")
    client.list_branches(workspace: "ws", repository: "repo", q: "main", sort: "-name")
    assert_requested(:get, api_url("#{repo}/refs/branches"), query: { "q" => "main", "sort" => "-name" })
  end

  test "creates a branch" do
    stub_call(:post, "#{repo}/refs/branches")
    client.create_branch(workspace: "ws", repository: "repo", name: "feature", target_hash: "abc123")
    assert_requested(:post, api_url("#{repo}/refs/branches"), body: { "name" => "feature", "target" => { "hash" => "abc123" } })
  end

  test "gets a branch by name" do
    stub_call(:get, "#{repo}/refs/branches/main")
    client.get_branch(workspace: "ws", repository: "repo", name: "main")
    assert_requested(:get, api_url("#{repo}/refs/branches/main"))
  end

  test "deletes a branch" do
    stub_call(:delete, "#{repo}/refs/branches/old")
    client.delete_branch(workspace: "ws", repository: "repo", name: "old")
    assert_requested(:delete, api_url("#{repo}/refs/branches/old"))
  end

  test "lists tags with filters" do
    stub_call(:get, "#{repo}/refs/tags")
    client.list_tags(workspace: "ws", repository: "repo", q: "v1", sort: "name")
    assert_requested(:get, api_url("#{repo}/refs/tags"), query: { "q" => "v1", "sort" => "name" })
  end

  test "creates a tag with a message" do
    stub_call(:post, "#{repo}/refs/tags")
    client.create_tag(workspace: "ws", repository: "repo", name: "v1.0", target_hash: "abc123", message: "release")
    assert_requested(:post, api_url("#{repo}/refs/tags"), body: {
                       "name" => "v1.0", "target" => { "hash" => "abc123" }, "message" => "release"
                     })
  end

  test "creates a tag without a message" do
    stub_call(:post, "#{repo}/refs/tags")
    client.create_tag(workspace: "ws", repository: "repo", name: "v1.0", target_hash: "abc123")
    assert_requested(:post, api_url("#{repo}/refs/tags"), body: { "name" => "v1.0", "target" => { "hash" => "abc123" } })
  end

  test "gets a tag by name" do
    stub_call(:get, "#{repo}/refs/tags/v1.0")
    client.get_tag(workspace: "ws", repository: "repo", name: "v1.0")
    assert_requested(:get, api_url("#{repo}/refs/tags/v1.0"))
  end

  test "deletes a tag" do
    stub_call(:delete, "#{repo}/refs/tags/v1.0")
    client.delete_tag(workspace: "ws", repository: "repo", name: "v1.0")
    assert_requested(:delete, api_url("#{repo}/refs/tags/v1.0"))
  end

  test "searches workspace code" do
    stub_call(:get, "/workspaces/ws/search/code")
    client.search_workspace_code(workspace: "ws", search_query: "foo", page: 2)
    assert_requested(:get, api_url("/workspaces/ws/search/code"), query: { "search_query" => "foo", "page" => "2" })
  end

  test "searches user code" do
    stub_call(:get, "/users/u1/search/code")
    client.search_user_code(selected_user: "u1", search_query: "bar", pagelen: 50)
    assert_requested(:get, api_url("/users/u1/search/code"), query: { "search_query" => "bar", "pagelen" => "50" })
  end
end
