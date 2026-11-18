"""The scorer on a generated kit (specfirst.score.kit; PLAN.md section 13.6, read-1).

One kit is written once for the module, without the R engine, as the tests
of the generator write theirs (tests/unit/test_gen_kits.py). It is kit 7 of
a set: its scenario states an emergence window of days, so the planted
window applies. What a kit of another seed decides is not asserted here:
the tests hold what must be true of every kit, and the checks of the module
against planted defects (rule R5).
"""

from __future__ import annotations

import copy
import dataclasses
import json
import shutil

import pytest

from specfirst.gen import decisions
from specfirst.gen import kits as genkits
from specfirst.score import attribute, command, defects, report, scorer
from specfirst.score import kit as kits

SEED = "unit-score"
NUMBER = 7


@pytest.fixture(scope="module")
def folder(root, tmp_path_factory):
    out = tmp_path_factory.mktemp("score-kits") / f"kit-{NUMBER:03d}"
    genkits.generate(root, genkits.kit_seed(SEED, NUMBER), out, genkits.split_of(NUMBER),
                     with_r=False, number=NUMBER)
    return out


@pytest.fixture(scope="module")
def kit(folder):
    return kits.load(folder)


@pytest.fixture(scope="module")
def machine(root, kit):
    return kits.machine_of(root, kit)


@pytest.fixture(scope="module")
def scored(machine, kit):
    lines: list[str] = []
    return kits.score_kit(machine, kit, lines.append, "kit-007"), lines


def test_a_kit_is_read_as_a_case(machine, kit):
    assert kit.units == decisions.SLICE_UNITS and set(kit.data) == {"visible", "twin"}
    case = kits.case(kit, machine.catalog)
    assert case.units == kit.units and case.standard_form == "sap"
    assert set(case.documents.texts) == {"sap", "house"}
    assert kits.case(kit, machine.catalog, "T").units == ("tfl-ae-summary",)
    arms = case.arms(case.gold_vector())
    assert len(arms) == kit.manifest["study"]["arms"]
    assert all(set(arm) == {"code", "dose", "names"} for arm in arms)
    # The other values of a decision are those the matrix of the kit was built with.
    key = ("tfl.population", "tfl-ae-summary")
    gold = next(r["value"] for r in kit.records if (r["id"], r["unit"]) == key)
    others = case.variants(key)
    assert others and gold not in others
    assert {pair["second"] for item in kit.matrix["decisions"] if item["id"] == key[0]
            for pair in item["pairs"] if pair["gold"]} == {value["rule"] for value in others}
    assert case.variants(("no.such.entry", "tfl-ae-summary")) == []


def test_a_folder_that_is_no_kit_is_refused(tmp_path):
    with pytest.raises(kits.KitError, match="not a kit"):
        kits.load(tmp_path)


def test_a_kit_whose_files_are_not_those_of_its_manifest_is_refused(folder, tmp_path):
    """Rule R3 (review of read-1a, finding R6). A decision marked unseparated, or
    given another class, would be scored in another way, and the gold check does
    not see it: the hashes of the manifest do."""
    drifted = tmp_path / "kit"
    shutil.copytree(folder, drifted)
    path = drifted / "gold" / "decisions.jsonl"
    lines = path.read_text(encoding="ascii").splitlines()
    record = json.loads(lines[0])
    record["identifiable"] = "unseparated" if record.get("identifiable") != "unseparated" \
        else "separated"
    lines[0] = json.dumps(record, sort_keys=True, separators=(",", ":"))
    path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    with pytest.raises(kits.KitError, match="not the files of kit.yaml.*gold/decisions.jsonl"):
        kits.load(drifted)
    assert command.main(drifted.parent.parent, ["kit", str(drifted), "--arm", "C"]) == 1


def test_the_gold_of_the_kit_is_built_again(machine, kit):
    """The scorer builds gold from the gold decisions; it must be the gold of the files."""
    assert kits.gold_problems(machine, kit) == []


