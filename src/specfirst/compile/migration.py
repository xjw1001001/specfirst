"""What a step between two catalog versions keeps (ADR-020, decision 4).

`standard/catalog@<n>/migration.yaml` lists, from the version before, every
alternative and every (entry, unit) that is added, removed, renamed or
changed in meaning, each line with its record of standard/BACKLOG.yaml:

    from: catalog@1
    to: catalog@2
    changes:
      - {alternative: ENTRY/ID, change: added, backlog: B-...}
      - {alternative: ENTRY/ID, change: removed, replacement: ENTRY/ID or null, backlog: ...}
      - {alternative: ENTRY/ID, change: renamed, to: ENTRY/ID, backlog: ...}
      - {alternative: ENTRY/ID, change: changed, backlog: ...}
      - {unit: ENTRY@UNIT, change: added | removed, backlog: ...}
      - {term: NAME, change: added | removed | changed, backlog: ...}

The meaning of an alternative is a hash, computed here, of what a reader and
the compiler see of it: the entry's question, `applies_when`, notes and
fixed rules, and the alternative's statement, definition, slots and fragment
of the compile template. Sources, probes, phrasings and reading notes are
not meaning: a fixed citation is not a migration. `problems` holds the file
against the two versions; `migrate` maps a decision record.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from specfirst.compile.catalog import Catalog
from specfirst.compile.compiler import CompileError, compile_template

FILE = "migration.yaml"
CHANGES = ("added", "removed", "renamed", "changed")


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def meanings(catalog: Catalog) -> dict[str, str]:
    """`ENTRY/ID` -> SHA-256 of the meaning of the alternative."""
    found = {}
    for entry in catalog.entries.values():
        try:
            fragments = compile_template(catalog, entry.id)
        except CompileError:
            fragments = {}
        shared = {"question": entry.question, "applies_when": entry.applies_when,
                  "notes": entry.raw.get("notes"), "fixed_rules": entry.raw.get("fixed_rules")}
        for raw in entry.raw.get("alternatives") or []:
            if not isinstance(raw, dict):
                continue
            alternative = str(raw.get("id", ""))
            body = {**shared, "statement": raw.get("statement"),
                    "definition": raw.get("definition"), "slots": raw.get("slots"),
                    "fragment": fragments.get(alternative)}
            found[f"{entry.id}/{alternative}"] = hashlib.sha256(
                _canonical(body).encode("ascii")).hexdigest()
    return found


def units(catalog: Catalog) -> set[str]:
    """`ENTRY@UNIT` for every question the catalog asks."""
    return {f"{entry_id}@{unit}" for entry_id, unit in catalog.keys()}


@dataclass(frozen=True)
class Differences:
    added: set[str]
    removed: set[str]
    changed: set[str]
    units_added: set[str]
    units_removed: set[str]
    terms: dict[str, str]  # term -> added | removed | changed


def terms(catalog: Catalog) -> dict[str, str]:
    """The defined terms of catalog.yaml (from catalog@2), each as canonical text."""
    return {str(name): _canonical(body) for name, body in (catalog.raw.get("terms") or {}).items()}


def differences(old: Catalog, new: Catalog) -> Differences:
    before, after = meanings(old), meanings(new)
    return Differences(
        added=set(after) - set(before),
        removed=set(before) - set(after),
        changed={key for key in set(before) & set(after) if before[key] != after[key]},
        units_added=units(new) - units(old),
        units_removed=units(old) - units(new),
        terms=_term_changes(terms(old), terms(new)),
    )


def _term_changes(old: dict[str, str], new: dict[str, str]) -> dict[str, str]:
    found = {name: "added" for name in set(new) - set(old)}
    found.update({name: "removed" for name in set(old) - set(new)})
    found.update({name: "changed" for name in set(old) & set(new) if old[name] != new[name]})
    return found


def read(catalog: Catalog) -> dict:
    path = catalog.directory / FILE
    if not path.is_file():
        return {}
    raw = catalog.read_yaml(FILE)
    return raw if isinstance(raw, dict) else {}


def problems(old: Catalog, new: Catalog, accepted: set[str]) -> list[str]:
    """The migration file of `new` against the two versions.

    `accepted`: the IDs of the backlog records accepted for, or done in, the
    new catalog version. Every difference has exactly one line, every line
    is a difference, and every line names one of them.
    """
    raw = read(new)
    found: list[str] = []
    if not raw:
        return [f"{new.label}: no {FILE}"]
    if raw.get("from") != old.label or raw.get("to") != new.label:
        found.append(f"{FILE}: from {raw.get('from')} to {raw.get('to')}, not from "
                     f"{old.label} to {new.label}")
    before, after = meanings(old), meanings(new)
    diff = differences(old, new)
    open_added, open_removed = set(diff.added), set(diff.removed)
    open_changed = set(diff.changed)
    open_units = {("added", key) for key in diff.units_added} | \
                 {("removed", key) for key in diff.units_removed}
    seen: set[tuple[str, str]] = set()
    open_terms = dict(diff.terms)
    for number, line in enumerate(raw.get("changes") or [], 1):
        where = f"{FILE}: change {number}"
        if not isinstance(line, dict):
            found.append(f"{where}: not a mapping")
            continue
        change = line.get("change")
        record = line.get("backlog")
        if record not in accepted:
            found.append(f"{where}: names the backlog record '{record}', which is not accepted "
                         f"for {new.label}")
        if "term" in line:
            name = str(line["term"])
            if open_terms.get(name) != change:
                found.append(f"{where}: the term '{name}' is not {change} in {new.label}")
            else:
                del open_terms[name]
            continue
        if "unit" in line:
            key = str(line["unit"])
            if (change, key) not in open_units:
                found.append(f"{where}: the unit {key} is not {change} in {new.label}")
            open_units.discard((change, key))
            continue
        key = str(line.get("alternative", ""))
        if (change, key) in seen:
            found.append(f"{where}: {key} is {change} twice")
        seen.add((change, key))
        if change not in CHANGES:
            found.append(f"{where}: the change '{change}' is not one of {', '.join(CHANGES)}")
        elif change == "added":
            if key not in diff.added:
                found.append(f"{where}: {key} is not added in {new.label}")
            open_added.discard(key)
        elif change == "removed":
            if key not in diff.removed:
                found.append(f"{where}: {key} is not removed in {new.label}")
            replacement = line.get("replacement")
            if replacement is not None and replacement not in after:
                found.append(f"{where}: the replacement {replacement} is not in {new.label}")
            open_removed.discard(key)
        elif change == "renamed":
            target = str(line.get("to", ""))
            if key not in diff.removed or target not in diff.added:
                found.append(f"{where}: {key} is not renamed to {target} in {new.label}")
            elif before[key] != after[target]:
                found.append(f"{where}: {key} and {target} differ in meaning: a rename keeps "
                             "the meaning; list it as removed with a replacement")
            open_removed.discard(key)
            open_added.discard(target)
        elif change == "changed":
            if key not in diff.changed:
                found.append(f"{where}: {key} does not change in meaning in {new.label}")
            open_changed.discard(key)
    for key in sorted(open_added):
        found.append(f"{key}: added in {new.label}, and {FILE} has no line for it")
    for key in sorted(open_removed):
        found.append(f"{key}: removed in {new.label}, and {FILE} has no line for it")
    for key in sorted(open_changed):
        found.append(f"{key}: changed in meaning in {new.label}, and {FILE} has no line for it")
    for change, key in sorted(open_units):
        found.append(f"{key}: the unit is {change} in {new.label}, and {FILE} has no line for it")
    for name, change in sorted(open_terms.items()):
        found.append(f"the term '{name}' is {change} in {new.label}, and {FILE} has no line for it")
    return found


def migrate(record: dict, new: Catalog) -> tuple[dict | None, str]:
    """A decision record of the version before, in `new`: (record or None, what happened).

    `kept`: the same ID and value. `renamed`: the new alternative ID. `changed`
    and `removed`: flagged for a person, who decides; the record is not
    carried (None). Nothing in M1 migrates records yet (ADR-020, decision 4).
    """
    value = record.get("value") if isinstance(record.get("value"), dict) else {}
    key = f"{record.get('id')}/{value.get('rule')}"
    unit = f"{record.get('id')}@{record.get('unit')}"
    for line in read(new).get("changes") or []:
        if not isinstance(line, dict):
            continue
        if line.get("unit") == unit and line.get("change") == "removed":
            return None, f"removed: the unit {unit} no longer answers the entry"
        if line.get("alternative") != key:
            continue
        change = line.get("change")
        if change == "renamed":
            entry_id, rule = str(line["to"]).split("/", 1)
            if entry_id != record.get("id"):
                return None, f"renamed to {line['to']} in another entry: a person decides"
            return {**record, "value": {**value, "rule": rule}}, f"renamed to {line['to']}"
        if change == "changed":
            return None, f"changed: {key} means something else in {new.label}; a person decides"
        if change == "removed":
            replacement = line.get("replacement")
            return None, (f"removed: {key}" + (f"; the replacement is {replacement}"
                                               if replacement else "") + "; a person decides")
    return dict(record), "kept"


def comparable(records: list[dict], new: Catalog) -> list[str]:
    """Why the scores of a kit are not comparable across the step to `new`.

    Two pairs are comparable on a kit only when every decision of the kit is
    kept by the step: the same alternative with the same meaning, or one
    renamed without a change of meaning (ADR-020, decision 4). An empty list
    means comparable. A step of the house is judged apart: a changed default
    changes a decision's value, which the kit's records already hold.
    """
    found = []
    for record in records:
        if not isinstance(record, dict) or str(record.get("id", "")).startswith("custom:"):
            continue
        _, how = migrate(record, new)
        if how != "kept" and not how.startswith("renamed"):
            found.append(f"{record.get('id')} ({record.get('unit')}): {how}")
    return found
