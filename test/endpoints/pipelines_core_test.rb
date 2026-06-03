# frozen_string_literal: true

require_relative "../test_helper"

class PipelinesCoreTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists pipelines with filters" do
    stub_call(:get, "#{repo}/pipelines")
    client.list_pipelines(workspace: "ws", repository: "repo", q: "x", sort: "-created_on", page: 2, pagelen: 10)
    assert_requested(:get, api_url("#{repo}/pipelines"), query: { "q" => "x", "sort" => "-created_on", "page" => "2", "pagelen" => "10" })
  end

  test "creates a pipeline with a target and variables" do
    stub_call(:post, "#{repo}/pipelines")
    client.create_pipeline(
      workspace: "ws", repository: "repo",
      target: { "type" => "pipeline_ref_target", "ref_name" => "main" },
      variables: [{ "key" => "FOO", "value" => "BAR" }]
    )
    assert_requested(:post, api_url("#{repo}/pipelines"), body: {
                       "target" => { "type" => "pipeline_ref_target", "ref_name" => "main" },
                       "variables" => [{ "key" => "FOO", "value" => "BAR" }],
                     })
  end

  test "creates a pipeline without variables" do
    stub_call(:post, "#{repo}/pipelines")
    client.create_pipeline(workspace: "ws", repository: "repo", target: { "type" => "pipeline_ref_target" })
    assert_requested(:post, api_url("#{repo}/pipelines"), body: { "target" => { "type" => "pipeline_ref_target" } })
  end

  test "gets a pipeline" do
    stub_call(:get, "#{repo}/pipelines/{p}")
    client.get_pipeline(workspace: "ws", repository: "repo", pipeline_uuid: "{p}")
    assert_requested(:get, api_url("#{repo}/pipelines/{p}"))
  end

  test "stops a pipeline" do
    stub_call(:post, "#{repo}/pipelines/{p}/stopPipeline")
    client.stop_pipeline(workspace: "ws", repository: "repo", pipeline_uuid: "{p}")
    assert_requested(:post, api_url("#{repo}/pipelines/{p}/stopPipeline"))
  end

  test "lists pipeline steps" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps")
    client.list_pipeline_steps(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", page: 2)
    assert_requested(:get, api_url("#{repo}/pipelines/{p}/steps"), query: { "page" => "2" })
  end

  test "gets a pipeline step" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}")
    client.get_pipeline_step(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    assert_requested(:get, api_url("#{repo}/pipelines/{p}/steps/{s}"))
  end

  test "gets a pipeline step log as text" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/log", body: "LOG")
    result = client.get_pipeline_step_log(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    assert_equal("LOG", result)
  end

  test "gets a pipeline step container log as text" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/logs/{l}", body: "CLOG")
    result = client.get_pipeline_step_container_log(
      workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}", log_uuid: "{l}",
    )
    assert_equal("CLOG", result)
  end

  test "lists pipeline step test reports" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/test_reports")
    client.list_pipeline_step_test_reports(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    assert_requested(:get, api_url("#{repo}/pipelines/{p}/steps/{s}/test_reports"))
  end

  test "lists pipeline step test cases" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases")
    client.list_pipeline_step_test_cases(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    assert_requested(:get, api_url("#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases"))
  end

  test "lists pipeline step test case reasons" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases/{t}/test_case_reasons")
    client.list_pipeline_step_test_case_reasons(
      workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}", test_case_uuid: "{t}",
    )
    assert_requested(:get, api_url("#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases/{t}/test_case_reasons"))
  end

  test "gets the pipeline config" do
    stub_call(:get, "#{repo}/pipelines_config")
    client.get_pipeline_config(workspace: "ws", repository: "repo")
    assert_requested(:get, api_url("#{repo}/pipelines_config"))
  end

  test "updates the pipeline config" do
    stub_call(:put, "#{repo}/pipelines_config")
    client.update_pipeline_config(workspace: "ws", repository: "repo", enabled: true, repository_pipeline: { "enabled" => true })
    assert_requested(:put, api_url("#{repo}/pipelines_config"), body: { "enabled" => true, "repository" => { "enabled" => true } })
  end

  test "updates the pipeline build number" do
    stub_call(:put, "#{repo}/pipelines_config/build_number")
    client.update_pipeline_build_number(workspace: "ws", repository: "repo", next_build_number: 42)
    assert_requested(:put, api_url("#{repo}/pipelines_config/build_number"), body: { "next" => 42 })
  end

  test "lists pipeline schedules" do
    stub_call(:get, "#{repo}/pipelines_config/schedules")
    client.list_pipeline_schedules(workspace: "ws", repository: "repo", page: 2)
    assert_requested(:get, api_url("#{repo}/pipelines_config/schedules"), query: { "page" => "2" })
  end

  test "creates a pipeline schedule" do
    stub_call(:post, "#{repo}/pipelines_config/schedules")
    client.create_pipeline_schedule(
      workspace: "ws", repository: "repo",
      target: { "ref_name" => "main" }, cron_pattern: "0 0 * * *", enabled: true
    )
    assert_requested(:post, api_url("#{repo}/pipelines_config/schedules"), body: {
                       "target" => { "ref_name" => "main" }, "cron_pattern" => "0 0 * * *", "enabled" => true
                     })
  end

  test "gets a pipeline schedule" do
    stub_call(:get, "#{repo}/pipelines_config/schedules/{sc}")
    client.get_pipeline_schedule(workspace: "ws", repository: "repo", schedule_uuid: "{sc}")
    assert_requested(:get, api_url("#{repo}/pipelines_config/schedules/{sc}"))
  end

  test "updates a pipeline schedule" do
    stub_call(:put, "#{repo}/pipelines_config/schedules/{sc}")
    client.update_pipeline_schedule(
      workspace: "ws", repository: "repo", schedule_uuid: "{sc}",
      enabled: false, cron_pattern: "0 1 * * *", target: { "ref_name" => "dev" }
    )
    assert_requested(:put, api_url("#{repo}/pipelines_config/schedules/{sc}"), body: {
                       "enabled" => false, "cron_pattern" => "0 1 * * *", "target" => { "ref_name" => "dev" }
                     })
  end

  test "deletes a pipeline schedule" do
    stub_call(:delete, "#{repo}/pipelines_config/schedules/{sc}")
    client.delete_pipeline_schedule(workspace: "ws", repository: "repo", schedule_uuid: "{sc}")
    assert_requested(:delete, api_url("#{repo}/pipelines_config/schedules/{sc}"))
  end

  test "lists pipeline schedule executions" do
    stub_call(:get, "#{repo}/pipelines_config/schedules/{sc}/executions")
    client.list_pipeline_schedule_executions(workspace: "ws", repository: "repo", schedule_uuid: "{sc}", page: 2)
    assert_requested(:get, api_url("#{repo}/pipelines_config/schedules/{sc}/executions"), query: { "page" => "2" })
  end

  test "gets the pipeline ssh key pair" do
    stub_call(:get, "#{repo}/pipelines_config/ssh/key_pair")
    client.get_pipeline_ssh_key_pair(workspace: "ws", repository: "repo")
    assert_requested(:get, api_url("#{repo}/pipelines_config/ssh/key_pair"))
  end

  test "updates the pipeline ssh key pair" do
    stub_call(:put, "#{repo}/pipelines_config/ssh/key_pair")
    client.update_pipeline_ssh_key_pair(workspace: "ws", repository: "repo", public_key: "pub", private_key: "priv")
    assert_requested(:put, api_url("#{repo}/pipelines_config/ssh/key_pair"), body: { "public_key" => "pub", "private_key" => "priv" })
  end

  test "deletes the pipeline ssh key pair" do
    stub_call(:delete, "#{repo}/pipelines_config/ssh/key_pair")
    client.delete_pipeline_ssh_key_pair(workspace: "ws", repository: "repo")
    assert_requested(:delete, api_url("#{repo}/pipelines_config/ssh/key_pair"))
  end

  test "lists pipeline known hosts" do
    stub_call(:get, "#{repo}/pipelines_config/ssh/known_hosts")
    client.list_pipeline_known_hosts(workspace: "ws", repository: "repo", page: 2)
    assert_requested(:get, api_url("#{repo}/pipelines_config/ssh/known_hosts"), query: { "page" => "2" })
  end

  test "creates a pipeline known host" do
    stub_call(:post, "#{repo}/pipelines_config/ssh/known_hosts")
    client.create_pipeline_known_host(
      workspace: "ws", repository: "repo", hostname: "bitbucket.org", public_key: { "key_type" => "ssh-rsa" },
    )
    assert_requested(:post, api_url("#{repo}/pipelines_config/ssh/known_hosts"), body: {
                       "hostname" => "bitbucket.org", "public_key" => { "key_type" => "ssh-rsa" }
                     })
  end

  test "gets a pipeline known host" do
    stub_call(:get, "#{repo}/pipelines_config/ssh/known_hosts/{kh}")
    client.get_pipeline_known_host(workspace: "ws", repository: "repo", known_host_uuid: "{kh}")
    assert_requested(:get, api_url("#{repo}/pipelines_config/ssh/known_hosts/{kh}"))
  end

  test "updates a pipeline known host" do
    stub_call(:put, "#{repo}/pipelines_config/ssh/known_hosts/{kh}")
    client.update_pipeline_known_host(
      workspace: "ws", repository: "repo", known_host_uuid: "{kh}",
      hostname: "example.com", public_key: { "key_type" => "ssh-ed25519" }
    )
    assert_requested(:put, api_url("#{repo}/pipelines_config/ssh/known_hosts/{kh}"), body: {
                       "hostname" => "example.com", "public_key" => { "key_type" => "ssh-ed25519" }
                     })
  end

  test "deletes a pipeline known host" do
    stub_call(:delete, "#{repo}/pipelines_config/ssh/known_hosts/{kh}")
    client.delete_pipeline_known_host(workspace: "ws", repository: "repo", known_host_uuid: "{kh}")
    assert_requested(:delete, api_url("#{repo}/pipelines_config/ssh/known_hosts/{kh}"))
  end
end
