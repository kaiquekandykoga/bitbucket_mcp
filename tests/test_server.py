from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from bitbucket_mcp import server


@pytest.fixture
def fake_client(monkeypatch):
    instance = MagicMock()
    monkeypatch.setattr(server, "Client", MagicMock(return_value=instance))
    return instance


class TestCurrentUserTool:
    def test_returns_client_result(self, fake_client):
        fake_client.current_user.return_value = {"display_name": "Kaique"}

        result = server.current_user()

        assert result == {"display_name": "Kaique"}
        fake_client.current_user.assert_called_once_with()


class TestCreatePullRequestTool:
    def test_passes_args_with_defaults(self, fake_client):
        fake_client.create_pull_request.return_value = {"id": 42, "title": "My PR"}

        result = server.create_pull_request(
            workspace="ws",
            repository="repo",
            title="My PR",
            source_branch="feature/x",
        )

        fake_client.create_pull_request.assert_called_once_with(
            workspace="ws",
            repository="repo",
            title="My PR",
            source_branch="feature/x",
            destination_branch="main",
            description=None,
            close_source_branch=None,
            reviewers=None,
        )
        assert result == {"id": 42, "title": "My PR"}

    def test_passes_overrides(self, fake_client):
        fake_client.create_pull_request.return_value = {"id": 1}

        server.create_pull_request(
            workspace="ws",
            repository="repo",
            title="t",
            source_branch="src",
            destination_branch="develop",
            description="hello",
            close_source_branch=True,
            reviewers=["{u}"],
        )

        fake_client.create_pull_request.assert_called_once_with(
            workspace="ws",
            repository="repo",
            title="t",
            source_branch="src",
            destination_branch="develop",
            description="hello",
            close_source_branch=True,
            reviewers=["{u}"],
        )


class TestListPullRequestsTool:
    def test_default(self, fake_client):
        fake_client.list_pull_requests.return_value = {"values": []}

        result = server.list_pull_requests(workspace="ws", repository="repo")

        fake_client.list_pull_requests.assert_called_once_with(
            workspace="ws",
            repository="repo",
            state=None,
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )
        assert result == {"values": []}

    def test_with_filters(self, fake_client):
        fake_client.list_pull_requests.return_value = {}

        server.list_pull_requests(
            workspace="ws",
            repository="repo",
            state="OPEN",
            q='author.uuid="x"',
            sort="-updated_on",
            page=2,
            pagelen=10,
        )

        fake_client.list_pull_requests.assert_called_once_with(
            workspace="ws",
            repository="repo",
            state="OPEN",
            q='author.uuid="x"',
            sort="-updated_on",
            page=2,
            pagelen=10,
        )


class TestListPullRequestsForCommitTool:
    def test_passes_args(self, fake_client):
        fake_client.list_pull_requests_for_commit.return_value = {}

        server.list_pull_requests_for_commit(
            workspace="ws", repository="repo", commit="abc", page=1, pagelen=5
        )

        fake_client.list_pull_requests_for_commit.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc", page=1, pagelen=5
        )


class TestListRepositoryPullRequestActivityTool:
    def test_passes_args(self, fake_client):
        fake_client.list_repository_pull_request_activity.return_value = {}

        server.list_repository_pull_request_activity(workspace="ws", repository="repo")

        fake_client.list_repository_pull_request_activity.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )


class TestGetPullRequestTool:
    def test_passes_args(self, fake_client):
        fake_client.get_pull_request.return_value = {"id": 1}

        result = server.get_pull_request(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.get_pull_request.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1
        )
        assert result == {"id": 1}


class TestUpdatePullRequestTool:
    def test_passes_all_args(self, fake_client):
        fake_client.update_pull_request.return_value = {}

        server.update_pull_request(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            title="t",
            description="d",
            destination_branch="develop",
            reviewers=["{u}"],
        )

        fake_client.update_pull_request.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            title="t",
            description="d",
            destination_branch="develop",
            reviewers=["{u}"],
        )

    def test_defaults(self, fake_client):
        fake_client.update_pull_request.return_value = {}

        server.update_pull_request(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.update_pull_request.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            title=None,
            description=None,
            destination_branch=None,
            reviewers=None,
        )


class TestListPullRequestActivityTool:
    def test_passes_args(self, fake_client):
        fake_client.list_pull_request_activity.return_value = {}

        server.list_pull_request_activity(
            workspace="ws", repository="repo", pull_request_id=1, page=2, pagelen=20
        )

        fake_client.list_pull_request_activity.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, page=2, pagelen=20
        )


class TestActionTools:
    @pytest.mark.parametrize(
        "tool_name",
        [
            "approve_pull_request",
            "unapprove_pull_request",
            "request_changes",
            "remove_request_changes",
            "decline_pull_request",
        ],
    )
    def test_action_tool_passes_args(self, fake_client, tool_name):
        getattr(fake_client, tool_name).return_value = {"ok": True}

        result = getattr(server, tool_name)(workspace="ws", repository="repo", pull_request_id=7)

        getattr(fake_client, tool_name).assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=7
        )
        assert result == {"ok": True}


class TestCommentTools:
    def test_list(self, fake_client):
        fake_client.list_pull_request_comments.return_value = {}

        server.list_pull_request_comments(
            workspace="ws", repository="repo", pull_request_id=1, q="x", sort="s"
        )

        fake_client.list_pull_request_comments.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            q="x",
            sort="s",
            page=None,
            pagelen=None,
        )

    def test_create(self, fake_client):
        fake_client.create_pull_request_comment.return_value = {}

        server.create_pull_request_comment(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            content="hello",
            parent_id=42,
            inline_path="src/a.py",
            inline_to=10,
            inline_from=5,
        )

        fake_client.create_pull_request_comment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            content="hello",
            parent_id=42,
            inline_path="src/a.py",
            inline_to=10,
            inline_from=5,
        )

    def test_get(self, fake_client):
        fake_client.get_pull_request_comment.return_value = {}

        server.get_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        fake_client.get_pull_request_comment.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

    def test_update(self, fake_client):
        fake_client.update_pull_request_comment.return_value = {}

        server.update_pull_request_comment(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            comment_id=7,
            content="edited",
        )

        fake_client.update_pull_request_comment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            comment_id=7,
            content="edited",
        )

    def test_delete(self, fake_client):
        fake_client.delete_pull_request_comment.return_value = {}

        server.delete_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        fake_client.delete_pull_request_comment.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

    def test_resolve(self, fake_client):
        fake_client.resolve_pull_request_comment.return_value = {}

        server.resolve_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        fake_client.resolve_pull_request_comment.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

    def test_reopen(self, fake_client):
        fake_client.reopen_pull_request_comment.return_value = {}

        server.reopen_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        fake_client.reopen_pull_request_comment.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )


class TestCommitsConflictsDiffStatTools:
    def test_commits(self, fake_client):
        fake_client.list_pull_request_commits.return_value = {}

        server.list_pull_request_commits(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.list_pull_request_commits.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, page=None, pagelen=None
        )

    def test_conflicts(self, fake_client):
        fake_client.list_pull_request_conflicts.return_value = {}

        server.list_pull_request_conflicts(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.list_pull_request_conflicts.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, page=None, pagelen=None
        )

    def test_diffstat(self, fake_client):
        fake_client.get_pull_request_diffstat.return_value = {}

        server.get_pull_request_diffstat(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.get_pull_request_diffstat.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, page=None, pagelen=None
        )


class TestDiffAndPatchTools:
    def test_diff(self, fake_client):
        fake_client.get_pull_request_diff.return_value = "diff text"

        result = server.get_pull_request_diff(workspace="ws", repository="repo", pull_request_id=1)

        assert result == "diff text"
        fake_client.get_pull_request_diff.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1
        )

    def test_patch(self, fake_client):
        fake_client.get_pull_request_patch.return_value = "patch text"

        result = server.get_pull_request_patch(workspace="ws", repository="repo", pull_request_id=1)

        assert result == "patch text"
        fake_client.get_pull_request_patch.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1
        )


class TestMergeTools:
    def test_merge_defaults(self, fake_client):
        fake_client.merge_pull_request.return_value = {}

        server.merge_pull_request(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.merge_pull_request.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            message=None,
            close_source_branch=None,
            merge_strategy=None,
            async_=None,
        )

    def test_merge_full(self, fake_client):
        fake_client.merge_pull_request.return_value = {}

        server.merge_pull_request(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            message="m",
            close_source_branch=True,
            merge_strategy="squash",
            async_=True,
        )

        fake_client.merge_pull_request.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            message="m",
            close_source_branch=True,
            merge_strategy="squash",
            async_=True,
        )

    def test_merge_task_status(self, fake_client):
        fake_client.get_merge_task_status.return_value = {}

        server.get_merge_task_status(
            workspace="ws", repository="repo", pull_request_id=1, task_id="t-1"
        )

        fake_client.get_merge_task_status.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, task_id="t-1"
        )


class TestStatusesTool:
    def test_list(self, fake_client):
        fake_client.list_pull_request_statuses.return_value = {}

        server.list_pull_request_statuses(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.list_pull_request_statuses.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )


class TestTaskTools:
    def test_list(self, fake_client):
        fake_client.list_pull_request_tasks.return_value = {}

        server.list_pull_request_tasks(workspace="ws", repository="repo", pull_request_id=1)

        fake_client.list_pull_request_tasks.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create(self, fake_client):
        fake_client.create_pull_request_task.return_value = {}

        server.create_pull_request_task(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            content="do it",
            comment_id=42,
            pending=True,
        )

        fake_client.create_pull_request_task.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            content="do it",
            comment_id=42,
            pending=True,
        )

    def test_get(self, fake_client):
        fake_client.get_pull_request_task.return_value = {}

        server.get_pull_request_task(
            workspace="ws", repository="repo", pull_request_id=1, task_id=5
        )

        fake_client.get_pull_request_task.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, task_id=5
        )

    def test_update(self, fake_client):
        fake_client.update_pull_request_task.return_value = {}

        server.update_pull_request_task(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            task_id=5,
            content="edited",
            state="RESOLVED",
        )

        fake_client.update_pull_request_task.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            task_id=5,
            content="edited",
            state="RESOLVED",
        )

    def test_delete(self, fake_client):
        fake_client.delete_pull_request_task.return_value = {}

        server.delete_pull_request_task(
            workspace="ws", repository="repo", pull_request_id=1, task_id=5
        )

        fake_client.delete_pull_request_task.assert_called_once_with(
            workspace="ws", repository="repo", pull_request_id=1, task_id=5
        )


class TestWorkspaceTools:
    def test_list_user_workspace_permissions(self, fake_client):
        fake_client.list_user_workspace_permissions.return_value = {}

        server.list_user_workspace_permissions(q="x", sort="s", page=1, pagelen=10)

        fake_client.list_user_workspace_permissions.assert_called_once_with(
            q="x", sort="s", page=1, pagelen=10
        )

    def test_list_user_workspaces(self, fake_client):
        fake_client.list_user_workspaces.return_value = {}

        server.list_user_workspaces(sort="slug", administrator=True)

        fake_client.list_user_workspaces.assert_called_once_with(
            sort="slug", administrator=True, page=None, pagelen=None
        )

    def test_get_user_workspace_permission(self, fake_client):
        fake_client.get_user_workspace_permission.return_value = {"permission": "owner"}

        server.get_user_workspace_permission(workspace="ws")

        fake_client.get_user_workspace_permission.assert_called_once_with(workspace="ws")

    def test_list_workspaces(self, fake_client):
        fake_client.list_workspaces.return_value = {}

        server.list_workspaces(role="owner")

        fake_client.list_workspaces.assert_called_once_with(
            role="owner", q=None, sort=None, page=None, pagelen=None
        )

    def test_get_workspace(self, fake_client):
        fake_client.get_workspace.return_value = {}

        server.get_workspace(workspace="ws")

        fake_client.get_workspace.assert_called_once_with(workspace="ws")

    def test_list_workspace_webhooks(self, fake_client):
        fake_client.list_workspace_webhooks.return_value = {}

        server.list_workspace_webhooks(workspace="ws")

        fake_client.list_workspace_webhooks.assert_called_once_with(
            workspace="ws", page=None, pagelen=None
        )

    def test_create_workspace_webhook(self, fake_client):
        fake_client.create_workspace_webhook.return_value = {}

        server.create_workspace_webhook(
            workspace="ws",
            url="https://example.com",
            events=["repo:push"],
            description="d",
            active=True,
            secret="s",
        )

        fake_client.create_workspace_webhook.assert_called_once_with(
            workspace="ws",
            url="https://example.com",
            events=["repo:push"],
            description="d",
            active=True,
            secret="s",
        )

    @pytest.mark.parametrize("tool_name", ["delete_workspace_webhook", "get_workspace_webhook"])
    def test_workspace_webhook_action(self, fake_client, tool_name):
        getattr(fake_client, tool_name).return_value = {}

        getattr(server, tool_name)(workspace="ws", uid="abc")

        getattr(fake_client, tool_name).assert_called_once_with(workspace="ws", uid="abc")

    def test_update_workspace_webhook(self, fake_client):
        fake_client.update_workspace_webhook.return_value = {}

        server.update_workspace_webhook(workspace="ws", uid="abc", url="https://new")

        fake_client.update_workspace_webhook.assert_called_once_with(
            workspace="ws",
            uid="abc",
            url="https://new",
            events=None,
            description=None,
            active=None,
            secret=None,
        )

    def test_list_workspace_members(self, fake_client):
        fake_client.list_workspace_members.return_value = {}

        server.list_workspace_members(workspace="ws", q="x")

        fake_client.list_workspace_members.assert_called_once_with(
            workspace="ws", q="x", page=None, pagelen=None
        )

    def test_get_workspace_member(self, fake_client):
        fake_client.get_workspace_member.return_value = {}

        server.get_workspace_member(workspace="ws", member="m")

        fake_client.get_workspace_member.assert_called_once_with(workspace="ws", member="m")

    def test_list_workspace_permissions(self, fake_client):
        fake_client.list_workspace_permissions.return_value = {}

        server.list_workspace_permissions(workspace="ws")

        fake_client.list_workspace_permissions.assert_called_once_with(
            workspace="ws", q=None, page=None, pagelen=None
        )

    def test_list_workspace_repository_permissions(self, fake_client):
        fake_client.list_workspace_repository_permissions.return_value = {}

        server.list_workspace_repository_permissions(workspace="ws")

        fake_client.list_workspace_repository_permissions.assert_called_once_with(
            workspace="ws", q=None, sort=None, page=None, pagelen=None
        )

    def test_list_workspace_repository_permissions_for_repo(self, fake_client):
        fake_client.list_workspace_repository_permissions_for_repo.return_value = {}

        server.list_workspace_repository_permissions_for_repo(workspace="ws", repository="repo")

        fake_client.list_workspace_repository_permissions_for_repo.assert_called_once_with(
            workspace="ws", repository="repo", q=None, sort=None, page=None, pagelen=None
        )

    def test_list_workspace_projects(self, fake_client):
        fake_client.list_workspace_projects.return_value = {}

        server.list_workspace_projects(workspace="ws")

        fake_client.list_workspace_projects.assert_called_once_with(
            workspace="ws", page=None, pagelen=None
        )

    def test_get_workspace_project(self, fake_client):
        fake_client.get_workspace_project.return_value = {}

        server.get_workspace_project(workspace="ws", project_key="MARS")

        fake_client.get_workspace_project.assert_called_once_with(
            workspace="ws", project_key="MARS"
        )

    def test_list_workspace_user_pull_requests(self, fake_client):
        fake_client.list_workspace_user_pull_requests.return_value = {}

        server.list_workspace_user_pull_requests(
            workspace="ws", selected_user="alice", state=["OPEN", "MERGED"]
        )

        fake_client.list_workspace_user_pull_requests.assert_called_once_with(
            workspace="ws",
            selected_user="alice",
            state=["OPEN", "MERGED"],
            page=None,
            pagelen=None,
        )

    def test_get_workspace_gpg_key(self, fake_client):
        fake_client.get_workspace_gpg_key.return_value = {}

        server.get_workspace_gpg_key(workspace="ws")

        fake_client.get_workspace_gpg_key.assert_called_once_with(workspace="ws")


