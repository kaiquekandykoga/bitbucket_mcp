# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for workspaces, their members, permissions, projects and webhooks.
    module Workspaces
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY

      def all
        [
          ToolFactory.build(
            name: "list_user_workspace_permissions",
            description: "List the caller's workspace memberships (deprecated; use list_user_workspaces).",
            properties: {
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_user_workspaces",
            description: "List workspaces accessible to the caller.",
            properties: {
              sort: Schema.str('Only "slug" is supported.'),
              administrator: Schema.bool("If true, restrict to workspaces the caller administers."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_user_workspace_permission",
            description: "Get the caller's effective role on a workspace.",
            properties: { workspace: WS },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_workspaces",
            description: "List workspaces for the caller (deprecated; use list_user_workspaces).",
            properties: {
              role: Schema.str('Filter by role ("owner", "collaborator", "member").'),
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_workspace",
            description: "Get a workspace by slug or UUID.",
            properties: { workspace: WS },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_workspace_webhooks",
            description: "List webhook subscriptions on a workspace.",
            properties: { workspace: WS, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_workspace_webhook",
            description: "Create a workspace-level webhook.",
            properties: {
              workspace: WS,
              url: Schema.str("Endpoint that Bitbucket will POST events to."),
              events: Schema.strs('Event keys (e.g. ["repo:push", "pullrequest:created"]).'),
              description: Schema.str("Optional description for the webhook."),
              active: Schema.bool("Whether the webhook is active."),
              secret: Schema.str("Used to sign payloads with HMAC."),
            },
            required: %w[workspace url events],
          ),
          ToolFactory.build(
            name: "delete_workspace_webhook",
            description: "Delete a workspace webhook by UUID.",
            properties: { workspace: WS, uid: Schema.str("Webhook UUID.") },
            required: %w[workspace uid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_workspace_webhook",
            description: "Get a workspace webhook by UUID.",
            properties: { workspace: WS, uid: Schema.str("Webhook UUID.") },
            required: %w[workspace uid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_workspace_webhook",
            description: "Update a workspace webhook.",
            properties: {
              workspace: WS, uid: Schema.str("Webhook UUID."),
              url: Schema.str("Endpoint that Bitbucket will POST events to."),
              events: Schema.strs('Event keys (e.g. ["repo:push", "pullrequest:created"]).'),
              description: Schema.str("Optional description for the webhook."),
              active: Schema.bool("Whether the webhook is active."),
              secret: Schema.str("Used to sign payloads with HMAC.")
            },
            required: %w[workspace uid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_workspace_members",
            description: "List members of a workspace.",
            properties: {
              workspace: WS,
              q: Schema.str("BBQL filter (admin/integration callers can filter by user.email)."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_workspace_member",
            description: "Get a single workspace membership.",
            properties: {
              workspace: WS,
              member: Schema.str("UUID or Atlassian Account ID of the user."),
            },
            required: %w[workspace member],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_workspace_permissions",
            description: "List per-user permissions in a workspace.",
            properties: {
              workspace: WS,
              q: Schema.str("BBQL filter query."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_workspace_repository_permissions",
            description: "List effective repository permissions for every user across the workspace.",
            properties: {
              workspace: WS,
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_workspace_repository_permissions_for_repo",
            description: "List per-user repository permissions for a single repository.",
            properties: {
              workspace: WS, repository: REPO,
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_workspace_projects",
            description: "List projects in a workspace.",
            properties: { workspace: WS, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_workspace_project",
            description: "Get a project by its key.",
            properties: { workspace: WS, project_key: Schema.str("Project key.") },
            required: %w[workspace project_key],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_workspace_user_pull_requests",
            description: "List pull requests across a workspace authored by a user.",
            properties: {
              workspace: WS,
              selected_user: Schema.str("Username, UUID, or Atlassian Account ID."),
              state: Schema.str("One state or a list of states (OPEN, MERGED, DECLINED, SUPERSEDED)."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace selected_user],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_workspace_gpg_key",
            description: "Get the workspace system GPG public key(s).",
            properties: { workspace: WS },
            required: %w[workspace],
            read_only: true,
          ),
        ]
      end
    end
  end
end
