# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Refs (branches and tags) and workspace/user code search.
    module RefsSearch
      def list_refs(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/refs",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def list_branches(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/refs/branches",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_branch(workspace:, repository:, name:, target_hash:)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/refs/branches",
          body: { "name" => name, "target" => { "hash" => target_hash } },
        )
      end

      def get_branch(workspace:, repository:, name:)
        request("GET", "/repositories/#{workspace}/#{repository}/refs/branches/#{name}")
      end

      def delete_branch(workspace:, repository:, name:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/refs/branches/#{name}")
      end

      def list_tags(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/refs/tags",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_tag(workspace:, repository:, name:, target_hash:, message: nil)
        body = { "name" => name, "target" => { "hash" => target_hash } }
        body["message"] = message unless message.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/refs/tags", body: body)
      end

      def get_tag(workspace:, repository:, name:)
        request("GET", "/repositories/#{workspace}/#{repository}/refs/tags/#{name}")
      end

      def delete_tag(workspace:, repository:, name:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/refs/tags/#{name}")
      end

      def search_workspace_code(workspace:, search_query:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/search/code",
          params: { "search_query" => search_query, "page" => page, "pagelen" => pagelen },
        )
      end

      def search_user_code(selected_user:, search_query:, page: nil, pagelen: nil)
        request(
          "GET",
          "/users/#{selected_user}/search/code",
          params: { "search_query" => search_query, "page" => page, "pagelen" => pagelen },
        )
      end
    end
  end
end
