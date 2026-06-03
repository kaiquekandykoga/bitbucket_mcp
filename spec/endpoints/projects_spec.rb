# frozen_string_literal: true

RSpec.describe BitbucketMcp::Endpoints::Projects do
  let(:client) { build_client }
  let(:base) { "/workspaces/ws/projects" }

  it "creates a workspace project" do
    stub_call(:post, base)
    client.create_workspace_project(workspace: "ws", key: "PRJ", name: "Project",
                                    description: "d", is_private: true, avatar: { "href" => "http://x" })
    expect(a_request(:post, api_url(base)).with(body: {
                                                  "key" => "PRJ",
                                                  "name" => "Project",
                                                  "description" => "d",
                                                  "is_private" => true,
                                                  "avatar" => { "href" => "http://x" },
                                                })).to have_been_made
  end

  it "updates a workspace project" do
    stub_call(:put, "#{base}/PRJ")
    client.update_workspace_project(workspace: "ws", project_key: "PRJ", name: "New", is_private: false)
    expect(a_request(:put, api_url("#{base}/PRJ"))
      .with(body: { "name" => "New", "is_private" => false })).to have_been_made
  end

  it "deletes a workspace project" do
    stub_call(:delete, "#{base}/PRJ")
    client.delete_workspace_project(workspace: "ws", project_key: "PRJ")
    expect(a_request(:delete, api_url("#{base}/PRJ"))).to have_been_made
  end

  it "lists project default reviewers" do
    stub_call(:get, "#{base}/PRJ/default-reviewers")
    client.list_project_default_reviewers(workspace: "ws", project_key: "PRJ", page: 2)
    expect(a_request(:get, api_url("#{base}/PRJ/default-reviewers"))
      .with(query: { "page" => "2" })).to have_been_made
  end

  it "gets a project default reviewer" do
    stub_call(:get, "#{base}/PRJ/default-reviewers/u1")
    client.get_project_default_reviewer(workspace: "ws", project_key: "PRJ", selected_user: "u1")
    expect(a_request(:get, api_url("#{base}/PRJ/default-reviewers/u1"))).to have_been_made
  end

  it "adds a project default reviewer" do
    stub_call(:put, "#{base}/PRJ/default-reviewers/u1")
    client.add_project_default_reviewer(workspace: "ws", project_key: "PRJ", selected_user: "u1")
    expect(a_request(:put, api_url("#{base}/PRJ/default-reviewers/u1"))).to have_been_made
  end

  it "removes a project default reviewer" do
    stub_call(:delete, "#{base}/PRJ/default-reviewers/u1")
    client.remove_project_default_reviewer(workspace: "ws", project_key: "PRJ", selected_user: "u1")
    expect(a_request(:delete, api_url("#{base}/PRJ/default-reviewers/u1"))).to have_been_made
  end

  it "lists project group permissions" do
    stub_call(:get, "#{base}/PRJ/permissions-config/groups")
    client.list_project_group_permissions(workspace: "ws", project_key: "PRJ", pagelen: 50)
    expect(a_request(:get, api_url("#{base}/PRJ/permissions-config/groups"))
      .with(query: { "pagelen" => "50" })).to have_been_made
  end

  it "gets a project group permission" do
    stub_call(:get, "#{base}/PRJ/permissions-config/groups/devs")
    client.get_project_group_permission(workspace: "ws", project_key: "PRJ", group_slug: "devs")
    expect(a_request(:get, api_url("#{base}/PRJ/permissions-config/groups/devs"))).to have_been_made
  end

  it "updates a project group permission" do
    stub_call(:put, "#{base}/PRJ/permissions-config/groups/devs")
    client.update_project_group_permission(workspace: "ws", project_key: "PRJ", group_slug: "devs", permission: "write")
    expect(a_request(:put, api_url("#{base}/PRJ/permissions-config/groups/devs"))
      .with(body: { "permission" => "write" })).to have_been_made
  end

  it "deletes a project group permission" do
    stub_call(:delete, "#{base}/PRJ/permissions-config/groups/devs")
    client.delete_project_group_permission(workspace: "ws", project_key: "PRJ", group_slug: "devs")
    expect(a_request(:delete, api_url("#{base}/PRJ/permissions-config/groups/devs"))).to have_been_made
  end

  it "lists project user permissions" do
    stub_call(:get, "#{base}/PRJ/permissions-config/users")
    client.list_project_user_permissions(workspace: "ws", project_key: "PRJ", page: 1)
    expect(a_request(:get, api_url("#{base}/PRJ/permissions-config/users"))
      .with(query: { "page" => "1" })).to have_been_made
  end

  it "gets a project user permission" do
    stub_call(:get, "#{base}/PRJ/permissions-config/users/u9")
    client.get_project_user_permission(workspace: "ws", project_key: "PRJ", selected_user_id: "u9")
    expect(a_request(:get, api_url("#{base}/PRJ/permissions-config/users/u9"))).to have_been_made
  end

  it "updates a project user permission" do
    stub_call(:put, "#{base}/PRJ/permissions-config/users/u9")
    client.update_project_user_permission(workspace: "ws", project_key: "PRJ", selected_user_id: "u9", permission: "admin")
    expect(a_request(:put, api_url("#{base}/PRJ/permissions-config/users/u9"))
      .with(body: { "permission" => "admin" })).to have_been_made
  end

  it "deletes a project user permission" do
    stub_call(:delete, "#{base}/PRJ/permissions-config/users/u9")
    client.delete_project_user_permission(workspace: "ws", project_key: "PRJ", selected_user_id: "u9")
    expect(a_request(:delete, api_url("#{base}/PRJ/permissions-config/users/u9"))).to have_been_made
  end
end
