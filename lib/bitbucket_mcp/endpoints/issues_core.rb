# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Issue tracker components, milestones, versions, issues, and import/export.
    module IssuesCore
      def list_components(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/components",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_component(workspace:, repository:, component_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/components/#{component_id}")
      end

      def list_milestones(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/milestones",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_milestone(workspace:, repository:, milestone_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/milestones/#{milestone_id}")
      end

      def list_versions(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/versions",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def get_version(workspace:, repository:, version_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/versions/#{version_id}")
      end

      def list_issues(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_issue(
        workspace:, repository:, title:,
        content: nil, kind: nil, priority: nil, state: nil,
        component: nil, milestone: nil, version: nil, assignee: nil
      )
        body = { "title" => title }
        body["content"] = { "raw" => content } unless content.nil?
        body["kind"] = kind unless kind.nil?
        body["priority"] = priority unless priority.nil?
        body["state"] = state unless state.nil?
        body["component"] = { "name" => component } unless component.nil?
        body["milestone"] = { "name" => milestone } unless milestone.nil?
        body["version"] = { "name" => version } unless version.nil?
        body["assignee"] = { "uuid" => assignee } unless assignee.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/issues", body: body)
      end

      def get_issue(workspace:, repository:, issue_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}")
      end

      def update_issue(
        workspace:, repository:, issue_id:,
        title: nil, content: nil, kind: nil, priority: nil, state: nil,
        component: nil, milestone: nil, version: nil, assignee: nil
      )
        body = {}
        body["title"] = title unless title.nil?
        body["content"] = { "raw" => content } unless content.nil?
        body["kind"] = kind unless kind.nil?
        body["priority"] = priority unless priority.nil?
        body["state"] = state unless state.nil?
        body["component"] = { "name" => component } unless component.nil?
        body["milestone"] = { "name" => milestone } unless milestone.nil?
        body["version"] = { "name" => version } unless version.nil?
        body["assignee"] = { "uuid" => assignee } unless assignee.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}", body: body)
      end

      def delete_issue(workspace:, repository:, issue_id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}")
      end

      def export_issues(workspace:, repository:)
        request("POST", "/repositories/#{workspace}/#{repository}/issues/export")
      end

      def get_issue_export(workspace:, repository:, repo_name:, task_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues/export/#{repo_name}-issues-#{task_id}.zip",
          text_response: true,
        )
      end

      def get_issue_import_status(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}/issues/import")
      end

      def import_issues(workspace:, repository:)
        request("POST", "/repositories/#{workspace}/#{repository}/issues/import")
      end
    end
  end
end
