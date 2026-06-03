# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for the authenticated user, public profiles, SSH keys and webhook event types.
    module UsersSshHooks
      module_function

      USER = Schema.str("Account: username, UUID, or Atlassian Account ID.")

      def all
        [
          ToolFactory.build(
            name: "current_user",
            description: "Return the authenticated Bitbucket user. Useful as a connectivity smoke test before calling other tools.",
            properties: {},
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_user_ssh_keys",
            description: "List a user's SSH keys.",
            properties: { selected_user: USER, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[selected_user],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_user_ssh_key",
            description: "Add an SSH key to a user.",
            properties: {
              selected_user: USER,
              key: Schema.str("The public key value."),
              label: Schema.str("Optional label for the key."),
            },
            required: %w[selected_user key],
          ),
          ToolFactory.build(
            name: "get_user_ssh_key",
            description: "Get a user's SSH key.",
            properties: { selected_user: USER, key_id: Schema.str("SSH key id (UUID).") },
            required: %w[selected_user key_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_user_ssh_key",
            description: "Update a user's SSH key.",
            properties: {
              selected_user: USER,
              key_id: Schema.str("SSH key id (UUID)."),
              label: Schema.str("New label for the key."),
              key: Schema.str("New public key value."),
            },
            required: %w[selected_user key_id],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_user_ssh_key",
            description: "Delete a user's SSH key.",
            properties: { selected_user: USER, key_id: Schema.str("SSH key id (UUID).") },
            required: %w[selected_user key_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_user",
            description: "Get a public Bitbucket user by username, UUID, or Atlassian Account ID.",
            properties: { selected_user: USER },
            required: %w[selected_user],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_user_emails",
            description: "List email addresses for the authenticated user.",
            properties: { page: Schema::PAGE, pagelen: Schema::PAGELEN },
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_user_email",
            description: "Get an email address by value (authenticated user only).",
            properties: { email: Schema.str("Email address to look up.") },
            required: %w[email],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_hook_event_subjects",
            description: "List the subject types that can be subscribed to via webhooks.",
            properties: {},
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_hook_events",
            description: "List all webhook event keys for a subject type.",
            properties: { subject_type: Schema.str('"workspace", "user", or "repository".') },
            required: %w[subject_type],
            read_only: true,
          ),
        ]
      end
    end
  end
end
