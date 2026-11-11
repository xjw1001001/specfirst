"""The compiler: templates, predicates, decisions to files, the house standard."""

from __future__ import annotations

import json

import pyarrow.parquet as pq
import pytest
import yaml

from specfirst import schemas
from specfirst.compile import catalog as catalog_module
from specfirst.compile import checks, overview, predicate, tiny
from specfirst.compile import house as house_module
from specfirst.compile.compiler import (
    CompileError,
    bind_tables,
    compile_decisions,
    relative_reference,
)
from specfirst.compile.template import (
    TemplateError,
    cut_labels,
    evaluate,
    midpoint_windows,
    names_used,
)


@pytest.fixture(scope="module")
def catalog(root):
    return catalog_module.load(catalog_module.default_dir(root))


@pytest.fixture(scope="module")
def house(root):
    return house_module.load(house_module.default_dir(root))


@pytest.fixture(scope="module")
def base(catalog, house):
    return checks.base_vector(catalog, house)


def changed(base: list[dict], entry_id: str, value: dict | None, unit: str | None = None):
    return [{**r, "value": value} if r["id"] == entry_id and unit in (None, r["unit"]) else r
            for r in base]


# -- templates ---------------------------------------------------------------


def test_template_directives():
    scope = {"days": 30, "values": ["A", "it's"], "mode": "x",
             "rows": [{"v": "AGE"}, {"v": "SEX"}]}
    assert evaluate({"shift": {"days": {"$get": "days"}}}, scope) == {"shift": {"days": 30}}
    assert evaluate("ASTDT <= X + ${days} AND R IN ${values|qlist}", scope) == \
        "ASTDT <= X + 30 AND R IN ('A', 'it''s')"
    assert evaluate([1, {"$if": {"get": "mode", "eq": "y"}, "then": 2}, 3], scope) == [1, 3]
    assert evaluate([{"$for": "r", "in": {"$get": "rows"}, "do": "An_${r.v}"}], scope) == \
        ["An_AGE", "An_SEX"]
    assert evaluate({"$dict": "r", "in": {"$get": "rows"}, "key": {"$get": "r.v"}, "value": 1},
                    scope) == {"AGE": 1, "SEX": 1}
    assert evaluate({"$pick": {"$get": "mode"}, "from": {"x": "chosen"}}, scope) == "chosen"
    assert evaluate({"a": {"$if": {"get": "mode", "eq": "y"}, "then": 1}}, scope) == {}
    assert names_used({"a": "${days}", "b": {"$for": "r", "in": {"$get": "rows"}, "do": "${r.v}"},
                       "c": {"$if": {"get": "mode", "eq": 1}, "then": 0}}) == \
        {"days", "rows", "mode"}


@pytest.mark.parametrize("node", [
    {"$get": "missing"}, "${missing}", {"$nope": 1}, {"$fn": "nope"},
    {"$pick": "z", "from": {"x": 1}}, "${rows}",
    {"$if": {"get": "mode", "eq": "y"}, "then": 1},  # a dropped branch at the top
])
def test_template_errors(node):
    with pytest.raises(TemplateError):
        evaluate(node, {"mode": "x", "rows": [1]})


def test_helpers():
    assert cut_labels([18, 65]) == ["<18", "18-<65", ">=65"]
    with pytest.raises(TemplateError):
        cut_labels([65, 18])
    windows = midpoint_windows([{"visit": "W2", "target": 15}, {"visit": "W4", "target": 30}])
    assert windows == [{"visit": "W2", "target": 15, "low": 2, "high": 22},
                       {"visit": "W4", "target": 30, "low": 23, "high": None}]


def test_predicates():
    tree = predicate.parse("design.a and (design.b or not design.c)")
    assert predicate.names(tree) == {"design.a", "design.b", "design.c"}
    assert predicate.evaluate(tree, {"design.a": True, "design.b": False, "design.c": False})
    assert not predicate.evaluate(tree, {"design.a": True, "design.b": False, "design.c": True})
    for bad in ("", "design.a and", "(design.a", "design.a design.b", "and", "Design.A", "a & b"):
        with pytest.raises(predicate.PredicateError):
            predicate.parse(bad)
    with pytest.raises(predicate.PredicateError):
        predicate.evaluate(tree, {"design.a": True})


def test_every_entry_applies_to_the_parallel_group_archetype(catalog):
    features = {name: True for name in catalog.design_features}
    for entry in catalog.entries.values():
        assert predicate.evaluate(predicate.parse(entry.applies_when), features), entry.id


# -- compile -----------------------------------------------------------------


