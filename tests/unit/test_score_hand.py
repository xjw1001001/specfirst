"""The scorer on HAND01, the hand-made study (PLAN.md section 13.6, read-1).

The numbers asserted here were worked out by hand from the lists of
subjects and events in `specfirst.score.hand`: the gold table, and for each
planted defect the cells of each dataset that it must change. The scorer
is held against them: detection, the layer, the decision, and that the
decision's gold value gives the gold text again.

The tests build the study with yamaa and the Python result engine: 7 and 9
subjects, a few seconds in all, no fetch cache and no R.
"""

from __future__ import annotations

import dataclasses

import pytest

from specfirst import gates
from specfirst.score import attribute, build, command, defects, gate, hand, scorer
from specfirst.score.candidate import Machine, vector
from specfirst.score.reading import same_value

# Two decisions of HAND01's plan (catalog@2): the related values, the total column.
RELATED_VALUES = ("ae.related.values", "mod-ae-emergence")
TOTAL = ("tfl.columns.total", "tfl-ae-summary")


@pytest.fixture(scope="module")
def machine(root):
    return Machine(root)


@pytest.fixture(scope="module")
def case(machine):
    return hand.case(machine.catalog, machine.house)


@pytest.fixture(scope="module")
def control(machine, case):
    return scorer.control_records(machine, case)


@pytest.mark.parametrize("which", ["visible", "twin"])
def test_the_gold_decisions_build_the_table_worked_out_by_hand(machine, case, which):
    _, gold = scorer.staged(machine, case, which)
    table = build.table_of(gold.grids[hand.OUTPUT])
    assert [column[0] for column in table.columns] == ["Placebo", "Low Dose", "High Dose", "Total"]
    ours = {(row[1], column[0]): cell["text"] for (row, column), cell in table.cells.items()}
    assert ours == hand.expected_cells(which)
    assert len(ours) == 28


def test_the_study_states_two_decisions_of_the_slice_and_takes_19_defaults(case):
    scoped = [r for r in case.gold if r["unit"] in case.units]
    assert len(scoped) == 21
    assert sorted(r["id"] for r in scoped if r["status"] == "stated") == [
        "ae.related.values", "tfl.columns.total"]
    assert {r["class"] for r in scoped} == {"document_rule", "house_default"}
    assert tuple(r["id"] for r in scoped if r["identifiable"] == "unseparated") == (
        hand.UNSEPARATED)
    assert len(hand.UNSEPARATED) == 10
    assert "[1/s1] " in case.documents.texts["sap"]


@pytest.mark.parametrize("stage, decisions", [("C", 21), ("T", 7)])
def test_the_parser_control_scores_100_percent(machine, stage, decisions):
    result = scorer.control(machine, hand.case(machine.catalog, machine.house, stage))
    assert result.perfect
    assert len(result.reading.decisions) == decisions
    for name in ("value", "status", "quote", "span"):
        assert result.reading.total(name) == (decisions, decisions)
    for score in result.builds.values():
        assert (score.produced, score.correct, score.strict, score.lenient) == (1, 28, 1, 1)
        assert score.denominators() == {"shared_rows": 28, "produced": 28, "all": 28}
    assert result.silent == [] and result.behind == {}


def test_the_standard_alone_builds_the_chain_but_the_related_rows(machine, case):
    """ae.related.values has no house default: the build leaves out what it binds and
    its cells wait for it (ADR-014, which changed ADR-005, decision 3; before, nothing
    was built). The house has no total column (open-default@2) and the study states one.
    The arm is held in detail in tests/unit/test_pending.py."""
    result = scorer.standard_alone(machine, case)
    assert [item.key[0] for item in result.reading.wrong()] == ["ae.related.values",
                                                                "tfl.columns.total"]
    # The rows of related and of serious related events wait in the three treatment
    # columns; their cells of the total column are wrong with the column.
    assert result.pending == {RELATED_VALUES: {"visible": 6, "twin": 6}}
    for score in result.builds.values():
        assert score.valid and (score.produced, score.in_gold) == (1, 1)
        assert score.correct == 15
    for dataset in ("visible", "twin"):
        owners = result.owners[dataset]
        assert len(owners) == 7 and {o.column[0] for o in owners} == {"Total"}
        assert {o.row[1] for o in owners if len(o.decisions) == 2} == {
            "Related adverse event", "Serious related adverse event"}
        assert all(TOTAL in o.decisions and o.confirmed and o.note != attribute.HIDDEN
                   for o in owners)
        assert [(a.axis, a.decisions) for a in result.axes[dataset]] == [
            ("rows", (RELATED_VALUES,)), ("columns", (TOTAL,))]
    assert result.behind == {} and result.silent == []


