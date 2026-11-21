"""The compiler: decisions to yamaa, ARS and layout files (PLAN.md sections 5.2, 7.1).

For a catalog decision the fragment is a pure function of the decision
value. Each alternative of an entry has one fragment in the entry's compile
template (`standard/catalog@<n>/templates/<id>.yaml`):

    alternatives:
      <alternative>:
        adam:                 yamaa fragments, by ADaM dataset
          ADAE: {columns: [...], intermediates: [...], rows: [...]}
        params:               values for the ARS and layout templates
          name: value

ADaM. The house parent spec of a dataset holds what no decision changes and
reads the columns that decisions own. The compiled spec of a dataset is one
entry file that names the parent and includes one fragment per decision.
Two decisions never write the same column; yamaa composes the layers.

Tables. The house has one ARS template and one layout template per table
family, with named parameters. A decision contributes parameter values: a
module decision to every family, a table-family decision to its own.

Everything written is a function of (catalog, house, decisions): no clock,
and a fixed order everywhere (rule R4).

Two options, both off by default, so that `specfirst compile` and the
generator compile as they always did:

    pending   (the scorer's mode, docs/decisions/ADR-014.md) a decision that
              a dataset or a table needs and that has no value does not stop
              the compile. What it binds is left out and listed in
              `Compiled.pending`: the ADaM columns and lookups its fragments
              would write and the output columns that derive from them, a
              dataset whose records rest on it (its keys derive from it, or it
              adds a row template), the analyses that read what is left out
              and their layout rows, an output that cannot be built without
              it. An optional decision of the house that the study leaves out
              is pending only where something reads its columns.
    sdtm      the columns of each SDTM file of the study. An output column
              that derives from a variable the SDTM lacks is left out, with a
              warning, when SDTMIG does not require the variable, and so is a
              dataset whose records rest on one; a table that reads what is
              left out is not produced (`Compiled.left_out`). A Required
              variable that the data lack stops the compile.

yamaa evaluates the columns an output needs and nothing else, so a column
is left out by leaving it out of the output: the house parent specs are
not changed. What derives from what is read from the composed spec by the
static lineage of the machine (`specfirst.machine.lineage`).
"""

from __future__ import annotations

import copy
import hashlib
import json
import os
from collections.abc import Collection, Mapping
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from specfirst.compile.catalog import Catalog
from specfirst.compile.house import House
from specfirst.compile.slots import SlotError, check_value
from specfirst.compile.standard_form import StandardForm, StandardFormError
from specfirst.compile.template import TemplateError, UndefinedName, evaluate

YAMAA_VERSION = "1.0"
ARS_LISTS = ("analysisSets", "analysisGroupings", "dataSubsets", "methods", "analyses", "outputs")
FRAGMENT_PARTS = ("intermediates", "columns", "rows")
# The version of SDTMIG whose core designations decide what may be left out: the one the
# generator writes (specfirst.gen.sdtm, which lists the variables of each domain it knows).
SDTMIG = "SDTMIG v3.4"
CORE_NAMES = {"Req": "Required", "Exp": "Expected", "Perm": "Permissible"}

Key = tuple[str, str]


class CompileError(ValueError):
    """The decisions cannot be compiled. `problems` lists every reason."""

    def __init__(self, problems: list[str]):
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass
class Compiled:
    """What one compile produced. Paths are relative to the output folder."""

    files: dict[str, str] = field(default_factory=dict)  # path -> text
    binds: dict[tuple[str, str], list[str]] = field(default_factory=dict)
    layout_binds: dict[tuple[str, str], list[str]] = field(default_factory=dict)
    datasets: list[str] = field(default_factory=list)
    adam_columns: dict[str, list[str]] = field(default_factory=dict)
    families: list[str] = field(default_factory=list)
    ars: dict | None = None
    layouts: dict[str, dict] = field(default_factory=dict)
    # The pending mode: per decision without a value, the elements left out for it
    # (`adam:<DATASET>.<COLUMN>`, `ars:<analysis ID>`, `output:<output ID>`).
    pending: dict[Key, list[str]] = field(default_factory=dict)
    # Given the columns of the SDTM: the elements left out because the SDTM lacks a
    # variable, each with the reason; and the warnings that say so.
    left_out: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def manifest(self) -> dict:
        found = {
            "datasets": self.datasets,
            "families": self.families,
            "files": {path: hashlib.sha256(text.encode("ascii")).hexdigest()
                      for path, text in sorted(self.files.items())},
            "decisions": [
                {"id": entry_id, "unit": unit, "binds": self.binds.get((entry_id, unit), []),
                 "layout": self.layout_binds.get((entry_id, unit), [])}
                for entry_id, unit in sorted(set(self.binds) | set(self.layout_binds))
            ],
        }
        # Only when there is something to say: a complete compile has the manifest
        # it always had (the compile.json of a generated kit).
        if self.pending:
            found["pending"] = [{"id": key[0], "unit": key[1], "left_out": elements}
                                for key, elements in sorted(self.pending.items())]
        if self.left_out:
            found["left_out"] = dict(sorted(self.left_out.items()))
        if self.warnings:
            found["warnings"] = list(self.warnings)
        return found

    def write(self, out_dir: Path) -> None:
        files = dict(self.files)
        files["compile.json"] = canonical_json(self.manifest())
        for relative, text in sorted(files.items()):
            path = out_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="ascii", newline="\n")