def test_compile_is_deterministic_and_complete(catalog, house, base, tmp_path):
    reference = relative_reference(house.directory, tmp_path / "adam")
    first = compile_decisions(catalog, house, base, reference)
    second = compile_decisions(catalog, house, list(reversed(base)), reference)
    assert first.files == second.files  # rule R4: the order of the records does not matter
    assert first.datasets == ["ADSL", "ADAE", "ADVS"]
    assert first.families == ["tfl-demographics", "tfl-ae-summary", "tfl-ae-soc-pt",
                              "tfl-vitals-by-visit"]
    first.write(tmp_path)
    manifest = json.loads((tmp_path / "compile.json").read_text(encoding="ascii"))
    assert sorted(manifest["files"]) == sorted(first.files)
    entry = yaml.safe_load((tmp_path / "adam" / "adae.yaml").read_text(encoding="ascii"))
    assert entry["parent"].endswith("standard/houses/open-default@1/adam/adae.yaml")
    assert "fragments/adae/ae.teae.end.yaml" in entry["include"]
    assert all(text.isascii() for text in first.files.values())


def test_a_fragment_is_a_pure_function_of_the_value(catalog, house, base, tmp_path):
    reference = relative_reference(house.directory, tmp_path / "adam")
    value = {"rule": "last_dose_plus_days", "days": 30}
    compiled = compile_decisions(catalog, house, changed(base, "ae.teae.end", value), reference)
    fragment = yaml.safe_load(compiled.files["adam/fragments/adae/ae.teae.end.yaml"])
    names = [column["name"] for column in fragment["columns"]]
    assert names == ["_TEENDDT", "_TEEND"]
    assert fragment["columns"][0]["derivation"] == \
        {"shift": {"type": "date", "source": "TRTEDT", "days": 30}}
    assert compiled.binds[("ae.teae.end", "mod-ae-emergence")] == \
        ["adam:ADAE._TEEND", "adam:ADAE._TEENDDT"]
    other = compile_decisions(catalog, house, changed(base, "ae.teae.end", {**value, "days": 7}),
                              reference)
    differing = {path for path in compiled.files if compiled.files[path] != other.files.get(path)}
    assert differing == {"adam/fragments/adae/ae.teae.end.yaml"}


def test_binds_are_proven_by_mutation(root, catalog, house, base, tmp_path):
    """A decision binds what changes when the decision changes, and nothing else."""
    reference = relative_reference(house.directory, tmp_path / "adam")
    compiled = compile_decisions(catalog, house, base, reference)
    assert compiled.binds[("ae.teae.end", "mod-ae-emergence")] == ["adam:ADAE._TEEND"]
    bind_tables(catalog, house, base, compiled, reference)
    for record in base:
        key = (record["id"], record["unit"])
        full = {**record, "status": "stated", "class": "document_rule",
                "citations": [{"doc": "sap", "anchor": "1/s1", "quote": "x"}],
                "binds": compiled.binds.get(key, [])}
        assert schemas.problems("decision-record", full, root=root) == []
    binds, layout = compiled.binds, compiled.layout_binds
    assert binds[("ae.teae.end", "mod-ae-emergence")] == ["adam:ADAE._TEEND"]
    # Leaving an output out removes all of it, and nothing of another output.
    include = binds[("tfl.output.include", "tfl-ae-soc-pt")]
    assert {"ars:Out_AESOCPT", "ars:An_AESOCPT_Pt", "ars:Grp_AEDECOD"} <= set(include)
    assert not any(bind.startswith(("ars:An_DM_", "ars:An_AESUM_")) for bind in include)
    # A list of rows binds the analyses of each row: any row can be left out.
    rows = binds[("tfl.demog.rows", "tfl-demographics")]
    assert {"ars:An_DM_AGE_Summ", "ars:An_DM_SEX_Summ", "ars:Grp_SEX"} <= set(rows)
    assert "ars:An_DM_N" not in rows
    # The analysis set of the demographics table: its analyses and the set only it uses.
    population = binds[("tfl.population", "tfl-demographics")]
    assert {"ars:An_DM_N", "ars:AnalysisSet_ITT"} <= set(population)
    assert "ars:AnalysisSet_SAF" not in binds[("tfl.population", "tfl-ae-summary")]
    # The quantile definition reaches continuous summaries, not categorical ones.
    quantile = binds[("tfl.quantile.definition", "tfl-demographics")]
    assert "ars:An_DM_AGE_Summ" in quantile and "ars:An_DM_SEX_Summ" not in quantile
    # The total column: the total analyses and their grouping, not the analyses by arm.
    total = binds[("tfl.columns.total", "tfl-ae-summary")]
    assert {"ars:An_AESUM_ANY_Tot", "ars:Grp_Total_AESUM"} <= set(total)
    assert "ars:An_AESUM_ANY" not in total
    # Statistics with quartiles: another method for the continuous rows, and the layout rows.
    assert "ars:An_DM_AGE_Summ" in binds[("tfl.demog.stats", "tfl-demographics")]
    assert layout[("tfl.demog.stats", "tfl-demographics")] == ["layout:tfl-demographics/rows"]
    # A display rule binds a layout part and no ARS element.
    assert ("tfl.rounding.rule", "tfl-ae-summary") not in binds
    assert layout[("tfl.rounding.rule", "tfl-ae-summary")] == ["layout:tfl-ae-summary/formats"]
    # The safety grouping reaches the three safety outputs, not the demographics table.
    shared = binds[("pop.safety.grouping", "mod-populations")]
    assert "ars:An_AESUM_N" in shared and "ars:An_DM_N" not in shared
    # Without a comparison the p-value format decides nothing in this study.
    assert ("tfl.pvalue.format", "tfl-demographics") not in binds
    assert ("tfl.pvalue.format", "tfl-demographics") not in layout


