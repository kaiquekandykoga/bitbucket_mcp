# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for pipeline variables, caches, runners, and OIDC discovery.
    module PipelinesVars
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY
      VARIABLE_UUID = Schema.str("Pipeline variable UUID.")
      KEY = Schema.str("Variable name (key).")
      VALUE = Schema.str("Variable value.")
      SECURED = Schema.bool("If true, the value is stored encrypted and hidden in the UI/API.")
      RUNNER_UUID = Schema.str("Pipeline runner UUID.")
      RUNNER_NAME = Schema.str("Runner name.")
      LABELS = Schema.strs("Optional list of runner labels.")
      ENV_UUID = Schema.str("Deployment environment UUID.")
      SELECTED_USER = Schema.str("User account UUID or username.")

      def all
        [
          ToolFactory.build(
            name: "list_pipeline_variables",
            description: "List pipeline variables for a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_pipeline_variable",
            description: "Create a pipeline variable.",
            properties: { workspace: WS, repository: REPO, key: KEY, value: VALUE, secured: SECURED },
            required: %w[workspace repository key value],
          ),
          ToolFactory.build(
            name: "get_pipeline_variable",
            description: "Get a pipeline variable.",
            properties: { workspace: WS, repository: REPO, variable_uuid: VARIABLE_UUID },
            required: %w[workspace repository variable_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pipeline_variable",
            description: "Update a pipeline variable.",
            properties: { workspace: WS, repository: REPO, variable_uuid: VARIABLE_UUID, key: KEY, value: VALUE, secured: SECURED },
            required: %w[workspace repository variable_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_pipeline_variable",
            description: "Delete a pipeline variable.",
            properties: { workspace: WS, repository: REPO, variable_uuid: VARIABLE_UUID },
            required: %w[workspace repository variable_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_pipeline_caches",
            description: "List pipeline caches.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_pipeline_caches",
            description: "Delete all caches (or by name).",
            properties: { workspace: WS, repository: REPO, name: Schema.str("Optional cache name to delete; omit to delete all.") },
            required: %w[workspace repository],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "delete_pipeline_cache",
            description: "Delete a single pipeline cache.",
            properties: { workspace: WS, repository: REPO, cache_uuid: Schema.str("Pipeline cache UUID.") },
            required: %w[workspace repository cache_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_pipeline_cache_content_uri",
            description: "Get the temporary download URI for a pipeline cache.",
            properties: { workspace: WS, repository: REPO, cache_uuid: Schema.str("Pipeline cache UUID.") },
            required: %w[workspace repository cache_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_repository_pipeline_runners",
            description: "List repository-scoped pipeline runners.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_repository_pipeline_runner",
            description: "Create a repository-scoped runner.",
            properties: { workspace: WS, repository: REPO, name: RUNNER_NAME, labels: LABELS },
            required: %w[workspace repository name],
          ),
          ToolFactory.build(
            name: "get_repository_pipeline_runner",
            description: "Get a repository-scoped runner.",
            properties: { workspace: WS, repository: REPO, runner_uuid: RUNNER_UUID },
            required: %w[workspace repository runner_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_repository_pipeline_runner",
            description: "Update a repository-scoped runner.",
            properties: { workspace: WS, repository: REPO, runner_uuid: RUNNER_UUID, name: RUNNER_NAME, labels: LABELS },
            required: %w[workspace repository runner_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_repository_pipeline_runner",
            description: "Delete a repository-scoped runner.",
            properties: { workspace: WS, repository: REPO, runner_uuid: RUNNER_UUID },
            required: %w[workspace repository runner_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_workspace_pipeline_runners",
            description: "List workspace-scoped pipeline runners.",
            properties: { workspace: WS, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_workspace_pipeline_runner",
            description: "Create a workspace-scoped runner.",
            properties: { workspace: WS, name: RUNNER_NAME, labels: LABELS },
            required: %w[workspace name],
          ),
          ToolFactory.build(
            name: "get_workspace_pipeline_runner",
            description: "Get a workspace-scoped runner.",
            properties: { workspace: WS, runner_uuid: RUNNER_UUID },
            required: %w[workspace runner_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_workspace_pipeline_runner",
            description: "Update a workspace-scoped runner.",
            properties: { workspace: WS, runner_uuid: RUNNER_UUID, name: RUNNER_NAME, labels: LABELS },
            required: %w[workspace runner_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_workspace_pipeline_runner",
            description: "Delete a workspace-scoped runner.",
            properties: { workspace: WS, runner_uuid: RUNNER_UUID },
            required: %w[workspace runner_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_workspace_pipeline_variables",
            description: "List workspace-level pipeline variables.",
            properties: { workspace: WS, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_workspace_pipeline_variable",
            description: "Create a workspace-level pipeline variable.",
            properties: { workspace: WS, key: KEY, value: VALUE, secured: SECURED },
            required: %w[workspace key value],
          ),
          ToolFactory.build(
            name: "get_workspace_pipeline_variable",
            description: "Get a workspace-level pipeline variable.",
            properties: { workspace: WS, variable_uuid: VARIABLE_UUID },
            required: %w[workspace variable_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_workspace_pipeline_variable",
            description: "Update a workspace-level pipeline variable.",
            properties: { workspace: WS, variable_uuid: VARIABLE_UUID, key: KEY, value: VALUE, secured: SECURED },
            required: %w[workspace variable_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_workspace_pipeline_variable",
            description: "Delete a workspace-level pipeline variable.",
            properties: { workspace: WS, variable_uuid: VARIABLE_UUID },
            required: %w[workspace variable_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_user_pipeline_variables",
            description: "List a user's account-level pipeline variables.",
            properties: { selected_user: SELECTED_USER, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[selected_user],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_user_pipeline_variable",
            description: "Create a user account-level pipeline variable.",
            properties: { selected_user: SELECTED_USER, key: KEY, value: VALUE, secured: SECURED },
            required: %w[selected_user key value],
          ),
          ToolFactory.build(
            name: "get_user_pipeline_variable",
            description: "Get a user account-level pipeline variable.",
            properties: { selected_user: SELECTED_USER, variable_uuid: VARIABLE_UUID },
            required: %w[selected_user variable_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_user_pipeline_variable",
            description: "Update a user account-level pipeline variable.",
            properties: { selected_user: SELECTED_USER, variable_uuid: VARIABLE_UUID, key: KEY, value: VALUE, secured: SECURED },
            required: %w[selected_user variable_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_user_pipeline_variable",
            description: "Delete a user account-level pipeline variable.",
            properties: { selected_user: SELECTED_USER, variable_uuid: VARIABLE_UUID },
            required: %w[selected_user variable_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_deployment_variables",
            description: "List deployment variables for an environment.",
            properties: { workspace: WS, repository: REPO, environment_uuid: ENV_UUID, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository environment_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_deployment_variable",
            description: "Create a deployment variable on an environment.",
            properties: { workspace: WS, repository: REPO, environment_uuid: ENV_UUID, key: KEY, value: VALUE, secured: SECURED },
            required: %w[workspace repository environment_uuid key value],
          ),
          ToolFactory.build(
            name: "update_deployment_variable",
            description: "Update a deployment variable.",
            properties: {
              workspace: WS, repository: REPO, environment_uuid: ENV_UUID, variable_uuid: VARIABLE_UUID,
              key: KEY, value: VALUE, secured: SECURED
            },
            required: %w[workspace repository environment_uuid variable_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_deployment_variable",
            description: "Delete a deployment variable.",
            properties: { workspace: WS, repository: REPO, environment_uuid: ENV_UUID, variable_uuid: VARIABLE_UUID },
            required: %w[workspace repository environment_uuid variable_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_pipelines_oidc_configuration",
            description: "Get the OIDC discovery document for a workspace's pipelines.",
            properties: { workspace: WS },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pipelines_oidc_keys",
            description: "Get the OIDC JWKS keys for a workspace's pipelines.",
            properties: { workspace: WS },
            required: %w[workspace],
            read_only: true,
          ),
        ]
      end
    end
  end
end
