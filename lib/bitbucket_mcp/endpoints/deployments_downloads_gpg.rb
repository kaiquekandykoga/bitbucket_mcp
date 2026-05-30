# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Deployments and environments, repository downloads, and user GPG keys.
    module DeploymentsDownloadsGpg
      def list_deployments(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/deployments",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_deployment(workspace:, repository:, deployment_uuid:)
        request("GET", "/repositories/#{workspace}/#{repository}/deployments/#{deployment_uuid}")
      end

      def list_environments(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/environments",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_environment(workspace:, repository:, name:, environment_type: nil, rank: nil)
        body = { "name" => name }
        body["environment_type"] = environment_type unless environment_type.nil?
        body["rank"] = rank unless rank.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/environments", body: body)
      end

      def get_environment(workspace:, repository:, environment_uuid:)
        request("GET", "/repositories/#{workspace}/#{repository}/environments/#{environment_uuid}")
      end

      def update_environment(workspace:, repository:, environment_uuid:, body: nil)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/environments/#{environment_uuid}/changes",
          body: body || {},
        )
      end

      def delete_environment(workspace:, repository:, environment_uuid:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/environments/#{environment_uuid}")
      end

      def list_downloads(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/downloads",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def upload_download(workspace:, repository:, files:)
        fields = []
        files.each do |filename, content|
          fields << ["files", filename, content]
        end
        body_bytes, content_type = build_multipart(fields)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/downloads",
          body_bytes: body_bytes,
          body_content_type: content_type,
        )
      end

      def get_download(workspace:, repository:, filename:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/downloads/#{filename}",
          text_response: true,
        )
      end

      def delete_download(workspace:, repository:, filename:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/downloads/#{filename}")
      end

      def list_user_gpg_keys(selected_user:, page: nil, pagelen: nil)
        request(
          "GET",
          "/users/#{selected_user}/gpg-keys",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_user_gpg_key(selected_user:, key:, name: nil)
        body = { "key" => key }
        body["name"] = name unless name.nil?
        request("POST", "/users/#{selected_user}/gpg-keys", body: body)
      end

      def get_user_gpg_key(selected_user:, fingerprint:)
        request("GET", "/users/#{selected_user}/gpg-keys/#{fingerprint}")
      end

      def delete_user_gpg_key(selected_user:, fingerprint:)
        request("DELETE", "/users/#{selected_user}/gpg-keys/#{fingerprint}")
      end
    end
  end
end
