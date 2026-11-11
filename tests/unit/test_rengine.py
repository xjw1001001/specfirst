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
