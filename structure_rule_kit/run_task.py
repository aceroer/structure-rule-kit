from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .parser import extract_section, replace_section
from .status_update import update_status
from .verify_log import append_verify_log


def run_agent_task(
    task_file: str,
    command: str = "",
    path: str = ".",
    update_project_status: bool = False,
    timeout: int = 120,
) -> dict:
    root = Path(path)
    task_path = Path(task_file)
    if not task_path.is_absolute():
        task_path = root / task_path
    if not task_path.exists():
        raise FileNotFoundError(str(task_path))

    text = task_path.read_text(encoding="utf-8")
    task_title = text.splitlines()[0].lstrip("# ").strip() if text.splitlines() else task_path.name
    actual_command = command.strip() or extract_section(text, "Required Checks").strip()
    if actual_command.startswith("Follow "):
        actual_command = ""

    verify = append_verify_log(
        str(root),
        command=actual_command,
        run=bool(actual_command),
        timeout=timeout,
        notes=f"Task: {task_path}",
    )
    result = verify["result"] or "not run"
    stamp = datetime.now().isoformat(timespec="seconds")
    result_text = f"""Completed: {stamp}

Command: `{actual_command or "Not run."}`
Result: {result}
Exit code: {verify["exit_code"] if verify["exit_code"] is not None else "Not run."}
"""
    updated = replace_section(text, "Result", result_text)
    task_path.write_text(updated, encoding="utf-8")

    if update_project_status:
        update_status(
            str(root),
            done=f"{task_title}: {result}",
            next_step="Review task result and continue.",
        )

    return {
        "task": str(task_path),
        "result": result,
        "exit_code": verify["exit_code"],
        "verification_log": verify["output"],
    }
