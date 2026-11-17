"""The reading score (PLAN.md section 9.1): a candidate's decision records against gold.

A run submits decision records (`out/decisions.jsonl`), the questions it
asked (`out/questions.jsonl`) and what it could not map
(`out/unmapped.jsonl`); section 11.1. This module compares them with the
gold decision records of a kit. It builds nothing and reads no study data.

Scope. A slice or a stage scores a list of units (ADR-005, decisions 1 and
2). Gold records of other units are not scored. Candidate records of other
units are counted and ignored.

A decision the candidate leaves out (ADR-005, decision 3) takes the house
default: its value, the status `default`, the class `house_default` and the
citation of the standards document. A decision without a default stays
open: no value and no status.

Dimensions, each per decision:

    value     the value is the gold value, exactly: the alternative and
              every slot
    status    the status is the gold status
    citation  `quote`: the record cites, and every quote stands in the
              document it names; `span`: one citation names an anchor that
              gold cites, with a quote that stands inside the text of that
              anchor
    asks      precision and recall of the questions asked, against the
              decisions whose gold status is `asked`
    unmapped  precision and recall of what is listed as unmapped, by
              document and anchor, against the gold list

By class (section 4.5):

    document_rule, house_default   scored on value, status and citation
    study_input                    scored as a question asked, not as a
                                   guess: its value counts only when the
                                   decision was asked
    gold_quirk                     never rewarded: counted, not scored
    no_gold                        excluded and counted

A decision that gold marks `unseparated` is scored like any other here: its
values are compared. The report lists it apart, because no result can
confirm the comparison (sections 4.7 and 9.3).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

Key = tuple[str, str]  # (entry ID, unit)
CITED = ("document_rule", "house_default")
SCORED = (*CITED, "study_input")
COUNTED_ONLY = ("gold_quirk", "no_gold")
DIMENSIONS = ("value", "status", "quote", "span")


def key_of(record: dict) -> Key:
    return (str(record.get("id")), str(record.get("unit")))


def _normal(value: object) -> object:
    """A value with whole floats as integers, so that 30 and 30.0 are one value."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {str(key): _normal(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_normal(item) for item in value]
    return value


def same_value(one: object, two: object) -> bool:
    """Two decision values are the same alternative with the same slots."""
    return json.dumps(_normal(one), sort_keys=True) == json.dumps(_normal(two), sort_keys=True)


def _squeeze(text: str) -> str:
    return " ".join(text.split())


@dataclass(frozen=True)
class Documents:
    """The documents a citation may name, by ID, as text.

    An anchor is written `[<anchor>]` at the start of a line (the standard
    form, `specfirst.compile.standard_form`). Its span is the text of that
    line after the anchor, with the lines that follow up to the next empty
    line. Blanks and line breaks never count: a quote stands in a text when
    its words stand there in a row.
    """

    texts: dict[str, str] = field(default_factory=dict)

    def has(self, doc: str, quote: str) -> bool:
        return doc in self.texts and bool(_squeeze(quote)) and (
            _squeeze(quote) in _squeeze(self.texts[doc]))

    def span(self, doc: str, anchor: str) -> str | None:
        """The text of an anchor, or None when the document has no such anchor."""
        if doc not in self.texts:
            return None
        lines = self.texts[doc].split("\n")
        mark = f"[{anchor}]"
        for number, line in enumerate(lines):
            if line.startswith(mark + " ") or line == mark:
                taken = [line[len(mark):]]
                for later in lines[number + 1:]:
                    if not later.strip():
                        break
                    taken.append(later)
                return _squeeze(" ".join(taken))
        return None

    def in_span(self, doc: str, anchor: str, quote: str) -> bool:
        span = self.span(doc, anchor)
        return span is not None and bool(_squeeze(quote)) and _squeeze(quote) in span


@dataclass
class DecisionScore:
    """One gold decision of the scope, and how the candidate did on it."""

    key: Key
    gold_class: str
    gold_status: str
    source: str  # given | default | open: where the candidate's record comes from
    status: str | None  # the candidate's status
    asked: bool
    identifiable: str | None  # gold: separated | unseparated | None
    gold_value: object = None
    value_given: object = None
    # None: the dimension is not scored for this decision.
    value: bool | None = None
    status_ok: bool | None = None
    quote: bool | None = None
    span: bool | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def scored(self) -> bool:
        return self.gold_class in SCORED

    def marks(self) -> dict[str, bool | None]:
        return {"value": self.value, "status": self.status_ok, "quote": self.quote,
                "span": self.span}


