# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::Snippets do
  let(:client) { build_client }

  it "lists snippets with a role filter" do
    stub_call(:get, "/snippets")
    client.list_snippets(role: "owner", page: 2)
    expect(a_request(:get, api_url("/snippets")).with(query: { "role" => "owner", "page" => "2" })).to have_been_made
  end

  it "creates a snippet via multipart" do
    stub_call(:post, "/snippets")
    client.create_snippet(title: "T", is_private: true, scm: "git", files: { "a.txt" => "hello" })
    expect(a_request(:post, api_url("/snippets")).with { |req| req.body.include?("hello") && req.body.include?("a.txt") }).to have_been_made
  end

  it "lists workspace snippets" do
    stub_call(:get, "/snippets/ws")
    client.list_workspace_snippets(workspace: "ws", role: "member")
    expect(a_request(:get, api_url("/snippets/ws")).with(query: { "role" => "member" })).to have_been_made
  end

  it "creates a workspace snippet via multipart" do
    stub_call(:post, "/snippets/ws")
    client.create_workspace_snippet(workspace: "ws", title: "T", files: { "b.rb" => "puts 1" })
    expect(a_request(:post, api_url("/snippets/ws")).with { |req| req.body.include?("puts 1") }).to have_been_made
  end

  it "gets a snippet" do
    stub_call(:get, "/snippets/ws/abc")
    client.get_snippet(workspace: "ws", encoded_id: "abc")
    expect(a_request(:get, api_url("/snippets/ws/abc"))).to have_been_made
  end

  it "updates a snippet via multipart" do
    stub_call(:put, "/snippets/ws/abc")
    client.update_snippet(workspace: "ws", encoded_id: "abc", title: "New", files: { "c.txt" => "data" })
    expect(a_request(:put, api_url("/snippets/ws/abc")).with { |req| req.body.include?("data") }).to have_been_made
  end

  it "deletes a snippet" do
    stub_call(:delete, "/snippets/ws/abc")
    client.delete_snippet(workspace: "ws", encoded_id: "abc")
    expect(a_request(:delete, api_url("/snippets/ws/abc"))).to have_been_made
  end

  it "lists snippet comments" do
    stub_call(:get, "/snippets/ws/abc/comments")
    client.list_snippet_comments(workspace: "ws", encoded_id: "abc", page: 1)
    expect(a_request(:get, api_url("/snippets/ws/abc/comments")).with(query: { "page" => "1" })).to have_been_made
  end

  it "creates a snippet comment" do
    stub_call(:post, "/snippets/ws/abc/comments")
    client.create_snippet_comment(workspace: "ws", encoded_id: "abc", content: "hi")
    expect(a_request(:post, api_url("/snippets/ws/abc/comments"))
      .with(body: { "content" => { "raw" => "hi" } })).to have_been_made
  end

  it "gets, updates and deletes a snippet comment" do
    stub_call(:get, "/snippets/ws/abc/comments/2")
    stub_call(:put, "/snippets/ws/abc/comments/2")
    stub_call(:delete, "/snippets/ws/abc/comments/2")
    client.get_snippet_comment(workspace: "ws", encoded_id: "abc", comment_id: 2)
    client.update_snippet_comment(workspace: "ws", encoded_id: "abc", comment_id: 2, content: "edit")
    client.delete_snippet_comment(workspace: "ws", encoded_id: "abc", comment_id: 2)
    expect(a_request(:get, api_url("/snippets/ws/abc/comments/2"))).to have_been_made
    expect(a_request(:put, api_url("/snippets/ws/abc/comments/2"))
      .with(body: { "content" => { "raw" => "edit" } })).to have_been_made
    expect(a_request(:delete, api_url("/snippets/ws/abc/comments/2"))).to have_been_made
  end

  it "lists snippet commits" do
    stub_call(:get, "/snippets/ws/abc/commits")
    client.list_snippet_commits(workspace: "ws", encoded_id: "abc", pagelen: 50)
    expect(a_request(:get, api_url("/snippets/ws/abc/commits")).with(query: { "pagelen" => "50" })).to have_been_made
  end

  it "gets a snippet commit" do
    stub_call(:get, "/snippets/ws/abc/commits/rev1")
    client.get_snippet_commit(workspace: "ws", encoded_id: "abc", revision: "rev1")
    expect(a_request(:get, api_url("/snippets/ws/abc/commits/rev1"))).to have_been_made
  end

  it "gets a snippet file as text" do
    stub_call(:get, "/snippets/ws/abc/files/a.txt", body: "FILE")
    expect(client.get_snippet_file(workspace: "ws", encoded_id: "abc", path: "a.txt")).to eq("FILE")
  end

  it "gets, watches and unwatches a snippet" do
    stub_call(:get, "/snippets/ws/abc/watch")
    stub_call(:put, "/snippets/ws/abc/watch")
    stub_call(:delete, "/snippets/ws/abc/watch")
    client.get_snippet_watch(workspace: "ws", encoded_id: "abc")
    client.watch_snippet(workspace: "ws", encoded_id: "abc")
    client.unwatch_snippet(workspace: "ws", encoded_id: "abc")
    expect(a_request(:get, api_url("/snippets/ws/abc/watch"))).to have_been_made
    expect(a_request(:put, api_url("/snippets/ws/abc/watch"))).to have_been_made
    expect(a_request(:delete, api_url("/snippets/ws/abc/watch"))).to have_been_made
  end

  it "lists snippet watchers" do
    stub_call(:get, "/snippets/ws/abc/watchers")
    client.list_snippet_watchers(workspace: "ws", encoded_id: "abc")
    expect(a_request(:get, api_url("/snippets/ws/abc/watchers"))).to have_been_made
  end

  it "gets a snippet at a revision" do
    stub_call(:get, "/snippets/ws/abc/node9")
    client.get_snippet_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9")
    expect(a_request(:get, api_url("/snippets/ws/abc/node9"))).to have_been_made
  end

  it "updates a snippet at a revision via multipart" do
    stub_call(:put, "/snippets/ws/abc/node9")
    client.update_snippet_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9",
                                      is_private: false, files: { "d.txt" => "rev-data" })
    expect(a_request(:put, api_url("/snippets/ws/abc/node9")).with { |req| req.body.include?("rev-data") }).to have_been_made
  end

  it "deletes a snippet at a revision" do
    stub_call(:delete, "/snippets/ws/abc/node9")
    client.delete_snippet_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9")
    expect(a_request(:delete, api_url("/snippets/ws/abc/node9"))).to have_been_made
  end

  it "gets a snippet file at a revision as text" do
    stub_call(:get, "/snippets/ws/abc/node9/files/a.txt", body: "REVFILE")
    expect(client.get_snippet_file_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9", path: "a.txt"))
      .to eq("REVFILE")
  end

  it "gets the snippet diff and patch as text" do
    stub_call(:get, "/snippets/ws/abc/rev1/diff", body: "DIFF")
    stub_call(:get, "/snippets/ws/abc/rev1/patch", body: "PATCH")
    expect(client.get_snippet_diff(workspace: "ws", encoded_id: "abc", revision: "rev1")).to eq("DIFF")
    expect(client.get_snippet_patch(workspace: "ws", encoded_id: "abc", revision: "rev1")).to eq("PATCH")
  end
end
