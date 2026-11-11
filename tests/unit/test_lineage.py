"""Static column dependencies of a composed specification (no engine needed)."""

from __future__ import annotations

from specfirst.machine.lineage import column_dependencies, pointer

SCHEMAS = {"DM": {"USUBJID", "AGE", "ARM"}, "VS": {"USUBJID", "VSTESTCD", "VSSTRESN", "VISITNUM"}}


def spec(**changes) -> dict:
    data = {
        "base": "DM",
        "input": {"DM": {"path": "dm.parquet"}, "VS": {"path": "vs.parquet"}},
        "output": {"columns": ["USUBJID", "AGEGR1", "HEIGHT", "FLAG"]},
        "intermediates": [{
            "id": "BASE_HT", "dataset": "VS", "key": ["USUBJID"],
            "filter": "VS.VSTESTCD = 'HEIGHT'",
            "order_by": [{"variable": "VS.VISITNUM", "direction": "asc", "nulls": "last"}],
            "keep": "first",
        }],
        "columns": [
            {"name": "USUBJID", "derivation": {"value": "DM.USUBJID"}},
            {"name": "AGE_N", "derivation": {"value": "DM.AGE"}},
            {"name": "AGEGR1", "derivation": {"value": {"case": [
                {"when": "AGE_N < 65 AND DM.ARM IS NOT NULL", "then": "'<65'"},
                {"otherwise": "'>=65'"},
            ]}}},
            {"name": "HEIGHT", "derivation": {"value": "ROUND(BASE_HT.VSSTRESN, 1)"}},
            {"name": "FLAG", "derivation": {"value": "'Y'"}},
        ],
    }
    data.update(changes)
    return data


def reads_of(lineage, element):
    return [read for read in lineage.reads if read.element == element]


def test_columns_helpers_and_intermediates():
    lineage = column_dependencies(spec(), SCHEMAS)
    edges = lineage.edges()
    assert edges["spec.USUBJID"] == ["DM.USUBJID"]
    assert edges["spec.AGEGR1"] == ["DM.ARM", "spec.AGE_N"]  # the helper, not DM.AGE directly
    assert edges["spec.AGE_N"] == ["DM.AGE"]
    assert edges["spec.HEIGHT"] == ["BASE_HT.VSSTRESN"]  # ROUND is a function, not a name
    assert edges["BASE_HT.VSSTRESN"] == ["VS.VSSTRESN", "intermediate.BASE_HT"]
    # Key, filter and order of the lookup are context dependencies.
    assert edges["intermediate.BASE_HT"] == [
        "VS.USUBJID", "VS.VISITNUM", "VS.VSTESTCD", "spec.USUBJID"
    ]
    assert edges["spec.FLAG"] == []  # a literal reads nothing
    assert edges["output.FLAG"] == ["spec.FLAG"]
    assert lineage.outputs == ("USUBJID", "AGEGR1", "HEIGHT", "FLAG")
    assert all(not read.unresolved and not read.unknown for read in lineage.reads)


def test_every_read_names_its_place():
    lineage = column_dependencies(spec(), SCHEMAS)
    assert [read.pointer for read in reads_of(lineage, "spec.AGEGR1")] == ["/columns/2/derivation"]
    assert reads_of(lineage, "intermediate.BASE_HT")[0].pointer == "/intermediates/0"
    assert reads_of(lineage, "BASE_HT.VSSTRESN")[0].pointer == "/intermediates/0"
    assert pointer("rows", 3, "derivations", "A/B~C") == "/rows/3/derivations/A~1B~0C"


