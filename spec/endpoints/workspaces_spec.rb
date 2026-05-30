# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::Workspaces do
  let(:client) { build_client }

  it "lists the caller's workspace permissions" do
    stub_call(:get, "/user/permissions/workspaces")
    client.list_user_workspace_permissions(q: "x", sort: "-name", page: 2)
    expect(a_request(:get, api_url("/user/permissions/workspaces"))
      .with(query: { "q" => "x", "sort" => "-name", "page" => "2" })).to have_been_made
  end

  it "lists the caller's workspaces" do
    stub_call(:get, "/user/workspaces")
    client.list_user_workspaces(sort: "slug", administrator: true, page: 2)
    expect(a_request(:get, api_url("/user/workspaces"))
      .with(query: { "sort" => "slug", "administrator" => "true", "page" => "2" })).to have_been_made
  end

  it "gets the caller's workspace permission" do
    stub_call(:get, "/user/workspaces/ws/permission")
    client.get_user_workspace_permission(workspace: "ws")
    expect(a_request(:get, api_url("/user/workspaces/ws/permission"))).to have_been_made
  end

  it "lists workspaces with filters" do
    stub_call(:get, "/workspaces")
    client.list_workspaces(role: "owner", q: "x", sort: "-name")
    expect(a_request(:get, api_url("/workspaces"))
      .with(query: { "role" => "owner", "q" => "x", "sort" => "-name" })).to have_been_made
  end

  it "gets a workspace" do
    stub_call(:get, "/workspaces/ws")
    client.get_workspace(workspace: "ws")
    expect(a_request(:get, api_url("/workspaces/ws"))).to have_been_made
  end

  it "lists workspace webhooks" do
    stub_call(:get, "/workspaces/ws/hooks")
    client.list_workspace_webhooks(workspace: "ws", page: 2)
    expect(a_request(:get, api_url("/workspaces/ws/hooks")).with(query: { "page" => "2" })).to have_been_made
  end

  it "creates a workspace webhook" do
    stub_call(:post, "/workspaces/ws/hooks")
    client.create_workspace_webhook(workspace: "ws", url: "https://e", events: ["repo:push"],
                                    description: "d", active: true, secret: "s")
    expect(a_request(:post, api_url("/workspaces/ws/hooks")).with(body: {
                                                                    "url" => "https://e",
                                                                    "events" => ["repo:push"],
                                                                    "description" => "d",
                                                                    "active" => true,
                                                                    "secret" => "s",
                                                                  })).to have_been_made
  end

  it "deletes a workspace webhook" do
    stub_call(:delete, "/workspaces/ws/hooks/u1")
    client.delete_workspace_webhook(workspace: "ws", uid: "u1")
    expect(a_request(:delete, api_url("/workspaces/ws/hooks/u1"))).to have_been_made
  end

  it "gets a workspace webhook" do
    stub_call(:get, "/workspaces/ws/hooks/u1")
    client.get_workspace_webhook(workspace: "ws", uid: "u1")
    expect(a_request(:get, api_url("/workspaces/ws/hooks/u1"))).to have_been_made
  end

  it "updates a workspace webhook" do
    stub_call(:put, "/workspaces/ws/hooks/u1")
    client.update_workspace_webhook(workspace: "ws", uid: "u1", url: "https://e", events: ["repo:push"], active: false)
    expect(a_request(:put, api_url("/workspaces/ws/hooks/u1")).with(body: {
                                                                      "url" => "https://e",
                                                                      "events" => ["repo:push"],
                                                                      "active" => false,
                                                                    })).to have_been_made
  end

  it "lists workspace members" do
    stub_call(:get, "/workspaces/ws/members")
    client.list_workspace_members(workspace: "ws", q: "x")
    expect(a_request(:get, api_url("/workspaces/ws/members")).with(query: { "q" => "x" })).to have_been_made
  end

  it "gets a workspace member" do
    stub_call(:get, "/workspaces/ws/members/m1")
    client.get_workspace_member(workspace: "ws", member: "m1")
    expect(a_request(:get, api_url("/workspaces/ws/members/m1"))).to have_been_made
  end

  it "lists workspace permissions" do
    stub_call(:get, "/workspaces/ws/permissions")
    client.list_workspace_permissions(workspace: "ws", q: "x")
    expect(a_request(:get, api_url("/workspaces/ws/permissions")).with(query: { "q" => "x" })).to have_been_made
  end

  it "lists workspace repository permissions" do
    stub_call(:get, "/workspaces/ws/permissions/repositories")
    client.list_workspace_repository_permissions(workspace: "ws", q: "x", sort: "-name")
    expect(a_request(:get, api_url("/workspaces/ws/permissions/repositories"))
      .with(query: { "q" => "x", "sort" => "-name" })).to have_been_made
  end

  it "lists workspace repository permissions for a repo" do
    stub_call(:get, "/workspaces/ws/permissions/repositories/repo")
    client.list_workspace_repository_permissions_for_repo(workspace: "ws", repository: "repo", q: "x")
    expect(a_request(:get, api_url("/workspaces/ws/permissions/repositories/repo"))
      .with(query: { "q" => "x" })).to have_been_made
  end

  it "lists workspace projects" do
    stub_call(:get, "/workspaces/ws/projects")
    client.list_workspace_projects(workspace: "ws", page: 2)
    expect(a_request(:get, api_url("/workspaces/ws/projects")).with(query: { "page" => "2" })).to have_been_made
  end

  it "gets a workspace project" do
    stub_call(:get, "/workspaces/ws/projects/PROJ")
    client.get_workspace_project(workspace: "ws", project_key: "PROJ")
    expect(a_request(:get, api_url("/workspaces/ws/projects/PROJ"))).to have_been_made
  end

  it "lists workspace user pull requests" do
    stub_call(:get, "/workspaces/ws/pullrequests/u1")
    client.list_workspace_user_pull_requests(workspace: "ws", selected_user: "u1", state: "OPEN")
    expect(a_request(:get, api_url("/workspaces/ws/pullrequests/u1"))
      .with(query: { "state" => "OPEN" })).to have_been_made
  end

  it "gets the workspace GPG key" do
    stub_call(:get, "/workspaces/ws/settings/gpg/public-key")
    client.get_workspace_gpg_key(workspace: "ws")
    expect(a_request(:get, api_url("/workspaces/ws/settings/gpg/public-key"))).to have_been_made
  end
end
