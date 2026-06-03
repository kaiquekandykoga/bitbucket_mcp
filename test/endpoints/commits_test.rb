# frozen_string_literal: true

require_relative "../test_helper"

class CommitsTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  def repo
    "/repositories/ws/repo"
  end

  test "gets a single commit" do
    stub_call(:get, "#{repo}/commit/abc")
    client.get_commit(workspace: "ws", repository: "repo", commit: "abc")
    assert_requested(:get, api_url("#{repo}/commit/abc"))
  end

  test "approves and unapproves a commit" do
    stub_call(:post, "#{repo}/commit/abc/approve")
    stub_call(:delete, "#{repo}/commit/abc/approve")
    client.approve_commit(workspace: "ws", repository: "repo", commit: "abc")
    client.unapprove_commit(workspace: "ws", repository: "repo", commit: "abc")
    assert_requested(:post, api_url("#{repo}/commit/abc/approve"))
    assert_requested(:delete, api_url("#{repo}/commit/abc/approve"))
  end

  test "lists commit comments with filters" do
    stub_call(:get, "#{repo}/commit/abc/comments")
    client.list_commit_comments(workspace: "ws", repository: "repo", commit: "abc", q: "x", sort: "-created_on")
    assert_requested(:get, api_url("#{repo}/commit/abc/comments"), query: { "q" => "x", "sort" => "-created_on" })
  end

  test "creates a plain commit comment" do
    stub_call(:post, "#{repo}/commit/abc/comments")
    client.create_commit_comment(workspace: "ws", repository: "repo", commit: "abc", content: "hi")
    assert_requested(:post, api_url("#{repo}/commit/abc/comments"), body: { "content" => { "raw" => "hi" } })
  end

  test "creates an inline reply commit comment" do
    stub_call(:post, "#{repo}/commit/abc/comments")
    client.create_commit_comment(workspace: "ws", repository: "repo", commit: "abc", content: "hi",
                                 parent_id: 5, inline_path: "a.rb", inline_to: 10, inline_from: 9)
    assert_requested(:post, api_url("#{repo}/commit/abc/comments"), body: {
                       "content" => { "raw" => "hi" },
                       "parent" => { "id" => 5 },
                       "inline" => { "path" => "a.rb", "to" => 10, "from" => 9 },
                     })
  end

  test "gets, updates and deletes a commit comment" do
    stub_call(:get, "#{repo}/commit/abc/comments/2")
    stub_call(:put, "#{repo}/commit/abc/comments/2")
    stub_call(:delete, "#{repo}/commit/abc/comments/2")
    client.get_commit_comment(workspace: "ws", repository: "repo", commit: "abc", comment_id: 2)
    client.update_commit_comment(workspace: "ws", repository: "repo", commit: "abc", comment_id: 2, content: "edit")
    client.delete_commit_comment(workspace: "ws", repository: "repo", commit: "abc", comment_id: 2)
    assert_requested(:get, api_url("#{repo}/commit/abc/comments/2"))
    assert_requested(:put, api_url("#{repo}/commit/abc/comments/2"), body: { "content" => { "raw" => "edit" } })
    assert_requested(:delete, api_url("#{repo}/commit/abc/comments/2"))
  end

  test "lists commit reports" do
    stub_call(:get, "#{repo}/commit/abc/reports")
    client.list_commit_reports(workspace: "ws", repository: "repo", commit: "abc", page: 2)
    assert_requested(:get, api_url("#{repo}/commit/abc/reports"), query: { "page" => "2" })
  end

  test "gets a commit report" do
    stub_call(:get, "#{repo}/commit/abc/reports/r1")
    client.get_commit_report(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1")
    assert_requested(:get, api_url("#{repo}/commit/abc/reports/r1"))
  end

  test "creates or updates a commit report" do
    stub_call(:put, "#{repo}/commit/abc/reports/r1")
    client.create_or_update_commit_report(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1",
                                          title: "T", report_type: "TEST", result: "PASSED", data: [{ "title" => "Coverage", "type" => "PERCENTAGE", "value" => 90 }])
    assert_requested(:put, api_url("#{repo}/commit/abc/reports/r1"), body: {
                       "title" => "T",
                       "report_type" => "TEST",
                       "result" => "PASSED",
                       "data" => [{ "title" => "Coverage", "type" => "PERCENTAGE", "value" => 90 }],
                     })
  end

  test "deletes a commit report" do
    stub_call(:delete, "#{repo}/commit/abc/reports/r1")
    client.delete_commit_report(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1")
    assert_requested(:delete, api_url("#{repo}/commit/abc/reports/r1"))
  end

  test "lists commit report annotations" do
    stub_call(:get, "#{repo}/commit/abc/reports/r1/annotations")
    client.list_commit_report_annotations(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1", page: 3)
    assert_requested(:get, api_url("#{repo}/commit/abc/reports/r1/annotations"), query: { "page" => "3" })
  end

  test "bulk creates or updates annotations with an array body" do
    stub_call(:post, "#{repo}/commit/abc/reports/r1/annotations")
    client.bulk_create_or_update_annotations(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1",
                                             annotations: [{ "external_id" => "a1", "summary" => "Issue" }])
    assert_requested(:post, api_url("#{repo}/commit/abc/reports/r1/annotations"), body: [{ "external_id" => "a1", "summary" => "Issue" }])
  end

  test "gets, updates and deletes a single annotation" do
    stub_call(:get, "#{repo}/commit/abc/reports/r1/annotations/an1")
    stub_call(:put, "#{repo}/commit/abc/reports/r1/annotations/an1")
    stub_call(:delete, "#{repo}/commit/abc/reports/r1/annotations/an1")
    client.get_commit_report_annotation(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1", annotation_id: "an1")
    client.create_or_update_commit_report_annotation(workspace: "ws", repository: "repo", commit: "abc",
                                                     report_id: "r1", annotation_id: "an1", annotation_type: "BUG", line: 12, severity: "HIGH")
    client.delete_commit_report_annotation(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1", annotation_id: "an1")
    assert_requested(:get, api_url("#{repo}/commit/abc/reports/r1/annotations/an1"))
    assert_requested(:put, api_url("#{repo}/commit/abc/reports/r1/annotations/an1"), body: {
                       "annotation_type" => "BUG", "line" => 12, "severity" => "HIGH"
                     })
    assert_requested(:delete, api_url("#{repo}/commit/abc/reports/r1/annotations/an1"))
  end

  test "lists commits, forwarding include/exclude as query params" do
    stub_call(:get, "#{repo}/commits")
    client.list_commits(workspace: "ws", repository: "repo", include: %w[a b], exclude: ["c"])
    # WebMock collapses repeated query keys to the last value; repeated-key (doseq)
    # encoding itself is asserted in client_spec via #build_request_target.
    assert_requested(:get, api_url("#{repo}/commits"), query: hash_including("include" => "b", "exclude" => "c"))
  end

  test "lists commits via POST with an include/exclude body" do
    stub_call(:post, "#{repo}/commits")
    client.list_commits_with_filter(workspace: "ws", repository: "repo", include: %w[a b], page: 2)
    assert_requested(:post, api_url("#{repo}/commits"), query: { "page" => "2" }, body: { "include" => %w[a b] })
  end

  test "lists commits via POST with no body when no filters are given" do
    stub_call(:post, "#{repo}/commits")
    client.list_commits_with_filter(workspace: "ws", repository: "repo")
    assert_requested(:post, api_url("#{repo}/commits")) { |req| req.body.to_s.empty? }
  end

  test "lists commits for a revision" do
    stub_call(:get, "#{repo}/commits/main")
    client.list_commits_for_revision(workspace: "ws", repository: "repo", revision: "main", include: ["x"], path: "src/a.rb")
    assert_requested(:get, api_url("#{repo}/commits/main"), query: hash_including("include" => "x", "path" => "src/a.rb"))
  end

  test "lists commits for a revision via POST with a body" do
    stub_call(:post, "#{repo}/commits/main")
    client.list_commits_for_revision_with_filter(workspace: "ws", repository: "repo", revision: "main", exclude: ["y"])
    assert_requested(:post, api_url("#{repo}/commits/main"), body: { "exclude" => ["y"] })
  end

  test "gets a diff as text with query params" do
    stub_call(:get, "#{repo}/diff/abc..def", body: "DIFF")
    result = client.get_diff(workspace: "ws", repository: "repo", spec: "abc..def", context: 5, ignore_whitespace: true)
    assert_equal("DIFF", result)
    assert_requested(:get, api_url("#{repo}/diff/abc..def"), query: { "context" => "5", "ignore_whitespace" => "true" })
  end

  test "gets a diffstat" do
    stub_call(:get, "#{repo}/diffstat/abc..def")
    client.get_diffstat(workspace: "ws", repository: "repo", spec: "abc..def", merge: false, path: %w[a b])
    assert_requested(:get, api_url("#{repo}/diffstat/abc..def"), query: hash_including("merge" => "false", "path" => "b"))
  end

  test "lists file conflicts" do
    stub_call(:get, "#{repo}/file-conflicts/abc..def")
    client.list_file_conflicts(workspace: "ws", repository: "repo", spec: "abc..def")
    assert_requested(:get, api_url("#{repo}/file-conflicts/abc..def"))
  end

  test "gets the merge base" do
    stub_call(:get, "#{repo}/merge-base/abc..def")
    client.get_merge_base(workspace: "ws", repository: "repo", revspec: "abc..def")
    assert_requested(:get, api_url("#{repo}/merge-base/abc..def"))
  end

  test "gets a patch as text" do
    stub_call(:get, "#{repo}/patch/abc", body: "PATCH")
    assert_equal("PATCH", client.get_patch(workspace: "ws", repository: "repo", spec: "abc"))
    assert_requested(:get, api_url("#{repo}/patch/abc"))
  end
end
