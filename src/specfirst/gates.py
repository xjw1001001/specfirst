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
from specfirst.paths import build_dir

# The evidence tests the base-0 gate must see pass (PLAN.md section 13.2).
BASE0_EVIDENCE = ("E1", "E2-E3", "E4", "E24", "E25-csr", "E25-single", "E26", "E27")


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


GATES: dict[str, tuple[Check, ...]] = {
    "base-0": (
        Check("pins", "specfirst fetch --verify", _pins),
        Check("lint", "ruff check .", _lint),
        Check("unit tests", 'pytest -m "not evidence" -q', _unit_tests),
        Check("evidence tests", "SPECFIRST_STRICT=1 pytest tests/evidence -m evidence -s -q",
              _evidence),
        Check("R packages", "Rscript --vanilla env/check_r.R $(cat env/r-packages.txt)",
              _r_packages),
        Check("ASCII", "python -m specfirst.asciicheck", _ascii),
    ),
}


def _head(root: Path) -> str:
    def git(*args: str) -> str:
        done = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
        return done.stdout.strip() if done.returncode == 0 else "unknown"

    state = "clean" if git("status", "--porcelain") == "" else "with uncommitted changes"
    return f"{git('rev-parse', 'HEAD')} ({state})"


def run_gate(
    root: Path,
    wp: str,
    checks: tuple[Check, ...] | None = None,
    echo: Callable[[str], None] = print,
) -> int:
    checks = GATES.get(wp) if checks is None else checks
    if checks is None:
        echo(f"no gate is defined for '{wp}' yet; defined: {', '.join(sorted(GATES))}")
        return 2
    ctx = Context(root, wp, echo)
    try:
        ctx.out(f"gate {wp} at commit {_head(root)}")
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
