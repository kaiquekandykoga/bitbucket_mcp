# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::IssuesCore do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists components with filters" do
    stub_call(:get, "#{repo}/components")
    client.list_components(workspace: "ws", repository: "repo", q: "x", sort: "name", page: 2)
    expect(a_request(:get, api_url("#{repo}/components"))
      .with(query: { "q" => "x", "sort" => "name", "page" => "2" })).to have_been_made
  end

  it "gets a component" do
    stub_call(:get, "#{repo}/components/5")
    client.get_component(workspace: "ws", repository: "repo", component_id: 5)
    expect(a_request(:get, api_url("#{repo}/components/5"))).to have_been_made
  end

  it "lists milestones with filters" do
    stub_call(:get, "#{repo}/milestones")
    client.list_milestones(workspace: "ws", repository: "repo", q: "x", sort: "name")
    expect(a_request(:get, api_url("#{repo}/milestones"))
      .with(query: { "q" => "x", "sort" => "name" })).to have_been_made
  end

  it "gets a milestone" do
    stub_call(:get, "#{repo}/milestones/7")
    client.get_milestone(workspace: "ws", repository: "repo", milestone_id: 7)
    expect(a_request(:get, api_url("#{repo}/milestones/7"))).to have_been_made
  end

  it "lists versions with filters" do
    stub_call(:get, "#{repo}/versions")
    client.list_versions(workspace: "ws", repository: "repo", q: "x", sort: "name")
    expect(a_request(:get, api_url("#{repo}/versions"))
      .with(query: { "q" => "x", "sort" => "name" })).to have_been_made
  end

  it "gets a version" do
    stub_call(:get, "#{repo}/versions/9")
    client.get_version(workspace: "ws", repository: "repo", version_id: 9)
    expect(a_request(:get, api_url("#{repo}/versions/9"))).to have_been_made
  end

  it "lists issues with filters" do
    stub_call(:get, "#{repo}/issues")
    client.list_issues(workspace: "ws", repository: "repo", q: "x", sort: "-created_on", page: 2)
    expect(a_request(:get, api_url("#{repo}/issues"))
      .with(query: { "q" => "x", "sort" => "-created_on", "page" => "2" })).to have_been_made
  end

  it "creates an issue with only a title" do
    stub_call(:post, "#{repo}/issues")
    client.create_issue(workspace: "ws", repository: "repo", title: "T")
    expect(a_request(:post, api_url("#{repo}/issues")).with(body: { "title" => "T" })).to have_been_made
  end

  it "creates an issue with all optional fields" do
    stub_call(:post, "#{repo}/issues")
    client.create_issue(workspace: "ws", repository: "repo", title: "T", content: "body",
                        kind: "bug", priority: "major", state: "open",
                        component: "api", milestone: "m1", version: "v1", assignee: "{u1}")
    expect(a_request(:post, api_url("#{repo}/issues")).with(body: {
                                                              "title" => "T",
                                                              "content" => { "raw" => "body" },
                                                              "kind" => "bug",
                                                              "priority" => "major",
                                                              "state" => "open",
                                                              "component" => { "name" => "api" },
                                                              "milestone" => { "name" => "m1" },
                                                              "version" => { "name" => "v1" },
                                                              "assignee" => { "uuid" => "{u1}" },
                                                            })).to have_been_made
  end

  it "gets an issue" do
    stub_call(:get, "#{repo}/issues/1")
    client.get_issue(workspace: "ws", repository: "repo", issue_id: 1)
    expect(a_request(:get, api_url("#{repo}/issues/1"))).to have_been_made
  end

  it "updates an issue with selected fields" do
    stub_call(:put, "#{repo}/issues/1")
    client.update_issue(workspace: "ws", repository: "repo", issue_id: 1,
                        title: "New", content: "body", state: "resolved", assignee: "{u}")
    expect(a_request(:put, api_url("#{repo}/issues/1")).with(body: {
                                                               "title" => "New",
                                                               "content" => { "raw" => "body" },
                                                               "state" => "resolved",
                                                               "assignee" => { "uuid" => "{u}" },
                                                             })).to have_been_made
  end

  it "deletes an issue" do
    stub_call(:delete, "#{repo}/issues/1")
    client.delete_issue(workspace: "ws", repository: "repo", issue_id: 1)
    expect(a_request(:delete, api_url("#{repo}/issues/1"))).to have_been_made
  end

  it "starts an issue export" do
    stub_call(:post, "#{repo}/issues/export")
    client.export_issues(workspace: "ws", repository: "repo")
    expect(a_request(:post, api_url("#{repo}/issues/export"))).to have_been_made
  end

  it "downloads an issue export as text" do
    stub_call(:get, "#{repo}/issues/export/repo-issues-t9.zip", body: "ZIPDATA")
    expect(client.get_issue_export(workspace: "ws", repository: "repo", repo_name: "repo", task_id: "t9")).to eq("ZIPDATA")
    expect(a_request(:get, api_url("#{repo}/issues/export/repo-issues-t9.zip"))).to have_been_made
  end

  it "gets the issue import status" do
    stub_call(:get, "#{repo}/issues/import")
    client.get_issue_import_status(workspace: "ws", repository: "repo")
    expect(a_request(:get, api_url("#{repo}/issues/import"))).to have_been_made
  end

  it "starts an issue import" do
    stub_call(:post, "#{repo}/issues/import")
    client.import_issues(workspace: "ws", repository: "repo")
    expect(a_request(:post, api_url("#{repo}/issues/import"))).to have_been_made
  end
end