def test_the_standard_alone_gives_the_table_at_stage_t(machine):
    """Every table decision of the study is the house default but the total column: the
    table is gold's without it, and its seven cells are the decision's."""
    result = scorer.standard_alone(machine, hand.case(machine.catalog, machine.house, "T"))
    assert len(result.reading.decisions) == 7
    assert [item.key for item in result.reading.wrong()] == [TOTAL]
    for dataset, score in result.builds.items():
        assert score.correct == 21 and len(result.owners[dataset]) == 7
        assert all(o.decisions == (TOTAL,) for o in result.owners[dataset])


def test_stage_t_reads_table_decisions_only(machine, case):
    staged = dataclasses.replace(case, stage="T")
    with pytest.raises(scorer.ScoreError, match="table decisions only"):
        scorer.run(machine, staged, [])


def test_outside_the_scope_the_gold_value_stands(machine, case):
    candidate = [{"id": "tfl.output.include", "unit": "tfl-demographics",
                  "value": {"rule": "included"}},
                 {"id": "tfl.population", "unit": "tfl-ae-summary",
                  "value": {"rule": "randomized"}}]
    made = {(r["id"], r["unit"]): r["value"] for r in vector(
        machine.catalog, machine.house, case.gold, candidate, case.units, case.features)}
    assert made[("tfl.output.include", "tfl-demographics")] == {"rule": "not_included"}
    assert made[("tfl.population", "tfl-ae-summary")] == {"rule": "randomized"}
    # No default: left open, and pending in the build (ADR-014).
    assert ("ae.related.values", "mod-ae-emergence") not in made
    assert made[("ae.teae.end", "mod-ae-emergence")] == {"rule": "last_dose_plus_days",
                                                        "days": 30}


# Planted defect -> (layer, the cells it must change on the visible data and on the
# twin, whether an axis must differ), each worked out by hand.
EXPECTED = {
    "S1-arms": ("L6", 2, 2, False),
    "S2-set": ("L5", 12, 11, False),
    "S2-set-rule": ("L4", 0, 9, False),
    "S3-window": ("L4", 0, 2, False),
    "S4-denominator": ("L5", 2, 1, False),
    "S5-column": ("L7", 7, 7, True),
    # Every percent that is no whole number: the six of the total column of the visible
    # table; on the twin 33.3 of the placebo arm and 57.1, 28.6, 14.3, 14.3 and 14.3 of
    # the total column.
    "S7-rounded": ("L6", 6, 6, False),
    "S9-sort": ("L7", 0, 0, True),
    "S9-sort-build": ("L7", 0, 0, True),
    "S10-frozen": ("L4", 0, 2, False),
}
BY_ID = {defect.id: defect for defect in defects.DEFECTS}


@pytest.mark.parametrize("name", list(EXPECTED))
def test_a_planted_defect_is_detected_and_attributed(machine, case, control, name):
    layer, visible, twin, axis = EXPECTED[name]
    outcome = defects.run_one(machine, case, BY_ID[name], *control)
    assert outcome.problems == []
    assert outcome.passed and outcome.defect.layer == layer
    result = outcome.result
    assert len(result.builds["visible"].wrong()) == visible
    assert len(result.builds["twin"].wrong()) == twin
    for dataset, cells in (("visible", visible), ("twin", twin)):
        owners = result.owners[dataset]
        assert len(owners) == cells and {o.layer for o in owners} <= {layer}
        assert bool(result.axes[dataset]) == axis
        assert result.builds[dataset].perfect == (cells == 0 and not axis)
        wanted = (outcome.planted.decision,) if outcome.planted.decision else ()
        for owner in [*owners, *result.axes[dataset]]:
            assert owner.decisions == wanted
            assert owner.confirmed is (True if wanted else None)
    if outcome.planted.decision:
        assert [item.key for item in result.reading.wrong()] == [outcome.planted.decision]
        assert result.silent == [] and result.behind == {}


