# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # The authenticated user, public user profiles, SSH keys and webhook event types.
    module UsersSshHooks
      def current_user
        request("GET", "/user")
      end

      def list_user_ssh_keys(selected_user:, page: nil, pagelen: nil)
        request(
          "GET",
          "/users/#{selected_user}/ssh-keys",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_user_ssh_key(selected_user:, key:, label: nil)
        body = { "key" => key }
        body["label"] = label unless label.nil?
        request("POST", "/users/#{selected_user}/ssh-keys", body: body)
      end

      def get_user_ssh_key(selected_user:, key_id:)
        request("GET", "/users/#{selected_user}/ssh-keys/#{key_id}")
      end

      def update_user_ssh_key(selected_user:, key_id:, label: nil, key: nil)
        body = {}
        body["label"] = label unless label.nil?
        body["key"] = key unless key.nil?
        request("PUT", "/users/#{selected_user}/ssh-keys/#{key_id}", body: body)
      end

      def delete_user_ssh_key(selected_user:, key_id:)
        request("DELETE", "/users/#{selected_user}/ssh-keys/#{key_id}")
      end

      def get_user(selected_user:)
        request("GET", "/users/#{selected_user}")
      end

      def list_user_emails(page: nil, pagelen: nil)
        request(
          "GET",
          "/user/emails",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_user_email(email:)
        request("GET", "/user/emails/#{email}")
      end

      def list_hook_event_subjects
        request("GET", "/hook_events")
      end

      def list_hook_events(subject_type:)
        request("GET", "/hook_events/#{subject_type}")
      end
    end
  end
end
