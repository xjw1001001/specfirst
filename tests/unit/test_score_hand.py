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

import pytest

from specfirst import gates
from specfirst.score import build, command, defects, gate, hand, scorer
from specfirst.score.candidate import Machine, vector
from specfirst.score.reading import same_value


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
    assert len(ours) == 24


def test_the_study_states_two_decisions_of_the_slice_and_takes_19_defaults(case):
    scoped = [r for r in case.gold if r["unit"] in case.units]
    assert len(scoped) == 21
    assert sorted(r["id"] for r in scoped if r["status"] == "stated") == [
        "ae.related.values", "ae.teae.end"]
    assert {r["class"] for r in scoped} == {"document_rule", "house_default"}
    assert tuple(r["id"] for r in scoped if r["identifiable"] == "unseparated") == (
        hand.UNSEPARATED)
    assert len(hand.UNSEPARATED) == 9
    assert "[1/s1] " in case.documents.texts["sap"]


@pytest.mark.parametrize("stage, decisions", [("C", 21), ("T", 7)])
def test_the_parser_control_scores_100_percent(machine, stage, decisions):
    result = scorer.control(machine, hand.case(machine.catalog, machine.house, stage))
    assert result.perfect
    assert len(result.reading.decisions) == decisions
    for name in ("value", "status", "quote", "span"):
        assert result.reading.total(name) == (decisions, decisions)
    for score in result.builds.values():
        assert (score.produced, score.correct, score.strict, score.lenient) == (1, 24, 1, 1)
        assert score.denominators() == {"shared_rows": 24, "produced": 24, "all": 24}
    assert result.silent == [] and result.behind == {}


def test_the_standard_alone_cannot_build_the_chain(machine, case):
    """ae.related.values has no house default (ADR-005, decision 3: what cannot be
    built without it counts as not produced)."""
    result = scorer.standard_alone(machine, case)
    assert [item.key[0] for item in result.reading.wrong()] == ["ae.teae.end",
                                                                "ae.related.values"]
    for name, score in result.builds.items():
        assert not score.valid and "ae.related.values" in score.failure
        assert (score.produced, score.in_gold, score.correct) == (0, 1, 0)
        assert score.denominators() == {"shared_rows": 0, "produced": 0, "all": 24}
        owners = result.owners[name]
        assert {(o.layer, o.decisions) for o in owners} == {
            ("build", (("ae.related.values", "mod-ae-emergence"),))}
    # With the list stated, the visible table is the gold table; the twin still has
    # the event on the 31st day, which the default (no end) counts.
    assert all(o.confirmed for o in result.owners["visible"])
    assert sum(1 for o in result.owners["twin"] if not o.confirmed) == 2
    assert result.behind == {("ae.teae.end", "mod-ae-emergence"): {"visible": 0, "twin": 2}}
    assert result.silent == []


def test_the_standard_alone_gives_the_table_at_stage_t(machine):
    """Every table decision of the study is the house default."""
    result = scorer.standard_alone(machine, hand.case(machine.catalog, machine.house, "T"))
    assert result.perfect and len(result.reading.decisions) == 7


def test_stage_t_reads_table_decisions_only(machine, case):
    staged = scorer.Case(case.id, case.units, case.gold, case.arms, case.data, case.documents,
                         stage="T")
    with pytest.raises(scorer.ScoreError, match="table decisions only"):
        scorer.run(machine, staged, [])


def test_outside_the_scope_the_gold_value_stands(machine, case):
    candidate = [{"id": "tfl.output.include", "unit": "tfl-demographics",
                  "value": {"rule": "included"}},
                 {"id": "tfl.population", "unit": "tfl-ae-summary",
                  "value": {"rule": "randomized"}}]
    made = {(r["id"], r["unit"]): r["value"] for r in vector(
        machine.catalog, machine.house, case.gold, candidate, case.units)}
    assert made[("tfl.output.include", "tfl-demographics")] == {"rule": "not_included"}
    assert made[("tfl.population", "tfl-ae-summary")] == {"rule": "randomized"}
    assert ("ae.related.values", "mod-ae-emergence") not in made  # no default: left open
    assert made[("ae.teae.end", "mod-ae-emergence")] == {"rule": "no_end"}


