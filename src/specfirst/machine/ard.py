"""The Python result engine: an ARS reporting event and ADaM data in, ARD rows out.

PLAN.md sections 7.1 and 7.2. One generic interpreter, no code per table.
How an analysis is read (records, groupings, cells, tables, the population
of an occurrence test) is written down as the numbered rules I1 to I19 in
standard/methods/README.md; the comments here name them. What an operation
computes is the method registry's business (specfirst.machine.methods).

The R engine in r/specfirstr/ follows the same rules and must give the same
rows (rule R11).

An ARD row (standard/schemas/ard.schema.json) names its analysis, its ARS
operation, per grouping the group it stands for, the registry method that
computed it and the hash of that method's options. `raw_value` holds the
number at full precision: nothing is rounded here.
"""

from __future__ import annotations

import itertools
import math
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

import numpy as np

from specfirst.machine import ars, methods
from specfirst.machine.registry import Registry

SUBJECT_KEY = "USUBJID"


class EngineError(ValueError):
    """The analyses cannot be run on these data."""


@dataclass
class Table:
    """The columns of one dataset that the analyses read.

    A text column is an object array with "" for a missing value; a number
    column is float64 with NaN for a missing value (rule I1).
    """

    name: str
    rows: int
    columns: dict[str, np.ndarray]
    kinds: dict[str, str]  # column -> "text" or "number"


# A number in a condition (rule I3): ARS writes every value as text, and a number
# is written as in JSON. Python's float() alone would also take "6_1", "nan" and
# " 61 ", and R's as.numeric "0x3D".
_NUMBER = re.compile(r"-?(?:0|[1-9][0-9]*)(?:[.][0-9]+)?(?:[eE][+-]?[0-9]+)?")


def _number_text(value: float) -> str:
    """A number as the text of a group value (standard/methods/README.md, rule I9).

    Zero is "0"; any other whole number has all its digits and neither a
    decimal point nor an exponent; any other number is the shortest decimal
    that reads back as the same number.
    """
    return str(int(value)) if value.is_integer() else repr(value)


def condition_numbers(wanted: list) -> list[float]:
    """The numbers a condition compares a number column with."""
    if not wanted or not all(isinstance(v, str) and _NUMBER.fullmatch(v) for v in wanted):
        raise EngineError(f"a number column is compared with {wanted!r}; a number is written "
                          "as in JSON")
    numbers = [float(value) for value in wanted]
    if not all(math.isfinite(number) for number in numbers):
        raise EngineError(f"a number column is compared with {wanted!r}, which is not a "
                          "finite number")
    return numbers


def table_from_arrow(name: str, table) -> Table:
    """Take over an Arrow table: numbers as float64, everything else as text."""
    import pyarrow as pa

    columns: dict[str, np.ndarray] = {}
    kinds: dict[str, str] = {}
    for field, column in zip(table.schema, table.columns, strict=True):
        kind = field.type
        if pa.types.is_dictionary(kind):
            column, kind = column.cast(kind.value_type), kind.value_type
        if pa.types.is_integer(kind) or pa.types.is_floating(kind) or pa.types.is_decimal(kind):
            values = column.cast(pa.float64()).to_numpy(zero_copy_only=False).astype(np.float64)
            columns[field.name], kinds[field.name] = values, "number"
            continue
        if pa.types.is_boolean(kind):
            items = [None if v is None else ("true" if v else "false") for v in column.to_pylist()]
        elif pa.types.is_string(kind) or pa.types.is_large_string(kind):
            items = column.to_pylist()
        else:  # dates and times: their ISO text, which sorts in time order
            items = [None if v is None else v.isoformat() for v in column.to_pylist()]
        values = np.empty(len(items), dtype=object)
        values[:] = ["" if v is None else v for v in items]
        columns[field.name], kinds[field.name] = values, "text"
    return Table(name, table.num_rows, columns, kinds)


