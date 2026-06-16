from pathlib import Path

from structure_rule_kit import (
    build_agent_brief,
    end_session,
    init_structure,
    run_agent_task,
    scaffold_mcp,
    start_session,
    write_config,
)
from tests.test_workflow_tools import fill_ready_fields


def test_write_config(tmp_path):
    init_structure(str(tmp_path))
    report = write_config(str(tmp_path))
    output = tmp_path / "structure" / "config.json"
    assert report["created"] is True
    assert output.exists()


def test_build_agent_brief(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    report = build_agent_brief(str(tmp_path), task="Implement workflow runner", budget=2200)
    output = tmp_path / "STRUCTURE_AGENT_BRIEF.md"
    assert report["ready"] is True
    assert output.exists()
    text = output.read_text(encoding="utf-8")
    assert "Structure Agent Brief" in text
    assert "Implement workflow runner" in text
    assert (tmp_path / "structure" / "repo_map.md").exists()
    assert (tmp_path / "STRUCTURE_CONTEXT_PRUNED.md").exists()


def test_start_and_end_session(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    start = start_session(str(tmp_path), task="Run session", goal="Exercise session runner")
    assert Path(start["task"]).exists()
    assert Path(start["brief"]).exists()
    assert start["status"] == "ready"

    end = end_session(
        str(tmp_path),
        done="Session runner exercised.",
        next_step="Review generated handoff.",
        command="python3 -c 'print(789)'",
        run=True,
    )
    assert Path(end["handoff"]).exists()
    assert Path(end["verification"]).exists()


def test_run_agent_task(tmp_path):
    init_structure(str(tmp_path))
    fill_ready_fields(tmp_path)
    start = start_session(str(tmp_path), task="Run task", goal="Exercise run-task")
    report = run_agent_task(start["task"], command="python3 -c 'print(321)'", path=str(tmp_path), update_project_status=True)
    task_text = Path(start["task"]).read_text(encoding="utf-8")
    assert report["result"] == "pass"
    assert report["exit_code"] == 0
    assert "Result: pass" in task_text


def test_scaffold_mcp(tmp_path):
    init_structure(str(tmp_path))
    report = scaffold_mcp(str(tmp_path))
    output = tmp_path / "structure" / "mcp_server.py"
    assert report["created"] is True
    assert output.exists()
    assert "list_resources" in output.read_text(encoding="utf-8")
