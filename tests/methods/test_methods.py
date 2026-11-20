"""The method vectors against both implementations and against exact arithmetic.

    python-vectors    every case of every vector file through specfirst.machine.methods
    r-vectors         the same cases through r/specfirstr (needs Rscript)
    exact-arithmetic  the expected values of the files, computed again by oracle.py
    fisher-r          the Fisher exact test on tables larger than 2 x 2: both
                      implementations against R's own fisher.test, case by
                      case (E27), and against exact fractions where
                      fisher.test is looser than statement 5
    fisher-limit      the R implementation refuses more tables than its limit

Numbers must agree within a relative 1e-12, well inside the 1e-9 of rule R11.
The mixed model for repeated measures is the exception: its expected values
come from a second optimization (oracle_mmrm), and the two maxima of the
restricted likelihood agree to about 1e-8; there the tolerance is 1e-6.
A test that needs R is skipped where R is not installed, except under
SPECFIRST_STRICT=1 (set by the gate), where it fails: a gate never passes by
skipping.
"""

from __future__ import annotations

import json
import os
from fractions import Fraction
from pathlib import Path

import oracle
import pytest

from specfirst.machine import methods, registry, rengine
from specfirst.paths import repo_root

TOLERANCE = 1e-12
# model.mmrm.*: two optimizations of the restricted likelihood (oracle_mmrm, mmrm).
MMRM_TOLERANCE = 1e-6
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
    if method == "test.cmh":
        return {"p_value": methods.cmh_p(given["strata"], given.get("values"), **options)}
    if method == "display.round.half_away_from_zero":
        return {"text": methods.round_half_away(given["value"], given["decimals"])}
    if method == "display.round.half_even":
        return {"text": methods.round_half_even(given["value"], given["decimals"])}
    if method == "display.pattern":
        return {"text": methods.pattern_text(given["value"], given["pattern"],
                                             mock=given.get("mock", False), **options)}
    if method == "display.pattern.signed":
        return {"text": methods.pattern_text(given["value"], given["pattern"], zero_sign="kept",
                                             **options)}
    raise AssertionError(f"no Python implementation of {method}")


def differences(expected: dict, found: dict, tolerance: float = TOLERANCE) -> list[str]:
    """What differs. A model-based method gives one value per group: a mapping."""
    problems = []
    if set(expected) != set(found):
        return [f"operations {sorted(found)} for {sorted(expected)}"]
    for name, want in expected.items():
        got = found[name]
        if isinstance(want, dict) or isinstance(got, dict):
            if not isinstance(want, dict) or not isinstance(got, dict):
                problems.append(f"{name}: {got!r}, expected {want!r}")
            else:
                problems += [f"{name}, {problem}"
                             for problem in differences(want, got, tolerance)]
            continue
        if want is None or got is None or isinstance(want, str):
            if want != got:
                problems.append(f"{name}: {got!r}, expected {want!r}")
        elif abs(got - want) > tolerance * max(abs(got), abs(want)):
            problems.append(f"{name}: {got!r}, expected {want!r}")
    return problems


def need_r() -> None:
    if not rengine.available():
        if os.environ.get("SPECFIRST_STRICT") == "1":
            pytest.fail("Rscript is not installed")
        pytest.skip("Rscript is not installed")


def python_vectors(tmp_path) -> list[str]:
    problems, count = [], 0
    known = registry.load(ROOT).methods
    for file in vector_files():
        if "python" not in known[file["method"]].implementations:
            continue  # a model-based method is R only (section 7.3)
        for case in file["cases"]:
            count += 1
            problems += [f"{file['method']}, {case['name']}: {problem}" for problem in
                         differences(case["expected"], python_result(file["method"], case))]
    print(f"Python implementations: {count} cases of "
          f"{sum('python' in m.implementations for m in known.values())} methods, "
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
                         differences(case["expected"], found[(file["method"], index)],
                                     model_tolerance(file["method"]))]
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
            tolerance = 1e-9 if file["method"].startswith("model.mmrm.") else TOLERANCE
            problems += [f"{file['method']}, {case['name']}: the file says {problem}"
                         for problem in differences(expected, case["expected"], tolerance)]
    print(f"expected values computed again in exact arithmetic: {covered} cases, {len(problems)} "
          f"differences; written by hand: {by_hand} cases (the display rules)")
    return problems


