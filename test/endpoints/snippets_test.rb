# frozen_string_literal: true

require_relative "../test_helper"

class SnippetsTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  test "lists snippets with a role filter" do
    stub_call(:get, "/snippets")
    client.list_snippets(role: "owner", page: 2)
    assert_requested(:get, api_url("/snippets"), query: { "role" => "owner", "page" => "2" })
  end

  test "creates a snippet via multipart" do
    stub_call(:post, "/snippets")
    client.create_snippet(title: "T", is_private: true, scm: "git", files: { "a.txt" => "hello" })
    assert_requested(:post, api_url("/snippets")) { |req| req.body.include?("hello") && req.body.include?("a.txt") }
  end

  test "lists workspace snippets" do
    stub_call(:get, "/snippets/ws")
    client.list_workspace_snippets(workspace: "ws", role: "member")
    assert_requested(:get, api_url("/snippets/ws"), query: { "role" => "member" })
  end

  test "creates a workspace snippet via multipart" do
    stub_call(:post, "/snippets/ws")
    client.create_workspace_snippet(workspace: "ws", title: "T", files: { "b.rb" => "puts 1" })
    assert_requested(:post, api_url("/snippets/ws")) { |req| req.body.include?("puts 1") }
  end

  test "gets a snippet" do
    stub_call(:get, "/snippets/ws/abc")
    client.get_snippet(workspace: "ws", encoded_id: "abc")
    assert_requested(:get, api_url("/snippets/ws/abc"))
  end

  test "updates a snippet via multipart" do
    stub_call(:put, "/snippets/ws/abc")
    client.update_snippet(workspace: "ws", encoded_id: "abc", title: "New", files: { "c.txt" => "data" })
    assert_requested(:put, api_url("/snippets/ws/abc")) { |req| req.body.include?("data") }
  end

  test "deletes a snippet" do
    stub_call(:delete, "/snippets/ws/abc")
    client.delete_snippet(workspace: "ws", encoded_id: "abc")
    assert_requested(:delete, api_url("/snippets/ws/abc"))
  end

  test "lists snippet comments" do
    stub_call(:get, "/snippets/ws/abc/comments")
    client.list_snippet_comments(workspace: "ws", encoded_id: "abc", page: 1)
    assert_requested(:get, api_url("/snippets/ws/abc/comments"), query: { "page" => "1" })
  end

  test "creates a snippet comment" do
    stub_call(:post, "/snippets/ws/abc/comments")
    client.create_snippet_comment(workspace: "ws", encoded_id: "abc", content: "hi")
    assert_requested(:post, api_url("/snippets/ws/abc/comments"), body: { "content" => { "raw" => "hi" } })
  end

  test "gets, updates and deletes a snippet comment" do
    stub_call(:get, "/snippets/ws/abc/comments/2")
    stub_call(:put, "/snippets/ws/abc/comments/2")
    stub_call(:delete, "/snippets/ws/abc/comments/2")
    client.get_snippet_comment(workspace: "ws", encoded_id: "abc", comment_id: 2)
    client.update_snippet_comment(workspace: "ws", encoded_id: "abc", comment_id: 2, content: "edit")
    client.delete_snippet_comment(workspace: "ws", encoded_id: "abc", comment_id: 2)
    assert_requested(:get, api_url("/snippets/ws/abc/comments/2"))
    assert_requested(:put, api_url("/snippets/ws/abc/comments/2"), body: { "content" => { "raw" => "edit" } })
    assert_requested(:delete, api_url("/snippets/ws/abc/comments/2"))
  end

  test "lists snippet commits" do
    stub_call(:get, "/snippets/ws/abc/commits")
    client.list_snippet_commits(workspace: "ws", encoded_id: "abc", pagelen: 50)
    assert_requested(:get, api_url("/snippets/ws/abc/commits"), query: { "pagelen" => "50" })
  end

  test "gets a snippet commit" do
    stub_call(:get, "/snippets/ws/abc/commits/rev1")
    client.get_snippet_commit(workspace: "ws", encoded_id: "abc", revision: "rev1")
    assert_requested(:get, api_url("/snippets/ws/abc/commits/rev1"))
  end

  test "gets a snippet file as text" do
    stub_call(:get, "/snippets/ws/abc/files/a.txt", body: "FILE")
    assert_equal("FILE", client.get_snippet_file(workspace: "ws", encoded_id: "abc", path: "a.txt"))
  end

  test "gets, watches and unwatches a snippet" do
    stub_call(:get, "/snippets/ws/abc/watch")
    stub_call(:put, "/snippets/ws/abc/watch")
    stub_call(:delete, "/snippets/ws/abc/watch")
    client.get_snippet_watch(workspace: "ws", encoded_id: "abc")
    client.watch_snippet(workspace: "ws", encoded_id: "abc")
    client.unwatch_snippet(workspace: "ws", encoded_id: "abc")
    assert_requested(:get, api_url("/snippets/ws/abc/watch"))
    assert_requested(:put, api_url("/snippets/ws/abc/watch"))
    assert_requested(:delete, api_url("/snippets/ws/abc/watch"))
  end

  test "lists snippet watchers" do
    stub_call(:get, "/snippets/ws/abc/watchers")
    client.list_snippet_watchers(workspace: "ws", encoded_id: "abc")
    assert_requested(:get, api_url("/snippets/ws/abc/watchers"))
  end

  test "gets a snippet at a revision" do
    stub_call(:get, "/snippets/ws/abc/node9")
    client.get_snippet_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9")
    assert_requested(:get, api_url("/snippets/ws/abc/node9"))
  end

  test "updates a snippet at a revision via multipart" do
    stub_call(:put, "/snippets/ws/abc/node9")
    client.update_snippet_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9",
                                      is_private: false, files: { "d.txt" => "rev-data" })
    assert_requested(:put, api_url("/snippets/ws/abc/node9")) { |req| req.body.include?("rev-data") }
  end

  test "deletes a snippet at a revision" do
    stub_call(:delete, "/snippets/ws/abc/node9")
    client.delete_snippet_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9")
    assert_requested(:delete, api_url("/snippets/ws/abc/node9"))
  end

  test "gets a snippet file at a revision as text" do
    stub_call(:get, "/snippets/ws/abc/node9/files/a.txt", body: "REVFILE")
    assert_equal("REVFILE",
                 client.get_snippet_file_at_revision(workspace: "ws", encoded_id: "abc", node_id: "node9", path: "a.txt"))
  end

  test "gets the snippet diff and patch as text" do
    stub_call(:get, "/snippets/ws/abc/rev1/diff", body: "DIFF")
    stub_call(:get, "/snippets/ws/abc/rev1/patch", body: "PATCH")
    assert_equal("DIFF", client.get_snippet_diff(workspace: "ws", encoded_id: "abc", revision: "rev1"))
    assert_equal("PATCH", client.get_snippet_patch(workspace: "ws", encoded_id: "abc", revision: "rev1"))
  end
end
