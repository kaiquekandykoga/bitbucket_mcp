# frozen_string_literal: true

module BitbucketMcp
  module Endpoints
    # Pipelines: runs and steps, configuration, schedules, SSH key pair and known hosts.
    module PipelinesCore
      def list_pipelines(workspace:, repository:, q: nil, sort: nil, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines",
          params: { "q" => q, "sort" => sort, "page" => page, "pagelen" => pagelen },
        )
      end

      def create_pipeline(workspace:, repository:, target:, variables: nil)
        body = { "target" => target }
        body["variables"] = variables unless variables.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/pipelines", body: body)
      end

      def get_pipeline(workspace:, repository:, pipeline_uuid:)
        request("GET", "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}")
      end

      def stop_pipeline(workspace:, repository:, pipeline_uuid:)
        request("POST", "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/stopPipeline")
      end

      def list_pipeline_steps(workspace:, repository:, pipeline_uuid:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/steps",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_pipeline_step(workspace:, repository:, pipeline_uuid:, step_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/steps/#{step_uuid}",
        )
      end

      def get_pipeline_step_log(workspace:, repository:, pipeline_uuid:, step_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/steps/#{step_uuid}/log",
          text_response: true,
        )
      end

      def get_pipeline_step_container_log(workspace:, repository:, pipeline_uuid:, step_uuid:, log_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/steps/#{step_uuid}/logs/#{log_uuid}",
          text_response: true,
        )
      end

      def list_pipeline_step_test_reports(workspace:, repository:, pipeline_uuid:, step_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/steps/#{step_uuid}/test_reports",
        )
      end

      def list_pipeline_step_test_cases(workspace:, repository:, pipeline_uuid:, step_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/steps/#{step_uuid}/test_reports/test_cases",
        )
      end

      def list_pipeline_step_test_case_reasons(workspace:, repository:, pipeline_uuid:, step_uuid:, test_case_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines/#{pipeline_uuid}/steps/#{step_uuid}/test_reports/test_cases/#{test_case_uuid}/test_case_reasons",
        )
      end

      def get_pipeline_config(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}/pipelines_config")
      end

      def update_pipeline_config(workspace:, repository:, enabled: nil, repository_pipeline: nil)
        body = {}
        body["enabled"] = enabled unless enabled.nil?
        body["repository"] = repository_pipeline unless repository_pipeline.nil?
        request("PUT", "/repositories/#{workspace}/#{repository}/pipelines_config", body: body)
      end

      def update_pipeline_build_number(workspace:, repository:, next_build_number:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pipelines_config/build_number",
          body: { "next" => next_build_number },
        )
      end

      def list_pipeline_schedules(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines_config/schedules",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_pipeline_schedule(workspace:, repository:, target:, cron_pattern:, enabled: nil)
        body = { "target" => target, "cron_pattern" => cron_pattern }
        body["enabled"] = enabled unless enabled.nil?
        request("POST", "/repositories/#{workspace}/#{repository}/pipelines_config/schedules", body: body)
      end

      def get_pipeline_schedule(workspace:, repository:, schedule_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines_config/schedules/#{schedule_uuid}",
        )
      end

      def update_pipeline_schedule(workspace:, repository:, schedule_uuid:, enabled: nil, cron_pattern: nil, target: nil)
        body = {}
        body["enabled"] = enabled unless enabled.nil?
        body["cron_pattern"] = cron_pattern unless cron_pattern.nil?
        body["target"] = target unless target.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pipelines_config/schedules/#{schedule_uuid}",
          body: body,
        )
      end

      def delete_pipeline_schedule(workspace:, repository:, schedule_uuid:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/pipelines_config/schedules/#{schedule_uuid}",
        )
      end

      def list_pipeline_schedule_executions(workspace:, repository:, schedule_uuid:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines_config/schedules/#{schedule_uuid}/executions",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def get_pipeline_ssh_key_pair(workspace:, repository:)
        request("GET", "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/key_pair")
      end

      def update_pipeline_ssh_key_pair(workspace:, repository:, public_key:, private_key:)
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/key_pair",
          body: { "public_key" => public_key, "private_key" => private_key },
        )
      end

      def delete_pipeline_ssh_key_pair(workspace:, repository:)
        request("DELETE", "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/key_pair")
      end

      def list_pipeline_known_hosts(workspace:, repository:, page: nil, pagelen: nil)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/known_hosts",
          params: { "page" => page, "pagelen" => pagelen },
        )
      end

      def create_pipeline_known_host(workspace:, repository:, hostname:, public_key:)
        request(
          "POST",
          "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/known_hosts",
          body: { "hostname" => hostname, "public_key" => public_key },
        )
      end

      def get_pipeline_known_host(workspace:, repository:, known_host_uuid:)
        request(
          "GET",
          "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/known_hosts/#{known_host_uuid}",
        )
      end

      def update_pipeline_known_host(workspace:, repository:, known_host_uuid:, hostname: nil, public_key: nil)
        body = {}
        body["hostname"] = hostname unless hostname.nil?
        body["public_key"] = public_key unless public_key.nil?
        request(
          "PUT",
          "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/known_hosts/#{known_host_uuid}",
          body: body,
        )
      end

      def delete_pipeline_known_host(workspace:, repository:, known_host_uuid:)
        request(
          "DELETE",
          "/repositories/#{workspace}/#{repository}/pipelines_config/ssh/known_hosts/#{known_host_uuid}",
        )
      end
    end
  end
end
