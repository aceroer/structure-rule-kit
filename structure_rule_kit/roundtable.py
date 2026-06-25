from __future__ import annotations

import json
from pathlib import Path

from .network import _now, _write_json
from .runtime import RUNTIME_DIR, runtime_init, stream_event
from .governance import SUBAGENTS_DIR


ROUNDTABLE_DIR = RUNTIME_DIR / "roundtable"
MEETINGS_DIR = ROUNDTABLE_DIR / "meetings"
MINUTES_DIR = ROUNDTABLE_DIR / "minutes"
VOTES_DIR = ROUNDTABLE_DIR / "votes"
APPLICATIONS_DIR = ROUNDTABLE_DIR / "applications"
ROUNDTABLE_RULES_FILE = ROUNDTABLE_DIR / "roundtable_rules.json"
ROUNDTABLE_LOG = ROUNDTABLE_DIR / "roundtable_log.jsonl"


ROUNDTABLE_RULES = {
    "version": "1.4.3",
    "philosophy": "Roundtables are append-only meeting terminals for agents and human board members.",
    "mechanisms": {
        "minutes": "Generate auditable minutes from meeting terminal events, votes, and organization reviews.",
        "weighted_voting": "Votes can use explicit weight or actor P-level weight. Human/P13 has weight 13.",
        "organization_application": "Agents can apply for organizational changes; P12 CEO or P13 human reviews decide.",
    },
    "default_vote_weights": {
        "human": 13,
        "P12": 12,
        "P11": 11,
        "P10": 10,
    },
}


def _root(path: str = ".") -> Path:
    return Path(path)


def _append_roundtable_log(path: str, event: str, payload: dict) -> None:
    root = _root(path) / ROUNDTABLE_DIR
    root.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": _now(), "event": event, **payload}
    with (_root(path) / ROUNDTABLE_LOG).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def _next_id(directory: Path, prefix: str, suffix: str = ".json") -> str:
    existing = []
    for item in directory.glob(f"{prefix}-*{suffix}"):
        tail = item.name.removeprefix(f"{prefix}-").removesuffix(suffix)
        number = tail.split("-", 1)[0]
        if number.isdigit():
            existing.append(int(number))
    return f"{prefix}-{max(existing, default=0) + 1:04d}"


