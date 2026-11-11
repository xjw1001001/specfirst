"""P2 for results, the classified differences, and the agreement of the two engines.

PLAN.md sections 4.6 and 4.8, rule R11.

A reference is an ARS file that carries results (`rawValue`). Our value is
compared with an embedded one at the precision the reference prints, in two
steps, because the reference drops trailing zeros ("70" for 70.0, "1" for a
p-value of 1.0000):

    printed   within half a unit of the last decimal of the raw value as it is
              printed. This is the comparison of evidence E2, and what
              "reproduced" counts.
    pattern   the same, but with at least as many decimals as the display
              pattern of the ARS operation has (`resultPattern`, "XX.X" for a
              mean): a raw value is at least as precise as its display.

Both allow a relative 1e-9 on top, for the floating error of two correct
computations (the tolerance of rule R11). A result that is reproduced as
printed but not at the precision of its pattern is a difference like any
other: the first step alone would hide half a unit of a value printed
without decimals. The comparison also lists the results that agree only on
the edge of the allowance.

Every difference needs exactly one entry in the kit's gold/exceptions.yaml,
with one class of section 4.8 and a proof. A proof names its kind, and this
module checks it against the built results:

    value_of_other_result  the embedded value is our value of another result
                           (two arms exchanged, E3)
    same_under_every       our value is the same under every value of a method
                           option, so no listed alternative gives the embedded one
    no_alternative         the other statistics of the same cell are reproduced,
                           and under no value of a method option is our value
                           the embedded one
    alternative            a build with another value of a method option gives
                           the embedded value (the proof of a rule_choice)
    no_records             the reference embeds no value, the engines give no
                           result, and the named counts are 0

A difference without an entry, an entry without a difference and a proof
that does not hold all fail the check.
"""

from __future__ import annotations

import copy
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from pathlib import Path
from urllib.parse import quote

import yaml

from specfirst import schemas
from specfirst.machine import ars
from specfirst.machine.canonical import write_jsonl
from specfirst.machine.registry import Registry

RELATIVE = 1e-9  # rule R11, and the floating allowance of the comparison with a reference
NOISE = 1e-12  # a relative difference below this is rounding of the last digits, not an edge
CLASSES = ("rule_choice", "reference_error", "data_difference")
PROOFS = ("value_of_other_result", "same_under_every", "no_alternative", "alternative",
          "no_records")
FORMAT = 0
_PATTERN_DECIMALS = re.compile(r"\.(X+)")

Rows = dict[str, dict]  # ARD rows by their ID


class ResultsError(ValueError):
    """The results, or the exceptions file, cannot be used."""


# ---- ARD files ------------------------------------------------------------------


def by_id(rows: list[dict]) -> Rows:
    found: Rows = {}
    for row in rows:
        if row.get("id") in found:
            raise ResultsError(f"two ARD rows have the ID {row.get('id')}")
        found[row["id"]] = row
    return found


def ard_problems(rows: list[dict], root: Path, limit: int = 20) -> list[str]:
    """Why rows are not a canonical ARD: the schema, the order, the IDs."""
    validator = schemas.validator("ard", root=root)
    problems = []
    for row in rows:
        for error in validator.iter_errors(row):
            problems.append(f"row {row.get('id')}: {error.message}")
            if len(problems) >= limit:
                return problems
    ids = [row.get("id") for row in rows]
    if None in ids:
        problems.append("a row has no id")
    elif ids != sorted(ids):
        problems.append("the rows are not sorted by id")
    problems += [f"id {key} is used {count} times" for key, count in Counter(ids).items()
                 if count > 1]
    return problems


def write_ard(path: Path, rows: list[dict], root: Path) -> None:
    """Write ARD rows as canonical JSON lines, after checking them."""
    problems = ard_problems(rows, root)
    if problems:
        raise ResultsError("not a valid ARD: " + "; ".join(problems))
    write_jsonl(path, rows)


# ---- the reference --------------------------------------------------------------


