"""Unit tests for publisher."""

import json
from unittest.mock import patch

from pamfilico_python_pubsub.publisher import publish_event


def test_publish_event_pushes_to_redis():
    with patch("pamfilico_python_pubsub.publisher.redis_client") as mock_redis:
        publish_event("SEND_TEST_EMAIL", email="test@example.com", message="hello")

        mock_redis.rpush.assert_called_once()
        args = mock_redis.rpush.call_args
        queue_name = args[0][0]
        task = json.loads(args[0][1])

        assert task["task_name"] == "SEND_TEST_EMAIL"
        assert task["kwargs"]["email"] == "test@example.com"
        assert task["kwargs"]["message"] == "hello"
        assert task["retry"] == []
        assert task["status"] == "pending"
