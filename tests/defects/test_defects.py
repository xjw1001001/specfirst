"""Planted defects on the pilot: the result checks must catch each one (rule R5).

PLAN.md section 13.3 (gate of real-2) names four. Each is planted as the
real case (lessons 9 and 16): in the ARS example or the binding the kit
pins, run by the real engines on the ADaM datasets the kit builds, and
judged by the functions the gate itself calls (`build.judge` for P2 with
the kit's exceptions, `results.agreement` for rule R11).

    D1-arms      the low dose and the high dose group exchange their conditions (E3)
    D2-set       the analysis set reads another population flag
    D3-quantile  the quantile definition is R's default, not SAS's (E4)
    D4-subset    an analysis loses its data subset
    D5-engines   each of the four planted in the R engine's input alone: the
                 two engines must be seen to disagree

Every case first shows that the unchanged inputs pass. A defect that the
pilot data cannot show is reported as such, not counted as caught: on these
data the safety set and the intent-to-treat set hold the same 254 subjects,
so exchanging them changes no result (D2 says so and uses the
efficacy-evaluable flag for the defect that must be caught).

These tests need `specfirst fetch`, the engine and R, and carry the marker
`evidence`. Without them they are skipped, except under SPECFIRST_STRICT=1
(set by the gate), where they fail.
"""

from __future__ import annotations

import copy
import json
import os
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest

from specfirst import kit as kits
from specfirst.machine import ard, ars, build, registry, rengine, results
from specfirst.paths import cache_dir, repo_root

pytestmark = pytest.mark.evidence

KIT = "cdiscpilot01"
TREATMENT, LOW, HIGH = "AnlsGrouping_01_Trt", "AnlsGrouping_01_Trt_2", "AnlsGrouping_01_Trt_3"
SAFETY, ITT = "AnalysisSet_02_SAF", "AnalysisSet_01_ITT"
OVERVIEW = "An07_01_TEAE_Summ_ByTrt"


class Missing(RuntimeError):
    """The fetch cache, the engine or R is not there."""


@dataclass
class Pilot:
    root: Path
    folder: Path  # a build of the kit, made for these tests
    spec: kits.ResultSet
    entries: list[dict]  # the kit's exceptions for the result set
    reference: ars.Event  # the example as pinned: its embedded results are the reference
    registry: registry.Registry
    gold: results.Rows  # what the Python engine gives on the unchanged inputs

    def data(self) -> dict:
        return copy.deepcopy(self.reference.data)

    def python(self, data: dict | None = None, binding: dict | None = None) -> results.Rows:
        """The Python engine on a changed reporting event or binding, and the built ADaM."""
        event = self.reference if data is None else ars.index(data)
        assert event.problems == []
        bound = ars.bind(event, self.registry, self.spec.binding if binding is None else binding)
        tables = ard.load_tables(self.folder / build.ADAM,
                                 ars.columns(event, self.spec.subject_key))
        return results.by_id(ard.run(event, self.registry, bound, tables, self.spec.subject_key))

    def r(self, work: Path, data: dict | None = None, binding: dict | None = None) -> results.Rows:
        """The R engine on a changed reporting event or binding, and the built ADaM."""
        event = self.reference if data is None else ars.index(data)
        bound = ars.bind(event, self.registry, self.spec.binding if binding is None else binding)
        tables = ard.load_tables(self.folder / build.ADAM,
                                 ars.columns(event, self.spec.subject_key))
        work.mkdir(parents=True, exist_ok=True)
        path = work / "event.json"
        path.write_text(json.dumps(event.data), encoding="ascii")
        rows, meta, _ = rengine.run(self.root, work, path, registry.json_path(self.root), bound,
                                    tables, self.spec.subject_key)
        assert rengine.data_problems(meta, tables) == []
        return results.by_id(rows)

    def judge(self, rows: results.Rows) -> tuple[bool, results.Comparison, list[str]]:
        """P2 for results, as the gate judges it: against the pinned example and its exceptions."""
        lines: list[str] = []
        ok, comparison = build.judge(
            "planted", self.reference, self.registry, rows, self.entries,
            build.alternatives(self.root, self.folder, self.spec), lines.append)
        return ok, comparison, lines


@pytest.fixture(scope="session")
def pilot(tmp_path_factory) -> Pilot:
    root = repo_root()
    try:
        if not (cache_dir(root) / "p7" / ".git").exists() or not (
                cache_dir(root) / "ars" / ".git").exists():
            raise Missing("not in the fetch cache: p7 or ars; run `specfirst fetch`")
        try:
            import yamaa  # noqa: F401
        except ImportError as error:
            raise Missing(f"yamaa is not installed: {error}") from error
        if not rengine.available():
            raise Missing("Rscript is not installed")
    except Missing as error:
        if os.environ.get("SPECFIRST_STRICT") == "1":
            pytest.fail(str(error))
        pytest.skip(str(error))
    folder = tmp_path_factory.mktemp("defects") / KIT
    said: list[str] = []
    assert build.build(root, KIT, into=folder, out=said.append) == 0, "\n".join(said)
    kit = kits.load_kit(root, KIT)
    spec = kit.results[0]
    inputs = build.result_inputs(root, folder, spec)
    entries = results.load_exceptions(folder / kit.exceptions)[spec.id]
    gold = results.by_id(ard.run(inputs.event, inputs.registry, inputs.binding, inputs.tables,
                                 spec.subject_key))
    return Pilot(root, folder, spec, entries, inputs.event, inputs.registry, gold)