def reference_id(event: ars.Event, analysis: dict, result: dict) -> str:
    """The ID our ARD row has for an embedded result of an analysis."""
    stated = {group["groupingId"]: group for group in result.get("resultGroups") or []}
    parts = [quote(analysis["id"], safe=""), quote(result["operationId"], safe="")]
    for entry in event.groupings_of(analysis):
        group = stated.pop(entry["groupingId"], {})
        if group.get("groupId") is not None:
            parts.append(quote(group["groupId"], safe=""))
        elif group.get("groupValue") is not None:
            parts.append("=" + quote(group["groupValue"], safe=""))
        else:
            parts.append("*")
    if stated:
        raise ResultsError(f"analysis {analysis['id']}: a result names the grouping "
                           f"{', '.join(sorted(stated))}, which the analysis does not have")
    return "ard:" + "/".join(parts)


def pattern_decimals(pattern: object) -> int:
    """The decimals a result pattern shows: 1 for "XX.X", 2 for "(XX.XX)", 0 for "XX"."""
    found = _PATTERN_DECIMALS.search(pattern) if isinstance(pattern, str) else None
    return len(found.group(1)) if found else 0


@dataclass(frozen=True)
class Embedded:
    printed: str  # the raw value as the reference prints it; "" when it has none
    decimals: int  # of the display pattern of its operation
    analysis_id: str
    operation_id: str
    cell: frozenset  # its groups, to find the other results of the same cell


def embedded(event: ars.Event) -> dict[str, Embedded]:
    """The results a reporting event carries, by the ID of our ARD row."""
    found: dict[str, Embedded] = {}
    for analysis in event.analyses.values():
        for result in analysis.get("results") or []:
            key = reference_id(event, analysis, result)
            if key in found:
                raise ResultsError(f"the reference has two results for {key}")
            operation = event.operations.get(result["operationId"], ("", {}))[1]
            cell = frozenset((group["groupingId"], group.get("groupId"), group.get("groupValue"))
                             for group in result.get("resultGroups") or [])
            found[key] = Embedded(str(result.get("rawValue") or ""),
                                  pattern_decimals(operation.get("resultPattern")),
                                  analysis["id"], result["operationId"], cell)
    return found


def state(printed: str, value: float | int | None, decimals: int = 0) -> str:
    """How our value stands to a printed one: match, edge, coarse or differ.

    differ  not within half a unit of the last printed decimal
    coarse  within that, but not at the precision of `decimals`
    edge    equal, but on the boundary of the half unit or beyond it by more
            than floating noise: it agrees only by the allowance
    match   equal, inside the half unit; or neither side has a value
    """
    if printed == "" and value is None:
        return "match"
    if printed == "" or value is None:
        return "differ"
    try:
        reference = Decimal(printed)
    except InvalidOperation:
        return "differ"
    if not reference.is_finite():
        return "differ"
    ours = Decimal(repr(value)) if isinstance(value, float) else Decimal(value)
    difference = abs(ours - reference)
    allowance = Decimal(repr(RELATIVE)) * max(abs(ours), abs(reference))
    as_printed = Decimal(5).scaleb(reference.as_tuple().exponent - 1)
    if difference > as_printed + allowance:
        return "differ"
    half = min(as_printed, Decimal(5).scaleb(-decimals - 1))
    if difference > half + allowance:
        return "coarse"
    noise = allowance * Decimal(repr(NOISE / RELATIVE))
    on_the_boundary = difference >= half * (1 - Decimal("1e-6"))
    return "edge" if on_the_boundary and difference > noise else "match"


def equal(printed: str, value: float | int | None, decimals: int = 0) -> bool:
    """Our value is the printed one, at the precision of the pattern too."""
    return state(printed, value, decimals) in ("match", "edge")


