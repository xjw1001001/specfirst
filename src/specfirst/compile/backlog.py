"""The review backlog of the standard as a file (ADR-020, decision 5; issue #28).

`standard/BACKLOG.yaml` holds one record per proposed change of the
standard. The issue keeps the discussion; the record keeps the state:

    id        i<issue>.<slug>, for example i01.zero-shown
    issue     the GitHub issue number
    layer     catalog | house | schema | docs | code
    target    an entry, an alternative, a default, a file
    kind      what the change is: add an alternative, change a default, ...
    status    open | accepted | done | waits | rejected
    version   accepted and done: the version label it is for (versions.yaml)
    for       waits: the work package or track it waits for
    reason    why, in a few words; required for waits and rejected
    adr       the ADR that settles it

A record `accepted` for a version that is frozen is a problem: at the
freeze every accepted record is done, or waits.
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

import yaml

from specfirst.compile import versions

FILE = "standard/BACKLOG.yaml"
LAYERS = ("catalog", "house", "schema", "docs", "code")
STATUSES = ("open", "accepted", "done", "waits", "rejected")
# The issues ADR-020 takes up: the review of std-1 at node N1, #28 and #33.
ISSUES = (*range(1, 25), 28, 33)
_ID = re.compile(r"^i[0-9]{2}c?\.[a-z0-9]+(-[a-z0-9]+)*$")
_FIELDS = ("id", "issue", "layer", "target", "kind", "status", "version", "for", "reason",
           "adr")


def load(root: Path) -> list[dict]:
    with open(root / FILE, encoding="ascii") as handle:
        raw = yaml.safe_load(handle) or {}
    records = raw.get("records") if isinstance(raw, dict) else None
    return [r for r in records if isinstance(r, dict)] if isinstance(records, list) else []


def accepted_for(records: list[dict], label: str) -> set[str]:
    """The IDs of the records accepted for, or done in, a version."""
    return {str(r["id"]) for r in records
            if r.get("status") in ("accepted", "done") and r.get("version") == label}


def problems(root: Path, issues: tuple[int, ...] = ISSUES) -> list[str]:
    """Every record is complete and has a known status; every issue has a record."""
    try:
        records = load(root)
        known = versions.load(root)
    except (OSError, yaml.YAMLError) as error:
        return [f"{FILE}: {error}"]
    found: list[str] = []
    if not records:
        return [f"{FILE}: no records"]
    counts = Counter(str(r.get("id")) for r in records)
    for name, count in sorted(counts.items()):
        if count > 1:
            found.append(f"{name}: {count} records with this ID")
    for record in records:
        name = str(record.get("id"))
        if not _ID.match(name):
            found.append(f"{name}: an ID is i<issue>.<slug>")
        for key in sorted(set(record) - set(_FIELDS)):
            found.append(f"{name}: unknown field '{key}'")
        for key in ("issue", "layer", "target", "kind", "status", "adr"):
            if record.get(key) in (None, ""):
                found.append(f"{name}: no {key}")
        if not isinstance(record.get("issue"), int):
            found.append(f"{name}: the issue is a number")
        elif not name.startswith(f"i{record['issue']:02d}"):
            found.append(f"{name}: the ID does not start with its issue")
        if record.get("layer") not in LAYERS:
            found.append(f"{name}: the layer '{record.get('layer')}' is not one of "
                         f"{', '.join(LAYERS)}")
        status = record.get("status")
        if status not in STATUSES:
            found.append(f"{name}: the status '{status}' is not one of {', '.join(STATUSES)}")
        if status in ("accepted", "done"):
            label = record.get("version")
            if label not in known:
                found.append(f"{name}: {status} for '{label}', which "
                             f"{versions.VERSIONS} does not list")
            elif status == "accepted" and known[label].status == "frozen":
                found.append(f"{name}: accepted for {label}, which is frozen: at a freeze "
                             "every accepted record is done, or waits")
        elif record.get("version"):
            found.append(f"{name}: a version belongs to an accepted or done record")
        if status == "waits" and not record.get("for"):
            found.append(f"{name}: waits, and does not say for what")
        if status in ("waits", "rejected") and not record.get("reason"):
            found.append(f"{name}: {status} without a reason")
    numbers = {r.get("issue") for r in records}
    for number in issues:
        if number not in numbers:
            found.append(f"issue #{number}: no record in {FILE}")
    return found


def summary(root: Path) -> list[str]:
    """Lines for `specfirst status`: the records not done, by layer and status."""
    try:
        records = load(root)
    except (OSError, yaml.YAMLError) as error:
        return [f"{FILE}: {error}"]
    lines = [f"==> {FILE} <=="]
    counts = Counter(str(r.get("status")) for r in records)
    lines.append(f"{len(records)} records: " + ", ".join(
        f"{counts[s]} {s}" for s in STATUSES if counts[s]))
    for layer in LAYERS:
        for status in ("open", "accepted", "waits"):
            chosen = [r for r in records if r.get("layer") == layer and r.get("status") == status]
            if not chosen:
                continue
            lines.append(f"{layer}, {status}:")
            for record in chosen:
                where = record.get("version") or record.get("for") or ""
                lines.append(f"  {record['id']} (#{record.get('issue')}) {record.get('target')}"
                             + (f" [{where}]" if where else ""))
    return lines
