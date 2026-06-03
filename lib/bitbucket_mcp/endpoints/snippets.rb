# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Snippets, their files, comments, commits, revisions and watchers.
    module Snippets
      def list_snippets(role: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/snippets",
          params: { "role" => role, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_snippet(title: nil, is_private: nil, scm: nil, files: nil)
        fields = []
        fields << ["title", nil, title] unless title.nil?
        fields << ["is_private", nil, is_private.to_s.downcase] unless is_private.nil?
        fields << ["scm", nil, scm] unless scm.nil?
        files&.each { |filename, content| fields << ["file", filename, content] }
        body_bytes, content_type = build_multipart(fields)
        request("POST", "/snippets", body_bytes: body_bytes, body_content_type: content_type)
      end

      def list_workspace_snippets(workspace:, role: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/snippets/#{workspace}",
          params: { "role" => role, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_workspace_snippet(workspace:, title: nil, is_private: nil, scm: nil, files: nil)
        fields = []
        fields << ["title", nil, title] unless title.nil?
        fields << ["is_private", nil, is_private.to_s.downcase] unless is_private.nil?
        fields << ["scm", nil, scm] unless scm.nil?
        files&.each { |filename, content| fields << ["file", filename, content] }
        body_bytes, content_type = build_multipart(fields)
        request("POST", "/snippets/#{workspace}", body_bytes: body_bytes, body_content_type: content_type)
      end

      def get_snippet(workspace:, encoded_id:)
        request("GET", "/snippets/#{workspace}/#{encoded_id}")
      end

      def update_snippet(workspace:, encoded_id:, title: nil, is_private: nil, files: nil)
        fields = []
        fields << ["title", nil, title] unless title.nil?
        fields << ["is_private", nil, is_private.to_s.downcase] unless is_private.nil?
        files&.each { |filename, content| fields << ["file", filename, content] }
        body_bytes, content_type = build_multipart(fields)
        request("PUT", "/snippets/#{workspace}/#{encoded_id}", body_bytes: body_bytes, body_content_type: content_type)
      end

      def delete_snippet(workspace:, encoded_id:)
        request("DELETE", "/snippets/#{workspace}/#{encoded_id}")
      end

      def list_snippet_comments(workspace:, encoded_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/snippets/#{workspace}/#{encoded_id}/comments",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_snippet_comment(workspace:, encoded_id:, content:)
        request(
          "POST",
          "/snippets/#{workspace}/#{encoded_id}/comments",
          body: { "content" => { "raw" => content } },
        )
      end

      def get_snippet_comment(workspace:, encoded_id:, comment_id:)
        request("GET", "/snippets/#{workspace}/#{encoded_id}/comments/#{comment_id}")
      end

      def update_snippet_comment(workspace:, encoded_id:, comment_id:, content:)
        request(
          "PUT",
          "/snippets/#{workspace}/#{encoded_id}/comments/#{comment_id}",
          body: { "content" => { "raw" => content } },
        )
      end

      def delete_snippet_comment(workspace:, encoded_id:, comment_id:)
        request("DELETE", "/snippets/#{workspace}/#{encoded_id}/comments/#{comment_id}")
      end

      def list_snippet_commits(workspace:, encoded_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/snippets/#{workspace}/#{encoded_id}/commits",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_snippet_commit(workspace:, encoded_id:, revision:)
        request("GET", "/snippets/#{workspace}/#{encoded_id}/commits/#{revision}")
      end

      def get_snippet_file(workspace:, encoded_id:, path:)
        request(
          "GET",
          "/snippets/#{workspace}/#{encoded_id}/files/#{path}",
          text_response: true,
        )
      end

      def get_snippet_watch(workspace:, encoded_id:)
        request("GET", "/snippets/#{workspace}/#{encoded_id}/watch")
      end

      def watch_snippet(workspace:, encoded_id:)
        request("PUT", "/snippets/#{workspace}/#{encoded_id}/watch")
      end

      def unwatch_snippet(workspace:, encoded_id:)
        request("DELETE", "/snippets/#{workspace}/#{encoded_id}/watch")
      end

      def list_snippet_watchers(workspace:, encoded_id:, page: nil, pagelen: nil)
        request(
          "GET",
          "/snippets/#{workspace}/#{encoded_id}/watchers",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_snippet_at_revision(workspace:, encoded_id:, node_id:)
        request("GET", "/snippets/#{workspace}/#{encoded_id}/#{node_id}")
      end

      def update_snippet_at_revision(workspace:, encoded_id:, node_id:, title: nil, is_private: nil, files: nil)
        fields = []
        fields << ["title", nil, title] unless title.nil?
        fields << ["is_private", nil, is_private.to_s.downcase] unless is_private.nil?
        files&.each { |filename, content| fields << ["file", filename, content] }
        body_bytes, content_type = build_multipart(fields)
        request("PUT", "/snippets/#{workspace}/#{encoded_id}/#{node_id}", body_bytes: body_bytes, body_content_type: content_type)
      end

      def delete_snippet_at_revision(workspace:, encoded_id:, node_id:)
        request("DELETE", "/snippets/#{workspace}/#{encoded_id}/#{node_id}")
      end

      def get_snippet_file_at_revision(workspace:, encoded_id:, node_id:, path:)
        request(
          "GET",
          "/snippets/#{workspace}/#{encoded_id}/#{node_id}/files/#{path}",
          text_response: true,
        )
      end

      def get_snippet_diff(workspace:, encoded_id:, revision:)
        request(
          "GET",
          "/snippets/#{workspace}/#{encoded_id}/#{revision}/diff",
          text_response: true,
        )
      end

      def get_snippet_patch(workspace:, encoded_id:, revision:)
        request(
          "GET",
          "/snippets/#{workspace}/#{encoded_id}/#{revision}/patch",
          text_response: true,
        )
      end
    end
  end
end
