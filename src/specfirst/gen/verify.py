"""The properties of a kit (PLAN.md sections 4.6 and 6.4, stage S7): P2, P3, P4.

P1 (the same bytes from two builds) is checked where a kit is written twice
(`specfirst.gen.kits`). The other three are checked here, on a dataset of a
kit, by functions that return what is wrong:

    P2  reproduction      the grid equals the reference. The reference of a
                          generated study is the hand calculation of
                          specfirst.gen.reference: SDTM rows and decision
                          values in, the texts of the table out, with no part
                          of the machine in between. Every cell, the columns
                          and the rows are compared.
    P3  traceability      every cell that prints a number has a complete path
                          to SDTM columns and at least one decision behind
                          it; the graph files hold what they say.
    P4  identifiability   mutation: for every decision of the study, every
                          alternative is compiled and built on the twin, and
                          the grids are compared pair by pair.

What "applicable" means for P4 (gen-2b; the owner's answer of 2026-11-17 on
finding G1 of the gen-2a review, docs/decisions/ADR-007.md and ADR-023.md).
Two things are known of a decision in a kit before anything is mutated:

    read      the output reads an element the decision sets (`gold.reach`:
              decided by the graph and by the compile, not by the data)
    claimed   no other decision of the kit makes the alternatives give the
              same output on any data that keep the premise of its row of
              `probes.REACHES` (`probes.reaches` on the field `reaches` of
              the log, which repeats `probes.REACHES`)

A decision is applicable in a kit when every pair of its gold value with
another value of `options` is claimed (another alternative; for an entry
with one alternative, another value of its slots): data could separate it,
and the probes of the kit are planted for its decisions so that the twin
does. Every
applicable decision must be separated: a kit in which a claimed pair gives
the same output is not written (`unfit`), and the gate fails on it. A
decision that is not read must change nothing; if it does, the reach is
wrong, and that is a defect; so is a claim for a decision that is not read.
A decision that is read and not claimed is built all the same and recorded
as it comes out: `unseparated` with the reason that another decision of the
kit makes its alternatives equal (the table groups by planned treatment, so
the source of actual treatment does not count; it has no emergence window,
so the treatment end date does not count).

The reference is also held against every mutated build: a variant of the
decisions is one more decision vector, and the machine and the hand
calculation must agree on it too.
"""

from __future__ import annotations

from collections.abc import Callable
from itertools import combinations
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import decisions, display, gold, probes, reference
from specfirst.machine import ars, graph
from specfirst.machine.canonical import read_jsonl

Out = Callable[[str], None]
NOT_READ = "the output does not read what the decision sets"
# The state of a decision that has nothing to be changed to: neither separated nor not.
NO_ALTERNATIVE = "no_alternative"
NO_PROBE = ("the output reads it, but under the other decisions of the kit its alternatives "
            "give the same output on any data of this design that follow SDTMIG v3.4 "
            "(probes.REACHES)")


# ---- P2 --------------------------------------------------------------------------------


def table_view(made: dict | None) -> dict | None:
    """What a grid shows, without IDs: the column labels, and per row its label and texts."""
    if made is None:
        return None
    return {"columns": [column["label"] for column in made["columns"]],
            "rows": [[row["label"], [cell["text"] for cell in row["cells"]]]
                     for row in made["rows"]]}


def reference_view(found: reference.Table | None) -> dict | None:
    """The hand calculation in the shape of `table_view`."""
    if found is None:
        return None
    return {"columns": list(found.columns),
            "rows": [["", list(found.header)], *[[label, list(texts)]
                                                 for label, texts in found.rows]]}


