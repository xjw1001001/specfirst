"""The method registry (PLAN.md section 7.3): what a method computes, in numbered semantics.

ARS names a method; it does not fix its arithmetic (E4). A registry entry
does: one YAML file per method in standard/methods/, with its operations,
its numbered semantics, its options and their defaults, the engines that
implement it, its test vectors and its cross-references. README.md in that
folder describes the format.

standard/methods/registry.json holds the same entries as one canonical JSON
file. It is generated (`specfirst methods --write`) and a test fails when it
is stale. The R engine reads it, because the locked R library has no YAML
reader; the Python engine reads the YAML files.

The entries are checked by this module, not by a schema in
standard/schemas/: adding one there needs an ADR the owner approves
(ADR-002).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from specfirst.machine.canonical import content_hash, json_text

FORMAT = 0
# A model-based method (ANCOVA with LS means, its pairwise comparisons, the
# dose-response test) is R only (PLAN.md section 7.3, ADR-015).
KINDS = ("descriptive", "test", "display", "model")
ENGINES = ("python", "r")
RESULTS = ("integer", "number", "text")
# What an option that is not chosen from a list of values takes (ADR-015):
# `columns`, the names of columns of the analysis dataset (the terms of a model),
# and `group`, the ID of a group of the analysis's grouping. Their values are
# stated by the analysis; a `group` option has no default.
TAKES = ("columns", "group")
_COLUMN = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")
KEYS = ("id", "kind", "title", "takes", "operations", "semantics", "options", "implementations",
        "vectors", "xref")
XREF_KEYS = ("ars_example", "siera", "acdc")


class RegistryError(ValueError):
    """The registry, or a use of it, is not valid."""


@dataclass(frozen=True)
class Method:
    id: str
    kind: str
    title: str
    takes: str
    operations: dict[str, dict]  # operation -> {"result": ..., "ars_names": [...]}
    semantics: tuple[str, ...]  # statement k is "S<k>", counted from 1
    options: dict[str, dict]  # option -> {"values": [...], "default": ...}
    implementations: tuple[str, ...]
    vectors: str
    xref: dict

    def record(self) -> dict:
        return {
            "id": self.id, "kind": self.kind, "title": self.title, "takes": self.takes,
            "operations": self.operations, "semantics": list(self.semantics),
            "options": self.options, "implementations": list(self.implementations),
            "vectors": self.vectors, "xref": self.xref,
        }


def _scalar(value: object) -> bool:
    """Text, a whole number, or true and false: what both engines write the same way."""
    return isinstance(value, str | int)


def parse_method(data: object, where: str) -> Method:
    """Read one entry. Every problem is reported at once."""
    if not isinstance(data, dict):
        raise RegistryError(f"{where}: expected a mapping")
    problems = [f"unknown key '{key}'" for key in data if key not in KEYS]
    problems += [f"'{key}' is missing" for key in KEYS if key not in data]
    for key in ("id", "kind", "title", "takes", "vectors"):
        if key in data and (not isinstance(data[key], str) or not data[key].strip()):
            problems.append(f"'{key}' must be text")
    if data.get("kind") not in KINDS:
        problems.append(f"'kind' must be one of {', '.join(KINDS)}")
    operations = data.get("operations")
    if not isinstance(operations, dict) or not operations:
        problems.append("'operations' must name at least one operation")
        operations = {}
    for name, operation in operations.items():
        if not isinstance(operation, dict) or set(operation) != {"result", "ars_names"}:
            problems.append(f"operation '{name}': needs exactly 'result' and 'ars_names'")
            continue
        if operation["result"] not in RESULTS:
            problems.append(f"operation '{name}': 'result' must be one of {', '.join(RESULTS)}")
        names = operation["ars_names"]
        if not isinstance(names, list) or not all(isinstance(n, str) and n for n in names):
            problems.append(f"operation '{name}': 'ars_names' must be a list of names")
    semantics = data.get("semantics")
    if not isinstance(semantics, list) or not semantics or not all(
            isinstance(s, str) and s.strip() for s in semantics):
        problems.append("'semantics' must be a list of statements, at least one")
        semantics = []
    options = data.get("options")
    if not isinstance(options, dict):
        problems.append("'options' must be a mapping; write {} for none")
        options = {}
    for name, option in options.items():
        if isinstance(option, dict) and set(option) == {"takes", "default"}:
            if option["takes"] not in TAKES:
                problems.append(f"option '{name}': 'takes' must be one of {', '.join(TAKES)}")
            elif option["takes"] == "columns" and option["default"] != []:
                problems.append(f"option '{name}': a list of columns has the default []")
            elif option["takes"] == "group" and option["default"] is not None:
                problems.append(f"option '{name}': a group has no default (null); the "
                                "analysis names it")
            if data.get("kind") != "model" and not (data.get("kind") == "test"
                                                    and option["takes"] == "columns"):
                problems.append(f"option '{name}': only a model-based method takes columns "
                                "or a group, and a test columns (its strata)")
            continue
        if not isinstance(option, dict) or set(option) != {"values", "default"}:
            problems.append(f"option '{name}': needs exactly 'values' and 'default', or "
                            "'takes' and 'default'")
            continue
        values = option["values"]
        if not isinstance(values, list) or not values or not all(_scalar(v) for v in values):
            problems.append(f"option '{name}': 'values' must list text, whole numbers or "
                            "true and false")
        elif option["default"] not in values:
            problems.append(f"option '{name}': the default is not one of its values")
    engines = data.get("implementations")
    if not isinstance(engines, list) or not engines or any(e not in ENGINES for e in engines):
        problems.append(f"'implementations' must list some of {', '.join(ENGINES)}")
        engines = []
    elif len(set(engines)) != len(engines):
        problems.append("'implementations' names an engine twice")
    elif data.get("kind") in ("descriptive", "test") and set(engines) != set(ENGINES):
        # Rule R11: two engines, one answer.
        problems.append("a descriptive method or a test needs both engines (rule R11)")
    elif data.get("kind") == "model" and engines != ["r"]:
        # Section 7.3: model-based methods are R only.
        problems.append("a model-based method is implemented in R only (PLAN.md section 7.3)")
    xref = data.get("xref")
    if not isinstance(xref, dict) or set(xref) != set(XREF_KEYS):
        problems.append(f"'xref' needs exactly {', '.join(XREF_KEYS)}")
        xref = {}
    for key in ("ars_example", "siera"):
        value = xref.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            problems.append(f"xref.{key}: must be a list of IDs, [] for none")
    if xref.get("acdc") is not None and not isinstance(xref.get("acdc"), str):
        problems.append("xref.acdc: must be an ID or null")
    if problems:
        raise RegistryError(f"{where}: " + "; ".join(problems))
    return Method(
        id=data["id"], kind=data["kind"], title=data["title"].strip(), takes=data["takes"].strip(),
        operations={str(k): {"result": v["result"], "ars_names": list(v["ars_names"])}
                    for k, v in operations.items()},
        semantics=tuple(" ".join(s.split()) for s in semantics),
        options={str(k): ({"takes": v["takes"], "default": v["default"]} if "takes" in v
                          else {"values": list(v["values"]), "default": v["default"]})
                 for k, v in options.items()},
        implementations=tuple(engines), vectors=data["vectors"], xref=dict(xref),
    )


@dataclass(frozen=True)
class Registry:
    methods: dict[str, Method]

    def method(self, method_id: str) -> Method:
        if method_id not in self.methods:
            raise RegistryError(f"no method '{method_id}' in the registry; known: "
                                f"{', '.join(sorted(self.methods))}")
        return self.methods[method_id]

    def operation(self, method_id: str, operation: str) -> dict:
        method = self.method(method_id)
        if operation not in method.operations:
            raise RegistryError(f"method '{method_id}' has no operation '{operation}'; it has "
                                f"{', '.join(method.operations)}")
        return method.operations[operation]

    def options(self, method_id: str, given: dict | None = None) -> dict:
        """The options of a method with every default filled in. Unknown names and values fail."""
        method = self.method(method_id)
        given = dict(given or {})
        resolved = {}
        for name, option in sorted(method.options.items()):
            value = given.pop(name, option["default"])
            if option.get("takes") == "columns":
                if not isinstance(value, list) or not all(
                        isinstance(item, str) and _COLUMN.match(item) for item in value) or len(
                        set(value)) != len(value):
                    raise RegistryError(f"method '{method_id}', option '{name}': {value!r} is "
                                        "not a list of distinct column names")
                resolved[name] = list(value)
                continue
            if option.get("takes") == "group":
                if not isinstance(value, str) or not value:
                    raise RegistryError(f"method '{method_id}', option '{name}': the analysis "
                                        f"must name a group, not {value!r}")
                resolved[name] = value
                continue
            if value not in option["values"] or type(value) is not type(option["default"]):
                raise RegistryError(f"method '{method_id}', option '{name}': {value!r} is not "
                                    f"one of {option['values']}")
            resolved[name] = value
        if given:
            raise RegistryError(f"method '{method_id}' has no option "
                                f"{', '.join(sorted(given))}")
        return resolved

    def options_hash(self, method_id: str, given: dict | None = None) -> str:
        """SHA-256 of the canonical JSON of the resolved options: `method_options_hash`."""
        return content_hash(self.options(method_id, given))

    def by_ars_name(self, name: str) -> list[tuple[str, str]]:
        """The (method, operation) pairs that take an ARS operation of this name."""
        wanted = name.strip().lower()
        return sorted(
            (method.id, operation)
            for method in self.methods.values()
            for operation, record in method.operations.items()
            if wanted in (n.lower() for n in record["ars_names"])
        )

    def record(self) -> dict:
        return {"registry": FORMAT,
                "methods": {key: self.methods[key].record() for key in sorted(self.methods)}}


def folder(root: Path) -> Path:
    return root / "standard" / "methods"


def json_path(root: Path) -> Path:
    return folder(root) / "registry.json"


def load(root: Path) -> Registry:
    """Read every entry of standard/methods/. Fails on the first invalid registry."""
    methods: dict[str, Method] = {}
    problems: list[str] = []
    for path in sorted(folder(root).glob("*.yaml")):
        where = f"standard/methods/{path.name}"
        try:
            with open(path, encoding="ascii") as handle:
                method = parse_method(yaml.safe_load(handle), where)
        except (RegistryError, yaml.YAMLError, UnicodeDecodeError) as error:
            problems.append(str(error))
            continue
        if path.name != f"{method.id}.yaml":
            problems.append(f"{where}: the entry is named '{method.id}'")
        if not method.vectors.startswith("tests/methods/") or not (root / method.vectors).is_file():
            problems.append(f"{where}: no test vectors at '{method.vectors}'")
        methods[method.id] = method
    if not methods and not problems:
        problems.append("standard/methods/ holds no entry")
    # An option that takes columns is stated by an analysis under a name the ARS reader
    # knows, so that the columns are read (the `reads` edges, ADR-015).
    from specfirst.machine.ars import MODEL_TERMS

    for method in methods.values():
        problems += [f"standard/methods/{method.id}.yaml: option '{name}' takes columns, and "
                     f"only {', '.join(MODEL_TERMS)} may"
                     for name, option in method.options.items()
                     if option.get("takes") == "columns" and name not in MODEL_TERMS]
    # A descriptive operation is found by the name ARS gives it, so no two may share one.
    taken: dict[str, str] = {}
    for method in methods.values():
        if method.kind != "descriptive":
            continue
        for operation, record in method.operations.items():
            for name in record["ars_names"]:
                other = taken.setdefault(name.lower(), f"{method.id}.{operation}")
                if other != f"{method.id}.{operation}":
                    problems.append(f"ARS operation name '{name}' is taken by {other} and by "
                                    f"{method.id}.{operation}")
    if problems:
        raise RegistryError("; ".join(problems))
    return Registry(methods)


def json_bytes(registry: Registry) -> bytes:
    return (json_text(registry.record()) + "\n").encode("ascii")


def write_json(root: Path) -> Path:
    path = json_path(root)
    path.write_bytes(json_bytes(load(root)))
    return path


def json_problems(root: Path) -> list[str]:
    """Why standard/methods/registry.json is not what the YAML entries give."""
    path = json_path(root)
    if not path.is_file():
        return ["standard/methods/registry.json is missing; run `specfirst methods --write`"]
    if path.read_bytes() != json_bytes(load(root)):
        return ["standard/methods/registry.json is stale; run `specfirst methods --write`"]
    return []


def run(root: Path, write: bool = False, out=print) -> int:
    """`specfirst methods [--write]`: list the registry; check or rewrite registry.json."""
    try:
        registry = load(root)
    except RegistryError as error:
        out(f"methods: {error}")
        return 1
    for method in registry.methods.values():
        options = ", ".join(f"{name}={option['default']}"
                            for name, option in sorted(method.options.items())) or "-"
        out(f"{method.id:34s} {method.kind:11s} {len(method.semantics):2d} statements  "
            f"{'+'.join(method.implementations):8s} operations: {', '.join(method.operations)}; "
            f"options: {options}")
    if write:
        out(f"wrote {write_json(root).relative_to(root).as_posix()}")
    problems = json_problems(root)
    for problem in problems:
        out(f"methods: {problem}")
    out(f"methods: {len(registry.methods)} entries" + ("" if not problems else ", registry.json "
                                                       "does not match"))
    return 1 if problems else 0
