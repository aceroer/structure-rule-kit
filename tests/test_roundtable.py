import json
from pathlib import Path

from structure_rule_kit import (
    actor_weight,
    agent_promote,
    create_issue,
    init_structure,
    meeting_post,
    meeting_show,
    meeting_start,
    minutes_generate,
    org_apply,
    org_review,
    roundtable_init,
    roundtable_status,
    stream_start,
    subagent_create,
    vote_cast,
    vote_open,
    vote_tally,
)
from structure_rule_kit.cli import main


def seed_roundtable_project(tmp_path):
    init_structure(str(tmp_path))
    create_issue(str(tmp_path), title="Roundtable", body="Discuss an agent route.")
    ceo = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")
    worker = subagent_create(str(tmp_path), permission="draft", issue="issue-0001")
    agent_promote(str(tmp_path), subagent=ceo["id"], level="P12")
    agent_promote(str(tmp_path), subagent=worker["id"], level="P6")
    stream = stream_start(str(tmp_path), issue="issue-0001", ceo_agent=ceo["id"])
    meeting = meeting_start(str(tmp_path), topic="Route review", stream=stream["id"], organizer=ceo["id"])
    return ceo, worker, stream, meeting


def test_roundtable_init_and_meeting_minutes(tmp_path):
    ceo, worker, _stream, meeting = seed_roundtable_project(tmp_path)
    meeting_post(str(tmp_path), meeting=meeting["id"], actor=ceo["id"], role="CEO", message="We need a safer route.")
    meeting_post(str(tmp_path), meeting=meeting["id"], actor=worker["id"], role="Worker", message="I propose a scoped draft.")
    minutes = minutes_generate(str(tmp_path), meeting=meeting["id"])
    payload = json.loads(Path(minutes["output"]).read_text(encoding="utf-8"))
    shown = meeting_show(str(tmp_path), meeting=meeting["id"])

    assert payload["topic"] == "Route review"
    assert ceo["id"] in payload["participants"]
    assert worker["id"] in payload["participants"]
    assert payload["summary"]["message_count"] == 2
    assert shown["events"][-1]["type"] == "minutes_generated"


def test_weighted_vote_uses_p_level_and_explicit_weight(tmp_path):
    ceo, worker, _stream, meeting = seed_roundtable_project(tmp_path)
    vote = vote_open(str(tmp_path), meeting=meeting["id"], motion="Adopt scoped route.", by=ceo["id"])
    vote_cast(str(tmp_path), vote=vote["id"], voter=ceo["id"], choice="yes")
    vote_cast(str(tmp_path), vote=vote["id"], voter=worker["id"], choice="no")
    vote_cast(str(tmp_path), vote=vote["id"], voter="human", choice="abstain", weight=2)
    tally = vote_tally(str(tmp_path), vote=vote["id"], close=True)

    assert actor_weight(str(tmp_path), ceo["id"]) == 12
    assert actor_weight(str(tmp_path), worker["id"]) == 6
    assert tally["tally"]["totals"]["yes"] == 12
    assert tally["tally"]["totals"]["no"] == 6
    assert tally["tally"]["totals"]["abstain"] == 2
    assert tally["tally"]["passed"] is True
    assert tally["payload"]["status"] == "closed"


def test_organization_application_review_requires_ceo_or_human(tmp_path):
    ceo, worker, _stream, meeting = seed_roundtable_project(tmp_path)
    application = org_apply(
        str(tmp_path),
        applicant=worker["id"],
        kind="promotion",
        target="P7",
        justification="Needs scoped source edit responsibility.",
        meeting=meeting["id"],
    )

    try:
        org_review(str(tmp_path), application=application["id"], decision="approved", reviewer=worker["id"])
    except PermissionError as exc:
        assert "P12 CEO" in str(exc)
    else:
        raise AssertionError("Expected non-CEO organization review to fail.")

    reviewed = org_review(str(tmp_path), application=application["id"], decision="approved", reviewer=ceo["id"], notes="Approved.")
    shown = meeting_show(str(tmp_path), meeting=meeting["id"])

    assert reviewed["payload"]["status"] == "approved"
    assert reviewed["review"]["reviewer"] == ceo["id"]
    assert shown["events"][-1]["type"] == "organization_review"


def test_roundtable_cli(tmp_path):
    ceo, worker, _stream, _meeting = seed_roundtable_project(tmp_path)

    assert main(["roundtable-init", "--path", str(tmp_path)]) == 0
    assert main(["meeting-start", "--path", str(tmp_path), "--topic", "CLI meeting", "--organizer", ceo["id"]]) == 0
    assert main(["meeting-post", "meeting-0002", "--path", str(tmp_path), "--actor", ceo["id"], "--message", "Open route."]) == 0
    assert main(["vote-open", "--path", str(tmp_path), "--meeting", "meeting-0002", "--motion", "Proceed.", "--by", ceo["id"]]) == 0
    assert main(["vote-cast", "vote-0001", "--path", str(tmp_path), "--voter", ceo["id"], "--choice", "yes"]) == 0
    assert main(["vote-cast", "vote-0001", "--path", str(tmp_path), "--voter", worker["id"], "--choice", "no"]) == 0
    assert main(["vote-tally", "vote-0001", "--path", str(tmp_path), "--close"]) == 0
    assert (
        main(
            [
                "org-apply",
                "--path",
                str(tmp_path),
                "--applicant",
                worker["id"],
                "--kind",
                "role-change",
                "--target",
                "P7",
                "--meeting",
                "meeting-0002",
            ]
        )
        == 0
    )
    assert main(["org-review", "application-0001", "--path", str(tmp_path), "--decision", "approved", "--reviewer", ceo["id"]]) == 0
    assert main(["minutes-generate", "meeting-0002", "--path", str(tmp_path)]) == 0
    assert main(["meeting-show", "meeting-0002", "--path", str(tmp_path)]) == 0
    assert main(["roundtable-status", "--path", str(tmp_path)]) == 0

    status = roundtable_status(str(tmp_path))
    assert status["meetings"] == 2
    assert status["minutes"] == 1
    assert status["votes"] == 1
    assert status["applications"] == 1
