# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`bitbucket_mcp` is a pure-Ruby gem: a Model Context Protocol (MCP) server that exposes the Bitbucket Cloud REST API (v2.0) as 310 tools, runnable by any MCP client over stdio. Runtime dependencies are minimal (`mcp`, `dotenv`, `base64`); the HTTP client is built on stdlib `net/http`.

## Commands

```sh
bundle install                                              # install dependencies

bundle exec rake                                           # default task: tests + RuboCop
bundle exec rake test                                      # run the whole test suite
bundle exec ruby -Itest test/endpoints/pull_requests_test.rb              # run one test file
bundle exec ruby -Itest test/endpoints/pull_requests_test.rb -n "/merge/" # run tests whose name matches a pattern

bundle exec rubocop                                        # lint
bundle exec rubocop -a                                     # lint + safe autocorrect

bundle exec bin/bitbucket-mcp --version                    # CLI (also --help)
npx @modelcontextprotocol/inspector bundle exec bitbucket-mcp   # drive the server by hand
```

Tests are hermetic — WebMock disables real network access and credentials are faked, so no Bitbucket account is needed. `Gemfile.lock` is intentionally not committed (CI resolves dependencies fresh per Ruby version). CI lints on Ruby 4.0 and tests on Ruby 4.0 and 3.4.

## Architecture

The codebase is four layers, wired together by a single naming convention.

**1. `Client` + `Endpoints` (the HTTP layer).** `lib/bitbucket_mcp/client.rb` is a thin Bitbucket Cloud client. It `include`s every module under `BitbucketMcp::Endpoints` (auto-discovered via `Endpoints.constants`). Each `lib/bitbucket_mcp/endpoints/<area>.rb` defines plain instance methods (e.g. `list_branches(workspace:, repository:, ...)`) that only build a path/params/body and delegate to the private `request(method, path, body:/body_bytes:/params:/text_response:)`. All transport concerns live in `request` and its helpers — endpoint methods never touch `net/http`.

Things `request` handles that endpoint methods rely on:
- **Param cleaning:** `nil` values in `params:` are dropped; array values become repeated query keys (`include=a&include=b`).
- **Verbatim path interpolation:** paths are *not* round-tripped through `URI.parse`, so brace-wrapped UUID segments like `/pipelines/{uuid}` work.
- **`text_response: true`** returns the raw body as a String (diffs, patches, file contents); otherwise the body is parsed JSON, or `{}` for an empty body.
- **Retries:** idempotent methods retry on retryable statuses (429/5xx) and network errors; non-idempotent writes (POST) retry only on 429 (provably not processed). Honors `Retry-After`; otherwise capped exponential backoff.
- **Error mapping:** HTTP 401 → `AuthenticationError` (no retry); other non-2xx → `ResponseError`. Both descend from `BitbucketMcp::Error` (see `errors.rb`).

**2. `Tools` + `ToolFactory` + `Schema` (the MCP tool layer).** Each `lib/bitbucket_mcp/tools/<area>.rb` mirrors the matching `endpoints/<area>.rb` file (15 paired areas) and exposes `.all`, an array of `ToolFactory.build(...)` results. `Schema` (`schema.rb`) provides JSON Schema fragment helpers (`str`, `int`, `bool`, `strs`, `array`, `object`, `str_map`) plus shared `WORKSPACE`/`REPOSITORY`/`PAGE`/`PAGELEN` constants. `Tools.all` aggregates every category module's `.all`, sorted by name.

**3. `Server` (the runtime).** `server.rb` builds an `MCP::Server` from `Tools.all` and serves it over stdio; the CLI (`bin/bitbucket-mcp`) handles `--version`/`--help` and otherwise loads `.env` (via `dotenv`, optional) and opens the transport.

**The central invariant: each tool's `name` must equal a `Client` method of the same name.** `ToolFactory.invoke` dispatches every tool call with `Client.new.public_send(name, **args)`. Consequences:
- Adding a capability = add a method in `endpoints/<area>.rb` **and** a `ToolFactory.build(name: "<same_name>", ...)` in the paired `tools/<area>.rb`, with property names matching the method's keyword args.
- Parameter **defaults live only in the client method signature** — tool schemas declare types and `required:`, not defaults.
- `server_test.rb` enforces this 1:1 mapping (every tool responds to a same-named client method), schema validity, and annotation correctness — run it after touching tools or endpoints.

**A `Client` is created fresh per tool call**, so credentials/tuning are read from the environment on every invocation: `BITBUCKET_EMAIL` and `BITBUCKET_API_TOKEN` (required), `BITBUCKET_TIMEOUT` (default 30s) and `BITBUCKET_MAX_RETRIES` (default 3, optional). `ToolFactory.invoke` returns the client result as text (String passthrough, else `JSON.pretty_generate`) and converts any `BitbucketMcp::Error` into a tool error response rather than crashing the transport; it also strips the framework-injected `:server_context` argument.

### Schema gotcha for structured params

For object- or array-valued arguments, use `Schema.object(...)` / `Schema.array(...)` — these deliberately **omit** `additionalProperties` / `items`. If you add those keys, MCP's input validation rejects otherwise-valid nested input. `server_test.rb` has a regression test for this (e.g. `set_repository_override_settings`'s `settings`, `create_branch_restriction`'s `groups`).

## Conventions

- **Tests** use `test-unit` + WebMock. Files live in `test/` as `<name>_test.rb`, classes are `< Test::Unit::TestCase` using `test "description" do`. `test/test_helper.rb` provides the shared helpers: `build_client`, `stub_api`, `stub_call`, `api_url`, `with_env`, `stub_sleep`, `capture_stdout`. Endpoint tests assert request shape with WebMock's `assert_requested` (which fails on mismatch but does not increment test-unit's assertion counter — a "0 assertions" line is normal and not a problem).
- **RuboCop** config (`.rubocop.yml`): `Metrics` is disabled and `LineLength` is excluded for `endpoints/`, `tools/`, and `test/` because those are wide, data-definition tables; strings are double-quoted; multiline literals/args take trailing commas. Keep new endpoint/tool entries on the single-line, table-like form the surrounding code uses.
- Endpoint keyword-argument names mirror Bitbucket's own query/path parameters (`q`, `sort`, `selected_user`, etc.).
