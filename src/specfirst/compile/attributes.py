"""Names, types and labels of a dataset against a reference (ADR-020, #33).

Two house rules of `open-default@2` decide what a difference of attributes
means:

- a variable carried from another dataset takes the label of its source;
  the parent's wording holds only for a variable it derives;
- a time of day is numeric, the seconds since midnight, as ADaMIG names the
  *TM variables and reference datasets store them.

`carried_label_problems` holds the house's parent specs to the first rule.
`compare` classifies every difference between a built dataset and a
reference, so that a label-only difference is proposed a one-line fix for
the study and a time stored by the rule is explained, not left unexplained.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

CARRIED = re.compile(r"^([A-Z][A-Z0-9]*)\.([A-Z][A-Z0-9_]*)$")
NUMBER_KINDS = ("int", "float", "number", "time")


@dataclass(frozen=True)
class Attribute:
    name: str
    kind: str  # the yamaa type of a spec, or the kind of a reference column
    label: str


@dataclass(frozen=True)
class Difference:
    name: str
    category: str  # missing | extra | label | time | type
    explained: bool
    text: str


def carried_from(column: dict) -> tuple[str, str] | None:
    """(dataset, variable) when a column carries a variable of another dataset unchanged."""
    derivation = column.get("derivation")
    if not isinstance(derivation, str):
        return None
    match = CARRIED.match(derivation.strip())
    if not match or match.group(2) != column.get("name"):
        return None
    return match.group(1), match.group(2)


def of_spec(spec: dict) -> dict[str, Attribute]:
    """The attributes of the output columns a yamaa spec writes, by name."""
    found = {}
    for column in spec.get("columns") or []:
        if isinstance(column, dict) and not str(column.get("name", "")).startswith("_"):
            found[str(column["name"])] = Attribute(str(column["name"]), str(column.get("type", "")),
                                                   str(column.get("label", "")))
    return found


def sdtm_label(domain: str, variable: str) -> str | None:
    """The SDTMIG label of a variable, as specfirst.gen.sdtm lists it."""
    from specfirst.gen import sdtm

    known = sdtm.DOMAINS.get(domain)
    if known is None:
        return None
    try:
        return known.variable(variable).label
    except KeyError:
        return None


def carried_label_problems(parents: dict[str, dict]) -> list[str]:
    """Every column a parent carries unchanged has the label of its source.

    `parents`: the parent specs of a house by dataset name. A source is an
    SDTM domain (its SDTMIG label) or another dataset of the house (its label
    there).
    """
    labels = {name: {a.name: a.label for a in of_spec(spec).values()}
              for name, spec in parents.items()}
    problems = []
    for dataset, spec in parents.items():
        for column in spec.get("columns") or []:
            if not isinstance(column, dict) or str(column.get("name", "")).startswith("_"):
                continue
            source = carried_from(column)
            if source is None:
                continue
            wanted = (labels[source[0]].get(source[1]) if source[0] in labels
                      else sdtm_label(*source))
            if wanted and column.get("label") != wanted:
                problems.append(f"{dataset}.{column['name']}: carried from {source[0]}, labelled "
                                f"'{column.get('label')}', not '{wanted}' (the label of its "
                                "source)")
    return problems


def compare(built: dict[str, Attribute], reference: dict[str, Attribute],
            carried: frozenset[str] = frozenset()) -> list[Difference]:
    """Every difference of names, types and labels, classified.

    `carried`: the names the built dataset carries from another dataset. A
    label-only difference of one is explained: the study's source labels it
    so, and the fix is one line of the study's spec. A time of day that the
    reference stores as a time and the build as the seconds since midnight is
    explained by the house rule.
    """
    found = []
    for name in sorted(set(reference) - set(built)):
        found.append(Difference(name, "missing", False, f"{name}: in the reference, not built"))
    for name in sorted(set(built) - set(reference)):
        found.append(Difference(name, "extra", False, f"{name}: built, not in the reference"))
    for name in sorted(set(built) & set(reference)):
        mine, theirs = built[name], reference[name]
        if mine.kind != theirs.kind:
            timed = (name.endswith("TM") and theirs.kind == "time"
                     and mine.kind in NUMBER_KINDS)
            found.append(Difference(
                name, "time" if timed else "type", timed,
                f"{name}: {mine.kind} against {theirs.kind}" + (
                    "; a time of day is numeric, the seconds since midnight (house rule)"
                    if timed else "")))
        if mine.label != theirs.label:
            explained = name in carried
            fix = f"set the label of {name} to '{theirs.label}' in the study's spec"
            found.append(Difference(
                name, "label", explained,
                f"{name}: labelled '{mine.label}', the reference '{theirs.label}'"
                + (f"; carried, so the source's label differs: {fix}" if explained
                   else f"; {fix}, or change the parent")))
    return found


def unexplained(differences: list[Difference]) -> list[Difference]:
    return [d for d in differences if not d.explained]
