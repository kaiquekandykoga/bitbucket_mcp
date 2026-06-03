# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::PipelinesVars do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }
  let(:ws) { "/workspaces/ws" }

  # ----- Pipelines: variables -----

  it "lists pipeline variables" do
    stub_call(:get, "#{repo}/pipelines_config/variables")
    client.list_pipeline_variables(workspace: "ws", repository: "repo", page: 2, pagelen: 10)
    expect(a_request(:get, api_url("#{repo}/pipelines_config/variables"))
      .with(query: { "page" => "2", "pagelen" => "10" })).to have_been_made
  end

  it "creates a pipeline variable" do
    stub_call(:post, "#{repo}/pipelines_config/variables")
    client.create_pipeline_variable(workspace: "ws", repository: "repo", key: "K", value: "V", secured: true)
    expect(a_request(:post, api_url("#{repo}/pipelines_config/variables"))
      .with(body: { "key" => "K", "value" => "V", "secured" => true })).to have_been_made
  end

  it "gets a pipeline variable" do
    stub_call(:get, "#{repo}/pipelines_config/variables/v1")
    client.get_pipeline_variable(workspace: "ws", repository: "repo", variable_uuid: "v1")
    expect(a_request(:get, api_url("#{repo}/pipelines_config/variables/v1"))).to have_been_made
  end

  it "updates a pipeline variable" do
    stub_call(:put, "#{repo}/pipelines_config/variables/v1")
    client.update_pipeline_variable(workspace: "ws", repository: "repo", variable_uuid: "v1", value: "V2")
    expect(a_request(:put, api_url("#{repo}/pipelines_config/variables/v1"))
      .with(body: { "value" => "V2" })).to have_been_made
  end

  it "deletes a pipeline variable" do
    stub_call(:delete, "#{repo}/pipelines_config/variables/v1")
    client.delete_pipeline_variable(workspace: "ws", repository: "repo", variable_uuid: "v1")
    expect(a_request(:delete, api_url("#{repo}/pipelines_config/variables/v1"))).to have_been_made
  end

  # ----- Pipelines: caches -----

  it "lists pipeline caches" do
    stub_call(:get, "#{repo}/pipelines-config/caches")
    client.list_pipeline_caches(workspace: "ws", repository: "repo", page: 1)
    expect(a_request(:get, api_url("#{repo}/pipelines-config/caches"))
      .with(query: { "page" => "1" })).to have_been_made
  end

  it "deletes pipeline caches by name" do
    stub_call(:delete, "#{repo}/pipelines-config/caches")
    client.delete_pipeline_caches(workspace: "ws", repository: "repo", name: "build")
    expect(a_request(:delete, api_url("#{repo}/pipelines-config/caches"))
      .with(query: { "name" => "build" })).to have_been_made
  end

  it "deletes a single pipeline cache" do
    stub_call(:delete, "#{repo}/pipelines-config/caches/c1")
    client.delete_pipeline_cache(workspace: "ws", repository: "repo", cache_uuid: "c1")
    expect(a_request(:delete, api_url("#{repo}/pipelines-config/caches/c1"))).to have_been_made
  end

  it "gets the pipeline cache content uri" do
    stub_call(:get, "#{repo}/pipelines-config/caches/c1/content-uri")
    client.get_pipeline_cache_content_uri(workspace: "ws", repository: "repo", cache_uuid: "c1")
    expect(a_request(:get, api_url("#{repo}/pipelines-config/caches/c1/content-uri"))).to have_been_made
  end

  # ----- Pipelines: repository runners -----

  it "lists repository pipeline runners" do
    stub_call(:get, "#{repo}/pipelines-config/runners")
    client.list_repository_pipeline_runners(workspace: "ws", repository: "repo", pagelen: 5)
    expect(a_request(:get, api_url("#{repo}/pipelines-config/runners"))
      .with(query: { "pagelen" => "5" })).to have_been_made
  end

  it "creates a repository pipeline runner" do
    stub_call(:post, "#{repo}/pipelines-config/runners")
    client.create_repository_pipeline_runner(workspace: "ws", repository: "repo", name: "R", labels: ["linux"])
    expect(a_request(:post, api_url("#{repo}/pipelines-config/runners"))
      .with(body: { "name" => "R", "labels" => ["linux"] })).to have_been_made
  end

  it "gets a repository pipeline runner" do
    stub_call(:get, "#{repo}/pipelines-config/runners/r1")
    client.get_repository_pipeline_runner(workspace: "ws", repository: "repo", runner_uuid: "r1")
    expect(a_request(:get, api_url("#{repo}/pipelines-config/runners/r1"))).to have_been_made
  end

  it "updates a repository pipeline runner" do
    stub_call(:put, "#{repo}/pipelines-config/runners/r1")
    client.update_repository_pipeline_runner(workspace: "ws", repository: "repo", runner_uuid: "r1", name: "R2")
    expect(a_request(:put, api_url("#{repo}/pipelines-config/runners/r1"))
      .with(body: { "name" => "R2" })).to have_been_made
  end

  it "deletes a repository pipeline runner" do
    stub_call(:delete, "#{repo}/pipelines-config/runners/r1")
    client.delete_repository_pipeline_runner(workspace: "ws", repository: "repo", runner_uuid: "r1")
    expect(a_request(:delete, api_url("#{repo}/pipelines-config/runners/r1"))).to have_been_made
  end

  # ----- Pipelines: workspace runners -----

  it "lists workspace pipeline runners" do
    stub_call(:get, "#{ws}/pipelines-config/runners")
    client.list_workspace_pipeline_runners(workspace: "ws", page: 3)
    expect(a_request(:get, api_url("#{ws}/pipelines-config/runners"))
      .with(query: { "page" => "3" })).to have_been_made
  end

  it "creates a workspace pipeline runner" do
    stub_call(:post, "#{ws}/pipelines-config/runners")
    client.create_workspace_pipeline_runner(workspace: "ws", name: "R", labels: ["self.hosted"])
    expect(a_request(:post, api_url("#{ws}/pipelines-config/runners"))
      .with(body: { "name" => "R", "labels" => ["self.hosted"] })).to have_been_made
  end

  it "gets a workspace pipeline runner" do
    stub_call(:get, "#{ws}/pipelines-config/runners/r1")
    client.get_workspace_pipeline_runner(workspace: "ws", runner_uuid: "r1")
    expect(a_request(:get, api_url("#{ws}/pipelines-config/runners/r1"))).to have_been_made
  end

  it "updates a workspace pipeline runner" do
    stub_call(:put, "#{ws}/pipelines-config/runners/r1")
    client.update_workspace_pipeline_runner(workspace: "ws", runner_uuid: "r1", labels: %w[a b])
    expect(a_request(:put, api_url("#{ws}/pipelines-config/runners/r1"))
      .with(body: { "labels" => %w[a b] })).to have_been_made
  end

  it "deletes a workspace pipeline runner" do
    stub_call(:delete, "#{ws}/pipelines-config/runners/r1")
    client.delete_workspace_pipeline_runner(workspace: "ws", runner_uuid: "r1")
    expect(a_request(:delete, api_url("#{ws}/pipelines-config/runners/r1"))).to have_been_made
  end

  # ----- Pipelines: workspace variables -----

  it "lists workspace pipeline variables" do
    stub_call(:get, "#{ws}/pipelines-config/variables")
    client.list_workspace_pipeline_variables(workspace: "ws", page: 1, pagelen: 20)
    expect(a_request(:get, api_url("#{ws}/pipelines-config/variables"))
      .with(query: { "page" => "1", "pagelen" => "20" })).to have_been_made
  end

  it "creates a workspace pipeline variable" do
    stub_call(:post, "#{ws}/pipelines-config/variables")
    client.create_workspace_pipeline_variable(workspace: "ws", key: "K", value: "V")
    expect(a_request(:post, api_url("#{ws}/pipelines-config/variables"))
      .with(body: { "key" => "K", "value" => "V" })).to have_been_made
  end

  it "gets a workspace pipeline variable" do
    stub_call(:get, "#{ws}/pipelines-config/variables/v1")
    client.get_workspace_pipeline_variable(workspace: "ws", variable_uuid: "v1")
    expect(a_request(:get, api_url("#{ws}/pipelines-config/variables/v1"))).to have_been_made
  end

  it "updates a workspace pipeline variable" do
    stub_call(:put, "#{ws}/pipelines-config/variables/v1")
    client.update_workspace_pipeline_variable(workspace: "ws", variable_uuid: "v1", key: "K2", secured: false)
    expect(a_request(:put, api_url("#{ws}/pipelines-config/variables/v1"))
      .with(body: { "key" => "K2", "secured" => false })).to have_been_made
  end

  it "deletes a workspace pipeline variable" do
    stub_call(:delete, "#{ws}/pipelines-config/variables/v1")
    client.delete_workspace_pipeline_variable(workspace: "ws", variable_uuid: "v1")
    expect(a_request(:delete, api_url("#{ws}/pipelines-config/variables/v1"))).to have_been_made
  end

  # ----- Pipelines: user variables -----

  it "lists user pipeline variables" do
    stub_call(:get, "/users/u1/pipelines_config/variables")
    client.list_user_pipeline_variables(selected_user: "u1", page: 2)
    expect(a_request(:get, api_url("/users/u1/pipelines_config/variables"))
      .with(query: { "page" => "2" })).to have_been_made
  end

  it "creates a user pipeline variable" do
    stub_call(:post, "/users/u1/pipelines_config/variables")
    client.create_user_pipeline_variable(selected_user: "u1", key: "K", value: "V", secured: true)
    expect(a_request(:post, api_url("/users/u1/pipelines_config/variables"))
      .with(body: { "key" => "K", "value" => "V", "secured" => true })).to have_been_made
  end

  it "gets a user pipeline variable" do
    stub_call(:get, "/users/u1/pipelines_config/variables/v1")
    client.get_user_pipeline_variable(selected_user: "u1", variable_uuid: "v1")
    expect(a_request(:get, api_url("/users/u1/pipelines_config/variables/v1"))).to have_been_made
  end

  it "updates a user pipeline variable" do
    stub_call(:put, "/users/u1/pipelines_config/variables/v1")
    client.update_user_pipeline_variable(selected_user: "u1", variable_uuid: "v1", value: "V2")
    expect(a_request(:put, api_url("/users/u1/pipelines_config/variables/v1"))
      .with(body: { "value" => "V2" })).to have_been_made
  end

  it "deletes a user pipeline variable" do
    stub_call(:delete, "/users/u1/pipelines_config/variables/v1")
    client.delete_user_pipeline_variable(selected_user: "u1", variable_uuid: "v1")
    expect(a_request(:delete, api_url("/users/u1/pipelines_config/variables/v1"))).to have_been_made
  end

  # ----- Pipelines: deployment variables -----

  it "lists deployment variables" do
    stub_call(:get, "#{repo}/deployments_config/environments/e1/variables")
    client.list_deployment_variables(workspace: "ws", repository: "repo", environment_uuid: "e1", page: 1)
    expect(a_request(:get, api_url("#{repo}/deployments_config/environments/e1/variables"))
      .with(query: { "page" => "1" })).to have_been_made
  end

  it "creates a deployment variable" do
    stub_call(:post, "#{repo}/deployments_config/environments/e1/variables")
    client.create_deployment_variable(workspace: "ws", repository: "repo", environment_uuid: "e1", key: "K", value: "V", secured: true)
    expect(a_request(:post, api_url("#{repo}/deployments_config/environments/e1/variables"))
      .with(body: { "key" => "K", "value" => "V", "secured" => true })).to have_been_made
  end

  it "updates a deployment variable" do
    stub_call(:put, "#{repo}/deployments_config/environments/e1/variables/v1")
    client.update_deployment_variable(workspace: "ws", repository: "repo", environment_uuid: "e1", variable_uuid: "v1", value: "V2")
    expect(a_request(:put, api_url("#{repo}/deployments_config/environments/e1/variables/v1"))
      .with(body: { "value" => "V2" })).to have_been_made
  end

  it "deletes a deployment variable" do
    stub_call(:delete, "#{repo}/deployments_config/environments/e1/variables/v1")
    client.delete_deployment_variable(workspace: "ws", repository: "repo", environment_uuid: "e1", variable_uuid: "v1")
    expect(a_request(:delete, api_url("#{repo}/deployments_config/environments/e1/variables/v1"))).to have_been_made
  end

  # ----- Pipelines: OIDC -----

  it "gets the pipelines OIDC configuration" do
    stub_call(:get, "#{ws}/pipelines-config/identity/oidc/.well-known/openid-configuration")
    client.get_pipelines_oidc_configuration(workspace: "ws")
    expect(a_request(:get, api_url("#{ws}/pipelines-config/identity/oidc/.well-known/openid-configuration"))).to have_been_made
  end

  it "gets the pipelines OIDC keys" do
    stub_call(:get, "#{ws}/pipelines-config/identity/oidc/keys.json")
    client.get_pipelines_oidc_keys(workspace: "ws")
    expect(a_request(:get, api_url("#{ws}/pipelines-config/identity/oidc/keys.json"))).to have_been_made
  end
end
