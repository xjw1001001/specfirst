"""Planted defects on the pilot: the result checks must catch each one (rule R5).

PLAN.md section 13.3 (gate of real-2) names four. Each is planted as the
real case (lessons 9 and 16): in the ARS example or the binding the kit
pins, run by the real engines on the ADaM datasets the kit builds, and
judged by the functions the gate itself calls (`build.judge` for P2 with
the kit's exceptions, `results.agreement` for rule R11).

    D1-arms      the low dose and the high dose group exchange their conditions
                 (E3); and the values of the two arms are exchanged in one
                 analysis only, the case of E3 as it happened
    D2-set       the analysis set reads another population flag
    D3-quantile  the quantile definition is R's default, not SAS's (E4)
    D4-subset    an analysis loses its data subset
    D5-engines   each of the four planted in the R engine's input alone: the
                 two engines must be seen to disagree
    D6-proofs    proofs that prove nothing, planted in the kit's exceptions:
                 each passed the check of real-2 and must fail (review of
                 real-2, finding F2)
    D7-display   the grid of the adverse event summary against the formatted
                 values of the example: defects planted in the layout, in
                 the results and in the grid file (real-3a)
    D8-trace     the trace of its cells: the shows edges against the grid
                 builder, the reads edges against the engine, and gaps
                 planted in the graph files (real-3a)
    D9-efficacy  Tables 14-3.01, 14-3.03 and 14-3.05 against the CSR (real-5a)
    D10-trace-model  the reads edges of the model-based analyses (real-5a)
    D11-efficacy-5b  Tables 14-3.11 and 14-3.13 against the CSR: the mixed
                 model, the CMH test, the categories, the proofs and the
                 decision records (real-5b)
    D12-cmh-engines  the CMH test planted in the R engine's input alone: the
                 two engines must be seen to disagree (rule R11, real-5b)
    D13-review   the review page and the acceptance of issue #31: a cell
                 without a panel, a script, a handler, a link that leaves the
                 page, a judged edge drawn as proven, an unseparated decision
                 drawn as proven, a decision or a catalog entry left off the
                 sheet of the page, the record of an upstream column left off
                 the panels, no SDTM column named in the panels, a broken path
                 to SDTM in the graph files, an entry of `formats` that is no
                 difference, and one under a misspelt result set (ADR-022)

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
import html
import json
import os
import re
import shutil
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from specfirst import kit as kits
from specfirst.machine import ard, ars, build, graph, grid, methods, registry, rengine, results
from specfirst.machine import layout as layouts
from specfirst.paths import cache_dir, repo_root

pytestmark = pytest.mark.evidence

KIT = "cdiscpilot01"
TREATMENT, LOW, HIGH = "AnlsGrouping_01_Trt", "AnlsGrouping_01_Trt_2", "AnlsGrouping_01_Trt_3"
SAFETY, ITT = "AnalysisSet_02_SAF", "AnalysisSet_01_ITT"
OVERVIEW = "An07_01_TEAE_Summ_ByTrt"
# D1, the exchange in one analysis: counts, a continuous summary, events, vital signs,
# and the analysis in which the reference itself has the two arms exchanged.
ETHNICITY = "An03_04_Ethnic_Summ_ByTrt"
ONE_ANALYSIS = ("An03_03_Sex_Summ_ByTrt", "An03_01_Age_Summ_ByTrt", "An07_03_SerTEAE_Summ_ByTrt",
                "An08_01_Obs_Summ_ByTrt", ETHNICITY)
# D6: results of the kit's exceptions file, by what their entry proves.
_SUMMARY = "Mth02_ContVar_Summ_ByGrp"
ETHNIC_N_LOW = (f"ard:{ETHNICITY}/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_2/"
                "AnlsGrouping_05_Ethnic_1")
AGE_Q1_HIGH = f"ard:An03_01_Age_Summ_ByTrt/{_SUMMARY}_5_Q1/AnlsGrouping_01_Trt_3"
HEIGHT_MEAN_HIGH = f"ard:An03_06_Height_Summ_ByTrt/{_SUMMARY}_2_Mean/AnlsGrouping_01_Trt_3"
HEIGHT_MEDIAN_LOW = f"ard:An03_06_Height_Summ_ByTrt/{_SUMMARY}_4_Median/AnlsGrouping_01_Trt_2"
NO_P_VALUE = ("ard:An07_10_SocPt_Comp_ByTrt_PlacLow/Mth03_CatVar_Comp_FishEx_1_pval/*/"
              "=VASCULAR%20DISORDERS/=WOUND%20HAEMORRHAGE")


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
    evidence: results.Evidence | None = None  # what a proof may ask for; made once

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

    def judge(self, rows: results.Rows,
              entries: list[dict] | None = None) -> tuple[bool, results.Comparison, list[str]]:
        """P2 for results, as the gate judges it: against the pinned example and its exceptions."""
        lines: list[str] = []
        if self.evidence is None:
            self.evidence = build.proof_evidence(self.root, self.folder, self.spec)
        ok, comparison = build.judge(
            "planted", self.reference, self.registry, rows,
            self.entries if entries is None else entries, self.evidence, lines.append)
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


def exchanged_in(rows: results.Rows, analysis_id: str) -> results.Rows:
    """The rows with the values of the low and the high dose arm exchanged in one analysis."""
    found = {key: dict(row) for key, row in rows.items()}
    for key, row in rows.items():
        parts = key.split("/")
        if row["analysis_id"] == analysis_id and LOW in parts:
            other = "/".join(HIGH if part == LOW else part for part in parts)
            assert other in rows, f"{key} has no result in the high dose arm"
            found[key]["raw_value"], found[other]["raw_value"] = (
                rows[other]["raw_value"], row["raw_value"])
    return found


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
    # The case of E3 as it happened: the two arms exchanged in one analysis only
    # (review of real-2, finding F11). In the analysis of ethnicity the exchange is
    # the reference's own error, so there the entries of the kit become stale.
    for analysis_id in ONE_ANALYSIS:
        rows = exchanged_in(pilot.gold, analysis_id)
        moved = changed(pilot, rows)
        ok, comparison, lines = pilot.judge(rows)
        unexplained = [line for line in lines if line.startswith("  unexplained:")]
        stale = sum("listed as an exception, but it is reproduced" in line for line in unexplained)
        _, disagreements = results.agreement(pilot.gold, rows)
        print(f"low and high dose exchanged in {analysis_id} only: {len(moved)} values change; "
              f"check passes: {ok}; unexplained {len(unexplained)}, of which stale entries "
              f"{stale}; against the other engine {len(disagreements)} disagree")
        if not moved:
            problems.append(f"{analysis_id}: exchanging the arms changes nothing; use another")
        if ok or not unexplained:
            problems.append(f"{analysis_id}: arms exchanged in this analysis alone pass the check")
        if len(disagreements) != len(moved):
            problems.append(f"{analysis_id}: {len(moved)} values change, the engines are said "
                            f"to disagree on {len(disagreements)}")
        if analysis_id == ETHNICITY and stale != 8:
            problems.append(f"{analysis_id}: {stale} stale entries; the kit has 8 entries for "
                            "the values the reference has exchanged there")
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


def d6_proofs(pilot: Pilot, tmp_path) -> list[str]:
    """Proofs that prove nothing, planted in the kit's own exceptions (review of real-2, F2).

    The reviewer's cases A3 and A8 to A11, each on the entry it was found
    on, and the proof the median of height had until real-3a. Every one
    passed the check of real-2. Each must fail now, for the reason given.
    """
    problems = control(pilot)
    option = {"method": "summary.continuous", "option": "quantile_definition"}
    race = "ard:An03_05_Race_Summ_ByTrt/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_1/"
    zero_of_race = sorted(key for key, row in pilot.gold.items()
                          if key.startswith(race) and row["raw_value"] == 0)
    if not zero_of_race:
        return [*problems, "no count of 0 among the race counts of the placebo arm: A11 "
                           "cannot be planted"]
    placebo = ETHNIC_N_LOW.replace(LOW, "AnlsGrouping_01_Trt_1")
    planted = {
        "A3 an exchanged count, proven by the placebo arm, which has the same value": (
            ETHNIC_N_LOW, {"kind": "value_of_other_result", "result": placebo},
            "the two are not exchanged"),
        "A8 the quartile of age, by an option with one value": (
            AGE_Q1_HIGH, {"kind": "no_alternative", "method": "summary.continuous",
                          "option": "sd_denominator"},
            "no value of sd_denominator changes a result of the operation"),
        "A9 an exchanged mean, as the same under every quantile definition": (
            HEIGHT_MEAN_HIGH, {"kind": "same_under_every", **option},
            "no value of quantile_definition changes a result of the operation"),
        "A10 the same mean, as given by no quantile definition": (
            HEIGHT_MEAN_HIGH, {"kind": "no_alternative", **option},
            "no value of quantile_definition changes a result of the operation"),
        "A11 no records, by a count of 0 of another analysis": (
            NO_P_VALUE, {"kind": "no_records", "zero": zero_of_race[:1]},
            "is not a count of the cell's own groups"),
        "no records, by the count of one of the two compared arms": (
            NO_P_VALUE, {"kind": "no_records", "zero": [
                "ard:An07_10_SocPt_Summ_ByTrt/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_1/"
                "=VASCULAR%20DISORDERS/=WOUND%20HAEMORRHAGE"]},
            "one count per compared group is needed"),
        "the median of height, as the same under every quantile definition": (
            HEIGHT_MEDIAN_LOW, {"kind": "same_under_every", **option},
            "no value of quantile_definition changes a result of the operation"),
    }
    by_result = {entry["result"]: entry for entry in pilot.entries}
    if pilot.gold[placebo]["raw_value"] != 3 or by_result[ETHNIC_N_LOW]["embedded"] != "3":
        problems.append("A3 needs a placebo count equal to the embedded count of the low dose arm")
    for name, (key, proof, message) in planted.items():
        entries = [dict(entry, proof=proof) if entry["result"] == key else entry
                   for entry in pilot.entries]
        ok, _, lines = pilot.judge(pilot.gold, entries)
        unexplained = [line for line in lines if line.startswith("  unexplained:")]
        print(f"{name}: check passes: {ok}"
              + (f"; {unexplained[0].split(': ', 2)[-1]}" if unexplained else ""))
        if ok or len(unexplained) != 1 or key not in unexplained[0]:
            problems.append(f"{name}: the proof passes, or more than this entry fails")
        elif message not in unexplained[0]:
            problems.append(f"{name}: fails for another reason: {unexplained[0]}")
    return problems


# ---- real-3a: the grid and the trace of its cells (ADR-005) ---------------------------


# The output D7 and D8 plant in: the adverse event summary of real-3a. Issue #31 builds the
# demographics before it and the table by organ class and term after it.
SUMMARY_OUTPUT = "Out14-3-1-1"


def _display(pilot: Pilot):
    """The adverse event summary: its layout, its built grid, the classes of its results."""
    shown = next(display for display in pilot.spec.displays if display.output == SUMMARY_OUTPUT)
    spec = layouts.read(pilot.folder / shown.layout)
    with open(pilot.folder / build.GRID / f"{shown.output}.json", encoding="ascii") as handle:
        made = json.load(handle)
    comparison = results.compare_reference(pilot.reference, pilot.gold)
    if pilot.evidence is None:
        pilot.evidence = build.proof_evidence(pilot.root, pilot.folder, pilot.spec)
    explained, _ = results.judge_entries(comparison, pilot.entries, pilot.gold, pilot.registry,
                                         pilot.evidence)
    return shown, spec, made, {key: entry["class"] for key, entry in explained.items()}


def d7_display(pilot: Pilot, tmp_path) -> list[str]:
    """P2 for grid text: what the comparison with the formatted values must see.

    Planted in the layout (another pattern, a row or the header left out,
    rows in another order), in the results (the arms exchanged in one
    analysis, a percent of another denominator) and in the grid file (a
    text, an ARD row). Each must fail. What the example cannot show is
    printed, not counted as caught: it formats results, not cells, so the
    order of the parts of a cell is the layout's alone; and no result of
    this output lies on a half, so the rounding rule cannot be told apart.
    """
    shown, spec, made, classes = _display(pilot)
    event, rows = pilot.reference, pilot.gold
    found = grid.compare_reference(event, spec, made, rows, classes)
    print(found.lines()[0])
    problems = [f"the unchanged grid does not pass: {p}" for p in found.problems[:3]]
    if made != grid.build(event, spec, rows):
        problems.append("the grid of the build is not what the layout and the ARD give")
    if (found.cells, found.results, found.equal) != (27, 51, 27) or found.no_reference:
        problems.append(f"expected 27 cells that show 51 results, all equal: {found.lines()[0]}")
    with open(pilot.folder / shown.layout, encoding="ascii") as handle:
        given = yaml.safe_load(handle)

    def with_layout(change) -> grid.DisplayComparison:
        data = copy.deepcopy(given)
        change(data)
        other = layouts.parse(data)
        return grid.compare_reference(event, other, grid.build(event, other, rows), rows,
                                      classes)

    def exchanged_rows(data: dict) -> None:
        listed = data["rows"][1]["analyses"]
        listed[0], listed[1] = listed[1], listed[0]

    body = given["rows"][1]["parts"]
    in_layout = {
        "the percent under the pattern (XX.X), without the blank":
            lambda d: d["rows"][1]["parts"]["pct"].update(pattern="(XX.X)"),
        "the percent with two decimals":
            lambda d: d["rows"][1]["parts"]["pct"].update(pattern="( XX.XX)"),
        "the count with one decimal":
            lambda d: d["rows"][1]["parts"]["n"].update(pattern="XX.X"),
        "the header count without its brackets":
            lambda d: d["rows"][0]["parts"]["N"].update(pattern="N=XX"),
        "the percent in place of the count":
            lambda d: d["rows"][1]["parts"]["n"].update(operation=body["pct"]["operation"],
                                                        pattern="XXX"),
        "the last row left out": lambda d: d["rows"][1]["analyses"].pop(),
        "the header left out": lambda d: d["rows"].pop(0),
        "the first two rows in the other order": exchanged_rows,
    }
    for name, change in in_layout.items():
        other = with_layout(change)
        print(f"layout, {name}: {len(other.differing)} cells differ, {len(other.problems)} "
              "problems")
        if not other.problems:
            problems.append(f"layout, {name}: passes")

    def with_rows(changed: results.Rows) -> grid.DisplayComparison:
        comparison = results.compare_reference(event, changed)
        explained, _ = results.judge_entries(comparison, pilot.entries, changed, pilot.registry,
                                             pilot.evidence)
        return grid.compare_reference(
            event, spec, grid.build(event, spec, changed), changed,
            {key: entry["class"] for key, entry in explained.items()})

    of_others = {key: dict(row) for key, row in rows.items()}
    for key, row in rows.items():  # the percent of every arm with the placebo arm below it
        if row["analysis_id"] == OVERVIEW and row["operation_id"].endswith("_pct"):
            count = rows[key.replace("_2_pct", "_1_n")]["raw_value"]
            of_others[key]["raw_value"] = 100.0 * count / 86
    in_rows = {
        f"low and high dose exchanged in {OVERVIEW}": exchanged_in(rows, OVERVIEW),
        "every percent of the first row with the placebo arm as its denominator": of_others,
    }
    for name, changed_rows in in_rows.items():
        other = with_rows(changed_rows)
        print(f"results, {name}: {len(other.differing)} cells differ, {len(other.problems)} "
              "problems")
        if not other.problems or not other.differing:
            problems.append(f"results, {name}: passes")

    def with_grid(change) -> list[str]:
        """What the check of a build says of a grid file: its form, then its content."""
        value = copy.deepcopy(made)
        change(value)
        return grid.grid_problems(value, pilot.root) or grid.compare_reference(
            event, spec, value, rows, classes).problems

    def exchanged_texts(value: dict) -> None:
        cells = value["rows"][1]["cells"]
        cells[0]["text"], cells[2]["text"] = cells[2]["text"], cells[0]["text"]

    in_grid = {
        "a text changed": lambda g: g["rows"][1]["cells"][0].update(text="66 ( 76.7)"),
        "the texts of two cells of a row exchanged": exchanged_texts,
        "the cells of a row in another order": lambda g: g["rows"][1]["cells"].reverse(),
        "the ARD rows of a cell taken from the next row":
            lambda g: g["rows"][1]["cells"][0].update(ard=g["rows"][2]["cells"][0]["ard"]),
    }
    for name, change in in_grid.items():
        said = with_grid(change)
        print(f"grid file, {name}: {len(said)} problems"
              + (f", for example: {said[0][:110]}" if said else ""))
        if not said:
            problems.append(f"grid file, {name}: passes")
    # What these 51 results cannot show.
    for name, change in {"the percent before the count": lambda d: d["rows"][1].update(
            cell="{pct} {n}")}.items():
        other = with_layout(change)
        print(f"not separable by this reference: {name}: {len(other.problems)} problems (it "
              "formats results, not cells)")
        if other.problems:
            problems.append(f"{name} is seen after all: count it among the planted defects")
    planned = grid.plan(event, spec, rows)
    on_a_half = [item.ard for row in planned.rows for cell in row.cells for item in cell.shown
                 if _on_a_half(rows[item.ard]["raw_value"], item.pattern)]
    print(f"not separable on these data: the rounding rule; results of the output that lie on "
          f"a half at their displayed decimals: {len(on_a_half)} of {found.results}")
    if on_a_half:
        problems.append("a result lies on a half: plant another rounding rule for it")
    return problems


def _on_a_half(value: float | int | None, pattern: str) -> bool:
    """Whether a value is exactly halfway between two texts of its pattern."""
    from decimal import Decimal

    if value is None:
        return False
    decimals = len(methods.pattern_mask(pattern)[1].partition(".")[2])
    scaled = Decimal(repr(value)) * (Decimal(10) ** decimals)
    return scaled % 1 == Decimal("0.5")


def _graph_of(pilot: Pilot) -> tuple[list[dict], list[dict]]:
    folder = pilot.folder / build.GRAPH
    with open(folder / "nodes.jsonl", encoding="ascii") as nodes, \
            open(folder / "edges.jsonl", encoding="ascii") as edges:
        return [json.loads(line) for line in nodes], [json.loads(line) for line in edges]


def shows_problems(pilot: Pilot, edges: list[dict]) -> list[str]:
    """The `shows` edges against the grid builder (lesson 16).

    A result that a cell shows is changed: exactly the cells of this grid with
    a `shows` edge to it must get another text. Then every result that no cell
    of it shows is changed at once: the grid must stay as it is. A result may
    stand in other grids too (the count of a header, issue #31); their cells
    are not this grid's.
    """
    shown, spec, made, _ = _display(pilot)
    event, rows = pilot.reference, pilot.gold
    cells_of: dict[str, set[str]] = {}
    for edge in edges:
        if edge["type"] == "shows" and edge["from"].startswith(f"cell:{shown.output}/"):
            cells_of.setdefault(edge["to"], set()).add(edge["from"])
    texts = {cell["id"]: cell["text"] for row in made["rows"] for cell in row["cells"]}
    problems = []
    planned = grid.plan(event, spec, rows)
    used = sorted({item.ard for row in planned.rows for cell in row.cells for item in cell.shown})
    for key in used:
        changed = dict(rows)
        changed[key] = dict(rows[key], raw_value=rows[key]["raw_value"] + 1)
        other = grid.build(event, spec, changed)
        moved = {cell["id"] for row in other["rows"] for cell in row["cells"]
                 if cell["text"] != texts[cell["id"]]}
        if moved != cells_of.get(key, set()):
            problems.append(f"{key}: changing it changes the cells {sorted(moved)}; its shows "
                            f"edges come from {sorted(cells_of.get(key, set()))}")
    others = {key: (row if key in cells_of else dict(
        row, raw_value=None if row["raw_value"] is None else row["raw_value"] + 1))
        for key, row in rows.items()}
    if grid.build(event, spec, others) != made:
        problems.append("with every result that no cell shows changed, the grid is another one")
    print(f"shows: {len(used)} results changed one at a time, {len(rows) - len(cells_of)} "
          f"results without a shows edge changed at once; {len(problems)} problems")
    return problems


def reads_problems(pilot: Pilot, edges: list[dict]) -> list[str]:
    """The `reads` edges against the engine (lesson 16).

    For every analysis behind the grid, the engine runs it, and the analyses
    its results are computed from, on changed data. First every column the
    engine is handed and these analyses have no `reads` edge to is emptied,
    then rolled by one row: the results of the analysis must stay the same.
    Then every column they do read is emptied: a result must change, or the
    change would prove nothing. (A roll alone would not do for that: a count
    by arm is the same when the arms are rolled over the subjects.)
    """
    import numpy as np

    event = pilot.reference
    tables = ard.load_tables(pilot.folder / build.ADAM,
                             ars.columns(event, pilot.spec.subject_key))
    reads: dict[str, set[str]] = {}
    from_results: dict[str, set[str]] = {}
    for edge in edges:
        if edge["type"] == "reads":
            reads.setdefault(edge["from"], set()).add(edge["to"])
        elif edge["type"] == "computes" and edge["from"] in pilot.gold:
            # The ARD rows of the example; those of the kit's other result sets (the
            # efficacy tables of real-5a) are held against the R engine by D10.
            own = graph.ars_id(pilot.gold[edge["from"]]["analysis_id"])
            from_results.setdefault(own, set()).add(edge["to"])

    def empty(values):
        if values.dtype == object:
            made = np.empty(len(values), dtype=object)
            made[:] = ""
            return made
        return np.full(len(values), np.nan)

    problems = []
    changed_columns = 0
    for analysis in sorted(from_results):
        needed = from_results[analysis] | {analysis}
        columns = set().union(*(reads.get(name, set()) for name in needed))
        data = pilot.data()
        data["analyses"] = [a for a in data["analyses"] if graph.ars_id(a["id"]) in needed]
        only = ars.index(data)
        bound = ars.bind(only, pilot.registry, pilot.spec.binding)
        gold = {key: row for key, row in pilot.gold.items()
                if graph.ars_id(row["analysis_id"]) == analysis}

        def moved(change, read: bool, only=only, bound=bound, columns=columns,
                  gold=gold) -> tuple[list[str], int]:
            """The results of the analysis that change, and how many columns were changed."""
            other, count = {}, 0
            for name, table in tables.items():
                values = dict(table.columns)
                for column in table.columns:
                    if (graph.adam_id(name, column) in columns) == read:
                        values[column] = change(table.columns[column])
                        count += 1
                other[name] = ard.Table(name, table.rows, values, table.kinds)
            try:
                found = results.by_id(ard.run(only, pilot.registry, bound, other,
                                              pilot.spec.subject_key))
            except ard.EngineError:
                return sorted(gold), count
            return [key for key, row in gold.items() if key not in found or not results.same(
                found[key]["raw_value"], row["raw_value"])], count

        for name, change in (("emptied", empty), ("rolled", lambda v: np.roll(v, 1))):
            differing, count = moved(change, read=False)
            changed_columns += count
            if differing:
                problems.append(f"{analysis}: with the {count} columns it has no reads edge to "
                                f"{name}, {len(differing)} of its {len(gold)} results change, "
                                f"for example {differing[0]}")
        differing, count = moved(empty, read=True)
        if not differing:
            problems.append(f"{analysis}: emptying the {count} columns it reads changes none of "
                            "its results: the change proves nothing")
    print(f"reads: {len(from_results)} analyses; for each, the columns without a reads edge "
          f"emptied and rolled ({changed_columns} changes of a column in all), then the columns "
          f"it reads emptied; {len(problems)} problems")
    return problems


def d8_trace(pilot: Pilot, tmp_path) -> list[str]:
    """P3 for the cells of the grid: complete paths, held against the builder and the engine."""
    shown, _, made, _ = _display(pilot)
    nodes, edges = _graph_of(pilot)
    # coverage.json holds every grid of the build (the efficacy tables of real-5a too).
    grids = {display.output: json.loads((pilot.folder / build.GRID / f"{display.output}.json")
                                        .read_text(encoding="utf-8"))
             for spec in kits.load_kit(pilot.root, KIT).results for display in spec.displays}
    assert grids[shown.output] == made
    lines, problems = graph.check_cells(pilot.folder / build.GRAPH, grids)
    for line in lines:
        print(line)
    problems = [f"the unchanged graph does not pass: {p}" for p in problems[:3]]
    problems += shows_problems(pilot, edges)
    problems += reads_problems(pilot, edges)
    # Planted: an edge the builder or the ARS reading would have missed. The files
    # still agree with each other; only the engine and the builder can tell.
    subset = ("ars:" + OVERVIEW, "adam:ADAE.TRTEMFL")
    without_read = [e for e in edges if (e["from"], e["to"]) != subset]
    cell = f"cell:{shown.output}/r2/c1"
    without_show = [e for e in edges if not (e["type"] == "shows" and e["from"] == cell)]
    planted = {
        f"the reads edge from {OVERVIEW} to ADAE.TRTEMFL left out":
            (lambda: reads_problems(pilot, without_read), len(edges) - len(without_read)),
        f"the shows edges of {cell} left out":
            (lambda: shows_problems(pilot, without_show), len(edges) - len(without_show)),
    }
    for name, (check, removed) in planted.items():
        found = check()
        print(f"planted, {name} ({removed} edges): {len(found)} problems"
              + (f", for example: {found[0][:150]}" if found else ""))
        if not found or not removed:
            problems.append(f"{name}: not seen")
    # Planted in the files: gaps the static check itself must see, on the real graph.
    copied = tmp_path / "graph"
    for name, keep in {
        "a result node left out": lambda r: r.get("id") != made["rows"][1]["cells"][0]["ard"][0],
        "every computes edge left out": lambda r: r.get("type") != "computes",
        "every reads edge left out": lambda r: r.get("type") != "reads",
    }.items():
        shutil.copytree(pilot.folder / build.GRAPH, copied, dirs_exist_ok=True)
        for file in ("nodes.jsonl", "edges.jsonl"):
            records = [r for r in (nodes if file == "nodes.jsonl" else edges) if keep(r)]
            (copied / file).write_text("".join(json.dumps(r) + "\n" for r in records), "ascii")
        _, found = graph.check_cells(copied, grids)
        found = [problem for problem in found if shown.output in problem]
        print(f"planted in the files, {name}: {len(found)} problems of {shown.output}")
        if not found:
            problems.append(f"{name}: the check of the files passes")
    return problems


# ---- real-5a: the efficacy tables against the CSR (ADR-012, ADR-015) --------------------

EFFICACY = "efficacy-adas"
W24 = "An_ADAS_W24"
MODEL_SUFFIXES = ("Dose", "PwPbo", "PwLow")
_EFFICACY: dict[int, Efficacy] = {}


@dataclass
class Efficacy:
    spec: kits.ResultSet
    event: ars.Event
    layouts: dict[str, layouts.Layout]  # output -> layout
    tables: dict[str, dict]  # output -> its CSR table, parsed from the page of the build's CSR
    entries: dict[str, list[dict]]  # output -> the kit's exceptions for its cells
    decisions: dict[str, dict]  # the kit's decision records by ID
    gold: results.Rows  # the gold ARD of the build


def efficacy(pilot: Pilot) -> Efficacy:
    if id(pilot) not in _EFFICACY:
        from specfirst.machine import csr

        kit = kits.load_kit(pilot.root, KIT)
        spec = next(s for s in kit.results if s.id == EFFICACY)
        inputs = build.result_inputs(pilot.root, pilot.folder, spec)
        found = {display.output: (layouts.read(pilot.folder / display.layout),
                                  csr.read_table(pilot.folder / display.reference.file,
                                                 display.reference.page,
                                                 display.reference.table))
                 for display in spec.displays}
        _EFFICACY[id(pilot)] = Efficacy(
            spec, inputs.event, {key: value[0] for key, value in found.items()},
            {key: value[1] for key, value in found.items()},
            csr.load_exceptions(pilot.folder / kit.exceptions),
            {record["id"]: record for name in kit.decisions
             for record in results_jsonl(pilot.folder / name)},
            results.by_id(results_jsonl(pilot.folder / build.ARD / f"{EFFICACY}.jsonl")))
    return _EFFICACY[id(pilot)]


def results_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def efficacy_rows(pilot: Pilot, eff: Efficacy, data: dict, work: Path) -> results.Rows:
    """Both engines on a changed reporting event, merged as the build merges them."""
    event = ars.index(data)
    assert event.problems == []
    bound = ars.bind(event, pilot.registry, eff.spec.binding)
    tables = ard.load_tables(pilot.folder / build.ADAM, ars.columns(event, eff.spec.subject_key))
    python = ard.run(event, pilot.registry, bound, tables, eff.spec.subject_key)
    work.mkdir(parents=True, exist_ok=True)
    path = work / "event.json"
    path.write_text(json.dumps(data), encoding="ascii")
    other, meta, _ = rengine.run(pilot.root, work, path, registry.json_path(pilot.root), bound,
                                 tables, eff.spec.subject_key)
    assert rengine.data_problems(meta, tables) == []
    return results.by_id(build.gold_rows(python, other, pilot.registry))


def efficacy_problems(eff: Efficacy, rows: results.Rows, event: ars.Event | None = None,
                      tables: dict | None = None, entries: dict | None = None) -> list[str]:
    """The check of the gate on every output: each grid against its CSR table."""
    problems = []
    for output, layout in sorted(eff.layouts.items()):
        try:
            made = grid.build(event or eff.event, layout, rows)
        except grid.GridError as error:
            problems.append(f"{output}: the grid cannot be built: {error}")
            continue
        compared = build.csr_against(made, (tables or eff.tables)[output], event or eff.event,
                                     layout, rows, (entries or eff.entries).get(output, []),
                                     eff.decisions)
        problems += [f"{output}: {problem}" for problem in compared.problems]
    return problems


def decision_problems(pilot: Pilot, records: list[dict],
                      pairs: list[tuple[ars.Event, kits.ResultSet]]) -> list[str]:
    """The gate's check `decisions` on events, each with its result set and the built
    ADaM data, which the last visit of the mixed model is held on (review of real-5b, G2)."""
    from specfirst.machine import decisions

    events, engines = [], []
    for event, spec in pairs:
        bound = ars.bind(event, pilot.registry, spec.binding)
        tables = ard.load_tables(pilot.folder / build.ADAM, ars.columns(event, spec.subject_key))
        events.append((event, bound))
        engines.append(ard.Engine(event, pilot.registry, bound, tables, spec.subject_key))
    return decisions.problems(pilot.root, records, events, pilot.registry, engines)[1]


def _parameters(data: dict, suffixes: tuple[str, ...], change,
                prefix: str = "An_ADAS_W") -> dict:
    """The event with the programmingCode parameters of some analyses changed: by default
    those of the ANCOVA of every week (real-5a), whose IDs start with An_ADAS_W."""
    for analysis in data["analyses"]:
        if analysis["id"].startswith(prefix) and analysis["id"].rsplit("_", 1)[-1] in suffixes:
            code = analysis["programmingCode"]
            code["parameters"] = change([dict(p) for p in code["parameters"]])
    return data


def d9_efficacy(pilot: Pilot, tmp_path) -> list[str]:
    """Defects planted in the efficacy tables: each must fail the check of the gate.

    In the reporting event, run by both engines: a decision the CSR's numbers
    rest on taken another way. In the reference and in the kit's exceptions:
    a changed cell of the CSR, and exceptions that are stale, missing or prove
    nothing. One defect the CSR cannot show is printed, not counted: the
    weights of the LS means change no printed cell (the tables print
    differences of LS means only).
    """
    eff = efficacy(pilot)
    problems = []
    control_problems = efficacy_problems(eff, eff.gold)
    print(f"unchanged: {len(control_problems)} problems")
    if control_problems:
        return ["the unchanged inputs do not pass the check", *control_problems[:5]]

    def data() -> dict:
        return copy.deepcopy(eff.event.data)

    def no_baseline(parameters):
        return [p for p in parameters if p["name"] != "covariates"]

    def by_rank(parameters):
        return [dict(p, value=["group_rank"]) if p["name"] == "dose" else p for p in parameters]

    def site_ids(parameters):
        return [dict(p, value=["SITEID"]) if p["name"] == "factors" else p for p in parameters]

    def asymptotic(parameters):
        return [*parameters, {"name": "df", "value": ["asymptotic"]}]

    def other_reference(parameters):
        return [dict(p, value=["Grp_Low"]) if p["name"] == "reference" else p
                for p in parameters]

    def itt(value: dict) -> dict:
        chosen = value["analysisSets"][0]
        assert chosen["condition"]["variable"] == "EFFFL"
        chosen["condition"]["variable"] = "ITTFL"
        return value

    def week16(value: dict) -> dict:
        subset = next(s for s in value["dataSubsets"] if s["id"] == "DS_ADAS_W24")
        visit = subset["compoundExpression"]["whereClauses"][1]["condition"]
        assert visit["value"] == ["Week 24"]
        visit["value"] = ["Week 16"]
        return value

    in_event = {
        "the ANCOVA without the baseline covariate":
            _parameters(data(), MODEL_SUFFIXES, no_baseline),
        "the dose as the rank of the group": _parameters(data(), ("Dose",), by_rank),
        "the site in place of the pooled site group":
            _parameters(data(), MODEL_SUFFIXES, site_ids),
        "the comparisons with asymptotic degrees of freedom":
            _parameters(data(), ("PwPbo", "PwLow"), asymptotic),
        "the comparison with placebo made against the low dose":
            _parameters(data(), ("PwPbo",), other_reference),
        "the intent-to-treat set in place of the efficacy set": itt(data()),
        "week 16 in place of week 24": week16(data()),
    }
    for number, (name, value) in enumerate(in_event.items()):
        rows = efficacy_rows(pilot, eff, value, tmp_path / f"event-{number}")
        found = efficacy_problems(eff, rows, ars.index(value))
        print(f"planted, {name}: {len(found)} problems"
              + (f", for example: {found[0][:160]}" if found else ""))
        if not found:
            problems.append(f"{name}: not seen")
    # The decision records against the event: the ANCOVA without the baseline is not
    # what custom:eff-model-terms says (gate check `decisions`).
    from specfirst.machine import decisions

    # The efficacy records: the kit's first decisions file (issue #31 adds the second).
    records = decisions.load(pilot.folder / kits.load_kit(pilot.root, KIT).decisions[0])
    cibic = efficacy_5b(pilot)[CIBIC]  # the records of real-5b bind its analyses
    for name, value in (("unchanged", data()),
                        ("the ANCOVA without the baseline covariate",
                         in_event["the ANCOVA without the baseline covariate"])):
        found = decision_problems(pilot, records, [(ars.index(value), eff.spec),
                                                   (ars.index(cibic.event.data), cibic.spec)])
        print(f"decision records, {name}: {len(found)} problems"
              + (f", for example: {found[0][:160]}" if found else ""))
        if (name == "unchanged") == bool(found):
            problems.append(f"decision records, {name}: {len(found)} problems")
    # The weights of the LS means: the LS means change, and no printed cell does.
    value = _parameters(data(), ("LSM",), lambda ps: [
        dict(p, value=["equal"]) if p["name"] == "weights" else p for p in ps])
    rows = efficacy_rows(pilot, eff, value, tmp_path / "weights")
    moved = [key for key, row in eff.gold.items() if "_LSM/" in key and not results.same(
        rows[key]["raw_value"], row["raw_value"])]
    found = efficacy_problems(eff, rows, ars.index(value))
    print(f"what the CSR cannot show: the LS means with equal weights change {len(moved)} "
          f"results of the LS means and {len(found)} cells (the tables print no LS mean)")
    if not moved or found:
        problems.append("the weights of the LS means: expected changed LS means and no "
                        f"changed cell, found {len(moved)} and {len(found)}")
    # In the reference and in the exceptions.
    changed_table = copy.deepcopy(eff.tables)
    line = next(line for line in changed_table["Out14-3-01"]["lines"]
                if line["label"].startswith("p-value(Dose"))
    assert line["cells"][2] == "0.245"
    line["cells"][2] = "0.254"
    as_printed = data()
    for method in as_printed["methods"]:
        for operation in method["operations"]:
            if operation["id"] in ("Mth_AncovaPw_3_lcl", "Mth_AncovaPw_4_ucl"):
                operation["resultPattern"] = "X.X"
    first = eff.entries["Out14-3-01"][0]
    planted = {
        "a cell of the CSR changed (0.245 to 0.254)":
            lambda: efficacy_problems(eff, eff.gold, tables=changed_table),
        "the confidence limits shown with the CSR's 1 decimal (the 9 exceptions are stale)":
            lambda: efficacy_problems(eff, eff.gold, event=ars.index(as_printed)),
        "an exception whose other pattern proves nothing (3 decimals)": lambda: efficacy_problems(
            eff, eff.gold, entries={**eff.entries, "Out14-3-01": [dict(first, proof={
                "kind": "other_pattern", "patterns": {"lower": "X.XXX", "upper": "X.XXX"}}),
                *eff.entries["Out14-3-01"][1:]]}),
        "an exception left out": lambda: efficacy_problems(
            eff, eff.gold, entries={**eff.entries, "Out14-3-01": eff.entries["Out14-3-01"][1:]}),
        "an exception with the class reference_error": lambda: efficacy_problems(
            eff, eff.gold, entries={**eff.entries, "Out14-3-01": [
                dict(first, **{"class": "reference_error"}), *eff.entries["Out14-3-01"][1:]]}),
        "an exception that names no decision record": lambda: efficacy_problems(
            eff, eff.gold, entries={**eff.entries, "Out14-3-01": [
                dict(first, decision="custom:none"), *eff.entries["Out14-3-01"][1:]]}),
    }
    for name, check in planted.items():
        found = check()
        print(f"planted, {name}: {len(found)} problems"
              + (f", for example: {found[0][:160]}" if found else ""))
        if not found:
            problems.append(f"{name}: not seen")
    return problems


def d10_trace_model(pilot: Pilot, tmp_path) -> list[str]:
    """The `reads` edges of the model-based analyses against the R engine (lesson 16).

    D8 for the analyses only the R engine runs. The analyses of the three
    tables that fit a model are run on the columns the event hands over, with
    every column they have no `reads` edge to emptied, then rolled by one
    row: their results must stay the same. With every column they read
    emptied, a result must change. Planted: the edge to ADQSADAS.BASE, the
    covariate of the model (a parameter of the analysis, not a variable, a
    set or a grouping), left out: its roll must be seen.
    """
    import numpy as np

    eff = efficacy(pilot)
    _, edges = _graph_of(pilot)
    names = {f"{W24.replace('W24', week)}_{suffix}" for week in ("W24", "W08", "W16")
             for suffix in MODEL_SUFFIXES}
    data = copy.deepcopy(eff.event.data)
    data["analyses"] = [a for a in data["analyses"] if a["id"] in names]
    only = ars.index(data)
    bound = ars.bind(only, pilot.registry, eff.spec.binding)
    tables = ard.load_tables(pilot.folder / build.ADAM,
                             ars.columns(eff.event, eff.spec.subject_key))
    gold = {key: row for key, row in eff.gold.items() if row["analysis_id"] in names}
    path = tmp_path / "event.json"
    path.write_text(json.dumps(data), encoding="ascii")

    def empty(values):
        if values.dtype == object:
            made = np.empty(len(values), dtype=object)
            made[:] = ""
            return made
        return np.full(len(values), np.nan)

    def moved(columns: set[str], change, read: bool, tag: str) -> tuple[list[str], int]:
        other, count = {}, 0
        for name, table in tables.items():
            values = dict(table.columns)
            for column in table.columns:
                if (graph.adam_id(name, column) in columns) == read:
                    values[column] = change(table.columns[column])
                    count += 1
            other[name] = ard.Table(name, table.rows, values, table.kinds)
        try:
            rows, _, _ = rengine.run(pilot.root, tmp_path / tag, path,
                                     registry.json_path(pilot.root), bound, other,
                                     eff.spec.subject_key)
        except rengine.REngineError:
            return sorted(gold), count
        found = results.by_id(rows)
        return [key for key, row in gold.items() if key not in found or not results.same(
            found[key]["raw_value"], row["raw_value"])], count

    def check(edges_used: list[dict], tag: str) -> list[str]:
        reads: set[str] = set()
        for name in names:
            reads |= {edge["to"] for edge in edges_used
                      if edge["type"] == "reads" and edge["from"] == graph.ars_id(name)}
        found = []
        for label, change in (("emptied", empty), ("rolled", lambda v: np.roll(v, 1))):
            differing, count = moved(reads, change, False, f"{tag}-{label}")
            print(f"  {tag}: the {count} columns without a reads edge {label}: "
                  f"{len(differing)} of {len(gold)} results change")
            if differing:
                found.append(f"with the {count} columns they have no reads edge to {label}, "
                             f"{len(differing)} results change, for example {differing[0]}")
        differing, count = moved(reads, empty, True, f"{tag}-read")
        if not differing:
            found.append(f"emptying the {count} columns they read changes no result")
        return found

    problems = check(edges, "unchanged")
    if not any(edge["type"] == "reads" and edge["to"] == "adam:ADQSADAS.BASE"
               and edge["from"] == graph.ars_id(f"{W24}_Dose") for edge in edges):
        problems.append("no reads edge from the dose-response analysis to ADQSADAS.BASE")
    without = [edge for edge in edges if not (
        edge["type"] == "reads" and edge["to"] == "adam:ADQSADAS.BASE")]
    found = check(without, "planted")
    print(f"planted, the reads edges to ADQSADAS.BASE left out ({len(edges) - len(without)} "
          f"edges): {len(found)} problems" + (f", for example: {found[0][:150]}" if found else ""))
    if not found:
        problems.append("the reads edges to ADQSADAS.BASE left out: not seen")
    return problems


# ---- real-5b: Tables 14-3.11 and 14-3.13 against the CSR (amendment of real-5b) --------

CIBIC = "efficacy-cibic"
MMRM = "An_ADAS_MMRM"
_EFFICACY_5B: dict[int, dict[str, Efficacy]] = {}


def efficacy_5b(pilot: Pilot) -> dict[str, Efficacy]:
    """The two result sets of real-5b, each with the outputs of real-5b only."""
    if id(pilot) not in _EFFICACY_5B:
        from specfirst.machine import csr

        kit = kits.load_kit(pilot.root, KIT)
        made = {}
        for set_id, outputs in ((EFFICACY, ("Out14-3-11",)), (CIBIC, ("Out14-3-13",))):
            spec = next(s for s in kit.results if s.id == set_id)
            inputs = build.result_inputs(pilot.root, pilot.folder, spec)
            displays = [d for d in spec.displays if d.output in outputs]
            made[set_id] = Efficacy(
                spec, inputs.event,
                {d.output: layouts.read(pilot.folder / d.layout) for d in displays},
                {d.output: csr.read_table(pilot.folder / d.reference.file, d.reference.page,
                                          d.reference.table) for d in displays},
                csr.load_exceptions(pilot.folder / kit.exceptions),
                {record["id"]: record for name in kit.decisions
             for record in results_jsonl(pilot.folder / name)},
                results.by_id(results_jsonl(pilot.folder / build.ARD / f"{set_id}.jsonl")))
        _EFFICACY_5B[id(pilot)] = made
    return _EFFICACY_5B[id(pilot)]


def _with_subset(data: dict, subset_id: str, change) -> dict:
    subset = next(s for s in data["dataSubsets"] if s["id"] == subset_id)
    subset["compoundExpression"]["whereClauses"] = change(
        subset["compoundExpression"]["whereClauses"])
    return data


def _seen(name: str, found: list[str], problems: list[str]) -> None:
    print(f"planted, {name}: {len(found)} problems"
          + (f", for example: {found[0][:170]}" if found else ""))
    if not found:
        problems.append(f"{name}: not seen")


def d11_efficacy_5b(pilot: Pilot, tmp_path) -> list[str]:
    """Defects planted in Tables 14-3.11 and 14-3.13: each must fail the check of the gate.

    In the reporting events, run by both engines: a decision the CSR's numbers
    rest on taken another way, among them gold taking the LS means averaged
    over the weeks, as the CSR does, where the SAP says Week 24 (the 12
    exceptions are then stale). In the references and in the exceptions: a
    changed cell of the CSR, and proofs that prove nothing. Against the
    decision records: an event that the records do not describe.
    """
    sets = efficacy_5b(pilot)
    adas, cibic = sets[EFFICACY], sets[CIBIC]
    problems = []
    for name, eff in sets.items():
        found = efficacy_problems(eff, eff.gold)
        print(f"unchanged, {name}: {len(found)} problems")
        if found:
            return [f"the unchanged inputs of {name} do not pass the check", *found[:5]]

    def mmrm(change, suffixes=("LSM", "PwPbo", "PwLow"), averaged=True) -> dict:
        value = copy.deepcopy(adas.event.data)
        value = _parameters(value, suffixes, change, prefix=MMRM)
        if averaged:  # the averaged analyses, which the proofs read, change alike
            value = _parameters(value, ("Avg",), change, prefix=MMRM)
        return value

    def option(name, given):
        return lambda ps: [dict(p, value=given) if p["name"] == name else p for p in ps]

    def cmh(change) -> dict:
        return _parameters(copy.deepcopy(cibic.event.data), ("Cmh",), change, prefix="An_CIBIC")

    def locf_too(clauses):
        return [c for c in clauses if c["condition"]["variable"] != "DTYPE"]

    def observed_only(clauses):
        return [*clauses, {"level": 2, "order": len(clauses) + 1, "condition": {
            "dataset": "ADQSCIBC", "variable": "DTYPE", "comparator": "EQ", "value": [""]}}]

    def population_percent(value: dict) -> dict:
        for analysis in value["analyses"]:
            for item in analysis.get("referencedAnalysisOperations") or []:
                if item["referencedOperationRelationshipId"].endswith("_DEN"):
                    item["analysisId"] = "An_CIBIC_EFF_N"
        return value

    def week24_alone_on_locf(value: dict) -> dict:
        """Gold's analyses on the records LOCF adds; the averaged ones as they are."""
        subset = copy.deepcopy(next(s for s in value["dataSubsets"]
                                    if s["id"] == "DS_ADAS_MMRM"))
        subset["id"] = "DS_ADAS_MMRM_LOCF"
        subset["compoundExpression"]["whereClauses"] = locf_too(
            subset["compoundExpression"]["whereClauses"])
        value["dataSubsets"].append(subset)
        for analysis in value["analyses"]:
            if analysis["id"] in (f"{MMRM}_LSM", f"{MMRM}_PwPbo", f"{MMRM}_PwLow"):
                analysis["dataSubsetId"] = "DS_ADAS_MMRM_LOCF"
        return value

    in_adas = {
        # Gold's analyses alone, the averaged ones the proofs read as they are (review of
        # real-5b, F1): the proofs must not stand in for gold.
        "gold's analyses alone at 90% confidence": mmrm(
            lambda ps: [*ps, {"name": "confidence_level", "value": ["90"]}], averaged=False),
        "gold's analyses alone on the records LOCF adds":
            week24_alone_on_locf(copy.deepcopy(adas.event.data)),
        "the mixed model with the records LOCF adds":
            _with_subset(copy.deepcopy(adas.event.data), "DS_ADAS_MMRM", locf_too),
        "Satterthwaite in place of Kenward-Roger": mmrm(option("df", ["satterthwaite"])),
        "a Toeplitz covariance": mmrm(option("covariance", ["toeplitz"])),
        "no baseline by week": mmrm(option("by_visit", [])),
        "the site in place of the pooled site group": mmrm(option("factors", ["SITEID"])),
        "gold takes the LS means averaged over the weeks, as the CSR does":
            mmrm(option("at", ["average"]), averaged=False),
    }
    in_cibic = {
        "the CMH test of general association": cmh(option("statistic",
                                                          ["general_association"])),
        "the CMH test without strata": cmh(lambda ps: [p for p in ps if p["name"] != "strata"]),
        "the CMH test with rank scores": cmh(option("scores", ["rank"])),
        # At week 8 LOCF adds no record: nothing comes before it to carry forward.
        "week 24 with the observed records only, without LOCF": _with_subset(
            copy.deepcopy(cibic.event.data), "DS_CIBIC_W24", observed_only),
        "the percent of the efficacy population in place of the subjects of the week":
            population_percent(copy.deepcopy(cibic.event.data)),
    }
    number = 0
    for eff, planted in ((adas, in_adas), (cibic, in_cibic)):
        for name, value in planted.items():
            number += 1
            rows = efficacy_rows(pilot, eff, value, tmp_path / f"event-{number}")
            _seen(name, efficacy_problems(eff, rows, ars.index(value)), problems)
    # The decision records against the events (gate check `decisions`).
    from specfirst.machine import decisions

    # The efficacy records: the kit's first decisions file (issue #31 adds the second).
    records = decisions.load(pilot.folder / kits.load_kit(pilot.root, KIT).decisions[0])

    def with_value(wanted: str, **value) -> list[dict]:
        return [dict(record, value={**record["value"], **value}) if record["id"] == wanted
                else record for record in records]

    for name, eff, value, given in (
            ("unchanged", None, None, records),
            ("gold takes the LS means averaged over the weeks", adas,
             in_adas["gold takes the LS means averaged over the weeks, as the CSR does"],
             records),
            ("the CMH test of general association", cibic,
             in_cibic["the CMH test of general association"], records),
            # Review of real-5b, G2 (the owner's answer of 2026-11-20): the visits by AVISIT,
            # text, in the record of the terms and in the six analyses alike, so that Week 8
            # is the last visit; every option is as its record says.
            ("the visits by AVISIT, in custom:eff-mmrm-terms and the six analyses alike (G2)",
             adas, mmrm(option("visit", ["AVISIT"])),
             with_value("custom:eff-mmrm-terms", visit=["AVISIT"])),
            ("custom:eff-mmrm-visit names Week 16 as the last week (G2)", None, None,
             with_value("custom:eff-mmrm-visit", last="Week 16"))):
        found = decision_problems(pilot, given, [
            (ars.index(value if each is eff else each.event.data), each.spec)
            for each in (adas, cibic)])
        print(f"decision records, {name}: {len(found)} problems"
              + (f", for example: {found[0][:160]}" if found else ""))
        if (name == "unchanged") == bool(found):
            problems.append(f"decision records, {name}: {len(found)} problems")
    # In the references and in the exceptions.
    tables = copy.deepcopy(cibic.tables)
    line = next(line for line in tables["Out14-3-13"]["lines"] if line["cells"] and
                line["cells"][3] == "0.2727")
    line["cells"][3] = "0.2737"
    entries_11 = adas.entries["Out14-3-11"]
    signed = next(n for n, e in enumerate(entries_11) if "display" in e["proof"])
    zero = next(n for n, e in enumerate(cibic.entries["Out14-3-13"]) if e["csr"] == "0")

    def replaced(eff, output, number, entry):
        listed = list(eff.entries[output])
        listed[number] = entry
        return {**eff.entries, output: listed}

    # Review of real-5b, G1: a pattern that carries the CSR's text around its mask.
    entries_13 = cibic.entries["Out14-3-13"]
    week8 = next(n for n, e in enumerate(entries_13) if e["cell"] == "cell:Out14-3-13/r2/c4")
    carried = {"p": "X.2727"}  # mask X: the p-value rounded to 0, then the CSR's ".2727"
    shown_13 = next(d for d in cibic.spec.displays if d.output == "Out14-3-13")
    text_13 = (pilot.folder / shown_13.layout).read_text(encoding="ascii")
    wrong_13 = text_13.replace("p: {analysis: An_CIBIC_W08_Cmh",
                               "p: {analysis: An_CIBIC_W16_Cmh", 1)
    assert wrong_13 != text_13
    week16 = Efficacy(**{**cibic.__dict__, "layouts": {
        **cibic.layouts, "Out14-3-13": layouts.parse(yaml.safe_load(wrong_13), "Out14-3-13")}})

    def spelled(name: str, text: str) -> str:
        """H1: a template whose format specs give `text` for any value of the part."""
        return "".join("{" + name + ":" + character + "<1.0}" for character in text)

    planted = {
        "a p-value of the CSR changed (0.2727 to 0.2737)":
            lambda: efficacy_problems(cibic, cibic.gold, tables=tables),
        "an other_build proof that names the analysis at Week 24 itself":
            lambda: efficacy_problems(adas, adas.gold, entries=replaced(
                adas, "Out14-3-11", 0, dict(entries_11[0], proof={
                    "kind": "other_build", "analyses": {
                        "An_ADAS_MMRM_LSM": "An_ADAS_MMRM_LSM"}}))),
        "the proof of '-0.0' without the sign kept":
            lambda: efficacy_problems(adas, adas.gold, entries=replaced(
                adas, "Out14-3-11", signed, dict(entries_11[signed], proof={
                    k: v for k, v in entries_11[signed]["proof"].items() if k != "display"}))),
        "a count of 0 proved by another pattern, not by the template":
            lambda: efficacy_problems(cibic, cibic.gold, entries=replaced(
                cibic, "Out14-3-13", zero, dict(cibic.entries["Out14-3-13"][zero], proof={
                    "kind": "other_pattern", "patterns": {"n": "X"}}))),
        "an exception of 14-3.13 left out":
            lambda: efficacy_problems(cibic, cibic.gold, entries={
                **cibic.entries, "Out14-3-13": cibic.entries["Out14-3-13"][1:]}),
        "a proof whose template is the CSR's text": lambda: efficacy_problems(
            adas, adas.gold, entries=replaced(adas, "Out14-3-11", 0, dict(
                entries_11[0], proof={"kind": "other_build",
                                      "template": entries_11[0]["csr"]}))),
        "a proof whose template adds text ('{lsm} (0.49)')": lambda: efficacy_problems(
            adas, adas.gold, entries=replaced(adas, "Out14-3-11", 0, dict(
                entries_11[0], proof={"kind": "other_build", "template": "{lsm} (0.49)",
                                      "analyses": entries_11[0]["proof"]["analyses"]}))),
        "an entry that names an unrelated decision (custom:eff-cmh)": lambda: efficacy_problems(
            adas, adas.gold, entries=replaced(adas, "Out14-3-11", 0, dict(
                entries_11[0], decision="custom:eff-cmh"))),
        "a proof whose pattern carries the CSR's text ('X.2727', other_pattern)":
            lambda: efficacy_problems(cibic, cibic.gold, entries=replaced(
                cibic, "Out14-3-13", week8, dict(entries_13[week8], proof={
                    "kind": "other_pattern", "patterns": carried}))),
        "a proof whose pattern carries the CSR's text ('X.2727', other_build)":
            lambda: efficacy_problems(cibic, cibic.gold, entries=replaced(
                cibic, "Out14-3-13", week8, dict(entries_13[week8], proof={
                    "kind": "other_build", "patterns": carried}))),
        "gold's week 8 p-value is week 16's, proved by a pattern that carries the CSR's text":
            lambda: efficacy_problems(week16, cibic.gold, entries=replaced(
                cibic, "Out14-3-13", week8, dict(entries_13[week8], proof={
                    "kind": "other_pattern", "patterns": carried}))),
        "a proof of 14-3.11 whose pattern carries the CSR's text ('X.X (0.49)')":
            lambda: efficacy_problems(adas, adas.gold, entries=replaced(
                adas, "Out14-3-11", 0, dict(entries_11[0], proof={
                    "kind": "other_build", "template": "{lsm}",
                    "analyses": entries_11[0]["proof"]["analyses"],
                    "patterns": {"lsm": "X.X (0.49)"}}))),
        "gold's week 8 p-value is week 16's, proved by a template whose format specs spell "
        "the CSR's text": lambda: efficacy_problems(week16, cibic.gold, entries=replaced(
            cibic, "Out14-3-13", week8, dict(entries_13[week8], proof={
                "kind": "other_build", "template": spelled("p", entries_13[week8]["csr"])}))),
        "a proof of 14-3.11 whose template's format specs spell the CSR's text":
            lambda: efficacy_problems(adas, adas.gold, entries=replaced(
                adas, "Out14-3-11", 0, dict(entries_11[0], proof={
                    "kind": "other_build",
                    "template": spelled("lsm", entries_11[0]["csr"])}))),
    }
    # Review of real-5b, K1 (the owner's answer of 2026-11-20): gold's CMH of week 8 without
    # its strata, proved by an other analysis with them. The two differ only in an option of
    # custom:eff-cmh, so before K1 the proof held.
    unstratified = copy.deepcopy(cibic.event.data)
    gold_cmh = next(a for a in unstratified["analyses"] if a["id"] == "An_CIBIC_W08_Cmh")
    unstratified["analyses"].append(dict(copy.deepcopy(gold_cmh), id="An_CIBIC_W08_Cmh_Site",
                                         name=gold_cmh["name"] + ", by pooled site group"))
    gold_cmh["programmingCode"]["parameters"] = [
        p for p in gold_cmh["programmingCode"]["parameters"] if p["name"] != "strata"]
    unstratified_rows = efficacy_rows(pilot, cibic, unstratified, tmp_path / "k1")
    by_site = replaced(cibic, "Out14-3-13", week8, dict(
        entries_13[week8], decision=["custom:eff-cmh", "custom:eff-cibic-display"],
        proof={"kind": "other_build", "patterns": {"p": "X.XXXX"},
               "analyses": {"An_CIBIC_W08_Cmh": "An_CIBIC_W08_Cmh_Site"}}))
    k1 = "gold's week 8 CMH without its strata, proved by the analysis with them (K1)"
    planted[k1] = lambda: efficacy_problems(cibic, unstratified_rows, ars.index(unstratified),
                                            entries=by_site)
    for name, check in planted.items():
        found = check()
        _seen(name, found, problems)
        if name == k1 and not any("an option whose values are columns" in p for p in found):
            problems.append(f"{name}: not seen by the rule of K1")
    return problems


def d12_cmh_engines(pilot: Pilot, tmp_path) -> list[str]:
    """Rule R11 for CMH: a defect in the R engine's input alone must show as a disagreement."""
    eff = efficacy_5b(pilot)[CIBIC]

    def engines(data: dict, r_data: dict, work: Path) -> tuple[list[str], list]:
        event, r_event = ars.index(data), ars.index(r_data)
        bound = ars.bind(event, pilot.registry, eff.spec.binding)
        r_bound = ars.bind(r_event, pilot.registry, eff.spec.binding)
        wanted = ars.columns(event, eff.spec.subject_key)
        for dataset, names in ars.columns(r_event, eff.spec.subject_key).items():
            wanted[dataset] = sorted({*wanted.get(dataset, []), *names})
        tables = ard.load_tables(pilot.folder / build.ADAM, wanted)
        python = ard.run(event, pilot.registry, bound, tables, eff.spec.subject_key)
        work.mkdir(parents=True, exist_ok=True)
        path = work / "event.json"
        path.write_text(json.dumps(r_data), encoding="ascii")
        other, _, _ = rengine.run(pilot.root, work, path, registry.json_path(pilot.root),
                                  r_bound, tables, eff.spec.subject_key)
        lines, disagreements = results.agreement(results.by_id(python), results.by_id(other))
        cmh = [d for d in disagreements if "_Cmh/" in str(d)]
        return lines, cmh

    data = copy.deepcopy(eff.event.data)
    lines, found = engines(data, data, tmp_path / "control")
    print(f"unchanged: {lines[0]}")
    problems = [f"the engines disagree on the unchanged inputs: {found[:3]}"] if found else []

    def cmh(change):
        return _parameters(copy.deepcopy(eff.event.data), ("Cmh",), change, prefix="An_CIBIC")

    planted = {
        "general association": cmh(lambda ps: [dict(p, value=["general_association"])
                                               if p["name"] == "statistic" else p
                                               for p in ps]),
        "no strata": cmh(lambda ps: [p for p in ps if p["name"] != "strata"]),
        "rank scores": cmh(lambda ps: [dict(p, value=["rank"]) if p["name"] == "scores" else p
                                       for p in ps]),
        # Not an option of the test, so the stamps stay the same and the values differ.
        "week 24 with the observed records only, without LOCF": _with_subset(
            copy.deepcopy(eff.event.data), "DS_CIBIC_W24", lambda clauses: [
                *clauses, {"level": 2, "order": len(clauses) + 1, "condition": {
                    "dataset": "ADQSCIBC", "variable": "DTYPE", "comparator": "EQ",
                    "value": [""]}}]),
    }
    for number, (name, r_data) in enumerate(planted.items(), start=1):
        _, found = engines(data, r_data, tmp_path / f"planted{number}")
        print(f"R engine alone, {name}: {len(found)} CMH results disagree")
        if not found:
            problems.append(f"{name}, in the R engine alone: the engines are said to agree")
    return problems


# ---- issue #31: the review page (ADR-022) -------------------------------------------------

# The outputs the acceptance of issue #31 names: the demographics and AE tables of the pilot.
REVIEWED = ("Out14-1-1", "Out14-3-1-1", "Out14-3-2-1")


def _linked_build(pilot: Pilot, tmp_path: Path) -> Path:
    """A build that is the pilot's but for its graph, which is a copy: the rest is linked."""
    work = tmp_path / "linked" / KIT
    (work / "gold").mkdir(parents=True)
    for item in pilot.folder.iterdir():
        if item.name != "gold":
            (work / item.name).symlink_to(item)
    for item in (pilot.folder / "gold").iterdir():
        if item.name != "graph":
            (work / "gold" / item.name).symlink_to(item)
    shutil.copytree(pilot.folder / build.GRAPH, work / build.GRAPH)
    return work


def d13_review(pilot: Pilot, tmp_path) -> list[str]:
    """The review page of the pilot and the acceptance of issue #31: they hold on the build,
    and each defect planted in the page, the review or the graph files is seen."""
    from unittest import mock

    from specfirst.viewer import check as checks
    from specfirst.viewer import model, page

    none = tmp_path / "no-recompute"
    review = model.load(pilot.root, KIT, pilot.folder, recompute=none)
    text = page.html(review)
    problems = [f"the unchanged page: {p}" for p in checks.page_problems(text, review)[:3]]
    lines, found = checks.acceptance(review, text, REVIEWED)
    for line in lines:
        print(line)
    problems += [f"the unchanged acceptance: {p}" for p in found[:3]]
    if page.html(model.load(pilot.root, KIT, pilot.folder, recompute=none)) != text:
        problems.append("the page of the same build is not the same twice")
    cell = sorted(c.id for c in review.cells.values() if c.output == "Out14-3-2-1")[0]
    record = sorted(review.decisions)[0]
    entry = next(line.key for line in review.sheet if line.kind == "catalog entry")

    def row_gone(key: str) -> str:
        """The page without the row of the sheet of a key: planted in the page (F3)."""
        anchor = html.escape("s-" + key.replace(" ", "_"))
        row = f'<tr class="decision" id="{anchor}" data-key="{html.escape(key)}">'
        assert row in text, row
        return text.replace(row, "<tr>")

    # A record that binds a column the TEAE counts read, through the columns it derives from
    # (ADAE.ASTDT, from which TRTEMFL derives): its block is taken out of every panel.
    teae = next(view for view in review.analyses.values()
                if view.id == "An07_01_TEAE_Summ_ByTrt")
    upstream = next(key for key, bound, read in teae.column_decisions if bound != read)
    no_block = text.replace(f'<li class="decision" data-key="{html.escape(upstream)}">', "<li>")
    # The panels name no SDTM column: the lines "Down to SDTM" are emptied.
    no_sdtm = re.sub(r"Down to SDTM: (<code>[^<]*</code>(, )?)+", "Down to SDTM: none", text)
    p4 = {(review.decisions[record].id, review.decisions[record].unit): model.UNSEPARATED}
    unseparated = model.load(pilot.root, KIT, pilot.folder, recompute=none, p4=p4)
    unseparated_text = page.html(unseparated)
    problems += [f"the page with an unseparated decision: {p}"
                 for p in checks.page_problems(unseparated_text, unseparated)[:3]]
    planted = {
        "a cell without a panel": lambda: checks.acceptance(
            review, text.replace(f'id="c-{cell}"', 'id="c-gone"'), REVIEWED)[1],
        "a script": lambda: checks.page_problems(
            text.replace("</body>", "<script>fetch('x')</script></body>"), review),
        "a handler": lambda: checks.page_problems(
            text.replace('<a class="number"', '<a onmouseover="x()" class="number"', 1), review),
        "a link that leaves the page": lambda: checks.page_problems(
            text.replace('href="#sheet"', 'href="https://example.org/"'), review),
        "a judged edge drawn as proven": lambda: checks.page_problems(text.replace(
            '<li class="citation"><span class="kind judged">',
            '<li class="citation"><span class="kind executed">', 1), review),
        "an unseparated decision drawn as proven": lambda: checks.page_problems(
            unseparated_text.replace("kind unseparated", "kind static"), unseparated),
        "a decision left off the sheet": lambda: checks.acceptance(
            review, row_gone(record), REVIEWED)[1],
        "an entry of the catalog left off the sheet": lambda: checks.acceptance(
            review, row_gone(entry), REVIEWED)[1],
        f"the decision {upstream} left off the panels": lambda: [
            p for p in checks.acceptance(review, no_block, REVIEWED)[1]
            if "does not draw the decision" in p],
        "no SDTM column named in the panels": lambda: [
            p for p in checks.acceptance(review, no_sdtm, REVIEWED)[1]
            if "reaches no SDTM column" in p],
    }
    for name, seen in planted.items():
        found = seen()
        print(f"planted, {name}: {len(found)} problems"
              + (f", for example: {found[0][:140]}" if found else ""))
        if not found:
            problems.append(f"{name}: not seen")
    # In the graph files: the derives_from edges of a column the demographics read are lost,
    # and coverage.json still says that it reaches SDTM.
    work = _linked_build(pilot, tmp_path)
    edges_file = work / build.GRAPH / "edges.jsonl"
    kept = [line for line in edges_file.read_text(encoding="ascii").splitlines(keepends=True)
            if not (json.loads(line)["type"] == "derives_from"
                    and json.loads(line)["from"] == "adam:ADSL.AGEGR1")]
    edges_file.write_text("".join(kept), encoding="ascii")
    broken = model.load(pilot.root, KIT, work, recompute=none)
    found = [p for p in checks.acceptance(broken, page.html(broken), REVIEWED)[1]
             if "reaches no SDTM column" in p]
    print(f"planted in the graph files, the derives_from edges of ADSL.AGEGR1 left out: "
          f"{len(found)} cells seen")
    if not found:
        problems.append("a broken path to SDTM in the graph files: not seen")
    # In the exceptions: a difference of display that no cell shows (issue #31, formats).
    extra = {"result": f"ard:{OVERVIEW}/Mth01_CatVar_Summ_ByGrp_1_n/AnlsGrouping_01_Trt_1",
             "formatted": "65.0", "class": "reference_error",
             "proof": {"kind": "not_its_own_pattern"}}
    real = results.load_formats

    def more(path):
        made = real(path)
        made.setdefault(pilot.spec.id, {})[extra["result"]] = extra
        return made

    said: list[str] = []
    with mock.patch.object(results, "load_formats", more):
        passed, _ = build.display_checks(pilot.root, KIT, pilot.folder, said.append)
    print(f"planted in the exceptions, a difference of display no cell shows: passes {passed}")
    if passed or not any("no cell of a built grid" in line for line in said):
        problems.append("an entry of formats that is no difference: not seen")
    # In the exceptions: the entry of a difference that a cell shows, under a misspelt result
    # set (the review of issue #31, F5).
    shown = real(pilot.folder / "gold" / "exceptions.yaml")[pilot.spec.id]

    def misspelt(path):
        made = real(path)
        made.pop(pilot.spec.id, None)
        made[pilot.spec.id[:-1]] = shown
        return made

    said = []
    with mock.patch.object(results, "load_formats", misspelt):
        passed, _ = build.display_checks(pilot.root, KIT, pilot.folder, said.append)
    print(f"planted in the exceptions, a difference of display under {pilot.spec.id[:-1]}: "
          f"passes {passed}")
    if passed or not any("which is no result set of the kit" in line for line in said):
        problems.append("an entry of formats under a misspelt result set: not seen")
    return problems


CASES = {"D1-arms": d1_arms, "D2-set": d2_set, "D3-quantile": d3_quantile,
         "D4-subset": d4_subset, "D5-engines": d5_engines, "D6-proofs": d6_proofs,
         "D7-display": d7_display, "D8-trace": d8_trace, "D9-efficacy": d9_efficacy,
         "D10-trace-model": d10_trace_model, "D11-efficacy-5b": d11_efficacy_5b,
         "D12-cmh-engines": d12_cmh_engines, "D13-review": d13_review}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_defects(case, pilot, tmp_path):
    print(f"\n--- {case}")
    problems = CASES[case](pilot, tmp_path)
    assert not problems, "\n".join(problems)
