"""`specfirst gate <wp>`: one command decides whether a work package is done.

A gate is a list of checks (PLAN.md section 13). It exits 0 only when every
check passes. Everything it prints also goes to build/gates/<wp>/gate.log,
which the report of the work package quotes (rule R8).
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from specfirst import asciicheck, doctor, fetch
from specfirst.compile import gate as std1
from specfirst.paths import build_dir, git_env

# The evidence tests the base-0 gate must see pass (PLAN.md section 13.2).
BASE0_EVIDENCE = ("E1", "E2-E3", "E4", "E24", "E25-csr", "E25-single", "E26", "E27")

# real-1 (PLAN.md section 13.3): the kit of the pilot study, the line P2 must
# print for it (E1), and the tests behind ADR-001.
PILOT = "cdiscpilot01"
PILOT_P2 = "TOTAL cells=9119605 mismatched=0"
REAL1_PILOT_TESTS = ("A1-resolve", "A2-runner", "A3-lineage", "A4-unread", "A5-adapted")


class Context:
    def __init__(self, root: Path, wp: str, echo: Callable[[str], None] = print):
        self.root = root
        self.wp = wp
        self.log_dir = build_dir(root) / "gates" / wp
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log = open(self.log_dir / "gate.log", "w", encoding="utf-8", newline="\n")
        self._echo = echo

    def out(self, line: str = "") -> None:
        self._echo(line)
        self._log.write(line + "\n")
        self._log.flush()

    def command(self, argv: list[str], env: dict[str, str] | None = None) -> int:
        """Run a command in the checkout; its output goes to the gate output."""
        merged = dict(os.environ, PYTHONUNBUFFERED="1", **(env or {}))
        process = subprocess.Popen(
            argv,
            cwd=self.root,
            env=merged,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout is not None
        for line in process.stdout:
            self.out(line.rstrip("\n"))
        return process.wait()

    def close(self) -> None:
        self._log.close()


@dataclass(frozen=True)
class Check:
    name: str
    shows: str  # what a person would type to run the same check
    run: Callable[[Context], bool]


def junit_problems(xml_path: Path, required: tuple[str, ...]) -> list[str]:
    """Why a pytest JUnit report does not prove that the required tests passed.

    A skipped test is a problem: a gate never passes by skipping.
    """
    if not xml_path.is_file():
        return [f"no test report at {xml_path}"]
    outcome: dict[str, str] = {}
    for case in ET.parse(xml_path).getroot().iter("testcase"):
        bad = [child.tag for child in case if child.tag in ("failure", "error", "skipped")]
        outcome[case.get("name", "")] = bad[0] if bad else "passed"
    problems = [f"{name}: {state}" for name, state in sorted(outcome.items()) if state != "passed"]
    for test_id in required:
        if not any(name.endswith(f"[{test_id}]") for name in outcome):
            problems.append(f"required test [{test_id}] did not run")
    return problems


def _environment(ctx: Context) -> bool:
    """Drift first (rule R3): the environment is the one the lock files describe."""
    return doctor.run(ctx.root, ctx.out) == 0


def _pins(ctx: Context) -> bool:
    return fetch.run(ctx.root, verify_only=True, out=ctx.out) == 0


def _lint(ctx: Context) -> bool:
    return ctx.command([sys.executable, "-m", "ruff", "check", "."]) == 0


def _unit_tests(ctx: Context) -> bool:
    return ctx.command([sys.executable, "-m", "pytest", "-m", "not evidence", "-q"]) == 0


def _evidence(ctx: Context) -> bool:
    report = ctx.log_dir / "evidence.xml"
    report.unlink(missing_ok=True)
    code = ctx.command(
        [sys.executable, "-m", "pytest", "tests/evidence", "-m", "evidence", "-s", "-q",
         f"--junitxml={report}"],
        env={"SPECFIRST_STRICT": "1"},
    )
    problems = junit_problems(report, BASE0_EVIDENCE)
    for problem in problems:
        ctx.out(f"evidence: {problem}")
    return code == 0 and not problems


def _r_packages(ctx: Context) -> bool:
    return doctor.load_r_packages(ctx.root, ctx.out)


def _ascii(ctx: Context) -> bool:
    return asciicheck.check(ctx.root, ctx.out) == 0


def _root_check(run: Callable[[Path, Callable[[str], None]], bool]) -> Callable[[Context], bool]:
    """A check that takes the checkout and a line printer."""
    return lambda ctx: run(ctx.root, ctx.out)


def _kit(ctx: Context) -> bool:
    """The pilot kit assembles from the cache at its pinned hashes; git holds no study data."""
    from specfirst import kit

    names = asciicheck.maintained_files(ctx.root)
    problems = kit.tracked_data_problems(ctx.root, names)
    for problem in problems:
        ctx.out(f"study data in git: {problem}")
    ctx.out(f"study data in git (E20): {len(names)} maintained files checked, "
            f"{len(problems)} problems")
    return kit.run_assemble(ctx.root, PILOT, ctx.out) == 0 and not problems


def _first_build(ctx: Context) -> Path:
    return build_dir(ctx.root) / "p1" / PILOT / "first"


def _p1(ctx: Context) -> bool:
    from specfirst.machine import build

    return build.determinism(ctx.root, PILOT, ctx.out)


def _p2(ctx: Context) -> bool:
    from specfirst.machine import build

    lines: list[str] = []

    def out(line: str) -> None:
        lines.append(line)
        ctx.out(line)

    passed = build.reproduction(ctx.root, PILOT, _first_build(ctx), out)
    if PILOT_P2 not in lines:
        ctx.out(f"P2: expected the line '{PILOT_P2}' (E1)")
        return False
    return passed


def _trace(ctx: Context) -> bool:
    from specfirst.machine import build

    return build.trace(ctx.root, PILOT, _first_build(ctx), ctx.out)


def _pilot_tests(ctx: Context) -> bool:
    report = ctx.log_dir / "pilot.xml"
    report.unlink(missing_ok=True)
    code = ctx.command(
        [sys.executable, "-m", "pytest", "tests/pilot", "-m", "evidence", "-s", "-q",
         f"--junitxml={report}"],
        env={"SPECFIRST_STRICT": "1"},
    )
    problems = junit_problems(report, REAL1_PILOT_TESTS)
    for problem in problems:
        ctx.out(f"pilot tests: {problem}")
    return code == 0 and not problems


# real-2 (PLAN.md section 13.3): the results the ARS example embeds, how many of
# them both engines must reproduce (E2), and the tests the gate must see pass.
PILOT_EXAMPLE = "common-safety-displays"  # the result set of the ARS example in kit.yaml
PILOT_EMBEDDED, PILOT_REPRODUCED = 3735, 3711
REAL2_PILOT_TESTS = (*REAL1_PILOT_TESTS, "A6-engine")
REAL2_METHOD_TESTS = ("python-vectors", "r-vectors", "exact-arithmetic", "fisher-r")
REAL2_DEFECTS = ("D1-arms", "D2-set", "D3-quantile", "D4-subset", "D5-engines")


def _registry(ctx: Context) -> bool:
    from specfirst.machine import registry

    return registry.run(ctx.root, out=ctx.out) == 0


def _pytest(ctx: Context, folder: str, report: str, required: tuple[str, ...]) -> bool:
    """Run the tests of a folder strictly: none may fail, be skipped or be missing."""
    xml = ctx.log_dir / report
    xml.unlink(missing_ok=True)
    code = ctx.command(
        [sys.executable, "-m", "pytest", folder, "-s", "-q", f"--junitxml={xml}"],
        env={"SPECFIRST_STRICT": "1"},
    )
    problems = junit_problems(xml, required)
    for problem in problems:
        ctx.out(f"{folder}: {problem}")
    return code == 0 and not problems


def _method_vectors(ctx: Context) -> bool:
    return _pytest(ctx, "tests/methods", "methods.xml", REAL2_METHOD_TESTS)


def _pilot_tests_2(ctx: Context) -> bool:
    return _pytest(ctx, "tests/pilot", "pilot.xml", REAL2_PILOT_TESTS)


def _defects(ctx: Context) -> bool:
    return _pytest(ctx, "tests/defects", "defects.xml", REAL2_DEFECTS)


def _results(ctx: Context) -> bool:
    """Both engines reproduce the embedded results, with nothing unexplained, and agree."""
    from specfirst.machine import build

    passed, counts = build.result_checks(ctx.root, PILOT, _first_build(ctx), ctx.out)
    # The counts of E2 are those of the ARS example; the kit's other result sets
    # (real-5a: our own event, which embeds nothing) are checked by result_checks too.
    counts = [count for count in counts if count["set"] == PILOT_EXAMPLE]
    engines = {count["engine"] for count in counts}
    if engines != {"Python", "R"}:
        ctx.out(f"results: expected the engines Python and R, found {sorted(engines)}")
        return False
    for count in counts:
        if count["total"] != PILOT_EMBEDDED or count["reproduced"] < PILOT_REPRODUCED:
            ctx.out(f"results: the {count['engine']} engine reproduces {count['reproduced']} of "
                    f"{count['total']}; the gate asks for at least {PILOT_REPRODUCED} of "
                    f"{PILOT_EMBEDDED} (E2)")
            passed = False
    return passed


def _gen(name: str) -> Callable[[Context], bool]:
    """A check of the generator (specfirst.gen.gate), by its function name."""
    def run(ctx: Context) -> bool:
        from specfirst.gen import gate

        return getattr(gate, name)(ctx.root, ctx.out)
    return run


def _gen2(name: str) -> Callable[[Context], bool]:
    """A check of the kits of generated studies (specfirst.gen.gate2), by its function name."""
    def run(ctx: Context) -> bool:
        from specfirst.gen import gate2

        return getattr(gate2, name)(ctx.root, ctx.out)
    return run


def _gen3(name: str) -> Callable[[Context], bool]:
    """A check of the documents of generated kits (specfirst.gen.gate3), by its function name."""
    def run(ctx: Context) -> bool:
        from specfirst.gen import gate3

        return getattr(gate3, name)(ctx.root, ctx.out)
    return run


# real-3a (ADR-005, decision 1): the outputs of the ARS example that are built as
# grids, each with its cells and the results they show; and the planted defects of
# the display and of its trace. The rest of real-3 adds the other four outputs here.
PILOT_GRIDS = {"Out14-3-1-1": (27, 51)}
REAL3A_DEFECTS = (*REAL2_DEFECTS, "D6-proofs", "D7-display", "D8-trace")


def _grids(ctx: Context) -> bool:
    """Every cell text is the reference's formatted value, or its difference has one class."""
    from specfirst.machine import build

    passed, counts = build.display_checks(ctx.root, PILOT, _first_build(ctx), ctx.out)
    # The outputs of the ARS example; the efficacy tables of real-5a are judged by
    # display_checks too, and counted by the gate real-5a.
    found = {count["output"]: count for count in counts if count["set"] == PILOT_EXAMPLE}
    if set(found) != set(PILOT_GRIDS):
        ctx.out(f"grids: the kit builds {sorted(found)}, the gate asks for {sorted(PILOT_GRIDS)}")
        return False
    for output, (cells, results) in PILOT_GRIDS.items():
        count = found[output]
        if (count["cells"], count["results"], count["no_reference"]) != (cells, results, 0) or (
                count["equal"] + count["classified"] != cells):
            ctx.out(f"grids: {output}: {count['cells']} cells show {count['results']} results; "
                    f"{count['equal']} equal the reference, {count['classified']} differ with "
                    f"one class, {count['no_reference']} results have no formatted value in "
                    f"the reference. The gate asks for {cells} cells that show {results} "
                    "results, each cell equal or with one classified difference")
            passed = False
    return passed


