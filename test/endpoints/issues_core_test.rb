# frozen_string_literal: true

require_relative "../test_helper"

class IssuesCoreTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists components with filters" do
    stub_call(:get, "#{repo}/components")
    client.list_components(workspace: "ws", repository: "repo", q: "x", sort: "name", page: 2)
    assert_requested(:get, api_url("#{repo}/components"), query: { "q" => "x", "sort" => "name", "page" => "2" })
  end

  test "gets a component" do
    stub_call(:get, "#{repo}/components/5")
    client.get_component(workspace: "ws", repository: "repo", component_id: 5)
    assert_requested(:get, api_url("#{repo}/components/5"))
  end

  test "lists milestones with filters" do
    stub_call(:get, "#{repo}/milestones")
    client.list_milestones(workspace: "ws", repository: "repo", q: "x", sort: "name")
    assert_requested(:get, api_url("#{repo}/milestones"), query: { "q" => "x", "sort" => "name" })
  end

  test "gets a milestone" do
    stub_call(:get, "#{repo}/milestones/7")
    client.get_milestone(workspace: "ws", repository: "repo", milestone_id: 7)
    assert_requested(:get, api_url("#{repo}/milestones/7"))
  end

  test "lists versions with filters" do
    stub_call(:get, "#{repo}/versions")
    client.list_versions(workspace: "ws", repository: "repo", q: "x", sort: "name")
    assert_requested(:get, api_url("#{repo}/versions"), query: { "q" => "x", "sort" => "name" })
  end

  test "gets a version" do
    stub_call(:get, "#{repo}/versions/9")
    client.get_version(workspace: "ws", repository: "repo", version_id: 9)
    assert_requested(:get, api_url("#{repo}/versions/9"))
  end

  test "lists issues with filters" do
    stub_call(:get, "#{repo}/issues")
    client.list_issues(workspace: "ws", repository: "repo", q: "x", sort: "-created_on", page: 2)
    assert_requested(:get, api_url("#{repo}/issues"), query: { "q" => "x", "sort" => "-created_on", "page" => "2" })
  end

  test "creates an issue with only a title" do
    stub_call(:post, "#{repo}/issues")
    client.create_issue(workspace: "ws", repository: "repo", title: "T")
    assert_requested(:post, api_url("#{repo}/issues"), body: { "title" => "T" })
  end

  test "creates an issue with all optional fields" do
    stub_call(:post, "#{repo}/issues")
    client.create_issue(workspace: "ws", repository: "repo", title: "T", content: "body",
                        kind: "bug", priority: "major", state: "open",
                        component: "api", milestone: "m1", version: "v1", assignee: "{u1}")
    assert_requested(:post, api_url("#{repo}/issues"), body: {
                       "title" => "T",
                       "content" => { "raw" => "body" },
                       "kind" => "bug",
                       "priority" => "major",
                       "state" => "open",
                       "component" => { "name" => "api" },
                       "milestone" => { "name" => "m1" },
                       "version" => { "name" => "v1" },
                       "assignee" => { "uuid" => "{u1}" },
                     })
  end

  test "gets an issue" do
    stub_call(:get, "#{repo}/issues/1")
    client.get_issue(workspace: "ws", repository: "repo", issue_id: 1)
    assert_requested(:get, api_url("#{repo}/issues/1"))
  end

  test "updates an issue with selected fields" do
    stub_call(:put, "#{repo}/issues/1")
    client.update_issue(workspace: "ws", repository: "repo", issue_id: 1,
                        title: "New", content: "body", state: "resolved", assignee: "{u}")
    assert_requested(:put, api_url("#{repo}/issues/1"), body: {
                       "title" => "New",
                       "content" => { "raw" => "body" },
                       "state" => "resolved",
                       "assignee" => { "uuid" => "{u}" },
                     })
  end

  test "deletes an issue" do
    stub_call(:delete, "#{repo}/issues/1")
    client.delete_issue(workspace: "ws", repository: "repo", issue_id: 1)
    assert_requested(:delete, api_url("#{repo}/issues/1"))
  end

  test "starts an issue export" do
    stub_call(:post, "#{repo}/issues/export")
    client.export_issues(workspace: "ws", repository: "repo")
    assert_requested(:post, api_url("#{repo}/issues/export"))
  end

  test "downloads an issue export as text" do
    stub_call(:get, "#{repo}/issues/export/repo-issues-t9.zip", body: "ZIPDATA")
    assert_equal("ZIPDATA", client.get_issue_export(workspace: "ws", repository: "repo", repo_name: "repo", task_id: "t9"))
    assert_requested(:get, api_url("#{repo}/issues/export/repo-issues-t9.zip"))
  end

  test "gets the issue import status" do
    stub_call(:get, "#{repo}/issues/import")
    client.get_issue_import_status(workspace: "ws", repository: "repo")
    assert_requested(:get, api_url("#{repo}/issues/import"))
  end

  test "starts an issue import" do
    stub_call(:post, "#{repo}/issues/import")
    client.import_issues(workspace: "ws", repository: "repo")
    assert_requested(:post, api_url("#{repo}/issues/import"))
  end
end
