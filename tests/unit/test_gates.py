"""The gate runner: it passes only when every check passes, and never by skipping."""

from __future__ import annotations

import textwrap

from specfirst import gates
from specfirst.gates import Check, junit_problems, run_gate


def gate(root, checks):
    lines: list[str] = []
    code = run_gate(root, "demo", tuple(checks), echo=lines.append)
    return code, "\n".join(lines)


def passing(ctx):
    ctx.out("all good")
    return True


def failing(ctx):
    ctx.out("something is wrong")
    return False


def crashing(ctx):
    raise RuntimeError("boom")


def test_gate_passes_when_every_check_passes(repo):
    code, text = gate(repo, [Check("one", "cmd one", passing), Check("two", "cmd two", passing)])
    assert code == 0
    assert "== [1/2] one: cmd one" in text
    assert text.endswith("GATE demo: PASS")
    log = (repo / "build" / "gates" / "demo" / "gate.log").read_text(encoding="utf-8")
    assert log.rstrip("\n") == text


def test_one_failing_check_fails_the_gate_and_the_rest_still_run(repo):
    code, text = gate(repo, [Check("one", "cmd", failing), Check("two", "cmd", passing)])
    assert code == 1
    assert "-- FAIL one" in text and "-- PASS two" in text
    assert text.endswith("GATE demo: FAIL")


def test_crashing_check_is_a_failing_check(repo):
    code, text = gate(repo, [Check("one", "cmd", crashing)])
    assert code == 1 and "RuntimeError: boom" in text


def test_gate_names_the_commit(repo, git):
    code, text = gate(repo, [Check("one", "cmd", passing)])
    assert git(repo, "rev-parse", "HEAD") in text.splitlines()[0]


def test_clean_flag_fails_on_uncommitted_changes(repo):
    checks = (Check("one", "cmd", passing),)
    lines: list[str] = []
    assert run_gate(repo, "demo", checks, echo=lines.append, require_clean=True) == 0
    assert "(clean)" in lines[0]

    (repo / "README.md").write_bytes(b"edited after the commit\n")
    lines = []
    assert run_gate(repo, "demo", checks, echo=lines.append, require_clean=True) == 1
    assert "(with uncommitted changes)" in lines[0]
    assert lines[-1] == "GATE demo: FAIL"
    assert not any(line.startswith("== ") for line in lines)  # no check ran

    lines = []
    assert run_gate(repo, "demo", checks, echo=lines.append) == 0  # no flag: it only says so
    assert "(with uncommitted changes)" in lines[0]


def test_unknown_work_package(repo):
    lines: list[str] = []
    assert run_gate(repo, "no-such-wp", echo=lines.append) == 2
    assert "no gate is defined" in lines[0]


def test_base0_gate_has_the_checks_of_the_plan():
    names = [check.name for check in gates.GATES["base-0"]]
    for needed in ("environment", "pins", "evidence tests", "R packages", "ASCII"):
        assert needed in names
    assert names[0] == "environment"  # drift is checked first (rule R3)


def test_real1_gate_has_the_checks_of_the_plan():
    names = [check.name for check in gates.GATES["real-1"]]
    assert names[0] == "environment"
    for needed in ("pins", "unit tests", "kit", "P1 determinism", "P2 reproduction", "trace",
                   "pilot tests", "ASCII"):
        assert needed in names
    # P2 and the trace check the first of the two builds that P1 made.
    assert names.index("P1 determinism") < names.index("P2 reproduction") < names.index("trace")
    # The cache is verified before it is used and again after everything that reads it.
    assert names.index("pins") < names.index("kit") < names.index("pilot tests")
    assert names.index("pilot tests") < names.index("cache untouched")
    assert gates.PILOT_P2 == "TOTAL cells=9119605 mismatched=0"  # E1


