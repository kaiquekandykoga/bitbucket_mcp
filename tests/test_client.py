from __future__ import annotations

import base64
import json
import urllib.error
import urllib.parse
from email.message import Message
from unittest.mock import MagicMock, patch

import pytest

from bitbucket_mcp.bitbucket.client import (
    BASE_URL,
    AuthenticationError,
    Client,
    ConfigurationError,
    ResponseError,
)


@pytest.fixture
def env_credentials(monkeypatch):
    monkeypatch.setenv("BITBUCKET_EMAIL", "user@example.com")
    monkeypatch.setenv("BITBUCKET_API_TOKEN", "secret-token")


@pytest.fixture
def client():
    return Client(email="a@b.com", api_token="tok")


@pytest.fixture
def mock_urlopen():
    with patch("bitbucket_mcp.bitbucket.client.urllib.request.urlopen") as mock:
        yield mock


def make_response(body: dict | bytes) -> MagicMock:
    response = MagicMock()
    if isinstance(body, bytes):
        response.read.return_value = body
    else:
        response.read.return_value = json.dumps(body).encode()
    response.__enter__.return_value = response
    response.__exit__.return_value = None
    return response


def make_http_error(code: int, body: bytes = b"") -> urllib.error.HTTPError:
    error = urllib.error.HTTPError(
        url="http://example.com",
        code=code,
        msg="error",
        hdrs=Message(),
        fp=None,
    )
    error.read = lambda: body
    return error


def sent_request(mock_urlopen):
    return mock_urlopen.call_args.args[0]


def sent_body(mock_urlopen):
    return json.loads(mock_urlopen.call_args.args[0].data)


def url_path_and_query(url: str) -> tuple[str, dict[str, list[str]]]:
    parsed = urllib.parse.urlparse(url)
    return parsed.path, urllib.parse.parse_qs(parsed.query)


class TestInit:
    def test_uses_explicit_args(self):
        client = Client(email="a@b.com", api_token="tok")
        assert client._email == "a@b.com"
        assert client._api_token == "tok"

    def test_falls_back_to_env(self, env_credentials):
        client = Client()
        assert client._email == "user@example.com"
        assert client._api_token == "secret-token"

    def test_explicit_args_override_env(self, env_credentials):
        client = Client(email="other@b.com", api_token="other-tok")
        assert client._email == "other@b.com"
        assert client._api_token == "other-tok"

    def test_missing_email_raises(self, monkeypatch):
        monkeypatch.delenv("BITBUCKET_EMAIL", raising=False)
        monkeypatch.setenv("BITBUCKET_API_TOKEN", "tok")
        with pytest.raises(ConfigurationError, match="BITBUCKET_EMAIL"):
            Client()

    def test_missing_api_token_raises(self, monkeypatch):
        monkeypatch.setenv("BITBUCKET_EMAIL", "a@b.com")
        monkeypatch.delenv("BITBUCKET_API_TOKEN", raising=False)
        with pytest.raises(ConfigurationError, match="BITBUCKET_API_TOKEN"):
            Client()


