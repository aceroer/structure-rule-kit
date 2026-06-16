from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path


ROOTS = ["rag", "mcp", "skills", "notebooks", "structure"]
GITHUB_DIRS = ["issues", "prs", "projects", "milestones", "actions", "labels"]


def _now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _slugify(value: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", value.lower())
    return "-".join(words[:10]) or "snapshot"


def _root(path: str = ".") -> Path:
    return Path(path) / ".contextgit"


def _append_log(root: Path, event: str, payload: dict) -> None:
    record = {"timestamp": _now(), "event": event, **payload}
    with (root / "log.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _read_text(path: Path, default: str = "") -> str:
    return path.read_text(encoding="utf-8") if path.exists() else default


def _current_branch(root: Path) -> str:
    return _read_text(root / "HEAD", "main").strip() or "main"


def _snapshot_entries(root: Path) -> list[dict]:
    entries = []
    log_path = root / "log.jsonl"
    if not log_path.exists():
        return entries
    for line in log_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if record.get("event") == "snapshot":
            entries.append(record)
    return entries


def init_context(path: str = ".", project_name: str = "", force: bool = False) -> dict:
    root = _root(path)
    if root.exists() and force:
        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    for directory in ["snapshots", "branches", "tags", "exports"]:
        (root / directory).mkdir(parents=True, exist_ok=True)
    for name in ROOTS:
        (root / "roots" / name).mkdir(parents=True, exist_ok=True)
    for name in GITHUB_DIRS:
        (root / "github" / name).mkdir(parents=True, exist_ok=True)
    (root / "HEAD").write_text("main\n", encoding="utf-8")
    config = {
        "project_name": project_name or "Unnamed Project",
        "default_branch": "main",
        "snapshot_format": "markdown",
        "routing_format": "json",
        "github_integration": False,
        "slack_integration": False,
    }
    (root / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    if not (root / "log.jsonl").exists():
        (root / "log.jsonl").write_text("", encoding="utf-8")
    branch_file = root / "branches" / "main.md"
    if not branch_file.exists():
        branch_file.write_text("# Branch: main\n\n## Purpose\n\nDefault context branch.\n", encoding="utf-8")
    _append_log(root, "init", {"branch": "main"})
    return {"output": str(root), "branch": "main"}


def _snapshot_body(path: str, snapshot_id: str, branch: str, message: str, source: str = "") -> str:
    repo = Path(path)
    status = _read_text(repo / "structure" / "status.md", "Not available.")
    decisions = _read_text(repo / "structure" / "decision_log.md", "Not available.")
    verification = _read_text(repo / "structure" / "verification_log.md", "Not available.")
    board = _read_text(repo / "structure" / "network" / "projects" / "board.md", "Not available.")
    brief = _read_text(repo / "STRUCTURE_AGENT_BRIEF.md", "Not available.")
    extra = _read_text(Path(source), "") if source else ""
    return f"""# Context Snapshot

## Snapshot ID

{snapshot_id}

## Branch

{branch}

## Message

{message or "Not specified."}

## Current State

### Status

{status}

### Agent Brief

{brief}

### Agent Network Board

{board}

## Key Decisions

{decisions}

## Verification

{verification}

## Source Notes

{extra or "Not specified."}

## Roots Updated

- RAG: see `.contextgit/roots/rag/`
- MCP: see `.contextgit/roots/mcp/`
- Skills: see `.contextgit/roots/skills/`
- Notebooks: see `.contextgit/roots/notebooks/`
- Structure: see `.contextgit/roots/structure/`
"""


def create_context_snapshot(path: str = ".", message: str = "", from_file: str = "", branch: str = "") -> dict:
    root = _root(path)
    if not root.exists():
        init_context(path)
    actual_branch = branch or _current_branch(root)
    entries = _snapshot_entries(root)
    snapshot_id = f"{len(entries) + 1:04d}"
    filename = f"{snapshot_id}-{_slugify(message)}.md"
    output = root / "snapshots" / filename
    body = _snapshot_body(path, snapshot_id, actual_branch, message, from_file)
    output.write_text(body, encoding="utf-8")
    latest = root / "snapshots" / "latest.md"
    latest.write_text(body, encoding="utf-8")
    _append_log(root, "snapshot", {"id": snapshot_id, "branch": actual_branch, "message": message, "file": str(output)})
    return {"id": snapshot_id, "output": str(output), "latest": str(latest), "branch": actual_branch}


def list_context_snapshots(path: str = ".") -> list[dict]:
    return _snapshot_entries(_root(path))


def latest_context_snapshot(path: str = ".") -> str:
    return _read_text(_root(path) / "snapshots" / "latest.md")


def create_context_branch(path: str = ".", name: str = "", purpose: str = "") -> dict:
    root = _root(path)
    if not root.exists():
        init_context(path)
    branch = _slugify(name or "branch")
    output = root / "branches" / f"{branch}.md"
    output.write_text(
        f"# Branch: {branch}\n\n## Purpose\n\n{purpose or 'Not specified.'}\n\n## Current Goal\n\nNot specified.\n\n## Notes\n\nNot specified.\n",
        encoding="utf-8",
    )
    _append_log(root, "branch", {"branch": branch})
    return {"branch": branch, "output": str(output)}


def checkout_context_branch(path: str = ".", name: str = "") -> dict:
    root = _root(path)
    branch = _slugify(name or "main")
    branch_file = root / "branches" / f"{branch}.md"
    if not branch_file.exists():
        create_context_branch(path, branch)
    (root / "HEAD").write_text(branch + "\n", encoding="utf-8")
    _append_log(root, "checkout", {"branch": branch})
    return {"branch": branch}


def create_context_tag(path: str = ".", name: str = "", snapshot: str = "", meaning: str = "") -> dict:
    root = _root(path)
    if not root.exists():
        init_context(path)
    tag = _slugify(name or "tag")
    actual_snapshot = snapshot or (_snapshot_entries(root)[-1]["id"] if _snapshot_entries(root) else "")
    output = root / "tags" / f"{tag}.md"
    output.write_text(
        f"# Tag: {tag}\n\n## Snapshot\n\n{actual_snapshot or 'Not specified.'}\n\n## Meaning\n\n{meaning or 'Not specified.'}\n",
        encoding="utf-8",
    )
    _append_log(root, "tag", {"tag": tag, "snapshot": actual_snapshot})
    return {"tag": tag, "output": str(output), "snapshot": actual_snapshot}


def export_context(path: str = ".", output: str = ".contextgit/exports/CONTEXT_EXPORT.md", include_roots: bool = False) -> dict:
    repo = Path(path)
    root = _root(path)
    if not root.exists():
        init_context(path)
    snapshots = list_context_snapshots(path)
    latest = latest_context_snapshot(path) or "Not available."
    chunks = [
        "# Context Export",
        "",
        f"Branch: {_current_branch(root)}",
        "",
        "## Snapshot History",
        "",
    ]
    if snapshots:
        chunks.extend(f"- {item['id']} {item['branch']} {item.get('message', '')}" for item in snapshots)
    else:
        chunks.append("- None.")
    chunks.extend(["", "## Latest Snapshot", "", latest])
    if include_roots:
        chunks.extend(["", "## Roots", ""])
        for name in ROOTS:
            files = sorted((root / "roots" / name).glob("*"))
            chunks.append(f"### {name}")
            chunks.append("")
            chunks.extend(f"- `{item.relative_to(root)}`" for item in files) if files else chunks.append("- None.")
            chunks.append("")
    output_path = repo / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")
    _append_log(root, "export", {"output": str(output_path)})
    return {"output": str(output_path), "snapshots": len(snapshots)}


def route_context(path: str = ".", output: str = ".contextgit/exports/routing.json") -> dict:
    root = _root(path)
    if not root.exists():
        init_context(path)
    payload = {
        "snapshot_message": "",
        "branch": _current_branch(root),
        "keep_in_context": [],
        "roots": {name: [] for name in ROOTS},
        "github": {"issues": [], "prs": [], "projects": [], "actions": []},
    }
    output_path = Path(path) / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {"output": str(output_path)}
