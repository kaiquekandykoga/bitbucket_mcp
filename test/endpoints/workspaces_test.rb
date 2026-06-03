# frozen_string_literal: true

require_relative "../test_helper"

class WorkspacesTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  test "lists the caller's workspace permissions" do
    stub_call(:get, "/user/permissions/workspaces")
    client.list_user_workspace_permissions(q: "x", sort: "-name", page: 2)
    assert_requested(:get, api_url("/user/permissions/workspaces"),
                     query: { "q" => "x", "sort" => "-name", "page" => "2" })
  end

  test "lists the caller's workspaces" do
    stub_call(:get, "/user/workspaces")
    client.list_user_workspaces(sort: "slug", administrator: true, page: 2)
    assert_requested(:get, api_url("/user/workspaces"),
                     query: { "sort" => "slug", "administrator" => "true", "page" => "2" })
  end

  test "gets the caller's workspace permission" do
    stub_call(:get, "/user/workspaces/ws/permission")
    client.get_user_workspace_permission(workspace: "ws")
    assert_requested(:get, api_url("/user/workspaces/ws/permission"))
  end

  test "lists workspaces with filters" do
    stub_call(:get, "/workspaces")
    client.list_workspaces(role: "owner", q: "x", sort: "-name")
    assert_requested(:get, api_url("/workspaces"),
                     query: { "role" => "owner", "q" => "x", "sort" => "-name" })
  end

  test "gets a workspace" do
    stub_call(:get, "/workspaces/ws")
    client.get_workspace(workspace: "ws")
    assert_requested(:get, api_url("/workspaces/ws"))
  end

  test "lists workspace webhooks" do
    stub_call(:get, "/workspaces/ws/hooks")
    client.list_workspace_webhooks(workspace: "ws", page: 2)
    assert_requested(:get, api_url("/workspaces/ws/hooks"), query: { "page" => "2" })
  end

  test "creates a workspace webhook" do
    stub_call(:post, "/workspaces/ws/hooks")
    client.create_workspace_webhook(workspace: "ws", url: "https://e", events: ["repo:push"],
                                    description: "d", active: true, secret: "s")
    assert_requested(:post, api_url("/workspaces/ws/hooks"), body: {
                       "url" => "https://e",
                       "events" => ["repo:push"],
                       "description" => "d",
                       "active" => true,
                       "secret" => "s",
                     })
  end

  test "deletes a workspace webhook" do
    stub_call(:delete, "/workspaces/ws/hooks/u1")
    client.delete_workspace_webhook(workspace: "ws", uid: "u1")
    assert_requested(:delete, api_url("/workspaces/ws/hooks/u1"))
  end

  test "gets a workspace webhook" do
    stub_call(:get, "/workspaces/ws/hooks/u1")
    client.get_workspace_webhook(workspace: "ws", uid: "u1")
    assert_requested(:get, api_url("/workspaces/ws/hooks/u1"))
  end

  test "updates a workspace webhook" do
    stub_call(:put, "/workspaces/ws/hooks/u1")
    client.update_workspace_webhook(workspace: "ws", uid: "u1", url: "https://e", events: ["repo:push"], active: false)
    assert_requested(:put, api_url("/workspaces/ws/hooks/u1"), body: {
                       "url" => "https://e",
                       "events" => ["repo:push"],
                       "active" => false,
                     })
  end

  test "lists workspace members" do
    stub_call(:get, "/workspaces/ws/members")
    client.list_workspace_members(workspace: "ws", q: "x")
    assert_requested(:get, api_url("/workspaces/ws/members"), query: { "q" => "x" })
  end

  test "gets a workspace member" do
    stub_call(:get, "/workspaces/ws/members/m1")
    client.get_workspace_member(workspace: "ws", member: "m1")
    assert_requested(:get, api_url("/workspaces/ws/members/m1"))
  end

  test "lists workspace permissions" do
    stub_call(:get, "/workspaces/ws/permissions")
    client.list_workspace_permissions(workspace: "ws", q: "x")
    assert_requested(:get, api_url("/workspaces/ws/permissions"), query: { "q" => "x" })
  end

  test "lists workspace repository permissions" do
    stub_call(:get, "/workspaces/ws/permissions/repositories")
    client.list_workspace_repository_permissions(workspace: "ws", q: "x", sort: "-name")
    assert_requested(:get, api_url("/workspaces/ws/permissions/repositories"),
                     query: { "q" => "x", "sort" => "-name" })
  end

  test "lists workspace repository permissions for a repo" do
    stub_call(:get, "/workspaces/ws/permissions/repositories/repo")
    client.list_workspace_repository_permissions_for_repo(workspace: "ws", repository: "repo", q: "x")
    assert_requested(:get, api_url("/workspaces/ws/permissions/repositories/repo"),
                     query: { "q" => "x" })
  end

  test "lists workspace projects" do
    stub_call(:get, "/workspaces/ws/projects")
    client.list_workspace_projects(workspace: "ws", page: 2)
    assert_requested(:get, api_url("/workspaces/ws/projects"), query: { "page" => "2" })
  end

  test "gets a workspace project" do
    stub_call(:get, "/workspaces/ws/projects/PROJ")
    client.get_workspace_project(workspace: "ws", project_key: "PROJ")
    assert_requested(:get, api_url("/workspaces/ws/projects/PROJ"))
  end

  test "lists workspace user pull requests" do
    stub_call(:get, "/workspaces/ws/pullrequests/u1")
    client.list_workspace_user_pull_requests(workspace: "ws", selected_user: "u1", state: "OPEN")
    assert_requested(:get, api_url("/workspaces/ws/pullrequests/u1"),
                     query: { "state" => "OPEN" })
  end

  test "gets the workspace GPG key" do
    stub_call(:get, "/workspaces/ws/settings/gpg/public-key")
    client.get_workspace_gpg_key(workspace: "ws")
    assert_requested(:get, api_url("/workspaces/ws/settings/gpg/public-key"))
  end
end