# A quote that is not in the document cannot stand inside the gold span either.
@pytest.mark.parametrize("name, failing", [("S11-quote", {"quote", "span"}),
                                           ("S12-span", {"span"})])
def test_a_planted_citation_fails_its_dimension_and_nothing_else(machine, case, control, name,
                                                                 failing):
    outcome = defects.run_one(machine, case, BY_ID[name], *control)
    assert outcome.passed and outcome.problems == []
    assert outcome.defect.dimension in failing
    reading = outcome.result.reading
    for other in ("value", "status", "quote", "span"):
        right, of = reading.total(other)
        assert (of - right) == (1 if other in failing else 0), other
    assert all(score.perfect for score in outcome.result.builds.values())


def test_two_defects_of_the_plan_do_not_apply_and_say_why():
    absent = [defect for defect in defects.DEFECTS if defect.layer is None]
    assert [defect.id for defect in absent] == ["S6-quantile", "S8-baseline"]
    assert all(defect.plant is None and "does not apply" in defect.note for defect in absent)
    # The twelve of section 9.5: ten are planted, two of them in two ways.
    assert len(defects.DEFECTS) == 14
    assert len({defect.plan for defect in defects.DEFECTS}) == 12
    nearest = [defect.id for defect in defects.DEFECTS if "nearest thing" in defect.note
               or "the slice has no" in defect.note or "the slice orders one thing" in defect.note]
    assert nearest == ["S7-rounded", "S9-sort", "S10-frozen"]


def test_the_suite_passes_and_prints_every_defect(machine, case):
    lines: list[str] = []
    passed, outcomes = defects.suite(machine, case, lines.append)
    assert passed and len(outcomes) == 14
    text = "\n".join(lines)
    assert "control: the gold decisions, through the parser, score 100%" in text
    assert "12 of 12 planted here; 12 of 12 detected and attributed" in text
    assert "S8-baseline: a baseline taken from the wrong record (E26)" in text


def test_the_suite_stops_when_the_control_does_not_hold(machine, case):
    broken = [dict(r) for r in case.gold]
    for record in broken:
        if record["id"] == "tfl.columns.total":
            record["status"] = "default"  # gold calls a stated decision a default
    lines: list[str] = []
    passed, outcomes = defects.suite(
        machine, dataclasses.replace(case, id="broken", gold=broken), lines.append)
    assert not passed and outcomes == []
    assert "no planted defect counts" in lines[-1]


def misread(control, changes):
    records = control[0]
    return [{**r, "value": changes[r["id"]]} if r["id"] in changes else r for r in records]


@pytest.mark.parametrize("entry, value", [
    ("tfl.rounding.rule", {"rule": "half_even"}),
    ("date.studyday.origin", {"rule": "dm_rfstdtc"}),
])
def test_a_wrong_value_that_these_data_cannot_show(machine, case, control, entry, value):
    """No percent of the study lies on a half, and no table of the slice shows a study
    day: the reading score has the error, no cell has it, and the report says so."""
    result = scorer.run(machine, case, misread(control, {entry: value}), documents=control[1])
    assert [item.key[0] for item in result.reading.wrong()] == [entry]
    assert all(score.perfect for score in result.builds.values())
    assert [key[0] for key in result.silent] == [entry] and result.behind == {}
    assert not result.perfect


def owners_of(result, dataset):
    """(row label, column header) -> (layer, the IDs of the owning decisions, confirmed)."""
    return {(o.row[1], o.column[0]): (o.layer, tuple(key[0] for key in o.decisions), o.confirmed)
            for o in result.owners[dataset]}


