# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for repositories, forks, webhooks, permissions, settings and source.
    module Repositories
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY

      def all
        [
          ToolFactory.build(
            name: "list_public_repositories",
            description: "List public repositories (deprecated; prefer workspace-scoped variant).",
            properties: {
              after: Schema.str("Filter to repositories created on or after this ISO-8601 timestamp / UUID cursor."),
              role: Schema.str("Filter by the caller's role on the repository."),
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_repositories",
            description: "List repositories in a workspace.",
            properties: {
              workspace: WS,
              role: Schema.str("Filter by the caller's role on the repository."),
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace],
            read_only: true,
          ),
          ToolFactory.build(
            name: "get_repository",
            description: "Get a repository by slug.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_repository",
            description: "Create a repository at the given workspace/repo_slug.",
            properties: {
              workspace: WS, repository: REPO,
              scm: Schema.str('Always "git".'),
              name: Schema.str("Display name of the repository."),
              description: Schema.str("Repository description."),
              is_private: Schema.bool("Whether the repository is private."),
              fork_policy: Schema.str('"allow_forks" | "no_public_forks" | "no_forks".'),
              language: Schema.str("Primary programming language."),
              has_issues: Schema.bool("Enable the issue tracker."),
              has_wiki: Schema.bool("Enable the wiki."),
              project_key: Schema.str('Workspace project key (e.g. "MARS").'),
              mainbranch_name: Schema.str("Name of the default branch.")
            },
            required: %w[workspace repository],
          ),
          ToolFactory.build(
            name: "update_repository",
            description: "Update repository metadata (may also create if absent).",
            properties: {
              workspace: WS, repository: REPO,
              name: Schema.str("Display name of the repository."),
              description: Schema.str("Repository description."),
              is_private: Schema.bool("Whether the repository is private."),
              fork_policy: Schema.str('"allow_forks" | "no_public_forks" | "no_forks".'),
              language: Schema.str("Primary programming language."),
              has_issues: Schema.bool("Enable the issue tracker."),
              has_wiki: Schema.bool("Enable the wiki."),
              project_key: Schema.str("Workspace project key."),
              mainbranch_name: Schema.str("Name of the default branch.")
            },
            required: %w[workspace repository],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "delete_repository",
            description: "Delete a repository. Pass redirect_to to send visitors to a friendly URL.",
            properties: {
              workspace: WS, repository: REPO,
              redirect_to: Schema.str("URL to redirect visitors to after deletion.")
            },
            required: %w[workspace repository],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_file_history",
            description: "List commits that modified a file.",
            properties: {
              workspace: WS, repository: REPO,
              commit: Schema.str("Commit hash or branch/tag name to start from."),
              path: Schema.str("Repo-relative file path."),
              renames: Schema.str('"true" or "false"; whether to follow renames (default "true").'),
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository commit path],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_repository_forks",
            description: "List forks of a repository.",
            properties: {
              workspace: WS, repository: REPO,
              role: Schema.str("Filter by the caller's role on the fork."),
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "fork_repository",
            description: "Fork a repository.",
            properties: {
              workspace: WS, repository: REPO,
              name: Schema.str("Name for the new fork. Required when forking to the same workspace."),
              destination_workspace: Schema.str("Workspace slug for the new fork (defaults to source)."),
              is_private: Schema.bool("Whether the fork is private."),
              description: Schema.str("Description for the new fork."),
              project_key: Schema.str("Workspace project key for the new fork."),
              fork_policy: Schema.str('"allow_forks" | "no_public_forks" | "no_forks".'),
              language: Schema.str("Primary programming language.")
            },
            required: %w[workspace repository],
          ),
          ToolFactory.build(
            name: "list_repository_webhooks",
            description: "List webhooks for a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_repository_webhook",
            description: "Create a repository-level webhook.",
            properties: {
              workspace: WS, repository: REPO,
              url: Schema.str("URL Bitbucket will POST events to."),
              events: Schema.strs('Event keys to subscribe to (e.g. "repo:push").'),
              description: Schema.str("Human-readable webhook description."),
              active: Schema.bool("Whether the webhook is active."),
              secret: Schema.str("Secret used to sign webhook payloads.")
            },
            required: %w[workspace repository url events],
          ),
          ToolFactory.build(
            name: "delete_repository_webhook",
            description: "Delete a repository webhook.",
            properties: { workspace: WS, repository: REPO, uid: Schema.str("Webhook uid.") },
            required: %w[workspace repository uid],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_repository_webhook",
            description: "Get a repository webhook.",
            properties: { workspace: WS, repository: REPO, uid: Schema.str("Webhook uid.") },
            required: %w[workspace repository uid],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_repository_webhook",
            description: "Update a repository webhook.",
            properties: {
              workspace: WS, repository: REPO,
              uid: Schema.str("Webhook uid."),
              url: Schema.str("URL Bitbucket will POST events to."),
              events: Schema.strs('Event keys to subscribe to (e.g. "repo:push").'),
              description: Schema.str("Human-readable webhook description."),
              active: Schema.bool("Whether the webhook is active."),
              secret: Schema.str("Secret used to sign webhook payloads.")
            },
            required: %w[workspace repository uid],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "get_repository_override_settings",
            description: "Get inheritance overrides on repository settings.",
            properties: { workspace: WS, repository: REPO },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "set_repository_override_settings",
            description: "Set inheritance overrides on repository settings (admin only).",
            properties: {
              workspace: WS, repository: REPO,
              settings: Schema.object("Map of setting name to boolean (as the override value).")
            },
            required: %w[workspace repository settings],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_repository_group_permissions",
            description: "List explicit group permissions on a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_repository_group_permission",
            description: "Delete an explicit group permission.",
            properties: { workspace: WS, repository: REPO, group_slug: Schema.str("Group slug.") },
            required: %w[workspace repository group_slug],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_repository_group_permission",
            description: "Get an explicit group permission.",
            properties: { workspace: WS, repository: REPO, group_slug: Schema.str("Group slug.") },
            required: %w[workspace repository group_slug],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_repository_group_permission",
            description: 'Grant or update an explicit group permission ("read"/"write"/"admin").',
            properties: {
              workspace: WS, repository: REPO,
              group_slug: Schema.str("Group slug."),
              permission: Schema.str('Permission level: "read", "write" or "admin".')
            },
            required: %w[workspace repository group_slug permission],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "list_repository_user_permissions",
            description: "List explicit user permissions on a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_repository_user_permission",
            description: "Delete an explicit user permission.",
            properties: { workspace: WS, repository: REPO, selected_user_id: Schema.str("Account id or UUID of the user.") },
            required: %w[workspace repository selected_user_id],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "get_repository_user_permission",
            description: "Get an explicit user permission.",
            properties: { workspace: WS, repository: REPO, selected_user_id: Schema.str("Account id or UUID of the user.") },
            required: %w[workspace repository selected_user_id],
            read_only: true,
          ),
          ToolFactory.build(
            name: "update_repository_user_permission",
            description: 'Grant or update an explicit user permission ("read"/"write"/"admin").',
            properties: {
              workspace: WS, repository: REPO,
              selected_user_id: Schema.str("Account id or UUID of the user."),
              permission: Schema.str('Permission level: "read", "write" or "admin".')
            },
            required: %w[workspace repository selected_user_id permission],
            idempotent: true,
          ),
          ToolFactory.build(
            name: "get_repository_root_src",
            description: "Get the root src listing of the repository main branch.",
            properties: {
              workspace: WS, repository: REPO,
              format: Schema.str('Pass "meta" to receive JSON metadata instead of contents.')
            },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "create_src_commit",
            description: "Create a commit by uploading/deleting files (multipart upload).",
            properties: {
              workspace: WS, repository: REPO,
              message: Schema.str("Commit message."),
              author: Schema.str('e.g. "Name <email@host>".'),
              parents: Schema.str("Parent commit SHA1."),
              branch: Schema.str("Branch to commit on. Pass a fresh name to create a new branch."),
              files_to_add: Schema.str_map("Mapping of repo-relative path to file contents (text)."),
              files_to_delete: Schema.strs("Repo-relative paths to remove in this commit.")
            },
            required: %w[workspace repository],
          ),
          ToolFactory.build(
            name: "get_repository_src",
            description: "Get a file or directory at a specific commit.",
            properties: {
              workspace: WS, repository: REPO,
              commit: Schema.str("Commit hash or branch/tag name."),
              path: Schema.str("Repo-relative file or directory path."),
              format: Schema.str('"meta" for JSON metadata, "rendered" for rendered HTML markup.'),
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              max_depth: Schema.int("For directory listings, recursion depth (default 1).")
            },
            required: %w[workspace repository commit path],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_repository_watchers",
            description: "List users watching a repository.",
            properties: { workspace: WS, repository: REPO, page: Schema::PAGE, pagelen: Schema::PAGELEN },
            required: %w[workspace repository],
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_user_repository_permissions",
            description: "List the caller's repository permissions (deprecated; prefer workspace-scoped variant).",
            properties: {
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            read_only: true,
          ),
          ToolFactory.build(
            name: "list_user_workspace_repository_permissions",
            description: "List the caller's repository permissions within a workspace.",
            properties: {
              workspace: WS,
              q: Schema.str("BBQL filter query."),
              sort: Schema.str("Field to sort by."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace],
            read_only: true,
          ),
        ]
      end
    end
  end
end
