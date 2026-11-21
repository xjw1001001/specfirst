# Issue #29 A standalone recomputation script per analysis: report

Date: 2026-11-21. Branch: `track/real`. Issue #29 of `xjw1001001/specfirst`:
"[review] A generated, standalone recomputation script per analysis, so a
statistician can rerun each number without the engine". The design was
sent to the owner through the base session and accepted as sent, with the
three recommendations (ADR-021, "The owner's answers"). Decisions:
docs/decisions/ADR-021.md.

## Verdict

(filled in after the gate)

## What the issue asks for, and where it stands

| The issue asks | Where |
| --- | --- |
| One script per analysis, R or Python, about 10 to 40 lines, from the ARS analysis and its decisions | `specfirst recompute <kit>`, `src/specfirst/recompute/` (reading, pywrite, rwrite, generate); 69 scripts, 42 Python and 27 R (section "The scripts") |
| The analysis set filter, the record filter, the grouping, the statistic; for a model or test, the method with its registry options | the steps of every script, in that order (ADR-021, decision 3) |
| No part of the specfirst engine; base R or Python and standard method packages | the static check, the sealed run, the generator's imports (section "No part of the engine") |
| Written to be read: one step per line group, the decision sentence above each step | the comments of every script (section "The scripts") |
| Run on the reference ADaM, compared with the ARD at full precision | the sealed run on copies of the pinned reference ADaM; `compare.py` (section "The comparison") |
| reproduced, differs (with the cells), not covered (with the reason) | report.json and report.txt, one line per analysis (section "The gate") |
| Exported for a reviewer's own session | `build/recompute/<kit>/bundle/`, `--export DIR`; the gate runs it again by its run_all.sh (section "The export") |
| Acceptance: the tables already reproduced (E24 to E26), a script per analysis that reproduces the ARD | 69 of 69 analyses of the kit's three reporting events; E24 and E25 through CDISC's example; E26 not built (ADR-021, decision 2) |
| Acceptance: a planted break in the engine, one swapped option, caught | the ANCOVA LS-means weights in the R engine; also the quartiles and CMH in both engines (section "Planted breaks") |

(the rest is filled in after the gate)