def canonical_json(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def canonical_yaml(data: object) -> str:
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False, width=10_000,
                          allow_unicode=False)


def compile_template(catalog: Catalog, entry_id: str) -> dict:
    """The compile template of an entry: {alternative: {adam, params}}."""
    entry = catalog.entry(entry_id)
    try:
        raw = catalog.read_yaml(entry.compile)
    except (OSError, yaml.YAMLError) as error:
        raise CompileError([f"{entry_id}: cannot read {entry.compile}: {error}"]) from None
    if not isinstance(raw, dict) or raw.get("entry") != entry_id:
        raise CompileError([f"{entry.compile} is not the compile template of {entry_id}"])
    alternatives = raw.get("alternatives")
    if not isinstance(alternatives, dict):
        raise CompileError([f"{entry.compile} has no alternatives"])
    return alternatives


def fragment_of(catalog: Catalog, entry_id: str, value: dict) -> dict:
    """The evaluated fragment of a decision value: {adam: {...}, params: {...}}."""
    alternatives = compile_template(catalog, entry_id)
    rule = value["rule"]
    if rule not in alternatives:
        raise CompileError([f"{entry_id}: the compile template has no alternative '{rule}'"])
    scope = {key: item for key, item in value.items() if key != "rule"}
    try:
        fragment = evaluate(alternatives[rule] or {}, scope)
    except TemplateError as error:
        raise CompileError([f"{entry_id}/{rule}: {error}"]) from None
    unknown = sorted(set(fragment) - {"adam", "params"})
    if unknown:
        raise CompileError([f"{entry_id}/{rule}: a compile template may not hold {unknown}"])
    return {"adam": fragment.get("adam") or {}, "params": fragment.get("params") or {}}


def _decided(catalog: Catalog, records: list[dict]) -> tuple[dict, list[str]]:
    """The records that carry a value, by (entry ID, unit), with what is wrong."""
    form = StandardForm(catalog)
    problems: list[str] = []
    decided: dict[tuple[str, str], dict] = {}
    seen: set[tuple[str, str]] = set()
    for record in records:
        key = (str(record.get("id")), str(record.get("unit")))
        if key[0].startswith("custom:"):
            problems.append(f"{key[0]}: a custom decision needs a hand-written fragment")
            continue
        if key in seen:
            problems.append(f"{key[0]} ({key[1]}): more than one record")
            continue
        seen.add(key)
        if record.get("value") is None:
            continue
        try:
            form.check_value(key[0], key[1], record["value"])
        except StandardFormError as error:
            problems.append(str(error))
            continue
        decided[key] = record
    return decided, problems


def compile_decisions(
    catalog: Catalog,
    house: House,
    records: list[dict],
    house_ref: str,
    sdtm_dir: str = "../sdtm",
    adam_dir: str = ".",
    data_format: str = "parquet",
    pending: bool = False,
    sdtm: Mapping[str, Collection[str]] | None = None,
) -> Compiled:
    """Compile decision records into yamaa specs, an ARS file and layout files.

    `house_ref` is the path of the house folder as the compiled ADaM specs
    name it, relative to their folder `adam/`. `sdtm_dir` and `adam_dir`
    are where those specs read SDTM and write ADaM, relative to `adam/` too.
    `pending` and `sdtm` (the columns of each SDTM file, by file stem) are
    the two options of the module docstring. Raises CompileError with every
    problem found.
    """
    decided, problems = _decided(catalog, records)
    fragments: dict[tuple[str, str], dict] = {}
    for key in catalog.keys():
        if key in decided:
            try:
                fragments[key] = fragment_of(catalog, key[0], decided[key]["value"])
            except CompileError as error:
                problems += error.problems
    if problems:
        raise CompileError(problems)
    result = Compiled()
    gone: dict[str, _Gone] = {}
    problems += _compile_adam(catalog, house, fragments, result, house_ref, sdtm_dir,
                              adam_dir, data_format, pending, sdtm, gone)
    problems += _compile_tables(catalog, house, fragments, result, pending, gone)
    if not problems and result.ars is not None:
        problems += unread_variables(result)
    if problems:
        raise CompileError(problems)
    for key in result.pending:
        result.pending[key] = sorted(set(result.pending[key]))
    return result


# -- ADaM --------------------------------------------------------------------


def adam_writers(catalog: Catalog) -> dict[str, list[str]]:
    """For each ADaM dataset, the entries whose fragments write into it, in catalog order."""
    writers: dict[str, list[str]] = {}
    for entry in catalog.entries.values():
        datasets: set[str] = set()
        for alternative in compile_template(catalog, entry.id).values():
            datasets |= set((alternative or {}).get("adam") or {})
        for dataset in sorted(datasets):
            writers.setdefault(dataset, []).append(entry.id)
    return writers


