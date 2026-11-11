"""Canonical writers: the same content gives the same bytes (rule R4, property P1)."""

from __future__ import annotations

import pytest

from specfirst.machine import canonical

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")


def test_json_text_is_sorted_ascii_and_compact():
    accented = "caf" + chr(233)  # this file itself stays ASCII (rule R10)
    assert canonical.json_text({"b": [1, 2.5, None], "a": accented}) == (
        '{"a":"caf\\u00e9","b":[1,2.5,null]}'
    )


def test_json_text_refuses_nan():
    with pytest.raises(ValueError):
        canonical.json_text({"value": float("nan")})


def test_content_hash_does_not_depend_on_key_order():
    assert canonical.content_hash({"a": 1, "b": 2}) == canonical.content_hash({"b": 2, "a": 1})
    assert canonical.content_hash({"a": 1}) != canonical.content_hash({"a": 2})


def test_jsonl_round_trip(tmp_path):
    records = [{"id": "b", "n": 1}, {"id": "a", "n": 2}]
    path = tmp_path / "deep" / "records.jsonl"
    canonical.write_jsonl(path, records)
    assert path.read_bytes() == b'{"id":"b","n":1}\n{"id":"a","n":2}\n'
    assert canonical.read_jsonl(path) == records
    canonical.write_jsonl(path, [])
    assert path.read_bytes() == b""


def table(**changes):
    columns = {
        "ID": pa.array(["a", "b", "c"]),
        "N": pa.array([1.0, None, 3.5]),
        "D": pa.array([0, 1, None], pa.date32()),
    }
    columns.update(changes)
    return pa.table(columns)


def written(tmp_path, name, value) -> bytes:
    canonical.write_parquet(tmp_path / name, value)
    return (tmp_path / name).read_bytes()


def test_same_table_gives_the_same_parquet_bytes(tmp_path):
    assert written(tmp_path, "one.parquet", table()) == written(tmp_path, "two.parquet", table())


def test_metadata_storage_type_and_chunks_do_not_change_the_bytes(tmp_path):
    plain = written(tmp_path, "plain.parquet", table())
    decorated = table(ID=pa.array(["a", "b", "c"], pa.large_string()))
    decorated = decorated.replace_schema_metadata({"pandas": "{}"})
    fields = [field.with_metadata({"yamaa:label": "x"}) for field in decorated.schema]
    decorated = decorated.cast(pa.schema(fields, metadata={"pandas": "{}"}))
    assert written(tmp_path, "decorated.parquet", decorated) == plain
    chunked = pa.concat_tables([table().slice(0, 1), table().slice(1)])
    assert chunked.column("ID").num_chunks == 2
    assert written(tmp_path, "chunked.parquet", chunked) == plain
    encoded = table(ID=pa.array(["a", "b", "c"]).dictionary_encode())
    assert written(tmp_path, "encoded.parquet", encoded) == plain


def test_a_changed_value_changes_the_bytes(tmp_path):
    plain = written(tmp_path, "plain.parquet", table())
    assert written(tmp_path, "value.parquet", table(N=pa.array([1.0, None, 3.6]))) != plain
    assert written(tmp_path, "null.parquet", table(N=pa.array([1.0, 0.0, 3.5]))) != plain
    renamed = table().rename_columns(["ID", "M", "D"])
    assert written(tmp_path, "name.parquet", renamed) != plain


def test_canonical_table_keeps_values_and_logical_types():
    source = table(ID=pa.array(["a", None, "c"], pa.large_string()))
    result = canonical.canonical_table(source)
    assert result.schema.names == ["ID", "N", "D"]
    assert [str(field.type) for field in result.schema] == ["string", "double", "date32[day]"]
    assert result.schema.metadata is None
    assert result.to_pylist() == source.to_pylist()


def test_sha256_file(tmp_path):
    path = tmp_path / "x.bin"
    path.write_bytes(b"abc")
    expected = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert canonical.sha256_file(path) == expected == canonical.sha256_bytes(b"abc")
