"""Publisher for background task queue."""

import json
import os

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
QUEUE_NAME = os.environ.get("QUEUE_NAME", "app_queue")

redis_client = redis.from_url(REDIS_URL)


def publish_event(event_name: str, **kwargs) -> None:
    """Publish a task to the background worker queue.

    All data needed to execute the task MUST be passed via kwargs.
    Do NOT pass database IDs that require the worker to query the DB.
    Resolve all data at publish time.
    """
    task = {
        "task_name": event_name,
        "kwargs": kwargs,
        "retry": [],
        "status": "pending",
    }
    redis_client.rpush(QUEUE_NAME, json.dumps(task))
