from __future__ import annotations

from typing import Any

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from bitbucket_mcp.bitbucket.client import Client

mcp = FastMCP("bitbucket_mcp")


@mcp.tool()
def current_user() -> dict:
    """Return the authenticated Bitbucket user.

    Useful as a connectivity smoke test before calling other tools.
    """
    return Client().current_user()


@mcp.tool()
def list_pull_requests_for_commit(
    workspace: str,
    repository: str,
    commit: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List pull requests that contain a given commit."""
    return Client().list_pull_requests_for_commit(
        workspace=workspace,
        repository=repository,
        commit=commit,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_pull_requests(
    workspace: str,
    repository: str,
    state: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List pull requests for a repository.

    Args:
        state: Filter by state (OPEN, MERGED, DECLINED, SUPERSEDED). Can be passed
            multiple times separated by commas.
        q: BBQL query (e.g. 'state="OPEN" AND author.uuid="..."').
        sort: Field to sort by (e.g. '-updated_on').
    """
    return Client().list_pull_requests(
        workspace=workspace,
        repository=repository,
        state=state,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_pull_request(
    workspace: str,
    repository: str,
    title: str,
    source_branch: str,
    destination_branch: str = "main",
    description: str | None = None,
    close_source_branch: bool | None = None,
    reviewers: list[str] | None = None,
) -> dict:
    """Create a pull request in Bitbucket Cloud.

    Args:
        workspace: Bitbucket workspace slug (the team or user owning the repo).
        repository: Repository slug.
        title: Pull request title.
        source_branch: Branch containing the new changes.
        destination_branch: Branch to merge into. Defaults to "main".
        description: Optional pull request description (markdown supported).
        close_source_branch: If true, source branch is deleted after merge.
        reviewers: Optional list of reviewer UUIDs.
    """
    return Client().create_pull_request(
        workspace=workspace,
        repository=repository,
        title=title,
        source_branch=source_branch,
        destination_branch=destination_branch,
        description=description,
        close_source_branch=close_source_branch,
        reviewers=reviewers,
    )


@mcp.tool()
def list_repository_pull_request_activity(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List activity (approvals, comments, etc.) across all PRs in a repository."""
    return Client().list_repository_pull_request_activity(
        workspace=workspace,
        repository=repository,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_pull_request(workspace: str, repository: str, pull_request_id: int) -> dict:
    """Fetch a single pull request by id."""
    return Client().get_pull_request(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def update_pull_request(
    workspace: str,
    repository: str,
    pull_request_id: int,
    title: str | None = None,
    description: str | None = None,
    destination_branch: str | None = None,
    reviewers: list[str] | None = None,
) -> dict:
    """Update a pull request's title, description, destination, or reviewers."""
    return Client().update_pull_request(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        title=title,
        description=description,
        destination_branch=destination_branch,
        reviewers=reviewers,
    )


@mcp.tool()
def list_pull_request_activity(
    workspace: str,
    repository: str,
    pull_request_id: int,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List activity (approvals, comments, etc.) for a single PR."""
    return Client().list_pull_request_activity(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def approve_pull_request(workspace: str, repository: str, pull_request_id: int) -> dict:
    """Approve a pull request as the authenticated user."""
    return Client().approve_pull_request(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def unapprove_pull_request(workspace: str, repository: str, pull_request_id: int) -> dict:
    """Remove the authenticated user's approval from a PR."""
    return Client().unapprove_pull_request(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def request_changes(workspace: str, repository: str, pull_request_id: int) -> dict:
    """Mark a PR as requesting changes."""
    return Client().request_changes(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def remove_request_changes(workspace: str, repository: str, pull_request_id: int) -> dict:
    """Remove the authenticated user's request-changes status from a PR."""
    return Client().remove_request_changes(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def list_pull_request_comments(
    workspace: str,
    repository: str,
    pull_request_id: int,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List comments on a pull request."""
    return Client().list_pull_request_comments(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_pull_request_comment(
    workspace: str,
    repository: str,
    pull_request_id: int,
    content: str,
    parent_id: int | None = None,
    inline_path: str | None = None,
    inline_to: int | None = None,
    inline_from: int | None = None,
) -> dict:
    """Add a comment to a pull request.

    Args:
        content: Comment body in markdown.
        parent_id: Parent comment id to reply to.
        inline_path: File path for an inline comment.
        inline_to: Line number in the destination (new) file.
        inline_from: Line number in the source (old) file.
    """
    return Client().create_pull_request_comment(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        content=content,
        parent_id=parent_id,
        inline_path=inline_path,
        inline_to=inline_to,
        inline_from=inline_from,
    )


@mcp.tool()
def get_pull_request_comment(
    workspace: str,
    repository: str,
    pull_request_id: int,
    comment_id: int,
) -> dict:
    """Fetch a single comment on a pull request."""
    return Client().get_pull_request_comment(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        comment_id=comment_id,
    )


@mcp.tool()
def update_pull_request_comment(
    workspace: str,
    repository: str,
    pull_request_id: int,
    comment_id: int,
    content: str,
) -> dict:
    """Edit an existing pull request comment."""
    return Client().update_pull_request_comment(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        comment_id=comment_id,
        content=content,
    )


@mcp.tool()
def delete_pull_request_comment(
    workspace: str,
    repository: str,
    pull_request_id: int,
    comment_id: int,
) -> dict:
    """Delete a pull request comment."""
    return Client().delete_pull_request_comment(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        comment_id=comment_id,
    )


@mcp.tool()
def resolve_pull_request_comment(
    workspace: str,
    repository: str,
    pull_request_id: int,
    comment_id: int,
) -> dict:
    """Mark a pull request comment as resolved."""
    return Client().resolve_pull_request_comment(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        comment_id=comment_id,
    )


@mcp.tool()
def reopen_pull_request_comment(
    workspace: str,
    repository: str,
    pull_request_id: int,
    comment_id: int,
) -> dict:
    """Reopen a previously-resolved pull request comment."""
    return Client().reopen_pull_request_comment(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        comment_id=comment_id,
    )


@mcp.tool()
def list_pull_request_commits(
    workspace: str,
    repository: str,
    pull_request_id: int,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List commits on a pull request."""
    return Client().list_pull_request_commits(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_pull_request_conflicts(
    workspace: str,
    repository: str,
    pull_request_id: int,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List merge conflicts for a pull request."""
    return Client().list_pull_request_conflicts(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def decline_pull_request(workspace: str, repository: str, pull_request_id: int) -> dict:
    """Decline a pull request."""
    return Client().decline_pull_request(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def get_pull_request_diff(
    workspace: str,
    repository: str,
    pull_request_id: int,
) -> str:
    """Return the raw unified diff for a pull request."""
    return Client().get_pull_request_diff(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def get_pull_request_diffstat(
    workspace: str,
    repository: str,
    pull_request_id: int,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """Return per-file diff stats for a pull request."""
    return Client().get_pull_request_diffstat(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def merge_pull_request(
    workspace: str,
    repository: str,
    pull_request_id: int,
    message: str | None = None,
    close_source_branch: bool | None = None,
    merge_strategy: str | None = None,
    async_: bool | None = None,
) -> dict:
    """Merge a pull request.

    Args:
        message: Optional merge commit message.
        close_source_branch: Delete the source branch after merging.
        merge_strategy: One of "merge_commit", "squash", "fast_forward".
        async_: If true, perform the merge asynchronously and return a task id.
    """
    return Client().merge_pull_request(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        message=message,
        close_source_branch=close_source_branch,
        merge_strategy=merge_strategy,
        async_=async_,
    )


@mcp.tool()
def get_merge_task_status(
    workspace: str,
    repository: str,
    pull_request_id: int,
    task_id: str,
) -> dict:
    """Poll the status of an asynchronous merge task."""
    return Client().get_merge_task_status(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        task_id=task_id,
    )


@mcp.tool()
def get_pull_request_patch(
    workspace: str,
    repository: str,
    pull_request_id: int,
) -> str:
    """Return the raw patch (git-format-patch output) for a pull request."""
    return Client().get_pull_request_patch(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
    )


@mcp.tool()
def list_pull_request_statuses(
    workspace: str,
    repository: str,
    pull_request_id: int,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List build statuses attached to a pull request."""
    return Client().list_pull_request_statuses(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_pull_request_tasks(
    workspace: str,
    repository: str,
    pull_request_id: int,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List tasks (action items) on a pull request."""
    return Client().list_pull_request_tasks(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_pull_request_task(
    workspace: str,
    repository: str,
    pull_request_id: int,
    content: str,
    comment_id: int | None = None,
    pending: bool | None = None,
) -> dict:
    """Create a task on a pull request, optionally anchored to a comment."""
    return Client().create_pull_request_task(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        content=content,
        comment_id=comment_id,
        pending=pending,
    )


@mcp.tool()
def get_pull_request_task(
    workspace: str,
    repository: str,
    pull_request_id: int,
    task_id: int,
) -> dict:
    """Fetch a single task on a pull request."""
    return Client().get_pull_request_task(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        task_id=task_id,
    )


@mcp.tool()
def update_pull_request_task(
    workspace: str,
    repository: str,
    pull_request_id: int,
    task_id: int,
    content: str | None = None,
    state: str | None = None,
) -> dict:
    """Update a task's content or state ("RESOLVED"/"UNRESOLVED")."""
    return Client().update_pull_request_task(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        task_id=task_id,
        content=content,
        state=state,
    )


@mcp.tool()
def delete_pull_request_task(
    workspace: str,
    repository: str,
    pull_request_id: int,
    task_id: int,
) -> dict:
    """Delete a task from a pull request."""
    return Client().delete_pull_request_task(
        workspace=workspace,
        repository=repository,
        pull_request_id=pull_request_id,
        task_id=task_id,
    )


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------


@mcp.tool()
def list_user_workspace_permissions(
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List the caller's workspace memberships (deprecated; use list_user_workspaces)."""
    return Client().list_user_workspace_permissions(q=q, sort=sort, page=page, pagelen=pagelen)


@mcp.tool()
def list_user_workspaces(
    sort: str | None = None,
    administrator: bool | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List workspaces accessible to the caller.

    Args:
        sort: Only "slug" is supported.
        administrator: If true, restrict to workspaces the caller administers.
    """
    return Client().list_user_workspaces(
        sort=sort, administrator=administrator, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_user_workspace_permission(workspace: str) -> dict:
    """Get the caller's effective role on a workspace."""
    return Client().get_user_workspace_permission(workspace=workspace)


@mcp.tool()
def list_workspaces(
    role: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List workspaces for the caller (deprecated; use list_user_workspaces).

    Args:
        role: Filter by role ("owner", "collaborator", "member").
    """
    return Client().list_workspaces(role=role, q=q, sort=sort, page=page, pagelen=pagelen)


@mcp.tool()
def get_workspace(workspace: str) -> dict:
    """Get a workspace by slug or UUID."""
    return Client().get_workspace(workspace=workspace)


@mcp.tool()
def list_workspace_webhooks(
    workspace: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List webhook subscriptions on a workspace."""
    return Client().list_workspace_webhooks(workspace=workspace, page=page, pagelen=pagelen)


@mcp.tool()
def create_workspace_webhook(
    workspace: str,
    url: str,
    events: list[str],
    description: str | None = None,
    active: bool | None = None,
    secret: str | None = None,
) -> dict:
    """Create a workspace-level webhook.

    Args:
        url: Endpoint that Bitbucket will POST events to.
        events: Event keys (e.g. ["repo:push", "pullrequest:created"]).
        secret: Used to sign payloads with HMAC.
    """
    return Client().create_workspace_webhook(
        workspace=workspace,
        url=url,
        events=events,
        description=description,
        active=active,
        secret=secret,
    )


@mcp.tool()
def delete_workspace_webhook(workspace: str, uid: str) -> dict:
    """Delete a workspace webhook by UUID."""
    return Client().delete_workspace_webhook(workspace=workspace, uid=uid)


@mcp.tool()
def get_workspace_webhook(workspace: str, uid: str) -> dict:
    """Get a workspace webhook by UUID."""
    return Client().get_workspace_webhook(workspace=workspace, uid=uid)


@mcp.tool()
def update_workspace_webhook(
    workspace: str,
    uid: str,
    url: str | None = None,
    events: list[str] | None = None,
    description: str | None = None,
    active: bool | None = None,
    secret: str | None = None,
) -> dict:
    """Update a workspace webhook."""
    return Client().update_workspace_webhook(
        workspace=workspace,
        uid=uid,
        url=url,
        events=events,
        description=description,
        active=active,
        secret=secret,
    )


@mcp.tool()
def list_workspace_members(
    workspace: str,
    q: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List members of a workspace.

    Args:
        q: BBQL filter (admin/integration callers can filter by user.email).
    """
    return Client().list_workspace_members(workspace=workspace, q=q, page=page, pagelen=pagelen)


@mcp.tool()
def get_workspace_member(workspace: str, member: str) -> dict:
    """Get a single workspace membership.

    Args:
        member: UUID or Atlassian Account ID of the user.
    """
    return Client().get_workspace_member(workspace=workspace, member=member)


@mcp.tool()
def list_workspace_permissions(
    workspace: str,
    q: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List per-user permissions in a workspace."""
    return Client().list_workspace_permissions(workspace=workspace, q=q, page=page, pagelen=pagelen)


@mcp.tool()
def list_workspace_repository_permissions(
    workspace: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List effective repository permissions for every user across the workspace."""
    return Client().list_workspace_repository_permissions(
        workspace=workspace, q=q, sort=sort, page=page, pagelen=pagelen
    )


@mcp.tool()
def list_workspace_repository_permissions_for_repo(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List per-user repository permissions for a single repository."""
    return Client().list_workspace_repository_permissions_for_repo(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_workspace_projects(
    workspace: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List projects in a workspace."""
    return Client().list_workspace_projects(workspace=workspace, page=page, pagelen=pagelen)


@mcp.tool()
def get_workspace_project(workspace: str, project_key: str) -> dict:
    """Get a project by its key."""
    return Client().get_workspace_project(workspace=workspace, project_key=project_key)


@mcp.tool()
def list_workspace_user_pull_requests(
    workspace: str,
    selected_user: str,
    state: str | list[str] | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List pull requests across a workspace authored by a user.

    Args:
        selected_user: Username, UUID, or Atlassian Account ID.
        state: One state or a list of states (OPEN, MERGED, DECLINED, SUPERSEDED).
    """
    return Client().list_workspace_user_pull_requests(
        workspace=workspace,
        selected_user=selected_user,
        state=state,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_workspace_gpg_key(workspace: str) -> dict:
    """Get the workspace system GPG public key(s)."""
    return Client().get_workspace_gpg_key(workspace=workspace)


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------


@mcp.tool()
def list_public_repositories(
    after: str | None = None,
    role: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List public repositories (deprecated; prefer workspace-scoped variant)."""
    return Client().list_public_repositories(
        after=after, role=role, q=q, sort=sort, page=page, pagelen=pagelen
    )


@mcp.tool()
def list_repositories(
    workspace: str,
    role: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List repositories in a workspace."""
    return Client().list_repositories(
        workspace=workspace, role=role, q=q, sort=sort, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_repository(workspace: str, repository: str) -> dict:
    """Get a repository by slug."""
    return Client().get_repository(workspace=workspace, repository=repository)


@mcp.tool()
def create_repository(
    workspace: str,
    repository: str,
    scm: str | None = None,
    name: str | None = None,
    description: str | None = None,
    is_private: bool | None = None,
    fork_policy: str | None = None,
    language: str | None = None,
    has_issues: bool | None = None,
    has_wiki: bool | None = None,
    project_key: str | None = None,
    mainbranch_name: str | None = None,
) -> dict:
    """Create a repository at the given workspace/repo_slug.

    Args:
        scm: Always "git".
        fork_policy: "allow_forks" | "no_public_forks" | "no_forks".
        project_key: Workspace project key (e.g. "MARS").
        mainbranch_name: Name of the default branch.
    """
    return Client().create_repository(
        workspace=workspace,
        repository=repository,
        scm=scm,
        name=name,
        description=description,
        is_private=is_private,
        fork_policy=fork_policy,
        language=language,
        has_issues=has_issues,
        has_wiki=has_wiki,
        project_key=project_key,
        mainbranch_name=mainbranch_name,
    )


@mcp.tool()
def update_repository(
    workspace: str,
    repository: str,
    name: str | None = None,
    description: str | None = None,
    is_private: bool | None = None,
    fork_policy: str | None = None,
    language: str | None = None,
    has_issues: bool | None = None,
    has_wiki: bool | None = None,
    project_key: str | None = None,
    mainbranch_name: str | None = None,
) -> dict:
    """Update repository metadata (may also create if absent)."""
    return Client().update_repository(
        workspace=workspace,
        repository=repository,
        name=name,
        description=description,
        is_private=is_private,
        fork_policy=fork_policy,
        language=language,
        has_issues=has_issues,
        has_wiki=has_wiki,
        project_key=project_key,
        mainbranch_name=mainbranch_name,
    )


@mcp.tool()
def delete_repository(
    workspace: str,
    repository: str,
    redirect_to: str | None = None,
) -> dict:
    """Delete a repository. Pass redirect_to to send visitors to a friendly URL."""
    return Client().delete_repository(
        workspace=workspace, repository=repository, redirect_to=redirect_to
    )


@mcp.tool()
def list_file_history(
    workspace: str,
    repository: str,
    commit: str,
    path: str,
    renames: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List commits that modified a file.

    Args:
        renames: "true" or "false" — whether to follow renames (default "true").
    """
    return Client().list_file_history(
        workspace=workspace,
        repository=repository,
        commit=commit,
        path=path,
        renames=renames,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_repository_forks(
    workspace: str,
    repository: str,
    role: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List forks of a repository."""
    return Client().list_repository_forks(
        workspace=workspace,
        repository=repository,
        role=role,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def fork_repository(
    workspace: str,
    repository: str,
    name: str | None = None,
    destination_workspace: str | None = None,
    is_private: bool | None = None,
    description: str | None = None,
    project_key: str | None = None,
    fork_policy: str | None = None,
    language: str | None = None,
) -> dict:
    """Fork a repository.

    Args:
        destination_workspace: Workspace slug for the new fork (defaults to source).
        name: Required when forking to the same workspace.
    """
    return Client().fork_repository(
        workspace=workspace,
        repository=repository,
        name=name,
        destination_workspace=destination_workspace,
        is_private=is_private,
        description=description,
        project_key=project_key,
        fork_policy=fork_policy,
        language=language,
    )


@mcp.tool()
def list_repository_webhooks(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List webhooks for a repository."""
    return Client().list_repository_webhooks(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_repository_webhook(
    workspace: str,
    repository: str,
    url: str,
    events: list[str],
    description: str | None = None,
    active: bool | None = None,
    secret: str | None = None,
) -> dict:
    """Create a repository-level webhook."""
    return Client().create_repository_webhook(
        workspace=workspace,
        repository=repository,
        url=url,
        events=events,
        description=description,
        active=active,
        secret=secret,
    )


@mcp.tool()
def delete_repository_webhook(workspace: str, repository: str, uid: str) -> dict:
    """Delete a repository webhook."""
    return Client().delete_repository_webhook(workspace=workspace, repository=repository, uid=uid)


@mcp.tool()
def get_repository_webhook(workspace: str, repository: str, uid: str) -> dict:
    """Get a repository webhook."""
    return Client().get_repository_webhook(workspace=workspace, repository=repository, uid=uid)


@mcp.tool()
def update_repository_webhook(
    workspace: str,
    repository: str,
    uid: str,
    url: str | None = None,
    events: list[str] | None = None,
    description: str | None = None,
    active: bool | None = None,
    secret: str | None = None,
) -> dict:
    """Update a repository webhook."""
    return Client().update_repository_webhook(
        workspace=workspace,
        repository=repository,
        uid=uid,
        url=url,
        events=events,
        description=description,
        active=active,
        secret=secret,
    )


@mcp.tool()
def get_repository_override_settings(workspace: str, repository: str) -> dict:
    """Get inheritance overrides on repository settings."""
    return Client().get_repository_override_settings(workspace=workspace, repository=repository)


@mcp.tool()
def set_repository_override_settings(
    workspace: str,
    repository: str,
    settings: dict[str, bool],
) -> dict:
    """Set inheritance overrides on repository settings (admin only)."""
    return Client().set_repository_override_settings(
        workspace=workspace, repository=repository, settings=settings
    )


@mcp.tool()
def list_repository_group_permissions(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List explicit group permissions on a repository."""
    return Client().list_repository_group_permissions(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def delete_repository_group_permission(
    workspace: str,
    repository: str,
    group_slug: str,
) -> dict:
    """Delete an explicit group permission."""
    return Client().delete_repository_group_permission(
        workspace=workspace, repository=repository, group_slug=group_slug
    )


@mcp.tool()
def get_repository_group_permission(
    workspace: str,
    repository: str,
    group_slug: str,
) -> dict:
    """Get an explicit group permission."""
    return Client().get_repository_group_permission(
        workspace=workspace, repository=repository, group_slug=group_slug
    )


@mcp.tool()
def update_repository_group_permission(
    workspace: str,
    repository: str,
    group_slug: str,
    permission: str,
) -> dict:
    """Grant or update an explicit group permission ("read"/"write"/"admin")."""
    return Client().update_repository_group_permission(
        workspace=workspace,
        repository=repository,
        group_slug=group_slug,
        permission=permission,
    )


@mcp.tool()
def list_repository_user_permissions(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List explicit user permissions on a repository."""
    return Client().list_repository_user_permissions(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def delete_repository_user_permission(
    workspace: str,
    repository: str,
    selected_user_id: str,
) -> dict:
    """Delete an explicit user permission."""
    return Client().delete_repository_user_permission(
        workspace=workspace, repository=repository, selected_user_id=selected_user_id
    )


@mcp.tool()
def get_repository_user_permission(
    workspace: str,
    repository: str,
    selected_user_id: str,
) -> dict:
    """Get an explicit user permission."""
    return Client().get_repository_user_permission(
        workspace=workspace, repository=repository, selected_user_id=selected_user_id
    )


@mcp.tool()
def update_repository_user_permission(
    workspace: str,
    repository: str,
    selected_user_id: str,
    permission: str,
) -> dict:
    """Grant or update an explicit user permission ("read"/"write"/"admin")."""
    return Client().update_repository_user_permission(
        workspace=workspace,
        repository=repository,
        selected_user_id=selected_user_id,
        permission=permission,
    )


@mcp.tool()
def get_repository_root_src(
    workspace: str,
    repository: str,
    format: str | None = None,
) -> str:
    """Get the root src listing of the repository main branch.

    Args:
        format: Pass "meta" to receive JSON metadata instead of contents.
    """
    return Client().get_repository_root_src(
        workspace=workspace, repository=repository, format=format
    )


@mcp.tool()
def create_src_commit(
    workspace: str,
    repository: str,
    message: str | None = None,
    author: str | None = None,
    parents: str | None = None,
    branch: str | None = None,
    files_to_add: dict[str, str] | None = None,
    files_to_delete: list[str] | None = None,
) -> dict:
    """Create a commit by uploading/deleting files (multipart upload).

    Args:
        message: Commit message.
        author: e.g. "Name <email@host>".
        parents: Parent commit SHA1.
        branch: Branch to commit on. Pass a fresh name to create a new branch.
        files_to_add: Mapping of repo-relative path to file contents (text).
        files_to_delete: Repo-relative paths to remove in this commit.
    """
    files_bytes = (
        {path: content.encode("utf-8") for path, content in files_to_add.items()}
        if files_to_add
        else None
    )
    return Client().create_src_commit(
        workspace=workspace,
        repository=repository,
        message=message,
        author=author,
        parents=parents,
        branch=branch,
        files_to_add=files_bytes,
        files_to_delete=files_to_delete,
    )


@mcp.tool()
def get_repository_src(
    workspace: str,
    repository: str,
    commit: str,
    path: str,
    format: str | None = None,
    q: str | None = None,
    sort: str | None = None,
    max_depth: int | None = None,
) -> str:
    """Get a file or directory at a specific commit.

    Args:
        format: "meta" for JSON metadata, "rendered" for rendered HTML markup.
        max_depth: For directory listings, recursion depth (default 1).
    """
    return Client().get_repository_src(
        workspace=workspace,
        repository=repository,
        commit=commit,
        path=path,
        format=format,
        q=q,
        sort=sort,
        max_depth=max_depth,
    )


@mcp.tool()
def list_repository_watchers(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List users watching a repository."""
    return Client().list_repository_watchers(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def list_user_repository_permissions(
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List the caller's repository permissions (deprecated; prefer workspace-scoped variant)."""
    return Client().list_user_repository_permissions(q=q, sort=sort, page=page, pagelen=pagelen)


@mcp.tool()
def list_user_workspace_repository_permissions(
    workspace: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List the caller's repository permissions within a workspace."""
    return Client().list_user_workspace_repository_permissions(
        workspace=workspace, q=q, sort=sort, page=page, pagelen=pagelen
    )


# ---------------------------------------------------------------------------
# Commits
# ---------------------------------------------------------------------------


@mcp.tool()
def get_commit(workspace: str, repository: str, commit: str) -> dict:
    """Get a single commit by SHA."""
    return Client().get_commit(workspace=workspace, repository=repository, commit=commit)


@mcp.tool()
def approve_commit(workspace: str, repository: str, commit: str) -> dict:
    """Approve a commit as the authenticated user."""
    return Client().approve_commit(workspace=workspace, repository=repository, commit=commit)


@mcp.tool()
def unapprove_commit(workspace: str, repository: str, commit: str) -> dict:
    """Remove the authenticated user's approval from a commit."""
    return Client().unapprove_commit(workspace=workspace, repository=repository, commit=commit)


@mcp.tool()
def list_commit_comments(
    workspace: str,
    repository: str,
    commit: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List comments (global and inline) on a commit."""
    return Client().list_commit_comments(
        workspace=workspace,
        repository=repository,
        commit=commit,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_commit_comment(
    workspace: str,
    repository: str,
    commit: str,
    content: str,
    parent_id: int | None = None,
    inline_path: str | None = None,
    inline_to: int | None = None,
    inline_from: int | None = None,
) -> dict:
    """Add a comment to a commit.

    Args:
        parent_id: Reply to this comment id.
        inline_path: File path to anchor an inline comment.
        inline_to: Destination (new) line number.
        inline_from: Source (old) line number.
    """
    return Client().create_commit_comment(
        workspace=workspace,
        repository=repository,
        commit=commit,
        content=content,
        parent_id=parent_id,
        inline_path=inline_path,
        inline_to=inline_to,
        inline_from=inline_from,
    )


@mcp.tool()
def get_commit_comment(
    workspace: str,
    repository: str,
    commit: str,
    comment_id: int,
) -> dict:
    """Fetch a single commit comment."""
    return Client().get_commit_comment(
        workspace=workspace, repository=repository, commit=commit, comment_id=comment_id
    )


@mcp.tool()
def update_commit_comment(
    workspace: str,
    repository: str,
    commit: str,
    comment_id: int,
    content: str,
) -> dict:
    """Update the content of a commit comment."""
    return Client().update_commit_comment(
        workspace=workspace,
        repository=repository,
        commit=commit,
        comment_id=comment_id,
        content=content,
    )


@mcp.tool()
def delete_commit_comment(
    workspace: str,
    repository: str,
    commit: str,
    comment_id: int,
) -> dict:
    """Delete a commit comment (soft-delete if it has replies)."""
    return Client().delete_commit_comment(
        workspace=workspace, repository=repository, commit=commit, comment_id=comment_id
    )


@mcp.tool()
def list_commit_reports(
    workspace: str,
    repository: str,
    commit: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List Code Insights reports for a commit."""
    return Client().list_commit_reports(
        workspace=workspace,
        repository=repository,
        commit=commit,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_commit_report(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
) -> dict:
    """Get a single Code Insights report."""
    return Client().get_commit_report(
        workspace=workspace, repository=repository, commit=commit, report_id=report_id
    )


@mcp.tool()
def create_or_update_commit_report(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
    title: str | None = None,
    details: str | None = None,
    external_id: str | None = None,
    reporter: str | None = None,
    link: str | None = None,
    remote_link_enabled: bool | None = None,
    logo_url: str | None = None,
    report_type: str | None = None,
    result: str | None = None,
    data: list[dict[str, Any]] | None = None,
) -> dict:
    """Create or update a Code Insights report.

    Args:
        report_type: "SECURITY" | "COVERAGE" | "TEST" | "BUG".
        result: "PASSED" | "FAILED" | "PENDING".
        data: Up to 10 report_data items.
    """
    return Client().create_or_update_commit_report(
        workspace=workspace,
        repository=repository,
        commit=commit,
        report_id=report_id,
        title=title,
        details=details,
        external_id=external_id,
        reporter=reporter,
        link=link,
        remote_link_enabled=remote_link_enabled,
        logo_url=logo_url,
        report_type=report_type,
        result=result,
        data=data,
    )


@mcp.tool()
def delete_commit_report(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
) -> dict:
    """Delete a Code Insights report."""
    return Client().delete_commit_report(
        workspace=workspace, repository=repository, commit=commit, report_id=report_id
    )


@mcp.tool()
def list_commit_report_annotations(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List annotations attached to a Code Insights report."""
    return Client().list_commit_report_annotations(
        workspace=workspace,
        repository=repository,
        commit=commit,
        report_id=report_id,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def bulk_create_or_update_annotations(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
    annotations: list[dict[str, Any]],
) -> Any:
    """Bulk create or update report annotations (max 1000)."""
    return Client().bulk_create_or_update_annotations(
        workspace=workspace,
        repository=repository,
        commit=commit,
        report_id=report_id,
        annotations=annotations,
    )


@mcp.tool()
def get_commit_report_annotation(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
    annotation_id: str,
) -> dict:
    """Get a single annotation."""
    return Client().get_commit_report_annotation(
        workspace=workspace,
        repository=repository,
        commit=commit,
        report_id=report_id,
        annotation_id=annotation_id,
    )


@mcp.tool()
def create_or_update_commit_report_annotation(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
    annotation_id: str,
    external_id: str | None = None,
    annotation_type: str | None = None,
    path: str | None = None,
    line: int | None = None,
    summary: str | None = None,
    details: str | None = None,
    result: str | None = None,
    severity: str | None = None,
    link: str | None = None,
) -> dict:
    """Create or update a single annotation.

    Args:
        annotation_type: "VULNERABILITY" | "CODE_SMELL" | "BUG".
        result: "PASSED" | "FAILED" | "SKIPPED" | "IGNORED".
        severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW".
    """
    return Client().create_or_update_commit_report_annotation(
        workspace=workspace,
        repository=repository,
        commit=commit,
        report_id=report_id,
        annotation_id=annotation_id,
        external_id=external_id,
        annotation_type=annotation_type,
        path=path,
        line=line,
        summary=summary,
        details=details,
        result=result,
        severity=severity,
        link=link,
    )


@mcp.tool()
def delete_commit_report_annotation(
    workspace: str,
    repository: str,
    commit: str,
    report_id: str,
    annotation_id: str,
) -> dict:
    """Delete a single annotation."""
    return Client().delete_commit_report_annotation(
        workspace=workspace,
        repository=repository,
        commit=commit,
        report_id=report_id,
        annotation_id=annotation_id,
    )


@mcp.tool()
def list_commits(
    workspace: str,
    repository: str,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List commits in a repository (topological / reverse-chronological).

    Args:
        include: Refs to include (e.g. ["master"]).
        exclude: Refs to exclude.
    """
    return Client().list_commits(
        workspace=workspace,
        repository=repository,
        include=include,
        exclude=exclude,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_commits_with_filter(
    workspace: str,
    repository: str,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List commits via POST (use when include/exclude lists are too long for the URL)."""
    return Client().list_commits_with_filter(
        workspace=workspace,
        repository=repository,
        include=include,
        exclude=exclude,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_commits_for_revision(
    workspace: str,
    repository: str,
    revision: str,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    path: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List commits reachable from a revision (SHA or ref).

    Args:
        path: Limit to commits touching this path.
    """
    return Client().list_commits_for_revision(
        workspace=workspace,
        repository=repository,
        revision=revision,
        include=include,
        exclude=exclude,
        path=path,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_commits_for_revision_with_filter(
    workspace: str,
    repository: str,
    revision: str,
    include: list[str] | None = None,
    exclude: list[str] | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List commits reachable from a revision via POST (longer include/exclude lists)."""
    return Client().list_commits_for_revision_with_filter(
        workspace=workspace,
        repository=repository,
        revision=revision,
        include=include,
        exclude=exclude,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_diff(
    workspace: str,
    repository: str,
    spec: str,
    context: int | None = None,
    path: list[str] | str | None = None,
    ignore_whitespace: bool | None = None,
    binary: bool | None = None,
    renames: bool | None = None,
    merge: bool | None = None,
    topic: bool | None = None,
) -> str:
    """Get a raw git-style diff for a commit or range.

    Args:
        spec: Single SHA "abc123" or range "abc..def".
        context: Lines of context (default 3).
        path: Limit diff to one or more file paths.
    """
    return Client().get_diff(
        workspace=workspace,
        repository=repository,
        spec=spec,
        context=context,
        path=path,
        ignore_whitespace=ignore_whitespace,
        binary=binary,
        renames=renames,
        merge=merge,
        topic=topic,
    )


@mcp.tool()
def get_diffstat(
    workspace: str,
    repository: str,
    spec: str,
    ignore_whitespace: bool | None = None,
    merge: bool | None = None,
    path: list[str] | str | None = None,
    renames: bool | None = None,
    topic: bool | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """Get per-file diff stats for a commit or range."""
    return Client().get_diffstat(
        workspace=workspace,
        repository=repository,
        spec=spec,
        ignore_whitespace=ignore_whitespace,
        merge=merge,
        path=path,
        renames=renames,
        topic=topic,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_file_conflicts(
    workspace: str,
    repository: str,
    spec: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List file conflicts for a commit spec."""
    return Client().list_file_conflicts(
        workspace=workspace, repository=repository, spec=spec, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_merge_base(workspace: str, repository: str, revspec: str) -> dict:
    """Get the best common ancestor between two commits.

    Args:
        revspec: Must be a double-dot range (e.g. "abc..def").
    """
    return Client().get_merge_base(workspace=workspace, repository=repository, revspec=revspec)


@mcp.tool()
def get_patch(workspace: str, repository: str, spec: str) -> str:
    """Get a raw patch (single commit or patch-series for a range)."""
    return Client().get_patch(workspace=workspace, repository=repository, spec=spec)


def main() -> None:
    load_dotenv()
    mcp.run()


if __name__ == "__main__":
    main()
