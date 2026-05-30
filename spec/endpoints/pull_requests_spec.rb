# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::PullRequests do
  let(:client) { build_client }
  let(:repo) { "/repositories/ws/repo" }

  it "lists pull requests for a commit" do
    stub_call(:get, "#{repo}/commit/abc/pullrequests")
    client.list_pull_requests_for_commit(workspace: "ws", repository: "repo", commit: "abc", page: 2)
    expect(a_request(:get, api_url("#{repo}/commit/abc/pullrequests")).with(query: { "page" => "2" })).to have_been_made
  end

  it "lists pull requests with filters" do
    stub_call(:get, "#{repo}/pullrequests")
    client.list_pull_requests(workspace: "ws", repository: "repo", state: "OPEN", q: "x", sort: "-updated_on")
    expect(a_request(:get, api_url("#{repo}/pullrequests"))
      .with(query: { "state" => "OPEN", "q" => "x", "sort" => "-updated_on" })).to have_been_made
  end

  it "creates a pull request with defaults and reviewers" do
    stub_call(:post, "#{repo}/pullrequests")
    client.create_pull_request(workspace: "ws", repository: "repo", title: "T", source_branch: "feature", reviewers: ["{u1}"])
    expect(a_request(:post, api_url("#{repo}/pullrequests")).with(body: {
                                                                    "title" => "T",
                                                                    "source" => { "branch" => { "name" => "feature" } },
                                                                    "destination" => { "branch" => { "name" => "main" } },
                                                                    "reviewers" => [{ "uuid" => "{u1}" }],
                                                                  })).to have_been_made
  end

  it "honors an explicit destination branch and description" do
    stub_call(:post, "#{repo}/pullrequests")
    client.create_pull_request(workspace: "ws", repository: "repo", title: "T", source_branch: "f",
                               destination_branch: "develop", description: "d", close_source_branch: true)
    expect(a_request(:post, api_url("#{repo}/pullrequests")).with(body: hash_including(
      "destination" => { "branch" => { "name" => "develop" } },
      "description" => "d",
      "close_source_branch" => true,
    ))).to have_been_made
  end

  it "lists repository pull request activity" do
    stub_call(:get, "#{repo}/pullrequests/activity")
    client.list_repository_pull_request_activity(workspace: "ws", repository: "repo")
    expect(a_request(:get, api_url("#{repo}/pullrequests/activity"))).to have_been_made
  end

  it "gets a pull request" do
    stub_call(:get, "#{repo}/pullrequests/1")
    client.get_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:get, api_url("#{repo}/pullrequests/1"))).to have_been_made
  end

  it "updates a pull request" do
    stub_call(:put, "#{repo}/pullrequests/1")
    client.update_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1,
                               title: "New", destination_branch: "main", reviewers: ["{u}"])
    expect(a_request(:put, api_url("#{repo}/pullrequests/1")).with(body: {
                                                                     "title" => "New",
                                                                     "destination" => { "branch" => { "name" => "main" } },
                                                                     "reviewers" => [{ "uuid" => "{u}" }],
                                                                   })).to have_been_made
  end

  it "lists pull request activity" do
    stub_call(:get, "#{repo}/pullrequests/1/activity")
    client.list_pull_request_activity(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/activity"))).to have_been_made
  end

  it "approves and unapproves a pull request" do
    stub_call(:post, "#{repo}/pullrequests/1/approve")
    stub_call(:delete, "#{repo}/pullrequests/1/approve")
    client.approve_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.unapprove_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/approve"))).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/pullrequests/1/approve"))).to have_been_made
  end

  it "requests and removes requested changes" do
    stub_call(:post, "#{repo}/pullrequests/1/request-changes")
    stub_call(:delete, "#{repo}/pullrequests/1/request-changes")
    client.request_changes(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.remove_request_changes(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/request-changes"))).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/pullrequests/1/request-changes"))).to have_been_made
  end

  it "lists pull request comments" do
    stub_call(:get, "#{repo}/pullrequests/1/comments")
    client.list_pull_request_comments(workspace: "ws", repository: "repo", pull_request_id: 1, q: "x")
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/comments")).with(query: { "q" => "x" })).to have_been_made
  end

  it "creates a plain pull request comment" do
    stub_call(:post, "#{repo}/pullrequests/1/comments")
    client.create_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, content: "hi")
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/comments"))
      .with(body: { "content" => { "raw" => "hi" } })).to have_been_made
  end

  it "creates an inline reply comment" do
    stub_call(:post, "#{repo}/pullrequests/1/comments")
    client.create_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, content: "hi",
                                       parent_id: 5, inline_path: "a.rb", inline_to: 10, inline_from: 9)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/comments")).with(body: {
                                                                               "content" => { "raw" => "hi" },
                                                                               "parent" => { "id" => 5 },
                                                                               "inline" => { "path" => "a.rb", "to" => 10, "from" => 9 },
                                                                             })).to have_been_made
  end

  it "gets, updates and deletes a comment" do
    stub_call(:get, "#{repo}/pullrequests/1/comments/2")
    stub_call(:put, "#{repo}/pullrequests/1/comments/2")
    stub_call(:delete, "#{repo}/pullrequests/1/comments/2")
    client.get_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    client.update_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2, content: "edit")
    client.delete_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    expect(a_request(:put, api_url("#{repo}/pullrequests/1/comments/2"))
      .with(body: { "content" => { "raw" => "edit" } })).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/pullrequests/1/comments/2"))).to have_been_made
  end

  it "resolves and reopens a comment thread" do
    stub_call(:post, "#{repo}/pullrequests/1/comments/2/resolve")
    stub_call(:delete, "#{repo}/pullrequests/1/comments/2/resolve")
    client.resolve_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    client.reopen_pull_request_comment(workspace: "ws", repository: "repo", pull_request_id: 1, comment_id: 2)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/comments/2/resolve"))).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/pullrequests/1/comments/2/resolve"))).to have_been_made
  end

  it "lists commits and conflicts" do
    stub_call(:get, "#{repo}/pullrequests/1/commits")
    stub_call(:get, "#{repo}/pullrequests/1/conflicts")
    client.list_pull_request_commits(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.list_pull_request_conflicts(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/commits"))).to have_been_made
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/conflicts"))).to have_been_made
  end

  it "declines a pull request" do
    stub_call(:post, "#{repo}/pullrequests/1/decline")
    client.decline_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/decline"))).to have_been_made
  end

  it "fetches the diff and patch as text" do
    stub_call(:get, "#{repo}/pullrequests/1/diff", body: "DIFF")
    stub_call(:get, "#{repo}/pullrequests/1/patch", body: "PATCH")
    expect(client.get_pull_request_diff(workspace: "ws", repository: "repo", pull_request_id: 1)).to eq("DIFF")
    expect(client.get_pull_request_patch(workspace: "ws", repository: "repo", pull_request_id: 1)).to eq("PATCH")
  end

  it "fetches the diffstat" do
    stub_call(:get, "#{repo}/pullrequests/1/diffstat")
    client.get_pull_request_diffstat(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/diffstat"))).to have_been_made
  end

  it "merges with a body and async query param" do
    stub_call(:post, "#{repo}/pullrequests/1/merge")
    client.merge_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1,
                              message: "m", merge_strategy: "squash", async_: true)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/merge"))
      .with(query: { "async" => "true" }, body: { "message" => "m", "merge_strategy" => "squash" })).to have_been_made
  end

  it "merges with no body when no options are given" do
    stub_call(:post, "#{repo}/pullrequests/1/merge")
    client.merge_pull_request(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/merge")).with { |req| req.body.to_s.empty? }).to have_been_made
  end

  it "gets the merge task status" do
    stub_call(:get, "#{repo}/pullrequests/1/merge/task-status/t9")
    client.get_merge_task_status(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: "t9")
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/merge/task-status/t9"))).to have_been_made
  end

  it "lists statuses and tasks" do
    stub_call(:get, "#{repo}/pullrequests/1/statuses")
    stub_call(:get, "#{repo}/pullrequests/1/tasks")
    client.list_pull_request_statuses(workspace: "ws", repository: "repo", pull_request_id: 1)
    client.list_pull_request_tasks(workspace: "ws", repository: "repo", pull_request_id: 1)
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/statuses"))).to have_been_made
    expect(a_request(:get, api_url("#{repo}/pullrequests/1/tasks"))).to have_been_made
  end

  it "creates, gets, updates and deletes a task" do
    stub_call(:post, "#{repo}/pullrequests/1/tasks")
    stub_call(:get, "#{repo}/pullrequests/1/tasks/3")
    stub_call(:put, "#{repo}/pullrequests/1/tasks/3")
    stub_call(:delete, "#{repo}/pullrequests/1/tasks/3")
    client.create_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, content: "do it", comment_id: 7, pending: true)
    client.get_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: 3)
    client.update_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: 3, state: "RESOLVED")
    client.delete_pull_request_task(workspace: "ws", repository: "repo", pull_request_id: 1, task_id: 3)
    expect(a_request(:post, api_url("#{repo}/pullrequests/1/tasks")).with(body: {
                                                                            "content" => { "raw" => "do it" }, "comment" => { "id" => 7 }, "pending" => true
                                                                          })).to have_been_made
    expect(a_request(:put, api_url("#{repo}/pullrequests/1/tasks/3")).with(body: { "state" => "RESOLVED" })).to have_been_made
    expect(a_request(:delete, api_url("#{repo}/pullrequests/1/tasks/3"))).to have_been_made
  end
end