# Planted defect -> (layer, the cells it must change on the visible data and on the
# twin, whether an axis must differ), each worked out by hand.
EXPECTED = {
    "S1-arms": ("L6", 2, 2, False),
    "S2-set": ("L5", 10, 8, False),
    "S2-set-rule": ("L4", 0, 8, False),
    "S3-window": ("L4", 0, 2, False),
    "S4-denominator": ("L5", 1, 2, False),
    "S5-column": ("L7", 6, 6, True),
    "S9-sort": ("L7", 0, 0, True),
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


def test_three_defects_of_the_plan_do_not_apply_and_say_why():
    absent = [defect for defect in defects.DEFECTS if defect.layer is None]
    assert [defect.id for defect in absent] == ["S6-quantile", "S7-pvalue", "S8-baseline"]
    assert all(defect.plant is None and "does not apply" in defect.note for defect in absent)
    assert len(defects.DEFECTS) == 13  # the twelve of section 9.5, one planted at two layers


def test_the_suite_passes_and_prints_every_defect(machine, case):
    lines: list[str] = []
    passed, outcomes = defects.suite(machine, case, lines.append)
    assert passed and len(outcomes) == 13
    text = "\n".join(lines)
    assert "control: the gold decisions, through the parser, score 100%" in text
    assert "10 of 10 planted here; 10 of 10 detected and attributed" in text
    assert "S7-pvalue: a p-value rounded twice (E25)" in text


def test_the_suite_stops_when_the_control_does_not_hold(machine, case):
    broken = [dict(r) for r in case.gold]
    for record in broken:
        if record["id"] == "ae.teae.end":
            record["status"] = "default"  # gold calls a stated decision a default
    lines: list[str] = []
    passed, outcomes = defects.suite(
        machine, scorer.Case("broken", case.units, broken, case.arms, case.data,
                             case.documents), lines.append)
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


def test_two_wrong_decisions_behind_one_cell_have_one_owner(machine, case, control):
    """Section 9.4: the first element that differs owns the error. On the twin the
    safety flag differs (L4), so every wrong cell is owned by pop.safety.rule, and
    its gold value does not give the gold text where the table also names the
    wrong set. On the visible data only the table's set differs (L5)."""
    result = scorer.run(machine, case, misread(control, {
        "pop.safety.rule": {"rule": "randomized_and_dosed"},
        "tfl.population": {"rule": "randomized"}}), documents=control[1])
    assert {(o.layer, o.decisions[0][0]) for o in result.owners["visible"]} == {
        ("L5", "tfl.population")}
    assert all(o.confirmed for o in result.owners["visible"])
    assert {(o.layer, o.decisions[0][0]) for o in result.owners["twin"]} == {
        ("L4", "pop.safety.rule")}
    assert not all(o.confirmed for o in result.owners["twin"])
    assert result.silent == [] and result.behind == {}


def test_the_candidate_and_gold_differ_only_where_the_decisions_do(machine, case, control):
    """A candidate that is right is built from the very vector of gold."""
    made = vector(machine.catalog, machine.house, case.gold, control[0], case.units)
    assert all(same_value(one["value"], two["value"]) and one["id"] == two["id"]
               for one, two in zip(made, case.gold_vector(), strict=True))


def test_the_unseparated_decisions_are_those_no_other_value_shows(machine, case):
    """`identifiable` is filled by the machine, never by the author (section 4.3): the
    first version of the study marked two decisions; mutation finds nine."""
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
    assert "twin: cells correct: 24 of 24 gold cells of the outputs produced" in text


def test_the_gate_of_the_part_cannot_pass_before_the_kits_are_scored(root):
    names = [check.name for check in gates.GATES["read-1a"]]
    assert names[0] == "environment" and "kits of gen-2a" in names
    assert {"hand-made study", "separation", "parser control", "planted defects",
            "pilot"} <= set(names)
    lines: list[str] = []
    assert gate.kits(root, lines.append) is False
    assert "read-1a is not done" in lines[-1]


def test_the_checks_of_the_gate_hold_on_the_hand_made_study(root):
    lines: list[str] = []
    assert gate.hand_table(root, lines.append)
    assert gate.control(root, lines.append)
    assert gate.arms(root, lines.append)
    text = "\n".join(lines)
    assert "HAND01, twin: 24 of 24 cells are the cells worked out by hand" in text
    assert "the control fails on the changed document: yes" in text
    assert "arm S, stage T: every score 100%: yes" in text


def test_the_hand_table_check_fails_on_another_table(root, monkeypatch):
    """Rule R5 for the check itself: one cell of the table by hand is changed."""
    twin = {**hand.EXPECTED["twin"], "": ("(N=3)", "(N=2)", "(N=3)", "(N=9)")}
    monkeypatch.setattr(hand, "EXPECTED", {**hand.EXPECTED, "twin": twin})
    lines: list[str] = []
    assert gate.hand_table(root, lines.append) is False
    assert any("problem: " in line and "'(N=9)'" in line for line in lines)
    assert "HAND01, twin: 23 of 24 cells are the cells worked out by hand" in lines
