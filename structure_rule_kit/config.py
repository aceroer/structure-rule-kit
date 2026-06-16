from __future__ import annotations

import json
from pathlib import Path


DEFAULT_CONFIG = {
    "context_budget": 8000,
    "repo_map_max_files": 240,
    "default_agent_target": "generic",
    "default_handoff_output": "STRUCTURE_HANDOFF.md",
    "default_brief_output": "STRUCTURE_AGENT_BRIEF.md",
    "default_context_output": "STRUCTURE_CONTEXT_PRUNED.md",
}


def load_config(path: str = ".") -> dict:
    root = Path(path)
    config_path = root / "structure" / "config.json"
    config = dict(DEFAULT_CONFIG)
    if config_path.exists():
        loaded = json.loads(config_path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            config.update(loaded)
    return config


def write_config(path: str = ".", output: str = "structure/config.json", force: bool = False) -> dict:
    root = Path(path)
    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not force:
        return {"output": str(output_path), "created": False}
    output_path.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
    return {"output": str(output_path), "created": True}
