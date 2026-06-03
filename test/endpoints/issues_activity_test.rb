# frozen_string_literal: true

require_relative "../test_helper"

class IssuesActivityTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def issue
    "/repositories/ws/repo/issues/1"
  end

  test "lists issue attachments" do
    stub_call(:get, "#{issue}/attachments")
    client.list_issue_attachments(workspace: "ws", repository: "repo", issue_id: 1, page: 2)
    assert_requested(:get, api_url("#{issue}/attachments"), query: { "page" => "2" })
  end

  test "uploads an issue attachment as multipart" do
    stub_call(:post, "#{issue}/attachments")
    client.upload_issue_attachment(workspace: "ws", repository: "repo", issue_id: 1, files: { "a.txt" => "hello" })
    assert_requested(:post, api_url("#{issue}/attachments")) do |req|
      req.headers["Content-Type"].to_s.start_with?("multipart/form-data") &&
        req.body.include?('name="files"; filename="a.txt"') && req.body.include?("hello")
    end
  end

  test "gets an issue attachment as text" do
    stub_call(:get, "#{issue}/attachments/a.txt", body: "FILEDATA")
    assert_equal("FILEDATA", client.get_issue_attachment(workspace: "ws", repository: "repo", issue_id: 1, path: "a.txt"))
  end

  test "deletes an issue attachment" do
    stub_call(:delete, "#{issue}/attachments/a.txt")
    client.delete_issue_attachment(workspace: "ws", repository: "repo", issue_id: 1, path: "a.txt")
    assert_requested(:delete, api_url("#{issue}/attachments/a.txt"))
  end

  test "lists issue changes with filters" do
    stub_call(:get, "#{issue}/changes")
    client.list_issue_changes(workspace: "ws", repository: "repo", issue_id: 1, q: "x", sort: "-created_on")
    assert_requested(:get, api_url("#{issue}/changes"), query: { "q" => "x", "sort" => "-created_on" })
  end

  test "creates an issue change with changes and message" do
    stub_call(:post, "#{issue}/changes")
    client.create_issue_change(workspace: "ws", repository: "repo", issue_id: 1,
                               changes: { "state" => { "new" => "resolved" } }, message: "done")
    assert_requested(:post, api_url("#{issue}/changes"), body: {
                       "changes" => { "state" => { "new" => "resolved" } },
                       "message" => { "raw" => "done" },
                     })
  end

  test "gets a single issue change" do
    stub_call(:get, "#{issue}/changes/9")
    client.get_issue_change(workspace: "ws", repository: "repo", issue_id: 1, change_id: 9)
    assert_requested(:get, api_url("#{issue}/changes/9"))
  end

  test "lists issue comments with filters" do
    stub_call(:get, "#{issue}/comments")
    client.list_issue_comments(workspace: "ws", repository: "repo", issue_id: 1, q: "x")
    assert_requested(:get, api_url("#{issue}/comments"), query: { "q" => "x" })
  end

  test "creates an issue comment" do
    stub_call(:post, "#{issue}/comments")
    client.create_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, content: "hi")
    assert_requested(:post, api_url("#{issue}/comments"), body: { "content" => { "raw" => "hi" } })
  end

  test "gets, updates and deletes an issue comment" do
    stub_call(:get, "#{issue}/comments/2")
    stub_call(:put, "#{issue}/comments/2")
    stub_call(:delete, "#{issue}/comments/2")
    client.get_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, comment_id: 2)
    client.update_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, comment_id: 2, content: "edit")
    client.delete_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, comment_id: 2)
    assert_requested(:get, api_url("#{issue}/comments/2"))
    assert_requested(:put, api_url("#{issue}/comments/2"), body: { "content" => { "raw" => "edit" } })
    assert_requested(:delete, api_url("#{issue}/comments/2"))
  end

  test "gets, casts and retracts a vote" do
    stub_call(:get, "#{issue}/vote")
    stub_call(:put, "#{issue}/vote")
    stub_call(:delete, "#{issue}/vote")
    client.get_issue_vote(workspace: "ws", repository: "repo", issue_id: 1)
    client.vote_for_issue(workspace: "ws", repository: "repo", issue_id: 1)
    client.unvote_issue(workspace: "ws", repository: "repo", issue_id: 1)
    assert_requested(:get, api_url("#{issue}/vote"))
    assert_requested(:put, api_url("#{issue}/vote"))
    assert_requested(:delete, api_url("#{issue}/vote"))
  end

  test "gets, starts and stops watching" do
    stub_call(:get, "#{issue}/watch")
    stub_call(:put, "#{issue}/watch")
    stub_call(:delete, "#{issue}/watch")
    client.get_issue_watch(workspace: "ws", repository: "repo", issue_id: 1)
    client.watch_issue(workspace: "ws", repository: "repo", issue_id: 1)
    client.unwatch_issue(workspace: "ws", repository: "repo", issue_id: 1)
    assert_requested(:get, api_url("#{issue}/watch"))
    assert_requested(:put, api_url("#{issue}/watch"))
    assert_requested(:delete, api_url("#{issue}/watch"))
  end
end