def test_real2_gate_has_the_checks_of_the_plan(root, tmp_path):
    """PLAN.md section 13.3: both engines, their agreement, P1, planted defects."""
    names = [check.name for check in gates.GATES["real-2"]]
    assert names[0] == "environment"
    # Everything the gate of real-1 checks is checked again.
    assert set(names) >= {check.name for check in gates.GATES["real-1"]}
    for needed in ("registry", "method vectors", "results", "planted defects"):
        assert needed in names
    # The results are those of the first of the two builds that P1 made.
    assert names.index("P1 determinism") < names.index("results") < names.index("planted defects")
    assert names.index("planted defects") < names.index("cache untouched")
    assert (gates.PILOT_EMBEDDED, gates.PILOT_REPRODUCED) == (3735, 3711)  # E2
    assert set(gates.REAL2_DEFECTS) == {"D1-arms", "D2-set", "D3-quantile", "D4-subset",
                                        "D5-engines"}

    # The results check fails when an engine is missing or reproduces too few.
    from specfirst.machine import build

    def counts(python, r=None):
        found = [{"set": "x", "engine": "Python", "total": 3735, "reproduced": python,
                  "not_reproduced": 3735 - python, "explained": True}]
        if r is not None:
            found.append({**found[0], "engine": "R", "reproduced": r})
        return found

    said: list[str] = []
    ctx = gates.Context(tmp_path, "demo", said.append)
    try:
        for given, expected in ((counts(3711, 3711), True), (counts(3711), False),
                                (counts(3711, 3710), False), (counts(3735, 3735), True)):
            build_checks = build.result_checks
            build.result_checks = lambda *args, given=given, **kwargs: (True, given)
            try:
                assert gates._results(ctx) is expected, given
            finally:
                build.result_checks = build_checks
    finally:
        ctx.close()
    assert any("expected the engines Python and R, found ['Python']" in line for line in said)
    assert any("the R engine reproduces 3710 of 3735" in line for line in said)


def test_std1_gate_has_the_checks_of_the_plan():
    """PLAN.md section 13.4: round trip, yamaa check, ARS schema, public sources."""
    names = [check.name for check in gates.GATES["std-1"]]
    for needed in ("round trip", "yamaa check", "ARS schema", "public sources",
                   "catalog", "house standard", "unit tests", "ASCII"):
        assert needed in names
    assert names[0] == "environment"  # drift is checked first (rule R3)
    assert names.index("pins") < names.index("public sources")  # the cache is verified first


def junit(tmp_path, body: str):
    path = tmp_path / "report.xml"
    path.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n<testsuites><testsuite name="pytest">\n'
        + textwrap.dedent(body)
        + "</testsuite></testsuites>\n",
        encoding="utf-8",
    )
    return path


PASSED = """
<testcase classname="tests.evidence.test_evidence" name="test_evidence[E1]" time="1.0" />
<testcase classname="tests.evidence.test_evidence" name="test_evidence[E24]" time="1.0" />
"""


def test_junit_all_required_passed(tmp_path):
    assert junit_problems(junit(tmp_path, PASSED), ("E1", "E24")) == []


def test_junit_skipped_test_is_a_problem(tmp_path):
    body = PASSED.replace(
        'name="test_evidence[E24]" time="1.0" />',
        'name="test_evidence[E24]" time="0.0"><skipped message="no cache" /></testcase>',
    )
    assert junit_problems(junit(tmp_path, body), ("E1", "E24")) == ["test_evidence[E24]: skipped"]


def test_junit_failed_test_is_a_problem(tmp_path):
    body = PASSED.replace(
        'name="test_evidence[E1]" time="1.0" />',
        'name="test_evidence[E1]" time="1.0"><failure message="mismatch" /></testcase>',
    )
    assert junit_problems(junit(tmp_path, body), ("E1", "E24")) == ["test_evidence[E1]: failure"]


def test_junit_required_test_that_did_not_run_is_a_problem(tmp_path):
    problems = junit_problems(junit(tmp_path, PASSED), ("E1", "E24", "E26"))
    assert problems == ["required test [E26] did not run"]


def test_junit_missing_report_is_a_problem(tmp_path):
    assert junit_problems(tmp_path / "absent.xml", ("E1",)) != []
