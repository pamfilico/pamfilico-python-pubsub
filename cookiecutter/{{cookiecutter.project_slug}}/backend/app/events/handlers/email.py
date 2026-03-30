"""Email event handlers for {{ cookiecutter.project_name }}."""

from pamfilico_python_pubsub import handler, send_email


@handler("SEND_WELCOME_EMAIL")
def handle_welcome_email(email: str, name: str, **kwargs):
    send_email(
        to=email,
        subject="Welcome!",
        html_body=f"<h1>Welcome, {name}!</h1><p>Your account is ready.</p>",
    )


@handler("SEND_TEST_EMAIL")
def handle_test_email(email: str, message: str = "Test email", **kwargs):
    send_email(to=email, subject="Test Email", html_body=f"<p>{message}</p>")
