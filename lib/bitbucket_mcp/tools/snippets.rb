# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for snippets, their files, comments, commits and watchers.
    module Snippets
      module_function

      WS = Schema.str("Workspace slug (the team or user that owns the snippet).")
      ENC_ID = Schema.str("Snippet encoded id.")
      ROLE = Schema.str('Filter by role: "owner", "contributor", or "member".')
      TITLE = Schema.str("Snippet title.")
      IS_PRIVATE = Schema.bool("Whether the snippet is private.")
      FILES = Schema.str_map("Mapping of {filename: text_content}.")

      def all
        [
          ToolFactory.build(
            name: "list_snippets",
            description: "List snippets visible to the caller.",
            properties: { role: ROLE, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_snippet",
            description: "Create a snippet (multipart upload).",
            properties: {
              title: TITLE, is_private: IS_PRIVATE,
              scm: Schema.str('Source control type, e.g. "git".'),
              files: FILES
            },
          ),
          ToolFactory.build(
            name: "list_workspace_snippets",
            description: "List snippets in a workspace.",
            properties: { workspace: WS, role: ROLE, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_workspace_snippet",
            description: "Create a snippet in a specific workspace.",
            properties: {
              workspace: WS, title: TITLE, is_private: IS_PRIVATE,
              scm: Schema.str('Source control type, e.g. "git".'),
              files: FILES
            },
            required: %w[workspace],
          ),
          ToolFactory.build(
            name: "get_snippet",
            description: "Get a snippet by its encoded id.",
            properties: { workspace: WS, encoded_id: ENC_ID },
            required: %w[workspace encoded_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_snippet",
            description: "Update a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID, title: TITLE, is_private: IS_PRIVATE, files: FILES },
            required: %w[workspace encoded_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_snippet",
            description: "Delete a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID },
            required: %w[workspace encoded_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_snippet_comments",
            description: "List comments on a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace encoded_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_snippet_comment",
            description: "Add a comment to a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID, content: Schema.str("Comment body (markdown supported).") },
            required: %w[workspace encoded_id content],
          ),
          ToolFactory.build(
            name: "get_snippet_comment",
            description: "Get a single snippet comment.",
            properties: { workspace: WS, encoded_id: ENC_ID, comment_id: Schema.int("Comment id.") },
            required: %w[workspace encoded_id comment_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_snippet_comment",
            description: "Update a snippet comment.",
            properties: {
              workspace: WS, encoded_id: ENC_ID,
              comment_id: Schema.int("Comment id."),
              content: Schema.str("New comment body (markdown supported).")
            },
            required: %w[workspace encoded_id comment_id content],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_snippet_comment",
            description: "Delete a snippet comment.",
            properties: { workspace: WS, encoded_id: ENC_ID, comment_id: Schema.int("Comment id.") },
            required: %w[workspace encoded_id comment_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_snippet_commits",
            description: "List commits in a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace encoded_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_snippet_commit",
            description: "Get a snippet commit.",
            properties: { workspace: WS, encoded_id: ENC_ID, revision: Schema.str("Commit revision (SHA1).") },
            required: %w[workspace encoded_id revision],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_snippet_file",
            description: "Get a file from the latest revision of a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID, path: Schema.str("File path within the snippet.") },
            required: %w[workspace encoded_id path],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_snippet_watch",
            description: "Check if the caller watches a snippet (404 if not).",
            properties: { workspace: WS, encoded_id: ENC_ID },
            required: %w[workspace encoded_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "watch_snippet",
            description: "Watch a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID },
            required: %w[workspace encoded_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "unwatch_snippet",
            description: "Unwatch a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID },
            required: %w[workspace encoded_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_snippet_watchers",
            description: "List users watching a snippet.",
            properties: { workspace: WS, encoded_id: ENC_ID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace encoded_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_snippet_at_revision",
            description: "Get a snippet at a specific revision.",
            properties: { workspace: WS, encoded_id: ENC_ID, node_id: Schema.str("Revision node id.") },
            required: %w[workspace encoded_id node_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_snippet_at_revision",
            description: "Update a snippet at a specific revision.",
            properties: {
              workspace: WS, encoded_id: ENC_ID,
              node_id: Schema.str("Revision node id."),
              title: TITLE, is_private: IS_PRIVATE, files: FILES
            },
            required: %w[workspace encoded_id node_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_snippet_at_revision",
            description: "Delete a snippet at a specific revision.",
            properties: { workspace: WS, encoded_id: ENC_ID, node_id: Schema.str("Revision node id.") },
            required: %w[workspace encoded_id node_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_snippet_file_at_revision",
            description: "Get a snippet file at a specific revision.",
            properties: {
              workspace: WS, encoded_id: ENC_ID,
              node_id: Schema.str("Revision node id."),
              path: Schema.str("File path within the snippet.")
            },
            required: %w[workspace encoded_id node_id path],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_snippet_diff",
            description: "Get the diff for a snippet revision.",
            properties: { workspace: WS, encoded_id: ENC_ID, revision: Schema.str("Commit revision (SHA1).") },
            required: %w[workspace encoded_id revision],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_snippet_patch",
            description: "Get the patch for a snippet revision.",
            properties: { workspace: WS, encoded_id: ENC_ID, revision: Schema.str("Commit revision (SHA1).") },
            required: %w[workspace encoded_id revision],
            read_only: true,
          ),
        ]
      end
    end
  end
end
