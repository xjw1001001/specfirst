"""The Python scripts: count, percent, continuous summary, chi-square and one-way ANOVA.

Each script reads the reference ADaM as Parquet with pandas, applies the
analysis set, the data subset and the groupings as the ARS states them, and
computes the statistic with numpy or scipy (ADR-021, decision 3).
"""

from __future__ import annotations

from collections.abc import Callable

from specfirst.recompute.common import (
    Decisions,
    comment,
    condition_words,
    header,
    lit,
    num,
    statement,
    where_words,
)
from specfirst.recompute.reading import (
    Analysis,
    Condition,
    Grouping,
    NotCovered,
    Where,
    json_number,
)

Types = Callable[[str, str], str]  # (dataset, column) -> "number", "text" or another kind
QUANTILE = {"sas5": "averaged_inverted_cdf", "r7": "linear"}  # numpy's names
DESCRIPTIVE = {("count.subjects",), ("count.subjects", "percent.subjects"),
               ("summary.continuous",)}
TESTS = {("test.chisq",), ("test.anova.oneway",)}
COMPARISONS = {"GT": ">", "GE": ">=", "LT": "<", "LE": "<="}


def frame(dataset: str) -> str:
    return dataset.lower()


class PyWriter:
    def __init__(self, analysis: Analysis, kit_id: str, registry: dict, decisions: Decisions,
                 types: Types, key: str, versions: dict[str, str],
                 other: Callable[[str], Analysis]):
        self.a, self.kit_id, self.registry, self.decisions = analysis, kit_id, registry, decisions
        self.types, self.key, self.versions, self.other = types, key, versions, other
        self.datasets: list[str] = []
        self.den_key = "()"

    # -- expressions --------------------------------------------------------------
    def need(self, dataset: str) -> str:
        if dataset.upper() not in self.datasets:
            self.datasets.append(dataset.upper())
        return frame(dataset)

    def condition(self, c: Condition, on: str, dataset: str) -> str:
        """Rule I3 on the frame `on` of `dataset`; rule I4 for a condition on another one."""
        if c.dataset.upper() != dataset.upper():
            other = self.need(c.dataset)
            inner = self.condition(c, other, c.dataset)
            return f"{on}[{lit(self.key)}].isin({other}.loc[{inner}, {lit(self.key)}])"
        column = f"{on}[{lit(c.variable)}]"
        kind = self.types(c.dataset, c.variable)
        if kind == "number":
            numbers = [json_number(v) for v in c.values]
            if None in numbers:
                raise NotCovered(f"{condition_words(c)}: a value that is not a number")
            listed = "[" + ", ".join(num(n) for n in numbers) + "]"
            if c.comparator in ("EQ", "IN"):
                return f"{column}.isin({listed})"
            if c.comparator in ("NE", "NOTIN"):
                return f"~{column}.isin({listed})"
            if c.comparator in COMPARISONS and len(numbers) == 1:
                return f"({column} {COMPARISONS[c.comparator]} {num(numbers[0])})"
        elif kind == "text":
            listed = "[" + ", ".join(lit(v) for v in c.values) + "]"
            if c.comparator in ("EQ", "IN"):
                return f'{column}.fillna("").isin({listed})'
            if c.comparator in ("NE", "NOTIN"):
                return f'~{column}.fillna("").isin({listed})'
        raise NotCovered(f"{condition_words(c)}: the comparator on a column of kind {kind}")

    def where(self, w: Where, on: str, dataset: str) -> str:
        if w.condition is not None:
            return self.condition(w.condition, on, dataset)
        parts = [self.where(p, on, dataset) for p in w.parts]
        if w.operator == "NOT" and len(parts) == 1:
            return f"~({parts[0]})"
        if w.operator in ("AND", "OR"):
            join = " & " if w.operator == "AND" else " | "
            return join.join(f"({p})" for p in parts)
        raise NotCovered(f"a compound expression with the operator {w.operator}")

    # -- steps --------------------------------------------------------------------
    def records(self, analysis: Analysis, name: str) -> list[str]:
        """The analysis records of `analysis` (rule I6): its set, then its subset."""
        data = self.need(analysis.dataset)
        lines = self.decisions.above([analysis.set_id])
        lines += comment(f"Analysis set {analysis.set_id} ({analysis.set_name}): "
                         f"{where_words(analysis.set_where)}")
        kept = self.where(analysis.set_where, data, analysis.dataset)
        lines.append(f"{name} = {data}[{kept}]")
        if analysis.subset_where is not None:
            lines += self.decisions.above([str(analysis.subset_id)])
            lines += comment(f"Data subset {analysis.subset_id} ({analysis.subset_name}): "
                             f"{where_words(analysis.subset_where)}")
            kept = self.where(analysis.subset_where, name, analysis.dataset)
            lines.append(f"{name} = {name}[{kept}]")
        return lines

    def groups(self, grouping: Grouping, name: str, on: str, dataset: str) -> list[str]:
        lines = self.decisions.above([grouping.id])
        bound = self.decisions.bound(grouping.id)
        lines += comment(f"Grouping {grouping.id} ({grouping.name}): defined groups by "
                         f"{grouping.dataset}.{grouping.variable} (rule I8)"
                         + (f"; decision {', '.join(bound)}" if bound else ""))
        lines.append(f"{name} = {{")
        for group in grouping.groups:
            lines.append(f"    {lit(group.id)}: {self.where(group.where, on, dataset)},")
        lines.append("}")
        return lines

    def data_driven(self, groupings: list[Grouping], name: str) -> list[str]:
        for g in groupings:
            if g.dataset.upper() != self.a.dataset.upper() or \
                    self.types(g.dataset, g.variable) != "text":
                raise NotCovered(f"data-driven grouping {g.id}: only a text column of the "
                                 "analysis dataset is covered")
        columns = [g.variable for g in groupings]
        lines = comment("Data-driven groupings " + ", ".join(
            f"{g.id} ({g.dataset}.{g.variable})" for g in groupings)
            + ": one group per combination of values that occurs on the analysis records; "
              "the empty text is missing (rules I1, I9, I10)")
        listed = "[" + ", ".join(lit(c) for c in columns) + "]"
        lines.append(f"values = records[{listed}].fillna(\"\")")
        lines.append("values = sorted(set(map(tuple, values[(values != \"\").all(axis=1)]"
                     ".to_numpy().tolist())))")
        masks = " & ".join(f"(records[{lit(c)}] == v[{i}])" for i, c in enumerate(columns))
        lines.append(f"{name} = {{tuple(\"=\" + x for x in v): {masks} for v in values}}")
        return lines

    @staticmethod
    def cells(by: list[tuple[str, bool]]) -> list[str]:
        """The loop over the cells (rule I10); `by`: (name, data-driven) per block."""
        if not by:
            return ["for key, cell in [((), records)]:"]
        loop = ", ".join(f"(k{i}, m{i})" for i in range(len(by)))
        parts = [f"*k{i}" if driven else f"k{i}" for i, (_, driven) in enumerate(by)]
        masks = " & ".join(f"m{i}" for i in range(len(by)))
        if len(by) == 1:
            first = f"for k0, m0 in {by[0][0]}.items():"
        else:
            first = f"for {loop} in product({', '.join(name + '.items()' for name, _ in by)}):"
        return [first, f"    key, cell = ({', '.join(parts)},), records[{masks}]"]

    def count(self, records: str, variable: str, dataset: str, mask: str | None) -> str:
        """count.subjects, statements 1 and 2: the distinct non-missing values."""
        column = lit(variable)
        if self.types(dataset, variable) == "text":
            kept = f"({records}[{column}].fillna(\"\") != \"\")"
            kept = f"{mask} & {kept}" if mask else kept
            return f"{records}.loc[{kept}, {column}].nunique()"
        kept = mask or f"{records}.index"
        return f"{records}.loc[{kept}, {column}].dropna().nunique()"

    # -- the script ---------------------------------------------------------------
    def write(self) -> tuple[str, str]:
        methods = tuple(self.a.methods)
        if methods in DESCRIPTIVE:
            return self.descriptive(methods), "descriptive"
        if methods in TESTS:
            return self.test(methods[0]), methods[0]
        raise NotCovered(f"no Python template for {', '.join(methods)}")

    def preamble(self, needs_numpy: bool, needs_stats: bool) -> list[str]:
        packages = (f"pandas {self.versions.get('pandas')}"
                    + (f", numpy {self.versions.get('numpy')}" if needs_numpy else "")
                    + (f", scipy {self.versions.get('scipy')}" if needs_stats else "")
                    + " (env/requirements.lock)")
        lines = header(self.a, self.kit_id,
                       f"python {self.a.id}.py <folder of the reference ADaM as Parquet> "
                       "<output CSV>", packages)
        lines += ["import sys", "from itertools import product", "from pathlib import Path", ""]
        lines += ["import numpy as np"] if needs_numpy else []
        lines.append("import pandas as pd")
        if needs_stats:
            lines.append("from scipy import stats")
        lines += ["", "adam, out = Path(sys.argv[1]), sys.argv[2]"]
        lines += [f"{frame(d)} = pd.read_parquet(adam / {lit(d.lower() + '.parquet')})"
                  for d in self.datasets]
        lines += ["", "", "def num(value):",
                  "    return \"\" if value is None or value != value else repr(float(value))",
                  "", ""]
        return lines

    def footer(self) -> list[str]:
        columns = ["operation_id"] + [f"group{i + 1}" for i in range(len(self.a.groupings))] \
            + ["value"]
        listed = "[" + ", ".join(lit(c) for c in columns) + "]"
        lines = [f"pd.DataFrame(rows, columns={listed}, dtype=object).to_csv(out, index=False)"]
        shown = self.decisions.bound(self.a.method_id)
        if shown:
            lines += comment("Display decisions (decimals, rounding), not part of the numbers: "
                             + ", ".join(shown))
        return lines

    def descriptive(self, methods: tuple[str, ...]) -> str:
        a = self.a
        if any(not g.by_group for g in a.groupings):
            raise NotCovered("a descriptive analysis with a compared grouping")
        body = self.records(a, "records")
        by: list[tuple[str, bool]] = []
        for i, g in enumerate(a.groupings):
            if not g.data_driven:
                body += self.groups(g, f"g{i + 1}", "records", a.dataset)
                by.append((f"g{i + 1}", False))
        driven = [g for g in a.groupings if g.data_driven]
        if driven:
            if [g.id for g in a.groupings[-len(driven):]] != [g.id for g in driven]:
                raise NotCovered("a data-driven grouping before a grouping with defined groups")
            body += self.data_driven(driven, "dd")
            by.append(("dd", True))
        ops = {op.operation: op for op in a.operations}
        if "pct" in ops:
            body += self.denominator(ops["pct"].denominator, a.groupings)
        body += ["", *self.decisions.above([a.id])]
        if "summary.continuous" in methods:
            option = a.options["summary.continuous"]["quantile_definition"]
            source = a.option_sources["summary.continuous"]["quantile_definition"]
            number = statement(self.registry, "summary.continuous",
                               f"quantile_definition {option}")
            body += comment(f"summary.continuous, statements 1 to 6 and 10; the quantiles by "
                            f"statement {number}, quantile_definition {option} ({source}): "
                            f"numpy's method {QUANTILE[option]}")
            if self.types(a.dataset, a.variable) != "number":
                raise NotCovered(f"a continuous summary of the text column {a.variable}")
        else:
            body += comment(f"count.subjects, statements 1 to 3: the distinct non-missing values "
                            f"of {a.dataset}.{a.variable} on the records of the cell"
                            + ("; percent.subjects, statements 1 to 4: 100 n over the "
                               "denominator, missing when it is 0" if "pct" in ops else ""))
        body += ["rows = []", *self.cells(by)]
        if "summary.continuous" in methods:
            quantile = lit(QUANTILE[option])
            formula = {
                "n": "n",
                "mean": "x.mean() if n else None",
                "sd": "None if n < 2 else (0.0 if x[0] == x[-1] else x.std(ddof=1))",
                "median": f"np.quantile(x, 0.5, method={quantile}) if n else None",
                "q1": f"np.quantile(x, 0.25, method={quantile}) if n else None",
                "q3": f"np.quantile(x, 0.75, method={quantile}) if n else None",
                "min": "x[0] if n else None",
                "max": "x[-1] if n else None",
            }
            body.append(f"    x = np.sort(cell[{lit(a.variable)}].dropna().to_numpy(dtype=float))")
            body.append("    n = len(x)")
            for op in a.operations:
                body.append(f"    rows.append(({lit(op.id)}, *key, num({formula[op.operation]})))")
        else:
            body.append(f"    n = {self.count('cell', a.variable, a.dataset, None)}")
            body.append(f"    rows.append(({lit(ops['n'].id)}, *key, num(n)))")
            if "pct" in ops:
                body.append(f"    d = den[{self.den_key}]")
                body.append(f"    rows.append(({lit(ops['pct'].id)}, *key, "
                            "num(100 * n / d if d else None)))")
        body += ["", *self.footer()]
        return "\n".join(self.preamble("summary.continuous" in methods, False) + body) + "\n"

    def denominator(self, reference: tuple[str, str] | None, groupings: list[Grouping]
                    ) -> list[str]:
        """The denominator of a percent: the count of the referenced analysis (rule I15)."""
        if reference is None:
            raise NotCovered("a percent without a denominator")
        other = self.other(reference[0])
        if tuple(other.methods) != ("count.subjects",):
            raise NotCovered(f"the denominator analysis {other.id} is not a count of subjects")
        positions = []
        for g in other.groupings:
            found = [i for i, mine in enumerate(groupings) if mine.id == g.id]
            if not found or g.data_driven:
                raise NotCovered(f"the denominator analysis {other.id} has a grouping the "
                                 "cell does not have")
            positions.append(found[0])
        lines = ["", *comment(f"The denominator: the count of subjects of {other.id} "
                              f"({other.name}) whose groups are all groups of the cell "
                              "(rule I15)")]
        lines += self.records(other, "den_records")
        names = []
        for j, g in enumerate(other.groupings):
            names.append(f"den_g{j + 1}")
            lines += self.groups(g, names[-1], "den_records", other.dataset)
        if not names:
            lines.append(f"den = {{(): {self.count('den_records', other.variable, other.dataset,
                                                    None)}}}")
            self.den_key = "()"
            return lines
        loop = ", ".join(f"(d{j}, n{j})" for j in range(len(names)))
        mask = " & ".join(f"n{j}" for j in range(len(names)))
        keys = ", ".join(f"d{j}" for j in range(len(names)))
        counted = self.count("den_records", other.variable, other.dataset, mask)
        if len(names) == 1:
            lines.append(f"den = {{(d0,): {counted} for d0, n0 in {names[0]}.items()}}")
        else:
            lines.append(f"den = {{({keys},): {counted} for {loop} in "
                         f"product({', '.join(n + '.items()' for n in names)})}}")
        # The key of the cell's denominator: the cell's groups of those groupings.
        self.den_key = "(" + ", ".join(f"key[{p}]" for p in positions) + ",)"
        return lines

    def test(self, method: str) -> str:
        a = self.a
        compared = [g for g in a.groupings if not g.by_group]
        if any(g.by_group for g in a.groupings) or any(g.data_driven for g in compared):
            raise NotCovered(f"{method} with a grouping by group or a data-driven grouping")
        body = self.records(a, "records")
        for i, g in enumerate(a.groupings):
            body += self.groups(g, f"g{i + 1}", "records", a.dataset)
        body += ["", *self.decisions.above([a.id])]
        key = "(" + ", ".join(lit("*") for _ in a.groupings) + ",)"
        if method == "test.chisq":
            if len(compared) != 2:
                raise NotCovered("a chi-square test with other than two compared groupings")
            body += comment("Rule I12a: the table of the distinct values of "
                            f"{a.dataset}.{a.variable} by group of {compared[0].id} and of "
                            f"{compared[1].id}")
            counted = self.count("records", a.variable, a.dataset, "r & c")
            body.append(f"table = np.array([[{counted} for c in g2.values()] "
                        "for r in g1.values()])")
            body += comment("test.chisq, statements 1, 2 and 4: rows and columns whose total is "
                            "0 are left out; with fewer than 2 left the result is missing; no "
                            "continuity correction")
            body.append("table = table[table.sum(axis=1) > 0][:, table.sum(axis=0) > 0]")
            body.append("p = stats.chi2_contingency(table, correction=False).pvalue "
                        "if min(table.shape) >= 2 else None")
        else:
            if len(compared) != 1:
                raise NotCovered("an analysis of variance with other than one compared grouping")
            if self.types(a.dataset, a.variable) != "number":
                raise NotCovered(f"an analysis of variance of the text column {a.variable}")
            body += comment(f"Rule I12c: the values of {a.dataset}.{a.variable} per group of "
                            f"{compared[0].id}; test.anova.oneway, statements 1 and 2: missing "
                            "values and groups without values are left out")
            body.append(f"samples = [records.loc[m, {lit(a.variable)}].dropna()"
                        ".to_numpy(dtype=float) for m in g1.values()]")
            body.append("samples = [s for s in samples if len(s)]")
            body.append("k, total = len(samples), sum(len(s) for s in samples)")
            body += comment("Statement 5: when no group holds two different values, 0, or "
                            "missing when all hold the same value; otherwise the F test of "
                            "statements 3 and 4")
            body += ["if k < 2 or total - k < 1:", "    p = None",
                     "elif all(s.min() == s.max() for s in samples):",
                     "    p = None if len({s[0] for s in samples}) == 1 else 0.0",
                     "else:", "    p = stats.f_oneway(*samples).pvalue"]
        body += [f"rows = [({lit(a.operations[0].id)}, *{key}, num(p))]", "", *self.footer()]
        return "\n".join(self.preamble(True, True) + body) + "\n"