def _defects_3a(ctx: Context) -> bool:
    return _pytest(ctx, "tests/defects", "defects.xml", REAL3A_DEFECTS)


# real-5a (ADR-012, ADR-015): the three efficacy tables of the part, each with its
# result set, its CSR table, its cells and the cells the CSR prints in; the classes of
# their differences are counted, not fixed (the owner reviews them at N2). real-5b adds
# two tables; each gate counts its own (the others are judged by display_checks too).
EFFICACY_SET = "efficacy-adas"
EFFICACY_GRIDS = {"Out14-3-01": (EFFICACY_SET, "14-3.01", 51, 40),
                  "Out14-3-03": (EFFICACY_SET, "14-3.03", 51, 40),
                  "Out14-3-05": (EFFICACY_SET, "14-3.05", 51, 40)}
REAL5A_METHOD_TESTS = (*REAL2_METHOD_TESTS, "model-vectors")
REAL5A_DEFECTS = (*REAL3A_DEFECTS, "D9-efficacy", "D10-trace-model")
# real-5b (ADR-012, amendment of real-5b to ADR-015): Table 14-3.11, the mixed model for
# repeated measures, and Table 14-3.13, CIBIC+ with the CMH test.
REAL5B_GRIDS = {"Out14-3-11": (EFFICACY_SET, "14-3.11", 24, 15),
                "Out14-3-13": ("efficacy-cibic", "14-3.13", 100, 78)}
