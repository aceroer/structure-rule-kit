import json
from pathlib import Path

from structure_rule_kit import (
    approval_grant,
    approval_request,
    create_issue,
    init_structure,
    model_call,
    model_capability_check,
    model_config_init,
    model_doctor,
    model_provider_set,
    model_request_build,
    subagent_create,
)
from structure_rule_kit.cli import main


def seed_project(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="API integration", body="Prepare a governed model API call.")
    subagent = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")
    return subagent


def test_model_config_and_provider_set(tmp_path):
    report = model_config_init(str(tmp_path))
    provider = model_provider_set(
        str(tmp_path),
        provider="openai",
        default_model="test-model",
        api_key_env="TEST_MODEL_API_KEY",
    )
    payload = json.loads(Path(provider["output"]).read_text(encoding="utf-8"))

    assert Path(report["providers"]).exists()
    assert payload["version"] == "1.3"
    assert payload["providers"]["openai"]["default_model"] == "test-model"
    assert payload["providers"]["openai"]["api_key_env"] == "TEST_MODEL_API_KEY"


def test_model_doctor_checks_key_presence(tmp_path, monkeypatch):
    model_config_init(str(tmp_path))
    model_provider_set(str(tmp_path), provider="openai", default_model="test-model", api_key_env="TEST_MODEL_API_KEY")

    missing = model_doctor(str(tmp_path), provider="openai")
    monkeypatch.setenv("TEST_MODEL_API_KEY", "secret")
    ready = model_doctor(str(tmp_path), provider="openai")

    assert missing["ok"] is False
    assert missing["api_key_present"] is False
    assert ready["ok"] is True
    assert ready["ready_for_live_call"] is True


def test_model_request_build_includes_issue_context(tmp_path):
    subagent = seed_project(tmp_path)
    model_provider_set(str(tmp_path), provider="openai", default_model="test-model")
    request = model_request_build(
        str(tmp_path),
        provider="openai",
        prompt="Plan the next step.",
        issue="issue-0001",
        subagent=subagent["id"],
    )
    payload = json.loads(Path(request["output"]).read_text(encoding="utf-8"))

    assert payload["model"] == "test-model"
    assert payload["subagent"] == subagent["id"]
    assert "API integration" in payload["request"]["messages"][1]["content"]


def test_model_call_dry_run_and_capability_gate(tmp_path):
    subagent = seed_project(tmp_path)
    model_provider_set(str(tmp_path), provider="openai", default_model="test-model")
    request = model_request_build(str(tmp_path), provider="openai", prompt="Draft.", subagent=subagent["id"])

    dry = model_call(str(tmp_path), request=request["id"])
    blocked = model_call(str(tmp_path), request=request["id"], apply=True)
    approval = approval_request(str(tmp_path), subagent=subagent["id"], action="model-call", target="openai")
    approval_grant(str(tmp_path), approval["id"])
    capability = model_capability_check(str(tmp_path), subagent=subagent["id"], target="openai")

    assert dry["status"] == "dry-run"
    assert dry["capability_ok"] is False
    assert blocked["status"] == "missing-capability-token"
    assert capability["ok"] is True


def test_model_api_cli(tmp_path, monkeypatch):
    subagent = seed_project(tmp_path)
    monkeypatch.setenv("TEST_MODEL_API_KEY", "secret")

    assert main(["model-config", "--path", str(tmp_path)]) == 0
    assert (
        main(
            [
                "model-provider-set",
                "--path",
                str(tmp_path),
                "--provider",
                "openai",
                "--model",
                "test-model",
                "--api-key-env",
                "TEST_MODEL_API_KEY",
            ]
        )
        == 0
    )
    assert main(["model-doctor", "--path", str(tmp_path), "--provider", "openai"]) == 0
    assert (
        main(
            [
                "model-request",
                "--path",
                str(tmp_path),
                "--provider",
                "openai",
                "--prompt",
                "Plan.",
                "--subagent",
                subagent["id"],
            ]
        )
        == 0
    )
    assert main(["model-call", "model-request-0001", "--path", str(tmp_path)]) == 0
    assert main(["model-call", "model-request-0001", "--path", str(tmp_path), "--apply"]) == 1
    assert main(["approval-request", subagent["id"], "--path", str(tmp_path), "--action", "model-call", "--target", "openai"]) == 0
    assert main(["approval-grant", "approval-0001", "--path", str(tmp_path)]) == 0
    assert main(["model-capability-check", "--path", str(tmp_path), "--subagent", subagent["id"], "--provider", "openai"]) == 0
