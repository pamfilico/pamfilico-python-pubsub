"""Unit tests for DLQ management CLI."""

import json
from unittest.mock import patch, MagicMock
from argparse import Namespace

from pamfilico_python_pubsub.manage_dlq import cmd_list, cmd_view, cmd_replay, cmd_replay_all, cmd_stats, cmd_clear


def _make_task(name="SEND_TEST_EMAIL", retries=3):
    return json.dumps({
        "task_name": name,
        "kwargs": {"email": "t@b.com"},
        "retry": [f"err{i}" for i in range(retries)],
        "status": "dead_letter",
        "moved_to_dlq_at": "2025-01-01T00:00:00+00:00",
    }).encode()


def test_cmd_list_empty(capsys):
    with patch("pamfilico_python_pubsub.manage_dlq.r") as mock_r:
        mock_r.lrange.return_value = []
        cmd_list(Namespace())
        assert "empty" in capsys.readouterr().out.lower()


def test_cmd_list_with_tasks(capsys):
    with patch("pamfilico_python_pubsub.manage_dlq.r") as mock_r:
        mock_r.lrange.return_value = [_make_task(), _make_task("SEND_WELCOME_EMAIL")]
        cmd_list(Namespace())
        out = capsys.readouterr().out
        assert "SEND_TEST_EMAIL" in out
        assert "SEND_WELCOME_EMAIL" in out
        assert "[0]" in out
        assert "[1]" in out


def test_cmd_view(capsys):
    with patch("pamfilico_python_pubsub.manage_dlq.r") as mock_r:
        mock_r.lrange.return_value = [_make_task()]
        cmd_view(Namespace(index=0))
        out = capsys.readouterr().out
        assert "SEND_TEST_EMAIL" in out
        assert "t@b.com" in out


def test_cmd_replay():
    with patch("pamfilico_python_pubsub.manage_dlq.r") as mock_r:
        task_bytes = _make_task()
        mock_r.lrange.return_value = [task_bytes]
        cmd_replay(Namespace(index=0))
        mock_r.rpush.assert_called_once()
        replayed = json.loads(mock_r.rpush.call_args[0][1])
        assert replayed["status"] == "pending"
        assert replayed["retry"] == []
        assert "moved_to_dlq_at" not in replayed
        mock_r.lrem.assert_called_once()


def test_cmd_replay_all():
    with patch("pamfilico_python_pubsub.manage_dlq.r") as mock_r:
        mock_r.lrange.return_value = [_make_task(), _make_task("OTHER")]
        cmd_replay_all(Namespace())
        assert mock_r.rpush.call_count == 2
        mock_r.delete.assert_called_once()


def test_cmd_stats(capsys):
    with patch("pamfilico_python_pubsub.manage_dlq.r") as mock_r:
        mock_r.lrange.return_value = [_make_task(), _make_task(), _make_task("OTHER")]
        cmd_stats(Namespace())
        out = capsys.readouterr().out
        assert "Total: 3" in out
        assert "SEND_TEST_EMAIL: 2" in out
        assert "OTHER: 1" in out


def test_cmd_clear_with_yes():
    with patch("pamfilico_python_pubsub.manage_dlq.r") as mock_r:
        mock_r.llen.return_value = 5
        cmd_clear(Namespace(yes=True))
        mock_r.delete.assert_called_once()
