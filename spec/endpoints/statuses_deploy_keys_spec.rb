# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::StatusesDeployKeys do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists commit statuses with filters" do
    stub_call(:get, "#{repo}/commit/abc/statuses")
    client.list_commit_statuses(workspace: "ws", repository: "repo", commit: "abc", q: "x", sort: "-created_on")
    expect(a_request(:get, api_url("#{repo}/commit/abc/statuses"))
      .with(query: { "q" => "x", "sort" => "-created_on" })).to have_been_made
  end

  it "creates a commit build status" do
    stub_call(:post, "#{repo}/commit/abc/statuses/build")
    client.create_commit_build_status(workspace: "ws", repository: "repo", commit: "abc",
                                      key: "ci", state: "SUCCESSFUL", url: "https://ci", name: "CI", description: "d", refname: "main")
    expect(a_request(:post, api_url("#{repo}/commit/abc/statuses/build")).with(body: {
                                                                                 "key" => "ci", "state" => "SUCCESSFUL", "url" => "https://ci",
                                                                                 "name" => "CI", "description" => "d", "refname" => "main"
                                                                               })).to have_been_made
  end

  it "gets a commit build status by key" do
    stub_call(:get, "#{repo}/commit/abc/statuses/build/ci")
    client.get_commit_build_status(workspace: "ws", repository: "repo", commit: "abc", key: "ci")
    expect(a_request(:get, api_url("#{repo}/commit/abc/statuses/build/ci"))).to have_been_made
  end

  it "updates a commit build status" do
    stub_call(:put, "#{repo}/commit/abc/statuses/build/ci")
    client.update_commit_build_status(workspace: "ws", repository: "repo", commit: "abc", key: "ci",
                                      state: "FAILED", url: "https://ci")
    expect(a_request(:put, api_url("#{repo}/commit/abc/statuses/build/ci"))
      .with(body: { "state" => "FAILED", "url" => "https://ci" })).to have_been_made
  end

  it "lists repository deploy keys" do
    stub_call(:get, "#{repo}/deploy-keys")
    client.list_deploy_keys(workspace: "ws", repository: "repo", page: 2)
    expect(a_request(:get, api_url("#{repo}/deploy-keys")).with(query: { "page" => "2" })).to have_been_made
  end

  it "creates a repository deploy key" do
    stub_call(:post, "#{repo}/deploy-keys")
    client.create_deploy_key(workspace: "ws", repository: "repo", key: "ssh-rsa AAAA", label: "laptop")
    expect(a_request(:post, api_url("#{repo}/deploy-keys"))
      .with(body: { "key" => "ssh-rsa AAAA", "label" => "laptop" })).to have_been_made
  end

  it "gets a repository deploy key" do
    stub_call(:get, "#{repo}/deploy-keys/9")
    client.get_deploy_key(workspace: "ws", repository: "repo", key_id: "9")
    expect(a_request(:get, api_url("#{repo}/deploy-keys/9"))).to have_been_made
  end

  it "updates a repository deploy key" do
    stub_call(:put, "#{repo}/deploy-keys/9")
    client.update_deploy_key(workspace: "ws", repository: "repo", key_id: "9", label: "renamed")
    expect(a_request(:put, api_url("#{repo}/deploy-keys/9"))
      .with(body: { "label" => "renamed" })).to have_been_made
  end

  it "deletes a repository deploy key" do
    stub_call(:delete, "#{repo}/deploy-keys/9")
    client.delete_deploy_key(workspace: "ws", repository: "repo", key_id: "9")
    expect(a_request(:delete, api_url("#{repo}/deploy-keys/9"))).to have_been_made
  end

  it "lists project deploy keys" do
    stub_call(:get, "/workspaces/ws/projects/PROJ/deploy-keys")
    client.list_project_deploy_keys(workspace: "ws", project_key: "PROJ", pagelen: 50)
    expect(a_request(:get, api_url("/workspaces/ws/projects/PROJ/deploy-keys"))
      .with(query: { "pagelen" => "50" })).to have_been_made
  end

  it "creates a project deploy key" do
    stub_call(:post, "/workspaces/ws/projects/PROJ/deploy-keys")
    client.create_project_deploy_key(workspace: "ws", project_key: "PROJ", key: "ssh-rsa AAAA", label: "ci")
    expect(a_request(:post, api_url("/workspaces/ws/projects/PROJ/deploy-keys"))
      .with(body: { "key" => "ssh-rsa AAAA", "label" => "ci" })).to have_been_made
  end

  it "gets a project deploy key" do
    stub_call(:get, "/workspaces/ws/projects/PROJ/deploy-keys/9")
    client.get_project_deploy_key(workspace: "ws", project_key: "PROJ", key_id: "9")
    expect(a_request(:get, api_url("/workspaces/ws/projects/PROJ/deploy-keys/9"))).to have_been_made
  end

  it "deletes a project deploy key" do
    stub_call(:delete, "/workspaces/ws/projects/PROJ/deploy-keys/9")
    client.delete_project_deploy_key(workspace: "ws", project_key: "PROJ", key_id: "9")
    expect(a_request(:delete, api_url("/workspaces/ws/projects/PROJ/deploy-keys/9"))).to have_been_made
  end
end
