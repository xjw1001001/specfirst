"""Dataset-JSON v1.1 (CDISC): the exchange form of the generated SDTM.

The machine reads Parquet; CDISC CORE reads Dataset-JSON. Both are written
from the same rows. The text is canonical: fixed key order, one row per
line, ASCII, and no clock (the creation time is a date of the study).
"""

from __future__ import annotations

import json
from pathlib import Path

from specfirst.gen.sdtm import Domain

VERSION = "1.1.0"
_TYPES = {"text": "string", "datetime": "string", "integer": "integer", "float": "float"}


def item_oid(domain: str, variable: str) -> str:
    return f"IT.{domain}.{variable}"


def cell(value: object, kind: str) -> object:
    """A value as Dataset-JSON holds it: no missing text, whole numbers as integers."""
    if value is None:
        return "" if kind in ("text", "datetime") else None
    if kind == "integer":
        return int(value)
    if kind == "float":
        number = float(value)
        return int(number) if number == int(number) else number
    return str(value)


def text_length(rows: list[dict], name: str) -> int:
    return max([len(str(row[name])) for row in rows if row[name] is not None], default=1)


def render(domain: Domain, rows: list[dict], study: str, stamp: str, system: dict) -> str:
    """The Dataset-JSON text of one dataset. `stamp` is its creation date and time."""
    columns = []
    for variable in domain.variables:
        column: dict[str, object] = {
            "itemOID": item_oid(domain.name, variable.name),
            "name": variable.name,
            "label": variable.label,
            "dataType": _TYPES[variable.kind],
        }
        if variable.kind in ("text", "datetime"):
            column["length"] = text_length(rows, variable.name)
        if variable.name in domain.keys:
            column["keySequence"] = domain.keys.index(variable.name) + 1
        columns.append(column)
    head = {
        "datasetJSONCreationDateTime": stamp,
        "datasetJSONVersion": VERSION,
        "fileOID": f"{study}.{domain.name}",
        "dbLastModifiedDateTime": stamp,
        "originator": system["name"],
        "sourceSystem": system,
        "studyOID": f"ST.{study}",
        "metaDataVersionOID": f"MDV.{study}.SDTM",
        "metaDataRef": "define.xml",
        "itemGroupOID": f"IG.{domain.name}",
        "records": len(rows),
        "name": domain.name,
        "label": domain.label,
    }
    lines = ["{"]
    for key, value in head.items():
        lines.append(f"{json.dumps(key)}: {json.dumps(value, ensure_ascii=True)},")
    lines.append('"columns": [')
    lines += [json.dumps(column, ensure_ascii=True) + ("," if i < len(columns) - 1 else "")
              for i, column in enumerate(columns)]
    lines.append("],")
    lines.append('"rows": [')
    for i, row in enumerate(rows):
        values = [cell(row[v.name], v.kind) for v in domain.variables]
        lines.append(json.dumps(values, ensure_ascii=True) + ("," if i < len(rows) - 1 else ""))
    lines.append("]")
    lines.append("}")
    return "\n".join(lines) + "\n"


def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    """Column names and rows of a Dataset-JSON file; missing text comes back as None."""
    with open(path, encoding="ascii") as handle:
        data = json.load(handle)
    names = [column["name"] for column in data["columns"]]
    rows = [{name: (None if value == "" else value) for name, value in zip(names, row, strict=True)}
            for row in data["rows"]]
    return names, rows
