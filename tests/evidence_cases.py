"""The evidence spikes of PLAN.md section 3 as repeatable cases.

Each case runs scripts from evidence/ exactly as section 3.1 gives the
commands, on the fetch cache, and checks what they print. The spikes
themselves are not changed: they are the evidence. real-2 and real-4 replace
them with the real engines and parsers.

The checks are plain functions from the printed text to a list of problems,
so tests/unit/test_evidence_checks.py can plant wrong outputs and see them
rejected (rule R5).
"""

from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

PILOT_DATASETS = (
    "adsl", "adae", "adtte", "advs", "adlbc", "adlbh", "adlbhy", "adqsnipx", "adqsadas", "adqscibc",
)
ARS_EXAMPLE = "workfiles/examples/ARS v1/Common Safety Displays.json"


class EvidenceError(RuntimeError):
    """A spike could not be run. This is always a failure."""


class MissingPrerequisite(EvidenceError):
    """The fetch cache or a tool is not there. Outside a gate the test is skipped."""


@dataclass
class Env:
    """What a case may use: the checkout, the fetch cache and a scratch folder."""

    root: Path
    cache: Path
    work: Path
    _csr_txt: Path | None = field(default=None, repr=False)

    def need(self, *sources: str) -> None:
        missing = [name for name in sources if not (self.cache / name / ".git").exists()]
        if missing:
            names = ", ".join(missing)
            raise MissingPrerequisite(f"not in the fetch cache: {names}; run `specfirst fetch`")

    @property
    def adam(self) -> Path:
        return self.cache / "p7" / "cdiscpilot01" / "data" / "adam"

    def spike(self, script: str, *args: object, cwd: Path | None = None) -> str:
        """Run one evidence script and return what it printed."""
        argv = [sys.executable, str(self.root / "evidence" / script), *map(str, args)]
        done = subprocess.run(argv, cwd=cwd or self.work, capture_output=True, text=True)
        if done.returncode != 0:
            raise EvidenceError(f"{script} exited {done.returncode}:\n{done.stdout}\n{done.stderr}")
        return done.stdout

    def csr_txt(self) -> Path:
        """`pdftotext -layout CSR.pdf csr.txt`, made once per run."""
        if self._csr_txt is None:
            self.need("p6")
            if shutil.which("pdftotext") is None:
                raise MissingPrerequisite("pdftotext (poppler-utils) is not installed")
            target = self.work / "csr.txt"
            pdf = self.cache / "p6" / "documents" / "CSR.pdf"
            subprocess.run(["pdftotext", "-layout", str(pdf), str(target)], check=True)
            self._csr_txt = target
        return self._csr_txt


# ---- running --------------------------------------------------------------


def run_e1(env: Env) -> str:
    """Rebuild the 10 pilot ADaM datasets with yamaa, then compare cell by cell.

    The run step writes <dataset>-yamaa.parquet next to the reference data,
    so it works on a copy and leaves the cache clean.
    """
    env.need("p7")
    copy = env.work / "p7"
    if copy.exists():
        shutil.rmtree(copy)
    shutil.copytree(env.cache / "p7", copy, ignore=shutil.ignore_patterns(".git"))
    built = env.spike("run_yamaa_project.py", "cdiscpilot01/spec/yamaa/project.yaml", cwd=copy)
    adam = copy / "cdiscpilot01" / "data" / "adam"
    compared = env.spike("compare_adam.py", adam, *PILOT_DATASETS)
    return built + compared


def run_ars(quantile: str) -> Callable[[Env], str]:
    def run(env: Env) -> str:
        env.need("ars", "p7")
        return env.spike("ars_spike.py", env.cache / "ars" / ARS_EXAMPLE, env.adam, quantile)

    return run


def run_e24(env: Env) -> str:
    env.need("p6", "p7")
    return env.spike("csr_demog_spike.py", env.csr_txt(), env.adam / "adsl.parquet")


def run_e25(rule: str) -> Callable[[Env], str]:
    def run(env: Env) -> str:
        env.need("p6", "p7")
        return env.spike("csr_ae_spike.py", env.csr_txt(), env.adam, rule)

    return run


def run_e26(env: Env) -> str:
    env.need("p7")
    return env.spike("csr_hylaw_spike.py", env.adam)


def run_e27(env: Env) -> str:
    env.need("p6")
    return env.spike("csr_fisher_rxc_spike.py", env.csr_txt())


# ---- checking -------------------------------------------------------------


def _need_line(out: str, line: str) -> list[str]:
    return [] if line in out.splitlines() else [f"missing line: {line!r}"]


