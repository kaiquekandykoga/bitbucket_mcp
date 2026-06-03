# frozen_string_literal: true

require_relative "lib/bitbucket_mcp/version"

Gem::Specification.new do |spec|
  spec.name = "bitbucket_mcp"
  spec.version = BitbucketMcp::VERSION
  spec.authors = ["Kaíque Kandy Koga"]
  spec.summary = "MCP server exposing the Bitbucket Cloud REST API to any MCP-compatible client."
  spec.description = <<~DESC
    A Model Context Protocol (MCP) server that exposes the Bitbucket Cloud REST API
    as tools any MCP-compatible client (Claude, editors, agents) can call. Pure Ruby,
    no runtime dependencies beyond the MCP SDK.
  DESC
  spec.homepage = "https://github.com/kaiquekandykoga/bitbucket_mcp"
  spec.license = "BSD-3-Clause"
  spec.required_ruby_version = ">= 3.1"

  spec.metadata["source_code_uri"] = spec.homepage
  spec.metadata["changelog_uri"] = "#{spec.homepage}/releases"
  spec.metadata["rubygems_mfa_required"] = "true"

  spec.files = Dir["lib/**/*.rb", "exe/*", "README.md", "LICENSE"]
  spec.bindir = "exe"
  spec.executables = ["bitbucket-mcp"]
  spec.require_paths = ["lib"]

  spec.add_dependency "base64", "~> 0.2"
  spec.add_dependency "dotenv", "~> 3.0"
  spec.add_dependency "mcp", "~> 0.1"

  spec.add_development_dependency "rake", "~> 13.0"
  spec.add_development_dependency "rubocop", "~> 1.60"
  spec.add_development_dependency "test-unit", "~> 3.6"
  spec.add_development_dependency "webmock", "~> 3.0"
end
