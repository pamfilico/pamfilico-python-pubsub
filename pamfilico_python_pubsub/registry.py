"""Handler registry for task dispatch."""

_handlers: dict[str, callable] = {}


def handler(task_name: str):
    """Decorator to register a function as a handler for a task type."""

    def decorator(func):
        if task_name in _handlers:
            raise ValueError(f"Duplicate handler for {task_name}")
        _handlers[task_name] = func
        return func

    return decorator


def get_handler(task_name: str) -> callable:
    """Get the handler for a task type. Raises KeyError if not found."""
    if task_name not in _handlers:
        raise KeyError(f"No handler registered for task: {task_name}")
    return _handlers[task_name]


def list_handlers() -> list[str]:
    """List all registered task names."""
    return sorted(_handlers.keys())
