"""Static column dependencies of a composed yamaa specification.

This is the approach of Pilot 7's review dashboard (PLAN.md section 7.1),
adapted from two of its files, which are MIT licensed (third_party/SOURCES.md
records them):

    RConsortium/submissions-pilot7-synthetic-data
    commit 213cb6ab3adc51abe4295cbbc546c0e6d46c3df8
    .github/scripts/study_dashboard/references.py
    .github/scripts/study_dashboard/lineage.py
    Copyright (c) 2026 R Consortium Pilot 7 contributors
    MIT License: third_party/licenses/PILOT7-MIT.txt

`References` is their class with two additions: it also records the bare
names it could not place (`unknown`) and the datasets an expression reads as
a whole (`whole`, as in COUNT(ALIAS.*)), and these can be collected per
reading element together with `unresolved`. The rules that decide what an
expression reads are unchanged, and tests/pilot checks that this module and
Pilot 7's own code give the same dependencies for the ten pilot
specifications.

It is a static index of declared references, not a trace of contributing
rows. Only names present in the declared schemas become dependencies.
Literal strings are excluded; joins, filters, keys and ordering are kept as
context dependencies.

Changed from Pilot 7: `column_dependencies` returns one `Read` per element
and place of reading, with the JSON pointer of that place in the composed
specification, so that an edge of the graph can name the file and line where
a column is read. Source spans are taken from yamaa's resolution instead of
being recomputed from the YAML text.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

TOKENS = re.compile(
    r"'(?:(?:'')|[^'])*'|\b[A-Za-z_][A-Za-z_0-9]*(?:\.[A-Za-z_][A-Za-z_0-9]*)?\b"
)
# Keys whose values are literals, not expressions.
LITERALS = {
    "dict", "label", "type", "nulls", "keep", "pattern", "format", "unit", "closed", "side",
    "separator", "method", "ties", "missing", "unmapped", "true_value", "false_value",
    "unconvertible", "invalid", "absent",
}
# Bare words of the expression language and of option values that are not names.
KEYWORDS = {
    "AND", "OR", "NOT", "IN", "LIKE", "IS", "NULL", "BETWEEN", "TRUE", "FALSE",
    "ASC", "DESC", "FIRST", "LAST",
}


class References:
    """Resolve declared expression references and the keys of lookups actually read."""

    def __init__(self, spec: dict, schemas: dict[str, set[str]]):
        self.spec, self.schemas = spec, schemas
        self.local = {c["name"] for c in spec.get("columns", [])}
        self.local |= {
            name for row in spec.get("rows", []) for name in row.get("derivations", {})
        }
        self.base = spec.get("base") or (
            next(iter(schemas)) if len(schemas) == 1 else None
        )
        self.aliases = {name: set(columns) for name, columns in schemas.items()}
        self.aliases["SELF"] = self.local | self.aliases.get(self.base, set())
        intermediates = spec.get("intermediates", [])
        for _ in range(len(intermediates) + 1):
            for item in intermediates:
                columns = self.aliases.get(item.get("dataset"), set()) | set(
                    item.get("derivations", {})
                )
                self.aliases[item["id"]] = (
                    columns & set(item["columns"]) if "columns" in item else columns
                )
        if self.base in self.aliases:
            self.aliases[self.base] |= self.local
        self.unresolved: set[str] = set()
        self.unknown: set[str] = set()
        self.whole: set[str] = set()

    def field(self, alias, name):
        if name not in self.aliases.get(alias, set()):
            self.unresolved.add(f"{alias}.{name}")
            return set()
        if alias == "SELF":
            return {f"spec.{name}" if name in self.local else f"{self.base}.{name}"}
        if alias == self.base and name not in self.schemas.get(alias, set()):
            return {f"spec.{name}"}
        return {f"{alias}.{name}"}

    def text(self, expression, donor, driver, bindings, join, row=False):
        result = set()
        for match in TOKENS.finditer(expression):
            token = match.group()
            if token.startswith("'") or expression[match.end():].lstrip().startswith("("):
                continue
            if token in bindings:
                value = bindings[token]
                result |= value() if callable(value) else value
            elif "." in token:
                alias, name = token.split(".", 1)
                result |= self.field(alias, name)
                if join and alias in self.schemas and alias not in {donor, driver}:
                    declaration = self.spec["input"].get(alias, {})
                    if isinstance(declaration, dict):
                        result |= self.keys(
                            declaration.get("key", []), alias, driver, implicit=True, row=row
                        )
            elif donor and token in self.aliases.get(donor, set()):
                result |= self.field(donor, token)
            elif token in self.local:
                result.add(f"spec.{token}")
            elif token in self.aliases and expression[match.end():].startswith(".*"):
                self.whole.add(token)  # COUNT(ALIAS.*): the rows of a dataset, no column
            elif token.upper() not in KEYWORDS:
                self.unknown.add(token)
        return result

    def keys(self, keys, donor, driver=None, bindings=None, implicit=False, row=False):
        pairs = (
            keys.items() if isinstance(keys, dict) else ((name, name) for name in keys)
        )
        result = set()
        for name, value in pairs:
            result |= self.read(f"{donor}.{name}", donor=donor, bindings=bindings, join=False)
            scope = driver if implicit and row else None
            result |= self.read(value, donor=scope, driver=driver, row=row)
            # Preserve a resolvable driver-field match when no column has that name.
            if (
                isinstance(value, str)
                and value not in self.local
                and value in self.schemas.get(driver or self.base, set())
            ):
                result |= self.field(driver or self.base, value)
        return result

    def bounds(self, value, donor, driver, bindings, row=False):
        result = self.read(value.get("value"), driver=driver, row=row)
        for key in ("lower", "upper"):
            if value.get(key):
                result |= self.read(
                    f"{donor}.{value[key]}", donor=donor, bindings=bindings, join=False
                )
        return result

    def local_bindings(self, definitions, donor, driver, parent, join, row=False):
        bindings, cache, active = dict(parent or {}), {}, set()

        def resolve(name):
            if name in active:
                self.unresolved.add(f"aggregate.{name}")
                return set()
            if name not in cache:
                active.add(name)
                definition = definitions[name]
                if isinstance(definition, dict) and "derivation" in definition:
                    definition = definition["derivation"]
                cache[name] = self.read(definition, donor, driver, bindings, join, row)
                active.remove(name)
            return cache[name]

        for name in definitions:
            bindings[name] = lambda name=name: resolve(name)
        return bindings

    def aggregate(self, value, donor, driver, bindings, join, row=False):
        if not isinstance(value, dict):
            return self.read(value, donor, driver, bindings, join, row)
        definitions = value.get("derivations", {})
        raw_bindings = self.local_bindings(definitions, donor, driver, bindings, False, row)
        raw = self.read(value.get("expr"), donor, driver, raw_bindings, False, row)
        relations = {
            ref.split(".", 1)[0] for ref in raw if ref.split(".", 1)[0] in self.schemas
        }
        relation = next(iter(relations)) if len(relations) == 1 else donor
        scoped = self.local_bindings(definitions, relation, driver, bindings, join, row)
        result = set()
        for key in ("expr", "filter", "group_by", "order_by"):
            result |= self.read(value.get(key), relation, driver, scoped, join, row)
        if relation and (relation != driver or not row) and join:
            declaration = self.spec["input"].get(relation, {})
            fallback = declaration.get("key", []) if isinstance(declaration, dict) else []
            result |= self.keys(
                value.get("key", fallback), relation, driver, implicit="key" not in value, row=row
            )
        if value.get("between") and relation:
            result |= self.bounds(value["between"], relation, driver, scoped, row)
        return result

    def read(self, value, donor=None, driver=None, bindings=None, join=True, row=False):
        bindings = bindings or {}
        if isinstance(value, str):
            return self.text(value, donor, driver, bindings, join, row)
        if isinstance(value, list):
            return set().union(
                *(self.read(v, donor, driver, bindings, join, row) for v in value)
            )
        result = set()
        if isinstance(value, dict):
            for key, item in value.items():
                if key in LITERALS:
                    continue
                if key == "aggregate":
                    result |= self.aggregate(item, donor, driver, bindings, join, row)
                elif key == "between" and donor:
                    result |= self.bounds(item, donor, driver, bindings, row)
                elif key == "str_template" and isinstance(item, dict):
                    for name in re.findall(
                        r"(?<!\{)\{([^{}]+)\}(?!\})", item.get("template", "")
                    ):
                        result |= self.read(name, donor, driver, bindings, join, row)
                else:
                    result |= self.read(item, donor, driver, bindings, join, row)
        return result


def pointer(*parts: object) -> str:
    """A JSON pointer (RFC 6901) into the composed specification."""
    return "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)


@dataclass(frozen=True)
class Read:
    """What one element reads at one place of the specification.

    element: `spec.<column>`, `intermediate.<id>`, `<id>.<column>` of an
    intermediate, or `row.<id>` of a row template.
    refs: the same kinds of names, plus `<input alias>.<column>`.
    """

    element: str
    pointer: str
    refs: frozenset[str]
    unresolved: frozenset[str] = frozenset()  # qualified names that no schema has
    unknown: frozenset[str] = frozenset()  # bare names that are neither columns nor keywords
    whole: frozenset[str] = frozenset()  # datasets read as a whole, such as COUNT(ALIAS.*)


@dataclass(frozen=True)
class Lineage:
    reads: tuple[Read, ...]
    outputs: tuple[str, ...]
    defined: frozenset[str]  # local names with a derivation, in a column or in a row template

    def edges(self) -> dict[str, list[str]]:
        """Dependencies per element, in the shape of Pilot 7's `build_lineage`."""
        edges: dict[str, set[str]] = {}
        for read in self.reads:
            edges.setdefault(read.element, set()).update(read.refs)
        for name in self.outputs:
            edges[f"output.{name}"] = {f"spec.{name}"}
        return {key: sorted(value - {key}) for key, value in edges.items()}


