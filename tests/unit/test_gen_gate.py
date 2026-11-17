"""The checks of the gate gen-1a, as far as they run without CDISC CORE.

The gate itself (`specfirst gate gen-1a`) runs CORE and plants its defects
in generated studies. Here the parts that decide are tested on planted
values (rule R5): the list of explained findings, the comparison of two
builds, the rule for seed files, the command line.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from specfirst import cdisccore, cli, gates
from specfirst.cdisccore import EXECUTION_ERROR, ISSUE, Finding
from specfirst.compile import catalog as catalogs
from specfirst.gen import GENERATOR, command, gate, pgfix, present, study
from specfirst.gen.rng import seed_sha256


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


def test_the_gate_has_the_checks_of_the_plan():
    """PLAN.md section 13.5: CORE, identical hashes, a probe for every pair; drift first."""
    names = [check.name for check in gates.GATES["gen-1a"]]
    assert names[0] == "environment"
    for needed in ("unit tests", "identical hashes", "CDISC CORE", "controlled terms", "probes",
                   "ASCII"):
        assert needed in names
    # The scratch folder of the checks is removed by the last of them.
    assert names.index("CDISC CORE") < names.index("controlled terms") < names.index("probes")
    assert len(gate.SEEDS) == 10 and len(set(gate.SEEDS)) == 10


# -- the list of explained findings ---------------------------------------------


def test_the_list_of_explained_findings_is_well_formed(root, catalog):
    explained = gate.load_explained()
    assert explained["core"] == cdisccore.read_pin(root).version
    assert explained["standard"] == gate.STANDARD
    entries = explained["explained"]
    ids = [entry["id"] for entry in entries]
    assert len(set(ids)) == len(ids)
    seen: set[str] = set()
    for entry in entries:
        assert entry["kind"] in ("cannot_run", "dataset", "every_record", "repeated_key",
                                 "study", "probe")
        assert len(entry["reason"]) > 40
        for rule in entry["rules"]:
            assert re.fullmatch(r"CORE-\d{6}", rule) and rule not in seen, rule
            seen.add(rule)
        assert (entry["kind"] == "cannot_run") == ("text" in entry)
        assert (entry["kind"] == "probe") == ("probes" in entry)
        assert (entry["kind"] == "repeated_key") == ("key" in entry)
        for probe in entry.get("probes", []):
            assert probe in catalog.probes and catalog.probes[probe]["kind"] == "record"


LOG = [
    {"data": "twin", "probe": "actual_arm_differs_from_planned", "subjects": ["S-9"]},
    {"data": "visible", "probe": "actual_arm_differs_from_planned", "subjects": ["S-7"]},
    {"data": "twin", "probe": "ae_starts_after_end_of_study", "subjects": ["S-4"]},
]
# In SV, three subjects: two with several visits (seven records), one with a single visit.
TABLES = {"AE": [{}] * 5, "EX": [{"USUBJID": "S-1"}, {"USUBJID": "S-2"}, {"USUBJID": "S-3"}],
          "SV": [{"USUBJID": s} for s in ("S-1",) * 3 + ("S-2",) * 4 + ("S-3",)],
          "DM": [{}] * 4, "TS": [{}] * 2}


def _report(*findings: Finding) -> cdisccore.Report:
    return cdisccore.Report(path=Path("report.json"), engine="1.0.0", standard="SDTMIG V3.4",
                            rules={f.rule: f.status for f in findings}, findings=findings,
                            datasets=("DM", "AE"))


def _unexplained(*findings: Finding, which: str = "twin") -> list[Finding]:
    return gate.classify(_report(*findings), gate.load_explained(), TABLES, LOG, which)[1]


def _broken(rule: str, text: str) -> Finding:
    return Finding(rule, "AE", "rule execution error", EXECUTION_ERROR, 1,
                   examples=({"values": text, "message": "rule execution error"},))


def test_an_engine_error_is_explained_only_with_its_error_text():
    assert _unexplained(_broken("CORE-002008", "Rule contains invalid operator")) == []
    # The same rule failing for another reason is a new finding.
    assert len(_unexplained(_broken("CORE-002008", "KeyError: 'AESTDTC'"))) == 1
    # A rule of that list that reports issues is not a rule that cannot run.
    assert len(_unexplained(Finding("CORE-002008", "AE", "x", ISSUE, 5))) == 1
    # A rule nobody listed.
    assert len(_unexplained(_broken("CORE-000001", "Rule contains invalid operator"))) == 1


def test_a_rule_that_reports_everything_must_report_everything():
    assert _unexplained(Finding("CORE-002034", "AE", "no flag", ISSUE, 5)) == []
    assert len(_unexplained(Finding("CORE-002034", "AE", "no flag", ISSUE, 4))) == 1
    # Without SVSEQ the rule reports the records of every subject with several visits:
    # seven of the eight here, of the subjects S-1 and S-2. Any other count is a finding
    # of its own.
    def visits(count, subjects=("S-1", "S-2"), **rows):
        rows = {"listed": count, "named": count, **rows}
        return Finding("CORE-000544", "SV", "SVSEQ", ISSUE, count, subjects, **rows)

    assert _unexplained(visits(7)) == []
    assert len(_unexplained(visits(8))) == 1
    assert len(_unexplained(visits(6))) == 1
    # Review finding F27: a finding of the right size that names other subjects, the one
    # with a single visit among them, is not this finding. Nor is one that names nobody,
    # or whose detail rows are fewer than its issues.
    assert len(_unexplained(visits(7, ("S-1", "S-3")))) == 1
    assert len(_unexplained(visits(7, ("S-1", "S-2", "S-3")))) == 1
    assert len(_unexplained(visits(7, ("S-1",)))) == 1
    assert len(_unexplained(visits(7, ()))) == 1
    assert len(_unexplained(visits(7, listed=3, named=3))) == 1
    assert len(_unexplained(Finding("CORE-000544", "SV", "SVSEQ", ISSUE, 7))) == 1
    # The same rule on a dataset that does have a sequence number is a real finding.
    assert len(_unexplained(Finding("CORE-000544", "EX", "EXSEQ", ISSUE, 3))) == 1
    assert len(_unexplained(Finding("CORE-000544", "LB", "LBSEQ", ISSUE, 3))) == 1
    assert _unexplained(Finding("CORE-000510", "DM", "split", ISSUE, 1)) == []
    assert len(_unexplained(Finding("CORE-000510", "DM", "split", ISSUE, 1, ("S-1",)))) == 1
    assert _unexplained(Finding("CORE-000735", "TS", "UNII", ISSUE, 1)) == []
    assert len(_unexplained(Finding("CORE-000735", "TS", "UNII", ISSUE, 2))) == 1


def test_a_probe_explains_only_the_subjects_it_planted():
    arms = ("CORE-000655", "DM", "arms differ", ISSUE)

    def found(count, subjects=(), listed=None, named=None):
        """A finding as a report gives it: one detail row with a subject for every issue."""
        return Finding(*arms, count, subjects, listed=count if listed is None else listed,
                       named=count if named is None else named)

    assert _unexplained(found(1, ("S-9",))) == []
    # A subject that no probe planted, alone or beside a planted one.
    assert len(_unexplained(found(1, ("S-1",)))) == 1
    assert len(_unexplained(found(2, ("S-1", "S-9")))) == 1
    # A subject planted by another probe, or in the other dataset of the study.
    assert len(_unexplained(found(1, ("S-4",)))) == 1
    assert len(_unexplained(found(1, ("S-7",)))) == 1
    assert _unexplained(found(1, ("S-7",)), which="visible") == []
    # A finding without subjects cannot be tied to a probe.
    assert len(_unexplained(found(1))) == 1
    # Review finding F13: more issues than detail rows, or a row without a subject: the
    # planted subject that happens to be listed does not explain the rest.
    assert len(_unexplained(found(3, ("S-9",), listed=1, named=1))) == 1
    assert len(_unexplained(found(2, ("S-9",), listed=2, named=1))) == 1
    assert _unexplained(found(2, ("S-9",), listed=2, named=2)) == []   # two records of S-9
    assert len(_unexplained(Finding(*arms, 1, ("S-9",)))) == 1         # not read from a report
    line = gate.describe(_unexplained(found(1, ("S-1",)))[0])
    assert "CORE-000655 DM" in line and "S-1" in line
    many = gate.describe(found(5, ("S-1", "S-2", "S-3", "S-4", "S-5")))
    assert "S-3 and 2 more" in many and "S-4" not in many


def test_a_rule_about_every_record_is_explained_for_its_dataset_only():
    """Review finding F13: an entry without datasets took any dataset of the right size."""
    for entry in gate.load_explained()["explained"]:
        if entry["kind"] in ("every_record", "repeated_key", "study", "probe"):
            assert entry.get("datasets"), entry["id"]
    # AE has five records here and TS two.
    for rule in ("CORE-002056", "CORE-002084"):
        assert _unexplained(Finding(rule, "AE", "missing", ISSUE, 5)) == []
        assert len(_unexplained(Finding(rule, "TS", "missing", ISSUE, 2))) == 1
        assert len(_unexplained(Finding(rule, "AE", "missing", ISSUE, 4))) == 1


def _counted(tables, **changes) -> cdisccore.Report:
    """A report as the pinned CORE writes it for these datasets."""
    values = {"path": Path("r"), "engine": "1.0.0", "standard": "SDTMIG V3.4",
              "rules": {f"R{n}": "SUCCESS" for n in range(500)}, "findings": (),
              "datasets": tuple(tables), "records": {n: len(r) for n, r in tables.items()},
              "terminology": "sdtmct-2025-09-26", "define": "2.1.0"}
    return cdisccore.Report(**{**values, **changes})


def test_a_report_of_another_engine_or_standard_does_not_count(root):
    assert gate.report_problems(root, _counted(TABLES), TABLES) == []
    problems = gate.report_problems(root, _counted(
        TABLES, engine="0.17.1", standard="SDTMIG V3.3", rules={"R1": "SUCCESS"}), TABLES)
    assert len(problems) == 3 and "0.17.1" in problems[0]


def test_a_report_counts_only_for_the_datasets_that_were_handed_over(root):
    """Review finding F12: a report that lists no dataset passed."""
    assert gate.report_problems(root, _counted(TABLES, records={}), TABLES) == [
        "CORE did not read the datasets as they were handed over: AE not read of 5 records, "
        "DM not read of 4 records, EX not read of 3 records, SV not read of 8 records, "
        "TS not read of 2 records"]
    # A dataset CORE skipped, one it read short, one nobody handed over.
    skipped = {n: len(r) for n, r in TABLES.items() if n != "SV"}
    assert gate.report_problems(root, _counted(TABLES, records=skipped), TABLES) == [
        "CORE did not read the datasets as they were handed over: SV not read of 8 records"]
    short = {**{n: len(r) for n, r in TABLES.items()}, "AE": 4, "LB": 9}
    assert gate.report_problems(root, _counted(TABLES, records=short), TABLES) == [
        "CORE did not read the datasets as they were handed over: AE 4 of 5 records, "
        "LB 9 of no records"]
    # CORE without the Define-XML, or with another terminology package than it names.
    assert gate.report_problems(root, _counted(TABLES, define=""), TABLES) == [
        "CORE read the Define-XML as '', not 2.1.0"]
    assert gate.report_problems(root, _counted(TABLES, terminology="sdtmct-2025-12-19"),
                                TABLES) == [
        "CORE used the terminology 'sdtmct-2025-12-19', not sdtmct-2025-09-26"]


def test_parallel_runs_of_core_stay_within_the_memory(monkeypatch):
    """Lesson 32: too many runs at once exhausted the memory of the machine."""
    need = gate.CORE_RUN_MEMORY_MB
    most = gate.MAX_WORKERS // cdisccore.POOL_SIZE
    assert gate.MAX_WORKERS == 4 and 1 <= most <= 4
    # However much memory and however many processors: never more workers than the rule.
    assert gate.core_workers(available_mb=640000, processors=128) == most
    assert gate.core_workers(available_mb=640000, processors=128) * cdisccore.POOL_SIZE <= 4
    assert gate.core_workers(available_mb=4 * need, processors=32) == min(2, most)
    assert gate.core_workers(available_mb=need, processors=32) == 1
    assert gate.core_workers(available_mb=64000, processors=2) == 1
    assert gate.core_workers(available_mb=0, processors=1) == 1


def test_a_planted_defect_counts_only_with_its_rule_dataset_and_subject(root, catalog, tmp_path,
                                                                        monkeypatch):
    """Lesson 36: a finding that merely lists the subject somewhere is not the planted one."""
    seeds = ("unit-planted",)
    label = study.catalog_label(catalog)
    gate.generate_all(root, tmp_path / "first", seeds)
    design = pgfix.sample(seeds[0], label)
    explained = gate.load_explained()

    def changed(folder):
        """What the check planted, read back from the copy it wrote."""
        tables = study.read_tables(folder, "twin")
        seen, twice = set(), None
        for row in tables["AE"]:
            key = (row["USUBJID"], row["AESEQ"])
            twice = row["USUBJID"] if key in seen else twice
            seen.add(key)
        planted = {s for r in study.read_probes(folder) if r["data"] == "twin"
                   for s in r["subjects"]}
        arm = next(r["USUBJID"] for r in tables["DM"] if r["ARMCD"] and r["ACTARMCD"]
                   and r["ARMCD"] != r["ACTARMCD"] and r["USUBJID"] not in planted)
        return twice, arm, [r["USUBJID"] for r in tables["DM"]]

    def report_of(findings, folder, **changes):
        tables = study.read_tables(folder, "twin")
        rules = {f"R{n}": "SUCCESS" for n in range(500)} | {f.rule: f.status for f in findings}
        return _counted(tables, rules=rules, findings=tuple(findings), **changes)

    def elsewhere(root_, folder, which):
        # An unexplained finding of another rule that lists every subject of the study.
        _, _, everyone = changed(folder)
        return report_of([Finding("CORE-009999", "SV", "something else", ISSUE, len(everyone),
                                  tuple(everyone))], folder)

    def as_core_does(root_, folder, which):
        twice, arm, _ = changed(folder)
        return report_of([
            Finding("CORE-000544", "AE", "AESEQ must be unique", ISSUE, 2, (twice,)),
            Finding("CORE-000655", "DM", "arms differ", ISSUE, 1, (arm,), listed=1, named=1)],
            folder)

    def wrong_dataset(root_, folder, which):
        twice, arm, _ = changed(folder)
        return report_of([
            Finding("CORE-000544", "EX", "EXSEQ must be unique", ISSUE, 2, (twice,)),
            Finding("CORE-000655", "DM", "arms differ", ISSUE, 1, (arm,), listed=1, named=1)],
            folder)

    def without_define(root_, folder, which):
        # CORE reports both defects, in a run that did not read the Define-XML.
        twice, arm, _ = changed(folder)
        return report_of([
            Finding("CORE-000544", "AE", "AESEQ must be unique", ISSUE, 2, (twice,)),
            Finding("CORE-000655", "DM", "arms differ", ISSUE, 1, (arm,), listed=1, named=1)],
            folder, define="")

    for number, (fake, expected) in enumerate(((elsewhere, False), (as_core_does, True),
                                               (wrong_dataset, False), (without_define, False))):
        monkeypatch.setattr(gate, "run_core", fake)
        said: list[str] = []
        assert gate.planted_core_defects(root, said.append, tmp_path / "first" / seeds[0],
                                         tmp_path / f"run-{number}", explained, design,
                                         label) is expected, fake.__name__
        missed = any("did not report both planted defects" in line for line in said)
        assert missed is (fake in (elsewhere, wrong_dataset))
        assert any("does not count" in line for line in said) is (fake is without_define)


def test_the_reports_of_core_outlive_the_scratch_folder(root, catalog, tmp_path, monkeypatch):
    """Rule R8: a line of the gate log about CORE has a report that can be read afterwards."""
    seeds = ("unit-keep",)
    gate.generate_all(root, tmp_path / "first", seeds)

    def fake(root_, folder, which):
        (folder / "core").mkdir(exist_ok=True)
        (folder / "core" / f"{which}.json").write_text(json.dumps({"which": which}), "ascii")
        return _counted(study.read_tables(folder, which))

    monkeypatch.setattr(gate, "run_core", fake)
    said: list[str] = []
    keep = tmp_path / "kept"
    # The fake reports no planted defect, so the check fails; its report is kept all the same.
    assert gate.core_check(root, said.append, tmp_path, seeds, keep=keep) is False
    assert sorted(p.name for p in keep.iterdir()) == ["planted-twin.json"]
    monkeypatch.setattr(gate, "planted_core_defects", lambda *args: True)
    assert gate.core_check(root, said.append, tmp_path, seeds, keep=keep) is False
    assert sorted(p.name for p in keep.iterdir()) == [
        "planted-twin.json", "unit-keep-twin.json", "unit-keep-visible.json"]
    # The report of the planted study and the two of the seed.
    assert "3 reports of CORE are kept in kept/ beside this log" in said
    assert any(line.startswith("explanations that no finding needed") for line in said)
    # Without a folder to keep them in, nothing is copied and nothing is said about it.
    said.clear()
    gate.core_check(root, said.append, tmp_path, seeds)
    assert not any("are kept" in line for line in said)


# -- controlled terms ------------------------------------------------------------


def _package() -> dict[str, dict]:
    """A terminology package as CORE's cache gives it, built from the generator's table."""
    from specfirst.gen import terms

    package = {c["code"]: {"name": name, "extensible": c["extensible"],
                           "terms": dict(c["terms"])} for name, c in terms.CT.items()}
    package["C66738"] = {"name": "TSPARMCD", "extensible": True,
                         "terms": {code: concept
                                   for code, (_, concept) in terms.TS_PARAMETERS.items()}}
    package["C67152"] = {"name": "TSPARM", "extensible": True,
                         "terms": {name: concept
                                   for name, concept in terms.TS_PARAMETERS.values()}}
    # Codelists of the values of trial summary parameters, as far as a study writes them.
    package["C99076"] = {"name": "INTMODEL", "extensible": True,
                         "terms": {"PARALLEL": "C82639"}}
    package["C99078"] = {"name": "INTTYPE", "extensible": True, "terms": {"DRUG": "C1909"}}
    package["C66732"] = {"name": "SEXPOP", "extensible": False, "terms": {"BOTH": "C49636"}}
    package["C99077"] = {"name": "STYPE", "extensible": False,
                         "terms": {"INTERVENTIONAL": "C98388"}}
    package["C66735"] = {"name": "TBLIND", "extensible": True,
                         "terms": {"DOUBLE BLIND": "C15228"}}
    package["C66785"] = {"name": "TCNTRL", "extensible": True, "terms": {"PLACEBO": "C49648"}}
    package["C66737"] = {"name": "TPHASE", "extensible": True,
                         "terms": {"PHASE II TRIAL": "C15601", "PHASE III TRIAL": "C15602"}}
    package["C66739"] = {"name": "TTYPE", "extensible": True, "terms": {"SAFETY": "C49667"}}
    return package


def test_the_terms_of_the_generator_are_checked_against_a_package(catalog):
    import copy

    from specfirst.gen import sdtm, terms

    package = _package()
    assert gate.package_problems(package) == []
    design = pgfix.sample("terms", study.catalog_label(catalog))
    people, _ = study.simulate(design, catalog, "terms", "twin")
    tables = sdtm.build(design, people)
    checked, problems = gate.term_problems(tables, package)
    assert problems == [] and checked > 5000

    # Planted: values outside their codelist, in three domains.
    broken = copy.deepcopy(tables)
    broken["DM"][0]["SEX"] = "X"
    broken["AE"][0]["AESEV"] = "TERRIBLE"
    broken["DS"][0]["DSDECOD"] = "GONE FISHING"
    found = gate.term_problems(broken, package)[1]
    assert len(found) == 3
    assert found[0].startswith("DM.SEX = 'X' ") and "not a term of SEX" in found[0]
    assert any(line.startswith("DS.DSDECOD = 'GONE FISHING'") for line in found)
    assert any(line.startswith("AE.AESEV = 'TERRIBLE'") for line in found)
    # Review finding F27: DSDECOD has one codelist per category of the record. A milestone
    # term in a disposition event is a term of the wrong one, and so the other way round.
    broken = copy.deepcopy(tables)
    event = next(r for r in broken["DS"] if r["DSCAT"] == "DISPOSITION EVENT")
    milestone = next(r for r in broken["DS"] if r["DSCAT"] == "PROTOCOL MILESTONE")
    event["DSDECOD"], milestone["DSDECOD"] = "RANDOMIZED", "COMPLETED"
    found = gate.term_problems(broken, package)[1]
    assert len(found) == 2
    assert (f"DS.DSDECOD = 'RANDOMIZED' {event['USUBJID']} of a record with DSCAT "
            "'DISPOSITION EVENT': not a term of NCOMPLT") in found
    assert any("'COMPLETED'" in line and line.endswith("not a term of PROTMLST")
               for line in found)
    # The country is checked without a codelist of the package; the codelists of the
    # study (arms, elements, causality, treatment names) when they are handed over.
    broken = copy.deepcopy(tables)
    broken["DM"][0]["COUNTRY"] = "XXX"
    broken["DM"][1]["COUNTRY"] = "usa"
    assert len(gate.term_problems(broken, package)[1]) == 2
    lists = sdtm.study_codelists(design, tables)
    checked_with, problems = gate.term_problems(tables, package, lists)
    assert problems == [] and checked_with > checked
    broken = copy.deepcopy(tables)
    broken["AE"][0]["AEREL"] = "MAYBE"
    broken["EX"][0]["EXTRT"] = "ASPIRIN"
    broken["DM"][0]["ARMCD"] = "ZZ"
    broken["SE"][0]["ETCD"] = "NOPE"
    assert gate.term_problems(broken, package)[1] == []      # not seen without the lists
    found = gate.term_problems(broken, package, lists)[1]
    assert len(found) == 4
    assert any(line.startswith("AE.AEREL = 'MAYBE'") and "the study codelist AEREL" in line
               for line in found)
    # Planted: a trial summary value whose code is the code of another term.
    broken = copy.deepcopy(tables)
    row = next(r for r in broken["TS"] if r["TSPARMCD"] == "TBLIND")
    row["TSVALCD"] = "C49648"
    assert gate.term_problems(broken, package)[1] == [
        "TS: C49648 is not the code of 'DOUBLE BLIND' (TBLIND)"]
    row = next(r for r in broken["TS"] if r["TSPARMCD"] == "NARMS")
    row["TSPARMCD"] = "ARMSNO"
    assert any("TSPARMCD = 'ARMSNO'" in line for line in gate.term_problems(broken, package)[1])

    # Planted: the package differs from the table the generator carries.
    other = copy.deepcopy(package)
    other[terms.CT["SEX"]["code"]]["terms"]["F"] = "C00000"
    assert gate.package_problems(other) == ["SEX: 'F' is C00000 in the package, C16576 here"]
    other = copy.deepcopy(package)
    del other[terms.CT["RACE"]["code"]]  # the packages of 2026 no longer have this codelist
    assert gate.package_problems(other) == ["RACE: the package has no codelist C74457"]
    other = copy.deepcopy(package)
    other[terms.CT["EPOCH"]["code"]]["extensible"] = False
    assert "extensible False" in gate.package_problems(other)[0]
    other = copy.deepcopy(package)
    other["C67152"]["terms"].pop("Trial Title")
    assert gate.package_problems(other) == [
        "trial summary parameter TITLE (Trial Title) is not C49802 in the package"]


# -- identical hashes ------------------------------------------------------------


def test_two_builds_of_a_study_have_identical_hashes(root, catalog, tmp_path):
    design = pgfix.sample("hashes", study.catalog_label(catalog))
    first = study.generate(root, design, "hashes", tmp_path / "a")
    second = study.generate(root, design, "hashes", tmp_path / "b")
    assert gate.hash_differences(first["files"], second["files"]) == []
    assert first == second
    other = study.generate(root, design, "another seed", tmp_path / "c")
    assert gate.hash_differences(first["files"], other["files"])
    # Planted defect: one changed byte, one missing file.
    path = tmp_path / "b" / "inputs" / "data" / "sdtm" / "dm.json"
    path.write_bytes(path.read_bytes().replace(b'"M"', b'"F"', 1))
    (tmp_path / "b" / "twin" / "data" / "sdtm" / "define.xml").unlink()
    assert gate.hash_differences(first["files"], study.file_hashes(tmp_path / "b")) == [
        "twin/data/sdtm/define.xml: only in one build",
        "inputs/data/sdtm/dm.json: the hashes differ"]


def test_everything_generated_names_the_catalog_version(root, catalog, tmp_path):
    # As the standard form names it: "Catalog: <name> <version>". A freeze changes the
    # version, and with it every generated file: that shows what must be generated again.
    label = study.catalog_label(catalog)
    assert label == f"{catalog.name} {catalog.version}" and catalog.name == "specfirst-m1"
    seed = "zq-seed-7719"
    design = pgfix.sample(seed, label)
    manifest = study.generate(root, design, seed, tmp_path)
    assert manifest["catalog"] == {"name": catalog.name, "version": catalog.version}
    assert manifest["generator"] == GENERATOR
    text_files = [p for p in tmp_path.rglob("*") if p.suffix in (".json", ".jsonl", ".yaml",
                                                                 ".xml")]
    assert len(text_files) >= 28
    for path in text_files:
        text = path.read_text(encoding="ascii")
        if path.name == "study.json":
            assert json.loads(text)["catalog"]["version"] == catalog.version
        else:
            assert label in text, path.name
    assert len(list(tmp_path.rglob("*.parquet"))) == 22  # their schema names it: see sdtm tests
    # The manifest lists every other file, and holds the hash of the seed, never the seed.
    assert set(manifest["files"]) == set(study.file_hashes(tmp_path))
    assert study.read_manifest(tmp_path) == manifest
    everything = b"".join(p.read_bytes() for p in tmp_path.rglob("*") if p.is_file())
    assert manifest["seed_sha256"].encode() in everything
    assert seed.encode() not in everything and seed not in json.dumps(manifest)


def test_a_design_of_another_catalog_version_is_refused(root, catalog, tmp_path):
    design = pgfix.sample("old", "specfirst-m1 some-earlier-version")
    with pytest.raises(study.StudyError, match="Sample the design again"):
        study.generate(root, design, "old", tmp_path)


def test_the_gate_checks_see_their_planted_defects(root, catalog, tmp_path):
    """The two checks that need no CORE, on one seed: both pass, both prove themselves."""
    said: list[str] = []
    seeds = ("unit-gate",)
    assert gate.determinism_check(root, said.append, tmp_path, seeds) is True
    assert any(line.startswith("planted defect: a build with another time stamp") for line in said)
    assert "planted defect: a study whose manifest alone differs: study.json: the hashes " \
        "differ" in said
    assert any(line.startswith("planted defect: a build that depends on the hash seed")
               for line in said)
    assert "by a process of its own (hash seed " in said[-2]
    assert said[-1] == "identical hashes: 0 problems"
    said.clear()
    assert gate.probes_check(root, said.append, tmp_path, seeds) is True
    assert sum(line.startswith("planted defect:") for line in said) == 3
    assert any("0 problems" in line for line in said)


def test_the_second_build_is_made_by_another_process(root, catalog, tmp_path, monkeypatch):
    """Review finding F12: two builds of one process share what a build must not depend on."""
    seeds = ("unit-apart",)
    here = gate.generate_all(root, tmp_path / "here", seeds)
    apart = gate.generate_apart(root, tmp_path / "apart", seeds, gate.other_hash_seed())
    assert gate.hash_differences(gate.build_hashes(tmp_path / "here" / seeds[0]),
                                 apart[seeds[0]]) == []
    # The manifest is compared like every other file.
    assert set(apart[seeds[0]]) == set(here[seeds[0]]["files"]) | {"study.json"}
    # Planted defect: a build that depends on the hash seed differs between two processes ...
    one = gate.generate_apart(root, tmp_path / "one", seeds, "1", planted=True)
    two = gate.generate_apart(root, tmp_path / "two", seeds, "2", planted=True)
    assert gate.hash_differences(one[seeds[0]], two[seeds[0]])
    # ... and two processes with one hash seed would not show it.
    again = gate.generate_apart(root, tmp_path / "again", seeds, "1", planted=True)
    assert gate.hash_differences(one[seeds[0]], again[seeds[0]]) == []
    monkeypatch.setenv("PYTHONHASHSEED", "1")
    assert gate.other_hash_seed() == "2"
    monkeypatch.delenv("PYTHONHASHSEED")
    assert gate.other_hash_seed() == "1"
    with pytest.raises(RuntimeError, match="a build in a process of its own failed"):
        gate.generate_apart(tmp_path / "no-checkout", tmp_path / "fails", seeds, "1")


def test_the_probe_check_fails_on_a_study_whose_twin_lost_a_probe(root, catalog, tmp_path):
    seeds = ("unit-gate",)
    gate.generate_all(root, tmp_path / "first", seeds)
    path = tmp_path / "first" / seeds[0] / "gold" / "probes.jsonl"
    records = [json.loads(line) for line in path.read_text(encoding="ascii").splitlines()]
    kept = [r for r in records
            if (r["probe"], r["data"]) != ("partial_exposure_date", "twin")]
    assert len(kept) == len(records) - 1
    path.write_text("".join(json.dumps(r) + "\n" for r in kept), encoding="ascii", newline="\n")
    said: list[str] = []
    assert gate.probes_check(root, said.append, tmp_path, seeds) is False
    assert any("trt.date.imputation: no probe in the twin separates" in line for line in said)


# -- seeds and the command line ---------------------------------------------------


def test_a_seed_file_stays_outside_the_repository(root, tmp_path):
    outside = tmp_path / "seed.txt"
    outside.write_bytes(b"sealed-seed-text\n")
    # The seed is the file, byte for byte: the hash in a manifest is the hash of the file.
    assert command.read_seed(root, None, str(outside)) == "sealed-seed-text\n"
    assert seed_sha256(command.read_seed(root, None, str(outside))) == hashlib.sha256(
        outside.read_bytes()).hexdigest()
    assert command.read_seed(root, "abc", None) == "abc"
    with pytest.raises(command.SeedError, match="inside the checkout"):
        command.read_seed(root, None, str(root / "docs" / "seed.txt"))
    # Another worktree or clone of a repository is a checkout as well.
    clone = tmp_path / "another-worktree"
    (clone / "notes").mkdir(parents=True)
    (clone / ".git").write_text("gitdir: elsewhere\n", encoding="ascii")
    (clone / "notes" / "seed.txt").write_bytes(b"sealed-seed-text\n")
    with pytest.raises(command.SeedError, match="inside the checkout"):
        command.read_seed(root, None, str(clone / "notes" / "seed.txt"))
    outside.write_bytes(b"sealed \xff")
    with pytest.raises(command.SeedError, match="not ASCII"):
        command.read_seed(root, None, str(outside))
    with pytest.raises(command.SeedError, match="exactly one"):
        command.read_seed(root, "abc", str(outside))
    with pytest.raises(command.SeedError, match="exactly one"):
        command.read_seed(root, None, None)
    outside.write_text("\n", encoding="ascii")
    with pytest.raises(command.SeedError, match="empty"):
        command.read_seed(root, None, str(outside))
    # No seed of a kit is written into the repository: the gate seeds are development seeds.
    assert all(seed.startswith("gen-1a-") for seed in gate.SEEDS)


def test_the_command_line_generates_and_checks_a_study(root, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("SPECFIRST_ROOT", str(root))
    design = tmp_path / "design.yaml"
    assert cli.main(["gen", "design", "--seed", "cli", "--out", str(design)]) == 0
    assert "design of the archetype PG-FIX" in capsys.readouterr().out
    out = tmp_path / "study"
    assert cli.main(["gen", "study", "--design", str(design), "--seed", "cli",
                     "--out", str(out)]) == 0
    assert "for the catalog specfirst-m1 " in capsys.readouterr().out
    assert (out / "inputs" / "data" / "sdtm" / "dm.parquet").is_file()
    assert (out / "twin" / "data" / "sdtm" / "define.xml").is_file()
    assert cli.main(["gen", "check", str(out), "--no-core"]) == 0
    assert capsys.readouterr().out.rstrip().endswith("study: ok")
    # Planted defect: a file changed after the manifest was written.
    with open(out / "gold" / "probes.jsonl", "a", encoding="ascii") as handle:
        handle.write("\n")
    assert cli.main(["gen", "check", str(out), "--no-core"]) == 1
    assert "gold/probes.jsonl: the hashes differ" in capsys.readouterr().out
    assert cli.main(["gen", "study", "--design", str(design), "--out", str(out)]) == 2
    limited = tmp_path / "limited"
    assert cli.main(["gen", "study", "--design", str(design), "--seed", "cli", "--out",
                     str(limited), "--domains", "DM", "AE"]) == 0
    files = sorted(p.name for p in (limited / "inputs" / "data" / "sdtm").iterdir())
    assert files == ["ae.json", "ae.parquet", "define.xml", "dm.json", "dm.parquet"]
    assert cli.main(["gen", "study", "--design", str(design), "--seed", "cli", "--out",
                     str(limited), "--domains", "XX"]) == 1


def test_coverage_of_the_visible_data_is_not_required(root, catalog, tmp_path):
    """The visible data carry a sampled part: what they log must be there, no more."""
    design = pgfix.sample("visible", study.catalog_label(catalog))
    study.generate(root, design, "visible", tmp_path)
    log = study.read_probes(tmp_path)
    _, _, problems = present.coverage(catalog, design, log, study.read_tables(tmp_path, "visible"),
                                      "visible")
    assert problems and not [line for line in problems if line.startswith("probe ")]


def test_the_country_codes_are_those_of_iso_3166():
    """The package of CORE holds no country codes, and its rules on them cannot run.

    ISO 3166-1 alpha-3, from the standard: Canada, Germany, Spain, the United
    Kingdom, Poland, the United States of America.
    """
    from specfirst.gen import terms

    assert sorted(terms.COUNTRIES) == ["CAN", "DEU", "ESP", "GBR", "POL", "USA"]