@dataclass
class _Gone:
    """Why an element is left out: decisions without a value, variables the SDTM lacks
    (`<DOMAIN>.<VARIABLE>`)."""

    keys: set = field(default_factory=set)
    absent: set = field(default_factory=set)

    def add(self, other: _Gone) -> bool:
        before = (len(self.keys), len(self.absent))
        self.keys |= other.keys
        self.absent |= other.absent
        return before != (len(self.keys), len(self.absent))


def _parts_written(catalog: Catalog, entry_id: str, dataset: str) -> dict[str, set[str]]:
    """What some alternative of an entry writes into a dataset: column names, the IDs
    of lookups (intermediates) and of row templates."""
    found: dict[str, set[str]] = {"columns": set(), "intermediates": set(), "rows": set()}
    for alternative in compile_template(catalog, entry_id).values():
        body = ((alternative or {}).get("adam") or {}).get(dataset) or {}
        for part, key in (("columns", "name"), ("intermediates", "id"), ("rows", "id")):
            found[part] |= {str(member.get(key)) for member in body.get(part) or []
                            if isinstance(member, dict)}
    return found


def _sdtmig_core(domain: str, variable: str) -> str | None:
    """The core designation (Req, Exp, Perm) of a variable in SDTMIG v3.4, as the
    generator lists the domains it writes; None for a variable it does not list."""
    from specfirst.gen import sdtm as sdtmig

    known = sdtmig.DOMAINS.get(domain)
    if known is None:
        return None
    try:
        return known.variable(variable).core
    except KeyError:
        return None


def sdtmig_variables(domain: str) -> set[str]:
    from specfirst.gen import sdtm as sdtmig

    known = sdtmig.DOMAINS.get(domain)
    return {variable.name for variable in known.variables} if known else set()


def absent_reason(variable: str) -> str:
    """Why a column that reads `<DOMAIN>.<VARIABLE>` is left out."""
    domain, name = variable.split(".", 1)
    core = _sdtmig_core(domain, name)
    said = (f"{CORE_NAMES[core]} in {SDTMIG}" if core in CORE_NAMES
            else f"not a variable of {domain} in {SDTMIG} as specfirst.gen.sdtm lists it")
    return f"the SDTM {domain} has no {name} ({said})"


def _composed(parent: dict, bodies: list[dict], columns: list[str]) -> dict:
    """The parent spec with the fragments included, as yamaa composes them: a fragment
    adds columns and intermediates (the compiler has made sure that no two write the
    same one), and adds its derivations to a row template of the same ID."""
    spec = copy.deepcopy(parent)
    for part in FRAGMENT_PARTS:
        members = list(spec.get(part) or [])
        for body in bodies:
            for member in copy.deepcopy(body.get(part) or []):
                same = next((m for m in members if part == "rows"
                             and m.get("id") == member.get("id")), None)
                if same is None:
                    members.append(member)
                    continue
                for field_name, value in member.items():
                    if field_name == "derivations":
                        same.setdefault("derivations", {}).update(value or {})
                    elif field_name != "id":
                        same[field_name] = value
        if members:
            spec[part] = members
    for row in spec.get("rows") or []:
        row.setdefault("dataset", spec.get("base"))
    spec["output"] = {**(spec.get("output") or {}), "columns": list(columns)}
    return spec


def _why(why: _Gone) -> str:
    said = [absent_reason(variable) for variable in sorted(why.absent)]
    if why.keys:
        said.append("it waits for " + ", ".join(key[0] for key in sorted(why.keys)))
    return "; ".join(said)


def _left_out(meta: dict, house: House, spec: dict, columns: list[str],
              waiting: dict[str, Key], sdtm: Mapping[str, Collection[str]] | None,
              gone: dict[str, _Gone], built: dict[str, list[str]]) -> dict[str, _Gone]:
    """The output columns of a dataset that cannot be built, each with why.

    A column cannot be built when it reads a column or a lookup that a
    pending decision would write (`waiting`: name -> decision), a variable
    that the SDTM lacks, an output column of another dataset that was left
    out (`gone`; `built`: the output columns of the datasets compiled
    before), or a column that cannot be built.
    """
    from specfirst.machine import lineage

    sdtm_inputs: dict[str, str] = {}
    schemas: dict[str, set[str]] = {}
    for alias, stem in (meta.get("inputs") or {}).items():
        if alias in house.adam:
            schemas[alias] = set(built.get(alias, ()))
        else:
            sdtm_inputs[alias] = stem
            schemas[alias] = sdtmig_variables(stem.upper()) | set(
                (sdtm or {}).get(stem, ()))
    reads: dict[str, tuple[set[str], set[str], set[str]]] = {}
    for read in lineage.column_dependencies(spec, schemas).reads:
        refs, unresolved, unknown = reads.setdefault(read.element, (set(), set(), set()))
        refs |= read.refs
        unresolved |= read.unresolved
        unknown |= read.unknown
    causes: dict[str, _Gone] = {}
    for element, (refs, unresolved, unknown) in reads.items():
        found = _Gone()
        found.keys |= {waiting[name] for name in unknown if name in waiting}
        for ref in refs | unresolved:
            alias, _, name = ref.partition(".")
            if alias in sdtm_inputs:
                if sdtm is not None and name not in set(sdtm.get(sdtm_inputs[alias], ())):
                    found.absent.add(f"{sdtm_inputs[alias].upper()}.{name}")
            elif alias in waiting and name:  # a column of a lookup that is not written
                found.keys.add(waiting[alias])
            elif f"adam:{alias}.{name}" in gone:
                found.add(gone[f"adam:{alias}.{name}"])
        if found.keys or found.absent:
            causes[element] = found
    grown = True
    while grown:
        grown = False
        for element, (refs, _, _) in reads.items():
            for ref in refs:
                if ref != element and ref in causes:
                    grown |= causes.setdefault(element, _Gone()).add(causes[ref])
    return {name: causes[f"spec.{name}"] for name in columns if f"spec.{name}" in causes}


