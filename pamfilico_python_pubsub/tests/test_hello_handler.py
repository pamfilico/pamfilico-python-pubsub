"""Unit tests for hello world handler."""

import sys

from pamfilico_python_pubsub.registry import get_handler


def _load_handlers():
    from pamfilico_python_pubsub import registry
    registry._handlers.clear()
    sys.modules.pop("pamfilico_python_pubsub.hello_handler", None)
    import pamfilico_python_pubsub.hello_handler  # noqa: F401


def test_hello_world_handler_registered():
    _load_handlers()
    handler = get_handler("HELLO_WORLD")
    assert handler is not None


def test_hello_world_handler_runs():
    _load_handlers()
    handler = get_handler("HELLO_WORLD")
    handler(name="Test")  # Should not raise
