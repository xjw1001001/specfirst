# Issue #27 AE by organ class and term: independent review

Reviewed: the fix of issue #27 of `xjw1001001/specfirst` on branch
`track/real`, as it is at `5313741`.

- The diff `3fbe162..5313741` without the merge of `main` = `5b8ff85`
  (commit `c7f09a0`). `git diff --stat e00bbb7 c7f09a0` names README.md and
  docs/decisions/ADR-012.md only; `git diff --stat c7f09a0 5313741` names
  ADR-011.md and docs/reports/issue-27.md only. The work is two commits:
  `e00bbb7` (code, test, CLAUDE.md, lesson 61; 6 files, 195 insertions, 14
  deletions) and `5313741` (ADR-011 and the report).
- The documents the findings quote, as committed at `5313741`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `docs/reports/issue-27.md` | 414 | `84175ecfecda16218bb18978d06a63c3e634a49f4f4a12e925236454942f2c86` |
  | `docs/decisions/ADR-011.md` | 149 | `e0c7ebf5883891a9bd72ca994da9e4cf33d29d42e04638fd90fa7143e87331fd` |
  | `tests/unit/test_soc_pt_pairs.py` | 165 | `fa6b6a0a1c7ba0913870c6d5550ad130e79a3030de39d60ed8d456ab0273ebeb` |
  | `src/specfirst/gen/gold.py` | 611 | `4451d759243b9d071c4850c8eb28558a30a8f0b5d2c95d2d9ab3fdd3278bd28d` |

Date: 2026-11-18.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
tracked file, made no commit, and wrote this file only. Nothing was
pushed, posted, labelled or closed; no package was installed; nothing was
written into the fetch cache.

## Outcome

No finding blocks. Every requirement of the brief holds in the reviewer's
own runs:

- The fix is correct and complete for the goal. The analysis by term of
  `tfl-ae-soc-pt` gives arms x the pairs of organ class and term that
  occur, with its total column and the analysis by organ class; every count
  and every percent of these four analyses equals the reviewer's own count
  on the issue's data at both sizes (R1, R2). Nothing else in `src/`
  relies on the term groupings having listed groups (see "What was read").
- The criterion "list a data-driven grouping only when it is on ADSL"
  holds for all four house templates. On the base vector, which compiles
  all four outputs, the listing before and after the fix differs in
  `Grp_AESOC` and `Grp_AEDECOD` only, and every ARD row of every other
  analysis has the same ID before and after (R3). Generated kits 1 to 4 of
  the seed `gen-2a` are the same 511 files before and after, with the
  hashes the report prints (R6). CDISCPILOT01 does not go through the
  changed function.
- The vector tests what the issue asks, and catches the defect: on
  `3fbe162` the final test file fails 4 of 4, the R test included (R5); on
  `e00bbb7` it passes 4 of 4 (R1). It also fails on the opposite defect,
  where nothing is listed (R4).
- The R11 evidence is real: both engines give the same 1,772 rows on the
  larger case, 0 disagree (R1).
- The numbers of the report and of ADR-011 match their commands; the
  reviewer's runs give the same counts and the same kit hashes. A few
  sentences say more than a run shows (F3); none of them is a number that
  matters.
- No rule of PLAN.md section 2 is broken. Nothing under `PLAN.md`,
  `standard/`, `env/`, `r/` or `src/specfirst/machine/` changed (R8).

Owed before the merge, by the merge rule and not by this review: the four
clean-clone gates that had not finished when this was written, and the
sections of the report that are placeholders for them (F2).

## What was read