def _compile_adam(catalog: Catalog, house: House, fragments: dict, result: Compiled,
                  house_ref: str, sdtm_dir: str, adam_dir: str, data_format: str,
                  pending: bool = False, sdtm: Mapping[str, Collection[str]] | None = None,
                  gone: dict[str, _Gone] | None = None) -> list[str]:
    problems: list[str] = []
    gone = {} if gone is None else gone
    writers = adam_writers(catalog)
    for dataset, meta in house.adam.items():
        writing = writers.get(dataset, [])
        present = [e for e in writing if any(key[0] == e for key in fragments)]
        if not present:
            continue  # no decision of this dataset applies to the study
        optional = set(meta.get("optional") or [])
        missing = [e for e in writing if e not in present and e not in optional]
        if missing and not pending:
            problems.append(f"{dataset}: no value for {', '.join(missing)}")
            continue
        parent = house.read(meta["parent"])
        defined = {column["name"] for column in parent.get("columns") or []}
        owners: dict[str, str] = {}
        includes = []
        bodies = []
        name = dataset.lower()
        for entry_id in present:
            unit = catalog.entry(entry_id).units[0]
            body = fragments[(entry_id, unit)]["adam"].get(dataset)
            if not body:
                continue  # this alternative writes nothing into this dataset
            unknown = sorted(set(body) - set(FRAGMENT_PARTS))
            if unknown:
                problems.append(f"{entry_id}: a fragment may not write {unknown}")
                continue
            for part, key in (("columns", "name"), ("intermediates", "id")):
                for member in body.get(part) or []:
                    label = f"{part}.{member.get(key)}"
                    if label in owners or (part == "columns" and member.get(key) in defined):
                        other = owners.get(label, "the house parent spec")
                        problems.append(f"{dataset}: {entry_id} and {other} both write {label}")
                    owners[label] = entry_id
            relative = f"adam/fragments/{name}/{entry_id}.yaml"
            result.files[relative] = canonical_yaml(
                {"yamaa": YAMAA_VERSION, "type": "spec", **body}
            )
            includes.append(f"fragments/{name}/{entry_id}.yaml")
            bodies.append(body)
            result.binds.setdefault((entry_id, unit), []).extend(
                f"adam:{dataset}.{column['name']}" for column in body.get("columns") or []
            )
        written = defined | {label.split(".", 1)[1] for label in owners
                             if label.startswith("columns.")}
        inputs = {}
        for input_name, stem in (meta.get("inputs") or {}).items():
            folder = adam_dir if input_name in house.adam else sdtm_dir
            inputs[input_name] = _join(folder, f"{stem}.{data_format}")
        columns = [column for column in meta.get("columns") or [] if column in written]
        # Pending decisions and variables the SDTM lacks: what cannot be built is left
        # out of the output. Without either, nothing is looked at. An optional decision
        # that the study leaves out writes nothing, as in the default mode; in the
        # pending mode what reads its columns waits for it.
        left_optional = ([e for e in writing if e not in present and e in optional]
                         if pending else [])
        waiting: dict[str, Key] = {}  # a column or a lookup a pending decision would write
        adds_records: set[Key] = set()  # pending decisions with a row template here
        for entry_id in [*missing, *left_optional]:
            key = (entry_id, catalog.entry(entry_id).units[0])
            parts = _parts_written(catalog, entry_id, dataset)
            for member in sorted(parts["columns"] | parts["intermediates"]):
                waiting[member] = key
            if parts["rows"] and entry_id in missing:
                adds_records.add(key)
        upstream = any(element.startswith(f"adam:{alias}.") for alias in meta.get("inputs") or {}
                       for element in gone)
        if waiting or sdtm is not None or upstream:
            lost = _left_out(meta, house, _composed(parent, bodies, columns), columns,
                             waiting, sdtm, gone, result.adam_columns)
            for column, key in waiting.items():
                if column in (meta.get("columns") or []) and column not in written:
                    if key[0] in missing:
                        lost[column] = _Gone({key})
                    else:  # optional: not written, and named only where something reads it
                        gone[f"adam:{dataset}.{column}"] = _Gone({key})
            needed = [c for c in [*(parent.get("keys") or []),
                                  *((parent.get("output") or {}).get("order_by") or [])]
                      if c in lost]
            required = sorted({variable for why in lost.values() for variable in why.absent
                               if _sdtmig_core(*variable.split(".", 1)) == "Req"})
            for variable in required:
                readers = sorted(c for c, why in lost.items() if variable in why.absent)
                domain, name_of = variable.split(".", 1)
                problems.append(f"{dataset}: the SDTM {domain} has no {name_of}, which "
                                f"{SDTMIG} requires (Required); {dataset} needs it for "
                                f"{', '.join(readers)}")
            if required:
                continue
            if needed or adds_records:
                # The records themselves cannot be built: the dataset is left out as a
                # whole, and what reads it with it. It waits for a decision, or it is
                # left out with a warning when the SDTM lacks what its records rest on.
                why = _Gone(set(adds_records))
                for column in needed:
                    why.add(lost[column])
                for column in meta.get("columns") or []:
                    gone[f"adam:{dataset}.{column}"] = why
                for key in why.keys:
                    result.pending.setdefault(key, []).append(f"adam:{dataset}")
                if why.absent:
                    said = _why(why)
                    result.left_out[f"adam:{dataset}"] = said
                    result.warnings.append(f"{dataset} is left out: its records cannot be "
                                           f"built: {said}")
                for path in [p for p in result.files if p.startswith(f"adam/fragments/{name}/")]:
                    del result.files[path]
                for key in list(result.binds):
                    result.binds[key] = [b for b in result.binds[key]
                                         if not b.startswith(f"adam:{dataset}.")]
                    if not result.binds[key]:
                        del result.binds[key]
                continue
            for column in sorted(lost, key=lambda c: (meta.get("columns") or []).index(c)):
                why = lost[column]
                element = f"adam:{dataset}.{column}"
                gone[element] = why
                for key in why.keys:
                    result.pending.setdefault(key, []).append(element)
                if why.absent:
                    said = "; ".join(absent_reason(variable) for variable in sorted(why.absent))
                    result.left_out[element] = said
                    result.warnings.append(f"{dataset}.{column} is left out: {said}")
            columns = [column for column in columns if column not in lost]
        entry_spec = {
            "yamaa": YAMAA_VERSION,
            "type": "spec",
            "parent": _join(house_ref, meta["parent"]),
            "include": includes,
            "input": inputs,
            "output": {"path": _join(adam_dir, f"{meta['output']}.{data_format}"),
                       "columns": columns},
        }
        result.files[f"adam/{name}.yaml"] = canonical_yaml(entry_spec)
        result.datasets.append(dataset)
        result.adam_columns[dataset] = columns
    for key in result.binds:
        result.binds[key] = sorted(set(result.binds[key]))
    return problems


