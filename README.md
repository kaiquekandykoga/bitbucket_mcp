# Bitbucket MCP

[![CI](https://github.com/kaiquekandykoga/bitbucket_mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/kaiquekandykoga/bitbucket_mcp/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-BSD--3--Clause-green)

An [MCP](https://modelcontextprotocol.io/) server that exposes **310
tools** covering nearly every endpoint of the [Bitbucket Cloud REST
API](https://developer.atlassian.com/cloud/bitbucket/rest/intro/) to
any MCP-compatible client (Claude Code, Claude Desktop, Cursor, Cline,
Zed, custom apps built on the MCP SDK, …). Manage pull requests,
repositories, pipelines, deployments, issues, branches, snippets,
webhooks, and permissions from your agent of choice.

## Contents

- [Workflow](#workflow)
- [Coverage](#coverage)
- [Requirements](#requirements)
- [Setup](#setup)
- [Connect to an MCP client](#connect-to-an-mcp-client)
- [Available tools](#available-tools)
- [Development](#development)
- [Debugging](#debugging-the-mcp-server)
- [Project layout](#project-layout)

## Workflow

1. You ask your agent to make changes (e.g. "write tests for X").
2. The agent edits, commits, and pushes a branch.
3. The agent calls the `create_pull_request` tool exposed by this server.
4. Bitbucket creates the PR; the agent returns the URL to you.

Beyond PR creation, agents can also fetch a PR's diff, leave inline
comments, approve or request changes, merge, and more — see
[Available tools](#available-tools).

## Coverage

| Group | What's in it |
|-------|--------------|
| [Pull requests](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/) | Lifecycle, review, comments, tasks, default reviewers |
| [Repositories](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-repositories/) | CRUD, forks, watchers, group/user permissions, override settings |
| [Workspaces](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-workspaces/) | Members, permissions, projects, GPG, webhooks |
| [Projects](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-projects/) | CRUD, default reviewers, deploy keys, permissions |
| [Commits](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-commits/) | Diffs, patches, comments, approvals, merge-base, file conflicts |
| [Refs](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-refs/) | Branches & tags |
| [Source](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-source/) | Browse files, commit via multipart upload |
| [Branch restrictions](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-branch-restrictions/) | Push/merge/delete rules |
| [Branching model](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-branching-model/) | Repo & project-level branching settings |
| [Commit statuses](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-commit-statuses/) | Build status reporting |
| [Pipelines](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pipelines/) | Run, stop, logs, schedules, variables, caches, runners, OIDC |
| [Deployments](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-deployments/) | Deploy keys, environments, deployments |
| [Reports (Code Insights)](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-reports/) | Reports + annotations |
| [Issue tracker](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-issue-tracker/) | Issues, comments, attachments, votes, watches, milestones, versions, components |
| [Webhooks](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-webhooks/) | Workspace + repo subscriptions, event types |
| [Snippets](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-snippets/) | Full lifecycle, comments, revisions, diff/patch |
| [Downloads](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-downloads/) | Upload, list, download, delete |
| [Users](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-users/) | Profiles + email management |
| [SSH](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-ssh/) / [GPG](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-gpg/) | User keys |
| Search | Workspace + user code search |

**Not included:** [Addon](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-addon/) routes and the JWT-scoped hosted-properties routes, since they require Connect-app auth rather than an email + API token.

## Requirements

- [uv](https://docs.astral.sh/uv/) (Python project + env manager)
- Python 3.10+
- A Bitbucket Cloud API token (Atlassian API token)

## Setup

```sh
uv sync
```

Set credentials in a local `.env`:

```
BITBUCKET_EMAIL=you@example.com
BITBUCKET_API_TOKEN=your_api_token_here
```

…or in your MCP client's config (see below). Values from the client
config take precedence over `.env`.

## Connect to an MCP client

This server speaks stdio MCP, so it works with any MCP-compatible
client. The configuration is the same shape everywhere — point the
client at the installed `bitbucket_mcp` script:

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

Where that block lives depends on the client:

- **Claude Code (CLI):** `claude mcp add bitbucket_mcp /path/to/bitbucket_mcp/.venv/bin/bitbucket_mcp`, or edit `~/.claude.json` / a project-level `.mcp.json` directly.
- **Claude Desktop:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows).
- **Cursor:** `~/.cursor/mcp.json` or a project-level `.cursor/mcp.json`.
- **Other clients (Cline, Zed, Continue, custom apps via the [MCP SDK](https://modelcontextprotocol.io/quickstart/server)):** consult the client's docs — the JSON block above is what most expect.

## Available tools

Repository-scoped tools take `workspace` and `repository` (the repo
slug); most PR tools also take `pull_request_id`. Listing tools accept
the standard Bitbucket `q` / `sort` / `page` / `pagelen` paginators where
applicable. Click any group below to expand its tools.

**Smoke test:** `current_user()` — returns the authenticated Bitbucket user.

<details>
<summary><strong>Pull requests</strong> — lifecycle, review, comments, tasks, default reviewers</summary>

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

#### Default reviewers

- **`list_default_reviewers(workspace, repository, page=None, pagelen=None)`**
- **`list_effective_default_reviewers(workspace, repository, page=None, pagelen=None)`** — Includes inherited project-level reviewers.
- **`get_default_reviewer(workspace, repository, target_username)`**
- **`add_default_reviewer(workspace, repository, target_username)`**
- **`remove_default_reviewer(workspace, repository, target_username)`**

</details>

<details>
<summary><strong>Workspaces</strong> — members, permissions, projects, webhooks, GPG</summary>

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

</details>

<details>
<summary><strong>Projects</strong> — CRUD, default reviewers, permissions</summary>

- **`create_workspace_project(workspace, key, name, description=None, is_private=None, avatar=None)`**
- **`update_workspace_project(workspace, project_key, key=None, name=None, description=None, is_private=None, avatar=None)`**
- **`delete_workspace_project(workspace, project_key)`**

#### Default reviewers

- **`list_project_default_reviewers(workspace, project_key, page=None, pagelen=None)`**
- **`get_project_default_reviewer(workspace, project_key, selected_user)`**
- **`add_project_default_reviewer(workspace, project_key, selected_user)`**
- **`remove_project_default_reviewer(workspace, project_key, selected_user)`**

#### Permissions

- **`list_project_group_permissions(workspace, project_key, page=None, pagelen=None)`**
- **`get_project_group_permission(workspace, project_key, group_slug)`**
- **`update_project_group_permission(workspace, project_key, group_slug, permission)`** — `permission` is `read`/`write`/`create-repo`/`admin`.
- **`delete_project_group_permission(workspace, project_key, group_slug)`**
- **`list_project_user_permissions(workspace, project_key, page=None, pagelen=None)`**
- **`get_project_user_permission(workspace, project_key, selected_user_id)`**
- **`update_project_user_permission(workspace, project_key, selected_user_id, permission)`**
- **`delete_project_user_permission(workspace, project_key, selected_user_id)`**

</details>

<details>
<summary><strong>Repositories</strong> — CRUD, files, forks, permissions, webhooks</summary>

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

</details>

<details>
<summary><strong>Refs (branches & tags)</strong></summary>

- **`list_refs(workspace, repository, q=None, sort=None, page=None, pagelen=None)`** — All refs (branches and tags).
- **`list_branches(workspace, repository, q=None, sort=None, page=None, pagelen=None)`**
- **`create_branch(workspace, repository, name, target_hash)`**
- **`get_branch(workspace, repository, name)`**
- **`delete_branch(workspace, repository, name)`**
- **`list_tags(workspace, repository, q=None, sort=None, page=None, pagelen=None)`**
- **`create_tag(workspace, repository, name, target_hash, message=None)`**
- **`get_tag(workspace, repository, name)`**
- **`delete_tag(workspace, repository, name)`**

</details>

<details>
<summary><strong>Branch restrictions & branching model</strong></summary>

#### Branch restrictions

- **`list_branch_restrictions(workspace, repository, kind=None, pattern=None, page=None, pagelen=None)`**
- **`create_branch_restriction(workspace, repository, kind, pattern=None, branch_match_kind=None, branch_type=None, users=None, groups=None, value=None)`**
- **`get_branch_restriction(workspace, repository, id)`**
- **`update_branch_restriction(workspace, repository, id, ...)`**
- **`delete_branch_restriction(workspace, repository, id)`**

#### Branching model

- **`get_branching_model(workspace, repository)`**
- **`get_effective_branching_model(workspace, repository)`** — After project inheritance.
- **`get_branching_model_settings(workspace, repository)`**
- **`update_branching_model_settings(workspace, repository, development=None, production=None, branch_types=None)`**
- **`get_project_branching_model(workspace, project_key)`**
- **`get_project_branching_model_settings(workspace, project_key)`**
- **`update_project_branching_model_settings(workspace, project_key, ...)`**

</details>

<details>
<summary><strong>Commits</strong> — lookup, diffs, patches, comments, Code Insights, build statuses</summary>

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

#### Build statuses

- **`list_commit_statuses(workspace, repository, commit, q=None, sort=None, page=None, pagelen=None)`**
- **`create_commit_build_status(workspace, repository, commit, key, state, url, name=None, description=None, refname=None)`** — `state` is `INPROGRESS`/`SUCCESSFUL`/`FAILED`/`STOPPED`.
- **`get_commit_build_status(workspace, repository, commit, key)`**
- **`update_commit_build_status(workspace, repository, commit, key, state=None, url=None, name=None, description=None, refname=None)`**

</details>

<details>
<summary><strong>Pipelines</strong> — runs, steps, logs, schedules, variables, runners, caches</summary>

#### Lifecycle & inspection

- **`list_pipelines(workspace, repository, q=None, sort=None, page=None, pagelen=None)`**
- **`create_pipeline(workspace, repository, target, variables=None)`** — `target` follows the Pipelines REST schema (e.g. `{"type": "pipeline_ref_target", "ref_type": "branch", "ref_name": "main", "selector": {"type": "default"}}`).
- **`get_pipeline(workspace, repository, pipeline_uuid)`**
- **`stop_pipeline(workspace, repository, pipeline_uuid)`**

#### Steps & logs

- **`list_pipeline_steps(workspace, repository, pipeline_uuid, page=None, pagelen=None)`**
- **`get_pipeline_step(workspace, repository, pipeline_uuid, step_uuid)`**
- **`get_pipeline_step_log(workspace, repository, pipeline_uuid, step_uuid)`** — Raw text log.
- **`get_pipeline_step_container_log(workspace, repository, pipeline_uuid, step_uuid, log_uuid)`**
- **`list_pipeline_step_test_reports(workspace, repository, pipeline_uuid, step_uuid)`**
- **`list_pipeline_step_test_cases(workspace, repository, pipeline_uuid, step_uuid)`**
- **`list_pipeline_step_test_case_reasons(workspace, repository, pipeline_uuid, step_uuid, test_case_uuid)`**

#### Configuration

- **`get_pipeline_config(workspace, repository)`**
- **`update_pipeline_config(workspace, repository, enabled=None, repository_pipeline=None)`**
- **`update_pipeline_build_number(workspace, repository, next_build_number)`**

#### Schedules

- **`list_pipeline_schedules(workspace, repository, page=None, pagelen=None)`**
- **`create_pipeline_schedule(workspace, repository, target, cron_pattern, enabled=None)`**
- **`get_pipeline_schedule(workspace, repository, schedule_uuid)`**
- **`update_pipeline_schedule(workspace, repository, schedule_uuid, ...)`**
- **`delete_pipeline_schedule(workspace, repository, schedule_uuid)`**
- **`list_pipeline_schedule_executions(workspace, repository, schedule_uuid, page=None, pagelen=None)`**

#### SSH

- **`get_pipeline_ssh_key_pair(workspace, repository)`**
- **`update_pipeline_ssh_key_pair(workspace, repository, public_key, private_key)`**
- **`delete_pipeline_ssh_key_pair(workspace, repository)`**
- **`list_pipeline_known_hosts(workspace, repository, page=None, pagelen=None)`**
- **`create_pipeline_known_host(workspace, repository, hostname, public_key)`** — `public_key` is `{"key": "...", "key_type": "..."}`.
- **`get_pipeline_known_host(workspace, repository, known_host_uuid)`**
- **`update_pipeline_known_host(workspace, repository, known_host_uuid, ...)`**
- **`delete_pipeline_known_host(workspace, repository, known_host_uuid)`**

#### Variables

- **`list_pipeline_variables(workspace, repository, page=None, pagelen=None)`** — Repository-scoped.
- **`create_pipeline_variable(workspace, repository, key, value, secured=None)`**
- **`get_pipeline_variable(workspace, repository, variable_uuid)`**
- **`update_pipeline_variable(workspace, repository, variable_uuid, ...)`**
- **`delete_pipeline_variable(workspace, repository, variable_uuid)`**
- **`list_workspace_pipeline_variables(workspace, page=None, pagelen=None)`**
- **`create_workspace_pipeline_variable(workspace, key, value, secured=None)`**
- **`get_workspace_pipeline_variable(workspace, variable_uuid)`**
- **`update_workspace_pipeline_variable(workspace, variable_uuid, ...)`**
- **`delete_workspace_pipeline_variable(workspace, variable_uuid)`**
- **`list_user_pipeline_variables(selected_user, page=None, pagelen=None)`**
- **`create_user_pipeline_variable(selected_user, key, value, secured=None)`**
- **`get_user_pipeline_variable(selected_user, variable_uuid)`**
- **`update_user_pipeline_variable(selected_user, variable_uuid, ...)`**
- **`delete_user_pipeline_variable(selected_user, variable_uuid)`**
- **`list_deployment_variables(workspace, repository, environment_uuid, page=None, pagelen=None)`**
- **`create_deployment_variable(workspace, repository, environment_uuid, key, value, secured=None)`**
- **`update_deployment_variable(workspace, repository, environment_uuid, variable_uuid, ...)`**
- **`delete_deployment_variable(workspace, repository, environment_uuid, variable_uuid)`**

#### Caches

- **`list_pipeline_caches(workspace, repository, page=None, pagelen=None)`**
- **`delete_pipeline_caches(workspace, repository, name=None)`** — Delete all caches, optionally filtered by name.
- **`delete_pipeline_cache(workspace, repository, cache_uuid)`**
- **`get_pipeline_cache_content_uri(workspace, repository, cache_uuid)`** — Temporary download URI.

#### Runners

- **`list_repository_pipeline_runners(workspace, repository, page=None, pagelen=None)`**
- **`create_repository_pipeline_runner(workspace, repository, name, labels=None)`**
- **`get_repository_pipeline_runner(workspace, repository, runner_uuid)`**
- **`update_repository_pipeline_runner(workspace, repository, runner_uuid, ...)`**
- **`delete_repository_pipeline_runner(workspace, repository, runner_uuid)`**
- **`list_workspace_pipeline_runners(workspace, page=None, pagelen=None)`**
- **`create_workspace_pipeline_runner(workspace, name, labels=None)`**
- **`get_workspace_pipeline_runner(workspace, runner_uuid)`**
- **`update_workspace_pipeline_runner(workspace, runner_uuid, ...)`**
- **`delete_workspace_pipeline_runner(workspace, runner_uuid)`**

#### OIDC

- **`get_pipelines_oidc_configuration(workspace)`**
- **`get_pipelines_oidc_keys(workspace)`**

</details>

<details>
<summary><strong>Deployments</strong> — deploy keys, environments, deployments</summary>

#### Deploy keys

- **`list_deploy_keys(workspace, repository, page=None, pagelen=None)`**
- **`create_deploy_key(workspace, repository, key, label=None)`**
- **`get_deploy_key(workspace, repository, key_id)`**
- **`update_deploy_key(workspace, repository, key_id, label=None, key=None)`**
- **`delete_deploy_key(workspace, repository, key_id)`**
- **`list_project_deploy_keys(workspace, project_key, page=None, pagelen=None)`**
- **`create_project_deploy_key(workspace, project_key, key, label=None)`**
- **`get_project_deploy_key(workspace, project_key, key_id)`**
- **`delete_project_deploy_key(workspace, project_key, key_id)`**

#### Environments & deployments

- **`list_deployments(workspace, repository, page=None, pagelen=None)`**
- **`get_deployment(workspace, repository, deployment_uuid)`**
- **`list_environments(workspace, repository, page=None, pagelen=None)`**
- **`create_environment(workspace, repository, name, environment_type=None, rank=None)`**
- **`get_environment(workspace, repository, environment_uuid)`**
- **`update_environment(workspace, repository, environment_uuid, body=None)`** — POSTs to `/changes`.
- **`delete_environment(workspace, repository, environment_uuid)`**

</details>

<details>
<summary><strong>Issue tracker</strong> — issues, comments, attachments, changes, votes & watches</summary>

#### Metadata

- **`list_components(workspace, repository, q=None, sort=None, page=None, pagelen=None)`**
- **`get_component(workspace, repository, component_id)`**
- **`list_milestones(workspace, repository, q=None, sort=None, page=None, pagelen=None)`**
- **`get_milestone(workspace, repository, milestone_id)`**
- **`list_versions(workspace, repository, q=None, sort=None, page=None, pagelen=None)`**
- **`get_version(workspace, repository, version_id)`**

#### Issues

- **`list_issues(workspace, repository, q=None, sort=None, page=None, pagelen=None)`**
- **`create_issue(workspace, repository, title, content=None, kind=None, priority=None, state=None, component=None, milestone=None, version=None, assignee=None)`**
- **`get_issue(workspace, repository, issue_id)`**
- **`update_issue(workspace, repository, issue_id, ...)`**
- **`delete_issue(workspace, repository, issue_id)`**

#### Export/import

- **`export_issues(workspace, repository)`** — Returns a task descriptor.
- **`get_issue_export(workspace, repository, repo_name, task_id)`** — Downloads the zip.
- **`get_issue_import_status(workspace, repository)`**
- **`import_issues(workspace, repository)`**

#### Attachments

- **`list_issue_attachments(workspace, repository, issue_id, page=None, pagelen=None)`**
- **`upload_issue_attachment(workspace, repository, issue_id, files)`** — `files` is `{filename: text_content}`.
- **`get_issue_attachment(workspace, repository, issue_id, path)`**
- **`delete_issue_attachment(workspace, repository, issue_id, path)`**

#### Changes

- **`list_issue_changes(workspace, repository, issue_id, q=None, sort=None, page=None, pagelen=None)`**
- **`create_issue_change(workspace, repository, issue_id, changes=None, message=None)`** — `changes` is `{field: {"new": value}}`.
- **`get_issue_change(workspace, repository, issue_id, change_id)`**

#### Comments

- **`list_issue_comments(workspace, repository, issue_id, q=None, sort=None, page=None, pagelen=None)`**
- **`create_issue_comment(workspace, repository, issue_id, content)`**
- **`get_issue_comment(workspace, repository, issue_id, comment_id)`**
- **`update_issue_comment(workspace, repository, issue_id, comment_id, content)`**
- **`delete_issue_comment(workspace, repository, issue_id, comment_id)`**

#### Votes & watches

- **`get_issue_vote(workspace, repository, issue_id)`** / **`vote_for_issue(...)`** / **`unvote_issue(...)`**
- **`get_issue_watch(workspace, repository, issue_id)`** / **`watch_issue(...)`** / **`unwatch_issue(...)`**

</details>

<details>
<summary><strong>Snippets</strong> — lifecycle, comments, revisions, diffs</summary>

#### Lifecycle

- **`list_snippets(role=None, page=None, pagelen=None)`**
- **`create_snippet(title=None, is_private=None, scm=None, files=None)`** — `files` is `{filename: text_content}`.
- **`list_workspace_snippets(workspace, role=None, page=None, pagelen=None)`**
- **`create_workspace_snippet(workspace, title=None, is_private=None, scm=None, files=None)`**
- **`get_snippet(workspace, encoded_id)`**
- **`update_snippet(workspace, encoded_id, title=None, is_private=None, files=None)`**
- **`delete_snippet(workspace, encoded_id)`**

#### Comments & commits

- **`list_snippet_comments(workspace, encoded_id, page=None, pagelen=None)`**
- **`create_snippet_comment(workspace, encoded_id, content)`**
- **`get_snippet_comment(workspace, encoded_id, comment_id)`**
- **`update_snippet_comment(workspace, encoded_id, comment_id, content)`**
- **`delete_snippet_comment(workspace, encoded_id, comment_id)`**
- **`list_snippet_commits(workspace, encoded_id, page=None, pagelen=None)`**
- **`get_snippet_commit(workspace, encoded_id, revision)`**

#### Files, watching & revisions

- **`get_snippet_file(workspace, encoded_id, path)`**
- **`get_snippet_watch(workspace, encoded_id)`** / **`watch_snippet(...)`** / **`unwatch_snippet(...)`**
- **`list_snippet_watchers(workspace, encoded_id, page=None, pagelen=None)`**
- **`get_snippet_at_revision(workspace, encoded_id, node_id)`**
- **`update_snippet_at_revision(workspace, encoded_id, node_id, title=None, is_private=None, files=None)`**
- **`delete_snippet_at_revision(workspace, encoded_id, node_id)`**
- **`get_snippet_file_at_revision(workspace, encoded_id, node_id, path)`**
- **`get_snippet_diff(workspace, encoded_id, revision)`**
- **`get_snippet_patch(workspace, encoded_id, revision)`**

</details>

<details>
<summary><strong>Downloads</strong></summary>

- **`list_downloads(workspace, repository, page=None, pagelen=None)`**
- **`upload_download(workspace, repository, files)`** — `files` is `{filename: text_content}`.
- **`get_download(workspace, repository, filename)`**
- **`delete_download(workspace, repository, filename)`**

</details>

<details>
<summary><strong>Users, SSH & GPG keys</strong></summary>

#### Users

- **`get_user(selected_user)`** — Public profile by username, UUID, or Atlassian Account ID.
- **`list_user_emails(page=None, pagelen=None)`** — Authenticated user's email addresses.
- **`get_user_email(email)`**

#### SSH keys

- **`list_user_ssh_keys(selected_user, page=None, pagelen=None)`**
- **`create_user_ssh_key(selected_user, key, label=None)`**
- **`get_user_ssh_key(selected_user, key_id)`**
- **`update_user_ssh_key(selected_user, key_id, label=None, key=None)`**
- **`delete_user_ssh_key(selected_user, key_id)`**

#### GPG keys

- **`list_user_gpg_keys(selected_user, page=None, pagelen=None)`**
- **`create_user_gpg_key(selected_user, key, name=None)`**
- **`get_user_gpg_key(selected_user, fingerprint)`**
- **`delete_user_gpg_key(selected_user, fingerprint)`**

</details>

<details>
<summary><strong>Webhook event types & search</strong></summary>

#### Webhook event types

- **`list_hook_event_subjects()`** — Subject types that can be subscribed to (workspace, user, repository).
- **`list_hook_events(subject_type)`** — All event keys for a subject type.

#### Search

- **`search_workspace_code(workspace, search_query, page=None, pagelen=None)`**
- **`search_user_code(selected_user, search_query, page=None, pagelen=None)`**

</details>

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

## Debugging the MCP server

Use the official MCP inspector to call tools by hand without going
through a client:

```sh
npx @modelcontextprotocol/inspector /path/to/bitbucket_mcp/.venv/bin/bitbucket_mcp
```

## Project layout

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
.github/workflows/
  ci.yml                                # lint + format check + pytest matrix
```
