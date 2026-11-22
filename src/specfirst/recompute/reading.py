"""The generator's own reading of an ARS reporting event (ADR-021, decision 4).

It reads the ARS JSON, the kit's binding and the method registry as plain
data, and implements what standard/methods/README.md states for them: the
binding of an ARS operation (rules B1 to B3), the order of the options, the
where clauses (rules I3 to I5) and the groupings (rules I8 to I10). It shares
no code with `specfirst.machine.ars` or `ard`: an error there is not repeated
in the scripts.
"""

from __future__ import annotations

from dataclasses import dataclass, field

REGISTRY_CONTEXT = "specfirst method registry"
REGISTRY_PREFIX = "Method registry: "


class NotCovered(Exception):
    """The generator writes no script for this analysis; the message says why."""


@dataclass(frozen=True)
class Condition:
    dataset: str
    variable: str
    comparator: str
    values: tuple[str, ...]


@dataclass(frozen=True)
class Where:
    """A where clause: one condition, or AND, OR or NOT over where clauses (rule I5)."""

    condition: Condition | None = None
    operator: str | None = None
    parts: tuple[Where, ...] = ()

    def conditions(self) -> list[Condition]:
        if self.condition is not None:
            return [self.condition]
        return [c for part in self.parts for c in part.conditions()]


@dataclass(frozen=True)
class Group:
    id: str
    name: str
    where: Where


@dataclass(frozen=True)
class Grouping:
    id: str
    name: str
    dataset: str
    variable: str
    data_driven: bool
    groups: tuple[Group, ...]
    by_group: bool  # resultsByGroup of the analysis that uses it


@dataclass(frozen=True)
class Operation:
    """An ARS operation bound to a registry operation."""

    id: str
    name: str
    method: str  # registry entry
    operation: str  # registry operation
    result: str  # integer, number or text
    numerator: str | None = None  # for a percent: the ARS operation of the numerator
    denominator: tuple[str, str] | None = None  # (analysis ID, ARS operation ID)


@dataclass
class Analysis:
    id: str
    name: str
    event: str
    dataset: str
    variable: str
    set_id: str
    set_name: str
    set_where: Where
    subset_id: str | None
    subset_name: str
    subset_where: Where | None
    groupings: list[Grouping]
    method_id: str  # the ARS method
    operations: list[Operation]
    options: dict[str, dict[str, object]]  # registry method -> option -> value
    option_sources: dict[str, dict[str, str]]  # registry method -> option -> where from
    numbers: set[float] = field(default_factory=set)  # every number the ARS states for it

    @property
    def methods(self) -> list[str]:
        return sorted({op.method for op in self.operations})


def where_of(clause: dict, where: str) -> Where:
    """A where clause of the ARS model: `condition` or `compoundExpression`."""
    condition = clause.get("condition")
    if condition:
        values = condition.get("value") or []
        if not isinstance(values, list):
            values = [values]
        return Where(condition=Condition(str(condition["dataset"]), str(condition["variable"]),
                                         str(condition["comparator"]),
                                         tuple(str(v) for v in values)))
    compound = clause.get("compoundExpression")
    if compound:
        parts = sorted(compound.get("whereClauses") or [], key=lambda c: c.get("order", 0))
        return Where(operator=str(compound["logicalOperator"]),
                     parts=tuple(where_of(part, where) for part in parts))
    raise NotCovered(f"{where}: a where clause with neither a condition nor a compound expression")


