"""Gold from decisions, on the tiny hand-made study (specfirst.gen.gold, display, verify).

The tiny study of specfirst.compile.tiny has four subjects and the edge
cases of the house specs: partial exposure dates, a dose without
randomization, an event collected as a month. Every alternative of every
decision of the slice is compiled and built on it by the machine, and the
grid is held against the hand calculation of specfirst.gen.reference: two
programs that share nothing must give the same table, cell by cell.
"""

from __future__ import annotations

import copy

import pytest

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.compile import tiny
from specfirst.gen import decisions, display, gold, reference, verify
from specfirst.machine import grid, methods

# The protocol of the tiny study, as far as a table needs it: low dose listed first.
ARMS = [{"code": "LOW", "dose": 10.0, "names": ["Low", "Low Dose"]},
        {"code": "PBO", "dose": 0.0, "names": ["PLACEBO", "Placebo"]}]
MAP = [{"code": "PBO", "label": "Placebo"}, {"code": "LOW", "label": "Low"}]
# Every alternative of every entry of the slice, with slot values that fit the tiny study.
VARIANTS: dict[str, list[dict]] = {
    "trt.planned.source": [{"rule": "dm_arm"}, {"rule": "dm_armcd_map", "map": MAP}],
    "trt.actual.source": [{"rule": "dm_actarm"}, {"rule": "first_ex_treatment"},
                          {"rule": "same_as_planned"}],
    "trt.start.source": [{"rule": "first_ex_with_dose"}, {"rule": "first_ex_record"},
                         {"rule": "dm_rfxstdtc"}],
    "trt.end.source": [{"rule": "last_ex_end_date"}, {"rule": "last_ex_start_date"},
                       {"rule": "ds_date_when_ex_missing"}, {"rule": "last_ex_record_end"}],
    "trt.date.imputation": [{"rule": "not_completed"}, {"rule": "first_day_of_month"}],
    "date.studyday.origin": [{"rule": "treatment_start"}, {"rule": "dm_rfstdtc"}],
    "pop.randomized.rule": [{"rule": "all_randomized"},
                            {"rule": "randomized_with_postbaseline", "test": "SYSBP"},
                            {"rule": "randomized_with_postbaseline", "test": "WEIGHT"}],
    "pop.safety.rule": [{"rule": "at_least_one_dose"}, {"rule": "randomized_and_dosed"}],
    "pop.safety.grouping": [{"rule": "actual"}, {"rule": "planned"}],
    "pop.efficacy.rule": [{"rule": "baseline_and_postbaseline", "test": "SYSBP"},
                          {"rule": "baseline_and_postbaseline", "test": "WEIGHT"},
                          {"rule": "attended_visit", "visit": "WEEK 2"},
                          {"rule": "attended_visit", "visit": "WEEK 4"}],
    "disp.status.record": [{"rule": "disposition_event"},
                           {"rule": "disposition_event_by_subcategory",
                            "subcategory": "STUDY PARTICIPATION"},
                           {"rule": "disposition_event_by_subcategory",
                            "subcategory": "STUDY TREATMENT"}],
    "ae.start.imputation": [{"rule": "first_of_month_not_before_first_dose"},
                            {"rule": "first_of_month"}, {"rule": "not_completed"}],
    "ae.teae.start": [{"rule": "on_or_after_first_dose_date"},
                      {"rule": "at_or_after_first_dose_time"}, {"rule": "by_time_when_collected"}],
    "ae.teae.end": [{"rule": "no_end"}, {"rule": "last_dose_plus_days", "days": 30},
                    {"rule": "last_dose_plus_days", "days": 2}],
    "ae.related.values": [{"rule": "stated_list", "values": ["POSSIBLE", "PROBABLE"]},
                          {"rule": "stated_list", "values": ["PROBABLE"]}],
    "tfl.output.include": [{"rule": "included"}, {"rule": "not_included"}],
    "tfl.population": [{"rule": "safety"}, {"rule": "randomized"}, {"rule": "efficacy"}],
    "tfl.columns.arms": [{"rule": "ascending_dose_placebo_first"}, {"rule": "protocol_order"}],
    "tfl.columns.total": [{"rule": "all_arms"}, {"rule": "none"},
                          {"rule": "active_arms", "control": "Placebo"}],
    "tfl.percent.format": [{"rule": "one_decimal_zero_blank", "decimals": 1},
                           {"rule": "one_decimal_always", "decimals": 1},
                           {"rule": "one_decimal_always", "decimals": 0},
                           {"rule": "one_decimal_zero_blank", "decimals": 2}],
    "tfl.rounding.rule": [{"rule": "half_away_from_zero"}, {"rule": "half_even"}],
    "tfl.ae.summary.rows": [{"rule": "standard_rows"},
                            {"rule": "stated_rows", "rows": ["SERIOUS", "ANY", "FATAL"]},
                            {"rule": "stated_rows", "rows": ["SERIOUS_RELATED", "ANY",
                                                             "DOSE_MODIFIED", "FATAL_RELATED"]}],
}


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