@dataclass
class Rate:
    """Precision and recall of a list against the gold list."""

    given: int
    gold: int
    hits: int

    @property
    def precision(self) -> float | None:
        return self.hits / self.given if self.given else None

    @property
    def recall(self) -> float | None:
        return self.hits / self.gold if self.gold else None

    @property
    def exact(self) -> bool:
        return self.given == self.gold == self.hits


@dataclass
class Reading:
    """The reading score of one candidate on one kit."""

    units: tuple[str, ...]
    decisions: list[DecisionScore]
    asks: Rate
    unmapped: Rate
    outside: list[Key] = field(default_factory=list)  # candidate records outside the scope
    unknown: list[Key] = field(default_factory=list)  # candidate records gold does not have
    problems: list[str] = field(default_factory=list)  # records that could not be used

    def counts(self, by: str = "class") -> list[dict]:
        """Per class, per unit or per both: how many decisions, and how many right
        in each dimension, with the number each dimension was scored on."""
        groups: dict[tuple, dict] = {}
        for item in self.decisions:
            name = {"class": (item.gold_class,), "unit": (item.key[1],),
                    "both": (item.gold_class, item.key[1])}[by]
            row = groups.setdefault(name, {"decisions": 0, "scored": 0, **{
                f"{d}{suffix}": 0 for d in DIMENSIONS for suffix in ("", "_of")}})
            row["decisions"] += 1
            row["scored"] += item.scored
            for dimension, mark in item.marks().items():
                if mark is not None:
                    row[f"{dimension}_of"] += 1
                    row[dimension] += mark
        keys = ("class",) if by == "class" else ("unit",) if by == "unit" else ("class", "unit")
        return [{**dict(zip(keys, name, strict=True)), **row}
                for name, row in sorted(groups.items())]

    def wrong(self) -> list[DecisionScore]:
        """The decisions a reviewer would have to change (decision 22): a scored
        decision whose value is not the gold value."""
        return [item for item in self.decisions if item.value is False]

    def total(self, dimension: str) -> tuple[int, int]:
        marks = [item.marks()[dimension] for item in self.decisions]
        return sum(1 for mark in marks if mark), sum(1 for mark in marks if mark is not None)

    @property
    def perfect(self) -> bool:
        """Every scored dimension of every decision is right; the asks and the
        unmapped list are exactly the gold lists; no record was unusable."""
        return (all(mark is not False for item in self.decisions
                    for mark in item.marks().values())
                and self.asks.exact and self.unmapped.exact and not self.problems
                and not self.unknown)


def effective(candidate: list[dict], defaults: dict[Key, dict],
              keys: list[Key]) -> tuple[dict[Key, tuple[str, dict | None]], list[str]]:
    """The record that stands for every key: (source, record), and what is wrong.

    source is `given` for a record of the candidate, `default` for the house
    default that stands in for a record left out, `open` when neither is
    there. Of two records for one key the first is taken and the second is
    a problem.
    """
    problems: list[str] = []
    given: dict[Key, dict] = {}
    for record in candidate:
        key = key_of(record)
        if key in given:
            problems.append(f"{key[0]} ({key[1]}): more than one record; the first is taken")
            continue
        given[key] = record
    found: dict[Key, tuple[str, dict | None]] = {}
    for key in keys:
        if key in given:
            found[key] = ("given", given[key])
        elif key in defaults:
            found[key] = ("default", defaults[key])
        else:
            found[key] = ("open", None)
    return found, problems


def _citations(record: dict | None) -> list[dict]:
    listed = (record or {}).get("citations")
    return [item for item in listed if isinstance(item, dict)] if isinstance(listed, list) else []