REAL5B_DEFECTS = (*REAL5A_DEFECTS, "D11-efficacy-5b", "D12-cmh-engines")


def _efficacy_of(grids: dict[str, tuple[str, str, int, int]]) -> Callable[[Context], bool]:
    """Every printed cell of the tables equals the CSR, or has exactly one class with a
    proof that holds."""
    def check(ctx: Context) -> bool:
        from specfirst.machine import build

        passed, counts = build.display_checks(ctx.root, PILOT, _first_build(ctx), ctx.out)
        found = {count["output"]: count for count in counts
                 if count["output"] in grids and count["set"] == grids[count["output"]][0]}
        if set(found) != set(grids):
            ctx.out(f"efficacy: the kit builds {sorted(found)} of the tables the gate asks "
                    f"for, {sorted(grids)}")
            return False
        classes: dict[str, int] = {}
        for output, count in sorted(found.items()):
            _, table, cells, printed = grids[output]
            if count.get("reference") != "csr" or (count["cells"], count["printed"]) != (
                    cells, printed) or count["problems"] or (
                    count["equal"] + count["classified"] != count["cells"]):
                ctx.out(f"efficacy: {output}: {count}. The gate asks for {cells} cells against "
                        f"CSR Table {table}, {printed} of them printed, each equal or with one "
                        "classified difference, and no problem")
                passed = False
            for name, number in count["classes"].items():
                classes[name] = classes.get(name, 0) + number
        ctx.out(f"efficacy: {len(found)} tables, {sum(c['cells'] for c in found.values())} "
                f"cells; {sum(c['equal'] for c in found.values())} equal the CSR; classified "
                "differences: " + (", ".join(f"{number} {name}" for name, number
                                             in sorted(classes.items())) or "none"))
        return passed
    return check