@pytest.fixture(scope="module")
def house(root):
    return houses.load(houses.default_dir(root))


@pytest.fixture(scope="module")
def rows():
    """The tiny study as rows, the way a study is read back from Dataset-JSON."""
    return {name.upper(): table.to_pylist() for name, table in tiny.tables().items()}


@pytest.fixture(scope="module")
def bench(root, catalog, house, tmp_path_factory):
    kit = tmp_path_factory.mktemp("tiny-kit")
    tiny.write(kit / gold.PLACES["visible"][0])
    return gold.Workbench(root, catalog, house, kit, "visible",
                          tmp_path_factory.mktemp("tiny-scratch"))


def _records(catalog, house, values):
    """The vector of a kit of the slice: these values, the other modules at the default,
    the other outputs not included."""
    found = []
    for entry_id, unit in catalog.keys():
        kind = catalog.units[unit].kind
        if entry_id in values and (unit == decisions.OUTPUT_UNIT or (
                kind == "module" and unit in decisions.SLICE_UNITS)):
            found.append({"id": entry_id, "unit": unit, "value": values[entry_id]})
        elif unit in decisions.DEFAULT_UNITS:
            found.append({"id": entry_id, "unit": unit,
                          "value": houses.default_value(catalog, house, entry_id, unit)})
        elif entry_id == "tfl.output.include" and kind == "table_family":
            found.append({"id": entry_id, "unit": unit, "value": {"rule": "not_included"}})
    return found


BASE = {entry_id: options[0] for entry_id, options in VARIANTS.items()}


def test_the_variants_are_the_alternatives_of_the_slice(catalog):
    entries = {entry.id: entry for entry in catalog.entries.values()
               if set(entry.units) & set(decisions.SLICE_UNITS)}
    assert set(VARIANTS) == set(entries)
    for entry_id, options in VARIANTS.items():
        assert {value["rule"] for value in options} == {
            alternative.id for alternative in entries[entry_id].alternatives}, entry_id


def test_the_machine_and_the_hand_calculation_agree_on_every_alternative(catalog, house,
                                                                          bench, rows):
    """P2 on the tiny study, for the base vector and every single change of it, and for
    every change beside three other bases that make the quiet decisions speak."""
    bases = [
        BASE,
        {**BASE, "tfl.population": {"rule": "randomized"},
         "pop.safety.grouping": {"rule": "planned"}},
        {**BASE, "tfl.population": {"rule": "efficacy"},
         "ae.teae.end": {"rule": "last_dose_plus_days", "days": 2},
         "ae.teae.start": {"rule": "at_or_after_first_dose_time"}},
        {**BASE, "ae.teae.end": {"rule": "last_dose_plus_days", "days": 30},
         "trt.date.imputation": {"rule": "first_day_of_month"},
         "trt.actual.source": {"rule": "first_ex_treatment"},
         "tfl.percent.format": {"rule": "one_decimal_always", "decimals": 1}},
    ]
    compared, empty, tables = 0, 0, set()
    for base in bases:
        for entry_id, options in VARIANTS.items():
            for value in options:
                values = {**base, entry_id: value}
                try:
                    shown = bench.show(_records(catalog, house, values), ARMS)
                except gold.GoldError as error:
                    # Four subjects: some analysis sets are empty. Neither program builds
                    # a table without a treatment column.
                    assert "in the analysis set has a value" in str(error), (entry_id, value)
                    assert verify.p2(rows, values, ARMS, None)[0].startswith(
                        "the reference cannot be calculated: no subject of the analysis set")
                    empty += 1
                    continue
                made = next(iter(shown.grids.values()), None)
                problems = verify.p2(rows, values, ARMS, made)
                assert problems == [], (entry_id, value, problems[:3])
                compared += 1
                tables.add(str(verify.table_view(made)))
    assert compared + empty == 4 * sum(len(options) for options in VARIANTS.values())
    assert empty < compared / 4
    # The comparison is not of one table with itself: the variants give many tables.
    assert len(tables) > 25
    # Far fewer runs of yamaa than builds: equal ADaM specs are run once.
    assert bench.runs < compared / 2