def test_the_gold_check_fails_on_another_gold(machine, kit):
    """Rule R5: a grid text, a result, a value of an ADaM column, a gold decision."""
    grids = copy.deepcopy(kit.grids)
    cell = next(iter(grids["visible"].values()))["rows"][1]["cells"][0]
    cell["text"] = "999"
    found = kits.gold_problems(machine, dataclasses.replace(kit, grids=grids))
    assert len(found) == 1 and "visible" in found[0] and "'999'" in found[0]

    grids = copy.deepcopy(kit.grids)
    cell = next(iter(grids["twin"].values()))["rows"][1]["cells"][0]
    cell["ard"] = cell["ard"][:1]  # the same texts, another trace
    found = kits.gold_problems(machine, dataclasses.replace(kit, grids=grids))
    assert len(found) == 1 and "the same texts" in found[0]

    ard = copy.deepcopy(kit.ard)
    key = next(iter(ard["twin"]))
    ard["twin"][key]["raw_value"] += 1
    found = kits.gold_problems(machine, dataclasses.replace(kit, ard=ard))
    assert found == [f"twin: result {key}: differs in the scorer's build"]

    adam = {which: dict(tables) for which, tables in kit.adam.items()}
    adam["visible"]["ADSL"] = adam["visible"]["ADSL"].drop_columns(["SAFFL"])
    found = kits.gold_problems(machine, dataclasses.replace(kit, adam=adam))
    assert any("visible: adam:ADSL.SAFFL" in problem for problem in found)

    other = next(value for value in kits.options(kit, machine.catalog, (
        "tfl.population", "tfl-ae-summary"))[1:])
    records = [{**r, "value": other} if r["id"] == "tfl.population" else r for r in kit.records]
    found = kits.gold_problems(machine, dataclasses.replace(kit, records=records))
    assert found and all("visible" in problem or "twin" in problem for problem in found)


def test_the_parser_control_scores_100_percent_on_the_kit(scored, kit):
    found, lines = scored
    assert found.gold == [] and found.control_holds
    scoped = sum(1 for r in kit.records if r["unit"] in kit.units)
    for stage, decisions_scored in (("C", scoped), ("T", 7)):
        result = found.control[stage]
        assert result.perfect and result.silent == [] and result.behind == {}
        for name in ("value", "status", "quote", "span"):
            assert result.reading.total(name) == (decisions_scored, decisions_scored)
    assert any(line.startswith("  arm C, stage T:") and line.endswith(": 100%") for line in lines)


def test_the_standard_alone_cannot_build_the_chain_of_a_kit(scored):
    """ae.related.values has no house default: every kit states it, and arm S cannot."""
    chain = scored[0].standard["C"]
    assert "ae.related.values" in [item.key[0] for item in chain.reading.wrong()]
    for score in chain.builds.values():
        assert not score.valid and score.produced == 0 and "ae.related.values" in score.failure
    table = scored[0].standard["T"]
    assert all(score.valid and score.produced == 1 for score in table.builds.values())


def test_no_planted_defect_fails_on_the_kit_and_the_matrix_agrees(scored):
    found, _ = scored
    states = {outcome.defect.id: outcome.state for outcome in found.outcomes}
    assert len(states) == 12 and found.failed == [] and found.matrix == []
    assert set(states.values()) <= {"passed", "silent", "not planted"}
    # What is planted in the results, in the ARS file or in a citation shows on every kit.
    for name in ("S1-arms", "S4-denominator", "S7-rounded", "S11-quote", "S12-span"):
        assert states[name] == "passed", name
    # The order of the columns: the decision and the step of the build show together.
    assert (states["S9-sort"] == "passed") == (states["S9-sort-build"] == "passed")
    # The scenario of the kit states a window of days.
    assert states["S3-window"] != "not planted"
    for outcome in found.outcomes:
        if outcome.state == "silent":
            assert all(score.perfect for score in outcome.result.builds.values())
            assert outcome.planted.decision in outcome.result.silent
    assert found.passed


def test_the_checks_of_a_kit_fail_on_their_planted_defects(machine, kit, scored):
    lines: list[str] = []
    assert kits.planted(machine, kit, scored[0], lines.append)
    assert len(lines) == 3 and all(line.endswith("fails: yes") for line in lines)
    assert _without(kit, "no-such-anchor") == kit.documents.texts["sap"]


def _without(kit, anchor):
    return kits._without_statement(kit.documents.texts["sap"], anchor)


def test_a_statement_is_taken_out_of_a_document(kit):
    stated = next(r for r in kit.records if r["status"] == "stated")
    anchor = stated["citations"][0]["anchor"]
    text = _without(kit, anchor)
    assert f"[{anchor}] " in kit.documents.texts["sap"] and f"[{anchor}] " not in text
    assert stated["statement"] not in " ".join(text.split())