class TestRepositoryTools:
    def test_list_public_repositories(self, fake_client):
        fake_client.list_public_repositories.return_value = {}

        server.list_public_repositories(role="owner")

        fake_client.list_public_repositories.assert_called_once_with(
            after=None, role="owner", q=None, sort=None, page=None, pagelen=None
        )

    def test_list_repositories(self, fake_client):
        fake_client.list_repositories.return_value = {}

        server.list_repositories(workspace="ws", role="member")

        fake_client.list_repositories.assert_called_once_with(
            workspace="ws", role="member", q=None, sort=None, page=None, pagelen=None
        )

    def test_get_repository(self, fake_client):
        fake_client.get_repository.return_value = {}

        server.get_repository(workspace="ws", repository="repo")

        fake_client.get_repository.assert_called_once_with(workspace="ws", repository="repo")

    def test_create_repository(self, fake_client):
        fake_client.create_repository.return_value = {}

        server.create_repository(
            workspace="ws",
            repository="repo",
            scm="git",
            name="My Repo",
            is_private=True,
            project_key="MARS",
            mainbranch_name="main",
        )

        fake_client.create_repository.assert_called_once_with(
            workspace="ws",
            repository="repo",
            scm="git",
            name="My Repo",
            description=None,
            is_private=True,
            fork_policy=None,
            language=None,
            has_issues=None,
            has_wiki=None,
            project_key="MARS",
            mainbranch_name="main",
        )

    def test_update_repository(self, fake_client):
        fake_client.update_repository.return_value = {}

        server.update_repository(workspace="ws", repository="repo", description="d")

        fake_client.update_repository.assert_called_once_with(
            workspace="ws",
            repository="repo",
            name=None,
            description="d",
            is_private=None,
            fork_policy=None,
            language=None,
            has_issues=None,
            has_wiki=None,
            project_key=None,
            mainbranch_name=None,
        )

    def test_delete_repository(self, fake_client):
        fake_client.delete_repository.return_value = {}

        server.delete_repository(workspace="ws", repository="repo", redirect_to="x")

        fake_client.delete_repository.assert_called_once_with(
            workspace="ws", repository="repo", redirect_to="x"
        )

    def test_list_file_history(self, fake_client):
        fake_client.list_file_history.return_value = {}

        server.list_file_history(
            workspace="ws",
            repository="repo",
            commit="abc",
            path="src/foo.py",
            renames="true",
        )

        fake_client.list_file_history.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            path="src/foo.py",
            renames="true",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_list_repository_forks(self, fake_client):
        fake_client.list_repository_forks.return_value = {}

        server.list_repository_forks(workspace="ws", repository="repo")

        fake_client.list_repository_forks.assert_called_once_with(
            workspace="ws",
            repository="repo",
            role=None,
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_fork_repository(self, fake_client):
        fake_client.fork_repository.return_value = {}

        server.fork_repository(
            workspace="ws",
            repository="repo",
            name="my-fork",
            destination_workspace="other",
        )

        fake_client.fork_repository.assert_called_once_with(
            workspace="ws",
            repository="repo",
            name="my-fork",
            destination_workspace="other",
            is_private=None,
            description=None,
            project_key=None,
            fork_policy=None,
            language=None,
        )

    def test_list_repository_webhooks(self, fake_client):
        fake_client.list_repository_webhooks.return_value = {}

        server.list_repository_webhooks(workspace="ws", repository="repo")

        fake_client.list_repository_webhooks.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_create_repository_webhook(self, fake_client):
        fake_client.create_repository_webhook.return_value = {}

        server.create_repository_webhook(
            workspace="ws",
            repository="repo",
            url="https://example.com",
            events=["repo:push"],
            secret="s",
        )

        fake_client.create_repository_webhook.assert_called_once_with(
            workspace="ws",
            repository="repo",
            url="https://example.com",
            events=["repo:push"],
            description=None,
            active=None,
            secret="s",
        )

    @pytest.mark.parametrize("tool_name", ["delete_repository_webhook", "get_repository_webhook"])
    def test_repository_webhook_action(self, fake_client, tool_name):
        getattr(fake_client, tool_name).return_value = {}

        getattr(server, tool_name)(workspace="ws", repository="repo", uid="abc")

        getattr(fake_client, tool_name).assert_called_once_with(
            workspace="ws", repository="repo", uid="abc"
        )

    def test_update_repository_webhook(self, fake_client):
        fake_client.update_repository_webhook.return_value = {}

        server.update_repository_webhook(workspace="ws", repository="repo", uid="abc", active=False)

        fake_client.update_repository_webhook.assert_called_once_with(
            workspace="ws",
            repository="repo",
            uid="abc",
            url=None,
            events=None,
            description=None,
            active=False,
            secret=None,
        )

    def test_get_repository_override_settings(self, fake_client):
        fake_client.get_repository_override_settings.return_value = {}

        server.get_repository_override_settings(workspace="ws", repository="repo")

        fake_client.get_repository_override_settings.assert_called_once_with(
            workspace="ws", repository="repo"
        )

    def test_set_repository_override_settings(self, fake_client):
        fake_client.set_repository_override_settings.return_value = {}

        server.set_repository_override_settings(
            workspace="ws", repository="repo", settings={"branching_model": False}
        )

        fake_client.set_repository_override_settings.assert_called_once_with(
            workspace="ws", repository="repo", settings={"branching_model": False}
        )

    def test_repository_group_permissions(self, fake_client):
        fake_client.list_repository_group_permissions.return_value = {}
        fake_client.get_repository_group_permission.return_value = {}
        fake_client.update_repository_group_permission.return_value = {}
        fake_client.delete_repository_group_permission.return_value = {}

        server.list_repository_group_permissions(workspace="ws", repository="repo")
        server.get_repository_group_permission(workspace="ws", repository="repo", group_slug="devs")
        server.update_repository_group_permission(
            workspace="ws", repository="repo", group_slug="devs", permission="write"
        )
        server.delete_repository_group_permission(
            workspace="ws", repository="repo", group_slug="devs"
        )

        fake_client.list_repository_group_permissions.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )
        fake_client.get_repository_group_permission.assert_called_once_with(
            workspace="ws", repository="repo", group_slug="devs"
        )
        fake_client.update_repository_group_permission.assert_called_once_with(
            workspace="ws", repository="repo", group_slug="devs", permission="write"
        )
        fake_client.delete_repository_group_permission.assert_called_once_with(
            workspace="ws", repository="repo", group_slug="devs"
        )

    def test_repository_user_permissions(self, fake_client):
        fake_client.list_repository_user_permissions.return_value = {}
        fake_client.get_repository_user_permission.return_value = {}
        fake_client.update_repository_user_permission.return_value = {}
        fake_client.delete_repository_user_permission.return_value = {}

        server.list_repository_user_permissions(workspace="ws", repository="repo")
        server.get_repository_user_permission(
            workspace="ws", repository="repo", selected_user_id="u"
        )
        server.update_repository_user_permission(
            workspace="ws", repository="repo", selected_user_id="u", permission="read"
        )
        server.delete_repository_user_permission(
            workspace="ws", repository="repo", selected_user_id="u"
        )

        fake_client.update_repository_user_permission.assert_called_once_with(
            workspace="ws", repository="repo", selected_user_id="u", permission="read"
        )

    def test_get_repository_root_src(self, fake_client):
        fake_client.get_repository_root_src.return_value = "content"

        result = server.get_repository_root_src(workspace="ws", repository="repo", format="meta")

        assert result == "content"
        fake_client.get_repository_root_src.assert_called_once_with(
            workspace="ws", repository="repo", format="meta"
        )

    def test_create_src_commit_encodes_text_to_bytes(self, fake_client):
        fake_client.create_src_commit.return_value = {}

        server.create_src_commit(
            workspace="ws",
            repository="repo",
            message="m",
            files_to_add={"src/foo.py": "print('hi')"},
            files_to_delete=["src/old.py"],
        )

        fake_client.create_src_commit.assert_called_once_with(
            workspace="ws",
            repository="repo",
            message="m",
            author=None,
            parents=None,
            branch=None,
            files_to_add={"src/foo.py": b"print('hi')"},
            files_to_delete=["src/old.py"],
        )

    def test_create_src_commit_no_files(self, fake_client):
        fake_client.create_src_commit.return_value = {}

        server.create_src_commit(workspace="ws", repository="repo", message="m")

        fake_client.create_src_commit.assert_called_once_with(
            workspace="ws",
            repository="repo",
            message="m",
            author=None,
            parents=None,
            branch=None,
            files_to_add=None,
            files_to_delete=None,
        )

    def test_get_repository_src(self, fake_client):
        fake_client.get_repository_src.return_value = "content"

        result = server.get_repository_src(
            workspace="ws", repository="repo", commit="HEAD", path="src/foo.py"
        )

        assert result == "content"
        fake_client.get_repository_src.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="HEAD",
            path="src/foo.py",
            format=None,
            q=None,
            sort=None,
            max_depth=None,
        )

    def test_list_repository_watchers(self, fake_client):
        fake_client.list_repository_watchers.return_value = {}

        server.list_repository_watchers(workspace="ws", repository="repo")

        fake_client.list_repository_watchers.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_list_user_repository_permissions(self, fake_client):
        fake_client.list_user_repository_permissions.return_value = {}

        server.list_user_repository_permissions()

        fake_client.list_user_repository_permissions.assert_called_once_with(
            q=None, sort=None, page=None, pagelen=None
        )

    def test_list_user_workspace_repository_permissions(self, fake_client):
        fake_client.list_user_workspace_repository_permissions.return_value = {}

        server.list_user_workspace_repository_permissions(workspace="ws")

        fake_client.list_user_workspace_repository_permissions.assert_called_once_with(
            workspace="ws", q=None, sort=None, page=None, pagelen=None
        )


