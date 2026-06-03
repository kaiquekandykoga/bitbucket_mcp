# frozen_string_literal: true

require_relative "../test_helper"

class ProjectsTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def base
    "/workspaces/ws/projects"
  end

  test "creates a workspace project" do
    stub_call(:post, base)
    client.create_workspace_project(workspace: "ws", key: "PRJ", name: "Project",
                                    description: "d", is_private: true, avatar: { "href" => "http://x" })
    assert_requested(:post, api_url(base), body: {
                       "key" => "PRJ",
                       "name" => "Project",
                       "description" => "d",
                       "is_private" => true,
                       "avatar" => { "href" => "http://x" },
                     })
  end

  test "updates a workspace project" do
    stub_call(:put, "#{base}/PRJ")
    client.update_workspace_project(workspace: "ws", project_key: "PRJ", name: "New", is_private: false)
    assert_requested(:put, api_url("#{base}/PRJ"), body: { "name" => "New", "is_private" => false })
  end

  test "deletes a workspace project" do
    stub_call(:delete, "#{base}/PRJ")
    client.delete_workspace_project(workspace: "ws", project_key: "PRJ")
    assert_requested(:delete, api_url("#{base}/PRJ"))
  end

  test "lists project default reviewers" do
    stub_call(:get, "#{base}/PRJ/default-reviewers")
    client.list_project_default_reviewers(workspace: "ws", project_key: "PRJ", page: 2)
    assert_requested(:get, api_url("#{base}/PRJ/default-reviewers"), query: { "page" => "2" })
  end

  test "gets a project default reviewer" do
    stub_call(:get, "#{base}/PRJ/default-reviewers/u1")
    client.get_project_default_reviewer(workspace: "ws", project_key: "PRJ", selected_user: "u1")
    assert_requested(:get, api_url("#{base}/PRJ/default-reviewers/u1"))
  end

  test "adds a project default reviewer" do
    stub_call(:put, "#{base}/PRJ/default-reviewers/u1")
    client.add_project_default_reviewer(workspace: "ws", project_key: "PRJ", selected_user: "u1")
    assert_requested(:put, api_url("#{base}/PRJ/default-reviewers/u1"))
  end

  test "removes a project default reviewer" do
    stub_call(:delete, "#{base}/PRJ/default-reviewers/u1")
    client.remove_project_default_reviewer(workspace: "ws", project_key: "PRJ", selected_user: "u1")
    assert_requested(:delete, api_url("#{base}/PRJ/default-reviewers/u1"))
  end

  test "lists project group permissions" do
    stub_call(:get, "#{base}/PRJ/permissions-config/groups")
    client.list_project_group_permissions(workspace: "ws", project_key: "PRJ", pagelen: 50)
    assert_requested(:get, api_url("#{base}/PRJ/permissions-config/groups"), query: { "pagelen" => "50" })
  end

  test "gets a project group permission" do
    stub_call(:get, "#{base}/PRJ/permissions-config/groups/devs")
    client.get_project_group_permission(workspace: "ws", project_key: "PRJ", group_slug: "devs")
    assert_requested(:get, api_url("#{base}/PRJ/permissions-config/groups/devs"))
  end

  test "updates a project group permission" do
    stub_call(:put, "#{base}/PRJ/permissions-config/groups/devs")
    client.update_project_group_permission(workspace: "ws", project_key: "PRJ", group_slug: "devs", permission: "write")
    assert_requested(:put, api_url("#{base}/PRJ/permissions-config/groups/devs"), body: { "permission" => "write" })
  end

  test "deletes a project group permission" do
    stub_call(:delete, "#{base}/PRJ/permissions-config/groups/devs")
    client.delete_project_group_permission(workspace: "ws", project_key: "PRJ", group_slug: "devs")
    assert_requested(:delete, api_url("#{base}/PRJ/permissions-config/groups/devs"))
  end

  test "lists project user permissions" do
    stub_call(:get, "#{base}/PRJ/permissions-config/users")
    client.list_project_user_permissions(workspace: "ws", project_key: "PRJ", page: 1)
    assert_requested(:get, api_url("#{base}/PRJ/permissions-config/users"), query: { "page" => "1" })
  end

  test "gets a project user permission" do
    stub_call(:get, "#{base}/PRJ/permissions-config/users/u9")
    client.get_project_user_permission(workspace: "ws", project_key: "PRJ", selected_user_id: "u9")
    assert_requested(:get, api_url("#{base}/PRJ/permissions-config/users/u9"))
  end

  test "updates a project user permission" do
    stub_call(:put, "#{base}/PRJ/permissions-config/users/u9")
    client.update_project_user_permission(workspace: "ws", project_key: "PRJ", selected_user_id: "u9", permission: "admin")
    assert_requested(:put, api_url("#{base}/PRJ/permissions-config/users/u9"), body: { "permission" => "admin" })
  end

  test "deletes a project user permission" do
    stub_call(:delete, "#{base}/PRJ/permissions-config/users/u9")
    client.delete_project_user_permission(workspace: "ws", project_key: "PRJ", selected_user_id: "u9")
    assert_requested(:delete, api_url("#{base}/PRJ/permissions-config/users/u9"))
  end
end
