"""Issue #26: a decision without a value is pending (docs/decisions/ADR-014.md).

When the reader asks about a decision that has no house default, or a
candidate leaves it out, the scorer's build leaves out what that decision
binds and builds the rest: the ADaM columns its fragments would write and
what derives from them, the analyses that read them, the rows of those
analyses, and an output that needs it as a whole. The gold cells of what is
left out are pending: neither right nor wrong, counted apart and named by
the decision.

The study is HAND01 (`specfirst.score.hand`): yamaa and the Python result
engine, a few seconds in all, no fetch cache and no R.
"""

from __future__ import annotations

import pytest

from specfirst.compile.compiler import CompileError, compile_decisions
from specfirst.score import build, hand, scorer
from specfirst.score.candidate import Data, Machine, vector

KEY = ("ae.related.values", "mod-ae-emergence")
ROWS = ("tfl.ae.summary.rows", "tfl-ae-summary")
RELATED = "Related adverse event"


@pytest.fixture(scope="module")
def machine(root):
    return Machine(root)


@pytest.fixture(scope="module")
def case(machine):
    return hand.case(machine.catalog, machine.house)


def asked(key):
    return {"id": key[0], "unit": key[1], "value": None, "status": "asked",
            "class": "study_input"}


def cells(made):
    table = build.table_of(made.grids[hand.OUTPUT])
    return {(row[1], column[0]): cell["text"] for (row, column), cell in table.cells.items()}


def test_the_repro_of_issue_26_builds_every_output(root):
    """The script of the issue, on its own terms: the house defaults and the asked
    decision. Before: `compile: ADAE: no value for ae.related.values`, no grid."""
    machine = Machine(root, datasets=("ADSL", "ADAE"))
    gold = hand.gold_values(machine.catalog, machine.house)
    found = vector(machine.catalog, machine.house, gold, [asked(KEY)], hand.UNITS)
    assert not any((r["id"], r["unit"]) == KEY for r in found)
    made = machine.build(found, Data("repro/asked", sdtm=hand.tables("visible")), hand.ARMS)
    assert made.ok, made.failure
    assert sorted(made.grids) == [hand.OUTPUT]
    assert RELATED not in [row["label"] for row in made.grids[hand.OUTPUT]["rows"]]
    assert set(made.pending.values()) == {(KEY,)}


@pytest.mark.parametrize("which", ["visible", "twin"])
def test_a_pending_decision_leaves_out_only_what_it_binds(machine, case, which):
    """Every other decision at gold: the grid is the gold grid without the row of
    related events, cell for cell."""
    candidate = [r for r in case.gold if (r["id"], r["unit"]) != KEY] + [asked(KEY)]
    found = vector(machine.catalog, machine.house, case.gold, candidate, case.units)
    made = machine.build(found, hand.data(which), hand.ARMS)
    assert made.ok, made.failure
    assert cells(made) == {key: text for key, text in hand.expected_cells(which).items()
                           if key[0] != RELATED}
    assert made.pending == {"adam:ADAE.RELGR1": (KEY,), "ars:An_AESUM_RELATED": (KEY,),
                            "ars:An_AESUM_RELATED_Tot": (KEY,)}
    assert "RELGR1" not in made.adam["ADAE"].column_names
    assert "AEREL" in made.adam["ADAE"].column_names


def test_the_compiler_keeps_its_default(machine, case):
    """`specfirst compile` and the generator compile as before: a decision without a
    value stops the compile. Only the scorer asks for the pending mode."""
    records = [r for r in case.gold_vector() if (r["id"], r["unit"]) != KEY]
    with pytest.raises(CompileError, match="ADAE: no value for ae.related.values"):
        compile_decisions(machine.catalog, machine.house, records, "../house")
    compiled = compile_decisions(machine.catalog, machine.house, records, "../house",
                                 pending=True)
    assert compiled.pending == {KEY: ["adam:ADAE.RELGR1", "ars:An_AESUM_RELATED",
                                      "ars:An_AESUM_RELATED_Tot"]}
    assert compiled.manifest()["pending"] == [
        {"id": KEY[0], "unit": KEY[1], "left_out": compiled.pending[KEY]}]
    complete = compile_decisions(machine.catalog, machine.house, case.gold_vector(), "../house",
                                 pending=True)
    assert complete.pending == {} and "pending" not in complete.manifest()
    assert complete.files == compile_decisions(machine.catalog, machine.house,
                                               case.gold_vector(), "../house").files


