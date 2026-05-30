# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::UsersSshHooks do
  let(:client) { build_client }

  it "gets the authenticated user" do
    stub_call(:get, "/user")
    client.current_user
    expect(a_request(:get, api_url("/user"))).to have_been_made
  end

  it "lists a user's ssh keys" do
    stub_call(:get, "/users/u1/ssh-keys")
    client.list_user_ssh_keys(selected_user: "u1", page: 2)
    expect(a_request(:get, api_url("/users/u1/ssh-keys")).with(query: { "page" => "2" })).to have_been_made
  end

  it "creates an ssh key" do
    stub_call(:post, "/users/u1/ssh-keys")
    client.create_user_ssh_key(selected_user: "u1", key: "ssh-rsa AAA", label: "laptop")
    expect(a_request(:post, api_url("/users/u1/ssh-keys"))
      .with(body: { "key" => "ssh-rsa AAA", "label" => "laptop" })).to have_been_made
  end

  it "gets an ssh key" do
    stub_call(:get, "/users/u1/ssh-keys/k9")
    client.get_user_ssh_key(selected_user: "u1", key_id: "k9")
    expect(a_request(:get, api_url("/users/u1/ssh-keys/k9"))).to have_been_made
  end

  it "updates an ssh key" do
    stub_call(:put, "/users/u1/ssh-keys/k9")
    client.update_user_ssh_key(selected_user: "u1", key_id: "k9", label: "new", key: "ssh-rsa BBB")
    expect(a_request(:put, api_url("/users/u1/ssh-keys/k9"))
      .with(body: { "label" => "new", "key" => "ssh-rsa BBB" })).to have_been_made
  end

  it "deletes an ssh key" do
    stub_call(:delete, "/users/u1/ssh-keys/k9")
    client.delete_user_ssh_key(selected_user: "u1", key_id: "k9")
    expect(a_request(:delete, api_url("/users/u1/ssh-keys/k9"))).to have_been_made
  end

  it "gets a public user" do
    stub_call(:get, "/users/u1")
    client.get_user(selected_user: "u1")
    expect(a_request(:get, api_url("/users/u1"))).to have_been_made
  end

  it "lists the authenticated user's emails" do
    stub_call(:get, "/user/emails")
    client.list_user_emails(page: 2)
    expect(a_request(:get, api_url("/user/emails")).with(query: { "page" => "2" })).to have_been_made
  end

  it "gets an email by value" do
    stub_call(:get, "/user/emails/me@example.com")
    client.get_user_email(email: "me@example.com")
    expect(a_request(:get, api_url("/user/emails/me@example.com"))).to have_been_made
  end

  it "lists hook event subjects" do
    stub_call(:get, "/hook_events")
    client.list_hook_event_subjects
    expect(a_request(:get, api_url("/hook_events"))).to have_been_made
  end

  it "lists hook events for a subject type" do
    stub_call(:get, "/hook_events/repository")
    client.list_hook_events(subject_type: "repository")
    expect(a_request(:get, api_url("/hook_events/repository"))).to have_been_made
  end
end