def differences(ours: dict | None, theirs: dict | None, names: tuple[str, str]) -> list[str]:
    """Where two table views differ: the columns, the rows, each cell."""
    if ours is None or theirs is None:
        return [] if ours is theirs else [
            f"{names[0 if ours is not None else 1]} has the output, "
            f"{names[1 if ours is not None else 0]} has not"]
    found = []
    if ours["columns"] != theirs["columns"]:
        found.append(f"columns: {names[0]} {ours['columns']}, {names[1]} {theirs['columns']}")
    if [row[0] for row in ours["rows"]] != [row[0] for row in theirs["rows"]]:
        found.append(f"rows: {names[0]} {[row[0] for row in ours['rows']]}, {names[1]} "
                     f"{[row[0] for row in theirs['rows']]}")
    if found:
        return found
    for (label, one), (_, two) in zip(ours["rows"], theirs["rows"], strict=True):
        for column, first, second in zip(ours["columns"], one, two, strict=True):
            if first != second:
                found.append(f"row '{label or 'header'}', column '{column}': {names[0]} "
                             f"{first!r}, {names[1]} {second!r}")
    return found


def changed_cells(one: dict | None, two: dict | None) -> int:
    """How many cells two table views do not share, by row label and column label."""
    def cells(view: dict | None) -> dict[tuple[str, str], str]:
        if view is None:
            return {}
        return {(label, column): text for label, texts in view["rows"]
                for column, text in zip(view["columns"], texts, strict=True)}

    first, second = cells(one), cells(two)
    count = sum(1 for key in set(first) | set(second) if first.get(key) != second.get(key))
    if count == 0 and one != two:   # the same cells in another order
        return max(len(first), 1)
    return count


def p2(tables: reference.Tables, values: dict[str, dict], arms: list[dict],
       made: dict | None) -> list[str]:
    """Why a grid is not the hand calculation of its decisions on these SDTM rows."""
    try:
        expected = reference.table(tables, values, [
            reference.Arm(arm["code"], arm["dose"], tuple(arm["names"])) for arm in arms])
    except reference.CannotCalculate as error:
        return [f"the reference cannot be calculated: {error}"]
    return differences(table_view(made), reference_view(expected), ("the grid", "the reference"))


# ---- P3 --------------------------------------------------------------------------------


