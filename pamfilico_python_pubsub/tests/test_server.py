"""Minimal Flask test server for integration tests. Exposes POST /publish-test."""

from flask import Flask, request

from pamfilico_python_pubsub import publish_event

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


@app.route("/publish-test", methods=["POST"])
def publish_test():
    """Publish ECHO_MESSAGE task. Accepts JSON {message: str} or form message=."""
    if request.is_json:
        message = request.json.get("message", "hello")
    else:
        message = request.form.get("message", "hello")
    publish_event("ECHO_MESSAGE", message=message)
    return {"status": "published", "message": message}


@app.route("/publish-add-test", methods=["POST"])
def publish_add_test():
    """Publish ADD_TWO_NUMBERS task. Accepts JSON {a: int, b: int}."""
    if request.is_json:
        a = request.json.get("a", 0)
        b = request.json.get("b", 0)
    else:
        a = int(request.form.get("a", 0))
        b = int(request.form.get("b", 0))
    publish_event("ADD_TWO_NUMBERS", a=a, b=b)
    return {"status": "published", "a": a, "b": b}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
