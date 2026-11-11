"""Planted defects for the checkers of the std-1 gate (rule R5, PLAN.md section 9.5).

Each test copies the catalog and the house standard, shows that the copy is
clean, plants one defect and expects the checker to name it.
"""

from __future__ import annotations

import copy
import shutil
from pathlib import Path

import pytest
import yaml

from specfirst.compile import catalog as catalog_module
from specfirst.compile import checks
from specfirst.compile import house as house_module
from specfirst.compile.compiler import compile_decisions, relative_reference
from specfirst.paths import cache_dir


@pytest.fixture
def work(root, tmp_path) -> Path:
    """A copy of what the checkers read, in a folder of its own."""
    copy_root = tmp_path / "root"
    shutil.copytree(root / "standard", copy_root / "standard")
    (copy_root / "third_party").mkdir()
    shutil.copy(root / "third_party" / "sources.yaml", copy_root / "third_party" / "sources.yaml")
    shutil.copy(root / "PLAN.md", copy_root / "PLAN.md")
    fake_cache(copy_root, catalog_module.load(catalog_module.default_dir(copy_root)))
    return copy_root


def load(work: Path):
    return (catalog_module.load(catalog_module.default_dir(work)),
            house_module.load(house_module.default_dir(work)))


def change(path: Path, plant) -> None:
    """Rewrite a YAML file after `plant` changed its data."""
    data = yaml.safe_load(path.read_text(encoding="ascii"))
    plant(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, width=10_000), encoding="ascii",
                    newline="\n")


def entry_file(work: Path, entry_id: str) -> Path:
    return work / "standard" / "catalog" / "entries" / f"{entry_id}.yaml"


def template_file(work: Path, entry_id: str) -> Path:
    return work / "standard" / "catalog" / "templates" / f"{entry_id}.yaml"