class TestCommitTools:
    def test_get_commit(self, fake_client):
        fake_client.get_commit.return_value = {}

        server.get_commit(workspace="ws", repository="repo", commit="abc")

        fake_client.get_commit.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc"
        )

    @pytest.mark.parametrize("tool_name", ["approve_commit", "unapprove_commit"])
    def test_commit_approval(self, fake_client, tool_name):
        getattr(fake_client, tool_name).return_value = {}

        getattr(server, tool_name)(workspace="ws", repository="repo", commit="abc")

        getattr(fake_client, tool_name).assert_called_once_with(
            workspace="ws", repository="repo", commit="abc"
        )

    def test_list_commit_comments(self, fake_client):
        fake_client.list_commit_comments.return_value = {}

        server.list_commit_comments(workspace="ws", repository="repo", commit="abc")

        fake_client.list_commit_comments.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create_commit_comment(self, fake_client):
        fake_client.create_commit_comment.return_value = {}

        server.create_commit_comment(
            workspace="ws",
            repository="repo",
            commit="abc",
            content="hi",
            inline_path="src/a.py",
            inline_to=10,
        )

        fake_client.create_commit_comment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            content="hi",
            parent_id=None,
            inline_path="src/a.py",
            inline_to=10,
            inline_from=None,
        )

    def test_get_commit_comment(self, fake_client):
        fake_client.get_commit_comment.return_value = {}

        server.get_commit_comment(workspace="ws", repository="repo", commit="abc", comment_id=5)

        fake_client.get_commit_comment.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc", comment_id=5
        )

    def test_update_commit_comment(self, fake_client):
        fake_client.update_commit_comment.return_value = {}

        server.update_commit_comment(
            workspace="ws",
            repository="repo",
            commit="abc",
            comment_id=5,
            content="edited",
        )

        fake_client.update_commit_comment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            comment_id=5,
            content="edited",
        )

    def test_delete_commit_comment(self, fake_client):
        fake_client.delete_commit_comment.return_value = {}

        server.delete_commit_comment(workspace="ws", repository="repo", commit="abc", comment_id=5)

        fake_client.delete_commit_comment.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc", comment_id=5
        )

    def test_list_commit_reports(self, fake_client):
        fake_client.list_commit_reports.return_value = {}

        server.list_commit_reports(workspace="ws", repository="repo", commit="abc")

        fake_client.list_commit_reports.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc", page=None, pagelen=None
        )

    def test_get_commit_report(self, fake_client):
        fake_client.get_commit_report.return_value = {}

        server.get_commit_report(workspace="ws", repository="repo", commit="abc", report_id="r")

        fake_client.get_commit_report.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc", report_id="r"
        )

    def test_create_or_update_commit_report(self, fake_client):
        fake_client.create_or_update_commit_report.return_value = {}

        server.create_or_update_commit_report(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            title="t",
            report_type="COVERAGE",
            result="PASSED",
        )

        fake_client.create_or_update_commit_report.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            title="t",
            details=None,
            external_id=None,
            reporter=None,
            link=None,
            remote_link_enabled=None,
            logo_url=None,
            report_type="COVERAGE",
            result="PASSED",
            data=None,
        )

    def test_delete_commit_report(self, fake_client):
        fake_client.delete_commit_report.return_value = {}

        server.delete_commit_report(workspace="ws", repository="repo", commit="abc", report_id="r")

        fake_client.delete_commit_report.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc", report_id="r"
        )

    def test_list_commit_report_annotations(self, fake_client):
        fake_client.list_commit_report_annotations.return_value = {}

        server.list_commit_report_annotations(
            workspace="ws", repository="repo", commit="abc", report_id="r"
        )

        fake_client.list_commit_report_annotations.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            page=None,
            pagelen=None,
        )

    def test_bulk_create_or_update_annotations(self, fake_client):
        fake_client.bulk_create_or_update_annotations.return_value = []

        server.bulk_create_or_update_annotations(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotations=[{"external_id": "a-1"}],
        )

        fake_client.bulk_create_or_update_annotations.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotations=[{"external_id": "a-1"}],
        )

    def test_get_commit_report_annotation(self, fake_client):
        fake_client.get_commit_report_annotation.return_value = {}

        server.get_commit_report_annotation(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotation_id="a",
        )

        fake_client.get_commit_report_annotation.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotation_id="a",
        )

    def test_create_or_update_commit_report_annotation(self, fake_client):
        fake_client.create_or_update_commit_report_annotation.return_value = {}

        server.create_or_update_commit_report_annotation(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotation_id="a",
            annotation_type="BUG",
            path="src/a.py",
            line=10,
        )

        fake_client.create_or_update_commit_report_annotation.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotation_id="a",
            external_id=None,
            annotation_type="BUG",
            path="src/a.py",
            line=10,
            summary=None,
            details=None,
            result=None,
            severity=None,
            link=None,
        )

    def test_delete_commit_report_annotation(self, fake_client):
        fake_client.delete_commit_report_annotation.return_value = {}

        server.delete_commit_report_annotation(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotation_id="a",
        )

        fake_client.delete_commit_report_annotation.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r",
            annotation_id="a",
        )

    def test_list_commits(self, fake_client):
        fake_client.list_commits.return_value = {}

        server.list_commits(workspace="ws", repository="repo", include=["main"])

        fake_client.list_commits.assert_called_once_with(
            workspace="ws",
            repository="repo",
            include=["main"],
            exclude=None,
            page=None,
            pagelen=None,
        )

    def test_list_commits_with_filter(self, fake_client):
        fake_client.list_commits_with_filter.return_value = {}

        server.list_commits_with_filter(
            workspace="ws", repository="repo", include=["a"], exclude=["b"]
        )

        fake_client.list_commits_with_filter.assert_called_once_with(
            workspace="ws",
            repository="repo",
            include=["a"],
            exclude=["b"],
            page=None,
            pagelen=None,
        )

    def test_list_commits_for_revision(self, fake_client):
        fake_client.list_commits_for_revision.return_value = {}

        server.list_commits_for_revision(
            workspace="ws", repository="repo", revision="main", path="src/x.py"
        )

        fake_client.list_commits_for_revision.assert_called_once_with(
            workspace="ws",
            repository="repo",
            revision="main",
            include=None,
            exclude=None,
            path="src/x.py",
            page=None,
            pagelen=None,
        )

    def test_list_commits_for_revision_with_filter(self, fake_client):
        fake_client.list_commits_for_revision_with_filter.return_value = {}

        server.list_commits_for_revision_with_filter(
            workspace="ws", repository="repo", revision="main", include=["foo"]
        )

        fake_client.list_commits_for_revision_with_filter.assert_called_once_with(
            workspace="ws",
            repository="repo",
            revision="main",
            include=["foo"],
            exclude=None,
            page=None,
            pagelen=None,
        )

    def test_get_diff(self, fake_client):
        fake_client.get_diff.return_value = "diff text"

        result = server.get_diff(
            workspace="ws",
            repository="repo",
            spec="abc..def",
            context=5,
            path=["src/a.py"],
        )

        assert result == "diff text"
        fake_client.get_diff.assert_called_once_with(
            workspace="ws",
            repository="repo",
            spec="abc..def",
            context=5,
            path=["src/a.py"],
            ignore_whitespace=None,
            binary=None,
            renames=None,
            merge=None,
            topic=None,
        )

    def test_get_diffstat(self, fake_client):
        fake_client.get_diffstat.return_value = {}

        server.get_diffstat(workspace="ws", repository="repo", spec="abc..def")

        fake_client.get_diffstat.assert_called_once_with(
            workspace="ws",
            repository="repo",
            spec="abc..def",
            ignore_whitespace=None,
            merge=None,
            path=None,
            renames=None,
            topic=None,
            page=None,
            pagelen=None,
        )

    def test_list_file_conflicts(self, fake_client):
        fake_client.list_file_conflicts.return_value = {}

        server.list_file_conflicts(workspace="ws", repository="repo", spec="abc..def")

        fake_client.list_file_conflicts.assert_called_once_with(
            workspace="ws",
            repository="repo",
            spec="abc..def",
            page=None,
            pagelen=None,
        )

    def test_get_merge_base(self, fake_client):
        fake_client.get_merge_base.return_value = {}

        server.get_merge_base(workspace="ws", repository="repo", revspec="abc..def")

        fake_client.get_merge_base.assert_called_once_with(
            workspace="ws", repository="repo", revspec="abc..def"
        )

    def test_get_patch(self, fake_client):
        fake_client.get_patch.return_value = "patch text"

        result = server.get_patch(workspace="ws", repository="repo", spec="abc")

        assert result == "patch text"
        fake_client.get_patch.assert_called_once_with(workspace="ws", repository="repo", spec="abc")


class TestToolRegistration:
    def test_all_tools_are_registered(self):
        registered = {tool.name for tool in server.mcp._tool_manager.list_tools()}
        expected = {
            # Smoke test
            "current_user",
            # Pull requests
            "list_pull_requests_for_commit",
            "list_pull_requests",
            "create_pull_request",
            "list_repository_pull_request_activity",
            "get_pull_request",
            "update_pull_request",
            "list_pull_request_activity",
            "approve_pull_request",
            "unapprove_pull_request",
            "request_changes",
            "remove_request_changes",
            "list_pull_request_comments",
            "create_pull_request_comment",
            "get_pull_request_comment",
            "update_pull_request_comment",
            "delete_pull_request_comment",
            "resolve_pull_request_comment",
            "reopen_pull_request_comment",
            "list_pull_request_commits",
            "list_pull_request_conflicts",
            "decline_pull_request",
            "get_pull_request_diff",
            "get_pull_request_diffstat",
            "merge_pull_request",
            "get_merge_task_status",
            "get_pull_request_patch",
            "list_pull_request_statuses",
            "list_pull_request_tasks",
            "create_pull_request_task",
            "get_pull_request_task",
            "update_pull_request_task",
            "delete_pull_request_task",
            # Workspaces
            "list_user_workspace_permissions",
            "list_user_workspaces",
            "get_user_workspace_permission",
            "list_workspaces",
            "get_workspace",
            "list_workspace_webhooks",
            "create_workspace_webhook",
            "delete_workspace_webhook",
            "get_workspace_webhook",
            "update_workspace_webhook",
            "list_workspace_members",
            "get_workspace_member",
            "list_workspace_permissions",
            "list_workspace_repository_permissions",
            "list_workspace_repository_permissions_for_repo",
            "list_workspace_projects",
            "get_workspace_project",
            "list_workspace_user_pull_requests",
            "get_workspace_gpg_key",
            # Repositories
            "list_public_repositories",
            "list_repositories",
            "get_repository",
            "create_repository",
            "update_repository",
            "delete_repository",
            "list_file_history",
            "list_repository_forks",
            "fork_repository",
            "list_repository_webhooks",
            "create_repository_webhook",
            "delete_repository_webhook",
            "get_repository_webhook",
            "update_repository_webhook",
            "get_repository_override_settings",
            "set_repository_override_settings",
            "list_repository_group_permissions",
            "delete_repository_group_permission",
            "get_repository_group_permission",
            "update_repository_group_permission",
            "list_repository_user_permissions",
            "delete_repository_user_permission",
            "get_repository_user_permission",
            "update_repository_user_permission",
            "get_repository_root_src",
            "create_src_commit",
            "get_repository_src",
            "list_repository_watchers",
            "list_user_repository_permissions",
            "list_user_workspace_repository_permissions",
            # Commits
            "get_commit",
            "approve_commit",
            "unapprove_commit",
            "list_commit_comments",
            "create_commit_comment",
            "get_commit_comment",
            "update_commit_comment",
            "delete_commit_comment",
            "list_commit_reports",
            "get_commit_report",
            "create_or_update_commit_report",
            "delete_commit_report",
            "list_commit_report_annotations",
            "bulk_create_or_update_annotations",
            "get_commit_report_annotation",
            "create_or_update_commit_report_annotation",
            "delete_commit_report_annotation",
            "list_commits",
            "list_commits_with_filter",
            "list_commits_for_revision",
            "list_commits_for_revision_with_filter",
            "get_diff",
            "get_diffstat",
            "list_file_conflicts",
            "get_merge_base",
            "get_patch",
            # Default reviewers
            "list_default_reviewers",
            "list_effective_default_reviewers",
            "get_default_reviewer",
            "add_default_reviewer",
            "remove_default_reviewer",
            # Branch restrictions
            "list_branch_restrictions",
            "create_branch_restriction",
            "get_branch_restriction",
            "update_branch_restriction",
            "delete_branch_restriction",
            # Branching model
            "get_branching_model",
            "get_effective_branching_model",
            "get_branching_model_settings",
            "update_branching_model_settings",
            "get_project_branching_model",
            "get_project_branching_model_settings",
            "update_project_branching_model_settings",
            # Commit statuses
            "list_commit_statuses",
            "create_commit_build_status",
            "get_commit_build_status",
            "update_commit_build_status",
            # Deploy keys
            "list_deploy_keys",
            "create_deploy_key",
            "get_deploy_key",
            "update_deploy_key",
            "delete_deploy_key",
            "list_project_deploy_keys",
            "create_project_deploy_key",
            "get_project_deploy_key",
            "delete_project_deploy_key",
            # Deployments & environments
            "list_deployments",
            "get_deployment",
            "list_environments",
            "create_environment",
            "get_environment",
            "update_environment",
            "delete_environment",
            # Downloads
            "list_downloads",
            "upload_download",
            "get_download",
            "delete_download",
            # GPG keys
            "list_user_gpg_keys",
            "create_user_gpg_key",
            "get_user_gpg_key",
            "delete_user_gpg_key",
            # Issue tracker
            "list_components",
            "get_component",
            "list_milestones",
            "get_milestone",
            "list_versions",
            "get_version",
            "list_issues",
            "create_issue",
            "get_issue",
            "update_issue",
            "delete_issue",
            "export_issues",
            "get_issue_export",
            "get_issue_import_status",
            "import_issues",
            "list_issue_attachments",
            "upload_issue_attachment",
            "get_issue_attachment",
            "delete_issue_attachment",
            "list_issue_changes",
            "create_issue_change",
            "get_issue_change",
            "list_issue_comments",
            "create_issue_comment",
            "get_issue_comment",
            "update_issue_comment",
            "delete_issue_comment",
            "get_issue_vote",
            "vote_for_issue",
            "unvote_issue",
            "get_issue_watch",
            "watch_issue",
            "unwatch_issue",
            # Projects (workspace-level mutations + reviewers + permissions)
            "create_workspace_project",
            "update_workspace_project",
            "delete_workspace_project",
            "list_project_default_reviewers",
            "get_project_default_reviewer",
            "add_project_default_reviewer",
            "remove_project_default_reviewer",
            "list_project_group_permissions",
            "get_project_group_permission",
            "update_project_group_permission",
            "delete_project_group_permission",
            "list_project_user_permissions",
            "get_project_user_permission",
            "update_project_user_permission",
            "delete_project_user_permission",
            # Refs
            "list_refs",
            "list_branches",
            "create_branch",
            "get_branch",
            "delete_branch",
            "list_tags",
            "create_tag",
            "get_tag",
            "delete_tag",
            # Search
            "search_workspace_code",
            "search_user_code",
            # Snippets
            "list_snippets",
            "create_snippet",
            "list_workspace_snippets",
            "create_workspace_snippet",
            "get_snippet",
            "update_snippet",
            "delete_snippet",
            "list_snippet_comments",
            "create_snippet_comment",
            "get_snippet_comment",
            "update_snippet_comment",
            "delete_snippet_comment",
            "list_snippet_commits",
            "get_snippet_commit",
            "get_snippet_file",
            "get_snippet_watch",
            "watch_snippet",
            "unwatch_snippet",
            "list_snippet_watchers",
            "get_snippet_at_revision",
            "update_snippet_at_revision",
            "delete_snippet_at_revision",
            "get_snippet_file_at_revision",
            "get_snippet_diff",
            "get_snippet_patch",
            # SSH keys
            "list_user_ssh_keys",
            "create_user_ssh_key",
            "get_user_ssh_key",
            "update_user_ssh_key",
            "delete_user_ssh_key",
            # Users
            "get_user",
            "list_user_emails",
            "get_user_email",
            # Hook events
            "list_hook_event_subjects",
            "list_hook_events",
            # Pipelines
            "list_pipelines",
            "create_pipeline",
            "get_pipeline",
            "stop_pipeline",
            "list_pipeline_steps",
            "get_pipeline_step",
            "get_pipeline_step_log",
            "get_pipeline_step_container_log",
            "list_pipeline_step_test_reports",
            "list_pipeline_step_test_cases",
            "list_pipeline_step_test_case_reasons",
            "get_pipeline_config",
            "update_pipeline_config",
            "update_pipeline_build_number",
            "list_pipeline_schedules",
            "create_pipeline_schedule",
            "get_pipeline_schedule",
            "update_pipeline_schedule",
            "delete_pipeline_schedule",
            "list_pipeline_schedule_executions",
            "get_pipeline_ssh_key_pair",
            "update_pipeline_ssh_key_pair",
            "delete_pipeline_ssh_key_pair",
            "list_pipeline_known_hosts",
            "create_pipeline_known_host",
            "get_pipeline_known_host",
            "update_pipeline_known_host",
            "delete_pipeline_known_host",
            "list_pipeline_variables",
            "create_pipeline_variable",
            "get_pipeline_variable",
            "update_pipeline_variable",
            "delete_pipeline_variable",
            "list_pipeline_caches",
            "delete_pipeline_caches",
            "delete_pipeline_cache",
            "get_pipeline_cache_content_uri",
            "list_repository_pipeline_runners",
            "create_repository_pipeline_runner",
            "get_repository_pipeline_runner",
            "update_repository_pipeline_runner",
            "delete_repository_pipeline_runner",
            "list_workspace_pipeline_runners",
            "create_workspace_pipeline_runner",
            "get_workspace_pipeline_runner",
            "update_workspace_pipeline_runner",
            "delete_workspace_pipeline_runner",
            "list_workspace_pipeline_variables",
            "create_workspace_pipeline_variable",
            "get_workspace_pipeline_variable",
            "update_workspace_pipeline_variable",
            "delete_workspace_pipeline_variable",
            "list_user_pipeline_variables",
            "create_user_pipeline_variable",
            "get_user_pipeline_variable",
            "update_user_pipeline_variable",
            "delete_user_pipeline_variable",
            "list_deployment_variables",
            "create_deployment_variable",
            "update_deployment_variable",
            "delete_deployment_variable",
            "get_pipelines_oidc_configuration",
            "get_pipelines_oidc_keys",
        }
        assert expected <= registered