def test_the_ars_file_holds_no_display_format(catalog, house, base, tmp_path):
    """Display formats are decisions of the layout; the ARS file states none (ADR-004)."""
    compiled = compile_decisions(catalog, house, base,
                                 relative_reference(house.directory, tmp_path / "adam"))
    assert "resultPattern" not in compiled.files["ars/reporting-event.json"]
    methods = {m["id"]: [o["id"] for o in m["operations"]] for m in compiled.ars["methods"]}
    assert "Mth_ContSummQ" not in methods  # no quartiles under the default statistics
    assert len(methods["Mth_ContSumm"]) == 6


def test_compile_problems_are_reported_together(catalog, house, base, tmp_path):
    reference = relative_reference(house.directory, tmp_path / "adam")
    broken = changed(changed(base, "ae.teae.end", None), "trt.start.source", {"rule": "guess"})
    with pytest.raises(CompileError) as error:
        compile_decisions(catalog, house, broken, reference)
    assert any("trt.start.source" in problem for problem in error.value.problems)
    with pytest.raises(CompileError, match="ADAE: no value for ae.teae.end"):
        compile_decisions(catalog, house, changed(base, "ae.teae.end", None), reference)
    with pytest.raises(CompileError, match="more than one record"):
        compile_decisions(catalog, house, base + base[:1], reference)
    custom = [{"id": "custom:shift-high-rule", "unit": "tfl-lab-shift", "value": {"rule": "x"}}]
    with pytest.raises(CompileError, match="hand-written fragment"):
        compile_decisions(catalog, house, base + custom, reference)
    # Never guess (section 5.2, rule 4): whether an output is planned must be said.
    silent = [r for r in base if (r["id"], r["unit"]) != ("tfl.output.include", "tfl-ae-soc-pt")]
    with pytest.raises(CompileError, match="tfl-ae-soc-pt: no value for tfl.output.include"):
        compile_decisions(catalog, house, silent, reference)


def test_an_optional_decision_leaves_its_column_out(catalog, house, base, tmp_path):
    reference = relative_reference(house.directory, tmp_path / "adam")
    without = [r for r in base if r["id"] != "pop.efficacy.rule"]
    compiled = compile_decisions(catalog, house, without, reference)
    assert "EFFFL" not in compiled.adam_columns["ADSL"]
    efficacy = changed(without, "tfl.population", {"rule": "efficacy"}, "tfl-vitals-by-visit")
    with pytest.raises(CompileError, match="ADSL.EFFFL, which no decision of the study writes"):
        compile_decisions(catalog, house, efficacy, reference)


def test_an_output_that_is_not_included_is_not_compiled(catalog, house, base, tmp_path):
    reference = relative_reference(house.directory, tmp_path / "adam")
    records = changed(base, "tfl.output.include", {"rule": "not_included"}, "tfl-ae-soc-pt")
    compiled = compile_decisions(catalog, house, records, reference)
    assert "tfl-ae-soc-pt" not in compiled.families
    assert "layout/tfl-ae-soc-pt.json" not in compiled.files
    assert [o["id"] for o in compiled.ars["outputs"]] == ["Out_DM", "Out_AESUM", "Out_VS"]
    assert not any(a["id"].startswith("An_AESOCPT") for a in compiled.ars["analyses"])


# -- house standard ----------------------------------------------------------


def test_the_standards_document_states_every_default(root, catalog, house):
    text = house_module.standards_document(catalog, house)
    assert (house.directory / "STANDARD.md").read_text(encoding="ascii") == text
    records = house_module.default_decisions(catalog, house)
    assert len(records) == len(house_module.defaults(catalog, house)) >= 50
    for record in records:
        assert record["status"] == "default" and record["class"] == "house_default"
        assert record["citations"][0]["doc"] == "house"
        assert schemas.problems("decision-record", record, root=root) == []
    for entry_id, _ in house_module.without_default(catalog):
        assert f"`{entry_id}`" in text


# -- the compiled specs run --------------------------------------------------


