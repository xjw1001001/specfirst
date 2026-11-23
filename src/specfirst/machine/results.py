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

Both allow a relative 1e-9 on top. It covers two things: the floating error
of two correct computations (the tolerance of rule R11), and a reference
value that was rounded to about ten significant digits before it was
embedded ("0.0771929825" for 0.07719298245614...). A result that is
reproduced as printed but not at the precision of its pattern is a
difference like any other: the first step alone would hide half a unit of a
value printed without decimals. The comparison also lists the results that
agree only on the edge of the allowance.

Every difference needs exactly one entry in the kit's gold/exceptions.yaml,
with one class of section 4.8 and a proof. A proof names its kind, and this
module checks it against the built results:

    value_of_other_result  two results are exchanged (two arms, E3): the embedded
                           value is our value of another result of the same
                           analysis and operation that differs in one group of
                           one grouping, and the reference's value of that
                           result is our value of this one
    same_under_every       our value is the same under every value of a method
                           option, so no listed alternative gives the embedded one
    no_alternative         the other statistics of the same cell are reproduced,
                           and under no value of a method option is our value
                           the embedded one
    alternative            a build with another value of a method option gives
                           the embedded value (the proof of a rule_choice)
    between_equal_values   our value is a quartile or a median, and the sorted
                           values of its cell between which every definition
                           of a sample quantile places it are all that value
    no_records             the reference embeds no value, the engines give no
                           result, and the named counts are 0: one count of
                           the cell's own groups per group the test compares

`same_under_every` and `between_equal_values` say what our values give; they
also ask that the n, the minimum and the maximum of the same cell are
embedded and reproduced, so that our cell holds the reference's data (review
of real-3a, F5: with a wrong population of ours, 36 wrong quartiles and
medians were accepted as errors of the reference).

A proof must say something about the reference, so three kinds are narrow
(review of real-2, finding F2). `same_under_every` and `no_alternative`
hold only for an option that changes some result of the same operation: a
mean is the same under every quantile definition, and that proves nothing.
Under the two quantile definitions of the registry a median never changes
(summary.continuous, statement 9), so no option proves anything about a
median; `between_equal_values` is the proof for one. It rests on Hyndman
and Fan (1996), "Sample quantiles in statistical packages": each of their
nine definitions, which include the five of SAS and the nine of R, gives a
value between x[j] and x[j + 1] with j = floor(n p + m), where m is from
-1/2 to 3/4 for p = 1/4, 1/2 and 3/4.

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

RELATIVE = 1e-9  # rule R11, and the allowance of the comparison with a reference
NOISE = 1e-12  # a relative difference below this is rounding of the last digits, not an edge
CLASSES = ("rule_choice", "reference_error", "data_difference")
PROOFS = ("value_of_other_result", "same_under_every", "no_alternative", "alternative",
          "between_equal_values", "no_records")
# The quantiles of summary.continuous in quarters: p = quarters / 4.
QUARTERS = {"q1": 1, "median": 2, "q3": 3}
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
    formatted: str | None = None  # the display of the value, where the reference has one


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
            formatted = result.get("formattedValue")
            found[key] = Embedded(str(result.get("rawValue") or ""),
                                  pattern_decimals(operation.get("resultPattern")),
                                  analysis["id"], result["operationId"], cell,
                                  formatted if isinstance(formatted, str) else None)
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


FORMAT_PROOFS = ("not_its_own_pattern", "half_in_floating_error")