def score(gold: list[dict], candidate: list[dict], defaults: dict[Key, dict],
          units: tuple[str, ...], documents: Documents | None = None,
          asked: set[Key] | None = None, unmapped: set[tuple[str, str]] | None = None,
          gold_unmapped: set[tuple[str, str]] | None = None) -> Reading:
    """Score a candidate's decision records against the gold records of the scope.

    `defaults` holds the record that stands in for a decision the candidate
    leaves out (`specfirst.compile.house.default_decisions`, by key).
    `asked` are the decisions the candidate asked about; `unmapped` what it
    listed as unmapped, as (document, anchor); `gold_unmapped` what the
    catalog truly lacks in the documents of the kit.
    """
    documents = documents or Documents()
    asked = set(asked or ())
    in_scope = [record for record in gold if record.get("unit") in units]
    keys = [key_of(record) for record in in_scope]
    stand, problems = effective(candidate, defaults, keys)
    scores = []
    for record in in_scope:
        key = key_of(record)
        source, ours = stand[key]
        gold_class = str(record.get("class") or "")
        item = DecisionScore(
            key=key, gold_class=gold_class, gold_status=str(record.get("status")),
            source=source, status=(ours or {}).get("status"), asked=key in asked,
            identifiable=record.get("identifiable"), gold_value=record.get("value"),
            value_given=(ours or {}).get("value"))
        if gold_class in SCORED:
            equal = ours is not None and same_value(ours.get("value"), record.get("value"))
            item.status_ok = item.status == item.gold_status
            if gold_class == "study_input":
                # A value nobody was asked for is a guess, right or not.
                item.value = equal and item.asked
                if equal and not item.asked:
                    item.notes.append("the gold value, but not asked: a guess")
            else:
                item.value = equal
        if gold_class in CITED:
            cited = _citations(ours)
            anchors = {(c.get("doc"), c.get("anchor")) for c in _citations(record)}
            item.quote = bool(cited) and all(
                documents.has(str(c.get("doc")), str(c.get("quote"))) for c in cited)
            # Gold that cites nothing gives no span to hold a citation against.
            item.span = any(
                (c.get("doc"), c.get("anchor")) in anchors
                and documents.in_span(str(c.get("doc")), str(c.get("anchor")),
                                      str(c.get("quote")))
                for c in cited) if anchors else None
            for c in cited:
                if not documents.has(str(c.get("doc")), str(c.get("quote"))):
                    item.notes.append(f"the quote is not in the document '{c.get('doc')}'")
                elif anchors and (c.get("doc"), c.get("anchor")) not in anchors:
                    item.notes.append(f"cites {c.get('doc')}#{c.get('anchor')}; gold cites "
                                      + ", ".join(f"{d}#{a}" for d, a in sorted(
                                          (str(d), str(a)) for d, a in anchors)))
        scores.append(item)
    gold_asks = {key_of(record) for record in in_scope if record.get("status") == "asked"}
    scoped_asks = {key for key in asked if key[1] in units}
    given_unmapped = set(unmapped or ())
    wanted_unmapped = set(gold_unmapped or ())
    known = {key_of(record) for record in gold}
    return Reading(
        units=tuple(units), decisions=scores,
        asks=Rate(len(scoped_asks), len(gold_asks), len(scoped_asks & gold_asks)),
        unmapped=Rate(len(given_unmapped), len(wanted_unmapped),
                      len(given_unmapped & wanted_unmapped)),
        outside=sorted({key_of(r) for r in candidate
                        if r.get("unit") not in units and key_of(r) in known}),
        unknown=sorted({key_of(r) for r in candidate if key_of(r) not in known}),
        problems=problems)


def ask_keys(records: list[dict], units_of: dict[str, tuple[str, ...]]) -> set[Key]:
    """The decisions a questions file asks about.

    A line names its decision as `decision`, and its unit as `unit` when
    the entry is answered once per table family. `units_of` gives the units
    of every catalog entry.
    """
    found: set[Key] = set()
    for record in records:
        entry = str(record.get("decision") or record.get("id") or "")
        units = units_of.get(entry, ())
        unit = record.get("unit") or (units[0] if len(units) == 1 else None)
        if entry and unit:
            found.add((entry, str(unit)))
    return found


def unmapped_keys(records: list[dict]) -> set[tuple[str, str]]:
    """What an unmapped file lists, as (document, anchor)."""
    return {(str(record.get("doc")), str(record.get("anchor"))) for record in records
            if record.get("doc") and record.get("anchor")}