def test_two_wrong_decisions_and_each_cell_has_the_owner_that_changes_it(machine, case, control):
    """Section 9.4, with every claim run. The emergence without an end changes two
    cells of the twin (the event on the 31st day); a count of zero without its percent
    changes eight cells of the visible table and twelve of the twin. With both wrong, no
    cell of the display belongs to the module: the results of those cells are the
    gold results, whatever differs in ADAE (review of read-1a, finding R2)."""
    result = scorer.run(machine, case, misread(control, {
        "ae.teae.end": {"rule": "no_end"},
        "tfl.percent.format": {"rule": "one_decimal_zero_blank", "decimals": 1}}),
        documents=control[1])
    display = ("L7", ("tfl.percent.format",), True)
    assert set(owners_of(result, "visible").values()) == {display}
    assert len(result.owners["visible"]) == 8
    twin = owners_of(result, "twin")
    assert len(twin) == 14
    module = {cell for cell, owner in twin.items() if owner == ("L4", ("ae.teae.end",), True)}
    assert module == {("Any adverse event", "Placebo"), ("Any adverse event", "Total")}
    assert all(owner == display for cell, owner in twin.items() if cell not in module)
    assert result.silent == [] and result.behind == {}


def test_two_wrong_decisions_behind_one_cell_own_it_together(machine, case, control):
    """The rule of the safety set and the set the table names, both wrong. On the
    visible data every dosed subject is randomized: only the table's set differs,
    and its twelve cells are its own. On the twin the candidate's table is on the
    randomized set, with L3 and without X1. Five cells are wrong under the table
    decision alone and right under the other alone (the low dose column): the table
    decision owns them. Six are wrong under each alone (the total column: back on the
    safety set, its rule of at least one dose brings X1 in; on the randomized set, L3
    is in): no one decision gives the gold text, both together do, and the owner is the
    far end with both."""
    result = scorer.run(machine, case, misread(control, {
        "pop.safety.rule": {"rule": "at_least_one_dose"},
        "tfl.population": {"rule": "randomized"}}), documents=control[1])
    table = ("L5", ("tfl.population",), True)
    assert set(owners_of(result, "visible").values()) == {table}
    assert len(result.owners["visible"]) == 12
    twin = owners_of(result, "twin")
    both = ("L4", ("pop.safety.rule", "tfl.population"), True)
    assert {cell for cell, owner in twin.items() if owner == both} == {
        ("", "Total"), ("Any adverse event", "Total"), ("Related adverse event", "Total"),
        ("Serious adverse event", "Total"), ("Serious related adverse event", "Total"),
        ("Adverse event leading to discontinuation of study treatment", "Total")}
    assert {cell for cell, owner in twin.items() if owner == table} == {
        ("", "Low Dose"), ("Any adverse event", "Low Dose"),
        ("Related adverse event", "Low Dose"), ("Serious adverse event", "Low Dose"),
        ("Serious related adverse event", "Low Dose")}
    assert len(twin) == 11
    joint = [o for o in result.owners["twin"] if len(o.decisions) == 2]
    assert all(o.note == attribute.JOINT and o.element == "adam:ADSL.SAFFL" for o in joint)
    assert result.silent == [] and result.behind == {}


def test_a_defect_of_the_build_beside_a_wrong_decision(machine, case, control):
    """Every percent rounded twice, and the table on the wrong set. A cell that the
    rounding alone makes wrong is not the decision's: the claim of the decision is
    run, fails, and the cell is owned by the results (L6), with no decision."""
    planted = BY_ID["S7-rounded"].plant(machine, case, control[0])
    result = scorer.run(machine, case, misread(control, {"tfl.population": {"rule": "randomized"}}),
                        hooks=planted.hooks, documents=control[1])
    twin = owners_of(result, "twin")
    # Placebo has the same three subjects in both sets: 1 of 3 is 33.3, shown as 33.0.
    assert twin[("Any adverse event", "Placebo")] == ("L6", (), None)
    # The low dose column has another subject (L3): the decision's, whatever the rounding.
    assert twin[("", "Low Dose")] == ("L5", ("tfl.population",), True)
    assert {owner for owner in twin.values()} == {("L6", (), None),
                                                  ("L5", ("tfl.population",), True)}
    assert not any(o.confirmed is False for name in result.owners for o in result.owners[name])