# ---------------------------------------------------------------------------
# Default reviewers
# ---------------------------------------------------------------------------


class TestDefaultReviewerTools:
    def test_list(self, fake_client):
        fake_client.list_default_reviewers.return_value = {"values": []}

        result = server.list_default_reviewers(workspace="ws", repository="repo")

        fake_client.list_default_reviewers.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )
        assert result == {"values": []}

    def test_list_effective(self, fake_client):
        fake_client.list_effective_default_reviewers.return_value = {"values": []}

        server.list_effective_default_reviewers(workspace="ws", repository="repo")

        fake_client.list_effective_default_reviewers.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_get(self, fake_client):
        fake_client.get_default_reviewer.return_value = {}

        server.get_default_reviewer(workspace="ws", repository="repo", target_username="bob")

        fake_client.get_default_reviewer.assert_called_once_with(
            workspace="ws", repository="repo", target_username="bob"
        )

    def test_add(self, fake_client):
        fake_client.add_default_reviewer.return_value = {}

        server.add_default_reviewer(workspace="ws", repository="repo", target_username="bob")

        fake_client.add_default_reviewer.assert_called_once_with(
            workspace="ws", repository="repo", target_username="bob"
        )

    def test_remove(self, fake_client):
        fake_client.remove_default_reviewer.return_value = {}

        server.remove_default_reviewer(workspace="ws", repository="repo", target_username="bob")

        fake_client.remove_default_reviewer.assert_called_once_with(
            workspace="ws", repository="repo", target_username="bob"
        )


# ---------------------------------------------------------------------------
# Branch restrictions
# ---------------------------------------------------------------------------


class TestBranchRestrictionTools:
    def test_list(self, fake_client):
        fake_client.list_branch_restrictions.return_value = {"values": []}

        server.list_branch_restrictions(workspace="ws", repository="repo")

        fake_client.list_branch_restrictions.assert_called_once_with(
            workspace="ws",
            repository="repo",
            kind=None,
            pattern=None,
            page=None,
            pagelen=None,
        )

    def test_create(self, fake_client):
        fake_client.create_branch_restriction.return_value = {"id": 1}

        server.create_branch_restriction(
            workspace="ws",
            repository="repo",
            kind="push",
            pattern="main",
            users=["{u}"],
            value=2,
        )

        fake_client.create_branch_restriction.assert_called_once_with(
            workspace="ws",
            repository="repo",
            kind="push",
            pattern="main",
            branch_match_kind=None,
            branch_type=None,
            users=["{u}"],
            groups=None,
            value=2,
        )

    def test_get(self, fake_client):
        fake_client.get_branch_restriction.return_value = {}

        server.get_branch_restriction(workspace="ws", repository="repo", id=42)

        fake_client.get_branch_restriction.assert_called_once_with(
            workspace="ws", repository="repo", id=42
        )

    def test_update(self, fake_client):
        fake_client.update_branch_restriction.return_value = {}

        server.update_branch_restriction(workspace="ws", repository="repo", id=42, kind="push")

        fake_client.update_branch_restriction.assert_called_once_with(
            workspace="ws",
            repository="repo",
            id=42,
            kind="push",
            pattern=None,
            branch_match_kind=None,
            branch_type=None,
            users=None,
            groups=None,
            value=None,
        )

    def test_delete(self, fake_client):
        fake_client.delete_branch_restriction.return_value = {}

        server.delete_branch_restriction(workspace="ws", repository="repo", id=42)

        fake_client.delete_branch_restriction.assert_called_once_with(
            workspace="ws", repository="repo", id=42
        )


# ---------------------------------------------------------------------------
# Branching model
# ---------------------------------------------------------------------------


class TestBranchingModelTools:
    def test_get(self, fake_client):
        fake_client.get_branching_model.return_value = {}

        server.get_branching_model(workspace="ws", repository="repo")

        fake_client.get_branching_model.assert_called_once_with(workspace="ws", repository="repo")

    def test_effective(self, fake_client):
        fake_client.get_effective_branching_model.return_value = {}

        server.get_effective_branching_model(workspace="ws", repository="repo")

        fake_client.get_effective_branching_model.assert_called_once_with(
            workspace="ws", repository="repo"
        )

    def test_get_settings(self, fake_client):
        fake_client.get_branching_model_settings.return_value = {}

        server.get_branching_model_settings(workspace="ws", repository="repo")

        fake_client.get_branching_model_settings.assert_called_once_with(
            workspace="ws", repository="repo"
        )

    def test_update_settings(self, fake_client):
        fake_client.update_branching_model_settings.return_value = {}

        server.update_branching_model_settings(
            workspace="ws",
            repository="repo",
            development={"use_mainbranch": True},
        )

        fake_client.update_branching_model_settings.assert_called_once_with(
            workspace="ws",
            repository="repo",
            development={"use_mainbranch": True},
            production=None,
            branch_types=None,
        )

    def test_project_get(self, fake_client):
        fake_client.get_project_branching_model.return_value = {}

        server.get_project_branching_model(workspace="ws", project_key="PROJ")

        fake_client.get_project_branching_model.assert_called_once_with(
            workspace="ws", project_key="PROJ"
        )

    def test_project_get_settings(self, fake_client):
        fake_client.get_project_branching_model_settings.return_value = {}

        server.get_project_branching_model_settings(workspace="ws", project_key="PROJ")

        fake_client.get_project_branching_model_settings.assert_called_once_with(
            workspace="ws", project_key="PROJ"
        )

    def test_project_update_settings(self, fake_client):
        fake_client.update_project_branching_model_settings.return_value = {}

        server.update_project_branching_model_settings(
            workspace="ws", project_key="PROJ", production={"enabled": False}
        )

        fake_client.update_project_branching_model_settings.assert_called_once_with(
            workspace="ws",
            project_key="PROJ",
            development=None,
            production={"enabled": False},
            branch_types=None,
        )


# ---------------------------------------------------------------------------
# Commit build statuses
# ---------------------------------------------------------------------------


class TestCommitBuildStatusTools:
    def test_list(self, fake_client):
        fake_client.list_commit_statuses.return_value = {"values": []}

        server.list_commit_statuses(workspace="ws", repository="repo", commit="abc")

        fake_client.list_commit_statuses.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create(self, fake_client):
        fake_client.create_commit_build_status.return_value = {}

        server.create_commit_build_status(
            workspace="ws",
            repository="repo",
            commit="abc",
            key="ci",
            state="SUCCESSFUL",
            url="https://example",
        )

        fake_client.create_commit_build_status.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            key="ci",
            state="SUCCESSFUL",
            url="https://example",
            name=None,
            description=None,
            refname=None,
        )

    def test_get(self, fake_client):
        fake_client.get_commit_build_status.return_value = {}

        server.get_commit_build_status(workspace="ws", repository="repo", commit="abc", key="ci")

        fake_client.get_commit_build_status.assert_called_once_with(
            workspace="ws", repository="repo", commit="abc", key="ci"
        )

    def test_update(self, fake_client):
        fake_client.update_commit_build_status.return_value = {}

        server.update_commit_build_status(
            workspace="ws",
            repository="repo",
            commit="abc",
            key="ci",
            state="FAILED",
        )

        fake_client.update_commit_build_status.assert_called_once_with(
            workspace="ws",
            repository="repo",
            commit="abc",
            key="ci",
            state="FAILED",
            url=None,
            name=None,
            description=None,
            refname=None,
        )


# ---------------------------------------------------------------------------
# Deploy keys
# ---------------------------------------------------------------------------


class TestDeployKeyTools:
    def test_list(self, fake_client):
        fake_client.list_deploy_keys.return_value = {"values": []}

        server.list_deploy_keys(workspace="ws", repository="repo")

        fake_client.list_deploy_keys.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_create(self, fake_client):
        fake_client.create_deploy_key.return_value = {}

        server.create_deploy_key(workspace="ws", repository="repo", key="ssh-rsa", label="prod")

        fake_client.create_deploy_key.assert_called_once_with(
            workspace="ws", repository="repo", key="ssh-rsa", label="prod"
        )

    def test_get(self, fake_client):
        fake_client.get_deploy_key.return_value = {}

        server.get_deploy_key(workspace="ws", repository="repo", key_id="42")

        fake_client.get_deploy_key.assert_called_once_with(
            workspace="ws", repository="repo", key_id="42"
        )

    def test_update(self, fake_client):
        fake_client.update_deploy_key.return_value = {}

        server.update_deploy_key(workspace="ws", repository="repo", key_id="42", label="new")

        fake_client.update_deploy_key.assert_called_once_with(
            workspace="ws", repository="repo", key_id="42", label="new", key=None
        )

    def test_delete(self, fake_client):
        fake_client.delete_deploy_key.return_value = {}

        server.delete_deploy_key(workspace="ws", repository="repo", key_id="42")

        fake_client.delete_deploy_key.assert_called_once_with(
            workspace="ws", repository="repo", key_id="42"
        )

    def test_project_list(self, fake_client):
        fake_client.list_project_deploy_keys.return_value = {"values": []}

        server.list_project_deploy_keys(workspace="ws", project_key="PROJ")

        fake_client.list_project_deploy_keys.assert_called_once_with(
            workspace="ws", project_key="PROJ", page=None, pagelen=None
        )

    def test_project_create(self, fake_client):
        fake_client.create_project_deploy_key.return_value = {}

        server.create_project_deploy_key(workspace="ws", project_key="PROJ", key="ssh-rsa")

        fake_client.create_project_deploy_key.assert_called_once_with(
            workspace="ws", project_key="PROJ", key="ssh-rsa", label=None
        )

    def test_project_get(self, fake_client):
        fake_client.get_project_deploy_key.return_value = {}

        server.get_project_deploy_key(workspace="ws", project_key="PROJ", key_id="42")

        fake_client.get_project_deploy_key.assert_called_once_with(
            workspace="ws", project_key="PROJ", key_id="42"
        )

    def test_project_delete(self, fake_client):
        fake_client.delete_project_deploy_key.return_value = {}

        server.delete_project_deploy_key(workspace="ws", project_key="PROJ", key_id="42")

        fake_client.delete_project_deploy_key.assert_called_once_with(
            workspace="ws", project_key="PROJ", key_id="42"
        )


