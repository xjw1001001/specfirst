"""Canonical serializers: the same content gives the same bytes (PLAN.md rule R4).

Every file the machine builds is written through this module, so that two
builds can be compared by hash (property P1 of section 4.6). Nothing here
reads a clock or depends on the order of a dict or a set.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pyarrow is loaded only by the functions that need it
    import pyarrow as pa


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def json_text(value: object) -> str:
    """One line of JSON: sorted keys, ASCII, no spaces, no NaN."""
    return json.dumps(
        value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False
    )


def content_hash(value: object) -> str:
    """SHA-256 of the canonical JSON of a value: the hash of a graph element."""
    return sha256_bytes(json_text(value).encode("ascii"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json_text(value) + "\n").encode("ascii"))


def write_jsonl(path: Path, records: Iterable[object]) -> None:
    """One canonical JSON value per line, in the order given: the caller sorts."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("".join(json_text(record) + "\n" for record in records).encode("ascii"))


def read_jsonl(path: Path) -> list[dict]:
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def canonical_table(table: pa.Table) -> pa.Table:
    """The table with nothing but names, logical types and values.

    Schema and field metadata are dropped, chunks are combined, and the
    storage variants of one logical type are made one: large strings and
    dictionary-encoded columns become plain strings or their value type.
    """
    import pyarrow as pa

    fields, arrays = [], []
    for field, column in zip(table.schema, table.columns, strict=True):
        kind = field.type
        if pa.types.is_dictionary(kind):
            kind = kind.value_type
        if pa.types.is_large_string(kind):
            kind = pa.string()
        if kind != field.type:
            column = column.cast(kind)
        arrays.append(column.combine_chunks())
        fields.append(pa.field(field.name, kind))
    return pa.Table.from_arrays(arrays, schema=pa.schema(fields))


def write_parquet(path: Path, table: pa.Table) -> None:
    """Write a dataset as Parquet with every writer option fixed.

    The file names the pyarrow version that wrote it, so the bytes are the
    same only under the pinned pyarrow (env/requirements.lock).
    """
    import pyarrow.parquet as pq

    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(
        canonical_table(table),
        path,
        version="2.6",
        data_page_version="1.0",
        compression="zstd",
        compression_level=3,
        use_dictionary=True,
        write_statistics=True,
        row_group_size=1 << 20,
        store_schema=True,
    )
