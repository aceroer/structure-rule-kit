from __future__ import annotations

from pathlib import Path

from .agent_brief import build_agent_brief
from .config import load_config
from .parser import extract_section
from .summary import summarize_structure


def _read(root: Path, relative: str) -> str:
    target = root / relative
    return target.read_text(encoding="utf-8") if target.exists() else ""


def _agent_markdown(path: str, target: str, brief_path: str) -> str:
    root = Path(path)
    summary = summarize_structure(path)
    rules = _read(root, "structure/rules.md")
    metrics = _read(root, "structure/metrics.md")
    toolbox = _read(root, "structure/toolbox.md")
    status = _read(root, "structure/status.md")
    target_name = target.title()

    return f"""# {target_name} Agent Instructions

This repository uses Structure Rule Kit.

## Required Reading

1. `STRUCTURE_RULE.md`
2. `structure/project_plan.md`
3. `structure/rules.md`
4. `structure/status.md`
5. `{brief_path}`

## Project Snapshot

- Project: {summary.get("Project", "Not specified yet.")}
- Current stage: {summary.get("Current stage", "Not specified yet.")}
- Current priority: {summary.get("Current priority", "Not specified yet.")}

## Current Task

{extract_section(status, "Current Task") or "Not specified yet."}

## Rules

{extract_section(rules, "General Rules") or "Follow `structure/rules.md`."}

## Forbidden Actions

{extract_section(rules, "Things Not To Do") or "Follow `structure/rules.md`."}

## Useful Commands

{extract_section(toolbox, "Test Commands") or extract_section(toolbox, "Useful Scripts") or "Not specified yet."}

## Completion Criteria

{extract_section(metrics, "Definition of Done") or "Follow `structure/metrics.md`."}
"""


def export_agent(path: str = ".", target: str = "generic", output: str = "", refresh: bool = True) -> dict:
    root = Path(path)
    normalized = target.lower()
    brief = build_agent_brief(path, task=f"{normalized} agent export", refresh=refresh)
    brief_relative = Path(brief["output"]).relative_to(root)

    if output:
        outputs = [output]
    elif normalized == "codex":
        outputs = ["AGENTS.md"]
    elif normalized == "claude":
        outputs = ["CLAUDE.md"]
    elif normalized == "cursor":
        outputs = [".cursor/rules/structure-rule.md"]
    elif normalized == "generic":
        outputs = ["GENERIC_AGENT.md"]
    else:
        outputs = [f"{normalized.upper()}_AGENT.md"]

    written = []
    content = _agent_markdown(path, normalized, str(brief_relative))
    for item in outputs:
        output_path = root / item
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        written.append(str(output_path))

    return {"target": normalized, "outputs": written, "brief": brief["output"], "status": brief["status"]}


def export_all_agents(path: str = ".", targets: list[str] | None = None, refresh: bool = True) -> dict:
    actual_targets = targets or ["codex", "claude", "cursor", "generic"]
    reports = [export_agent(path, target=target, refresh=refresh) for target in actual_targets]
    outputs = []
    for report in reports:
        outputs.extend(report["outputs"])
    return {"targets": actual_targets, "outputs": outputs, "reports": reports}
