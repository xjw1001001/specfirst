"""Structural templates: a fragment is a pure function of a decision value.

Compile templates (catalog) and house templates are YAML data with a few
directives. A template is evaluated on data, never on text, so a slot value
can change a fragment's content but not its structure (PLAN.md section 5.2,
rule 2: canonical compile).

Directives, each a mapping with one `$` key:

    {$get: name}                      a value of the scope; `a.b` reads a field
    {$if: COND, then: X, else: Y}     without `else`, a false branch is dropped
    {$for: var, in: LIST, do: X}      one X per item; spliced into a list
    {$dict: var, in: LIST, key: K, value: V}   a mapping built from a list
    {$pick: KEY, from: MAPPING}       the member of a mapping
    {$concat: [LIST, ...]}            lists joined
    {$fn: name, args: [...]}          a pure helper from FUNCTIONS

Conditions: {get: name, eq: V} | {get: name, in: [V, ...]} | {not: COND} |
{all: [COND, ...]} | {any: [COND, ...]}.

Inside a string, `${name}` inserts a scalar and `${name|filter}` formats it:
`q` quotes text for a yamaa expression, `qlist` writes a list for IN, `id`
makes an identifier.
"""

from __future__ import annotations

import re
from collections.abc import Callable

_INTERPOLATION = re.compile(r"\$\{([a-z][A-Za-z0-9_.]*)(?:\|([a-z]+))?\}")
_DROP = object()


class TemplateError(ValueError):
    """A template cannot be evaluated."""


# -- helpers -----------------------------------------------------------------


def cut_labels(cuts: list) -> list[str]:
    """Group labels for ascending cut points: [18, 65] gives <18, 18-<65, >=65."""
    if not cuts or sorted(cuts) != list(cuts) or len(set(cuts)) != len(cuts):
        raise TemplateError(f"cut points must be ascending and distinct: {cuts!r}")
    labels = [f"<{_plain(cuts[0])}"]
    for low, high in zip(cuts, cuts[1:], strict=False):
        labels.append(f"{_plain(low)}-<{_plain(high)}")
    labels.append(f">={_plain(cuts[-1])}")
    return labels


def midpoint_windows(visits: list) -> list[dict]:
    """Windows whose limits are the midpoints between consecutive target days.

    The first window starts on study day 2. A day belongs to the earlier
    visit up to the midpoint, rounded down; the last window has no upper
    limit (`high` is null).
    """
    targets = [visit["target"] for visit in visits]
    if sorted(targets) != targets or len(set(targets)) != len(targets):
        raise TemplateError(f"target days must be ascending and distinct: {targets!r}")
    windows = []
    low = 2
    for index, visit in enumerate(visits):
        last = index == len(visits) - 1
        high = None if last else (visit["target"] + visits[index + 1]["target"]) // 2
        windows.append({"visit": visit["visit"], "target": visit["target"],
                        "low": low, "high": high})
        low = (high or 0) + 1
    return windows


def numbered(items: list) -> list[dict]:
    """Each item with its position, from 1: [{item, number}, ...]."""
    return [{"item": item, "number": number} for number, item in enumerate(items, start=1)]


def next_order(number: int) -> int:
    """The position after `number`: the order of a grouping that follows the first one."""
    return number + 1


FUNCTIONS: dict[str, Callable] = {
    "cut_labels": cut_labels,
    "midpoint_windows": midpoint_windows,
    "numbered": numbered,
    "next_order": next_order,
}


# -- evaluation --------------------------------------------------------------


def _plain(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, int | float | str):
        raise TemplateError(f"only text and numbers can be written into a string: {value!r}")
    return repr(value) if isinstance(value, float) else str(value)


def _quote(value: object) -> str:
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    return _plain(value)


def _format(value: object, how: str | None) -> str:
    if how is None:
        return _plain(value)
    if how == "q":
        return _quote(value)
    if how == "qlist":
        if not isinstance(value, list) or not value:
            raise TemplateError(f"qlist needs a non-empty list: {value!r}")
        return "(" + ", ".join(_quote(item) for item in value) + ")"
    if how == "id":
        return re.sub(r"[^A-Za-z0-9]+", "_", _plain(value)).strip("_")
    raise TemplateError(f"unknown filter '{how}'")


_READS: list[set[str]] = []


def lookup(scope: dict, name: str) -> object:
    for reads in _READS:
        reads.add(name.split(".")[0])
    value: object = scope
    for part in name.split("."):
        if not isinstance(value, dict) or part not in value:
            raise TemplateError(f"'{name}' is not defined")
        value = value[part]
    return value


def _condition(cond: object, scope: dict) -> bool:
    if not isinstance(cond, dict):
        raise TemplateError(f"not a condition: {cond!r}")
    if "not" in cond:
        return not _condition(cond["not"], scope)
    if "all" in cond:
        return all(_condition(item, scope) for item in cond["all"])
    if "any" in cond:
        return any(_condition(item, scope) for item in cond["any"])
    if "get" in cond:
        value = lookup(scope, cond["get"])
        if "eq" in cond:
            return value == _whole(cond["eq"], scope)
        if "in" in cond:
            return value in _whole(cond["in"], scope)
    raise TemplateError(f"not a condition: {cond!r}")


