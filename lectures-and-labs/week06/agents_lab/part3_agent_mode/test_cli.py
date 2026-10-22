import json
import os
import subprocess
import sys
from pathlib import Path

import cli


def test_add_list_done_and_delete_persist_between_runs(
    tmp_path: Path, monkeypatch
) -> None:
    tasks_file = tmp_path / "tasks.json"
    monkeypatch.setattr(cli, "TASKS_FILE", tasks_file)

    assert cli.main(["add", "buy milk"]) == 0
    assert cli.main(["add", "walk the dog"]) == 0
    assert cli.main(["done", "1"]) == 0

    assert cli.main(["list"]) == 0

    store = json.loads(tasks_file.read_text(encoding="utf-8"))
    assert store == {
        "next_id": 3,
        "tasks": [
            {"id": 1, "title": "buy milk", "done": True},
            {"id": 2, "title": "walk the dog", "done": False},
        ],
    }

    assert cli.main(["delete", "2"]) == 0
    assert json.loads(tasks_file.read_text(encoding="utf-8")) == {
        "next_id": 3,
        "tasks": [{"id": 1, "title": "buy milk", "done": True}],
    }


def test_cli_commands_share_saved_tasks_across_processes(tmp_path: Path) -> None:
    cli_path = Path(cli.__file__)
    tasks_file = tmp_path / "tasks.json"

    add_result = subprocess.run(
        [sys.executable, str(cli_path), "add", "buy milk"],
        capture_output=True,
        text=True,
        env={**os.environ, "TODO_FILE": str(tasks_file)},
        check=False,
    )
    list_result = subprocess.run(
        [sys.executable, str(cli_path), "list"],
        capture_output=True,
        text=True,
        env={**os.environ, "TODO_FILE": str(tasks_file)},
        check=False,
    )

    assert add_result.returncode == 0
    assert list_result.returncode == 0
    assert "buy milk" in list_result.stdout


def test_empty_list_and_unknown_task_report_useful_output(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(cli, "TASKS_FILE", tmp_path / "tasks.json")

    assert cli.main(["list"]) == 0
    assert "No tasks yet." in capsys.readouterr().out
    assert cli.main(["done", "42"]) == 1
    assert "no task with ID 42" in capsys.readouterr().err


def test_empty_title_is_rejected(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "TASKS_FILE", tmp_path / "tasks.json")

    assert cli.main(["add", "   "]) == 2
    assert "task title cannot be empty" in capsys.readouterr().err
    assert not (tmp_path / "tasks.json").exists()