`CLAUDE.md`; PLAN.md section 2 (2.1 to 2.4) and 13.3; rules I1 to I15 of
`standard/methods/README.md`; ADR-002 (decision 4), ADR-007 (decision 1 and
"For the owner"), ADR-011; `docs/reports/issue-27.md`; lesson 61; the
issue's text (`gh issue view 27 --json body`, read only); the four ARS and
the four layout templates of `standard/houses/open-default@1/`, `common.yaml`
and `STANDARD.md` (the total column); the catalog entries
`tfl.ae.socpt.threshold` and `tfl.ae.socpt.counts`; in full
`src/specfirst/gen/gold.py`, `gen/display.py` (the part that builds
columns), `score/candidate.py`; `machine/ard.py` (groupings, cells, rule
I15, `run`), `cells` and `members` of `r/specfirstr/R/engine.R`,
`results.agreement`, the problems `ars.index` reports for groupings,
`score/attribute.py` (`_reaches`), `gen/decisions.py` (`vector`),
`score/pilot.py` (`standard_vector`), `score/hand.py` (`STATED`);
`docs/state/real.md` (the open layout kinds).

Who relies on listed groups. `resolve_groupings` is called by
`gen.gold.show` (the gold of a generated kit and `Workbench`),
`score.candidate.Machine._tables` (every build of the scorer) and the new
test; `machine/build.py` (CDISCPILOT01) does not call it. Of what these
paths do next: `gen.display` needs a listed column grouping, and every
column grouping of the house is the treatment grouping on ADSL;
`Build.groups` is read by `attribute._reaches`, which skips a group without
a group ID, and a data-driven value is part of the ARD ID, so a changed
value is seen as a changed row; `results.with_results` and the ARD writer
handle `groupValue`; `ars.index` refuses a data-driven grouping without a
dataset, before `grouping["groupingDataset"]` is read. Which builds can
contain the table by term: generated kits state every family but the
adverse event summary "not included" (`gen.decisions.vector`); HAND01
states it not included (`score.hand.STATED`); the scorer's pilot leaves out
the other three families (`score.pilot.standard_vector`); a candidate
vector takes gold values outside its scope (`candidate.vector`). So no
current build has a data-driven grouping outside ADSL, and no current
result changes.

## What was run

All Linux commands ran in Ubuntu 24.04 under WSL2 as root, from script
files, after the `scripts/env.sh` of the worktree, with
`PYTHONDONTWRITEBYTECODE=1`, in clones made with `git clone --quiet
--no-local /mnt/d/trial_work/specfirst/.git` into `<scratch>` =
`/root/scratch-review-issue27`: `before` = `3fbe162`, `after` = `e00bbb7`,
`head` = `5313741`, each with `PYTHONPATH=<clone>/src` and run from inside
the clone. R1 to R6 ran in one acquisition of `flock
/run/lock/specfirst-heavy.lock`, under `taskset -c 0-3`. The reviewer's
scripts are kept outside the repository. Python 3.12.3, R 4.6.2.

| # | What | Result |
| --- | --- | --- |
| R1 | the test file on `after`, all four tests | 4 passed in 2.99 s; 150 and 600 counts; 1,772 rows in both engines, 0 disagree |
| R2 | the reviewer's own recount of counts and percents | 240 and 880 cells, 0 wrong or missing, 0 not expected |
| R3 | `resolve_groupings` and the Python engine on all four house outputs, before and after | only the two term groupings differ; only the IDs of the four analyses by organ class or term change |
| R4 | planted: nothing is listed | 3 of 3 Python tests fail |
| R5 | the final test file on `before`, all four tests | 4 failed in 239.78 s; 1,500 and 12,000 counts |
| R6 | kits 1 to 4 of the seed `gen-2a`, after and before | identical, 511 files each; the report's hashes |
| R7 | CDISC's two ARS examples and the ARS model at the pin | as ADR-011 and the report say |
| R8 | scope, ASCII, length of CLAUDE.md, private data | nothing outside the track; 0 non-ASCII bytes; 59 lines; no user path, no token |
| R9 | the executor's gates on `c7f09a0` | real-2 PASS; the other four not seen |

### R1 After the fix

```text
$ cd <scratch>/after && python -m pytest tests/unit/test_soc_pt_pairs.py -s -q -p no:cacheprovider
300 records, 10 SOCs x 50 PTs, 50 SOC/PT pairs occur: An_AESOCPT_Pt has 150 count results; build 0.2 s
1500 records, 20 SOCs x 200 PTs, 200 SOC/PT pairs occur: An_AESOCPT_Pt has 600 count results; build 0.3 s
engines: 1772 results in both, 0 disagree; largest relative difference 0.0e+00 (allowed 1e-09)
4 passed in 2.99s
exit 0
```

