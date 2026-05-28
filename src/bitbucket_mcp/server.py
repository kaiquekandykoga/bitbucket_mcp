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


# ---------------------------------------------------------------------------
# Pull request default reviewers
# ---------------------------------------------------------------------------


@mcp.tool()
def list_default_reviewers(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List default reviewers configured on a repository."""
    return Client().list_default_reviewers(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def list_effective_default_reviewers(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List effective default reviewers (repo + inherited from project)."""
    return Client().list_effective_default_reviewers(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_default_reviewer(workspace: str, repository: str, target_username: str) -> dict:
    """Get a default reviewer.

    Args:
        target_username: UUID or Atlassian Account ID of the reviewer.
    """
    return Client().get_default_reviewer(
        workspace=workspace, repository=repository, target_username=target_username
    )


@mcp.tool()
def add_default_reviewer(workspace: str, repository: str, target_username: str) -> dict:
    """Add a user to repository default reviewers."""
    return Client().add_default_reviewer(
        workspace=workspace, repository=repository, target_username=target_username
    )


@mcp.tool()
def remove_default_reviewer(workspace: str, repository: str, target_username: str) -> dict:
    """Remove a user from repository default reviewers."""
    return Client().remove_default_reviewer(
        workspace=workspace, repository=repository, target_username=target_username
    )


# ---------------------------------------------------------------------------
# Branch restrictions
# ---------------------------------------------------------------------------


@mcp.tool()
def list_branch_restrictions(
    workspace: str,
    repository: str,
    kind: str | None = None,
    pattern: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List branch restrictions for a repository.

    Args:
        kind: Restriction kind to filter by (e.g. "push", "force", "delete",
            "require_approvals_to_merge").
        pattern: Branch pattern to filter by.
    """
    return Client().list_branch_restrictions(
        workspace=workspace,
        repository=repository,
        kind=kind,
        pattern=pattern,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_branch_restriction(
    workspace: str,
    repository: str,
    kind: str,
    pattern: str | None = None,
    branch_match_kind: str | None = None,
    branch_type: str | None = None,
    users: list[str] | None = None,
    groups: list[dict[str, Any]] | None = None,
    value: int | None = None,
) -> dict:
    """Create a branch restriction.

    Args:
        kind: Restriction kind (e.g. "push", "force", "delete",
            "require_approvals_to_merge").
        pattern: Glob pattern matching the branches.
        branch_match_kind: "glob" or "branching_model".
        branch_type: Branch type when branch_match_kind is "branching_model".
        users: UUIDs of exempt users.
        groups: Group references (with slug/owner) that are exempt.
        value: Integer value (e.g. number of required approvals).
    """
    return Client().create_branch_restriction(
        workspace=workspace,
        repository=repository,
        kind=kind,
        pattern=pattern,
        branch_match_kind=branch_match_kind,
        branch_type=branch_type,
        users=users,
        groups=groups,
        value=value,
    )


@mcp.tool()
def get_branch_restriction(workspace: str, repository: str, id: int) -> dict:
    """Get a branch restriction by id."""
    return Client().get_branch_restriction(workspace=workspace, repository=repository, id=id)


@mcp.tool()
def update_branch_restriction(
    workspace: str,
    repository: str,
    id: int,
    kind: str | None = None,
    pattern: str | None = None,
    branch_match_kind: str | None = None,
    branch_type: str | None = None,
    users: list[str] | None = None,
    groups: list[dict[str, Any]] | None = None,
    value: int | None = None,
) -> dict:
    """Update a branch restriction."""
    return Client().update_branch_restriction(
        workspace=workspace,
        repository=repository,
        id=id,
        kind=kind,
        pattern=pattern,
        branch_match_kind=branch_match_kind,
        branch_type=branch_type,
        users=users,
        groups=groups,
        value=value,
    )


@mcp.tool()
def delete_branch_restriction(workspace: str, repository: str, id: int) -> dict:
    """Delete a branch restriction."""
    return Client().delete_branch_restriction(workspace=workspace, repository=repository, id=id)


# ---------------------------------------------------------------------------
# Branching model
# ---------------------------------------------------------------------------


@mcp.tool()
def get_branching_model(workspace: str, repository: str) -> dict:
    """Get the branching model for a repository."""
    return Client().get_branching_model(workspace=workspace, repository=repository)


@mcp.tool()
def get_effective_branching_model(workspace: str, repository: str) -> dict:
    """Get the effective branching model (after project inheritance)."""
    return Client().get_effective_branching_model(workspace=workspace, repository=repository)


@mcp.tool()
def get_branching_model_settings(workspace: str, repository: str) -> dict:
    """Get branching model settings for a repository."""
    return Client().get_branching_model_settings(workspace=workspace, repository=repository)


@mcp.tool()
def update_branching_model_settings(
    workspace: str,
    repository: str,
    development: dict[str, Any] | None = None,
    production: dict[str, Any] | None = None,
    branch_types: list[dict[str, Any]] | None = None,
) -> dict:
    """Update branching model settings.

    Args:
        development: Configuration for the development branch (e.g.
            ``{"use_mainbranch": True}`` or ``{"name": "develop"}``).
        production: Configuration for the production branch (or
            ``{"enabled": False}`` to disable).
        branch_types: List of ``{"kind": ..., "enabled": ..., "prefix": ...}``
            entries.
    """
    return Client().update_branching_model_settings(
        workspace=workspace,
        repository=repository,
        development=development,
        production=production,
        branch_types=branch_types,
    )


@mcp.tool()
def get_project_branching_model(workspace: str, project_key: str) -> dict:
    """Get the project-level branching model."""
    return Client().get_project_branching_model(workspace=workspace, project_key=project_key)


@mcp.tool()
def get_project_branching_model_settings(workspace: str, project_key: str) -> dict:
    """Get the project-level branching model settings."""
    return Client().get_project_branching_model_settings(
        workspace=workspace, project_key=project_key
    )


@mcp.tool()
def update_project_branching_model_settings(
    workspace: str,
    project_key: str,
    development: dict[str, Any] | None = None,
    production: dict[str, Any] | None = None,
    branch_types: list[dict[str, Any]] | None = None,
) -> dict:
    """Update project-level branching model settings."""
    return Client().update_project_branching_model_settings(
        workspace=workspace,
        project_key=project_key,
        development=development,
        production=production,
        branch_types=branch_types,
    )


# ---------------------------------------------------------------------------
# Commit build statuses
# ---------------------------------------------------------------------------


@mcp.tool()
def list_commit_statuses(
    workspace: str,
    repository: str,
    commit: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List build statuses attached to a commit."""
    return Client().list_commit_statuses(
        workspace=workspace,
        repository=repository,
        commit=commit,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_commit_build_status(
    workspace: str,
    repository: str,
    commit: str,
    key: str,
    state: str,
    url: str,
    name: str | None = None,
    description: str | None = None,
    refname: str | None = None,
) -> dict:
    """Create a build status for a commit.

    Args:
        key: Unique key for the status (e.g. CI job name).
        state: "INPROGRESS", "SUCCESSFUL", "FAILED", or "STOPPED".
        url: Link to the external build.
        refname: Branch name (for branch-specific statuses).
    """
    return Client().create_commit_build_status(
        workspace=workspace,
        repository=repository,
        commit=commit,
        key=key,
        state=state,
        url=url,
        name=name,
        description=description,
        refname=refname,
    )


@mcp.tool()
def get_commit_build_status(
    workspace: str,
    repository: str,
    commit: str,
    key: str,
) -> dict:
    """Get a build status by key."""
    return Client().get_commit_build_status(
        workspace=workspace, repository=repository, commit=commit, key=key
    )


@mcp.tool()
def update_commit_build_status(
    workspace: str,
    repository: str,
    commit: str,
    key: str,
    state: str | None = None,
    url: str | None = None,
    name: str | None = None,
    description: str | None = None,
    refname: str | None = None,
) -> dict:
    """Update an existing build status."""
    return Client().update_commit_build_status(
        workspace=workspace,
        repository=repository,
        commit=commit,
        key=key,
        state=state,
        url=url,
        name=name,
        description=description,
        refname=refname,
    )


# ---------------------------------------------------------------------------
# Deploy keys
# ---------------------------------------------------------------------------


@mcp.tool()
def list_deploy_keys(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List deploy keys for a repository."""
    return Client().list_deploy_keys(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_deploy_key(
    workspace: str,
    repository: str,
    key: str,
    label: str | None = None,
) -> dict:
    """Add a deploy key to a repository."""
    return Client().create_deploy_key(
        workspace=workspace, repository=repository, key=key, label=label
    )


@mcp.tool()
def get_deploy_key(workspace: str, repository: str, key_id: str) -> dict:
    """Get a repository deploy key."""
    return Client().get_deploy_key(workspace=workspace, repository=repository, key_id=key_id)


@mcp.tool()
def update_deploy_key(
    workspace: str,
    repository: str,
    key_id: str,
    label: str | None = None,
    key: str | None = None,
) -> dict:
    """Update a repository deploy key."""
    return Client().update_deploy_key(
        workspace=workspace,
        repository=repository,
        key_id=key_id,
        label=label,
        key=key,
    )


@mcp.tool()
def delete_deploy_key(workspace: str, repository: str, key_id: str) -> dict:
    """Delete a repository deploy key."""
    return Client().delete_deploy_key(workspace=workspace, repository=repository, key_id=key_id)


@mcp.tool()
def list_project_deploy_keys(
    workspace: str,
    project_key: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List deploy keys for a project."""
    return Client().list_project_deploy_keys(
        workspace=workspace, project_key=project_key, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_project_deploy_key(
    workspace: str,
    project_key: str,
    key: str,
    label: str | None = None,
) -> dict:
    """Add a deploy key to a project."""
    return Client().create_project_deploy_key(
        workspace=workspace, project_key=project_key, key=key, label=label
    )


@mcp.tool()
def get_project_deploy_key(workspace: str, project_key: str, key_id: str) -> dict:
    """Get a project deploy key."""
    return Client().get_project_deploy_key(
        workspace=workspace, project_key=project_key, key_id=key_id
    )


@mcp.tool()
def delete_project_deploy_key(workspace: str, project_key: str, key_id: str) -> dict:
    """Delete a project deploy key."""
    return Client().delete_project_deploy_key(
        workspace=workspace, project_key=project_key, key_id=key_id
    )


# ---------------------------------------------------------------------------
# Deployments & environments
# ---------------------------------------------------------------------------


@mcp.tool()
def list_deployments(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List deployments for a repository."""
    return Client().list_deployments(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_deployment(workspace: str, repository: str, deployment_uuid: str) -> dict:
    """Get a single deployment."""
    return Client().get_deployment(
        workspace=workspace, repository=repository, deployment_uuid=deployment_uuid
    )


@mcp.tool()
def list_environments(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List deployment environments for a repository."""
    return Client().list_environments(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_environment(
    workspace: str,
    repository: str,
    name: str,
    environment_type: dict[str, Any] | None = None,
    rank: int | None = None,
) -> dict:
    """Create a deployment environment.

    Args:
        environment_type: e.g. ``{"name": "Production"}``.
        rank: Ordering position.
    """
    return Client().create_environment(
        workspace=workspace,
        repository=repository,
        name=name,
        environment_type=environment_type,
        rank=rank,
    )


@mcp.tool()
def get_environment(workspace: str, repository: str, environment_uuid: str) -> dict:
    """Get a deployment environment by UUID."""
    return Client().get_environment(
        workspace=workspace, repository=repository, environment_uuid=environment_uuid
    )


@mcp.tool()
def update_environment(
    workspace: str,
    repository: str,
    environment_uuid: str,
    body: dict[str, Any] | None = None,
) -> dict:
    """Update a deployment environment (POST .../changes)."""
    return Client().update_environment(
        workspace=workspace,
        repository=repository,
        environment_uuid=environment_uuid,
        body=body,
    )


@mcp.tool()
def delete_environment(workspace: str, repository: str, environment_uuid: str) -> dict:
    """Delete a deployment environment."""
    return Client().delete_environment(
        workspace=workspace, repository=repository, environment_uuid=environment_uuid
    )


# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------


@mcp.tool()
def list_downloads(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List downloads attached to a repository."""
    return Client().list_downloads(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def upload_download(
    workspace: str,
    repository: str,
    files: dict[str, str],
) -> dict:
    """Upload one or more files to repository downloads.

    Args:
        files: Mapping of ``{filename: text_content}``.
    """
    files_bytes = {name: content.encode("utf-8") for name, content in files.items()}
    return Client().upload_download(workspace=workspace, repository=repository, files=files_bytes)


@mcp.tool()
def get_download(workspace: str, repository: str, filename: str) -> str:
    """Get a download (returns raw bytes as text)."""
    return Client().get_download(workspace=workspace, repository=repository, filename=filename)


@mcp.tool()
def delete_download(workspace: str, repository: str, filename: str) -> dict:
    """Delete a download artifact."""
    return Client().delete_download(workspace=workspace, repository=repository, filename=filename)


# ---------------------------------------------------------------------------
# GPG keys
# ---------------------------------------------------------------------------


@mcp.tool()
def list_user_gpg_keys(
    selected_user: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List a user's GPG keys."""
    return Client().list_user_gpg_keys(selected_user=selected_user, page=page, pagelen=pagelen)


@mcp.tool()
def create_user_gpg_key(
    selected_user: str,
    key: str,
    name: str | None = None,
) -> dict:
    """Add a GPG key to a user."""
    return Client().create_user_gpg_key(selected_user=selected_user, key=key, name=name)


@mcp.tool()
def get_user_gpg_key(selected_user: str, fingerprint: str) -> dict:
    """Get a single GPG key by fingerprint."""
    return Client().get_user_gpg_key(selected_user=selected_user, fingerprint=fingerprint)


@mcp.tool()
def delete_user_gpg_key(selected_user: str, fingerprint: str) -> dict:
    """Delete a GPG key."""
    return Client().delete_user_gpg_key(selected_user=selected_user, fingerprint=fingerprint)


# ---------------------------------------------------------------------------
# Issue tracker
# ---------------------------------------------------------------------------


@mcp.tool()
def list_components(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List issue tracker components."""
    return Client().list_components(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_component(workspace: str, repository: str, component_id: int) -> dict:
    """Get a single issue tracker component."""
    return Client().get_component(
        workspace=workspace, repository=repository, component_id=component_id
    )


@mcp.tool()
def list_milestones(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List issue tracker milestones."""
    return Client().list_milestones(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_milestone(workspace: str, repository: str, milestone_id: int) -> dict:
    """Get a single issue tracker milestone."""
    return Client().get_milestone(
        workspace=workspace, repository=repository, milestone_id=milestone_id
    )


@mcp.tool()
def list_versions(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List issue tracker versions."""
    return Client().list_versions(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_version(workspace: str, repository: str, version_id: int) -> dict:
    """Get a single issue tracker version."""
    return Client().get_version(workspace=workspace, repository=repository, version_id=version_id)


@mcp.tool()
def list_issues(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List issues for a repository."""
    return Client().list_issues(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_issue(
    workspace: str,
    repository: str,
    title: str,
    content: str | None = None,
    kind: str | None = None,
    priority: str | None = None,
    state: str | None = None,
    component: str | None = None,
    milestone: str | None = None,
    version: str | None = None,
    assignee: str | None = None,
) -> dict:
    """Create an issue.

    Args:
        kind: "bug" | "enhancement" | "proposal" | "task".
        priority: "trivial" | "minor" | "major" | "critical" | "blocker".
        state: "new" | "open" | "resolved" | "on hold" | "invalid" |
            "duplicate" | "wontfix" | "closed".
        assignee: User UUID.
    """
    return Client().create_issue(
        workspace=workspace,
        repository=repository,
        title=title,
        content=content,
        kind=kind,
        priority=priority,
        state=state,
        component=component,
        milestone=milestone,
        version=version,
        assignee=assignee,
    )


@mcp.tool()
def get_issue(workspace: str, repository: str, issue_id: int) -> dict:
    """Get a single issue."""
    return Client().get_issue(workspace=workspace, repository=repository, issue_id=issue_id)


@mcp.tool()
def update_issue(
    workspace: str,
    repository: str,
    issue_id: int,
    title: str | None = None,
    content: str | None = None,
    kind: str | None = None,
    priority: str | None = None,
    state: str | None = None,
    component: str | None = None,
    milestone: str | None = None,
    version: str | None = None,
    assignee: str | None = None,
) -> dict:
    """Update an issue."""
    return Client().update_issue(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        title=title,
        content=content,
        kind=kind,
        priority=priority,
        state=state,
        component=component,
        milestone=milestone,
        version=version,
        assignee=assignee,
    )


@mcp.tool()
def delete_issue(workspace: str, repository: str, issue_id: int) -> dict:
    """Delete an issue."""
    return Client().delete_issue(workspace=workspace, repository=repository, issue_id=issue_id)


@mcp.tool()
def export_issues(workspace: str, repository: str) -> dict:
    """Start an export of the repository issues (returns a task)."""
    return Client().export_issues(workspace=workspace, repository=repository)


@mcp.tool()
def get_issue_export(
    workspace: str,
    repository: str,
    repo_name: str,
    task_id: str,
) -> str:
    """Download a previously-generated issue export zip."""
    return Client().get_issue_export(
        workspace=workspace,
        repository=repository,
        repo_name=repo_name,
        task_id=task_id,
    )


@mcp.tool()
def get_issue_import_status(workspace: str, repository: str) -> dict:
    """Get the status of the most recent issue import."""
    return Client().get_issue_import_status(workspace=workspace, repository=repository)


@mcp.tool()
def import_issues(workspace: str, repository: str) -> dict:
    """Start an issue import."""
    return Client().import_issues(workspace=workspace, repository=repository)


@mcp.tool()
def list_issue_attachments(
    workspace: str,
    repository: str,
    issue_id: int,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List attachments on an issue."""
    return Client().list_issue_attachments(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def upload_issue_attachment(
    workspace: str,
    repository: str,
    issue_id: int,
    files: dict[str, str],
) -> dict:
    """Upload attachments to an issue.

    Args:
        files: Mapping of ``{filename: text_content}``.
    """
    files_bytes = {name: content.encode("utf-8") for name, content in files.items()}
    return Client().upload_issue_attachment(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        files=files_bytes,
    )


@mcp.tool()
def get_issue_attachment(
    workspace: str,
    repository: str,
    issue_id: int,
    path: str,
) -> str:
    """Download an attachment (raw bytes as text)."""
    return Client().get_issue_attachment(
        workspace=workspace, repository=repository, issue_id=issue_id, path=path
    )


@mcp.tool()
def delete_issue_attachment(
    workspace: str,
    repository: str,
    issue_id: int,
    path: str,
) -> dict:
    """Delete an issue attachment."""
    return Client().delete_issue_attachment(
        workspace=workspace, repository=repository, issue_id=issue_id, path=path
    )


@mcp.tool()
def list_issue_changes(
    workspace: str,
    repository: str,
    issue_id: int,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List the change log entries for an issue."""
    return Client().list_issue_changes(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_issue_change(
    workspace: str,
    repository: str,
    issue_id: int,
    changes: dict[str, Any] | None = None,
    message: str | None = None,
) -> dict:
    """Apply a change to an issue (transition, assignee, etc.).

    Args:
        changes: Mapping of field → ``{"new": "value"}``. e.g.
            ``{"state": {"new": "resolved"}, "assignee": {"new": "{uuid}"}}``.
        message: Optional comment message in markdown.
    """
    return Client().create_issue_change(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        changes=changes,
        message=message,
    )


@mcp.tool()
def get_issue_change(
    workspace: str,
    repository: str,
    issue_id: int,
    change_id: int,
) -> dict:
    """Get a single change log entry."""
    return Client().get_issue_change(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        change_id=change_id,
    )


@mcp.tool()
def list_issue_comments(
    workspace: str,
    repository: str,
    issue_id: int,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List comments on an issue."""
    return Client().list_issue_comments(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_issue_comment(
    workspace: str,
    repository: str,
    issue_id: int,
    content: str,
) -> dict:
    """Add a comment to an issue."""
    return Client().create_issue_comment(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        content=content,
    )


@mcp.tool()
def get_issue_comment(
    workspace: str,
    repository: str,
    issue_id: int,
    comment_id: int,
) -> dict:
    """Get a single issue comment."""
    return Client().get_issue_comment(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        comment_id=comment_id,
    )


@mcp.tool()
def update_issue_comment(
    workspace: str,
    repository: str,
    issue_id: int,
    comment_id: int,
    content: str,
) -> dict:
    """Edit an issue comment."""
    return Client().update_issue_comment(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        comment_id=comment_id,
        content=content,
    )


@mcp.tool()
def delete_issue_comment(
    workspace: str,
    repository: str,
    issue_id: int,
    comment_id: int,
) -> dict:
    """Delete an issue comment."""
    return Client().delete_issue_comment(
        workspace=workspace,
        repository=repository,
        issue_id=issue_id,
        comment_id=comment_id,
    )


@mcp.tool()
def get_issue_vote(workspace: str, repository: str, issue_id: int) -> dict:
    """Check if the caller has voted for an issue (404 if not)."""
    return Client().get_issue_vote(workspace=workspace, repository=repository, issue_id=issue_id)


@mcp.tool()
def vote_for_issue(workspace: str, repository: str, issue_id: int) -> dict:
    """Vote for an issue."""
    return Client().vote_for_issue(workspace=workspace, repository=repository, issue_id=issue_id)


@mcp.tool()
def unvote_issue(workspace: str, repository: str, issue_id: int) -> dict:
    """Retract the caller's vote on an issue."""
    return Client().unvote_issue(workspace=workspace, repository=repository, issue_id=issue_id)


@mcp.tool()
def get_issue_watch(workspace: str, repository: str, issue_id: int) -> dict:
    """Check if the caller is watching an issue (404 if not)."""
    return Client().get_issue_watch(workspace=workspace, repository=repository, issue_id=issue_id)


@mcp.tool()
def watch_issue(workspace: str, repository: str, issue_id: int) -> dict:
    """Start watching an issue."""
    return Client().watch_issue(workspace=workspace, repository=repository, issue_id=issue_id)


@mcp.tool()
def unwatch_issue(workspace: str, repository: str, issue_id: int) -> dict:
    """Stop watching an issue."""
    return Client().unwatch_issue(workspace=workspace, repository=repository, issue_id=issue_id)


# ---------------------------------------------------------------------------
# Projects (workspace-level mutations + permissions + default reviewers)
# ---------------------------------------------------------------------------


@mcp.tool()
def create_workspace_project(
    workspace: str,
    key: str,
    name: str,
    description: str | None = None,
    is_private: bool | None = None,
    avatar: dict[str, Any] | None = None,
) -> dict:
    """Create a project in a workspace."""
    return Client().create_workspace_project(
        workspace=workspace,
        key=key,
        name=name,
        description=description,
        is_private=is_private,
        avatar=avatar,
    )


@mcp.tool()
def update_workspace_project(
    workspace: str,
    project_key: str,
    key: str | None = None,
    name: str | None = None,
    description: str | None = None,
    is_private: bool | None = None,
    avatar: dict[str, Any] | None = None,
) -> dict:
    """Update an existing project."""
    return Client().update_workspace_project(
        workspace=workspace,
        project_key=project_key,
        key=key,
        name=name,
        description=description,
        is_private=is_private,
        avatar=avatar,
    )


@mcp.tool()
def delete_workspace_project(workspace: str, project_key: str) -> dict:
    """Delete a project."""
    return Client().delete_workspace_project(workspace=workspace, project_key=project_key)


@mcp.tool()
def list_project_default_reviewers(
    workspace: str,
    project_key: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List default reviewers for a project."""
    return Client().list_project_default_reviewers(
        workspace=workspace, project_key=project_key, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_project_default_reviewer(workspace: str, project_key: str, selected_user: str) -> dict:
    """Get a project default reviewer."""
    return Client().get_project_default_reviewer(
        workspace=workspace, project_key=project_key, selected_user=selected_user
    )


@mcp.tool()
def add_project_default_reviewer(workspace: str, project_key: str, selected_user: str) -> dict:
    """Add a default reviewer to a project."""
    return Client().add_project_default_reviewer(
        workspace=workspace, project_key=project_key, selected_user=selected_user
    )


@mcp.tool()
def remove_project_default_reviewer(workspace: str, project_key: str, selected_user: str) -> dict:
    """Remove a default reviewer from a project."""
    return Client().remove_project_default_reviewer(
        workspace=workspace, project_key=project_key, selected_user=selected_user
    )


@mcp.tool()
def list_project_group_permissions(
    workspace: str,
    project_key: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List explicit group permissions on a project."""
    return Client().list_project_group_permissions(
        workspace=workspace, project_key=project_key, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_project_group_permission(workspace: str, project_key: str, group_slug: str) -> dict:
    """Get a project group permission."""
    return Client().get_project_group_permission(
        workspace=workspace, project_key=project_key, group_slug=group_slug
    )


@mcp.tool()
def update_project_group_permission(
    workspace: str,
    project_key: str,
    group_slug: str,
    permission: str,
) -> dict:
    """Grant or update a project group permission ("read"/"write"/"create-repo"/"admin")."""
    return Client().update_project_group_permission(
        workspace=workspace,
        project_key=project_key,
        group_slug=group_slug,
        permission=permission,
    )


@mcp.tool()
def delete_project_group_permission(workspace: str, project_key: str, group_slug: str) -> dict:
    """Delete a project group permission."""
    return Client().delete_project_group_permission(
        workspace=workspace, project_key=project_key, group_slug=group_slug
    )


@mcp.tool()
def list_project_user_permissions(
    workspace: str,
    project_key: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List explicit user permissions on a project."""
    return Client().list_project_user_permissions(
        workspace=workspace, project_key=project_key, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_project_user_permission(workspace: str, project_key: str, selected_user_id: str) -> dict:
    """Get a project user permission."""
    return Client().get_project_user_permission(
        workspace=workspace,
        project_key=project_key,
        selected_user_id=selected_user_id,
    )


@mcp.tool()
def update_project_user_permission(
    workspace: str,
    project_key: str,
    selected_user_id: str,
    permission: str,
) -> dict:
    """Grant or update a project user permission ("read"/"write"/"create-repo"/"admin")."""
    return Client().update_project_user_permission(
        workspace=workspace,
        project_key=project_key,
        selected_user_id=selected_user_id,
        permission=permission,
    )


@mcp.tool()
def delete_project_user_permission(workspace: str, project_key: str, selected_user_id: str) -> dict:
    """Delete a project user permission."""
    return Client().delete_project_user_permission(
        workspace=workspace,
        project_key=project_key,
        selected_user_id=selected_user_id,
    )


# ---------------------------------------------------------------------------
# Refs (branches & tags)
# ---------------------------------------------------------------------------


@mcp.tool()
def list_refs(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List all refs (branches and tags) for a repository."""
    return Client().list_refs(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def list_branches(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List branches for a repository."""
    return Client().list_branches(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_branch(
    workspace: str,
    repository: str,
    name: str,
    target_hash: str,
) -> dict:
    """Create a branch pointing at ``target_hash``."""
    return Client().create_branch(
        workspace=workspace,
        repository=repository,
        name=name,
        target_hash=target_hash,
    )


@mcp.tool()
def get_branch(workspace: str, repository: str, name: str) -> dict:
    """Get a branch by name."""
    return Client().get_branch(workspace=workspace, repository=repository, name=name)


@mcp.tool()
def delete_branch(workspace: str, repository: str, name: str) -> dict:
    """Delete a branch."""
    return Client().delete_branch(workspace=workspace, repository=repository, name=name)


@mcp.tool()
def list_tags(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List tags for a repository."""
    return Client().list_tags(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_tag(
    workspace: str,
    repository: str,
    name: str,
    target_hash: str,
    message: str | None = None,
) -> dict:
    """Create a tag."""
    return Client().create_tag(
        workspace=workspace,
        repository=repository,
        name=name,
        target_hash=target_hash,
        message=message,
    )


@mcp.tool()
def get_tag(workspace: str, repository: str, name: str) -> dict:
    """Get a tag by name."""
    return Client().get_tag(workspace=workspace, repository=repository, name=name)


@mcp.tool()
def delete_tag(workspace: str, repository: str, name: str) -> dict:
    """Delete a tag."""
    return Client().delete_tag(workspace=workspace, repository=repository, name=name)


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@mcp.tool()
def search_workspace_code(
    workspace: str,
    search_query: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """Search code across a workspace.

    Args:
        search_query: Bitbucket code search query.
    """
    return Client().search_workspace_code(
        workspace=workspace, search_query=search_query, page=page, pagelen=pagelen
    )


@mcp.tool()
def search_user_code(
    selected_user: str,
    search_query: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """Search code across a user's repositories."""
    return Client().search_user_code(
        selected_user=selected_user,
        search_query=search_query,
        page=page,
        pagelen=pagelen,
    )


# ---------------------------------------------------------------------------
# Snippets
# ---------------------------------------------------------------------------


@mcp.tool()
def list_snippets(
    role: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List snippets visible to the caller.

    Args:
        role: "owner", "contributor", or "member".
    """
    return Client().list_snippets(role=role, page=page, pagelen=pagelen)


@mcp.tool()
def create_snippet(
    title: str | None = None,
    is_private: bool | None = None,
    scm: str | None = None,
    files: dict[str, str] | None = None,
) -> dict:
    """Create a snippet (multipart upload).

    Args:
        files: Mapping of ``{filename: text_content}``.
    """
    files_bytes = (
        {name: content.encode("utf-8") for name, content in files.items()} if files else None
    )
    return Client().create_snippet(title=title, is_private=is_private, scm=scm, files=files_bytes)


@mcp.tool()
def list_workspace_snippets(
    workspace: str,
    role: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List snippets in a workspace."""
    return Client().list_workspace_snippets(
        workspace=workspace, role=role, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_workspace_snippet(
    workspace: str,
    title: str | None = None,
    is_private: bool | None = None,
    scm: str | None = None,
    files: dict[str, str] | None = None,
) -> dict:
    """Create a snippet in a specific workspace."""
    files_bytes = (
        {name: content.encode("utf-8") for name, content in files.items()} if files else None
    )
    return Client().create_workspace_snippet(
        workspace=workspace,
        title=title,
        is_private=is_private,
        scm=scm,
        files=files_bytes,
    )


@mcp.tool()
def get_snippet(workspace: str, encoded_id: str) -> dict:
    """Get a snippet by its encoded id."""
    return Client().get_snippet(workspace=workspace, encoded_id=encoded_id)


@mcp.tool()
def update_snippet(
    workspace: str,
    encoded_id: str,
    title: str | None = None,
    is_private: bool | None = None,
    files: dict[str, str] | None = None,
) -> dict:
    """Update a snippet."""
    files_bytes = (
        {name: content.encode("utf-8") for name, content in files.items()} if files else None
    )
    return Client().update_snippet(
        workspace=workspace,
        encoded_id=encoded_id,
        title=title,
        is_private=is_private,
        files=files_bytes,
    )


@mcp.tool()
def delete_snippet(workspace: str, encoded_id: str) -> dict:
    """Delete a snippet."""
    return Client().delete_snippet(workspace=workspace, encoded_id=encoded_id)


@mcp.tool()
def list_snippet_comments(
    workspace: str,
    encoded_id: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List comments on a snippet."""
    return Client().list_snippet_comments(
        workspace=workspace, encoded_id=encoded_id, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_snippet_comment(workspace: str, encoded_id: str, content: str) -> dict:
    """Add a comment to a snippet."""
    return Client().create_snippet_comment(
        workspace=workspace, encoded_id=encoded_id, content=content
    )


@mcp.tool()
def get_snippet_comment(workspace: str, encoded_id: str, comment_id: int) -> dict:
    """Get a single snippet comment."""
    return Client().get_snippet_comment(
        workspace=workspace, encoded_id=encoded_id, comment_id=comment_id
    )


@mcp.tool()
def update_snippet_comment(
    workspace: str,
    encoded_id: str,
    comment_id: int,
    content: str,
) -> dict:
    """Update a snippet comment."""
    return Client().update_snippet_comment(
        workspace=workspace,
        encoded_id=encoded_id,
        comment_id=comment_id,
        content=content,
    )


@mcp.tool()
def delete_snippet_comment(workspace: str, encoded_id: str, comment_id: int) -> dict:
    """Delete a snippet comment."""
    return Client().delete_snippet_comment(
        workspace=workspace, encoded_id=encoded_id, comment_id=comment_id
    )


@mcp.tool()
def list_snippet_commits(
    workspace: str,
    encoded_id: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List commits in a snippet."""
    return Client().list_snippet_commits(
        workspace=workspace, encoded_id=encoded_id, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_snippet_commit(workspace: str, encoded_id: str, revision: str) -> dict:
    """Get a snippet commit."""
    return Client().get_snippet_commit(
        workspace=workspace, encoded_id=encoded_id, revision=revision
    )


@mcp.tool()
def get_snippet_file(workspace: str, encoded_id: str, path: str) -> str:
    """Get a file from the latest revision of a snippet."""
    return Client().get_snippet_file(workspace=workspace, encoded_id=encoded_id, path=path)


@mcp.tool()
def get_snippet_watch(workspace: str, encoded_id: str) -> dict:
    """Check if the caller watches a snippet (404 if not)."""
    return Client().get_snippet_watch(workspace=workspace, encoded_id=encoded_id)


@mcp.tool()
def watch_snippet(workspace: str, encoded_id: str) -> dict:
    """Watch a snippet."""
    return Client().watch_snippet(workspace=workspace, encoded_id=encoded_id)


@mcp.tool()
def unwatch_snippet(workspace: str, encoded_id: str) -> dict:
    """Unwatch a snippet."""
    return Client().unwatch_snippet(workspace=workspace, encoded_id=encoded_id)


@mcp.tool()
def list_snippet_watchers(
    workspace: str,
    encoded_id: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List users watching a snippet."""
    return Client().list_snippet_watchers(
        workspace=workspace, encoded_id=encoded_id, page=page, pagelen=pagelen
    )


@mcp.tool()
def get_snippet_at_revision(workspace: str, encoded_id: str, node_id: str) -> dict:
    """Get a snippet at a specific revision."""
    return Client().get_snippet_at_revision(
        workspace=workspace, encoded_id=encoded_id, node_id=node_id
    )


@mcp.tool()
def update_snippet_at_revision(
    workspace: str,
    encoded_id: str,
    node_id: str,
    title: str | None = None,
    is_private: bool | None = None,
    files: dict[str, str] | None = None,
) -> dict:
    """Update a snippet at a specific revision."""
    files_bytes = (
        {name: content.encode("utf-8") for name, content in files.items()} if files else None
    )
    return Client().update_snippet_at_revision(
        workspace=workspace,
        encoded_id=encoded_id,
        node_id=node_id,
        title=title,
        is_private=is_private,
        files=files_bytes,
    )


@mcp.tool()
def delete_snippet_at_revision(workspace: str, encoded_id: str, node_id: str) -> dict:
    """Delete a snippet at a specific revision."""
    return Client().delete_snippet_at_revision(
        workspace=workspace, encoded_id=encoded_id, node_id=node_id
    )


@mcp.tool()
def get_snippet_file_at_revision(
    workspace: str,
    encoded_id: str,
    node_id: str,
    path: str,
) -> str:
    """Get a snippet file at a specific revision."""
    return Client().get_snippet_file_at_revision(
        workspace=workspace, encoded_id=encoded_id, node_id=node_id, path=path
    )


@mcp.tool()
def get_snippet_diff(workspace: str, encoded_id: str, revision: str) -> str:
    """Get the diff for a snippet revision."""
    return Client().get_snippet_diff(workspace=workspace, encoded_id=encoded_id, revision=revision)


@mcp.tool()
def get_snippet_patch(workspace: str, encoded_id: str, revision: str) -> str:
    """Get the patch for a snippet revision."""
    return Client().get_snippet_patch(workspace=workspace, encoded_id=encoded_id, revision=revision)


# ---------------------------------------------------------------------------
# SSH keys
# ---------------------------------------------------------------------------


@mcp.tool()
def list_user_ssh_keys(
    selected_user: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List a user's SSH keys."""
    return Client().list_user_ssh_keys(selected_user=selected_user, page=page, pagelen=pagelen)


@mcp.tool()
def create_user_ssh_key(
    selected_user: str,
    key: str,
    label: str | None = None,
) -> dict:
    """Add an SSH key to a user."""
    return Client().create_user_ssh_key(selected_user=selected_user, key=key, label=label)


@mcp.tool()
def get_user_ssh_key(selected_user: str, key_id: str) -> dict:
    """Get a user's SSH key."""
    return Client().get_user_ssh_key(selected_user=selected_user, key_id=key_id)


@mcp.tool()
def update_user_ssh_key(
    selected_user: str,
    key_id: str,
    label: str | None = None,
    key: str | None = None,
) -> dict:
    """Update a user's SSH key."""
    return Client().update_user_ssh_key(
        selected_user=selected_user, key_id=key_id, label=label, key=key
    )


@mcp.tool()
def delete_user_ssh_key(selected_user: str, key_id: str) -> dict:
    """Delete a user's SSH key."""
    return Client().delete_user_ssh_key(selected_user=selected_user, key_id=key_id)


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


@mcp.tool()
def get_user(selected_user: str) -> dict:
    """Get a public Bitbucket user by username, UUID, or Atlassian Account ID."""
    return Client().get_user(selected_user=selected_user)


@mcp.tool()
def list_user_emails(
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List email addresses for the authenticated user."""
    return Client().list_user_emails(page=page, pagelen=pagelen)


@mcp.tool()
def get_user_email(email: str) -> dict:
    """Get an email address by value (authenticated user only)."""
    return Client().get_user_email(email=email)


# ---------------------------------------------------------------------------
# Webhook event types
# ---------------------------------------------------------------------------


@mcp.tool()
def list_hook_event_subjects() -> dict:
    """List the subject types that can be subscribed to via webhooks."""
    return Client().list_hook_event_subjects()


@mcp.tool()
def list_hook_events(subject_type: str) -> dict:
    """List all webhook event keys for a subject type.

    Args:
        subject_type: "workspace", "user", or "repository".
    """
    return Client().list_hook_events(subject_type=subject_type)


# ---------------------------------------------------------------------------
# Pipelines: pipelines & steps
# ---------------------------------------------------------------------------


@mcp.tool()
def list_pipelines(
    workspace: str,
    repository: str,
    q: str | None = None,
    sort: str | None = None,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List pipelines for a repository."""
    return Client().list_pipelines(
        workspace=workspace,
        repository=repository,
        q=q,
        sort=sort,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_pipeline(
    workspace: str,
    repository: str,
    target: dict[str, Any],
    variables: list[dict[str, Any]] | None = None,
) -> dict:
    """Trigger a pipeline.

    Args:
        target: e.g. ``{"type": "pipeline_ref_target", "ref_type": "branch",
            "ref_name": "main", "selector": {"type": "default"}}``.
        variables: ``[{"key": "FOO", "value": "BAR", "secured": false}, ...]``.
    """
    return Client().create_pipeline(
        workspace=workspace,
        repository=repository,
        target=target,
        variables=variables,
    )


@mcp.tool()
def get_pipeline(workspace: str, repository: str, pipeline_uuid: str) -> dict:
    """Get a pipeline by UUID."""
    return Client().get_pipeline(
        workspace=workspace, repository=repository, pipeline_uuid=pipeline_uuid
    )


@mcp.tool()
def stop_pipeline(workspace: str, repository: str, pipeline_uuid: str) -> dict:
    """Stop a running pipeline."""
    return Client().stop_pipeline(
        workspace=workspace, repository=repository, pipeline_uuid=pipeline_uuid
    )


@mcp.tool()
def list_pipeline_steps(
    workspace: str,
    repository: str,
    pipeline_uuid: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List the steps of a pipeline."""
    return Client().list_pipeline_steps(
        workspace=workspace,
        repository=repository,
        pipeline_uuid=pipeline_uuid,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def get_pipeline_step(
    workspace: str,
    repository: str,
    pipeline_uuid: str,
    step_uuid: str,
) -> dict:
    """Get a single pipeline step."""
    return Client().get_pipeline_step(
        workspace=workspace,
        repository=repository,
        pipeline_uuid=pipeline_uuid,
        step_uuid=step_uuid,
    )


@mcp.tool()
def get_pipeline_step_log(
    workspace: str,
    repository: str,
    pipeline_uuid: str,
    step_uuid: str,
) -> str:
    """Get the full text log for a pipeline step."""
    return Client().get_pipeline_step_log(
        workspace=workspace,
        repository=repository,
        pipeline_uuid=pipeline_uuid,
        step_uuid=step_uuid,
    )


@mcp.tool()
def get_pipeline_step_container_log(
    workspace: str,
    repository: str,
    pipeline_uuid: str,
    step_uuid: str,
    log_uuid: str,
) -> str:
    """Get a container-specific log for a pipeline step."""
    return Client().get_pipeline_step_container_log(
        workspace=workspace,
        repository=repository,
        pipeline_uuid=pipeline_uuid,
        step_uuid=step_uuid,
        log_uuid=log_uuid,
    )


@mcp.tool()
def list_pipeline_step_test_reports(
    workspace: str,
    repository: str,
    pipeline_uuid: str,
    step_uuid: str,
) -> dict:
    """List test reports for a pipeline step."""
    return Client().list_pipeline_step_test_reports(
        workspace=workspace,
        repository=repository,
        pipeline_uuid=pipeline_uuid,
        step_uuid=step_uuid,
    )


@mcp.tool()
def list_pipeline_step_test_cases(
    workspace: str,
    repository: str,
    pipeline_uuid: str,
    step_uuid: str,
) -> dict:
    """List test cases for a pipeline step."""
    return Client().list_pipeline_step_test_cases(
        workspace=workspace,
        repository=repository,
        pipeline_uuid=pipeline_uuid,
        step_uuid=step_uuid,
    )


@mcp.tool()
def list_pipeline_step_test_case_reasons(
    workspace: str,
    repository: str,
    pipeline_uuid: str,
    step_uuid: str,
    test_case_uuid: str,
) -> dict:
    """List failure reasons for a test case."""
    return Client().list_pipeline_step_test_case_reasons(
        workspace=workspace,
        repository=repository,
        pipeline_uuid=pipeline_uuid,
        step_uuid=step_uuid,
        test_case_uuid=test_case_uuid,
    )


# ---------------------------------------------------------------------------
# Pipelines: configuration
# ---------------------------------------------------------------------------


@mcp.tool()
def get_pipeline_config(workspace: str, repository: str) -> dict:
    """Get pipelines configuration for a repository."""
    return Client().get_pipeline_config(workspace=workspace, repository=repository)


@mcp.tool()
def update_pipeline_config(
    workspace: str,
    repository: str,
    enabled: bool | None = None,
    repository_pipeline: dict[str, Any] | None = None,
) -> dict:
    """Update pipelines configuration."""
    return Client().update_pipeline_config(
        workspace=workspace,
        repository=repository,
        enabled=enabled,
        repository_pipeline=repository_pipeline,
    )


@mcp.tool()
def update_pipeline_build_number(
    workspace: str,
    repository: str,
    next_build_number: int,
) -> dict:
    """Set the next pipeline build number for a repository."""
    return Client().update_pipeline_build_number(
        workspace=workspace,
        repository=repository,
        next_build_number=next_build_number,
    )


# ---------------------------------------------------------------------------
# Pipelines: schedules
# ---------------------------------------------------------------------------


@mcp.tool()
def list_pipeline_schedules(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List pipeline schedules."""
    return Client().list_pipeline_schedules(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_pipeline_schedule(
    workspace: str,
    repository: str,
    target: dict[str, Any],
    cron_pattern: str,
    enabled: bool | None = None,
) -> dict:
    """Create a pipeline schedule."""
    return Client().create_pipeline_schedule(
        workspace=workspace,
        repository=repository,
        target=target,
        cron_pattern=cron_pattern,
        enabled=enabled,
    )


@mcp.tool()
def get_pipeline_schedule(workspace: str, repository: str, schedule_uuid: str) -> dict:
    """Get a pipeline schedule."""
    return Client().get_pipeline_schedule(
        workspace=workspace, repository=repository, schedule_uuid=schedule_uuid
    )


@mcp.tool()
def update_pipeline_schedule(
    workspace: str,
    repository: str,
    schedule_uuid: str,
    enabled: bool | None = None,
    cron_pattern: str | None = None,
    target: dict[str, Any] | None = None,
) -> dict:
    """Update a pipeline schedule."""
    return Client().update_pipeline_schedule(
        workspace=workspace,
        repository=repository,
        schedule_uuid=schedule_uuid,
        enabled=enabled,
        cron_pattern=cron_pattern,
        target=target,
    )


@mcp.tool()
def delete_pipeline_schedule(workspace: str, repository: str, schedule_uuid: str) -> dict:
    """Delete a pipeline schedule."""
    return Client().delete_pipeline_schedule(
        workspace=workspace, repository=repository, schedule_uuid=schedule_uuid
    )


@mcp.tool()
def list_pipeline_schedule_executions(
    workspace: str,
    repository: str,
    schedule_uuid: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List execution history for a pipeline schedule."""
    return Client().list_pipeline_schedule_executions(
        workspace=workspace,
        repository=repository,
        schedule_uuid=schedule_uuid,
        page=page,
        pagelen=pagelen,
    )


# ---------------------------------------------------------------------------
# Pipelines: SSH key pair
# ---------------------------------------------------------------------------


@mcp.tool()
def get_pipeline_ssh_key_pair(workspace: str, repository: str) -> dict:
    """Get the pipeline SSH key pair (public key only)."""
    return Client().get_pipeline_ssh_key_pair(workspace=workspace, repository=repository)


@mcp.tool()
def update_pipeline_ssh_key_pair(
    workspace: str,
    repository: str,
    public_key: str,
    private_key: str,
) -> dict:
    """Set the pipeline SSH key pair."""
    return Client().update_pipeline_ssh_key_pair(
        workspace=workspace,
        repository=repository,
        public_key=public_key,
        private_key=private_key,
    )


@mcp.tool()
def delete_pipeline_ssh_key_pair(workspace: str, repository: str) -> dict:
    """Delete the pipeline SSH key pair."""
    return Client().delete_pipeline_ssh_key_pair(workspace=workspace, repository=repository)


# ---------------------------------------------------------------------------
# Pipelines: known hosts
# ---------------------------------------------------------------------------


@mcp.tool()
def list_pipeline_known_hosts(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List known SSH hosts for pipelines."""
    return Client().list_pipeline_known_hosts(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_pipeline_known_host(
    workspace: str,
    repository: str,
    hostname: str,
    public_key: dict[str, Any],
) -> dict:
    """Add a known SSH host."""
    return Client().create_pipeline_known_host(
        workspace=workspace,
        repository=repository,
        hostname=hostname,
        public_key=public_key,
    )


@mcp.tool()
def get_pipeline_known_host(workspace: str, repository: str, known_host_uuid: str) -> dict:
    """Get a known SSH host."""
    return Client().get_pipeline_known_host(
        workspace=workspace, repository=repository, known_host_uuid=known_host_uuid
    )


@mcp.tool()
def update_pipeline_known_host(
    workspace: str,
    repository: str,
    known_host_uuid: str,
    hostname: str | None = None,
    public_key: dict[str, Any] | None = None,
) -> dict:
    """Update a known SSH host."""
    return Client().update_pipeline_known_host(
        workspace=workspace,
        repository=repository,
        known_host_uuid=known_host_uuid,
        hostname=hostname,
        public_key=public_key,
    )


@mcp.tool()
def delete_pipeline_known_host(workspace: str, repository: str, known_host_uuid: str) -> dict:
    """Delete a known SSH host."""
    return Client().delete_pipeline_known_host(
        workspace=workspace, repository=repository, known_host_uuid=known_host_uuid
    )


# ---------------------------------------------------------------------------
# Pipelines: repository variables
# ---------------------------------------------------------------------------


@mcp.tool()
def list_pipeline_variables(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List pipeline variables for a repository."""
    return Client().list_pipeline_variables(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_pipeline_variable(
    workspace: str,
    repository: str,
    key: str,
    value: str,
    secured: bool | None = None,
) -> dict:
    """Create a pipeline variable."""
    return Client().create_pipeline_variable(
        workspace=workspace,
        repository=repository,
        key=key,
        value=value,
        secured=secured,
    )


@mcp.tool()
def get_pipeline_variable(workspace: str, repository: str, variable_uuid: str) -> dict:
    """Get a pipeline variable."""
    return Client().get_pipeline_variable(
        workspace=workspace, repository=repository, variable_uuid=variable_uuid
    )


@mcp.tool()
def update_pipeline_variable(
    workspace: str,
    repository: str,
    variable_uuid: str,
    key: str | None = None,
    value: str | None = None,
    secured: bool | None = None,
) -> dict:
    """Update a pipeline variable."""
    return Client().update_pipeline_variable(
        workspace=workspace,
        repository=repository,
        variable_uuid=variable_uuid,
        key=key,
        value=value,
        secured=secured,
    )


@mcp.tool()
def delete_pipeline_variable(workspace: str, repository: str, variable_uuid: str) -> dict:
    """Delete a pipeline variable."""
    return Client().delete_pipeline_variable(
        workspace=workspace, repository=repository, variable_uuid=variable_uuid
    )


# ---------------------------------------------------------------------------
# Pipelines: caches
# ---------------------------------------------------------------------------


@mcp.tool()
def list_pipeline_caches(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List pipeline caches."""
    return Client().list_pipeline_caches(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def delete_pipeline_caches(workspace: str, repository: str, name: str | None = None) -> dict:
    """Delete all caches (or by name)."""
    return Client().delete_pipeline_caches(workspace=workspace, repository=repository, name=name)


@mcp.tool()
def delete_pipeline_cache(workspace: str, repository: str, cache_uuid: str) -> dict:
    """Delete a single pipeline cache."""
    return Client().delete_pipeline_cache(
        workspace=workspace, repository=repository, cache_uuid=cache_uuid
    )


@mcp.tool()
def get_pipeline_cache_content_uri(workspace: str, repository: str, cache_uuid: str) -> dict:
    """Get the temporary download URI for a pipeline cache."""
    return Client().get_pipeline_cache_content_uri(
        workspace=workspace, repository=repository, cache_uuid=cache_uuid
    )


# ---------------------------------------------------------------------------
# Pipelines: runners
# ---------------------------------------------------------------------------


@mcp.tool()
def list_repository_pipeline_runners(
    workspace: str,
    repository: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List repository-scoped pipeline runners."""
    return Client().list_repository_pipeline_runners(
        workspace=workspace, repository=repository, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_repository_pipeline_runner(
    workspace: str,
    repository: str,
    name: str,
    labels: list[str] | None = None,
) -> dict:
    """Create a repository-scoped runner."""
    return Client().create_repository_pipeline_runner(
        workspace=workspace, repository=repository, name=name, labels=labels
    )


@mcp.tool()
def get_repository_pipeline_runner(workspace: str, repository: str, runner_uuid: str) -> dict:
    """Get a repository-scoped runner."""
    return Client().get_repository_pipeline_runner(
        workspace=workspace, repository=repository, runner_uuid=runner_uuid
    )


@mcp.tool()
def update_repository_pipeline_runner(
    workspace: str,
    repository: str,
    runner_uuid: str,
    name: str | None = None,
    labels: list[str] | None = None,
) -> dict:
    """Update a repository-scoped runner."""
    return Client().update_repository_pipeline_runner(
        workspace=workspace,
        repository=repository,
        runner_uuid=runner_uuid,
        name=name,
        labels=labels,
    )


@mcp.tool()
def delete_repository_pipeline_runner(workspace: str, repository: str, runner_uuid: str) -> dict:
    """Delete a repository-scoped runner."""
    return Client().delete_repository_pipeline_runner(
        workspace=workspace, repository=repository, runner_uuid=runner_uuid
    )


@mcp.tool()
def list_workspace_pipeline_runners(
    workspace: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List workspace-scoped pipeline runners."""
    return Client().list_workspace_pipeline_runners(workspace=workspace, page=page, pagelen=pagelen)


@mcp.tool()
def create_workspace_pipeline_runner(
    workspace: str,
    name: str,
    labels: list[str] | None = None,
) -> dict:
    """Create a workspace-scoped runner."""
    return Client().create_workspace_pipeline_runner(workspace=workspace, name=name, labels=labels)


@mcp.tool()
def get_workspace_pipeline_runner(workspace: str, runner_uuid: str) -> dict:
    """Get a workspace-scoped runner."""
    return Client().get_workspace_pipeline_runner(workspace=workspace, runner_uuid=runner_uuid)


@mcp.tool()
def update_workspace_pipeline_runner(
    workspace: str,
    runner_uuid: str,
    name: str | None = None,
    labels: list[str] | None = None,
) -> dict:
    """Update a workspace-scoped runner."""
    return Client().update_workspace_pipeline_runner(
        workspace=workspace, runner_uuid=runner_uuid, name=name, labels=labels
    )


@mcp.tool()
def delete_workspace_pipeline_runner(workspace: str, runner_uuid: str) -> dict:
    """Delete a workspace-scoped runner."""
    return Client().delete_workspace_pipeline_runner(workspace=workspace, runner_uuid=runner_uuid)


# ---------------------------------------------------------------------------
# Pipelines: workspace & user variables
# ---------------------------------------------------------------------------


@mcp.tool()
def list_workspace_pipeline_variables(
    workspace: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List workspace-level pipeline variables."""
    return Client().list_workspace_pipeline_variables(
        workspace=workspace, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_workspace_pipeline_variable(
    workspace: str,
    key: str,
    value: str,
    secured: bool | None = None,
) -> dict:
    """Create a workspace-level pipeline variable."""
    return Client().create_workspace_pipeline_variable(
        workspace=workspace, key=key, value=value, secured=secured
    )


@mcp.tool()
def get_workspace_pipeline_variable(workspace: str, variable_uuid: str) -> dict:
    """Get a workspace-level pipeline variable."""
    return Client().get_workspace_pipeline_variable(
        workspace=workspace, variable_uuid=variable_uuid
    )


@mcp.tool()
def update_workspace_pipeline_variable(
    workspace: str,
    variable_uuid: str,
    key: str | None = None,
    value: str | None = None,
    secured: bool | None = None,
) -> dict:
    """Update a workspace-level pipeline variable."""
    return Client().update_workspace_pipeline_variable(
        workspace=workspace,
        variable_uuid=variable_uuid,
        key=key,
        value=value,
        secured=secured,
    )


@mcp.tool()
def delete_workspace_pipeline_variable(workspace: str, variable_uuid: str) -> dict:
    """Delete a workspace-level pipeline variable."""
    return Client().delete_workspace_pipeline_variable(
        workspace=workspace, variable_uuid=variable_uuid
    )


@mcp.tool()
def list_user_pipeline_variables(
    selected_user: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List a user's account-level pipeline variables."""
    return Client().list_user_pipeline_variables(
        selected_user=selected_user, page=page, pagelen=pagelen
    )


@mcp.tool()
def create_user_pipeline_variable(
    selected_user: str,
    key: str,
    value: str,
    secured: bool | None = None,
) -> dict:
    """Create a user account-level pipeline variable."""
    return Client().create_user_pipeline_variable(
        selected_user=selected_user, key=key, value=value, secured=secured
    )


@mcp.tool()
def get_user_pipeline_variable(selected_user: str, variable_uuid: str) -> dict:
    """Get a user account-level pipeline variable."""
    return Client().get_user_pipeline_variable(
        selected_user=selected_user, variable_uuid=variable_uuid
    )


@mcp.tool()
def update_user_pipeline_variable(
    selected_user: str,
    variable_uuid: str,
    key: str | None = None,
    value: str | None = None,
    secured: bool | None = None,
) -> dict:
    """Update a user account-level pipeline variable."""
    return Client().update_user_pipeline_variable(
        selected_user=selected_user,
        variable_uuid=variable_uuid,
        key=key,
        value=value,
        secured=secured,
    )


@mcp.tool()
def delete_user_pipeline_variable(selected_user: str, variable_uuid: str) -> dict:
    """Delete a user account-level pipeline variable."""
    return Client().delete_user_pipeline_variable(
        selected_user=selected_user, variable_uuid=variable_uuid
    )


# ---------------------------------------------------------------------------
# Pipelines: deployment variables
# ---------------------------------------------------------------------------


@mcp.tool()
def list_deployment_variables(
    workspace: str,
    repository: str,
    environment_uuid: str,
    page: int | None = None,
    pagelen: int | None = None,
) -> dict:
    """List deployment variables for an environment."""
    return Client().list_deployment_variables(
        workspace=workspace,
        repository=repository,
        environment_uuid=environment_uuid,
        page=page,
        pagelen=pagelen,
    )


@mcp.tool()
def create_deployment_variable(
    workspace: str,
    repository: str,
    environment_uuid: str,
    key: str,
    value: str,
    secured: bool | None = None,
) -> dict:
    """Create a deployment variable on an environment."""
    return Client().create_deployment_variable(
        workspace=workspace,
        repository=repository,
        environment_uuid=environment_uuid,
        key=key,
        value=value,
        secured=secured,
    )


@mcp.tool()
def update_deployment_variable(
    workspace: str,
    repository: str,
    environment_uuid: str,
    variable_uuid: str,
    key: str | None = None,
    value: str | None = None,
    secured: bool | None = None,
) -> dict:
    """Update a deployment variable."""
    return Client().update_deployment_variable(
        workspace=workspace,
        repository=repository,
        environment_uuid=environment_uuid,
        variable_uuid=variable_uuid,
        key=key,
        value=value,
        secured=secured,
    )


@mcp.tool()
def delete_deployment_variable(
    workspace: str,
    repository: str,
    environment_uuid: str,
    variable_uuid: str,
) -> dict:
    """Delete a deployment variable."""
    return Client().delete_deployment_variable(
        workspace=workspace,
        repository=repository,
        environment_uuid=environment_uuid,
        variable_uuid=variable_uuid,
    )


# ---------------------------------------------------------------------------
# Pipelines: OIDC
# ---------------------------------------------------------------------------


@mcp.tool()
def get_pipelines_oidc_configuration(workspace: str) -> dict:
    """Get the OIDC discovery document for a workspace's pipelines."""
    return Client().get_pipelines_oidc_configuration(workspace=workspace)


@mcp.tool()
def get_pipelines_oidc_keys(workspace: str) -> dict:
    """Get the OIDC JWKS keys for a workspace's pipelines."""
    return Client().get_pipelines_oidc_keys(workspace=workspace)


def main() -> None:
    load_dotenv()
    mcp.run()


if __name__ == "__main__":
    main()
