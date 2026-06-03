# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::Repositories do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists public repositories" do
    stub_call(:get, "/repositories")
    client.list_public_repositories(role: "member", q: "x", sort: "-updated_on", page: 2)
    expect(a_request(:get, api_url("/repositories"))
      .with(query: { "role" => "member", "q" => "x", "sort" => "-updated_on", "page" => "2" })).to have_been_made
  end

  it "lists repositories in a workspace" do
    stub_call(:get, "/repositories/ws")
    client.list_repositories(workspace: "ws", role: "owner", page: 3)
    expect(a_request(:get, api_url("/repositories/ws"))
      .with(query: { "role" => "owner", "page" => "3" })).to have_been_made
  end

  it "gets a repository" do
    stub_call(:get, repo)
    client.get_repository(workspace: "ws", repository: "repo")
    expect(a_request(:get, api_url(repo))).to have_been_made
  end

  it "creates a repository" do
    stub_call(:post, repo)
    client.create_repository(workspace: "ws", repository: "repo", scm: "git", is_private: true,
                             project_key: "MARS", mainbranch_name: "main")
    expect(a_request(:post, api_url(repo)).with(body: {
                                                  "scm" => "git",
                                                  "is_private" => true,
                                                  "project" => { "key" => "MARS" },
                                                  "mainbranch" => { "name" => "main" },
                                                })).to have_been_made
  end

  it "updates a repository" do
    stub_call(:put, repo)
    client.update_repository(workspace: "ws", repository: "repo", name: "New", has_issues: false, project_key: "MARS")
    expect(a_request(:put, api_url(repo)).with(body: {
                                                 "name" => "New",
                                                 "has_issues" => false,
                                                 "project" => { "key" => "MARS" },
                                               })).to have_been_made
  end

  it "deletes a repository with a redirect" do
    stub_call(:delete, repo)
    client.delete_repository(workspace: "ws", repository: "repo", redirect_to: "https://example.com")
    expect(a_request(:delete, api_url(repo)).with(query: { "redirect_to" => "https://example.com" })).to have_been_made
  end

  it "lists file history" do
    stub_call(:get, "#{repo}/filehistory/abc/lib/x.rb")
    client.list_file_history(workspace: "ws", repository: "repo", commit: "abc", path: "lib/x.rb", renames: "true")
    expect(a_request(:get, api_url("#{repo}/filehistory/abc/lib/x.rb"))
      .with(query: { "renames" => "true" })).to have_been_made
  end

  it "lists repository forks" do
    stub_call(:get, "#{repo}/forks")
    client.list_repository_forks(workspace: "ws", repository: "repo", role: "member")
    expect(a_request(:get, api_url("#{repo}/forks")).with(query: { "role" => "member" })).to have_been_made
  end

  it "forks a repository with a body" do
    stub_call(:post, "#{repo}/forks")
    client.fork_repository(workspace: "ws", repository: "repo", name: "fork", destination_workspace: "other", project_key: "P")
    expect(a_request(:post, api_url("#{repo}/forks")).with(body: {
                                                             "name" => "fork",
                                                             "workspace" => { "slug" => "other" },
                                                             "project" => { "key" => "P" },
                                                           })).to have_been_made
  end

  it "forks a repository with no body when no options are given" do
    stub_call(:post, "#{repo}/forks")
    client.fork_repository(workspace: "ws", repository: "repo")
    expect(a_request(:post, api_url("#{repo}/forks")).with { |req| req.body.to_s.empty? }).to have_been_made
  end

  it "lists repository webhooks" do
    stub_call(:get, "#{repo}/hooks")
    client.list_repository_webhooks(workspace: "ws", repository: "repo", page: 2)
    expect(a_request(:get, api_url("#{repo}/hooks")).with(query: { "page" => "2" })).to have_been_made
  end

  it "creates a repository webhook" do
    stub_call(:post, "#{repo}/hooks")
    client.create_repository_webhook(workspace: "ws", repository: "repo", url: "https://h", events: ["repo:push"], active: true)
    expect(a_request(:post, api_url("#{repo}/hooks")).with(body: {
                                                             "url" => "https://h",
                                                             "events" => ["repo:push"],
                                                             "active" => true,
                                                           })).to have_been_made
  end

  it "gets, updates and deletes a webhook" do
    stub_call(:get, "#{repo}/hooks/uid1")
    stub_call(:put, "#{repo}/hooks/uid1")
    stub_call(:delete, "#{repo}/hooks/uid1")
    client.get_repository_webhook(workspace: "ws", repository: "repo", uid: "uid1")
    client.update_repository_webhook(workspace: "ws", repository: "repo", uid: "uid1", url: "https://h2", events: ["repo:push"])
    client.delete_repository_webhook(workspace: "ws", repository: "repo", uid: "uid1")
    expect(a_request(:get, api_url("#{repo}/hooks/uid1"))).to have_been_made
    expect(a_request(:put, api_url("#{repo}/hooks/uid1")).with(body: {
                                                                 "url" => "https://h2", "events" => ["repo:push"]
                                                               })).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/hooks/uid1"))).to have_been_made
  end

  it "gets and sets override settings" do
    stub_call(:get, "#{repo}/override-settings")
    stub_call(:put, "#{repo}/override-settings")
    client.get_repository_override_settings(workspace: "ws", repository: "repo")
    client.set_repository_override_settings(workspace: "ws", repository: "repo", settings: { "restrict_merges" => true })
    expect(a_request(:get, api_url("#{repo}/override-settings"))).to have_been_made
    expect(a_request(:put, api_url("#{repo}/override-settings"))
      .with(body: { "restrict_merges" => true })).to have_been_made
  end

  it "lists, gets, updates and deletes group permissions" do
    stub_call(:get, "#{repo}/permissions-config/groups")
    stub_call(:get, "#{repo}/permissions-config/groups/devs")
    stub_call(:put, "#{repo}/permissions-config/groups/devs")
    stub_call(:delete, "#{repo}/permissions-config/groups/devs")
    client.list_repository_group_permissions(workspace: "ws", repository: "repo", page: 1)
    client.get_repository_group_permission(workspace: "ws", repository: "repo", group_slug: "devs")
    client.update_repository_group_permission(workspace: "ws", repository: "repo", group_slug: "devs", permission: "write")
    client.delete_repository_group_permission(workspace: "ws", repository: "repo", group_slug: "devs")
    expect(a_request(:get, api_url("#{repo}/permissions-config/groups")).with(query: { "page" => "1" })).to have_been_made
    expect(a_request(:get, api_url("#{repo}/permissions-config/groups/devs"))).to have_been_made
    expect(a_request(:put, api_url("#{repo}/permissions-config/groups/devs"))
      .with(body: { "permission" => "write" })).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/permissions-config/groups/devs"))).to have_been_made
  end

  it "lists, gets, updates and deletes user permissions" do
    stub_call(:get, "#{repo}/permissions-config/users")
    stub_call(:get, "#{repo}/permissions-config/users/u1")
    stub_call(:put, "#{repo}/permissions-config/users/u1")
    stub_call(:delete, "#{repo}/permissions-config/users/u1")
    client.list_repository_user_permissions(workspace: "ws", repository: "repo", pagelen: 50)
    client.get_repository_user_permission(workspace: "ws", repository: "repo", selected_user_id: "u1")
    client.update_repository_user_permission(workspace: "ws", repository: "repo", selected_user_id: "u1", permission: "admin")
    client.delete_repository_user_permission(workspace: "ws", repository: "repo", selected_user_id: "u1")
    expect(a_request(:get, api_url("#{repo}/permissions-config/users")).with(query: { "pagelen" => "50" })).to have_been_made
    expect(a_request(:get, api_url("#{repo}/permissions-config/users/u1"))).to have_been_made
    expect(a_request(:put, api_url("#{repo}/permissions-config/users/u1"))
      .with(body: { "permission" => "admin" })).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/permissions-config/users/u1"))).to have_been_made
  end

  it "gets the repository root src as text" do
    stub_call(:get, "#{repo}/src", body: "ROOT")
    result = client.get_repository_root_src(workspace: "ws", repository: "repo", format: "meta")
    expect(result).to eq("ROOT")
    expect(a_request(:get, api_url("#{repo}/src")).with(query: { "format" => "meta" })).to have_been_made
  end

  it "creates a src commit via multipart" do
    stub_call(:post, "#{repo}/src")
    client.create_src_commit(workspace: "ws", repository: "repo", message: "msg", branch: "feature",
                             files_to_add: { "lib/x.rb" => "puts 1" }, files_to_delete: ["old.rb"])
    expect(a_request(:post, api_url("#{repo}/src"))).to have_been_made
  end

  it "gets the repository src at a commit as text" do
    stub_call(:get, "#{repo}/src/abc/lib/x.rb", body: "FILE")
    result = client.get_repository_src(workspace: "ws", repository: "repo", commit: "abc", path: "lib/x.rb", max_depth: 2)
    expect(result).to eq("FILE")
    expect(a_request(:get, api_url("#{repo}/src/abc/lib/x.rb")).with(query: { "max_depth" => "2" })).to have_been_made
  end

  it "lists repository watchers" do
    stub_call(:get, "#{repo}/watchers")
    client.list_repository_watchers(workspace: "ws", repository: "repo", page: 2)
    expect(a_request(:get, api_url("#{repo}/watchers")).with(query: { "page" => "2" })).to have_been_made
  end

  it "lists the caller's repository permissions" do
    stub_call(:get, "/user/permissions/repositories")
    client.list_user_repository_permissions(q: "x", sort: "-updated_on")
    expect(a_request(:get, api_url("/user/permissions/repositories"))
      .with(query: { "q" => "x", "sort" => "-updated_on" })).to have_been_made
  end

  it "lists the caller's repository permissions within a workspace" do
    stub_call(:get, "/user/workspaces/ws/permissions/repositories")
    client.list_user_workspace_repository_permissions(workspace: "ws", q: "x")
    expect(a_request(:get, api_url("/user/workspaces/ws/permissions/repositories"))
      .with(query: { "q" => "x" })).to have_been_made
  end
end
