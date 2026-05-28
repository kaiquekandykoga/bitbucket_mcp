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
        }
        assert expected <= registered
