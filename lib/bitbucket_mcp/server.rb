# frozen_string_literal: true

require "mcp"

require_relative "version"
require_relative "tools"

module BitbucketMcp
  # Builds and runs the Bitbucket MCP server over stdio.
  module Server
    module_function

    SERVER_NAME = "bitbucket_mcp"

    USAGE = <<~TEXT
      bitbucket-mcp - MCP server for the Bitbucket Cloud REST API

      Usage: bitbucket-mcp [options]

      The server speaks the Model Context Protocol over stdio. It is normally
      launched by an MCP client (Claude, an editor, an agent), not run directly.

      Options:
        -v, --version   Print the version and exit.
        -h, --help      Print this help and exit.

      Required environment variables:
        BITBUCKET_EMAIL       Atlassian account email.
        BITBUCKET_API_TOKEN   Atlassian API token (scoped to Bitbucket).

      Optional environment variables:
        BITBUCKET_TIMEOUT       Per-request timeout in seconds (default 30).
        BITBUCKET_MAX_RETRIES   Retries for transient failures (default 3).
    TEXT

    # Build the underlying MCP::Server with every Bitbucket tool registered.
    def build
      MCP::Server.new(
        name: SERVER_NAME,
        version: BitbucketMcp::VERSION,
        tools: BitbucketMcp::Tools.all,
      )
    end

    # Entry point for the executable. Handles --version/--help, then serves stdio.
    def run(argv = ARGV)
      case argv[0]
      when "-v", "--version"
        puts BitbucketMcp::VERSION
        return
      when "-h", "--help"
        puts USAGE
        return
      end

      load_dotenv
      MCP::Server::Transports::StdioTransport.new(build).open
    end

    # Load a local .env file when the optional `dotenv` gem is available. The
    # server also works with credentials injected directly into the environment.
    def load_dotenv
      require "dotenv"
      Dotenv.load
    rescue LoadError
      nil
    end
  end
end