# ---------------------------------------------------------------------------
# Deployments & environments
# ---------------------------------------------------------------------------


class TestDeploymentTools:
    def test_list_deployments(self, fake_client):
        fake_client.list_deployments.return_value = {"values": []}

        server.list_deployments(workspace="ws", repository="repo")

        fake_client.list_deployments.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_get_deployment(self, fake_client):
        fake_client.get_deployment.return_value = {}

        server.get_deployment(workspace="ws", repository="repo", deployment_uuid="d1")

        fake_client.get_deployment.assert_called_once_with(
            workspace="ws", repository="repo", deployment_uuid="d1"
        )

    def test_list_environments(self, fake_client):
        fake_client.list_environments.return_value = {"values": []}

        server.list_environments(workspace="ws", repository="repo")

        fake_client.list_environments.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_create_environment(self, fake_client):
        fake_client.create_environment.return_value = {}

        server.create_environment(workspace="ws", repository="repo", name="Prod", rank=1)

        fake_client.create_environment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            name="Prod",
            environment_type=None,
            rank=1,
        )

    def test_get_environment(self, fake_client):
        fake_client.get_environment.return_value = {}

        server.get_environment(workspace="ws", repository="repo", environment_uuid="e1")

        fake_client.get_environment.assert_called_once_with(
            workspace="ws", repository="repo", environment_uuid="e1"
        )

    def test_update_environment(self, fake_client):
        fake_client.update_environment.return_value = {}

        server.update_environment(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            body={"name": "Staging"},
        )

        fake_client.update_environment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            body={"name": "Staging"},
        )

    def test_delete_environment(self, fake_client):
        fake_client.delete_environment.return_value = {}

        server.delete_environment(workspace="ws", repository="repo", environment_uuid="e1")

        fake_client.delete_environment.assert_called_once_with(
            workspace="ws", repository="repo", environment_uuid="e1"
        )


# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------


class TestDownloadTools:
    def test_list(self, fake_client):
        fake_client.list_downloads.return_value = {"values": []}

        server.list_downloads(workspace="ws", repository="repo")

        fake_client.list_downloads.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_upload_encodes_text(self, fake_client):
        fake_client.upload_download.return_value = {}

        server.upload_download(workspace="ws", repository="repo", files={"x.txt": "hello"})

        fake_client.upload_download.assert_called_once_with(
            workspace="ws", repository="repo", files={"x.txt": b"hello"}
        )

    def test_get(self, fake_client):
        fake_client.get_download.return_value = "data"

        result = server.get_download(workspace="ws", repository="repo", filename="x.txt")

        assert result == "data"
        fake_client.get_download.assert_called_once_with(
            workspace="ws", repository="repo", filename="x.txt"
        )

    def test_delete(self, fake_client):
        fake_client.delete_download.return_value = {}

        server.delete_download(workspace="ws", repository="repo", filename="x.txt")

        fake_client.delete_download.assert_called_once_with(
            workspace="ws", repository="repo", filename="x.txt"
        )


# ---------------------------------------------------------------------------
# GPG keys
# ---------------------------------------------------------------------------


class TestUserGpgKeyTools:
    def test_list(self, fake_client):
        fake_client.list_user_gpg_keys.return_value = {"values": []}

        server.list_user_gpg_keys(selected_user="bob")

        fake_client.list_user_gpg_keys.assert_called_once_with(
            selected_user="bob", page=None, pagelen=None
        )

    def test_create(self, fake_client):
        fake_client.create_user_gpg_key.return_value = {}

        server.create_user_gpg_key(selected_user="bob", key="-----")

        fake_client.create_user_gpg_key.assert_called_once_with(
            selected_user="bob", key="-----", name=None
        )

    def test_get(self, fake_client):
        fake_client.get_user_gpg_key.return_value = {}

        server.get_user_gpg_key(selected_user="bob", fingerprint="ABCD")

        fake_client.get_user_gpg_key.assert_called_once_with(
            selected_user="bob", fingerprint="ABCD"
        )

    def test_delete(self, fake_client):
        fake_client.delete_user_gpg_key.return_value = {}

        server.delete_user_gpg_key(selected_user="bob", fingerprint="ABCD")

        fake_client.delete_user_gpg_key.assert_called_once_with(
            selected_user="bob", fingerprint="ABCD"
        )


# ---------------------------------------------------------------------------
# Issue tracker
# ---------------------------------------------------------------------------


class TestIssueTrackerTools:
    def test_list_components(self, fake_client):
        fake_client.list_components.return_value = {"values": []}

        server.list_components(workspace="ws", repository="repo")

        fake_client.list_components.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_get_component(self, fake_client):
        fake_client.get_component.return_value = {}

        server.get_component(workspace="ws", repository="repo", component_id=1)

        fake_client.get_component.assert_called_once_with(
            workspace="ws", repository="repo", component_id=1
        )

    def test_list_milestones(self, fake_client):
        fake_client.list_milestones.return_value = {"values": []}

        server.list_milestones(workspace="ws", repository="repo")

        fake_client.list_milestones.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_get_milestone(self, fake_client):
        fake_client.get_milestone.return_value = {}

        server.get_milestone(workspace="ws", repository="repo", milestone_id=2)

        fake_client.get_milestone.assert_called_once_with(
            workspace="ws", repository="repo", milestone_id=2
        )

    def test_list_versions(self, fake_client):
        fake_client.list_versions.return_value = {"values": []}

        server.list_versions(workspace="ws", repository="repo")

        fake_client.list_versions.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_get_version(self, fake_client):
        fake_client.get_version.return_value = {}

        server.get_version(workspace="ws", repository="repo", version_id=3)

        fake_client.get_version.assert_called_once_with(
            workspace="ws", repository="repo", version_id=3
        )

    def test_list_issues(self, fake_client):
        fake_client.list_issues.return_value = {"values": []}

        server.list_issues(workspace="ws", repository="repo")

        fake_client.list_issues.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create_issue(self, fake_client):
        fake_client.create_issue.return_value = {}

        server.create_issue(workspace="ws", repository="repo", title="bug")

        fake_client.create_issue.assert_called_once_with(
            workspace="ws",
            repository="repo",
            title="bug",
            content=None,
            kind=None,
            priority=None,
            state=None,
            component=None,
            milestone=None,
            version=None,
            assignee=None,
        )

    def test_get_issue(self, fake_client):
        fake_client.get_issue.return_value = {}

        server.get_issue(workspace="ws", repository="repo", issue_id=42)

        fake_client.get_issue.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=42
        )

    def test_update_issue(self, fake_client):
        fake_client.update_issue.return_value = {}

        server.update_issue(workspace="ws", repository="repo", issue_id=42, state="resolved")

        fake_client.update_issue.assert_called_once_with(
            workspace="ws",
            repository="repo",
            issue_id=42,
            title=None,
            content=None,
            kind=None,
            priority=None,
            state="resolved",
            component=None,
            milestone=None,
            version=None,
            assignee=None,
        )

    def test_delete_issue(self, fake_client):
        fake_client.delete_issue.return_value = {}

        server.delete_issue(workspace="ws", repository="repo", issue_id=42)

        fake_client.delete_issue.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=42
        )

    def test_export_issues(self, fake_client):
        fake_client.export_issues.return_value = {}

        server.export_issues(workspace="ws", repository="repo")

        fake_client.export_issues.assert_called_once_with(workspace="ws", repository="repo")

    def test_get_issue_export(self, fake_client):
        fake_client.get_issue_export.return_value = "data"

        result = server.get_issue_export(
            workspace="ws", repository="repo", repo_name="r", task_id="t1"
        )

        assert result == "data"
        fake_client.get_issue_export.assert_called_once_with(
            workspace="ws", repository="repo", repo_name="r", task_id="t1"
        )

    def test_get_issue_import_status(self, fake_client):
        fake_client.get_issue_import_status.return_value = {}

        server.get_issue_import_status(workspace="ws", repository="repo")

        fake_client.get_issue_import_status.assert_called_once_with(
            workspace="ws", repository="repo"
        )

    def test_import_issues(self, fake_client):
        fake_client.import_issues.return_value = {}

        server.import_issues(workspace="ws", repository="repo")

        fake_client.import_issues.assert_called_once_with(workspace="ws", repository="repo")

    def test_list_issue_attachments(self, fake_client):
        fake_client.list_issue_attachments.return_value = {"values": []}

        server.list_issue_attachments(workspace="ws", repository="repo", issue_id=1)

        fake_client.list_issue_attachments.assert_called_once_with(
            workspace="ws",
            repository="repo",
            issue_id=1,
            page=None,
            pagelen=None,
        )

    def test_upload_issue_attachment_encodes_text(self, fake_client):
        fake_client.upload_issue_attachment.return_value = {}

        server.upload_issue_attachment(
            workspace="ws",
            repository="repo",
            issue_id=1,
            files={"x.txt": "hi"},
        )

        fake_client.upload_issue_attachment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            issue_id=1,
            files={"x.txt": b"hi"},
        )

    def test_get_issue_attachment(self, fake_client):
        fake_client.get_issue_attachment.return_value = "data"

        result = server.get_issue_attachment(
            workspace="ws", repository="repo", issue_id=1, path="x.txt"
        )

        assert result == "data"

    def test_delete_issue_attachment(self, fake_client):
        fake_client.delete_issue_attachment.return_value = {}

        server.delete_issue_attachment(workspace="ws", repository="repo", issue_id=1, path="x.txt")

        fake_client.delete_issue_attachment.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1, path="x.txt"
        )

    def test_list_issue_changes(self, fake_client):
        fake_client.list_issue_changes.return_value = {"values": []}

        server.list_issue_changes(workspace="ws", repository="repo", issue_id=1)

        fake_client.list_issue_changes.assert_called_once_with(
            workspace="ws",
            repository="repo",
            issue_id=1,
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create_issue_change(self, fake_client):
        fake_client.create_issue_change.return_value = {}

        server.create_issue_change(
            workspace="ws",
            repository="repo",
            issue_id=1,
            changes={"state": {"new": "resolved"}},
        )

        fake_client.create_issue_change.assert_called_once_with(
            workspace="ws",
            repository="repo",
            issue_id=1,
            changes={"state": {"new": "resolved"}},
            message=None,
        )

    def test_get_issue_change(self, fake_client):
        fake_client.get_issue_change.return_value = {}

        server.get_issue_change(workspace="ws", repository="repo", issue_id=1, change_id=5)

        fake_client.get_issue_change.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1, change_id=5
        )

    def test_list_issue_comments(self, fake_client):
        fake_client.list_issue_comments.return_value = {"values": []}

        server.list_issue_comments(workspace="ws", repository="repo", issue_id=1)

        fake_client.list_issue_comments.assert_called_once_with(
            workspace="ws",
            repository="repo",
            issue_id=1,
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create_issue_comment(self, fake_client):
        fake_client.create_issue_comment.return_value = {}

        server.create_issue_comment(workspace="ws", repository="repo", issue_id=1, content="hi")

        fake_client.create_issue_comment.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1, content="hi"
        )

    def test_get_issue_comment(self, fake_client):
        fake_client.get_issue_comment.return_value = {}

        server.get_issue_comment(workspace="ws", repository="repo", issue_id=1, comment_id=5)

        fake_client.get_issue_comment.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1, comment_id=5
        )

    def test_update_issue_comment(self, fake_client):
        fake_client.update_issue_comment.return_value = {}

        server.update_issue_comment(
            workspace="ws",
            repository="repo",
            issue_id=1,
            comment_id=5,
            content="edit",
        )

        fake_client.update_issue_comment.assert_called_once_with(
            workspace="ws",
            repository="repo",
            issue_id=1,
            comment_id=5,
            content="edit",
        )

    def test_delete_issue_comment(self, fake_client):
        fake_client.delete_issue_comment.return_value = {}

        server.delete_issue_comment(workspace="ws", repository="repo", issue_id=1, comment_id=5)

        fake_client.delete_issue_comment.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1, comment_id=5
        )

    def test_get_vote(self, fake_client):
        fake_client.get_issue_vote.return_value = {}

        server.get_issue_vote(workspace="ws", repository="repo", issue_id=1)

        fake_client.get_issue_vote.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1
        )

    def test_vote(self, fake_client):
        fake_client.vote_for_issue.return_value = {}

        server.vote_for_issue(workspace="ws", repository="repo", issue_id=1)

        fake_client.vote_for_issue.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1
        )

    def test_unvote(self, fake_client):
        fake_client.unvote_issue.return_value = {}

        server.unvote_issue(workspace="ws", repository="repo", issue_id=1)

        fake_client.unvote_issue.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1
        )

    def test_get_watch(self, fake_client):
        fake_client.get_issue_watch.return_value = {}

        server.get_issue_watch(workspace="ws", repository="repo", issue_id=1)

        fake_client.get_issue_watch.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1
        )

    def test_watch(self, fake_client):
        fake_client.watch_issue.return_value = {}

        server.watch_issue(workspace="ws", repository="repo", issue_id=1)

        fake_client.watch_issue.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1
        )

    def test_unwatch(self, fake_client):
        fake_client.unwatch_issue.return_value = {}

        server.unwatch_issue(workspace="ws", repository="repo", issue_id=1)

        fake_client.unwatch_issue.assert_called_once_with(
            workspace="ws", repository="repo", issue_id=1
        )


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


