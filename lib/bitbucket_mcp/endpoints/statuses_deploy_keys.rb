# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Commit build statuses and repository/project deploy keys.
    module StatusesDeployKeys
      def list_commit_statuses(workspace:, repository:, commit:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/statuses",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_commit_build_status(
        workspace:, repository:, commit:, key:, state:, url:,
        name: nil, description: nil, refname: nil
      )
        body = { "key" => key, "state" => state, "url" => url }
        body["name"] = name unless name.nil?
        body["description"] = description unless description.nil?
        body["refname"] = refname unless refname.nil?
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/statuses/build",
          body: body,
        )
      end

      def get_commit_build_status(workspace:, repository:, commit:, key:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/statuses/build/#{key}",
        )
      end

      def update_commit_build_status(
        workspace:, repository:, commit:, key:,
        state: nil, url: nil, name: nil, description: nil, refname: nil
      )
        body = {}
        body["state"] = state unless state.nil?
        body["url"] = url unless url.nil?
        body["name"] = name unless name.nil?
        body["description"] = description unless description.nil?
        body["refname"] = refname unless refname.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/statuses/build/#{key}",
          body: body,
        )
      end

      def list_deploy_keys(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/deploy-keys",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_deploy_key(workspace:, repository:, key:, label: nil)
        body = { "key" => key }
        body["label"] = label unless label.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/deploy-keys", body: body)
      end

      def get_deploy_key(workspace:, repository:, key_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/deploy-keys/#{key_id}")
      end

      def update_deploy_key(workspace:, repository:, key_id:, label: nil, key: nil)
        body = {}
        body["label"] = label unless label.nil?
        body["key"] = key unless key.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}/deploy-keys/#{key_id}", body: body)
      end

      def delete_deploy_key(workspace:, repository:, key_id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/deploy-keys/#{key_id}")
      end

      def list_project_deploy_keys(workspace:, project_key:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/projects/#{project_key}/deploy-keys",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_project_deploy_key(workspace:, project_key:, key:, label: nil)
        body = { "key" => key }
        body["label"] = label unless label.nil?
        request("POST", "/workspaces/#{workspace}/projects/#{project_key}/deploy-keys", body: body)
      end

      def get_project_deploy_key(workspace:, project_key:, key_id:)
        request("GET", "/workspaces/#{workspace}/projects/#{project_key}/deploy-keys/#{key_id}")
      end

      def delete_project_deploy_key(workspace:, project_key:, key_id:)
        request("DELETE", "/workspaces/#{workspace}/projects/#{project_key}/deploy-keys/#{key_id}")
      end
    end
  end
end
