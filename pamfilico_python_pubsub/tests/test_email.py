"""Unit tests for email sending."""

from unittest.mock import patch, MagicMock

from pamfilico_python_pubsub.email import send_email


def test_send_email_html_only():
    with patch("pamfilico_python_pubsub.email.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        send_email(to="user@example.com", subject="Hello", html_body="<p>Hi</p>")

        mock_server.sendmail.assert_called_once()
        args = mock_server.sendmail.call_args[0]
        assert args[1] == "user@example.com"
        assert "Hello" in args[2]
        assert "<p>Hi</p>" in args[2]


def test_send_email_with_text_body():
    with patch("pamfilico_python_pubsub.email.smtplib.SMTP") as mock_smtp:
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        send_email(
            to="user@example.com",
            subject="Test",
            html_body="<p>HTML</p>",
            text_body="Plain text",
        )

        args = mock_server.sendmail.call_args[0]
        assert "Plain text" in args[2]
        assert "<p>HTML</p>" in args[2]


def test_send_email_with_tls():
    with patch("pamfilico_python_pubsub.email.smtplib.SMTP") as mock_smtp, \
         patch("pamfilico_python_pubsub.email.SMTP_USE_TLS", True), \
         patch("pamfilico_python_pubsub.email.SMTP_USER", "user"), \
         patch("pamfilico_python_pubsub.email.SMTP_PASSWORD", "pass"):
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp.return_value.__exit__ = MagicMock(return_value=False)

        send_email(to="a@b.com", subject="S", html_body="<p>B</p>")

        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("user", "pass")