@dataclass
class Comparison:
    reference: dict[str, Embedded] = field(default_factory=dict)
    reproduced: int = 0  # as printed: the count of evidence E2
    edge: list[tuple[str, str, object]] = field(default_factory=list)  # equal, at the edge
    coarse: dict[str, tuple[str, object]] = field(default_factory=dict)  # as printed only
    differing: dict[str, tuple[str, object]] = field(default_factory=dict)  # id -> (printed, ours)
    absent: dict[str, str] = field(default_factory=dict)  # id -> printed; we have no such row
    extra: Counter = field(default_factory=Counter)  # our rows the reference lacks, by analysis

    @property
    def total(self) -> int:
        return len(self.reference)

    @property
    def open(self) -> dict[str, tuple[str, object]]:
        """Every embedded result that needs a class: id -> (printed, ours or None)."""
        return {**self.differing, **self.coarse,
                **{key: (printed, None) for key, printed in self.absent.items()}}


def compare_reference(event: ars.Event, rows: Rows) -> Comparison:
    """Compare the results a reporting event embeds with our rows."""
    result = Comparison(reference=embedded(event))
    for key, item in result.reference.items():
        if key not in rows:
            result.absent[key] = item.printed
            continue
        value = rows[key]["raw_value"]
        found = state(item.printed, value, item.decimals)
        if found == "differ":
            result.differing[key] = (item.printed, value)
            continue
        result.reproduced += 1
        if found == "coarse":
            result.coarse[key] = (item.printed, value)
        elif found == "edge":
            result.edge.append((key, item.printed, value))
    result.extra = Counter(row["analysis_id"] for key, row in rows.items()
                           if key not in result.reference)
    return result


# ---- exceptions -----------------------------------------------------------------


def load_exceptions(path: Path) -> dict[str, list[dict]]:
    """Read gold/exceptions.yaml: result set -> entries. The shape is checked here."""
    with open(path, encoding="ascii") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict) or data.get("exceptions") != FORMAT:
        raise ResultsError(f"{path.name}: expected `exceptions: {FORMAT}`")
    sets = data.get("results")
    if not isinstance(sets, dict):
        raise ResultsError(f"{path.name}: 'results' must map a result set to its entries")
    problems = []
    for name, entries in sets.items():
        if not isinstance(entries, list):
            problems.append(f"{name}: expected a list of entries")
            continue
        seen = set()
        for i, entry in enumerate(entries):
            where = f"{name}[{i}]"
            if not isinstance(entry, dict):
                problems.append(f"{where}: expected a mapping")
                continue
            where = f"{name}: {entry.get('result', where)}"
            unknown = set(entry) - {"result", "embedded", "class", "proof", "sources"}
            if unknown:
                problems.append(f"{where}: unknown key {', '.join(sorted(unknown))}")
            if not isinstance(entry.get("result"), str) or not entry["result"].startswith("ard:"):
                problems.append(f"{where}: 'result' must be the ID of an ARD row")
            elif entry["result"] in seen:
                problems.append(f"{where}: listed twice")
            seen.add(entry.get("result"))
            if not isinstance(entry.get("embedded"), str):
                problems.append(f"{where}: 'embedded' must be the reference's value as text")
            if entry.get("class") not in CLASSES:
                problems.append(f"{where}: 'class' must be one of {', '.join(CLASSES)}")
            proof = entry.get("proof")
            if not isinstance(proof, dict) or proof.get("kind") not in PROOFS:
                problems.append(f"{where}: 'proof' needs a 'kind' out of {', '.join(PROOFS)}")
            if not isinstance(entry.get("sources", []), list):
                problems.append(f"{where}: 'sources' must be a list")
    if problems:
        raise ResultsError(f"{path.name}: " + "; ".join(problems))
    return {str(name): list(entries) for name, entries in sets.items()}


Alternative = Callable[[str, str, object], Rows]  # (registry method, option, value) -> our rows


def same(one: float | int | None, two: float | int | None) -> bool:
    """Two of our own values are one number, within the relative tolerance."""
    if one is None or two is None:
        return one is two
    return abs(one - two) <= RELATIVE * max(abs(one), abs(two))