def test_the_standard_alone_builds_the_chain_with_the_related_row_pending(machine, case):
    """Arm S on HAND01: ae.related.values has no house default. Before ADR-014 the
    build stopped and no output was produced."""
    result = scorer.standard_alone(machine, case)
    assert [item.key[0] for item in result.reading.wrong()] == ["ae.teae.end",
                                                                "ae.related.values"]
    assert result.pending == {KEY: {"visible": 4, "twin": 4}}
    assert result.silent == [] and result.behind == {}
    assert not result.perfect
    for score in result.builds.values():
        assert score.valid, score.failure
        assert (score.produced, score.in_gold, score.waiting) == (1, 1, 0)
        assert score.pending_by_decision() == {KEY: 4}
        assert score.denominators() == {"shared_rows": 20, "produced": 20, "all": 20}
        assert not score.perfect
        assert any("pending" in line and "ae.related.values (4 cells)" in line
                   for line in score.lines())
    # The visible data cannot show the default of ae.teae.end; the twin can, in two
    # cells, and that decision alone owns them.
    visible, twin = result.builds["visible"], result.builds["twin"]
    assert (visible.correct, visible.strict, visible.lenient) == (20, 1, 1)
    assert result.owners["visible"] == []
    assert (twin.correct, twin.strict, twin.lenient) == (18, 0, 0)
    owners = result.owners["twin"]
    assert {(o.row[1], o.column[0]) for o in owners} == {("Any adverse event", "Placebo"),
                                                         ("Any adverse event", "Total")}
    assert all(o.decisions == (("ae.teae.end", "mod-ae-emergence"),) and o.layer == "L4"
               and o.confirmed for o in owners)


def test_a_table_decision_without_a_value_leaves_the_output_pending(machine, case):
    """The rows of the table are asked and not answered: the whole output waits. It is
    neither produced nor counted as not produced (ADR-014, decision 3): it leaves the
    denominator of the outputs too (review of std-issues, finding 4)."""
    candidate = [r for r in case.gold if (r["id"], r["unit"]) != ROWS] + [asked(ROWS)]
    result = scorer.run(machine, case, candidate)
    assert result.pending == {ROWS: {"visible": 24, "twin": 24}}
    for score in result.builds.values():
        assert score.valid
        assert (score.produced, score.in_gold, score.waiting) == (0, 0, 1)
        assert (score.strict, score.lenient) == (0, 0)
        assert score.denominators() == {"shared_rows": 0, "produced": 0, "all": 0}
        assert score.wrong() == [] and not score.perfect
        assert any("produced: 0 of 0 outputs in gold, and 1 waits for a decision" in line
                   for line in score.lines())
    assert all(owners == [] for owners in result.owners.values())


def test_an_axis_is_owned_without_the_rows_that_wait(machine, case):
    """The rows of the table are read as ANY, RELATED, SERIOUS and ae.related.values
    is asked. The axis of rows is held without the row that waits (gold: ANY, SERIOUS,
    DISCONTINUATION, FATAL; the candidate: ANY, SERIOUS), and the rows decision alone
    gives it back: it owns the axis. Before, the attribution held the axis against the
    whole gold axis and named ae.related.values as well (seen in the gate read-2a)."""
    rows = {"id": ROWS[0], "unit": ROWS[1],
            "value": {"rule": "stated_rows", "rows": ["ANY", "RELATED", "SERIOUS"]}}
    candidate = [r for r in case.gold if (r["id"], r["unit"]) not in (KEY, ROWS)] + [
        asked(KEY), rows]
    result = scorer.run(machine, case, candidate)
    assert result.pending == {KEY: {"visible": 4, "twin": 4}}
    for name in result.builds:
        assert [(a.output, a.axis, a.decisions, a.confirmed) for a in result.axes[name]] == [
            (hand.OUTPUT, "rows", (ROWS,), True)]
        assert {o.decisions for o in result.owners[name]} == {(ROWS,)}


EFFICACY = ("pop.efficacy.rule", "mod-populations")
POPULATION = ("tfl.population", "tfl-ae-summary")


def test_an_optional_decision_without_a_value_that_a_table_reads(machine, case):
    """The house lets a study leave out pop.efficacy.rule (`optional` of ADSL): its
    column EFFFL is then not written. When the table is on the efficacy set it reads
    EFFFL, and the decision is pending: the output waits for it, named (review of
    std-issues, finding 1; before, the compile stopped: `the tables read ADSL.EFFFL,
    which no decision of the study writes`)."""
    records = [{**r, "value": {"rule": "efficacy"}} if (r["id"], r["unit"]) == POPULATION
               else r for r in case.gold_vector() if (r["id"], r["unit"]) != EFFICACY]
    made = machine.build(records, hand.data("visible"), hand.ARMS)
    assert made.ok, made.failure
    assert made.grids == {}
    assert made.pending[f"output:{hand.OUTPUT}"] == (EFFICACY,)
    assert made.pending["adam:ADSL.EFFFL"] == (EFFICACY,)
    # A study that does not make the decision and reads no EFFFL waits for nothing.
    plain = machine.build(case.gold_vector(), hand.data("visible"), hand.ARMS)
    assert plain.ok and plain.pending == {}


