# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for pull requests and their comments, tasks and merges.
    module PullRequests
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY
      PR_ID = Schema.int("Pull request id.")

      def all
        [
          ToolFactory.build(
            name: "list_pull_requests_for_commit",
            description: "List pull requests that contain a given commit.",
            properties: {
              workspace: WS, repository: REPO,
              commit: Schema.str("Commit hash (SHA1)."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository commit],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_pull_requests",
            description: "List pull requests for a repository.",
            properties: {
              workspace: WS, repository: REPO,
              state: Schema.str("Filter by state (OPEN, MERGED, DECLINED, SUPERSEDED); comma-separate for multiple."),
              q: Schema.str('BBQL query, e.g. \'state="OPEN" AND author.uuid="..."\'.'),
              sort: Schema.str("Field to sort by, e.g. '-updated_on'."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_pull_request",
            description: "Create a pull request in Bitbucket Cloud.",
            properties: {
              workspace: WS, repository: REPO,
              title: Schema.str("Pull request title."),
              source_branch: Schema.str("Branch containing the new changes."),
              destination_branch: Schema.str('Branch to merge into. Defaults to "main".'),
              description: Schema.str("Optional description (markdown supported)."),
              close_source_branch: Schema.bool("If true, the source branch is deleted after merge."),
              reviewers: Schema.strs("Optional list of reviewer UUIDs.")
            },
            required: %w[workspace repository title source_branch],
          ),
          ToolFactory.build(
            name: "list_repository_pull_request_activity",
            description: "List activity (approvals, comments, etc.) across all PRs in a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pull_request",
            description: "Fetch a single pull request by id.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pull_request",
            description: "Update a pull request's title, description, destination, or reviewers.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              title: Schema.str("New title."),
              description: Schema.str("New description (markdown supported)."),
              destination_branch: Schema.str("New destination branch name."),
              reviewers: Schema.strs("Replacement list of reviewer UUIDs.")
            },
            required: %w[workspace repository pull_request_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_pull_request_activity",
            description: "List activity (approvals, comments, etc.) for a single PR.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "approve_pull_request",
            description: "Approve a pull request as the authenticated user.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "unapprove_pull_request",
            description: "Remove the authenticated user's approval from a PR.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "request_changes",
            description: "Mark a PR as requesting changes.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "remove_request_changes",
            description: "Remove the authenticated user's request-changes status from a PR.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_pull_request_comments",
            description: "List comments on a pull request.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_pull_request_comment",
            description: "Add a comment to a pull request. Supports inline (file/line) comments and replies.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              content: Schema.str("Comment body (markdown supported)."),
              parent_id: Schema.int("Id of the comment this is a reply to."),
              inline_path: Schema.str("File path for an inline comment."),
              inline_to: Schema.int("Line number in the new version of the file."),
              inline_from: Schema.int("Line number in the old version of the file.")
            },
            required: %w[workspace repository pull_request_id content],
          ),
          ToolFactory.build(
            name: "get_pull_request_comment",
            description: "Fetch a single pull request comment by id.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, comment_id: Schema.int("Comment id.") },
            required: %w[workspace repository pull_request_id comment_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pull_request_comment",
            description: "Edit the body of a pull request comment.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              comment_id: Schema.int("Comment id."),
              content: Schema.str("New comment body (markdown supported).")
            },
            required: %w[workspace repository pull_request_id comment_id content],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_pull_request_comment",
            description: "Delete a pull request comment.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, comment_id: Schema.int("Comment id.") },
            required: %w[workspace repository pull_request_id comment_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "resolve_pull_request_comment",
            description: "Mark a pull request comment thread as resolved.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, comment_id: Schema.int("Comment id.") },
            required: %w[workspace repository pull_request_id comment_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "reopen_pull_request_comment",
            description: "Reopen (unresolve) a pull request comment thread.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, comment_id: Schema.int("Comment id.") },
            required: %w[workspace repository pull_request_id comment_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_pull_request_commits",
            description: "List the commits that are part of a pull request.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_pull_request_conflicts",
            description: "List merge conflicts for a pull request.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "decline_pull_request",
            description: "Decline (reject) a pull request.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
          ),
          ToolFactory.build(
            name: "get_pull_request_diff",
            description: "Get the raw unified diff for a pull request.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pull_request_diffstat",
            description: "Get the diffstat (per-file change summary) for a pull request.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "merge_pull_request",
            description: "Merge a pull request.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              message: Schema.str("Optional merge commit message."),
              close_source_branch: Schema.bool("Delete the source branch after merging."),
              merge_strategy: Schema.str('One of "merge_commit", "squash", "fast_forward".'),
              async_: Schema.bool("If true, perform the merge asynchronously and return a task id.")
            },
            required: %w[workspace repository pull_request_id],
          ),
          ToolFactory.build(
            name: "get_merge_task_status",
            description: "Check the status of an asynchronous merge task.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, task_id: Schema.str("Merge task id.") },
            required: %w[workspace repository pull_request_id task_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pull_request_patch",
            description: "Get the raw patch (mailbox format) for a pull request.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_pull_request_statuses",
            description: "List commit/build statuses associated with a pull request.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_pull_request_tasks",
            description: "List tasks on a pull request.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository pull_request_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_pull_request_task",
            description: "Create a task on a pull request, optionally attached to a comment.",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              content: Schema.str("Task description."),
              comment_id: Schema.int("Id of the comment to attach the task to."),
              pending: Schema.bool("Whether the task starts in the pending (unresolved) state.")
            },
            required: %w[workspace repository pull_request_id content],
          ),
          ToolFactory.build(
            name: "get_pull_request_task",
            description: "Fetch a single pull request task by id.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, task_id: Schema.int("Task id.") },
            required: %w[workspace repository pull_request_id task_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pull_request_task",
            description: "Update a pull request task's content or state (RESOLVED/UNRESOLVED).",
            properties: {
              workspace: WS, repository: REPO, pull_request_id: PR_ID,
              task_id: Schema.int("Task id."),
              content: Schema.str("New task description."),
              state: Schema.str('Task state, e.g. "RESOLVED" or "UNRESOLVED".')
            },
            required: %w[workspace repository pull_request_id task_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_pull_request_task",
            description: "Delete a pull request task.",
            properties: { workspace: WS, repository: REPO, pull_request_id: PR_ID, task_id: Schema.int("Task id.") },
            required: %w[workspace repository pull_request_id task_id],
            destructive: true, idempotent: true
          ),
        ]
      end
    end
  end
end
