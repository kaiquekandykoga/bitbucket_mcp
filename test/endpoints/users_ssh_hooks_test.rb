# frozen_string_literal: true

require_relative "../test_helper"

class UsersSshHooksTest < Test::Unit::TestCase
  include TestHelpers

  def client
    @client ||= build_client
  end

  test "gets the authenticated user" do
    stub_call(:get, "/user")
    client.current_user
    assert_requested(:get, api_url("/user"))
  end

  test "lists a user's ssh keys" do
    stub_call(:get, "/users/u1/ssh-keys")
    client.list_user_ssh_keys(selected_user: "u1", page: 2)
    assert_requested(:get, api_url("/users/u1/ssh-keys"), query: { "page" => "2" })
  end

  test "creates an ssh key" do
    stub_call(:post, "/users/u1/ssh-keys")
    client.create_user_ssh_key(selected_user: "u1", key: "ssh-rsa AAA", label: "laptop")
    assert_requested(:post, api_url("/users/u1/ssh-keys"), body: { "key" => "ssh-rsa AAA", "label" => "laptop" })
  end

  test "gets an ssh key" do
    stub_call(:get, "/users/u1/ssh-keys/k9")
    client.get_user_ssh_key(selected_user: "u1", key_id: "k9")
    assert_requested(:get, api_url("/users/u1/ssh-keys/k9"))
  end

  test "updates an ssh key" do
    stub_call(:put, "/users/u1/ssh-keys/k9")
    client.update_user_ssh_key(selected_user: "u1", key_id: "k9", label: "new", key: "ssh-rsa BBB")
    assert_requested(:put, api_url("/users/u1/ssh-keys/k9"), body: { "label" => "new", "key" => "ssh-rsa BBB" })
  end

  test "deletes an ssh key" do
    stub_call(:delete, "/users/u1/ssh-keys/k9")
    client.delete_user_ssh_key(selected_user: "u1", key_id: "k9")
    assert_requested(:delete, api_url("/users/u1/ssh-keys/k9"))
  end

  test "gets a public user" do
    stub_call(:get, "/users/u1")
    client.get_user(selected_user: "u1")
    assert_requested(:get, api_url("/users/u1"))
  end

  test "lists the authenticated user's emails" do
    stub_call(:get, "/user/emails")
    client.list_user_emails(page: 2)
    assert_requested(:get, api_url("/user/emails"), query: { "page" => "2" })
  end

  test "gets an email by value" do
    stub_call(:get, "/user/emails/me@example.com")
    client.get_user_email(email: "me@example.com")
    assert_requested(:get, api_url("/user/emails/me@example.com"))
  end

  test "lists hook event subjects" do
    stub_call(:get, "/hook_events")
    client.list_hook_event_subjects
    assert_requested(:get, api_url("/hook_events"))
  end

  test "lists hook events for a subject type" do
    stub_call(:get, "/hook_events/repository")
    client.list_hook_events(subject_type: "repository")
    assert_requested(:get, api_url("/hook_events/repository"))
  end
end