def check_e1(out: str) -> list[str]:
    """9,119,605 cells, 0 mismatches, all 10 datasets compared."""
    problems = _need_line(out, "TOTAL cells=9119605 mismatched=0 match=100.0000%")
    rows = [line for line in out.splitlines() if re.match(r"^AD[A-Z]+\s+rows=", line)]
    if len(rows) != len(PILOT_DATASETS):
        problems.append(f"expected {len(PILOT_DATASETS)} dataset lines, found {len(rows)}")
    for line in rows:
        if not re.search(r"mismatched=\s*0 type_diffs=", line):
            problems.append(f"dataset with mismatches: {line.strip()}")
    return problems


def check_ars(quantile: str, expected: dict[str, int]) -> Callable[[str], list[str]]:
    """The counts of matching, differing and not computed embedded results.

    Keys left out of `expected` are not compared, but the total is always
    3,735.
    """

    def check(out: str) -> list[str]:
        problems = _need_line(out, f"quantile definition: {quantile}")
        match = re.search(r"^embedded results: (\d+) (\{.*\})$", out, flags=re.MULTILINE)
        if not match:
            return [*problems, "missing line: 'embedded results: ...'"]
        total, counts = int(match.group(1)), ast.literal_eval(match.group(2))
        if total != 3735 or sum(counts.values()) != 3735:
            problems.append(f"expected 3735 embedded results, found {total} with {counts}")
        for key, value in expected.items():
            if counts.get(key, 0) != value:
                problems.append(f"expected {key}={value}, found {counts.get(key, 0)}")
        return problems

    return check


def check_e24(out: str) -> list[str]:
    expected = "CSR Table 14-2.01: printed cells parsed=244 reproduced=244 (100.0%)"
    problems = _need_line(out, expected)
    problems += [f"unexpected: {line.strip()}" for line in out.splitlines() if "differs:" in line]
    return problems


def check_e25(rule: str, reproduced: int) -> Callable[[str], list[str]]:
    def check(out: str) -> list[str]:
        percent = f"{100 * reproduced / 1175:.1f}"
        line = (f"p-value display rule={rule}: printed cells parsed=1175 "
                f"reproduced={reproduced} ({percent}%)")
        return _need_line(out, line)

    return check


E26_EXPECTED = (
    ("footnote", "reference", 38, 51, "0.405", "0.386"),
    ("worst_case", "reference", 45, 51, "0.405", "0.386"),
    ("worst_case", "last_predose", 51, 51, "0.392", "0.381"),
)


def check_e26(out: str) -> list[str]:
    pattern = re.compile(
        r"^shift=(\S+)\s+baseline=(\S+)\s+equal (\d+) of (\d+)\s+p-values (\S+) and (\S+)",
        flags=re.MULTILINE,
    )
    found = tuple((a, b, int(c), int(d), e, f) for a, b, c, d, e, f in pattern.findall(out))
    if found != E26_EXPECTED:
        return [f"expected {E26_EXPECTED}, found {found}"]
    return []


def check_e27(out: str) -> list[str]:
    return (_need_line(out, "3 x 3 reading (low, normal, high): equal 59 of 59")
            + _need_line(out, "3 x 2 reading (normal, abnormal):  equal 10 of 59"))


# ---- the cases ------------------------------------------------------------


@dataclass(frozen=True)
class Case:
    id: str
    shows: str
    run: Callable[[Env], str]
    check: Callable[[str], list[str]]


CASES = (
    Case("E1", "yamaa rebuilds the 10 pilot ADaM datasets: 9,119,605 cells, 0 mismatches",
         run_e1, check_e1),
    Case("E2-E3", "the ARS interpreter matches 3,711 of 3,735 results; 23 differ, 1 not computed",
         run_ars("sas5"), check_ars("sas5", {"match": 3711, "differ": 23, "not_computed": 1})),
    Case("E4", "with the R default quantile definition only 3,662 results match",
         run_ars("r7"), check_ars("r7", {"match": 3662})),
    Case("E24", "CSR Table 14-2.01: 244 of 244 printed cells", run_e24, check_e24),
    Case("E25-csr", "CSR Table 14-5.01 with the CSR's double rounding: 1,175 of 1,175",
         run_e25("csr"), check_e25("csr", 1175)),
    Case("E25-single", "CSR Table 14-5.01 with single rounding: 1,171 of 1,175",
         run_e25("single"), check_e25("single", 1171)),
    Case("E26", "CSR Table 14-6.06 under three pairs of rules: 38, 45 and 51 of 51",
         run_e26, check_e26),
    Case("E27", "CSR Tables 14-6.02 and 14-6.03: exact Fisher on 3 x 3 tables gives 59 of 59",
         run_e27, check_e27),
)