_efficacy = _efficacy_of(EFFICACY_GRIDS)
_efficacy_5b = _efficacy_of(REAL5B_GRIDS)


def _e22_hint(ctx: Context) -> bool:
    """Evidence E22: the LS means of Table 14-3.11 are averages over the weeks.

    Gold takes them at Week 24, as the SAP says (custom:eff-mmrm-visit). The hint
    holds when no printed number of the table follows from Week 24 and every one
    follows from the average: each of its differing cells has an other_build
    proof that holds and names the averaged analyses.
    """
    from specfirst.machine import build, csr

    passed, counts = build.display_checks(ctx.root, PILOT, _first_build(ctx), lambda line: None)
    count = next((c for c in counts if c["output"] == "Out14-3-11"), None)
    entries = csr.load_exceptions(ctx.root / "kits" / PILOT / "gold" / "exceptions.yaml").get(
        "Out14-3-11", [])
    averaged = [entry for entry in entries if entry["proof"].get("kind") == "other_build"
                and all(str(other).endswith("_Avg")
                        for other in (entry["proof"].get("analyses") or {"": ""}).values())]
    if count is None:
        ctx.out("E22: Table 14-3.11 is not built")
        return False
    body = count["printed"] - 3  # the three counts of the header are no model result
    # Cells the CSR leaves empty are empty in the grid too: they count as equal.
    equal = count["equal"] - (count["cells"] - count["printed"]) - 3
    ctx.out(f"E22: Table 14-3.11 prints {body} numbers of the model; at Week 24 {equal} of "
            f"them equal the CSR; averaged over weeks 8, 16 and 24, {len(averaged)} cells give "
            f"the CSR's text (other_build proofs that hold: {count['classified']} of "
            f"{count['cells'] - count['equal']} differing cells)")
    holds = passed and equal == 0 and len(averaged) == body and count["classified"] == body
    ctx.out("E22: the LS means of Table 14-3.11 are averages over the weeks: "
            + ("the hint holds" if holds else "not shown"))
    return holds


def _cmh_engines(ctx: Context) -> bool:
    """Rule R11 for the CMH test: the R engine's results are the Python engine's."""
    from specfirst.machine.canonical import read_jsonl

    folder = _first_build(ctx) / "gold" / "ard"
    found: dict[str, dict[str, object]] = {}
    for engine, suffix in (("Python", ""), ("R", ".r")):
        path = folder / f"efficacy-cibic{suffix}.jsonl"
        if not path.is_file():
            ctx.out(f"CMH: no ARD of the {engine} engine at {path}")
            return False
        found[engine] = {row["id"]: row["raw_value"] for row in read_jsonl(path)
                         if row["method_id"] == "test.cmh"}
    python, r = found["Python"], found["R"]
    worst = 0.0
    problems = []
    if set(python) != set(r) or len(python) != 3:
        problems.append(f"the engines give {sorted(python)} and {sorted(r)}; three p-values "
                        "are asked for, one per week")
    for key in sorted(set(python) & set(r)):
        a, b = python[key], r[key]
        if not isinstance(a, float) or not isinstance(b, float):
            problems.append(f"{key}: {a!r} and {b!r}")
            continue
        worst = max(worst, abs(a - b) / max(abs(a), abs(b)))
        ctx.out(f"CMH: {key}: Python {a!r}, R {b!r}")
    if worst > 1e-9:
        problems.append(f"the largest relative difference is {worst:.1e} (allowed 1e-09)")
    ctx.out(f"CMH: {len(python)} results in both engines; largest relative difference "
            f"{worst:.1e} (allowed 1e-09)" + "".join(f"; {p}" for p in problems))
    return not problems


def _decisions(ctx: Context) -> bool:
    from specfirst.machine import build

    return build.decision_checks(ctx.root, PILOT, _first_build(ctx), ctx.out)


