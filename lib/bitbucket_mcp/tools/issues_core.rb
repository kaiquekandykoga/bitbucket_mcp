# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for issue tracker components, milestones, versions, issues and import/export.
    module IssuesCore
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY

      KIND = Schema.str('Issue kind: "bug", "enhancement", "proposal" or "task".')
      PRIORITY = Schema.str('Issue priority: "trivial", "minor", "major", "critical" or "blocker".')
      ISSUE_STATE = Schema.str('Issue state: "new", "open", "resolved", "on hold", "invalid", "duplicate", "wontfix" or "closed".')
      COMPONENT = Schema.str("Component name.")
      MILESTONE = Schema.str("Milestone name.")
      VERSION = Schema.str("Version name.")
      ASSIGNEE = Schema.str("Assignee user UUID.")

      def all
        [
          ToolFactory.build(
            name: "list_components",
            description: "List issue tracker components.",
            properties: {
              workspace: WS, repository: REPO,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_component",
            description: "Get a single issue tracker component.",
            properties: { workspace: WS, repository: REPO, component_id: Schema.int("Component id.") },
            required: %w[workspace repository component_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_milestones",
            description: "List issue tracker milestones.",
            properties: {
              workspace: WS, repository: REPO,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_milestone",
            description: "Get a single issue tracker milestone.",
            properties: { workspace: WS, repository: REPO, milestone_id: Schema.int("Milestone id.") },
            required: %w[workspace repository milestone_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_versions",
            description: "List issue tracker versions.",
            properties: {
              workspace: WS, repository: REPO,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_version",
            description: "Get a single issue tracker version.",
            properties: { workspace: WS, repository: REPO, version_id: Schema.int("Version id.") },
            required: %w[workspace repository version_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_issues",
            description: "List issues for a repository.",
            properties: {
              workspace: WS, repository: REPO,
              q: Schema.str("BBQL filter query."), sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_issue",
            description: "Create an issue.",
            properties: {
              workspace: WS, repository: REPO,
              title: Schema.str("Issue title."),
              content: Schema.str("Issue description (markdown supported)."),
              kind: KIND, priority: PRIORITY, state: ISSUE_STATE,
              component: COMPONENT, milestone: MILESTONE, version: VERSION, assignee: ASSIGNEE
            },
            required: %w[workspace repository title],
          ),
          ToolFactory.build(
            name: "get_issue",
            description: "Get a single issue.",
            properties: { workspace: WS, repository: REPO, issue_id: Schema.int("Issue id.") },
            required: %w[workspace repository issue_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_issue",
            description: "Update an issue.",
            properties: {
              workspace: WS, repository: REPO, issue_id: Schema.int("Issue id."),
              title: Schema.str("New issue title."),
              content: Schema.str("New issue description (markdown supported)."),
              kind: KIND, priority: PRIORITY, state: ISSUE_STATE,
              component: COMPONENT, milestone: MILESTONE, version: VERSION, assignee: ASSIGNEE
            },
            required: %w[workspace repository issue_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_issue",
            description: "Delete an issue.",
            properties: { workspace: WS, repository: REPO, issue_id: Schema.int("Issue id.") },
            required: %w[workspace repository issue_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "export_issues",
            description: "Start an export of the repository issues (returns a task).",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
          ),
          ToolFactory.build(
            name: "get_issue_export",
            description: "Download a previously-generated issue export zip.",
            properties: {
              workspace: WS, repository: REPO,
              repo_name: Schema.str("Repository name used in the export filename."),
              task_id: Schema.str("Export task id.")
            },
            required: %w[workspace repository repo_name task_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_issue_import_status",
            description: "Get the status of the most recent issue import.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "import_issues",
            description: "Start an issue import.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
          ),
        ]
      end
    end
  end
end
