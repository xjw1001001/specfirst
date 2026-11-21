"""Issue #29 on CDISCPILOT01 (ADR-021): the recomputation scripts reproduce the ARD, and
they catch a planted break of the engine; the checks of the scripts fail on planted defects
(rule R5).

The planted breaks change one option in the engine and nothing else: the ARS, the decision
records and the registry stay as they are, so the ARD rows keep their option hash, and the
scripts, generated from those unchanged inputs, give what they gave.

- weights: the R engine computes the ANCOVA LS means with equal weights where the analysis
  states proportional (the acceptance of #29). No printed cell of the CSR tables shows an LS
  mean, and rule R11 does not apply to a method only R implements.
- quantiles: both engines compute quartiles by R type 7 where the analysis states SAS
  definition 5. The engines agree, so rule R11 is silent.
- CMH: both engines compute the general association statistic where the analysis states
  row mean scores. The engines agree.

These tests need `specfirst fetch`, the engine and R, and carry the marker `evidence`.
Without them they are skipped, except under SPECFIRST_STRICT=1 (a gate), where they fail.
With SPECFIRST_RECOMPUTE_REUSE=1 (set by the gate issue-29 after its check "recompute"),
the build and the run of build/recompute/<kit> are used; otherwise the kit is built and the
bundle run here.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

import pytest

from specfirst import kit as kits
from specfirst.machine import ard, build, methods, rengine, results
from specfirst.machine import registry as registries
from specfirst.machine.canonical import read_jsonl
from specfirst.paths import cache_dir, repo_root
from specfirst.recompute import generate, static
from specfirst.recompute import run as recompute

pytestmark = pytest.mark.evidence
KIT = "cdiscpilot01"
ANALYSES = 69  # the analyses of the kit's three reporting events (ADR-021, decision 2)


class Missing(Exception):
    pass


@dataclass
class Pilot:
    root: Path
    folder: Path  # the build
    kit: kits.Kit
    bundle: Path
    work: Path  # the sealed run: out/, report.json
    report: dict

    def gold(self, event: str) -> list[dict]:
        return read_jsonl(self.folder / build.ARD / f"{event}.jsonl")


@pytest.fixture(scope="session")
def pilot(tmp_path_factory) -> Pilot:
    root = repo_root()
    try:
        if not (cache_dir(root) / "p7" / ".git").exists():
            raise Missing("not in the fetch cache: p7; run `specfirst fetch`")
        if not rengine.available():
            raise Missing("Rscript is not installed")
    except Missing as error:
        if os.environ.get("SPECFIRST_STRICT") == "1":
            pytest.fail(str(error))
        pytest.skip(str(error))
    base = generate.recompute_dir(root, KIT)
    checks = base / "run" / "checks.json"
    if os.environ.get("SPECFIRST_RECOMPUTE_REUSE") == "1" and checks.is_file():
        folder = Path(json.loads(checks.read_text(encoding="ascii"))["build"])
    else:
        folder = tmp_path_factory.mktemp("recompute") / KIT
        said: list[str] = []
        assert build.build(root, KIT, into=folder, out=said.append) == 0, "\n".join(said)
        recompute.recompute(root, KIT, build=folder, out=said.append)
    report = json.loads((base / "run" / "report.json").read_text(encoding="ascii"))
    return Pilot(root, folder, kits.load_kit(root, KIT), base / "bundle", base / "run", report)


def statuses(report: dict) -> dict[str, str]:
    return {f"{line['event']}/{line['analysis']}": line["status"] for line in report["analyses"]}


def planted_root(pilot: Pilot, tmp_path: Path, file: str, old: str, new: str) -> Path:
    """A copy of the R engine with one text replaced, exactly once."""
    target = tmp_path / "planted"
    shutil.copytree(pilot.root / "r", target / "r")
    path = target / "r" / "specfirstr" / "R" / file
    text = path.read_text(encoding="utf-8")
    assert text.count(old) == 1, f"{file}: the plant's text is not there once"
    path.write_text(text.replace(old, new), encoding="utf-8")
    return target


def r_rows(pilot: Pilot, engine_root: Path, event: str, work: Path) -> list[dict]:
    spec = next(s for s in pilot.kit.results if s.id == event)
    inputs = build.result_inputs(pilot.root, pilot.folder, spec)
    rows, meta, _ = rengine.run(engine_root, work, pilot.folder / spec.ars,
                                registries.json_path(pilot.root), inputs.binding,
                                inputs.tables, spec.subject_key)
    assert rengine.data_problems(meta, inputs.tables) == []
    return rows


def python_rows(pilot: Pilot, event: str) -> list[dict]:
    spec = next(s for s in pilot.kit.results if s.id == event)
    inputs = build.result_inputs(pilot.root, pilot.folder, spec)
    return ard.run(inputs.event, inputs.registry, inputs.binding, inputs.tables,
                   spec.subject_key)


def planted_ard(pilot: Pilot, tmp_path: Path, event: str, rows: list[dict]) -> Path:
    """The gold ARD of every event, with the planted rows of one."""
    folder = tmp_path / "ard"
    folder.mkdir()
    for spec in pilot.kit.results:
        target = folder / f"{spec.id}.jsonl"
        if spec.id == event:
            results.write_ard(target, rows, pilot.root)
        else:
            shutil.copyfile(pilot.folder / build.ARD / f"{spec.id}.jsonl", target)
    return folder


def changed(gold: list[dict], planted: list[dict]) -> set[str]:
    old = {row["id"]: row["raw_value"] for row in gold}
    new = {row["id"]: row["raw_value"] for row in planted}
    return {key for key in old.keys() | new.keys()
            if key not in old or key not in new or not results.same(old[key], new[key])}


def shown_rows(pilot: Pilot) -> set[str]:
    """Every ARD row a cell of a built grid shows."""
    found: set[str] = set()
    for path in sorted((pilot.folder / build.GRID).glob("*.json")):
        if path.name.endswith(".shell.json"):
            continue
        made = json.loads(path.read_text(encoding="utf-8"))

        def walk(value: object) -> None:
            if isinstance(value, dict):
                for item in value.values():
                    if isinstance(item, str) and item.startswith("ard:"):
                        found.add(item)
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item.startswith("ard:"):
                        found.add(item)
                    walk(item)

        walk(made)
    return found


def caught(pilot: Pilot, tmp_path: Path, ard_folder: Path) -> dict[str, str]:
    report = recompute.compare(pilot.bundle, pilot.work / "out", ard_folder,
                               tmp_path / "report.json")
    return statuses(report)


def unplanted(pilot: Pilot, tmp_path: Path, monkeypatch) -> None:
    """The control: every analysis is reproduced, so a differs below is the plant's."""
    print("\n".join(compare_lines(pilot.report)[-1:]))
    assert pilot.report["counts"] == {"reproduced": ANALYSES}


