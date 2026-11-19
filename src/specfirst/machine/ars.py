"""An ARS reporting event as the result engines read it (PLAN.md sections 4.1, 7.1, 7.3).

This module reads structure only, no data: the index of a reporting event,
its check against the JSON Schema generated from the ARS model, the ADaM
columns each analysis reads, and the binding of ARS operations to the
method registry.

Binding. ARS names an operation; the registry says how it is computed. Each
ARS operation of a method that an analysis uses is bound to one registry
operation, by the first of these that applies:

    B1  the binding the caller gives for the operation's ID (a kit gives one
        for an ARS file it did not write, such as the CDISC example);
    B2  the method's description is "Method registry: <id>": the operation
        of that entry that takes the ARS operation's name;
    B3  the one descriptive registry operation that takes the ARS
        operation's name ("Count of subjects", "Mean", ...).

An operation that none of them binds is an error: the engines never guess.
The options of a method are the registry's defaults, then what the caller
gives per registry method, then the parameters of the analysis itself
(`programmingCode` with the context "specfirst method registry").
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from specfirst.machine.registry import Registry, RegistryError

REGISTRY_CONTEXT = "specfirst method registry"
DESCRIPTION_PREFIX = "Method registry: "
# The parameters of `programmingCode` (context REGISTRY_CONTEXT) that name columns
# of the analysis dataset: the terms of a model (ADR-015). They are read like a
# variable: `reads` gives them the role "model".
MODEL_TERMS = ("factors", "covariates")
COMPARATORS = ("EQ", "NE", "IN", "NOTIN", "GT", "GE", "LT", "LE")
LOGICAL = ("AND", "OR", "NOT")
ROLES = ("NUMERATOR", "DENOMINATOR")


class ArsError(ValueError):
    """The reporting event cannot be used as it is."""


def read(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def schema_problems(event: object, schema: dict) -> list[str]:
    """Why a reporting event does not fit the JSON Schema generated from the ARS model."""
    from jsonschema.validators import validator_for

    validator = validator_for(schema)(schema)
    errors = sorted(validator.iter_errors(event), key=lambda e: [str(p) for p in e.path])
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in errors]


def clause_parts(clause: dict) -> tuple[str, object]:
    """A where clause, of a set, a subset or a group, taken apart.

    Returns ("condition", its condition), or its logical operator with the
    list of its where clauses. This is the one place that knows the shape.
    """
    if clause.get("condition"):
        return "condition", clause["condition"]
    expression = clause.get("compoundExpression") or {}
    return str(expression.get("logicalOperator")), list(expression.get("whereClauses") or [])


def conditions(clause: dict) -> Iterator[dict]:
    """Every condition of a where clause."""
    kind, content = clause_parts(clause)
    if kind == "condition":
        yield content
    else:
        for inner in content:
            yield from conditions(inner)


def and_parts(clause: dict) -> list[dict]:
    """The parts a where clause joins with AND at its top; the clause itself otherwise."""
    kind, content = clause_parts(clause)
    if kind == "AND":
        return [part for inner in content for part in and_parts(inner)]
    return [clause]


def _by_id(items: object, what: str, problems: list[str]) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for item in items if isinstance(items, list) else []:
        key = item.get("id") if isinstance(item, dict) else None
        if not isinstance(key, str) or not key:
            problems.append(f"{what} without an id")
        elif key in found:
            problems.append(f"{what} '{key}' is defined twice")
        else:
            found[key] = item
    return found


@dataclass
class Event:
    """A reporting event with its parts by ID. `problems` lists what does not hang together."""

    data: dict
    analyses: dict[str, dict] = field(default_factory=dict)
    methods: dict[str, dict] = field(default_factory=dict)
    operations: dict[str, tuple[str, dict]] = field(default_factory=dict)  # id -> (method, op)
    sets: dict[str, dict] = field(default_factory=dict)
    subsets: dict[str, dict] = field(default_factory=dict)
    groupings: dict[str, dict] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    def groupings_of(self, analysis: dict) -> list[dict]:
        """The ordered groupings of an analysis, by their order."""
        return sorted(analysis.get("orderedGroupings") or [], key=lambda g: g.get("order", 0))

    def used_methods(self) -> list[str]:
        return sorted({analysis["methodId"] for analysis in self.analyses.values()})


def index(data: object) -> Event:
    """Index a reporting event and check its references. Does not read data."""
    if not isinstance(data, dict):
        raise ArsError("a reporting event is a JSON object")
    event = Event(data)
    problems = event.problems
    event.analyses = _by_id(data.get("analyses"), "analysis", problems)
    event.methods = _by_id(data.get("methods"), "method", problems)
    event.sets = _by_id(data.get("analysisSets"), "analysis set", problems)
    event.subsets = _by_id(data.get("dataSubsets"), "data subset", problems)
    event.groupings = _by_id(data.get("analysisGroupings"), "grouping", problems)
    for method_id, method in event.methods.items():
        for operation_id, operation in _by_id(
                method.get("operations"), f"operation of method '{method_id}'", problems).items():
            if operation_id in event.operations:
                problems.append(f"operation '{operation_id}' is defined in two methods")
            event.operations[operation_id] = (method_id, operation)
    for grouping_id, grouping in event.groupings.items():
        groups = _by_id(grouping.get("groups"), f"group of grouping '{grouping_id}'", problems)
        if grouping.get("dataDriven") and groups:
            problems.append(f"grouping '{grouping_id}' is data-driven and lists groups")
        if not grouping.get("dataDriven") and not groups:
            problems.append(f"grouping '{grouping_id}' is not data-driven and lists no group")
        if not grouping.get("groupingVariable") or not grouping.get("groupingDataset"):
            problems.append(f"grouping '{grouping_id}' names no dataset or no variable")
    clauses = [(f"analysis set '{k}'", v) for k, v in event.sets.items()]
    clauses += [(f"data subset '{k}'", v) for k, v in event.subsets.items()]
    clauses += [(f"group '{g['id']}'", g) for grouping in event.groupings.values()
                for g in grouping.get("groups") or [] if isinstance(g, dict) and g.get("id")]
    for where, clause in clauses:
        problems += [f"{where}: {problem}" for problem in clause_problems(clause)]
    for analysis_id, analysis in event.analyses.items():
        where = f"analysis '{analysis_id}'"
        if analysis.get("methodId") not in event.methods:
            problems.append(f"{where}: method '{analysis.get('methodId')}' is not defined")
        if not analysis.get("dataset") or not analysis.get("variable"):
            problems.append(f"{where}: names no dataset or no variable")
        for key, known in (("analysisSetId", event.sets), ("dataSubsetId", event.subsets)):
            if analysis.get(key) is not None and analysis[key] not in known:
                problems.append(f"{where}: {key} '{analysis[key]}' is not defined")
        orders = Counter()
        for entry in analysis.get("orderedGroupings") or []:
            orders[entry.get("order")] += 1
            if entry.get("groupingId") not in event.groupings:
                problems.append(f"{where}: grouping '{entry.get('groupingId')}' is not defined")
        problems += [f"{where}: two groupings have the order {order}"
                     for order, count in orders.items() if count > 1]
        for reference in analysis.get("referencedAnalysisOperations") or []:
            if reference.get("analysisId") not in event.analyses:
                problems.append(f"{where}: references analysis '{reference.get('analysisId')}', "
                                "which is not defined")
    return event


def clause_problems(clause: dict) -> list[str]:
    """Why a where clause cannot be evaluated."""
    condition, compound = clause.get("condition"), clause.get("compoundExpression")
    if bool(condition) == bool(compound):
        return ["needs a condition or a compound expression, and not both"]
    if condition:
        problems = []
        comparator, values = condition.get("comparator"), condition.get("value") or []
        if not condition.get("dataset") or not condition.get("variable"):
            problems.append("a condition names no dataset or no variable")
        if not all(isinstance(value, str) for value in values):
            problems.append("a condition has a value that is not text")
        if comparator not in COMPARATORS:
            problems.append(f"unknown comparator '{comparator}'")
        elif comparator in ("IN", "NOTIN") and not values:
            problems.append(f"{comparator} needs at least one value")
        elif comparator not in ("IN", "NOTIN") and len(values) != 1:
            problems.append(f"{comparator} needs exactly one value, found {len(values)}")
        return problems
    operator, inner = compound.get("logicalOperator"), compound.get("whereClauses") or []
    if operator not in LOGICAL:
        return [f"unknown logical operator '{operator}'"]
    if not inner or (operator == "NOT" and len(inner) != 1):
        return [f"{operator} has {len(inner)} where clauses"]
    return [problem for part in inner for problem in clause_problems(part)]


def reads(event: Event, analysis_id: str, subject_key: str) -> list[tuple[str, str, str]]:
    """What an analysis reads: sorted (role, dataset, variable).

    Roles: variable, set, subset, grouping, model (a factor or a covariate
    of a model-based method, ADR-015), and key for the subject key of every
    dataset that is read. These are the `reads` edges of PLAN.md section
    4.2, which real-3 puts into the graph.
    """
    analysis = event.analyses[analysis_id]
    found = {("variable", analysis["dataset"], analysis["variable"])}
    found |= {("model", analysis["dataset"], column) for column in model_terms(analysis)}
    for role, key, known in (("set", "analysisSetId", event.sets),
                             ("subset", "dataSubsetId", event.subsets)):
        if analysis.get(key):
            found |= {(role, c["dataset"], c["variable"]) for c in conditions(known[analysis[key]])}
    for entry in event.groupings_of(analysis):
        grouping = event.groupings[entry["groupingId"]]
        found.add(("grouping", grouping["groupingDataset"], grouping["groupingVariable"]))
        for group in grouping.get("groups") or []:
            found |= {("grouping", c["dataset"], c["variable"]) for c in conditions(group)}
    found |= {("key", dataset, subject_key) for _, dataset, _ in set(found)}
    return sorted(found)


def model_terms(analysis: dict) -> list[str]:
    """The columns an analysis names as the factors and covariates of its model."""
    code = analysis.get("programmingCode") or {}
    if code.get("context") != REGISTRY_CONTEXT:
        return []
    return sorted({str(value) for parameter in code.get("parameters") or []
                   if parameter.get("name") in MODEL_TERMS
                   for value in parameter.get("value") or []})


def columns(event: Event, subject_key: str) -> dict[str, list[str]]:
    """The columns of every dataset that the analyses of the event read."""
    wanted: dict[str, set[str]] = {}
    for analysis_id in event.analyses:
        for _, dataset, variable in reads(event, analysis_id, subject_key):
            wanted.setdefault(dataset, set()).add(variable)
    return {dataset: sorted(names) for dataset, names in sorted(wanted.items())}


@dataclass(frozen=True)
class Binding:
    """ARS operations bound to registry operations, and the options of every analysis."""

    operations: dict[str, tuple[str, str]]  # ARS operation ID -> (registry method, operation)
    options: dict[str, dict[str, dict]]  # analysis ID -> registry method -> resolved options

    def record(self) -> dict:
        return {
            "operations": {key: {"method": method, "operation": operation}
                           for key, (method, operation) in sorted(self.operations.items())},
            "options": {key: self.options[key] for key in sorted(self.options)},
        }


def _bind_operation(operation_id: str, method: dict, operation: dict, registry: Registry,
                    given: dict) -> tuple[str, str]:
    if operation_id in given:  # B1
        entry = given[operation_id]
        if not isinstance(entry, dict) or set(entry) != {"method", "operation"}:
            raise ArsError(f"binding of '{operation_id}': needs exactly 'method' and 'operation'")
        registry.operation(entry["method"], entry["operation"])
        return entry["method"], entry["operation"]
    name = str(operation.get("name", ""))
    description = str(method.get("description") or "")
    if description.startswith(DESCRIPTION_PREFIX):  # B2
        named = description[len(DESCRIPTION_PREFIX):].strip()
        if named in registry.methods:
            fits = [pair for pair in registry.by_ars_name(name) if pair[0] == named]
            if len(fits) != 1:
                raise ArsError(f"operation '{operation_id}': registry entry '{named}' has no "
                               f"operation that takes the name '{name}'")
            return fits[0]
    fits = [pair for pair in registry.by_ars_name(name)  # B3
            if registry.method(pair[0]).kind == "descriptive"]
    if len(fits) != 1:
        raise ArsError(f"operation '{operation_id}' ('{name}') of method '{method.get('id')}' is "
                       "not bound to the method registry")
    return fits[0]


def bind(event: Event, registry: Registry, given: dict | None = None) -> Binding:
    """Bind the operations of every method an analysis uses, and resolve the options."""
    given = given or {}
    unknown = sorted(set(given) - {"operations", "options"})
    if unknown:
        raise ArsError(f"binding: unknown key {', '.join(unknown)}")
    given_operations = given.get("operations") or {}
    given_options = given.get("options") or {}
    stray = sorted(set(given_operations) - set(event.operations))
    if stray:
        raise ArsError(f"binding: no such ARS operation: {', '.join(stray)}")
    try:
        operations = {
            operation_id: _bind_operation(operation_id, event.methods[method_id], operation,
                                          registry, given_operations)
            for operation_id, (method_id, operation) in sorted(event.operations.items())
            if method_id in event.used_methods()
        }
        for method_id in given_options:
            registry.options(method_id, given_options[method_id])
        options: dict[str, dict[str, dict]] = {}
        for analysis_id, analysis in event.analyses.items():
            used = sorted({operations[operation_id][0]
                           for operation_id, (method_id, _) in event.operations.items()
                           if method_id == analysis["methodId"]})
            own = _analysis_parameters(analysis_id, analysis, used, registry)
            options[analysis_id] = {
                method_id: registry.options(
                    method_id, {**(given_options.get(method_id) or {}), **own.get(method_id, {})})
                for method_id in used
            }
    except RegistryError as error:
        raise ArsError(f"binding: {error}") from error
    return Binding(operations, options)


def _analysis_parameters(analysis_id: str, analysis: dict, used: list[str],
                         registry: Registry) -> dict[str, dict]:
    """Options an analysis states itself, by registry method."""
    code = analysis.get("programmingCode") or {}
    if code.get("context") != REGISTRY_CONTEXT:
        return {}
    found: dict[str, dict] = {}
    for parameter in code.get("parameters") or []:
        name, values = parameter.get("name"), parameter.get("value") or []
        owners = [method_id for method_id in used if name in registry.method(method_id).options]
        option = registry.method(owners[0]).options[name] if len(owners) == 1 else {}
        if option.get("takes") == "columns":  # the terms of a model: any number of columns
            if name not in MODEL_TERMS:
                raise ArsError(f"analysis '{analysis_id}': parameter '{name}' names columns, "
                               f"and only {', '.join(MODEL_TERMS)} may (ADR-015)")
            found.setdefault(owners[0], {})[name] = [str(value) for value in values]
            continue
        if len(owners) != 1 or len(values) != 1:
            raise ArsError(f"analysis '{analysis_id}': parameter '{name}' must be one option of "
                           f"one of its methods ({', '.join(used)}), with one value")
        default = option["default"]
        value: object = values[0]
        if isinstance(default, bool):
            value = {"true": True, "false": False}.get(str(value).lower(), value)
        elif isinstance(default, int):
            value = int(value) if str(value).lstrip("-").isdigit() else value
        found.setdefault(owners[0], {})[name] = value
    return found


# ---- outputs and displays (real-3) ----------------------------------------------------


def outputs(event: Event) -> dict[str, dict]:
    """The outputs of a reporting event by ID."""
    found = event.data.get("outputs")
    if not isinstance(found, list):
        return {}
    return {item["id"]: item for item in found if isinstance(item, dict) and item.get("id")}


def display_sections(event: Event, output_id: str) -> dict[str, list[str]]:
    """The texts of the first display of an output, by section type, in their order.

    A subsection is written in the display, or names a subsection of the
    event's global display sections. A name that is not defined gives no text.
    """
    output = outputs(event).get(output_id) or {}
    shared = {sub.get("id"): sub.get("text")
              for section in event.data.get("globalDisplaySections") or []
              for sub in section.get("subSections") or []}
    displays = sorted(output.get("displays") or [], key=lambda item: item.get("order", 0))
    sections = (displays[0].get("display") or {}).get("displaySections") if displays else None
    found: dict[str, list[str]] = {}
    for section in sections or []:
        texts = found.setdefault(str(section.get("sectionType")), [])
        for entry in sorted(section.get("orderedSubSections") or [],
                            key=lambda item: item.get("order", 0)):
            text = (entry.get("subSection") or {}).get("text")
            if text is None:
                text = shared.get(entry.get("subSectionId"))
            if isinstance(text, str):
                texts.append(text)
    return found


def listed_analyses(event: Event, output_id: str) -> list[str]:
    """The analyses the main list of contents lists under an output, in its order."""
    def items(entry: dict) -> list[dict]:
        listed = (entry.get("sublist") or {}).get("listItems")
        return [item for item in listed if isinstance(item, dict)] \
            if isinstance(listed, list) else []

    def below(entry: dict) -> Iterator[str]:
        for inner in items(entry):
            if inner.get("analysisId"):
                yield inner["analysisId"]
            yield from below(inner)

    def find(entry: dict) -> Iterator[str]:
        for inner in items(entry):
            if inner.get("outputId") == output_id:
                yield from below(inner)
            else:
                yield from find(inner)

    contents = (event.data.get("mainListOfContents") or {}).get("contentsList") or {}
    return list(dict.fromkeys(find({"sublist": contents})))
