"""P4 on a reference study, by mutation: the class of every decision (issue #30, ADR-019).

`specfirst.machine.separation` decides the class of a decision from what
its other values change. This module makes the builds and the matrix. A
decision vector is built on the data of a study by the chain of the scorer
(`specfirst.score.candidate.Machine`: the compiler, yamaa, the Python result
engine, the grids of layout draft 0): once at gold, and once for every other
value of every decision, with all other decisions kept.

The values tried for one decision:

- every alternative of its catalog entry with the examples of its slots,
  and every list of the gold value with one item left out
  (`compiler.other_values`: what the compile check proves the binds
  against);
- for every integer slot of the gold alternative, the values of the slot
  next to gold, one at a time, down and up, until a value separates in the
  outputs or the scan ends: at the bound of the slot, or `span` steps from
  gold (`scan`).

What an output reads (`reach`), from the gold build and from the build of
the other value: the analyses behind its cells (numerators and
denominators), their analysis sets, data subsets, groupings and methods,
the output itself in the ARS file, every part of its layout, the ADaM
columns these analyses read and every ADaM column, working column, lookup
and row template those are derived from. A value is read by an output when
an element that it changes in the compile (`candidate.element_changes`)
is in that set for either build, or when it decides whether the output is
built at all. That is static: the compile and the trace, not the data.

The matrix (`Mutation.matrix`) has one entry per decision of the units it
covers: the class, `identifiable` for the decision record, whether an
output reads it and which, every value tried with its level and its
counts, the values that reproduce, the intervals, and a reason in words.
Its summary and its review come from `specfirst.machine.separation`.

Two studies have a matrix here (`specfirst gen separate`):

    sep01           the test study of issue #30 (specfirst.gen.sep01): one
                    window that four values reproduce, one inert rule, one rule
                    separated in ADaM and not in the table
    cdiscpilot01    the pilot's SDTM as kits/cdiscpilot01 pins it, read from
                    the fetch cache; report only (PLAN.md section 6.1)

A generated kit keeps its own matrix (`specfirst.gen.verify`): P4 as stated
is its requirement, and nothing here changes its files.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from specfirst import kit as kits
from specfirst.compile import catalog as catalogs
from specfirst.compile import checks, compiler
from specfirst.gen import probes
from specfirst.machine import ars
from specfirst.machine import separation as sep
from specfirst.machine.canonical import sha256_file
from specfirst.paths import cache_dir
from specfirst.score.candidate import SUBJECT_KEY, Arms, Build, Data, Key, Machine, element_changes

Out = Callable[[str], None]
Reach = Callable[[Build], dict[str, set[str]]]
# The units of the slice "adverse event summary first" (ADR-005): what a matrix covers.
SLICE = probes.SLICE_UNITS
OUTPUT_UNIT = "tfl-ae-summary"
# How far from gold an integer slot is scanned, at most, on each side.
SPAN = 30
PILOT = "cdiscpilot01"


class SeparationError(RuntimeError):
    """A matrix cannot be made: the gold vector does not build, or the data are not there."""


# ---- values ---------------------------------------------------------------------------


def label(value: dict) -> str:
    """How a value is named in the matrix: its rule, with its slots."""
    slots = ", ".join(f"{name}={json.dumps(value[name], sort_keys=True)}"
                      for name in sorted(value) if name != "rule")
    return f"{value['rule']}({slots})" if slots else str(value["rule"])


def scan_slots(catalog: catalogs.Catalog, entry_id: str,
               value: dict) -> list[tuple[str, int, float | None, float | None]]:
    """The integer slots of the gold alternative: name, gold value, minimum, maximum."""
    try:
        alternative = catalog.entry(entry_id).alternative(value["rule"])
    except KeyError:
        return []
    return [(slot.name, value[slot.name], slot.minimum, slot.maximum) for slot in alternative.slots
            if slot.type == "int" and isinstance(value.get(slot.name), int)
            and not isinstance(value.get(slot.name), bool)]


def house_vector(catalog: catalogs.Catalog, house, stated: dict[Key, dict] | None = None,
                 output: str = OUTPUT_UNIT,
                 features: dict[str, bool] | None = None) -> list[dict]:
    """A vector for one output: every house default, for a design of these features; the
    first example of the first alternative where a decision has none; of the other table
    families only `tfl.output.include`, as `not_included`; then the values of `stated`."""
    found = []
    for record in checks.base_vector(catalog, house, features):
        kind = catalog.units[record["unit"]].kind
        if kind == "table_family" and record["unit"] != output:
            if record["id"] != "tfl.output.include":
                continue
            record = {**record, "value": {"rule": "not_included"}}
        key = (record["id"], record["unit"])
        if stated and key in stated:
            record = {**record, "value": stated[key]}
        found.append({"id": record["id"], "unit": record["unit"], "value": record["value"]})
    missing = sorted(set(stated or {}) - {(r["id"], r["unit"]) for r in found})
    if missing:
        raise SeparationError(f"not decisions of the vector: {missing}")
    return found


# ---- what an output reads -------------------------------------------------------------


def reach(build: Build) -> dict[str, set[str]]:
    """For every output a build prints: the elements on the way of its cells."""
    if not build.ok or build.ars is None:
        return {}
    event = ars.index(build.ars)
    following: dict[str, set[str]] = {}
    for edge in build.edges:
        if edge["type"] == "derives_from":
            following.setdefault(edge["from"], set()).add(edge["to"])
    found = {}
    for output, grid in sorted(build.grids.items()):
        unit = build.outputs.get(output)
        elements = {f"ars:{output}"}
        elements |= {f"layout:{unit}/{part}" for part in build.layouts.get(unit) or {}}
        analyses = set()
        for row in grid["rows"]:
            for cell in row["cells"]:
                path = build.paths.get(cell["id"])
                if path is not None:
                    analyses |= set(path.analyses)
        columns = set()
        for name in sorted(analyses):
            analysis = event.analyses[name]
            elements |= {f"ars:{part}" for part in (
                name, analysis.get("analysisSetId"), analysis.get("dataSubsetId"),
                analysis.get("methodId")) if part}
            elements |= {f"ars:{entry['groupingId']}"
                         for entry in analysis.get("orderedGroupings") or []}
            columns |= {f"adam:{dataset}.{variable}"
                        for _, dataset, variable in ars.reads(event, name, SUBJECT_KEY)}
        seen, stack = set(columns), list(columns)
        while stack:
            for source in following.get(stack.pop(), ()):
                if source.startswith("adam:") and source not in seen:
                    seen.add(source)
                    stack.append(source)
        for column in seen:
            dataset = column[len("adam:"):].split(".")[0]
            elements |= {column, *(f"adam:{dataset}.{name}"
                                   for name in build.through.get(column, []))}
        found[output] = elements
    return found


# ---- the mutation ---------------------------------------------------------------------


class Mutation:
    """The builds of one decision vector on one dataset, and its matrix.

    `reach_of` replaces `reach` (a planted defect of the static reach).
    """

    def __init__(self, machine: Machine, data: Data, arms: Arms, records: list[dict],
                 span: int = SPAN, reach_of: Reach | None = None):
        self.machine = machine
        self.data = data
        self.arms = arms
        self.records = [dict(record) for record in records]
        self.span = span
        self.reach_of = reach_of or reach
        self.sdtm = None if data.sdtm is None else {
            stem: set(table.column_names) for stem, table in data.sdtm.items()}
        self.gold = machine.build(self.records, data, arms)
        if not self.gold.ok:
            raise SeparationError(f"the gold vector does not build on {data.name}: "
                                  f"{self.gold.failure}")
        self.gold_reach = self.reach_of(self.gold)
        self.gold_compiled = machine.compile(self.records, self.sdtm)
        self.builds = 1

    def _changed(self, key: Key, value: dict) -> list[dict]:
        return [{**record, "value": value} if (record["id"], record["unit"]) == key else record
                for record in self.records]

    def tried(self, key: Key, value: dict) -> dict:
        """What one other value of one decision changes: its level, its counts, and the
        outputs that read an element it changes."""
        changed = self._changed(key, value)
        built = self.machine.build(changed, self.data, self.arms)
        self.builds += 1
        compared = sep.compare(self.gold, built)
        compiled = self.machine.compile(changed, self.sdtm)
        elements = element_changes(
            None if isinstance(self.gold_compiled, str) else self.gold_compiled,
            None if isinstance(compiled, str) else compiled)
        theirs = self.reach_of(built) if built.ok else {}
        reads = sorted(output for output in set(self.gold_reach) | set(theirs)
                       if elements & (self.gold_reach.get(output, set())
                                      | theirs.get(output, set()))
                       or (built.ok and (output in self.gold.grids) != (output in built.grids)))
        return {"label": label(value), "value": value, **compared.as_dict(), "reads": reads}

    def scan(self, key: Key, value: dict, slot: str, gold: int, minimum: float | None,
             maximum: float | None, seen: dict[str, dict]) -> tuple[dict, list[dict]]:
        """The interval of an integer slot of the gold value, and the values it scanned
        (each once: a value that `seen` holds is not built again)."""
        low_limit, high_limit = gold - self.span, gold + self.span
        if minimum is not None:
            low_limit = max(low_limit, int(minimum))
        if maximum is not None:
            high_limit = min(high_limit, int(maximum))
        levels: dict[int, str] = {}
        scanned = []
        for step, limit in ((-1, low_limit), (1, high_limit)):
            number = gold + step
            while (number >= limit) if step < 0 else (number <= limit):
                other = {**value, slot: number}
                name = label(other)
                if name not in seen:
                    seen[name] = self.tried(key, other)
                    scanned.append(seen[name])
                levels[number] = seen[name]["level"]
                if levels[number] in sep.SEPARATING:
                    break
                number += step
        return sep.interval(slot, gold, levels, low_limit, high_limit, minimum,
                            maximum), scanned

    def decision(self, key: Key) -> dict:
        """The entry of one decision in the matrix."""
        catalog = self.machine.catalog
        value = next(r["value"] for r in self.records if (r["id"], r["unit"]) == key)
        seen: dict[str, dict] = {}
        values = []
        for other in compiler.other_values(catalog, key[0], value):
            name = label(other)
            if name not in seen:
                seen[name] = self.tried(key, other)
                values.append(seen[name])
        intervals = []
        for slot, gold, minimum, maximum in scan_slots(catalog, key[0], value):
            span, scanned = self.scan(key, value, slot, gold, minimum, maximum, seen)
            intervals.append(span)
            values += scanned
        values.sort(key=lambda item: item["label"])
        read = any(item["reads"] for item in values)
        klass = sep.classify(read, [item["level"] for item in values])
        outputs = sorted({output for item in values for output in item["reads"]})
        reproduce = [item["label"] for item in values if item["level"] == "none"]
        below = [item["label"] for item in values if item["level"] in sep.BELOW_OUTPUTS]
        item = {"id": key[0], "unit": key[1], "gold": label(value), "value": value,
                "class": klass,
                "identifiable": sep.identifiable(klass), "read": read, "outputs": outputs,
                "reproduce": reproduce, "dataset_only": below, "intervals": intervals,
                "reason": reason(klass, outputs, reproduce, below), "values": values}
        return item

    def matrix(self, units: tuple[str, ...] = SLICE, study: str = "",
               keys: list[Key] | None = None) -> dict:
        """The matrix of the decisions of these units (or of `keys`), in vector order."""
        wanted = [(r["id"], r["unit"]) for r in self.records
                  if r["unit"] in units and r.get("value") is not None]
        if keys is not None:
            missing = sorted(set(keys) - set(wanted))
            if missing:
                raise SeparationError(f"not decisions of the matrix: {missing}")
            wanted = [key for key in wanted if key in keys]
        decisions = [self.decision(key) for key in wanted]
        made = {"study": study, "data": self.data.name, "units": list(units), "span": self.span,
                "outputs": sorted(self.gold.grids), "decisions": decisions}
        made["summary"] = {**sep.summary(decisions), "builds": self.builds}
        made["review"] = sep.review(made)
        made["problems"] = [problem for item in decisions for problem in sep.problems(item)]
        return made


def reason(klass: str, outputs: list[str], reproduce: list[str], below: list[str]) -> str:
    """The class of a decision in words."""
    if klass == "inert":
        return "no output reads what the decision sets, under any value tried"
    if klass == sep.NO_ALTERNATIVE:
        return "the decision has no other value to be changed to"
    if klass == "separated":
        return "every value tried changes the outputs"
    if klass == "unseparated":
        return ("the same ADaM datasets, results and outputs as gold under "
                + ", ".join(reproduce) + ": the data cannot tell them apart")
    return (f"the outputs that read it ({', '.join(outputs)}) are the same as gold under "
            + ", ".join(below) + "; the ADaM datasets or the results differ")


def lines(matrix: dict) -> list[str]:
    """A matrix as text: the summary, the review, and every decision with its values."""
    summary = matrix["summary"]
    said = [f"P4 by class on {matrix['data']} ({matrix['study']}): {summary['decisions']} "
            f"decisions of the units {', '.join(matrix['units'])}; outputs "
            f"{', '.join(matrix['outputs']) or 'none'}; {summary['builds']} builds; integer "
            f"slots scanned up to {matrix['span']} steps from gold"]
    for klass in (*sep.REVIEW_ORDER,):
        names = summary[klass]
        said.append(f"  {klass}: {len(names)}" + (f": {', '.join(names)}" if names else ""))
    said.append("  values tried, by level: " + ", ".join(
        f"{level} {count}" for level, count in summary["values"].items()))
    said.append("  review (unseparated first):")
    items = {(item["id"], item["unit"]): item for item in matrix["decisions"]}
    for entry in matrix["review"]:
        more = ""
        shown = _not_in_an_interval(items[(entry["id"], entry["unit"])],
                                    entry.get("reproduce") or [])
        if shown:
            more += "; reproduce: " + ", ".join(shown)
        if entry.get("outputs"):
            more += "; outputs: " + ", ".join(entry["outputs"])
        for span in entry.get("intervals") or []:
            more += (f"; {span['slot']} from {span['low']} ({span['below']}) to {span['high']} "
                     f"({span['above']})")
        said.append(f"    {entry['class']}{'' if entry['asked'] else ' (not asked)'}: "
                    f"{entry['id']} ({entry['unit']}){more}")
    said.append("  decisions:")
    for item in matrix["decisions"]:
        said.append(f"    {item['id']} ({item['unit']}) = {item['gold']}: {item['class']}, "
                    f"identifiable {item['identifiable']}; {item['reason']}")
        for value in item["values"]:
            said.append(f"      {value['label']}: {value['level']} (adam {value['adam']}, "
                        f"results {value['results']}, cells {value['cells']})"
                        + (f"; read by {', '.join(value['reads'])}" if value["reads"] else "")
                        + (f"; {value['failure'][:160]}" if value.get("failure") else ""))
    said += [f"  problem: {problem}" for problem in matrix["problems"]]
    said.append(f"  problems: {len(matrix['problems'])}")
    return said


def _not_in_an_interval(item: dict, labels: list[str]) -> list[str]:
    """The labels of values that no interval of the decision stands for. A value inside an
    interval is the gold value with that slot at a number from the low to the high end."""
    values = {value["label"]: value["value"] for value in item["values"]}
    found = []
    for name in labels:
        value = values[name]
        covered = False
        for span in item.get("intervals") or []:
            slot = span["slot"]
            number = value.get(slot)
            same_rest = ({k: part for k, part in value.items() if k != slot}
                         == {k: part for k, part in item["value"].items() if k != slot})
            if same_rest and isinstance(number, int) and span["low"] <= number <= span["high"]:
                covered = True
        if not covered:
            found.append(name)
    return found


# ---- the pilot ------------------------------------------------------------------------


def _pinned(root: Path, kit: kits.Kit, path: str) -> Path:
    entry = next((item for item in kit.files if item.path == path), None)
    if entry is None:
        raise SeparationError(f"the kit {kit.id} lists no file {path}")
    origin = cache_dir(root) / entry.source / entry.origin
    if not origin.is_file():
        raise SeparationError(f"{entry.source}:{entry.origin} is not in the fetch cache: run "
                              "`specfirst fetch`")
    if sha256_file(origin) != entry.sha256:
        raise SeparationError(f"{entry.source}:{entry.origin} does not have the pinned SHA-256")
    return origin


def pilot_data(root: Path) -> Data:
    """The SDTM of the pilot, every file that kits/cdiscpilot01 pins, its hash checked."""
    import pyarrow.parquet as pq

    kit = kits.load_kit(root, PILOT)
    prefix = f"{kit.sdtm}/"
    tables = {}
    for item in sorted(kit.files, key=lambda item: item.path):
        if item.path.startswith(prefix) and item.path.endswith(".parquet"):
            stem = item.path[len(prefix):-len(".parquet")]
            tables[stem] = pq.read_table(_pinned(root, kit, item.path))
    if "dm" not in tables:
        raise SeparationError(f"the kit {PILOT} pins no DM")
    return Data(f"{PILOT}/sdtm", sdtm=tables)


def pilot_arms(data: Data) -> Arms:
    """The arms of the pilot from its SDTM, in the order of their dose: code (ARMCD), dose
    (the highest EXDOSE of the arm's exposure records: the high dose of the pilot is
    titrated, 54 mg and then 81 mg), and the texts that name the arm (ARM, and EXTRT where
    no other arm's exposure records have the same treatment name). An arm without
    exposure records (the screen failures, ARMCD `Scrnfail` in the pilot) is no arm of a
    treatment column. Two arms with the same highest dose are refused: their order would
    be a guess."""
    dm, ex = data.sdtm["dm"], data.sdtm["ex"]
    arm_of = {}
    for subject, code, name in zip(dm.column("USUBJID").to_pylist(),
                                   dm.column("ARMCD").to_pylist(), dm.column("ARM").to_pylist(),
                                   strict=True):
        if code and code.upper() not in ("SCRNFAIL", "NOTASSGN"):
            arm_of[subject] = (code, name)
    doses: dict[str, set[float]] = {}
    treatments: dict[str, set[str]] = {}
    for subject, treatment, dose in zip(ex.column("USUBJID").to_pylist(),
                                        ex.column("EXTRT").to_pylist(),
                                        ex.column("EXDOSE").to_pylist(), strict=True):
        if subject in arm_of:
            code = arm_of[subject][0]
            doses.setdefault(code, set()).add(float(dose))
            treatments.setdefault(code, set()).add(treatment)
    names = {code: name for code, name in arm_of.values() if code in doses}
    found = []
    for code in sorted(names):
        own = {name for name in treatments[code]
               if not any(name in treatments[other] for other in treatments if other != code)}
        found.append({"code": code, "dose": max(doses[code]),
                      "names": sorted({names[code], *own})})
    if len({arm["dose"] for arm in found}) != len(found):
        raise SeparationError("two arms of the study have the same highest dose")
    return sorted(found, key=lambda arm: arm["dose"])


# The vector on the pilot, report only. `house`: the house standard alone for the adverse
# event summary (the vector of arm S of read-1a's pilot report). Under open-default@2 its
# treatment-emergent window of 30 days shows the interval of a numeric parameter on real
# data; the vector `window` of issue #30 (the house of open-default@1 with that window)
# is the same vector now and is gone (ADR-020, #3).
PILOT_VECTORS: dict[str, dict[Key, dict]] = {
    "house": {},
}


def pilot_matrix(root: Path, vector: str = "house", span: int = SPAN,
                 machine: Machine | None = None) -> dict:
    """The matrix of the slice on the pilot's SDTM under one of `PILOT_VECTORS`."""
    if vector not in PILOT_VECTORS:
        raise SeparationError(f"no vector {vector!r} of the pilot: {', '.join(PILOT_VECTORS)}")
    machine = machine or Machine(root)
    data = pilot_data(root)
    from specfirst.score.pilot import PILOT_FEATURES

    records = house_vector(machine.catalog, machine.house, PILOT_VECTORS[vector],
                           features=PILOT_FEATURES)
    made = Mutation(machine, data, pilot_arms(data), records, span).matrix(
        study=f"{PILOT}, vector {vector}")
    made["vector"] = vector
    return made


def write(matrix: dict, path: Path) -> None:
    """A matrix as canonical JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(matrix, indent=1, sort_keys=True) + "\n", encoding="ascii",
                    newline="\n")