def test_row_templates_define_columns_per_row():
    rows = [
        {"id": "raw", "dataset": "VS", "filter": "VS.VSTESTCD = 'HEIGHT'",
         "derivations": {"AVAL": {"value": "VS.VSSTRESN"}, "DTYPE": {"value": "''"}}},
        {"id": "mean", "dataset": "VS", "group_by": ["VS.USUBJID"],
         "derivations": {"AVAL": {"value": {"aggregate": {"expr": "MEAN(VS.VSSTRESN)"}}},
                         "DTYPE": {"value": "'AVERAGE'"}}},
    ]
    data = spec(
        base="VS", rows=rows, intermediates=[],
        output={"columns": ["USUBJID", "AVAL", "DTYPE"]},
        columns=[{"name": "USUBJID", "derivation": {"value": "VS.USUBJID"}},
                 {"name": "AVAL"}, {"name": "DTYPE"}],
    )
    lineage = column_dependencies(data, SCHEMAS)
    assert [read.pointer for read in reads_of(lineage, "spec.AVAL")] == [
        "/rows/0/derivations/AVAL", "/rows/1/derivations/AVAL"
    ]
    edges = lineage.edges()
    assert edges["spec.AVAL"] == ["VS.VSSTRESN", "row.mean", "row.raw"]
    assert edges["spec.DTYPE"] == ["row.mean", "row.raw"]
    assert edges["row.raw"] == ["VS.VSTESTCD"]
    assert edges["row.mean"] == ["VS.USUBJID"]
    assert lineage.defined == {"USUBJID", "AVAL", "DTYPE"}


def test_a_column_without_a_derivation_is_not_defined():
    data = spec(columns=[*spec()["columns"], {"name": "ORPHAN"}],
                output={"columns": ["USUBJID", "ORPHAN"]})
    lineage = column_dependencies(data, SCHEMAS)
    assert "ORPHAN" not in lineage.defined and "USUBJID" in lineage.defined
    assert [read.pointer for read in reads_of(lineage, "spec.ORPHAN")] == ["/columns/5"]


def change_derivation(index: int, value) -> dict:
    columns = [dict(column) for column in spec()["columns"]]
    columns[index]["derivation"] = {"value": value}
    return spec(columns=columns)


def test_planted_unknown_references_are_recorded_where_they_are_read():
    lineage = column_dependencies(change_derivation(3, "DM.NO_SUCH + NOWHERE.X"), SCHEMAS)
    (read,) = reads_of(lineage, "spec.HEIGHT")
    assert read.unresolved == {"DM.NO_SUCH", "NOWHERE.X"} and not read.refs
    assert all(not r.unresolved for r in lineage.reads if r.element != "spec.HEIGHT")

    lineage = column_dependencies(change_derivation(3, "HEIGTH_RAW * 2"), SCHEMAS)
    (read,) = reads_of(lineage, "spec.HEIGHT")
    assert read.unknown == {"HEIGTH_RAW"} and not read.unresolved


def test_keywords_literals_and_functions_are_not_names():
    expression = (
        "CASE_FN(DM.AGE) IN (1, 2) AND NOT DM.ARM LIKE 'Dm.AGE and AGE_N' OR DM.ARM IS NULL"
    )
    lineage = column_dependencies(change_derivation(4, expression), SCHEMAS)
    (read,) = reads_of(lineage, "spec.FLAG")
    assert read.refs == {"DM.AGE", "DM.ARM"} and not read.unknown and not read.unresolved


def test_a_dataset_read_as_a_whole_is_recorded():
    value = {"aggregate": {"expr": "COUNT(VS.*)", "filter": "VS.VSTESTCD = 'HEIGHT'"}}
    lineage = column_dependencies(change_derivation(4, value), SCHEMAS)
    (read,) = reads_of(lineage, "spec.FLAG")
    assert read.whole == {"VS"} and not read.unknown
    assert "VS.VSTESTCD" in read.refs


def test_mapping_dictionaries_and_templates():
    mapping = {"mapping": {"source": {"variable": "DM.ARM"}, "dict": {"DM.AGE": "AGE_N"},
                           "unmapped": "AGE_N"}}
    lineage = column_dependencies(change_derivation(4, mapping), SCHEMAS)
    assert reads_of(lineage, "spec.FLAG")[0].refs == {"DM.ARM"}  # the dictionary holds literals

    template = {"str_template": {"template": "{AGE_N} years, arm {DM.ARM}, {{literal}}"}}
    lineage = column_dependencies(change_derivation(4, template), SCHEMAS)
    assert reads_of(lineage, "spec.FLAG")[0].refs == {"spec.AGE_N", "DM.ARM"}