def load_formats(path: Path) -> dict[str, dict[str, dict]]:
    """The `formats` section of gold/exceptions.yaml (issue #31): result set -> ARD row ->
    entry. A difference of display only: the reference's raw value is ours, and its
    formatted value is not that raw value under the pattern of its operation (proof
    `not_its_own_pattern`; specfirst.machine.grid.compare_reference holds it); or the
    reference's raw value lies on a half at the decimals of the pattern and ours is that
    value up to floating error, on the other side of the half (proof
    `half_in_floating_error`, class `data_difference`; real-3). An entry has `result`,
    `formatted` (the reference's text), `class` and `proof`, and may have `sources`."""
    with open(path, encoding="ascii") as handle:
        data = yaml.safe_load(handle) or {}
    sets = data.get("formats") or {}
    if not isinstance(sets, dict):
        raise ResultsError(f"{path.name}: 'formats' must map a result set to its entries")
    problems, found = [], {}
    for name, entries in sets.items():
        found[str(name)] = {}
        for i, entry in enumerate(entries if isinstance(entries, list) else [None]):
            where = f"formats of {name}[{i}]"
            if not isinstance(entry, dict) or not {"result", "formatted", "class", "proof"} <= \
                    set(entry) <= {"result", "formatted", "class", "proof", "sources"}:
                problems.append(f"{where}: an entry has result, formatted, class and proof, "
                                "and may have sources")
                continue
            if not str(entry["result"]).startswith("ard:") or entry["result"] in found[str(name)]:
                problems.append(f"{where}: 'result' must be the ID of an ARD row, once")
            if not isinstance(entry["formatted"], str):
                problems.append(f"{where}: 'formatted' must be the reference's text")
            if entry["class"] not in CLASSES:
                problems.append(f"{where}: 'class' must be one of {', '.join(CLASSES)}")
            if not isinstance(entry["proof"], dict) or entry["proof"].get("kind") not in \
                    FORMAT_PROOFS:
                problems.append(f"{where}: 'proof' needs a 'kind' out of "
                                f"{', '.join(FORMAT_PROOFS)}")
            found[str(name)][str(entry["result"])] = entry
    if problems:
        raise ResultsError(f"{path.name}: " + "; ".join(problems))
    return found


Alternative = Callable[[str, str, object], Rows]  # (registry method, option, value) -> our rows
Group = tuple[str, str | None]  # ("id", group ID), ("value", group value) or ("all", None)


def _nothing(_: str) -> None:
    return None


@dataclass(frozen=True)
class Evidence:
    """What a proof may ask for beyond the rows of the build.

    alternative      our rows under another value of a method option
    cell_values      for a result of summary.continuous: its registry
                     operation and the sorted values of its cell; None for
                     any other result
    compared_groups  for an analysis with an occurrence test: the groups of
                     its compared grouping that the test compares, that is,
                     those with subjects in its population (rules I12b and
                     I13); None for any other analysis
    """

    alternative: Alternative
    cell_values: Callable[[str], tuple[str, list[float]] | None] = _nothing
    compared_groups: Callable[[str], list[Group] | None] = _nothing


def same(one: float | int | None, two: float | int | None) -> bool:
    """Two of our own values are one number, within the relative tolerance."""
    if one is None or two is None:
        return one is two
    return abs(one - two) <= RELATIVE * max(abs(one), abs(two))


def row_groups(row: dict) -> dict[str, Group]:
    """The groups of an ARD row, by grouping."""
    found: dict[str, Group] = {}
    n = 1
    while f"group{n}_groupingId" in row:
        if row.get(f"group{n}_groupId") is not None:
            group: Group = ("id", row[f"group{n}_groupId"])
        elif row.get(f"group{n}_groupValue") is not None:
            group = ("value", row[f"group{n}_groupValue"])
        else:
            group = ("all", None)
        found[row[f"group{n}_groupingId"]] = group
        n += 1
    return found


def embedded_groups(item: Embedded) -> dict[str, Group]:
    """The groups of an embedded result, by grouping, as `row_groups` gives them."""
    return {grouping: ("id", group) if group is not None
            else ("value", value) if value is not None else ("all", None)
            for grouping, group, value in item.cell}


def _other_result_problem(key: str, item: Embedded, other: object, rows: Rows) -> str | None:
    """Why `other` is not the same analysis and operation in one other group."""
    if other not in rows or other == key:
        return f"the proof names {other!r}, which is not another of our results"
    there = rows[other]
    if (there["analysis_id"], there["operation_id"]) != (item.analysis_id, item.operation_id):
        return f"the proof names {other}, a result of another analysis or operation"
    mine, theirs = embedded_groups(item), row_groups(there)
    differing = [grouping for grouping in sorted(set(mine) | set(theirs))
                 if mine.get(grouping) != theirs.get(grouping)]
    if len(differing) != 1 or "all" in (mine.get(differing[0], ("all", None))[0],
                                        theirs.get(differing[0], ("all", None))[0]):
        return (f"the proof names {other}, which does not differ from this result in exactly "
                "one group of one grouping")
    return None


