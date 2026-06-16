from __future__ import annotations

import argparse
import json
from pathlib import Path


RESOURCE_NAMES = [
    "STRUCTURE_RULE.md",
    "STRUCTURE_AGENT_BRIEF.md",
    "STRUCTURE_CONTEXT_PRUNED.md",
    "STRUCTURE_CONTEXT_PACK.md",
]


def list_resource_paths(root: Path) -> list[Path]:
    paths = [root / name for name in RESOURCE_NAMES]
    structure_dir = root / "structure"
    if structure_dir.exists():
        paths.extend(sorted(structure_dir.glob("*.md")))
        paths.extend(sorted(structure_dir.glob("*.json")))
    return [path for path in paths if path.exists() and path.is_file()]


def list_resources(path: str = ".") -> list[dict]:
    root = Path(path).resolve()
    resources = []
    for resource_path in list_resource_paths(root):
        relative = resource_path.relative_to(root)
        resources.append(
            {
                "uri": f"structure-rule://{relative}",
                "name": str(relative),
                "mimeType": "application/json" if resource_path.suffix == ".json" else "text/markdown",
            }
        )
    return resources


def read_resource(path: str = ".", uri: str = "") -> dict:
    root = Path(path).resolve()
    prefix = "structure-rule://"
    if not uri.startswith(prefix):
        raise ValueError(f"Unsupported URI: {uri}")
    target = (root / uri[len(prefix):]).resolve()
    if root != target and root not in target.parents:
        raise ValueError("Resource escapes repository root")
    return {"uri": uri, "text": target.read_text(encoding="utf-8")}


def run_server(path: str = ".", request: str = "") -> dict:
    payload = json.loads(request) if request else {"method": "resources/list"}
    method = payload.get("method")
    if method == "resources/list":
        return {"resources": list_resources(path)}
    if method == "resources/read":
        uri = payload.get("params", {}).get("uri", "")
        return read_resource(path, uri)
    return {"error": f"Unsupported method: {method}"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="structure-rule-mcp-server")
    parser.add_argument("--path", default=".")
    parser.add_argument("--request", default="")
    args = parser.parse_args(argv)
    print(json.dumps(run_server(args.path, args.request), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