class TestCurrentUser:
    def test_returns_parsed_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"display_name": "Kaique", "uuid": "{abc}"})

        result = client.current_user()

        assert result == {"display_name": "Kaique", "uuid": "{abc}"}

    def test_calls_user_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.current_user()

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/user"
        assert request.method == "GET"

    def test_sends_basic_auth_header(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.current_user()

        request = sent_request(mock_urlopen)
        expected = "Basic " + base64.b64encode(b"a@b.com:tok").decode()
        assert request.get_header("Authorization") == expected

    def test_sends_accept_json_header(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.current_user()

        request = sent_request(mock_urlopen)
        assert request.get_header("Accept") == "application/json"

    def test_401_raises_authentication_error(self, client, mock_urlopen):
        mock_urlopen.side_effect = make_http_error(401)

        with pytest.raises(AuthenticationError, match="HTTP 401"):
            client.current_user()

    def test_500_raises_response_error(self, client, mock_urlopen):
        mock_urlopen.side_effect = make_http_error(500, b"server boom")

        with pytest.raises(ResponseError, match="HTTP 500"):
            client.current_user()


class TestRequestEmptyResponseHandling:
    def test_empty_body_returns_empty_dict(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        result = client.approve_pull_request(workspace="ws", repository="r", pull_request_id=1)

        assert result == {}


class TestListPullRequestsForCommit:
    def test_calls_correct_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        result = client.list_pull_requests_for_commit(
            workspace="ws", repository="repo", commit="abc123"
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/commit/abc123/pullrequests"
        assert request.method == "GET"
        assert result == {"values": []}

    def test_query_params(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_pull_requests_for_commit(
            workspace="ws", repository="repo", commit="abc", page=2, pagelen=50
        )

        _, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert query == {"page": ["2"], "pagelen": ["50"]}


class TestListPullRequests:
    def test_calls_correct_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pull_requests(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests"
        assert request.method == "GET"
        assert query == {}

    def test_state_filter(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_pull_requests(workspace="ws", repository="repo", state="OPEN")

        _, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert query == {"state": ["OPEN"]}

    def test_all_query_params(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_pull_requests(
            workspace="ws",
            repository="repo",
            state="MERGED",
            q='author.uuid="x"',
            sort="-updated_on",
            page=3,
            pagelen=25,
        )

        _, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert query == {
            "state": ["MERGED"],
            "q": ['author.uuid="x"'],
            "sort": ["-updated_on"],
            "page": ["3"],
            "pagelen": ["25"],
        }


class TestCreatePullRequest:
    def _call(self, client, **overrides):
        kwargs = {
            "workspace": "ws",
            "repository": "repo",
            "title": "My PR",
            "source_branch": "feature/x",
            "destination_branch": "main",
        }
        kwargs.update(overrides)
        return client.create_pull_request(**kwargs)

    def test_returns_parsed_response(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 42, "title": "My PR", "state": "OPEN"})

        result = self._call(client)

        assert result == {"id": 42, "title": "My PR", "state": "OPEN"}

    def test_posts_to_pullrequests_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        self._call(client)

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests"
        assert request.method == "POST"

    def test_sends_request_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        self._call(client, description="Fixes #123")

        assert sent_body(mock_urlopen) == {
            "title": "My PR",
            "source": {"branch": {"name": "feature/x"}},
            "destination": {"branch": {"name": "main"}},
            "description": "Fixes #123",
        }

    def test_omits_optional_fields(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        self._call(client)

        sent = sent_body(mock_urlopen)
        assert "description" not in sent
        assert "close_source_branch" not in sent
        assert "reviewers" not in sent

    def test_close_source_branch_and_reviewers(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        self._call(
            client,
            close_source_branch=True,
            reviewers=["{uuid-1}", "{uuid-2}"],
        )

        sent = sent_body(mock_urlopen)
        assert sent["close_source_branch"] is True
        assert sent["reviewers"] == [{"uuid": "{uuid-1}"}, {"uuid": "{uuid-2}"}]

    def test_sends_content_type_json(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        self._call(client)

        request = sent_request(mock_urlopen)
        assert request.get_header("Content-type") == "application/json"

    def test_sends_basic_auth_header(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        self._call(client)

        request = sent_request(mock_urlopen)
        expected = "Basic " + base64.b64encode(b"a@b.com:tok").decode()
        assert request.get_header("Authorization") == expected

    def test_401_raises_authentication_error(self, client, mock_urlopen):
        mock_urlopen.side_effect = make_http_error(401)

        with pytest.raises(AuthenticationError, match="HTTP 401"):
            self._call(client)

    def test_400_raises_response_error(self, client, mock_urlopen):
        mock_urlopen.side_effect = make_http_error(400, b"bad branch")

        with pytest.raises(ResponseError, match="HTTP 400"):
            self._call(client)


class TestListRepositoryPullRequestActivity:
    def test_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_repository_pull_request_activity(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/activity"
        assert request.method == "GET"


class TestGetPullRequest:
    def test_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        result = client.get_pull_request(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1"
        assert request.method == "GET"
        assert result == {"id": 1}


class TestUpdatePullRequest:
    def test_endpoint_and_method(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pull_request(
            workspace="ws", repository="repo", pull_request_id=5, title="new"
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/5"
        assert request.method == "PUT"

    def test_body_only_includes_provided(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pull_request(
            workspace="ws", repository="repo", pull_request_id=5, title="new"
        )

        assert sent_body(mock_urlopen) == {"title": "new"}

    def test_full_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pull_request(
            workspace="ws",
            repository="repo",
            pull_request_id=5,
            title="t",
            description="d",
            destination_branch="develop",
            reviewers=["{u}"],
        )

        assert sent_body(mock_urlopen) == {
            "title": "t",
            "description": "d",
            "destination": {"branch": {"name": "develop"}},
            "reviewers": [{"uuid": "{u}"}],
        }


class TestListPullRequestActivity:
    def test_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_pull_request_activity(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/activity"
        assert request.method == "GET"


class TestApproveDeclineRequestChanges:
    @pytest.mark.parametrize(
        ("method_name", "http_method", "url_suffix"),
        [
            ("approve_pull_request", "POST", "/approve"),
            ("unapprove_pull_request", "DELETE", "/approve"),
            ("request_changes", "POST", "/request-changes"),
            ("remove_request_changes", "DELETE", "/request-changes"),
            ("decline_pull_request", "POST", "/decline"),
        ],
    )
    def test_action_endpoints(self, client, mock_urlopen, method_name, http_method, url_suffix):
        mock_urlopen.return_value = make_response({})

        getattr(client, method_name)(workspace="ws", repository="repo", pull_request_id=7)

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/7{url_suffix}"
        assert request.method == http_method


class TestPullRequestComments:
    def test_list_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pull_request_comments(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/comments"
        assert request.method == "GET"

    def test_create_top_level(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, content="hi"
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/comments"
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"content": {"raw": "hi"}}

    def test_create_reply(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, content="hi", parent_id=99
        )

        assert sent_body(mock_urlopen) == {"content": {"raw": "hi"}, "parent": {"id": 99}}

    def test_create_inline(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_pull_request_comment(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            content="nit",
            inline_path="src/a.py",
            inline_to=42,
            inline_from=40,
        )

        assert sent_body(mock_urlopen) == {
            "content": {"raw": "nit"},
            "inline": {"path": "src/a.py", "to": 42, "from": 40},
        }

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 7})

        client.get_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/comments/7"
        assert request.method == "GET"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pull_request_comment(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            comment_id=7,
            content="edited",
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/comments/7"
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"content": {"raw": "edited"}}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.delete_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/comments/7"
        assert request.method == "DELETE"

    def test_resolve(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.resolve_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        request = sent_request(mock_urlopen)
        assert (
            request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/comments/7/resolve"
        )
        assert request.method == "POST"

    def test_reopen(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.reopen_pull_request_comment(
            workspace="ws", repository="repo", pull_request_id=1, comment_id=7
        )

        request = sent_request(mock_urlopen)
        assert (
            request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/comments/7/resolve"
        )
        assert request.method == "DELETE"


class TestListPullRequestCommitsAndConflicts:
    def test_commits(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pull_request_commits(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/commits"
        assert request.method == "GET"

    def test_conflicts(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pull_request_conflicts(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/conflicts"
        assert request.method == "GET"


class TestDiffAndPatch:
    def test_diff_returns_raw_text(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"diff --git a/x b/x\n")

        result = client.get_pull_request_diff(workspace="ws", repository="repo", pull_request_id=1)

        assert result == "diff --git a/x b/x\n"
        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/diff"
        assert request.method == "GET"

    def test_patch_returns_raw_text(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"From abc...")

        result = client.get_pull_request_patch(workspace="ws", repository="repo", pull_request_id=1)

        assert result == "From abc..."
        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/patch"

    def test_diffstat_returns_json(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": [{"status": "modified"}]})

        result = client.get_pull_request_diffstat(
            workspace="ws", repository="repo", pull_request_id=1
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/diffstat"
        assert result == {"values": [{"status": "modified"}]}


class TestMerge:
    def test_minimal(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"state": "MERGED"})

        client.merge_pull_request(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/merge"
        assert request.method == "POST"
        assert query == {}
        assert request.data is None

    def test_full_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.merge_pull_request(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            message="merging",
            close_source_branch=True,
            merge_strategy="squash",
        )

        assert sent_body(mock_urlopen) == {
            "message": "merging",
            "close_source_branch": True,
            "merge_strategy": "squash",
        }

    def test_async_param(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.merge_pull_request(workspace="ws", repository="repo", pull_request_id=1, async_=True)

        _, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert query == {"async": ["True"]}

    def test_merge_task_status(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"task_status": "PENDING"})

        client.get_merge_task_status(
            workspace="ws", repository="repo", pull_request_id=1, task_id="t-1"
        )

        request = sent_request(mock_urlopen)
        assert (
            request.full_url
            == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/merge/task-status/t-1"
        )
        assert request.method == "GET"


class TestStatuses:
    def test_endpoint(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pull_request_statuses(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/statuses"
        assert request.method == "GET"


class TestTasks:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pull_request_tasks(workspace="ws", repository="repo", pull_request_id=1)

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/tasks"
        assert request.method == "GET"

    def test_create_minimal(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        client.create_pull_request_task(
            workspace="ws", repository="repo", pull_request_id=1, content="fix it"
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/pullrequests/1/tasks"
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"content": {"raw": "fix it"}}

    def test_create_anchored_to_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_pull_request_task(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            content="fix it",
            comment_id=99,
            pending=True,
        )

        assert sent_body(mock_urlopen) == {
            "content": {"raw": "fix it"},
            "comment": {"id": 99},
            "pending": True,
        }

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 5})

        client.get_pull_request_task(
            workspace="ws", repository="repo", pull_request_id=1, task_id=5
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/tasks/5"
        assert request.method == "GET"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pull_request_task(
            workspace="ws",
            repository="repo",
            pull_request_id=1,
            task_id=5,
            content="updated",
            state="RESOLVED",
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/tasks/5"
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {
            "content": {"raw": "updated"},
            "state": "RESOLVED",
        }

    def test_update_partial(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pull_request_task(
            workspace="ws", repository="repo", pull_request_id=1, task_id=5, state="RESOLVED"
        )

        assert sent_body(mock_urlopen) == {"state": "RESOLVED"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.delete_pull_request_task(
            workspace="ws", repository="repo", pull_request_id=1, task_id=5
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/pullrequests/1/tasks/5"
        assert request.method == "DELETE"


class TestAuthHeaderOnNewEndpoints:
    def test_basic_auth_on_get_pull_request(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pull_request(workspace="ws", repository="repo", pull_request_id=1)

        expected = "Basic " + base64.b64encode(b"a@b.com:tok").decode()
        assert sent_request(mock_urlopen).get_header("Authorization") == expected


class TestErrorMappingOnNewEndpoints:
    def test_401_on_approve(self, client, mock_urlopen):
        mock_urlopen.side_effect = make_http_error(401)

        with pytest.raises(AuthenticationError, match="HTTP 401"):
            client.approve_pull_request(workspace="ws", repository="r", pull_request_id=1)

    def test_404_on_get(self, client, mock_urlopen):
        mock_urlopen.side_effect = make_http_error(404, b"not found")

        with pytest.raises(ResponseError, match="HTTP 404"):
            client.get_pull_request(workspace="ws", repository="r", pull_request_id=1)


# ---------------------------------------------------------------------------
# Workspaces
# ---------------------------------------------------------------------------


class TestWorkspaceEndpoints:
    def test_list_user_workspace_permissions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_workspace_permissions(q="x", sort="s", page=2, pagelen=10)

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/user/permissions/workspaces"
        assert request.method == "GET"
        assert query == {"q": ["x"], "sort": ["s"], "page": ["2"], "pagelen": ["10"]}

    def test_list_user_workspaces(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_workspaces(sort="slug", administrator=True)

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/user/workspaces"
        assert request.method == "GET"
        assert query == {"sort": ["slug"], "administrator": ["True"]}

    def test_get_user_workspace_permission(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"permission": "owner"})

        client.get_user_workspace_permission(workspace="ws")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/user/workspaces/ws/permission"
        assert request.method == "GET"

    def test_list_workspaces(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspaces(role="owner")

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/workspaces"
        assert request.method == "GET"
        assert query == {"role": ["owner"]}

    def test_get_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"slug": "ws"})

        client.get_workspace(workspace="ws")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws"
        assert request.method == "GET"

    def test_list_workspace_webhooks(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_webhooks(workspace="ws")

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/workspaces/ws/hooks"
        assert request.method == "GET"

    def test_create_workspace_webhook_minimal(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"uuid": "{w}"})

        client.create_workspace_webhook(
            workspace="ws", url="https://example.com/hook", events=["repo:push"]
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws/hooks"
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {
            "url": "https://example.com/hook",
            "events": ["repo:push"],
        }

    def test_create_workspace_webhook_full(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_workspace_webhook(
            workspace="ws",
            url="https://example.com/hook",
            events=["repo:push", "pullrequest:created"],
            description="my hook",
            active=True,
            secret="s3cret",
        )

        assert sent_body(mock_urlopen) == {
            "url": "https://example.com/hook",
            "events": ["repo:push", "pullrequest:created"],
            "description": "my hook",
            "active": True,
            "secret": "s3cret",
        }

    def test_delete_workspace_webhook(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.delete_workspace_webhook(workspace="ws", uid="{abc}")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws/hooks/%7Babc%7D".replace(
            "%7B", "{"
        ).replace("%7D", "}")
        assert request.method == "DELETE"

    def test_get_workspace_webhook(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"uuid": "{abc}"})

        client.get_workspace_webhook(workspace="ws", uid="{abc}")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws/hooks/{{abc}}"
        assert request.method == "GET"

    def test_update_workspace_webhook(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_workspace_webhook(
            workspace="ws", uid="{abc}", url="https://new", events=["repo:push"]
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws/hooks/{{abc}}"
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {
            "url": "https://new",
            "events": ["repo:push"],
        }

    def test_list_workspace_members(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_members(workspace="ws", q='user.email IN ("a@b.com")')

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/members"
        assert query == {"q": ['user.email IN ("a@b.com")']}

    def test_get_workspace_member(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"user": {}})

        client.get_workspace_member(workspace="ws", member="{uuid}")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws/members/{{uuid}}"
        assert request.method == "GET"

    def test_list_workspace_permissions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_permissions(workspace="ws", q='permission="admin"')

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/permissions"
        assert query == {"q": ['permission="admin"']}

    def test_list_workspace_repository_permissions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_repository_permissions(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/permissions/repositories"

    def test_list_workspace_repository_permissions_for_repo(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_repository_permissions_for_repo(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/permissions/repositories/repo"

    def test_list_workspace_projects(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_projects(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects"

    def test_get_workspace_project(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"key": "MARS"})

        client.get_workspace_project(workspace="ws", project_key="MARS")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws/projects/MARS"
        assert request.method == "GET"

    def test_list_workspace_user_pull_requests_single_state(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_user_pull_requests(
            workspace="ws", selected_user="alice", state="OPEN"
        )

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/pullrequests/alice"
        assert query == {"state": ["OPEN"]}

    def test_list_workspace_user_pull_requests_multi_state(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_workspace_user_pull_requests(
            workspace="ws", selected_user="alice", state=["OPEN", "MERGED"]
        )

        _, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert query == {"state": ["OPEN", "MERGED"]}

    def test_get_workspace_gpg_key(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"key": "ABC"})

        client.get_workspace_gpg_key(workspace="ws")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/workspaces/ws/settings/gpg/public-key"
        assert request.method == "GET"


# ---------------------------------------------------------------------------
# Repositories
# ---------------------------------------------------------------------------


class TestRepositoryEndpoints:
    def test_list_public_repositories(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_public_repositories(after="2024-01-01T00:00:00Z", role="member")

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories"
        assert query == {"after": ["2024-01-01T00:00:00Z"], "role": ["member"]}

    def test_list_repositories(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_repositories(workspace="ws", role="admin", q='name="repo"', sort="-updated_on")

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws"
        assert query == {
            "role": ["admin"],
            "q": ['name="repo"'],
            "sort": ["-updated_on"],
        }

    def test_get_repository(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"slug": "repo"})

        client.get_repository(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo"
        assert request.method == "GET"

    def test_create_repository_minimal(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_repository(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo"
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {}

    def test_create_repository_full(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_repository(
            workspace="ws",
            repository="repo",
            scm="git",
            name="My Repo",
            description="A repo",
            is_private=True,
            fork_policy="no_forks",
            language="python",
            has_issues=True,
            has_wiki=False,
            project_key="MARS",
            mainbranch_name="main",
        )

        assert sent_body(mock_urlopen) == {
            "scm": "git",
            "name": "My Repo",
            "description": "A repo",
            "is_private": True,
            "fork_policy": "no_forks",
            "language": "python",
            "has_issues": True,
            "has_wiki": False,
            "project": {"key": "MARS"},
            "mainbranch": {"name": "main"},
        }

    def test_update_repository(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_repository(
            workspace="ws", repository="repo", description="updated", is_private=False
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo"
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {
            "description": "updated",
            "is_private": False,
        }

    def test_delete_repository(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.delete_repository(workspace="ws", repository="repo", redirect_to="https://elsewhere")

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo"
        assert request.method == "DELETE"
        assert query == {"redirect_to": ["https://elsewhere"]}

    def test_list_file_history(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_file_history(
            workspace="ws",
            repository="repo",
            commit="abc",
            path="src/foo.py",
            renames="true",
        )

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/filehistory/abc/src/foo.py"
        assert request.method == "GET"
        assert query == {"renames": ["true"]}

    def test_list_repository_forks(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_repository_forks(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/forks"

    def test_fork_repository(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.fork_repository(
            workspace="ws",
            repository="repo",
            name="my-fork",
            destination_workspace="other",
            is_private=True,
            project_key="X",
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/forks"
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {
            "name": "my-fork",
            "workspace": {"slug": "other"},
            "is_private": True,
            "project": {"key": "X"},
        }

    def test_fork_repository_no_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.fork_repository(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        assert request.data is None

    def test_list_repository_webhooks(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_repository_webhooks(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/hooks"

    def test_create_repository_webhook(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_repository_webhook(
            workspace="ws",
            repository="repo",
            url="https://example.com",
            events=["repo:push"],
            active=True,
        )

        assert sent_body(mock_urlopen) == {
            "url": "https://example.com",
            "events": ["repo:push"],
            "active": True,
        }

    def test_repository_webhook_lifecycle(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_repository_webhook(workspace="ws", repository="repo", uid="abc")
        client.delete_repository_webhook(workspace="ws", repository="repo", uid="abc")
        client.update_repository_webhook(
            workspace="ws", repository="repo", uid="abc", description="x"
        )

        urls = [call.args[0].full_url for call in mock_urlopen.call_args_list]
        methods = [call.args[0].method for call in mock_urlopen.call_args_list]
        assert all(url == f"{BASE_URL}/repositories/ws/repo/hooks/abc" for url in urls)
        assert methods == ["GET", "DELETE", "PUT"]

    def test_get_repository_override_settings(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"branching_model": True})

        client.get_repository_override_settings(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/override-settings"
        assert request.method == "GET"

    def test_set_repository_override_settings(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.set_repository_override_settings(
            workspace="ws",
            repository="repo",
            settings={"branching_model": False, "default_reviewers": True},
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {
            "branching_model": False,
            "default_reviewers": True,
        }

    def test_group_permissions_lifecycle(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_repository_group_permissions(workspace="ws", repository="repo")
        client.get_repository_group_permission(
            workspace="ws", repository="repo", group_slug="developers"
        )
        client.update_repository_group_permission(
            workspace="ws",
            repository="repo",
            group_slug="developers",
            permission="write",
        )
        client.delete_repository_group_permission(
            workspace="ws", repository="repo", group_slug="developers"
        )

        urls_and_methods = [
            (call.args[0].full_url, call.args[0].method) for call in mock_urlopen.call_args_list
        ]
        assert urls_and_methods == [
            (
                f"{BASE_URL}/repositories/ws/repo/permissions-config/groups",
                "GET",
            ),
            (
                f"{BASE_URL}/repositories/ws/repo/permissions-config/groups/developers",
                "GET",
            ),
            (
                f"{BASE_URL}/repositories/ws/repo/permissions-config/groups/developers",
                "PUT",
            ),
            (
                f"{BASE_URL}/repositories/ws/repo/permissions-config/groups/developers",
                "DELETE",
            ),
        ]

    def test_update_group_permission_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_repository_group_permission(
            workspace="ws",
            repository="repo",
            group_slug="developers",
            permission="admin",
        )

        assert sent_body(mock_urlopen) == {"permission": "admin"}

    def test_user_permissions_lifecycle(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_repository_user_permissions(workspace="ws", repository="repo")
        client.get_repository_user_permission(
            workspace="ws", repository="repo", selected_user_id="{uuid}"
        )
        client.update_repository_user_permission(
            workspace="ws",
            repository="repo",
            selected_user_id="{uuid}",
            permission="read",
        )
        client.delete_repository_user_permission(
            workspace="ws", repository="repo", selected_user_id="{uuid}"
        )

        methods = [call.args[0].method for call in mock_urlopen.call_args_list]
        assert methods == ["GET", "GET", "PUT", "DELETE"]

    def test_update_user_permission_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_repository_user_permission(
            workspace="ws",
            repository="repo",
            selected_user_id="{uuid}",
            permission="read",
        )

        assert sent_body(mock_urlopen) == {"permission": "read"}

    def test_get_repository_root_src(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"file content here")

        result = client.get_repository_root_src(workspace="ws", repository="repo", format="meta")

        assert result == "file content here"
        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/src"
        assert query == {"format": ["meta"]}

    def test_create_src_commit_multipart(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"hash": "abc123"})

        client.create_src_commit(
            workspace="ws",
            repository="repo",
            message="commit",
            author="A <a@b>",
            branch="main",
            files_to_add={"src/foo.py": b"print('hi')\n"},
            files_to_delete=["src/old.py"],
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/src"
        assert request.method == "POST"
        content_type = request.get_header("Content-type")
        assert content_type.startswith("multipart/form-data; boundary=")
        body = request.data
        assert b'name="message"' in body
        assert b"commit" in body
        assert b'name="author"' in body
        assert b"A <a@b>" in body
        assert b'name="branch"' in body
        assert b"main" in body
        assert b'name="files"' in body
        assert b"src/old.py" in body
        assert b'name="src/foo.py"' in body
        assert b'filename="foo.py"' in body
        assert b"print('hi')" in body

    def test_get_repository_src(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"contents")

        result = client.get_repository_src(
            workspace="ws",
            repository="repo",
            commit="HEAD",
            path="src/foo.py",
            format="rendered",
            max_depth=2,
        )

        assert result == "contents"
        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/src/HEAD/src/foo.py"
        assert query == {"format": ["rendered"], "max_depth": ["2"]}

    def test_list_repository_watchers(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_repository_watchers(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/watchers"

    def test_list_user_repository_permissions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_repository_permissions(q='repository.name="x"')

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/user/permissions/repositories"
        assert query == {"q": ['repository.name="x"']}

    def test_list_user_workspace_repository_permissions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_workspace_repository_permissions(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/user/workspaces/ws/permissions/repositories"


# ---------------------------------------------------------------------------
# Commits
# ---------------------------------------------------------------------------


class TestCommitEndpoints:
    def test_get_commit(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"hash": "abc"})

        client.get_commit(workspace="ws", repository="repo", commit="abc")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/commit/abc"
        assert request.method == "GET"

    def test_approve_commit(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.approve_commit(workspace="ws", repository="repo", commit="abc")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/commit/abc/approve"
        assert request.method == "POST"

    def test_unapprove_commit(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.unapprove_commit(workspace="ws", repository="repo", commit="abc")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/commit/abc/approve"
        assert request.method == "DELETE"

    def test_list_commit_comments(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commit_comments(workspace="ws", repository="repo", commit="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/commit/abc/comments"

    def test_create_commit_comment_top_level(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_commit_comment(
            workspace="ws", repository="repo", commit="abc", content="lgtm"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"content": {"raw": "lgtm"}}

    def test_create_commit_comment_inline_reply(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_commit_comment(
            workspace="ws",
            repository="repo",
            commit="abc",
            content="nit",
            parent_id=10,
            inline_path="src/a.py",
            inline_to=42,
            inline_from=40,
        )

        assert sent_body(mock_urlopen) == {
            "content": {"raw": "nit"},
            "parent": {"id": 10},
            "inline": {"path": "src/a.py", "to": 42, "from": 40},
        }

    def test_commit_comment_lifecycle(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_commit_comment(workspace="ws", repository="repo", commit="abc", comment_id=5)
        client.update_commit_comment(
            workspace="ws",
            repository="repo",
            commit="abc",
            comment_id=5,
            content="edited",
        )
        client.delete_commit_comment(workspace="ws", repository="repo", commit="abc", comment_id=5)

        urls = [call.args[0].full_url for call in mock_urlopen.call_args_list]
        methods = [call.args[0].method for call in mock_urlopen.call_args_list]
        assert all(u == f"{BASE_URL}/repositories/ws/repo/commit/abc/comments/5" for u in urls)
        assert methods == ["GET", "PUT", "DELETE"]

    def test_list_commit_reports(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commit_reports(workspace="ws", repository="repo", commit="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/commit/abc/reports"

    def test_create_or_update_commit_report(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_or_update_commit_report(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r-1",
            title="My Report",
            details="details",
            report_type="COVERAGE",
            result="PASSED",
            data=[{"type": "NUMBER", "title": "Coverage", "value": 95}],
        )

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/commit/abc/reports/r-1"
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {
            "title": "My Report",
            "details": "details",
            "report_type": "COVERAGE",
            "result": "PASSED",
            "data": [{"type": "NUMBER", "title": "Coverage", "value": 95}],
        }

    def test_get_and_delete_commit_report(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_commit_report(workspace="ws", repository="repo", commit="abc", report_id="r-1")
        client.delete_commit_report(
            workspace="ws", repository="repo", commit="abc", report_id="r-1"
        )

        urls = [call.args[0].full_url for call in mock_urlopen.call_args_list]
        methods = [call.args[0].method for call in mock_urlopen.call_args_list]
        assert all(u == f"{BASE_URL}/repositories/ws/repo/commit/abc/reports/r-1" for u in urls)
        assert methods == ["GET", "DELETE"]

    def test_list_commit_report_annotations(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commit_report_annotations(
            workspace="ws", repository="repo", commit="abc", report_id="r-1"
        )

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/commit/abc/reports/r-1/annotations"

    def test_bulk_create_or_update_annotations(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response([{"uuid": "a-1"}])

        result = client.bulk_create_or_update_annotations(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r-1",
            annotations=[
                {
                    "external_id": "ann-1",
                    "annotation_type": "BUG",
                    "summary": "broken",
                    "path": "src/a.py",
                    "line": 5,
                    "severity": "HIGH",
                }
            ],
        )

        assert result == [{"uuid": "a-1"}]
        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        body = json.loads(request.data)
        assert isinstance(body, list)
        assert body[0]["external_id"] == "ann-1"

    def test_annotation_lifecycle(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_commit_report_annotation(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r-1",
            annotation_id="a-1",
        )
        client.create_or_update_commit_report_annotation(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r-1",
            annotation_id="a-1",
            annotation_type="BUG",
            path="src/a.py",
            line=10,
            severity="HIGH",
        )
        client.delete_commit_report_annotation(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r-1",
            annotation_id="a-1",
        )

        urls = [call.args[0].full_url for call in mock_urlopen.call_args_list]
        methods = [call.args[0].method for call in mock_urlopen.call_args_list]
        expected = f"{BASE_URL}/repositories/ws/repo/commit/abc/reports/r-1/annotations/a-1"
        assert all(u == expected for u in urls)
        assert methods == ["GET", "PUT", "DELETE"]

    def test_create_or_update_annotation_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_or_update_commit_report_annotation(
            workspace="ws",
            repository="repo",
            commit="abc",
            report_id="r-1",
            annotation_id="a-1",
            annotation_type="VULNERABILITY",
            path="src/a.py",
            line=10,
            severity="CRITICAL",
            result="FAILED",
        )

        assert sent_body(mock_urlopen) == {
            "annotation_type": "VULNERABILITY",
            "path": "src/a.py",
            "line": 10,
            "severity": "CRITICAL",
            "result": "FAILED",
        }

    def test_list_commits(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commits(
            workspace="ws",
            repository="repo",
            include=["master", "develop"],
            exclude=["legacy"],
        )

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/commits"
        assert request.method == "GET"
        assert query == {"include": ["master", "develop"], "exclude": ["legacy"]}

    def test_list_commits_with_filter(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commits_with_filter(
            workspace="ws", repository="repo", include=["a"], exclude=["b"]
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/commits"
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"include": ["a"], "exclude": ["b"]}

    def test_list_commits_with_filter_no_body(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_commits_with_filter(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert request.data is None

    def test_list_commits_for_revision(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commits_for_revision(
            workspace="ws", repository="repo", revision="main", path="src/x.py"
        )

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/commits/main"
        assert query == {"path": ["src/x.py"]}

    def test_list_commits_for_revision_with_filter(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commits_for_revision_with_filter(
            workspace="ws", repository="repo", revision="main", include=["foo"]
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/commits/main"
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"include": ["foo"]}

    def test_get_diff(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"diff --git ...")

        result = client.get_diff(
            workspace="ws",
            repository="repo",
            spec="abc..def",
            context=5,
            path=["src/a.py", "src/b.py"],
            ignore_whitespace=True,
        )

        assert result == "diff --git ..."
        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/diff/abc..def"
        assert query == {
            "context": ["5"],
            "path": ["src/a.py", "src/b.py"],
            "ignore_whitespace": ["True"],
        }

    def test_get_diffstat(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": [{"status": "modified"}]})

        client.get_diffstat(workspace="ws", repository="repo", spec="abc..def")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/diffstat/abc..def"

    def test_list_file_conflicts(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_file_conflicts(workspace="ws", repository="repo", spec="abc..def")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/file-conflicts/abc..def"

    def test_get_merge_base(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"hash": "base"})

        client.get_merge_base(workspace="ws", repository="repo", revspec="abc..def")

        request = sent_request(mock_urlopen)
        assert request.full_url == f"{BASE_URL}/repositories/ws/repo/merge-base/abc..def"

    def test_get_patch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"From abc...")

        result = client.get_patch(workspace="ws", repository="repo", spec="abc")

        assert result == "From abc..."
        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/patch/abc"


class TestParamsDoSeq:
    """Verify list-valued query params are serialized as repeated keys."""

    def test_include_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_commits(workspace="ws", repository="repo", include=["a", "b", "c"])

        query_string = sent_request(mock_urlopen).full_url.split("?", 1)[1]
        assert "include=a" in query_string
        assert "include=b" in query_string
        assert "include=c" in query_string