def p3(root: Path, kit_dir: Path, which: str, records: list[dict],
       catalog: catalogs.Catalog) -> tuple[list[str], list[str]]:
    """The lines of the trace check of one dataset of a kit, and its problems."""
    import json

    import pyarrow.parquet as pq

    sdtm_dir, place = gold.PLACES[which]
    folder = kit_dir / place
    expected = {path.stem.upper(): pq.read_schema(path).names
                for path in sorted((folder / gold.ADAM).glob("*.parquet"))}
    sdtm = {path.stem.upper(): set(pq.read_schema(path).names)
            for path in sorted((kit_dir / sdtm_dir).glob("*.parquet"))}
    lines, problems = graph.check_graph(root, folder / gold.GRAPH, expected, {}, sdtm)
    grids = {}
    for path in sorted((folder / gold.GRID).glob("*.json")):
        if not path.name.endswith(".shell.json"):
            with open(path, encoding="ascii") as handle:
                grids[path.name[:-len(".json")]] = json.load(handle)
    more, behind = graph.check_cells(folder / gold.GRAPH, grids)
    lines += more
    problems += behind
    with open(folder / gold.GRAPH / "coverage.json", encoding="ascii") as handle:
        coverage = json.load(handle)
    reached = coverage.get("decisions") or {}
    nodes = {node["id"] for node in read_jsonl(folder / gold.GRAPH / "nodes.jsonl")}
    # The reads edges of an analysis are what the ARS file says it reads, no fewer: the
    # check of the cells is content with one reads edge per analysis.
    event = ars.index(ars.read(folder / gold.ARS_OUT / f"{gold.EVENT}.json"))
    reads: dict[str, set[str]] = {}
    for edge in read_jsonl(folder / gold.GRAPH / "edges.jsonl"):
        if edge["type"] == "reads":
            reads.setdefault(edge["from"], set()).add(edge["to"])
    for name in sorted(node for node in nodes if node.startswith("ars:")):
        named = {graph.adam_id(dataset, variable) for _, dataset, variable in ars.reads(
            event, name[len("ars:"):], gold.SUBJECT_KEY)}
        if reads.get(name, set()) != named:
            problems.append(f"{name}: its reads edges are not the columns the ARS file names: "
                            f"{sorted(named ^ reads.get(name, set()))[:4]}")
    wanted = {gold.decision_id(record, catalog) for record in records}
    problems += [f"{name}: a decision of the kit without a node" for name in sorted(
        wanted - nodes)]
    problems += [f"{name}: a decision node that is no decision of the kit" for name in sorted(
        {node for node in nodes if node.startswith("decision:")} - wanted)]
    problems += [f"{name}: coverage.json does not say what the decision sets"
                 for name in sorted(wanted - set(reached))]
    # Every cell that prints a number has a decision behind it: an analysis it shows is
    # set by a decision (its analysis set, its grouping, its rows).
    read = {element for entry in reached.values() for element in entry["read"]}
    for _, made in sorted(grids.items()):
        for row in made["rows"]:
            for cell in row["cells"]:
                analyses = {"ars:" + key[len("ard:"):].split("/")[0] for key in cell["ard"]}
                if any(character.isdigit() for character in cell["text"]) and not (
                        analyses & read):
                    problems.append(f"{cell['id']}: no decision of the kit sets an analysis "
                                    "it shows")
    applicable = sorted(name for name, entry in reached.items() if entry["read"])
    columns = sum(len(names) for names in expected.values())
    on_the_way = len({element for element in read if element.startswith("adam:")
                      and element.split(".", 1)[1] in expected.get(
                          element[len("adam:"):].split(".", 1)[0], [])})
    lines.append(f"decisions: {len(wanted)} in the kit, {len(applicable)} set an element the "
                 f"output reads, {len(wanted) - len(applicable)} do not")
    lines.append(f"ADaM output columns: {columns}; set by a decision and on the way of a cell: "
                 f"{on_the_way}; the others are read by no cell of this output or are set by "
                 "the house standard")
    return lines, problems


# ---- P4 --------------------------------------------------------------------------------


def options(entry: catalogs.Entry, design: dict, parameters: dict,
            values: dict[str, dict]) -> list[dict]:
    """The values a decision of a kit is changed between: the gold value first.

    One value per alternative, with the slot values that fit the design; an
    entry with one alternative is changed between the values of its slots.
    The control of a total column over the active arms is the label that the
    treatment columns of this vector give the placebo arm.
    """
    current = values[entry.id]
    found = [current]
    for value in decisions.variants(entry, design, parameters):
        if value["rule"] == current["rule"]:
            continue
        if entry.id == "tfl.columns.total" and value["rule"] == "active_arms":
            value = {**value, "control": decisions.placebo_label(design, values)}
        found.append(value)
    if len(found) == 1:
        slots = decisions.slot_values(entry.id, current["rule"], design, parameters)
        for name, choices in slots.items():
            found += [{**current, name: choice} for choice in choices
                      if choice != current[name]]
    return found


def label(value: dict, among: list[dict]) -> str:
    """How a value is named in the matrix: its rule, with its slots where rules repeat."""
    if sum(1 for other in among if other["rule"] == value["rule"]) == 1:
        return value["rule"]
    slots = ", ".join(f"{key}={value[key]}" for key in sorted(value) if key != "rule")
    return f"{value['rule']}({slots})"


def claims(entry_id: str, one: dict, two: dict, values: dict[str, dict], parameters: dict,
           reach_tables: dict[str, dict]) -> bool:
    """Whether the log of probes claims that two values of a decision can differ in the
    output: the values differ (two alternatives, or two values of the slots of an entry with
    one alternative: finding H1 of the gen-2b review), and the condition of `REACHES` that
    the log repeats holds for the decision vector."""
    return one != two and entry_id in reach_tables and probes.reaches(
        entry_id, one["rule"], two["rule"], values, parameters, reach_tables)


