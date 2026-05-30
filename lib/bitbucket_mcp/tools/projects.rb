# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for workspace projects, default reviewers and project permissions.
    module Projects
      module_function

      WS = Schema::WORKSPACE
      PROJECT_KEY = Schema.str("Project key (the short identifier for the project).")

      def all
        [
          ToolFactory.build(
            name: "create_workspace_project",
            description: "Create a project in a workspace.",
            properties: {
              workspace: WS,
              key: Schema.str("Project key (the short identifier for the project)."),
              name: Schema.str("Project display name."),
              description: Schema.str("Optional project description."),
              is_private: Schema.bool("If true, the project is private."),
              avatar: Schema.object("Optional avatar object, e.g. {\"href\": \"...\"}."),
            },
            required: %w[workspace key name],
          ),
          ToolFactory.build(
            name: "update_workspace_project",
            description: "Update an existing project.",
            properties: {
              workspace: WS, project_key: PROJECT_KEY,
              key: Schema.str("New project key."),
              name: Schema.str("New project display name."),
              description: Schema.str("New project description."),
              is_private: Schema.bool("If true, the project is private."),
              avatar: Schema.object("Avatar object, e.g. {\"href\": \"...\"}.")
            },
            required: %w[workspace project_key],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_workspace_project",
            description: "Delete a project.",
            properties: { workspace: WS, project_key: PROJECT_KEY },
            required: %w[workspace project_key],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_project_default_reviewers",
            description: "List default reviewers for a project.",
            properties: { workspace: WS, project_key: PROJECT_KEY, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace project_key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_project_default_reviewer",
            description: "Get a project default reviewer.",
            properties: { workspace: WS, project_key: PROJECT_KEY, selected_user: Schema.str("Reviewer account id or UUID.") },
            required: %w[workspace project_key selected_user],
            read_only: true,
          ),
          ToolFactory.build(
            name: "add_project_default_reviewer",
            description: "Add a default reviewer to a project.",
            properties: { workspace: WS, project_key: PROJECT_KEY, selected_user: Schema.str("Reviewer account id or UUID.") },
            required: %w[workspace project_key selected_user],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "remove_project_default_reviewer",
            description: "Remove a default reviewer from a project.",
            properties: { workspace: WS, project_key: PROJECT_KEY, selected_user: Schema.str("Reviewer account id or UUID.") },
            required: %w[workspace project_key selected_user],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_project_group_permissions",
            description: "List explicit group permissions on a project.",
            properties: { workspace: WS, project_key: PROJECT_KEY, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace project_key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_project_group_permission",
            description: "Get a project group permission.",
            properties: { workspace: WS, project_key: PROJECT_KEY, group_slug: Schema.str("Group slug.") },
            required: %w[workspace project_key group_slug],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_project_group_permission",
            description: 'Grant or update a project group permission ("read"/"write"/"create-repo"/"admin").',
            properties: {
              workspace: WS, project_key: PROJECT_KEY,
              group_slug: Schema.str("Group slug."),
              permission: Schema.str('Permission level: "read", "write", "create-repo" or "admin".')
            },
            required: %w[workspace project_key group_slug permission],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_project_group_permission",
            description: "Delete a project group permission.",
            properties: { workspace: WS, project_key: PROJECT_KEY, group_slug: Schema.str("Group slug.") },
            required: %w[workspace project_key group_slug],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_project_user_permissions",
            description: "List explicit user permissions on a project.",
            properties: { workspace: WS, project_key: PROJECT_KEY, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace project_key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_project_user_permission",
            description: "Get a project user permission.",
            properties: { workspace: WS, project_key: PROJECT_KEY, selected_user_id: Schema.str("User account id or UUID.") },
            required: %w[workspace project_key selected_user_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_project_user_permission",
            description: 'Grant or update a project user permission ("read"/"write"/"create-repo"/"admin").',
            properties: {
              workspace: WS, project_key: PROJECT_KEY,
              selected_user_id: Schema.str("User account id or UUID."),
              permission: Schema.str('Permission level: "read", "write", "create-repo" or "admin".')
            },
            required: %w[workspace project_key selected_user_id permission],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_project_user_permission",
            description: "Delete a project user permission.",
            properties: { workspace: WS, project_key: PROJECT_KEY, selected_user_id: Schema.str("User account id or UUID.") },
            required: %w[workspace project_key selected_user_id],
            destructive: true, idempotent: true
          ),
        ]
      end
    end
  end
end
