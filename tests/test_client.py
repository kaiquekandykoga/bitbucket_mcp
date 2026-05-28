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


# ---------------------------------------------------------------------------
# Pull request default reviewers
# ---------------------------------------------------------------------------


class TestDefaultReviewers:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_default_reviewers(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/default-reviewers"
        assert request.method == "GET"

    def test_list_effective(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_effective_default_reviewers(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/effective-default-reviewers"

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_default_reviewer(workspace="ws", repository="repo", target_username="{u}")

        request = sent_request(mock_urlopen)
        assert request.full_url.endswith("/repositories/ws/repo/default-reviewers/{u}")
        assert request.method == "GET"

    def test_add(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.add_default_reviewer(workspace="ws", repository="repo", target_username="bob")

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert request.full_url.endswith("/repositories/ws/repo/default-reviewers/bob")

    def test_remove(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.remove_default_reviewer(workspace="ws", repository="repo", target_username="bob")

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Branch restrictions
# ---------------------------------------------------------------------------


class TestBranchRestrictions:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_branch_restrictions(workspace="ws", repository="repo", kind="push")

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/branch-restrictions"
        assert query == {"kind": ["push"]}

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        client.create_branch_restriction(
            workspace="ws",
            repository="repo",
            kind="push",
            pattern="main",
            users=["{u}"],
            value=2,
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        body = sent_body(mock_urlopen)
        assert body["kind"] == "push"
        assert body["pattern"] == "main"
        assert body["users"] == [{"uuid": "{u}"}]
        assert body["value"] == 2

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        client.get_branch_restriction(workspace="ws", repository="repo", id=42)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/branch-restrictions/42"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        client.update_branch_restriction(workspace="ws", repository="repo", id=42, pattern="dev*")

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"pattern": "dev*"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_branch_restriction(workspace="ws", repository="repo", id=42)

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Branching model
# ---------------------------------------------------------------------------


class TestBranchingModel:
    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_branching_model(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/branching-model"

    def test_get_effective(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_effective_branching_model(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/effective-branching-model"

    def test_get_settings(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_branching_model_settings(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/branching-model/settings"

    def test_update_settings(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_branching_model_settings(
            workspace="ws",
            repository="repo",
            development={"use_mainbranch": True},
            production={"enabled": False},
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        body = sent_body(mock_urlopen)
        assert body["development"] == {"use_mainbranch": True}
        assert body["production"] == {"enabled": False}

    def test_project_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_project_branching_model(workspace="ws", project_key="PROJ")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/branching-model"

    def test_project_get_settings(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_project_branching_model_settings(workspace="ws", project_key="PROJ")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/branching-model/settings"

    def test_project_update_settings(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_project_branching_model_settings(
            workspace="ws", project_key="PROJ", development={"name": "develop"}
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"development": {"name": "develop"}}


# ---------------------------------------------------------------------------
# Commit build statuses
# ---------------------------------------------------------------------------


class TestCommitBuildStatuses:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_commit_statuses(workspace="ws", repository="repo", commit="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/commit/abc/statuses"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"key": "ci"})

        client.create_commit_build_status(
            workspace="ws",
            repository="repo",
            commit="abc",
            key="ci",
            state="SUCCESSFUL",
            url="https://ci.example.com/1",
            name="CI",
            description="OK",
            refname="main",
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/commit/abc/statuses/build"
        assert request.method == "POST"
        body = sent_body(mock_urlopen)
        assert body["key"] == "ci"
        assert body["state"] == "SUCCESSFUL"
        assert body["url"] == "https://ci.example.com/1"
        assert body["name"] == "CI"
        assert body["description"] == "OK"
        assert body["refname"] == "main"

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_commit_build_status(workspace="ws", repository="repo", commit="abc", key="ci")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/commit/abc/statuses/build/ci"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_commit_build_status(
            workspace="ws",
            repository="repo",
            commit="abc",
            key="ci",
            state="FAILED",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"state": "FAILED"}


# ---------------------------------------------------------------------------
# Deploy keys
# ---------------------------------------------------------------------------


class TestDeployKeys:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_deploy_keys(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/deploy-keys"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        client.create_deploy_key(
            workspace="ws", repository="repo", key="ssh-rsa AAA...", label="prod"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        body = sent_body(mock_urlopen)
        assert body == {"key": "ssh-rsa AAA...", "label": "prod"}

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_deploy_key(workspace="ws", repository="repo", key_id="42")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/deploy-keys/42"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_deploy_key(workspace="ws", repository="repo", key_id="42", label="staging")

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"label": "staging"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_deploy_key(workspace="ws", repository="repo", key_id="42")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_project_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_project_deploy_keys(workspace="ws", project_key="PROJ")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/deploy-keys"

    def test_project_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        client.create_project_deploy_key(
            workspace="ws", project_key="PROJ", key="ssh-rsa AAA...", label="ci"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"key": "ssh-rsa AAA...", "label": "ci"}

    def test_project_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_project_deploy_key(workspace="ws", project_key="PROJ", key_id="42")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/deploy-keys/42"

    def test_project_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_project_deploy_key(workspace="ws", project_key="PROJ", key_id="42")

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Deployments & environments
# ---------------------------------------------------------------------------


class TestDeployments:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_deployments(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/deployments"

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_deployment(workspace="ws", repository="repo", deployment_uuid="dep1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/deployments/dep1"


class TestEnvironments:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_environments(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/environments"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"uuid": "{x}"})

        client.create_environment(
            workspace="ws",
            repository="repo",
            name="Production",
            environment_type={"name": "Production"},
            rank=1,
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        body = sent_body(mock_urlopen)
        assert body == {
            "name": "Production",
            "environment_type": {"name": "Production"},
            "rank": 1,
        }

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_environment(workspace="ws", repository="repo", environment_uuid="env1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/environments/env1"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_environment(
            workspace="ws",
            repository="repo",
            environment_uuid="env1",
            body={"name": "Staging"},
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert request.method == "POST"
        assert path == "/2.0/repositories/ws/repo/environments/env1/changes"
        assert sent_body(mock_urlopen) == {"name": "Staging"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_environment(workspace="ws", repository="repo", environment_uuid="env1")

        request = sent_request(mock_urlopen)
        assert request.method == "DELETE"


# ---------------------------------------------------------------------------
# Downloads
# ---------------------------------------------------------------------------


class TestDownloads:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_downloads(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/downloads"

    def test_upload(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.upload_download(workspace="ws", repository="repo", files={"x.txt": b"hello"})

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        content_type = request.get_header("Content-type")
        assert content_type.startswith("multipart/form-data;")
        assert b"hello" in request.data
        assert b'filename="x.txt"' in request.data

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"binary")

        result = client.get_download(workspace="ws", repository="repo", filename="x.txt")

        assert result == "binary"
        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/downloads/x.txt"

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_download(workspace="ws", repository="repo", filename="x.txt")

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# GPG keys
# ---------------------------------------------------------------------------


class TestUserGpgKeys:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_gpg_keys(selected_user="bob")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob/gpg-keys"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_user_gpg_key(selected_user="bob", key="-----BEGIN", name="primary")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"key": "-----BEGIN", "name": "primary"}

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_user_gpg_key(selected_user="bob", fingerprint="ABCD")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob/gpg-keys/ABCD"

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_user_gpg_key(selected_user="bob", fingerprint="ABCD")

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Issue tracker
# ---------------------------------------------------------------------------


class TestIssueTracker:
    def test_list_components(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_components(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/components"

    def test_get_component(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_component(workspace="ws", repository="repo", component_id=1)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/components/1"

    def test_list_milestones(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_milestones(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/milestones"

    def test_get_milestone(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_milestone(workspace="ws", repository="repo", milestone_id=2)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/milestones/2"

    def test_list_versions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_versions(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/versions"

    def test_get_version(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_version(workspace="ws", repository="repo", version_id=3)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/versions/3"

    def test_list_issues(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_issues(workspace="ws", repository="repo", q='state="open"')

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/repositories/ws/repo/issues"
        assert query == {"q": ['state="open"']}

    def test_create_issue(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"id": 1})

        client.create_issue(
            workspace="ws",
            repository="repo",
            title="Bug",
            content="body",
            kind="bug",
            priority="major",
            state="new",
            component="ui",
            milestone="v1",
            version="0.1",
            assignee="{u}",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        body = sent_body(mock_urlopen)
        assert body == {
            "title": "Bug",
            "content": {"raw": "body"},
            "kind": "bug",
            "priority": "major",
            "state": "new",
            "component": {"name": "ui"},
            "milestone": {"name": "v1"},
            "version": {"name": "0.1"},
            "assignee": {"uuid": "{u}"},
        }

    def test_get_issue(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_issue(workspace="ws", repository="repo", issue_id=42)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/42"

    def test_update_issue(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_issue(workspace="ws", repository="repo", issue_id=42, state="resolved")

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"state": "resolved"}

    def test_delete_issue(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_issue(workspace="ws", repository="repo", issue_id=42)

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_export_issues(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"task_id": "abc"})

        client.export_issues(workspace="ws", repository="repo")

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert request.method == "POST"
        assert path == "/2.0/repositories/ws/repo/issues/export"

    def test_get_issue_export(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"binary zip data")

        result = client.get_issue_export(
            workspace="ws", repository="repo", repo_name="r", task_id="task1"
        )

        assert result == "binary zip data"
        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/export/r-issues-task1.zip"

    def test_get_issue_import_status(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_issue_import_status(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/import"

    def test_import_issues(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.import_issues(workspace="ws", repository="repo")

        assert sent_request(mock_urlopen).method == "POST"

    def test_list_issue_attachments(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_issue_attachments(workspace="ws", repository="repo", issue_id=1)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/1/attachments"

    def test_upload_issue_attachment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.upload_issue_attachment(
            workspace="ws", repository="repo", issue_id=1, files={"x.txt": b"abc"}
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert request.get_header("Content-type").startswith("multipart/form-data")

    def test_get_issue_attachment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"file body")

        result = client.get_issue_attachment(
            workspace="ws", repository="repo", issue_id=1, path="x.txt"
        )

        assert result == "file body"

    def test_delete_issue_attachment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_issue_attachment(workspace="ws", repository="repo", issue_id=1, path="x.txt")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_issue_changes(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_issue_changes(workspace="ws", repository="repo", issue_id=1)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/1/changes"

    def test_create_issue_change(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_issue_change(
            workspace="ws",
            repository="repo",
            issue_id=1,
            changes={"state": {"new": "resolved"}},
            message="done",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        body = sent_body(mock_urlopen)
        assert body == {
            "changes": {"state": {"new": "resolved"}},
            "message": {"raw": "done"},
        }

    def test_get_issue_change(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_issue_change(workspace="ws", repository="repo", issue_id=1, change_id=2)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/1/changes/2"

    def test_list_issue_comments(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_issue_comments(workspace="ws", repository="repo", issue_id=1)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/1/comments"

    def test_create_issue_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_issue_comment(workspace="ws", repository="repo", issue_id=1, content="hi")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"content": {"raw": "hi"}}

    def test_get_issue_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_issue_comment(workspace="ws", repository="repo", issue_id=1, comment_id=5)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/1/comments/5"

    def test_update_issue_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_issue_comment(
            workspace="ws",
            repository="repo",
            issue_id=1,
            comment_id=5,
            content="edited",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"content": {"raw": "edited"}}

    def test_delete_issue_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_issue_comment(workspace="ws", repository="repo", issue_id=1, comment_id=5)

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_get_issue_vote(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_issue_vote(workspace="ws", repository="repo", issue_id=1)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/1/vote"

    def test_vote(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.vote_for_issue(workspace="ws", repository="repo", issue_id=1)

        assert sent_request(mock_urlopen).method == "PUT"

    def test_unvote(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.unvote_issue(workspace="ws", repository="repo", issue_id=1)

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_get_watch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_issue_watch(workspace="ws", repository="repo", issue_id=1)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/issues/1/watch"

    def test_watch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.watch_issue(workspace="ws", repository="repo", issue_id=1)

        assert sent_request(mock_urlopen).method == "PUT"

    def test_unwatch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.unwatch_issue(workspace="ws", repository="repo", issue_id=1)

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Projects (workspace-level)
# ---------------------------------------------------------------------------


class TestWorkspaceProjects:
    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_workspace_project(
            workspace="ws",
            key="PROJ",
            name="Project",
            description="desc",
            is_private=True,
        )

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert request.method == "POST"
        assert path == "/2.0/workspaces/ws/projects"
        assert sent_body(mock_urlopen) == {
            "key": "PROJ",
            "name": "Project",
            "description": "desc",
            "is_private": True,
        }

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_workspace_project(workspace="ws", project_key="PROJ", name="New Name")

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"name": "New Name"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_workspace_project(workspace="ws", project_key="PROJ")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_default_reviewers(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_project_default_reviewers(workspace="ws", project_key="PROJ")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/default-reviewers"

    def test_get_default_reviewer(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_project_default_reviewer(workspace="ws", project_key="PROJ", selected_user="bob")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/default-reviewers/bob"

    def test_add_default_reviewer(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.add_project_default_reviewer(workspace="ws", project_key="PROJ", selected_user="bob")

        assert sent_request(mock_urlopen).method == "PUT"

    def test_remove_default_reviewer(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.remove_project_default_reviewer(
            workspace="ws", project_key="PROJ", selected_user="bob"
        )

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_group_permissions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_project_group_permissions(workspace="ws", project_key="PROJ")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/permissions-config/groups"

    def test_get_group_permission(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_project_group_permission(workspace="ws", project_key="PROJ", group_slug="devs")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/permissions-config/groups/devs"

    def test_update_group_permission(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_project_group_permission(
            workspace="ws", project_key="PROJ", group_slug="devs", permission="write"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"permission": "write"}

    def test_delete_group_permission(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_project_group_permission(
            workspace="ws", project_key="PROJ", group_slug="devs"
        )

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_user_permissions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_project_user_permissions(workspace="ws", project_key="PROJ")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/permissions-config/users"

    def test_get_user_permission(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_project_user_permission(
            workspace="ws", project_key="PROJ", selected_user_id="u1"
        )

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/projects/PROJ/permissions-config/users/u1"

    def test_update_user_permission(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_project_user_permission(
            workspace="ws",
            project_key="PROJ",
            selected_user_id="u1",
            permission="admin",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"permission": "admin"}

    def test_delete_user_permission(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_project_user_permission(
            workspace="ws", project_key="PROJ", selected_user_id="u1"
        )

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Refs
# ---------------------------------------------------------------------------


class TestRefs:
    def test_list_refs(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_refs(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/refs"

    def test_list_branches(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_branches(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/refs/branches"

    def test_create_branch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_branch(workspace="ws", repository="repo", name="feature/x", target_hash="abc")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {
            "name": "feature/x",
            "target": {"hash": "abc"},
        }

    def test_get_branch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_branch(workspace="ws", repository="repo", name="main")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/refs/branches/main"

    def test_delete_branch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_branch(workspace="ws", repository="repo", name="feature/x")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_tags(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_tags(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/refs/tags"

    def test_create_tag(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_tag(
            workspace="ws",
            repository="repo",
            name="v1.0",
            target_hash="abc",
            message="ship it",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {
            "name": "v1.0",
            "target": {"hash": "abc"},
            "message": "ship it",
        }

    def test_get_tag(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_tag(workspace="ws", repository="repo", name="v1.0")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/refs/tags/v1.0"

    def test_delete_tag(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_tag(workspace="ws", repository="repo", name="v1.0")

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


class TestSearch:
    def test_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.search_workspace_code(workspace="ws", search_query="hello")

        request = sent_request(mock_urlopen)
        path, query = url_path_and_query(request.full_url)
        assert path == "/2.0/workspaces/ws/search/code"
        assert query == {"search_query": ["hello"]}

    def test_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.search_user_code(selected_user="bob", search_query="hello")

        path, query = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob/search/code"
        assert query == {"search_query": ["hello"]}


# ---------------------------------------------------------------------------
# Snippets
# ---------------------------------------------------------------------------


class TestSnippets:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_snippets()

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_snippet(title="t", is_private=True, files={"x.txt": b"hi"})

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert request.get_header("Content-type").startswith("multipart/form-data")
        assert b"hi" in request.data

    def test_list_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_snippets(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws"

    def test_create_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_workspace_snippet(workspace="ws", title="t")

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert request.method == "POST"
        assert path == "/2.0/snippets/ws"

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_snippet(workspace="ws", encoded_id="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_snippet(workspace="ws", encoded_id="abc", title="new")

        assert sent_request(mock_urlopen).method == "PUT"

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_snippet(workspace="ws", encoded_id="abc")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_comments(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_snippet_comments(workspace="ws", encoded_id="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc/comments"

    def test_create_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_snippet_comment(workspace="ws", encoded_id="abc", content="hi")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"content": {"raw": "hi"}}

    def test_get_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_snippet_comment(workspace="ws", encoded_id="abc", comment_id=1)

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc/comments/1"

    def test_update_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_snippet_comment(
            workspace="ws", encoded_id="abc", comment_id=1, content="edit"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"content": {"raw": "edit"}}

    def test_delete_comment(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_snippet_comment(workspace="ws", encoded_id="abc", comment_id=1)

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_commits(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_snippet_commits(workspace="ws", encoded_id="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc/commits"

    def test_get_commit(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_snippet_commit(workspace="ws", encoded_id="abc", revision="r1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc/commits/r1"

    def test_get_file(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"hello")

        result = client.get_snippet_file(workspace="ws", encoded_id="abc", path="x.txt")

        assert result == "hello"

    def test_get_watch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_snippet_watch(workspace="ws", encoded_id="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc/watch"

    def test_watch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.watch_snippet(workspace="ws", encoded_id="abc")

        assert sent_request(mock_urlopen).method == "PUT"

    def test_unwatch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.unwatch_snippet(workspace="ws", encoded_id="abc")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_watchers(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_snippet_watchers(workspace="ws", encoded_id="abc")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc/watchers"

    def test_get_at_revision(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_snippet_at_revision(workspace="ws", encoded_id="abc", node_id="n1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/snippets/ws/abc/n1"

    def test_update_at_revision(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_snippet_at_revision(
            workspace="ws", encoded_id="abc", node_id="n1", title="new"
        )

        assert sent_request(mock_urlopen).method == "PUT"

    def test_delete_at_revision(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_snippet_at_revision(workspace="ws", encoded_id="abc", node_id="n1")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_get_file_at_revision(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"hello")

        result = client.get_snippet_file_at_revision(
            workspace="ws", encoded_id="abc", node_id="n1", path="x.txt"
        )

        assert result == "hello"

    def test_get_diff(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"diff")

        result = client.get_snippet_diff(workspace="ws", encoded_id="abc", revision="r1")

        assert result == "diff"

    def test_get_patch(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"patch")

        result = client.get_snippet_patch(workspace="ws", encoded_id="abc", revision="r1")

        assert result == "patch"


# ---------------------------------------------------------------------------
# SSH keys
# ---------------------------------------------------------------------------


class TestUserSshKeys:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_ssh_keys(selected_user="bob")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob/ssh-keys"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_user_ssh_key(selected_user="bob", key="ssh-rsa AAA...", label="laptop")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"key": "ssh-rsa AAA...", "label": "laptop"}

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_user_ssh_key(selected_user="bob", key_id="42")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob/ssh-keys/42"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_user_ssh_key(selected_user="bob", key_id="42", label="new")

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"label": "new"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_user_ssh_key(selected_user="bob", key_id="42")

        assert sent_request(mock_urlopen).method == "DELETE"


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------


class TestUsers:
    def test_get_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"username": "bob"})

        client.get_user(selected_user="bob")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob"

    def test_list_user_emails(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_emails()

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/user/emails"

    def test_get_user_email(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_user_email(email="bob@example.com")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/user/emails/bob@example.com"


# ---------------------------------------------------------------------------
# Webhook event types
# ---------------------------------------------------------------------------


class TestHookEvents:
    def test_list_subjects(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_hook_event_subjects()

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/hook_events"

    def test_list_events(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_hook_events(subject_type="repository")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/hook_events/repository"


# ---------------------------------------------------------------------------
# Pipelines
# ---------------------------------------------------------------------------


class TestPipelinesCore:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pipelines(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        target = {"type": "pipeline_ref_target", "ref_name": "main"}
        client.create_pipeline(workspace="ws", repository="repo", target=target)

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"target": target}

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipeline(workspace="ws", repository="repo", pipeline_uuid="p1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines/p1"

    def test_stop(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.stop_pipeline(workspace="ws", repository="repo", pipeline_uuid="p1")

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert request.method == "POST"
        assert path == "/2.0/repositories/ws/repo/pipelines/p1/stopPipeline"

    def test_list_steps(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pipeline_steps(workspace="ws", repository="repo", pipeline_uuid="p1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines/p1/steps"

    def test_get_step(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipeline_step(
            workspace="ws", repository="repo", pipeline_uuid="p1", step_uuid="s1"
        )

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines/p1/steps/s1"

    def test_get_step_log(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"log output")

        result = client.get_pipeline_step_log(
            workspace="ws", repository="repo", pipeline_uuid="p1", step_uuid="s1"
        )

        assert result == "log output"
        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines/p1/steps/s1/log"

    def test_get_step_container_log(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"container log")

        result = client.get_pipeline_step_container_log(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
            log_uuid="l1",
        )

        assert result == "container log"
        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines/p1/steps/s1/logs/l1"

    def test_list_test_reports(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_pipeline_step_test_reports(
            workspace="ws", repository="repo", pipeline_uuid="p1", step_uuid="s1"
        )

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == ("/2.0/repositories/ws/repo/pipelines/p1/steps/s1/test_reports")

    def test_list_test_cases(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_pipeline_step_test_cases(
            workspace="ws", repository="repo", pipeline_uuid="p1", step_uuid="s1"
        )

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == ("/2.0/repositories/ws/repo/pipelines/p1/steps/s1/test_reports/test_cases")

    def test_list_test_case_reasons(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.list_pipeline_step_test_case_reasons(
            workspace="ws",
            repository="repo",
            pipeline_uuid="p1",
            step_uuid="s1",
            test_case_uuid="t1",
        )

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == (
            "/2.0/repositories/ws/repo/pipelines/p1/steps/s1/test_reports"
            "/test_cases/t1/test_case_reasons"
        )


class TestPipelineConfig:
    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipeline_config(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pipeline_config(workspace="ws", repository="repo", enabled=True)

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"enabled": True}

    def test_update_build_number(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pipeline_build_number(workspace="ws", repository="repo", next_build_number=42)

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert request.method == "PUT"
        assert path == "/2.0/repositories/ws/repo/pipelines_config/build_number"
        assert sent_body(mock_urlopen) == {"next": 42}


class TestPipelineSchedules:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pipeline_schedules(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config/schedules"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        target = {"ref_name": "main"}
        client.create_pipeline_schedule(
            workspace="ws",
            repository="repo",
            target=target,
            cron_pattern="0 0 * * *",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        body = sent_body(mock_urlopen)
        assert body == {"target": target, "cron_pattern": "0 0 * * *"}

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipeline_schedule(workspace="ws", repository="repo", schedule_uuid="s1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config/schedules/s1"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pipeline_schedule(
            workspace="ws", repository="repo", schedule_uuid="s1", enabled=False
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"enabled": False}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_pipeline_schedule(workspace="ws", repository="repo", schedule_uuid="s1")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_executions(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pipeline_schedule_executions(
            workspace="ws", repository="repo", schedule_uuid="s1"
        )

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == ("/2.0/repositories/ws/repo/pipelines_config/schedules/s1/executions")


class TestPipelineSshKeyPair:
    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipeline_ssh_key_pair(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config/ssh/key_pair"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pipeline_ssh_key_pair(
            workspace="ws", repository="repo", public_key="pub", private_key="priv"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"public_key": "pub", "private_key": "priv"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_pipeline_ssh_key_pair(workspace="ws", repository="repo")

        assert sent_request(mock_urlopen).method == "DELETE"


class TestPipelineKnownHosts:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pipeline_known_hosts(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config/ssh/known_hosts"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_pipeline_known_host(
            workspace="ws",
            repository="repo",
            hostname="github.com",
            public_key={"key": "AAA"},
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {
            "hostname": "github.com",
            "public_key": {"key": "AAA"},
        }

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipeline_known_host(workspace="ws", repository="repo", known_host_uuid="h1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config/ssh/known_hosts/h1"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pipeline_known_host(
            workspace="ws",
            repository="repo",
            known_host_uuid="h1",
            hostname="gitlab.com",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"hostname": "gitlab.com"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_pipeline_known_host(workspace="ws", repository="repo", known_host_uuid="h1")

        assert sent_request(mock_urlopen).method == "DELETE"


class TestPipelineVariables:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pipeline_variables(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config/variables"

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_pipeline_variable(
            workspace="ws", repository="repo", key="FOO", value="bar", secured=True
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"key": "FOO", "value": "bar", "secured": True}

    def test_get(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipeline_variable(workspace="ws", repository="repo", variable_uuid="v1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines_config/variables/v1"

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_pipeline_variable(
            workspace="ws", repository="repo", variable_uuid="v1", value="newval"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"value": "newval"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_pipeline_variable(workspace="ws", repository="repo", variable_uuid="v1")

        assert sent_request(mock_urlopen).method == "DELETE"


class TestPipelineCaches:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_pipeline_caches(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines-config/caches"

    def test_delete_all(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_pipeline_caches(workspace="ws", repository="repo", name="npm")

        request = sent_request(mock_urlopen)
        assert request.method == "DELETE"
        _, query = url_path_and_query(request.full_url)
        assert query == {"name": ["npm"]}

    def test_delete_single(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_pipeline_cache(workspace="ws", repository="repo", cache_uuid="c1")

        request = sent_request(mock_urlopen)
        path, _ = url_path_and_query(request.full_url)
        assert request.method == "DELETE"
        assert path == "/2.0/repositories/ws/repo/pipelines-config/caches/c1"

    def test_content_uri(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"uri": "https://..."})

        client.get_pipeline_cache_content_uri(workspace="ws", repository="repo", cache_uuid="c1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines-config/caches/c1/content-uri"


class TestPipelineRunners:
    def test_list_repo(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_repository_pipeline_runners(workspace="ws", repository="repo")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines-config/runners"

    def test_create_repo(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_repository_pipeline_runner(
            workspace="ws", repository="repo", name="r1", labels=["linux"]
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"name": "r1", "labels": ["linux"]}

    def test_get_repo(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_repository_pipeline_runner(workspace="ws", repository="repo", runner_uuid="r1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/repositories/ws/repo/pipelines-config/runners/r1"

    def test_update_repo(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_repository_pipeline_runner(
            workspace="ws", repository="repo", runner_uuid="r1", name="new"
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"name": "new"}

    def test_delete_repo(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_repository_pipeline_runner(
            workspace="ws", repository="repo", runner_uuid="r1"
        )

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_pipeline_runners(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/pipelines-config/runners"

    def test_create_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_workspace_pipeline_runner(workspace="ws", name="r1")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"name": "r1"}

    def test_get_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_workspace_pipeline_runner(workspace="ws", runner_uuid="r1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/pipelines-config/runners/r1"

    def test_update_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_workspace_pipeline_runner(workspace="ws", runner_uuid="r1", labels=["linux"])

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"labels": ["linux"]}

    def test_delete_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_workspace_pipeline_runner(workspace="ws", runner_uuid="r1")

        assert sent_request(mock_urlopen).method == "DELETE"


class TestWorkspaceAndUserPipelineVariables:
    def test_list_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_workspace_pipeline_variables(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/pipelines-config/variables"

    def test_create_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_workspace_pipeline_variable(workspace="ws", key="K", value="V")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"key": "K", "value": "V"}

    def test_get_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_workspace_pipeline_variable(workspace="ws", variable_uuid="v1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/pipelines-config/variables/v1"

    def test_update_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_workspace_pipeline_variable(workspace="ws", variable_uuid="v1", value="new")

        assert sent_request(mock_urlopen).method == "PUT"

    def test_delete_workspace(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_workspace_pipeline_variable(workspace="ws", variable_uuid="v1")

        assert sent_request(mock_urlopen).method == "DELETE"

    def test_list_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_user_pipeline_variables(selected_user="bob")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob/pipelines_config/variables"

    def test_create_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_user_pipeline_variable(selected_user="bob", key="K", value="V")

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"key": "K", "value": "V"}

    def test_get_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_user_pipeline_variable(selected_user="bob", variable_uuid="v1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/users/bob/pipelines_config/variables/v1"

    def test_update_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_user_pipeline_variable(selected_user="bob", variable_uuid="v1", value="new")

        assert sent_request(mock_urlopen).method == "PUT"

    def test_delete_user(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_user_pipeline_variable(selected_user="bob", variable_uuid="v1")

        assert sent_request(mock_urlopen).method == "DELETE"


class TestDeploymentVariables:
    def test_list(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({"values": []})

        client.list_deployment_variables(workspace="ws", repository="repo", environment_uuid="e1")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == ("/2.0/repositories/ws/repo/deployments_config/environments/e1/variables")

    def test_create(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.create_deployment_variable(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            key="K",
            value="V",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "POST"
        assert sent_body(mock_urlopen) == {"key": "K", "value": "V"}

    def test_update(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.update_deployment_variable(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            variable_uuid="v1",
            value="new",
        )

        request = sent_request(mock_urlopen)
        assert request.method == "PUT"
        assert sent_body(mock_urlopen) == {"value": "new"}

    def test_delete(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response(b"")

        client.delete_deployment_variable(
            workspace="ws",
            repository="repo",
            environment_uuid="e1",
            variable_uuid="v1",
        )

        assert sent_request(mock_urlopen).method == "DELETE"


class TestPipelinesOidc:
    def test_get_configuration(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipelines_oidc_configuration(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == (
            "/2.0/workspaces/ws/pipelines-config/identity/oidc/.well-known/openid-configuration"
        )

    def test_get_keys(self, client, mock_urlopen):
        mock_urlopen.return_value = make_response({})

        client.get_pipelines_oidc_keys(workspace="ws")

        path, _ = url_path_and_query(sent_request(mock_urlopen).full_url)
        assert path == "/2.0/workspaces/ws/pipelines-config/identity/oidc/keys.json"
