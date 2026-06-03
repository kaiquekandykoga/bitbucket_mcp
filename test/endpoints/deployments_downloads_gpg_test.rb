# frozen_string_literal: true

require_relative "../test_helper"

class DeploymentsDownloadsGpgTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists deployments" do
    stub_call(:get, "#{repo}/deployments")
    client.list_deployments(workspace: "ws", repository: "repo", page: 2)
    assert_requested(:get, api_url("#{repo}/deployments"), query: { "page" => "2" })
  end

  test "gets a deployment" do
    stub_call(:get, "#{repo}/deployments/d-1")
    client.get_deployment(workspace: "ws", repository: "repo", deployment_uuid: "d-1")
    assert_requested(:get, api_url("#{repo}/deployments/d-1"))
  end

  test "lists environments" do
    stub_call(:get, "#{repo}/environments")
    client.list_environments(workspace: "ws", repository: "repo", pagelen: 10)
    assert_requested(:get, api_url("#{repo}/environments"), query: { "pagelen" => "10" })
  end

  test "creates an environment" do
    stub_call(:post, "#{repo}/environments")
    client.create_environment(workspace: "ws", repository: "repo", name: "Prod",
                              environment_type: { "name" => "Production" }, rank: 1)
    assert_requested(:post, api_url("#{repo}/environments"), body: {
                       "name" => "Prod",
                       "environment_type" => { "name" => "Production" },
                       "rank" => 1,
                     })
  end

  test "gets an environment" do
    stub_call(:get, "#{repo}/environments/e-1")
    client.get_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1")
    assert_requested(:get, api_url("#{repo}/environments/e-1"))
  end

  test "updates an environment with a body" do
    stub_call(:post, "#{repo}/environments/e-1/changes")
    client.update_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1",
                              body: { "change" => { "restrictions" => {} } })
    assert_requested(:post, api_url("#{repo}/environments/e-1/changes"), body: { "change" => { "restrictions" => {} } })
  end

  test "updates an environment with an empty body when none is given" do
    stub_call(:post, "#{repo}/environments/e-1/changes")
    client.update_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1")
    assert_requested(:post, api_url("#{repo}/environments/e-1/changes"), body: {})
  end

  test "deletes an environment" do
    stub_call(:delete, "#{repo}/environments/e-1")
    client.delete_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1")
    assert_requested(:delete, api_url("#{repo}/environments/e-1"))
  end

  test "lists downloads" do
    stub_call(:get, "#{repo}/downloads")
    client.list_downloads(workspace: "ws", repository: "repo", page: 1)
    assert_requested(:get, api_url("#{repo}/downloads"), query: { "page" => "1" })
  end

  test "uploads downloads as multipart" do
    stub_call(:post, "#{repo}/downloads")
    client.upload_download(workspace: "ws", repository: "repo", files: { "notes.txt" => "hello" })
    assert_requested(:post, api_url("#{repo}/downloads")) do |req|
      req.headers["Content-Type"].to_s.start_with?("multipart/form-data") &&
        req.body.include?('name="files"; filename="notes.txt"') &&
        req.body.include?("hello")
    end
  end

  test "gets a download as text" do
    stub_call(:get, "#{repo}/downloads/notes.txt", body: "CONTENTS")
    assert_equal("CONTENTS", client.get_download(workspace: "ws", repository: "repo", filename: "notes.txt"))
  end

  test "deletes a download" do
    stub_call(:delete, "#{repo}/downloads/notes.txt")
    client.delete_download(workspace: "ws", repository: "repo", filename: "notes.txt")
    assert_requested(:delete, api_url("#{repo}/downloads/notes.txt"))
  end

  test "lists user gpg keys" do
    stub_call(:get, "/users/u-1/gpg-keys")
    client.list_user_gpg_keys(selected_user: "u-1", page: 3)
    assert_requested(:get, api_url("/users/u-1/gpg-keys"), query: { "page" => "3" })
  end

  test "creates a user gpg key" do
    stub_call(:post, "/users/u-1/gpg-keys")
    client.create_user_gpg_key(selected_user: "u-1", key: "ABC", name: "laptop")
    assert_requested(:post, api_url("/users/u-1/gpg-keys"), body: { "key" => "ABC", "name" => "laptop" })
  end

  test "gets a user gpg key" do
    stub_call(:get, "/users/u-1/gpg-keys/fp-9")
    client.get_user_gpg_key(selected_user: "u-1", fingerprint: "fp-9")
    assert_requested(:get, api_url("/users/u-1/gpg-keys/fp-9"))
  end

  test "deletes a user gpg key" do
    stub_call(:delete, "/users/u-1/gpg-keys/fp-9")
    client.delete_user_gpg_key(selected_user: "u-1", fingerprint: "fp-9")
    assert_requested(:delete, api_url("/users/u-1/gpg-keys/fp-9"))
  end
end
