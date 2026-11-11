"""The method vectors against both implementations and against exact arithmetic.

    python-vectors    every case of every vector file through specfirst.machine.methods
    r-vectors         the same cases through r/specfirstr (needs Rscript)
    exact-arithmetic  the expected values of the files, computed again by oracle.py
    fisher-r          the Fisher exact test on tables larger than 2 x 2: our
                      enumeration against R's fisher.test, case by case (E27)

Numbers must agree within a relative 1e-12, well inside the 1e-9 of rule R11.
A test that needs R is skipped where R is not installed, except under
SPECFIRST_STRICT=1 (set by the gate), where it fails: a gate never passes by
skipping.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import oracle
import pytest

from specfirst.machine import methods, registry, rengine
from specfirst.paths import repo_root

TOLERANCE = 1e-12
ROOT = repo_root(Path(__file__).resolve().parent)


def vector_files() -> list[dict]:
    """Every vector file the registry names, in the order of the registry."""
    found = []
    for method in registry.load(ROOT).methods.values():
        with open(ROOT / method.vectors, encoding="ascii") as handle:
            data = json.load(handle)
        assert data["method"] == method.id, method.vectors
        found.append(data)
    return found


def python_result(method: str, case: dict) -> dict:
    given, options = case["input"], case.get("options") or {}
    if method == "count.subjects":
        return {"n": methods.count_subjects(given["values"])}
    if method == "percent.subjects":
        return {"pct": methods.percent(given["numerator"], given["denominator"])}
    if method == "summary.continuous":
        return methods.summary_continuous(given["values"], **options)
    if method == "test.chisq":
        return {"p_value": methods.chisq_p(given["table"])}
    if method == "test.anova.oneway":
        return {"p_value": methods.anova_oneway_p(given["groups"])}
    if method == "test.fisher.exact":
        return {"p_value": methods.fisher_exact_p(given["table"])}
    if method == "display.round.half_away_from_zero":
        return {"text": methods.round_half_away(given["value"], given["decimals"])}
    raise AssertionError(f"no Python implementation of {method}")


def differences(expected: dict, found: dict) -> list[str]:
    problems = []
    if set(expected) != set(found):
        return [f"operations {sorted(found)} for {sorted(expected)}"]
    for name, want in expected.items():
        got = found[name]
        if want is None or got is None or isinstance(want, str):
            if want != got:
                problems.append(f"{name}: {got!r}, expected {want!r}")
        elif abs(got - want) > TOLERANCE * max(abs(got), abs(want)):
            problems.append(f"{name}: {got!r}, expected {want!r}")
    return problems


def need_r() -> None:
    if not rengine.available():
        if os.environ.get("SPECFIRST_STRICT") == "1":
            pytest.fail("Rscript is not installed")
        pytest.skip("Rscript is not installed")


def python_vectors(tmp_path) -> list[str]:
    problems, count = [], 0
    for file in vector_files():
        for case in file["cases"]:
            count += 1
            problems += [f"{file['method']}, {case['name']}: {problem}" for problem in
                         differences(case["expected"], python_result(file["method"], case))]
    print(f"Python implementations: {count} cases of {len(vector_files())} methods, "
          f"{len(problems)} differences")
    return problems


def r_vectors(tmp_path) -> list[str]:
    need_r()
    known = registry.load(ROOT).methods
    files = [file for file in vector_files() if "r" in known[file["method"]].implementations]
    found = rengine.run_vectors(ROOT, tmp_path, files)
    problems, count = [], 0
    for file in files:
        for index, case in enumerate(file["cases"]):
            count += 1
            problems += [f"{file['method']}, {case['name']}: {problem}" for problem in
                         differences(case["expected"], found[(file["method"], index)])]
    print(f"R implementations: {count} cases of {len(files)} methods, {len(problems)} "
          "differences")
    return problems


def exact_arithmetic(tmp_path) -> list[str]:
    problems, covered, by_hand = [], 0, 0
    for file in vector_files():
        for case in file["cases"]:
            try:
                expected = oracle.expected(file["method"], case)
            except oracle.NotCovered:
                by_hand += 1
                continue
            covered += 1
            problems += [f"{file['method']}, {case['name']}: the file says {problem}"
                         for problem in differences(expected, case["expected"])]
    print(f"expected values computed again in exact arithmetic: {covered} cases, {len(problems)} "
          f"differences; written by hand: {by_hand} cases (the display rule)")
    return problems


def fisher_r(tmp_path) -> list[str]:
    """Tables larger than 2 x 2: our enumeration against R's fisher.test (E27)."""
    need_r()
    with open(ROOT / "tests/methods/test_fisher_exact.json", encoding="ascii") as handle:
        file = json.load(handle)
    larger = [case for case in file["cases"]
              if len(case["input"]["table"]) > 2 or len(case["input"]["table"][0]) > 2]
    assert len(larger) >= 6
    found = rengine.run_vectors(ROOT, tmp_path, [{"method": file["method"], "cases": larger}])
    problems = []
    for index, case in enumerate(larger):
        ours = methods.fisher_exact_p(case["input"]["table"])
        theirs = found[(file["method"], index)]["p_value"]
        rows, columns = len(case["input"]["table"]), len(case["input"]["table"][0])
        print(f"{rows} x {columns} {case['name']:55s} enumeration {ours!r:22} fisher.test "
              f"{theirs!r}")
        problems += [f"{case['name']}: {problem}"
                     for problem in differences({"p_value": theirs}, {"p_value": ours})]
    return problems


CASES = {"python-vectors": python_vectors, "r-vectors": r_vectors,
         "exact-arithmetic": exact_arithmetic, "fisher-r": fisher_r}


@pytest.mark.parametrize("case", list(CASES), ids=list(CASES))
def test_methods(case, tmp_path):
    print(f"\n--- {case}")
    problems = CASES[case](tmp_path)
    assert not problems, "\n".join(problems)


# Statements no vector can exercise, because they are about which results an
# analysis references, not about arithmetic. tests/unit/test_ard.py has them.
NOT_IN_VECTORS = {"percent.subjects": {2, 3}}


def test_every_operation_and_every_statement_has_a_vector():
    for file in vector_files():
        method = registry.load(ROOT).methods[file["method"]]
        seen = {name for case in file["cases"] for name in case["expected"]}
        assert seen == set(method.operations), file["method"]
        for case in file["cases"]:
            assert set(case) <= {"name", "statements", "input", "options", "expected", "source"}
            assert all(1 <= number <= len(method.semantics) for number in case["statements"])
        cited = {number for case in file["cases"] for number in case["statements"]}
        wanted = set(range(1, len(method.semantics) + 1)) - NOT_IN_VECTORS.get(method.id, set())
        assert cited >= wanted, (
            f"{file['method']}: no vector for statement {sorted(wanted - cited)}")