def _join(folder: str, name: str) -> str:
    return name if folder in ("", ".") else f"{folder.rstrip('/')}/{name}"


def relative_reference(target: Path, start: Path) -> str:
    """`target` as a POSIX path relative to the folder `start`."""
    return Path(os.path.relpath(target, start)).as_posix()


# -- tables ------------------------------------------------------------------


def parameters_of(catalog: Catalog, fragments: dict) -> tuple[dict, dict, dict, list[str]]:
    """Shared parameters, parameters by family, who set each, and conflicts."""
    problems: list[str] = []
    shared: dict[str, object] = {}
    by_family: dict[str, dict[str, object]] = {}
    setter: dict[tuple[str, str], tuple[str, str]] = {}  # (scope, name) -> decision key
    for key in catalog.keys():
        if key not in fragments:
            continue
        unit = catalog.units.get(key[1])
        scope = key[1] if unit is not None and unit.kind == "table_family" else ""
        target = by_family.setdefault(scope, {}) if scope else shared
        for name, value in fragments[key]["params"].items():
            other = setter.get((scope, name)) or setter.get(("", name))
            if other is None and not scope:
                other = next((k for (s, n), k in setter.items() if n == name), None)
            if other is not None:
                problems.append(f"{key[0]} and {other[0]} both set the parameter '{name}'")
                continue
            target[name] = value
            setter[(scope, name)] = key
    return shared, by_family, setter, problems


def family_templates(house: House, unit: str) -> tuple[dict, dict]:
    """The ARS and the layout template of a table family."""
    ars = house.read(house.ars["families"][unit])
    layout = house.read(house.layout["families"][unit])
    if not isinstance(ars, dict) or not isinstance(layout, dict):
        raise CompileError([f"the templates of {unit} are not mappings"])
    return ars, layout


