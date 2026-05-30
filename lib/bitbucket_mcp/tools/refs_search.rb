# frozen_string_literal: true

module BitbucketMcp
  module Tools
    # Tool definitions for refs (branches and tags) and code search.
    module RefsSearch
      module_function

      WS = Schema::WORKSPACE
      REPO = Schema::REPOSITORY

      def all
        [
          ToolFactory.build(
            name: "list_refs",
            description: "List all refs (branches and tags) for a repository.",
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
            name: "list_branches",
            description: "List branches for a repository.",
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
            name: "create_branch",
            description: "Create a branch pointing at target_hash.",
            properties: {
              workspace: WS, repository: REPO,
              name: Schema.str("Branch name."),
              target_hash: Schema.str("Commit hash the branch should point at.")
            },
            required: %w[workspace repository name target_hash],
          ),
          ToolFactory.build(
            name: "get_branch",
            description: "Get a branch by name.",
            properties: { workspace: WS, repository: REPO, name: Schema.str("Branch name.") },
            required: %w[workspace repository name],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_branch",
            description: "Delete a branch.",
            properties: { workspace: WS, repository: REPO, name: Schema.str("Branch name.") },
            required: %w[workspace repository name],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "list_tags",
            description: "List tags for a repository.",
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
            name: "create_tag",
            description: "Create a tag.",
            properties: {
              workspace: WS, repository: REPO,
              name: Schema.str("Tag name."),
              target_hash: Schema.str("Commit hash the tag should point at."),
              message: Schema.str("Optional annotated tag message.")
            },
            required: %w[workspace repository name target_hash],
          ),
          ToolFactory.build(
            name: "get_tag",
            description: "Get a tag by name.",
            properties: { workspace: WS, repository: REPO, name: Schema.str("Tag name.") },
            required: %w[workspace repository name],
            read_only: true,
          ),
          ToolFactory.build(
            name: "delete_tag",
            description: "Delete a tag.",
            properties: { workspace: WS, repository: REPO, name: Schema.str("Tag name.") },
            required: %w[workspace repository name],
            destructive: true, idempotent: true
          ),
          ToolFactory.build(
            name: "search_workspace_code",
            description: "Search code across a workspace.",
            properties: {
              workspace: WS,
              search_query: Schema.str("Bitbucket code search query."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[workspace search_query],
            read_only: true,
          ),
          ToolFactory.build(
            name: "search_user_code",
            description: "Search code across a user's repositories.",
            properties: {
              selected_user: Schema.str("Account id or UUID of the user whose repositories to search."),
              search_query: Schema.str("Bitbucket code search query."),
              page: Schema::PAGE, pagelen: Schema::PAGELEN
            },
            required: %w[selected_user search_query],
            read_only: true,
          ),
        ]
      end
    end
  end
end
