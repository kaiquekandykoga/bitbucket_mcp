# frozen_string_literal: true

require_relative "bitbucket_mcp/version"
require_relative "bitbucket_mcp/errors"
require_relative "bitbucket_mcp/client"
require_relative "bitbucket_mcp/schema"
require_relative "bitbucket_mcp/tool_factory"
require_relative "bitbucket_mcp/tools"
require_relative "bitbucket_mcp/server"

# Top-level namespace for the Bitbucket MCP server.
#
# - {BitbucketMcp::Client} talks to the Bitbucket Cloud REST API.
# - {BitbucketMcp::Tools} exposes each client method as an MCP tool.
# - {BitbucketMcp::Server} runs the tools over the Model Context Protocol.
module BitbucketMcp
end
