# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::Commits do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "gets a single commit" do
    stub_call(:get, "#{repo}/commit/abc")
    client.get_commit(workspace: "ws", repository: "repo", commit: "abc")
    expect(a_request(:get, api_url("#{repo}/commit/abc"))).to have_been_made
  end

  it "approves and unapproves a commit" do
    stub_call(:post, "#{repo}/commit/abc/approve")
    stub_call(:delete, "#{repo}/commit/abc/approve")
    client.approve_commit(workspace: "ws", repository: "repo", commit: "abc")
    client.unapprove_commit(workspace: "ws", repository: "repo", commit: "abc")
    expect(a_request(:post, api_url("#{repo}/commit/abc/approve"))).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/commit/abc/approve"))).to have_been_made
  end

  it "lists commit comments with filters" do
    stub_call(:get, "#{repo}/commit/abc/comments")
    client.list_commit_comments(workspace: "ws", repository: "repo", commit: "abc", q: "x", sort: "-created_on")
    expect(a_request(:get, api_url("#{repo}/commit/abc/comments"))
      .with(query: { "q" => "x", "sort" => "-created_on" })).to have_been_made
  end

  it "creates a plain commit comment" do
    stub_call(:post, "#{repo}/commit/abc/comments")
    client.create_commit_comment(workspace: "ws", repository: "repo", commit: "abc", content: "hi")
    expect(a_request(:post, api_url("#{repo}/commit/abc/comments"))
      .with(body: { "content" => { "raw" => "hi" } })).to have_been_made
  end

  it "creates an inline reply commit comment" do
    stub_call(:post, "#{repo}/commit/abc/comments")
    client.create_commit_comment(workspace: "ws", repository: "repo", commit: "abc", content: "hi",
                                 parent_id: 5, inline_path: "a.rb", inline_to: 10, inline_from: 9)
    expect(a_request(:post, api_url("#{repo}/commit/abc/comments")).with(body: {
                                                                           "content" => { "raw" => "hi" },
                                                                           "parent" => { "id" => 5 },
                                                                           "inline" => { "path" => "a.rb", "to" => 10, "from" => 9 },
                                                                         })).to have_been_made
  end

  it "gets, updates and deletes a commit comment" do
    stub_call(:get, "#{repo}/commit/abc/comments/2")
    stub_call(:put, "#{repo}/commit/abc/comments/2")
    stub_call(:delete, "#{repo}/commit/abc/comments/2")
    client.get_commit_comment(workspace: "ws", repository: "repo", commit: "abc", comment_id: 2)
    client.update_commit_comment(workspace: "ws", repository: "repo", commit: "abc", comment_id: 2, content: "edit")
    client.delete_commit_comment(workspace: "ws", repository: "repo", commit: "abc", comment_id: 2)
    expect(a_request(:get, api_url("#{repo}/commit/abc/comments/2"))).to have_been_made
    expect(a_request(:put, api_url("#{repo}/commit/abc/comments/2"))
      .with(body: { "content" => { "raw" => "edit" } })).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/commit/abc/comments/2"))).to have_been_made
  end

  it "lists commit reports" do
    stub_call(:get, "#{repo}/commit/abc/reports")
    client.list_commit_reports(workspace: "ws", repository: "repo", commit: "abc", page: 2)
    expect(a_request(:get, api_url("#{repo}/commit/abc/reports")).with(query: { "page" => "2" })).to have_been_made
  end

  it "gets a commit report" do
    stub_call(:get, "#{repo}/commit/abc/reports/r1")
    client.get_commit_report(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1")
    expect(a_request(:get, api_url("#{repo}/commit/abc/reports/r1"))).to have_been_made
  end

  it "creates or updates a commit report" do
    stub_call(:put, "#{repo}/commit/abc/reports/r1")
    client.create_or_update_commit_report(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1",
                                          title: "T", report_type: "TEST", result: "PASSED", data: [{ "title" => "Coverage", "type" => "PERCENTAGE", "value" => 90 }])
    expect(a_request(:put, api_url("#{repo}/commit/abc/reports/r1")).with(body: {
                                                                            "title" => "T",
                                                                            "report_type" => "TEST",
                                                                            "result" => "PASSED",
                                                                            "data" => [{ "title" => "Coverage", "type" => "PERCENTAGE", "value" => 90 }],
                                                                          })).to have_been_made
  end

  it "deletes a commit report" do
    stub_call(:delete, "#{repo}/commit/abc/reports/r1")
    client.delete_commit_report(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1")
    expect(a_request(:delete, api_url("#{repo}/commit/abc/reports/r1"))).to have_been_made
  end

  it "lists commit report annotations" do
    stub_call(:get, "#{repo}/commit/abc/reports/r1/annotations")
    client.list_commit_report_annotations(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1", page: 3)
    expect(a_request(:get, api_url("#{repo}/commit/abc/reports/r1/annotations"))
      .with(query: { "page" => "3" })).to have_been_made
  end

  it "bulk creates or updates annotations with an array body" do
    stub_call(:post, "#{repo}/commit/abc/reports/r1/annotations")
    client.bulk_create_or_update_annotations(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1",
                                             annotations: [{ "external_id" => "a1", "summary" => "Issue" }])
    expect(a_request(:post, api_url("#{repo}/commit/abc/reports/r1/annotations"))
      .with(body: [{ "external_id" => "a1", "summary" => "Issue" }])).to have_been_made
  end

  it "gets, updates and deletes a single annotation" do
    stub_call(:get, "#{repo}/commit/abc/reports/r1/annotations/an1")
    stub_call(:put, "#{repo}/commit/abc/reports/r1/annotations/an1")
    stub_call(:delete, "#{repo}/commit/abc/reports/r1/annotations/an1")
    client.get_commit_report_annotation(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1", annotation_id: "an1")
    client.create_or_update_commit_report_annotation(workspace: "ws", repository: "repo", commit: "abc",
                                                     report_id: "r1", annotation_id: "an1", annotation_type: "BUG", line: 12, severity: "HIGH")
    client.delete_commit_report_annotation(workspace: "ws", repository: "repo", commit: "abc", report_id: "r1", annotation_id: "an1")
    expect(a_request(:get, api_url("#{repo}/commit/abc/reports/r1/annotations/an1"))).to have_been_made
    expect(a_request(:put, api_url("#{repo}/commit/abc/reports/r1/annotations/an1")).with(body: {
                                                                                            "annotation_type" => "BUG", "line" => 12, "severity" => "HIGH"
                                                                                          })).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/commit/abc/reports/r1/annotations/an1"))).to have_been_made
  end

  it "lists commits, forwarding include/exclude as query params" do
    stub_call(:get, "#{repo}/commits")
    client.list_commits(workspace: "ws", repository: "repo", include: %w[a b], exclude: ["c"])
    # WebMock collapses repeated query keys to the last value; repeated-key (doseq)
    # encoding itself is asserted in client_spec via #build_request_target.
    expect(a_request(:get, api_url("#{repo}/commits"))
      .with(query: hash_including("include" => "b", "exclude" => "c"))).to have_been_made
  end

  it "lists commits via POST with an include/exclude body" do
    stub_call(:post, "#{repo}/commits")
    client.list_commits_with_filter(workspace: "ws", repository: "repo", include: %w[a b], page: 2)
    expect(a_request(:post, api_url("#{repo}/commits"))
      .with(query: { "page" => "2" }, body: { "include" => %w[a b] })).to have_been_made
  end

  it "lists commits via POST with no body when no filters are given" do
    stub_call(:post, "#{repo}/commits")
    client.list_commits_with_filter(workspace: "ws", repository: "repo")
    expect(a_request(:post, api_url("#{repo}/commits")).with { |req| req.body.to_s.empty? }).to have_been_made
  end

  it "lists commits for a revision" do
    stub_call(:get, "#{repo}/commits/main")
    client.list_commits_for_revision(workspace: "ws", repository: "repo", revision: "main", include: ["x"], path: "src/a.rb")
    expect(a_request(:get, api_url("#{repo}/commits/main"))
      .with(query: hash_including("include" => "x", "path" => "src/a.rb"))).to have_been_made
  end

  it "lists commits for a revision via POST with a body" do
    stub_call(:post, "#{repo}/commits/main")
    client.list_commits_for_revision_with_filter(workspace: "ws", repository: "repo", revision: "main", exclude: ["y"])
    expect(a_request(:post, api_url("#{repo}/commits/main")).with(body: { "exclude" => ["y"] })).to have_been_made
  end

  it "gets a diff as text with query params" do
    stub_call(:get, "#{repo}/diff/abc..def", body: "DIFF")
    result = client.get_diff(workspace: "ws", repository: "repo", spec: "abc..def", context: 5, ignore_whitespace: true)
    expect(result).to eq("DIFF")
    expect(a_request(:get, api_url("#{repo}/diff/abc..def"))
      .with(query: { "context" => "5", "ignore_whitespace" => "true" })).to have_been_made
  end

  it "gets a diffstat" do
    stub_call(:get, "#{repo}/diffstat/abc..def")
    client.get_diffstat(workspace: "ws", repository: "repo", spec: "abc..def", merge: false, path: %w[a b])
    expect(a_request(:get, api_url("#{repo}/diffstat/abc..def"))
      .with(query: hash_including("merge" => "false", "path" => "b"))).to have_been_made
  end

  it "lists file conflicts" do
    stub_call(:get, "#{repo}/file-conflicts/abc..def")
    client.list_file_conflicts(workspace: "ws", repository: "repo", spec: "abc..def")
    expect(a_request(:get, api_url("#{repo}/file-conflicts/abc..def"))).to have_been_made
  end

  it "gets the merge base" do
    stub_call(:get, "#{repo}/merge-base/abc..def")
    client.get_merge_base(workspace: "ws", repository: "repo", revspec: "abc..def")
    expect(a_request(:get, api_url("#{repo}/merge-base/abc..def"))).to have_been_made
  end

  it "gets a patch as text" do
    stub_call(:get, "#{repo}/patch/abc", body: "PATCH")
    expect(client.get_patch(workspace: "ws", repository: "repo", spec: "abc")).to eq("PATCH")
    expect(a_request(:get, api_url("#{repo}/patch/abc"))).to have_been_made
  end
end
