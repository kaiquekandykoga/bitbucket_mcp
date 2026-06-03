# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for deployments and environments, downloads, and GPG keys.
    module DeploymentsDownloadsGpg
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY

      def all
        [
          ToolFactory.build(
            name: "list_deployments",
            description: "List deployments for a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_deployment",
            description: "Get a single deployment.",
            properties: { workspace: WS, repository: REPO, deployment_uuid: Schema.str("Deployment UUID.") },
            required: %w[workspace repository deployment_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_environments",
            description: "List deployment environments for a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_environment",
            description: "Create a deployment environment.",
            properties: {
              workspace: WS, repository: REPO,
              name: Schema.str("Environment name."),
              environment_type: Schema.str('Environment type, e.g. {"name": "Production"}.'),
              rank: Schema.int("Ordering position.")
            },
            required: %w[workspace repository name],
          ),
          ToolFactory.build(
            name: "get_environment",
            description: "Get a deployment environment by UUID.",
            properties: { workspace: WS, repository: REPO, environment_uuid: Schema.str("Environment UUID.") },
            required: %w[workspace repository environment_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_environment",
            description: "Update a deployment environment (POST .../changes).",
            properties: {
              workspace: WS, repository: REPO,
              environment_uuid: Schema.str("Environment UUID."),
              body: Schema.str("Change request body.")
            },
            required: %w[workspace repository environment_uuid],
          ),
          ToolFactory.build(
            name: "delete_environment",
            description: "Delete a deployment environment.",
            properties: { workspace: WS, repository: REPO, environment_uuid: Schema.str("Environment UUID.") },
            required: %w[workspace repository environment_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_downloads",
            description: "List downloads attached to a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "upload_download",
            description: "Upload one or more files to repository downloads.",
            properties: {
              workspace: WS, repository: REPO,
              files: Schema.str_map("Mapping of {filename: text_content}.")
            },
            required: %w[workspace repository files],
          ),
          ToolFactory.build(
            name: "get_download",
            description: "Get a download (returns raw bytes as text).",
            properties: { workspace: WS, repository: REPO, filename: Schema.str("Download file name.") },
            required: %w[workspace repository filename],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_download",
            description: "Delete a download artifact.",
            properties: { workspace: WS, repository: REPO, filename: Schema.str("Download file name.") },
            required: %w[workspace repository filename],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_user_gpg_keys",
            description: "List a user's GPG keys.",
            properties: {
              selected_user: Schema.str("Account UUID, username, or email of the user."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[selected_user],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_user_gpg_key",
            description: "Add a GPG key to a user.",
            properties: {
              selected_user: Schema.str("Account UUID, username, or email of the user."),
              key: Schema.str("Armored GPG public key."),
              name: Schema.str("Optional name for the key."),
            },
            required: %w[selected_user key],
          ),
          ToolFactory.build(
            name: "get_user_gpg_key",
            description: "Get a single GPG key by fingerprint.",
            properties: {
              selected_user: Schema.str("Account UUID, username, or email of the user."),
              fingerprint: Schema.str("GPG key fingerprint."),
            },
            required: %w[selected_user fingerprint],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_user_gpg_key",
            description: "Delete a GPG key.",
            properties: {
              selected_user: Schema.str("Account UUID, username, or email of the user."),
              fingerprint: Schema.str("GPG key fingerprint."),
            },
            required: %w[selected_user fingerprint],
            destructive: true, idempotent: true
          ),
        ]
      end
    end
  end
end
