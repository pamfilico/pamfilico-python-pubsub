"""Hello world handler — simplest possible working example."""

import logging

from pamfilico_python_pubsub.registry import handler

logger = logging.getLogger(__name__)


@handler("HELLO_WORLD")
def handle_hello_world(name: str = "World", **kwargs):
    """Log a greeting. Use this as a smoke test for the worker pipeline."""
    logger.info(f"Hello, {name}!")