def _no_records_problem(item: Embedded, zero: list, rows: Rows,
                        evidence: Evidence) -> str | None:
    """Why the named counts do not show that the cell has no records in a compared group."""
    if not zero:
        return "the proof names no count that shows there are no records"
    mine = embedded_groups(item)
    compared = [grouping for grouping, (kind, _) in mine.items() if kind == "all"]
    if len(compared) != 1:
        return "a proof by counts of 0 is for a test with one compared grouping"
    grouping = compared[0]
    own = {name: group for name, group in mine.items() if name != grouping}
    wanted = evidence.compared_groups(item.analysis_id)
    if wanted is None:
        return (f"the groups of {grouping} that analysis {item.analysis_id} compares are not "
                "known")
    seen: list[Group] = []
    for other in zero:
        row = rows.get(other)
        if row is None or row["method_id"] != "count.subjects" or row["raw_value"] != 0:
            return f"{other} is not a count of 0 among our results"
        groups = row_groups(row)
        in_grouping = groups.pop(grouping, ("all", None))
        if groups != own or in_grouping[0] == "all":
            return (f"{other} is not a count of the cell's own groups in one group of "
                    f"{grouping}")
        seen.append(in_grouping)
    if sorted(seen) != sorted(wanted):
        return (f"the counts are for the groups {', '.join(str(key) for _, key in sorted(seen))} "
                f"of {grouping}; the test compares "
                f"{', '.join(str(key) for _, key in sorted(wanted))}: one count per compared "
                "group is needed")
    return None