def test_a_decision_that_adds_records_makes_its_dataset_wait(machine, case):
    """bds.eot.record adds the end-of-treatment records to ADVS (a row template).
    Without a value the records of ADVS depend on it: ADVS waits as a whole, and the
    adverse event summary, which reads no ADVS, is built (review of std-issues,
    finding 3; before, ADVS was built without those records and nothing waited)."""
    key = ("bds.eot.record", "mod-bds-visits")
    assert key in {(r["id"], r["unit"]) for r in case.gold_vector()}
    records = [r for r in case.gold_vector() if (r["id"], r["unit"]) != key]
    made = machine.build(records, hand.data("visible"), hand.ARMS)
    assert made.ok, made.failure
    assert made.pending["adam:ADVS"] == (key,)
    assert "ADVS" not in made.adam and "ADVS" in machine.compile(case.gold_vector()).datasets
    assert cells(made) == hand.expected_cells("visible")


def test_what_derives_from_a_pending_column_is_left_out_too(machine, case):
    """The start of treatment is asked: the safety flag and treatment emergence derive
    from it, every analysis reads one of them, and the output waits for it."""
    key = ("trt.start.source", "mod-treatment")
    candidate = [r for r in case.gold if (r["id"], r["unit"]) != key] + [asked(key)]
    found = vector(machine.catalog, machine.house, case.gold, candidate, case.units)
    made = machine.build(found, hand.data("visible"), hand.ARMS)
    assert made.ok, made.failure
    assert made.grids == {}
    assert made.pending[f"output:{hand.OUTPUT}"] == (key,)
    for column in ("adam:ADSL.TRTSDT", "adam:ADSL.SAFFL", "adam:ADAE.TRTSDT",
                   "adam:ADAE.TRTEMFL"):
        assert made.pending[column] == (key,), column
    assert "TRTSDT" not in made.adam["ADSL"].column_names
    assert {"USUBJID", "TRT01P", "RANDFL"} <= set(made.adam["ADSL"].column_names)


def test_pending_cells_are_neither_right_nor_wrong():
    """build.score on two small grids: the cells of a pending row leave every
    denominator, and the axis of rows is held without them."""
    columns = ["Placebo", "Drug"]

    def grid(rows):
        made = []
        for number, (label, texts) in enumerate(rows.items(), start=1):
            made.append({"id": f"r{number}", "label": label, "cells": [
                {"id": f"cell:Out_A/r{number}/c{n}", "column": f"c{n}", "text": text, "ard": []}
                for n, text in enumerate(texts, start=1)]})
        return {"schema": "specfirst/grid@0", "output_id": "Out_A", "titles": [],
                "footnotes": [], "rows": made,
                "columns": [{"id": f"c{n}", "label": label} for n, label in enumerate(columns, 1)]}

    gold = grid({"Any event": ["1", "2"], "Related event": ["0", "1"], "Fatal event": ["0", "0"]})
    ours = grid({"Any event": ["1", "2"], "Fatal event": ["0", "1"]})
    waiting = {"cell:Out_A/r2/c1": (KEY,), "cell:Out_A/r2/c2": (KEY,)}
    found = build.score("visible", {"Out_A": gold}, {"Out_A": ours}, pending=waiting)
    assert (found.correct, found.denominators()) == (
        3, {"shared_rows": 4, "produced": 4, "all": 4})
    assert [(w.row[1], w.column[0]) for w in found.wrong()] == [("Fatal event", "Drug")]
    assert found.outputs[0].rows_equal and found.pending_by_decision() == {KEY: 2}
    assert (found.strict, found.lenient) == (0, 0)
    # Without the pending map the same grids lack a row (ADR-005, decision 4).
    plain = build.score("visible", {"Out_A": gold}, {"Out_A": ours})
    assert (plain.correct, plain.denominators()["all"], plain.outputs[0].rows_equal) == (
        3, 6, False)
    # A whole output that waits is not produced and not wrong.
    every = {cell["id"]: (KEY,) for row in gold["rows"] for cell in row["cells"]}
    found = build.score("visible", {"Out_A": gold}, {}, pending=every)
    assert (found.produced, found.in_gold, found.waiting, found.wrong(),
            found.denominators()["all"]) == (0, 0, 1, [], 0)
    assert any("1 output waits" in line for line in found.lines())
    assert not found.perfect


def test_a_build_without_pending_cells_reads_as_before(machine, case):
    """No line of a score without pending cells changes (the logs of the gates of
    read-1a and read-2a)."""
    result = scorer.control(machine, case)
    assert result.pending == {}
    for score in result.builds.values():
        assert not any("pending" in line or "wait" in line for line in score.lines())