def other_values(catalog: Catalog, entry_id: str, value: dict) -> list[dict]:
    """The other values of an entry that a bind is proven against.

    Every alternative with every example of its slots; and, for the value
    itself, each list or table with one item left out. A list that names
    rows, visits or windows binds the elements of each item only when the
    item can go: the examples alone may all hold it.
    """
    values: list[dict] = []

    def add(other: dict) -> None:
        if other != value and other not in values:
            values.append(other)

    entry = catalog.entry(entry_id)
    for alternative in entry.alternatives:
        rows = max([len(slot.examples) for slot in alternative.slots] or [1])
        for row in range(rows):
            other = {"rule": alternative.id}
            for slot in alternative.slots:
                other[slot.name] = slot.examples[row % len(slot.examples)]
            add(other)
    try:
        current = entry.alternative(value["rule"])
    except KeyError:
        return values
    for slot in current.slots:
        items = value.get(slot.name)
        if isinstance(items, list) and len(items) > 1:
            for index in range(len(items)):
                shorter = {**value, slot.name: items[:index] + items[index + 1:]}
                try:
                    check_value(slot, shorter[slot.name])
                except SlotError:
                    continue
                add(shorter)
    return values


def bind_tables(catalog: Catalog, house: House, records: list[dict], compiled: Compiled,
                house_ref: str, **options: str) -> None:
    """Fill the binds of a compile for ARS elements and layout parts (the `decides` edge).

    A decision binds an element when changing the decision to another value
    of its entry changes the element or removes it, all other decisions
    kept. The other values are those of `other_values`: every alternative
    with its examples, and each list of the value with one item left out.
    This is the compile check of PLAN.md section 4.2: the edge is proven by
    mutation, not read off a template. It costs one compile per other value,
    and it is complete for these values only: a value that no example and
    no shorter list reaches is not tried.

    An ADaM bind is the column a fragment writes. It may be a working column
    (`adam:ADAE._TEEND`); the dataset variables it reaches follow from the
    `derives_from` edges of the resolved spec.
    """
    base_ars = {name: {e["id"]: e for e in (compiled.ars or {}).get(name, [])}
                for name in ARS_LISTS}
    for record in records:
        key = (record.get("id"), record.get("unit"))
        if record.get("value") is None or key[0] not in catalog.entries:
            continue
        ars: set[str] = set()
        layout: set[str] = set()
        for value in other_values(catalog, key[0], record["value"]):
            changed = [{**r, "value": value} if (r.get("id"), r.get("unit")) == key else r
                       for r in records]
            try:
                other = compile_decisions(catalog, house, changed, house_ref, **options)
            except CompileError:
                continue  # this value does not fit the other decisions of the study
            for name in ARS_LISTS:
                theirs = {e["id"]: e for e in (other.ars or {}).get(name, [])}
                ars |= {f"ars:{element_id}" for element_id, element in base_ars[name].items()
                        if theirs.get(element_id) != element}
            for unit, parts in compiled.layouts.items():
                layout |= {f"layout:{unit}/{part}" for part, body in parts.items()
                           if other.layouts.get(unit, {}).get(part, _DROPPED) != body}
        adam = [bind for bind in compiled.binds.get(key, []) if bind.startswith("adam:")]
        if adam or ars:
            compiled.binds[key] = sorted(set(adam) | ars)
        if layout:
            compiled.layout_binds[key] = sorted(layout)


_DROPPED = object()


def _with_reads(node: object, scope: dict, where: str, problems: list[str],
                undefined: set[str] | None = None) -> tuple[object, set]:
    reads: set[str] = set()
    try:
        return evaluate(node, scope, reads), reads
    except TemplateError as error:
        problems.append(f"{where}: {error}")
        if undefined is not None and isinstance(error, UndefinedName):
            undefined.add(error.name)
        return None, reads


def _parameters(catalog: Catalog, key: Key) -> set[str]:
    """The table parameters that some alternative of a decision sets."""
    names: set[str] = set()
    for alternative in compile_template(catalog, key[0]).values():
        names |= set((alternative or {}).get("params") or {})
    return names


def _output_id(layout_template: dict, scope: dict, unit: str) -> str:
    """The output ID of a family, from its layout template; the unit when the ID
    cannot be evaluated."""
    try:
        found = evaluate((layout_template.get("output") or {}).get("id"), scope)
    except TemplateError:
        return unit
    return str(found) if isinstance(found, str) and found else unit


def _strings(node: object) -> set[str]:
    if isinstance(node, str):
        return {node}
    if isinstance(node, dict):
        return set().union(*(_strings(child) for child in node.values())) if node else set()
    if isinstance(node, list):
        return set().union(*(_strings(child) for child in node)) if node else set()
    return set()


def analysis_reads(analysis: dict, find) -> set[tuple[str, str]]:
    """The (dataset, variable) pairs one analysis reads: its variable, its analysis set,
    its data subset and its groupings. `find(list, id)` gives an element of the ARS."""
    reads: set[tuple[str, str]] = set()
    if analysis.get("dataset") and analysis.get("variable"):
        reads.add((analysis["dataset"], analysis["variable"]))
    nodes = [find("analysisSets", analysis.get("analysisSetId")),
             find("dataSubsets", analysis.get("dataSubsetId"))]
    for ordered in analysis.get("orderedGroupings") or []:
        grouping = find("analysisGroupings", ordered.get("groupingId"))
        if grouping and grouping.get("groupingDataset") and grouping.get("groupingVariable"):
            reads.add((grouping["groupingDataset"], grouping["groupingVariable"]))
        nodes.append(grouping)
    for condition in _conditions([node for node in nodes if node]):
        if condition.get("dataset") and condition.get("variable"):
            reads.add((condition["dataset"], condition["variable"]))
    return reads


