"""Demo handlers for integration testing. ECHO_MESSAGE and ADD_TWO_NUMBERS write to Redis."""

import os

import redis

from pamfilico_python_pubsub.registry import handler

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
TEST_RESULT_KEY = os.environ.get("PUBSUB_TEST_RESULT_KEY", "test:echo:result")
TEST_ADD_RESULT_KEY = os.environ.get("PUBSUB_TEST_ADD_RESULT_KEY", "test:add_result")

_redis = redis.from_url(REDIS_URL)


@handler("ECHO_MESSAGE")
def handle_echo_message(message: str, **kwargs) -> None:
    """Store the message in Redis for integration test verification."""
    _redis.set(TEST_RESULT_KEY, message)


@handler("ADD_TWO_NUMBERS")
def handle_add_two_numbers(a: int, b: int, **kwargs) -> None:
    """Add two numbers and store result in Redis for integration test verification."""
    _redis.set(TEST_ADD_RESULT_KEY, str(a + b))