def test_the_sweep_of_the_matrix_has_no_problem(scored, kit):
    """Every pair of the matrix, as the one wrong decision of a candidate; then pairs
    of two wrong decisions."""
    swept = scored[0].sweep
    pairs = [pair for item in kit.matrix["decisions"] for pair in item["pairs"] if pair["gold"]]
    assert swept.problems == []
    assert swept.values == len(pairs) > 15
    assert swept.decisions == len(kit.matrix["decisions"])
    assert swept.shown == sum(1 for pair in pairs if pair["separated"])
    assert swept.silent + swept.visible_only == sum(1 for pair in pairs if not pair["separated"])
    assert swept.cells > 0 and 0 < swept.counted <= swept.values
    assert all(where == {kits.OWNING_LAYER[name]} for name, where in swept.layers.items())
    assert 0 < swept.pairs <= kits.PAIR_MODULES * kits.PAIR_TABLES
    assert swept.pair_cells == swept.one_cause + swept.both_causes + swept.together > 0


def test_the_layer_of_a_decision_is_what_the_compile_says_it_sets(kit):
    """`OWNING_LAYER` against gold/spec/compile.json of the kit: a decision that
    binds an ADaM column acts at L4, one that binds an element of the ARS file and
    no column at L5, and a decision of the display binds neither."""
    with open(kit.folder / "gold" / "spec" / "compile.json", encoding="ascii") as handle:
        compiled = json.load(handle)
    seen = set()
    for item in compiled["decisions"]:
        if item["id"] not in kits.OWNING_LAYER:
            continue  # a decision of mod-demographics: not of the slice
        kinds = {bind.split(":")[0] for bind in item["binds"]}
        layer = kits.OWNING_LAYER[item["id"]]
        if "adam" in kinds:
            assert layer == "L4", item["id"]
        elif "ars" in kinds:
            assert layer == "L5", item["id"]
        if layer == "L7":
            assert not kinds and item["layout"], item["id"]
        seen.add(item["id"])
    assert {record["id"] for record in kit.records if record["unit"] in kit.units} <= seen
    assert set(kits.OWNING_LAYER.values()) == {"L4", "L5", "L7"}


def test_the_sweep_fails_on_a_matrix_that_says_the_opposite(machine, kit):
    """Rule R5 for the sweep: one pair of the matrix is turned around; another has
    another number of changed cells."""
    matrix = copy.deepcopy(kit.matrix)
    item = next(item for item in matrix["decisions"] if item["id"] == "tfl.population")
    pair = next(pair for pair in item["pairs"] if pair["gold"])
    pair["separated"] = not pair["separated"]
    swept = kits.sweep(machine, dataclasses.replace(kit, matrix=matrix))
    assert len(swept.problems) == 1
    assert swept.problems[0].startswith(f"tfl.population = {pair['second']}: the matrix says")

    # A decision that changes cells and no axis: the end of treatment emergence, which
    # the scenario of this kit states and its twin separates.
    matrix = copy.deepcopy(kit.matrix)
    item = next(item for item in matrix["decisions"] if item["id"] == "ae.teae.end")
    pair = next(pair for pair in item["pairs"] if pair["gold"] and pair["separated"])
    pair["cells"] += 1
    swept = kits.sweep(machine, dataclasses.replace(kit, matrix=matrix))
    assert swept.problems == [
        f"ae.teae.end = {pair['second']}: the matrix counts {pair['cells']} changed "
        f"cells on the twin, the scorer {pair['cells'] - 1}"]


def test_the_sweep_fails_when_a_cell_is_owned_by_no_decision(machine, kit, monkeypatch):
    """Rule R5 for the ownership: a machine that proves no `decides` edge."""
    monkeypatch.setattr(machine, "changes", lambda records, key, value: set())
    swept = kits.sweep(machine, kit)
    # The decision is still found, by running; that no element names it is the problem.
    assert swept.problems and any("the decision owns it by running alone" in problem
                                  for problem in swept.problems)