def control(pilot: Pilot) -> list[str]:
    """The unchanged inputs pass: otherwise a failing check would prove nothing."""
    ok, comparison, lines = pilot.judge(pilot.gold)
    print(f"unchanged: {comparison.reproduced} of {comparison.total} reproduced, "
          f"{len(comparison.open)} explained, check passes: {ok}")
    return [] if ok else ["the unchanged inputs do not pass the check", *lines[-5:]]


def changed(pilot: Pilot, rows: results.Rows) -> list[str]:
    """The IDs whose value is not the gold value."""
    return sorted(key for key in set(rows) | set(pilot.gold)
                  if key not in rows or key not in pilot.gold
                  or not results.same(rows[key]["raw_value"], pilot.gold[key]["raw_value"]))


def exchange_arms(data: dict) -> dict:
    grouping = next(g for g in data["analysisGroupings"] if g["id"] == TREATMENT)
    low, high = (next(g for g in grouping["groups"] if g["id"] == key) for key in (LOW, HIGH))
    low["condition"], high["condition"] = high["condition"], low["condition"]
    return data


def other_flag(data: dict) -> dict:
    chosen = next(s for s in data["analysisSets"] if s["id"] == SAFETY)
    assert chosen["condition"]["variable"] == "SAFFL"
    chosen["condition"]["variable"] = "EFFFL"
    return data


def r_definition(pilot: Pilot) -> dict:
    binding = copy.deepcopy(pilot.spec.binding)
    binding["options"]["summary.continuous"]["quantile_definition"] = "r7"
    return binding


def without_subset(data: dict, analysis_id: str) -> dict:
    analysis = next(a for a in data["analyses"] if a["id"] == analysis_id)
    del analysis["dataSubsetId"]
    return data


def d1_arms(pilot: Pilot, tmp_path) -> list[str]:
    problems = control(pilot)
    rows = pilot.python(exchange_arms(pilot.data()))
    ok, comparison, lines = pilot.judge(rows)
    hints = results.exchanged(pilot.reference, comparison, rows)
    unlisted = [line for line in lines if "a difference with no class" in line]
    print(f"low and high dose exchanged: check passes: {ok}; {comparison.reproduced} of "
          f"{comparison.total} reproduced; {len(comparison.differing)} other values, of which "
          f"{hints[TREATMENT]} are our value of the other arm")
    if ok:
        problems.append("exchanged arms pass the check")
    if hints[TREATMENT] < 0.9 * len(comparison.differing) or len(comparison.differing) < 1000:
        problems.append(f"the differences are not attributed to the treatment grouping: {hints}")
    if not unlisted:
        problems.append("no difference without a class is reported")
    # The 22 exchanged values of E3 are what the reference has: with our arms
    # exchanged too, they agree, and the check says that their entries are stale.
    reproduced_now = [entry["result"] for entry in pilot.entries
                      if entry["proof"]["kind"] == "value_of_other_result"
                      and entry["result"] not in comparison.open]
    print(f"entries with the proof value_of_other_result that are reproduced now: "
          f"{len(reproduced_now)} of 22")
    if len(reproduced_now) != 22:
        problems.append(f"{len(reproduced_now)} of the 22 exchanged results agree, expected 22")
    return problems


def d2_set(pilot: Pilot, tmp_path) -> list[str]:
    problems = control(pilot)
    rows = pilot.python(other_flag(pilot.data()))
    ok, comparison, lines = pilot.judge(rows)
    analyses = Counter(key[4:].split("/")[0] for key in comparison.open)
    print(f"safety set read from EFFFL: check passes: {ok}; {comparison.reproduced} of "
          f"{comparison.total} reproduced; differences in {len(analyses)} analyses")
    if ok or comparison.reproduced > 3000:
        problems.append("another population flag passes the check, or changes little")
    using = {a["id"] for a in pilot.reference.analyses.values()
             if a.get("analysisSetId") == SAFETY}
    if not set(analyses) <= using or len(analyses) < 20:
        problems.append(f"the differences are not in the analyses of the set: {sorted(analyses)}")
    # What these data cannot show: the intent-to-treat set in place of the safety set.
    data = pilot.data()
    for analysis in data["analyses"]:
        if analysis.get("analysisSetId") == SAFETY:
            analysis["analysisSetId"] = ITT
    same = changed(pilot, pilot.python(data))
    print(f"intent-to-treat set in place of the safety set: {len(same)} results change (both "
          "sets hold the same subjects in the pilot: not separable on these data)")
    if same:
        problems.append("the two sets differ on the pilot after all: use this case for D2")
    return problems


