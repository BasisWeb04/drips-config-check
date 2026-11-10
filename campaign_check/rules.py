from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, time
from typing import Any


@dataclass(frozen=True)
class Rule:
    rule_id: str
    name: str
    description: str


@dataclass(frozen=True)
class Issue:
    rule_id: str
    path: str
    message: str


RULES = (
    Rule("CFG001", "Schedule order", "Campaign start must be before campaign end."),
    Rule("CFG002", "Contact window", "Contact hours must stay within 08:00 to 21:00 in each recipient's local time."),
    Rule("CFG003", "SMS opt-out", "Every SMS message must include clear Reply STOP wording."),
    Rule("CFG004", "Merge fields", "Every merge field used in a message must be declared in data_fields."),
    Rule("CFG005", "Start step", "The flow start value must name an existing step."),
    Rule("CFG006", "Reachable steps", "Every flow step must be reachable from the start."),
    Rule("CFG007", "Next-step links", "Every next value must name an existing step or be null."),
    Rule("CFG008", "Audience segment", "The audience segment must be declared in segments."),
    Rule("CFG009", "Unique step IDs", "Every flow step ID must be unique."),
)

MERGE_FIELD = re.compile(r"{{\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*}}")
REPLY_STOP = re.compile(r"\breply\s+stop\b", re.IGNORECASE)


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _parse_time(value: Any) -> time | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None


def validate_config(config: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []
    schedule = config.get("schedule", {})
    if not isinstance(schedule, dict):
        schedule = {}

    start = _parse_datetime(schedule.get("start"))
    end = _parse_datetime(schedule.get("end"))
    if start is None or end is None or start >= end:
        issues.append(Issue("CFG001", "$.schedule", "Schedule start must be a valid time before schedule end."))

    contact_window = schedule.get("contact_window", {})
    if not isinstance(contact_window, dict):
        contact_window = {}
    window_start = _parse_time(contact_window.get("start"))
    window_end = _parse_time(contact_window.get("end"))
    timezone = contact_window.get("timezone")
    if (
        window_start is None
        or window_end is None
        or window_start < time(8, 0)
        or window_end > time(21, 0)
        or window_start >= window_end
        or timezone != "recipient"
    ):
        issues.append(Issue(
            "CFG002",
            "$.schedule.contact_window",
            "Use a window within 08:00 to 21:00 and timezone 'recipient'.",
        ))

    flow = config.get("flow", {})
    if not isinstance(flow, dict):
        flow = {}
    raw_steps = flow.get("steps", [])
    steps = [step for step in raw_steps if isinstance(step, dict)] if isinstance(raw_steps, list) else []

    declared_fields = set(config.get("data_fields", [])) if isinstance(config.get("data_fields"), list) else set()
    for index, step in enumerate(steps):
        if step.get("type") != "sms":
            continue
        message = step.get("message")
        path = f"$.flow.steps[{index}].message"
        if not isinstance(message, str) or not REPLY_STOP.search(message):
            issues.append(Issue("CFG003", path, "SMS message needs clear 'Reply STOP' opt-out wording."))
        if isinstance(message, str):
            for field in MERGE_FIELD.findall(message):
                if field not in declared_fields:
                    issues.append(Issue("CFG004", path, f"Merge field '{field}' is not declared in $.data_fields."))

    step_ids = [step.get("id") for step in steps if isinstance(step.get("id"), str)]
    known_ids = set(step_ids)
    flow_start = flow.get("start")
    if flow_start not in known_ids:
        issues.append(Issue("CFG005", "$.flow.start", f"Start step '{flow_start}' does not exist in $.flow.steps."))

    if flow_start in known_ids:
        step_by_id = {step["id"]: step for step in steps if step.get("id") in known_ids}
        reachable: set[str] = set()
        current = flow_start
        while current in step_by_id and current not in reachable:
            reachable.add(current)
            next_id = step_by_id[current].get("next")
            if not isinstance(next_id, str):
                break
            current = next_id
        for index, step in enumerate(steps):
            step_id = step.get("id")
            if isinstance(step_id, str) and step_id not in reachable:
                issues.append(Issue("CFG006", f"$.flow.steps[{index}].id", f"Step '{step_id}' cannot be reached from $.flow.start."))

    for index, step in enumerate(steps):
        next_id = step.get("next")
        if next_id is not None and next_id not in known_ids:
            issues.append(Issue("CFG007", f"$.flow.steps[{index}].next", f"Next step '{next_id}' does not exist."))

    segments = set(config.get("segments", [])) if isinstance(config.get("segments"), list) else set()
    audience = config.get("audience", {})
    segment = audience.get("segment") if isinstance(audience, dict) else None
    if segment not in segments:
        issues.append(Issue("CFG008", "$.audience.segment", f"Segment '{segment}' is not declared in $.segments."))

    seen: set[str] = set()
    for index, step_id in enumerate(step_ids):
        if step_id in seen:
            issues.append(Issue("CFG009", f"$.flow.steps[{index}].id", f"Step ID '{step_id}' is repeated."))
        seen.add(step_id)

    return issues

