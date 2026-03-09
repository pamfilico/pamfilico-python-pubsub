# Pamfilico Python Pubsub

Redis LIST pub/sub for background task processing. Publisher–Worker pattern with handler decorator, retries, and dead letter queue.

## Installation

```bash
poetry add git+https://github.com/pamfilico/pamfilico-python-pubsub.git
```

## Quick Start

### 1. Define handlers

```python
from pamfilico_python_pubsub import handler

@handler("SEND_WELCOME_EMAIL")
def handle_welcome_email(email: str, name: str, **kwargs):
    send_email(to=email, subject="Welcome!", html_body=f"<h1>Hi {name}!</h1>")
```

### 2. Publish tasks

```python
from pamfilico_python_pubsub import publish_event

publish_event("SEND_WELCOME_EMAIL", email=user.email, name=user.name)
```

### 3. Run the worker

```bash
pubsub-worker --handlers myapp.events.handlers
```

## Testing

```bash
poetry run pytest -v                    # Unit tests only
./run-tests.sh                          # Full suite with Docker
```

## License

MIT – see [LICENSE](LICENSE)
