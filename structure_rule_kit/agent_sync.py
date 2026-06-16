from __future__ import annotations

from .agent_brief import build_agent_brief
from .agent_export import export_agent
from .agent_ready import check_agent_ready
from .context_prune import build_context_prune
from .mcp_manifest import build_mcp_manifest
from .repo_map import scan_repo_map
from .skill_export import export_skill


def sync_agent(path: str = ".", target: str = "codex", skill_name: str = "project-structure", budget: int | None = None) -> dict:
    repo_map = scan_repo_map(path)
    ready = check_agent_ready(path)
    context = build_context_prune(path, budget=budget or 8000)
    brief = build_agent_brief(path, task=f"{target} sync", budget=budget, refresh=False)
    agent = export_agent(path, target=target, refresh=False)
    skill = export_skill(path, name=skill_name, refresh=False)
    manifest = build_mcp_manifest(path)
    return {
        "status": ready["status"],
        "ready": ready["ready"],
        "repo_map": repo_map["output"],
        "context": context["output"],
        "brief": brief["output"],
        "agent_outputs": agent["outputs"],
        "skill": skill["output"],
        "mcp_manifest": manifest["output"],
    }