MODEL_METHODS = ("model.ancova.lsmeans", "model.ancova.pairwise", "model.ancova.dose_response",
                 "model.mmrm.lsmeans", "model.mmrm.pairwise")


def model_tolerance(method: str) -> float:
    return MMRM_TOLERANCE if method.startswith("model.mmrm.") else TOLERANCE


def model_vectors(tmp_path) -> list[str]:
    """The model-based methods (R only): every vector, and every option seen to matter.

    The expected values come from oracle_models (exact fractions and the
    closed form of the t distribution) and oracle_mmrm (a restricted
    likelihood maximized in numpy), which share nothing with the R
    implementation. A vector file whose cases leave an option at one value
    proves nothing about it; and what an implementation that ignored an
    option would compute (the LS means always with equal weights, the
    comparisons always with residual degrees of freedom, the dose always by
    its rank, the LS means of the mixed model always at the last visit, its
    comparisons always with the Kenward-Roger standard errors), planted by
    fixing the option in the inputs, not in the R code, must be seen by the
    vectors (rule R5).
    """
    need_r()
    files = [file for file in vector_files() if file["method"] in MODEL_METHODS]
    if [file["method"] for file in files] != sorted(MODEL_METHODS):
        return [f"vector files of the model-based methods: {[f['method'] for f in files]}"]
    problems, count = [], 0
    found = rengine.run_vectors(ROOT, tmp_path / "honest", files)
    for file in files:
        for index, case in enumerate(file["cases"]):
            count += 1
            problems += [f"{file['method']}, {case['name']}: {problem}" for problem in
                         differences(case["expected"], found[(file["method"], index)],
                                     model_tolerance(file["method"]))]
    known = registry.load(ROOT).methods
    for file in files:
        for name, option in known[file["method"]].options.items():
            if "values" not in option:
                continue
            used = {json.dumps((case.get("options") or {}).get(name, option["default"]))
                    for case in file["cases"]}
            if len(used) != len(option["values"]):
                problems.append(f"{file['method']}: the vectors give option {name} "
                                f"{len(used)} of its {len(option['values'])} values")
    print(f"model-based methods in R: {count} cases of {len(files)} methods, {len(problems)} "
          "differences")
    planted = {"model.ancova.lsmeans": ("weights", "equal"),
               "model.ancova.pairwise": ("df", "residual"),
               "model.ancova.dose_response": ("dose", "group_rank"),
               "model.mmrm.lsmeans": ("at", "last"),
               "model.mmrm.pairwise": ("df", "kenward_roger_linear")}
    for file in files:
        option, fixed = planted[file["method"]]
        changed = [dict(case, options={**(case.get("options") or {}), option: fixed})
                   for case in file["cases"]]
        wrong = rengine.run_vectors(ROOT, tmp_path / f"planted-{option}",
                                    [dict(file, cases=changed)])
        seen = sum(bool(differences(case["expected"], wrong[(file["method"], index)],
                                    model_tolerance(file["method"])))
                   for index, case in enumerate(file["cases"]))
        print(f"planted: {file['method']} always with {option} = {fixed}: {seen} cases differ")
        if not seen:
            problems.append(f"{file['method']}: the vectors do not see option {option} "
                            f"fixed at {fixed}")
    return problems