def d3_quantile(pilot: Pilot, tmp_path) -> list[str]:
    problems = control(pilot)
    rows = pilot.python(binding=r_definition(pilot))
    ok, comparison, lines = pilot.judge(rows)
    unlisted = sorted(key for key in comparison.open
                      if key not in {entry["result"] for entry in pilot.entries})
    operations = Counter(key.split("/")[1].rsplit("_", 1)[-1] for key in unlisted)
    fewer = 3711 - comparison.reproduced
    print(f"quantile definition r7: check passes: {ok}; {comparison.reproduced} of "
          f"{comparison.total} reproduced as printed, {fewer} fewer (E4: 49); at the precision "
          f"of the result pattern {len(unlisted)} new differences: {dict(operations)}")
    if ok:
        problems.append("another quantile definition passes the check")
    if fewer != 49:
        problems.append(f"{fewer} results fewer are reproduced as printed, E4 says 49")
    if len(unlisted) != 97:
        problems.append(f"{len(unlisted)} new differences at the precision of the pattern, "
                        "expected 97")
    if set(operations) - {"Q1", "Q3"}:
        problems.append(f"differences outside the quartiles: {dict(operations)}")
    if any(rows[key]["method_id"] != "summary.continuous" for key in unlisted):
        problems.append("a difference is not a result of summary.continuous")
    # The options hash says which rows were computed otherwise.
    stamped = {key for key in rows
               if rows[key]["method_options_hash"] != pilot.gold[key]["method_options_hash"]}
    if not set(unlisted) <= stamped or any(
            rows[key]["method_id"] != "summary.continuous" for key in stamped):
        problems.append("the options hash does not mark the rows of the changed method")
    return problems


def d4_subset(pilot: Pilot, tmp_path) -> list[str]:
    problems = control(pilot)
    rows = pilot.python(without_subset(pilot.data(), OVERVIEW))
    ok, comparison, lines = pilot.judge(rows)
    unlisted = sorted(key for key in comparison.open
                      if key not in {entry["result"] for entry in pilot.entries})
    print(f"{OVERVIEW} without its data subset: check passes: {ok}; new differences "
          f"{len(unlisted)}")
    if ok or not unlisted:
        problems.append("a dropped data subset passes the check")
    if any(not key.startswith(f"ard:{OVERVIEW}/") for key in unlisted):
        problems.append("differences outside the analysis that lost its subset")
    # The same for every analysis that names a data subset. A defect the
    # reference cannot show is named as such; one it could show must be caught.
    with_subset = [a["id"] for a in pilot.reference.analyses.values() if a.get("dataSubsetId")]
    outcome: dict[str, list[str]] = {"caught": [], "changes no result": [],
                                     "changes only results the reference does not list": []}
    for analysis_id in with_subset:
        rows = pilot.python(without_subset(pilot.data(), analysis_id))
        passes, comparison, _ = pilot.judge(rows)
        moved = changed(pilot, rows)
        if not passes:
            outcome["caught"].append(analysis_id)
        elif not moved:
            outcome["changes no result"].append(analysis_id)
        elif not any(key in comparison.reference for key in moved):
            outcome["changes only results the reference does not list"].append(analysis_id)
        else:
            problems.append(f"{analysis_id} without its data subset changes results the "
                            "reference lists, and passes the check")
    print(f"each of the {len(with_subset)} analyses with a data subset, one at a time:")
    for name, found in outcome.items():
        print(f"  {name}: {len(found)}{' (' + ', '.join(found) + ')' if name != 'caught' else ''}")
    if len(outcome["caught"]) < 15:
        problems.append(f"only {len(outcome['caught'])} of {len(with_subset)} are caught")
    return problems


def d5_engines(pilot: Pilot, tmp_path) -> list[str]:
    """Rule R11: a defect in one engine's input alone must show as a disagreement."""
    lines, disagreements = results.agreement(pilot.gold, pilot.r(tmp_path / "control"))
    print(f"unchanged: {lines[0]}")
    problems = [f"the engines disagree on the unchanged inputs: {disagreements[:3]}"] \
        if disagreements else []
    planted = {
        "low and high dose exchanged": {"data": exchange_arms(pilot.data())},
        "safety set read from EFFFL": {"data": other_flag(pilot.data())},
        "quantile definition r7": {"binding": r_definition(pilot)},
        f"{OVERVIEW} without its data subset": {"data": without_subset(pilot.data(), OVERVIEW)},
    }
    for number, (name, change) in enumerate(planted.items(), start=1):
        rows = pilot.r(tmp_path / f"planted{number}", **change)
        lines, disagreements = results.agreement(pilot.gold, rows)
        print(f"R engine alone, {name}: {len(disagreements)} results disagree")
        if not disagreements:
            problems.append(f"{name}, in the R engine alone: the engines are said to agree")
    return problems


CASES = {"D1-arms": d1_arms, "D2-set": d2_set, "D3-quantile": d3_quantile,
         "D4-subset": d4_subset, "D5-engines": d5_engines}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_defects(case, pilot, tmp_path):
    print(f"\n--- {case}")
    problems = CASES[case](pilot, tmp_path)
    assert not problems, "\n".join(problems)
