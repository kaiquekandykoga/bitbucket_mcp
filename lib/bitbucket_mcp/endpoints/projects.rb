# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Workspace-scoped projects: create/update/delete, default reviewers, and group/user permissions.
    module Projects
      def create_workspace_project(workspace:, key:, name:, description: nil, is_private: nil, avatar: nil)
        body = { "key" => key, "name" => name }
        body["description"] = description unless description.nil?
        body["is_private"] = is_private unless is_private.nil?
        body["avatar"] = avatar unless avatar.nil?
        request("POST", "/workspaces/#{workspace}/projects", body: body)
      end

      def update_workspace_project(
        workspace:, project_key:,
        key: nil, name: nil, description: nil, is_private: nil, avatar: nil
      )
        body = {}
        body["key"] = key unless key.nil?
        body["name"] = name unless name.nil?
        body["description"] = description unless description.nil?
        body["is_private"] = is_private unless is_private.nil?
        body["avatar"] = avatar unless avatar.nil?
        request("PUT", "/workspaces/#{workspace}/projects/#{project_key}", body: body)
      end

      def delete_workspace_project(workspace:, project_key:)
        request("DELETE", "/workspaces/#{workspace}/projects/#{project_key}")
      end

      def list_project_default_reviewers(workspace:, project_key:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/projects/#{project_key}/default-reviewers",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_project_default_reviewer(workspace:, project_key:, selected_user:)
        request(
          "GET",
          "/workspaces/#{workspace}/projects/#{project_key}/default-reviewers/#{selected_user}",
        )
      end

      def add_project_default_reviewer(workspace:, project_key:, selected_user:)
        request(
          "PUT",
          "/workspaces/#{workspace}/projects/#{project_key}/default-reviewers/#{selected_user}",
        )
      end

      def remove_project_default_reviewer(workspace:, project_key:, selected_user:)
        request(
          "DELETE",
          "/workspaces/#{workspace}/projects/#{project_key}/default-reviewers/#{selected_user}",
        )
      end

      def list_project_group_permissions(workspace:, project_key:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/groups",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_project_group_permission(workspace:, project_key:, group_slug:)
        request(
          "GET",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/groups/#{group_slug}",
        )
      end

      def update_project_group_permission(workspace:, project_key:, group_slug:, permission:)
        request(
          "PUT",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/groups/#{group_slug}",
          body: { "permission" => permission },
        )
      end

      def delete_project_group_permission(workspace:, project_key:, group_slug:)
        request(
          "DELETE",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/groups/#{group_slug}",
        )
      end

      def list_project_user_permissions(workspace:, project_key:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/users",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_project_user_permission(workspace:, project_key:, selected_user_id:)
        request(
          "GET",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/users/#{selected_user_id}",
        )
      end

      def update_project_user_permission(workspace:, project_key:, selected_user_id:, permission:)
        request(
          "PUT",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/users/#{selected_user_id}",
          body: { "permission" => permission },
        )
      end

      def delete_project_user_permission(workspace:, project_key:, selected_user_id:)
        request(
          "DELETE",
          "/workspaces/#{workspace}/projects/#{project_key}/permissions-config/users/#{selected_user_id}",
        )
      end
    end
  end
end
