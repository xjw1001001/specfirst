"""Load and apply the shared formats in standard/schemas/.

Version 0 has four schemas: decision-record, ard, grid and graph. The graph
schema has two parts, "node" and "edge". Changing a schema needs an ADR
(PLAN.md section 13.2).
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from specfirst.paths import repo_root

NAMES = ("decision-record", "ard", "grid", "graph")


def schema_dir(root: Path | None = None) -> Path:
    return (root or repo_root()) / "standard" / "schemas"


def load(name: str, root: Path | None = None) -> dict:
    if name not in NAMES:
        raise KeyError(f"unknown schema '{name}'; known: {', '.join(NAMES)}")
    with open(schema_dir(root) / f"{name}.schema.json", encoding="ascii") as handle:
        return json.load(handle)


def validator(name: str, part: str | None = None, root: Path | None = None) -> Draft202012Validator:
    """A validator for a schema, or for one of its parts (graph: "node", "edge")."""
    schema = load(name, root)
    if part is not None:
        if part not in schema.get("$defs", {}):
            raise KeyError(f"schema '{name}' has no part '{part}'")
        schema = {"$schema": schema["$schema"], "$ref": f"#/$defs/{part}", "$defs": schema["$defs"]}
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def problems(
    name: str, instance: object, part: str | None = None, root: Path | None = None
) -> list[str]:
    """Why an instance does not fit a schema. An empty list means it fits."""
    errors = sorted(validator(name, part, root).iter_errors(instance), key=lambda e: list(e.path))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]
