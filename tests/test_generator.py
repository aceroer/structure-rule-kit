from structure_rule_kit import init_structure


def test_init_structure_creates_files(tmp_path):
    report = init_structure(str(tmp_path))
    assert report["created"]
    assert (tmp_path / "STRUCTURE_RULE.md").exists()
    assert (tmp_path / "structure" / "project_plan.md").exists()
    assert (tmp_path / "structure" / "protocols.md").exists()
    assert (tmp_path / "structure" / "agent_notes.md").exists()


def test_init_structure_protocols_include_roles(tmp_path):
    init_structure(str(tmp_path))
    protocols = (tmp_path / "structure" / "protocols.md").read_text(encoding="utf-8")

    assert "## Role Protocol" in protocols
    assert "P12 | CEO Agent" in protocols
    assert "P13 | Human Supervisor" in protocols
    assert "## Executive Office Protocol" in protocols
    assert "| COO |" in protocols
    assert "| CTO |" in protocols
    assert "| CFO |" in protocols
    assert "| CSO |" in protocols
    assert "| CRO |" in protocols


def test_init_structure_skips_existing_without_force(tmp_path):
    init_structure(str(tmp_path))
    report = init_structure(str(tmp_path))
    assert report["skipped"]
