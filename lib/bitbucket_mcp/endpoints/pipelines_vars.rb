# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Pipeline variables, caches, runners (repository/workspace), workspace/user/deployment
    # variables, and pipelines OIDC discovery.
    module PipelinesVars
      def list_pipeline_variables(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines_config/variables",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_pipeline_variable(workspace:, repository:, key:, value:, secured: nil)
        body = { "key" => key, "value" => value }
        body["secured"] = secured unless secured.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/pipelines_config/variables", body: body)
      end

      def get_pipeline_variable(workspace:, repository:, variable_uuid:)
        request("GET", "/repositories/#{workspace}/#{repository}/pipelines_config/variables/#{variable_uuid}")
      end

      def update_pipeline_variable(workspace:, repository:, variable_uuid:, key: nil, value: nil, secured: nil)
        body = {}
        body["key"] = key unless key.nil?
        body["value"] = value unless value.nil?
        body["secured"] = secured unless secured.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pipelines_config/variables/#{variable_uuid}",
          body: body,
        )
      end

      def delete_pipeline_variable(workspace:, repository:, variable_uuid:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/pipelines_config/variables/#{variable_uuid}")
      end

      def list_pipeline_caches(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines-config/caches",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def delete_pipeline_caches(workspace:, repository:, name: nil)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/pipelines-config/caches",
          params: { "name" => name },
        )
      end

      def delete_pipeline_cache(workspace:, repository:, cache_uuid:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/pipelines-config/caches/#{cache_uuid}")
      end

      def get_pipeline_cache_content_uri(workspace:, repository:, cache_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines-config/caches/#{cache_uuid}/content-uri",
        )
      end

      def list_repository_pipeline_runners(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines-config/runners",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_repository_pipeline_runner(workspace:, repository:, name:, labels: nil)
        body = { "name" => name }
        body["labels"] = labels unless labels.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/pipelines-config/runners", body: body)
      end

      def get_repository_pipeline_runner(workspace:, repository:, runner_uuid:)
        request("GET", "/repositories/#{workspace}/#{repository}/pipelines-config/runners/#{runner_uuid}")
      end

      def update_repository_pipeline_runner(workspace:, repository:, runner_uuid:, name: nil, labels: nil)
        body = {}
        body["name"] = name unless name.nil?
        body["labels"] = labels unless labels.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pipelines-config/runners/#{runner_uuid}",
          body: body,
        )
      end

      def delete_repository_pipeline_runner(workspace:, repository:, runner_uuid:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/pipelines-config/runners/#{runner_uuid}")
      end

      def list_workspace_pipeline_runners(workspace:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/pipelines-config/runners",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_workspace_pipeline_runner(workspace:, name:, labels: nil)
        body = { "name" => name }
        body["labels"] = labels unless labels.nil?
        request("POST", "/workspaces/#{workspace}/pipelines-config/runners", body: body)
      end

      def get_workspace_pipeline_runner(workspace:, runner_uuid:)
        request("GET", "/workspaces/#{workspace}/pipelines-config/runners/#{runner_uuid}")
      end

      def update_workspace_pipeline_runner(workspace:, runner_uuid:, name: nil, labels: nil)
        body = {}
        body["name"] = name unless name.nil?
        body["labels"] = labels unless labels.nil?
        request("PUT", "/workspaces/#{workspace}/pipelines-config/runners/#{runner_uuid}", body: body)
      end

      def delete_workspace_pipeline_runner(workspace:, runner_uuid:)
        request("DELETE", "/workspaces/#{workspace}/pipelines-config/runners/#{runner_uuid}")
      end

      def list_workspace_pipeline_variables(workspace:, page: nil, pagelen: nil)
        request(
          "GET",
          "/workspaces/#{workspace}/pipelines-config/variables",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_workspace_pipeline_variable(workspace:, key:, value:, secured: nil)
        body = { "key" => key, "value" => value }
        body["secured"] = secured unless secured.nil?
        request("POST", "/workspaces/#{workspace}/pipelines-config/variables", body: body)
      end

      def get_workspace_pipeline_variable(workspace:, variable_uuid:)
        request("GET", "/workspaces/#{workspace}/pipelines-config/variables/#{variable_uuid}")
      end

      def update_workspace_pipeline_variable(workspace:, variable_uuid:, key: nil, value: nil, secured: nil)
        body = {}
        body["key"] = key unless key.nil?
        body["value"] = value unless value.nil?
        body["secured"] = secured unless secured.nil?
        request("PUT", "/workspaces/#{workspace}/pipelines-config/variables/#{variable_uuid}", body: body)
      end

      def delete_workspace_pipeline_variable(workspace:, variable_uuid:)
        request("DELETE", "/workspaces/#{workspace}/pipelines-config/variables/#{variable_uuid}")
      end

      def list_user_pipeline_variables(selected_user:, page: nil, pagelen: nil)
        request(
          "GET",
          "/users/#{selected_user}/pipelines_config/variables",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_user_pipeline_variable(selected_user:, key:, value:, secured: nil)
        body = { "key" => key, "value" => value }
        body["secured"] = secured unless secured.nil?
        request("POST", "/users/#{selected_user}/pipelines_config/variables", body: body)
      end

      def get_user_pipeline_variable(selected_user:, variable_uuid:)
        request("GET", "/users/#{selected_user}/pipelines_config/variables/#{variable_uuid}")
      end

      def update_user_pipeline_variable(selected_user:, variable_uuid:, key: nil, value: nil, secured: nil)
        body = {}
        body["key"] = key unless key.nil?
        body["value"] = value unless value.nil?
        body["secured"] = secured unless secured.nil?
        request("PUT", "/users/#{selected_user}/pipelines_config/variables/#{variable_uuid}", body: body)
      end

      def delete_user_pipeline_variable(selected_user:, variable_uuid:)
        request("DELETE", "/users/#{selected_user}/pipelines_config/variables/#{variable_uuid}")
      end

      def list_deployment_variables(workspace:, repository:, environment_uuid:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/deployments_config/environments/#{environment_uuid}/variables",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_deployment_variable(workspace:, repository:, environment_uuid:, key:, value:, secured: nil)
        body = { "key" => key, "value" => value }
        body["secured"] = secured unless secured.nil?
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/deployments_config/environments/#{environment_uuid}/variables",
          body: body,
        )
      end

      def update_deployment_variable(workspace:, repository:, environment_uuid:, variable_uuid:, key: nil, value: nil, secured: nil)
        body = {}
        body["key"] = key unless key.nil?
        body["value"] = value unless value.nil?
        body["secured"] = secured unless secured.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/deployments_config/environments/#{environment_uuid}/variables/#{variable_uuid}",
          body: body,
        )
      end

      def delete_deployment_variable(workspace:, repository:, environment_uuid:, variable_uuid:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/deployments_config/environments/#{environment_uuid}/variables/#{variable_uuid}",
        )
      end

      def get_pipelines_oidc_configuration(workspace:)
        request("GET", "/workspaces/#{workspace}/pipelines-config/identity/oidc/.well-known/openid-configuration")
      end

      def get_pipelines_oidc_keys(workspace:)
        request("GET", "/workspaces/#{workspace}/pipelines-config/identity/oidc/keys.json")
      end
    end
  end
end
