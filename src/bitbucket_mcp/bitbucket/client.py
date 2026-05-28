from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request
import uuid as _uuid
from typing import Any

BASE_URL = "https://api.bitbucket.org/2.0"


class BitbucketError(Exception):
    pass


class ConfigurationError(BitbucketError):
    pass


class AuthenticationError(BitbucketError):
    pass


class ResponseError(BitbucketError):
    pass


class Client:
    def __init__(self, email: str | None = None, api_token: str | None = None) -> None:
        email = email or os.environ.get("BITBUCKET_EMAIL")
        api_token = api_token or os.environ.get("BITBUCKET_API_TOKEN")

        if not email:
            raise ConfigurationError("BITBUCKET_EMAIL is not set")
        if not api_token:
            raise ConfigurationError("BITBUCKET_API_TOKEN is not set")

        self._email = email
        self._api_token = api_token

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

        try:
            with urllib.request.urlopen(request) as response:
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
            body_text = exc.read().decode("utf-8", errors="replace")
            raise ResponseError(f"Bitbucket API error (HTTP {exc.code}): {body_text}") from exc

    def _basic_auth_header(self) -> str:
        token = f"{self._email}:{self._api_token}".encode()
        return f"Basic {base64.b64encode(token).decode('ascii')}"


def _clean(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}


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
