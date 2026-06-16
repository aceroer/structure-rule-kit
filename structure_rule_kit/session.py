from __future__ import annotations

from .agent_brief import build_agent_brief
from .config import load_config
from .handoff import build_handoff_pack
from .status_update import update_status
from .task import create_agent_task
from .verify_log import append_verify_log


def start_session(
    path: str = ".",
    task: str = "",
    goal: str = "",
    budget: int | None = None,
    output: str = "",
) -> dict:
    task_report = create_agent_task(path, title=task or "Session task", goal=goal)
    update_status(path, current=task or goal or "Agent session started.", next_step="Work from generated agent brief.")
    brief = build_agent_brief(path, task=task or goal, output=output, budget=budget)
    return {"task": task_report["output"], "brief": brief["output"], "status": brief["status"]}


def end_session(
    path: str = ".",
    done: str = "",
    next_step: str = "",
    command: str = "",
    run: bool = False,
    handoff_output: str = "",
) -> dict:
    config = load_config(path)
    verification = None
    if command:
        verification = append_verify_log(path, command=command, run=run, notes="Session end verification.")
    status = update_status(path, done=done, next_step=next_step)
    handoff = build_handoff_pack(
        path,
        task=next_step or done,
        output=handoff_output or str(config["default_handoff_output"]),
    )
    return {
        "status": status["output"],
        "handoff": handoff["output"],
        "verification": verification["output"] if verification else "",
    }
