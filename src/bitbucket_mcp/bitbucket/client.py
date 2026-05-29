from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid as _uuid
from typing import Any

from bitbucket_mcp import __version__

BASE_URL = "https://api.bitbucket.org/2.0"

# Networking defaults. Override via the BITBUCKET_TIMEOUT / BITBUCKET_MAX_RETRIES
# environment variables, or the Client constructor.
DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
RETRY_BACKOFF_BASE = 1.0
RETRY_MAX_DELAY = 60.0
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})
IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})
USER_AGENT = f"bitbucket-mcp/{__version__}"


class BitbucketError(Exception):
    pass


class ConfigurationError(BitbucketError):
    pass


class AuthenticationError(BitbucketError):
    pass


class ResponseError(BitbucketError):
    pass


class Client:
    def __init__(
        self,
        email: str | None = None,
        api_token: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        email = email or os.environ.get("BITBUCKET_EMAIL")
        api_token = api_token or os.environ.get("BITBUCKET_API_TOKEN")

        if not email:
            raise ConfigurationError("BITBUCKET_EMAIL is not set")
        if not api_token:
            raise ConfigurationError("BITBUCKET_API_TOKEN is not set")

        self._email = email
        self._api_token = api_token
        self._timeout = (
            timeout if timeout is not None else _env_float("BITBUCKET_TIMEOUT", DEFAULT_TIMEOUT)
        )
        self._max_retries = (
            max_retries
            if max_retries is not None
            else _env_int("BITBUCKET_MAX_RETRIES", DEFAULT_MAX_RETRIES)
        )

        if self._timeout <= 0:
            raise ConfigurationError("timeout must be greater than 0")
        if self._max_retries < 0:
            raise ConfigurationError("max_retries must be 0 or greater")

    def current_user(self) -> dict[str, Any]:
        return self._request("GET", "/user")

    def list_pull_requests_for_commit(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}/pullrequests",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def list_pull_requests(
        self,
        *,
        workspace: str,
        repository: str,
        state: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests",
            params=_clean({"state": state, "q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_pull_request(
        self,
        *,
        workspace: str,
        repository: str,
        title: str,
        source_branch: str,
        destination_branch: str,
        description: str | None = None,
        close_source_branch: bool | None = None,
        reviewers: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "title": title,
            "source": {"branch": {"name": source_branch}},
            "destination": {"branch": {"name": destination_branch}},
        }
        if description is not None:
            body["description"] = description
        if close_source_branch is not None:
            body["close_source_branch"] = close_source_branch
        if reviewers is not None:
            body["reviewers"] = [{"uuid": uuid} for uuid in reviewers]
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests",
            body=body,
        )

    def list_repository_pull_request_activity(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/activity",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_pull_request(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}",
        )

    def update_pull_request(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        title: str | None = None,
        description: str | None = None,
        destination_branch: str | None = None,
        reviewers: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if description is not None:
            body["description"] = description
        if destination_branch is not None:
            body["destination"] = {"branch": {"name": destination_branch}}
        if reviewers is not None:
            body["reviewers"] = [{"uuid": uuid} for uuid in reviewers]
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}",
            body=body,
        )

    def list_pull_request_activity(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/activity",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def approve_pull_request(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/approve",
        )

    def unapprove_pull_request(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/approve",
        )

    def request_changes(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/request-changes",
        )

    def remove_request_changes(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/request-changes",
        )

    def list_pull_request_comments(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/comments",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_pull_request_comment(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        content: str,
        parent_id: int | None = None,
        inline_path: str | None = None,
        inline_to: int | None = None,
        inline_from: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"content": {"raw": content}}
        if parent_id is not None:
            body["parent"] = {"id": parent_id}
        if inline_path is not None:
            inline: dict[str, Any] = {"path": inline_path}
            if inline_to is not None:
                inline["to"] = inline_to
            if inline_from is not None:
                inline["from"] = inline_from
            body["inline"] = inline
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/comments",
            body=body,
        )

    def get_pull_request_comment(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}"
            f"/comments/{comment_id}",
        )

    def update_pull_request_comment(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        comment_id: int,
        content: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}"
            f"/comments/{comment_id}",
            body={"content": {"raw": content}},
        )

    def delete_pull_request_comment(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}"
            f"/comments/{comment_id}",
        )

    def resolve_pull_request_comment(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}"
            f"/comments/{comment_id}/resolve",
        )

    def reopen_pull_request_comment(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}"
            f"/comments/{comment_id}/resolve",
        )

    def list_pull_request_commits(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/commits",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def list_pull_request_conflicts(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/conflicts",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def decline_pull_request(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/decline",
        )

    def get_pull_request_diff(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/diff",
            text_response=True,
        )

    def get_pull_request_diffstat(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/diffstat",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def merge_pull_request(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        message: str | None = None,
        close_source_branch: bool | None = None,
        merge_strategy: str | None = None,
        async_: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if message is not None:
            body["message"] = message
        if close_source_branch is not None:
            body["close_source_branch"] = close_source_branch
        if merge_strategy is not None:
            body["merge_strategy"] = merge_strategy
        params = _clean({"async": async_})
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/merge",
            body=body or None,
            params=params,
        )

    def get_merge_task_status(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        task_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}"
            f"/merge/task-status/{task_id}",
        )

    def get_pull_request_patch(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/patch",
            text_response=True,
        )

    def list_pull_request_statuses(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/statuses",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def list_pull_request_tasks(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/tasks",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_pull_request_task(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        content: str,
        comment_id: int | None = None,
        pending: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"content": {"raw": content}}
        if comment_id is not None:
            body["comment"] = {"id": comment_id}
        if pending is not None:
            body["pending"] = pending
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/tasks",
            body=body,
        )

    def get_pull_request_task(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        task_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/tasks/{task_id}",
        )

    def update_pull_request_task(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        task_id: int,
        content: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if content is not None:
            body["content"] = {"raw": content}
        if state is not None:
            body["state"] = state
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/tasks/{task_id}",
            body=body,
        )

    def delete_pull_request_task(
        self,
        *,
        workspace: str,
        repository: str,
        pull_request_id: int,
        task_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pullrequests/{pull_request_id}/tasks/{task_id}",
        )

    # ----- Workspaces -----

    def list_user_workspace_permissions(
        self,
        *,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/user/permissions/workspaces",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def list_user_workspaces(
        self,
        *,
        sort: str | None = None,
        administrator: bool | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/user/workspaces",
            params=_clean(
                {"sort": sort, "administrator": administrator, "page": page, "pagelen": pagelen}
            ),
        )

    def get_user_workspace_permission(self, *, workspace: str) -> dict[str, Any]:
        return self._request("GET", f"/user/workspaces/{workspace}/permission")

    def list_workspaces(
        self,
        *,
        role: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/workspaces",
            params=_clean({"role": role, "q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def get_workspace(self, *, workspace: str) -> dict[str, Any]:
        return self._request("GET", f"/workspaces/{workspace}")

    def list_workspace_webhooks(
        self,
        *,
        workspace: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/hooks",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_workspace_webhook(
        self,
        *,
        workspace: str,
        url: str,
        events: list[str],
        description: str | None = None,
        active: bool | None = None,
        secret: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            body["description"] = description
        if active is not None:
            body["active"] = active
        if secret is not None:
            body["secret"] = secret
        return self._request("POST", f"/workspaces/{workspace}/hooks", body=body)

    def delete_workspace_webhook(self, *, workspace: str, uid: str) -> dict[str, Any]:
        return self._request("DELETE", f"/workspaces/{workspace}/hooks/{uid}")

    def get_workspace_webhook(self, *, workspace: str, uid: str) -> dict[str, Any]:
        return self._request("GET", f"/workspaces/{workspace}/hooks/{uid}")

    def update_workspace_webhook(
        self,
        *,
        workspace: str,
        uid: str,
        url: str | None = None,
        events: list[str] | None = None,
        description: str | None = None,
        active: bool | None = None,
        secret: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if description is not None:
            body["description"] = description
        if active is not None:
            body["active"] = active
        if secret is not None:
            body["secret"] = secret
        return self._request("PUT", f"/workspaces/{workspace}/hooks/{uid}", body=body)

    def list_workspace_members(
        self,
        *,
        workspace: str,
        q: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/members",
            params=_clean({"q": q, "page": page, "pagelen": pagelen}),
        )

    def get_workspace_member(self, *, workspace: str, member: str) -> dict[str, Any]:
        return self._request("GET", f"/workspaces/{workspace}/members/{member}")

    def list_workspace_permissions(
        self,
        *,
        workspace: str,
        q: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/permissions",
            params=_clean({"q": q, "page": page, "pagelen": pagelen}),
        )

    def list_workspace_repository_permissions(
        self,
        *,
        workspace: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/permissions/repositories",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def list_workspace_repository_permissions_for_repo(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/permissions/repositories/{repository}",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def list_workspace_projects(
        self,
        *,
        workspace: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_workspace_project(
        self,
        *,
        workspace: str,
        project_key: str,
    ) -> dict[str, Any]:
        return self._request("GET", f"/workspaces/{workspace}/projects/{project_key}")

    def list_workspace_user_pull_requests(
        self,
        *,
        workspace: str,
        selected_user: str,
        state: str | list[str] | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/pullrequests/{selected_user}",
            params=_clean({"state": state, "page": page, "pagelen": pagelen}),
        )

    def get_workspace_gpg_key(self, *, workspace: str) -> dict[str, Any]:
        return self._request("GET", f"/workspaces/{workspace}/settings/gpg/public-key")

    # ----- Repositories -----

    def list_public_repositories(
        self,
        *,
        after: str | None = None,
        role: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/repositories",
            params=_clean(
                {
                    "after": after,
                    "role": role,
                    "q": q,
                    "sort": sort,
                    "page": page,
                    "pagelen": pagelen,
                }
            ),
        )

    def list_repositories(
        self,
        *,
        workspace: str,
        role: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}",
            params=_clean({"role": role, "q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def get_repository(self, *, workspace: str, repository: str) -> dict[str, Any]:
        return self._request("GET", f"/repositories/{workspace}/{repository}")

    def create_repository(
        self,
        *,
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
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if scm is not None:
            body["scm"] = scm
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if is_private is not None:
            body["is_private"] = is_private
        if fork_policy is not None:
            body["fork_policy"] = fork_policy
        if language is not None:
            body["language"] = language
        if has_issues is not None:
            body["has_issues"] = has_issues
        if has_wiki is not None:
            body["has_wiki"] = has_wiki
        if project_key is not None:
            body["project"] = {"key": project_key}
        if mainbranch_name is not None:
            body["mainbranch"] = {"name": mainbranch_name}
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}",
            body=body,
        )

    def update_repository(
        self,
        *,
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
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if is_private is not None:
            body["is_private"] = is_private
        if fork_policy is not None:
            body["fork_policy"] = fork_policy
        if language is not None:
            body["language"] = language
        if has_issues is not None:
            body["has_issues"] = has_issues
        if has_wiki is not None:
            body["has_wiki"] = has_wiki
        if project_key is not None:
            body["project"] = {"key": project_key}
        if mainbranch_name is not None:
            body["mainbranch"] = {"name": mainbranch_name}
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}",
            body=body,
        )

    def delete_repository(
        self,
        *,
        workspace: str,
        repository: str,
        redirect_to: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}",
            params=_clean({"redirect_to": redirect_to}),
        )

    def list_file_history(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        path: str,
        renames: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/filehistory/{commit}/{path}",
            params=_clean(
                {"renames": renames, "q": q, "sort": sort, "page": page, "pagelen": pagelen}
            ),
        )

    def list_repository_forks(
        self,
        *,
        workspace: str,
        repository: str,
        role: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/forks",
            params=_clean({"role": role, "q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def fork_repository(
        self,
        *,
        workspace: str,
        repository: str,
        name: str | None = None,
        destination_workspace: str | None = None,
        is_private: bool | None = None,
        description: str | None = None,
        project_key: str | None = None,
        fork_policy: str | None = None,
        language: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if destination_workspace is not None:
            body["workspace"] = {"slug": destination_workspace}
        if is_private is not None:
            body["is_private"] = is_private
        if description is not None:
            body["description"] = description
        if project_key is not None:
            body["project"] = {"key": project_key}
        if fork_policy is not None:
            body["fork_policy"] = fork_policy
        if language is not None:
            body["language"] = language
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/forks",
            body=body or None,
        )

    def list_repository_webhooks(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/hooks",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_repository_webhook(
        self,
        *,
        workspace: str,
        repository: str,
        url: str,
        events: list[str],
        description: str | None = None,
        active: bool | None = None,
        secret: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url, "events": events}
        if description is not None:
            body["description"] = description
        if active is not None:
            body["active"] = active
        if secret is not None:
            body["secret"] = secret
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/hooks",
            body=body,
        )

    def delete_repository_webhook(
        self,
        *,
        workspace: str,
        repository: str,
        uid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/hooks/{uid}",
        )

    def get_repository_webhook(
        self,
        *,
        workspace: str,
        repository: str,
        uid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/hooks/{uid}",
        )

    def update_repository_webhook(
        self,
        *,
        workspace: str,
        repository: str,
        uid: str,
        url: str | None = None,
        events: list[str] | None = None,
        description: str | None = None,
        active: bool | None = None,
        secret: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if url is not None:
            body["url"] = url
        if events is not None:
            body["events"] = events
        if description is not None:
            body["description"] = description
        if active is not None:
            body["active"] = active
        if secret is not None:
            body["secret"] = secret
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/hooks/{uid}",
            body=body,
        )

    def get_repository_override_settings(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/override-settings",
        )

    def set_repository_override_settings(
        self,
        *,
        workspace: str,
        repository: str,
        settings: dict[str, bool],
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/override-settings",
            body=settings,
        )

    def list_repository_group_permissions(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/permissions-config/groups",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def delete_repository_group_permission(
        self,
        *,
        workspace: str,
        repository: str,
        group_slug: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/permissions-config/groups/{group_slug}",
        )

    def get_repository_group_permission(
        self,
        *,
        workspace: str,
        repository: str,
        group_slug: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/permissions-config/groups/{group_slug}",
        )

    def update_repository_group_permission(
        self,
        *,
        workspace: str,
        repository: str,
        group_slug: str,
        permission: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/permissions-config/groups/{group_slug}",
            body={"permission": permission},
        )

    def list_repository_user_permissions(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/permissions-config/users",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def delete_repository_user_permission(
        self,
        *,
        workspace: str,
        repository: str,
        selected_user_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/permissions-config/users/{selected_user_id}",
        )

    def get_repository_user_permission(
        self,
        *,
        workspace: str,
        repository: str,
        selected_user_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/permissions-config/users/{selected_user_id}",
        )

    def update_repository_user_permission(
        self,
        *,
        workspace: str,
        repository: str,
        selected_user_id: str,
        permission: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/permissions-config/users/{selected_user_id}",
            body={"permission": permission},
        )

    def get_repository_root_src(
        self,
        *,
        workspace: str,
        repository: str,
        format: str | None = None,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/src",
            params=_clean({"format": format}),
            text_response=True,
        )

    def create_src_commit(
        self,
        *,
        workspace: str,
        repository: str,
        message: str | None = None,
        author: str | None = None,
        parents: str | None = None,
        branch: str | None = None,
        files_to_add: dict[str, bytes] | None = None,
        files_to_delete: list[str] | None = None,
    ) -> dict[str, Any]:
        fields: list[tuple[str, str | None, bytes]] = []
        if message is not None:
            fields.append(("message", None, message.encode("utf-8")))
        if author is not None:
            fields.append(("author", None, author.encode("utf-8")))
        if parents is not None:
            fields.append(("parents", None, parents.encode("utf-8")))
        if branch is not None:
            fields.append(("branch", None, branch.encode("utf-8")))
        if files_to_delete:
            for path in files_to_delete:
                fields.append(("files", None, path.encode("utf-8")))
        if files_to_add:
            for path, content in files_to_add.items():
                fields.append((path, path.rsplit("/", 1)[-1], content))
        body_bytes, content_type = _build_multipart(fields)
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/src",
            body_bytes=body_bytes,
            body_content_type=content_type,
        )

    def get_repository_src(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        path: str,
        format: str | None = None,
        q: str | None = None,
        sort: str | None = None,
        max_depth: int | None = None,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/src/{commit}/{path}",
            params=_clean({"format": format, "q": q, "sort": sort, "max_depth": max_depth}),
            text_response=True,
        )

    def list_repository_watchers(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/watchers",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def list_user_repository_permissions(
        self,
        *,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/user/permissions/repositories",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def list_user_workspace_repository_permissions(
        self,
        *,
        workspace: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/user/workspaces/{workspace}/permissions/repositories",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    # ----- Commits -----

    def get_commit(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}",
        )

    def approve_commit(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/commit/{commit}/approve",
        )

    def unapprove_commit(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/commit/{commit}/approve",
        )

    def list_commit_comments(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}/comments",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_commit_comment(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        content: str,
        parent_id: int | None = None,
        inline_path: str | None = None,
        inline_to: int | None = None,
        inline_from: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"content": {"raw": content}}
        if parent_id is not None:
            body["parent"] = {"id": parent_id}
        if inline_path is not None:
            inline: dict[str, Any] = {"path": inline_path}
            if inline_to is not None:
                inline["to"] = inline_to
            if inline_from is not None:
                inline["from"] = inline_from
            body["inline"] = inline
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/commit/{commit}/comments",
            body=body,
        )

    def get_commit_comment(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}/comments/{comment_id}",
        )

    def update_commit_comment(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        comment_id: int,
        content: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/commit/{commit}/comments/{comment_id}",
            body={"content": {"raw": content}},
        )

    def delete_commit_comment(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/commit/{commit}/comments/{comment_id}",
        )

    def list_commit_reports(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}/reports",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_commit_report(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        report_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}/reports/{report_id}",
        )

    def create_or_update_commit_report(
        self,
        *,
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
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if details is not None:
            body["details"] = details
        if external_id is not None:
            body["external_id"] = external_id
        if reporter is not None:
            body["reporter"] = reporter
        if link is not None:
            body["link"] = link
        if remote_link_enabled is not None:
            body["remote_link_enabled"] = remote_link_enabled
        if logo_url is not None:
            body["logo_url"] = logo_url
        if report_type is not None:
            body["report_type"] = report_type
        if result is not None:
            body["result"] = result
        if data is not None:
            body["data"] = data
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/commit/{commit}/reports/{report_id}",
            body=body,
        )

    def delete_commit_report(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        report_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/commit/{commit}/reports/{report_id}",
        )

    def list_commit_report_annotations(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        report_id: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}"
            f"/reports/{report_id}/annotations",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def bulk_create_or_update_annotations(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        report_id: str,
        annotations: list[dict[str, Any]],
    ) -> Any:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/commit/{commit}"
            f"/reports/{report_id}/annotations",
            body=annotations,
        )

    def get_commit_report_annotation(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        report_id: str,
        annotation_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}"
            f"/reports/{report_id}/annotations/{annotation_id}",
        )

    def create_or_update_commit_report_annotation(
        self,
        *,
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
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if external_id is not None:
            body["external_id"] = external_id
        if annotation_type is not None:
            body["annotation_type"] = annotation_type
        if path is not None:
            body["path"] = path
        if line is not None:
            body["line"] = line
        if summary is not None:
            body["summary"] = summary
        if details is not None:
            body["details"] = details
        if result is not None:
            body["result"] = result
        if severity is not None:
            body["severity"] = severity
        if link is not None:
            body["link"] = link
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/commit/{commit}"
            f"/reports/{report_id}/annotations/{annotation_id}",
            body=body,
        )

    def delete_commit_report_annotation(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        report_id: str,
        annotation_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/commit/{commit}"
            f"/reports/{report_id}/annotations/{annotation_id}",
        )

    def list_commits(
        self,
        *,
        workspace: str,
        repository: str,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commits",
            params=_clean(
                {"include": include, "exclude": exclude, "page": page, "pagelen": pagelen}
            ),
        )

    def list_commits_with_filter(
        self,
        *,
        workspace: str,
        repository: str,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if include is not None:
            body["include"] = include
        if exclude is not None:
            body["exclude"] = exclude
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/commits",
            body=body or None,
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def list_commits_for_revision(
        self,
        *,
        workspace: str,
        repository: str,
        revision: str,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        path: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commits/{revision}",
            params=_clean(
                {
                    "include": include,
                    "exclude": exclude,
                    "path": path,
                    "page": page,
                    "pagelen": pagelen,
                }
            ),
        )

    def list_commits_for_revision_with_filter(
        self,
        *,
        workspace: str,
        repository: str,
        revision: str,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if include is not None:
            body["include"] = include
        if exclude is not None:
            body["exclude"] = exclude
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/commits/{revision}",
            body=body or None,
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_diff(
        self,
        *,
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
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/diff/{spec}",
            params=_clean(
                {
                    "context": context,
                    "path": path,
                    "ignore_whitespace": ignore_whitespace,
                    "binary": binary,
                    "renames": renames,
                    "merge": merge,
                    "topic": topic,
                }
            ),
            text_response=True,
        )

    def get_diffstat(
        self,
        *,
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
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/diffstat/{spec}",
            params=_clean(
                {
                    "ignore_whitespace": ignore_whitespace,
                    "merge": merge,
                    "path": path,
                    "renames": renames,
                    "topic": topic,
                    "page": page,
                    "pagelen": pagelen,
                }
            ),
        )

    def list_file_conflicts(
        self,
        *,
        workspace: str,
        repository: str,
        spec: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/file-conflicts/{spec}",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_merge_base(
        self,
        *,
        workspace: str,
        repository: str,
        revspec: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/merge-base/{revspec}",
        )

    def get_patch(
        self,
        *,
        workspace: str,
        repository: str,
        spec: str,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/patch/{spec}",
            text_response=True,
        )

    # ----- Pull request default reviewers -----

    def list_default_reviewers(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/default-reviewers",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def list_effective_default_reviewers(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/effective-default-reviewers",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_default_reviewer(
        self,
        *,
        workspace: str,
        repository: str,
        target_username: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/default-reviewers/{target_username}",
        )

    def add_default_reviewer(
        self,
        *,
        workspace: str,
        repository: str,
        target_username: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/default-reviewers/{target_username}",
        )

    def remove_default_reviewer(
        self,
        *,
        workspace: str,
        repository: str,
        target_username: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/default-reviewers/{target_username}",
        )

    # ----- Branch restrictions -----

    def list_branch_restrictions(
        self,
        *,
        workspace: str,
        repository: str,
        kind: str | None = None,
        pattern: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/branch-restrictions",
            params=_clean({"kind": kind, "pattern": pattern, "page": page, "pagelen": pagelen}),
        )

    def create_branch_restriction(
        self,
        *,
        workspace: str,
        repository: str,
        kind: str,
        pattern: str | None = None,
        branch_match_kind: str | None = None,
        branch_type: str | None = None,
        users: list[str] | None = None,
        groups: list[dict[str, Any]] | None = None,
        value: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"kind": kind}
        if pattern is not None:
            body["pattern"] = pattern
        if branch_match_kind is not None:
            body["branch_match_kind"] = branch_match_kind
        if branch_type is not None:
            body["branch_type"] = branch_type
        if users is not None:
            body["users"] = [{"uuid": u} for u in users]
        if groups is not None:
            body["groups"] = groups
        if value is not None:
            body["value"] = value
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/branch-restrictions",
            body=body,
        )

    def get_branch_restriction(
        self,
        *,
        workspace: str,
        repository: str,
        id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/branch-restrictions/{id}",
        )

    def update_branch_restriction(
        self,
        *,
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
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if kind is not None:
            body["kind"] = kind
        if pattern is not None:
            body["pattern"] = pattern
        if branch_match_kind is not None:
            body["branch_match_kind"] = branch_match_kind
        if branch_type is not None:
            body["branch_type"] = branch_type
        if users is not None:
            body["users"] = [{"uuid": u} for u in users]
        if groups is not None:
            body["groups"] = groups
        if value is not None:
            body["value"] = value
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/branch-restrictions/{id}",
            body=body,
        )

    def delete_branch_restriction(
        self,
        *,
        workspace: str,
        repository: str,
        id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/branch-restrictions/{id}",
        )

    # ----- Branching model -----

    def get_branching_model(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/branching-model",
        )

    def get_effective_branching_model(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/effective-branching-model",
        )

    def get_branching_model_settings(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/branching-model/settings",
        )

    def update_branching_model_settings(
        self,
        *,
        workspace: str,
        repository: str,
        development: dict[str, Any] | None = None,
        production: dict[str, Any] | None = None,
        branch_types: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if development is not None:
            body["development"] = development
        if production is not None:
            body["production"] = production
        if branch_types is not None:
            body["branch_types"] = branch_types
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/branching-model/settings",
            body=body,
        )

    def get_project_branching_model(
        self,
        *,
        workspace: str,
        project_key: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/branching-model",
        )

    def get_project_branching_model_settings(
        self,
        *,
        workspace: str,
        project_key: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/branching-model/settings",
        )

    def update_project_branching_model_settings(
        self,
        *,
        workspace: str,
        project_key: str,
        development: dict[str, Any] | None = None,
        production: dict[str, Any] | None = None,
        branch_types: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if development is not None:
            body["development"] = development
        if production is not None:
            body["production"] = production
        if branch_types is not None:
            body["branch_types"] = branch_types
        return self._request(
            "PUT",
            f"/workspaces/{workspace}/projects/{project_key}/branching-model/settings",
            body=body,
        )

    # ----- Commit build statuses -----

    def list_commit_statuses(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}/statuses",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_commit_build_status(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        key: str,
        state: str,
        url: str,
        name: str | None = None,
        description: str | None = None,
        refname: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key, "state": state, "url": url}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if refname is not None:
            body["refname"] = refname
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/commit/{commit}/statuses/build",
            body=body,
        )

    def get_commit_build_status(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        key: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/commit/{commit}/statuses/build/{key}",
        )

    def update_commit_build_status(
        self,
        *,
        workspace: str,
        repository: str,
        commit: str,
        key: str,
        state: str | None = None,
        url: str | None = None,
        name: str | None = None,
        description: str | None = None,
        refname: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if state is not None:
            body["state"] = state
        if url is not None:
            body["url"] = url
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if refname is not None:
            body["refname"] = refname
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/commit/{commit}/statuses/build/{key}",
            body=body,
        )

    # ----- Deployments: deploy keys -----

    def list_deploy_keys(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/deploy-keys",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_deploy_key(
        self,
        *,
        workspace: str,
        repository: str,
        key: str,
        label: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key}
        if label is not None:
            body["label"] = label
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/deploy-keys",
            body=body,
        )

    def get_deploy_key(
        self,
        *,
        workspace: str,
        repository: str,
        key_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/deploy-keys/{key_id}",
        )

    def update_deploy_key(
        self,
        *,
        workspace: str,
        repository: str,
        key_id: str,
        label: str | None = None,
        key: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if label is not None:
            body["label"] = label
        if key is not None:
            body["key"] = key
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/deploy-keys/{key_id}",
            body=body,
        )

    def delete_deploy_key(
        self,
        *,
        workspace: str,
        repository: str,
        key_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/deploy-keys/{key_id}",
        )

    def list_project_deploy_keys(
        self,
        *,
        workspace: str,
        project_key: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/deploy-keys",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_project_deploy_key(
        self,
        *,
        workspace: str,
        project_key: str,
        key: str,
        label: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key}
        if label is not None:
            body["label"] = label
        return self._request(
            "POST",
            f"/workspaces/{workspace}/projects/{project_key}/deploy-keys",
            body=body,
        )

    def get_project_deploy_key(
        self,
        *,
        workspace: str,
        project_key: str,
        key_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/deploy-keys/{key_id}",
        )

    def delete_project_deploy_key(
        self,
        *,
        workspace: str,
        project_key: str,
        key_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/workspaces/{workspace}/projects/{project_key}/deploy-keys/{key_id}",
        )

    # ----- Deployments: deployments & environments -----

    def list_deployments(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/deployments",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_deployment(
        self,
        *,
        workspace: str,
        repository: str,
        deployment_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/deployments/{deployment_uuid}",
        )

    def list_environments(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/environments",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_environment(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
        environment_type: dict[str, Any] | None = None,
        rank: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if environment_type is not None:
            body["environment_type"] = environment_type
        if rank is not None:
            body["rank"] = rank
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/environments",
            body=body,
        )

    def get_environment(
        self,
        *,
        workspace: str,
        repository: str,
        environment_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/environments/{environment_uuid}",
        )

    def update_environment(
        self,
        *,
        workspace: str,
        repository: str,
        environment_uuid: str,
        body: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/environments/{environment_uuid}/changes",
            body=body or {},
        )

    def delete_environment(
        self,
        *,
        workspace: str,
        repository: str,
        environment_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/environments/{environment_uuid}",
        )

    # ----- Downloads -----

    def list_downloads(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/downloads",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def upload_download(
        self,
        *,
        workspace: str,
        repository: str,
        files: dict[str, bytes],
    ) -> dict[str, Any]:
        fields: list[tuple[str, str | None, bytes]] = []
        for filename, content in files.items():
            fields.append(("files", filename, content))
        body_bytes, content_type = _build_multipart(fields)
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/downloads",
            body_bytes=body_bytes,
            body_content_type=content_type,
        )

    def get_download(
        self,
        *,
        workspace: str,
        repository: str,
        filename: str,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/downloads/{filename}",
            text_response=True,
        )

    def delete_download(
        self,
        *,
        workspace: str,
        repository: str,
        filename: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/downloads/{filename}",
        )

    # ----- GPG keys -----

    def list_user_gpg_keys(
        self,
        *,
        selected_user: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/users/{selected_user}/gpg-keys",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_user_gpg_key(
        self,
        *,
        selected_user: str,
        key: str,
        name: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key}
        if name is not None:
            body["name"] = name
        return self._request(
            "POST",
            f"/users/{selected_user}/gpg-keys",
            body=body,
        )

    def get_user_gpg_key(
        self,
        *,
        selected_user: str,
        fingerprint: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/users/{selected_user}/gpg-keys/{fingerprint}",
        )

    def delete_user_gpg_key(
        self,
        *,
        selected_user: str,
        fingerprint: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/users/{selected_user}/gpg-keys/{fingerprint}",
        )

    # ----- Issue tracker -----

    def list_components(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/components",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def get_component(
        self,
        *,
        workspace: str,
        repository: str,
        component_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/components/{component_id}",
        )

    def list_milestones(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/milestones",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def get_milestone(
        self,
        *,
        workspace: str,
        repository: str,
        milestone_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/milestones/{milestone_id}",
        )

    def list_versions(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/versions",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def get_version(
        self,
        *,
        workspace: str,
        repository: str,
        version_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/versions/{version_id}",
        )

    def list_issues(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_issue(
        self,
        *,
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
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"title": title}
        if content is not None:
            body["content"] = {"raw": content}
        if kind is not None:
            body["kind"] = kind
        if priority is not None:
            body["priority"] = priority
        if state is not None:
            body["state"] = state
        if component is not None:
            body["component"] = {"name": component}
        if milestone is not None:
            body["milestone"] = {"name": milestone}
        if version is not None:
            body["version"] = {"name": version}
        if assignee is not None:
            body["assignee"] = {"uuid": assignee}
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/issues",
            body=body,
        )

    def get_issue(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}",
        )

    def update_issue(
        self,
        *,
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
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if content is not None:
            body["content"] = {"raw": content}
        if kind is not None:
            body["kind"] = kind
        if priority is not None:
            body["priority"] = priority
        if state is not None:
            body["state"] = state
        if component is not None:
            body["component"] = {"name": component}
        if milestone is not None:
            body["milestone"] = {"name": milestone}
        if version is not None:
            body["version"] = {"name": version}
        if assignee is not None:
            body["assignee"] = {"uuid": assignee}
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}",
            body=body,
        )

    def delete_issue(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}",
        )

    def export_issues(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/issues/export",
        )

    def get_issue_export(
        self,
        *,
        workspace: str,
        repository: str,
        repo_name: str,
        task_id: str,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/export/{repo_name}-issues-{task_id}.zip",
            text_response=True,
        )

    def get_issue_import_status(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/import",
        )

    def import_issues(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/issues/import",
        )

    def list_issue_attachments(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/attachments",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def upload_issue_attachment(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        files: dict[str, bytes],
    ) -> dict[str, Any]:
        fields: list[tuple[str, str | None, bytes]] = []
        for filename, content in files.items():
            fields.append(("files", filename, content))
        body_bytes, content_type = _build_multipart(fields)
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/attachments",
            body_bytes=body_bytes,
            body_content_type=content_type,
        )

    def get_issue_attachment(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        path: str,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/attachments/{path}",
            text_response=True,
        )

    def delete_issue_attachment(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        path: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/attachments/{path}",
        )

    def list_issue_changes(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/changes",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_issue_change(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        changes: dict[str, Any] | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if changes is not None:
            body["changes"] = changes
        if message is not None:
            body["message"] = {"raw": message}
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/changes",
            body=body,
        )

    def get_issue_change(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        change_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/changes/{change_id}",
        )

    def list_issue_comments(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/comments",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_issue_comment(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        content: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/comments",
            body={"content": {"raw": content}},
        )

    def get_issue_comment(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/comments/{comment_id}",
        )

    def update_issue_comment(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        comment_id: int,
        content: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/comments/{comment_id}",
            body={"content": {"raw": content}},
        )

    def delete_issue_comment(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/comments/{comment_id}",
        )

    def get_issue_vote(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/vote",
        )

    def vote_for_issue(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/vote",
        )

    def unvote_issue(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/vote",
        )

    def get_issue_watch(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/watch",
        )

    def watch_issue(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/watch",
        )

    def unwatch_issue(
        self,
        *,
        workspace: str,
        repository: str,
        issue_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/issues/{issue_id}/watch",
        )

    # ----- Projects (workspace-scoped, mutations) -----

    def create_workspace_project(
        self,
        *,
        workspace: str,
        key: str,
        name: str,
        description: str | None = None,
        is_private: bool | None = None,
        avatar: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key, "name": name}
        if description is not None:
            body["description"] = description
        if is_private is not None:
            body["is_private"] = is_private
        if avatar is not None:
            body["avatar"] = avatar
        return self._request(
            "POST",
            f"/workspaces/{workspace}/projects",
            body=body,
        )

    def update_workspace_project(
        self,
        *,
        workspace: str,
        project_key: str,
        key: str | None = None,
        name: str | None = None,
        description: str | None = None,
        is_private: bool | None = None,
        avatar: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if key is not None:
            body["key"] = key
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if is_private is not None:
            body["is_private"] = is_private
        if avatar is not None:
            body["avatar"] = avatar
        return self._request(
            "PUT",
            f"/workspaces/{workspace}/projects/{project_key}",
            body=body,
        )

    def delete_workspace_project(
        self,
        *,
        workspace: str,
        project_key: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/workspaces/{workspace}/projects/{project_key}",
        )

    def list_project_default_reviewers(
        self,
        *,
        workspace: str,
        project_key: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/default-reviewers",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_project_default_reviewer(
        self,
        *,
        workspace: str,
        project_key: str,
        selected_user: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}",
        )

    def add_project_default_reviewer(
        self,
        *,
        workspace: str,
        project_key: str,
        selected_user: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}",
        )

    def remove_project_default_reviewer(
        self,
        *,
        workspace: str,
        project_key: str,
        selected_user: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/workspaces/{workspace}/projects/{project_key}/default-reviewers/{selected_user}",
        )

    def list_project_group_permissions(
        self,
        *,
        workspace: str,
        project_key: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/permissions-config/groups",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_project_group_permission(
        self,
        *,
        workspace: str,
        project_key: str,
        group_slug: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/permissions-config/groups/{group_slug}",
        )

    def update_project_group_permission(
        self,
        *,
        workspace: str,
        project_key: str,
        group_slug: str,
        permission: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/workspaces/{workspace}/projects/{project_key}/permissions-config/groups/{group_slug}",
            body={"permission": permission},
        )

    def delete_project_group_permission(
        self,
        *,
        workspace: str,
        project_key: str,
        group_slug: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/workspaces/{workspace}/projects/{project_key}/permissions-config/groups/{group_slug}",
        )

    def list_project_user_permissions(
        self,
        *,
        workspace: str,
        project_key: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}/permissions-config/users",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_project_user_permission(
        self,
        *,
        workspace: str,
        project_key: str,
        selected_user_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/projects/{project_key}"
            f"/permissions-config/users/{selected_user_id}",
        )

    def update_project_user_permission(
        self,
        *,
        workspace: str,
        project_key: str,
        selected_user_id: str,
        permission: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/workspaces/{workspace}/projects/{project_key}"
            f"/permissions-config/users/{selected_user_id}",
            body={"permission": permission},
        )

    def delete_project_user_permission(
        self,
        *,
        workspace: str,
        project_key: str,
        selected_user_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/workspaces/{workspace}/projects/{project_key}"
            f"/permissions-config/users/{selected_user_id}",
        )

    # ----- Refs (branches & tags) -----

    def list_refs(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/refs",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def list_branches(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/refs/branches",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_branch(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
        target_hash: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/refs/branches",
            body={"name": name, "target": {"hash": target_hash}},
        )

    def get_branch(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/refs/branches/{name}",
        )

    def delete_branch(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/refs/branches/{name}",
        )

    def list_tags(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/refs/tags",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_tag(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
        target_hash: str,
        message: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name, "target": {"hash": target_hash}}
        if message is not None:
            body["message"] = message
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/refs/tags",
            body=body,
        )

    def get_tag(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/refs/tags/{name}",
        )

    def delete_tag(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/refs/tags/{name}",
        )

    # ----- Search -----

    def search_workspace_code(
        self,
        *,
        workspace: str,
        search_query: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/search/code",
            params=_clean({"search_query": search_query, "page": page, "pagelen": pagelen}),
        )

    def search_user_code(
        self,
        *,
        selected_user: str,
        search_query: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/users/{selected_user}/search/code",
            params=_clean({"search_query": search_query, "page": page, "pagelen": pagelen}),
        )

    # ----- Snippets -----

    def list_snippets(
        self,
        *,
        role: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/snippets",
            params=_clean({"role": role, "page": page, "pagelen": pagelen}),
        )

    def create_snippet(
        self,
        *,
        title: str | None = None,
        is_private: bool | None = None,
        scm: str | None = None,
        files: dict[str, bytes] | None = None,
    ) -> dict[str, Any]:
        fields: list[tuple[str, str | None, bytes]] = []
        if title is not None:
            fields.append(("title", None, title.encode("utf-8")))
        if is_private is not None:
            fields.append(("is_private", None, str(is_private).lower().encode("utf-8")))
        if scm is not None:
            fields.append(("scm", None, scm.encode("utf-8")))
        if files:
            for filename, content in files.items():
                fields.append(("file", filename, content))
        body_bytes, content_type = _build_multipart(fields)
        return self._request(
            "POST",
            "/snippets",
            body_bytes=body_bytes,
            body_content_type=content_type,
        )

    def list_workspace_snippets(
        self,
        *,
        workspace: str,
        role: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}",
            params=_clean({"role": role, "page": page, "pagelen": pagelen}),
        )

    def create_workspace_snippet(
        self,
        *,
        workspace: str,
        title: str | None = None,
        is_private: bool | None = None,
        scm: str | None = None,
        files: dict[str, bytes] | None = None,
    ) -> dict[str, Any]:
        fields: list[tuple[str, str | None, bytes]] = []
        if title is not None:
            fields.append(("title", None, title.encode("utf-8")))
        if is_private is not None:
            fields.append(("is_private", None, str(is_private).lower().encode("utf-8")))
        if scm is not None:
            fields.append(("scm", None, scm.encode("utf-8")))
        if files:
            for filename, content in files.items():
                fields.append(("file", filename, content))
        body_bytes, content_type = _build_multipart(fields)
        return self._request(
            "POST",
            f"/snippets/{workspace}",
            body_bytes=body_bytes,
            body_content_type=content_type,
        )

    def get_snippet(
        self,
        *,
        workspace: str,
        encoded_id: str,
    ) -> dict[str, Any]:
        return self._request("GET", f"/snippets/{workspace}/{encoded_id}")

    def update_snippet(
        self,
        *,
        workspace: str,
        encoded_id: str,
        title: str | None = None,
        is_private: bool | None = None,
        files: dict[str, bytes] | None = None,
    ) -> dict[str, Any]:
        fields: list[tuple[str, str | None, bytes]] = []
        if title is not None:
            fields.append(("title", None, title.encode("utf-8")))
        if is_private is not None:
            fields.append(("is_private", None, str(is_private).lower().encode("utf-8")))
        if files:
            for filename, content in files.items():
                fields.append(("file", filename, content))
        body_bytes, content_type = _build_multipart(fields)
        return self._request(
            "PUT",
            f"/snippets/{workspace}/{encoded_id}",
            body_bytes=body_bytes,
            body_content_type=content_type,
        )

    def delete_snippet(
        self,
        *,
        workspace: str,
        encoded_id: str,
    ) -> dict[str, Any]:
        return self._request("DELETE", f"/snippets/{workspace}/{encoded_id}")

    def list_snippet_comments(
        self,
        *,
        workspace: str,
        encoded_id: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/comments",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_snippet_comment(
        self,
        *,
        workspace: str,
        encoded_id: str,
        content: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/snippets/{workspace}/{encoded_id}/comments",
            body={"content": {"raw": content}},
        )

    def get_snippet_comment(
        self,
        *,
        workspace: str,
        encoded_id: str,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/comments/{comment_id}",
        )

    def update_snippet_comment(
        self,
        *,
        workspace: str,
        encoded_id: str,
        comment_id: int,
        content: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/snippets/{workspace}/{encoded_id}/comments/{comment_id}",
            body={"content": {"raw": content}},
        )

    def delete_snippet_comment(
        self,
        *,
        workspace: str,
        encoded_id: str,
        comment_id: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/snippets/{workspace}/{encoded_id}/comments/{comment_id}",
        )

    def list_snippet_commits(
        self,
        *,
        workspace: str,
        encoded_id: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/commits",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_snippet_commit(
        self,
        *,
        workspace: str,
        encoded_id: str,
        revision: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/commits/{revision}",
        )

    def get_snippet_file(
        self,
        *,
        workspace: str,
        encoded_id: str,
        path: str,
    ) -> str:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/files/{path}",
            text_response=True,
        )

    def get_snippet_watch(
        self,
        *,
        workspace: str,
        encoded_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/watch",
        )

    def watch_snippet(
        self,
        *,
        workspace: str,
        encoded_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/snippets/{workspace}/{encoded_id}/watch",
        )

    def unwatch_snippet(
        self,
        *,
        workspace: str,
        encoded_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/snippets/{workspace}/{encoded_id}/watch",
        )

    def list_snippet_watchers(
        self,
        *,
        workspace: str,
        encoded_id: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/watchers",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_snippet_at_revision(
        self,
        *,
        workspace: str,
        encoded_id: str,
        node_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/{node_id}",
        )

    def update_snippet_at_revision(
        self,
        *,
        workspace: str,
        encoded_id: str,
        node_id: str,
        title: str | None = None,
        is_private: bool | None = None,
        files: dict[str, bytes] | None = None,
    ) -> dict[str, Any]:
        fields: list[tuple[str, str | None, bytes]] = []
        if title is not None:
            fields.append(("title", None, title.encode("utf-8")))
        if is_private is not None:
            fields.append(("is_private", None, str(is_private).lower().encode("utf-8")))
        if files:
            for filename, content in files.items():
                fields.append(("file", filename, content))
        body_bytes, content_type = _build_multipart(fields)
        return self._request(
            "PUT",
            f"/snippets/{workspace}/{encoded_id}/{node_id}",
            body_bytes=body_bytes,
            body_content_type=content_type,
        )

    def delete_snippet_at_revision(
        self,
        *,
        workspace: str,
        encoded_id: str,
        node_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/snippets/{workspace}/{encoded_id}/{node_id}",
        )

    def get_snippet_file_at_revision(
        self,
        *,
        workspace: str,
        encoded_id: str,
        node_id: str,
        path: str,
    ) -> str:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/{node_id}/files/{path}",
            text_response=True,
        )

    def get_snippet_diff(
        self,
        *,
        workspace: str,
        encoded_id: str,
        revision: str,
    ) -> str:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/{revision}/diff",
            text_response=True,
        )

    def get_snippet_patch(
        self,
        *,
        workspace: str,
        encoded_id: str,
        revision: str,
    ) -> str:
        return self._request(
            "GET",
            f"/snippets/{workspace}/{encoded_id}/{revision}/patch",
            text_response=True,
        )

    # ----- SSH keys -----

    def list_user_ssh_keys(
        self,
        *,
        selected_user: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/users/{selected_user}/ssh-keys",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_user_ssh_key(
        self,
        *,
        selected_user: str,
        key: str,
        label: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key}
        if label is not None:
            body["label"] = label
        return self._request(
            "POST",
            f"/users/{selected_user}/ssh-keys",
            body=body,
        )

    def get_user_ssh_key(
        self,
        *,
        selected_user: str,
        key_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/users/{selected_user}/ssh-keys/{key_id}",
        )

    def update_user_ssh_key(
        self,
        *,
        selected_user: str,
        key_id: str,
        label: str | None = None,
        key: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if label is not None:
            body["label"] = label
        if key is not None:
            body["key"] = key
        return self._request(
            "PUT",
            f"/users/{selected_user}/ssh-keys/{key_id}",
            body=body,
        )

    def delete_user_ssh_key(
        self,
        *,
        selected_user: str,
        key_id: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/users/{selected_user}/ssh-keys/{key_id}",
        )

    # ----- Users -----

    def get_user(
        self,
        *,
        selected_user: str,
    ) -> dict[str, Any]:
        return self._request("GET", f"/users/{selected_user}")

    def list_user_emails(
        self,
        *,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            "/user/emails",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_user_email(self, *, email: str) -> dict[str, Any]:
        return self._request("GET", f"/user/emails/{email}")

    # ----- Webhook event types -----

    def list_hook_event_subjects(self) -> dict[str, Any]:
        return self._request("GET", "/hook_events")

    def list_hook_events(self, *, subject_type: str) -> dict[str, Any]:
        return self._request("GET", f"/hook_events/{subject_type}")

    # ----- Pipelines: pipelines & steps -----

    def list_pipelines(
        self,
        *,
        workspace: str,
        repository: str,
        q: str | None = None,
        sort: str | None = None,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines",
            params=_clean({"q": q, "sort": sort, "page": page, "pagelen": pagelen}),
        )

    def create_pipeline(
        self,
        *,
        workspace: str,
        repository: str,
        target: dict[str, Any],
        variables: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"target": target}
        if variables is not None:
            body["variables"] = variables
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pipelines",
            body=body,
        )

    def get_pipeline(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}",
        )

    def stop_pipeline(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}/stopPipeline",
        )

    def list_pipeline_steps(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}/steps",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def get_pipeline_step(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
        step_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}/steps/{step_uuid}",
        )

    def get_pipeline_step_log(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
        step_uuid: str,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}"
            f"/steps/{step_uuid}/log",
            text_response=True,
        )

    def get_pipeline_step_container_log(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
        step_uuid: str,
        log_uuid: str,
    ) -> str:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}"
            f"/steps/{step_uuid}/logs/{log_uuid}",
            text_response=True,
        )

    def list_pipeline_step_test_reports(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
        step_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}"
            f"/steps/{step_uuid}/test_reports",
        )

    def list_pipeline_step_test_cases(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
        step_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}"
            f"/steps/{step_uuid}/test_reports/test_cases",
        )

    def list_pipeline_step_test_case_reasons(
        self,
        *,
        workspace: str,
        repository: str,
        pipeline_uuid: str,
        step_uuid: str,
        test_case_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines/{pipeline_uuid}"
            f"/steps/{step_uuid}/test_reports/test_cases/{test_case_uuid}/test_case_reasons",
        )

    # ----- Pipelines: configuration -----

    def get_pipeline_config(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config",
        )

    def update_pipeline_config(
        self,
        *,
        workspace: str,
        repository: str,
        enabled: bool | None = None,
        repository_pipeline: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if enabled is not None:
            body["enabled"] = enabled
        if repository_pipeline is not None:
            body["repository"] = repository_pipeline
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pipelines_config",
            body=body,
        )

    def update_pipeline_build_number(
        self,
        *,
        workspace: str,
        repository: str,
        next_build_number: int,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pipelines_config/build_number",
            body={"next": next_build_number},
        )

    # ----- Pipelines: schedules -----

    def list_pipeline_schedules(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config/schedules",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_pipeline_schedule(
        self,
        *,
        workspace: str,
        repository: str,
        target: dict[str, Any],
        cron_pattern: str,
        enabled: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"target": target, "cron_pattern": cron_pattern}
        if enabled is not None:
            body["enabled"] = enabled
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pipelines_config/schedules",
            body=body,
        )

    def get_pipeline_schedule(
        self,
        *,
        workspace: str,
        repository: str,
        schedule_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config/schedules/{schedule_uuid}",
        )

    def update_pipeline_schedule(
        self,
        *,
        workspace: str,
        repository: str,
        schedule_uuid: str,
        enabled: bool | None = None,
        cron_pattern: str | None = None,
        target: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if enabled is not None:
            body["enabled"] = enabled
        if cron_pattern is not None:
            body["cron_pattern"] = cron_pattern
        if target is not None:
            body["target"] = target
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pipelines_config/schedules/{schedule_uuid}",
            body=body,
        )

    def delete_pipeline_schedule(
        self,
        *,
        workspace: str,
        repository: str,
        schedule_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pipelines_config/schedules/{schedule_uuid}",
        )

    def list_pipeline_schedule_executions(
        self,
        *,
        workspace: str,
        repository: str,
        schedule_uuid: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config"
            f"/schedules/{schedule_uuid}/executions",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    # ----- Pipelines: ssh key pair -----

    def get_pipeline_ssh_key_pair(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config/ssh/key_pair",
        )

    def update_pipeline_ssh_key_pair(
        self,
        *,
        workspace: str,
        repository: str,
        public_key: str,
        private_key: str,
    ) -> dict[str, Any]:
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pipelines_config/ssh/key_pair",
            body={"public_key": public_key, "private_key": private_key},
        )

    def delete_pipeline_ssh_key_pair(
        self,
        *,
        workspace: str,
        repository: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pipelines_config/ssh/key_pair",
        )

    # ----- Pipelines: known hosts -----

    def list_pipeline_known_hosts(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config/ssh/known_hosts",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_pipeline_known_host(
        self,
        *,
        workspace: str,
        repository: str,
        hostname: str,
        public_key: dict[str, Any],
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pipelines_config/ssh/known_hosts",
            body={"hostname": hostname, "public_key": public_key},
        )

    def get_pipeline_known_host(
        self,
        *,
        workspace: str,
        repository: str,
        known_host_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config"
            f"/ssh/known_hosts/{known_host_uuid}",
        )

    def update_pipeline_known_host(
        self,
        *,
        workspace: str,
        repository: str,
        known_host_uuid: str,
        hostname: str | None = None,
        public_key: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if hostname is not None:
            body["hostname"] = hostname
        if public_key is not None:
            body["public_key"] = public_key
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pipelines_config"
            f"/ssh/known_hosts/{known_host_uuid}",
            body=body,
        )

    def delete_pipeline_known_host(
        self,
        *,
        workspace: str,
        repository: str,
        known_host_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pipelines_config"
            f"/ssh/known_hosts/{known_host_uuid}",
        )

    # ----- Pipelines: variables -----

    def list_pipeline_variables(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config/variables",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_pipeline_variable(
        self,
        *,
        workspace: str,
        repository: str,
        key: str,
        value: str,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key, "value": value}
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pipelines_config/variables",
            body=body,
        )

    def get_pipeline_variable(
        self,
        *,
        workspace: str,
        repository: str,
        variable_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines_config/variables/{variable_uuid}",
        )

    def update_pipeline_variable(
        self,
        *,
        workspace: str,
        repository: str,
        variable_uuid: str,
        key: str | None = None,
        value: str | None = None,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if key is not None:
            body["key"] = key
        if value is not None:
            body["value"] = value
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pipelines_config/variables/{variable_uuid}",
            body=body,
        )

    def delete_pipeline_variable(
        self,
        *,
        workspace: str,
        repository: str,
        variable_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pipelines_config/variables/{variable_uuid}",
        )

    # ----- Pipelines: caches -----

    def list_pipeline_caches(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines-config/caches",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def delete_pipeline_caches(
        self,
        *,
        workspace: str,
        repository: str,
        name: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pipelines-config/caches",
            params=_clean({"name": name}),
        )

    def delete_pipeline_cache(
        self,
        *,
        workspace: str,
        repository: str,
        cache_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pipelines-config/caches/{cache_uuid}",
        )

    def get_pipeline_cache_content_uri(
        self,
        *,
        workspace: str,
        repository: str,
        cache_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines-config"
            f"/caches/{cache_uuid}/content-uri",
        )

    # ----- Pipelines: repository runners -----

    def list_repository_pipeline_runners(
        self,
        *,
        workspace: str,
        repository: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines-config/runners",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_repository_pipeline_runner(
        self,
        *,
        workspace: str,
        repository: str,
        name: str,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if labels is not None:
            body["labels"] = labels
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/pipelines-config/runners",
            body=body,
        )

    def get_repository_pipeline_runner(
        self,
        *,
        workspace: str,
        repository: str,
        runner_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/pipelines-config/runners/{runner_uuid}",
        )

    def update_repository_pipeline_runner(
        self,
        *,
        workspace: str,
        repository: str,
        runner_uuid: str,
        name: str | None = None,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if labels is not None:
            body["labels"] = labels
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/pipelines-config/runners/{runner_uuid}",
            body=body,
        )

    def delete_repository_pipeline_runner(
        self,
        *,
        workspace: str,
        repository: str,
        runner_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/pipelines-config/runners/{runner_uuid}",
        )

    # ----- Pipelines: workspace runners -----

    def list_workspace_pipeline_runners(
        self,
        *,
        workspace: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/pipelines-config/runners",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_workspace_pipeline_runner(
        self,
        *,
        workspace: str,
        name: str,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if labels is not None:
            body["labels"] = labels
        return self._request(
            "POST",
            f"/workspaces/{workspace}/pipelines-config/runners",
            body=body,
        )

    def get_workspace_pipeline_runner(
        self,
        *,
        workspace: str,
        runner_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}",
        )

    def update_workspace_pipeline_runner(
        self,
        *,
        workspace: str,
        runner_uuid: str,
        name: str | None = None,
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if name is not None:
            body["name"] = name
        if labels is not None:
            body["labels"] = labels
        return self._request(
            "PUT",
            f"/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}",
            body=body,
        )

    def delete_workspace_pipeline_runner(
        self,
        *,
        workspace: str,
        runner_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/workspaces/{workspace}/pipelines-config/runners/{runner_uuid}",
        )

    # ----- Pipelines: workspace variables -----

    def list_workspace_pipeline_variables(
        self,
        *,
        workspace: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/pipelines-config/variables",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_workspace_pipeline_variable(
        self,
        *,
        workspace: str,
        key: str,
        value: str,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key, "value": value}
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "POST",
            f"/workspaces/{workspace}/pipelines-config/variables",
            body=body,
        )

    def get_workspace_pipeline_variable(
        self,
        *,
        workspace: str,
        variable_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}",
        )

    def update_workspace_pipeline_variable(
        self,
        *,
        workspace: str,
        variable_uuid: str,
        key: str | None = None,
        value: str | None = None,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if key is not None:
            body["key"] = key
        if value is not None:
            body["value"] = value
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "PUT",
            f"/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}",
            body=body,
        )

    def delete_workspace_pipeline_variable(
        self,
        *,
        workspace: str,
        variable_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/workspaces/{workspace}/pipelines-config/variables/{variable_uuid}",
        )

    # ----- Pipelines: user variables -----

    def list_user_pipeline_variables(
        self,
        *,
        selected_user: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/users/{selected_user}/pipelines_config/variables",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_user_pipeline_variable(
        self,
        *,
        selected_user: str,
        key: str,
        value: str,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key, "value": value}
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "POST",
            f"/users/{selected_user}/pipelines_config/variables",
            body=body,
        )

    def get_user_pipeline_variable(
        self,
        *,
        selected_user: str,
        variable_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/users/{selected_user}/pipelines_config/variables/{variable_uuid}",
        )

    def update_user_pipeline_variable(
        self,
        *,
        selected_user: str,
        variable_uuid: str,
        key: str | None = None,
        value: str | None = None,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if key is not None:
            body["key"] = key
        if value is not None:
            body["value"] = value
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "PUT",
            f"/users/{selected_user}/pipelines_config/variables/{variable_uuid}",
            body=body,
        )

    def delete_user_pipeline_variable(
        self,
        *,
        selected_user: str,
        variable_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/users/{selected_user}/pipelines_config/variables/{variable_uuid}",
        )

    # ----- Pipelines: deployment variables -----

    def list_deployment_variables(
        self,
        *,
        workspace: str,
        repository: str,
        environment_uuid: str,
        page: int | None = None,
        pagelen: int | None = None,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/repositories/{workspace}/{repository}/deployments_config"
            f"/environments/{environment_uuid}/variables",
            params=_clean({"page": page, "pagelen": pagelen}),
        )

    def create_deployment_variable(
        self,
        *,
        workspace: str,
        repository: str,
        environment_uuid: str,
        key: str,
        value: str,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"key": key, "value": value}
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "POST",
            f"/repositories/{workspace}/{repository}/deployments_config"
            f"/environments/{environment_uuid}/variables",
            body=body,
        )

    def update_deployment_variable(
        self,
        *,
        workspace: str,
        repository: str,
        environment_uuid: str,
        variable_uuid: str,
        key: str | None = None,
        value: str | None = None,
        secured: bool | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {}
        if key is not None:
            body["key"] = key
        if value is not None:
            body["value"] = value
        if secured is not None:
            body["secured"] = secured
        return self._request(
            "PUT",
            f"/repositories/{workspace}/{repository}/deployments_config"
            f"/environments/{environment_uuid}/variables/{variable_uuid}",
            body=body,
        )

    def delete_deployment_variable(
        self,
        *,
        workspace: str,
        repository: str,
        environment_uuid: str,
        variable_uuid: str,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/repositories/{workspace}/{repository}/deployments_config"
            f"/environments/{environment_uuid}/variables/{variable_uuid}",
        )

    # ----- Pipelines: OIDC -----

    def get_pipelines_oidc_configuration(
        self,
        *,
        workspace: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/pipelines-config/identity/oidc/.well-known"
            f"/openid-configuration",
        )

    def get_pipelines_oidc_keys(
        self,
        *,
        workspace: str,
    ) -> dict[str, Any]:
        return self._request(
            "GET",
            f"/workspaces/{workspace}/pipelines-config/identity/oidc/keys.json",
        )

    def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
        body_bytes: bytes | None = None,
        body_content_type: str | None = None,
        params: dict[str, Any] | None = None,
        text_response: bool = False,
    ) -> Any:
        url = f"{BASE_URL}{path}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params, doseq=True)}"
        headers = {
            "Authorization": self._basic_auth_header(),
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if body is not None:
            data = json.dumps(body).encode()
            headers["Content-Type"] = "application/json"
        elif body_bytes is not None:
            data = body_bytes
            if body_content_type is not None:
                headers["Content-Type"] = body_content_type
        else:
            data = None
        request = urllib.request.Request(url, data=data, headers=headers, method=method)

        for attempt in range(self._max_retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self._timeout) as response:
                    raw = response.read()
                    if text_response:
                        return raw.decode("utf-8", errors="replace")
                    if not raw:
                        return {}
                    return json.loads(raw)
            except urllib.error.HTTPError as exc:
                if exc.code == 401:
                    raise AuthenticationError(
                        "Authentication failed (HTTP 401). "
                        "Check BITBUCKET_EMAIL and BITBUCKET_API_TOKEN."
                    ) from exc
                if attempt < self._max_retries and _should_retry(method, exc):
                    time.sleep(_retry_delay(attempt, exc))
                    continue
                body_text = exc.read().decode("utf-8", errors="replace")
                raise ResponseError(f"Bitbucket API error (HTTP {exc.code}): {body_text}") from exc
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt < self._max_retries and _should_retry(method, exc):
                    time.sleep(_retry_delay(attempt, exc))
                    continue
                reason = getattr(exc, "reason", exc)
                raise ResponseError(f"Bitbucket API request failed: {reason}") from exc

    def _basic_auth_header(self) -> str:
        token = f"{self._email}:{self._api_token}".encode()
        return f"Basic {base64.b64encode(token).decode('ascii')}"


def _clean(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be a number, got {raw!r}") from exc


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ConfigurationError(f"{name} must be an integer, got {raw!r}") from exc


def _should_retry(method: str, exc: Exception) -> bool:
    """Decide whether a failed request should be retried.

    Reads (and other idempotent methods) retry on any retryable status or
    network error. Non-idempotent writes (POST) only retry on HTTP 429, where
    the request was rate-limited and provably not processed, so a retry cannot
    duplicate the side effect.
    """
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code not in RETRYABLE_STATUS:
            return False
        if exc.code == 429:
            return True
        return method in IDEMPOTENT_METHODS
    # Connection/timeout error: outcome is unknown, so only retry idempotent methods.
    return method in IDEMPOTENT_METHODS


def _retry_delay(attempt: int, exc: Exception) -> float:
    """Seconds to wait before the next attempt (0-indexed)."""
    retry_after = _parse_retry_after(exc)
    if retry_after is not None:
        return min(retry_after, RETRY_MAX_DELAY)
    return min(RETRY_MAX_DELAY, RETRY_BACKOFF_BASE * (2**attempt))


def _parse_retry_after(exc: Exception) -> float | None:
    """Return the Retry-After header value in seconds, if present and numeric."""
    if isinstance(exc, urllib.error.HTTPError) and exc.headers is not None:
        value = exc.headers.get("Retry-After")
        if value is not None and value.strip().isdigit():
            return float(value.strip())
    return None


def _build_multipart(
    fields: list[tuple[str, str | None, bytes]],
) -> tuple[bytes, str]:
    boundary = f"BitbucketBoundary{_uuid.uuid4().hex}"
    parts: list[bytes] = []
    for name, filename, content in fields:
        parts.append(f"--{boundary}\r\n".encode())
        if filename is None:
            parts.append(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        else:
            parts.append(
                (
                    f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'
                    f"Content-Type: application/octet-stream\r\n\r\n"
                ).encode()
            )
        parts.append(content)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"
