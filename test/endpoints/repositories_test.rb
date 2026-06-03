# frozen_string_literal: true

require_relative "../test_helper"

class RepositoriesTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists public repositories" do
    stub_call(:get, "/repositories")
    client.list_public_repositories(role: "member", q: "x", sort: "-updated_on", page: 2)
    assert_requested(:get, api_url("/repositories"), query: { "role" => "member", "q" => "x", "sort" => "-updated_on", "page" => "2" })
  end

  test "lists repositories in a workspace" do
    stub_call(:get, "/repositories/ws")
    client.list_repositories(workspace: "ws", role: "owner", page: 3)
    assert_requested(:get, api_url("/repositories/ws"), query: { "role" => "owner", "page" => "3" })
  end

  test "gets a repository" do
    stub_call(:get, repo)
    client.get_repository(workspace: "ws", repository: "repo")
    assert_requested(:get, api_url(repo))
  end

  test "creates a repository" do
    stub_call(:post, repo)
    client.create_repository(workspace: "ws", repository: "repo", scm: "git", is_private: true,
                             project_key: "MARS", mainbranch_name: "main")
    assert_requested(:post, api_url(repo), body: {
                       "scm" => "git",
                       "is_private" => true,
                       "project" => { "key" => "MARS" },
                       "mainbranch" => { "name" => "main" },
                     })
  end

  test "updates a repository" do
    stub_call(:put, repo)
    client.update_repository(workspace: "ws", repository: "repo", name: "New", has_issues: false, project_key: "MARS")
    assert_requested(:put, api_url(repo), body: {
                       "name" => "New",
                       "has_issues" => false,
                       "project" => { "key" => "MARS" },
                     })
  end

  test "deletes a repository with a redirect" do
    stub_call(:delete, repo)
    client.delete_repository(workspace: "ws", repository: "repo", redirect_to: "https://example.com")
    assert_requested(:delete, api_url(repo), query: { "redirect_to" => "https://example.com" })
  end

  test "lists file history" do
    stub_call(:get, "#{repo}/filehistory/abc/lib/x.rb")
    client.list_file_history(workspace: "ws", repository: "repo", commit: "abc", path: "lib/x.rb", renames: "true")
    assert_requested(:get, api_url("#{repo}/filehistory/abc/lib/x.rb"), query: { "renames" => "true" })
  end

  test "lists repository forks" do
    stub_call(:get, "#{repo}/forks")
    client.list_repository_forks(workspace: "ws", repository: "repo", role: "member")
    assert_requested(:get, api_url("#{repo}/forks"), query: { "role" => "member" })
  end

  test "forks a repository with a body" do
    stub_call(:post, "#{repo}/forks")
    client.fork_repository(workspace: "ws", repository: "repo", name: "fork", destination_workspace: "other", project_key: "P")
    assert_requested(:post, api_url("#{repo}/forks"), body: {
                       "name" => "fork",
                       "workspace" => { "slug" => "other" },
                       "project" => { "key" => "P" },
                     })
  end

  test "forks a repository with no body when no options are given" do
    stub_call(:post, "#{repo}/forks")
    client.fork_repository(workspace: "ws", repository: "repo")
    assert_requested(:post, api_url("#{repo}/forks")) { |req| req.body.to_s.empty? }
  end

  test "lists repository webhooks" do
    stub_call(:get, "#{repo}/hooks")
    client.list_repository_webhooks(workspace: "ws", repository: "repo", page: 2)
    assert_requested(:get, api_url("#{repo}/hooks"), query: { "page" => "2" })
  end

  test "creates a repository webhook" do
    stub_call(:post, "#{repo}/hooks")
    client.create_repository_webhook(workspace: "ws", repository: "repo", url: "https://h", events: ["repo:push"], active: true)
    assert_requested(:post, api_url("#{repo}/hooks"), body: {
                       "url" => "https://h",
                       "events" => ["repo:push"],
                       "active" => true,
                     })
  end

  test "gets, updates and deletes a webhook" do
    stub_call(:get, "#{repo}/hooks/uid1")
    stub_call(:put, "#{repo}/hooks/uid1")
    stub_call(:delete, "#{repo}/hooks/uid1")
    client.get_repository_webhook(workspace: "ws", repository: "repo", uid: "uid1")
    client.update_repository_webhook(workspace: "ws", repository: "repo", uid: "uid1", url: "https://h2", events: ["repo:push"])
    client.delete_repository_webhook(workspace: "ws", repository: "repo", uid: "uid1")
    assert_requested(:get, api_url("#{repo}/hooks/uid1"))
    assert_requested(:put, api_url("#{repo}/hooks/uid1"), body: {
                       "url" => "https://h2", "events" => ["repo:push"]
                     })
    assert_requested(:delete, api_url("#{repo}/hooks/uid1"))
  end

  test "gets and sets override settings" do
    stub_call(:get, "#{repo}/override-settings")
    stub_call(:put, "#{repo}/override-settings")
    client.get_repository_override_settings(workspace: "ws", repository: "repo")
    client.set_repository_override_settings(workspace: "ws", repository: "repo", settings: { "restrict_merges" => true })
    assert_requested(:get, api_url("#{repo}/override-settings"))
    assert_requested(:put, api_url("#{repo}/override-settings"), body: { "restrict_merges" => true })
  end

  test "lists, gets, updates and deletes group permissions" do
    stub_call(:get, "#{repo}/permissions-config/groups")
    stub_call(:get, "#{repo}/permissions-config/groups/devs")
    stub_call(:put, "#{repo}/permissions-config/groups/devs")
    stub_call(:delete, "#{repo}/permissions-config/groups/devs")
    client.list_repository_group_permissions(workspace: "ws", repository: "repo", page: 1)
    client.get_repository_group_permission(workspace: "ws", repository: "repo", group_slug: "devs")
    client.update_repository_group_permission(workspace: "ws", repository: "repo", group_slug: "devs", permission: "write")
    client.delete_repository_group_permission(workspace: "ws", repository: "repo", group_slug: "devs")
    assert_requested(:get, api_url("#{repo}/permissions-config/groups"), query: { "page" => "1" })
    assert_requested(:get, api_url("#{repo}/permissions-config/groups/devs"))
    assert_requested(:put, api_url("#{repo}/permissions-config/groups/devs"), body: { "permission" => "write" })
    assert_requested(:delete, api_url("#{repo}/permissions-config/groups/devs"))
  end

  test "lists, gets, updates and deletes user permissions" do
    stub_call(:get, "#{repo}/permissions-config/users")
    stub_call(:get, "#{repo}/permissions-config/users/u1")
    stub_call(:put, "#{repo}/permissions-config/users/u1")
    stub_call(:delete, "#{repo}/permissions-config/users/u1")
    client.list_repository_user_permissions(workspace: "ws", repository: "repo", pagelen: 50)
    client.get_repository_user_permission(workspace: "ws", repository: "repo", selected_user_id: "u1")
    client.update_repository_user_permission(workspace: "ws", repository: "repo", selected_user_id: "u1", permission: "admin")
    client.delete_repository_user_permission(workspace: "ws", repository: "repo", selected_user_id: "u1")
    assert_requested(:get, api_url("#{repo}/permissions-config/users"), query: { "pagelen" => "50" })
    assert_requested(:get, api_url("#{repo}/permissions-config/users/u1"))
    assert_requested(:put, api_url("#{repo}/permissions-config/users/u1"), body: { "permission" => "admin" })
    assert_requested(:delete, api_url("#{repo}/permissions-config/users/u1"))
  end

  test "gets the repository root src as text" do
    stub_call(:get, "#{repo}/src", body: "ROOT")
    result = client.get_repository_root_src(workspace: "ws", repository: "repo", format: "meta")
    assert_equal("ROOT", result)
    assert_requested(:get, api_url("#{repo}/src"), query: { "format" => "meta" })
  end

  test "creates a src commit via multipart" do
    stub_call(:post, "#{repo}/src")
    client.create_src_commit(workspace: "ws", repository: "repo", message: "msg", branch: "feature",
                             files_to_add: { "lib/x.rb" => "puts 1" }, files_to_delete: ["old.rb"])
    assert_requested(:post, api_url("#{repo}/src"))
  end

  test "gets the repository src at a commit as text" do
    stub_call(:get, "#{repo}/src/abc/lib/x.rb", body: "FILE")
    result = client.get_repository_src(workspace: "ws", repository: "repo", commit: "abc", path: "lib/x.rb", max_depth: 2)
    assert_equal("FILE", result)
    assert_requested(:get, api_url("#{repo}/src/abc/lib/x.rb"), query: { "max_depth" => "2" })
  end

  test "lists repository watchers" do
    stub_call(:get, "#{repo}/watchers")
    client.list_repository_watchers(workspace: "ws", repository: "repo", page: 2)
    assert_requested(:get, api_url("#{repo}/watchers"), query: { "page" => "2" })
  end

  test "lists the caller's repository permissions" do
    stub_call(:get, "/user/permissions/repositories")
    client.list_user_repository_permissions(q: "x", sort: "-updated_on")
    assert_requested(:get, api_url("/user/permissions/repositories"), query: { "q" => "x", "sort" => "-updated_on" })
  end

  test "lists the caller's repository permissions within a workspace" do
    stub_call(:get, "/user/workspaces/ws/permissions/repositories")
    client.list_user_workspace_repository_permissions(workspace: "ws", q: "x")
    assert_requested(:get, api_url("/user/workspaces/ws/permissions/repositories"), query: { "q" => "x" })
  end
end
