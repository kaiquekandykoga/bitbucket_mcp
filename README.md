# Bitbucket MCP

An [MCP](https://modelcontextprotocol.io/) server that exposes large
chunks of the [Bitbucket Cloud REST API](https://developer.atlassian.com/cloud/bitbucket/rest/intro/)
to Claude Code (or any MCP client). It covers the
[Pull Requests](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/),
[Repositories](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-repositories/),
[Workspaces](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-workspaces/),
and [Commits](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-commits/)
API groups, so Claude can list, create, review, comment on, approve,
merge, and decline pull requests; create and fork repositories; browse
files and history; inspect commits, diffs, patches, and Code Insights
reports; and manage workspace members, webhooks, and projects on your
behalf.

## Workflow

1. You ask Claude Code to make changes (e.g. "write tests for X").
2. Claude Code edits, commits, and pushes a branch.
3. Claude Code calls the `create_pull_request` tool exposed by this server.
4. Bitbucket creates the PR; Claude Code returns the URL to you.

Beyond PR creation, Claude Code can also fetch a PR's diff, leave inline
comments, approve or request changes, merge, and more — see
[Available tools](#available-tools).

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python project + env manager)
- Python 3.10+
- A Bitbucket Cloud API token (Atlassian API token)

## Setup

```sh
uv sync
```

Set credentials either in a local `.env`:

```
BITBUCKET_EMAIL=you@example.com
BITBUCKET_API_TOKEN=your_api_token_here
```

…or in the Claude Code MCP config (see below). Values from the MCP
config take precedence over `.env`.

## Connect to Claude Code

Register the server with the Claude Code CLI:

```sh
claude mcp add bitbucket_mcp /path/to/bitbucket_mcp/.venv/bin/bitbucket_mcp
```

Or edit your Claude Code MCP config directly:

```json
{
  "mcpServers": {
    "bitbucket_mcp": {
      "command": "/path/to/bitbucket_mcp/.venv/bin/bitbucket_mcp",
      "env": {
        "BITBUCKET_EMAIL": "you@example.com",
        "BITBUCKET_API_TOKEN": "your_api_token_here"
      }
    }
  }
}
```

`env` is optional — omit it if you'd rather use `.env`.

## Try it locally

Once the server is registered, open Claude Code in any project and ask:

> Use bitbucket_mcp to show my current Bitbucket user.

Claude Code will call the `current_user` tool — a good smoke test for
your credentials. Then try the real workflow:

> On the `kaiquekandykoga/bitbucket_mcp` repo, create a pull request
> titled "Add foo" from branch `feature/foo` into `main`.

Claude Code will call `create_pull_request` and return the new PR's URL.

Or drive a full review loop end-to-end:

> List my open PRs on `kaiquekandykoga/bitbucket_mcp`, then show the
> diff of the most recent one and add an inline comment on the first
> changed line.

## Available tools

This server implements every endpoint in the Bitbucket Cloud
[Pull Requests](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/),
[Repositories](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-repositories/),
[Workspaces](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-workspaces/),
and [Commits](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-commits/)
API groups. Repository-scoped tools take `workspace` and `repository`
(the repo slug); most PR tools also take `pull_request_id`. Listing
tools accept the standard Bitbucket `q` / `sort` / `page` / `pagelen`
paginators where applicable.

### Smoke test

- **`current_user()`** — Returns the authenticated Bitbucket user.

### Pull requests

#### Lifecycle

- **`list_pull_requests(workspace, repository, state=None, q=None, sort=None, page=None, pagelen=None)`** — List PRs for a repository, optionally filtered by state.
- **`list_pull_requests_for_commit(workspace, repository, commit, page=None, pagelen=None)`** — List PRs that contain a given commit.
- **`create_pull_request(workspace, repository, title, source_branch, destination_branch="main", description=None, close_source_branch=None, reviewers=None)`** — Create a PR. Returns the Bitbucket PR object (`links.html.href` is the web URL).
- **`get_pull_request(workspace, repository, pull_request_id)`** — Fetch one PR.
- **`update_pull_request(workspace, repository, pull_request_id, title=None, description=None, destination_branch=None, reviewers=None)`** — Edit PR metadata.
- **`decline_pull_request(workspace, repository, pull_request_id)`** — Decline a PR.
- **`merge_pull_request(workspace, repository, pull_request_id, message=None, close_source_branch=None, merge_strategy=None, async_=None)`** — Merge a PR. `merge_strategy` is one of `merge_commit`, `squash`, `fast_forward`.
- **`get_merge_task_status(workspace, repository, pull_request_id, task_id)`** — Poll the status of an async merge.

#### Review

- **`approve_pull_request(workspace, repository, pull_request_id)`**
- **`unapprove_pull_request(workspace, repository, pull_request_id)`**
- **`request_changes(workspace, repository, pull_request_id)`**
- **`remove_request_changes(workspace, repository, pull_request_id)`**

#### Activity & contents

- **`list_repository_pull_request_activity(workspace, repository, page=None, pagelen=None)`** — All PR activity for the repo.
- **`list_pull_request_activity(workspace, repository, pull_request_id, page=None, pagelen=None)`** — Activity for one PR.
- **`list_pull_request_commits(workspace, repository, pull_request_id, page=None, pagelen=None)`**
- **`list_pull_request_conflicts(workspace, repository, pull_request_id, page=None, pagelen=None)`**
- **`list_pull_request_statuses(workspace, repository, pull_request_id, q=None, sort=None, page=None, pagelen=None)`** — Attached build statuses.
- **`get_pull_request_diff(workspace, repository, pull_request_id)`** — Returns the raw unified diff (string).
- **`get_pull_request_diffstat(workspace, repository, pull_request_id, page=None, pagelen=None)`** — Per-file change stats.
- **`get_pull_request_patch(workspace, repository, pull_request_id)`** — Returns the raw `git format-patch` output (string).

#### Comments

- **`list_pull_request_comments(workspace, repository, pull_request_id, q=None, sort=None, page=None, pagelen=None)`**
- **`create_pull_request_comment(workspace, repository, pull_request_id, content, parent_id=None, inline_path=None, inline_to=None, inline_from=None)`** — Top-level, reply (`parent_id`), or inline (`inline_path` + `inline_to`/`inline_from`).
- **`get_pull_request_comment(workspace, repository, pull_request_id, comment_id)`**
- **`update_pull_request_comment(workspace, repository, pull_request_id, comment_id, content)`**
- **`delete_pull_request_comment(workspace, repository, pull_request_id, comment_id)`**
- **`resolve_pull_request_comment(workspace, repository, pull_request_id, comment_id)`**
- **`reopen_pull_request_comment(workspace, repository, pull_request_id, comment_id)`**

#### Tasks

- **`list_pull_request_tasks(workspace, repository, pull_request_id, q=None, sort=None, page=None, pagelen=None)`**
- **`create_pull_request_task(workspace, repository, pull_request_id, content, comment_id=None, pending=None)`**
- **`get_pull_request_task(workspace, repository, pull_request_id, task_id)`**
- **`update_pull_request_task(workspace, repository, pull_request_id, task_id, content=None, state=None)`** — `state` is `RESOLVED` or `UNRESOLVED`.
- **`delete_pull_request_task(workspace, repository, pull_request_id, task_id)`**

### Workspaces

- **`list_user_workspaces(sort=None, administrator=None, page=None, pagelen=None)`** — Workspaces accessible to the caller. `sort` accepts only `slug`.
- **`get_user_workspace_permission(workspace)`** — Caller's effective role on a workspace.
- **`list_user_workspace_permissions(q=None, sort=None, page=None, pagelen=None)`** — (Deprecated) caller's workspace memberships.
- **`list_workspaces(role=None, q=None, sort=None, page=None, pagelen=None)`** — (Deprecated) Use `list_user_workspaces`.
- **`get_workspace(workspace)`** — Fetch a workspace by slug or UUID.
- **`list_workspace_members(workspace, q=None, page=None, pagelen=None)`** — `q` supports `user.email IN (...)` filters for admins.
- **`get_workspace_member(workspace, member)`** — `member` is a UUID or Atlassian Account ID.
- **`list_workspace_permissions(workspace, q=None, page=None, pagelen=None)`** — Per-user workspace permissions.
- **`list_workspace_repository_permissions(workspace, q=None, sort=None, page=None, pagelen=None)`** — All effective repo permissions across the workspace.
- **`list_workspace_repository_permissions_for_repo(workspace, repository, q=None, sort=None, page=None, pagelen=None)`** — Per-user permissions on one repo.
- **`list_workspace_projects(workspace, page=None, pagelen=None)`**
- **`get_workspace_project(workspace, project_key)`**
- **`list_workspace_user_pull_requests(workspace, selected_user, state=None, page=None, pagelen=None)`** — Workspace-wide PRs authored by a user; `state` can be a single string or list.
- **`get_workspace_gpg_key(workspace)`** — Workspace system GPG public key(s).
- **`list_workspace_webhooks(workspace, page=None, pagelen=None)`**
- **`create_workspace_webhook(workspace, url, events, description=None, active=None, secret=None)`** — `events` is a list of event keys (e.g. `repo:push`, `pullrequest:created`).
- **`get_workspace_webhook(workspace, uid)`**
- **`update_workspace_webhook(workspace, uid, url=None, events=None, description=None, active=None, secret=None)`**
- **`delete_workspace_webhook(workspace, uid)`**

### Repositories

#### Lifecycle

- **`list_repositories(workspace, role=None, q=None, sort=None, page=None, pagelen=None)`**
- **`list_public_repositories(after=None, role=None, q=None, sort=None, page=None, pagelen=None)`** — (Deprecated) all public repos.
- **`get_repository(workspace, repository)`**
- **`create_repository(workspace, repository, scm=None, name=None, description=None, is_private=None, fork_policy=None, language=None, has_issues=None, has_wiki=None, project_key=None, mainbranch_name=None)`** — `fork_policy` is one of `allow_forks`, `no_public_forks`, `no_forks`.
- **`update_repository(workspace, repository, name=None, description=None, is_private=None, fork_policy=None, language=None, has_issues=None, has_wiki=None, project_key=None, mainbranch_name=None)`**
- **`delete_repository(workspace, repository, redirect_to=None)`**
- **`fork_repository(workspace, repository, name=None, destination_workspace=None, is_private=None, description=None, project_key=None, fork_policy=None, language=None)`**
- **`list_repository_forks(workspace, repository, role=None, q=None, sort=None, page=None, pagelen=None)`**
- **`list_repository_watchers(workspace, repository, page=None, pagelen=None)`**

#### Browsing files

- **`get_repository_root_src(workspace, repository, format=None)`** — Listing for the main-branch HEAD; pass `format="meta"` for JSON metadata.
- **`get_repository_src(workspace, repository, commit, path, format=None, q=None, sort=None, max_depth=None)`** — File contents or directory listing at a specific commit. `format` is `meta` (JSON metadata) or `rendered` (HTML).
- **`create_src_commit(workspace, repository, message=None, author=None, parents=None, branch=None, files_to_add=None, files_to_delete=None)`** — Commit by uploading text files (`files_to_add` is a `{path: content_str}` mapping) and/or deleting paths (`files_to_delete`).
- **`list_file_history(workspace, repository, commit, path, renames=None, q=None, sort=None, page=None, pagelen=None)`** — Commits that modified a file. `renames` is `"true"`/`"false"`.

#### Permissions & settings

- **`list_repository_group_permissions(workspace, repository, page=None, pagelen=None)`**
- **`get_repository_group_permission(workspace, repository, group_slug)`**
- **`update_repository_group_permission(workspace, repository, group_slug, permission)`** — `permission` is `read`/`write`/`admin`.
- **`delete_repository_group_permission(workspace, repository, group_slug)`**
- **`list_repository_user_permissions(workspace, repository, page=None, pagelen=None)`**
- **`get_repository_user_permission(workspace, repository, selected_user_id)`**
- **`update_repository_user_permission(workspace, repository, selected_user_id, permission)`** — `permission` is `read`/`write`/`admin`.
- **`delete_repository_user_permission(workspace, repository, selected_user_id)`**
- **`list_user_repository_permissions(q=None, sort=None, page=None, pagelen=None)`** — (Deprecated) caller's repo permissions.
- **`list_user_workspace_repository_permissions(workspace, q=None, sort=None, page=None, pagelen=None)`** — Caller's repo permissions within a workspace.
- **`get_repository_override_settings(workspace, repository)`** — Which settings the repo overrides from the workspace.
- **`set_repository_override_settings(workspace, repository, settings)`** — `settings` is a flat dict of boolean flags.

#### Webhooks

- **`list_repository_webhooks(workspace, repository, page=None, pagelen=None)`**
- **`create_repository_webhook(workspace, repository, url, events, description=None, active=None, secret=None)`**
- **`get_repository_webhook(workspace, repository, uid)`**
- **`update_repository_webhook(workspace, repository, uid, url=None, events=None, description=None, active=None, secret=None)`**
- **`delete_repository_webhook(workspace, repository, uid)`**

### Commits

#### Lookup & listing

- **`get_commit(workspace, repository, commit)`**
- **`list_commits(workspace, repository, include=None, exclude=None, page=None, pagelen=None)`** — `include`/`exclude` are lists of refs.
- **`list_commits_with_filter(workspace, repository, include=None, exclude=None, page=None, pagelen=None)`** — POST variant for long include/exclude lists.
- **`list_commits_for_revision(workspace, repository, revision, include=None, exclude=None, path=None, page=None, pagelen=None)`** — Commits reachable from a revision; optional `path` filter.
- **`list_commits_for_revision_with_filter(workspace, repository, revision, include=None, exclude=None, page=None, pagelen=None)`** — POST variant.

#### Diff, patch & merge

- **`get_diff(workspace, repository, spec, context=None, path=None, ignore_whitespace=None, binary=None, renames=None, merge=None, topic=None)`** — `spec` is a SHA or `a..b` range.
- **`get_diffstat(workspace, repository, spec, ignore_whitespace=None, merge=None, path=None, renames=None, topic=None, page=None, pagelen=None)`**
- **`get_patch(workspace, repository, spec)`** — Raw `git format-patch` output.
- **`list_file_conflicts(workspace, repository, spec, page=None, pagelen=None)`**
- **`get_merge_base(workspace, repository, revspec)`** — `revspec` must be a `a..b` range.

#### Approvals

- **`approve_commit(workspace, repository, commit)`**
- **`unapprove_commit(workspace, repository, commit)`**

#### Comments

- **`list_commit_comments(workspace, repository, commit, q=None, sort=None, page=None, pagelen=None)`**
- **`create_commit_comment(workspace, repository, commit, content, parent_id=None, inline_path=None, inline_to=None, inline_from=None)`** — Top-level, reply, or inline.
- **`get_commit_comment(workspace, repository, commit, comment_id)`**
- **`update_commit_comment(workspace, repository, commit, comment_id, content)`**
- **`delete_commit_comment(workspace, repository, commit, comment_id)`** — Soft-deletes if the comment has replies.

#### Code Insights reports

- **`list_commit_reports(workspace, repository, commit, page=None, pagelen=None)`**
- **`get_commit_report(workspace, repository, commit, report_id)`**
- **`create_or_update_commit_report(workspace, repository, commit, report_id, title=None, details=None, external_id=None, reporter=None, link=None, remote_link_enabled=None, logo_url=None, report_type=None, result=None, data=None)`** — `report_type` is `SECURITY`/`COVERAGE`/`TEST`/`BUG`; `result` is `PASSED`/`FAILED`/`PENDING`.
- **`delete_commit_report(workspace, repository, commit, report_id)`**
- **`list_commit_report_annotations(workspace, repository, commit, report_id, page=None, pagelen=None)`**
- **`bulk_create_or_update_annotations(workspace, repository, commit, report_id, annotations)`** — Max 1000 annotations per report.
- **`get_commit_report_annotation(workspace, repository, commit, report_id, annotation_id)`**
- **`create_or_update_commit_report_annotation(workspace, repository, commit, report_id, annotation_id, external_id=None, annotation_type=None, path=None, line=None, summary=None, details=None, result=None, severity=None, link=None)`** — `annotation_type` is `VULNERABILITY`/`CODE_SMELL`/`BUG`; `severity` is `CRITICAL`/`HIGH`/`MEDIUM`/`LOW`.
- **`delete_commit_report_annotation(workspace, repository, commit, report_id, annotation_id)`**

## Layout

```
pyproject.toml                          # project config, deps, scripts, ruff, pytest
src/bitbucket_mcp/
  __init__.py                           # __version__
  server.py                             # FastMCP server (entry point)
  bitbucket/
    __init__.py
    client.py                           # Bitbucket Cloud HTTP client (stdlib urllib)
tests/
  test_client.py                        # client tests (mocks urllib.request.urlopen)
  test_server.py                        # server tool tests (mocks the Client)
```

## Development

```sh
uv run pytest                           # run all tests
uv run pytest -v                        # verbose: show each test name
uv run pytest -k pull_request           # only PR-related tests
uv run ruff check .                     # lint
uv run ruff format .                    # format
```

Tests mock the HTTP boundary (`urllib.request.urlopen`) and the
`Client` class, so they're hermetic — no network calls and no real
Bitbucket credentials needed.

### Debugging the MCP server

Use the official MCP inspector to call tools by hand without going
through Claude Code:

```sh
npx @modelcontextprotocol/inspector /path/to/bitbucket_mcp/.venv/bin/bitbucket_mcp
```
