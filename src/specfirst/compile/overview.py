"""One readable page of the whole catalog, for the owner's review at node N1.

`specfirst catalog --overview FILE` renders it. It adds nothing to the
catalog: every line comes from an entry file, `sources.yaml` or the house
standard.
"""

from __future__ import annotations

from specfirst.compile import house as house_module
from specfirst.compile.catalog import Catalog, Entry
from specfirst.compile.house import House


def _cell(text: str) -> str:
    return " ".join(str(text).split()).replace("|", "/")


def _default(entry: Entry) -> str:
    if entry.house_default is None:
        return "none: the documents state it, or a person is asked"
    if isinstance(entry.house_default, dict):
        return "; ".join(f"`{rule}` for {unit}" for unit, rule in entry.house_default.items())
    return f"`{entry.house_default}`"


def render(catalog: Catalog, house: House) -> str:
    """The overview as Markdown text."""
    alternatives = sum(len(entry.alternatives) for entry in catalog.entries.values())
    without = house_module.without_default(catalog)
    lines = [
        f"# Decision catalog {catalog.name} {catalog.version}: overview",
        "",
        f"Rendered by `specfirst catalog --overview` from `standard/catalog/` and the house "
        f"standard {house.label}. {len(catalog.entries)} entries, {len(catalog.keys())} "
        f"questions when an entry is counted once per unit, {alternatives} alternatives, "
        f"{len(without)} questions without a default.",
        "",
        "In a statement, `{name}` is a typed slot and `{output}` names the table: "
        + "; ".join(f"{unit.id} is \"{unit.phrase}\"" for unit in catalog.units.values()
                    if unit.phrase) + ".",
        "",
    ]
    current = None
    for entry in catalog.entries.values():
        group = ("Table families: " + ", ".join(entry.units)) if entry.per_family else \
            f"{entry.units[0]}: {catalog.units[entry.units[0]].title}"
        if group != current:
            current = group
            lines += [f"## {group}", ""]
        lines += [f"### `{entry.id}`: {entry.question}", "",
                  f"Applies when: `{entry.applies_when}`. Default: {_default(entry)}.", "",
                  "| Alternative | Statement | Meaning |", "| --- | --- | --- |"]
        for alternative in entry.alternatives:
            lines.append(f"| `{alternative.id}` | {_cell(alternative.statement)} | "
                         f"{_cell(alternative.definition)} |")
        lines.append("")
        if entry.raw.get("notes"):
            lines += [f"For every alternative: {_cell(entry.raw['notes'])}", ""]
        for alternative in entry.alternatives:
            for slot in alternative.slots:
                extra = [f"type `{slot.type}`"]
                if slot.choices is not None:
                    extra.append("one of " + ", ".join(str(c) for c in slot.choices))
                if slot.item:
                    extra.append(f"each written as `{slot.item}`")
                lines.append(f"- Slot `{slot.name}` of `{alternative.id}`: " + "; ".join(extra)
                             + ".")
        cited = "; ".join(
            f"{catalog.sources.get(s.get('ref'), {}).get('title', s.get('ref'))} "
            f"({_cell(s.get('where', ''))})" for s in entry.sources)
        lines += [f"- Sources: {cited}.", f"- Probes: {', '.join(entry.probes)}.", ""]
    deferred = catalog.raw.get("deferred") or {}
    partly = catalog.raw.get("deferred_alternatives") or {}
    if deferred or partly:
        lines += ["## Left out of this draft", ""]
        lines += [f"- `{name}`: {_cell(reason)}" for name, reason in deferred.items()]
        lines += [f"- `{name}`: {_cell(reason)}" for name, reason in partly.items()]
        lines.append("")
    return "\n".join(lines)
