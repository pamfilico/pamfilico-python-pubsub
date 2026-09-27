"""Pamfilico Python Pubsub - Redis LIST pub/sub for background task processing."""

from importlib.metadata import PackageNotFoundError, version as _dist_version

try:
    #: Read from the INSTALLED distribution, never hardcoded — a literal here is
    #: one more thing that can drift from pyproject.toml and from the git tag,
    #: which is the exact failure this is meant to make visible. Consumers pin by
    #: tag and can assert on this to prove which build they actually got.
    __version__ = _dist_version("pamfilico-python-pubsub")
except PackageNotFoundError:  # running from a source tree, not installed
    __version__ = "0.0.0.dev0"

from pamfilico_python_pubsub.publisher import publish_event
from pamfilico_python_pubsub.registry import handler, get_handler, list_handlers
from pamfilico_python_pubsub.worker import run_worker
from pamfilico_python_pubsub.email import send_email

__all__ = [
    "__version__",
    "publish_event",
    "handler",
    "get_handler",
    "list_handlers",
    "run_worker",
    "send_email",
]
