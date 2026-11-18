"""The planted defects of the scorer (PLAN.md section 9.5, rule R5), for the slice
"adverse event summary first" (ADR-005).

"The scorer is trusted only when it detects and correctly attributes each of
these." A defect is planted in what the scorer scores: a decision of the
candidate takes another value, a step of the candidate's build is changed
(the ARS file, the layout, the results), or a citation is changed. The
planted candidate is then scored like any other, by `scorer.run`.

    detected     the score the defect must lower is lower: wrong cells, an
                 axis that is not the gold axis, or a citation that fails.
                 A defect marked `twin only` must leave every score of the
                 visible data at 100%.
    attributed   every wrong cell and every axis of the candidate is owned
                 by the layer the defect was planted at; when a decision
                 was planted, by that decision, and building the candidate
                 again with the gold value gives the gold text.
    silent       a planted decision that no cell of the case shows: the
                 reading score has it wrong by value, and the gold vector
                 with this one value builds the gold tables on every
                 dataset. The data of the case cannot show the defect
                 (section 9.3). It is neither detected by a build score nor
                 a failure of the scorer; on a generated kit it is held
                 against the identifiability matrix of the kit
                 (specfirst.score.kit).

Before anything is planted the control must hold: the gold decisions,
through the parser, score 100% (`scorer.control`). A scorer that finds
fault with gold proves nothing by finding fault with a defect.

Twelve defects are listed in section 9.5. Ten are planted here, two of them
in two ways (a wrong analysis set at two layers; an unstable sort as a
decision and as a step of the build): fourteen entries in `DEFECTS`, twelve
plants. Three of the ten are planted as the nearest thing the slice has,
and `DEFECTS` says so for each: the table has no p-value, no sort but the
order of its treatment columns, and no list of sites. Two do not apply at
all: the adverse event summary has no quantile and no baseline value
(docs/decisions/ADR-008.md, decision 7).
"""

from __future__ import annotations

import dataclasses
import json
from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal
from urllib.parse import quote

from specfirst.score import report, scorer
from specfirst.score.build import table_of
from specfirst.score.candidate import Data, Hooks, Key, Machine
from specfirst.score.scorer import Case, Result

DOCUMENTS = "L0"  # the layer of a citation (section 4.1)
TABLE_UNIT = "tfl-ae-summary"
Out = Callable[[str], None]


@dataclass
class Planted:
    """A candidate with one defect."""

    what: str  # what was changed, in words
    records: list[dict]
    hooks: Hooks | None = None
    decision: Key | None = None  # the decision that was changed, if one was
    value: dict | None = None  # the value it was changed to
    data: dict[str, Data] | None = None  # the datasets to score on, when the plant changes them


@dataclass(frozen=True)
class Defect:
    id: str
    plan: str  # the defect in the words of section 9.5
    layer: str | None  # the layer it is planted at; None: it does not apply to the slice
    note: str  # how it is planted here, or why it does not apply
    plant: Callable[[Machine, Case, list[dict]], Planted | str] | None = None
    twin_only: bool = False
    dimension: str | None = None  # a citation defect: the dimension of the reading score


@dataclass
class Outcome:
    defect: Defect
    planted: Planted | None = None
    reason: str = ""  # why it could not be planted on this case
    result: Result | None = None
    detected: bool = False
    attributed: bool = False
    silent: bool = False  # a planted decision that the data of the case cannot show
    shows: dict[str, str] = field(default_factory=dict)  # dataset -> what the score shows
    problems: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.planted is not None and self.detected and self.attributed

    @property
    def state(self) -> str:
        """does not apply | not planted | passed | silent | failed"""
        if self.defect.layer is None:
            return "does not apply"
        if self.planted is None:
            return "not planted"
        return "passed" if self.passed else "silent" if self.silent else "failed"


# ---- helpers ---------------------------------------------------------------------------


def _with_value(records: list[dict], key: Key, value: dict) -> list[dict]:
    """The records with one decision misread: its value is changed, the rest is kept."""
    if not any((r["id"], r["unit"]) == key for r in records):
        return [*records, {"id": key[0], "unit": key[1], "value": value, "status": "stated",
                           "class": "document_rule"}]
    return [{**r, "value": value} if (r["id"], r["unit"]) == key else r for r in records]