def test_the_base_table_of_the_tiny_study(catalog, house, bench, rows):
    """The numbers themselves, counted on paper from specfirst.compile.tiny."""
    shown = bench.show(_records(catalog, house, BASE), ARMS)
    made = shown.grids["Out_AESUM"]
    view = verify.table_view(made)
    # Safety set by actual treatment: S2 in Placebo; S1 and S4 in Low Dose. S3 was never
    # dosed.
    assert view["columns"] == ["Placebo", "Low Dose", "Total"]
    assert view["rows"][0] == ["", ["(N=1)", "(N=2)", "(N=3)"]]
    texts = display.texts(made)
    # S1: nausea on the day of the first dose and a serious headache later; S2: three
    # events, the first collected as its month and completed to the first dose date.
    assert texts[("Any adverse event", "Placebo")] == "1 (100.0)"
    assert texts[("Any adverse event", "Low Dose")] == "1 ( 50.0)"
    assert texts[("Serious adverse event", "Low Dose")] == "1 ( 50.0)"
    assert texts[("Serious adverse event", "Placebo")] == "0"
    assert texts[("Fatal adverse event", "Total")] == "0"
    assert made["titles"] == ["Summary of Treatment-Emergent Adverse Events"]
    assert grid.grid_problems(made, bench.root) == []
    # Every cell names the ARD rows it shows, and a count of zero has a row behind it.
    by_id = {row["id"]: row for row in shown.rows}
    for row in made["rows"]:
        for cell in row["cells"]:
            assert cell["ard"] and all(key in by_id for key in cell["ard"])
    zero = next(cell for row in made["rows"] for cell in row["cells"] if cell["text"] == "0")
    assert by_id[zero["ard"][0]]["raw_value"] == 0 and len(zero["ard"]) == 1


def test_the_groups_of_a_treatment_grouping_are_listed(catalog, house, bench):
    shown = bench.show(_records(catalog, house, BASE), ARMS)
    assert shown.compiled.ars["analysisGroupings"][0]["dataDriven"] is True
    grouping = next(g for g in shown.data["analysisGroupings"] if g["id"] == "Grp_TRT01A")
    assert grouping["dataDriven"] is False
    # IDs by the sorted values, order by the rule of the layout.
    assert [(g["id"], g["name"], g["order"]) for g in grouping["groups"]] == [
        ("Grp_TRT01A_1", "Low Dose", 2), ("Grp_TRT01A_2", "Placebo", 1)]
    other = bench.show(_records(catalog, house, {
        **BASE, "tfl.columns.arms": {"rule": "protocol_order"}}), ARMS)
    grouping = next(g for g in other.data["analysisGroupings"] if g["id"] == "Grp_TRT01A")
    assert [(g["id"], g["order"]) for g in grouping["groups"]] == [
        ("Grp_TRT01A_1", 1), ("Grp_TRT01A_2", 2)]
    # The results are the same rows under both orders; only the grid differs.
    assert shown.rows == other.rows
    assert verify.table_view(other.grids["Out_AESUM"])["columns"] == [
        "Low Dose", "Placebo", "Total"]
    assert gold.order_values(["B", "Placebo", "Low Dose"], ARMS, "protocol_order") == [
        "Low Dose", "Placebo", "B"]
    with pytest.raises(gold.GoldError, match="unknown column order"):
        gold.order_values(["A"], ARMS, "by_size")


def test_the_mock_shell_shows_masks(catalog, house, bench):
    shown = bench.show(_records(catalog, house, BASE), ARMS)
    layout = shown.compiled.layouts[decisions.OUTPUT_UNIT]
    shell = display.build(shown.event, layout, None)
    made = shown.grids["Out_AESUM"]
    assert [c["label"] for c in shell["columns"]] == [c["label"] for c in made["columns"]]
    cells = [cell["text"] for row in shell["rows"] for cell in row["cells"]]
    assert set(cells) == {"(N=xx)", "xx (xxx.x)"}
    assert grid.grid_problems(shell, bench.root) == []


