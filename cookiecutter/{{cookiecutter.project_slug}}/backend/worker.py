"""Background worker process for {{ cookiecutter.project_name }}."""

import logging
import sys

from pamfilico_python_pubsub import run_worker

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
        stream=sys.stdout,
    )
    run_worker(handlers_module="app.events.handlers")
