"""The standard form: decisions as uniform sentences (PLAN.md sections 4.4 and 6.6).

Each alternative of each catalog entry has one statement template. A
decision renders to exactly one statement, and a parser maps any statement
back to its decision without a model. Decisions to statements to decisions
is an exact round trip.

A standard-form document is Markdown. One section per unit, one line per
decision, each line starting with its anchor:

    ## 3 Adverse event emergence (mod-ae-emergence)

    [3/s2] Treatment emergence ends 30 days after the last dose date.

The anchor `3/s2` (section 3, statement 2) is what a citation names.

A document may instead anchor each statement by its entry, `[ae.teae.end]`,
or `[tfl.population/tfl-demographics]` for an entry answered per table
family, so that an anchor does not move when an entry is added (the house
standard from open-default@2, ADR-020 and #15). Such a document may also
state the fixed rules of an entry, `[ae.teae.start/no_start_date] <text>`,
which hold for every alternative and are not decisions, and a decision whose
value depends on the design, one numbered line per case,
`[pop.safety.rule/1] <statement>`, each after a line that says when it holds.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from specfirst.compile.catalog import Alternative, Catalog, Entry
from specfirst.compile.slots import Slot, SlotError, parse_value, render_value

OUTPUT_SLOT = "output"
_PLACEHOLDER = re.compile(r"\{([^{}]*)\}")
_ENTRY_ANCHOR = r"[a-z][a-z0-9_]*(?:\.[a-z0-9_]+)+(?:/[a-z0-9_-]+)*"
_ANCHORED = re.compile(r"^\[([0-9]+/s[0-9]+|" + _ENTRY_ANCHOR + r")\] (.*)$")
_ANCHOR = re.compile(r"\[(?:[0-9]+/s[0-9]+|" + _ENTRY_ANCHOR + r")\]")
_POSITION = re.compile(r"^[0-9]+/s[0-9]+$")
ANCHOR_STYLES = ("position", "entry")
# Lines of a document that say more about a statement; the parser skips them.
NOTE_PREFIXES = ("Meaning: ", "Source: ")
_CATALOG = re.compile(r"^Catalog: (\S+) (\S+)$")
_LEAD = re.compile(r"^[^A-Z]*")  # what may stand before the first capital letter of a line
_SECTION = re.compile(r"^## ([0-9]+) (.+) \(([a-z0-9-]+)\)$")
_DOCUMENT = re.compile(r"^Document: ([a-z][a-z0-9_-]*)$")
# What may continue a token of a type; the text after a slot must not start with it.
_CONTINUES = {
    "int": "0123456789",
    "number": "0123456789",
    "name": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_",
}


class StandardFormError(ValueError):
    """A decision cannot be rendered, or a statement or document cannot be parsed."""


@dataclass(frozen=True)
class Template:
    """A statement template, split into literal text and slots."""

    text: str
    tokens: tuple[tuple[str, object], ...]  # ("text", str) | ("slot", Slot) | ("output", None)

    @property
    def slot_names(self) -> list[str]:
        return [token.name for kind, token in self.tokens if kind == "slot"]

    @property
    def has_output(self) -> bool:
        return any(kind == "output" for kind, _ in self.tokens)

    def skeleton(self) -> str:
        """The template with every slot replaced by its type: equal skeletons are ambiguous."""
        parts = []
        for kind, token in self.tokens:
            parts.append(token if kind == "text" else "{output}" if kind == "output"
                         else "{" + token.type + "}")
        return "".join(parts)


def compile_template(alternative: Alternative) -> Template:
    """Split a statement into its tokens. Unknown slots raise StandardFormError."""
    tokens: list[tuple[str, object]] = []
    pos = 0
    text = alternative.statement
    for match in _PLACEHOLDER.finditer(text):
        if match.start() > pos:
            tokens.append(("text", text[pos : match.start()]))
        name = match.group(1)
        if name == OUTPUT_SLOT:
            tokens.append(("output", None))
        else:
            try:
                tokens.append(("slot", alternative.slot(name)))
            except KeyError:
                raise StandardFormError(
                    f"the statement uses the undeclared slot '{name}'"
                ) from None
        pos = match.end()
    if pos < len(text):
        tokens.append(("text", text[pos:]))
    for kind, token in tokens:
        if kind == "text" and ("{" in token or "}" in token):
            raise StandardFormError("the statement has a stray brace")
    return Template(text=text, tokens=tuple(tokens))


def template_problems(entry: Entry, alternative: Alternative) -> list[str]:
    """What is wrong with one statement template, by reading it alone."""
    where = f"{entry.id}/{alternative.id}"
    text = alternative.statement
    problems = []
    if not text:
        return [f"{where}: no statement"]
    if not text.isascii() or "\n" in text or "  " in text or text != text.strip():
        problems.append(f"{where}: the statement must be one line of ASCII with single spaces")
    if not text.endswith("."):
        problems.append(f"{where}: the statement must end with a full stop")
    if not text[0].isupper():
        problems.append(f"{where}: the statement must start with a capital letter")
    try:
        template = compile_template(alternative)
    except StandardFormError as error:
        return problems + [f"{where}: {error}"]
    used = template.slot_names
    for slot in alternative.slots:
        if used.count(slot.name) != 1:
            problems.append(f"{where}: slot '{slot.name}' must be used exactly once")
    outputs = sum(1 for kind, _ in template.tokens if kind == "output")
    if entry.per_family and outputs != 1:
        problems.append(f"{where}: an entry with `units` names its output once, as {{output}}")
    if not entry.per_family and outputs:
        problems.append(f"{where}: {{output}} belongs to entries with `units`")
    for index, (kind, token) in enumerate(template.tokens):
        if kind == "text":
            continue
        following = template.tokens[index + 1] if index + 1 < len(template.tokens) else None
        if index == 0:
            problems.append(f"{where}: the statement must not start with a slot")
        if following is None or following[0] != "text":
            problems.append(f"{where}: a slot must be followed by text")
            continue
        after = following[1]
        if kind == "output":
            continue
        scalar = token.item_type or token.type
        if after[0] in _CONTINUES.get(scalar, ""):
            problems.append(f"{where}: the text after slot '{token.name}' could continue its value")
        if scalar == "number" and after[0] == "." and after[1:2].isdigit():
            problems.append(f"{where}: the text after slot '{token.name}' reads as decimals")
        if scalar == "name" and after[0] == "." and after[1:2].isupper():
            problems.append(f"{where}: the text after slot '{token.name}' reads as a variable")
        if token.item_type and after.startswith(", "):
            problems.append(f"{where}: a comma after list slot '{token.name}' is ambiguous")
        if token.type == "records" and after.startswith("; "):
            problems.append(f"{where}: a semicolon after slot '{token.name}' is ambiguous")
    return problems


class StandardForm:
    """Render and parse the statements of one catalog."""

    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        self._templates: dict[tuple[str, str], Template] = {}
        self._broken: dict[tuple[str, str], str] = {}
        for entry in catalog.entries.values():
            for alternative in entry.alternatives:
                key = (entry.id, alternative.id)
                try:
                    self._templates[key] = compile_template(alternative)
                except StandardFormError as error:
                    self._broken[key] = str(error)

    # -- one statement -------------------------------------------------------

    def template(self, entry_id: str, rule: str) -> Template:
        key = (entry_id, rule)
        if key in self._broken:
            raise StandardFormError(f"{entry_id}/{rule}: {self._broken[key]}")
        if key not in self._templates:
            raise StandardFormError(f"the catalog has no alternative {entry_id}/{rule}")
        return self._templates[key]

    def check_value(self, entry_id: str, unit: str, value: object) -> Alternative:
        """Raise unless `value` is a complete value of an alternative of the entry."""
        if entry_id not in self.catalog.entries:
            raise StandardFormError(f"the catalog has no entry '{entry_id}'")
        entry = self.catalog.entries[entry_id]
        if unit not in entry.units:
            raise StandardFormError(f"{entry_id}: unit '{unit}' does not answer this entry")
        if not isinstance(value, dict) or not isinstance(value.get("rule"), str):
            raise StandardFormError(f"{entry_id}: a value is a mapping with a rule")
        try:
            alternative = entry.alternative(value["rule"])
        except KeyError as error:
            raise StandardFormError(str(error.args[0])) from None
        wanted = {slot.name for slot in alternative.slots}
        given = set(value) - {"rule"}
        if wanted != given:
            raise StandardFormError(
                f"{entry_id}/{alternative.id}: needs the slots {sorted(wanted)}, "
                f"got {sorted(given)}"
            )
        return alternative

    def render(self, entry_id: str, unit: str, value: dict) -> str:
        """The statement of a decision value."""
        alternative = self.check_value(entry_id, unit, value)
        template = self.template(entry_id, alternative.id)
        parts = []
        for kind, token in template.tokens:
            if kind == "text":
                parts.append(token)
            elif kind == "output":
                parts.append(self._phrase(unit))
            else:
                try:
                    parts.append(render_value(token, value[token.name]))
                except SlotError as error:
                    raise StandardFormError(f"{entry_id}/{alternative.id}: {error}") from None
        return "".join(parts)

    def _phrase(self, unit: str) -> str:
        phrase = self.catalog.units[unit].phrase if unit in self.catalog.units else ""
        if not phrase:
            raise StandardFormError(f"unit '{unit}' has no phrase to name its output")
        return phrase

    def _match(self, entry: Entry, alternative: Alternative, text: str) -> list[tuple[str, dict]]:
        """Every (unit, value) under which the template gives exactly `text`."""
        template = self._templates.get((entry.id, alternative.id))
        if template is None:
            return []
        found: list[tuple[str, dict]] = []

        def walk(index: int, pos: int, unit: str | None, value: dict) -> None:
            if index == len(template.tokens):
                if pos == len(text):
                    found.append((unit or entry.units[0], dict(value)))
                return
            kind, token = template.tokens[index]
            if kind == "text":
                if text.startswith(token, pos):
                    walk(index + 1, pos + len(token), unit, value)
            elif kind == "output":
                for candidate in entry.units:
                    known = self.catalog.units.get(candidate)
                    phrase = known.phrase if known else ""
                    if phrase and text.startswith(phrase, pos):
                        walk(index + 1, pos + len(phrase), candidate, value)
            else:
                slot: Slot = token
                try:
                    parsed, after = parse_value(slot, text, pos)
                except SlotError:
                    return
                walk(index + 1, after, unit, {**value, slot.name: parsed})

        walk(0, 0, None, {"rule": alternative.id})
        return found

    def matches(self, statement: str) -> list[tuple[str, str, dict]]:
        """Every (entry ID, unit, value) whose statement is exactly `statement`."""
        found = []
        for entry in self.catalog.entries.values():
            for alternative in entry.alternatives:
                for unit, value in self._match(entry, alternative, statement):
                    found.append((entry.id, unit, value))
        return found

    def parse(self, statement: str) -> tuple[str, str, dict]:
        """The decision a statement states. Raises unless there is exactly one."""
        found = self.matches(statement)
        if not found:
            raise StandardFormError(f"no template gives this statement: {statement}")
        if len(found) > 1:
            names = ", ".join(f"{entry_id}/{value['rule']} ({unit})"
                              for entry_id, unit, value in found)
            raise StandardFormError(f"ambiguous statement, it fits {names}: {statement}")
        return found[0]

    # -- documents -----------------------------------------------------------

    def order(self, records: list[dict]) -> list[dict]:
        """Records in document order: by unit, then by catalog entry."""
        units = list(self.catalog.units)
        entries = list(self.catalog.entries)

        def key(record: dict) -> tuple[int, int]:
            unit, entry_id = record["unit"], record["id"]
            if unit not in units or entry_id not in entries:
                raise StandardFormError(f"not a catalog decision: {entry_id} ({unit})")
            return units.index(unit), entries.index(entry_id)

        return sorted(records, key=key)

    def anchor_of(self, entry_id: str, unit: str) -> str:
        """The anchor of a decision in a document anchored by entry."""
        entry = self.catalog.entries[entry_id]
        return f"{entry_id}/{unit}" if entry.per_family else entry_id

    def render_document(
        self, doc: str, title: str, records: list[dict], preface: tuple[str, ...] = (),
        explain: bool = False, anchors: str = "position", after=None, fixed: bool = False,
        sections: tuple[tuple[str, tuple[str, ...]], ...] = (),
    ) -> str:
        """A standard-form document stating the given decisions, one anchor each.

        `records` need `id`, `unit` and `value`; in place of `value`, `cases`
        lists `{when, value}` for a decision that depends on the design (anchors
        by entry only). With `explain`, each statement is followed by a line
        "Meaning:" with the definition of its alternative and the notes of its
        entry; `after(record, value)` gives more such lines (they start with
        "Source: "). The parser skips them. With `anchors="entry"` every anchor
        names its entry, and with `fixed` the fixed rules of the entries of a
        unit follow its statements. `sections` are (heading, paragraphs) put
        before the first unit. Returns the Markdown text.
        """
        if anchors not in ANCHOR_STYLES:
            raise StandardFormError(f"anchors are one of {', '.join(ANCHOR_STYLES)}")
        if anchors == "position" and (fixed or any("cases" in r for r in records)):
            raise StandardFormError("fixed rules and cases need anchors by entry")
        if not _DOCUMENT.match(f"Document: {doc}"):
            raise StandardFormError(f"'{doc}' is not a document ID")
        seen = set()
        for record in records:
            key = (record["id"], record["unit"])
            if key in seen:
                raise StandardFormError(f"two decisions for {record['id']} ({record['unit']})")
            seen.add(key)
        lines = [f"# {title}", "", f"Document: {doc}",
                 f"Catalog: {self.catalog.name} {self.catalog.version}", ""]
        for paragraph in preface:
            lines += [paragraph, ""]
        for heading, paragraphs in sections:
            lines += [f"## {heading}", ""]
            for paragraph in paragraphs:
                lines += [paragraph, ""]
        section = 0
        current = None
        number = 0
        ordered = self.order(records)

        def explained(record: dict, value: dict) -> list[str]:
            found = []
            if explain:
                entry = self.catalog.entries[record["id"]]
                meaning = " ".join(" ".join(str(part).split()) for part in (
                    entry.alternative(value["rule"]).definition,
                    entry.raw.get("notes"),
                ) if part)
                if meaning:
                    found += [f"Meaning: {meaning}", ""]
            if after is not None:
                for line in after(record, value):
                    if not line.startswith(NOTE_PREFIXES):
                        raise StandardFormError(f"a note line starts with one of {NOTE_PREFIXES}")
                    found += [line, ""]
            return found

        def fixed_lines(unit: str) -> list[str]:
            found = []
            for entry in self.catalog.entries.values():
                if unit in entry.units and entry.fixed_rules and not (
                        entry.per_family and unit != entry.units[0]):
                    found += [f"Fixed rules of `{entry.id}`, for every alternative:", ""]
                    for rule in entry.fixed_rules:
                        said = " ".join(str(rule["text"]).split())
                        found += [f"[{entry.id}/{rule['id']}] {said}", ""]
            return found

        for index, record in enumerate(ordered):
            if record["unit"] != current:
                current = record["unit"]
                section += 1
                number = 0
                lines += [f"## {section} {self.catalog.units[current].title} ({current})", ""]
            number += 1
            if anchors == "position":
                anchor = f"{section}/s{number}"
            else:
                anchor = self.anchor_of(record["id"], record["unit"])
            if "cases" in record:
                for count, case in enumerate(record["cases"], start=1):
                    lines += [case["say"], ""]
                    statement = self.render(record["id"], record["unit"], case["value"])
                    lines += [f"[{anchor}/{count}] {statement}", ""]
                    lines += explained(record, case["value"])
            else:
                statement = self.render(record["id"], record["unit"], record["value"])
                lines += [f"[{anchor}] {statement}", ""]
                lines += explained(record, record["value"])
            last = index == len(ordered) - 1 or ordered[index + 1]["unit"] != current
            if fixed and last:
                lines += fixed_lines(current)
        return "\n".join(lines)

    def parse_document(self, text: str) -> tuple[str, list[dict]]:
        """The document ID and the decisions a standard-form document states.

        Every anchored line must be a statement of the catalog, in the section
        of its unit. Each record has `id`, `unit`, `value`, `statement` and
        `anchor`. The cases of a decision by design and the fixed rules are
        checked and left out (`parse_full` gives them).
        """
        doc, records, _, _ = self.parse_full(text)
        return doc, records

    def parse_full(self, text: str) -> tuple[str, list[dict], dict, list[str]]:
        """`parse_document`, with the cases by decision and the fixed rules stated.

        Cases: (entry, unit) -> the records of its numbered lines, in order.
        Fixed rules: the anchors `<entry>/<rule>`, each stated with its text.
        """
        doc = None
        cases: dict[tuple[str, str], list[dict]] = {}
        fixed: list[str] = []
        current_unit = None
        catalog = None
        section_unit: dict[str, str] = {}
        records: list[dict] = []
        seen: dict[tuple[str, str], str] = {}
        for number, line in enumerate(text.split("\n"), start=1):
            match = _DOCUMENT.match(line)
            if match:
                if doc is not None:
                    raise StandardFormError(f"line {number}: a second 'Document:' line")
                doc = match.group(1)
                continue
            match = _CATALOG.match(line)
            if match:
                catalog = (match.group(1), match.group(2))
                if catalog != (self.catalog.name, self.catalog.version):
                    raise StandardFormError(
                        f"line {number}: written for the catalog {' '.join(catalog)}, "
                        f"not for {self.catalog.name} {self.catalog.version}"
                    )
                continue
            match = _SECTION.match(line)
            if match:
                section_unit[match.group(1)] = match.group(3)
                current_unit = match.group(3)
                continue
            match = _ANCHORED.match(line)
            if not match:
                # A line that holds an anchor is a statement or an error: an
                # indented, bulleted or emphasized statement must not be lost.
                if line.startswith("[") or _ANCHOR.search(line):
                    raise StandardFormError(f"line {number}: not an anchored statement: {line}")
                bare = _LEAD.sub("", line).rstrip("*_` ")
                if bare and not line.startswith(("#", *NOTE_PREFIXES)) and self.matches(bare):
                    raise StandardFormError(f"line {number}: a statement without its anchor: "
                                            f"{line}")
                continue
            anchor, statement = match.groups()
            if not _POSITION.match(anchor):
                rule = self._fixed_rule(anchor)
                if rule is not None:
                    if " ".join(statement.split()) != " ".join(str(rule["text"]).split()):
                        raise StandardFormError(f"line {number}: the fixed rule {anchor} is not "
                                                "stated as the catalog states it")
                    if anchor in fixed:
                        raise StandardFormError(f"line {number}: anchor {anchor} is used twice")
                    fixed.append(anchor)
                    continue
            try:
                entry_id, unit, value = self.parse(statement)
            except StandardFormError as error:
                raise StandardFormError(f"line {number}: {error}") from None
            if _POSITION.match(anchor):
                section = anchor.split("/")[0]
                if section_unit.get(section) != unit:
                    raise StandardFormError(
                        f"line {number}: {entry_id} belongs to unit {unit}, not to section "
                        f"{section}")
            else:
                if current_unit != unit:
                    raise StandardFormError(
                        f"line {number}: {entry_id} belongs to unit {unit}, not to the section "
                        f"of {current_unit}")
                base = self.anchor_of(entry_id, unit)
                tail = anchor[len(base) + 1:] if anchor.startswith(base + "/") else ""
                if tail.isdigit():
                    found = cases.setdefault((entry_id, unit), [])
                    if int(tail) != len(found) + 1:
                        raise StandardFormError(f"line {number}: case {anchor} is out of order")
                    found.append({"id": entry_id, "unit": unit, "value": value,
                                  "statement": statement, "anchor": anchor})
                    continue
                if anchor != base:
                    raise StandardFormError(f"line {number}: the anchor {anchor} does not name "
                                            f"{base}")
            if anchor in seen.values():
                raise StandardFormError(f"line {number}: anchor {anchor} is used twice")
            if (entry_id, unit) in seen:
                raise StandardFormError(
                    f"line {number}: {entry_id} ({unit}) is stated twice, "
                    f"at {seen[(entry_id, unit)]} and {anchor}"
                )
            seen[(entry_id, unit)] = anchor
            records.append({"id": entry_id, "unit": unit, "value": value,
                            "statement": statement, "anchor": anchor})
        if doc is None:
            raise StandardFormError("the document has no 'Document: <id>' line")
        if catalog is None:
            raise StandardFormError("the document has no 'Catalog: <name> <version>' line")
        for key in cases:
            if key in seen:
                raise StandardFormError(f"{key[0]} ({key[1]}) is stated both alone and by cases")
        return doc, records, cases, fixed

    def _fixed_rule(self, anchor: str) -> dict | None:
        """The fixed rule an anchor `<entry>/<rule>` names, or None."""
        entry_id, _, rule_id = anchor.partition("/")
        entry = self.catalog.entries.get(entry_id)
        if entry is None or not rule_id or rule_id in entry.units:
            return None
        return next((rule for rule in entry.fixed_rules if rule.get("id") == rule_id), None)


def decision_record(parsed: dict, doc: str, status: str, decision_class: str) -> dict:
    """A decision record (schema version 0) for one parsed statement."""
    return {
        "id": parsed["id"],
        "unit": parsed["unit"],
        "value": parsed["value"],
        "status": status,
        "class": decision_class,
        "statement": parsed["statement"],
        "citations": [{"doc": doc, "anchor": parsed["anchor"], "quote": parsed["statement"]}],
    }
