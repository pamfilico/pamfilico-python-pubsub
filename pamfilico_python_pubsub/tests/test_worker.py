"""Unit tests for worker."""

import json
from unittest.mock import MagicMock, patch

from pamfilico_python_pubsub.registry import handler
from pamfilico_python_pubsub.worker import run_worker


def test_worker_processes_task():
    task = json.dumps({
        "task_name": "SEND_TEST_EMAIL",
        "kwargs": {"email": "test@example.com", "message": "hello"},
        "retry": [],
        "status": "pending",
    })

    call_count = 0

    def fake_blpop(queue, timeout):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return (queue, task)
        raise KeyboardInterrupt

    mock_handler = MagicMock()
    with patch("pamfilico_python_pubsub.worker.redis_client") as mock_redis, \
         patch("pamfilico_python_pubsub.worker.registry") as mock_registry:
        mock_redis.blpop.side_effect = fake_blpop
        mock_registry.get_handler.return_value = mock_handler

        try:
            run_worker()
        except KeyboardInterrupt:
            pass

        mock_registry.get_handler.assert_called_with("SEND_TEST_EMAIL")
        mock_handler.assert_called_once_with(email="test@example.com", message="hello")


def test_worker_processes_add_two_numbers():
    task = json.dumps({
        "task_name": "ADD_TWO_NUMBERS",
        "kwargs": {"a": 5, "b": 3},
        "retry": [],
        "status": "pending",
    })

    call_count = 0

    def fake_blpop(queue, timeout):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return (queue, task)
        raise KeyboardInterrupt

    mock_handler = MagicMock()
    with patch("pamfilico_python_pubsub.worker.redis_client") as mock_redis, \
         patch("pamfilico_python_pubsub.worker.registry") as mock_registry:
        mock_redis.blpop.side_effect = fake_blpop
        mock_registry.get_handler.return_value = mock_handler

        try:
            run_worker()
        except KeyboardInterrupt:
            pass

        mock_registry.get_handler.assert_called_with("ADD_TWO_NUMBERS")
        mock_handler.assert_called_once_with(a=5, b=3)


def test_worker_requeues_on_failure():
    @handler("FAILING_TASK")
    def failing_handler(**kwargs):
        raise Exception("SMTP down")

    task = json.dumps({
        "task_name": "FAILING_TASK",
        "kwargs": {},
        "retry": [],
        "status": "pending",
    })

    call_count = 0

    def fake_blpop(queue, timeout):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return (queue, task)
        raise KeyboardInterrupt

    with patch("pamfilico_python_pubsub.worker.redis_client") as mock_redis, \
         patch("pamfilico_python_pubsub.worker.MAX_RETRIES", 3):
        mock_redis.blpop.side_effect = fake_blpop

        try:
            run_worker()
        except KeyboardInterrupt:
            pass

        mock_redis.rpush.assert_called_once()
        args = mock_redis.rpush.call_args[0]
        requeued = json.loads(args[1])
        assert requeued["status"] == "failed"
        assert len(requeued["retry"]) == 1
        assert "SMTP down" in requeued["retry"][0]
