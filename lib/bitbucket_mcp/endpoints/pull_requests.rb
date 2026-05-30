# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Pull requests and their comments, tasks, commits, conflicts, diffs and merges.
    module PullRequests
      def list_pull_requests_for_commit(workspace:, repository:, commit:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/pullrequests",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def list_pull_requests(workspace:, repository:, state: nil, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests",
          params: { "state" => state, "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_pull_request(
        workspace:, repository:, title:, source_branch:, destination_branch: "main",
        description: nil, close_source_branch: nil, reviewers: nil
      )
        body = {
          "title" => title,
          "source" => { "branch" => { "name" => source_branch } },
          "destination" => { "branch" => { "name" => destination_branch } },
        }
        body["description"] = description unless description.nil?
        body["close_source_branch"] = close_source_branch unless close_source_branch.nil?
        body["reviewers"] = reviewers.map { |uuid| { "uuid" => uuid } } unless reviewers.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/pullrequests", body: body)
      end

      def list_repository_pull_request_activity(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/activity",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_pull_request(workspace:, repository:, pull_request_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}")
      end

      def update_pull_request(
        workspace:, repository:, pull_request_id:,
        title: nil, description: nil, destination_branch: nil, reviewers: nil
      )
        body = {}
        body["title"] = title unless title.nil?
        body["description"] = description unless description.nil?
        body["destination"] = { "branch" => { "name" => destination_branch } } unless destination_branch.nil?
        body["reviewers"] = reviewers.map { |uuid| { "uuid" => uuid } } unless reviewers.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}", body: body)
      end

      def list_pull_request_activity(workspace:, repository:, pull_request_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/activity",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def approve_pull_request(workspace:, repository:, pull_request_id:)
        request("POST", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/approve")
      end

      def unapprove_pull_request(workspace:, repository:, pull_request_id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/approve")
      end

      def request_changes(workspace:, repository:, pull_request_id:)
        request("POST", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/request-changes")
      end

      def remove_request_changes(workspace:, repository:, pull_request_id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/request-changes")
      end

      def list_pull_request_comments(workspace:, repository:, pull_request_id:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/comments",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_pull_request_comment(
        workspace:, repository:, pull_request_id:, content:,
        parent_id: nil, inline_path: nil, inline_to: nil, inline_from: nil
      )
        body = { "content" => { "raw" => content } }
        body["parent"] = { "id" => parent_id } unless parent_id.nil?
        unless inline_path.nil?
          inline = { "path" => inline_path }
          inline["to"] = inline_to unless inline_to.nil?
          inline["from"] = inline_from unless inline_from.nil?
          body["inline"] = inline
        end
        request("POST", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/comments", body: body)
      end

      def get_pull_request_comment(workspace:, repository:, pull_request_id:, comment_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/comments/#{comment_id}",
        )
      end

      def update_pull_request_comment(workspace:, repository:, pull_request_id:, comment_id:, content:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/comments/#{comment_id}",
          body: { "content" => { "raw" => content } },
        )
      end

      def delete_pull_request_comment(workspace:, repository:, pull_request_id:, comment_id:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/comments/#{comment_id}",
        )
      end

      def resolve_pull_request_comment(workspace:, repository:, pull_request_id:, comment_id:)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/comments/#{comment_id}/resolve",
        )
      end

      def reopen_pull_request_comment(workspace:, repository:, pull_request_id:, comment_id:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/comments/#{comment_id}/resolve",
        )
      end

      def list_pull_request_commits(workspace:, repository:, pull_request_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/commits",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def list_pull_request_conflicts(workspace:, repository:, pull_request_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/conflicts",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def decline_pull_request(workspace:, repository:, pull_request_id:)
        request("POST", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/decline")
      end

      def get_pull_request_diff(workspace:, repository:, pull_request_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/diff",
          text_response: true,
        )
      end

      def get_pull_request_diffstat(workspace:, repository:, pull_request_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/diffstat",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def merge_pull_request(
        workspace:, repository:, pull_request_id:,
        message: nil, close_source_branch: nil, merge_strategy: nil, async_: nil
      )
        body = {}
        body["message"] = message unless message.nil?
        body["close_source_branch"] = close_source_branch unless close_source_branch.nil?
        body["merge_strategy"] = merge_strategy unless merge_strategy.nil?
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/merge",
          body: body.empty? ? nil : body,
          params: { "async" => async_ },
        )
      end

      def get_merge_task_status(workspace:, repository:, pull_request_id:, task_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/merge/task-status/#{task_id}",
        )
      end

      def get_pull_request_patch(workspace:, repository:, pull_request_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/patch",
          text_response: true,
        )
      end

      def list_pull_request_statuses(workspace:, repository:, pull_request_id:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/statuses",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_pull_request_tasks(workspace:, repository:, pull_request_id:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/tasks",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_pull_request_task(workspace:, repository:, pull_request_id:, content:, comment_id: nil, pending: nil)
        body = { "content" => { "raw" => content } }
        body["comment"] = { "id" => comment_id } unless comment_id.nil?
        body["pending"] = pending unless pending.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/tasks", body: body)
      end

      def get_pull_request_task(workspace:, repository:, pull_request_id:, task_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/tasks/#{task_id}",
        )
      end

      def update_pull_request_task(workspace:, repository:, pull_request_id:, task_id:, content: nil, state: nil)
        body = {}
        body["content"] = { "raw" => content } unless content.nil?
        body["state"] = state unless state.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/tasks/#{task_id}",
          body: body,
        )
      end

      def delete_pull_request_task(workspace:, repository:, pull_request_id:, task_id:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/pullrequests/#{pull_request_id}/tasks/#{task_id}",
        )
      end
    end
  end
end
