from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .agent_ready import check_agent_ready
from .config import load_config
from .context_prune import build_context_prune
from .repo_map import scan_repo_map
from .summary import summarize_structure


def _read_if_exists(path: Path, limit: int = 3200) -> str:
    if not path.exists():
        return "Not available."
    text = path.read_text(encoding="utf-8").strip()
    if len(text) <= limit:
        return text
    return text[-limit:].strip()


def _latest_file(root: Path, pattern: str) -> Path | None:
    files = sorted(root.glob(pattern), key=lambda item: item.stat().st_mtime if item.exists() else 0)
    return files[-1] if files else None


def build_agent_brief(
    path: str = ".",
    task: str = "",
    output: str = "",
    budget: int | None = None,
    refresh: bool = True,
) -> dict:
    root = Path(path)
    config = load_config(path)
    actual_budget = budget if budget is not None else int(config["context_budget"])
    brief_output = output or str(config["default_brief_output"])

    if refresh:
        scan_repo_map(path, max_files=int(config["repo_map_max_files"]))
        build_context_prune(path, output=str(config["default_context_output"]), budget=actual_budget)

    ready = check_agent_ready(path)
    summary = summarize_structure(path)
    latest_task = _latest_file(root, "structure/tasks/*.md")

    chunks = [
        "# Structure Agent Brief",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Task",
        "",
        task.strip() or "Not specified.",
        "",
        "## Readiness",
        "",
        f"Status: {ready['status']}",
        "",
    ]
    if ready["issues"]:
        chunks.append("### Issues")
        chunks.append("")
        for item in ready["issues"]:
            chunks.append(f"- [{item['severity']}] {item['message']}")
        chunks.append("")

    chunks.append("## Project Snapshot")
    chunks.append("")
    for key, value in summary.items():
        chunks.append(f"- {key}: {str(value).strip()}")

    chunks.extend(
        [
            "",
            "## Latest Task",
            "",
            _read_if_exists(latest_task) if latest_task else "Not available.",
            "",
            "## Context Pack",
            "",
            _read_if_exists(root / str(config["default_context_output"]), limit=actual_budget),
            "",
            "## Repository Map",
            "",
            _read_if_exists(root / "structure" / "repo_map.md"),
            "",
            "## Decision Log",
            "",
            _read_if_exists(root / "structure" / "decision_log.md"),
            "",
            "## Verification Log",
            "",
            _read_if_exists(root / "structure" / "verification_log.md"),
        ]
    )

    output_path = root / brief_output
    output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    return {"output": str(output_path), "status": ready["status"], "ready": ready["ready"]}
