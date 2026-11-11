"""The compiler: decisions to yamaa, ARS and layout files (PLAN.md sections 5.2, 7.1).

For a catalog decision the fragment is a pure function of the decision
value. Each alternative of an entry has one fragment in the entry's compile
template (`standard/catalog/templates/<id>.yaml`):

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
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from specfirst.compile.catalog import Catalog
from specfirst.compile.house import House
from specfirst.compile.standard_form import StandardForm, StandardFormError
from specfirst.compile.template import TemplateError, evaluate

YAMAA_VERSION = "1.0"
ARS_LISTS = ("analysisSets", "analysisGroupings", "dataSubsets", "methods", "analyses", "outputs")
FRAGMENT_PARTS = ("intermediates", "columns", "rows")


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

    def manifest(self) -> dict:
        return {
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
) -> Compiled:
    """Compile decision records into yamaa specs, an ARS file and layout files.

    `house_ref` is the path of the house folder as the compiled ADaM specs
    name it, relative to their folder `adam/`. `sdtm_dir` and `adam_dir`
    are where those specs read SDTM and write ADaM, relative to `adam/` too.
    Raises CompileError with every problem found.
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
    problems += _compile_adam(catalog, house, fragments, result, house_ref, sdtm_dir,
                              adam_dir, data_format)
    problems += _compile_tables(catalog, house, fragments, result)
    if not problems and result.ars is not None:
        problems += unread_variables(result)
    if problems:
        raise CompileError(problems)
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


def _compile_adam(catalog: Catalog, house: House, fragments: dict, result: Compiled,
                  house_ref: str, sdtm_dir: str, adam_dir: str, data_format: str) -> list[str]:
    problems: list[str] = []
    writers = adam_writers(catalog)
    for dataset, meta in house.adam.items():
        writing = writers.get(dataset, [])
        present = [e for e in writing if any(key[0] == e for key in fragments)]
        if not present:
            continue  # no decision of this dataset applies to the study
        optional = set(meta.get("optional") or [])
        missing = [e for e in writing if e not in present and e not in optional]
        if missing:
            problems.append(f"{dataset}: no value for {', '.join(missing)}")
            continue
        parent = house.read(meta["parent"])
        defined = {column["name"] for column in parent.get("columns") or []}
        owners: dict[str, str] = {}
        includes = []
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
    """Every other value of an entry that its alternatives and their examples give."""
    values = []
    for alternative in catalog.entry(entry_id).alternatives:
        rows = max([len(slot.examples) for slot in alternative.slots] or [1])
        for row in range(rows):
            other = {"rule": alternative.id}
            for slot in alternative.slots:
                other[slot.name] = slot.examples[row % len(slot.examples)]
            if other != value and other not in values:
                values.append(other)
    return values


def bind_tables(catalog: Catalog, house: House, records: list[dict], compiled: Compiled,
                house_ref: str, **options: str) -> None:
    """Fill the binds of a compile for ARS elements and layout parts (the `decides` edge).

    A decision binds an element when changing the decision to another value
    of its entry (another alternative, or another example of a slot) changes
    the element or removes it, all other decisions kept. This is the compile
    check of PLAN.md section 4.2: the edge is proven by mutation, not read off
    a template. It costs one compile per other value.

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


def _with_reads(node: object, scope: dict, where: str, problems: list[str]) -> tuple[object, set]:
    reads: set[str] = set()
    try:
        return evaluate(node, scope, reads), reads
    except TemplateError as error:
        problems.append(f"{where}: {error}")
        return None, reads


def _compile_tables(catalog: Catalog, house: House, fragments: dict,
                    result: Compiled) -> list[str]:
    shared, by_family, _, problems = parameters_of(catalog, fragments)
    families = [unit for unit, known in catalog.units.items()
                if known.kind == "table_family" and unit in (house.ars.get("families") or {})]
    for unit in families:
        if "included" not in by_family.get(unit, {}):
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
        for name, expression in (ars_template.get("define") or {}).items():
            scope[name], _ = _with_reads(expression, scope, f"{unit}: define {name}", problems)
        family_analyses: list[dict] = []
        for name in ARS_LISTS:
            for index, member in enumerate(ars_template.get(name) or []):
                # A member may stand for no element (a false $if) or for several ($for).
                value, reads = _with_reads([member], scope, f"{unit}: ars {name}[{index}]",
                                           problems)
                for element in value or []:
                    if not isinstance(element, dict):
                        continue
                    known = next((e for e in doc[name] if e.get("id") == element.get("id")), None)
                    if known is None:
                        doc[name].append(element)
                    elif known != element:
                        problems.append(
                            f"{unit}: ars {name} '{element.get('id')}' is defined twice"
                        )
                    if name == "analyses":
                        family_analyses.append(element)
        item, _ = _with_reads(ars_template.get("listItem"), scope, f"{unit}: listItem", problems)
        if isinstance(item, dict):
            item["order"] = len(items) + 1
            item["sublist"] = {"listItems": [
                {"name": analysis["name"], "level": 2, "order": number,
                 "analysisId": analysis["id"]}
                for number, analysis in enumerate(family_analyses, start=1)
            ]}
            items.append(item)
        layout: dict = {}
        for part, template in layout_template.items():
            layout[part], _ = _with_reads(template, scope, f"{unit}: layout {part}", problems)
        result.layouts[unit] = layout
        result.families.append(unit)
        result.files[f"layout/{unit}.json"] = canonical_json(layout)
    if problems:
        return problems
    prune_ars(doc)
    result.ars = doc
    result.files["ars/reporting-event.json"] = canonical_json(doc)
    return problems


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
