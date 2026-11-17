"""What is handed to the R engine, and the proof that it read the same values."""

from __future__ import annotations

import json

import pytest
import toy_results as toy

from specfirst.machine import ard, rengine

pa = pytest.importorskip("pyarrow")


def table() -> ard.Table:
    return ard.table_from_arrow("X", pa.table({
        "TEXT": ["a", None, "CARD / heart", ""],
        "NUMBER": [0.1, None, 15.116279069767442, -0.0],
        "WHOLE": pa.array([1, 2, None, 4], pa.int64()),
    }))


def test_the_handover_loses_nothing():
    text = rengine.handover_text(table())
    assert text.isascii() and text.endswith("\n")
    data = json.loads(text)
    assert (data["dataset"], data["rows"]) == ("X", 4)
    columns = {column["name"]: column for column in data["columns"]}
    assert columns["TEXT"] == {"name": "TEXT", "kind": "text",
                               "values": ["a", None, "CARD / heart", None]}
    assert columns["NUMBER"]["values"] == [0.1, None, 15.116279069767442, -0.0]
    assert columns["WHOLE"] == {"name": "WHOLE", "kind": "number", "values": [1.0, 2.0, None, 4.0]}
    assert "0.1,null,15.116279069767442,-0.0" in text  # the shortest decimals, not rounded


def test_fingerprints_change_with_any_value():
    first = rengine.fingerprints({"X": table()})
    assert sorted(first) == ["X.NUMBER", "X.TEXT", "X.WHOLE"]
    other = table()
    other.columns["NUMBER"][0] = 0.1 + 2e-17  # the next double
    changed = rengine.fingerprints({"X": other})
    assert changed["X.NUMBER"] != first["X.NUMBER"] and changed["X.TEXT"] == first["X.TEXT"]
    # A missing value is not the text "NA", and not a zero.
    other = table()
    other.columns["NUMBER"][1] = 0.0
    assert rengine.fingerprints({"X": other})["X.NUMBER"] != first["X.NUMBER"]
    assert rengine.data_problems({"columns": first}, {"X": table()}) == []
    assert rengine.data_problems({"columns": {**changed, "X.MORE": "0"}}, {"X": table()}) == [
        "column X.NUMBER: the R engine read other values",
        "column X.MORE: read by the R engine only"]
    del changed["X.TEXT"]
    assert "column X.TEXT: not read by the R engine" in rengine.data_problems(
        {"columns": changed}, {"X": table()})


def test_the_r_engine_reads_what_was_handed_over(root, tmp_path):
    if not rengine.available():
        pytest.skip("Rscript is not installed")
    from specfirst.machine import ars, registry

    event = ars.index(toy.event_data())
    known = registry.load(root)
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event.data), encoding="ascii")
    # Text with a blank, a slash and a letter outside ASCII (U+0153), and a number
    # that needs 17 digits. The new organ class adds a group: 74 rows, not 67.
    adsl = dict(toy.ADSL, SEX=["F", "F", "M", "M", "F", "M", "M", None],
                AGE=[61.0, 70.0, 55.0, None, 64.0, 72.0, 80.1, 0.30000000000000004])
    adae = dict(toy.ADAE, AESOC=["CARD / c" + chr(0x153) + "ur", *toy.ADAE["AESOC"][1:]])
    tables = toy.tables(adsl=adsl, adae=adae)
    rows, meta, _ = rengine.run(root, tmp_path / "work", path, registry.json_path(root),
                                ars.bind(event, known), tables, "USUBJID")
    assert rengine.data_problems(meta, tables) == []
    assert meta["engine"] == "r" and meta["rows"] == len(rows) == 74
    ours = ard.run(event, known, ars.bind(event, known), tables)
    assert [row["id"] for row in rows] == [row["id"] for row in ours]
    encoded = [row["id"] for row in rows if "c%C5%93ur" in row["id"]]
    assert "ard:A_SOC/M_CAT_n/Arm_A/=CARD%20%2F%20c%C5%93ur/=AF" in encoded


def test_a_failing_r_engine_is_an_error(root, tmp_path):
    if not rengine.available():
        pytest.skip("Rscript is not installed")
    from specfirst.machine import ars, registry

    data = toy.event_data()
    data["analyses"][2]["variable"] = "SEX"  # a summary of text
    event = ars.index(data)
    known = registry.load(root)
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event.data), encoding="ascii")
    with pytest.raises(rengine.REngineError, match="holds text; this method needs numbers"):
        rengine.run(root, tmp_path / "work", path, registry.json_path(root),
                    ars.bind(event, known), toy.tables(), "USUBJID")


# ---- the two engines on the edges of rules I3 and I9 (review of real-2, F5 and F11) ----


def both_engines(root, work, data, tables):
    """The rows of the Python and of the R engine for one event on the same tables."""
    from specfirst.machine import ars, registry, results

    event = ars.index(data)
    assert event.problems == [], event.problems
    known = registry.load(root)
    path = work / "event.json"
    work.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(event.data), encoding="ascii")
    binding = ars.bind(event, known)
    ours = results.by_id(ard.run(event, known, binding, tables))
    rows, meta, _ = rengine.run(root, work, path, registry.json_path(root), binding, tables,
                                "USUBJID")
    assert rengine.data_problems(meta, tables) == []
    return ours, results.by_id(rows)


