# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for default reviewers, branch restrictions and branching models.
    module ReviewersBranching
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY
      DEVELOPMENT = Schema.object("Configuration for the development branch (e.g. {\"use_mainbranch\": true} or {\"name\": \"develop\"}).")
      PRODUCTION = Schema.object("Configuration for the production branch (or {\"enabled\": false} to disable).")
      BRANCH_TYPES = Schema.array('List of {"kind": ..., "enabled": ..., "prefix": ...} entries.')

      def all
        [
          ToolFactory.build(
            name: "list_default_reviewers",
            description: "List default reviewers configured on a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_effective_default_reviewers",
            description: "List effective default reviewers (repo + inherited from project).",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_default_reviewer",
            description: "Get a default reviewer.",
            properties: {
              workspace: WS, repository: REPO,
              target_username: Schema.str("UUID or Atlassian Account ID of the reviewer.")
            },
            required: %w[workspace repository target_username],
            read_only: true,
          ),
          ToolFactory.build(
            name: "add_default_reviewer",
            description: "Add a user to repository default reviewers.",
            properties: {
              workspace: WS, repository: REPO,
              target_username: Schema.str("UUID or Atlassian Account ID of the reviewer.")
            },
            required: %w[workspace repository target_username],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "remove_default_reviewer",
            description: "Remove a user from repository default reviewers.",
            properties: {
              workspace: WS, repository: REPO,
              target_username: Schema.str("UUID or Atlassian Account ID of the reviewer.")
            },
            required: %w[workspace repository target_username],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_branch_restrictions",
            description: "List branch restrictions for a repository.",
            properties: {
              workspace: WS, repository: REPO,
              kind: Schema.str('Restriction kind to filter by (e.g. "push", "force", "delete", "require_approvals_to_merge").'),
              pattern: Schema.str("Branch pattern to filter by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_branch_restriction",
            description: "Create a branch restriction.",
            properties: {
              workspace: WS, repository: REPO,
              kind: Schema.str('Restriction kind (e.g. "push", "force", "delete", "require_approvals_to_merge").'),
              pattern: Schema.str("Glob pattern matching the branches."),
              branch_match_kind: Schema.str('"glob" or "branching_model".'),
              branch_type: Schema.str('Branch type when branch_match_kind is "branching_model".'),
              users: Schema.strs("UUIDs of exempt users."),
              groups: Schema.array("Group references (with slug/owner) that are exempt."),
              value: Schema.int("Integer value (e.g. number of required approvals).")
            },
            required: %w[workspace repository kind],
          ),
          ToolFactory.build(
            name: "get_branch_restriction",
            description: "Get a branch restriction by id.",
            properties: { workspace: WS, repository: REPO, id: Schema.int("Branch restriction id.") },
            required: %w[workspace repository id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_branch_restriction",
            description: "Update a branch restriction.",
            properties: {
              workspace: WS, repository: REPO, id: Schema.int("Branch restriction id."),
              kind: Schema.str('Restriction kind (e.g. "push", "force", "delete", "require_approvals_to_merge").'),
              pattern: Schema.str("Glob pattern matching the branches."),
              branch_match_kind: Schema.str('"glob" or "branching_model".'),
              branch_type: Schema.str('Branch type when branch_match_kind is "branching_model".'),
              users: Schema.strs("UUIDs of exempt users."),
              groups: Schema.array("Group references (with slug/owner) that are exempt."),
              value: Schema.int("Integer value (e.g. number of required approvals).")
            },
            required: %w[workspace repository id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_branch_restriction",
            description: "Delete a branch restriction.",
            properties: { workspace: WS, repository: REPO, id: Schema.int("Branch restriction id.") },
            required: %w[workspace repository id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_branching_model",
            description: "Get the branching model for a repository.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_effective_branching_model",
            description: "Get the effective branching model (after project inheritance).",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_branching_model_settings",
            description: "Get branching model settings for a repository.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_branching_model_settings",
            description: "Update branching model settings.",
            properties: {
              workspace: WS, repository: REPO,
              development: DEVELOPMENT, production: PRODUCTION, branch_types: BRANCH_TYPES
            },
            required: %w[workspace repository],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "get_project_branching_model",
            description: "Get the project-level branching model.",
            properties: { workspace: WS, project_key: Schema.str("Project key.") },
            required: %w[workspace project_key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_project_branching_model_settings",
            description: "Get the project-level branching model settings.",
            properties: { workspace: WS, project_key: Schema.str("Project key.") },
            required: %w[workspace project_key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_project_branching_model_settings",
            description: "Update project-level branching model settings.",
            properties: {
              workspace: WS, project_key: Schema.str("Project key."),
              development: DEVELOPMENT, production: PRODUCTION, branch_types: BRANCH_TYPES
            },
            required: %w[workspace project_key],
            idempotent: true,
          ),
        ]
      end
    end
  end
end