def mutate(root: Path, catalog: catalogs.Catalog, house: houses.House, kit_dir: Path,
           which: str, design: dict, records: list[dict], reached: dict[str, dict],
           log: list[dict], tables: reference.Tables, scratch: Path,
           reach_tables: dict[str, dict] | None = None) -> tuple[dict, list[str], list[str]]:
    """The identifiability matrix of one dataset of a kit; its defects; why the kit is unfit.

    For every decision of the slice that the kit makes: every value of
    `options` is compiled and built, the grids are compared pair by pair,
    and each build is held against the reference. Returns

    - the matrix: the content of identifiability.json;
    - the defects: a variant that cannot be built or that differs from its
      reference, and a decision the output does not read whose change
      changes the output;
    - what makes the kit unfit: a pair of the gold value with another
      alternative that the log of probes claims and that gives the same
      output. Such a kit does not separate a decision that the output reads
      and that data could separate; it is not written, and the gate fails.

    `reach_tables` replaces the field `reaches` of the log (for a planted
    claim).
    """
    values = decisions.as_values(records)
    parameters = next(line["parameters"] for line in log if line["data"] == which)
    if reach_tables is None:
        reach_tables = {entry_id: reach for line in log if line["data"] == which
                        for entry_id, reach in line["reaches"].items()}
    bench = gold.Workbench(root, catalog, house, kit_dir, which, scratch)
    defects: list[str] = []
    unfit: list[str] = []
    matrix = []
    builds = 0
    for entry in decisions.entries(catalog, design):
        if entry.id not in values:
            continue
        unit = decisions.OUTPUT_UNIT if entry.per_family else entry.units[0]
        name = gold.decision_id({"id": entry.id, "unit": unit}, catalog)
        choices = options(entry, design, parameters, values)
        views = []
        for choice in choices:
            changed = [{**record, "value": choice}
                       if (record["id"], record["unit"]) == (entry.id, unit) else record
                       for record in records]
            vector = decisions.as_values(changed)
            arms = gold.arms_of(design, vector)
            builds += 1
            try:
                shown = bench.show(changed, arms)
            except gold.GoldError as error:
                defects.append(f"{entry.id} = {label(choice, choices)}: cannot be built: "
                               f"{error}")
                views.append({"failed": str(error)})
                continue
            made = next(iter(shown.grids.values()), None)
            views.append(table_view(made))
            defects += [f"{entry.id} = {label(choice, choices)}: P2: {problem}"
                        for problem in p2(tables, vector, arms, made)[:5]]
        read = bool(reached.get(name, {}).get("read"))
        pairs = []
        for first, second in combinations(range(len(choices)), 2):
            separated = views[first] != views[second]
            one, two = choices[first], choices[second]
            claimed = claims(entry.id, one, two, values, parameters, reach_tables)
            pairs.append({"first": label(one, choices), "second": label(two, choices),
                          "gold": first == 0, "separated": separated,
                          "cells": changed_cells(views[first], views[second]),
                          "claimed": bool(claimed)})
            if first == 0 and claimed and not separated:
                unfit.append(f"{entry.id}: {pairs[-1]['first']} and {pairs[-1]['second']} "
                             "can differ in the output under these decisions (the log of "
                             "probes claims it); the two builds on the twin are the same")
            if first == 0 and claimed and not read:
                defects.append(f"{entry.id}: the log of probes claims a difference in the "
                               "output, and the output does not read what the decision sets")
            if not read and separated and first == 0:
                defects.append(f"{entry.id}: the output does not read what the decision sets, "
                               f"and yet {pairs[-1]['second']} gives another output")
        of_gold = [pair for pair in pairs if pair["gold"]]
        claimed_all = bool(of_gold) and all(pair["claimed"] for pair in of_gold)
        if of_gold and all(pair["separated"] for pair in of_gold):
            state, reason = "separated", ""
        elif not of_gold:
            state, reason = NO_ALTERNATIVE, ("the entry has one alternative, and its slot "
                                             "can take one value in this study")
        elif not read:
            state, reason = "unseparated", NOT_READ
        else:
            same = ", ".join(pair["second"] for pair in of_gold if not pair["separated"])
            state = "unseparated"
            note = (reach_tables.get(entry.id) or {}).get("note")
            reason = f"{NO_PROBE}" + (f"; {note}" if note else "") + \
                f": the same output under {same}"
        matrix.append({"id": entry.id, "unit": unit, "read": read, "applicable": claimed_all,
                       "identifiable": state, "reason": reason,
                       "gold": label(choices[0], choices), "pairs": pairs})
    summary = {
        "decisions": len(matrix),
        "read": sum(1 for item in matrix if item["read"]),
        "applicable": sum(1 for item in matrix if item["applicable"]),
        "separated": sorted(item["id"] for item in matrix if item["identifiable"] == "separated"),
        "unseparated_not_read": sorted(item["id"] for item in matrix
                                       if item["identifiable"] == "unseparated"
                                       and not item["read"]),
        "unseparated_read": sorted(item["id"] for item in matrix
                                   if item["identifiable"] == "unseparated" and item["read"]),
        "no_alternative": sorted(item["id"] for item in matrix
                                 if item["identifiable"] == NO_ALTERNATIVE),
        "applicable_and_unseparated": sorted(
            item["id"] for item in matrix
            if item["applicable"] and item["identifiable"] != "separated"),
        "pairs": sum(len(item["pairs"]) for item in matrix),
        "pairs_separated": sum(1 for item in matrix for pair in item["pairs"]
                               if pair["separated"]),
        "pairs_claimed": sum(1 for item in matrix for pair in item["pairs"] if pair["claimed"]),
        "builds": builds, "runs_of_yamaa": bench.runs,
    }
    return {"data": which, "output": decisions.OUTPUT_UNIT, "summary": summary,
            "decisions": matrix}, defects, unfit


