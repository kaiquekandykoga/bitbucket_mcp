# frozen_string_literal: true

require_relative "../test_helper"

class StatusesDeployKeysTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists commit statuses with filters" do
    stub_call(:get, "#{repo}/commit/abc/statuses")
    client.list_commit_statuses(workspace: "ws", repository: "repo", commit: "abc", q: "x", sort: "-created_on")
    assert_requested(:get, api_url("#{repo}/commit/abc/statuses"), query: { "q" => "x", "sort" => "-created_on" })
  end

  test "creates a commit build status" do
    stub_call(:post, "#{repo}/commit/abc/statuses/build")
    client.create_commit_build_status(workspace: "ws", repository: "repo", commit: "abc",
                                      key: "ci", state: "SUCCESSFUL", url: "https://ci", name: "CI", description: "d", refname: "main")
    assert_requested(:post, api_url("#{repo}/commit/abc/statuses/build"), body: {
                       "key" => "ci", "state" => "SUCCESSFUL", "url" => "https://ci",
                       "name" => "CI", "description" => "d", "refname" => "main"
                     })
  end

  test "gets a commit build status by key" do
    stub_call(:get, "#{repo}/commit/abc/statuses/build/ci")
    client.get_commit_build_status(workspace: "ws", repository: "repo", commit: "abc", key: "ci")
    assert_requested(:get, api_url("#{repo}/commit/abc/statuses/build/ci"))
  end

  test "updates a commit build status" do
    stub_call(:put, "#{repo}/commit/abc/statuses/build/ci")
    client.update_commit_build_status(workspace: "ws", repository: "repo", commit: "abc", key: "ci",
                                      state: "FAILED", url: "https://ci")
    assert_requested(:put, api_url("#{repo}/commit/abc/statuses/build/ci"), body: { "state" => "FAILED", "url" => "https://ci" })
  end

  test "lists repository deploy keys" do
    stub_call(:get, "#{repo}/deploy-keys")
    client.list_deploy_keys(workspace: "ws", repository: "repo", page: 2)
    assert_requested(:get, api_url("#{repo}/deploy-keys"), query: { "page" => "2" })
  end

  test "creates a repository deploy key" do
    stub_call(:post, "#{repo}/deploy-keys")
    client.create_deploy_key(workspace: "ws", repository: "repo", key: "ssh-rsa AAAA", label: "laptop")
    assert_requested(:post, api_url("#{repo}/deploy-keys"), body: { "key" => "ssh-rsa AAAA", "label" => "laptop" })
  end

  test "gets a repository deploy key" do
    stub_call(:get, "#{repo}/deploy-keys/9")
    client.get_deploy_key(workspace: "ws", repository: "repo", key_id: "9")
    assert_requested(:get, api_url("#{repo}/deploy-keys/9"))
  end

  test "updates a repository deploy key" do
    stub_call(:put, "#{repo}/deploy-keys/9")
    client.update_deploy_key(workspace: "ws", repository: "repo", key_id: "9", label: "renamed")
    assert_requested(:put, api_url("#{repo}/deploy-keys/9"), body: { "label" => "renamed" })
  end

  test "deletes a repository deploy key" do
    stub_call(:delete, "#{repo}/deploy-keys/9")
    client.delete_deploy_key(workspace: "ws", repository: "repo", key_id: "9")
    assert_requested(:delete, api_url("#{repo}/deploy-keys/9"))
  end

  test "lists project deploy keys" do
    stub_call(:get, "/workspaces/ws/projects/PROJ/deploy-keys")
    client.list_project_deploy_keys(workspace: "ws", project_key: "PROJ", pagelen: 50)
    assert_requested(:get, api_url("/workspaces/ws/projects/PROJ/deploy-keys"), query: { "pagelen" => "50" })
  end

  test "creates a project deploy key" do
    stub_call(:post, "/workspaces/ws/projects/PROJ/deploy-keys")
    client.create_project_deploy_key(workspace: "ws", project_key: "PROJ", key: "ssh-rsa AAAA", label: "ci")
    assert_requested(:post, api_url("/workspaces/ws/projects/PROJ/deploy-keys"), body: { "key" => "ssh-rsa AAAA", "label" => "ci" })
  end

  test "gets a project deploy key" do
    stub_call(:get, "/workspaces/ws/projects/PROJ/deploy-keys/9")
    client.get_project_deploy_key(workspace: "ws", project_key: "PROJ", key_id: "9")
    assert_requested(:get, api_url("/workspaces/ws/projects/PROJ/deploy-keys/9"))
  end

  test "deletes a project deploy key" do
    stub_call(:delete, "/workspaces/ws/projects/PROJ/deploy-keys/9")
    client.delete_project_deploy_key(workspace: "ws", project_key: "PROJ", key_id: "9")
    assert_requested(:delete, api_url("/workspaces/ws/projects/PROJ/deploy-keys/9"))
  end
end