def _rows(path, key):
    return {tuple(row[k] for k in key): row for row in pq.read_table(path).to_pylist()}


def test_the_base_decisions_build_the_tiny_study(catalog, house, base, tmp_path):
    """yamaa builds ADSL, ADAE and ADVS from the compiled specs; values follow the statements."""
    tiny.write(tmp_path / "sdtm")
    reference = relative_reference(house.directory, tmp_path / "spec" / "adam")
    compiled = compile_decisions(catalog, house, base, reference,
                                 sdtm_dir="../../sdtm", adam_dir="../../adam")
    compiled.write(tmp_path / "spec")
    (tmp_path / "adam").mkdir()
    for dataset in compiled.datasets:
        spec = tmp_path / "spec" / "adam" / f"{dataset.lower()}.yaml"
        assert checks.yamaa_check(spec) == []
        assert checks.yamaa_run(spec) == []
        written = pq.read_table(tmp_path / "adam" / f"{dataset.lower()}.parquet")
        assert written.column_names == compiled.adam_columns[dataset]

    adsl = _rows(tmp_path / "adam" / "adsl.parquet", ["USUBJID"])
    s1, s2, s3 = adsl[("S1",)], adsl[("S2",)], adsl[("S3",)]
    assert str(s1["TRTSDT"]) == "2024-03-10" and str(s1["TRTEDT"]) == "2024-04-20"
    assert (s1["SAFFL"], s2["SAFFL"], s3["SAFFL"]) == ("Y", "Y", "N")  # S3 was never dosed
    assert (s1["ITTFL"], s3["ITTFL"]) == ("Y", "Y")
    assert (s1["AGEGR1"], s2["AGEGR1"], s3["AGEGR1"]) == ("65-80", "65-80", ">80")  # 65, 80, 81
    assert (s1["EOSSTT"], s2["EOSSTT"], s3["EOSSTT"]) == ("COMPLETED", "DISCONTINUED", "ONGOING")
    assert s2["DCSREAS"] == "ADVERSE EVENT"
    assert (s1["WEIGHTBL"], s1["HEIGHTBL"], s1["BMIBL"]) == (71.0, 170.0, 24.6)

    adae = _rows(tmp_path / "adam" / "adae.parquet", ["USUBJID", "AESEQ"])
    assert adae[("S1", 1)]["TRTEMFL"] is None      # ended before the first dose
    assert adae[("S1", 2)]["TRTEMFL"] == "Y"       # starts on the first dose date
    assert adae[("S1", 2)]["ASTDY"] == 1 and adae[("S1", 1)]["ASTDY"] == -5  # no day 0
    assert str(adae[("S2", 1)]["ASTDT"]) == "2024-03-12"  # 2024-03 moved to the first dose date
    assert adae[("S2", 1)]["ASTDTF"] == "D"
    assert adae[("S3", 1)]["TRTEMFL"] is None      # not treated
    assert adae[("S1", 3)]["RELGR1"] == "RELATED" and adae[("S1", 2)]["RELGR1"] == "NOT RELATED"

    advs = _rows(tmp_path / "adam" / "advs.parquet", ["USUBJID", "PARAMCD", "VSSEQ", "DTYPE"])
    assert advs[("S1", "SYSBP", 2, "")]["ABLFL"] == "Y"      # 07:30, before the dose at 08:00
    assert advs[("S1", "SYSBP", 3, "")]["ABLFL"] is None     # 09:00, after the dose
    assert advs[("S1", "WEIGHT", 9, "")]["ABLFL"] == "Y"     # first dose date, no time
    assert advs[("S2", "SYSBP", 1, "")]["ABLFL"] == "Y"      # only an unscheduled value (E26)
    week2 = advs[("S1", "SYSBP", 4, "")]
    assert (week2["AVISIT"], week2["ANL01FL"], week2["BASE"], week2["CHG"]) == \
        ("WEEK 2", "Y", 124.0, 4.0)
    assert advs[("S1", "SYSBP", 5, "")]["AVISIT"] is None    # unscheduled: no nominal visit
    eot = advs[("S1", "SYSBP", 6, "LOV")]                    # last value up to 2024-04-20
    assert (eot["AVISIT"], eot["AVAL"], eot["ANL01FL"]) == ("End of Treatment", 122.0, "Y")
    assert ("S1", "SYSBP", 7, "LOV") not in advs             # 2024-04-25 is after the last dose


def test_the_overview_names_every_entry_and_alternative(catalog, house):
    text = overview.render(catalog, house)
    assert text.isascii()
    for entry in catalog.entries.values():
        assert f"### `{entry.id}`: {entry.question}" in text
        for alternative in entry.alternatives:
            assert f"| `{alternative.id}` | " in text
    for name in catalog.raw["deferred"]:
        assert f"- `{name}`: " in text