def _compile_tables(catalog: Catalog, house: House, fragments: dict, result: Compiled,
                    pending: bool = False, gone: dict[str, _Gone] | None = None) -> list[str]:
    gone = gone or {}
    shared, by_family, _, problems = parameters_of(catalog, fragments)
    missing = [key for key in catalog.keys() if key not in fragments] if pending else []
    families = [unit for unit, known in catalog.units.items()
                if known.kind == "table_family" and unit in (house.ars.get("families") or {})]
    for unit in families:
        if "included" not in by_family.get(unit, {}):
            key = ("tfl.output.include", unit)
            if key in missing:
                # Whether the output is planned waits for the decision itself.
                _, layout_template = family_templates(house, unit)
                scope = {**shared, **by_family.get(unit, {})}
                result.pending.setdefault(key, []).append(
                    f"output:{_output_id(layout_template, scope, unit)}")
                continue
            problems.append(f"{unit}: no value for tfl.output.include")
    included = [unit for unit in families if by_family.get(unit, {}).get("included") is True]
    if not included or problems:
        return problems
    common = house.read(house.ars["common"])
    doc, _ = _with_reads(common["reporting_event"], shared, "ars/common", problems)
    if not isinstance(doc, dict):
        return problems
    for name in ARS_LISTS:
        doc.setdefault(name, [])
    items = doc["mainListOfContents"]["contentsList"]["listItems"]
    for unit in included:
        scope = {**shared, **by_family.get(unit, {})}
        ars_template, layout_template = family_templates(house, unit)
        # The family is evaluated first and put into the document afterwards, so that a
        # family that waits for a decision, or cannot be built, leaves no element.
        local: list[str] = []
        undefined: set[str] = set()
        for name, expression in (ars_template.get("define") or {}).items():
            scope[name], _ = _with_reads(expression, scope, f"{unit}: define {name}", local,
                                         undefined)
        elements: dict[str, list[dict]] = {name: [] for name in ARS_LISTS}
        for name in ARS_LISTS:
            for index, member in enumerate(ars_template.get(name) or []):
                # A member may stand for no element (a false $if) or for several ($for).
                value, _ = _with_reads([member], scope, f"{unit}: ars {name}[{index}]", local,
                                       undefined)
                elements[name] += [element for element in value or []
                                   if isinstance(element, dict)]
        item, _ = _with_reads(ars_template.get("listItem"), scope, f"{unit}: listItem", local,
                              undefined)
        layout: dict = {}
        for part, template in layout_template.items():
            layout[part], _ = _with_reads(template, scope, f"{unit}: layout {part}", local,
                                          undefined)
        output = _output_id(layout_template, scope, unit)
        if local:
            # A parameter that only a decision without a value could set: the output waits.
            waiting = [key for key in missing if _parameters(catalog, key) & undefined
                       and (key[1] == unit or catalog.units[key[1]].kind != "table_family")]
            if not waiting:
                problems += local
                continue
            for key in waiting:
                result.pending.setdefault(key, []).append(f"output:{output}")
            continue
        if gone:
            skip = _without_what_is_gone(unit, output, elements, layout, doc, gone, result)
            if skip:
                continue
        family_analyses: list[dict] = []
        for name in ARS_LISTS:
            for element in elements[name]:
                known = next((e for e in doc[name] if e.get("id") == element.get("id")), None)
                if known is None:
                    doc[name].append(element)
                elif known != element:
                    problems.append(
                        f"{unit}: ars {name} '{element.get('id')}' is defined twice"
                    )
                if name == "analyses":
                    family_analyses.append(element)
        if isinstance(item, dict):
            item["order"] = len(items) + 1
            item["sublist"] = {"listItems": [
                {"name": analysis["name"], "level": 2, "order": number,
                 "analysisId": analysis["id"]}
                for number, analysis in enumerate(family_analyses, start=1)
            ]}
            items.append(item)
        result.layouts[unit] = layout
        result.families.append(unit)
        result.files[f"layout/{unit}.json"] = canonical_json(layout)
    if problems or not result.families:
        return problems  # nothing to write when every included output waits
    prune_ars(doc)
    result.ars = doc
    result.files["ars/reporting-event.json"] = canonical_json(doc)
    return problems