def roundtable_init(path: str = ".", force: bool = False) -> dict:
    runtime_init(path)
    root = _root(path)
    for directory in [root / ROUNDTABLE_DIR, root / MEETINGS_DIR, root / MINUTES_DIR, root / VOTES_DIR, root / APPLICATIONS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    rules_path = root / ROUNDTABLE_RULES_FILE
    created = False
    if force or not rules_path.exists():
        _write_json(rules_path, ROUNDTABLE_RULES)
        created = True
    log_path = root / ROUNDTABLE_LOG
    if not log_path.exists():
        log_path.write_text("", encoding="utf-8")
    _append_roundtable_log(path, "roundtable_init", {"rules": str(rules_path), "created": created})
    return {"output": str(root / ROUNDTABLE_DIR), "rules": str(rules_path), "created": created}


def _meeting_path(path: str, meeting: str) -> Path:
    root = _root(path) / MEETINGS_DIR
    for candidate in root.glob(f"{meeting}*.jsonl"):
        return candidate
    direct = root / f"{meeting}.jsonl"
    if direct.exists():
        return direct
    raise FileNotFoundError(f"meeting/{meeting}")


def _append_meeting_event(meeting_path: Path, event_type: str, payload: dict) -> dict:
    lines = meeting_path.read_text(encoding="utf-8").splitlines() if meeting_path.exists() else []
    event = {
        "event_id": f"event-{len(lines) + 1:04d}",
        "timestamp": _now(),
        "type": event_type,
        **payload,
    }
    with meeting_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    return event


def _meeting_events(path: str, meeting: str) -> list[dict]:
    meeting_path = _meeting_path(path, meeting)
    events = []
    for line in meeting_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            events.append(json.loads(line))
    return events


def meeting_start(
    path: str = ".",
    topic: str = "",
    stream: str = "",
    organizer: str = "human",
    agenda: str = "",
) -> dict:
    roundtable_init(path)
    root = _root(path)
    meeting_root = root / MEETINGS_DIR
    meeting_id = _next_id(meeting_root, "meeting", ".jsonl")
    output = meeting_root / f"{meeting_id}.jsonl"
    output.write_text("", encoding="utf-8")
    event = _append_meeting_event(
        output,
        "meeting_started",
        {
            "meeting": meeting_id,
            "topic": topic or meeting_id,
            "stream": stream,
            "organizer": organizer,
            "agenda": agenda,
            "state": "active",
        },
    )
    if stream:
        stream_event(path, stream=stream, event_type="roundtable_started", actor=organizer, message=topic or meeting_id, payload={"meeting": meeting_id})
    _append_roundtable_log(path, "meeting_start", {"meeting": meeting_id, "stream": stream, "topic": topic})
    return {"id": meeting_id, "output": str(output), "event": event}


def meeting_post(
    path: str = ".",
    meeting: str = "",
    actor: str = "",
    message: str = "",
    role: str = "",
) -> dict:
    roundtable_init(path)
    meeting_path = _meeting_path(path, meeting)
    event = _append_meeting_event(
        meeting_path,
        "message",
        {
            "actor": actor or "anonymous",
            "role": role,
            "message": message,
        },
    )
    _append_roundtable_log(path, "meeting_post", {"meeting": meeting, "actor": actor, "event": event["event_id"]})
    return {"meeting": meeting, "output": str(meeting_path), "event": event}


def _load_subagent(path: str, actor: str) -> dict:
    root = _root(path) / SUBAGENTS_DIR
    for candidate in root.glob(f"{actor}*.json"):
        return json.loads(candidate.read_text(encoding="utf-8"))
    return {}


def actor_weight(path: str = ".", actor: str = "", weight: float | None = None) -> float:
    if weight is not None:
        return float(weight)
    if not actor or actor.lower() in {"human", "owner", "p13"}:
        return 13.0
    payload = _load_subagent(path, actor)
    level = payload.get("corporate_level", "P1")
    if level.startswith("P") and level[1:].isdigit():
        return float(level[1:])
    return 1.0


def vote_open(path: str = ".", meeting: str = "", motion: str = "", by: str = "") -> dict:
    roundtable_init(path)
    root = _root(path)
    vote_root = root / VOTES_DIR
    vote_id = _next_id(vote_root, "vote")
    payload = {
        "id": vote_id,
        "meeting": meeting,
        "motion": motion or "Not specified.",
        "opened_by": by or "human",
        "status": "open",
        "votes": [],
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = vote_root / f"{vote_id}.json"
    _write_json(output, payload)
    meeting_path = _meeting_path(path, meeting)
    _append_meeting_event(meeting_path, "vote_opened", {"vote": vote_id, "motion": payload["motion"], "actor": payload["opened_by"]})
    _append_roundtable_log(path, "vote_open", {"vote": vote_id, "meeting": meeting})
    return {"id": vote_id, "output": str(output), "payload": payload}


def _vote_path(path: str, vote: str) -> Path:
    root = _root(path) / VOTES_DIR
    for candidate in root.glob(f"{vote}*.json"):
        return candidate
    raise FileNotFoundError(f"vote/{vote}")


def vote_cast(path: str = ".", vote: str = "", voter: str = "", choice: str = "", weight: float | None = None, reason: str = "") -> dict:
    roundtable_init(path)
    vote_path = _vote_path(path, vote)
    payload = json.loads(vote_path.read_text(encoding="utf-8"))
    if payload.get("status") != "open":
        raise ValueError(f"Vote {vote} is not open.")
    choice = choice.lower()
    if choice not in {"yes", "no", "abstain"}:
        raise ValueError("Vote choice must be yes, no, or abstain.")
    actual_weight = actor_weight(path, voter, weight)
    payload["votes"] = [item for item in payload.get("votes", []) if item.get("voter") != voter]
    record = {
        "voter": voter,
        "choice": choice,
        "weight": actual_weight,
        "reason": reason,
        "created_at": _now(),
    }
    payload["votes"].append(record)
    payload["updated_at"] = _now()
    _write_json(vote_path, payload)
    meeting_path = _meeting_path(path, payload["meeting"])
    _append_meeting_event(meeting_path, "vote_cast", {"vote": vote, **record})
    _append_roundtable_log(path, "vote_cast", {"vote": vote, "voter": voter, "choice": choice, "weight": actual_weight})
    return {"vote": vote, "output": str(vote_path), "payload": payload, "record": record}


def vote_tally(path: str = ".", vote: str = "", close: bool = False) -> dict:
    roundtable_init(path)
    vote_path = _vote_path(path, vote)
    payload = json.loads(vote_path.read_text(encoding="utf-8"))
    totals = {"yes": 0.0, "no": 0.0, "abstain": 0.0}
    for record in payload.get("votes", []):
        totals[record["choice"]] += float(record.get("weight", 0))
    passed = totals["yes"] > totals["no"]
    result = {
        "vote": vote,
        "meeting": payload["meeting"],
        "motion": payload["motion"],
        "totals": totals,
        "passed": passed,
        "votes": len(payload.get("votes", [])),
        "status": "closed" if close else payload.get("status", "open"),
        "tallied_at": _now(),
    }
    payload["last_tally"] = result
    if close:
        payload["status"] = "closed"
        payload["closed_at"] = _now()
        meeting_path = _meeting_path(path, payload["meeting"])
        _append_meeting_event(meeting_path, "vote_closed", result)
    payload["updated_at"] = _now()
    _write_json(vote_path, payload)
    _append_roundtable_log(path, "vote_tally", {"vote": vote, "passed": passed, "closed": close})
    return {"output": str(vote_path), "payload": payload, "tally": result}


def org_apply(
    path: str = ".",
    applicant: str = "",
    kind: str = "",
    target: str = "",
    justification: str = "",
    meeting: str = "",
) -> dict:
    roundtable_init(path)
    root = _root(path)
    app_root = root / APPLICATIONS_DIR
    application_id = _next_id(app_root, "application")
    payload = {
        "id": application_id,
        "applicant": applicant,
        "kind": kind or "general",
        "target": target,
        "justification": justification or "Not specified.",
        "meeting": meeting,
        "status": "submitted",
        "created_at": _now(),
        "updated_at": _now(),
    }
    output = app_root / f"{application_id}.json"
    _write_json(output, payload)
    if meeting:
        meeting_path = _meeting_path(path, meeting)
        _append_meeting_event(meeting_path, "organization_application", {"application": application_id, "applicant": applicant, "kind": payload["kind"], "target": target})
    _append_roundtable_log(path, "org_apply", {"application": application_id, "applicant": applicant, "kind": payload["kind"]})
    return {"id": application_id, "output": str(output), "payload": payload}


def _application_path(path: str, application: str) -> Path:
    root = _root(path) / APPLICATIONS_DIR
    for candidate in root.glob(f"{application}*.json"):
        return candidate
    raise FileNotFoundError(f"application/{application}")


def _can_review(path: str, reviewer: str) -> bool:
    return actor_weight(path, reviewer) >= 12


def org_review(path: str = ".", application: str = "", decision: str = "", reviewer: str = "", notes: str = "") -> dict:
    roundtable_init(path)
    if not _can_review(path, reviewer):
        raise PermissionError("Organization review requires a P12 CEO agent or P13 human supervisor.")
    decision = decision.lower()
    if decision not in {"approved", "rejected", "needs-info"}:
        raise ValueError("Decision must be approved, rejected, or needs-info.")
    app_path = _application_path(path, application)
    payload = json.loads(app_path.read_text(encoding="utf-8"))
    review = {
        "decision": decision,
        "reviewer": reviewer or "human",
        "notes": notes,
        "reviewed_at": _now(),
    }
    payload["status"] = decision
    payload["review"] = review
    payload["updated_at"] = _now()
    _write_json(app_path, payload)
    if payload.get("meeting"):
        meeting_path = _meeting_path(path, payload["meeting"])
        _append_meeting_event(meeting_path, "organization_review", {"application": application, **review})
    _append_roundtable_log(path, "org_review", {"application": application, "decision": decision, "reviewer": reviewer})
    return {"output": str(app_path), "payload": payload, "review": review}


def minutes_generate(path: str = ".", meeting: str = "") -> dict:
    roundtable_init(path)
    events = _meeting_events(path, meeting)
    if not events:
        raise ValueError(f"Meeting {meeting} has no events.")
    start = events[0]
    participants = sorted({event.get("actor") or event.get("organizer") or event.get("voter") for event in events if event.get("actor") or event.get("organizer") or event.get("voter")})
    messages = [event for event in events if event["type"] == "message"]
    votes = [event for event in events if event["type"] in {"vote_opened", "vote_closed"}]
    applications = [event for event in events if event["type"] in {"organization_application", "organization_review"}]
    payload = {
        "meeting": meeting,
        "topic": start.get("topic", meeting),
        "stream": start.get("stream", ""),
        "generated_at": _now(),
        "participants": participants,
        "summary": {
            "message_count": len(messages),
            "vote_events": len(votes),
            "organization_events": len(applications),
        },
        "agenda": start.get("agenda", ""),
        "key_points": [event.get("message", "") for event in messages if event.get("message")],
        "votes": votes,
        "organization_reviews": applications,
    }
    minutes_root = _root(path) / MINUTES_DIR
    minutes_id = _next_id(minutes_root, "minutes")
    output = minutes_root / f"{minutes_id}-{meeting}.json"
    _write_json(output, payload)
    meeting_path = _meeting_path(path, meeting)
    _append_meeting_event(meeting_path, "minutes_generated", {"minutes": str(output), "actor": "secretary"})
    _append_roundtable_log(path, "minutes_generate", {"meeting": meeting, "minutes": str(output)})
    return {"id": minutes_id, "output": str(output), "payload": payload}


def meeting_show(path: str = ".", meeting: str = "") -> dict:
    events = _meeting_events(path, meeting)
    return {"meeting": meeting, "events": events, "count": len(events), "output": str(_meeting_path(path, meeting))}


def roundtable_status(path: str = ".") -> dict:
    roundtable_init(path)
    root = _root(path)
    meetings = list((root / MEETINGS_DIR).glob("*.jsonl"))
    minutes = list((root / MINUTES_DIR).glob("*.json"))
    votes = list((root / VOTES_DIR).glob("*.json"))
    applications = list((root / APPLICATIONS_DIR).glob("*.json"))
    log_path = root / ROUNDTABLE_LOG
    log_events = len(log_path.read_text(encoding="utf-8").splitlines()) if log_path.exists() else 0
    return {
        "ready": (root / ROUNDTABLE_RULES_FILE).exists(),
        "meetings": len(meetings),
        "minutes": len(minutes),
        "votes": len(votes),
        "applications": len(applications),
        "roundtable_log_events": log_events,
        "rules": str(root / ROUNDTABLE_RULES_FILE),
    }