def compare_lines(report: dict) -> list[str]:
    from specfirst.recompute.bundle.compare import text_lines

    return text_lines(report)


def plant_ancova_weights(pilot: Pilot, tmp_path: Path, monkeypatch) -> None:
    """The acceptance of #29: one swapped option in the engine is caught by the scripts."""
    engine = planted_root(pilot, tmp_path, "models.R", "weights = weights, data = frame",
                          "weights = \"equal\", data = frame")
    rows = r_rows(pilot, engine, "efficacy-adas", tmp_path / "work")
    gold = pilot.gold("efficacy-adas")
    python = [row for row in gold if row["method_id"] not in
              results.r_only_methods(registries.load(pilot.root))]
    planted = build.gold_rows(python, rows, registries.load(pilot.root))
    moved = changed(gold, planted)
    shown = moved & shown_rows(pilot)
    found = caught(pilot, tmp_path, planted_ard(pilot, tmp_path, "efficacy-adas", planted))
    differs = sorted(k for k, v in found.items() if v == "differs")
    print(f"\nplanted: the ANCOVA LS means with equal weights where the analysis states "
          f"proportional: {len(moved)} ARD rows change, {len(shown)} of them shown by a cell "
          f"of a built grid; the scripts: {len(differs)} analyses differ: {', '.join(differs)}")
    assert moved and not shown, "the plant must change rows that no printed cell shows"
    lsm = {f"efficacy-adas/An_ADAS_W{w}_LSM" for w in ("24", "08", "16")}
    assert set(differs) == lsm
    assert sum(1 for v in found.values() if v == "reproduced") == ANALYSES - len(lsm)