def _without_what_is_gone(unit: str, output: str, elements: dict[str, list[dict]], layout: dict,
                          doc: dict, gone: dict[str, _Gone], result: Compiled) -> bool:
    """Take out of one family the analyses that read an ADaM column left out, and their
    layout rows. Returns True when the family as a whole is left out: it reads a column
    that the SDTM cannot give (not produced), or what remains of it would have no
    header count or no row (it waits)."""
    def find(name: str, element_id: object) -> dict | None:
        for pool in (elements[name], doc[name]):
            found = next((e for e in pool if e.get("id") == element_id), None)
            if found is not None:
                return found
        return None

    dropped: dict[str, set] = {}
    for analysis in elements["analyses"]:
        for dataset, variable in sorted(analysis_reads(analysis, find)):
            why = gone.get(f"adam:{dataset}.{variable}")
            if why is None:
                continue
            if why.absent:
                said = (f"{output} is not produced: its analysis {analysis['id']} reads "
                        f"{dataset}.{variable}, which is left out: {_why(why)}")
                result.left_out[f"output:{output}"] = said
                result.warnings.append(said)
                return True
            dropped.setdefault(analysis["id"], set()).update(why.keys)
            for key in why.keys:  # the column it waits for, named where it is read
                result.pending.setdefault(key, []).append(f"adam:{dataset}.{variable}")
    grown = bool(dropped)
    while grown:
        grown = False
        for analysis in elements["analyses"]:
            for reference in analysis.get("referencedAnalysisOperations") or []:
                other = reference.get("analysisId")
                if other in dropped and other != analysis["id"]:
                    keys = dropped.setdefault(analysis["id"], set())
                    if not dropped[other] <= keys:
                        keys |= dropped[other]
                        grown = True
    if not dropped:
        return False
    rows = [row for row in layout.get("rows") or [] if not _strings(row) & set(dropped)]
    if _strings(layout.get("columns")) & set(dropped) or not rows:
        for key in set().union(*dropped.values()):
            result.pending.setdefault(key, []).append(f"output:{output}")
        return True
    layout["rows"] = rows
    elements["analyses"] = [a for a in elements["analyses"] if a["id"] not in dropped]
    for analysis_id, keys in dropped.items():
        for key in keys:
            result.pending.setdefault(key, []).append(f"ars:{analysis_id}")
    return False


def ars_references(doc: dict) -> dict[str, set[str]]:
    """The IDs that the analyses of an ARS document refer to, by list."""
    used: dict[str, set[str]] = {name: set() for name in ARS_LISTS}
    for analysis in doc.get("analyses", []):
        if analysis.get("analysisSetId"):
            used["analysisSets"].add(analysis["analysisSetId"])
        if analysis.get("dataSubsetId"):
            used["dataSubsets"].add(analysis["dataSubsetId"])
        if analysis.get("methodId"):
            used["methods"].add(analysis["methodId"])
        for grouping in analysis.get("orderedGroupings") or []:
            used["analysisGroupings"].add(grouping.get("groupingId"))
    return used


def prune_ars(doc: dict) -> None:
    """Drop the analysis sets, groupings, data subsets and methods no analysis uses (P3).

    A method stays when an operation of a method in use names one of its
    operations (the denominator of a percentage).
    """
    used = ars_references(doc)
    operations = {
        relationship.get("operationId")
        for method in doc["methods"] if method.get("id") in used["methods"]
        for operation in method.get("operations") or []
        for relationship in operation.get("referencedOperationRelationships") or []
    }
    for method in doc["methods"]:
        if any(operation.get("id") in operations for operation in method.get("operations") or []):
            used["methods"].add(method.get("id"))
    for name in ("analysisSets", "analysisGroupings", "dataSubsets", "methods"):
        doc[name] = [element for element in doc[name] if element.get("id") in used[name]]


def _conditions(node: object) -> list[dict]:
    """Every where-clause condition below a node."""
    found: list[dict] = []
    if isinstance(node, dict):
        if isinstance(node.get("condition"), dict):
            found.append(node["condition"])
        for child in node.values():
            found += _conditions(child)
    elif isinstance(node, list):
        for child in node:
            found += _conditions(child)
    return found


def ars_reads(doc: dict) -> set[tuple[str, str]]:
    """The (dataset, variable) pairs an ARS document reads (the `reads` edge, section 4.2)."""
    reads: set[tuple[str, str]] = set()
    for analysis in doc.get("analyses", []):
        if analysis.get("dataset") and analysis.get("variable"):
            reads.add((analysis["dataset"], analysis["variable"]))
    for grouping in doc.get("analysisGroupings", []):
        if grouping.get("groupingDataset") and grouping.get("groupingVariable"):
            reads.add((grouping["groupingDataset"], grouping["groupingVariable"]))
    for name in ("analysisSets", "analysisGroupings", "dataSubsets"):
        for condition in _conditions(doc.get(name, [])):
            if condition.get("dataset") and condition.get("variable"):
                reads.add((condition["dataset"], condition["variable"]))
    return reads


def unread_variables(result: Compiled) -> list[str]:
    """The variables the ARS file reads that the compiled ADaM specs do not write."""
    problems = []
    for dataset, variable in sorted(ars_reads(result.ars or {})):
        if dataset not in result.adam_columns:
            problems.append(f"the tables read {dataset}.{variable}, but {dataset} is not compiled")
        elif variable not in result.adam_columns[dataset]:
            problems.append(
                f"the tables read {dataset}.{variable}, which no decision of the study writes"
            )
    return problems
