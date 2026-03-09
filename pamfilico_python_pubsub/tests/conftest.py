"""Shared pytest fixtures."""

import pytest


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset handler registry between tests to avoid cross-test pollution."""
    from pamfilico_python_pubsub import registry

    registry._handlers.clear()
    yield
    registry._handlers.clear()