`results.agreement` reports a row that only one engine has as a
disagreement, so "0 disagree" covers the set of rows as well as the values.
1,772 = 6 + 2 + 3 + 1 + 1,200 + 400 + 120 + 40, as the report adds it.

### R2 The reviewer's own recount

A script of the reviewer makes the issue's data again (its recipe, seed 1),
builds them with `Machine.build` of `after` as the issue's repro does, and
holds every count and percent row of `An_AESOCPT_Pt`, `_Pt_Tot`, `_Soc` and
`_Soc_Tot` against counts it makes itself (a percent against n / N x 100,
N = 100 per arm and 300 in the total column, which pools all arms in the
house default):

```text
10x5: pairs 50, socs 10; cells expected 240, found 240; wrong or missing 0; not expected 0; ID shapes {('id', 'value', 'value'): 400, ('id', 'value'): 80}
   example ['ard:An_AESOCPT_Pt/Mth_CatSumm_n/Grp_TRT01A_1/=SOC%2000/=PT%2000-00'] not produced {'Out_AESOCPT': "display: analysis 'An_AESOCPT_Soc' is grouped by ['Grp_TRT01A', 'Grp_AESOC'], its column by Grp_TRT01A"}
20x10: pairs 200, socs 20; cells expected 880, found 880; wrong or missing 0; not expected 0; ID shapes {('id', 'value', 'value'): 1600, ('id', 'value'): 160}
```

240 = 150 + 50 + 30 + 10 and 880 = 600 + 200 + 60 + 20 cells, each with a
count and a percent. Treatment is a listed group, organ class and term are
values, as ADR-011 says. The output builds no grid, before and after: its
layout (`nesting`) is real-4's.

### R3 Every house template, before and after

A script of the reviewer compiles the base vector of the catalog
(`checks.base_vector`, all four outputs), makes small invented ADSL, ADAE
and ADVS tables for every column the compiled event reads (36 subjects, 40
adverse event records on 4 organ classes x 3 terms), calls
`gold.resolve_groupings` and then the Python engine, once with the code of
`before` and once with that of `after`, and compares:

```text
families ['tfl-demographics', 'tfl-ae-summary', 'tfl-ae-soc-pt', 'tfl-vitals-by-visit'] same: True
compiled groupings (dataset, dataDriven): {'Grp_AEDECOD': ['ADAE', True], 'Grp_AESOC': ['ADAE', True], 'Grp_AGEGR1': ['ADSL', True], 'Grp_ETHNIC': ['ADSL', True], 'Grp_RACEGR1': ['ADSL', True], 'Grp_SEX': ['ADSL', True], 'Grp_TRT01A': ['ADSL', True], 'Grp_TRT01P': ['ADSL', True], 'Grp_Total_AESOCPT': ['ADSL', False], 'Grp_Total_AESUM': ['ADSL', False], 'Grp_Total_DM': ['ADSL', False], 'Grp_Total_VS': ['ADSL', False], 'Grp_VS_AVISIT': ['ADVS', False], 'Grp_VS_PARAMCD': ['ADVS', False]}
compiled same: True
groupings that differ after the listing: ['Grp_AEDECOD', 'Grp_AESOC']
ARD rows: before 1248 after 944 common 832
only before, by analysis: {'An_AESOCPT_Pt': 288, 'An_AESOCPT_Soc': 24, 'An_AESOCPT_Pt_Tot': 96, 'An_AESOCPT_Soc_Tot': 8}
only after, by analysis:  {'An_AESOCPT_Pt': 60, 'An_AESOCPT_Pt_Tot': 20, 'An_AESOCPT_Soc_Tot': 8, 'An_AESOCPT_Soc': 24}
analyses with a changed ID: ['An_AESOCPT_Pt', 'An_AESOCPT_Pt_Tot', 'An_AESOCPT_Soc', 'An_AESOCPT_Soc_Tot']
rows of other analyses equal: True
```