def plant_quantiles(pilot: Pilot, tmp_path: Path, monkeypatch) -> None:
    """Both engines with R type 7 where the analysis states SAS 5: R11 is silent."""
    original = methods.quantile

    def swapped(ordered, quarters, definition):
        return original(ordered, quarters, {"sas5": "r7", "r7": "sas5"}[definition])

    monkeypatch.setattr(methods, "quantile", swapped)
    event = "common-safety-displays"
    python = python_rows(pilot, event)
    engine = planted_root(pilot, tmp_path, "methods.R", "QUANTILE_TYPES <- c(sas5 = 2L, r7 = 7L)",
                          "QUANTILE_TYPES <- c(sas5 = 7L, r7 = 2L)")
    other = r_rows(pilot, engine, event, tmp_path / "work")
    disagree = changed(python, other)
    moved = changed(pilot.gold(event), python)
    found = caught(pilot, tmp_path, planted_ard(pilot, tmp_path, event, python))
    differs = sorted(k for k, v in found.items() if v == "differs")
    print(f"\nplanted: quartiles by R type 7 in both engines: {len(moved)} ARD rows change, "
          f"the engines disagree on {len(disagree)}; the scripts: {len(differs)} analyses "
          f"differ: {', '.join(differs)}")
    assert moved and not disagree
    quartiles = {f"{event}/{a}" for a in ("An03_01_Age_Summ_ByTrt", "An03_06_Height_Summ_ByTrt",
                                          "An08_01_Obs_Summ_ByTrt", "An08_02_ChgBl_Summ_ByTrt")}
    assert set(differs) == quartiles


def plant_cmh(pilot: Pilot, tmp_path: Path, monkeypatch) -> None:
    """Both engines with the general association statistic where the analysis states row
    mean scores: R11 is silent."""
    original = methods.cmh_p

    def swapped(tables, values=None, statistic="general_association", scores="table"):
        other = {"general_association": "row_mean_scores",
                 "row_mean_scores": "general_association"}[statistic]
        return original(tables, values, statistic=other, scores=scores)

    monkeypatch.setattr(methods, "cmh_p", swapped)
    event = "efficacy-cibic"
    python = python_rows(pilot, event)
    guard = '  if (!statistic %in% c("general_association", "row_mean_scores")) {'
    engine = planted_root(pilot, tmp_path, "methods.R", guard,
                          '  statistic <- setdiff(c("general_association", "row_mean_scores"), '
                          'statistic)\n' + guard)
    other = r_rows(pilot, engine, event, tmp_path / "work")
    disagree = changed(python, other)
    moved = changed(pilot.gold(event), python)
    found = caught(pilot, tmp_path, planted_ard(pilot, tmp_path, event, python))
    differs = sorted(k for k, v in found.items() if v == "differs")
    print(f"\nplanted: CMH general association in both engines: {len(moved)} ARD rows change, "
          f"the engines disagree on {len(disagree)}; the scripts: {len(differs)} analyses "
          f"differ: {', '.join(differs)}")
    assert moved and not disagree
    assert set(differs) == {f"{event}/An_CIBIC_W{w}_Cmh" for w in ("08", "16", "24")}


def plan_entry(pilot: Pilot, analysis: str) -> dict:
    plan = json.loads((pilot.bundle / "plan.json").read_text(encoding="ascii"))
    return next(e for e in plan["analyses"] if e["analysis"] == analysis)


def checker_plants(pilot: Pilot, tmp_path: Path, monkeypatch) -> None:
    """The checks of the scripts fail on defects planted for them (rule R5)."""
    numbers = recompute.analysis_numbers(pilot.root, KIT, pilot.folder)
    age = plan_entry(pilot, "An03_01_Age_Summ_ByTrt")
    lsm = plan_entry(pilot, "An_ADAS_W24_LSM")
    python = (pilot.bundle / age["file"]).read_text(encoding="ascii")
    r = (pilot.bundle / lsm["file"]).read_text(encoding="ascii")
    allowed_py = numbers[(age["event"], age["analysis"])]
    allowed_r = numbers[(lsm["event"], lsm["analysis"])]
    gold = {row["id"]: row["raw_value"] for row in pilot.gold("efficacy-adas")}
    pasted = next(v for k, v in sorted(gold.items()) if "An_ADAS_W24_LSM" in k)
    assert static.python_problems(python, age["datasets"], allowed_py) == []
    planted_py = {
        "an import of the engine": python.replace("import sys\n", "import sys\nimport specfirst\n"),
        "the ARD read": python.replace('"adsl.parquet"', '"common-safety-displays.jsonl"'),
        "the built ADaM by a path": python.replace('"adsl.parquet"',
                                                   '"../data/adam/adsl.parquet"'),
        "a number of the ARD": python.replace("n = len(x)", f"n = len(x) + 0 * {pasted!r}"),
    }
    for name, text in planted_py.items():
        problems = static.python_problems(text, age["datasets"], allowed_py)
        print(f"planted in {age['analysis']}: {name}: {problems[:1]}")
        assert problems, name
    tokens_path = tmp_path / "lsm.R"
    planted_r = {
        "a source of the engine": r.replace(
            "args <- commandArgs", 'source("r/specfirstr/R/models.R")\nargs <- commandArgs'),
        "a library": r.replace("args <- commandArgs", "library(specfirstr)\nargs <- commandArgs"),
        "a number of the ARD": r.replace("level = 95 / 100", f"level = 95 / 100 + 0 * {pasted!r}"),
    }
    tokens_path.write_text(r, encoding="ascii")
    assert static.r_problems(static.r_tokens([tokens_path])[str(tokens_path)], lsm["datasets"],
                             allowed_r) == []
    for name, text in planted_r.items():
        tokens_path.write_text(text, encoding="ascii")
        problems = static.r_problems(static.r_tokens([tokens_path])[str(tokens_path)],
                                     lsm["datasets"], allowed_r)
        print(f"planted in {lsm['analysis']}: {name}: {problems[:1]}")
        assert problems, name
    # The sealed run refuses the engine even where the static check would not look.
    bundle = tmp_path / "bundle"
    shutil.copytree(pilot.bundle, bundle)
    (bundle / age["file"]).write_text(planted_py["an import of the engine"], encoding="ascii")
    with tempfile.TemporaryDirectory() as name:
        parquet, csv = recompute.data_folder(bundle, pilot.folder / pilot.kit.reference, Path(name))
        why = recompute.run_one(bundle, age, parquet, csv, tmp_path / "out", tmp_path / "logs")
    print(f"planted in {age['analysis']}: the sealed run: {why}")
    assert why and "refused by the sealed run" in why