def fake_cache(work: Path, catalog) -> Path:
    """A fetch cache that holds every cited file with the text it must hold.

    The fixture builds it from the clean catalog, before a defect is planted.
    """
    cache = work / "cache"
    for entry in catalog.entries.values():
        for source in entry.sources:
            known = catalog.sources.get(source.get("ref"), {})
            if known.get("kind") == "pinned" and source.get("path"):
                path = cache / known["source"] / source["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "a", encoding="ascii") as handle:
                    handle.write(str(source.get("find", "")) + "\n")
    return cache


def static_problems(work: Path) -> dict[str, list[str]]:
    catalog, house = load(work)
    return {
        "catalog": checks.catalog_problems(catalog, work),
        "examples": checks.evaluate_examples(catalog),
        "sources": checks.source_problems(catalog, work, work / "cache"),
        "probes": checks.probe_problems(catalog),
        "wording": checks.wording_problems(catalog),
        "roundtrip": checks.roundtrip_problems(catalog)[0],
        "templates": checks.template_problems(catalog, house),
        "house": checks.house_problems(catalog, house, work),
    }


def test_the_clean_copy_passes_every_static_checker(work):
    assert static_problems(work) == {name: [] for name in (
        "catalog", "examples", "sources", "probes", "wording", "roundtrip", "templates", "house")}


def _alternative(data: dict, rule: str) -> dict:
    return next(a for a in data["alternatives"] if a["id"] == rule)


def _set(key: str, value):
    return lambda data: data.__setitem__(key, value)


STATIC_DEFECTS = [
    # (what is planted, file, change, checker, text of the expected problem)
    ("a field the schema does not know", "entry:ae.teae.end", _set("confidence", 0.9),
     "catalog", "schema"),
    ("a unit that does not exist", "entry:ae.teae.end", _set("unit", "mod-nowhere"),
     "catalog", "unknown unit 'mod-nowhere'"),
    ("an undeclared design feature", "entry:ae.teae.end", _set("applies_when", "design.on_mars"),
     "catalog", "unknown feature 'design.on_mars'"),
    ("a predicate that does not parse", "entry:ae.teae.end",
     _set("applies_when", "design.always and"), "catalog", "applies_when"),
    ("a default that is not an alternative", "entry:ae.teae.end",
     _set("house_default", "sometimes"), "catalog", "house default 'sometimes'"),
    ("a slot the statement does not use", "entry:ae.teae.end",
     lambda d: _alternative(d, "last_dose_plus_days").__setitem__(
         "statement", "Treatment emergence ends some days after the treatment end date."),
     "catalog", "slot 'days' must be used exactly once"),
    ("text after a slot that could continue its value", "entry:ae.teae.end",
     lambda d: _alternative(d, "last_dose_plus_days").__setitem__(
         "statement", "Treatment emergence ends {days}0 days after the treatment end date."),
     "catalog", "could continue its value"),
    ("two alternatives with the same sentence", "entry:ae.teae.end",
     lambda d: _alternative(d, "end_of_study").__setitem__(
         "statement", "Treatment emergence has no end date."),
     "catalog", "the same sentence as ae.teae.end/no_end"),
    ("an example outside the limits of its slot", "entry:ae.teae.end",
     lambda d: _alternative(d, "last_dose_plus_days")["slots"]["days"].__setitem__(
         "examples", [30, -7]), "catalog", "below the minimum"),
    ("a compile template without one alternative", "template:ae.teae.end",
     lambda d: d["alternatives"].__delitem__("end_of_study"),
     "catalog", "must have exactly the alternatives"),
    ("a compile template that reads an unknown slot", "template:ae.teae.end",
     lambda d: d["alternatives"]["no_end"].__setitem__("params", {"x": {"$get": "weeks"}}),
     "examples", "'weeks' is not defined"),
    ("an entry without a source", "entry:ae.teae.end", _set("sources", []),
     "sources", "ae.teae.end: no public source"),
    ("a source that is not in the registry", "entry:ae.teae.end",
     _set("sources", [{"ref": "folklore", "where": "everybody knows"}]),
     "sources", "'folklore' is not in sources.yaml"),
    ("a pinned source without a file", "entry:ae.teae.end",
     _set("sources", [{"ref": "yamaa", "where": "somewhere in the repository"}]),
     "sources", "pinned source 'yamaa' needs a path"),
    ("a cited file that the pinned source does not hold", "entry:ae.teae.end",
     _set("sources", [{"ref": "yamaa", "where": "a benchmark", "path": "benchmarks/none.yaml"}]),
     "sources", "yamaa has no file benchmarks/none.yaml"),
    ("a cited text that does not stand in the file", "entry:ae.start.imputation",
     lambda d: d["sources"][1].__setitem__("find", "not_before: BIRTHDAY"),
     "sources", "'not_before: BIRTHDAY' does not stand in"),
    ("a pair of alternatives without a probe", "entry:ae.teae.end",
     _set("probes", ["ae_starts_after_emergence_window", "ae_starts_after_end_of_study"]),
     "probes", "no probe separates last_dose_plus_days from end_of_study"),
    ("a probe that does not exist", "entry:ae.teae.start", _set("probes", ["wishful_thinking"]),
     "probes", "'wishful_thinking' is not in probes.yaml"),
    ("a slot that no probe varies", "probes",
     lambda d: d["probes"]["ae_starts_after_emergence_window"].__delitem__("varies"),
     "probes", "no probe varies the slot 'days'"),
    ("a phrasing that loses its number", "phrasing:ae.teae.end",
     lambda d: d["alternatives"]["last_dose_plus_days"].__setitem__(
         "plain", "Treatment emergence ends 30 days after the treatment end date."),
     "wording", "must use exactly the slots ['days']"),
    ("a phrasing that repeats the statement", "phrasing:ae.teae.end",
     lambda d: d["alternatives"]["no_end"].__setitem__(
         "plain", "Treatment emergence has no end date."),
     "wording", "repeats another sentence"),
    ("an alternative without phrasings", "phrasing:ae.teae.end",
     lambda d: d["alternatives"].__delitem__("end_of_study"),
     "wording", "ae.teae.end/end_of_study: needs at least two phrasings"),
    ("a parameter that no template reads", "template:tfl.vs.layout",
     lambda d: d["alternatives"]["stacked"].__setitem__("params", {"block_order": "stacked"}),
     "templates", "no template reads 'block_order'"),
    ("a parameter that two entries set", "template:tfl.vs.layout",
     lambda d: d["alternatives"]["stacked"].__setitem__("params", {"rounding": "half_even"}),
     "templates", "'rounding' is set by more than one entry"),
    ("a house standard for another catalog", "house", _set("catalog", "somebody-else"),
     "house", "made for the catalog 'somebody-else'"),
    ("a default value for an unknown entry", "house",
     _set("default_values", {"ae.nothing": {"days": 3}}),
     "house", "default_values names the unknown entry 'ae.nothing'"),
    ("a missing parent spec", "house",
     lambda d: d["adam"]["ADVS"].__setitem__("parent", "adam/advs-v2.yaml"),
     "house", "parent spec of ADVS is missing"),
]


def _path(work: Path, where: str) -> Path:
    kind, _, name = where.partition(":")
    catalog = work / "standard" / "catalog"
    if kind == "entry":
        return entry_file(work, name)
    if kind == "template":
        return template_file(work, name)
    if kind == "phrasing":
        return catalog / "phrasings" / f"{name}.yaml"
    if kind == "probes":
        return catalog / "probes.yaml"
    return work / "standard" / "houses" / "open-default@1" / "house.yaml"


@pytest.mark.parametrize("what, where, plant, checker, expected", STATIC_DEFECTS,
                         ids=[defect[0] for defect in STATIC_DEFECTS])
def test_planted_defect_is_found(work, what, where, plant, checker, expected):
    change(_path(work, where), plant)
    found = static_problems(work)[checker]
    assert any(expected in problem for problem in found), (what, found[:5])


def test_an_unused_source_is_found(work):
    path = work / "standard" / "catalog" / "sources.yaml"
    change(path, lambda d: d["sources"].__setitem__(
        "rumour", {"kind": "document", "title": "Hearsay", "version": "1",
                   "url": "https://example.invalid/", "confirmed": "cited"}))
    assert "sources.yaml: rumour is cited by no entry" in static_problems(work)["sources"]


def test_reading_notes_that_skip_an_alternative_are_found(work):
    note = work / "standard" / "catalog" / "knowledge" / "ae.teae.end.md"
    note.write_text(note.read_text(encoding="ascii").replace("`end_of_study`", "the last one"),
                    encoding="ascii", newline="\n")
    assert "ae.teae.end: the reading notes do not cover `end_of_study`" in \
        static_problems(work)["wording"]


def test_an_edited_standards_document_is_found(work):
    document = work / "standard" / "houses" / "open-default@1" / "STANDARD.md"
    text = document.read_text(encoding="ascii")
    assert "Treatment emergence has no end date." in text
    document.write_text(text.replace("Treatment emergence has no end date.",
                                     "Treatment emergence ends at the end-of-study date."),
                        encoding="ascii", newline="\n")
    found = static_problems(work)["house"]
    assert any("STANDARD.md differs from its rendering" in problem for problem in found)


def test_a_statement_that_fits_two_decisions_is_found(work):
    """The round trip must be unique: two entries may not share one sentence."""
    change(entry_file(work, "bds.eot.record"), lambda d: _alternative(d, "none").__setitem__(
        "statement", "Treatment emergence has no end date."))
    found = static_problems(work)["roundtrip"]
    assert any("ambiguous" in problem and "ae.teae.end/no_end" in problem for problem in found)


def test_a_statement_that_does_not_read_back_is_found(work):
    """Text after a slot swallows part of the value: 30 renders as 300 and reads back as 300."""
    change(entry_file(work, "ae.teae.end"),
           lambda d: _alternative(d, "last_dose_plus_days").__setitem__(
               "statement", "Treatment emergence ends {days}0 days after the treatment end date."))
    found = static_problems(work)["roundtrip"]
    assert any("ae.teae.end/last_dose_plus_days" in problem and "not exact" in problem
               for problem in found)


# -- compiled files ----------------------------------------------------------


def compile_base(work: Path, out: Path) -> checks.Variant:
    catalog, house = load(work)
    base = checks.base_vector(catalog, house)
    reference = checks.house_reference(house, out)
    compiled = compile_decisions(catalog, house, base, reference,
                                 sdtm_dir=checks.VARIANT_SDTM, adam_dir=checks.VARIANT_ADAM)
    return checks.Variant("base", base, compiled)


def test_yamaa_check_finds_a_fragment_that_reads_an_unknown_column(work, tmp_path):
    out = tmp_path / "out"
    assert checks.yamaa_problems([compile_base(work, out)], out) == ([], 3)
    change(template_file(work, "ae.teae.end"), lambda d: d["alternatives"]["no_end"]["adam"][
        "ADAE"]["columns"][0].__setitem__("derivation", "NOPE"))
    problems, checked = checks.yamaa_problems([compile_base(work, out)], tmp_path / "bad")
    assert checked == 3
    assert any("ADAE" in problem and "NOPE" in problem for problem in problems)


def test_yamaa_run_finds_a_spec_that_checks_but_cannot_run(work, tmp_path):
    """The real case of docs/lessons.md: a lookup filter that reads a column of the current row."""
    def plant(data: dict) -> None:
        lookup = data["alternatives"]["last_on_or_before_first_dose"]["adam"]["ADSL"][
            "intermediates"]["do"]
        del lookup["derivations"], lookup["between"]
        lookup["filter"] = "VS.VSTESTCD = ${test|q} AND VS.VSDTC <= _TRTSDTC"

    assert checks.run_problems([compile_base(work, tmp_path / "ok")], tmp_path / "ok") == ([], 3)
    change(template_file(work, "demo.baseline.record"), plant)
    out = tmp_path / "bad"
    variant = compile_base(work, out)
    assert checks.yamaa_problems([variant], out)[0] == []  # yamaa check reads no data
    problems, _ = checks.run_problems([variant], out)
    assert any("ADSL" in problem and "_TRTSDTC" in problem for problem in problems)


def test_an_alternative_that_changes_nothing_is_found(work, tmp_path):
    """Canonical compile: two alternatives of one entry never give the same files."""
    change(template_file(work, "bds.unscheduled.use"), lambda d: d["alternatives"].__setitem__(
        "excluded", copy.deepcopy(d["alternatives"]["compete"])))
    catalog, house = load(work)
    found = checks.compile_all(catalog, house, tmp_path / "out")
    problems, _ = checks.coverage_problems(catalog, house, found,
                                           checks.house_reference(house, tmp_path / "out"))
    assert any(problem.startswith("bds.unscheduled.use/excluded") and "same files" in problem
               for problem in problems)


def test_two_decisions_that_write_one_column_are_found(work, tmp_path):
    def plant(data: dict) -> None:
        columns = data["alternatives"]["at_least_one_dose"]["adam"]["ADSL"]["columns"]
        columns.append({**columns[0], "name": "ITTFL"})

    change(template_file(work, "pop.safety.rule"), plant)
    catalog, house = load(work)
    found = checks.compile_all(catalog, house, tmp_path / "out")
    problems, _ = checks.coverage_problems(catalog, house, found,
                                           checks.house_reference(house, tmp_path / "out"))
    assert any("both write columns.ITTFL" in problem for problem in problems)


@pytest.fixture
def compiled(root, tmp_path):
    catalog, house = (catalog_module.load(catalog_module.default_dir(root)),
                      house_module.load(house_module.default_dir(root)))
    return compile_decisions(catalog, house, checks.base_vector(catalog, house),
                             relative_reference(house.directory, tmp_path / "adam"))


ARS_DEFECTS = [
    ("an analysis on an undefined analysis set",
     lambda doc: doc["analyses"][0].__setitem__("analysisSetId", "AnalysisSet_PP"),
     "analysisSetId 'AnalysisSet_PP' is not defined"),
    ("an analysis with an undefined method",
     lambda doc: doc["analyses"][0].__setitem__("methodId", "Mth_Magic"),
     "methodId 'Mth_Magic' is not defined"),
    ("an analysis by an undefined grouping",
     lambda doc: doc["analyses"][0]["orderedGroupings"][0].__setitem__("groupingId", "Grp_X"),
     "grouping 'Grp_X' is not defined"),
    ("two analyses with one ID",
     lambda doc: doc["analyses"].append(copy.deepcopy(doc["analyses"][0])),
     "is used twice"),
    ("a list of contents that names an unknown analysis",
     lambda doc: doc["mainListOfContents"]["contentsList"]["listItems"][0]["sublist"][
         "listItems"][0].__setitem__("analysisId", "An_Lost"),
     "lists the unknown analysis 'An_Lost'"),
    ("a denominator taken from an unknown analysis",
     lambda doc: next(a for a in doc["analyses"] if a.get("referencedAnalysisOperations"))[
         "referencedAnalysisOperations"][1].__setitem__("analysisId", "An_Nobody"),
     "refers to the unknown analysis 'An_Nobody'"),
]


@pytest.mark.parametrize("what, plant, expected", ARS_DEFECTS, ids=[d[0] for d in ARS_DEFECTS])
def test_ars_reference_defect_is_found(compiled, what, plant, expected):
    permissive: dict = {}  # the references are checked whatever the schema says
    assert checks.ars_problems(compiled.ars, permissive) == []
    doc = copy.deepcopy(compiled.ars)
    plant(doc)
    assert any(expected in problem for problem in checks.ars_problems(doc, permissive)), what


def test_ars_schema_defect_is_found(root, compiled):
    """Needs the pinned ARS schema of the fetch cache; the gate repeats it as a control."""
    schema_path = cache_dir(root) / checks.ARS_SCHEMA[0] / checks.ARS_SCHEMA[1]
    if not schema_path.is_file():
        pytest.skip("no fetch cache: `specfirst gate std-1` runs this control on the real schema")
    schema = checks.load_ars_schema(cache_dir(root))
    assert checks.ars_problems(compiled.ars, schema) == []
    assert checks.ars_schema_control(compiled.ars, schema) == []


def test_layout_defects_are_found(compiled):
    assert checks.layout_problems(compiled) == []
    renamed = copy.deepcopy(compiled)
    renamed.layouts["tfl-ae-summary"]["rows"][0]["analysis"] = "An_AESUM_GONE"
    found = checks.layout_problems(renamed)
    assert "layout tfl-ae-summary: the analysis 'An_AESUM_GONE' is not in the ARS file" in found
    assert "ARS: no layout shows the analysis 'An_AESUM_ANY'" in found  # nothing may be unused
    emptied = copy.deepcopy(compiled)
    emptied.layouts["tfl-vitals-by-visit"]["formats"] = {}
    assert "layout tfl-vitals-by-visit: the part 'formats' is missing" in \
        checks.layout_problems(emptied)