So the data-driven groupings of the house are on ADSL except the two term
groupings; the categorical rows of demographics (`Grp_SEX` and the others)
stay listed, as ADR-011 decision 2 says; and the IDs of every result of the
demographics table, the adverse event summary, the vital signs table and
the first two analyses of the table by term are the same before and after.

### R4 A planted defect: nothing listed

A copy of `after` with `SUBJECT_DATASET = "NONE"` in `gen/gold.py`, so that
the treatment grouping stays data-driven too:

```text
$ python -m pytest tests/unit/test_soc_pt_pairs.py -q -p no:cacheprovider -k 'not r_engine'
E       AssertionError: assert 130 == (3 * 50)
E       AssertionError: assert 549 == (3 * 200)
E       AssertionError: assert 'Grp_TRT01A' in {'Grp_Total_AESOCPT'}
3 failed, 1 deselected in 1.14s
exit 1
```

An arm without a record of a pair then has no count, not a zero; the vector
sees it.

### R5 Before the fix, with the final test file

The test file of `e00bbb7` copied into the clone of `3fbe162` (and removed
again afterwards):

```text
$ cd <scratch>/before && python -m pytest tests/unit/test_soc_pt_pairs.py -s -q -p no:cacheprovider
300 records, 10 SOCs x 50 PTs, 50 SOC/PT pairs occur: An_AESOCPT_Pt has 1500 count results; build 1.1 s
1500 records, 20 SOCs x 200 PTs, 200 SOC/PT pairs occur: An_AESOCPT_Pt has 12000 count results; build 63.5 s
E       AssertionError: assert 1500 == (3 * 50)
E       AssertionError: assert 12000 == (3 * 200)
E       AssertionError: assert not ({'Grp_AEDECOD', 'Grp_AESOC', 'Grp_TRT01A', 'Grp_Total_AESOCPT'} & {'Grp_AEDECOD', 'Grp_AESOC'})
E       AssertionError: assert 12000 == (3 * 200)
FAILED tests/unit/test_soc_pt_pairs.py::test_the_term_counts_are_arms_times_the_pairs_that_occur[10x5]
FAILED tests/unit/test_soc_pt_pairs.py::test_the_term_counts_are_arms_times_the_pairs_that_occur[20x10]
FAILED tests/unit/test_soc_pt_pairs.py::test_population_groupings_are_listed_and_record_groupings_are_not
FAILED tests/unit/test_soc_pt_pairs.py::test_the_r_engine_gives_the_same_rows_on_the_pairs
4 failed in 239.78s (0:03:59)
exit 1
```

The R test fails on its count, after its assertion that the two engines
agree has passed: before the fix both engines gave the same 12,000 crossed
counts. The counts are the issue's and the report's; the times are close to
the report's (65.5 s and 65.7 s there).

### R6 Generated kits

```text
$ python -m specfirst gen kits --out <scratch>/kits-after --count 4 --seed gen-2a     # in the clone of e00bbb7
after exit 0 after 95 s
kit 1 of the set: sfpbt5zj, train, 127 files; 14 of 22 decisions separated on the twin
kit 2 of the set: sfmyncmq, train, 127 files; 15 of 22 decisions separated on the twin
kit 3 of the set: sfg5vbvq, train, 126 files; 15 of 21 decisions separated on the twin
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin
$ python -m specfirst gen kits --out <scratch>/kits-before --count 4 --seed gen-2a    # in the clone of 3fbe162
before exit 0 after 96 s
[the same four lines]
$ diff -r kits-before kits-after
kits: identical
511
511
947f40b73a1078be6b299753315e83f828794bdd88e8366a1c8ecc2addb4f0bd  kits-after/kit-001/kit.yaml
7602f342569f61f46feca20a47625beec1ffa56ba71afde2f33274ff50f1f6af  kits-after/kit-002/kit.yaml
a91624ae4b2bca1b13ce40d0bd94c22119ca5389c04f7b0b11935f586337e218  kits-after/kit-003/kit.yaml
e23d3a9099492e0e6978b6a107fc3fb6648dafdc0e9f5de8334e9eeb0e95bd18  kits-after/kit-004/kit.yaml
[the same four hashes for kits-before]
```

