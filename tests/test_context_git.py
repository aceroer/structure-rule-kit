import json
from pathlib import Path

from structure_rule_kit import (
    checkout_context_branch,
    create_context_branch,
    create_context_snapshot,
    create_context_tag,
    create_issue,
    create_pr,
    create_review,
    export_context,
    init_context,
    init_structure,
    latest_context_snapshot,
    list_context_snapshots,
    route_context,
    snapshot_network,
)
from tests.test_workflow_tools import fill_ready_fields


def test_init_context(tmp_path):
    init_structure(str(tmp_path))
    report = init_context(str(tmp_path), project_name="Example")
    root = tmp_path / ".contextgit"
    assert report["branch"] == "main"
    assert (root / "HEAD").read_text(encoding="utf-8").strip() == "main"
    assert (root / "snapshots").exists()
    assert (root / "roots" / "rag").exists()
    assert (root / "github" / "issues").exists()


def test_context_snapshot_log_latest_export(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    init_context(str(tmp_path))
    snapshot = create_context_snapshot(str(tmp_path), message="Initial state")
    entries = list_context_snapshots(str(tmp_path))
    latest = latest_context_snapshot(str(tmp_path))
    export = export_context(str(tmp_path), include_roots=True)

    assert snapshot["id"] == "0001"
    assert len(entries) == 1
    assert "Initial state" in latest
    assert Path(export["output"]).exists()
    assert "Context Export" in Path(export["output"]).read_text(encoding="utf-8")


def test_context_branch_checkout_tag_route(tmp_path):
    init_structure(str(tmp_path))
    init_context(str(tmp_path))
    branch = create_context_branch(str(tmp_path), "experiment", purpose="Try alternate path")
    checkout = checkout_context_branch(str(tmp_path), "experiment")
    snapshot = create_context_snapshot(str(tmp_path), message="Experiment state")
    tag = create_context_tag(str(tmp_path), "v0.6-plan", snapshot=snapshot["id"], meaning="Stable plan")
    route = route_context(str(tmp_path))

    assert branch["branch"] == "experiment"
    assert checkout["branch"] == "experiment"
    assert tag["snapshot"] == "0001"
    payload = json.loads(Path(route["output"]).read_text(encoding="utf-8"))
    assert payload["branch"] == "experiment"


def test_network_snapshot_links_records(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    issue = create_issue(str(tmp_path), title="Snapshot issue")
    pr = create_pr(str(tmp_path), title="Snapshot PR", issue=issue["id"])
    review = create_review(str(tmp_path), pr=pr["id"], decision="approve")
    report = snapshot_network(str(tmp_path), message="Network checkpoint")

    assert report["snapshot"] == "0001"
    assert Path(report["snapshot_file"]).exists()
    assert len(report["updated"]) >= 3
    for item in report["updated"]:
        payload = json.loads(Path(item).read_text(encoding="utf-8"))
        assert payload["linked_snapshot"] == "0001"
