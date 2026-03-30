# {{ cookiecutter.project_name }} - Pub/Sub Worker

Background task processing powered by [pamfilico-python-pubsub](https://github.com/pamfilico/pamfilico-python-pubsub).

## Quick Start

```bash
# Start Redis + Mailpit + Worker
docker compose -f docker-compose.dev.yml up -d

# Publish a test task
python -c "
from app.events.publisher import publish_event
publish_event('SEND_TEST_EMAIL', email='test@localhost', message='Hello!')
"

# Check Mailpit UI at http://localhost:8025
```

## Adding Handlers

Create a new file in `backend/app/events/handlers/`:

```python
from pamfilico_python_pubsub import handler, send_email

@handler("MY_NEW_TASK")
def handle_my_task(email: str, **kwargs):
    send_email(to=email, subject="New Task", html_body="<p>Done!</p>")
```

Then import it in `backend/app/events/handlers/__init__.py`:

```python
from app.events.handlers import email, my_new_module  # noqa: F401
```

## Environment Variables

See `.env.example` for all available configuration.
