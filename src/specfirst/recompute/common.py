"""What the Python and the R scripts share: literals, comments, the plan of a script."""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field

from specfirst.recompute.reading import Analysis, Condition, NotCovered, Where, first_sentence

WIDTH = 96  # the width of a comment line


def lit(text: str) -> str:
    """A string literal that Python and R read the same way (ASCII, JSON escapes)."""
    return json.dumps(str(text), ensure_ascii=True)


def num(value: float) -> str:
    """A number literal: the shortest text that reads back as the same number."""
    value = float(value)
    return str(int(value)) if value.is_integer() and abs(value) < 1e15 else repr(value)


def ascii_text(text: str) -> str:
    return str(text).encode("ascii", "backslashreplace").decode("ascii")


def comment(text: str, mark: str = "#") -> list[str]:
    """One comment, wrapped; continuation lines are indented."""
    lines = textwrap.wrap(ascii_text(" ".join(str(text).split())), WIDTH - len(mark) - 1,
                          subsequent_indent="  ", break_on_hyphens=False)
    return [f"{mark} {line}" for line in lines] or [mark]


def condition_words(condition: Condition) -> str:
    values = ", ".join(v if v != "" else "(missing)" for v in condition.values)
    if condition.comparator in ("IN", "NOTIN"):
        values = f"({values})"
    return f"{condition.dataset}.{condition.variable} {condition.comparator} {values}"


def where_words(where: Where | None) -> str:
    if where is None:
        return "none"
    if where.condition is not None:
        return condition_words(where.condition)
    if where.operator == "NOT":
        return f"NOT ({where_words(where.parts[0])})"
    return f" {where.operator} ".join(
        f"({where_words(p)})" if p.operator in ("AND", "OR") else where_words(p)
        for p in where.parts)


@dataclass
class Decisions:
    """The decision records of the kit, by the ARS element they bind."""

    by_element: dict[str, list[dict]] = field(default_factory=dict)
    used: set[str] = field(default_factory=set)

    def above(self, elements: list[str], mark: str = "#") -> list[str]:
        """The records that bind one of the elements and stand above no earlier step."""
        lines: list[str] = []
        for element in elements:
            for record in self.by_element.get(element, []):
                rid = str(record.get("id"))
                if rid in self.used:
                    continue
                self.used.add(rid)
                lines += comment(f"{rid} ({record.get('status')}): "
                                 f"{first_sentence(record.get('statement', ''))}", mark)
        return lines

    def bound(self, element: str) -> list[str]:
        return [str(r.get("id")) for r in self.by_element.get(element, [])]


def statement(registry: dict, method: str, starts: str) -> int:
    """The number of the registry statement of `method` that starts with `starts`."""
    for number, text in enumerate(registry[method]["semantics"], start=1):
        if " ".join(str(text).split()).startswith(starts):
            return number
    raise NotCovered(f"registry {method}: no statement starts with '{starts}'")


@dataclass
class Plan:
    """What a script is written to give: the plan entry of its analysis."""

    analysis: str
    event: str
    language: str  # python or r
    template: str
    file: str  # path in the bundle
    datasets: list[str]
    operations: dict[str, dict]  # ARS operation ID -> {method, operation, result}
    groupings: list[str]
    tolerance: float
    numbers: list[float]

    def record(self) -> dict:
        return {"analysis": self.analysis, "event": self.event, "language": self.language,
                "template": self.template, "file": self.file, "datasets": self.datasets,
                "operations": self.operations, "groupings": self.groupings,
                "tolerance": self.tolerance, "numbers": sorted(self.numbers)}


# How close a script's value must be to the ARD's (ADR-021, decision 6): closed-form
# arithmetic to a relative 1e-9; the mixed model, an iterative fit, to 1e-6, as its vectors.
TOLERANCE = 1e-9
TOLERANCE_ITERATIVE = 1e-6


def header(analysis: Analysis, kit_id: str, how: str, packages: str, mark: str = "#") -> list[str]:
    groupings = ", ".join(g.id for g in analysis.groupings) or "none"
    lines = comment(f"Recomputation of {analysis.id} ({analysis.name}), reporting event "
                    f"{analysis.event} of the kit {kit_id}.", mark)
    lines += comment("Written by `specfirst recompute` from the ARS analysis, its decision "
                     "records and the method registry (issue #29, ADR-021). It calls no part "
                     "of specfirst.", mark)
    lines += comment(f"Run: {how}", mark)
    lines += comment(f"Packages: {packages}.", mark)
    lines += comment("Output: one row per result: operation_id; per grouping "
                     f"({groupings}) the group ID, '=' and the value of a data-driven group, "
                     "or '*' for a compared grouping; the value at full precision, empty "
                     "when missing.", mark)
    return lines