These are the hashes of the report. The diff touches nothing a task folder
of read-2a holds (catalog, method registry, schemas, skills), and the kit is
the same bytes, so the report's statement on read-2a holds.

### R7 CDISC's examples and the ARS model

Read only, in the fetch cache; the pin of `ars` is
`2c9b4b68724386e8f91dc576724855af7fafac65`. A script of the reviewer lists
every grouping of the two examples and the analyses that use a data-driven
one:

```text
== Common Safety Displays.json
  AnlsGrouping_01_Trt  ADSL.TRT01A dataDriven=False groups=3
  [Sex, AgeGp, Race, Ethnic on ADSL: defined, 2, 2, 9, 2 groups]
  AnlsGrouping_06_Soc  ADAE.AESOC dataDriven=True groups=0
  AnlsGrouping_07_Pt   ADAE.AEDECOD dataDriven=True groups=0
  [Param, Visit on ADVS: defined, 4 and 11 groups]
  analysis An07_09_Soc_Summ_ByTrt [...] per op {'Mth01_CatVar_Summ_ByGrp_1_n': 69, 'Mth01_CatVar_Summ_ByGrp_2_pct': 69} combos 23 arms 3
  analysis An07_10_SocPt_Summ_ByTrt [...] per op {'Mth01_CatVar_Summ_ByGrp_1_n': 690, 'Mth01_CatVar_Summ_ByGrp_2_pct': 690} combos 230 arms 3
== FDA Standard Safety Tables and Figures.json
  [six groupings, all on ADSL, all defined: 3, 2, 2, 3, 5, 2 groups]
```

In `model/ars_ldm.yaml` a `GroupingFactor` has the slots `id`,
`groupingDataset`, `groupingVariable`, `dataDriven`, `groups`; an
`OrderedGroupingFactor` has `order`, `groupingId`, `resultsByGroup`. The
words "nest" and "hierarch" occur only at `NestedList` and `LevelOrder` and
the slot `level`; "parent" only for operations and analyses; "depend" not at
all. The model has no nested or dependent grouping, as ADR-011 says, and the
example models the table as the house does: 690 counts = 3 arms x 230
pairs, every arm with every pair.

### R8 Scope and files

```text
$ git diff --name-only 3fbe162 5313741 -- PLAN.md standard env r src/specfirst/machine .github scripts Makefile pyproject.toml | wc -l
0
$ wc -l < CLAUDE.md
59
[non-ASCII bytes in the eight files of the diff (code, test, CLAUDE.md, lessons, ADR-011, report): 0 each]
[a search of the report and ADR-011 for a Windows user folder, a token or a password]
none
```

### R9 The gates of the executor

`build/gates/real-2/clean-clone.log` of the worktree (not committed) is the
gate real-2 on a clean clone of `c7f09a0`: "1059 passed, 23 deselected",
every check PASS, "GATE real-2: PASS". The gates real-3a, gen-2a, gen-3a and
read-1a on `c7f09a0` had not written a log when this review was written.
The reviewer did not run a gate.

## Findings

### F1 (not blocking; closed by R5) The final test file was not run with R before the fix

The report's first "before" run is of the test file "as first written
(without the total column)", 4 of 4 failed; the final file was run before
the fix without R ("3 failed, 1 deselected"), and the report says "the R
test is unchanged from the run above". Nothing in the repository shows the
first version of the file, so the sentence could not be checked as it
stands. R5 runs the final file, R test included, on `3fbe162`: 4 of 4 fail,
the R test on its count. Rule R5 is met.

### F2 (not blocking for this review; owed before the merge) Gates, report and state file