# Rule I3 on all eight subjects of the toy study. Ages: arm A 61, 70, 55 and one
# missing; arm B 64, 72, 80, 50. Sex: arm A F, F, M, M; arm B F, M, M and one missing.
I3_CASES = [
    ("AGE", "EQ", ["61"], (1, 0)),
    ("AGE", "NE", ["61"], (3, 4)),  # true for the missing age
    ("AGE", "IN", ["61", "64"], (1, 1)),
    ("AGE", "NOTIN", ["61", "64"], (3, 3)),  # true for the missing age
    ("AGE", "GT", ["64"], (1, 2)),
    ("AGE", "GE", ["64"], (1, 3)),
    ("AGE", "LT", ["61"], (1, 1)),  # false for the missing age
    ("AGE", "LE", ["6.1e1"], (2, 1)),  # a number with an exponent
    ("SEX", "NE", ["F"], (2, 3)),  # true for the missing sex
    ("SEX", "NOTIN", ["F", "M"], (0, 1)),
    ("SEX", "GE", ["M"], (2, 2)),  # false for the missing sex
    ("SEX", "EQ", [""], (0, 1)),  # the empty text stands for the missing value
    ("SEX", "NE", [""], (4, 3)),
]


def test_both_engines_follow_rule_i3(root, tmp_path):
    if not rengine.available():
        pytest.skip("Rscript is not installed")
    from specfirst.machine import results

    data = toy.event_data()
    for number, (variable, comparator, values, _) in enumerate(I3_CASES, start=1):
        data["dataSubsets"].append({"id": f"C{number}", "name": f"case {number}",
                                    **toy.condition("ADSL", variable, comparator, *values)})
        data["analyses"].append(toy.analysis(f"A_C{number}", "M_N", "ADSL", "USUBJID",
                                             [("ARM", True)], dataSubsetId=f"C{number}"))
    ours, theirs = both_engines(root, tmp_path, data, toy.tables())
    for number, (variable, comparator, values, expected) in enumerate(I3_CASES, start=1):
        found = tuple(ours[f"ard:A_C{number}/M_N_n/Arm_{arm}"]["raw_value"] for arm in "AB")
        assert found == expected, (variable, comparator, values)
    assert results.agreement(ours, theirs)[1] == []
    assert len(I3_CASES) >= 10


@pytest.mark.parametrize("value", ["0x3D", "6_1", "nan", " 61", "061", "1e999", ".5"])
def test_both_engines_refuse_what_is_not_a_number(root, tmp_path, value):
    """Rule I3: a number is written as in JSON. Python alone took 6_1, R alone 0x3D."""
    if not rengine.available():
        pytest.skip("Rscript is not installed")
    from specfirst.machine import ars, registry

    data = toy.event_data()
    data["dataSubsets"].append({"id": "C", "name": "c",
                                **toy.condition("ADSL", "AGE", "EQ", value)})
    data["analyses"] = [toy.analysis("A_C", "M_N", "ADSL", "USUBJID", [("ARM", True)],
                                     dataSubsetId="C")]
    event = ars.index(data)
    known = registry.load(root)
    binding = ars.bind(event, known)
    message = "not a finite number" if value == "1e999" else "a number is written as in JSON"
    with pytest.raises(ard.EngineError, match=message):
        ard.run(event, known, binding, toy.tables())
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event.data), encoding="ascii")
    with pytest.raises(rengine.REngineError, match=message):
        rengine.run(root, tmp_path / "work", path, registry.json_path(root), binding,
                    toy.tables(), "USUBJID")


def test_a_condition_value_that_is_not_text_is_a_problem_of_the_event():
    from specfirst.machine import ars

    data = toy.event_data()
    data["dataSubsets"][0]["condition"]["value"] = [1.0]
    assert "data subset 'TEAE': a condition has a value that is not text" in ars.index(
        data).problems


def test_both_engines_write_a_number_as_a_group_value_the_same_way(root, tmp_path):
    """Rule I9. Until real-3a R wrote 1e+15 and -0, and read the text "NA" as missing."""
    if not rengine.available():
        pytest.skip("Rscript is not installed")
    from specfirst.machine import results

    ages = [1e15, 0.0, -0.0, 5e-324, 0.1, 1.5e-07, 1e22, 61.0]
    adsl = dict(toy.ADSL, AGE=ages, SEX=["NA"] * 8, SAFFL=["Y"] * 8)
    # A control character (U+0001) and a quotation mark in a group value.
    adae = dict(toy.ADAE, AESOC=["CARD" + chr(1) + '"x"', *toy.ADAE["AESOC"][1:]])
    data = toy.event_data()
    data["analysisGroupings"] += [
        {"id": "BYAGE", "name": "Age", "groupingDataset": "ADSL", "groupingVariable": "AGE",
         "dataDriven": True},
        {"id": "BYSEX", "name": "Sex as it is", "groupingDataset": "ADSL",
         "groupingVariable": "SEX", "dataDriven": True}]
    data["analyses"] += [
        toy.analysis("A_BYAGE", "M_N", "ADSL", "USUBJID", [("BYAGE", True)]),
        toy.analysis("A_BYSEX", "M_N", "ADSL", "USUBJID", [("BYSEX", True)])]
    ours, theirs = both_engines(root, tmp_path, data, toy.tables(adsl=adsl, adae=adae))
    by_age = {row["group1_groupValue"]: row["raw_value"] for key, row in ours.items()
              if key.startswith("ard:A_BYAGE/")}
    assert by_age == {"1000000000000000": 1, "0": 2, "5e-324": 1, "0.1": 1, "1.5e-07": 1,
                      "10000000000000000000000": 1, "61": 1}
    assert ours["ard:A_BYSEX/M_N_n/=NA"]["raw_value"] == 8
    assert any("%01%22x%22" in key for key in ours)
    assert sorted(ours) == sorted(theirs)
    assert results.agreement(ours, theirs)[1] == []
