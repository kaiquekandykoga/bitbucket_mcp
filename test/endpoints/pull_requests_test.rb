# frozen_string_literal: true

require_relative "../test_helper"

class PullRequestsTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "lists pull requests for a commit" do
    stub_call(:get, "#{repo}/commit/abc/pullrequests")
    client.list_pull_requests_for_commit(workspace: "ws", repository: "repo", commit: "abc", page: 2)
    assert_requested(:get, api_url("#{repo}/commit/abc/pullrequests"), query: { "page" => "2" })
  end

  test "lists pull requests with filters" do
    stub_call(:get, "#{repo}/pullrequests")
    client.list_pull_requests(workspace: "ws", repository: "repo", state: "OPEN", q: "x", sort: "-updated_on")
    assert_requested(:get, api_url("#{repo}/pullrequests"), query: { "state" => "OPEN", "q" => "x", "sort" => "-updated_on" })
  end

  test "creates a pull request with defaults and reviewers" do
    stub_call(:post, "#{repo}/pullrequests")
    client.create_pull_request(workspace: "ws", repository: "repo", title: "T", source_branch: "feature", reviewers: ["{u1}"])
    assert_requested(:post, api_url("#{repo}/pullrequests"), body: {
                       "title" => "T",
                       "source" => { "branch" => { "name" => "feature" } },
                       "destination" => { "branch" => { "name" => "main" } },
                       "reviewers" => [{ "uuid" => "{u1}" }],
                     })
  end

  test "honors an explicit destination branch and description" do
    stub_call(:post, "#{repo}/pullrequests")
    client.create_pull_request(workspace: "ws", repository: "repo", title: "T", source_branch: "f",
                               destination_branch: "develop", description: "d", close_source_branch: true)
    assert_requested(:post, api_url("#{repo}/pullrequests"), body: hash_including(
      "destination" => { "branch" => { "name" => "develop" } },
      "description" => "d",
      "close_source_branch" => true,
    ))
  end

  test "lists repository pull request activity" do
    stub_call(:get, "#{repo}/pullrequests/activity")
    client.list_repository_pull_request_activity(workspace: "ws", repository: "repo")
    assert_requested(:get, api_url("#{repo}/pullrequests/activity"))
  end

  test "gets a pull request" do
    stub_call(:get, "#{repo}/pullrequests/1")
    client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:get, api_url("#{repo}/pullrequests/1"))
  end

  test "updates a pull request" do
    stub_call(:put, "#{repo}/pullrequests/1")
    client.update_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1,
                               title: "New", destination_branch: "main", reviewers: ["{u}"])
    assert_requested(:put, api_url("#{repo}/pullrequests/1"), body: {
                       "title" => "New",
                       "destination" => { "branch" => { "name" => "main" } },
                       "reviewers" => [{ "uuid" => "{u}" }],
                     })
  end

  test "lists pull request activity" do
    stub_call(:get, "#{repo}/pullrequests/1/activity")
    client.list_pull_request_activity(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:get, api_url("#{repo}/pullrequests/1/activity"))
  end

  test "approves and unapproves a pull request" do
    stub_call(:post, "#{repo}/pullrequests/1/approve")
    stub_call(:delete, "#{repo}/pullrequests/1/approve")
    client.approve_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.unapprove_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/approve"))
    assert_requested(:delete, api_url("#{repo}/pullrequests/1/approve"))
  end

  test "requests and removes requested changes" do
    stub_call(:post, "#{repo}/pullrequests/1/request-changes")
    stub_call(:delete, "#{repo}/pullrequests/1/request-changes")
    client.request_changes(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.remove_request_changes(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/request-changes"))
    assert_requested(:delete, api_url("#{repo}/pullrequests/1/request-changes"))
  end

  test "lists pull request comments" do
    stub_call(:get, "#{repo}/pullrequests/1/comments")
    client.list_pull_request_comments(workspace: "ws", repository: "repo", pull_request_id: 1, q: "x")
    assert_requested(:get, api_url("#{repo}/pullrequests/1/comments"), query: { "q" => "x" })
  end

  test "creates a plain pull request comment" do
    stub_call(:post, "#{repo}/pullrequests/1/comments")
    client.create_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, content: "hi")
    assert_requested(:post, api_url("#{repo}/pullrequests/1/comments"), body: { "content" => { "raw" => "hi" } })
  end

  test "creates an inline reply comment" do
    stub_call(:post, "#{repo}/pullrequests/1/comments")
    client.create_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, content: "hi",
                                       parent_id: 5, inline_path: "a.rb", inline_to: 10, inline_from: 9)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/comments"), body: {
                       "content" => { "raw" => "hi" },
                       "parent" => { "id" => 5 },
                       "inline" => { "path" => "a.rb", "to" => 10, "from" => 9 },
                     })
  end

  test "gets, updates and deletes a comment" do
    stub_call(:get, "#{repo}/pullrequests/1/comments/2")
    stub_call(:put, "#{repo}/pullrequests/1/comments/2")
    stub_call(:delete, "#{repo}/pullrequests/1/comments/2")
    client.get_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    client.update_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2, content: "edit")
    client.delete_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    assert_requested(:put, api_url("#{repo}/pullrequests/1/comments/2"), body: { "content" => { "raw" => "edit" } })
    assert_requested(:delete, api_url("#{repo}/pullrequests/1/comments/2"))
  end

  test "resolves and reopens a comment thread" do
    stub_call(:post, "#{repo}/pullrequests/1/comments/2/resolve")
    stub_call(:delete, "#{repo}/pullrequests/1/comments/2/resolve")
    client.resolve_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    client.reopen_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/comments/2/resolve"))
    assert_requested(:delete, api_url("#{repo}/pullrequests/1/comments/2/resolve"))
  end

  test "lists commits and conflicts" do
    stub_call(:get, "#{repo}/pullrequests/1/commits")
    stub_call(:get, "#{repo}/pullrequests/1/conflicts")
    client.list_pull_request_commits(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.list_pull_request_conflicts(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:get, api_url("#{repo}/pullrequests/1/commits"))
    assert_requested(:get, api_url("#{repo}/pullrequests/1/conflicts"))
  end

  test "declines a pull request" do
    stub_call(:post, "#{repo}/pullrequests/1/decline")
    client.decline_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/decline"))
  end

  test "fetches the diff and patch as text" do
    stub_call(:get, "#{repo}/pullrequests/1/diff", body: "DIFF")
    stub_call(:get, "#{repo}/pullrequests/1/patch", body: "PATCH")
    assert_equal("DIFF", client.get_pull_request_diff(workspace: "ws", repository: "repo", pull_request_id: 1))
    assert_equal("PATCH", client.get_pull_request_patch(workspace: "ws", repository: "repo", pull_request_id: 1))
  end

  test "fetches the diffstat" do
    stub_call(:get, "#{repo}/pullrequests/1/diffstat")
    client.get_pull_request_diffstat(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:get, api_url("#{repo}/pullrequests/1/diffstat"))
  end

  test "merges with a body and async query param" do
    stub_call(:post, "#{repo}/pullrequests/1/merge")
    client.merge_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1,
                              message: "m", merge_strategy: "squash", async_: true)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/merge"), query: { "async" => "true" }, body: { "message" => "m", "merge_strategy" => "squash" })
  end

  test "merges with no body when no options are given" do
    stub_call(:post, "#{repo}/pullrequests/1/merge")
    client.merge_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/merge")) { |req| req.body.to_s.empty? }
  end

  test "gets the merge task status" do
    stub_call(:get, "#{repo}/pullrequests/1/merge/task-status/t9")
    client.get_merge_task_status(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: "t9")
    assert_requested(:get, api_url("#{repo}/pullrequests/1/merge/task-status/t9"))
  end

  test "lists statuses and tasks" do
    stub_call(:get, "#{repo}/pullrequests/1/statuses")
    stub_call(:get, "#{repo}/pullrequests/1/tasks")
    client.list_pull_request_statuses(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.list_pull_request_tasks(workspace: "ws", repository: "repo", pull_request_id: 1)
    assert_requested(:get, api_url("#{repo}/pullrequests/1/statuses"))
    assert_requested(:get, api_url("#{repo}/pullrequests/1/tasks"))
  end

  test "creates, gets, updates and deletes a task" do
    stub_call(:post, "#{repo}/pullrequests/1/tasks")
    stub_call(:get, "#{repo}/pullrequests/1/tasks/3")
    stub_call(:put, "#{repo}/pullrequests/1/tasks/3")
    stub_call(:delete, "#{repo}/pullrequests/1/tasks/3")
    client.create_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, content: "do it", comment_id: 7, pending: true)
    client.get_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: 3)
    client.update_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: 3, state: "RESOLVED")
    client.delete_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: 3)
    assert_requested(:post, api_url("#{repo}/pullrequests/1/tasks"), body: {
                       "content" => { "raw" => "do it" }, "comment" => { "id" => 7 }, "pending" => true
                     })
    assert_requested(:put, api_url("#{repo}/pullrequests/1/tasks/3"), body: { "state" => "RESOLVED" })
    assert_requested(:delete, api_url("#{repo}/pullrequests/1/tasks/3"))
  end
end
