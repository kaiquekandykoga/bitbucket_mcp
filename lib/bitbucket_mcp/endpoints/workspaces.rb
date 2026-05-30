# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Workspaces, their members, permissions, projects, webhooks and settings.
    module Workspaces
      def list_user_workspace_permissions(q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/user/permissions/workspaces",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_user_workspaces(sort: nil, administrator: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/user/workspaces",
          params: { "sort" => sort, "administrator" => administrator, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_user_workspace_permission(workspace:)
        request("GET", "/user/workspaces/#{workspace}/permission")
      end

      def list_workspaces(role: nil, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces",
          params: { "role" => role, "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_workspace(workspace:)
        request("GET", "/workspaces/#{workspace}")
      end

      def list_workspace_webhooks(workspace:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/hooks",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_workspace_webhook(workspace:, url:, events:, description: nil, active: nil, secret: nil)
        body = { "url" => url, "events" => events }
        body["description"] = description unless description.nil?
        body["active"] = active unless active.nil?
        body["secret"] = secret unless secret.nil?
        request("POST", "/workspaces/#{workspace}/hooks", body: body)
      end

      def delete_workspace_webhook(workspace:, uid:)
        request("DELETE", "/workspaces/#{workspace}/hooks/#{uid}")
      end

      def get_workspace_webhook(workspace:, uid:)
        request("GET", "/workspaces/#{workspace}/hooks/#{uid}")
      end

      def update_workspace_webhook(workspace:, uid:, url: nil, events: nil, description: nil, active: nil, secret: nil)
        body = {}
        body["url"] = url unless url.nil?
        body["events"] = events unless events.nil?
        body["description"] = description unless description.nil?
        body["active"] = active unless active.nil?
        body["secret"] = secret unless secret.nil?
        request("PUT", "/workspaces/#{workspace}/hooks/#{uid}", body: body)
      end

      def list_workspace_members(workspace:, q: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/members",
          params: { "q" => q, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_workspace_member(workspace:, member:)
        request("GET", "/workspaces/#{workspace}/members/#{member}")
      end

      def list_workspace_permissions(workspace:, q: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/permissions",
          params: { "q" => q, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_workspace_repository_permissions(workspace:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/permissions/repositories",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_workspace_repository_permissions_for_repo(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/permissions/repositories/#{repository}",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_workspace_projects(workspace:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/projects",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_workspace_project(workspace:, project_key:)
        request("GET", "/workspaces/#{workspace}/projects/#{project_key}")
      end

      def list_workspace_user_pull_requests(workspace:, selected_user:, state: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/pullrequests/#{selected_user}",
          params: { "state" => state, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_workspace_gpg_key(workspace:)
        request("GET", "/workspaces/#{workspace}/settings/gpg/public-key")
      end
    end
  end
end