def test_a_claim_that_fails_is_no_owner(machine, case, control, monkeypatch):
    """Rule R5 for the run of a claim: a machine whose `decides` edges all point at
    the first differing decision. The claim of that decision is run for every cell
    and holds only for its own; the other cells go to the decision that holds."""
    key = ("ae.teae.end", "mod-ae-emergence")
    class Everything(set):
        """A set of elements that holds every element."""

        def __and__(self, other):
            return other

        def __or__(self, other):
            return self

        __ror__ = __or__

    everything = Everything()
    real = machine.changes
    monkeypatch.setattr(machine, "changes", lambda records, k, value: (
        everything if k == key else real(records, k, value)))
    result = scorer.run(machine, case, misread(control, {
        "ae.teae.end": {"rule": "no_end"},
        "tfl.percent.format": {"rule": "one_decimal_zero_blank", "decimals": 1}}),
        documents=control[1])
    twin = owners_of(result, "twin")
    assert sum(1 for owner in twin.values() if owner[1] == ("ae.teae.end",)) == 2
    assert sum(1 for owner in twin.values() if owner == ("L7", ("tfl.percent.format",), True)) == 12


def test_without_a_run_the_owner_is_the_first_claim(machine, case, control):
    result = scorer.run(machine, case, misread(control, {
        "ae.teae.end": {"rule": "no_end"},
        "tfl.percent.format": {"rule": "one_decimal_zero_blank", "decimals": 1}}),
        documents=control[1], prove=False)
    twin = owners_of(result, "twin")
    assert {owner[2] for owner in twin.values()} == {None}
    # The display cells are the display's without any run: their results are gold's.
    assert sum(1 for owner in twin.values() if owner[0] == "L7") == 12


def test_every_wrong_cell_must_have_an_owner(machine, case, control, monkeypatch):
    """Rule R5 for the suite: a scorer that leaves every second wrong cell without
    an owner (review of read-1a, finding R3)."""
    real = attribute.attribute

    def half(*args, **kwargs):
        owners, axes = real(*args, **kwargs)
        return owners[::2], axes

    monkeypatch.setattr(attribute, "attribute", half)
    outcome = defects.run_one(machine, case, BY_ID["S2-set"], *control)
    assert not outcome.passed and outcome.state == "failed"
    assert any("wrong cells have" in problem for problem in outcome.problems)


def test_an_axis_of_columns_is_owned_by_the_data_behind_it(machine, case, control):
    """A decision that writes the treatment label in another way changes the headers
    of the treatment columns. The columns are the values of the grouping variable:
    the axis rests on data, and its owner is found at L4 like that of a cell
    (lesson 52: the walk of an axis began at the analyses, and the axis had no owner)."""
    key = ("trt.actual.source", "mod-treatment")
    result = scorer.run(machine, case, misread(control, {key[0]: {"rule": "first_ex_treatment"}}),
                        documents=control[1])
    for dataset in ("visible", "twin"):
        table = build.table_of(scorer.staged(machine, case, dataset)[1].grids[hand.OUTPUT])
        score = result.builds[dataset].outputs[0]
        assert not score.columns_equal and score.rows_equal
        # The three treatment columns have other headers; the total column stands.
        assert len(result.owners[dataset]) == 21 == len(table.cells) - len(table.rows)
        assert {cell.reason for cell in score.wrong} == {"no_column"}
        [axis] = result.axes[dataset]
        assert (axis.axis, axis.layer, axis.element) == ("columns", "L4", "adam:ADSL.TRT01A")
        for owner in [axis, *result.owners[dataset]]:
            assert owner.layer == "L4" and owner.decisions == (key,) and owner.confirmed is True
    assert result.silent == [] and result.behind == {}


def test_the_candidate_and_gold_differ_only_where_the_decisions_do(machine, case, control):
    """A candidate that is right is built from the very vector of gold."""
    made = vector(machine.catalog, machine.house, case.gold, control[0], case.units)
    assert all(same_value(one["value"], two["value"]) and one["id"] == two["id"]
               for one, two in zip(made, case.gold_vector(), strict=True))


def test_the_unseparated_decisions_are_those_no_other_value_shows(machine, case):
    """`identifiable` is filled by the machine, never by the author (section 4.3): the
    first version of the study marked two decisions; mutation finds ten under
    open-default@2 (nine under open-default@1: the grouping of the safety set is the
    tenth, as every subject of the set is dosed as planned)."""
    found = scorer.separation(machine, case, first_only=True)
    assert len(found) == 21
    silent = tuple(key[0] for key, values in found.items()
                   if not any(any(changed.values()) for _, changed in values))
    assert silent == hand.UNSEPARATED
    # A separated decision is shown by at least one value; a value need not show.
    window = found[("ae.teae.end", "mod-ae-emergence")]
    assert window[0][0] == {"rule": "no_end"} and window[0][1] == {"visible": 0, "twin": 2}
    # The twin of a hand-made study is no superset of its visible data: the source of
    # the treatment end date is shown by the visible data only.
    end = found[("trt.end.source", "mod-treatment")]
    assert end[0][0] == {"rule": "last_ex_start_date"} and end[0][1] == {"visible": 4, "twin": 0}


