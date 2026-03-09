"""Integration tests - require docker compose -f docker-compose.test.yml up."""

import os
import time

import pytest
import redis
import requests

from pamfilico_python_pubsub import publish_event

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6380")
QUEUE_NAME = os.environ.get("QUEUE_NAME", "test_queue")
API_URL = os.environ.get("PUBSUB_TEST_API_URL", "http://localhost:5001")
TEST_RESULT_KEY = os.environ.get("PUBSUB_TEST_RESULT_KEY", "test:echo:result")
TEST_ADD_RESULT_KEY = os.environ.get("PUBSUB_TEST_ADD_RESULT_KEY", "test:add_result")


def _redis_available() -> bool:
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        return True
    except Exception:
        return False


def _api_available() -> bool:
    try:
        resp = requests.get(f"{API_URL}/health", timeout=2)
        return resp.status_code == 200
    except Exception:
        return False


integration_required = pytest.mark.skipif(
    not _redis_available() or not _api_available(),
    reason="Redis and API required - run ./run-tests.sh or docker compose -f docker-compose.test.yml up",
)


@integration_required
def test_publish_via_api_and_verify_worker_processed():
    """Publish via API, wait for worker, verify result in Redis."""
    r = redis.from_url(REDIS_URL)
    r.delete(TEST_RESULT_KEY)

    message = f"integration-test-{time.time()}"
    resp = requests.post(
        f"{API_URL}/publish-test",
        json={"message": message},
        timeout=5,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"

    for _ in range(50):
        result = r.get(TEST_RESULT_KEY)
        if result is not None:
            if isinstance(result, bytes):
                result = result.decode()
            assert result == message
            return
        time.sleep(0.1)

    pytest.fail(f"Worker did not process task within 5s. Result key: {TEST_RESULT_KEY}")


@integration_required
def test_publish_directly_and_verify_worker_processed():
    """Publish via publish_event directly, verify worker processes."""
    r = redis.from_url(REDIS_URL)
    r.delete(TEST_RESULT_KEY)

    message = f"direct-publish-{time.time()}"
    publish_event("ECHO_MESSAGE", message=message)

    for _ in range(50):
        result = r.get(TEST_RESULT_KEY)
        if result is not None:
            if isinstance(result, bytes):
                result = result.decode()
            assert result == message
            return
        time.sleep(0.1)

    pytest.fail("Worker did not process direct publish within 5s")


@integration_required
def test_add_two_numbers_via_api():
    """Publish ADD_TWO_NUMBERS via API, verify worker computes and stores result."""
    r = redis.from_url(REDIS_URL)
    r.delete(TEST_ADD_RESULT_KEY)

    resp = requests.post(
        f"{API_URL}/publish-add-test",
        json={"a": 3, "b": 7},
        timeout=5,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "published"

    for _ in range(50):
        result = r.get(TEST_ADD_RESULT_KEY)
        if result is not None:
            if isinstance(result, bytes):
                result = result.decode()
            assert result == "10"
            return
        time.sleep(0.1)

    pytest.fail("Worker did not process ADD_TWO_NUMBERS within 5s")


@integration_required
def test_add_two_numbers_direct_publish():
    """Publish ADD_TWO_NUMBERS directly, verify worker computes result."""
    r = redis.from_url(REDIS_URL)
    r.delete(TEST_ADD_RESULT_KEY)

    publish_event("ADD_TWO_NUMBERS", a=100, b=23)

    for _ in range(50):
        result = r.get(TEST_ADD_RESULT_KEY)
        if result is not None:
            if isinstance(result, bytes):
                result = result.decode()
            assert result == "123"
            return
        time.sleep(0.1)

    pytest.fail("Worker did not process ADD_TWO_NUMBERS within 5s")
