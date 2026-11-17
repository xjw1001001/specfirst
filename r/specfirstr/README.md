# specfirstr

The R result engine (PLAN.md section 7.1, ADR-002). It reads the same ARS
file, the same method registry and the same data as the Python engine in
`src/specfirst/machine/ard.py`, follows the same rules I1 to I15
(`standard/methods/README.md`) and must give the same ARD rows (rule R11).
The model-based methods of real-5 will live here too.

| File | Content |
| --- | --- |
| `run.R` | the command: run a job, or run the method vectors |
| `R/util.R` | text, hashes, JSON lines |
| `R/methods.R` | one function per registry entry |
| `R/engine.R` | the interpreter: where clauses, groupings, cells, tables, rows |
| `R/vectors.R` | the vectors of `tests/methods/` through `R/methods.R` |

```bash
. scripts/env.sh
Rscript --vanilla r/specfirstr/run.R <job.json>                    # written by `specfirst build`
Rscript --vanilla r/specfirstr/run.R --vectors <in.json> <out.json>
```

How it differs from the Python engine, on purpose:

- The arithmetic comes from R's `stats` package: `quantile` types 2 and 7,
  `sd`, `chisq.test`, `fisher.test` for a 2 x 2 table, and the F test of
  `anova(lm())`. The Python methods are written from the definitions. The
  two share no code. One method is the same algorithm on both sides: the
  Fisher test on a table larger than 2 x 2 is summed over every table,
  because `fisher.test` does not follow the registry there
  (`test.fisher.exact`, statement 8). `tests/methods` compares both sums
  with `fisher.test` and with exact fractions.
- It does not read Parquet or YAML: the locked R library has no reader for
  either. `specfirst build` hands it the columns the analyses read as JSON
  (one file per dataset) and the registry as
  `standard/methods/registry.json`. It reports a SHA-256 of every column
  as it read it, and the build compares that with the Parquet data. The
  JSON is read without jsonlite's simplification, which takes the text
  "NA" for a missing value.

Rules of the folder:

- Base R and jsonlite only, loaded from the locked library alone
  (`SPECFIRST_R_LIBS`, lesson 6).
- The code is sourced, not installed as a package: `specfirst doctor` counts
  any package outside `env/r-packages.lock` as drift.
- Text is compared and sorted by code point (`LC_COLLATE` is set to `C`),
  as Python does.
- ASCII only (rule R10).