def json_number(text: str) -> float | None:
    """A number written as in JSON (rule I3), or None."""
    import re

    if re.fullmatch(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?", text):
        return float(text)
    return None


def _by_id(items: list[dict] | None) -> dict[str, dict]:
    return {str(item["id"]): item for item in items or []}


class Event:
    """One reporting event, read for the generator."""

    def __init__(self, data: dict, event_id: str, registry: dict, binding: dict):
        self.data = data
        self.id = event_id
        self.registry = registry  # registry.json "methods"
        self.binding = binding or {}
        self.sets = _by_id(data.get("analysisSets"))
        self.subsets = _by_id(data.get("dataSubsets"))
        self.groupings = _by_id(data.get("analysisGroupings"))
        self.methods = _by_id(data.get("methods"))
        self.analyses = _by_id(data.get("analyses"))

    # -- binding (rules B1 to B3) -------------------------------------------------
    def _bind(self, method: dict, op: dict) -> tuple[str, str]:
        given = (self.binding.get("operations") or {}).get(op["id"])
        if given:  # B1
            return str(given["method"]), str(given["operation"])
        description = str(method.get("description") or "")
        name = str(op.get("name") or "")
        if description.startswith(REGISTRY_PREFIX):  # B2
            entry_id = description[len(REGISTRY_PREFIX):].strip()
            entry = self.registry.get(entry_id)
            if entry is None:
                raise NotCovered(f"method {method['id']} names '{entry_id}', not in the registry")
            found = [k for k, v in entry["operations"].items() if name in v["ars_names"]]
            if len(found) != 1:
                raise NotCovered(f"operation {op['id']} ('{name}') is not one operation of "
                                 f"{entry_id}")
            return entry_id, found[0]
        found = [(mid, k) for mid, m in self.registry.items() if m["kind"] == "descriptive"
                 for k, v in m["operations"].items() if name in v["ars_names"]]  # B3
        if len(found) != 1:
            raise NotCovered(f"operation {op['id']} ('{name}') is bound by no rule B1 to B3")
        return found[0]

    def _options(self, analysis: dict, methods: list[str]
                 ) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, str]]]:
        """Registry defaults, then the kit's binding, then programmingCode (README)."""
        options: dict[str, dict[str, object]] = {}
        sources: dict[str, dict[str, str]] = {}
        code = analysis.get("programmingCode") or {}
        stated = {}
        if code.get("context") == REGISTRY_CONTEXT:
            stated = {str(p["name"]): [str(v) for v in p.get("value") or []]
                      for p in code.get("parameters") or []}
        given = self.binding.get("options") or {}
        for mid in methods:
            entry = self.registry[mid]
            options[mid], sources[mid] = {}, {}
            for name, spec in sorted(entry["options"].items()):
                value, source = spec.get("default"), "the registry's default"
                if name in (given.get(mid) or {}):
                    value, source = given[mid][name], "kit.yaml's binding"
                if name in stated:
                    texts = stated[name]
                    if spec.get("takes") == "columns":
                        value = texts
                    elif spec.get("takes") == "group":
                        value = texts[0] if texts else None
                    else:
                        matched = [v for v in spec["values"] if str(v) == (texts or [""])[0]]
                        if len(texts) != 1 or not matched:
                            raise NotCovered(f"{analysis['id']}: option {name} = {texts} is not "
                                             f"a value of {mid}")
                        value = matched[0]
                    source = "the analysis's programmingCode"
                options[mid][name], sources[mid][name] = value, source
        unknown = sorted(set(stated) - {n for mid in methods
                                        for n in self.registry[mid]["options"]})
        if unknown:
            raise NotCovered(f"{analysis['id']}: parameters {unknown} are no option of {methods}")
        return options, sources

    # -- analyses -------------------------------------------------------------------
    def grouping(self, ordered: dict) -> Grouping:
        g = self.groupings[str(ordered["groupingId"])]
        groups = tuple(Group(str(x["id"]), str(x.get("name") or x["id"]),
                             where_of(x, f"group {x['id']}"))
                       for x in sorted(g.get("groups") or [], key=lambda x: x.get("order", 0)))
        data_driven = bool(g.get("dataDriven"))
        if not data_driven and not groups:
            raise NotCovered(f"grouping {g['id']} has neither groups nor dataDriven")
        return Grouping(str(g["id"]), str(g.get("name") or g["id"]),
                        str(g.get("groupingDataset") or ""), str(g.get("groupingVariable") or ""),
                        data_driven, groups, bool(ordered.get("resultsByGroup")))

    def analysis(self, analysis_id: str) -> Analysis:
        a = self.analyses[analysis_id]
        method = self.methods[str(a.get("methodId") or a.get("method", {}).get("id"))]
        aset = self.sets[str(a["analysisSetId"])]
        subset = self.subsets.get(str(a.get("dataSubsetId") or "")) if a.get("dataSubsetId") \
            else None
        groupings = [self.grouping(o) for o in sorted(a.get("orderedGroupings") or [],
                                                      key=lambda o: o.get("order", 0))]
        refs = {str(r["referencedOperationRelationshipId"]): str(r["analysisId"])
                for r in a.get("referencedAnalysisOperations") or []}
        operations = []
        for op in sorted(method.get("operations") or [], key=lambda o: o.get("order", 0)):
            mid, oid = self._bind(method, op)
            result = self.registry[mid]["operations"][oid]["result"]
            numerator = denominator = None
            for rel in op.get("referencedOperationRelationships") or []:
                role = (rel.get("referencedOperationRole") or {}).get("controlledTerm")
                target = refs.get(str(rel["id"]), str(rel.get("analysisId") or a["id"]))
                if role == "NUMERATOR":
                    if target != a["id"]:
                        raise NotCovered(f"{a['id']}: a numerator in another analysis")
                    numerator = str(rel["operationId"])
                elif role == "DENOMINATOR":
                    denominator = (target, str(rel["operationId"]))
            operations.append(Operation(str(op["id"]), str(op.get("name") or ""), mid, oid,
                                        result, numerator, denominator))
        methods = sorted({op.method for op in operations})
        options, sources = self._options(a, methods)
        made = Analysis(
            id=analysis_id, name=str(a.get("name") or ""), event=self.id,
            dataset=str(a["dataset"]), variable=str(a["variable"]),
            set_id=str(aset["id"]), set_name=str(aset.get("name") or ""),
            set_where=where_of(aset, f"analysis set {aset['id']}"),
            subset_id=str(subset["id"]) if subset else None,
            subset_name=str(subset.get("name") or "") if subset else "",
            subset_where=where_of(subset, f"data subset {subset['id']}") if subset else None,
            groupings=groupings, method_id=str(method["id"]), operations=operations,
            options=options, option_sources=sources)
        made.numbers = self.numbers_of(made)
        return made

    def numbers_of(self, analysis: Analysis) -> set[float]:
        """Every number the ARS states for the analysis: in its where clauses, its groups
        and those of the analyses it references, and its options (the static check)."""
        found: set[float] = set()
        wheres = [analysis.set_where, analysis.subset_where]
        wheres += [g.where for grouping in analysis.groupings for g in grouping.groups]
        for op in analysis.operations:
            if op.denominator and op.denominator[0] != analysis.id:
                other = self.analysis(op.denominator[0])
                wheres += [other.set_where, other.subset_where]
                wheres += [g.where for grouping in other.groupings for g in grouping.groups]
        for where in wheres:
            for condition in (where.conditions() if where else []):
                found |= {n for n in map(json_number, condition.values) if n is not None}
        for options in analysis.options.values():
            for value in options.values():
                for item in value if isinstance(value, list) else [value]:
                    if isinstance(item, bool):
                        continue
                    if isinstance(item, int | float):
                        found.add(float(item))
        return found


def first_sentence(text: str) -> str:
    """The decision sentence: the statement up to its first full stop and blank."""
    text = " ".join(str(text).split())
    for i, char in enumerate(text):
        if char == "." and (i + 1 == len(text) or text[i + 1] == " ") and \
                not text[max(0, i - 3):i].endswith(("e.g", "i.e")):
            return text[:i + 1]
    return text


def decisions_binding(records: list[dict]) -> dict[str, list[dict]]:
    """Decision records by the ARS element they bind: `ars:<id>` -> records, in file order."""
    found: dict[str, list[dict]] = {}
    for record in records:
        for target in record.get("binds") or []:
            if str(target).startswith("ars:"):
                found.setdefault(str(target)[4:], []).append(record)
    return found
