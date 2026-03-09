# Pamfilico Python Pubsub

Redis LIST pub/sub for background task processing. Publisher–Worker pattern with handler decorator, retries, and dead letter queue. Same pattern used in TravelSuite (BoatFast, TourFast, CarFast) and other Pamfilico apps.

## Installation

```bash
poetry add git+https://github.com/pamfilico/pamfilico-python-pubsub.git
```

---

## Quick Start

### 1. Define event handlers

Create `app/events/handlers/email.py`:

```python
from pamfilico_python_pubsub import handler
from app.notifications.email import send_email  # your SMTP helper


@handler("SEND_WELCOME_EMAIL")
def handle_welcome_email(email: str, name: str, **kwargs):
    send_email(
        to=email,
        subject="Welcome!",
        html_body=f"<h1>Welcome, {name}!</h1><p>Your account is ready.</p>",
    )


@handler("SEND_WAITLIST_EMAIL")
def handle_waitlist(email: str, **kwargs):
    send_email(
        to=email,
        subject="You're on the Waitlist!",
        html_body="<p>Thanks for signing up. We'll notify you when your spot opens.</p>",
    )


@handler("SEND_BOOKING_REQUEST_CUSTOMER_EMAIL")
def handle_booking_customer(email: str, subject: str, html_body: str, text_body: str = "", **kwargs):
    send_email(to=email, subject=subject, html_body=html_body, text_body=text_body)
```

Create `app/events/handlers/__init__.py` so handlers register at import:

```python
from app.events.handlers import email  # noqa: F401
```

### 2. Publish from API endpoints

Resolve **all data at publish time**. Workers are stateless — no DB access.

```python
from flask import request
from pamfilico_python_pubsub import publish_event


# Waitlist signup
@api.route("/waitlist", methods=["POST"])
def post_waitlist():
    email = request.json.get("email")
    # ... validate, save to DB ...
    publish_event("SEND_WAITLIST_EMAIL", email=email)
    return standard_response(data={"status": "signed up"}, ui_message="You're on the list!")


# Welcome email after signup
@api.route("/users", methods=["POST"])
def create_user():
    user = User.create(...)
    publish_event("SEND_WELCOME_EMAIL", email=user.email, name=user.name)
    return standard_response(data=user.to_dict(), status_code=201)


# Booking confirmation — render HTML in API, pass to worker
@api.route("/bookings", methods=["POST"])
def create_booking():
    booking = Booking.create(...)
    customer = db.session.get(User, booking.customer_id)
    html = render_template("emails/booking_confirm.html", booking=booking, customer=customer)
    publish_event(
        "SEND_BOOKING_REQUEST_CUSTOMER_EMAIL",
        email=customer.email,
        subject=f"Booking {booking.ref} Confirmed",
        html_body=html,
        text_body=f"Your booking {booking.ref} is confirmed.",
    )
    return standard_response(data=booking.to_dict(), status_code=201)
```

### 3. Run the worker

**Option A: CLI** (handlers in separate package)

```bash
export REDIS_URL=redis://localhost:6379
export QUEUE_NAME=myapp_queue
pubsub-worker --handlers app.events.handlers
```

**Option B: Custom `worker.py`** (handlers in your app)

```python
# worker.py — at project root
from app.events.handlers import email  # noqa: F401  # registers handlers
from pamfilico_python_pubsub import run_worker

if __name__ == "__main__":
    run_worker()
```

Run it:

```bash
export REDIS_URL=redis://localhost:6379
export QUEUE_NAME=myapp_queue
python worker.py
```

**Option C: Docker**

```dockerfile
# Dockerfile.worker
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install poetry && poetry install --no-interaction
CMD ["python", "worker.py"]
```

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  backend:
    build: ./backend
    environment:
      REDIS_URL: redis://redis:6379
      QUEUE_NAME: myapp_queue_dev

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.worker
    environment:
      REDIS_URL: redis://redis:6379
      QUEUE_NAME: myapp_queue_dev
    depends_on:
      - redis
```

---

## Project structure (CarFast/BoatFast style)

```
backend/
├── worker.py                    # Entry point: imports handlers, runs run_worker()
├── app/
│   ├── events/
│   │   ├── __init__.py         # from app.events import handlers  # noqa
│   │   └── handlers/
│   │       ├── __init__.py     # from app.events.handlers import email  # noqa
│   │       └── email.py        # @handler("SEND_*") functions
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py         # publish_event("SEND_WELCOME_EMAIL", ...)
│   │       └── waitlist.py     # publish_event("SEND_WAITLIST_EMAIL", ...)
│   └── notifications/
│       └── email.py            # send_email(to, subject, html_body)
```

---

## API reference

| Function / decorator   | Description                          |
|-----------------------|--------------------------------------|
| `publish_event(name, **kwargs)` | Enqueue a task                |
| `@handler(task_name)`  | Register a handler for a task type   |
| `get_handler(name)`    | Look up handler (raises `KeyError`)  |
| `list_handlers()`      | List registered task names           |
| `run_worker(handlers_module=None)` | Main worker loop (BLPOP)      |

---

## Environment variables

| Variable            | Default                 | Description           |
|---------------------|-------------------------|-----------------------|
| `REDIS_URL`         | `redis://localhost:6379`| Redis connection      |
| `QUEUE_NAME`        | `app_queue`             | Main queue name       |
| `DEAD_LETTER_QUEUE`  | `{QUEUE_NAME}_dlq`     | Dead letter queue     |
| `MAX_RETRIES`       | `3`                     | Retries before DLQ    |

---

## Critical rule: resolve data at publish time

```python
# BAD — worker would need to query DB
publish_event("SEND_BOOKING_EMAIL", booking_id=booking.id)

# GOOD — all data passed in
publish_event(
    "SEND_BOOKING_EMAIL",
    email=customer.email,
    subject="Booking Confirmed",
    html_body=rendered_html,
    text_body=plain_text,
)
```

Workers must not import database models or open sessions.

---

## Testing

```bash
poetry run pytest -v              # Unit tests (mocked Redis)
./run-tests.sh                    # Integration: Docker Redis + API + Worker
```

---

## License

MIT – see [LICENSE](LICENSE)
