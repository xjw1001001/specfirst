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


def test_unknown_work_package(repo):
    lines: list[str] = []
    assert run_gate(repo, "no-such-wp", echo=lines.append) == 2
    assert "no gate is defined" in lines[0]


def test_base0_gate_has_the_checks_of_the_plan():
    names = [check.name for check in gates.GATES["base-0"]]
    for needed in ("pins", "evidence tests", "R packages", "ASCII"):
        assert needed in names


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
