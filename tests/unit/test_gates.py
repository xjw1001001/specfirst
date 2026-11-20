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
        found = [{"set": gates.PILOT_EXAMPLE, "engine": "Python", "total": 3735,
                  "reproduced": python, "not_reproduced": 3735 - python, "explained": True}]
        if r is not None:
            found.append({**found[0], "engine": "R", "reproduced": r})
        # Another result set of the kit (real-5a: our own event, nothing embedded) is
        # judged by result_checks, not counted against E2.
        found.append({**found[0], "set": "efficacy-adas", "total": 0, "reproduced": 0})
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


def test_real3a_gate_has_the_checks_of_adr_005(root, tmp_path, monkeypatch):
    """ADR-005, part real-3a: the gate of real-2, the grid text, the trace of the cells, P1."""
    checks = gates.GATES["real-3a"]
    names = [check.name for check in checks]
    assert names[0] == "environment"
    # Everything the gate of real-2 checks is checked again, by the same functions.
    before = {check.name: check.run for check in gates.GATES["real-2"]}
    after = {check.name: check.run for check in checks}
    assert set(after) == {*before, "grids"}
    assert all(after[name] is run for name, run in before.items() if name != "planted defects")
    assert names.index("P1 determinism") < names.index("trace") < names.index("grids")
    assert names.index("grids") < names.index("planted defects") < names.index("cache untouched")
    assert set(gates.REAL3A_DEFECTS) == {*gates.REAL2_DEFECTS, "D6-proofs", "D7-display",
                                         "D8-trace"}
    assert gates.PILOT_GRIDS == {"Out14-3-1-1": (27, 51)}

    # The check of the grids fails on anything but: the outputs the gate names, their
    # cells and results, and every cell equal or with one classified difference.
    from specfirst.machine import build

    def count(**changed):
        return {"set": gates.PILOT_EXAMPLE, "output": "Out14-3-1-1", "cells": 27,
                "results": 51, "equal": 27, "differing": 0, "classified": 0,
                "no_reference": 0, "problems": 0, **changed}

    said: list[str] = []
    ctx = gates.Context(tmp_path, "demo", said.append)
    try:
        for given, passes, expected in (
            ([count()], True, True),
            ([count(equal=25, differing=2, classified=2)], True, True),
            ([count()], False, False),  # the check of the build itself failed
            ([count(equal=26, differing=1)], True, False),  # a difference with no class
            ([count(cells=24, results=48, equal=24)], True, False),  # a row is missing
            ([count(equal=26, no_reference=1)], True, False),
            ([], True, False),
            ([count(), count(output="Out14-1-1")], True, False),  # an output it does not know
            ([count(), count(set="efficacy-adas", output="Out14-3-01")], True, True),  # real-5a
        ):
            monkeypatch.setattr(build, "display_checks",
                                lambda *args, g=given, p=passes, **kwargs: (p, g))
            assert gates._grids(ctx) is expected, given
    finally:
        ctx.close()
    assert any("The gate asks for 27 cells that show 51 results" in line for line in said)
    assert any("the kit builds [], the gate asks for ['Out14-3-1-1']" in line for line in said)


def test_real5a_gate_has_the_checks_of_adr_012(tmp_path, monkeypatch):
    """ADR-012, part real-5a: the gate of real-3a, the CSR tables, the decisions."""
    checks = gates.GATES["real-5a"]
    names = [check.name for check in checks]
    assert names[0] == "environment"
    before = {check.name: check.run for check in gates.GATES["real-3a"]}
    after = {check.name: check.run for check in checks}
    assert set(after) == {*before, "efficacy", "decisions"}
    changed = {"method vectors", "planted defects"}  # with the tests of real-5a required
    assert all(after[name] is run for name, run in before.items() if name not in changed)
    assert names.index("P1 determinism") < names.index("trace") < names.index("efficacy")
    assert names.index("efficacy") < names.index("planted defects") < names.index(
        "cache untouched")
    assert set(gates.REAL5A_DEFECTS) == {*gates.REAL3A_DEFECTS, "D9-efficacy",
                                         "D10-trace-model"}
    assert "model-vectors" in gates.REAL5A_METHOD_TESTS
    assert set(gates.EFFICACY_GRIDS) == {"Out14-3-01", "Out14-3-03", "Out14-3-05"}

    from specfirst.machine import build

    def count(output: str, **changed) -> dict:
        return {"set": gates.EFFICACY_SET, "output": output, "reference": "csr",
                "cells": 51, "printed": 40, "equal": 48, "differing": 3, "classified": 3,
                "classes": {"rule_choice": 3}, "problems": 0, **changed}

    every = [count(name) for name in sorted(gates.EFFICACY_GRIDS)]
    said: list[str] = []
    ctx = gates.Context(tmp_path, "demo", said.append)
    try:
        for given, passes, expected in (
            (every, True, True),
            (every, False, False),  # the check of the build itself failed
            ([*every[:2], count("Out14-3-05", classified=2)], True, False),  # one with no class
            ([*every[:2], count("Out14-3-05", problems=1)], True, False),
            ([*every[:2], count("Out14-3-05", cells=48, equal=45)], True, False),  # a row less
            ([*every[:2], count("Out14-3-05", printed=39)], True, False),
            ([*every[:2], count("Out14-3-05", reference="ars")], True, False),
            (every[:2], True, False),  # a table missing
            # A table of another part (real-5b) is judged by display_checks and counted by
            # the gate of its part, not by this one.
            ([*every, count("Out14-3-11")], True, True),
        ):
            monkeypatch.setattr(build, "display_checks",
                                lambda *args, g=given, p=passes, **kwargs: (p, g))
            assert gates._efficacy(ctx) is expected, given
    finally:
        ctx.close()
    assert any("classified differences: 9 rule_choice" in line for line in said)
    assert any("The gate asks for 51 cells against CSR Table 14-3.05" in line for line in said)