class TestWorkspaceProjectTools:
    def test_create(self, fake_client):
        fake_client.create_workspace_project.return_value = {}

        server.create_workspace_project(workspace="ws", key="PROJ", name="My Project")

        fake_client.create_workspace_project.assert_called_once_with(
            workspace="ws",
            key="PROJ",
            name="My Project",
            description=None,
            is_private=None,
            avatar=None,
        )

    def test_update(self, fake_client):
        fake_client.update_workspace_project.return_value = {}

        server.update_workspace_project(workspace="ws", project_key="PROJ", name="new")

        fake_client.update_workspace_project.assert_called_once_with(
            workspace="ws",
            project_key="PROJ",
            key=None,
            name="new",
            description=None,
            is_private=None,
            avatar=None,
        )

    def test_delete(self, fake_client):
        fake_client.delete_workspace_project.return_value = {}

        server.delete_workspace_project(workspace="ws", project_key="PROJ")

        fake_client.delete_workspace_project.assert_called_once_with(
            workspace="ws", project_key="PROJ"
        )

    def test_list_default_reviewers(self, fake_client):
        fake_client.list_project_default_reviewers.return_value = {"values": []}

        server.list_project_default_reviewers(workspace="ws", project_key="PROJ")

        fake_client.list_project_default_reviewers.assert_called_once_with(
            workspace="ws", project_key="PROJ", page=None, pagelen=None
        )

    def test_get_default_reviewer(self, fake_client):
        fake_client.get_project_default_reviewer.return_value = {}

        server.get_project_default_reviewer(workspace="ws", project_key="PROJ", selected_user="bob")

        fake_client.get_project_default_reviewer.assert_called_once_with(
            workspace="ws", project_key="PROJ", selected_user="bob"
        )

    def test_add_default_reviewer(self, fake_client):
        fake_client.add_project_default_reviewer.return_value = {}

        server.add_project_default_reviewer(workspace="ws", project_key="PROJ", selected_user="bob")

        fake_client.add_project_default_reviewer.assert_called_once_with(
            workspace="ws", project_key="PROJ", selected_user="bob"
        )

    def test_remove_default_reviewer(self, fake_client):
        fake_client.remove_project_default_reviewer.return_value = {}

        server.remove_project_default_reviewer(
            workspace="ws", project_key="PROJ", selected_user="bob"
        )

        fake_client.remove_project_default_reviewer.assert_called_once_with(
            workspace="ws", project_key="PROJ", selected_user="bob"
        )

    def test_list_group_permissions(self, fake_client):
        fake_client.list_project_group_permissions.return_value = {"values": []}

        server.list_project_group_permissions(workspace="ws", project_key="PROJ")

        fake_client.list_project_group_permissions.assert_called_once_with(
            workspace="ws", project_key="PROJ", page=None, pagelen=None
        )

    def test_get_group_permission(self, fake_client):
        fake_client.get_project_group_permission.return_value = {}

        server.get_project_group_permission(workspace="ws", project_key="PROJ", group_slug="devs")

        fake_client.get_project_group_permission.assert_called_once_with(
            workspace="ws", project_key="PROJ", group_slug="devs"
        )

    def test_update_group_permission(self, fake_client):
        fake_client.update_project_group_permission.return_value = {}

        server.update_project_group_permission(
            workspace="ws",
            project_key="PROJ",
            group_slug="devs",
            permission="write",
        )

        fake_client.update_project_group_permission.assert_called_once_with(
            workspace="ws",
            project_key="PROJ",
            group_slug="devs",
            permission="write",
        )

    def test_delete_group_permission(self, fake_client):
        fake_client.delete_project_group_permission.return_value = {}

        server.delete_project_group_permission(
            workspace="ws", project_key="PROJ", group_slug="devs"
        )

        fake_client.delete_project_group_permission.assert_called_once_with(
            workspace="ws", project_key="PROJ", group_slug="devs"
        )

    def test_list_user_permissions(self, fake_client):
        fake_client.list_project_user_permissions.return_value = {"values": []}

        server.list_project_user_permissions(workspace="ws", project_key="PROJ")

        fake_client.list_project_user_permissions.assert_called_once_with(
            workspace="ws", project_key="PROJ", page=None, pagelen=None
        )

    def test_get_user_permission(self, fake_client):
        fake_client.get_project_user_permission.return_value = {}

        server.get_project_user_permission(
            workspace="ws", project_key="PROJ", selected_user_id="u1"
        )

        fake_client.get_project_user_permission.assert_called_once_with(
            workspace="ws", project_key="PROJ", selected_user_id="u1"
        )

    def test_update_user_permission(self, fake_client):
        fake_client.update_project_user_permission.return_value = {}

        server.update_project_user_permission(
            workspace="ws",
            project_key="PROJ",
            selected_user_id="u1",
            permission="admin",
        )

        fake_client.update_project_user_permission.assert_called_once_with(
            workspace="ws",
            project_key="PROJ",
            selected_user_id="u1",
            permission="admin",
        )

    def test_delete_user_permission(self, fake_client):
        fake_client.delete_project_user_permission.return_value = {}

        server.delete_project_user_permission(
            workspace="ws", project_key="PROJ", selected_user_id="u1"
        )

        fake_client.delete_project_user_permission.assert_called_once_with(
            workspace="ws", project_key="PROJ", selected_user_id="u1"
        )


# ---------------------------------------------------------------------------
# Refs
# ---------------------------------------------------------------------------


class TestRefTools:
    def test_list_refs(self, fake_client):
        fake_client.list_refs.return_value = {"values": []}

        server.list_refs(workspace="ws", repository="repo")

        fake_client.list_refs.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_list_branches(self, fake_client):
        fake_client.list_branches.return_value = {"values": []}

        server.list_branches(workspace="ws", repository="repo")

        fake_client.list_branches.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create_branch(self, fake_client):
        fake_client.create_branch.return_value = {}

        server.create_branch(
            workspace="ws",
            repository="repo",
            name="feature/x",
            target_hash="abc",
        )

        fake_client.create_branch.assert_called_once_with(
            workspace="ws",
            repository="repo",
            name="feature/x",
            target_hash="abc",
        )

    def test_get_branch(self, fake_client):
        fake_client.get_branch.return_value = {}

        server.get_branch(workspace="ws", repository="repo", name="main")

        fake_client.get_branch.assert_called_once_with(
            workspace="ws", repository="repo", name="main"
        )

    def test_delete_branch(self, fake_client):
        fake_client.delete_branch.return_value = {}

        server.delete_branch(workspace="ws", repository="repo", name="feature/x")

        fake_client.delete_branch.assert_called_once_with(
            workspace="ws", repository="repo", name="feature/x"
        )

    def test_list_tags(self, fake_client):
        fake_client.list_tags.return_value = {"values": []}

        server.list_tags(workspace="ws", repository="repo")

        fake_client.list_tags.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create_tag(self, fake_client):
        fake_client.create_tag.return_value = {}

        server.create_tag(
            workspace="ws",
            repository="repo",
            name="v1.0",
            target_hash="abc",
            message="release",
        )

        fake_client.create_tag.assert_called_once_with(
            workspace="ws",
            repository="repo",
            name="v1.0",
            target_hash="abc",
            message="release",
        )

    def test_get_tag(self, fake_client):
        fake_client.get_tag.return_value = {}

        server.get_tag(workspace="ws", repository="repo", name="v1.0")

        fake_client.get_tag.assert_called_once_with(workspace="ws", repository="repo", name="v1.0")

    def test_delete_tag(self, fake_client):
        fake_client.delete_tag.return_value = {}

        server.delete_tag(workspace="ws", repository="repo", name="v1.0")

        fake_client.delete_tag.assert_called_once_with(
            workspace="ws", repository="repo", name="v1.0"
        )


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class TestSearchTools:
    def test_workspace(self, fake_client):
        fake_client.search_workspace_code.return_value = {}

        server.search_workspace_code(workspace="ws", search_query="hello")

        fake_client.search_workspace_code.assert_called_once_with(
            workspace="ws", search_query="hello", page=None, pagelen=None
        )

    def test_user(self, fake_client):
        fake_client.search_user_code.return_value = {}

        server.search_user_code(selected_user="bob", search_query="hello")

        fake_client.search_user_code.assert_called_once_with(
            selected_user="bob", search_query="hello", page=None, pagelen=None
        )


# ---------------------------------------------------------------------------
# Snippets
# ---------------------------------------------------------------------------


class TestSnippetTools:
    def test_list(self, fake_client):
        fake_client.list_snippets.return_value = {"values": []}

        server.list_snippets()

        fake_client.list_snippets.assert_called_once_with(role=None, page=None, pagelen=None)

    def test_create(self, fake_client):
        fake_client.create_snippet.return_value = {}

        server.create_snippet(title="t", files={"x.txt": "hi"})

        fake_client.create_snippet.assert_called_once_with(
            title="t", is_private=None, scm=None, files={"x.txt": b"hi"}
        )

    def test_create_no_files(self, fake_client):
        fake_client.create_snippet.return_value = {}

        server.create_snippet(title="t")

        fake_client.create_snippet.assert_called_once_with(
            title="t", is_private=None, scm=None, files=None
        )

    def test_list_workspace(self, fake_client):
        fake_client.list_workspace_snippets.return_value = {"values": []}

        server.list_workspace_snippets(workspace="ws")

        fake_client.list_workspace_snippets.assert_called_once_with(
            workspace="ws", role=None, page=None, pagelen=None
        )

    def test_create_workspace(self, fake_client):
        fake_client.create_workspace_snippet.return_value = {}

        server.create_workspace_snippet(workspace="ws", title="t", files={"x.txt": "hi"})

        fake_client.create_workspace_snippet.assert_called_once_with(
            workspace="ws",
            title="t",
            is_private=None,
            scm=None,
            files={"x.txt": b"hi"},
        )

    def test_get(self, fake_client):
        fake_client.get_snippet.return_value = {}

        server.get_snippet(workspace="ws", encoded_id="abc")

        fake_client.get_snippet.assert_called_once_with(workspace="ws", encoded_id="abc")

    def test_update(self, fake_client):
        fake_client.update_snippet.return_value = {}

        server.update_snippet(workspace="ws", encoded_id="abc", title="new")

        fake_client.update_snippet.assert_called_once_with(
            workspace="ws",
            encoded_id="abc",
            title="new",
            is_private=None,
            files=None,
        )

    def test_delete(self, fake_client):
        fake_client.delete_snippet.return_value = {}

        server.delete_snippet(workspace="ws", encoded_id="abc")

        fake_client.delete_snippet.assert_called_once_with(workspace="ws", encoded_id="abc")

    def test_list_comments(self, fake_client):
        fake_client.list_snippet_comments.return_value = {"values": []}

        server.list_snippet_comments(workspace="ws", encoded_id="abc")

        fake_client.list_snippet_comments.assert_called_once_with(
            workspace="ws", encoded_id="abc", page=None, pagelen=None
        )

    def test_create_comment(self, fake_client):
        fake_client.create_snippet_comment.return_value = {}

        server.create_snippet_comment(workspace="ws", encoded_id="abc", content="hi")

        fake_client.create_snippet_comment.assert_called_once_with(
            workspace="ws", encoded_id="abc", content="hi"
        )

    def test_get_comment(self, fake_client):
        fake_client.get_snippet_comment.return_value = {}

        server.get_snippet_comment(workspace="ws", encoded_id="abc", comment_id=1)

        fake_client.get_snippet_comment.assert_called_once_with(
            workspace="ws", encoded_id="abc", comment_id=1
        )

    def test_update_comment(self, fake_client):
        fake_client.update_snippet_comment.return_value = {}

        server.update_snippet_comment(
            workspace="ws", encoded_id="abc", comment_id=1, content="edit"
        )

        fake_client.update_snippet_comment.assert_called_once_with(
            workspace="ws",
            encoded_id="abc",
            comment_id=1,
            content="edit",
        )

    def test_delete_comment(self, fake_client):
        fake_client.delete_snippet_comment.return_value = {}

        server.delete_snippet_comment(workspace="ws", encoded_id="abc", comment_id=1)

        fake_client.delete_snippet_comment.assert_called_once_with(
            workspace="ws", encoded_id="abc", comment_id=1
        )

    def test_list_commits(self, fake_client):
        fake_client.list_snippet_commits.return_value = {"values": []}

        server.list_snippet_commits(workspace="ws", encoded_id="abc")

        fake_client.list_snippet_commits.assert_called_once_with(
            workspace="ws", encoded_id="abc", page=None, pagelen=None
        )

    def test_get_commit(self, fake_client):
        fake_client.get_snippet_commit.return_value = {}

        server.get_snippet_commit(workspace="ws", encoded_id="abc", revision="r1")

        fake_client.get_snippet_commit.assert_called_once_with(
            workspace="ws", encoded_id="abc", revision="r1"
        )

    def test_get_file(self, fake_client):
        fake_client.get_snippet_file.return_value = "data"

        result = server.get_snippet_file(workspace="ws", encoded_id="abc", path="x.txt")

        assert result == "data"
        fake_client.get_snippet_file.assert_called_once_with(
            workspace="ws", encoded_id="abc", path="x.txt"
        )

    def test_get_watch(self, fake_client):
        fake_client.get_snippet_watch.return_value = {}

        server.get_snippet_watch(workspace="ws", encoded_id="abc")

        fake_client.get_snippet_watch.assert_called_once_with(workspace="ws", encoded_id="abc")

    def test_watch(self, fake_client):
        fake_client.watch_snippet.return_value = {}

        server.watch_snippet(workspace="ws", encoded_id="abc")

        fake_client.watch_snippet.assert_called_once_with(workspace="ws", encoded_id="abc")

    def test_unwatch(self, fake_client):
        fake_client.unwatch_snippet.return_value = {}

        server.unwatch_snippet(workspace="ws", encoded_id="abc")

        fake_client.unwatch_snippet.assert_called_once_with(workspace="ws", encoded_id="abc")

    def test_list_watchers(self, fake_client):
        fake_client.list_snippet_watchers.return_value = {"values": []}

        server.list_snippet_watchers(workspace="ws", encoded_id="abc")

        fake_client.list_snippet_watchers.assert_called_once_with(
            workspace="ws", encoded_id="abc", page=None, pagelen=None
        )

    def test_get_at_revision(self, fake_client):
        fake_client.get_snippet_at_revision.return_value = {}

        server.get_snippet_at_revision(workspace="ws", encoded_id="abc", node_id="n1")

        fake_client.get_snippet_at_revision.assert_called_once_with(
            workspace="ws", encoded_id="abc", node_id="n1"
        )

    def test_update_at_revision(self, fake_client):
        fake_client.update_snippet_at_revision.return_value = {}

        server.update_snippet_at_revision(
            workspace="ws", encoded_id="abc", node_id="n1", title="new"
        )

        fake_client.update_snippet_at_revision.assert_called_once_with(
            workspace="ws",
            encoded_id="abc",
            node_id="n1",
            title="new",
            is_private=None,
            files=None,
        )

    def test_delete_at_revision(self, fake_client):
        fake_client.delete_snippet_at_revision.return_value = {}

        server.delete_snippet_at_revision(workspace="ws", encoded_id="abc", node_id="n1")

        fake_client.delete_snippet_at_revision.assert_called_once_with(
            workspace="ws", encoded_id="abc", node_id="n1"
        )

    def test_get_file_at_revision(self, fake_client):
        fake_client.get_snippet_file_at_revision.return_value = "data"

        result = server.get_snippet_file_at_revision(
            workspace="ws", encoded_id="abc", node_id="n1", path="x.txt"
        )

        assert result == "data"

    def test_get_diff(self, fake_client):
        fake_client.get_snippet_diff.return_value = "diff"

        result = server.get_snippet_diff(workspace="ws", encoded_id="abc", revision="r1")

        assert result == "diff"

    def test_get_patch(self, fake_client):
        fake_client.get_snippet_patch.return_value = "patch"

        result = server.get_snippet_patch(workspace="ws", encoded_id="abc", revision="r1")

        assert result == "patch"


