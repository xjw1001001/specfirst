"""The R scripts: Fisher's exact test, CMH, ANCOVA and the mixed model (ADR-021, decision 3).

The locked R library reads no Parquet, so an R script reads the CSV copies
that `adam_csv.py` writes from the reference ADaM, every column as text,
and turns the columns it computes with into numbers itself.
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

Types = Callable[[str, str], str]
COMPARISONS = {"GT": ">", "GE": ">=", "LT": "<", "LE": "<="}
MODELS = {"model.ancova.lsmeans", "model.ancova.pairwise", "model.ancova.dose_response",
          "model.mmrm.lsmeans", "model.mmrm.pairwise"}
# The registry operations of a model, in the order of emmeans' summary columns.
EMMEANS = {"lsmean": "emmean", "estimate": "estimate", "se": "SE", "lower_cl": "lower.CL",
           "upper_cl": "upper.CL", "p_value": "p.value"}


def frame(dataset: str) -> str:
    return dataset.lower()


class RWriter:
    def __init__(self, analysis: Analysis, kit_id: str, registry: dict, decisions: Decisions,
                 types: Types, key: str, versions: dict[str, str]):
        self.a, self.kit_id, self.registry, self.decisions = analysis, kit_id, registry, decisions
        self.types, self.key, self.versions = types, key, versions
        self.datasets: list[str] = []
        self.numbers: dict[str, set[str]] = {}  # dataset -> its columns read as numbers

    # -- expressions --------------------------------------------------------------
    def need(self, dataset: str, number_columns: tuple[str, ...] = ()) -> str:
        if dataset.upper() not in self.datasets:
            self.datasets.append(dataset.upper())
        self.numbers.setdefault(dataset.upper(), set()).update(number_columns)
        return frame(dataset)

    def column(self, dataset: str, variable: str, on: str) -> str:
        if self.types(dataset, variable) == "number":
            self.need(dataset, (variable,))
        return f"{on}${variable}"

    def condition(self, c: Condition, on: str, dataset: str) -> str:
        """Rule I3 on the data frame `on` of `dataset`; rule I4 for another dataset."""
        if c.dataset.upper() != dataset.upper():
            other = self.need(c.dataset)
            inner = self.condition(c, other, c.dataset)
            return f"{on}${self.key} %in% {other}${self.key}[{inner}]"
        kind = self.types(c.dataset, c.variable)
        column = self.column(c.dataset, c.variable, on)
        if kind == "number":
            numbers = [json_number(v) for v in c.values]
            if None in numbers:
                raise NotCovered(f"{condition_words(c)}: a value that is not a number")
            listed = "c(" + ", ".join(num(n) for n in numbers) + ")"
            if c.comparator in ("EQ", "IN"):
                return f"{column} %in% {listed}"
            if c.comparator in ("NE", "NOTIN"):
                return f"!({column} %in% {listed})"
            if c.comparator in COMPARISONS and len(numbers) == 1:
                return f"(!is.na({column}) & {column} {COMPARISONS[c.comparator]} " \
                       f"{num(numbers[0])})"
        elif kind == "text":
            texts = [v for v in c.values if v != ""]
            parts = [f"{column} %in% c(" + ", ".join(lit(v) for v in texts) + ")"] \
                if texts else []
            if "" in c.values:  # the empty text stands for the missing value (rule I3)
                parts.append(f"is.na({column})")
            if not parts:
                raise NotCovered(f"{condition_words(c)}: a condition without a value")
            inside = parts[0] if len(parts) == 1 else f"({' | '.join(parts)})"
            if c.comparator in ("EQ", "IN"):
                return inside
            if c.comparator in ("NE", "NOTIN"):
                return f"!({inside})"
        raise NotCovered(f"{condition_words(c)}: the comparator on a column of kind {kind}")

    def where(self, w: Where, on: str, dataset: str) -> str:
        if w.condition is not None:
            return self.condition(w.condition, on, dataset)
        parts = [self.where(p, on, dataset) for p in w.parts]
        if w.operator == "NOT" and len(parts) == 1:
            return f"!({parts[0]})"
        if w.operator in ("AND", "OR"):
            join = " & " if w.operator == "AND" else " | "
            return join.join(f"({p})" for p in parts)
        raise NotCovered(f"a compound expression with the operator {w.operator}")

    # -- steps --------------------------------------------------------------------
    def records(self) -> list[str]:
        a = self.a
        data = self.need(a.dataset)
        lines = self.decisions.above([a.set_id])
        lines += comment(f"Analysis set {a.set_id} ({a.set_name}): {where_words(a.set_where)}")
        lines.append(f"records <- {data}[{self.where(a.set_where, data, a.dataset)}, ]")
        if a.subset_where is not None:
            lines += self.decisions.above([str(a.subset_id)])
            lines += comment(f"Data subset {a.subset_id} ({a.subset_name}): "
                             f"{where_words(a.subset_where)}")
            lines.append(f"records <- records[{self.where(a.subset_where, 'records', a.dataset)}"
                         ", ]")
        return lines

    def membership(self, grouping: Grouping, on: str, dataset: str, name: str) -> list[str]:
        """The group of each record: a matrix of one column per group (rules I8, I17)."""
        lines = self.decisions.above([grouping.id])
        bound = self.decisions.bound(grouping.id)
        lines += comment(f"Grouping {grouping.id} ({grouping.name}): defined groups by "
                         f"{grouping.dataset}.{grouping.variable} (rule I8)"
                         + (f"; decision {', '.join(bound)}" if bound else ""))
        lines.append(f"{name} <- cbind(")
        for i, group in enumerate(grouping.groups):
            end = "," if i + 1 < len(grouping.groups) else ""
            lines.append(f"  {lit(group.id)} = {self.where(group.where, on, dataset)}{end}")
        lines.append(")")
        return lines

    # -- the script ---------------------------------------------------------------
    def write(self) -> tuple[str, str]:
        methods = self.a.methods
        if methods == ["test.fisher.exact"]:
            return self.fisher(), "test.fisher.exact"
        if methods == ["test.cmh"]:
            return self.cmh(), "test.cmh"
        if len(methods) == 1 and methods[0] in MODELS:
            if methods[0].startswith("model.ancova"):
                return self.ancova(methods[0]), methods[0]
            return self.mmrm(methods[0]), methods[0]
        raise NotCovered(f"no R template for {', '.join(methods)}")

    def preamble(self, packages: list[str]) -> list[str]:
        versions = ", ".join(f"{p} {self.versions.get(p)}" for p in packages)
        lines = header(self.a, self.kit_id,
                       f"Rscript {self.a.id}.R <folder of the CSV copies of the reference ADaM> "
                       "<output CSV>", f"R {self.versions.get('R')}"
                       + (f", {versions}" if packages else "") + " (env/r-packages.lock)")
        lines += ["args <- commandArgs(trailingOnly = TRUE)", "adam <- args[1]"]
        for dataset in self.datasets:
            name = frame(dataset)
            lines.append(f"{name} <- utils::read.csv(file.path(adam, {lit(name + '.csv')}), "
                         "colClasses = \"character\", na.strings = \"\")")
            for column in sorted(self.numbers.get(dataset, ())):
                lines.append(f"{name}${column} <- as.numeric({name}${column})")
        lines += ["num <- function(v) ifelse(is.na(v), \"\", sprintf(\"%.17g\", v))", ""]
        return lines

    def footer(self, rows: str) -> list[str]:
        lines = [f"utils::write.csv({rows}, args[2], row.names = FALSE)"]
        shown = self.decisions.bound(self.a.method_id)
        if shown:
            lines += comment("Display decisions (decimals, rounding), not part of the numbers: "
                             + ", ".join(shown))
        return lines

    def columns(self) -> list[str]:
        return [f"group{i + 1}" for i in range(len(self.a.groupings))]

    # -- Fisher's exact test (rule I12b) ----------------------------------------------
    def population(self) -> tuple[list[str], str]:
        """Rule I13: the subjects of the analysis set in its dataset, restricted by the parts
        of the data subset joined by AND at its top whose conditions are all on it."""
        a = self.a
        dataset = {c.dataset.upper() for c in a.set_where.conditions()}
        if len(dataset) != 1:
            raise NotCovered("an analysis set on more than one dataset")
        base = dataset.pop()
        data = self.need(base)
        parts = [a.set_where]
        if a.subset_where is not None:
            top = list(a.subset_where.parts) if a.subset_where.operator == "AND" \
                else [a.subset_where]
            parts += [p for p in top if p.conditions() and
                      all(c.dataset.upper() == base for c in p.conditions())]
        kept = " & ".join(f"({self.where(p, data, base)})" for p in parts)
        lines = comment(f"Rule I13: the population, the subjects of {base} in the analysis set, "
                        "restricted by the parts of the data subset on that dataset: "
                        + " AND ".join(where_words(p) for p in parts))
        lines.append(f"population <- {data}[{kept}, ]")
        return lines, data

    def fisher(self) -> str:
        a = self.a
        compared = [g for g in a.groupings if not g.by_group]
        driven = [g for g in a.groupings if g.by_group]
        if len(compared) != 1 or a.groupings[0].by_group or \
                any(not g.data_driven for g in driven) or a.variable != self.key:
            raise NotCovered("Fisher's test is covered as rule I12b: one compared grouping "
                             "first, then data-driven groupings, on the subject key")
        for g in driven:
            if g.dataset.upper() != a.dataset.upper():
                raise NotCovered(f"data-driven grouping {g.id} on another dataset")
        body = self.records()
        population, base = self.population()
        body += population
        grouping = compared[0]
        body += self.membership(grouping, "population", base, "arms")
        body += comment("The groups of the compared grouping that have subjects in the "
                        "population are the rows (rule I12b)")
        body.append("arms <- arms[, colSums(arms) > 0, drop = FALSE]")
        columns = [g.variable for g in driven]
        if driven:
            body += comment("Data-driven groupings " + ", ".join(
                f"{g.id} ({g.dataset}.{g.variable})" for g in driven)
                + ": the combinations of values that occur on the analysis records (rules I9, "
                  "I10)")
            listed = "c(" + ", ".join(lit(c) for c in columns) + ")"
            body.append(f"cells <- unique(records[stats::complete.cases(records[{listed}]), "
                        f"{listed}, drop = FALSE])")
            ordered = ", ".join(f"cells${c}" for c in columns)
            body.append(f"cells <- cells[order({ordered}), , drop = FALSE]")
        else:
            body.append("cells <- data.frame(row.names = 1L)")
        body += ["", *self.decisions.above([a.id])]
        body += comment("Per cell the table of rule I12b: per row, the subjects with at least one "
                        "record in the cell and the other subjects of the population. "
                        "test.fisher.exact, statements 1, 2 and 5: rows and columns whose total "
                        "is 0 are left out; fewer than 2 left gives a missing result; "
                        "stats::fisher.test is the registry's test for a 2 x 2 table, not for a "
                        "larger one (statement 8)")
        body.append("p <- sapply(seq_len(nrow(cells)), function(i) {")
        if driven:
            match = " & ".join(f"records${c} %in% cells${c}[i]" for c in columns)
            body.append(f"  ids <- unique(records${self.key}[{match}])")
        else:
            body.append(f"  ids <- unique(records${self.key})")
        body.append(f"  with <- colSums(arms & population${self.key} %in% ids)")
        body.append("  table <- cbind(with, colSums(arms) - with)  # a row per group")
        body.append("  table <- table[rowSums(table) > 0, colSums(table) > 0, drop = FALSE]")
        body.append("  if (min(dim(table)) < 2) return(NA)")
        body.append("  if (any(dim(table) > 2)) stop(\"a table larger than 2 x 2 (statement 8)\")")
        body.append("  stats::fisher.test(table)$p.value")
        body.append("})")
        groups = [lit("*")] + [f"paste0(\"=\", cells${c})" for c in columns]
        names = self.columns()
        made = ", ".join(f"{n} = {g}" for n, g in zip(names, groups, strict=True))
        body.append(f"rows <- data.frame(operation_id = {lit(a.operations[0].id)}, {made}, "
                    "value = num(p))")
        body += ["", *self.footer("rows")]
        return "\n".join(self.preamble([]) + body) + "\n"

    # -- CMH (rule I12d) ----------------------------------------------------------
    def cmh(self) -> str:
        a = self.a
        options = a.options["test.cmh"]
        if len(a.groupings) != 1 or a.groupings[0].by_group or a.groupings[0].data_driven:
            raise NotCovered("CMH is covered with one compared grouping of defined groups")
        if options["scores"] != "table" and options["statistic"] == "row_mean_scores":
            raise NotCovered("CMH with rank scores")
        if self.types(a.dataset, a.variable) != "number":
            raise NotCovered("CMH with table scores needs a number column")
        strata = [str(s) for s in options["strata"]]
        variable = self.column(a.dataset, a.variable, "records")
        body = self.records()
        body += self.membership(a.groupings[0], "records", a.dataset, "member")
        body.append("stopifnot(all(rowSums(member) <= 1))  # a record in two groups is an error")
        body.append("records$TRT <- factor(apply(member, 1, function(m) colnames(member)[m][1]), "
                    "levels = colnames(member))")
        body += ["", *self.decisions.above([a.id])]
        listed = "c(" + ", ".join(lit(s) for s in ["TRT", a.variable, *strata]) + ")"
        body += comment("Rule I12d: a record with a missing value of a stratum column or of the "
                        "analysis variable is left out; a subject with two records is an error")
        body.append(f"d <- records[stats::complete.cases(records[{listed}]), ]")
        body.append(f"stopifnot(!anyDuplicated(d${self.key}))")
        stratum = "d$" + strata[0] if len(strata) == 1 else \
            "interaction(" + ", ".join(f"d${s}" for s in strata) + ", drop = TRUE)"
        body.append(f"d$STRATUM <- factor({stratum})" if strata else "d$STRATUM <- factor(1)")
        body += comment("test.cmh, statement 2: a row or column whose total is 0 is left out, a "
                        "stratum with fewer than 2 subjects adds nothing")
        body.append("d <- d[d$STRATUM %in% names(which(table(d$STRATUM) >= 2)), ]")
        body.append("d$TRT <- droplevels(d$TRT)")
        body.append(f"values <- sort(unique({variable.replace('records$', 'd$')}))")
        statistic = options["statistic"]
        n_stat = statement(self.registry, "test.cmh", "The option statistic chooses B")
        n_scores = statement(self.registry, "test.cmh", "The option scores")
        if statistic == "row_mean_scores":
            body += comment(f"Statements {n_stat} and {n_scores}: statistic row_mean_scores "
                            f"({a.option_sources['test.cmh']['statistic']}) with the values as "
                            "scores: coin's test of an ordered response with those scores")
            body.append(f"d$Y <- factor(d${a.variable}, levels = values, ordered = TRUE)")
            test = "coin::cmh_test(Y ~ TRT | STRATUM, data = d, scores = list(Y = values))"
        else:
            body += comment(f"Statement {n_stat}: statistic general_association "
                            f"({a.option_sources['test.cmh']['statistic']}): coin's test of a "
                            "nominal response")
            body.append(f"d$Y <- factor(d${a.variable}, levels = values)")
            test = "coin::cmh_test(Y ~ TRT | STRATUM, data = d)"
        body += comment("With fewer than 2 rows or columns left the result is missing "
                        "(statement 2)")
        body.append("p <- if (nlevels(d$TRT) < 2 || length(values) < 2) NA else "
                    f"as.numeric(coin::pvalue({test}))")
        body.append(f"rows <- data.frame(operation_id = {lit(a.operations[0].id)}, "
                    f"group1 = {lit('*')}, value = num(p))")
        body += ["", *self.footer("rows")]
        return "\n".join(self.preamble(["coin"]) + body) + "\n"

    # -- the models ---------------------------------------------------------------
    def model_records(self, columns: list[str]) -> list[str]:
        a = self.a
        if len(a.groupings) != 1 or a.groupings[0].data_driven:
            raise NotCovered("a model with other than one grouping of defined groups (rule I17)")
        lines = self.membership(a.groupings[0], "records", a.dataset, "member")
        lines.append("stopifnot(all(rowSums(member) <= 1))  # rule I17: a record in two groups")
        lines.append("records$TRT <- factor(apply(member, 1, function(m) colnames(member)[m][1]), "
                     "levels = colnames(member))")
        listed = "c(" + ", ".join(lit(c) for c in ["TRT", *columns]) + ")"
        lines.append(f"d <- records[stats::complete.cases(records[{listed}]), ]")
        return lines

    def ancova(self, method: str) -> str:
        a = self.a
        options = a.options[method]
        factors = [str(f) for f in options["factors"]]
        covariates = [str(c) for c in options["covariates"]]
        y = a.variable
        for column in [y, *covariates]:
            if self.types(a.dataset, column) != "number":
                raise NotCovered(f"the model column {column} is not a number column")
            self.column(a.dataset, column, "records")
        body = self.records()
        body += comment(f"{method}, statement 1: the model records belong to a group and have "
                        f"a value of {', '.join([y, *factors, *covariates])}")
        body += self.model_records([y, *factors, *covariates])
        body += ["", *self.decisions.above([a.id])]
        for f in factors:
            body.append(f"stopifnot(length(unique(d${f})) > 1)  # statement 2: a factor of one "
                        "level would be left out")
        terms = " + ".join([*factors, *covariates])
        source = a.option_sources[method]
        df = options["df"]
        if method == "model.ancova.dose_response":
            if options["model"] != "continuous_dose":
                raise NotCovered("the dose-response test as a linear contrast")
            grouping = a.groupings[0]
            if options["dose"] == "grouping_value":
                if self.types(grouping.dataset, grouping.variable) != "number":
                    raise NotCovered("the dose of a group from a text column")
                where = self.need(grouping.dataset, (grouping.variable,))
                dose = (f"{where}${grouping.variable}[match(d${self.key}, {where}${self.key})]"
                        if grouping.dataset.upper() != a.dataset.upper()
                        else f"d${grouping.variable}")
                body += comment("Statement 2: the dose of a group is the value of "
                                f"{grouping.dataset}.{grouping.variable} (dose grouping_value, "
                                f"{source['dose']})")
            else:
                dose = "as.numeric(d$TRT)"
                body += comment(f"Statement 2: the dose of a group is its rank (dose group_rank, "
                                f"{source['dose']})")
            body.append(f"d$DOSE <- {dose}")
            body += comment("Statement 3: y = mu + b dose + the factors + the covariates; the "
                            "estimate b and the test of b = 0 (the t test of summary.lm, which "
                            "for one term of one degree of freedom is the Type III F test)")
            body.append(f"fit <- stats::lm({y} ~ DOSE" + (f" + {terms}" if terms else "")
                        + ", data = d)")
            body.append("b <- summary(fit)$coefficients[\"DOSE\", ]")
            if df == "residual":
                p = "b[[\"Pr(>|t|)\"]]"
            else:
                p = "2 * stats::pnorm(-abs(b[[\"t value\"]]))"
            values = {"estimate": "b[[\"Estimate\"]]", "p_value": p}
            ops = [op for op in a.operations]
            made = ", ".join(lit(op.id) for op in ops)
            body.append(f"rows <- data.frame(operation_id = c({made}), group1 = {lit('*')}, "
                        f"value = num(c({', '.join(values[op.operation] for op in ops)})))")
            body += ["", *self.footer("rows")]
            return "\n".join(self.preamble([]) + body) + "\n"
        body += comment("Statements 2 and 3: y = mu + tau[group] + the factors + the covariates, "
                        "no interaction, by ordinary least squares")
        body.append(f"fit <- stats::lm({y} ~ TRT" + (f" + {terms}" if terms else "")
                    + ", data = d)")
        level = options.get("confidence_level", 95)
        if method == "model.ancova.lsmeans":
            weights = options["weights"]
            body += comment(f"Statement 4: weights {weights} ({source['weights']}); covariates "
                            "at their mean over the model records; no factor is nested")
            body.append(f"emm <- emmeans::emmeans(fit, ~ TRT, weights = {lit(weights)}, "
                        "nesting = NULL)")
        else:
            reference = str(options["reference"])
            body += comment(f"Statements 2 and 3: each group against {reference} "
                            f"({source['reference']}); not adjusted (statement 5)")
            body.append("emm <- emmeans::emmeans(fit, ~ TRT, nesting = NULL)")
            body.append(f"emm <- emmeans::contrast(emm, method = \"trt.vs.ctrl\", "
                        f"ref = match({lit(reference)}, levels(d$TRT)), adjust = \"none\")")
        if df == "asymptotic":
            body.append("emm <- update(emm, df = Inf)  # df asymptotic: the normal distribution")
        body += comment(f"df {df} ({source['df']}), confidence level {level} "
                        f"({source.get('confidence_level', 'the registry')})")
        tests = "TRUE" if method == "model.ancova.pairwise" else "FALSE"
        body.append(f"s <- as.data.frame(summary(emm, infer = c(TRUE, {tests}), "
                    f"level = {num(level)} / 100))")
        body += self.model_rows(method, reference=options.get("reference"))
        body += ["", *self.footer("rows")]
        return "\n".join(self.preamble(["emmeans"]) + body) + "\n"

    def model_rows(self, method: str, reference: object = None) -> list[str]:
        """One row per group (and per operation) of the summary `s` (rule I18)."""
        a = self.a
        lines = []
        if reference is None:
            lines.append("group <- as.character(s$TRT)")
        else:
            lines.append(f"group <- setdiff(levels(d$TRT), {lit(str(reference))})  # the order "
                         "of emmeans' contrasts")
        parts = []
        for op in a.operations:
            if op.operation not in EMMEANS:
                raise NotCovered(f"the operation {op.operation} of {method}")
            parts.append(f"data.frame(operation_id = {lit(op.id)}, group1 = group, "
                         f"value = num(s[[{lit(EMMEANS[op.operation])}]]))")
        lines.append("rows <- rbind(")
        lines += [f"  {p}{',' if i + 1 < len(parts) else ''}" for i, p in enumerate(parts)]
        lines.append(")")
        return lines

    def mmrm(self, method: str) -> str:
        a = self.a
        options = a.options[method]
        factors = [str(f) for f in options["factors"]]
        covariates = [str(c) for c in options["covariates"]]
        visit = [str(v) for v in options["visit"]]
        by_visit = [str(v) for v in options["by_visit"]]
        if len(visit) != 1 or self.types(a.dataset, visit[0]) != "number":
            raise NotCovered("a mixed model needs exactly one visit column of numbers")
        y = a.variable
        for column in [y, *covariates, visit[0]]:
            if self.types(a.dataset, column) != "number":
                raise NotCovered(f"the model column {column} is not a number column")
            self.column(a.dataset, column, "records")
        body = self.records()
        body += comment(f"{method}, statement 1: the model records belong to a group and have a "
                        f"value of {', '.join([y, visit[0], self.key, *factors, *covariates])}")
        body += self.model_records([y, visit[0], self.key, *factors, *covariates])
        body.append(f"stopifnot(!anyDuplicated(d[c({lit(self.key)}, {lit(visit[0])})]))  "
                    "# two records of a subject at a visit")
        body += comment("Statement 2: the visits in increasing order; the last is the last of "
                        "them")
        body.append(f"d$VISIT <- factor(d${visit[0]}, levels = sort(unique(d${visit[0]})))")
        body.append(f"d${self.key} <- factor(d${self.key})")
        body += ["", *self.decisions.above([a.id])]
        source = a.option_sources[method]
        terms = ["TRT * VISIT" if options["treatment_by_visit"] == "yes" else "TRT + VISIT"]
        for column in [*factors, *covariates]:
            terms.append(f"{column} * VISIT" if column in by_visit else column)
        covariance = {"unstructured": "us", "toeplitz": "toep"}[str(options["covariance"])]
        for f in factors:
            body.append(f"stopifnot(length(unique(d${f})) > 1)  # statement 3: a factor of one "
                        "level would be left out")
        body += comment(f"Statements 3 to 5: {' + '.join(terms)} (treatment_by_visit "
                        f"{options['treatment_by_visit']}, by_visit {', '.join(by_visit) or 'none'}"
                        f"); covariance {options['covariance']} ({source['covariance']}), by "
                        "REML; the optimizer nlminb reaches the maximum where mmrm's default "
                        "stops before it (statement 5: a fit that does not reach it)")
        df = str(options["df"])
        if df == "kenward_roger_linear":
            control = ("mmrm::mmrm_control(method = \"Kenward-Roger\", "
                       "vcov = \"Kenward-Roger-Linear\", optimizer = \"nlminb\")")
        else:
            control = "mmrm::mmrm_control(method = \"Satterthwaite\", optimizer = \"nlminb\")"
        body += comment(f"Statements 7 and 8: df {df} ({source['df']})")
        body.append(f"fit <- mmrm::mmrm({y} ~ {' + '.join(terms)} + {covariance}(VISIT | "
                    f"{self.key}), data = d, reml = TRUE, control = {control})")
        at = str(options["at"])
        body += comment(f"Statement 6: at {at} ({source['at']}); covariates at their mean, "
                        "factors averaged with equal weights")
        if at == "last":
            body.append("emm <- emmeans::emmeans(fit, ~ TRT, at = list(VISIT = "
                        "levels(d$VISIT)[nlevels(d$VISIT)]), weights = \"equal\")")
        else:
            body.append("emm <- emmeans::emmeans(fit, ~ TRT, weights = \"equal\")")
        reference = options.get("reference")
        if method == "model.mmrm.pairwise":
            body += comment(f"Each group against {reference} ({source['reference']}); not "
                            "adjusted")
            body.append(f"emm <- emmeans::contrast(emm, method = \"trt.vs.ctrl\", "
                        f"ref = match({lit(str(reference))}, levels(d$TRT)), adjust = \"none\")")
        level = options.get("confidence_level", 95)
        tests = "TRUE" if method == "model.mmrm.pairwise" else "FALSE"
        body.append(f"s <- as.data.frame(summary(emm, infer = c(TRUE, {tests}), "
                    f"level = {num(level)} / 100))")
        body += self.model_rows(method, reference=reference)
        body += ["", *self.footer("rows")]
        return "\n".join(self.preamble(["mmrm", "emmeans"]) + body) + "\n"