def test_real5b_gate_has_the_checks_of_adr_012(tmp_path, monkeypatch):
    """ADR-012, part real-5b: the gate of real-5a for its two tables, E22 and CMH."""
    names = [check.name for check in gates.GATES["real-5b"]]
    before = {check.name: check.run for check in gates.GATES["real-5a"]}
    after = {check.name: check.run for check in gates.GATES["real-5b"]}
    assert set(after) == {*before, "E22 hint", "CMH"} - {"grids"}
    changed = {"efficacy", "planted defects"}
    assert all(after[name] is run for name, run in before.items()
               if name not in changed and name in after)
    assert names.index("efficacy") < names.index("E22 hint") < names.index("planted defects")
    assert set(gates.REAL5B_DEFECTS) == {*gates.REAL5A_DEFECTS, "D11-efficacy-5b",
                                         "D12-cmh-engines"}
    assert set(gates.REAL5B_GRIDS) == {"Out14-3-11", "Out14-3-13"}
    assert gates.REAL5B_GRIDS["Out14-3-13"][0] == "efficacy-cibic"

    from specfirst.machine import build

    said: list[str] = []
    ctx = gates.Context(tmp_path, "demo", said.append)
    # The E22 hint: of the 24 cells of 14-3.11, 9 are empty and 3 are the header's counts;
    # the 12 others differ at Week 24, each with a proof from the averaged analyses.
    table = {"set": gates.EFFICACY_SET, "output": "Out14-3-11", "reference": "csr",
             "cells": 24, "printed": 15, "equal": 12, "differing": 12, "classified": 12,
             "classes": {"rule_choice": 12}, "problems": 0}
    averaged = [{"cell": f"cell:Out14-3-11/r{n}/c3", "proof": {
        "kind": "other_build", "analyses": {"An_X": "An_X_Avg"}}} for n in range(12)]
    monkeypatch.setattr("specfirst.machine.csr.load_exceptions",
                        lambda path, a=averaged: {"Out14-3-11": a})
    try:
        for given, entries, expected in (
            (table, averaged, True),
            (dict(table, equal=13, differing=11, classified=11), averaged[:11], False),
            (table, averaged[:11], False),
            (table, [dict(e, proof={"kind": "other_pattern"}) for e in averaged], False),
        ):
            monkeypatch.setattr(build, "display_checks",
                                lambda *args, g=given, **kwargs: (True, [g]))
            monkeypatch.setattr("specfirst.machine.csr.load_exceptions",
                                lambda path, a=entries: {"Out14-3-11": a})
            assert gates._e22_hint(ctx) is expected, (given, len(entries))
    finally:
        ctx.close()
    assert any("the hint holds" in line for line in said)


def test_the_cmh_check_of_real5b_sees_a_disagreement(tmp_path):
    """The gate check `CMH` (rule R11) on ARD files of its own, with planted defects
    (review of real-5b, F2): a value moved, a row left out, a missing value."""
    import json

    folder = tmp_path / "build" / "p1" / gates.PILOT / "first" / "gold" / "ard"
    folder.mkdir(parents=True)

    def row(week: str, value) -> dict:
        return {"id": f"ard:An_CIBIC_{week}_Cmh/Mth_Cmh_1_pval/*", "method_id": "test.cmh",
                "raw_value": value}

    python = [row("W08", 0.2727284040371243), row("W16", 0.40031471449145817),
              row("W24", 0.6180439310104722),
              {"id": "ard:An_CIBIC_W08_N/Mth_Count_1_n/Grp_Pbo", "method_id": "count.subjects",
               "raw_value": 77}]

    def check(r_rows: list[dict]) -> bool:
        for name, rows in (("efficacy-cibic.jsonl", python), ("efficacy-cibic.r.jsonl", r_rows)):
            (folder / name).write_text("".join(json.dumps(r) + "\n" for r in rows),
                                       encoding="ascii")
        ctx = gates.Context(tmp_path, "demo", lambda line: None)
        try:
            return gates._cmh_engines(ctx)
        finally:
            ctx.close()

    assert check(python) is True
    assert check([dict(r, raw_value=r["raw_value"] * (1 + 5e-10)) for r in python]) is True
    assert check([dict(r, raw_value=r["raw_value"] * (1 + 2e-9)) if "W16" in r["id"] else r
                  for r in python]) is False
    assert check([r for r in python if "W24" not in r["id"]]) is False
    assert check([dict(r, raw_value=None) if "W08" in r["id"] else r for r in python]) is False


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
