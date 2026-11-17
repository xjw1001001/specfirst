# Track read

Result: scorer, harness, reader agent, first scores (PLAN.md section 13.6),
first for the slice "adverse event summary first" (ADR-005).

## Passed

- Nothing yet. Part read-1a is half done: its gate cannot pass before the
  kits of gen-2a are scored (see "Open").

## Open

read-1a, first half (2026-11-17): the scorer exists and has run on a
hand-made study and on the pilot. Evidence: docs/reports/read-1a.md and
docs/reports/read-1a.first-half.gate.log (`specfirst gate read-1a` on a
clone of `e091d15`: 13 of 14 checks pass; "kits of gen-2a" fails, by
design). CI is green on that commit. No review yet: rule R7 applies when the gate passes.

What exists (`src/specfirst/score/`; each module says what it does):

- `reading`: the reading score of section 9.1, by class and by unit.
- `build`: the four scores of ADR-005, decision 4, each with its
  denominator, for the visible data and for the twin.
- `attribute`: section 9.4. The layer and the decision that own a wrong
  cell, and every attribution to a decision run by building again.
- `candidate`, `display0`: a decision vector built on a dataset. The grid
  comes from a stand-in (below).
- `scorer`: a candidate on a case; arm S and arm C; stage C (the chain) and
  stage T (table decisions on gold ADaM).
- `defects`: the planted defects of section 9.5 for the slice.
- `hand`: the study HAND01 (7 and 9 subjects) with its table by hand. It
  separates 12 of the 21 decisions of the slice on one of its two
  datasets; the other nine are marked `unseparated`, found by mutation
  (lesson 43). Its twin is no superset of its visible data: one decision
  (`trt.end.source`) is shown by the visible data only.
- `pilot`: arm S at stage T on the reference ADaM of CDISCPILOT01.
- `gate`, `command`: `specfirst gate read-1a`, `specfirst score ...`.

What waits for gen-2a (it is on `main` when `git fetch` shows
`docs/reports/gen-2a.review.md` on `origin/main`). Do these in order:

1. Merge `main` into `track/read` with Windows git; `make install` once;
   `specfirst doctor`. Expect conflicts in `src/specfirst/gates.py`,
   `src/specfirst/cli.py`, `CLAUDE.md` (line 14, one line: the file must
   stay under 60) and `docs/lessons.md` (rows 40 to 42 here: renumber the
   later ones).
2. Build the candidate with the builder that builds the kits' gold. The
   seam is `specfirst.score.candidate.Machine._adam` and `_tables`; a
   `Build` is what the rest of the scorer reads. `display0` then goes, or
   stays for HAND01 only if the two builders give the same grid there. The
   test of the swap is arm C: on every kit the gold decisions must build
   the kit's own gold grids, cell for cell.
3. A `scorer.Case` per kit (gold decision records, the two datasets, the
   arms, the documents if any) and `specfirst score kit <kit>`.
4. `specfirst.score.gate.kits`: arm C at 100% on every kit, and the planted
   defects on the kits. Decide there where each planted decision must show:
   a kit's own identifiability matrix says which pairs its twin separates,
   and docs/state/gen.md lists pairs that cancel in some twins. A planted
   decision that a twin cannot show is reported by the scorer as `silent`;
   it is not a failure of the scorer.
5. An ADR for the choices listed under "For the owner" (the next free
   number), the report with the runs on the kits, the fresh-context review,
   `scripts/clean_clone_gate.sh read-1a`, the merge.

Two small things to do with step 2, found after the gate run and left so
that the code of the log is the code of the branch:

- `Machine.build` knows a dataset by its name. Stage T names its data
  `<name>/T` whatever the gold vector is; two cases with one data name and
  different gold would share a build. Put a digest of the gold vector into
  the name.
- A hook is known by its name too: two hooks need two names.

For the owner (choices made where the plan is silent; docs/reports/read-1a.md
says each in full). They stand unless the owner objects:

- Arm S builds nothing on the chain. `ae.related.values` has no house
  default in `catalog@1`, ADAE needs it, and ADR-005 says that what cannot
  be built without a decision counts as not produced. So "R against S" on
  the chain compares with zero in every study, and arm S says something at
  stage T only. A default for that decision, or an ADAE that builds without
  it, is a new catalog version or a change of the house standard (the std
  track); the scorer needs no change for either.
- What a row and a column are when two tables are compared: a row is its
  section and label, a column its header text; position counts for the
  strict score only.
- Attribution compares from the far end: analysis data first, then the
  analysis, the results, the layout. A cell has one owner. A second wrong
  decision behind the same cell shows when the first is right; the report
  lists it as "behind another owner" with the cells it changes alone.
- Three of the twelve planted defects of section 9.5 do not apply to a
  table of counts and percents (quantile, p-value rounded twice, baseline).
  Two are planted as the nearest thing the slice has: "an unstable sort" as
  the other order of the treatment columns, "a frozen site list" as the
  list of related causality values cut down to those in the visible data.
  Three are planted in the build, not in a decision (arms exchanged, wrong
  denominator, missing column): no decision of the slice does these.
- The pilot: which analysis of CDISC's example is which row of the house
  table (five of eight; `ROWS` in `specfirst.score.pilot`). Titles,
  footnotes and the header of the row labels are not compared.
- Not done in this part: the three layers of ADaM scoring of section 9.3
  (they need all four families), the cost dimension (read-2a), natural-form
  documents (the anchors of gen-3a).

The grid stand-in. The compiler writes layout draft 0 and the grid builder
reads layout version 0, which has no total column, no rule for a count of
zero and one rounding rule (ADR-003, docs/state/real.md). `display0` shows a
compiled table of counts and percents as a grid of schema version 0 and
takes a missing ARD row of an arm as a count of zero (finding F2 of the
review of real-3a). It is for the scorer's own builds only.

For other tracks:

- std: `ae.related.values` without a default (above). The pilot shows
  three rows that `tfl.ae.summary.rows` cannot name: related serious
  events, related events leading to death, events leading to dose
  modification (ADR-005, "For the owner", item 3).
- std, gen: the 22 decisions of the slice do not compile alone.
  `date.studyday.origin` writes into ADVS, so ADVS needs every decision of
  mod-bds-visits, and ADSL needs those of mod-demographics (lesson 42).
- real: the percent of 100 is shown as "( 100.0)" under the pattern
  "( XX.X)", one character wider than every other cell (ADR-003 says the
  registry chose not to cut it).

## Next

- Finish read-1a on the kits of gen-2a (the five steps above).
- Then read-2a (needs read-1a and gen-3a) and the report
  docs/reports/slice-ae-summary.md. It is not a delivery.
- Then the rest of read-1 Scorer (needs real-3 for fixtures, then gen-2),
  read-2 (needs gen-2) and read-3 (D3, node N3).

How to run things:

- `specfirst score hand --arm C` (or `--arm S`, `--stage T`,
  `--decisions FILE`), `specfirst score defects`, `specfirst score pilot`.
  The first two need neither the fetch cache nor R; a run takes seconds.
- A gate of a commit runs on a clone (lesson 28). On this machine:
  `git clone --no-local /mnt/d/trial_work/specfirst/.git <clone>` in the
  Linux file system, check out the commit, source `scripts/env.sh` of the
  worktree, `cd` into the clone, and
  `flock /run/lock/specfirst-heavy.lock taskset -c 0-3 env
  PYTHONPATH=<clone>/src python -m specfirst gate read-1a --clean`.
- The WSL machine is shared: wrap a gate, a test suite or a build of kits in
  that lock, and expect to wait for it (20 minutes on 2026-11-17).

## Handed over by base-0

- The planted-defect pattern of rule R5 is in use already:
  `tests/unit/test_evidence_checks.py` and the invalid examples in
  `standard/schemas/examples/`.
