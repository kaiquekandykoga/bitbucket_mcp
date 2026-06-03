# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for commits, commit comments, Code Insights reports/annotations, diffs and patches.
    module Commits
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY
      COMMIT = Schema.str("Commit hash (SHA1).")
      REPORT_ID = Schema.str("External report id (your unique identifier for the report).")
      ANNOTATION_ID = Schema.str("External annotation id (your unique identifier for the annotation).")
      SPEC = Schema.str('Commit SHA "abc123" or range "abc..def".')

      def all
        [
          ToolFactory.build(
            name: "get_commit",
            description: "Get a single commit by SHA.",
            properties: { workspace: WS, repository: REPO, commit: COMMIT },
            required: %w[workspace repository commit],
            read_only: true,
          ),
          ToolFactory.build(
            name: "approve_commit",
            description: "Approve a commit as the authenticated user.",
            properties: { workspace: WS, repository: REPO, commit: COMMIT },
            required: %w[workspace repository commit],
          ),
          ToolFactory.build(
            name: "unapprove_commit",
            description: "Remove the authenticated user's approval from a commit.",
            properties: { workspace: WS, repository: REPO, commit: COMMIT },
            required: %w[workspace repository commit],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_commit_comments",
            description: "List comments (global and inline) on a commit.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT,
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository commit],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_commit_comment",
            description: "Add a comment to a commit. Supports inline (file/line) comments and replies.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT,
              content: Schema.str("Comment body (markdown supported)."),
              parent_id: Schema.int("Reply to this comment id."),
              inline_path: Schema.str("File path to anchor an inline comment."),
              inline_to: Schema.int("Destination (new) line number."),
              inline_from: Schema.int("Source (old) line number.")
            },
            required: %w[workspace repository commit content],
          ),
          ToolFactory.build(
            name: "get_commit_comment",
            description: "Fetch a single commit comment.",
            properties: { workspace: WS, repository: REPO, commit: COMMIT, comment_id: Schema.int("Comment id.") },
            required: %w[workspace repository commit comment_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_commit_comment",
            description: "Update the content of a commit comment.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT,
              comment_id: Schema.int("Comment id."),
              content: Schema.str("New comment body (markdown supported).")
            },
            required: %w[workspace repository commit comment_id content],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_commit_comment",
            description: "Delete a commit comment (soft-delete if it has replies).",
            properties: { workspace: WS, repository: REPO, commit: COMMIT, comment_id: Schema.int("Comment id.") },
            required: %w[workspace repository commit comment_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_commit_reports",
            description: "List Code Insights reports for a commit.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository commit],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_commit_report",
            description: "Get a single Code Insights report.",
            properties: { workspace: WS, repository: REPO, commit: COMMIT, report_id: REPORT_ID },
            required: %w[workspace repository commit report_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_or_update_commit_report",
            description: "Create or update a Code Insights report.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT, report_id: REPORT_ID,
              title: Schema.str("Report title."),
              details: Schema.str("Longer description shown in the report."),
              external_id: Schema.str("Your own external id for the report."),
              reporter: Schema.str("Name of the tool/service that produced the report."),
              link: Schema.str("URL to the full report."),
              remote_link_enabled: Schema.bool("Whether the report links out to a remote URL."),
              logo_url: Schema.str("URL of a logo to display with the report."),
              report_type: Schema.str('"SECURITY" | "COVERAGE" | "TEST" | "BUG".'),
              result: Schema.str('"PASSED" | "FAILED" | "PENDING".'),
              data: Schema.array("Up to 10 report_data items (objects).")
            },
            required: %w[workspace repository commit report_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_commit_report",
            description: "Delete a Code Insights report.",
            properties: { workspace: WS, repository: REPO, commit: COMMIT, report_id: REPORT_ID },
            required: %w[workspace repository commit report_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_commit_report_annotations",
            description: "List annotations attached to a Code Insights report.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT, report_id: REPORT_ID,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository commit report_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "bulk_create_or_update_annotations",
            description: "Bulk create or update report annotations (max 1000).",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT, report_id: REPORT_ID,
              annotations: Schema.array("Annotation objects to create or update.")
            },
            required: %w[workspace repository commit report_id annotations],
          ),
          ToolFactory.build(
            name: "get_commit_report_annotation",
            description: "Get a single annotation.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT,
              report_id: REPORT_ID, annotation_id: ANNOTATION_ID
            },
            required: %w[workspace repository commit report_id annotation_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_or_update_commit_report_annotation",
            description: "Create or update a single annotation.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT,
              report_id: REPORT_ID, annotation_id: ANNOTATION_ID,
              external_id: Schema.str("Your own external id for the annotation."),
              annotation_type: Schema.str('"VULNERABILITY" | "CODE_SMELL" | "BUG".'),
              path: Schema.str("File path the annotation refers to."),
              line: Schema.int("Line number the annotation refers to."),
              summary: Schema.str("Short summary of the annotation."),
              details: Schema.str("Longer description of the annotation."),
              result: Schema.str('"PASSED" | "FAILED" | "SKIPPED" | "IGNORED".'),
              severity: Schema.str('"CRITICAL" | "HIGH" | "MEDIUM" | "LOW".'),
              link: Schema.str("URL with more detail about the annotation.")
            },
            required: %w[workspace repository commit report_id annotation_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_commit_report_annotation",
            description: "Delete a single annotation.",
            properties: {
              workspace: WS, repository: REPO, commit: COMMIT,
              report_id: REPORT_ID, annotation_id: ANNOTATION_ID
            },
            required: %w[workspace repository commit report_id annotation_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_commits",
            description: "List commits in a repository (topological / reverse-chronological).",
            properties: {
              workspace: WS, repository: REPO,
              include: Schema.strs('Refs to include (e.g. ["master"]).'),
              exclude: Schema.strs("Refs to exclude."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_commits_with_filter",
            description: "List commits via POST (use when include/exclude lists are too long for the URL).",
            properties: {
              workspace: WS, repository: REPO,
              include: Schema.strs("Refs to include."),
              exclude: Schema.strs("Refs to exclude."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
          ),
          ToolFactory.build(
            name: "list_commits_for_revision",
            description: "List commits reachable from a revision (SHA or ref).",
            properties: {
              workspace: WS, repository: REPO,
              revision: Schema.str("Revision (commit SHA or ref name)."),
              include: Schema.strs("Refs to include."),
              exclude: Schema.strs("Refs to exclude."),
              path: Schema.str("Limit to commits touching this path."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository revision],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_commits_for_revision_with_filter",
            description: "List commits reachable from a revision via POST (longer include/exclude lists).",
            properties: {
              workspace: WS, repository: REPO,
              revision: Schema.str("Revision (commit SHA or ref name)."),
              include: Schema.strs("Refs to include."),
              exclude: Schema.strs("Refs to exclude."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository revision],
          ),
          ToolFactory.build(
            name: "get_diff",
            description: "Get a raw git-style diff for a commit or range.",
            properties: {
              workspace: WS, repository: REPO, spec: SPEC,
              context: Schema.int("Lines of context (default 3)."),
              path: Schema.strs("Limit diff to one or more file paths."),
              ignore_whitespace: Schema.bool("Ignore whitespace-only changes."),
              binary: Schema.bool("Include binary file diffs."),
              renames: Schema.bool("Detect renames."),
              merge: Schema.bool("Diff against the merge base for a range."),
              topic: Schema.bool("Treat the range as a topic-branch diff.")
            },
            required: %w[workspace repository spec],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_diffstat",
            description: "Get per-file diff stats for a commit or range.",
            properties: {
              workspace: WS, repository: REPO, spec: SPEC,
              ignore_whitespace: Schema.bool("Ignore whitespace-only changes."),
              merge: Schema.bool("Diff against the merge base for a range."),
              path: Schema.strs("Limit stats to one or more file paths."),
              renames: Schema.bool("Detect renames."),
              topic: Schema.bool("Treat the range as a topic-branch diff."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository spec],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_file_conflicts",
            description: "List file conflicts for a commit spec.",
            properties: {
              workspace: WS, repository: REPO, spec: SPEC,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository spec],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_merge_base",
            description: "Get the best common ancestor between two commits.",
            properties: {
              workspace: WS, repository: REPO,
              revspec: Schema.str('Double-dot range (e.g. "abc..def").')
            },
            required: %w[workspace repository revspec],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_patch",
            description: "Get a raw patch (single commit or patch-series for a range).",
            properties: { workspace: WS, repository: REPO, spec: SPEC },
            required: %w[workspace repository spec],
            read_only: true,
          ),
        ]
      end
    end
  end
end
