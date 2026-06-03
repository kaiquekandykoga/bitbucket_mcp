# frozen_string_literal: true

require_relative "../test_helper"

class PipelinesVarsTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  def ws
    "/workspaces/ws"
  end

  # ----- Pipelines: variables -----

  test "lists pipeline variables" do
    stub_call(:get, "#{repo}/pipelines_config/variables")
    client.list_pipeline_variables(workspace: "ws", repository: "repo", page: 2, pagelen: 10)
    assert_requested(:get, api_url("#{repo}/pipelines_config/variables"), query: { "page" => "2", "pagelen" => "10" })
  end

  test "creates a pipeline variable" do
    stub_call(:post, "#{repo}/pipelines_config/variables")
    client.create_pipeline_variable(workspace: "ws", repository: "repo", key: "K", value: "V", secured: true)
    assert_requested(:post, api_url("#{repo}/pipelines_config/variables"), body: { "key" => "K", "value" => "V", "secured" => true })
  end

  test "gets a pipeline variable" do
    stub_call(:get, "#{repo}/pipelines_config/variables/v1")
    client.get_pipeline_variable(workspace: "ws", repository: "repo", variable_uuid: "v1")
    assert_requested(:get, api_url("#{repo}/pipelines_config/variables/v1"))
  end

  test "updates a pipeline variable" do
    stub_call(:put, "#{repo}/pipelines_config/variables/v1")
    client.update_pipeline_variable(workspace: "ws", repository: "repo", variable_uuid: "v1", value: "V2")
    assert_requested(:put, api_url("#{repo}/pipelines_config/variables/v1"), body: { "value" => "V2" })
  end

  test "deletes a pipeline variable" do
    stub_call(:delete, "#{repo}/pipelines_config/variables/v1")
    client.delete_pipeline_variable(workspace: "ws", repository: "repo", variable_uuid: "v1")
    assert_requested(:delete, api_url("#{repo}/pipelines_config/variables/v1"))
  end

  # ----- Pipelines: caches -----

  test "lists pipeline caches" do
    stub_call(:get, "#{repo}/pipelines-config/caches")
    client.list_pipeline_caches(workspace: "ws", repository: "repo", page: 1)
    assert_requested(:get, api_url("#{repo}/pipelines-config/caches"), query: { "page" => "1" })
  end

  test "deletes pipeline caches by name" do
    stub_call(:delete, "#{repo}/pipelines-config/caches")
    client.delete_pipeline_caches(workspace: "ws", repository: "repo", name: "build")
    assert_requested(:delete, api_url("#{repo}/pipelines-config/caches"), query: { "name" => "build" })
  end

  test "deletes a single pipeline cache" do
    stub_call(:delete, "#{repo}/pipelines-config/caches/c1")
    client.delete_pipeline_cache(workspace: "ws", repository: "repo", cache_uuid: "c1")
    assert_requested(:delete, api_url("#{repo}/pipelines-config/caches/c1"))
  end

  test "gets the pipeline cache content uri" do
    stub_call(:get, "#{repo}/pipelines-config/caches/c1/content-uri")
    client.get_pipeline_cache_content_uri(workspace: "ws", repository: "repo", cache_uuid: "c1")
    assert_requested(:get, api_url("#{repo}/pipelines-config/caches/c1/content-uri"))
  end

  # ----- Pipelines: repository runners -----

  test "lists repository pipeline runners" do
    stub_call(:get, "#{repo}/pipelines-config/runners")
    client.list_repository_pipeline_runners(workspace: "ws", repository: "repo", pagelen: 5)
    assert_requested(:get, api_url("#{repo}/pipelines-config/runners"), query: { "pagelen" => "5" })
  end

  test "creates a repository pipeline runner" do
    stub_call(:post, "#{repo}/pipelines-config/runners")
    client.create_repository_pipeline_runner(workspace: "ws", repository: "repo", name: "R", labels: ["linux"])
    assert_requested(:post, api_url("#{repo}/pipelines-config/runners"), body: { "name" => "R", "labels" => ["linux"] })
  end

  test "gets a repository pipeline runner" do
    stub_call(:get, "#{repo}/pipelines-config/runners/r1")
    client.get_repository_pipeline_runner(workspace: "ws", repository: "repo", runner_uuid: "r1")
    assert_requested(:get, api_url("#{repo}/pipelines-config/runners/r1"))
  end

  test "updates a repository pipeline runner" do
    stub_call(:put, "#{repo}/pipelines-config/runners/r1")
    client.update_repository_pipeline_runner(workspace: "ws", repository: "repo", runner_uuid: "r1", name: "R2")
    assert_requested(:put, api_url("#{repo}/pipelines-config/runners/r1"), body: { "name" => "R2" })
  end

  test "deletes a repository pipeline runner" do
    stub_call(:delete, "#{repo}/pipelines-config/runners/r1")
    client.delete_repository_pipeline_runner(workspace: "ws", repository: "repo", runner_uuid: "r1")
    assert_requested(:delete, api_url("#{repo}/pipelines-config/runners/r1"))
  end

  # ----- Pipelines: workspace runners -----

  test "lists workspace pipeline runners" do
    stub_call(:get, "#{ws}/pipelines-config/runners")
    client.list_workspace_pipeline_runners(workspace: "ws", page: 3)
    assert_requested(:get, api_url("#{ws}/pipelines-config/runners"), query: { "page" => "3" })
  end

  test "creates a workspace pipeline runner" do
    stub_call(:post, "#{ws}/pipelines-config/runners")
    client.create_workspace_pipeline_runner(workspace: "ws", name: "R", labels: ["self.hosted"])
    assert_requested(:post, api_url("#{ws}/pipelines-config/runners"), body: { "name" => "R", "labels" => ["self.hosted"] })
  end

  test "gets a workspace pipeline runner" do
    stub_call(:get, "#{ws}/pipelines-config/runners/r1")
    client.get_workspace_pipeline_runner(workspace: "ws", runner_uuid: "r1")
    assert_requested(:get, api_url("#{ws}/pipelines-config/runners/r1"))
  end

  test "updates a workspace pipeline runner" do
    stub_call(:put, "#{ws}/pipelines-config/runners/r1")
    client.update_workspace_pipeline_runner(workspace: "ws", runner_uuid: "r1", labels: %w[a b])
    assert_requested(:put, api_url("#{ws}/pipelines-config/runners/r1"), body: { "labels" => %w[a b] })
  end

  test "deletes a workspace pipeline runner" do
    stub_call(:delete, "#{ws}/pipelines-config/runners/r1")
    client.delete_workspace_pipeline_runner(workspace: "ws", runner_uuid: "r1")
    assert_requested(:delete, api_url("#{ws}/pipelines-config/runners/r1"))
  end

  # ----- Pipelines: workspace variables -----

  test "lists workspace pipeline variables" do
    stub_call(:get, "#{ws}/pipelines-config/variables")
    client.list_workspace_pipeline_variables(workspace: "ws", page: 1, pagelen: 20)
    assert_requested(:get, api_url("#{ws}/pipelines-config/variables"), query: { "page" => "1", "pagelen" => "20" })
  end

  test "creates a workspace pipeline variable" do
    stub_call(:post, "#{ws}/pipelines-config/variables")
    client.create_workspace_pipeline_variable(workspace: "ws", key: "K", value: "V")
    assert_requested(:post, api_url("#{ws}/pipelines-config/variables"), body: { "key" => "K", "value" => "V" })
  end

  test "gets a workspace pipeline variable" do
    stub_call(:get, "#{ws}/pipelines-config/variables/v1")
    client.get_workspace_pipeline_variable(workspace: "ws", variable_uuid: "v1")
    assert_requested(:get, api_url("#{ws}/pipelines-config/variables/v1"))
  end

  test "updates a workspace pipeline variable" do
    stub_call(:put, "#{ws}/pipelines-config/variables/v1")
    client.update_workspace_pipeline_variable(workspace: "ws", variable_uuid: "v1", key: "K2", secured: false)
    assert_requested(:put, api_url("#{ws}/pipelines-config/variables/v1"), body: { "key" => "K2", "secured" => false })
  end

  test "deletes a workspace pipeline variable" do
    stub_call(:delete, "#{ws}/pipelines-config/variables/v1")
    client.delete_workspace_pipeline_variable(workspace: "ws", variable_uuid: "v1")
    assert_requested(:delete, api_url("#{ws}/pipelines-config/variables/v1"))
  end

  # ----- Pipelines: user variables -----

  test "lists user pipeline variables" do
    stub_call(:get, "/users/u1/pipelines_config/variables")
    client.list_user_pipeline_variables(selected_user: "u1", page: 2)
    assert_requested(:get, api_url("/users/u1/pipelines_config/variables"), query: { "page" => "2" })
  end

  test "creates a user pipeline variable" do
    stub_call(:post, "/users/u1/pipelines_config/variables")
    client.create_user_pipeline_variable(selected_user: "u1", key: "K", value: "V", secured: true)
    assert_requested(:post, api_url("/users/u1/pipelines_config/variables"), body: { "key" => "K", "value" => "V", "secured" => true })
  end

  test "gets a user pipeline variable" do
    stub_call(:get, "/users/u1/pipelines_config/variables/v1")
    client.get_user_pipeline_variable(selected_user: "u1", variable_uuid: "v1")
    assert_requested(:get, api_url("/users/u1/pipelines_config/variables/v1"))
  end

  test "updates a user pipeline variable" do
    stub_call(:put, "/users/u1/pipelines_config/variables/v1")
    client.update_user_pipeline_variable(selected_user: "u1", variable_uuid: "v1", value: "V2")
    assert_requested(:put, api_url("/users/u1/pipelines_config/variables/v1"), body: { "value" => "V2" })
  end

  test "deletes a user pipeline variable" do
    stub_call(:delete, "/users/u1/pipelines_config/variables/v1")
    client.delete_user_pipeline_variable(selected_user: "u1", variable_uuid: "v1")
    assert_requested(:delete, api_url("/users/u1/pipelines_config/variables/v1"))
  end

  # ----- Pipelines: deployment variables -----

  test "lists deployment variables" do
    stub_call(:get, "#{repo}/deployments_config/environments/e1/variables")
    client.list_deployment_variables(workspace: "ws", repository: "repo", environment_uuid: "e1", page: 1)
    assert_requested(:get, api_url("#{repo}/deployments_config/environments/e1/variables"), query: { "page" => "1" })
  end

  test "creates a deployment variable" do
    stub_call(:post, "#{repo}/deployments_config/environments/e1/variables")
    client.create_deployment_variable(workspace: "ws", repository: "repo", environment_uuid: "e1", key: "K", value: "V", secured: true)
    assert_requested(:post, api_url("#{repo}/deployments_config/environments/e1/variables"), body: { "key" => "K", "value" => "V", "secured" => true })
  end

  test "updates a deployment variable" do
    stub_call(:put, "#{repo}/deployments_config/environments/e1/variables/v1")
    client.update_deployment_variable(workspace: "ws", repository: "repo", environment_uuid: "e1", variable_uuid: "v1", value: "V2")
    assert_requested(:put, api_url("#{repo}/deployments_config/environments/e1/variables/v1"), body: { "value" => "V2" })
  end

  test "deletes a deployment variable" do
    stub_call(:delete, "#{repo}/deployments_config/environments/e1/variables/v1")
    client.delete_deployment_variable(workspace: "ws", repository: "repo", environment_uuid: "e1", variable_uuid: "v1")
    assert_requested(:delete, api_url("#{repo}/deployments_config/environments/e1/variables/v1"))
  end

  # ----- Pipelines: OIDC -----

  test "gets the pipelines OIDC configuration" do
    stub_call(:get, "#{ws}/pipelines-config/identity/oidc/.well-known/openid-configuration")
    client.get_pipelines_oidc_configuration(workspace: "ws")
    assert_requested(:get, api_url("#{ws}/pipelines-config/identity/oidc/.well-known/openid-configuration"))
  end

  test "gets the pipelines OIDC keys" do
    stub_call(:get, "#{ws}/pipelines-config/identity/oidc/keys.json")
    client.get_pipelines_oidc_keys(workspace: "ws")
    assert_requested(:get, api_url("#{ws}/pipelines-config/identity/oidc/keys.json"))
  end
end