# ---------------------------------------------------------------------------
# SSH keys
# ---------------------------------------------------------------------------


class TestUserSshKeyTools:
    def test_list(self, fake_client):
        fake_client.list_user_ssh_keys.return_value = {"values": []}

        server.list_user_ssh_keys(selected_user="bob")

        fake_client.list_user_ssh_keys.assert_called_once_with(
            selected_user="bob", page=None, pagelen=None
        )

    def test_create(self, fake_client):
        fake_client.create_user_ssh_key.return_value = {}

        server.create_user_ssh_key(selected_user="bob", key="ssh-rsa")

        fake_client.create_user_ssh_key.assert_called_once_with(
            selected_user="bob", key="ssh-rsa", label=None
        )

    def test_get(self, fake_client):
        fake_client.get_user_ssh_key.return_value = {}

        server.get_user_ssh_key(selected_user="bob", key_id="42")

        fake_client.get_user_ssh_key.assert_called_once_with(selected_user="bob", key_id="42")

    def test_update(self, fake_client):
        fake_client.update_user_ssh_key.return_value = {}

        server.update_user_ssh_key(selected_user="bob", key_id="42", label="new")

        fake_client.update_user_ssh_key.assert_called_once_with(
            selected_user="bob", key_id="42", label="new", key=None
        )

    def test_delete(self, fake_client):
        fake_client.delete_user_ssh_key.return_value = {}

        server.delete_user_ssh_key(selected_user="bob", key_id="42")

        fake_client.delete_user_ssh_key.assert_called_once_with(selected_user="bob", key_id="42")


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


class TestUserTools:
    def test_get_user(self, fake_client):
        fake_client.get_user.return_value = {"username": "bob"}

        server.get_user(selected_user="bob")

        fake_client.get_user.assert_called_once_with(selected_user="bob")

    def test_list_user_emails(self, fake_client):
        fake_client.list_user_emails.return_value = {"values": []}

        server.list_user_emails()

        fake_client.list_user_emails.assert_called_once_with(page=None, pagelen=None)

    def test_get_user_email(self, fake_client):
        fake_client.get_user_email.return_value = {}

        server.get_user_email(email="bob@example.com")

        fake_client.get_user_email.assert_called_once_with(email="bob@example.com")


# ---------------------------------------------------------------------------
# Hook events
# ---------------------------------------------------------------------------


class TestHookEventTools:
    def test_subjects(self, fake_client):
        fake_client.list_hook_event_subjects.return_value = {"values": []}

        server.list_hook_event_subjects()

        fake_client.list_hook_event_subjects.assert_called_once_with()

    def test_events(self, fake_client):
        fake_client.list_hook_events.return_value = {"values": []}

        server.list_hook_events(subject_type="repository")

        fake_client.list_hook_events.assert_called_once_with(subject_type="repository")


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------


class TestPipelineCoreTools:
    def test_list(self, fake_client):
        fake_client.list_pipelines.return_value = {"values": []}

        server.list_pipelines(workspace="ws", repository="repo")

        fake_client.list_pipelines.assert_called_once_with(
            workspace="ws",
            repository="repo",
            q=None,
            sort=None,
            page=None,
            pagelen=None,
        )

    def test_create(self, fake_client):
        fake_client.create_pipeline.return_value = {}

        server.create_pipeline(workspace="ws", repository="repo", target={"ref_name": "main"})

        fake_client.create_pipeline.assert_called_once_with(
            workspace="ws",
            repository="repo",
            target={"ref_name": "main"},
            variables=None,
        )

    def test_get(self, fake_client):
        fake_client.get_pipeline.return_value = {}

        server.get_pipeline(workspace="ws", repository="repo", pipeline_uuid="p1")

        fake_client.get_pipeline.assert_called_once_with(
            workspace="ws", repository="repo", pipeline_uuid="p1"
        )

    def test_stop(self, fake_client):
        fake_client.stop_pipeline.return_value = {}

        server.stop_pipeline(workspace="ws", repository="repo", pipeline_uuid="p1")

        fake_client.stop_pipeline.assert_called_once_with(
            workspace="ws", repository="repo", pipeline_uuid="p1"
        )

    def test_list_steps(self, fake_client):
        fake_client.list_pipeline_steps.return_value = {"values": []}

        server.list_pipeline_steps(workspace="ws", repository="repo", pipeline_uuid="p1")

        fake_client.list_pipeline_steps.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            page=None,
            pagelen=None,
        )

    def test_get_step(self, fake_client):
        fake_client.get_pipeline_step.return_value = {}

        server.get_pipeline_step(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
        )

        fake_client.get_pipeline_step.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
        )

    def test_get_step_log(self, fake_client):
        fake_client.get_pipeline_step_log.return_value = "log"

        result = server.get_pipeline_step_log(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
        )

        assert result == "log"

    def test_get_step_container_log(self, fake_client):
        fake_client.get_pipeline_step_container_log.return_value = "log"

        result = server.get_pipeline_step_container_log(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
            log_uuid="l1",
        )

        assert result == "log"

    def test_test_reports(self, fake_client):
        fake_client.list_pipeline_step_test_reports.return_value = {}

        server.list_pipeline_step_test_reports(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
        )

        fake_client.list_pipeline_step_test_reports.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
        )

    def test_test_cases(self, fake_client):
        fake_client.list_pipeline_step_test_cases.return_value = {}

        server.list_pipeline_step_test_cases(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
        )

        fake_client.list_pipeline_step_test_cases.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
        )

    def test_test_case_reasons(self, fake_client):
        fake_client.list_pipeline_step_test_case_reasons.return_value = {}

        server.list_pipeline_step_test_case_reasons(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
            test_case_uuid="t1",
        )

        fake_client.list_pipeline_step_test_case_reasons.assert_called_once_with(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
            test_case_uuid="t1",
        )


class TestPipelineConfigTools:
    def test_get(self, fake_client):
        fake_client.get_pipeline_config.return_value = {}

        server.get_pipeline_config(workspace="ws", repository="repo")

        fake_client.get_pipeline_config.assert_called_once_with(workspace="ws", repository="repo")

    def test_update(self, fake_client):
        fake_client.update_pipeline_config.return_value = {}

        server.update_pipeline_config(workspace="ws", repository="repo", enabled=True)

        fake_client.update_pipeline_config.assert_called_once_with(
            workspace="ws",
            repository="repo",
            enabled=True,
            repository_pipeline=None,
        )

    def test_build_number(self, fake_client):
        fake_client.update_pipeline_build_number.return_value = {}

        server.update_pipeline_build_number(workspace="ws", repository="repo", next_build_number=42)

        fake_client.update_pipeline_build_number.assert_called_once_with(
            workspace="ws", repository="repo", next_build_number=42
        )


class TestPipelineScheduleTools:
    def test_list(self, fake_client):
        fake_client.list_pipeline_schedules.return_value = {"values": []}

        server.list_pipeline_schedules(workspace="ws", repository="repo")

        fake_client.list_pipeline_schedules.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_create(self, fake_client):
        fake_client.create_pipeline_schedule.return_value = {}

        server.create_pipeline_schedule(
            workspace="ws",
            repository="repo",
            target={"ref": "main"},
            cron_pattern="0 0 * * *",
        )

        fake_client.create_pipeline_schedule.assert_called_once_with(
            workspace="ws",
            repository="repo",
            target={"ref": "main"},
            cron_pattern="0 0 * * *",
            enabled=None,
        )

    def test_get(self, fake_client):
        fake_client.get_pipeline_schedule.return_value = {}

        server.get_pipeline_schedule(workspace="ws", repository="repo", schedule_uuid="s1")

        fake_client.get_pipeline_schedule.assert_called_once_with(
            workspace="ws", repository="repo", schedule_uuid="s1"
        )

    def test_update(self, fake_client):
        fake_client.update_pipeline_schedule.return_value = {}

        server.update_pipeline_schedule(
            workspace="ws",
            repository="repo",
            schedule_uuid="s1",
            enabled=False,
        )

        fake_client.update_pipeline_schedule.assert_called_once_with(
            workspace="ws",
            repository="repo",
            schedule_uuid="s1",
            enabled=False,
            cron_pattern=None,
            target=None,
        )

    def test_delete(self, fake_client):
        fake_client.delete_pipeline_schedule.return_value = {}

        server.delete_pipeline_schedule(workspace="ws", repository="repo", schedule_uuid="s1")

        fake_client.delete_pipeline_schedule.assert_called_once_with(
            workspace="ws", repository="repo", schedule_uuid="s1"
        )

    def test_list_executions(self, fake_client):
        fake_client.list_pipeline_schedule_executions.return_value = {"values": []}

        server.list_pipeline_schedule_executions(
            workspace="ws", repository="repo", schedule_uuid="s1"
        )

        fake_client.list_pipeline_schedule_executions.assert_called_once_with(
            workspace="ws",
            repository="repo",
            schedule_uuid="s1",
            page=None,
            pagelen=None,
        )


class TestPipelineSshKeyPairTools:
    def test_get(self, fake_client):
        fake_client.get_pipeline_ssh_key_pair.return_value = {}

        server.get_pipeline_ssh_key_pair(workspace="ws", repository="repo")

        fake_client.get_pipeline_ssh_key_pair.assert_called_once_with(
            workspace="ws", repository="repo"
        )

    def test_update(self, fake_client):
        fake_client.update_pipeline_ssh_key_pair.return_value = {}

        server.update_pipeline_ssh_key_pair(
            workspace="ws", repository="repo", public_key="pub", private_key="priv"
        )

        fake_client.update_pipeline_ssh_key_pair.assert_called_once_with(
            workspace="ws", repository="repo", public_key="pub", private_key="priv"
        )

    def test_delete(self, fake_client):
        fake_client.delete_pipeline_ssh_key_pair.return_value = {}

        server.delete_pipeline_ssh_key_pair(workspace="ws", repository="repo")

        fake_client.delete_pipeline_ssh_key_pair.assert_called_once_with(
            workspace="ws", repository="repo"
        )


