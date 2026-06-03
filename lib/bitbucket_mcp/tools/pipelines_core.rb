# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for pipelines: runs and steps, configuration, schedules,
    # SSH key pair and known hosts.
    module PipelinesCore
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY
      PIPELINE_UUID = Schema.str("Pipeline UUID.")
      STEP_UUID = Schema.str("Pipeline step UUID.")
      SCHEDULE_UUID = Schema.str("Pipeline schedule UUID.")
      KNOWN_HOST_UUID = Schema.str("Known host UUID.")

      def all
        [
          ToolFactory.build(
            name: "list_pipelines",
            description: "List pipelines for a repository.",
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
            name: "create_pipeline",
            description: "Trigger a pipeline.",
            properties: {
              workspace: WS, repository: REPO,
              target: Schema.object('Pipeline target, e.g. {"type": "pipeline_ref_target", "ref_type": "branch", "ref_name": "main", "selector": {"type": "default"}}.'),
              variables: Schema.array('Pipeline variables, e.g. [{"key": "FOO", "value": "BAR", "secured": false}, ...].')
            },
            required: %w[workspace repository target],
          ),
          ToolFactory.build(
            name: "get_pipeline",
            description: "Get a pipeline by UUID.",
            properties: { workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID },
            required: %w[workspace repository pipeline_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "stop_pipeline",
            description: "Stop a running pipeline.",
            properties: { workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID },
            required: %w[workspace repository pipeline_uuid],
          ),
          ToolFactory.build(
            name: "list_pipeline_steps",
            description: "List the steps of a pipeline.",
            properties: {
              workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository pipeline_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pipeline_step",
            description: "Get a single pipeline step.",
            properties: { workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID, step_uuid: STEP_UUID },
            required: %w[workspace repository pipeline_uuid step_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pipeline_step_log",
            description: "Get the full text log for a pipeline step.",
            properties: { workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID, step_uuid: STEP_UUID },
            required: %w[workspace repository pipeline_uuid step_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pipeline_step_container_log",
            description: "Get a container-specific log for a pipeline step.",
            properties: {
              workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID, step_uuid: STEP_UUID,
              log_uuid: Schema.str("Log UUID.")
            },
            required: %w[workspace repository pipeline_uuid step_uuid log_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_pipeline_step_test_reports",
            description: "List test reports for a pipeline step.",
            properties: { workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID, step_uuid: STEP_UUID },
            required: %w[workspace repository pipeline_uuid step_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_pipeline_step_test_cases",
            description: "List test cases for a pipeline step.",
            properties: { workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID, step_uuid: STEP_UUID },
            required: %w[workspace repository pipeline_uuid step_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_pipeline_step_test_case_reasons",
            description: "List failure reasons for a test case.",
            properties: {
              workspace: WS, repository: REPO, pipeline_uuid: PIPELINE_UUID, step_uuid: STEP_UUID,
              test_case_uuid: Schema.str("Test case UUID.")
            },
            required: %w[workspace repository pipeline_uuid step_uuid test_case_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pipeline_config",
            description: "Get pipelines configuration for a repository.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pipeline_config",
            description: "Update pipelines configuration.",
            properties: {
              workspace: WS, repository: REPO,
              enabled: Schema.bool("Whether pipelines are enabled for the repository."),
              repository_pipeline: Schema.object("Repository-level pipeline configuration object.")
            },
            required: %w[workspace repository],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "update_pipeline_build_number",
            description: "Set the next pipeline build number for a repository.",
            properties: {
              workspace: WS, repository: REPO,
              next_build_number: Schema.int("The next build number to assign.")
            },
            required: %w[workspace repository next_build_number],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_pipeline_schedules",
            description: "List pipeline schedules.",
            properties: {
              workspace: WS, repository: REPO,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_pipeline_schedule",
            description: "Create a pipeline schedule.",
            properties: {
              workspace: WS, repository: REPO,
              target: Schema.object("Pipeline target object (ref type, ref name, selector)."),
              cron_pattern: Schema.str("Cron expression controlling when the schedule runs."),
              enabled: Schema.bool("Whether the schedule is enabled.")
            },
            required: %w[workspace repository target cron_pattern],
          ),
          ToolFactory.build(
            name: "get_pipeline_schedule",
            description: "Get a pipeline schedule.",
            properties: { workspace: WS, repository: REPO, schedule_uuid: SCHEDULE_UUID },
            required: %w[workspace repository schedule_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pipeline_schedule",
            description: "Update a pipeline schedule.",
            properties: {
              workspace: WS, repository: REPO, schedule_uuid: SCHEDULE_UUID,
              enabled: Schema.bool("Whether the schedule is enabled."),
              cron_pattern: Schema.str("Cron expression controlling when the schedule runs."),
              target: Schema.object("Pipeline target object (ref type, ref name, selector).")
            },
            required: %w[workspace repository schedule_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_pipeline_schedule",
            description: "Delete a pipeline schedule.",
            properties: { workspace: WS, repository: REPO, schedule_uuid: SCHEDULE_UUID },
            required: %w[workspace repository schedule_uuid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_pipeline_schedule_executions",
            description: "List execution history for a pipeline schedule.",
            properties: {
              workspace: WS, repository: REPO, schedule_uuid: SCHEDULE_UUID,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository schedule_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_pipeline_ssh_key_pair",
            description: "Get the pipeline SSH key pair (public key only).",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pipeline_ssh_key_pair",
            description: "Set the pipeline SSH key pair.",
            properties: {
              workspace: WS, repository: REPO,
              public_key: Schema.str("SSH public key."),
              private_key: Schema.str("SSH private key.")
            },
            required: %w[workspace repository public_key private_key],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_pipeline_ssh_key_pair",
            description: "Delete the pipeline SSH key pair.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_pipeline_known_hosts",
            description: "List known SSH hosts for pipelines.",
            properties: {
              workspace: WS, repository: REPO,
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_pipeline_known_host",
            description: "Add a known SSH host.",
            properties: {
              workspace: WS, repository: REPO,
              hostname: Schema.str("Hostname of the known host."),
              public_key: Schema.object("Public key object (key type and key data).")
            },
            required: %w[workspace repository hostname public_key],
          ),
          ToolFactory.build(
            name: "get_pipeline_known_host",
            description: "Get a known SSH host.",
            properties: { workspace: WS, repository: REPO, known_host_uuid: KNOWN_HOST_UUID },
            required: %w[workspace repository known_host_uuid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_pipeline_known_host",
            description: "Update a known SSH host.",
            properties: {
              workspace: WS, repository: REPO, known_host_uuid: KNOWN_HOST_UUID,
              hostname: Schema.str("Hostname of the known host."),
              public_key: Schema.object("Public key object (key type and key data).")
            },
            required: %w[workspace repository known_host_uuid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_pipeline_known_host",
            description: "Delete a known SSH host.",
            properties: { workspace: WS, repository: REPO, known_host_uuid: KNOWN_HOST_UUID },
            required: %w[workspace repository known_host_uuid],
            destructive: true, idempotent: true
          ),
        ]
      end
    end
  end
end