def _gold_value(case: Case, key: Key) -> dict | None:
    return next((r.get("value") for r in case.gold if (r["id"], r["unit"]) == key), None)


def _other_rule(machine: Machine, key: Key, value: dict) -> dict | None:
    """Another alternative of the entry that needs no slot value."""
    for alternative in machine.catalog.entry(key[0]).alternatives:
        if alternative.id != value["rule"] and not alternative.slots:
            return {"rule": alternative.id}
    return None


def _misread(machine: Machine, case: Case, records: list[dict], key: Key,
             value: dict | None = None) -> Planted | str:
    """One decision read as another value: the one given, else the first other value
    a study of the case's design can decide, else another alternative without a slot."""
    gold = _gold_value(case, key)
    if gold is None:
        return f"the gold decisions have no value for {key[0]} ({key[1]})"
    if value is None and case.variants is not None:
        value = next(iter(case.variants(key)), None)
        if value is None:
            return f"a study of this design can decide nothing else for {key[0]}"
    value = value or _other_rule(machine, key, gold)
    if value is None:
        return f"{key[0]} has no other alternative without a slot"
    return Planted(f"{key[0]} ({key[1]}): {json.dumps(gold, sort_keys=True)} becomes "
                   f"{json.dumps(value, sort_keys=True)}", _with_value(records, key, value),
                   decision=key, value=value)


def _layout(machine: Machine, case: Case) -> dict:
    compiled = machine.compile(case.gold_vector())
    if isinstance(compiled, str) or TABLE_UNIT not in compiled.layouts:
        raise scorer.ScoreError(f"{case.id}: the gold decisions give no layout of {TABLE_UNIT}")
    return compiled.layouts[TABLE_UNIT]


# ---- the plants ------------------------------------------------------------------------


