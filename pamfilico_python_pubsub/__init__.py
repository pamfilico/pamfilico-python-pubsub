"""Pamfilico Python Pubsub - Redis LIST pub/sub for background task processing."""

__version__ = "0.2.0"

from pamfilico_python_pubsub.publisher import publish_event
from pamfilico_python_pubsub.registry import handler, get_handler, list_handlers
from pamfilico_python_pubsub.worker import run_worker
from pamfilico_python_pubsub.email import send_email

__all__ = [
    "publish_event",
    "handler",
    "get_handler",
    "list_handlers",
    "run_worker",
    "send_email",
]
