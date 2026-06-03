# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::DeploymentsDownloadsGpg do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists deployments" do
    stub_call(:get, "#{repo}/deployments")
    client.list_deployments(workspace: "ws", repository: "repo", page: 2)
    expect(a_request(:get, api_url("#{repo}/deployments")).with(query: { "page" => "2" })).to have_been_made
  end

  it "gets a deployment" do
    stub_call(:get, "#{repo}/deployments/d-1")
    client.get_deployment(workspace: "ws", repository: "repo", deployment_uuid: "d-1")
    expect(a_request(:get, api_url("#{repo}/deployments/d-1"))).to have_been_made
  end

  it "lists environments" do
    stub_call(:get, "#{repo}/environments")
    client.list_environments(workspace: "ws", repository: "repo", pagelen: 10)
    expect(a_request(:get, api_url("#{repo}/environments")).with(query: { "pagelen" => "10" })).to have_been_made
  end

  it "creates an environment" do
    stub_call(:post, "#{repo}/environments")
    client.create_environment(workspace: "ws", repository: "repo", name: "Prod",
                              environment_type: { "name" => "Production" }, rank: 1)
    expect(a_request(:post, api_url("#{repo}/environments")).with(body: {
                                                                    "name" => "Prod",
                                                                    "environment_type" => { "name" => "Production" },
                                                                    "rank" => 1,
                                                                  })).to have_been_made
  end

  it "gets an environment" do
    stub_call(:get, "#{repo}/environments/e-1")
    client.get_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1")
    expect(a_request(:get, api_url("#{repo}/environments/e-1"))).to have_been_made
  end

  it "updates an environment with a body" do
    stub_call(:post, "#{repo}/environments/e-1/changes")
    client.update_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1",
                              body: { "change" => { "restrictions" => {} } })
    expect(a_request(:post, api_url("#{repo}/environments/e-1/changes"))
      .with(body: { "change" => { "restrictions" => {} } })).to have_been_made
  end

  it "updates an environment with an empty body when none is given" do
    stub_call(:post, "#{repo}/environments/e-1/changes")
    client.update_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1")
    expect(a_request(:post, api_url("#{repo}/environments/e-1/changes")).with(body: {})).to have_been_made
  end

  it "deletes an environment" do
    stub_call(:delete, "#{repo}/environments/e-1")
    client.delete_environment(workspace: "ws", repository: "repo", environment_uuid: "e-1")
    expect(a_request(:delete, api_url("#{repo}/environments/e-1"))).to have_been_made
  end

  it "lists downloads" do
    stub_call(:get, "#{repo}/downloads")
    client.list_downloads(workspace: "ws", repository: "repo", page: 1)
    expect(a_request(:get, api_url("#{repo}/downloads")).with(query: { "page" => "1" })).to have_been_made
  end

  it "uploads downloads as multipart" do
    stub_call(:post, "#{repo}/downloads")
    client.upload_download(workspace: "ws", repository: "repo", files: { "notes.txt" => "hello" })
    expect(a_request(:post, api_url("#{repo}/downloads")).with do |req|
      req.headers["Content-Type"].to_s.start_with?("multipart/form-data") &&
        req.body.include?('name="files"; filename="notes.txt"') &&
        req.body.include?("hello")
    end).to have_been_made
  end

  it "gets a download as text" do
    stub_call(:get, "#{repo}/downloads/notes.txt", body: "CONTENTS")
    expect(client.get_download(workspace: "ws", repository: "repo", filename: "notes.txt")).to eq("CONTENTS")
  end

  it "deletes a download" do
    stub_call(:delete, "#{repo}/downloads/notes.txt")
    client.delete_download(workspace: "ws", repository: "repo", filename: "notes.txt")
    expect(a_request(:delete, api_url("#{repo}/downloads/notes.txt"))).to have_been_made
  end

  it "lists user gpg keys" do
    stub_call(:get, "/users/u-1/gpg-keys")
    client.list_user_gpg_keys(selected_user: "u-1", page: 3)
    expect(a_request(:get, api_url("/users/u-1/gpg-keys")).with(query: { "page" => "3" })).to have_been_made
  end

  it "creates a user gpg key" do
    stub_call(:post, "/users/u-1/gpg-keys")
    client.create_user_gpg_key(selected_user: "u-1", key: "ABC", name: "laptop")
    expect(a_request(:post, api_url("/users/u-1/gpg-keys"))
      .with(body: { "key" => "ABC", "name" => "laptop" })).to have_been_made
  end

  it "gets a user gpg key" do
    stub_call(:get, "/users/u-1/gpg-keys/fp-9")
    client.get_user_gpg_key(selected_user: "u-1", fingerprint: "fp-9")
    expect(a_request(:get, api_url("/users/u-1/gpg-keys/fp-9"))).to have_been_made
  end

  it "deletes a user gpg key" do
    stub_call(:delete, "/users/u-1/gpg-keys/fp-9")
    client.delete_user_gpg_key(selected_user: "u-1", fingerprint: "fp-9")
    expect(a_request(:delete, api_url("/users/u-1/gpg-keys/fp-9"))).to have_been_made
  end
end