def _method_vectors_5a(ctx: Context) -> bool:
    return _pytest(ctx, "tests/methods", "methods.xml", REAL5A_METHOD_TESTS)


def _defects_5a(ctx: Context) -> bool:
    return _pytest(ctx, "tests/defects", "defects.xml", REAL5A_DEFECTS)


def _defects_5b(ctx: Context) -> bool:
    return _pytest(ctx, "tests/defects", "defects.xml", REAL5B_DEFECTS)


def _score(name: str) -> Callable[[Context], bool]:
    """A check of the scorer (specfirst.score.gate), by its function name."""
    def run(ctx: Context) -> bool:
        from specfirst.score import gate

        return getattr(gate, name)(ctx.root, ctx.out)
    return run


# read-1a: the test of the scorer on the pilot that the gate must see pass.
READ1A_PILOT_TESTS = ("P1-arm-s",)


def _score_pilot_tests(ctx: Context) -> bool:
    return _pytest(ctx, "tests/score", "score.xml", READ1A_PILOT_TESTS)


def _harness(name: str) -> Callable[[Context], bool]:
    """A check of the reader harness (specfirst.harness.gate), by its function name."""
    def run(ctx: Context) -> bool:
        from specfirst.harness import gate

        return getattr(gate, name)(ctx.root, ctx.out)
    return run


_REAL1_CHECK = f"specfirst check {PILOT} --build build/p1/{PILOT}/first"

