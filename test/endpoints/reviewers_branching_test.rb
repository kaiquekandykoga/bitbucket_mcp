# frozen_string_literal: true

require_relative "../test_helper"

class ReviewersBranchingTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists default reviewers" do
    stub_call(:get, "#{repo}/default-reviewers")
    client.list_default_reviewers(workspace: "ws", repository: "repo", page: 2, pagelen: 10)
    assert_requested(:get, api_url("#{repo}/default-reviewers"),
                     query: { "page" => "2", "pagelen" => "10" })
  end

  test "lists effective default reviewers" do
    stub_call(:get, "#{repo}/effective-default-reviewers")
    client.list_effective_default_reviewers(workspace: "ws", repository: "repo", page: 1)
    assert_requested(:get, api_url("#{repo}/effective-default-reviewers"),
                     query: { "page" => "1" })
  end

  test "gets a default reviewer" do
    stub_call(:get, "#{repo}/default-reviewers/alice")
    client.get_default_reviewer(workspace: "ws", repository: "repo", target_username: "alice")
    assert_requested(:get, api_url("#{repo}/default-reviewers/alice"))
  end

  test "adds a default reviewer" do
    stub_call(:put, "#{repo}/default-reviewers/alice")
    client.add_default_reviewer(workspace: "ws", repository: "repo", target_username: "alice")
    assert_requested(:put, api_url("#{repo}/default-reviewers/alice"))
  end

  test "removes a default reviewer" do
    stub_call(:delete, "#{repo}/default-reviewers/alice")
    client.remove_default_reviewer(workspace: "ws", repository: "repo", target_username: "alice")
    assert_requested(:delete, api_url("#{repo}/default-reviewers/alice"))
  end

  test "lists branch restrictions with filters" do
    stub_call(:get, "#{repo}/branch-restrictions")
    client.list_branch_restrictions(workspace: "ws", repository: "repo", kind: "push", pattern: "main")
    assert_requested(:get, api_url("#{repo}/branch-restrictions"),
                     query: { "kind" => "push", "pattern" => "main" })
  end

  test "creates a branch restriction with users and groups" do
    stub_call(:post, "#{repo}/branch-restrictions")
    client.create_branch_restriction(workspace: "ws", repository: "repo", kind: "push",
                                     pattern: "main", branch_match_kind: "glob", branch_type: "release",
                                     users: ["{u1}"], groups: [{ "slug" => "devs" }], value: 2)
    assert_requested(:post, api_url("#{repo}/branch-restrictions"), body: {
                       "kind" => "push",
                       "pattern" => "main",
                       "branch_match_kind" => "glob",
                       "branch_type" => "release",
                       "users" => [{ "uuid" => "{u1}" }],
                       "groups" => [{ "slug" => "devs" }],
                       "value" => 2,
                     })
  end

  test "creates a branch restriction with only the required kind" do
    stub_call(:post, "#{repo}/branch-restrictions")
    client.create_branch_restriction(workspace: "ws", repository: "repo", kind: "delete")
    assert_requested(:post, api_url("#{repo}/branch-restrictions"),
                     body: { "kind" => "delete" })
  end

  test "gets a branch restriction" do
    stub_call(:get, "#{repo}/branch-restrictions/7")
    client.get_branch_restriction(workspace: "ws", repository: "repo", id: 7)
    assert_requested(:get, api_url("#{repo}/branch-restrictions/7"))
  end

  test "updates a branch restriction" do
    stub_call(:put, "#{repo}/branch-restrictions/7")
    client.update_branch_restriction(workspace: "ws", repository: "repo", id: 7,
                                     kind: "push", pattern: "release/*", branch_match_kind: "glob", branch_type: "release",
                                     users: ["{u2}"], groups: [{ "slug" => "admins" }], value: 3)
    assert_requested(:put, api_url("#{repo}/branch-restrictions/7"), body: {
                       "kind" => "push",
                       "pattern" => "release/*",
                       "branch_match_kind" => "glob",
                       "branch_type" => "release",
                       "users" => [{ "uuid" => "{u2}" }],
                       "groups" => [{ "slug" => "admins" }],
                       "value" => 3,
                     })
  end

  test "deletes a branch restriction" do
    stub_call(:delete, "#{repo}/branch-restrictions/7")
    client.delete_branch_restriction(workspace: "ws", repository: "repo", id: 7)
    assert_requested(:delete, api_url("#{repo}/branch-restrictions/7"))
  end

  test "gets the branching model and effective branching model" do
    stub_call(:get, "#{repo}/branching-model")
    stub_call(:get, "#{repo}/effective-branching-model")
    client.get_branching_model(workspace: "ws", repository: "repo")
    client.get_effective_branching_model(workspace: "ws", repository: "repo")
    assert_requested(:get, api_url("#{repo}/branching-model"))
    assert_requested(:get, api_url("#{repo}/effective-branching-model"))
  end

  test "gets branching model settings" do
    stub_call(:get, "#{repo}/branching-model/settings")
    client.get_branching_model_settings(workspace: "ws", repository: "repo")
    assert_requested(:get, api_url("#{repo}/branching-model/settings"))
  end

  test "updates branching model settings" do
    stub_call(:put, "#{repo}/branching-model/settings")
    client.update_branching_model_settings(workspace: "ws", repository: "repo",
                                           development: { "use_mainbranch" => true }, production: { "enabled" => false },
                                           branch_types: [{ "kind" => "feature", "enabled" => true, "prefix" => "feature/" }])
    assert_requested(:put, api_url("#{repo}/branching-model/settings"), body: {
                       "development" => { "use_mainbranch" => true },
                       "production" => { "enabled" => false },
                       "branch_types" => [{ "kind" => "feature", "enabled" => true, "prefix" => "feature/" }],
                     })
  end

  test "gets the project branching model and settings" do
    stub_call(:get, "/workspaces/ws/projects/PROJ/branching-model")
    stub_call(:get, "/workspaces/ws/projects/PROJ/branching-model/settings")
    client.get_project_branching_model(workspace: "ws", project_key: "PROJ")
    client.get_project_branching_model_settings(workspace: "ws", project_key: "PROJ")
    assert_requested(:get, api_url("/workspaces/ws/projects/PROJ/branching-model"))
    assert_requested(:get, api_url("/workspaces/ws/projects/PROJ/branching-model/settings"))
  end

  test "updates project branching model settings" do
    stub_call(:put, "/workspaces/ws/projects/PROJ/branching-model/settings")
    client.update_project_branching_model_settings(workspace: "ws", project_key: "PROJ",
                                                   development: { "name" => "develop" }, production: { "use_mainbranch" => true },
                                                   branch_types: [{ "kind" => "hotfix", "enabled" => true, "prefix" => "hotfix/" }])
    assert_requested(:put, api_url("/workspaces/ws/projects/PROJ/branching-model/settings"), body: {
                       "development" => { "name" => "develop" },
                       "production" => { "use_mainbranch" => true },
                       "branch_types" => [{ "kind" => "hotfix", "enabled" => true, "prefix" => "hotfix/" }],
                     })
  end
end