def test_the_command_scores_an_arm(root, capsys):
    assert command.main(root, ["hand", "--arm", "C", "--stage", "T"]) == 0
    text = capsys.readouterr().out
    assert "case hand01, arm C, stage T" in text and "every score is 100%" in text
    assert "twin: cells correct: 28 of 28 gold cells of the outputs produced" in text


def test_the_gate_of_the_part_has_the_checks_of_the_plan():
    """ADR-005, part read-1a: the planted defects and the parser control, on the
    hand-made study and on the kits of gen-2a; the pilot is a report. Drift first."""
    from specfirst.gen import gate2

    names = [check.name for check in gates.GATES["read-1a"]]
    assert names[0] == "environment" and names[-1] == "ASCII"
    assert {"unit tests", "hand-made study", "separation", "parser control", "standard alone",
            "planted defects", "pilot", "pilot tests", "kits of gen-2a",
            "cache untouched"} <= set(names)
    # The kits are those of the gate of gen-2a: its seed, its count, its limit of workers.
    assert (gate2.SEED, gate2.COUNT) == ("gen-2a", 10) and gate2.MAX_WORKERS <= 4
    assert gate.write_kits.__defaults__ == (gate2.SEED, gate2.COUNT)


def test_the_checks_of_the_gate_hold_on_the_hand_made_study(root):
    lines: list[str] = []
    assert gate.hand_table(root, lines.append)
    assert gate.control(root, lines.append)
    assert gate.arms(root, lines.append)
    assert gate.planted_defects(root, lines.append)
    text = "\n".join(lines)
    assert "HAND01, twin: 28 of 28 cells are the cells worked out by hand" in text
    assert "the control fails on the changed document: yes" in text
    assert ("arm S, stage T: tfl.columns.total is the one wrong decision and owns the 7 cells "
            "of the total column alone: yes") in text
    assert "every defect that applies is planted on HAND01, detected and attributed: yes" in text


def test_the_control_check_fails_on_an_arm_c_that_reads_no_document(root, monkeypatch):
    """Rule R5 for check 7 (review of read-1a, finding R3): the changed document goes
    through `scorer.control`, so a control that takes the gold records and reads
    nothing does not see the change, and the check says so."""
    def blind(machine, case):
        return [dict(r) for r in case.gold if r["unit"] in case.units], case.documents

    monkeypatch.setattr(scorer, "control_records", blind)
    lines: list[str] = []
    assert gate.control(root, lines.append) is False
    assert lines[-1] == "the control fails on the changed document: NO"


def test_the_defects_check_fails_when_a_defect_cannot_be_planted(root, monkeypatch):
    """Rule R5 for check 9: on HAND01 every defect that applies must be planted."""
    index = next(n for n, defect in enumerate(defects.DEFECTS) if defect.id == "S5-column")
    unplanted = dataclasses.replace(defects.DEFECTS[index],
                                    plant=lambda machine, case, records: "nothing to plant in")
    monkeypatch.setattr(defects, "DEFECTS", (*defects.DEFECTS[:index], unplanted,
                                             *defects.DEFECTS[index + 1:]))
    lines: list[str] = []
    assert gate.planted_defects(root, lines.append) is False
    assert lines[-1].endswith("detected and attributed: NO")


def test_the_hand_table_check_fails_on_another_table(root, monkeypatch):
    """Rule R5 for the check itself: one cell of the table by hand is changed."""
    twin = {**hand.EXPECTED["twin"], "": ("(N=3)", "(N=2)", "(N=2)", "(N=9)")}
    monkeypatch.setattr(hand, "EXPECTED", {**hand.EXPECTED, "twin": twin})
    lines: list[str] = []
    assert gate.hand_table(root, lines.append) is False
    assert any("problem: " in line and "'(N=9)'" in line for line in lines)
    assert "HAND01, twin: 27 of 28 cells are the cells worked out by hand" in lines
