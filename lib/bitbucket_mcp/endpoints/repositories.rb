# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Repositories: listing, creation, forks, webhooks, permissions, settings and source.
    module Repositories
      def list_public_repositories(after: nil, role: nil, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories",
          params: { "after" => after, "role" => role, "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_repositories(workspace:, role: nil, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}",
          params: { "role" => role, "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_repository(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}")
      end

      def create_repository(
        workspace:, repository:, scm: nil, name: nil, description: nil, is_private: nil,
        fork_policy: nil, language: nil, has_issues: nil, has_wiki: nil, project_key: nil, mainbranch_name: nil
      )
        body = {}
        body["scm"] = scm unless scm.nil?
        body["name"] = name unless name.nil?
        body["description"] = description unless description.nil?
        body["is_private"] = is_private unless is_private.nil?
        body["fork_policy"] = fork_policy unless fork_policy.nil?
        body["language"] = language unless language.nil?
        body["has_issues"] = has_issues unless has_issues.nil?
        body["has_wiki"] = has_wiki unless has_wiki.nil?
        body["project"] = { "key" => project_key } unless project_key.nil?
        body["mainbranch"] = { "name" => mainbranch_name } unless mainbranch_name.nil?
        request("POST", "/repositories/#{workspace}/#{repository}", body: body)
      end

      def update_repository(
        workspace:, repository:, name: nil, description: nil, is_private: nil,
        fork_policy: nil, language: nil, has_issues: nil, has_wiki: nil, project_key: nil, mainbranch_name: nil
      )
        body = {}
        body["name"] = name unless name.nil?
        body["description"] = description unless description.nil?
        body["is_private"] = is_private unless is_private.nil?
        body["fork_policy"] = fork_policy unless fork_policy.nil?
        body["language"] = language unless language.nil?
        body["has_issues"] = has_issues unless has_issues.nil?
        body["has_wiki"] = has_wiki unless has_wiki.nil?
        body["project"] = { "key" => project_key } unless project_key.nil?
        body["mainbranch"] = { "name" => mainbranch_name } unless mainbranch_name.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}", body: body)
      end

      def delete_repository(workspace:, repository:, redirect_to: nil)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}",
          params: { "redirect_to" => redirect_to },
        )
      end

      def list_file_history(workspace:, repository:, commit:, path:, renames: nil, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/filehistory/#{commit}/#{path}",
          params: { "renames" => renames, "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_repository_forks(workspace:, repository:, role: nil, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/forks",
          params: { "role" => role, "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def fork_repository(
        workspace:, repository:, name: nil, destination_workspace: nil, is_private: nil,
        description: nil, project_key: nil, fork_policy: nil, language: nil
      )
        body = {}
        body["name"] = name unless name.nil?
        body["workspace"] = { "slug" => destination_workspace } unless destination_workspace.nil?
        body["is_private"] = is_private unless is_private.nil?
        body["description"] = description unless description.nil?
        body["project"] = { "key" => project_key } unless project_key.nil?
        body["fork_policy"] = fork_policy unless fork_policy.nil?
        body["language"] = language unless language.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/forks", body: body.empty? ? nil : body)
      end

      def list_repository_webhooks(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/hooks",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_repository_webhook(workspace:, repository:, url:, events:, description: nil, active: nil, secret: nil)
        body = { "url" => url, "events" => events }
        body["description"] = description unless description.nil?
        body["active"] = active unless active.nil?
        body["secret"] = secret unless secret.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/hooks", body: body)
      end

      def delete_repository_webhook(workspace:, repository:, uid:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/hooks/#{uid}")
      end

      def get_repository_webhook(workspace:, repository:, uid:)
        request("GET", "/repositories/#{workspace}/#{repository}/hooks/#{uid}")
      end

      def update_repository_webhook(workspace:, repository:, uid:, url: nil, events: nil, description: nil, active: nil, secret: nil)
        body = {}
        body["url"] = url unless url.nil?
        body["events"] = events unless events.nil?
        body["description"] = description unless description.nil?
        body["active"] = active unless active.nil?
        body["secret"] = secret unless secret.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}/hooks/#{uid}", body: body)
      end

      def get_repository_override_settings(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}/override-settings")
      end

      def set_repository_override_settings(workspace:, repository:, settings:)
        request("PUT", "/repositories/#{workspace}/#{repository}/override-settings", body: settings)
      end

      def list_repository_group_permissions(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/permissions-config/groups",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def delete_repository_group_permission(workspace:, repository:, group_slug:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/permissions-config/groups/#{group_slug}")
      end

      def get_repository_group_permission(workspace:, repository:, group_slug:)
        request("GET", "/repositories/#{workspace}/#{repository}/permissions-config/groups/#{group_slug}")
      end

      def update_repository_group_permission(workspace:, repository:, group_slug:, permission:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/permissions-config/groups/#{group_slug}",
          body: { "permission" => permission },
        )
      end

      def list_repository_user_permissions(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/permissions-config/users",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def delete_repository_user_permission(workspace:, repository:, selected_user_id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/permissions-config/users/#{selected_user_id}")
      end

      def get_repository_user_permission(workspace:, repository:, selected_user_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/permissions-config/users/#{selected_user_id}")
      end

      def update_repository_user_permission(workspace:, repository:, selected_user_id:, permission:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/permissions-config/users/#{selected_user_id}",
          body: { "permission" => permission },
        )
      end

      def get_repository_root_src(workspace:, repository:, format: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/src",
          params: { "format" => format },
          text_response: true,
        )
      end

      def create_src_commit(
        workspace:, repository:, message: nil, author: nil, parents: nil, branch: nil,
        files_to_add: nil, files_to_delete: nil
      )
        fields = []
        fields << ["message", nil, message] unless message.nil?
        fields << ["author", nil, author] unless author.nil?
        fields << ["parents", nil, parents] unless parents.nil?
        fields << ["branch", nil, branch] unless branch.nil?
        files_to_delete.each { |path| fields << ["files", nil, path] } if files_to_delete && !files_to_delete.empty?
        if files_to_add && !files_to_add.empty?
          files_to_add.each { |path, content| fields << [path, path.split("/").last, content] }
        end
        body_bytes, content_type = build_multipart(fields)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/src",
          body_bytes: body_bytes,
          body_content_type: content_type,
        )
      end

      def get_repository_src(workspace:, repository:, commit:, path:, format: nil, q: nil, sort: nil, max_depth: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/src/#{commit}/#{path}",
          params: { "format" => format, "q" => q, "sort" => sort, "max_depth" => max_depth },
          text_response: true,
        )
      end

      def list_repository_watchers(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/watchers",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def list_user_repository_permissions(q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/user/permissions/repositories",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_user_workspace_repository_permissions(workspace:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/user/workspaces/#{workspace}/permissions/repositories",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end
    end
  end
end
