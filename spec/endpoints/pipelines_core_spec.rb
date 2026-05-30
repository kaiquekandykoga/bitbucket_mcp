# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::PipelinesCore do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists pipelines with filters" do
    stub_call(:get, "#{repo}/pipelines")
    client.list_pipelines(workspace: "ws", repository: "repo", q: "x", sort: "-created_on", page: 2, pagelen: 10)
    expect(a_request(:get, api_url("#{repo}/pipelines"))
      .with(query: { "q" => "x", "sort" => "-created_on", "page" => "2", "pagelen" => "10" })).to have_been_made
  end

  it "creates a pipeline with a target and variables" do
    stub_call(:post, "#{repo}/pipelines")
    client.create_pipeline(
      workspace: "ws", repository: "repo",
      target: { "type" => "pipeline_ref_target", "ref_name" => "main" },
      variables: [{ "key" => "FOO", "value" => "BAR" }]
    )
    expect(a_request(:post, api_url("#{repo}/pipelines")).with(body: {
                                                                 "target" => { "type" => "pipeline_ref_target", "ref_name" => "main" },
                                                                 "variables" => [{ "key" => "FOO", "value" => "BAR" }],
                                                               })).to have_been_made
  end

  it "creates a pipeline without variables" do
    stub_call(:post, "#{repo}/pipelines")
    client.create_pipeline(workspace: "ws", repository: "repo", target: { "type" => "pipeline_ref_target" })
    expect(a_request(:post, api_url("#{repo}/pipelines"))
      .with(body: { "target" => { "type" => "pipeline_ref_target" } })).to have_been_made
  end

  it "gets a pipeline" do
    stub_call(:get, "#{repo}/pipelines/{p}")
    client.get_pipeline(workspace: "ws", repository: "repo", pipeline_uuid: "{p}")
    expect(a_request(:get, api_url("#{repo}/pipelines/{p}"))).to have_been_made
  end

  it "stops a pipeline" do
    stub_call(:post, "#{repo}/pipelines/{p}/stopPipeline")
    client.stop_pipeline(workspace: "ws", repository: "repo", pipeline_uuid: "{p}")
    expect(a_request(:post, api_url("#{repo}/pipelines/{p}/stopPipeline"))).to have_been_made
  end

  it "lists pipeline steps" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps")
    client.list_pipeline_steps(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", page: 2)
    expect(a_request(:get, api_url("#{repo}/pipelines/{p}/steps")).with(query: { "page" => "2" })).to have_been_made
  end

  it "gets a pipeline step" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}")
    client.get_pipeline_step(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    expect(a_request(:get, api_url("#{repo}/pipelines/{p}/steps/{s}"))).to have_been_made
  end

  it "gets a pipeline step log as text" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/log", body: "LOG")
    result = client.get_pipeline_step_log(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    expect(result).to eq("LOG")
  end

  it "gets a pipeline step container log as text" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/logs/{l}", body: "CLOG")
    result = client.get_pipeline_step_container_log(
      workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}", log_uuid: "{l}",
    )
    expect(result).to eq("CLOG")
  end

  it "lists pipeline step test reports" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/test_reports")
    client.list_pipeline_step_test_reports(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    expect(a_request(:get, api_url("#{repo}/pipelines/{p}/steps/{s}/test_reports"))).to have_been_made
  end

  it "lists pipeline step test cases" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases")
    client.list_pipeline_step_test_cases(workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}")
    expect(a_request(:get, api_url("#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases"))).to have_been_made
  end

  it "lists pipeline step test case reasons" do
    stub_call(:get, "#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases/{t}/test_case_reasons")
    client.list_pipeline_step_test_case_reasons(
      workspace: "ws", repository: "repo", pipeline_uuid: "{p}", step_uuid: "{s}", test_case_uuid: "{t}",
    )
    expect(a_request(:get, api_url("#{repo}/pipelines/{p}/steps/{s}/test_reports/test_cases/{t}/test_case_reasons"))).to have_been_made
  end

  it "gets the pipeline config" do
    stub_call(:get, "#{repo}/pipelines_config")
    client.get_pipeline_config(workspace: "ws", repository: "repo")
    expect(a_request(:get, api_url("#{repo}/pipelines_config"))).to have_been_made
  end

  it "updates the pipeline config" do
    stub_call(:put, "#{repo}/pipelines_config")
    client.update_pipeline_config(workspace: "ws", repository: "repo", enabled: true, repository_pipeline: { "enabled" => true })
    expect(a_request(:put, api_url("#{repo}/pipelines_config"))
      .with(body: { "enabled" => true, "repository" => { "enabled" => true } })).to have_been_made
  end

  it "updates the pipeline build number" do
    stub_call(:put, "#{repo}/pipelines_config/build_number")
    client.update_pipeline_build_number(workspace: "ws", repository: "repo", next_build_number: 42)
    expect(a_request(:put, api_url("#{repo}/pipelines_config/build_number"))
      .with(body: { "next" => 42 })).to have_been_made
  end

  it "lists pipeline schedules" do
    stub_call(:get, "#{repo}/pipelines_config/schedules")
    client.list_pipeline_schedules(workspace: "ws", repository: "repo", page: 2)
    expect(a_request(:get, api_url("#{repo}/pipelines_config/schedules")).with(query: { "page" => "2" })).to have_been_made
  end

  it "creates a pipeline schedule" do
    stub_call(:post, "#{repo}/pipelines_config/schedules")
    client.create_pipeline_schedule(
      workspace: "ws", repository: "repo",
      target: { "ref_name" => "main" }, cron_pattern: "0 0 * * *", enabled: true
    )
    expect(a_request(:post, api_url("#{repo}/pipelines_config/schedules")).with(body: {
                                                                                  "target" => { "ref_name" => "main" }, "cron_pattern" => "0 0 * * *", "enabled" => true
                                                                                })).to have_been_made
  end

  it "gets a pipeline schedule" do
    stub_call(:get, "#{repo}/pipelines_config/schedules/{sc}")
    client.get_pipeline_schedule(workspace: "ws", repository: "repo", schedule_uuid: "{sc}")
    expect(a_request(:get, api_url("#{repo}/pipelines_config/schedules/{sc}"))).to have_been_made
  end

  it "updates a pipeline schedule" do
    stub_call(:put, "#{repo}/pipelines_config/schedules/{sc}")
    client.update_pipeline_schedule(
      workspace: "ws", repository: "repo", schedule_uuid: "{sc}",
      enabled: false, cron_pattern: "0 1 * * *", target: { "ref_name" => "dev" }
    )
    expect(a_request(:put, api_url("#{repo}/pipelines_config/schedules/{sc}")).with(body: {
                                                                                      "enabled" => false, "cron_pattern" => "0 1 * * *", "target" => { "ref_name" => "dev" }
                                                                                    })).to have_been_made
  end

  it "deletes a pipeline schedule" do
    stub_call(:delete, "#{repo}/pipelines_config/schedules/{sc}")
    client.delete_pipeline_schedule(workspace: "ws", repository: "repo", schedule_uuid: "{sc}")
    expect(a_request(:delete, api_url("#{repo}/pipelines_config/schedules/{sc}"))).to have_been_made
  end

  it "lists pipeline schedule executions" do
    stub_call(:get, "#{repo}/pipelines_config/schedules/{sc}/executions")
    client.list_pipeline_schedule_executions(workspace: "ws", repository: "repo", schedule_uuid: "{sc}", page: 2)
    expect(a_request(:get, api_url("#{repo}/pipelines_config/schedules/{sc}/executions"))
      .with(query: { "page" => "2" })).to have_been_made
  end

  it "gets the pipeline ssh key pair" do
    stub_call(:get, "#{repo}/pipelines_config/ssh/key_pair")
    client.get_pipeline_ssh_key_pair(workspace: "ws", repository: "repo")
    expect(a_request(:get, api_url("#{repo}/pipelines_config/ssh/key_pair"))).to have_been_made
  end

  it "updates the pipeline ssh key pair" do
    stub_call(:put, "#{repo}/pipelines_config/ssh/key_pair")
    client.update_pipeline_ssh_key_pair(workspace: "ws", repository: "repo", public_key: "pub", private_key: "priv")
    expect(a_request(:put, api_url("#{repo}/pipelines_config/ssh/key_pair"))
      .with(body: { "public_key" => "pub", "private_key" => "priv" })).to have_been_made
  end

  it "deletes the pipeline ssh key pair" do
    stub_call(:delete, "#{repo}/pipelines_config/ssh/key_pair")
    client.delete_pipeline_ssh_key_pair(workspace: "ws", repository: "repo")
    expect(a_request(:delete, api_url("#{repo}/pipelines_config/ssh/key_pair"))).to have_been_made
  end

  it "lists pipeline known hosts" do
    stub_call(:get, "#{repo}/pipelines_config/ssh/known_hosts")
    client.list_pipeline_known_hosts(workspace: "ws", repository: "repo", page: 2)
    expect(a_request(:get, api_url("#{repo}/pipelines_config/ssh/known_hosts"))
      .with(query: { "page" => "2" })).to have_been_made
  end

  it "creates a pipeline known host" do
    stub_call(:post, "#{repo}/pipelines_config/ssh/known_hosts")
    client.create_pipeline_known_host(
      workspace: "ws", repository: "repo", hostname: "bitbucket.org", public_key: { "key_type" => "ssh-rsa" },
    )
    expect(a_request(:post, api_url("#{repo}/pipelines_config/ssh/known_hosts")).with(body: {
                                                                                        "hostname" => "bitbucket.org", "public_key" => { "key_type" => "ssh-rsa" }
                                                                                      })).to have_been_made
  end

  it "gets a pipeline known host" do
    stub_call(:get, "#{repo}/pipelines_config/ssh/known_hosts/{kh}")
    client.get_pipeline_known_host(workspace: "ws", repository: "repo", known_host_uuid: "{kh}")
    expect(a_request(:get, api_url("#{repo}/pipelines_config/ssh/known_hosts/{kh}"))).to have_been_made
  end

  it "updates a pipeline known host" do
    stub_call(:put, "#{repo}/pipelines_config/ssh/known_hosts/{kh}")
    client.update_pipeline_known_host(
      workspace: "ws", repository: "repo", known_host_uuid: "{kh}",
      hostname: "example.com", public_key: { "key_type" => "ssh-ed25519" }
    )
    expect(a_request(:put, api_url("#{repo}/pipelines_config/ssh/known_hosts/{kh}")).with(body: {
                                                                                            "hostname" => "example.com", "public_key" => { "key_type" => "ssh-ed25519" }
                                                                                          })).to have_been_made
  end

  it "deletes a pipeline known host" do
    stub_call(:delete, "#{repo}/pipelines_config/ssh/known_hosts/{kh}")
    client.delete_pipeline_known_host(workspace: "ws", repository: "repo", known_host_uuid: "{kh}")
    expect(a_request(:delete, api_url("#{repo}/pipelines_config/ssh/known_hosts/{kh}"))).to have_been_made
  end
end
