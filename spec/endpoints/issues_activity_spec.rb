# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::IssuesActivity do
  let(:client) { build_client }
  let(:issue) { "/repositories/ws/repo/issues/1" }

  it "lists issue attachments" do
    stub_call(:get, "#{issue}/attachments")
    client.list_issue_attachments(workspace: "ws", repository: "repo", issue_id: 1, page: 2)
    expect(a_request(:get, api_url("#{issue}/attachments")).with(query: { "page" => "2" })).to have_been_made
  end

  it "uploads an issue attachment as multipart" do
    stub_call(:post, "#{issue}/attachments")
    client.upload_issue_attachment(workspace: "ws", repository: "repo", issue_id: 1, files: { "a.txt" => "hello" })
    expect(a_request(:post, api_url("#{issue}/attachments")).with do |req|
      req.headers["Content-Type"].to_s.start_with?("multipart/form-data") &&
        req.body.include?('name="files"; filename="a.txt"') && req.body.include?("hello")
    end).to have_been_made
  end

  it "gets an issue attachment as text" do
    stub_call(:get, "#{issue}/attachments/a.txt", body: "FILEDATA")
    expect(client.get_issue_attachment(workspace: "ws", repository: "repo", issue_id: 1, path: "a.txt")).to eq("FILEDATA")
  end

  it "deletes an issue attachment" do
    stub_call(:delete, "#{issue}/attachments/a.txt")
    client.delete_issue_attachment(workspace: "ws", repository: "repo", issue_id: 1, path: "a.txt")
    expect(a_request(:delete, api_url("#{issue}/attachments/a.txt"))).to have_been_made
  end

  it "lists issue changes with filters" do
    stub_call(:get, "#{issue}/changes")
    client.list_issue_changes(workspace: "ws", repository: "repo", issue_id: 1, q: "x", sort: "-created_on")
    expect(a_request(:get, api_url("#{issue}/changes"))
      .with(query: { "q" => "x", "sort" => "-created_on" })).to have_been_made
  end

  it "creates an issue change with changes and message" do
    stub_call(:post, "#{issue}/changes")
    client.create_issue_change(workspace: "ws", repository: "repo", issue_id: 1,
                               changes: { "state" => { "new" => "resolved" } }, message: "done")
    expect(a_request(:post, api_url("#{issue}/changes")).with(body: {
                                                                "changes" => { "state" => { "new" => "resolved" } },
                                                                "message" => { "raw" => "done" },
                                                              })).to have_been_made
  end

  it "gets a single issue change" do
    stub_call(:get, "#{issue}/changes/9")
    client.get_issue_change(workspace: "ws", repository: "repo", issue_id: 1, change_id: 9)
    expect(a_request(:get, api_url("#{issue}/changes/9"))).to have_been_made
  end

  it "lists issue comments with filters" do
    stub_call(:get, "#{issue}/comments")
    client.list_issue_comments(workspace: "ws", repository: "repo", issue_id: 1, q: "x")
    expect(a_request(:get, api_url("#{issue}/comments")).with(query: { "q" => "x" })).to have_been_made
  end

  it "creates an issue comment" do
    stub_call(:post, "#{issue}/comments")
    client.create_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, content: "hi")
    expect(a_request(:post, api_url("#{issue}/comments"))
      .with(body: { "content" => { "raw" => "hi" } })).to have_been_made
  end

  it "gets, updates and deletes an issue comment" do
    stub_call(:get, "#{issue}/comments/2")
    stub_call(:put, "#{issue}/comments/2")
    stub_call(:delete, "#{issue}/comments/2")
    client.get_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, comment_id: 2)
    client.update_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, comment_id: 2, content: "edit")
    client.delete_issue_comment(workspace: "ws", repository: "repo", issue_id: 1, comment_id: 2)
    expect(a_request(:get, api_url("#{issue}/comments/2"))).to have_been_made
    expect(a_request(:put, api_url("#{issue}/comments/2"))
      .with(body: { "content" => { "raw" => "edit" } })).to have_been_made
    expect(a_request(:delete, api_url("#{issue}/comments/2"))).to have_been_made
  end

  it "gets, casts and retracts a vote" do
    stub_call(:get, "#{issue}/vote")
    stub_call(:put, "#{issue}/vote")
    stub_call(:delete, "#{issue}/vote")
    client.get_issue_vote(workspace: "ws", repository: "repo", issue_id: 1)
    client.vote_for_issue(workspace: "ws", repository: "repo", issue_id: 1)
    client.unvote_issue(workspace: "ws", repository: "repo", issue_id: 1)
    expect(a_request(:get, api_url("#{issue}/vote"))).to have_been_made
    expect(a_request(:put, api_url("#{issue}/vote"))).to have_been_made
    expect(a_request(:delete, api_url("#{issue}/vote"))).to have_been_made
  end

  it "gets, starts and stops watching" do
    stub_call(:get, "#{issue}/watch")
    stub_call(:put, "#{issue}/watch")
    stub_call(:delete, "#{issue}/watch")
    client.get_issue_watch(workspace: "ws", repository: "repo", issue_id: 1)
    client.watch_issue(workspace: "ws", repository: "repo", issue_id: 1)
    client.unwatch_issue(workspace: "ws", repository: "repo", issue_id: 1)
    expect(a_request(:get, api_url("#{issue}/watch"))).to have_been_made
    expect(a_request(:put, api_url("#{issue}/watch"))).to have_been_made
    expect(a_request(:delete, api_url("#{issue}/watch"))).to have_been_made
  end
end
