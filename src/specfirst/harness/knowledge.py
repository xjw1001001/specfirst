"""The reader's knowledge: the `core-reader` skill and the reading notes v0 of the units
(PLAN.md section 10; docs/decisions/ADR-010.md, decision 10).

    skills/core-reader/SKILL.md   the shared procedure, written by hand
    skills/<unit>/SKILL.md        reading notes v0 of a unit, rendered from the catalog
                                  and the house of the default pair: for every entry of
                                  the unit its question, its alternatives with their
                                  statements, the house default (from catalog@2 the
                                  house's, ADR-020) and its reading note
                                  (standard/catalog@<n>/knowledge/)

Both are Agent Skill folders: a SKILL.md whose front matter names the skill
and says what it is for (the format of pharma-skills, PLAN.md E16).

`problems` holds the committed notes against their rendering and against
the leak check of section 11.4: no skill may hold a kit ID, a study ID, a
subject ID or the seed of a kit, or a paragraph of the store of model text.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from specfirst.compile import house as houses
from specfirst.compile.catalog import Catalog
from specfirst.gen import kits as genkits
from specfirst.harness import task as tasks

# The units of the slice of ADR-005 whose reading notes read-2a writes.
UNITS = ("mod-treatment", "mod-populations", "mod-ae-emergence", "tfl-ae-summary")
MIN_PARAGRAPH = 40  # a paragraph of the store at least this long is a leak when quoted


def _note_body(text: str) -> list[str]:
    """A reading note without its title line, its headings one level down."""
    lines = text.rstrip("\n").split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    return [("#" + line) if line.startswith("## ") else line for line in lines]


def _slots(value: dict) -> str:
    return "".join(f", {name} {value[name]}" for name in value if name != "rule")


def house_default(catalog: Catalog, house: houses.House, entry_id: str,
                  unit: str) -> tuple[set[str], str]:
    """The alternatives the house takes by default for a question, and the words that
    say so: one default, one per case of the design, or none."""
    if houses.by_design(catalog, house, entry_id, unit):
        cases = houses.choices(house, entry_id, unit, catalog.entry(entry_id).per_family)
        parts = []
        for case in cases:
            value = {"rule": case["rule"], **(case.get("values") or {})}
            when = (f"for a study where {case['when']} holds" if "when" in case
                    else "for any other study")
            parts.append(f"`{case['rule']}`{_slots(value)} {when}")
        return ({case["rule"] for case in cases},
                "it depends on the design: " + "; ".join(parts) + ".")
    value = houses.default_value(catalog, house, entry_id, unit)
    if value is None:
        return set(), "none. A document states it, or it is asked."
    return {value["rule"]}, f"`{value['rule']}`{_slots(value)}."


def render_unit(catalog: Catalog, house: houses.House, unit: str) -> str:
    """The reading notes v0 of a unit, from the catalog and the house."""
    title = catalog.units[unit].title
    entries = [entry for entry in catalog.entries.values() if unit in entry.units]
    lines = [
        "---",
        f"name: {unit}",
        f"description: Reading notes v0 for the unit {unit} ({title}). For each of its "
        f"{len(entries)} catalog questions, where a protocol or a statistical analysis plan "
        "states the decision, the words to look for and the traps. Rendered from the "
        f"decision catalog {catalog.name} {catalog.version} and the house standard "
        f"{house.label}.",
        "---",
        "",
        f"# {title} ({unit}): reading notes v0",
        "",
        f"Rendered from the decision catalog `{catalog.name}` version {catalog.version} and "
        f"the house standard `{house.label}` by "
        "`specfirst run skills --write`; do not edit by hand. Read `core-reader` first: it "
        "says how to record a decision. Here, for every question of the unit: its "
        "alternatives with the statement each gives, the house default, and where documents "
        "state it.",
        "",
        "Questions of this unit: " + ", ".join(f"`{entry.id}`" for entry in entries) + ".",
    ]
    for entry in entries:
        defaults, said = house_default(catalog, house, entry.id, unit)
        lines += ["", f"## `{entry.id}`: {entry.question}", "", "Alternatives:", ""]
        for alternative in entry.alternatives:
            slots = ", ".join(slot.name for slot in alternative.slots)
            mark = " (the house default)" if alternative.id in defaults else ""
            lines.append(f"- `{alternative.id}`{mark}" + (f", slots {slots}" if slots else "")
                         + f": \"{alternative.statement}\"")
            if alternative.definition:
                lines.append(f"  Meaning: {' '.join(alternative.definition.split())}")
        lines += ["", "House default: " + said, ""]
        note = catalog.directory / entry.reading if entry.reading else None
        if note is not None and note.is_file():
            lines += _note_body(note.read_text(encoding="ascii"))
    return "\n".join(lines) + "\n"


def write(root: Path) -> list[Path]:
    """Render the reading notes of the units into skills/<unit>/SKILL.md."""
    catalog, house = houses.load_pair(root)
    written = []
    for unit in UNITS:
        path = tasks.skill_path(root, unit)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_unit(catalog, house, unit), encoding="ascii", newline="\n")
        written.append(path)
    return written


def _front_matter(text: str) -> dict[str, str]:
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return {}
    head = text[4:text.index("\n---\n", 4)]
    found = {}
    for line in head.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            found[key.strip()] = value.strip()
    return found


def format_problems(name: str, text: str) -> list[str]:
    """Why a SKILL.md is not an Agent Skill of this name."""
    meta = _front_matter(text)
    found = []
    if meta.get("name") != name:
        found.append(f"{name}: the front matter names '{meta.get('name')}'")
    if not meta.get("description"):
        found.append(f"{name}: the front matter has no description")
    return found


def secrets_of(kit_dir: Path, seed: str | None = None) -> list[str]:
    """What a kit holds that no skill may name: its ID, its study ID, its subject IDs
    (visible and twin), its seed."""
    manifest = genkits.read_manifest(kit_dir)
    found = {str(manifest["id"]), str(manifest["study"]["id"])}
    for sdtm in ("inputs/data/sdtm", "twin/data/sdtm"):
        path = kit_dir / sdtm / "dm.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            names = [column["name"] for column in data.get("columns") or []]
            if "USUBJID" in names:
                index = names.index("USUBJID")
                found |= {str(row[index]) for row in data.get("rows") or []}
    if seed:
        found.add(seed)
    return sorted(found)


def store_paragraphs(store: Path) -> list[str]:
    """The accepted paragraphs and the filler of the store of model text."""
    found = []
    for name in ("paragraphs.jsonl", "filler.jsonl"):
        path = store / name
        if not path.is_file():
            continue
        for line in path.read_text(encoding="ascii").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if "attempts" in record:
                found += [attempt["text"] for attempt in record["attempts"]
                          if attempt.get("n") == record.get("accepted")]
            elif record.get("text"):
                found.append(record["text"])
    return found


def _squeeze(text: str) -> str:
    return " ".join(text.split())


def leaks(text: str, secrets: list[str], paragraphs: list[str]) -> list[str]:
    """What a skill names that it must not: a secret as a whole word, or a paragraph of
    the store of model text (section 11.4)."""
    found = []
    for secret in secrets:
        if re.search(rf"(?<![A-Za-z0-9]){re.escape(secret)}(?![A-Za-z0-9])", text,
                     flags=re.IGNORECASE):
            found.append(f"names '{secret}'")
    squeezed = _squeeze(text)
    for paragraph in paragraphs:
        if len(_squeeze(paragraph)) >= MIN_PARAGRAPH and _squeeze(paragraph) in squeezed:
            found.append(f"quotes the paragraph '{_squeeze(paragraph)[:60]}...'")
    return found


def catalog_text(catalog: Catalog) -> str:
    """Every statement and meaning of the catalog, blanks collapsed: what a skill may
    say because the catalog says it."""
    return "\n".join(_squeeze(text) for entry in catalog.entries.values()
                     for alternative in entry.alternatives
                     for text in (alternative.statement, alternative.definition) if text)


def problems(root: Path, secrets: list[str], paragraphs: list[str]) -> list[str]:
    """Why the skills of the checkout are not those the task builder may ship: a
    missing or malformed SKILL.md, notes that are not their rendering, a leak. A
    paragraph of the store that the catalog itself states (a rewrite that kept the
    statement) is no leak."""
    catalog, house = houses.load_pair(root)
    known = catalog_text(catalog)
    paragraphs = [p for p in paragraphs if _squeeze(p) not in known]
    found = []
    for name in (tasks.CORE, *UNITS):
        path = tasks.skill_path(root, name)
        if not path.is_file():
            found.append(f"{name}: no {path.relative_to(root).as_posix()}")
            continue
        text = path.read_text(encoding="ascii")
        found += format_problems(name, text)
        if name in UNITS and text != render_unit(catalog, house, name):
            found.append(f"{name}: SKILL.md is not the rendering of the catalog "
                         "(`specfirst run skills --write`)")
        found += [f"{name}: {leak}" for leak in leaks(text, secrets, paragraphs)]
    return found