def _proof_problem(entry: dict, rows: Rows, comparison: Comparison, registry: Registry,
                   alternative: Alternative) -> str | None:
    """Why the proof of an entry does not hold; None when it does."""
    proof, key = entry["proof"], entry["result"]
    kind, item = proof["kind"], comparison.reference[key]
    printed = item.printed
    ours = rows.get(key, {}).get("raw_value")
    if kind == "value_of_other_result":
        other = proof.get("result")
        if other not in rows or other == key:
            return f"the proof names {other!r}, which is not another of our results"
        if entry["class"] != "reference_error":
            return "a value of another result proves a reference_error only"
        if not equal(printed, rows[other]["raw_value"], item.decimals):
            return (f"the embedded value {printed} is not our value of {other} "
                    f"({rows[other]['raw_value']})")
        return None
    if kind in ("same_under_every", "no_alternative", "alternative"):
        method_id, option = proof.get("method"), proof.get("option")
        if method_id not in registry.methods or option not in registry.methods[method_id].options:
            return f"the registry has no option {method_id}.{option}"
        if key not in rows or rows[key]["method_id"] != method_id:
            return f"method {method_id} does not compute this result"
        values = registry.methods[method_id].options[option]["values"]
        if kind == "alternative":
            if entry["class"] != "rule_choice":
                return "an alternative proves a rule_choice only"
            if proof.get("value") not in values:
                return f"{proof.get('value')!r} is not a value of {method_id}.{option}"
            other = alternative(method_id, option, proof["value"]).get(key, {}).get("raw_value")
            if not equal(printed, other, item.decimals):
                return (f"with {option} = {proof['value']} our value is {other}, not the "
                        f"embedded {printed}")
            return None
        if entry["class"] != "reference_error":
            return "a value that no alternative gives proves a reference_error only"
        for value in values:
            other = alternative(method_id, option, value).get(key, {}).get("raw_value")
            if kind == "same_under_every" and not same(other, ours):
                return f"with {option} = {value} our value is {other}, not {ours}"
            if equal(printed, other, item.decimals):
                return f"with {option} = {value} our value is the embedded {printed}"
        if kind == "no_alternative":
            # The other statistics of the cell agree, so the data are the same.
            others = [other for other, there in comparison.reference.items()
                      if other != key and there.analysis_id == item.analysis_id
                      and there.cell == item.cell]
            if not others:
                return "the reference has no other result of the same cell"
            for other in others:
                if other in comparison.open:
                    return f"{other}, of the same cell, is not reproduced either"
        return None
    # no_records
    if printed != "":
        return f"the reference embeds the value {printed}"
    if key in rows:
        return "our engines give a result"
    zero = proof.get("zero") or []
    if not zero:
        return "the proof names no count that shows there are no records"
    for other in zero:
        if other not in rows or rows[other]["raw_value"] != 0:
            return f"{other} is not a count of 0 among our results"
    return None


def check_exceptions(comparison: Comparison, entries: list[dict], rows: Rows, registry: Registry,
                     alternative: Alternative) -> tuple[list[str], list[str]]:
    """Every difference has one entry whose proof holds, and every entry is a difference."""
    lines, problems = [], []
    open_results = comparison.open
    listed = {entry["result"]: entry for entry in entries}
    classes = Counter()
    for key, (printed, ours) in sorted(open_results.items()):
        entry = listed.get(key)
        if entry is None:
            problems.append(f"{key}: embedded {printed or '(no value)'}, ours {ours}: a "
                            "difference with no class")
            continue
        if entry["embedded"] != printed:
            problems.append(f"{key}: the entry says the reference embeds {entry['embedded']!r}, "
                            f"it embeds {printed!r}")
            continue
        problem = _proof_problem(entry, rows, comparison, registry, alternative)
        if problem:
            problems.append(f"{key}: the proof ({entry['proof']['kind']}) does not hold: "
                            f"{problem}")
            continue
        classes[(entry["class"], entry["proof"]["kind"])] += 1
    for key in sorted(set(listed) - set(open_results)):
        problems.append(f"{key}: listed as an exception, but it is reproduced or not a result "
                        "of the reference")
    for (name, kind), count in sorted(classes.items()):
        lines.append(f"  explained: {count:3d} {name}, proof {kind}")
    return lines, problems