class TestPipelineKnownHostTools:
    def test_list(self, fake_client):
        fake_client.list_pipeline_known_hosts.return_value = {"values": []}

        server.list_pipeline_known_hosts(workspace="ws", repository="repo")

        fake_client.list_pipeline_known_hosts.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_create(self, fake_client):
        fake_client.create_pipeline_known_host.return_value = {}

        server.create_pipeline_known_host(
            workspace="ws",
            repository="repo",
            hostname="github.com",
            public_key={"key": "AAA"},
        )

        fake_client.create_pipeline_known_host.assert_called_once_with(
            workspace="ws",
            repository="repo",
            hostname="github.com",
            public_key={"key": "AAA"},
        )

    def test_get(self, fake_client):
        fake_client.get_pipeline_known_host.return_value = {}

        server.get_pipeline_known_host(workspace="ws", repository="repo", known_host_uuid="h1")

        fake_client.get_pipeline_known_host.assert_called_once_with(
            workspace="ws", repository="repo", known_host_uuid="h1"
        )

    def test_update(self, fake_client):
        fake_client.update_pipeline_known_host.return_value = {}

        server.update_pipeline_known_host(
            workspace="ws",
            repository="repo",
            known_host_uuid="h1",
            hostname="gitlab.com",
        )

        fake_client.update_pipeline_known_host.assert_called_once_with(
            workspace="ws",
            repository="repo",
            known_host_uuid="h1",
            hostname="gitlab.com",
            public_key=None,
        )

    def test_delete(self, fake_client):
        fake_client.delete_pipeline_known_host.return_value = {}

        server.delete_pipeline_known_host(workspace="ws", repository="repo", known_host_uuid="h1")

        fake_client.delete_pipeline_known_host.assert_called_once_with(
            workspace="ws", repository="repo", known_host_uuid="h1"
        )


class TestPipelineVariableTools:
    def test_list(self, fake_client):
        fake_client.list_pipeline_variables.return_value = {"values": []}

        server.list_pipeline_variables(workspace="ws", repository="repo")

        fake_client.list_pipeline_variables.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_create(self, fake_client):
        fake_client.create_pipeline_variable.return_value = {}

        server.create_pipeline_variable(
            workspace="ws",
            repository="repo",
            key="K",
            value="V",
            secured=True,
        )

        fake_client.create_pipeline_variable.assert_called_once_with(
            workspace="ws",
            repository="repo",
            key="K",
            value="V",
            secured=True,
        )

    def test_get(self, fake_client):
        fake_client.get_pipeline_variable.return_value = {}

        server.get_pipeline_variable(workspace="ws", repository="repo", variable_uuid="v1")

        fake_client.get_pipeline_variable.assert_called_once_with(
            workspace="ws", repository="repo", variable_uuid="v1"
        )

    def test_update(self, fake_client):
        fake_client.update_pipeline_variable.return_value = {}

        server.update_pipeline_variable(
            workspace="ws", repository="repo", variable_uuid="v1", value="new"
        )

        fake_client.update_pipeline_variable.assert_called_once_with(
            workspace="ws",
            repository="repo",
            variable_uuid="v1",
            key=None,
            value="new",
            secured=None,
        )

    def test_delete(self, fake_client):
        fake_client.delete_pipeline_variable.return_value = {}

        server.delete_pipeline_variable(workspace="ws", repository="repo", variable_uuid="v1")

        fake_client.delete_pipeline_variable.assert_called_once_with(
            workspace="ws", repository="repo", variable_uuid="v1"
        )


class TestPipelineCacheTools:
    def test_list(self, fake_client):
        fake_client.list_pipeline_caches.return_value = {"values": []}

        server.list_pipeline_caches(workspace="ws", repository="repo")

        fake_client.list_pipeline_caches.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_delete_all(self, fake_client):
        fake_client.delete_pipeline_caches.return_value = {}

        server.delete_pipeline_caches(workspace="ws", repository="repo", name="npm")

        fake_client.delete_pipeline_caches.assert_called_once_with(
            workspace="ws", repository="repo", name="npm"
        )

    def test_delete_single(self, fake_client):
        fake_client.delete_pipeline_cache.return_value = {}

        server.delete_pipeline_cache(workspace="ws", repository="repo", cache_uuid="c1")

        fake_client.delete_pipeline_cache.assert_called_once_with(
            workspace="ws", repository="repo", cache_uuid="c1"
        )

    def test_content_uri(self, fake_client):
        fake_client.get_pipeline_cache_content_uri.return_value = {}

        server.get_pipeline_cache_content_uri(workspace="ws", repository="repo", cache_uuid="c1")

        fake_client.get_pipeline_cache_content_uri.assert_called_once_with(
            workspace="ws", repository="repo", cache_uuid="c1"
        )


class TestPipelineRunnerTools:
    def test_list_repo(self, fake_client):
        fake_client.list_repository_pipeline_runners.return_value = {"values": []}

        server.list_repository_pipeline_runners(workspace="ws", repository="repo")

        fake_client.list_repository_pipeline_runners.assert_called_once_with(
            workspace="ws", repository="repo", page=None, pagelen=None
        )

    def test_create_repo(self, fake_client):
        fake_client.create_repository_pipeline_runner.return_value = {}

        server.create_repository_pipeline_runner(
            workspace="ws", repository="repo", name="r1", labels=["linux"]
        )

        fake_client.create_repository_pipeline_runner.assert_called_once_with(
            workspace="ws", repository="repo", name="r1", labels=["linux"]
        )

    def test_get_repo(self, fake_client):
        fake_client.get_repository_pipeline_runner.return_value = {}

        server.get_repository_pipeline_runner(workspace="ws", repository="repo", runner_uuid="r1")

        fake_client.get_repository_pipeline_runner.assert_called_once_with(
            workspace="ws", repository="repo", runner_uuid="r1"
        )

    def test_update_repo(self, fake_client):
        fake_client.update_repository_pipeline_runner.return_value = {}

        server.update_repository_pipeline_runner(
            workspace="ws",
            repository="repo",
            runner_uuid="r1",
            name="new",
        )

        fake_client.update_repository_pipeline_runner.assert_called_once_with(
            workspace="ws",
            repository="repo",
            runner_uuid="r1",
            name="new",
            labels=None,
        )

    def test_delete_repo(self, fake_client):
        fake_client.delete_repository_pipeline_runner.return_value = {}

        server.delete_repository_pipeline_runner(
            workspace="ws", repository="repo", runner_uuid="r1"
        )

        fake_client.delete_repository_pipeline_runner.assert_called_once_with(
            workspace="ws", repository="repo", runner_uuid="r1"
        )

    def test_list_workspace(self, fake_client):
        fake_client.list_workspace_pipeline_runners.return_value = {"values": []}

        server.list_workspace_pipeline_runners(workspace="ws")

        fake_client.list_workspace_pipeline_runners.assert_called_once_with(
            workspace="ws", page=None, pagelen=None
        )

    def test_create_workspace(self, fake_client):
        fake_client.create_workspace_pipeline_runner.return_value = {}

        server.create_workspace_pipeline_runner(workspace="ws", name="r1")

        fake_client.create_workspace_pipeline_runner.assert_called_once_with(
            workspace="ws", name="r1", labels=None
        )

    def test_get_workspace(self, fake_client):
        fake_client.get_workspace_pipeline_runner.return_value = {}

        server.get_workspace_pipeline_runner(workspace="ws", runner_uuid="r1")

        fake_client.get_workspace_pipeline_runner.assert_called_once_with(
            workspace="ws", runner_uuid="r1"
        )

    def test_update_workspace(self, fake_client):
        fake_client.update_workspace_pipeline_runner.return_value = {}

        server.update_workspace_pipeline_runner(workspace="ws", runner_uuid="r1", labels=["x"])

        fake_client.update_workspace_pipeline_runner.assert_called_once_with(
            workspace="ws", runner_uuid="r1", name=None, labels=["x"]
        )

    def test_delete_workspace(self, fake_client):
        fake_client.delete_workspace_pipeline_runner.return_value = {}

        server.delete_workspace_pipeline_runner(workspace="ws", runner_uuid="r1")

        fake_client.delete_workspace_pipeline_runner.assert_called_once_with(
            workspace="ws", runner_uuid="r1"
        )


class TestWorkspaceAndUserPipelineVariableTools:
    def test_list_workspace(self, fake_client):
        fake_client.list_workspace_pipeline_variables.return_value = {"values": []}

        server.list_workspace_pipeline_variables(workspace="ws")

        fake_client.list_workspace_pipeline_variables.assert_called_once_with(
            workspace="ws", page=None, pagelen=None
        )

    def test_create_workspace(self, fake_client):
        fake_client.create_workspace_pipeline_variable.return_value = {}

        server.create_workspace_pipeline_variable(workspace="ws", key="K", value="V")

        fake_client.create_workspace_pipeline_variable.assert_called_once_with(
            workspace="ws", key="K", value="V", secured=None
        )

    def test_get_workspace(self, fake_client):
        fake_client.get_workspace_pipeline_variable.return_value = {}

        server.get_workspace_pipeline_variable(workspace="ws", variable_uuid="v1")

        fake_client.get_workspace_pipeline_variable.assert_called_once_with(
            workspace="ws", variable_uuid="v1"
        )

    def test_update_workspace(self, fake_client):
        fake_client.update_workspace_pipeline_variable.return_value = {}

        server.update_workspace_pipeline_variable(workspace="ws", variable_uuid="v1", value="new")

        fake_client.update_workspace_pipeline_variable.assert_called_once_with(
            workspace="ws",
            variable_uuid="v1",
            key=None,
            value="new",
            secured=None,
        )

    def test_delete_workspace(self, fake_client):
        fake_client.delete_workspace_pipeline_variable.return_value = {}

        server.delete_workspace_pipeline_variable(workspace="ws", variable_uuid="v1")

        fake_client.delete_workspace_pipeline_variable.assert_called_once_with(
            workspace="ws", variable_uuid="v1"
        )

    def test_list_user(self, fake_client):
        fake_client.list_user_pipeline_variables.return_value = {"values": []}

        server.list_user_pipeline_variables(selected_user="bob")

        fake_client.list_user_pipeline_variables.assert_called_once_with(
            selected_user="bob", page=None, pagelen=None
        )

    def test_create_user(self, fake_client):
        fake_client.create_user_pipeline_variable.return_value = {}

        server.create_user_pipeline_variable(selected_user="bob", key="K", value="V")

        fake_client.create_user_pipeline_variable.assert_called_once_with(
            selected_user="bob", key="K", value="V", secured=None
        )

    def test_get_user(self, fake_client):
        fake_client.get_user_pipeline_variable.return_value = {}

        server.get_user_pipeline_variable(selected_user="bob", variable_uuid="v1")

        fake_client.get_user_pipeline_variable.assert_called_once_with(
            selected_user="bob", variable_uuid="v1"
        )

    def test_update_user(self, fake_client):
        fake_client.update_user_pipeline_variable.return_value = {}

        server.update_user_pipeline_variable(selected_user="bob", variable_uuid="v1", value="new")

        fake_client.update_user_pipeline_variable.assert_called_once_with(
            selected_user="bob",
            variable_uuid="v1",
            key=None,
            value="new",
            secured=None,
        )

    def test_delete_user(self, fake_client):
        fake_client.delete_user_pipeline_variable.return_value = {}

        server.delete_user_pipeline_variable(selected_user="bob", variable_uuid="v1")

        fake_client.delete_user_pipeline_variable.assert_called_once_with(
            selected_user="bob", variable_uuid="v1"
        )


class TestDeploymentVariableTools:
    def test_list(self, fake_client):
        fake_client.list_deployment_variables.return_value = {"values": []}

        server.list_deployment_variables(workspace="ws", repository="repo", environment_uuid="e1")

        fake_client.list_deployment_variables.assert_called_once_with(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            page=None,
            pagelen=None,
        )

    def test_create(self, fake_client):
        fake_client.create_deployment_variable.return_value = {}

        server.create_deployment_variable(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            key="K",
            value="V",
        )

        fake_client.create_deployment_variable.assert_called_once_with(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            key="K",
            value="V",
            secured=None,
        )

    def test_update(self, fake_client):
        fake_client.update_deployment_variable.return_value = {}

        server.update_deployment_variable(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            variable_uuid="v1",
            value="new",
        )

        fake_client.update_deployment_variable.assert_called_once_with(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            variable_uuid="v1",
            key=None,
            value="new",
            secured=None,
        )

    def test_delete(self, fake_client):
        fake_client.delete_deployment_variable.return_value = {}

        server.delete_deployment_variable(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            variable_uuid="v1",
        )

        fake_client.delete_deployment_variable.assert_called_once_with(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            variable_uuid="v1",
        )


class TestPipelinesOidcTools:
    def test_get_configuration(self, fake_client):
        fake_client.get_pipelines_oidc_configuration.return_value = {}

        server.get_pipelines_oidc_configuration(workspace="ws")

        fake_client.get_pipelines_oidc_configuration.assert_called_once_with(workspace="ws")

    def test_get_keys(self, fake_client):
        fake_client.get_pipelines_oidc_keys.return_value = {}

        server.get_pipelines_oidc_keys(workspace="ws")

        fake_client.get_pipelines_oidc_keys.assert_called_once_with(workspace="ws")
