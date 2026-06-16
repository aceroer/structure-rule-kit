from __future__ import annotations

from pathlib import Path


SERVER_TEMPLATE = '''from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def list_resources() -> list[dict]:
    resources = []
    for path in [ROOT / "STRUCTURE_RULE.md", *sorted((ROOT / "structure").glob("*.md"))]:
        if path.exists():
            rel = path.relative_to(ROOT)
            resources.append({
                "uri": f"structure-rule://{rel}",
                "name": str(rel),
                "mimeType": "text/markdown",
            })
    return resources


def read_resource(uri: str) -> dict:
    prefix = "structure-rule://"
    if not uri.startswith(prefix):
        raise ValueError(f"Unsupported URI: {uri}")
    target = (ROOT / uri[len(prefix):]).resolve()
    if ROOT not in target.parents and target != ROOT:
        raise ValueError("Resource escapes repository root")
    return {"uri": uri, "text": target.read_text(encoding="utf-8")}


if __name__ == "__main__":
    print(json.dumps({"resources": list_resources()}, indent=2))
'''


def scaffold_mcp(path: str = ".", output: str = "structure/mcp_server.py", force: bool = False) -> dict:
    root = Path(path)
    output_path = root / output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and not force:
        return {"output": str(output_path), "created": False}
    output_path.write_text(SERVER_TEMPLATE, encoding="utf-8")
    return {"output": str(output_path), "created": True}
