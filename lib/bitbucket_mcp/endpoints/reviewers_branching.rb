# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Pull request default reviewers, branch restrictions and branching models.
    module ReviewersBranching
      def list_default_reviewers(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/default-reviewers",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def list_effective_default_reviewers(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/effective-default-reviewers",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_default_reviewer(workspace:, repository:, target_username:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/default-reviewers/#{target_username}",
        )
      end

      def add_default_reviewer(workspace:, repository:, target_username:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/default-reviewers/#{target_username}",
        )
      end

      def remove_default_reviewer(workspace:, repository:, target_username:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/default-reviewers/#{target_username}",
        )
      end

      def list_branch_restrictions(workspace:, repository:, kind: nil, pattern: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/branch-restrictions",
          params: { "kind" => kind, "pattern" => pattern, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_branch_restriction(
        workspace:, repository:, kind:,
        pattern: nil, branch_match_kind: nil, branch_type: nil, users: nil, groups: nil, value: nil
      )
        body = { "kind" => kind }
        body["pattern"] = pattern unless pattern.nil?
        body["branch_match_kind"] = branch_match_kind unless branch_match_kind.nil?
        body["branch_type"] = branch_type unless branch_type.nil?
        body["users"] = users.map { |uuid| { "uuid" => uuid } } unless users.nil?
        body["groups"] = groups unless groups.nil?
        body["value"] = value unless value.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/branch-restrictions", body: body)
      end

      def get_branch_restriction(workspace:, repository:, id:)
        request("GET", "/repositories/#{workspace}/#{repository}/branch-restrictions/#{id}")
      end

      def update_branch_restriction(
        workspace:, repository:, id:,
        kind: nil, pattern: nil, branch_match_kind: nil, branch_type: nil, users: nil, groups: nil, value: nil
      )
        body = {}
        body["kind"] = kind unless kind.nil?
        body["pattern"] = pattern unless pattern.nil?
        body["branch_match_kind"] = branch_match_kind unless branch_match_kind.nil?
        body["branch_type"] = branch_type unless branch_type.nil?
        body["users"] = users.map { |uuid| { "uuid" => uuid } } unless users.nil?
        body["groups"] = groups unless groups.nil?
        body["value"] = value unless value.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}/branch-restrictions/#{id}", body: body)
      end

      def delete_branch_restriction(workspace:, repository:, id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/branch-restrictions/#{id}")
      end

      def get_branching_model(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}/branching-model")
      end

      def get_effective_branching_model(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}/effective-branching-model")
      end

      def get_branching_model_settings(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}/branching-model/settings")
      end

      def update_branching_model_settings(workspace:, repository:, development: nil, production: nil, branch_types: nil)
        body = {}
        body["development"] = development unless development.nil?
        body["production"] = production unless production.nil?
        body["branch_types"] = branch_types unless branch_types.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}/branching-model/settings", body: body)
      end

      def get_project_branching_model(workspace:, project_key:)
        request("GET", "/workspaces/#{workspace}/projects/#{project_key}/branching-model")
      end

      def get_project_branching_model_settings(workspace:, project_key:)
        request("GET", "/workspaces/#{workspace}/projects/#{project_key}/branching-model/settings")
      end

      def update_project_branching_model_settings(workspace:, project_key:, development: nil, production: nil, branch_types: nil)
        body = {}
        body["development"] = development unless development.nil?
        body["production"] = production unless production.nil?
        body["branch_types"] = branch_types unless branch_types.nil?
        request("PUT", "/workspaces/#{workspace}/projects/#{project_key}/branching-model/settings", body: body)
      end
    end
  end
end
