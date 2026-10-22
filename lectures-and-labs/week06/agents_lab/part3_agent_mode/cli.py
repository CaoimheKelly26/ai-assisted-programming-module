"""A small persistent command-line to-do list."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


TASKS_FILE = Path(
    os.environ.get("TODO_FILE", Path(__file__).with_name("tasks.json"))
)


def load_store() -> dict[str, Any]:
    if not TASKS_FILE.exists():
        return {"next_id": 1, "tasks": []}

    try:
        store = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"{TASKS_FILE} is not valid JSON") from error

    if (
        not isinstance(store, dict)
        or not isinstance(store.get("next_id"), int)
        or not isinstance(store.get("tasks"), list)
    ):
        raise ValueError(f"{TASKS_FILE} has an invalid to-do list format")

    for task in store["tasks"]:
        if (
            not isinstance(task, dict)
            or not isinstance(task.get("id"), int)
            or not isinstance(task.get("title"), str)
            or not isinstance(task.get("done"), bool)
        ):
            raise ValueError(f"{TASKS_FILE} has an invalid to-do list format")

    return store


def save_store(store: dict[str, Any]) -> None:
    TASKS_FILE.write_text(
        json.dumps(store, indent=2) + "\n",
        encoding="utf-8",
    )


def find_task(store: dict[str, Any], task_id: int) -> dict[str, Any] | None:
    return next(
        (task for task in store["tasks"] if task["id"] == task_id),
        None,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage your to-do list.")
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="add a task")
    add_parser.add_argument("title", help="what you need to do")

    commands.add_parser("list", help="list all tasks")

    done_parser = commands.add_parser("done", help="mark a task as done")
    done_parser.add_argument("task_id", type=int, help="the task ID")

    delete_parser = commands.add_parser("delete", help="delete a task")
    delete_parser.add_argument("task_id", type=int, help="the task ID")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        store = load_store()
        if args.command == "add":
            if not args.title.strip():
                print("error: task title cannot be empty", file=sys.stderr)
                return 2
            task_id = store["next_id"]
            store["tasks"].append(
                {"id": task_id, "title": args.title, "done": False}
            )
            store["next_id"] += 1
            save_store(store)
            print(f"Added task {task_id}: {args.title}")
            return 0

        if args.command == "list":
            if not store["tasks"]:
                print("No tasks yet.")
            for task in store["tasks"]:
                marker = "x" if task["done"] else " "
                print(f'{task["id"]}. [{marker}] {task["title"]}')
            return 0

        task = find_task(store, args.task_id)
        if task is None:
            print(f"error: no task with ID {args.task_id}", file=sys.stderr)
            return 1

        if args.command == "done":
            if not task["done"]:
                task["done"] = True
                save_store(store)
            print(f"Marked task {args.task_id} as done.")
        elif args.command == "delete":
            store["tasks"].remove(task)
            save_store(store)
            print(f"Deleted task {args.task_id}.")
        return 0
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
