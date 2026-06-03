# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Issue tracker attachments, changes, comments, votes and watches.
    module IssuesActivity
      def list_issue_attachments(workspace:, repository:, issue_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/attachments",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def upload_issue_attachment(workspace:, repository:, issue_id:, files:)
        fields = []
        files.each { |filename, content| fields << ["files", filename, content] }
        body_bytes, content_type = build_multipart(fields)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/attachments",
          body_bytes: body_bytes,
          body_content_type: content_type,
        )
      end

      def get_issue_attachment(workspace:, repository:, issue_id:, path:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/attachments/#{path}",
          text_response: true,
        )
      end

      def delete_issue_attachment(workspace:, repository:, issue_id:, path:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/attachments/#{path}",
        )
      end

      def list_issue_changes(workspace:, repository:, issue_id:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/changes",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_issue_change(workspace:, repository:, issue_id:, changes: nil, message: nil)
        body = {}
        body["changes"] = changes unless changes.nil?
        body["message"] = { "raw" => message } unless message.nil?
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/changes",
          body: body,
        )
      end

      def get_issue_change(workspace:, repository:, issue_id:, change_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/changes/#{change_id}",
        )
      end

      def list_issue_comments(workspace:, repository:, issue_id:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/comments",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_issue_comment(workspace:, repository:, issue_id:, content:)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/comments",
          body: { "content" => { "raw" => content } },
        )
      end

      def get_issue_comment(workspace:, repository:, issue_id:, comment_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/comments/#{comment_id}",
        )
      end

      def update_issue_comment(workspace:, repository:, issue_id:, comment_id:, content:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/comments/#{comment_id}",
          body: { "content" => { "raw" => content } },
        )
      end

      def delete_issue_comment(workspace:, repository:, issue_id:, comment_id:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/comments/#{comment_id}",
        )
      end

      def get_issue_vote(workspace:, repository:, issue_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/vote")
      end

      def vote_for_issue(workspace:, repository:, issue_id:)
        request("PUT", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/vote")
      end

      def unvote_issue(workspace:, repository:, issue_id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/vote")
      end

      def get_issue_watch(workspace:, repository:, issue_id:)
        request("GET", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/watch")
      end

      def watch_issue(workspace:, repository:, issue_id:)
        request("PUT", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/watch")
      end

      def unwatch_issue(workspace:, repository:, issue_id:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/issues/#{issue_id}/watch")
      end
    end
  end
end
