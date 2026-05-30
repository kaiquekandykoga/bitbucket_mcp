# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Commits, commit comments, Code Insights reports/annotations, diffs and patches.
    module Commits
      def get_commit(workspace:, repository:, commit:)
        request("GET", "/repositories/#{workspace}/#{repository}/commit/#{commit}")
      end

      def approve_commit(workspace:, repository:, commit:)
        request("POST", "/repositories/#{workspace}/#{repository}/commit/#{commit}/approve")
      end

      def unapprove_commit(workspace:, repository:, commit:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/commit/#{commit}/approve")
      end

      def list_commit_comments(workspace:, repository:, commit:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/comments",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_commit_comment(
        workspace:, repository:, commit:, content:,
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
        request("POST", "/repositories/#{workspace}/#{repository}/commit/#{commit}/comments", body: body)
      end

      def get_commit_comment(workspace:, repository:, commit:, comment_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/comments/#{comment_id}",
        )
      end

      def update_commit_comment(workspace:, repository:, commit:, comment_id:, content:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/comments/#{comment_id}",
          body: { "content" => { "raw" => content } },
        )
      end

      def delete_commit_comment(workspace:, repository:, commit:, comment_id:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/comments/#{comment_id}",
        )
      end

      def list_commit_reports(workspace:, repository:, commit:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_commit_report(workspace:, repository:, commit:, report_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}",
        )
      end

      def create_or_update_commit_report(
        workspace:, repository:, commit:, report_id:,
        title: nil, details: nil, external_id: nil, reporter: nil, link: nil,
        remote_link_enabled: nil, logo_url: nil, report_type: nil, result: nil, data: nil
      )
        body = {}
        body["title"] = title unless title.nil?
        body["details"] = details unless details.nil?
        body["external_id"] = external_id unless external_id.nil?
        body["reporter"] = reporter unless reporter.nil?
        body["link"] = link unless link.nil?
        body["remote_link_enabled"] = remote_link_enabled unless remote_link_enabled.nil?
        body["logo_url"] = logo_url unless logo_url.nil?
        body["report_type"] = report_type unless report_type.nil?
        body["result"] = result unless result.nil?
        body["data"] = data unless data.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}",
          body: body,
        )
      end

      def delete_commit_report(workspace:, repository:, commit:, report_id:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}",
        )
      end

      def list_commit_report_annotations(workspace:, repository:, commit:, report_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}/annotations",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def bulk_create_or_update_annotations(workspace:, repository:, commit:, report_id:, annotations:)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}/annotations",
          body: annotations,
        )
      end

      def get_commit_report_annotation(workspace:, repository:, commit:, report_id:, annotation_id:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}/annotations/#{annotation_id}",
        )
      end

      def create_or_update_commit_report_annotation(
        workspace:, repository:, commit:, report_id:, annotation_id:,
        external_id: nil, annotation_type: nil, path: nil, line: nil, summary: nil,
        details: nil, result: nil, severity: nil, link: nil
      )
        body = {}
        body["external_id"] = external_id unless external_id.nil?
        body["annotation_type"] = annotation_type unless annotation_type.nil?
        body["path"] = path unless path.nil?
        body["line"] = line unless line.nil?
        body["summary"] = summary unless summary.nil?
        body["details"] = details unless details.nil?
        body["result"] = result unless result.nil?
        body["severity"] = severity unless severity.nil?
        body["link"] = link unless link.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}/annotations/#{annotation_id}",
          body: body,
        )
      end

      def delete_commit_report_annotation(workspace:, repository:, commit:, report_id:, annotation_id:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/commit/#{commit}/reports/#{report_id}/annotations/#{annotation_id}",
        )
      end

      def list_commits(workspace:, repository:, include: nil, exclude: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commits",
          params: { "include" => include, "exclude" => exclude, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_commits_with_filter(workspace:, repository:, include: nil, exclude: nil, page: nil, pagelen: nil)
        body = {}
        body["include"] = include unless include.nil?
        body["exclude"] = exclude unless exclude.nil?
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/commits",
          body: body.empty? ? nil : body,
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def list_commits_for_revision(
        workspace:, repository:, revision:,
        include: nil, exclude: nil, path: nil, page: nil, pagelen: nil
      )
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/commits/#{revision}",
          params: { "include" => include, "exclude" => exclude, "path" => path, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_commits_for_revision_with_filter(
        workspace:, repository:, revision:, include: nil, exclude: nil, page: nil, pagelen: nil
      )
        body = {}
        body["include"] = include unless include.nil?
        body["exclude"] = exclude unless exclude.nil?
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/commits/#{revision}",
          body: body.empty? ? nil : body,
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_diff(
        workspace:, repository:, spec:,
        context: nil, path: nil, ignore_whitespace: nil, binary: nil, renames: nil, merge: nil, topic: nil
      )
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/diff/#{spec}",
          params: {
            "context" => context, "path" => path, "ignore_whitespace" => ignore_whitespace,
            "binary" => binary, "renames" => renames, "merge" => merge, "topic" => topic
          },
          text_response: true,
        )
      end

      def get_diffstat(
        workspace:, repository:, spec:,
        ignore_whitespace: nil, merge: nil, path: nil, renames: nil, topic: nil, page: nil, pagelen: nil
      )
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/diffstat/#{spec}",
          params: {
            "ignore_whitespace" => ignore_whitespace, "merge" => merge, "path" => path,
            "renames" => renames, "topic" => topic, "page" => page, "pagelen" => pagelen
          },
        )
      end

      def list_file_conflicts(workspace:, repository:, spec:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/file-conflicts/#{spec}",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_merge_base(workspace:, repository:, revspec:)
        request("GET", "/repositories/#{workspace}/#{repository}/merge-base/#{revspec}")
      end

      def get_patch(workspace:, repository:, spec:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/patch/#{spec}",
          text_response: true,
        )
      end
    end
  end
end
