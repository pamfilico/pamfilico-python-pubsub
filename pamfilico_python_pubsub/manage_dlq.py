"""Dead Letter Queue management CLI."""

import argparse
import json
import os

import redis

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
QUEUE_NAME = os.environ.get("QUEUE_NAME", "app_queue")
DLQ_NAME = os.environ.get("DEAD_LETTER_QUEUE", f"{QUEUE_NAME}_dlq")

r = redis.from_url(REDIS_URL)


def cmd_list(args):
    """List all tasks in the DLQ."""
    tasks = r.lrange(DLQ_NAME, 0, -1)
    if not tasks:
        print("DLQ is empty.")
        return
    for i, raw in enumerate(tasks):
        task = json.loads(raw)
        print(f"[{i}] {task['task_name']} | retries: {len(task.get('retry', []))} | dlq_at: {task.get('moved_to_dlq_at', 'N/A')}")


def cmd_view(args):
    """View details of a specific DLQ task."""
    tasks = r.lrange(DLQ_NAME, 0, -1)
    if args.index >= len(tasks):
        print(f"Index {args.index} out of range (DLQ has {len(tasks)} tasks).")
        return
    task = json.loads(tasks[args.index])
    print(json.dumps(task, indent=2))


def cmd_replay(args):
    """Replay a single task from DLQ back to the main queue."""
    tasks = r.lrange(DLQ_NAME, 0, -1)
    if args.index >= len(tasks):
        print(f"Index {args.index} out of range.")
        return
    task = json.loads(tasks[args.index])
    task["retry"] = []
    task["status"] = "pending"
    task.pop("moved_to_dlq_at", None)
    r.rpush(QUEUE_NAME, json.dumps(task))
    r.lrem(DLQ_NAME, 1, tasks[args.index])
    print(f"Replayed: {task['task_name']}")


def cmd_replay_all(args):
    """Replay all tasks from DLQ back to the main queue."""
    tasks = r.lrange(DLQ_NAME, 0, -1)
    if not tasks:
        print("DLQ is empty.")
        return
    for raw in tasks:
        task = json.loads(raw)
        task["retry"] = []
        task["status"] = "pending"
        task.pop("moved_to_dlq_at", None)
        r.rpush(QUEUE_NAME, json.dumps(task))
    r.delete(DLQ_NAME)
    print(f"Replayed {len(tasks)} tasks.")


def cmd_stats(args):
    """Show statistics by task type."""
    tasks = r.lrange(DLQ_NAME, 0, -1)
    if not tasks:
        print("DLQ is empty.")
        return
    stats = {}
    for raw in tasks:
        task = json.loads(raw)
        name = task["task_name"]
        stats[name] = stats.get(name, 0) + 1
    print(f"Total: {len(tasks)}")
    for name, count in sorted(stats.items()):
        print(f"  {name}: {count}")


def cmd_clear(args):
    """Clear the entire DLQ (permanent deletion)."""
    count = r.llen(DLQ_NAME)
    if count == 0:
        print("DLQ is already empty.")
        return
    if args.yes:
        r.delete(DLQ_NAME)
        print(f"Cleared {count} tasks.")
    else:
        confirm = input(f"Delete {count} tasks from DLQ? [y/N]: ")
        if confirm.lower() == "y":
            r.delete(DLQ_NAME)
            print(f"Cleared {count} tasks.")
        else:
            print("Cancelled.")


def main():
    parser = argparse.ArgumentParser(description="Dead Letter Queue Management")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="List all DLQ tasks")

    p_view = sub.add_parser("view", help="View task details")
    p_view.add_argument("index", type=int)

    p_replay = sub.add_parser("replay", help="Replay a single task")
    p_replay.add_argument("index", type=int)

    sub.add_parser("replay-all", help="Replay all tasks")
    sub.add_parser("stats", help="Show stats by task type")

    p_clear = sub.add_parser("clear", help="Clear the DLQ")
    p_clear.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")

    args = parser.parse_args()
    commands = {
        "list": cmd_list,
        "view": cmd_view,
        "replay": cmd_replay,
        "replay-all": cmd_replay_all,
        "stats": cmd_stats,
        "clear": cmd_clear,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
