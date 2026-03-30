"""Email event handlers. Import this module to register all email handlers."""

from pamfilico_python_pubsub.registry import handler
from pamfilico_python_pubsub.email import send_email


@handler("SEND_WELCOME_EMAIL")
def handle_welcome_email(email: str, name: str, **kwargs):
    send_email(
        to=email,
        subject="Welcome!",
        html_body=f"<h1>Welcome, {name}!</h1><p>Your account is ready.</p>",
    )


@handler("SEND_PASSWORD_RESET_EMAIL")
def handle_password_reset(email: str, reset_link: str, **kwargs):
    send_email(
        to=email,
        subject="Password Reset",
        html_body=f'<p>Click <a href="{reset_link}">here</a> to reset your password.</p>',
    )


@handler("SEND_MAGIC_LINK_EMAIL")
def handle_magic_link(email: str, magic_link: str, **kwargs):
    send_email(
        to=email,
        subject="Your Sign-In Link",
        html_body=f'<p>Click <a href="{magic_link}">here</a> to sign in.</p>',
    )


@handler("SEND_BOOKING_REQUEST_CUSTOMER_EMAIL")
def handle_booking_customer(email: str, subject: str, html_body: str, text_body: str = "", **kwargs):
    send_email(to=email, subject=subject, html_body=html_body, text_body=text_body)


@handler("SEND_INVITE_EMAIL")
def handle_invite(email: str, subject: str, html_body: str, text_body: str = "", **kwargs):
    send_email(to=email, subject=subject, html_body=html_body, text_body=text_body)


@handler("SEND_WAITLIST_EMAIL")
def handle_waitlist(email: str, **kwargs):
    send_email(
        to=email,
        subject="You're on the Waitlist!",
        html_body="<p>Thanks for signing up. We'll notify you when your spot opens.</p>",
    )


@handler("SEND_TEST_EMAIL")
def handle_test_email(email: str, message: str = "Test email from worker", **kwargs):
    send_email(to=email, subject="Test Email", html_body=f"<p>{message}</p>")