def test_the_sweep_fails_on_a_scorer_that_is_wrong(machine, kit, monkeypatch):
    """Rule R5, the mutants of the review of read-1a (finding R3): every second
    wrong cell without an owner; two layers that exchange their names; an owner that
    is the first differing decision whatever it decides, called confirmed."""
    real = attribute.attribute

    def half(*args, **kwargs):
        owners, axes = real(*args, **kwargs)
        return owners[::2], axes

    monkeypatch.setattr(attribute, "attribute", half)
    swept = kits.sweep(machine, kit)
    assert any("wrong cells and axes have" in problem for problem in swept.problems)

    def exchanged(*args, **kwargs):
        owners, axes = real(*args, **kwargs)
        for owner in [*owners, *axes]:
            owner.layer = {"L5": "L7", "L7": "L5"}.get(owner.layer, owner.layer)
        return owners, axes

    monkeypatch.setattr(attribute, "attribute", exchanged)
    swept = kits.sweep(machine, kit)
    assert any("owned at layer L7; the decision acts at L5" in problem
               for problem in swept.problems)

    monkeypatch.setattr(attribute, "attribute", real)
    monkeypatch.setattr(attribute, "_settle", lambda claims, differing, holds: (
        claims[0], (differing[0],), True, ""))
    swept = kits.sweep(machine, kit)
    assert any(" with " in problem and "alone, it is wrong under" in problem
               for problem in swept.problems)


def test_a_wrong_value_of_an_unseparated_decision_is_compared_by_value(machine, kit):
    """ADR-007, the owner's answer on decision 6: where the matrix of a kit says
    `unseparated`, the scorer compares decision values and reports the decision apart."""
    item = next(item for item in kit.matrix["decisions"] if item["identifiable"] == "unseparated")
    key = (item["id"], item["unit"])
    case = kits.case(kit, machine.catalog)
    records, documents = scorer.control_records(machine, case)
    other = case.variants(key)[0]
    candidate = [{**r, "value": other} if (r["id"], r["unit"]) == key else r for r in records]
    result = scorer.run(machine, case, candidate, documents=documents)
    assert [score.key for score in result.reading.wrong()] == [key]
    assert result.builds["twin"].perfect and not result.perfect
    text = "\n".join(report.lines(result))
    assert "unseparated in gold, compared by value only" in text
    assert f"{key[0]} (wrong)" in text


def test_a_set_passes_only_when_every_kit_and_every_defect_does(root, folder, scored, kit,
                                                                monkeypatch):
    found, _ = scored
    monkeypatch.setattr(kits, "score_kit", lambda machine, kit, out, name="": found)
    lines: list[str] = []
    everywhere = all(outcome.state == "passed" for outcome in found.outcomes)
    assert kits.score_set(root, folder.parent, lines.append) is everywhere
    assert "gold built again is the gold of the kit: 1 of 1 kits" in lines
    assert "parser control 100% in both stages: 1 of 1 kits" in lines
    assert "planted defects that failed: 0" in lines
    assert lines[-1] == f"kits: {'PASS' if everywhere else 'FAIL'}"

    # A planted defect that is not attributed fails the set, whatever else holds.
    broken = copy.copy(found)
    first = found.outcomes[0]
    broken.outcomes = [dataclasses.replace(first, attributed=False), *found.outcomes[1:]]
    monkeypatch.setattr(kits, "score_kit", lambda machine, kit, out, name="": broken)
    lines = []
    assert kits.score_set(root, folder.parent, lines.append) is False
    assert f"planted defects that failed: 1: {first.defect.id} on {kit.id}" in lines
    assert lines[-1] == "kits: FAIL"

    lines = []
    assert kits.score_set(root, folder, lines.append) is False  # a kit folder holds no kit
    assert lines == [f"{folder}: no kit"]


def test_the_command_scores_a_kit(root, folder, capsys):
    assert command.main(root, ["kit", str(folder), "--arm", "C", "--stage", "T"]) == 0
    text = capsys.readouterr().out
    assert "arm C, stage T" in text and "every score is 100%" in text
    assert command.main(root, ["kit", str(folder / "gold")]) == 1
    assert "cannot score" in capsys.readouterr().out


def test_a_silent_plant_is_neither_passed_nor_failed():
    by_id = {defect.id: defect for defect in defects.DEFECTS}
    planted = defects.Planted("a decision", [], decision=("x", "u"), value={"rule": "y"})
    outcome = defects.Outcome(by_id["S9-sort"], planted, silent=True)
    assert outcome.state == "silent" and not outcome.passed
    assert defects.Outcome(by_id["S9-sort"]).state == "not planted"
    assert defects.Outcome(by_id["S6-quantile"]).state == "does not apply"
    assert defects.Outcome(by_id["S9-sort"], planted).state == "failed"