def exchanged(event: ars.Event, comparison: Comparison, rows: Rows) -> Counter:
    """Differences that look like groups exchanged: grouping ID -> number of results.

    A differing result counts for a grouping when the embedded value is our
    value of the same analysis and operation in another group of that
    grouping. This attributes a difference; it proves nothing by itself.
    """
    found: Counter = Counter()
    for key, (printed, _) in comparison.differing.items():
        parts = key[len("ard:"):].split("/")
        item = comparison.reference[key]
        analysis = event.analyses.get(item.analysis_id)
        if analysis is None:
            continue
        for position, entry in enumerate(event.groupings_of(analysis), start=2):
            grouping = event.groupings[entry["groupingId"]]
            others = [quote(group["id"], safe="") for group in grouping.get("groups") or []]
            if position >= len(parts) or parts[position] not in others:
                continue
            for other in others:
                candidate = "ard:" + "/".join([*parts[:position], other, *parts[position + 1:]])
                if other != parts[position] and candidate in rows and equal(
                        printed, rows[candidate]["raw_value"], item.decimals):
                    found[grouping["id"]] += 1
                    break
    return found


# ---- the two engines ------------------------------------------------------------


def agreement(first: Rows, second: Rows, names: tuple[str, str] = ("Python", "R"),
              tolerance: float = RELATIVE) -> tuple[list[str], list[str]]:
    """Rule R11: the same rows, the same stamps, and values within the relative tolerance."""
    problems = [f"{key}: only the {names[0]} engine has it"
                for key in sorted(set(first) - set(second))]
    problems += [f"{key}: only the {names[1]} engine has it"
                 for key in sorted(set(second) - set(first))]
    largest, compared = 0.0, 0
    for key in sorted(set(first) & set(second)):
        one, two = first[key], second[key]
        if ({k: v for k, v in one.items() if k != "raw_value"}
                != {k: v for k, v in two.items() if k != "raw_value"}):
            problems.append(f"{key}: the two engines stamp it differently")
            continue
        a, b = one["raw_value"], two["raw_value"]
        compared += 1
        if a is None or b is None:
            if a is not b:
                problems.append(f"{key}: {names[0]} {a}, {names[1]} {b}")
            continue
        scale = max(abs(a), abs(b))
        relative = abs(a - b) / scale if scale else 0.0
        largest = max(largest, relative)
        if relative > tolerance:
            problems.append(f"{key}: {names[0]} {a!r}, {names[1]} {b!r}, relative difference "
                            f"{relative:.1e}")
    lines = [f"engines: {compared} results in both, {len(problems)} disagree; largest relative "
             f"difference {largest:.1e} (allowed {tolerance:g})"]
    return lines, problems


# ---- the gold ARS ---------------------------------------------------------------


def raw_text(value: float | int | None) -> str | None:
    """A result as ARS `rawValue`: the shortest decimal that reads back as the same number."""
    if value is None:
        return None
    return repr(value) if isinstance(value, float) else str(value)


def with_results(event: ars.Event, rows: list[dict]) -> dict:
    """The reporting event with the results of every analysis replaced by ours.

    Raw values only: a formatted value is a display, and displays are built
    from the grid (PLAN.md section 7.2).
    """
    data = copy.deepcopy(event.data)
    regenerated: dict[str, list[dict]] = {}
    for row in sorted(rows, key=lambda r: r["id"]):
        groups, n = [], 1
        while f"group{n}_groupingId" in row:
            group = {"groupingId": row[f"group{n}_groupingId"]}
            if row.get(f"group{n}_groupId") is not None:
                group["groupId"] = row[f"group{n}_groupId"]
            if row.get(f"group{n}_groupValue") is not None:
                group["groupValue"] = row[f"group{n}_groupValue"]
            groups.append(group)
            n += 1
        result: dict[str, object] = {"operationId": row["operation_id"]}
        if groups:
            result["resultGroups"] = groups
        text = raw_text(row["raw_value"])
        if text is not None:
            result["rawValue"] = text
        regenerated.setdefault(row["analysis_id"], []).append(result)
    for analysis in data.get("analyses") or []:
        analysis["results"] = regenerated.get(analysis["id"], [])
    return data