def load_tables(folder: Path, wanted: dict[str, list[str]]) -> dict[str, Table]:
    """Read from <folder>/<dataset>.parquet the columns the analyses read."""
    import pyarrow.parquet as pq

    tables = {}
    for dataset, names in wanted.items():
        path = folder / f"{dataset.lower()}.parquet"
        if not path.is_file():
            raise EngineError(f"dataset {dataset}: no file {path.name} in {folder}")
        missing = sorted(set(names) - set(pq.read_schema(path).names))
        if missing:
            raise EngineError(f"dataset {dataset} has no column {', '.join(missing)}")
        tables[dataset] = table_from_arrow(dataset, pq.read_table(path, columns=names))
    return tables


def compare(values: np.ndarray, kind: str, comparator: str, wanted: list) -> np.ndarray:
    """One condition on one column (rule I3)."""
    if kind == "number":
        numbers = condition_numbers(wanted)
        with np.errstate(invalid="ignore"):
            if comparator == "EQ":
                return values == numbers[0]
            if comparator == "NE":
                return ~(values == numbers[0])
            if comparator == "IN":
                return np.isin(values, numbers)
            if comparator == "NOTIN":
                return ~np.isin(values, numbers)
            return {"GT": values > numbers[0], "GE": values >= numbers[0],
                    "LT": values < numbers[0], "LE": values <= numbers[0]}[comparator]
    texts = ["" if value is None else str(value) for value in wanted]
    if comparator == "EQ":
        return values == texts[0]
    if comparator == "NE":
        return values != texts[0]
    if comparator == "IN":
        return np.isin(values, texts)
    if comparator == "NOTIN":
        return ~np.isin(values, texts)
    result = np.zeros(len(values), dtype=bool)
    present = values != ""  # an ordered comparison with a missing value is false
    part = values[present]
    result[present] = {"GT": part > texts[0], "GE": part >= texts[0],
                       "LT": part < texts[0], "LE": part <= texts[0]}[comparator]
    return result


@dataclass(frozen=True)
class Result:
    analysis_id: str
    operation_id: str  # of the ARS method
    groups: tuple[tuple[int, str, str, str | None], ...]  # (n, grouping, id|value|all, key)
    method_id: str  # of the registry
    options_hash: str
    value: float | int | None

    def pairs(self) -> frozenset:
        """What identifies the cell: its groups, without the groupings that are compared."""
        return frozenset((grouping, kind, key) for _, grouping, kind, key in self.groups
                         if kind != "all")

    def row(self) -> dict:
        row: dict[str, object] = {"analysis_id": self.analysis_id,
                                  "operation_id": self.operation_id}
        parts = [quote(self.analysis_id, safe=""), quote(self.operation_id, safe="")]
        for n, grouping, kind, key in self.groups:
            row[f"group{n}_groupingId"] = grouping
            if kind == "id":
                row[f"group{n}_groupId"] = key
                parts.append(quote(key, safe=""))
            elif kind == "value":
                row[f"group{n}_groupValue"] = key
                parts.append("=" + quote(key, safe=""))
            else:
                parts.append("*")
        row["id"] = "ard:" + "/".join(parts)
        row["method_id"] = self.method_id
        row["method_options_hash"] = self.options_hash
        row["raw_value"] = self.value
        return row


