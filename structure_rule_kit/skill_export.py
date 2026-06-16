from __future__ import annotations

from pathlib import Path

from .agent_brief import build_agent_brief
from .parser import extract_section
from .summary import summarize_structure


def _read(root: Path, relative: str) -> str:
    target = root / relative
    return target.read_text(encoding="utf-8") if target.exists() else ""


def export_skill(path: str = ".", name: str = "project-structure", output_dir: str = "skills", refresh: bool = True) -> dict:
    root = Path(path)
    brief = build_agent_brief(path, task=f"skill export {name}", refresh=refresh)
    skill_dir = root / output_dir / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path = skill_dir / "SKILL.md"

    summary = summarize_structure(path)
    rules = _read(root, "structure/rules.md")
    metrics = _read(root, "structure/metrics.md")
    toolbox = _read(root, "structure/toolbox.md")

    content = f"""# {name}

Use this skill when working in this repository.

## Purpose

Load the Structure Rule Kit operating layer, then work from the current agent
brief instead of guessing project intent.

## Project Snapshot

- Project: {summary.get("Project", "Not specified yet.")}
- Current stage: {summary.get("Current stage", "Not specified yet.")}
- Current priority: {summary.get("Current priority", "Not specified yet.")}

## Required Files

1. `STRUCTURE_RULE.md`
2. `STRUCTURE_AGENT_BRIEF.md`
3. `structure/project_plan.md`
4. `structure/rules.md`
5. `structure/status.md`
6. `structure/metrics.md`

## Rules

{extract_section(rules, "General Rules") or "Follow `structure/rules.md`."}

## Forbidden Actions

{extract_section(rules, "Things Not To Do") or "Follow `structure/rules.md`."}

## Useful Commands

{extract_section(toolbox, "Test Commands") or extract_section(toolbox, "Useful Scripts") or "Not specified yet."}

## Completion Criteria

{extract_section(metrics, "Definition of Done") or "Follow `structure/metrics.md`."}

## Workflow

1. Read `STRUCTURE_RULE.md`.
2. Read `STRUCTURE_AGENT_BRIEF.md`.
3. Keep changes scoped to the active task.
4. Run the relevant checks.
5. Record verification with `structure-rule verify-log` when useful.
6. Update status or create a handoff before exiting.
"""
    skill_path.write_text(content, encoding="utf-8")
    return {"output": str(skill_path), "brief": brief["output"], "status": brief["status"]}