def _arms(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    layout = _layout(machine, case)
    analyses = [row["analysis"] for row in layout["rows"]]
    header = layout["columns"]["header_count"]

    def exchange(rows: list[dict]) -> list[dict]:
        # A group of a result is named by its ID when the groups are listed, by its
        # value when the grouping is data-driven (rule I14).
        by_id = any("group1_groupId" in row for row in rows if row["analysis_id"] == header)
        field, mark = ("group1_groupId", "") if by_id else ("group1_groupValue", "=")
        arms = sorted({row.get(field) for row in rows if row["analysis_id"] == header} - {None})
        for analysis_id in analyses:
            counts = {row.get(field): row["raw_value"] for row in rows
                      if row["analysis_id"] == analysis_id and row["operation_id"].endswith("_n")}
            pair = next(((a, b) for i, a in enumerate(arms) for b in arms[i + 1:]
                         if counts.get(a, 0) != counts.get(b, 0)), None)
            if pair is None:
                continue
            swap = {pair[0]: pair[1], pair[1]: pair[0]}
            for row in rows:
                group = row.get(field)
                if row["analysis_id"] == analysis_id and group in swap:
                    row[field] = swap[group]
                    row["id"] = row["id"].rsplit("/", 1)[0] + "/" + mark + quote(
                        swap[group], safe="")
            return sorted(rows, key=lambda row: row["id"])
        return rows

    return Planted("in the results of the first analysis in which two arms differ, the "
                   "results of the two arms are exchanged", records,
                   hooks=Hooks(f"{case.id}/arms-exchanged", ard=exchange))


def _denominator(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    if len(_layout(machine, case)["rows"]) < 2:
        return "the gold table has one row: no count of another row to divide by"

    def plant(compiled) -> None:
        layout = compiled.layouts[TABLE_UNIT]
        first, second = layout["rows"][0], layout["rows"][1]
        analyses = {analysis["id"]: analysis for analysis in compiled.ars["analyses"]}
        for name, columns in (("analysis", layout["columns"]),
                              ("total_analysis", layout["columns"].get("total"))):
            if not columns or not first.get(name) or not second.get(name):
                continue
            # The subjects with an event of the first row, counted as the header count
            # is counted: the same analysis set, the same grouping.
            count = json.loads(json.dumps(analyses[first[name]]))
            count["id"] = f"{first[name]}_PLANTED"
            count["methodId"] = analyses[columns["header_count"]]["methodId"]
            count.pop("referencedAnalysisOperations", None)
            compiled.ars["analyses"].append(count)
            for reference in analyses[second[name]]["referencedAnalysisOperations"]:
                if reference["analysisId"] == columns["header_count"]:
                    reference["analysisId"] = count["id"]

    return Planted("in the ARS file, the percent of the second row takes its denominator "
                   "from the subjects counted in the first row, not from the subjects of "
                   "the analysis set", records,
                   hooks=Hooks(f"{case.id}/wrong-denominator", compiled=plant))


def _column(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    if not _layout(machine, case)["columns"].get("total"):
        return "the gold table has no total column to leave out"

    def plant(compiled) -> None:
        layout = compiled.layouts[TABLE_UNIT]
        layout["columns"]["total"] = None
        for row in layout["rows"]:
            row["total_analysis"] = None

    return Planted("in the layout, the total column is left out; the ARS file still has its "
                   "analyses", records,
                   hooks=Hooks(f"{case.id}/missing-column", compiled=plant))


def _set_of_table(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    return _misread(machine, case, records, ("tfl.population", TABLE_UNIT))


def _set_by_rule(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    table = _gold_value(case, ("tfl.population", TABLE_UNIT)) or {}
    entry = {"safety": "pop.safety.rule", "randomized": "pop.randomized.rule",
             "efficacy": "pop.efficacy.rule"}.get(table.get("rule"))
    if entry is None:
        return "the gold table names no analysis set that a rule of mod-populations forms"
    return _misread(machine, case, records, (entry, "mod-populations"))


def _window(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    key = ("ae.teae.end", "mod-ae-emergence")
    gold = _gold_value(case, key) or {}
    if gold.get("rule") != "last_dose_plus_days":
        return "the gold decision ae.teae.end names no window of days"
    return _misread(machine, case, records, key, {**gold, "days": gold["days"] + 1})


def _sort(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    return _misread(machine, case, records, ("tfl.columns.arms", TABLE_UNIT))


ORDERS = ("ascending_dose_placebo_first", "protocol_order")


def _sort_in_the_build(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    """The columns in the other order while every decision is the gold decision."""
    if _layout(machine, case)["columns"].get("order") not in ORDERS:
        return "the gold layout orders its columns by a rule this plant does not know"

    def plant(compiled) -> None:
        columns = compiled.layouts[TABLE_UNIT]["columns"]
        columns["order"] = ORDERS[1 - ORDERS.index(columns["order"])]

    hooks = Hooks(f"{case.id}/other-order", compiled=plant)
    vector = case.gold_vector()
    same = True
    for data in case.data.values():
        gold = machine.build(vector, data, case.arms(vector))
        other = machine.build(vector, data, case.arms(vector), hooks)
        same &= all(output in other.grids and table_of(other.grids[output]).columns
                    == table_of(grid).columns for output, grid in gold.grids.items())
    if same:
        return "the two orders give this study the same columns"
    return Planted("in the layout, the treatment columns are ordered by the other rule; "
                   "every decision is the gold decision", records, hooks=hooks)


def _rounded_twice(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    """Every percent rounded to a whole number after the engine; the grid then rounds
    that number again, to its one decimal: 66.7 becomes 67.0."""
    def twice(rows: list[dict]) -> list[dict]:
        for row in rows:
            if row["operation_id"].endswith("_pct") and row.get("raw_value") is not None:
                row["raw_value"] = float(Decimal(repr(float(row["raw_value"]))).quantize(
                    Decimal(1), rounding=ROUND_HALF_UP))
        return rows

    return Planted("in the results, every percent is rounded to a whole number before the "
                   "grid rounds it to one decimal", records,
                   hooks=Hooks(f"{case.id}/rounded-twice", ard=twice))


def _frozen(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    """The list of related causality values, cut down to those the visible data hold.

    Where the visible data hold every value of the gold list (a generated
    kit: its visible data are large), the reader that froze the list is
    given less to see: the case is scored with visible data that lack the
    adverse event records of the first value of the list. The twin is
    never changed.
    """
    import pyarrow.compute as pc

    key = ("ae.related.values", "mod-ae-emergence")
    gold = _gold_value(case, key) or {}
    if gold.get("rule") != "stated_list":
        return "the gold decision ae.related.values is no list"
    visible = case.data.get("visible")
    table = (visible.sdtm or {}).get("ae") if visible else None
    if table is None or "AEREL" not in table.column_names:
        return "the case has no visible adverse event records to freeze a list from"
    seen = set(table.column("AEREL").to_pylist())
    frozen = [value for value in gold["values"] if value in seen]
    data, note = None, ""
    if frozen == gold["values"]:
        if len(frozen) < 2:
            return ("the gold list has one value, and the visible data hold it: a list "
                    "frozen from them is the gold list")
        gone, frozen = frozen[0], frozen[1:]
        kept = table.filter(pc.fill_null(pc.not_equal(table.column("AEREL"), gone), True))
        data = {**case.data, "visible": Data(f"{visible.name}/without-{quote(gone, safe='')}",
                                             sdtm={**visible.sdtm, "ae": kept})}
        note = (f"; the visible data hold every value of the list, so the case is scored "
                f"with visible data that lack the {table.num_rows - kept.num_rows} adverse "
                f"event records with the causality {gone}")
    if not frozen:
        return "the visible data hold no related causality value"
    planted = _misread(machine, case, records, key, {**gold, "values": frozen})
    if isinstance(planted, Planted):
        planted.data, planted.what = data, planted.what + note
    return planted


def _cited(case: Case, records: list[dict]) -> list[dict]:
    return [r for r in records if r.get("unit") in case.units and r.get("status") == "stated"
            and r.get("citations")]


def _quote(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    cited = _cited(case, records)
    if not cited:
        return "no stated decision of the scope cites a document"
    key = (cited[0]["id"], cited[0]["unit"])
    changed = [{**r, "citations": [{**c, "quote": c["quote"] + " (as amended)"}
                                   for c in r["citations"]]}
               if (r["id"], r["unit"]) == key else r for r in records]
    return Planted(f"{key[0]} ({key[1]}): the quote gets words the document does not have",
                   changed, decision=key)


def _span(machine: Machine, case: Case, records: list[dict]) -> Planted | str:
    cited = _cited(case, records)
    others = [r for r in records if r.get("citations") and r is not (cited[0] if cited else None)
              and r["citations"][0]["doc"] == (cited[0]["citations"][0]["doc"] if cited else "")]
    if not cited or not others:
        return "the scope has no two decisions cited in one document"
    key = (cited[0]["id"], cited[0]["unit"])
    anchor = others[0]["citations"][0]["anchor"]
    changed = [{**r, "citations": [{**c, "anchor": anchor} for c in r["citations"]]}
               if (r["id"], r["unit"]) == key else r for r in records]
    return Planted(f"{key[0]} ({key[1]}): the citation names the anchor {anchor}, that of "
                   "another decision; the quote is unchanged", changed, decision=key)


_NO_NUMBER = ("does not apply: the adverse event summary shows counts of subjects and "
              "percents, and nothing near it: ")

DEFECTS = (
    Defect("S1-arms", "arms exchanged in one analysis (E3)", "L6",
           "planted in the results, after the engine", _arms),
    Defect("S2-set", "a wrong analysis set", "L5",
           "the table names another analysis set (decision tfl.population)", _set_of_table),
    Defect("S2-set-rule", "a wrong analysis set", "L4",
           "the set of the table is formed by another rule (a decision of mod-populations)",
           _set_by_rule),
    Defect("S3-window", "a window off by one day", "L4",
           "treatment emergence ends one day later (decision ae.teae.end)", _window),
    Defect("S4-denominator", "a wrong denominator", "L5",
           "planted in the ARS file: no decision of the slice changes a denominator",
           _denominator),
    Defect("S5-column", "a missing column", "L7", "planted in the layout", _column),
    Defect("S6-quantile", "a changed quantile definition (E4)", None,
           _NO_NUMBER + "no quantile"),
    Defect("S7-rounded", "a p-value rounded twice (E25)", "L6",
           "the table has no p-value; planted as the nearest thing it has, a percent rounded "
           "twice, in the results after the engine", _rounded_twice),
    Defect("S8-baseline", "a baseline taken from the wrong record (E26)", None,
           _NO_NUMBER + "no baseline value"),
    Defect("S9-sort", "an unstable sort", "L7",
           "the slice orders one thing, the treatment columns: planted as the other order, "
           "read as a decision (tfl.columns.arms). An order that changes from run to run is "
           "for P1 to find", _sort),
    Defect("S9-sort-build", "an unstable sort", "L7",
           "the same order, wrong in the build: planted in the layout, no decision changed",
           _sort_in_the_build),
    Defect("S10-frozen", "a frozen site list (caught on the twin only)", "L4",
           "the slice has no site list; its frozen list is the causality values that count "
           "as related, cut down to those the visible data hold (decision ae.related.values)",
           _frozen, twin_only=True),
    Defect("S11-quote", "a quote that is not in the document", DOCUMENTS,
           "planted in a citation of the candidate", _quote, dimension="quote"),
    Defect("S12-span", "a citation that points at the wrong span", DOCUMENTS,
           "planted in a citation of the candidate", _span, dimension="span"),
)


# ---- the suite -------------------------------------------------------------------------


def judge(defect: Defect, planted: Planted, result: Result) -> Outcome:
    """Whether a planted defect was detected and attributed to its layer."""
    outcome = Outcome(defect, planted, result=result)
    if defect.dimension:
        marks = {item.key: item.marks()[defect.dimension] for item in result.reading.decisions}
        failed = [key for key, mark in marks.items() if mark is False]
        outcome.detected = planted.decision in failed
        outcome.attributed = failed == [planted.decision]
        outcome.shows = {"reading": f"{defect.dimension}: wrong for "
                         + (", ".join(key[0] for key in failed) or "no decision")}
        if not all(score.perfect for score in result.builds.values()):
            outcome.problems.append("a changed citation changed a build score")
            outcome.attributed = False
        return outcome
    wanted = (planted.decision,) if planted.decision else ()
    shown = False
    for name, score in result.builds.items():
        owners, axes = result.owners[name], result.axes[name]
        if score.perfect:
            outcome.shows[name] = "every score 100%"
            continue
        cells = score.denominators()["all"]
        outcome.shows[name] = (f"{len(score.wrong())} of {cells} gold cells wrong, strict "
                               f"{score.strict} of {score.in_gold}")
        shown = True
        other_axes = sum((not output.rows_equal) + (not output.columns_equal)
                         for output in score.outputs if output.produced)
        if len(owners) != len(score.wrong()) or len(axes) != other_axes:
            outcome.problems.append(
                f"{name}: {len(score.wrong())} wrong cells have {len(owners)} owners, and "
                f"{other_axes} axes that are not the gold axes have {len(axes)}")
        for owner in [*owners, *axes]:
            where = getattr(owner, "cell", None) or f"axis {getattr(owner, 'axis', '')}"
            if owner.layer != defect.layer:
                outcome.problems.append(f"{name}, {where}: owned by layer {owner.layer}, "
                                        f"planted at {defect.layer}")
            elif owner.decisions != wanted:
                names = ", ".join(key[0] for key in owner.decisions) or "no decision"
                outcome.problems.append(f"{name}, {where}: owned by {names}")
            elif wanted and owner.confirmed is not True:
                outcome.problems.append(f"{name}, {where}: the gold value of the decision does "
                                        "not give the gold text")
    if not shown and planted.decision is not None and planted.hooks is None \
            and planted.decision in result.silent:
        outcome.silent = True
        return outcome
    outcome.detected = shown
    if defect.twin_only:
        if not result.builds["visible"].perfect:
            outcome.problems.append("it shows on the visible data, and must show on the twin "
                                    "only")
        if result.builds["twin"].perfect:
            outcome.problems.append("it does not show on the twin")
        outcome.detected = (result.builds["visible"].perfect
                            and not result.builds["twin"].perfect)
    outcome.attributed = shown and not outcome.problems
    return outcome


def run_one(machine: Machine, case: Case, defect: Defect, records: list[dict],
            documents) -> Outcome:
    if defect.plant is None:
        return Outcome(defect, reason=defect.note)
    planted = defect.plant(machine, case, records)
    if isinstance(planted, str):
        return Outcome(defect, reason=planted)
    on = case if planted.data is None else dataclasses.replace(case, data=planted.data)
    result = scorer.run(machine, on, planted.records, arm=defect.id, hooks=planted.hooks,
                        documents=documents)
    return judge(defect, planted, result)


def suite(machine: Machine, case: Case, out: Out = print) -> tuple[bool, list[Outcome]]:
    """Plant every defect that applies on a case. Returns whether the control holds
    and every planted defect was detected and attributed, with the outcomes."""
    control = scorer.control(machine, case)
    out(f"planted defects on the case {case.id}, stage {case.stage}")
    if not control.perfect:
        for line in report.lines(control):
            out("  " + line)
        out("the control does not score 100%: no planted defect counts")
        return False, []
    out("  control: the gold decisions, through the parser, score 100%")
    records, documents = scorer.control_records(machine, case)
    outcomes = []
    for defect in DEFECTS:
        outcome = run_one(machine, case, defect, records, documents)
        outcomes.append(outcome)
        out(f"  {defect.id}: {defect.plan}")
        if defect.layer is None:
            out(f"    {defect.note}")
            continue
        if outcome.planted is None:
            out(f"    not planted on this case: {outcome.reason}")
            continue
        out(f"    planted at {defect.layer} ({defect.note}): {outcome.planted.what}")
        for name, shows in outcome.shows.items():
            out(f"    {name}: {shows}")
        result = outcome.result
        for name in result.builds:
            for layer, unit, decisions, cells, confirmed in _owned(result, name):
                out(f"    {name}: {cells} owned by layer {layer}, unit {unit}, decision "
                    f"{decisions}" + ("" if decisions == "-" else f"; confirmed {confirmed}"))
        if result.silent and not defect.dimension:
            out("    wrong by value and shown by no cell: "
                + ", ".join(key[0] for key in result.silent))
        for problem in outcome.problems:
            out(f"    problem: {problem}")
        if outcome.silent:
            out("    silent: the reading score has the decision wrong by value; the gold "
                "decisions with this one value build the gold tables on every dataset of "
                "the case")
            continue
        out(f"    detected: {'yes' if outcome.detected else 'NO'}; attributed to its layer: "
            f"{'yes' if outcome.attributed else 'NO'}")
    applies = [o for o in outcomes if o.defect.layer is not None]
    planted = [o for o in applies if o.planted is not None]
    passed = [o for o in planted if o.passed]
    silent = [o for o in planted if o.silent]
    out(f"planted defects on {case.id}: {len(DEFECTS)} entries for the twelve defects of "
        f"section 9.5 (two are planted in two ways); {len(DEFECTS) - len(applies)} do not "
        f"apply to the slice; {len(planted)} of {len(applies)} planted here; {len(passed)} "
        f"of {len(planted)} detected and attributed; {len(silent)} silent on these data")
    return len(passed) == len(planted), outcomes


def _owned(result: Result, name: str) -> list[tuple[str, str, str, str, str]]:
    from specfirst.score import attribute

    rows = [(layer, unit, decisions, f"{cells} cells", f"{confirmed} of {cells}")
            for layer, unit, decisions, cells, confirmed in attribute.summary(
                result.owners[name])]
    for axis in result.axes[name]:
        rows.append((axis.layer, axis.unit or "-",
                     ", ".join(k[0] for k in axis.decisions) or "-", f"the axis {axis.axis}",
                     {None: "-", True: "yes", False: "no"}[axis.confirmed]))
    return rows
