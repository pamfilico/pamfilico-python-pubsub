"""Worker process for background task consumption."""

import importlib
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timezone

import redis

from pamfilico_python_pubsub.publisher import QUEUE_NAME, REDIS_URL, redis_client
from pamfilico_python_pubsub import registry

DLQ_NAME = os.environ.get("DEAD_LETTER_QUEUE", f"{QUEUE_NAME}_dlq")
MAX_RETRIES = int(os.environ.get("MAX_RETRIES", "3"))

logger = logging.getLogger("worker")


def run_worker(handlers_module: str | None = None) -> None:
    """Run the worker loop. Optionally import handlers from the given module(s) first.

    handlers_module can be a single module path or comma-separated list:
        "myapp.handlers" or "myapp.handlers,myapp.email_handlers"
    """
    if handlers_module:
        for mod in handlers_module.split(","):
            mod = mod.strip()
            if mod:
                importlib.import_module(mod)
    logger.info(f"Worker started. Queue={QUEUE_NAME}, DLQ={DLQ_NAME}, MaxRetries={MAX_RETRIES}")
    while True:
        result = redis_client.blpop(QUEUE_NAME, timeout=1)
        if result is None:
            continue

        raw = result[1]
        task = json.loads(raw)
        task_name = task["task_name"]
        kwargs = task.get("kwargs", {})
        retries = task.get("retry", [])

        logger.info(f"Processing: {task_name} (retries: {len(retries)})")

        try:
            handler_fn = registry.get_handler(task_name)
            handler_fn(**kwargs)
            logger.info(f"Success: {task_name}")
        except KeyError as e:
            logger.error(f"Unknown task: {task_name} - {e}")
            task["retry"] = retries + [str(e)]
            task["status"] = "dead_letter"
            task["moved_to_dlq_at"] = datetime.now(timezone.utc).isoformat()
            redis_client.rpush(DLQ_NAME, json.dumps(task))
        except Exception as e:
            error_msg = f"{e}\n{traceback.format_exc()}"
            retries.append(error_msg)
            task["retry"] = retries
            task["status"] = "failed"

            if len(retries) >= MAX_RETRIES:
                task["status"] = "dead_letter"
                task["moved_to_dlq_at"] = datetime.now(timezone.utc).isoformat()
                redis_client.rpush(DLQ_NAME, json.dumps(task))
                logger.error(f"DLQ: {task_name} after {len(retries)} retries")
            else:
                redis_client.rpush(QUEUE_NAME, json.dumps(task))
                logger.warning(f"Retry {len(retries)}/{MAX_RETRIES}: {task_name}")


def main() -> None:
    """CLI entry point for pubsub-worker script."""
    import argparse

    parser = argparse.ArgumentParser(description="Run the pubsub worker")
    parser.add_argument(
        "--handlers",
        type=str,
        default=None,
        help="Python module path to import for handler registration (e.g. myapp.events.handlers)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )
    run_worker(handlers_module=args.handlers)


if __name__ == "__main__":
    main()
