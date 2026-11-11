"""The shared formats, version 0 (PLAN.md section 13.2).

Each schema is a valid JSON Schema, accepts its valid examples and rejects
its planted invalid ones (rule R5).
"""

from __future__ import annotations

import json

import pytest
from jsonschema import Draft202012Validator

from specfirst import schemas

EXAMPLES = ("decision-record", "ard", "grid", "graph-node", "graph-edge")


def examples(root, name: str) -> dict:
    path = root / "standard" / "schemas" / "examples" / f"{name}.examples.json"
    with open(path, encoding="ascii") as handle:
        return json.load(handle)


def cases(kind: str) -> list:
    from specfirst.paths import repo_root

    root = repo_root()
    found = []
    for name in EXAMPLES:
        doc = examples(root, name)
        for case in doc[kind]:
            label = f"{name}: {case['name']}"
            found.append(pytest.param(doc["schema"], doc.get("part"), case, id=label))
    return found


@pytest.mark.parametrize("name", schemas.NAMES)
def test_schema_is_a_valid_json_schema(root, name):
    schema = schemas.load(name, root)
    Draft202012Validator.check_schema(schema)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert schema["$id"] == f"specfirst:schemas/0/{name}"


@pytest.mark.parametrize("schema, part, case", cases("valid"))
def test_valid_example_is_accepted(root, schema, part, case):
    assert schemas.problems(schema, case["instance"], part, root) == []


@pytest.mark.parametrize("schema, part, case", cases("invalid"))
def test_planted_defect_is_rejected(root, schema, part, case):
    assert case["why"]
    assert schemas.problems(schema, case["instance"], part, root) != [], case["why"]


@pytest.mark.parametrize("name", EXAMPLES)
def test_every_schema_has_planted_defects(root, name):
    doc = examples(root, name)
    assert len(doc["valid"]) >= 2
    assert len(doc["invalid"]) >= 5


def test_a_graph_line_is_a_node_or_an_edge(root):
    node = examples(root, "graph-node")["valid"][0]["instance"]
    edge = examples(root, "graph-edge")["valid"][0]["instance"]
    assert schemas.problems("graph", node, root=root) == []
    assert schemas.problems("graph", edge, root=root) == []
    assert schemas.problems("graph", {**node, **edge}, root=root) != []


def test_element_ids_are_the_same_in_every_schema(root):
    patterns = {
        schemas.load(name, root)["$defs"]["element_id"]["pattern"]
        for name in ("decision-record", "graph")
    }
    assert len(patterns) == 1


def test_unknown_names_are_errors(root):
    with pytest.raises(KeyError):
        schemas.load("nope", root)
    with pytest.raises(KeyError):
        schemas.validator("graph", "nope", root)