def comparison_plants(pilot: Pilot, tmp_path: Path, monkeypatch) -> None:
    """The comparison fails on a swapped option in a script, a lost row, an extra row and a
    value off by a relative 1e-8."""
    age = plan_entry(pilot, "An03_01_Age_Summ_ByTrt")
    bundle = tmp_path / "bundle"
    shutil.copytree(pilot.bundle, bundle)
    script = bundle / age["file"]
    script.write_text(script.read_text(encoding="ascii").replace(
        '"averaged_inverted_cdf"', '"linear"'), encoding="ascii")
    outputs = tmp_path / "out"
    shutil.copytree(pilot.work / "out", outputs)
    with tempfile.TemporaryDirectory() as name:
        parquet, csv = recompute.data_folder(bundle, pilot.folder / pilot.kit.reference, Path(name))
        assert recompute.run_one(bundle, age, parquet, csv, outputs, tmp_path / "logs") is None
    lsm = outputs / "efficacy-adas" / "An_ADAS_W24_LSM.csv"
    lines = lsm.read_text(encoding="ascii").splitlines()
    lsm.write_text("\n".join(lines[:-1]) + "\n", encoding="ascii")  # a lost row
    n = outputs / "efficacy-adas" / "An_EFF_N.csv"
    n.write_text(n.read_text(encoding="ascii") + 'Mth_Count_1_n,Grp_None,"1"\n',
                 encoding="ascii")  # an extra row
    pw = outputs / "efficacy-adas" / "An_ADAS_W24_PwPbo.csv"
    head, first, *rest = pw.read_text(encoding="ascii").splitlines()
    value = float(first.rsplit(",", 1)[1].strip('"'))
    pw.write_text("\n".join([head, f"{first.rsplit(',', 1)[0]},{value * (1 + 1e-8)!r}", *rest])
                  + "\n", encoding="ascii")  # a value off by a relative 1e-8
    found = statuses(recompute.compare(bundle, outputs, bundle / "ard", tmp_path / "r.json"))
    differs = sorted(k for k, v in found.items() if v == "differs")
    print(f"\nplanted in the scripts' outputs: {', '.join(differs)} differ")
    assert set(differs) == {"common-safety-displays/An03_01_Age_Summ_ByTrt",
                            "efficacy-adas/An_ADAS_W24_LSM", "efficacy-adas/An_EFF_N",
                            "efficacy-adas/An_ADAS_W24_PwPbo"}


# The cases the gate issue-29 requires, by their IDs (gates.RECOMPUTE_TESTS).
CASES = {
    "RC1-unplanted": unplanted,
    "RC2-weights": plant_ancova_weights,
    "RC3-quantiles": plant_quantiles,
    "RC4-cmh": plant_cmh,
    "RC5-checks": checker_plants,
    "RC6-comparison": comparison_plants,
}


@pytest.mark.parametrize("case", sorted(CASES))
def test_recompute(pilot: Pilot, case: str, tmp_path, monkeypatch) -> None:
    CASES[case](pilot, tmp_path, monkeypatch)