def column_dependencies(spec: dict, schemas: dict[str, set[str]]) -> Lineage:
    """Index the composed specification `spec`, given the columns of each input alias."""
    references = References(spec, schemas)
    reads: list[Read] = []

    def record(element: str, place: str, compute) -> None:
        references.unresolved, references.unknown, references.whole = set(), set(), set()
        refs = compute()
        reads.append(
            Read(element, place, frozenset(refs) - {element}, frozenset(references.unresolved),
                 frozenset(references.unknown), frozenset(references.whole))
        )

    for j, item in enumerate(spec.get("intermediates", [])):
        identifier, dataset = item["id"], item["dataset"]
        derived = item.get("derivations", {})
        bindings = {name: {f"{identifier}.{name}"} for name in derived}
        bindings.update({f"{dataset}.{name}": {f"{identifier}.{name}"} for name in derived})

        def context(item=item, dataset=dataset, bindings=bindings):
            found = references.keys(item.get("key", []), dataset, bindings=bindings)
            for key in ("filter", "order_by", "group_by"):
                found |= references.read(
                    item.get(key), donor=dataset, bindings=bindings, join=False
                )
            if item.get("between"):
                found |= references.bounds(item["between"], dataset, None, bindings)
            return found

        record(f"intermediate.{identifier}", pointer("intermediates", j), context)
        for name in sorted(references.aliases[identifier] | set(derived)):
            if name in derived:
                others = {
                    key: value for key, value in bindings.items()
                    if key not in {name, f"{dataset}.{name}"}
                }

                def source(name=name, dataset=dataset, others=others, derived=derived):
                    return references.read(
                        derived[name], donor=dataset, bindings=others, join=False
                    )

                place = pointer("intermediates", j, "derivations", name)
            else:

                def source(name=name, dataset=dataset):
                    return references.field(dataset, name)

                place = pointer("intermediates", j)
            record(
                f"{identifier}.{name}", place,
                lambda source=source, identifier=identifier: (
                    source() | {f"intermediate.{identifier}"}
                ),
            )

    templates = spec.get("rows", [])
    for k, row in enumerate(templates):
        record(
            f'row.{row["id"]}', pointer("rows", k),
            lambda row=row: references.read(
                {key: row[key] for key in ("filter", "group_by") if key in row},
                driver=row["dataset"], row=True,
            ),
        )

    columns = {column["name"]: (i, column) for i, column in enumerate(spec.get("columns", []))}

    def declared(name: str):
        return columns[name][1].get("derivation") if name in columns else None

    def column_place(name: str) -> str | None:
        if name not in columns:
            return None
        i, column = columns[name]
        return pointer("columns", i, "derivation") if "derivation" in column else pointer(
            "columns", i
        )

    defined = {name for name in columns if declared(name) is not None}
    for name in sorted(references.local):
        element = f"spec.{name}"
        if spec.get("filter") is not None:
            record(element, pointer("filter"),
                   lambda: references.read(spec.get("filter"), driver=references.base))
        if not templates:
            record(element, column_place(name) or pointer("columns"),
                   lambda name=name: references.read(declared(name), driver=references.base))
            continue
        for k, row in enumerate(templates):
            in_row = name in row.get("derivations", {})
            if in_row:
                defined.add(name)
                expression = row["derivations"][name]
                place = pointer("rows", k, "derivations", name)
            else:
                expression = declared(name)
                place = column_place(name) or pointer("rows", k)
            record(
                element, place,
                lambda expression=expression, row=row, in_row=in_row: references.read(
                    expression, driver=row["dataset"], row=in_row
                ) | {f'row.{row["id"]}'},
            )
    return Lineage(tuple(reads), tuple(spec["output"]["columns"]), frozenset(defined))
