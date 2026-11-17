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


# real-3a (ADR-005, decision 1): the outputs of the ARS example that are built as
# grids, each with its cells and the results they show; and the planted defects of
# the display and of its trace. The rest of real-3 adds the other four outputs here.
PILOT_GRIDS = {"Out14-3-1-1": (27, 51)}
REAL3A_DEFECTS = (*REAL2_DEFECTS, "D6-proofs", "D7-display", "D8-trace")


def _grids(ctx: Context) -> bool:
    """Every cell text is the reference's formatted value, or its difference has one class."""
    from specfirst.machine import build

    passed, counts = build.display_checks(ctx.root, PILOT, _first_build(ctx), ctx.out)
    found = {count["output"]: count for count in counts}
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
