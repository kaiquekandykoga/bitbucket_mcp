# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::RefsSearch do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists refs with filters" do
    stub_call(:get, "#{repo}/refs")
    client.list_refs(workspace: "ws", repository: "repo", q: "x", sort: "name", page: 2)
    expect(a_request(:get, api_url("#{repo}/refs"))
      .with(query: { "q" => "x", "sort" => "name", "page" => "2" })).to have_been_made
  end

  it "lists branches with filters" do
    stub_call(:get, "#{repo}/refs/branches")
    client.list_branches(workspace: "ws", repository: "repo", q: "main", sort: "-name")
    expect(a_request(:get, api_url("#{repo}/refs/branches"))
      .with(query: { "q" => "main", "sort" => "-name" })).to have_been_made
  end

  it "creates a branch" do
    stub_call(:post, "#{repo}/refs/branches")
    client.create_branch(workspace: "ws", repository: "repo", name: "feature", target_hash: "abc123")
    expect(a_request(:post, api_url("#{repo}/refs/branches"))
      .with(body: { "name" => "feature", "target" => { "hash" => "abc123" } })).to have_been_made
  end

  it "gets a branch by name" do
    stub_call(:get, "#{repo}/refs/branches/main")
    client.get_branch(workspace: "ws", repository: "repo", name: "main")
    expect(a_request(:get, api_url("#{repo}/refs/branches/main"))).to have_been_made
  end

  it "deletes a branch" do
    stub_call(:delete, "#{repo}/refs/branches/old")
    client.delete_branch(workspace: "ws", repository: "repo", name: "old")
    expect(a_request(:delete, api_url("#{repo}/refs/branches/old"))).to have_been_made
  end

  it "lists tags with filters" do
    stub_call(:get, "#{repo}/refs/tags")
    client.list_tags(workspace: "ws", repository: "repo", q: "v1", sort: "name")
    expect(a_request(:get, api_url("#{repo}/refs/tags"))
      .with(query: { "q" => "v1", "sort" => "name" })).to have_been_made
  end

  it "creates a tag with a message" do
    stub_call(:post, "#{repo}/refs/tags")
    client.create_tag(workspace: "ws", repository: "repo", name: "v1.0", target_hash: "abc123", message: "release")
    expect(a_request(:post, api_url("#{repo}/refs/tags")).with(body: {
                                                                 "name" => "v1.0", "target" => { "hash" => "abc123" }, "message" => "release"
                                                               })).to have_been_made
  end

  it "creates a tag without a message" do
    stub_call(:post, "#{repo}/refs/tags")
    client.create_tag(workspace: "ws", repository: "repo", name: "v1.0", target_hash: "abc123")
    expect(a_request(:post, api_url("#{repo}/refs/tags"))
      .with(body: { "name" => "v1.0", "target" => { "hash" => "abc123" } })).to have_been_made
  end

  it "gets a tag by name" do
    stub_call(:get, "#{repo}/refs/tags/v1.0")
    client.get_tag(workspace: "ws", repository: "repo", name: "v1.0")
    expect(a_request(:get, api_url("#{repo}/refs/tags/v1.0"))).to have_been_made
  end

  it "deletes a tag" do
    stub_call(:delete, "#{repo}/refs/tags/v1.0")
    client.delete_tag(workspace: "ws", repository: "repo", name: "v1.0")
    expect(a_request(:delete, api_url("#{repo}/refs/tags/v1.0"))).to have_been_made
  end

  it "searches workspace code" do
    stub_call(:get, "/workspaces/ws/search/code")
    client.search_workspace_code(workspace: "ws", search_query: "foo", page: 2)
    expect(a_request(:get, api_url("/workspaces/ws/search/code"))
      .with(query: { "search_query" => "foo", "page" => "2" })).to have_been_made
  end

  it "searches user code" do
    stub_call(:get, "/users/u1/search/code")
    client.search_user_code(selected_user: "u1", search_query: "bar", pagelen: 50)
    expect(a_request(:get, api_url("/users/u1/search/code"))
      .with(query: { "search_query" => "bar", "pagelen" => "50" })).to have_been_made
  end
end