The report's sections "Gates on clean clones" and "Review" say "running" and
"not yet done". By the merge rule (CLAUDE.md, PLAN.md section 2.4) the five
gates must pass, and by rule R8 the report must show them with their output,
before `track/real` merges. At the time of this review real-2 had passed on
`c7f09a0` (R9) and the other four had not finished. This verdict does not
stand in for them; it covers the code at `e00bbb7` and the claims of
`5313741`, and a gate log or report text added later changes no code it
covers.

`docs/state/real.md`, the handover of the track, does not mention issue
#27 or ADR-011. The issue cites its lines 223 to 226 (the open layout kind
"data-driven and nested for organ class and term"). It should say that the
results of the table by term are now arms x the pairs that occur, and that
the rows of the grid are still real-4's.

### F3 (not blocking) Sentences that say more than a run shows

None of these is a number that matters, and the numbers next to them are
the outputs shown.

- Timing. The report explains the two "before" times of the small case
  (2.0 s and 1.3 s) by "the first build of a run also compiles the
  decisions". After the fix the first build of a run also compiles, and
  takes 0.1 s (the report) or 0.2 s (R1), so compiling does not explain
  0.7 s. ADR-011 then writes "was about 2 s and 65 s"; for the small case
  the issue's repro gave 0.8 s on the machine of the issue and 1.1 s in the
  report's own run of it, and R5 gives 1.1 s. The large case
  (about 65 s, now 0.2 s) is what the issue is about, and it is right.
- ADR-011, consequences: "An organ class or term that occurs on a record
  of the analysis set but on no record of the analysis ... had a row of
  zeros and now has none." This follows from the code (the old listing read
  the values of ADAE in the analysis set, not in the data subset; rule I9
  reads the analysis records) and no current output has the table, but no
  run shows it. It agrees with the catalog: the house default of
  `tfl.ae.socpt.threshold` says "Every preferred term with at least one
  event is shown."
- The report names generated kits and CDISCPILOT01 as what is unchanged,
  but not the scorer's builds of HAND01 and of the pilot (`specfirst score
  hand|pilot`), which do go through `resolve_groupings`. They are unchanged
  too: their vectors include the adverse event summary only (see "What was
  read"), and R3 shows that a grouping on ADSL is listed as before.

### F4 (not blocking; for real-4) The rule is a dataset name, and its limit is wider than the ADR says

`resolve_groupings` lists a data-driven grouping when its dataset is ADSL.
ADR-011 names one limit: a column grouping on another dataset is not
listed, and `gen.display` stops with a message. The same holds for a row
grouping of records whose categories a table shows in full, for example
severity (AESEV) or relationship as rows of an adverse event table: kept
data-driven, a category without a record in the analysis gives no row,
not a row of zeros. No house template has such a grouping today. A
template that needs every category gives the grouping defined groups, as
CDISC's examples do for every grouping but organ class and term (R7);
real-4 should know this when it writes the templates of the 16 tables.

The vector holds the scorer's path (`Machine.build`), not `gen.gold.build`;
both call the same two functions, so the gold of a kit with the table
would give the same results. The analyses of event counts
(`tfl.ae.socpt.counts` = `subjects_and_events`) are grouped the same way and
are not in the vector; nothing asked for them.

## For the owner

Nothing in ADR-011 is the owner's to decide. None of the cases of PLAN.md
section 2.3 applies: no license question; no gate was changed; the public
standard is settled by CDISC's own example, which models the table exactly
as the house does (R7); nothing is published or deleted; nothing under
`standard/`, `PLAN.md` or `standard/schemas/` changed. The decision narrows
decision 1 of ADR-007, which was itself the executor's and stands unless
the owner objects, and it changes code the brief gives the executor.

One thing to know. Item 1 of ADR-007's "For the owner" ("decision 1 or a
change of rule I9: which should stay") stays open, and ADR-011 does not
answer it. Its last paragraph says that either answer must keep the pairs
that occur for groupings of records; that is what rule I9 already says, so
it adds no new condition, but it means the answer will now have to treat
groupings of the subject population and groupings of records differently.

Verdict: SIGNED