def fisher_r(tmp_path) -> list[str]:
    """Tables larger than 2 x 2: our sums against R's fisher.test (E27).

    fisher.test is R's own function here, not the R implementation of the
    registry. The two must agree, except where a table with the same margins
    is more probable than the observed one by a relative 1e-7 to 1e-6: by
    statement 5 it does not count, and fisher.test counts it (statement 8).
    There the registry implementations must give the sum in exact fractions,
    and fisher.test must be seen to differ, or statement 8 says too much.
    """
    need_r()
    with open(ROOT / "tests/methods/test_fisher_exact.json", encoding="ascii") as handle:
        file = json.load(handle)
    larger = [case for case in file["cases"]
              if len(case["input"]["table"]) > 2 or len(case["input"]["table"][0]) > 2]
    assert len(larger) >= 8
    theirs = rengine.run_vectors(ROOT, tmp_path / "fisher.test",
                                 [{"method": "stats::fisher.test", "cases": larger}])
    in_r = rengine.run_vectors(ROOT, tmp_path / "registry",
                               [{"method": file["method"], "cases": larger}])
    problems, looser = [], 0
    for index, case in enumerate(larger):
        table = case["input"]["table"]
        ours = methods.fisher_exact_p(table)
        ours_in_r = in_r[(file["method"], index)]["p_value"]
        r_own = theirs[("stats::fisher.test", index)]["p_value"]
        above = oracle.fisher_just_above(table, Fraction(1, 10**7), Fraction(1, 10**6))
        print(f"{len(table)} x {len(table[0])} {case['name'][:55]:55s} Python {ours!r:22} R "
              f"{ours_in_r!r:22} fisher.test {r_own!r}"
              + (f"  (a table {above[0]:.3e} more probable)" if above else ""))
        problems += [f"{case['name']}: Python against R: {problem}"
                     for problem in differences({"p_value": ours_in_r}, {"p_value": ours})]
        if not above:
            problems += [f"{case['name']}: against fisher.test: {problem}"
                         for problem in differences({"p_value": r_own}, {"p_value": ours})]
            continue
        looser += 1
        exact = oracle.fisher_exact_p(table)
        problems += [f"{case['name']}: against exact fractions: {problem}"
                     for problem in differences({"p_value": exact}, {"p_value": ours})]
        if ours is None or r_own is None or abs(r_own - ours) <= 1e-9 * ours:
            problems.append(f"{case['name']}: fisher.test gives {r_own!r}, the sum of statement "
                            f"5 is {ours!r}: statement 8 says they differ")
    print(f"tables larger than 2 x 2: {len(larger)}; with a table just above the observed "
          f"probability, where fisher.test is looser: {looser}")
    if looser < 2:
        problems.append("no vector shows what statement 8 says of fisher.test")
    return problems


def fisher_limit(tmp_path) -> list[str]:
    """Statement 6 in R: more tables than the limit are refused, not approximated."""
    need_r()
    table = [[3, 1, 2], [4, 0, 5], [1, 2, 6]]
    case = {"name": "limit", "input": {"table": table}}
    found = rengine.run_vectors(ROOT, tmp_path / "under", [
        {"method": "test.fisher.exact", "cases": [case]}])
    problems = differences({"p_value": methods.fisher_exact_p(table)},
                           found[("test.fisher.exact", 0)])
    try:
        rengine.run_vectors(ROOT, tmp_path / "over", [{"method": "test.fisher.exact", "cases": [
            {"name": "limit", "input": {"table": table, "max_tables": 50}}]}])
    except rengine.REngineError as error:
        said = [line for line in str(error).splitlines() if "tables to sum" in line]
        print(f"R, with a limit of 50 tables: {said[0] if said else error}")
        if "more than 50 tables to sum" not in str(error):
            problems.append(f"the R implementation fails for another reason: {error}")
    else:
        problems.append("the R implementation sums more tables than its limit")
    return problems


CASES = {"python-vectors": python_vectors, "r-vectors": r_vectors,
         "exact-arithmetic": exact_arithmetic, "fisher-r": fisher_r,
         "fisher-limit": fisher_limit, "model-vectors": model_vectors}


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
