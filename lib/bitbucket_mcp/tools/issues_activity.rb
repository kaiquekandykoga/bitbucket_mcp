# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for issue attachments, changes, comments, votes and watches.
    module IssuesActivity
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY
      ISSUE_ID = Schema.int("Issue id.")

      def all
        [
          ToolFactory.build(
            name: "list_issue_attachments",
            description: "List attachments on an issue.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository issue_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "upload_issue_attachment",
            description: "Upload attachments to an issue.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              files: Schema.str_map("Mapping of {filename: text_content}.")
            },
            required: %w[workspace repository issue_id files],
          ),
          ToolFactory.build(
            name: "get_issue_attachment",
            description: "Download an attachment (raw bytes as text).",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              path: Schema.str("Attachment file name/path.")
            },
            required: %w[workspace repository issue_id path],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_issue_attachment",
            description: "Delete an issue attachment.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              path: Schema.str("Attachment file name/path.")
            },
            required: %w[workspace repository issue_id path],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_issue_changes",
            description: "List the change log entries for an issue.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository issue_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_issue_change",
            description: "Apply a change to an issue (transition, assignee, etc.).",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              changes: Schema.object('Mapping of field to {"new": "value"}, e.g. {"state": {"new": "resolved"}}.'),
              message: Schema.str("Optional comment message in markdown.")
            },
            required: %w[workspace repository issue_id],
          ),
          ToolFactory.build(
            name: "get_issue_change",
            description: "Get a single change log entry.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              change_id: Schema.int("Change log entry id.")
            },
            required: %w[workspace repository issue_id change_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_issue_comments",
            description: "List comments on an issue.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository issue_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_issue_comment",
            description: "Add a comment to an issue.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              content: Schema.str("Comment body (markdown supported).")
            },
            required: %w[workspace repository issue_id content],
          ),
          ToolFactory.build(
            name: "get_issue_comment",
            description: "Get a single issue comment.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              comment_id: Schema.int("Comment id.")
            },
            required: %w[workspace repository issue_id comment_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_issue_comment",
            description: "Edit an issue comment.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              comment_id: Schema.int("Comment id."),
              content: Schema.str("New comment body (markdown supported).")
            },
            required: %w[workspace repository issue_id comment_id content],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_issue_comment",
            description: "Delete an issue comment.",
            properties: {
              workspace: WS, repository: REPO, issue_id: ISSUE_ID,
              comment_id: Schema.int("Comment id.")
            },
            required: %w[workspace repository issue_id comment_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_issue_vote",
            description: "Check if the caller has voted for an issue (404 if not).",
            properties: { workspace: WS, repository: REPO, issue_id: ISSUE_ID },
            required: %w[workspace repository issue_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "vote_for_issue",
            description: "Vote for an issue.",
            properties: { workspace: WS, repository: REPO, issue_id: ISSUE_ID },
            required: %w[workspace repository issue_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "unvote_issue",
            description: "Retract the caller's vote on an issue.",
            properties: { workspace: WS, repository: REPO, issue_id: ISSUE_ID },
            required: %w[workspace repository issue_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_issue_watch",
            description: "Check if the caller is watching an issue (404 if not).",
            properties: { workspace: WS, repository: REPO, issue_id: ISSUE_ID },
            required: %w[workspace repository issue_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "watch_issue",
            description: "Start watching an issue.",
            properties: { workspace: WS, repository: REPO, issue_id: ISSUE_ID },
            required: %w[workspace repository issue_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "unwatch_issue",
            description: "Stop watching an issue.",
            properties: { workspace: WS, repository: REPO, issue_id: ISSUE_ID },
            required: %w[workspace repository issue_id],
            destructive: true, idempotent: true
          ),
        ]
      end
    end
  end
end