def identifiable(matrix: dict) -> dict[tuple[str, str], str]:
    """(entry, unit) -> separated or unseparated, for the decision records of a kit.

    A decision with nothing to be changed to has no entry: the field
    `identifiable` of its record stays empty.
    """
    return {(item["id"], item["unit"]): item["identifiable"] for item in matrix["decisions"]
            if item["identifiable"] != NO_ALTERNATIVE}


def grid_of(kit_dir: Path, which: str) -> dict | None:
    """The grid of the output of the slice in a kit, as written."""
    import json

    folder = kit_dir / gold.PLACES[which][1] / gold.GRID
    paths = [path for path in sorted(folder.glob("*.json"))
             if not path.name.endswith(".shell.json")]
    if not paths:
        return None
    with open(paths[0], encoding="ascii") as handle:
        return json.load(handle)


def shell_problems(kit_dir: Path, which: str) -> list[str]:
    """The mock shell shows no number, and it has the cells of its grid."""
    import json

    folder = kit_dir / gold.PLACES[which][1] / gold.GRID
    problems = []
    for path in sorted(folder.glob("*.shell.json")):
        with open(path, encoding="ascii") as handle:
            shell = json.load(handle)
        with open(folder / path.name.replace(".shell.json", ".json"), encoding="ascii") as handle:
            made = json.load(handle)
        problems += [f"{cell['id']}: the mock shell shows a number: {cell['text']!r}"
                     for row in shell["rows"] for cell in row["cells"]
                     if any(character.isdigit() for character in cell["text"])]
        if [[cell["id"] for cell in row["cells"]] for row in shell["rows"]] != [
                [cell["id"] for cell in row["cells"]] for row in made["rows"]] or \
                display.texts(shell).keys() != display.texts(made).keys():
            problems.append(f"{path.name}: the mock shell has other cells than the grid")
    return problems