GATES: dict[str, tuple[Check, ...]] = {
    "base-0": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("evidence tests", "SPECFIRST_STRICT=1 pytest tests/evidence -m evidence -s -q",
              _evidence),
        Check("R packages", "Rscript --vanilla env/check_r.R $(cat env/r-packages.txt)",
              _r_packages),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    "real-1": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("kit", f"specfirst kit assemble {PILOT}", _kit),
        Check("P1 determinism", f"specfirst check {PILOT} --twice (its first part)", _p1),
        Check("P2 reproduction", f"{_REAL1_CHECK} (its first part)", _p2),
        Check("trace", f"{_REAL1_CHECK} (its second part)", _trace),
        Check("pilot tests", "SPECFIRST_STRICT=1 pytest tests/pilot -m evidence -s -q",
              _pilot_tests),
        # The checks above read the fetch cache; it must still be what was fetched.
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    "real-2": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("registry", "specfirst methods", _registry),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("method vectors", "SPECFIRST_STRICT=1 pytest tests/methods -s -q", _method_vectors),
        Check("kit", f"specfirst kit assemble {PILOT}", _kit),
        Check("P1 determinism", f"specfirst check {PILOT} --twice (its first part)", _p1),
        Check("P2 reproduction", f"{_REAL1_CHECK} (its second part)", _p2),
        Check("trace", f"{_REAL1_CHECK} (its third part)", _trace),
        Check("results", f"{_REAL1_CHECK} (its last part)", _results),
        Check("pilot tests", "SPECFIRST_STRICT=1 pytest tests/pilot -s -q", _pilot_tests_2),
        Check("planted defects", "SPECFIRST_STRICT=1 pytest tests/defects -s -q", _defects),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # ADR-005, part real-3a: everything the gate of real-2 checks; every cell text of
    # the adverse event summary equals the example's formattedValue or has one
    # classified difference (grids); every numeric cell has a complete path to SDTM
    # variables (trace, which walks the cells since real-3a); the build is
    # deterministic (P1, which covers the grids, the shells, the pages and the graph).
    "real-3a": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("registry", "specfirst methods", _registry),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("method vectors", "SPECFIRST_STRICT=1 pytest tests/methods -s -q", _method_vectors),
        Check("kit", f"specfirst kit assemble {PILOT}", _kit),
        Check("P1 determinism", f"specfirst check {PILOT} --twice (its first part)", _p1),
        Check("P2 reproduction", f"{_REAL1_CHECK} (its second part)", _p2),
        Check("trace", f"{_REAL1_CHECK} (its third part)", _trace),
        Check("results", f"{_REAL1_CHECK} (its fourth part)", _results),
        Check("grids", f"{_REAL1_CHECK} (its last part)", _grids),
        Check("pilot tests", "SPECFIRST_STRICT=1 pytest tests/pilot -s -q", _pilot_tests_2),
        Check("planted defects", "SPECFIRST_STRICT=1 pytest tests/defects -s -q", _defects_3a),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # ADR-012, part real-5a of the slice efficacy-first (ADR-015): everything the gate
    # of real-3a checks; the registry entries of ANCOVA, its pairwise comparisons and
    # its dose-response test with their vectors, computed again another way (method
    # vectors, model-vectors); every printed cell of Tables 14-3.01, 14-3.03 and
    # 14-3.05 equals the CSR, parsed again from its pages, or has exactly one class
    # with a proof (efficacy); the decision records hold against the reporting event
    # (decisions); every cell has a complete trace (trace); the build is
    # deterministic (P1); each check has planted defects (method vectors, D9, D10).
    "real-5a": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("registry", "specfirst methods", _registry),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("method vectors", "SPECFIRST_STRICT=1 pytest tests/methods -s -q",
              _method_vectors_5a),
        Check("kit", f"specfirst kit assemble {PILOT}", _kit),
        Check("P1 determinism", f"specfirst check {PILOT} --twice (its first part)", _p1),
        Check("P2 reproduction", f"{_REAL1_CHECK} (its second part)", _p2),
        Check("trace", f"{_REAL1_CHECK} (its third part)", _trace),
        Check("results", f"{_REAL1_CHECK} (its fourth part)", _results),
        Check("grids", f"{_REAL1_CHECK} (its last part), the ARS example", _grids),
        Check("efficacy", f"{_REAL1_CHECK} (its last part), the CSR tables", _efficacy),
        Check("decisions", f"specfirst.machine.build.decision_checks on build/p1/{PILOT}/first",
              _decisions),
        Check("pilot tests", "SPECFIRST_STRICT=1 pytest tests/pilot -s -q", _pilot_tests_2),
        Check("planted defects", "SPECFIRST_STRICT=1 pytest tests/defects -s -q", _defects_5a),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # ADR-012, part real-5b of the slice efficacy-first (ADR-015 and its amendment of
    # real-5b): everything the gate of real-5a checks, for Tables 14-3.11 and 14-3.13;
    # the registry entries of the mixed model and of CMH with their vectors, computed
    # again another way (method vectors); every printed cell of the two tables equals
    # the CSR or has exactly one class with a proof (efficacy); the hint of E22 on the
    # LS means of 14-3.11 is tested (E22 hint); the two engines agree on CMH (CMH,
    # rule R11); each check has planted defects (D11, D12).
    "real-5b": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("registry", "specfirst methods", _registry),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("method vectors", "SPECFIRST_STRICT=1 pytest tests/methods -s -q",
              _method_vectors_5a),
        Check("kit", f"specfirst kit assemble {PILOT}", _kit),
        Check("P1 determinism", f"specfirst check {PILOT} --twice (its first part)", _p1),
        Check("P2 reproduction", f"{_REAL1_CHECK} (its second part)", _p2),
        Check("trace", f"{_REAL1_CHECK} (its third part)", _trace),
        Check("results", f"{_REAL1_CHECK} (its fourth part)", _results),
        Check("efficacy", f"{_REAL1_CHECK} (its last part), CSR Tables 14-3.11 and 14-3.13",
              _efficacy_5b),
        Check("E22 hint", "the LS means of 14-3.11 against the CSR, at Week 24 and averaged",
              _e22_hint),
        Check("CMH", f"the test.cmh rows of build/p1/{PILOT}/first, Python against R",
              _cmh_engines),
        Check("decisions", f"specfirst.machine.build.decision_checks on build/p1/{PILOT}/first",
              _decisions),
        Check("pilot tests", "SPECFIRST_STRICT=1 pytest tests/pilot -s -q", _pilot_tests_2),
        Check("planted defects", "SPECFIRST_STRICT=1 pytest tests/defects -s -q", _defects_5b),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # PLAN.md section 13.4: the round trip is exact for every alternative;
    # compiled fragments pass yamaa check and the ARS schema; every entry has
    # at least one public source.
    "std-1": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("catalog", "specfirst catalog", _root_check(std1.catalog_check)),
        Check("public sources", "specfirst catalog --sources", _root_check(std1.sources_check)),
        Check("round trip", "specfirst catalog --roundtrip", _root_check(std1.roundtrip_check)),
        Check("yamaa check", "specfirst catalog --yamaa", _root_check(std1.yamaa_check)),
        Check("yamaa run", "specfirst catalog --run", _root_check(std1.run_check)),
        Check("ARS schema", "specfirst catalog --tables", _root_check(std1.tables_check)),
        Check("house standard", "specfirst house", _root_check(std1.house_check)),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # PLAN.md section 13.5 and ADR-005: the gate of gen-1 for the datasets and
    # the decisions of the slice. The environment check covers CDISC CORE.
    "gen-1a": (
        Check("environment", "specfirst doctor", _environment),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("identical hashes", "specfirst.gen.gate.determinism: 10 seeds, generated twice",
              _gen("determinism")),
        Check("CDISC CORE", "specfirst.gen.gate.core: visible and twin of the 10 seeds",
              _gen("core")),
        Check("controlled terms", "specfirst.gen.gate.controlled_terms: values against "
              "the CT package of CORE", _gen("controlled_terms")),
        Check("probes", "specfirst.gen.gate.probe_coverage: every pair of alternatives",
              _gen("probe_coverage")),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # PLAN.md section 13.5 and ADR-005: the gate of gen-2 for the one output of the
    # slice: 10 kits pass P1 to P4, every applicable decision is separated on the twin,
    # the engines agree. gen-2a added a rounding rule to the method registry and two
    # words to the column lineage of the machine: the registry, the method vectors and
    # the tests of the pilot kit are checked with it.
    "gen-2a": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("registry", "specfirst methods", _registry),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("method vectors", "SPECFIRST_STRICT=1 pytest tests/methods -s -q", _method_vectors),
        Check("pilot tests", "SPECFIRST_STRICT=1 pytest tests/pilot -s -q", _pilot_tests_2),
        Check("kits", "specfirst.gen.gate2.kits_pass: 10 kits, each written twice; P1 to P4",
              _gen2("kits_pass")),
        Check("separation", "specfirst.gen.gate2.separation: every applicable decision, and "
              "the matrix of the 10 kits", _gen2("separation")),
        Check("engines", "specfirst.gen.gate2.engines: the Python and the R engine on every "
              "result", _gen2("engines")),
        Check("splits", "specfirst.gen.gate2.splits: the splits of section 6.7", _gen2("splits")),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # ADR-005, part read-1a (PLAN.md section 13.6, read-1 for the slice): the planted
    # defects of section 9.5 that apply to the slice are each detected and attributed
    # to the right layer; the parser control scores 100%. First on a hand-made study
    # and on the pilot (report only), then on the kits of the gate of gen-2a, which the
    # check `kits of gen-2a` writes again from the seed of that gate: on every kit the
    # gold built again is the gold of the kit, the control scores 100% in both stages,
    # no planted defect fails and the sweep of its matrix has no problem; every defect
    # is detected and attributed on at least one kit.
    "read-1a": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("hand-made study", "specfirst.score.gate.hand_table: HAND01 against the table "
              "worked out by hand", _score("hand_table")),
        Check("separation", "specfirst.score.gate.separated: every other value of every "
              "decision, alone on gold", _score("separated")),
        Check("parser control", "specfirst score hand --arm C (both stages)", _score("control")),
        Check("standard alone", "specfirst score hand --arm S (both stages)", _score("arms")),
        Check("planted defects", "specfirst score defects", _score("planted_defects")),
        Check("pilot", "specfirst score pilot (report only)", _score("pilot_report")),
        Check("pilot tests", "SPECFIRST_STRICT=1 pytest tests/score -s -q", _score_pilot_tests),
        Check("kits of gen-2a", "specfirst.score.gate.kits: the 10 kits of the seed of the "
              "gate gen-2a, written again; then specfirst score kits", _score("kits")),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # ADR-005, part gen-3a (PLAN.md section 13.5, gen-3 for the slice; ADR-009): the
    # parser recovers 100% of the decisions from every standard-form document; every
    # natural document passes the slot check and the read-back check; a planted bad
    # rewrite (a changed number) is rejected; each kit records which probes are visible.
    # The tiers, the anchors and the summary pages are checked with them. No model is
    # called: the natural form comes from the store in src/specfirst/gen/rewrites.
    "gen-3a": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("kits", "specfirst.gen.gate3.kits_written: the 10 kits of the seed of the gate "
              "gen-2a, each by a process of its own; the tiers of their documents",
              _gen3("kits_written")),
        Check("parser", "specfirst.gen.gate3.parser: 100% of the decisions from the "
              "standard-form documents (with the house standard and the oracle)",
              _gen3("parser")),
        Check("slots", "specfirst.gen.gate3.slots: every decision paragraph of the natural "
              "form", _gen3("slots")),
        Check("read-back", "specfirst.gen.gate3.readback: the verifier's pick for the text of "
              "every paragraph", _gen3("readback")),
        Check("bad rewrite", "specfirst.gen.gate3.bad_rewrite: a changed number is rejected",
              _gen3("bad_rewrite")),
        Check("tiers", "specfirst.gen.gate3.tiers: full, standard, the ask demo and the oracle",
              _gen3("tiers")),
        Check("anchors", "specfirst.gen.gate3.anchors: every citation stands at its anchor",
              _gen3("anchors")),
        Check("visible probes", "specfirst.gen.gate3.visible_probes: listed in kit.yaml and "
              "found in the visible data", _gen3("visible_probes")),
        Check("summary", "specfirst.gen.gate3.summaries: one page per kit", _gen3("summaries")),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
    # ADR-005, part read-2a (PLAN.md section 13.6, read-2 for the slice;
    # docs/decisions/ADR-010.md): a dry run of each arm on one train kit ends within
    # budget with valid output files; the canary scan is clean. The train kit is kit 4
    # of the seed of the gate gen-2a. No check calls a model: the dry run of arm R made
    # with the model is kept in src/specfirst/harness/kept and checked from its record.
    "read-2a": (
        Check("environment", "specfirst doctor", _environment),
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("kit", "specfirst.harness.gate.kit: kit 4 of the seed of the gate gen-2a, "
              "written again; its gold built again", _harness("kit")),
        Check("skills", "specfirst run skills: core-reader and the reading notes v0 of "
              "the four units; the leak check", _harness("skills")),
        Check("task", "specfirst run task: the task folder of the kit, twice; stage T",
              _harness("task")),
        Check("oracle", "specfirst ask: every decision of the task, and an entry the "
              "catalog lacks", _harness("oracle_check")),
        Check("adapter", "specfirst.harness.adapter: the command line and the deny rules",
              _harness("adapter_check")),
        Check("budget", "specfirst.harness.record: a run record against its budget",
              _harness("budget")),
        Check("output files", "specfirst run validate: the rules of ADR-010, decision 6",
              _harness("outputs_check")),
        Check("canary scan", "specfirst.harness.canary: the canaries of each protected "
              "kind", _harness("canary_check")),
        Check("arm S", "specfirst run arm KIT --arm S --score", _harness("arm_s")),
        Check("arm C", "specfirst run arm KIT --arm C --score", _harness("arm_c")),
        Check("arm R, stub reader", "specfirst run arm KIT --arm R --stub PLAN --score; "
              "the run kept and checked", _harness("arm_r_stub")),
        Check("arm R, kept dry run", "specfirst run check src/specfirst/harness/kept/R-... "
              "--kit KIT --score", _harness("arm_r")),
        Check("scratch removed", "the kit, tasks and runs of the gate", _harness("done")),
        Check("cache untouched", "specfirst fetch --verify", _pins),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
}


def head(root: Path) -> tuple[str, bool | None]:
    """The commit of the checkout, and whether its tree is clean (None: git could not tell)."""
    env = {**os.environ, **git_env(root)}

    def git(*args: str) -> str | None:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, env=env)
        return done.stdout.strip() if done.returncode == 0 else None

    commit = git("rev-parse", "HEAD")
    status = git("status", "--porcelain")
    return commit or "unknown", None if status is None else status == ""


def run_gate(
    root: Path,
    wp: str,
    checks: tuple[Check, ...] | None = None,
    echo: Callable[[str], None] = print,
    require_clean: bool = False,
) -> int:
    """Run the checks of a gate. With require_clean, uncommitted changes fail it."""
    checks = GATES.get(wp) if checks is None else checks
    if checks is None:
        echo(f"no gate is defined for '{wp}' yet; defined: {', '.join(sorted(GATES))}")
        return 2
    commit, clean = head(root)  # before the log folder appears in the tree
    state = {True: "clean", False: "with uncommitted changes", None: "state unknown"}[clean]
    ctx = Context(root, wp, echo)
    try:
        ctx.out(f"gate {wp} at commit {commit} ({state})")
        if require_clean and clean is not True:
            ctx.out("--clean: the gate counts only on a tree without uncommitted changes")
            ctx.out(f"GATE {wp}: FAIL")
            return 1
        if os.environ.get("SPECFIRST_REWRITES"):
            # The kits of a gate take their natural form from the store of the repository
            # (docs/decisions/ADR-009.md, decision 5); another store gives other kits.
            ctx.out("SPECFIRST_REWRITES is set: a gate writes and judges kits from the store "
                    "of the repository only; unset it")
            ctx.out(f"GATE {wp}: FAIL")
            return 1
        results: list[tuple[str, bool, float]] = []
        for number, check in enumerate(checks, start=1):
            ctx.out("")
            ctx.out(f"== [{number}/{len(checks)}] {check.name}: {check.shows}")
            started = time.monotonic()
            try:
                passed = bool(check.run(ctx))
            except Exception as error:  # a crashing check is a failing check
                ctx.out(f"{type(error).__name__}: {error}")
                passed = False
            seconds = time.monotonic() - started
            ctx.out(f"-- {'PASS' if passed else 'FAIL'} {check.name} ({seconds:.1f} s)")
            results.append((check.name, passed, seconds))
        ctx.out("")
        for name, passed, seconds in results:
            ctx.out(f"{'PASS' if passed else 'FAIL'}  {name:15s} {seconds:8.1f} s")
        ok = all(passed for _, passed, _ in results)
        ctx.out(f"GATE {wp}: {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    finally:
        ctx.close()
