"""Unit tests for registry."""

import pytest

from pamfilico_python_pubsub.registry import get_handler, handler, list_handlers


def test_handler_registers_function():
    @handler("TEST_TASK")
    def my_handler(x: int, **kwargs):
        return x * 2

    assert get_handler("TEST_TASK") is my_handler
    assert "TEST_TASK" in list_handlers()


def test_get_handler_raises_for_unknown_task():
    with pytest.raises(KeyError, match="No handler registered for task: UNKNOWN"):
        get_handler("UNKNOWN")


def test_duplicate_handler_raises():
    @handler("DUP_TASK")
    def first():
        pass

    with pytest.raises(ValueError, match="Duplicate handler for DUP_TASK"):

        @handler("DUP_TASK")
        def second():
            pass