class Engine:
    def __init__(self, event: ars.Event, registry: Registry, binding: ars.Binding,
                 tables: dict[str, Table], subject_key: str = SUBJECT_KEY):
        if event.problems:
            raise EngineError("the reporting event is not usable: " + "; ".join(event.problems))
        self.event, self.registry, self.binding = event, registry, binding
        self.tables, self.subject_key = tables, subject_key
        self._masks: dict[tuple[str, int], np.ndarray] = {}
        self._values: dict[tuple[str, str], np.ndarray] = {}
        self._texts: dict[tuple[str, str], np.ndarray] = {}
        self._results: dict[str, list[Result]] = {}
        self._running: list[str] = []
        self._populations: dict[str, tuple[str, np.ndarray]] = {}
        # The records of every cell of a continuous summary, for `cell_values`.
        self._cells: dict[tuple[str, tuple], np.ndarray] = {}
        self._by_row: dict[str, Result] | None = None

    # ---- columns ----------------------------------------------------------------

    def table(self, dataset: str) -> Table:
        if dataset not in self.tables:
            raise EngineError(f"dataset {dataset} was not handed to the engine")
        return self.tables[dataset]

    def column(self, dataset: str, name: str) -> tuple[np.ndarray, str]:
        table = self.table(dataset)
        if name not in table.columns:
            raise EngineError(f"dataset {dataset} has no column {name}")
        return table.columns[name], table.kinds[name]

    def text(self, dataset: str, name: str) -> np.ndarray:
        """A column as text; numbers are written as group values are."""
        if (dataset, name) not in self._texts:
            values, kind = self.column(dataset, name)
            if kind == "number":
                texts = np.empty(len(values), dtype=object)
                texts[:] = ["" if math.isnan(v) else _number_text(v) for v in values.tolist()]
                values = texts
            self._texts[(dataset, name)] = values
        return self._texts[(dataset, name)]

    def numbers(self, dataset: str, name: str) -> np.ndarray:
        values, kind = self.column(dataset, name)
        if kind != "number":
            raise EngineError(f"{dataset}.{name} holds text; this method needs numbers")
        return values

    # ---- where clauses (rules I3 to I5) --------------------------------------------

    def where(self, dataset: str, clause: dict) -> np.ndarray:
        """The records of `dataset` that fulfil a where clause."""
        key = (dataset, id(clause))
        if key not in self._masks:
            self._masks[key] = self._where(dataset, clause)
        return self._masks[key]

    def _where(self, dataset: str, clause: dict) -> np.ndarray:
        operator, content = ars.clause_parts(clause)
        if operator == "condition":
            source = content["dataset"]
            values, kind = self.column(source, content["variable"])
            mask = compare(values, kind, content["comparator"], content.get("value") or [])
            if source == dataset:
                return mask
            # Rule I4: it holds for at least one record of the same subject there.
            subjects = set(self.text(source, self.subject_key)[mask].tolist()) - {""}
            here = self.text(dataset, self.subject_key)
            return np.fromiter((key in subjects for key in here.tolist()), dtype=bool,
                               count=len(here))
        parts = [self.where(dataset, inner) for inner in content]
        if operator == "AND":
            return np.logical_and.reduce(parts)
        if operator == "OR":
            return np.logical_or.reduce(parts)
        return ~parts[0]

    # ---- groupings (rules I7 to I10) -----------------------------------------------

    def group_values(self, dataset: str, grouping: dict) -> np.ndarray:
        """The grouping variable as text on every record of `dataset` (rule I9)."""
        key = (dataset, grouping["id"])
        if key in self._values:
            return self._values[key]
        source, variable = grouping["groupingDataset"], grouping["groupingVariable"]
        if source == dataset:
            values = self.text(dataset, variable)
        else:
            lookup: dict[str, str] = {}
            for subject, value in zip(self.text(source, self.subject_key).tolist(),
                                      self.text(source, variable).tolist(), strict=True):
                if lookup.setdefault(subject, value) != value:
                    raise EngineError(
                        f"grouping '{grouping['id']}': subject {subject} has two values of "
                        f"{source}.{variable}")
            subjects = self.text(dataset, self.subject_key).tolist()
            values = np.empty(len(subjects), dtype=object)
            values[:] = [lookup.get(subject, "") for subject in subjects]
        self._values[key] = values
        return values

    def members(self, dataset: str, grouping: dict, rows: np.ndarray) -> list:
        """The groups of a grouping on some records: (kind, key, mask over `rows`)."""
        if grouping.get("dataDriven"):
            values = self.group_values(dataset, grouping)[rows]
            return [("value", value, values == value)
                    for value in sorted(set(values.tolist()) - {""})]
        return [("id", group["id"], self.where(dataset, group)[rows])
                for group in grouping["groups"]]

    def cells(self, dataset: str, rows: np.ndarray, by: list[tuple[int, dict]]) -> list:
        """Every cell of an analysis: its groups and its records (rule I10)."""
        fixed = [(n, grouping, self.members(dataset, grouping, rows))
                 for n, grouping in by if not grouping.get("dataDriven")]
        driven = [(n, grouping, self.group_values(dataset, grouping)[rows])
                  for n, grouping in by if grouping.get("dataDriven")]
        combinations: list[tuple] = [()]
        if driven:
            present = np.ones(len(rows), dtype=bool)
            for _, _, values in driven:
                present &= values != ""
            combinations = sorted(set(zip(*(values[present].tolist() for _, _, values in driven),
                                          strict=True)))
        found = []
        for choice in itertools.product(*(groups for _, _, groups in fixed)):
            mask = np.ones(len(rows), dtype=bool)
            for _, _, member in choice:
                mask &= member
            for combination in combinations:
                inner = mask.copy()
                for (_, _, values), wanted in zip(driven, combination, strict=True):
                    inner &= values == wanted
                labels = [(n, grouping["id"], kind, key)
                          for (n, grouping, _), (kind, key, _) in zip(fixed, choice, strict=True)]
                labels += [(n, grouping["id"], "value", wanted)
                           for (n, grouping, _), wanted in zip(driven, combination, strict=True)]
                found.append((sorted(labels), rows[inner]))
        return found

    # ---- tests (rules I12 and I13) -------------------------------------------------

    def population(self, analysis: dict) -> tuple[str, np.ndarray]:
        """The dataset and the records of the population of an occurrence test (rule I13)."""
        if analysis["id"] in self._populations:
            return self._populations[analysis["id"]]
        where = f"analysis '{analysis['id']}'"
        if not analysis.get("analysisSetId"):
            raise EngineError(f"{where}: an occurrence test needs an analysis set")
        chosen = self.event.sets[analysis["analysisSetId"]]
        datasets = sorted({condition["dataset"] for condition in ars.conditions(chosen)})
        if len(datasets) != 1:
            raise EngineError(f"{where}: the analysis set must be on one dataset, found "
                              f"{datasets}")
        source = datasets[0]
        keep = self.where(source, chosen).copy()
        if analysis.get("dataSubsetId"):
            for part in ars.and_parts(self.event.subsets[analysis["dataSubsetId"]]):
                if {condition["dataset"] for condition in ars.conditions(part)} == {source}:
                    keep &= self.where(source, part)
        self._populations[analysis["id"]] = (source, np.flatnonzero(keep))
        return self._populations[analysis["id"]]

    def population_groups(self, analysis: dict, grouping: dict) -> list[tuple[str, str, int]]:
        """The groups an occurrence test compares: (kind, key, subjects in the population).

        Rule I12b: a group without a subject in the population gives no row
        of the table, so it is not listed.
        """
        source, population = self.population(analysis)
        everyone = self.text(source, self.subject_key)[population]
        sizes = [(kind, key, methods.count_subjects(everyone[member].tolist()))
                 for kind, key, member in self.members(source, grouping, population)]
        return [(kind, key, size) for kind, key, size in sizes if size > 0]

    def compared_groups(self, analysis_id: str) -> list[tuple[str, str]] | None:
        """The groups the occurrence test of an analysis compares; None when it has none."""
        analysis = self.event.analyses.get(analysis_id)
        if analysis is None or analysis["variable"] != self.subject_key:
            return None
        compared = [self.event.groupings[entry["groupingId"]]
                    for entry in self.event.groupings_of(analysis)
                    if not entry.get("resultsByGroup")]
        if len(compared) != 1 or not analysis.get("analysisSetId"):
            return None
        return [(kind, key) for kind, key, _ in self.population_groups(analysis, compared[0])]

    def cell_values(self, row_id: str) -> tuple[str, list[float]] | None:
        """For a row of summary.continuous: its registry operation and its cell's sorted values."""
        if self._by_row is None:
            self._by_row = {result.row()["id"]: result for analysis_id in self.event.analyses
                            for result in self.results(analysis_id)}
        result = self._by_row.get(row_id)
        if result is None or result.method_id != "summary.continuous":
            return None
        analysis = self.event.analyses[result.analysis_id]
        cell = self._cells[(result.analysis_id, result.groups)]
        values = self.numbers(analysis["dataset"], analysis["variable"])[cell].tolist()
        return (self.binding.operations[result.operation_id][1],
                sorted(value for value in values if not math.isnan(value)))

    def counts(self, analysis: dict, rows: np.ndarray, compared: list[dict]) -> list[list[int]]:
        """The table of a chi-square or Fisher test on the records of one cell (rule I12)."""
        dataset, variable = analysis["dataset"], analysis["variable"]
        where = f"analysis '{analysis['id']}'"
        subjects = self.text(dataset, variable)[rows]
        if len(compared) == 2:
            first = self.members(dataset, compared[0], rows)
            second = self.members(dataset, compared[1], rows)
            return [[methods.count_subjects(subjects[a & b].tolist()) for _, _, b in second]
                    for _, _, a in first]
        if len(compared) != 1:
            raise EngineError(f"{where}: a test on a table compares one or two groupings, "
                              f"found {len(compared)}")
        if variable != self.subject_key:
            raise EngineError(f"{where}: an occurrence test counts subjects, so the analysis "
                              f"variable must be {self.subject_key}")
        grouping = compared[0]
        table = []
        for kind, key, size in self.population_groups(analysis, grouping):
            if kind == "value":
                here = self.group_values(dataset, grouping)[rows] == key
            else:
                group = next(g for g in grouping["groups"] if g["id"] == key)
                here = self.where(dataset, group)[rows]
            occurred = methods.count_subjects(subjects[here].tolist())
            if occurred > size:
                raise EngineError(f"{where}: group {key} has {occurred} subjects with a record "
                                  f"and {size} in the population")
            table.append([occurred, size - occurred])
        return table

    def strata_tables(self, analysis: dict, rows: np.ndarray, compared: list[dict],
                      strata: list[str]) -> tuple[list[list[list[int]]], list[float] | None]:
        """The tables of a stratified test on the records of one cell (rule I12d).

        One table per stratum, a combination of values of the strata columns that
        occurs; a record with a missing stratum value is left out. Rows: the groups
        of the one compared grouping; columns: the distinct values of the analysis
        variable, in increasing order; a count is a number of subjects, and a
        subject with two records in the cell is an error. The values are returned
        as numbers when the variable holds numbers, else None.
        """
        dataset, variable = analysis["dataset"], analysis["variable"]
        where = f"analysis '{analysis['id']}'"
        if len(compared) != 1:
            raise EngineError(f"{where}: a stratified test compares one grouping, found "
                              f"{len(compared)}")
        _, kind = self.column(dataset, variable)
        texts = self.text(dataset, variable)[rows]
        present = texts != ""
        for name in strata:
            present &= self.text(dataset, name)[rows] != ""
        subjects = self.text(dataset, self.subject_key)[rows]
        chosen = subjects[present].tolist()
        if len(set(chosen)) != len(chosen):
            raise EngineError(f"{where}: a subject has two records in a cell of a stratified "
                              "test")
        if kind == "number":
            numbers = self.numbers(dataset, variable)[rows]
            values = sorted(set(numbers[present].tolist()))
            column_of = {value: j for j, value in enumerate(values)}
            columns = [column_of.get(value, -1) for value in numbers.tolist()]
        else:
            values = sorted(set(texts[present].tolist()))
            column_of = {value: j for j, value in enumerate(values)}
            columns = [column_of.get(value, -1) for value in texts.tolist()]
        columns_of_strata = [self.text(dataset, name)[rows].tolist() for name in strata]
        keys = (list(zip(*columns_of_strata, strict=True)) if strata
                else [()] * len(rows))
        stratum_keys = sorted({keys[i] for i in np.flatnonzero(present).tolist()})
        groups = self.members(dataset, compared[0], rows)
        tables = []
        for stratum in stratum_keys:
            table = [[0] * len(values) for _ in groups]
            for i in np.flatnonzero(present).tolist():
                if keys[i] != stratum:
                    continue
                for g, (_, _, member) in enumerate(groups):
                    if member[i]:
                        table[g][columns[i]] += 1
            tables.append(table)
        return tables, ([float(v) for v in values] if kind == "number" else None)

    # ---- analyses ------------------------------------------------------------------

    def r_only(self, analysis_id: str) -> bool:
        """Whether the analysis uses a model-based method, which only the R engine runs.

        PLAN.md section 7.3: model-based methods are R only. Their results come
        from the R engine (ADR-015); this engine gives none for them.
        """
        analysis = self.event.analyses.get(analysis_id) or {}
        used = {self.binding.operations[operation_id][0]
                for operation_id, (method_id, _) in self.event.operations.items()
                if method_id == analysis.get("methodId") and operation_id in
                self.binding.operations}
        return bool(used) and all(
            "python" not in self.registry.method(method_id).implementations for method_id in used)

    def results(self, analysis_id: str) -> list[Result]:
        if analysis_id not in self._results and self.r_only(analysis_id):
            self._results[analysis_id] = []
        if analysis_id not in self._results:
            if analysis_id in self._running:
                chain = " -> ".join([*self._running, analysis_id])
                raise EngineError(f"analyses reference each other in a circle: {chain}")
            if analysis_id not in self.event.analyses:
                raise EngineError(f"no analysis '{analysis_id}'")
            self._running.append(analysis_id)
            try:
                self._results[analysis_id] = self._analysis(self.event.analyses[analysis_id])
            finally:
                self._running.pop()
        return self._results[analysis_id]

    def _analysis(self, analysis: dict) -> list[Result]:
        analysis_id, dataset, variable = analysis["id"], analysis["dataset"], analysis["variable"]
        where = f"analysis '{analysis_id}'"
        keep = np.ones(self.table(dataset).rows, dtype=bool)  # rule I6
        if analysis.get("analysisSetId"):
            keep &= self.where(dataset, self.event.sets[analysis["analysisSetId"]])
        if analysis.get("dataSubsetId"):
            keep &= self.where(dataset, self.event.subsets[analysis["dataSubsetId"]])
        rows = np.flatnonzero(keep)
        ordered = [(n, entry, self.event.groupings[entry["groupingId"]])
                   for n, entry in enumerate(self.event.groupings_of(analysis), start=1)]
        by = [(n, grouping) for n, entry, grouping in ordered if entry.get("resultsByGroup")]
        compared = [grouping for _, entry, grouping in ordered if not entry.get("resultsByGroup")]
        compared_labels = [(n, grouping["id"], "all", None)
                           for n, entry, grouping in ordered if not entry.get("resultsByGroup")]
        operations = sorted(
            ((operation, *self.binding.operations[operation_id])
             for operation_id, (method_id, operation) in self.event.operations.items()
             if method_id == analysis["methodId"]),
            key=lambda item: (item[0].get("order", 0), item[0]["id"]))
        for _, method_id, _ in operations:
            if "python" not in self.registry.method(method_id).implementations:
                raise EngineError(f"{where}: method {method_id} has no Python implementation")
        options = self.binding.options[analysis_id]
        hashes = {method_id: self.registry.options_hash(method_id, chosen)
                  for method_id, chosen in options.items()}
        found: list[Result] = []
        percents = []
        for labels, cell in self.cells(dataset, rows, by):
            summary = None
            for operation, method_id, name in operations:
                groups = tuple(labels)
                if method_id == "count.subjects":
                    value = methods.count_subjects(self.text(dataset, variable)[cell].tolist())
                elif method_id == "summary.continuous":
                    if summary is None:
                        summary = methods.summary_continuous(
                            self.numbers(dataset, variable)[cell].tolist(), **options[method_id])
                        self._cells[(analysis_id, groups)] = cell
                    value = summary[name]
                elif method_id == "percent.subjects":
                    percents.append((groups, operation))
                    continue
                elif method_id in ("test.chisq", "test.fisher.exact"):
                    table = self.counts(analysis, cell, compared)
                    test = methods.chisq_p if method_id == "test.chisq" else methods.fisher_exact_p
                    value = test(table)
                    groups = tuple(sorted([*labels, *compared_labels]))
                elif method_id == "test.cmh":
                    chosen = dict(options[method_id])
                    strata = chosen.pop("strata")
                    tables, values = self.strata_tables(analysis, cell, compared, strata)
                    value = methods.cmh_p(tables, values, **chosen)
                    groups = tuple(sorted([*labels, *compared_labels]))
                elif method_id == "test.anova.oneway":
                    if len(compared) != 1:
                        raise EngineError(f"{where}: the analysis of variance compares one "
                                          f"grouping, found {len(compared)}")
                    numbers = self.numbers(dataset, variable)[cell]
                    value = methods.anova_oneway_p(
                        numbers[member].tolist()
                        for _, _, member in self.members(dataset, compared[0], cell))
                    groups = tuple(sorted([*labels, *compared_labels]))
                else:
                    raise EngineError(f"{where}: the Python engine does not know {method_id}")
                if isinstance(value, float) and not math.isfinite(value):
                    raise EngineError(f"{where}, operation {operation['id']}: the result is "
                                      f"{value}")
                found.append(Result(analysis_id, operation["id"], groups, method_id,
                                    hashes[method_id], value))
        for groups, operation in percents:
            numerator = self._referenced(analysis, operation, "NUMERATOR", groups, found)
            denominator = self._referenced(analysis, operation, "DENOMINATOR", groups, found)
            found.append(Result(analysis_id, operation["id"], groups, "percent.subjects",
                                hashes["percent.subjects"],
                                methods.percent(numerator, denominator)))
        return found

    def _referenced(self, analysis: dict, operation: dict, role: str, groups: tuple,
                    own: list[Result]) -> float | int | None:
        """The result an operation references in a role, for one cell (percent.subjects)."""
        where = f"analysis '{analysis['id']}', operation '{operation['id']}'"
        relationships = [r for r in operation.get("referencedOperationRelationships") or []
                         if (r.get("referencedOperationRole") or {}).get("controlledTerm") == role]
        if len(relationships) != 1:
            raise EngineError(f"{where}: needs one referenced operation with the role {role}")
        targets = [r["analysisId"] for r in analysis.get("referencedAnalysisOperations") or []
                   if r.get("referencedOperationRelationshipId") == relationships[0]["id"]]
        if len(targets) != 1:
            raise EngineError(f"{where}: the analysis does not say which analysis gives the "
                              f"{role}")
        pool = own if targets[0] == analysis["id"] else self.results(targets[0])
        cell = frozenset((grouping, kind, key) for _, grouping, kind, key in groups)
        wanted = relationships[0]["operationId"]
        if role == "NUMERATOR":  # in the same cell
            fits = [r for r in pool if r.operation_id == wanted and r.pairs() == cell]
        else:  # the one result whose groups are all groups of the cell
            fits = [r for r in pool if r.operation_id == wanted and r.pairs() <= cell]
        if len(fits) != 1:
            raise EngineError(f"{where}: {len(fits)} results of {targets[0]}.{wanted} fit the "
                              f"cell as {role}")
        return fits[0].value

    def run(self) -> list[dict]:
        """Every analysis of the event, as ARD rows sorted by their ID.

        An analysis of a model-based method gives no row here (`r_only`).
        """
        rows = [result.row() for analysis_id in self.event.analyses
                for result in self.results(analysis_id)]
        rows.sort(key=lambda row: row["id"])
        for one, two in itertools.pairwise(rows):
            if one["id"] == two["id"]:
                raise EngineError(f"two results have the ID {one['id']}")
        return rows


def run(event: ars.Event, registry: Registry, binding: ars.Binding, tables: dict[str, Table],
        subject_key: str = SUBJECT_KEY) -> list[dict]:
    return Engine(event, registry, binding, tables, subject_key).run()
