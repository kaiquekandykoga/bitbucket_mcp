# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for commit build statuses and repository/project deploy keys.
    module StatusesDeployKeys
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY

      def all
        [
          ToolFactory.build(
            name: "list_commit_statuses",
            description: "List build statuses attached to a commit.",
            properties: {
              workspace: WS, repository: REPO,
              commit: Schema.str("Commit hash (SHA1)."),
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository commit],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_commit_build_status",
            description: "Create a build status for a commit.",
            properties: {
              workspace: WS, repository: REPO,
              commit: Schema.str("Commit hash (SHA1)."),
              key: Schema.str("Unique key for the status (e.g. CI job name)."),
              state: Schema.str('"INPROGRESS", "SUCCESSFUL", "FAILED", or "STOPPED".'),
              url: Schema.str("Link to the external build."),
              name: Schema.str("Human-readable status name."),
              description: Schema.str("Optional status description."),
              refname: Schema.str("Branch name (for branch-specific statuses).")
            },
            required: %w[workspace repository commit key state url],
          ),
          ToolFactory.build(
            name: "get_commit_build_status",
            description: "Get a build status by key.",
            properties: {
              workspace: WS, repository: REPO,
              commit: Schema.str("Commit hash (SHA1)."),
              key: Schema.str("Unique key for the status.")
            },
            required: %w[workspace repository commit key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_commit_build_status",
            description: "Update an existing build status.",
            properties: {
              workspace: WS, repository: REPO,
              commit: Schema.str("Commit hash (SHA1)."),
              key: Schema.str("Unique key for the status."),
              state: Schema.str('"INPROGRESS", "SUCCESSFUL", "FAILED", or "STOPPED".'),
              url: Schema.str("Link to the external build."),
              name: Schema.str("Human-readable status name."),
              description: Schema.str("Optional status description."),
              refname: Schema.str("Branch name (for branch-specific statuses).")
            },
            required: %w[workspace repository commit key],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_deploy_keys",
            description: "List deploy keys for a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_deploy_key",
            description: "Add a deploy key to a repository.",
            properties: {
              workspace: WS, repository: REPO,
              key: Schema.str("The SSH public key."),
              label: Schema.str("Optional label for the key.")
            },
            required: %w[workspace repository key],
          ),
          ToolFactory.build(
            name: "get_deploy_key",
            description: "Get a repository deploy key.",
            properties: { workspace: WS, repository: REPO, key_id: Schema.str("Deploy key id.") },
            required: %w[workspace repository key_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_deploy_key",
            description: "Update a repository deploy key.",
            properties: {
              workspace: WS, repository: REPO,
              key_id: Schema.str("Deploy key id."),
              label: Schema.str("New label for the key."),
              key: Schema.str("The SSH public key.")
            },
            required: %w[workspace repository key_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_deploy_key",
            description: "Delete a repository deploy key.",
            properties: { workspace: WS, repository: REPO, key_id: Schema.str("Deploy key id.") },
            required: %w[workspace repository key_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_project_deploy_keys",
            description: "List deploy keys for a project.",
            properties: {
              workspace: WS,
              project_key: Schema.str("Project key."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace project_key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_project_deploy_key",
            description: "Add a deploy key to a project.",
            properties: {
              workspace: WS,
              project_key: Schema.str("Project key."),
              key: Schema.str("The SSH public key."),
              label: Schema.str("Optional label for the key."),
            },
            required: %w[workspace project_key key],
          ),
          ToolFactory.build(
            name: "get_project_deploy_key",
            description: "Get a project deploy key.",
            properties: {
              workspace: WS,
              project_key: Schema.str("Project key."),
              key_id: Schema.str("Deploy key id."),
            },
            required: %w[workspace project_key key_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_project_deploy_key",
            description: "Delete a project deploy key.",
            properties: {
              workspace: WS,
              project_key: Schema.str("Project key."),
              key_id: Schema.str("Deploy key id."),
            },
            required: %w[workspace project_key key_id],
            destructive: true, idempotent: true
          ),
        ]
      end
    end
  end
end