def _equal_values_problem(key: str, ours: object, evidence: Evidence) -> str | None:
    """Why the values around a quantile do not fix it under every definition."""
    found = evidence.cell_values(key)
    if found is None or found[0] not in QUARTERS or ours is None:
        return "this result is not a quartile or a median that summary.continuous computed"
    quarters, values = QUARTERS[found[0]], found[1]
    n = len(values)
    # Hyndman and Fan: j = floor(n p + m) with -1/2 <= m <= 3/4, and the quantile
    # is between x[j] and x[j + 1]. In whole numbers, with p = quarters / 4:
    low = max(1, (n * quarters - 2) // 4)
    high = min(n, (n * quarters + 3) // 4 + 1)
    if any(not same(value, ours) for value in values[low - 1:high]):
        return (f"the sorted values {low} to {high} of the {n} in the cell are not all our "
                f"value {ours}: another definition of the quantile could give another value")
    return None


# The statistics of summary.continuous that pin down the data of a cell: how many values,
# and the two ends (the review of real-3a, F5).
ANCHORS = ("n", "min", "max")


def _anchor_problem(key: str, item, comparison: Comparison, evidence: Evidence) -> str | None:
    """Why the data of a cell may not be the reference's: its n, minimum and maximum are not
    all embedded and reproduced. A proof that only asks what our values give says nothing
    when our own cell is wrong (a wrong population, review of real-3a, F5)."""
    found: dict[str, str] = {}
    for other, there in comparison.reference.items():
        if other == key or there.analysis_id != item.analysis_id or there.cell != item.cell:
            continue
        values = evidence.cell_values(other)
        if values is not None and values[0] in ANCHORS:
            found[values[0]] = other
    missing = [name for name in ANCHORS if name not in found]
    if missing:
        return (f"the reference has no {', '.join(missing)} of the same cell: nothing shows that "
                "our cell holds the reference's values")
    open_ = [found[name] for name in ANCHORS if found[name] in comparison.open]
    if open_:
        return f"{open_[0]}, of the same cell, is not reproduced: the cell's data may differ"
    return None


def _proof_problem(entry: dict, rows: Rows, comparison: Comparison, registry: Registry,
                   evidence: Evidence) -> str | None:
    """Why the proof of an entry does not hold; None when it does."""
    proof, key = entry["proof"], entry["result"]
    kind, item = proof["kind"], comparison.reference[key]
    printed = item.printed
    ours = rows.get(key, {}).get("raw_value")
    alternative = evidence.alternative
    if kind == "value_of_other_result":
        other = proof.get("result")
        problem = _other_result_problem(key, item, other, rows)
        if problem:
            return problem
        if entry["class"] != "reference_error":
            return "a value of another result proves a reference_error only"
        if not equal(printed, rows[other]["raw_value"], item.decimals):
            return (f"the embedded value {printed} is not our value of {other} "
                    f"({rows[other]['raw_value']})")
        # Two groups exchanged: the reference has our value of this result there.
        # Without this, any group that happens to have the embedded value would do.
        back = comparison.reference.get(other)
        if back is None or not equal(back.printed, ours, back.decimals):
            return (f"the reference's value of {other} "
                    f"({'not listed' if back is None else back.printed or '(no value)'}) is "
                    f"not our value of this result ({ours}): the two are not exchanged")
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
        # The option must be able to change this operation at all: otherwise "the
        # same under every value" is true of any result and proves nothing.
        if not any(not same(alternative(method_id, option, value).get(other, {}).get("raw_value"),
                            row["raw_value"])
                   for value in values for other, row in rows.items()
                   if row["operation_id"] == item.operation_id):
            return (f"no value of {option} changes a result of the operation "
                    f"{item.operation_id}: the option says nothing about this result")
        for value in values:
            other = alternative(method_id, option, value).get(key, {}).get("raw_value")
            if kind == "same_under_every" and not same(other, ours):
                return f"with {option} = {value} our value is {other}, not {ours}"
            if equal(printed, other, item.decimals):
                return f"with {option} = {value} our value is the embedded {printed}"
        if kind == "same_under_every":
            return _anchor_problem(key, item, comparison, evidence)
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
    if kind == "between_equal_values":
        if entry["class"] != "reference_error":
            return "values that fix a quantile under every definition prove a reference_error only"
        return _equal_values_problem(key, ours, evidence) or _anchor_problem(
            key, item, comparison, evidence)
    # no_records
    if printed != "":
        return f"the reference embeds the value {printed}"
    if key in rows:
        return "our engines give a result"
    return _no_records_problem(item, proof.get("zero") or [], rows, evidence)


def judge_entries(comparison: Comparison, entries: list[dict], rows: Rows, registry: Registry,
                  evidence: Evidence | Alternative) -> tuple[dict[str, dict], list[str]]:
    """The differences that are explained, each with its entry, and the problems of the others.

    A difference is explained when an entry names it and its embedded value
    and the proof of the entry holds. `evidence` may be the `alternative`
    function alone; a proof that asks for the data behind a cell then does
    not hold.
    """
    if not isinstance(evidence, Evidence):
        evidence = Evidence(evidence)
    explained: dict[str, dict] = {}
    problems = []
    listed = {entry["result"]: entry for entry in entries}
    for key, (printed, ours) in sorted(comparison.open.items()):
        entry = listed.get(key)
        if entry is None:
            problems.append(f"{key}: embedded {printed or '(no value)'}, ours {ours}: a "
                            "difference with no class")
            continue
        if entry["embedded"] != printed:
            problems.append(f"{key}: the entry says the reference embeds {entry['embedded']!r}, "
                            f"it embeds {printed!r}")
            continue
        problem = _proof_problem(entry, rows, comparison, registry, evidence)
        if problem:
            problems.append(f"{key}: the proof ({entry['proof']['kind']}) does not hold: "
                            f"{problem}")
            continue
        explained[key] = entry
    return explained, problems


def check_exceptions(comparison: Comparison, entries: list[dict], rows: Rows, registry: Registry,
                     evidence: Evidence | Alternative) -> tuple[list[str], list[str]]:
    """Every difference has one entry whose proof holds, and every entry is a difference."""
    lines = []
    open_results = comparison.open
    listed = {entry["result"]: entry for entry in entries}
    explained, problems = judge_entries(comparison, entries, rows, registry, evidence)
    classes = Counter((entry["class"], entry["proof"]["kind"]) for entry in explained.values())
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


def r_only_methods(registry: Registry) -> set[str]:
    """The registry methods only the R engine implements: the model-based ones (ADR-015)."""
    return {method.id for method in registry.methods.values()
            if "python" not in method.implementations}


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