def _whole(node: object, scope: dict) -> object:
    """A nested value that must stand for something."""
    value = _evaluate(node, scope)
    if value is _DROP:
        raise TemplateError("a dropped branch has nothing to stand for")
    return list(value) if isinstance(value, _Splice) else value


def _directive(node: dict, scope: dict) -> object:
    if "$get" in node:
        return lookup(scope, node["$get"])
    if "$if" in node:
        if _condition(node["$if"], scope):
            return _evaluate(node.get("then"), scope)
        return _evaluate(node["else"], scope) if "else" in node else _DROP
    if "$for" in node:
        items = _whole(node["in"], scope)
        if not isinstance(items, list):
            raise TemplateError(f"$for needs a list, got {items!r}")
        results = []
        for item in items:
            result = _evaluate(node["do"], {**scope, node["$for"]: item})
            if result is _DROP:
                continue
            if isinstance(result, _Splice):
                results.extend(result)
            else:
                results.append(result)
        return _Splice(results)
    if "$dict" in node:
        items = _whole(node["in"], scope)
        built = {}
        for item in items:
            inner = {**scope, node["$dict"]: item}
            key = _whole(node["key"], inner)
            if key in built:
                raise TemplateError(f"$dict builds the key {key!r} twice")
            built[key] = _whole(node["value"], inner)
        return built
    if "$pick" in node:
        key = _whole(node["$pick"], scope)
        table = node["from"]
        if key not in table:
            raise TemplateError(f"$pick: no member '{key}'")
        return _evaluate(table[key], scope)
    if "$concat" in node:
        joined: list = []
        for part in node["$concat"]:
            value = _whole(part, scope)
            joined.extend(value if isinstance(value, list) else [value])
        return joined
    if "$fn" in node:
        name = node["$fn"]
        if name not in FUNCTIONS:
            raise TemplateError(f"unknown helper '{name}'")
        return FUNCTIONS[name](*[_whole(arg, scope) for arg in node.get("args", [])])
    raise TemplateError(f"unknown directive in {sorted(node)!r}")


class _Splice(list):
    """The result of $for: its items join the surrounding list."""


def evaluate(node: object, scope: dict, reads: set[str] | None = None) -> object:
    """The value of a template node in a scope.

    With `reads`, the names looked up during the evaluation are added to it
    (first path segment; loop variables included).
    """
    if reads is not None:
        _READS.append(reads)
    try:
        value = _evaluate(node, scope)
    finally:
        if reads is not None:
            _READS.pop()
    if value is _DROP:
        raise TemplateError("a dropped branch has nothing to stand for")
    return list(value) if isinstance(value, _Splice) else value


def _evaluate(node: object, scope: dict) -> object:
    if isinstance(node, str):
        return _INTERPOLATION.sub(
            lambda m: _format(lookup(scope, m.group(1)), m.group(2)), node
        )
    if isinstance(node, list):
        items: list = []
        for item in node:
            value = _evaluate(item, scope)
            if value is _DROP:
                continue
            if isinstance(value, _Splice):
                items.extend(value)
            else:
                items.append(value)
        return items
    if isinstance(node, dict):
        if any(isinstance(key, str) and key.startswith("$") for key in node):
            return _directive(node, scope)
        built = {}
        for key, child in node.items():
            value = _evaluate(child, scope)
            if value is _DROP:
                continue
            new_key = _evaluate(key, scope) if isinstance(key, str) else key
            built[new_key] = list(value) if isinstance(value, _Splice) else value
        return built
    return node


def names_used(node: object) -> set[str]:
    """The scope names a template reads (first path segment), loop variables excluded."""
    used: set[str] = set()

    def walk(item: object, bound: frozenset[str]) -> None:
        if isinstance(item, str):
            for match in _INTERPOLATION.finditer(item):
                name = match.group(1).split(".")[0]
                if name not in bound:
                    used.add(name)
        elif isinstance(item, list):
            for child in item:
                walk(child, bound)
        elif isinstance(item, dict):
            inner = bound
            for key in ("$for", "$dict"):
                if key in item:
                    inner = bound | {item[key]}
            for key in ("$get", "get"):
                if key in item and isinstance(item[key], str):
                    name = item[key].split(".")[0]
                    if name not in bound:
                        used.add(name)
            for key, child in item.items():
                if key in ("$get", "$fn", "$for", "$dict"):
                    continue
                if key == "get" and isinstance(child, str):
                    continue
                if key == "in" and ("$for" in item or "$dict" in item):
                    walk(child, bound)
                    continue
                if isinstance(key, str):
                    walk(key, inner)
                walk(child, inner)

    walk(node, frozenset())
    return used
