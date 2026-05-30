# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::ReviewersBranching do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists default reviewers" do
    stub_call(:get, "#{repo}/default-reviewers")
    client.list_default_reviewers(workspace: "ws", repository: "repo", page: 2, pagelen: 10)
    expect(a_request(:get, api_url("#{repo}/default-reviewers"))
      .with(query: { "page" => "2", "pagelen" => "10" })).to have_been_made
  end

  it "lists effective default reviewers" do
    stub_call(:get, "#{repo}/effective-default-reviewers")
    client.list_effective_default_reviewers(workspace: "ws", repository: "repo", page: 1)
    expect(a_request(:get, api_url("#{repo}/effective-default-reviewers"))
      .with(query: { "page" => "1" })).to have_been_made
  end

  it "gets a default reviewer" do
    stub_call(:get, "#{repo}/default-reviewers/alice")
    client.get_default_reviewer(workspace: "ws", repository: "repo", target_username: "alice")
    expect(a_request(:get, api_url("#{repo}/default-reviewers/alice"))).to have_been_made
  end

  it "adds a default reviewer" do
    stub_call(:put, "#{repo}/default-reviewers/alice")
    client.add_default_reviewer(workspace: "ws", repository: "repo", target_username: "alice")
    expect(a_request(:put, api_url("#{repo}/default-reviewers/alice"))).to have_been_made
  end

  it "removes a default reviewer" do
    stub_call(:delete, "#{repo}/default-reviewers/alice")
    client.remove_default_reviewer(workspace: "ws", repository: "repo", target_username: "alice")
    expect(a_request(:delete, api_url("#{repo}/default-reviewers/alice"))).to have_been_made
  end

  it "lists branch restrictions with filters" do
    stub_call(:get, "#{repo}/branch-restrictions")
    client.list_branch_restrictions(workspace: "ws", repository: "repo", kind: "push", pattern: "main")
    expect(a_request(:get, api_url("#{repo}/branch-restrictions"))
      .with(query: { "kind" => "push", "pattern" => "main" })).to have_been_made
  end

  it "creates a branch restriction with users and groups" do
    stub_call(:post, "#{repo}/branch-restrictions")
    client.create_branch_restriction(workspace: "ws", repository: "repo", kind: "push",
                                     pattern: "main", branch_match_kind: "glob", branch_type: "release",
                                     users: ["{u1}"], groups: [{ "slug" => "devs" }], value: 2)
    expect(a_request(:post, api_url("#{repo}/branch-restrictions")).with(body: {
                                                                           "kind" => "push",
                                                                           "pattern" => "main",
                                                                           "branch_match_kind" => "glob",
                                                                           "branch_type" => "release",
                                                                           "users" => [{ "uuid" => "{u1}" }],
                                                                           "groups" => [{ "slug" => "devs" }],
                                                                           "value" => 2,
                                                                         })).to have_been_made
  end

  it "creates a branch restriction with only the required kind" do
    stub_call(:post, "#{repo}/branch-restrictions")
    client.create_branch_restriction(workspace: "ws", repository: "repo", kind: "delete")
    expect(a_request(:post, api_url("#{repo}/branch-restrictions"))
      .with(body: { "kind" => "delete" })).to have_been_made
  end

  it "gets a branch restriction" do
    stub_call(:get, "#{repo}/branch-restrictions/7")
    client.get_branch_restriction(workspace: "ws", repository: "repo", id: 7)
    expect(a_request(:get, api_url("#{repo}/branch-restrictions/7"))).to have_been_made
  end

  it "updates a branch restriction" do
    stub_call(:put, "#{repo}/branch-restrictions/7")
    client.update_branch_restriction(workspace: "ws", repository: "repo", id: 7,
                                     kind: "push", pattern: "release/*", branch_match_kind: "glob", branch_type: "release",
                                     users: ["{u2}"], groups: [{ "slug" => "admins" }], value: 3)
    expect(a_request(:put, api_url("#{repo}/branch-restrictions/7")).with(body: {
                                                                            "kind" => "push",
                                                                            "pattern" => "release/*",
                                                                            "branch_match_kind" => "glob",
                                                                            "branch_type" => "release",
                                                                            "users" => [{ "uuid" => "{u2}" }],
                                                                            "groups" => [{ "slug" => "admins" }],
                                                                            "value" => 3,
                                                                          })).to have_been_made
  end

  it "deletes a branch restriction" do
    stub_call(:delete, "#{repo}/branch-restrictions/7")
    client.delete_branch_restriction(workspace: "ws", repository: "repo", id: 7)
    expect(a_request(:delete, api_url("#{repo}/branch-restrictions/7"))).to have_been_made
  end

  it "gets the branching model and effective branching model" do
    stub_call(:get, "#{repo}/branching-model")
    stub_call(:get, "#{repo}/effective-branching-model")
    client.get_branching_model(workspace: "ws", repository: "repo")
    client.get_effective_branching_model(workspace: "ws", repository: "repo")
    expect(a_request(:get, api_url("#{repo}/branching-model"))).to have_been_made
    expect(a_request(:get, api_url("#{repo}/effective-branching-model"))).to have_been_made
  end

  it "gets branching model settings" do
    stub_call(:get, "#{repo}/branching-model/settings")
    client.get_branching_model_settings(workspace: "ws", repository: "repo")
    expect(a_request(:get, api_url("#{repo}/branching-model/settings"))).to have_been_made
  end

  it "updates branching model settings" do
    stub_call(:put, "#{repo}/branching-model/settings")
    client.update_branching_model_settings(workspace: "ws", repository: "repo",
                                           development: { "use_mainbranch" => true }, production: { "enabled" => false },
                                           branch_types: [{ "kind" => "feature", "enabled" => true, "prefix" => "feature/" }])
    expect(a_request(:put, api_url("#{repo}/branching-model/settings")).with(body: {
                                                                               "development" => { "use_mainbranch" => true },
                                                                               "production" => { "enabled" => false },
                                                                               "branch_types" => [{ "kind" => "feature", "enabled" => true, "prefix" => "feature/" }],
                                                                             })).to have_been_made
  end

  it "gets the project branching model and settings" do
    stub_call(:get, "/workspaces/ws/projects/PROJ/branching-model")
    stub_call(:get, "/workspaces/ws/projects/PROJ/branching-model/settings")
    client.get_project_branching_model(workspace: "ws", project_key: "PROJ")
    client.get_project_branching_model_settings(workspace: "ws", project_key: "PROJ")
    expect(a_request(:get, api_url("/workspaces/ws/projects/PROJ/branching-model"))).to have_been_made
    expect(a_request(:get, api_url("/workspaces/ws/projects/PROJ/branching-model/settings"))).to have_been_made
  end

  it "updates project branching model settings" do
    stub_call(:put, "/workspaces/ws/projects/PROJ/branching-model/settings")
    client.update_project_branching_model_settings(workspace: "ws", project_key: "PROJ",
                                                   development: { "name" => "develop" }, production: { "use_mainbranch" => true },
                                                   branch_types: [{ "kind" => "hotfix", "enabled" => true, "prefix" => "hotfix/" }])
    expect(a_request(:put, api_url("/workspaces/ws/projects/PROJ/branching-model/settings")).with(body: {
                                                                                                    "development" => { "name" => "develop" },
                                                                                                    "production" => { "use_mainbranch" => true },
                                                                                                    "branch_types" => [{ "kind" => "hotfix", "enabled" => true, "prefix" => "hotfix/" }],
                                                                                                  })).to have_been_made
  end
end
