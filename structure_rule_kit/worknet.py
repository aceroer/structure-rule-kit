from __future__ import annotations

import json
import re
from pathlib import Path

from .github_bridge import github_comment, github_sync_report, load_github_config
from .network import _append_log, _ensure_network, _find_item, _load_items, _now, _write_json, create_issue
from .status_update import update_status
from .task import create_agent_task
from .verify_log import append_verify_log


CURRENT_SESSION = Path("structure/worknet/current.json")


def _read_task_section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_match = re.search(r"^## .+?$", text[start:], flags=re.MULTILINE)
    end = start + next_match.start() if next_match else len(text)
    return text[start:end].strip()


def task_from_issue(path: str = ".", issue: str = "", output_dir: str = "structure/tasks") -> dict:
    root = _ensure_network(path)
    issue_path, payload = _find_item(root, "issues", issue)
    task = create_agent_task(
        path,
        title=payload.get("title", issue),
        goal=payload.get("body", ""),
        scope=f"Work on local issue `{issue}`.",
        forbidden="Do not change unrelated files.",
        checks="Run the relevant project checks before closing the issue.",
        output_dir=output_dir,
    )
    payload["linked_task"] = task["output"]
    payload["updated_at"] = _now()
    _write_json(issue_path, payload)
    _append_log(root, "task_from_issue", {"id": issue, "task": task["output"]})
    return {"issue": issue, "task": task["output"], "output": task["output"]}


def issue_from_task(path: str = ".", task_file: str = "", label: list[str] | None = None) -> dict:
    root_path = Path(path)
    task_path = Path(task_file)
    if not task_path.is_absolute():
        task_path = root_path / task_file
    text = task_path.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# Agent Task:").strip() if text.splitlines() else "Task issue"
    goal = _read_task_section(text, "Goal") or "Not specified."
    report = create_issue(path, title=title, body=goal, labels=label or ["agent-task"])
    root = _ensure_network(path)
    issue_path, payload = _find_item(root, "issues", report["id"])
    payload["linked_task"] = str(task_path)
    payload["updated_at"] = _now()
    _write_json(issue_path, payload)
    _append_log(root, "issue_from_task", {"id": report["id"], "task": str(task_path)})
    return {"issue": report["id"], "task": str(task_path), "output": report["output"]}


def work_start(path: str = ".", issue: str = "", task: str = "", note: str = "") -> dict:
    root = _ensure_network(path)
    issue_path, payload = _find_item(root, "issues", issue)
    if task:
        payload["linked_task"] = task
    payload["worknet_status"] = "active"
    payload["started_at"] = payload.get("started_at") or _now()
    payload["updated_at"] = _now()
    _write_json(issue_path, payload)
    session = {
        "issue": issue,
        "task": payload.get("linked_task", task),
        "note": note,
        "started_at": _now(),
    }
    output = Path(path) / CURRENT_SESSION
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(session, indent=2), encoding="utf-8")
    update_status(path, current=f"Working on {issue}: {payload.get('title', '')}")
    _append_log(root, "work_start", {"id": issue, "task": session["task"]})
    return {"issue": issue, "session": str(output), "status": "active"}


def work_end(
    path: str = ".",
    done: str = "",
    next_step: str = "",
    command: str = "",
    run: bool = False,
    issue: str = "",
    github_comment_body: str = "",
    apply_comment: bool = False,
) -> dict:
    root_path = Path(path)
    session_path = root_path / CURRENT_SESSION
    session = json.loads(session_path.read_text(encoding="utf-8")) if session_path.exists() else {}
    issue_id = issue or session.get("issue", "")
    root = _ensure_network(path)
    issue_output = ""
    if issue_id:
        issue_path, payload = _find_item(root, "issues", issue_id)
        payload["worknet_status"] = "finished"
        payload["finished_at"] = _now()
        payload["updated_at"] = _now()
        _write_json(issue_path, payload)
        issue_output = str(issue_path)
    status = update_status(path, done=done, next_step=next_step)
    verification = None
    if command:
        verification = append_verify_log(path, command=command, notes=done, run=run)
    comment = None
    if github_comment_body and issue_id:
        comment = github_comment(path, issue=issue_id, body=github_comment_body, apply=apply_comment)
    report = github_sync_report(path)
    if session_path.exists():
        session_path.unlink()
    _append_log(root, "work_end", {"id": issue_id, "done": done, "verification": bool(verification)})
    return {
        "issue": issue_id,
        "issue_output": issue_output,
        "status": status["output"],
        "verification": verification,
        "github_comment": comment,
        "sync_report": report["output"],
    }


def worknet_status(path: str = ".") -> dict:
    root = _ensure_network(path)
    issues = _load_items(root / "issues")
    prs = _load_items(root / "prs")
    milestones = _load_items(root / "milestones")
    session_path = Path(path) / CURRENT_SESSION
    current = json.loads(session_path.read_text(encoding="utf-8")) if session_path.exists() else None
    github = load_github_config(path)
    groups: dict[str, int] = {}
    for issue in issues:
        status = issue.get("worknet_status") or issue.get("status", "open")
        groups[status] = groups.get(status, 0) + 1
    ready = bool(github.get("repo")) and bool(issues)
    return {
        "ready": ready,
        "repo": github.get("repo", ""),
        "current": current,
        "issues": len(issues),
        "prs": len(prs),
        "milestones": len(milestones),
        "issue_status": groups,
    }
