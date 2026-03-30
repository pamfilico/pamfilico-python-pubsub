"""Unit tests for email handlers."""

import importlib
import sys
from unittest.mock import patch

from pamfilico_python_pubsub.registry import get_handler


def _load_handlers():
    """Force re-registration of email handlers."""
    from pamfilico_python_pubsub import registry
    registry._handlers.clear()
    # Remove from sys.modules so import executes decorators again
    sys.modules.pop("pamfilico_python_pubsub.email_handlers", None)
    import pamfilico_python_pubsub.email_handlers  # noqa: F401


def test_welcome_email_handler():
    _load_handlers()
    handler = get_handler("SEND_WELCOME_EMAIL")
    with patch("pamfilico_python_pubsub.email_handlers.send_email") as mock_send:
        handler(email="user@example.com", name="Alice")
        mock_send.assert_called_once()
        assert "Alice" in mock_send.call_args[1]["html_body"]


def test_password_reset_handler():
    _load_handlers()
    handler = get_handler("SEND_PASSWORD_RESET_EMAIL")
    with patch("pamfilico_python_pubsub.email_handlers.send_email") as mock_send:
        handler(email="user@example.com", reset_link="https://example.com/reset/abc")
        mock_send.assert_called_once()
        assert "reset/abc" in mock_send.call_args[1]["html_body"]


def test_magic_link_handler():
    _load_handlers()
    handler = get_handler("SEND_MAGIC_LINK_EMAIL")
    with patch("pamfilico_python_pubsub.email_handlers.send_email") as mock_send:
        handler(email="user@example.com", magic_link="https://example.com/auth/verify?token=xyz")
        mock_send.assert_called_once()
        assert "token=xyz" in mock_send.call_args[1]["html_body"]


def test_booking_handler():
    _load_handlers()
    handler = get_handler("SEND_BOOKING_REQUEST_CUSTOMER_EMAIL")
    with patch("pamfilico_python_pubsub.email_handlers.send_email") as mock_send:
        handler(email="c@b.com", subject="Booking", html_body="<p>Confirmed</p>", text_body="Confirmed")
        mock_send.assert_called_once_with(to="c@b.com", subject="Booking", html_body="<p>Confirmed</p>", text_body="Confirmed")


def test_invite_handler():
    _load_handlers()
    handler = get_handler("SEND_INVITE_EMAIL")
    with patch("pamfilico_python_pubsub.email_handlers.send_email") as mock_send:
        handler(email="i@b.com", subject="Invite", html_body="<p>Join</p>")
        mock_send.assert_called_once()


def test_waitlist_handler():
    _load_handlers()
    handler = get_handler("SEND_WAITLIST_EMAIL")
    with patch("pamfilico_python_pubsub.email_handlers.send_email") as mock_send:
        handler(email="w@b.com")
        mock_send.assert_called_once()
        assert "Waitlist" in mock_send.call_args[1]["subject"]


def test_test_email_handler():
    _load_handlers()
    handler = get_handler("SEND_TEST_EMAIL")
    with patch("pamfilico_python_pubsub.email_handlers.send_email") as mock_send:
        handler(email="t@b.com", message="Hello test")
        mock_send.assert_called_once()
        assert "Hello test" in mock_send.call_args[1]["html_body"]