def test_planted_display_defects_are_seen(catalog, house, bench, rows):
    """Rule R5 for the comparison with the reference: a wrong grid is not the reference."""
    shown = bench.show(_records(catalog, house, BASE), ARMS)
    made = shown.grids["Out_AESUM"]
    assert verify.p2(rows, BASE, ARMS, made) == []
    # A changed text, a column that moved, a row that is missing.
    broken = copy.deepcopy(made)
    broken["rows"][1]["cells"][1]["text"] = "2 (100.0)"
    found = verify.p2(rows, BASE, ARMS, broken)
    assert found == ["row 'Any adverse event', column 'Low Dose': the grid '2 (100.0)', the "
                     "reference '1 ( 50.0)'"]
    broken = copy.deepcopy(made)
    broken["columns"][0], broken["columns"][1] = broken["columns"][1], broken["columns"][0]
    assert verify.p2(rows, BASE, ARMS, broken)[0].startswith("columns: the grid")
    broken = copy.deepcopy(made)
    del broken["rows"][2]
    assert verify.p2(rows, BASE, ARMS, broken)[0].startswith("rows: the grid")
    assert verify.p2(rows, BASE, ARMS, None) == ["the reference has the output, the grid has not"]
    # A builder that rounds the other way, or shows a zero the other way.
    layout = copy.deepcopy(shown.compiled.layouts[decisions.OUTPUT_UNIT])
    layout["formats"]["percent"]["zero_count"] = "count_and_percent"
    wrong = display.build(shown.event, layout, {row["id"]: row for row in shown.rows})
    assert len(verify.p2(rows, BASE, ARMS, wrong)) >= 3
    layout["formats"]["rounding"] = "half_up"
    with pytest.raises(display.DisplayError, match="rounding"):
        display.build(shown.event, layout, {})
    # A result the layout shows and the ARD lacks is an error, not an empty cell.
    by_id = {row["id"]: row for row in shown.rows}
    del by_id[made["rows"][1]["cells"][0]["ard"][0]]
    with pytest.raises(display.DisplayError, match="the ARD does not have it"):
        display.build(shown.event, shown.compiled.layouts[decisions.OUTPUT_UNIT], by_id)
    assert verify.changed_cells(verify.table_view(made), verify.table_view(wrong)) >= 3
    # Every cell of the table: three columns, the header and the six standard rows.
    assert verify.changed_cells(verify.table_view(made), None) == 21


def test_rounding_rules_of_the_registry_differ_at_a_half():
    assert methods.pattern_text(6.25, "(XXX.X)") == "(  6.3)"
    assert methods.pattern_text(6.25, "(XXX.X)", rounding="half_even") == "(  6.2)"
    assert methods.round_half_even(18.75, 1) == "18.8" and methods.round_half_even(2.5, 0) == "2"
    assert methods.round_half_even(None, 1) is None
    with pytest.raises(methods.MethodError):
        methods.pattern_text(1.0, "XX.X", rounding="half_down")
    assert reference.rounded.__module__ != methods.__name__   # two implementations


def test_not_before_moves_a_partial_start_only_within_its_month(root, catalog, house,
                                                                tmp_path):
    """The point the review of gen-1a left open: what yamaa's `not_before` does with a
    partial start date in a month before the treatment start.

    S1 is dosed from 2024-03-10. It gets two more events: one collected as
    "2024-03", one as "2024-02", both ongoing. The first alternative of
    ae.start.imputation reads "the first day of that month, or ... the
    treatment start date when it falls in that month".
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    kit = tmp_path / "kit"
    tiny.write(kit / gold.PLACES["visible"][0])
    path = kit / gold.PLACES["visible"][0] / "ae.parquet"
    table = pq.read_table(path)
    first = table.slice(0, 1).to_pylist()[0]
    more = [{**first, "USUBJID": "S1", "AESEQ": seq, "AESTDTC": start, "AEENDTC": None}
            for seq, start in ((8, "2024-03"), (9, "2024-02"))]
    pq.write_table(pa.concat_tables([table, pa.Table.from_pylist(more, schema=table.schema)]),
                   path)
    bench = gold.Workbench(root, catalog, house, kit, "visible", tmp_path / "scratch")
    found = {}
    for rule in ("first_of_month_not_before_first_dose", "first_of_month", "not_completed"):
        values = {**BASE, "ae.start.imputation": {"rule": rule}}
        shown = bench.show(_records(catalog, house, values), ARMS)
        adae = next(plan for plan in shown.plans if plan.name == "ADAE").table.to_pylist()
        found[rule] = {row["AESEQ"]: (str(row["ASTDT"]) if row["ASTDT"] else None,
                                      row["TRTEMFL"])
                       for row in adae if row["USUBJID"] == "S1" and row["AESEQ"] in (8, 9)}
    # In the month of the first dose the date moves up to the dose; in an earlier month
    # it stays the first day of its own month, before the dose, and the event is not
    # emergent. The engine does what the statement says.
    assert found["first_of_month_not_before_first_dose"] == {
        8: ("2024-03-10", "Y"), 9: ("2024-02-01", None)}
    assert found["first_of_month"] == {8: ("2024-03-01", None), 9: ("2024-02-01", None)}
    assert found["not_completed"] == {8: (None, "Y"), 9: (None, "Y")}
    # So the earlier month separates the first alternative from "not completed", and the
    # month of the dose separates it from the plain first day. The hand calculation reads
    # the statement the same way.
    import datetime

    dose = datetime.date(2024, 3, 10)
    for rule, by_seq in found.items():
        for seq, text in ((8, "2024-03"), (9, "2024-02")):
            ours = reference.analysis_start(text, dose, rule)
            assert (ours.isoformat() if ours else None) == by_seq[seq][0], (rule, seq)
