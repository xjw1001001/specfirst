# real-2 Result engines: independent review

Reviewed: work package real-2 of PLAN.md section 13.3, on branch
`track/real`, in one pass.

- The diff `main..track/real`: `main` is
  `2cb4c6300408482afe80daa799214517b23d9b3d`, `track/real` is
  `1e0f164ec986710dd8a291eabce21c0621ba4a44`; 69 files, 7,269 insertions,
  159 deletions. Three commits: `f357e74` (the findings N1 to N7 of the
  review of real-1), `259ab8d` (real-2), `1e0f164` (the merge of `main`
  with std-1).
- Three files that are not committed, as they stood when read:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `docs/reports/real-2.md` | 588 | `4c908b34ea2338711884b1f9296790a9a38ff98d5166082da953beb8f568ec22` |
  | `docs/reports/real-2.gate.log` | 385 | `b8ec16d185eb228e7f503224a650c5cdc00e2f438dca01128d8e3a6d9f50ea6f` |
  | `docs/state/real.md` | 151 | `4aa5e8af4a8f814b23f25af96abbe4ed628d0a2d2f24157342f8b1d8320db09b` |

  The report still held the lines `@@REVIEW_VERDICT@@`, `@@REVIEW_SECTION@@`
  and `@@CI@@`. What replaces them was not reviewed.

Date: 2026-11-11.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. The reviewer changed no
tracked file, made no commit, and wrote this file only. No network was
used, nothing was posted, no package was installed.

## Outcome

No finding blocks. The gate statement of real-2 holds in every check the
reviewer made:

- `specfirst gate real-2` exited 0 in the worktree at `1e0f164`: 15 of 15
  checks. Its output equals the gate part of `docs/reports/real-2.gate.log`
  line for line, apart from 16 lines that must differ (R2).
- Both engines: 3,735 embedded results, 3,711 reproduced as printed, 23 with
  another value, 1 without a result of ours. The reviewer's own recount,
  which uses none of the checking code, gives the same numbers (R4).
- The 25 entries of `kits/cdiscpilot01/gold/exceptions.yaml` are right. The
  22 exchanged values, the two quartile cases and the empty p-value were
  each checked from the pilot ADSL and the example, apart from the checker
  (R4, R6, R9).
- The two engines agree on all 4,238 rows; the largest relative difference
  is 2.4e-13. Defects planted by the reviewer in the code of one engine
  show as disagreements wherever the pilot data can show them (R6).
- P1: the three result files have the same hashes in the clean clone of the
  author, in the worktree and in two builds of the reviewer in other
  folders and under other process settings (R3).

Twelve findings do not block (F1 to F12). The ones with the most weight:
the check of the proofs accepts three kinds of proof that prove nothing
(F2); the registry says R's `fisher.test` uses the tolerance of the
enumeration, and for tables larger than 2 x 2 it does not, so that the two
implementations differ by 5 to 21 percent on six tables the reviewer found
(F3); the Python standard deviation of a cell whose values are all equal
is not always 0, and the engines then disagree (F4); and five statements of
`r/specfirstr/R/util.R` stand, three of them letter for letter, in a file
of siera, where no test looks (F7).

The verdict covers commit `1e0f164` and the three files as read. The commit
that adds the report, the gate log, the state file and this review should
add nothing else, so that the gate evidence of `1e0f164` stands for it. A
fix of a finding changes code: it belongs to a later commit with its own
gate run, as N1 to N7 of real-1 were handled.

## Scope and method

### What was read

- `CLAUDE.md`; PLAN.md "How to use this file", section 2, section 3 (rows E2
  to E5, E11, E12, E27), sections 4.6, 4.8, 7.1 to 7.3, 8, 9.5, 12, 13.3,
  14; `docs/decisions/ADR-002.md`; `standard/methods/README.md`;
  `docs/lessons.md`; `docs/reports/real-1.review.md`.
- Of the diff, in full: `src/specfirst/machine/{registry,methods,ars,ard,
  rengine,results,build}.py`; the changes of `src/specfirst/{gates,kit,cli}.py`
  and of `machine/{graph,compare}.py`; `r/specfirstr/run.R` and
  `R/{util,methods,engine,vectors}.R`; the seven entries of
  `standard/methods/`; the seven vector files, `oracle.py` and
  `test_methods.py` of `tests/methods/`; `tests/defects/test_defects.py`;
  `tests/toy_results.py`; `tests/unit/test_{ard,ars,results,rengine,
  method_functions}.py`; `kits/cdiscpilot01/{kit.yaml,README.md,
  gold/exceptions.yaml}`; `evidence/adr002_siera_trial.{sh,out}`;
  `docs/upstream/ars-issue-common-safety-displays.md`;
  `third_party/SOURCES.md`; the three uncommitted files; the merge commit
  as a combined diff.
- As a diff or in part: `tests/unit/test_{registry,build,kit,gates,graph,
  compare}.py`, `tests/toy_kit.py`, `tests/pilot/test_pilot.py`, the three
  README files of `tests/defects`, `tests/methods` and `r/specfirstr`,
  `scripts/clean_clone_gate.sh`.
- In the fetch cache, read only: siera's `inst/method-library/` (the list of
  templates, `06_fishers_exact/method.json` and `template.R`) and
  `R/readARS.R` lines 618 to 640; the R files of every cached source, by a
  script that compares lines (R9); the two copies of the CSR, as text made
  with poppler 24.02 in the scratch folder and removed again, for the rows
  of Table 14-2.01 that the issue draft cites.
- Not read: anything outside the worktree other than the cache and the
  scratch folder; the owner's copy of the plan that the report names.

### What was run

All Linux commands ran in Ubuntu 24.04 under WSL2 as root, after
`. scripts/env.sh`, with `PYTHONDONTWRITEBYTECODE=1`, from script files
outside the repository. Python 3.12.3, R 4.6.2. `<scratch>` is
`/root/scratch/review-real2`; everything the experiments wrote is there.
R1 to R13 below name the runs of this review; a rule of the plan is
always written out as "rule R11".

Side effects in the worktree, all in the ignored folder `build/`: the
reviewer's gate run replaced `build/gates/real-2/gate.log`, `methods.xml`,
`pilot.xml` and `defects.xml` (copies of the earlier ones are in
`<scratch>/author-gates`), built `build/p1/` again and assembled
`build/kits/cdiscpilot01` again. `build/gates/real-2/clean-clone.log` was
not touched (same hash before and after).

| # | What | Result |
| --- | --- | --- |
| R1 | `specfirst gate real-2` in the worktree | `GATE real-2: PASS`, exit 0, 15 of 15 |
| R2 | the author's gate log against R1; the report's quotes against the log | the same run, line for line; 220 quoted lines, all in the log, in order |
| R3 | two more builds, in other folders and under other settings | 26 files, the same hashes as the clean clone |
| R4 | the reviewer's own recount of the embedded results | 3,735; 3,711; 23; 1; 1; 504: as the gate says |
| R5 | 14 changed entries of the exceptions file | 9 fail as they should; 5 false or empty proofs pass (F2) |
| R6 | defects in the rows, in the Python engine, in the code of the R engine | caught wherever the pilot can show them (below) |
| R7 | both engines on 65 made-up inputs at the edges of rules I1 to I15 | 45 give the same rows; 4 are refused by both; 16 differ or stop in one engine, none in silence (F5) |
| R8 | the methods on the reviewer's inputs: Python, R, exact fractions | agree, except F3 and F4 |
| R9 | hand-over plants; the engine on Pilot 7's own files; the issue draft; clean-room scans | below; F7, F10 |
| R10 | the graph code of `main` and of `track/real` on the pilot | the same 3,975 pairs; 148 edges cite another line |
| R11 | the pinned ARS schema on a damaged example; `specfirst check` on a changed build | 8 of 9 damages found; the changed build is refused |
| R12 | the ARS file std-1 compiles from its base decisions | 44 analyses, no problem, 9 operations bound |
| R13 | `specfirst fetch --verify` before and after; `specfirst doctor`; `git status` | every pin verified, both times; `doctor: ok`; no tracked file changed |

#### R1 The gate

`specfirst gate real-2` in the worktree at `1e0f164`, with the author's
uncommitted files in place. Excerpts:

```text
gate real-2 at commit 1e0f164ec986710dd8a291eabce21c0621ba4a44 (with uncommitted changes)
methods: 7 entries
674 passed, 19 deselected in 232.30s (0:03:52)
Python implementations: 77 cases of 7 methods, 0 differences
R implementations: 60 cases of 6 methods, 0 differences
expected values computed again in exact arithmetic: 60 cases, 0 differences; written by hand: 17 cases (the display rule)
study data in git (E20): 373 maintained files checked, 0 problems
P1 determinism: 26 of 26 files have the same SHA-256 in both builds
TOTAL cells=9119605 mismatched=0
trace: complete
results common-safety-displays, Python engine: 3735 embedded results, 3711 reproduced as printed, 23 with another value, 1 without a result of ours
results common-safety-displays, Python engine: 0 unexplained
results common-safety-displays, R engine: 3735 embedded results, 3711 reproduced as printed, 23 with another value, 1 without a result of ours
results common-safety-displays, R engine: 0 unexplained
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
results: pass
Python engine: 31 analyses on 23 columns of ADAE, ADSL, ADVS: 4238 rows in 0.51 s (the spike: about 3 minutes; the target: under 10 seconds)
low and high dose exchanged: check passes: False; 1836 of 3735 reproduced; 1898 other values, of which 1896 are our value of the other arm
safety set read from EFFFL: check passes: False; 2754 of 3735 reproduced; differences in 28 analyses
quantile definition r7: check passes: False; 3662 of 3735 reproduced as printed, 49 fewer (E4: 49); at the precision of the result pattern 97 new differences: {'Q1': 45, 'Q3': 52}
An07_01_TEAE_Summ_ByTrt without its data subset: check passes: False; new differences 4
R engine alone, low and high dose exchanged: 1930 results disagree
56 passed in 179.91s (0:02:59)
fetch: every pin verified
ASCII check: 373 files checked, 0 with non-ASCII bytes
PASS  unit tests         232.8 s
PASS  P1 determinism      90.3 s
PASS  results              4.9 s
PASS  planted defects    180.5 s
GATE real-2: PASS
```

#### R2 The gate log is the log of this code

The clean clone the log names, `/tmp/specfirst-clean-ZCcz7L/specfirst`, was
gone when the review began: the WSL distribution had stopped while idle and
cleared `/tmp` when it started again. So the log could not be compared with
the clone's own `gate.log`. What could be checked:

```text
cmp docs/reports/real-2.gate.log build/gates/real-2/clean-clone.log   -> identical
gate part of the log: lines 49 to 383 | gate real-2 at commit 1e0f164ec986710dd8a291eabce21c0621ba4a44 (clean)
differing lines against R1 after normalising seconds, folders and progress dots: 16
```

The 16 lines are 8 pairs: `(clean)` against `(with uncommitted changes)`;
the path of Python in the doctor line; pytest's closing lines of the unit
tests and of the planted defects (the time in brackets); 371 against 373
files in the data check and in the ASCII check (the two untracked report
files); and two lines of the summary whose seconds have three digits. All
26 hash lines of P1 are the same in both runs.

The report quotes 220 lines of the log; every one is in the log, in order.
The 16 places marked `[...]` leave out what the report says they leave out
and nothing else.

#### R3 P1 beyond the gate

```text
b1: specfirst build cdiscpilot01 --into <scratch>/b1
b2: cd / && TZ=Asia/Tokyo PYTHONHASHSEED=12345 LC_ALL=C LANG=C specfirst build cdiscpilot01 --into <scratch>/b2-with-a-longer-name/and/depth
build.json equal: True files: 26
gold/ard/common-safety-displays.jsonl   76c528ce523c6a13 76c528ce523c6a13
gold/ard/common-safety-displays.r.jsonl de20ea90cae0946d de20ea90cae0946d
gold/ars/common-safety-displays.json    a3d51da218b6839e a3d51da218b6839e
```

These are the hashes of the clean clone's log. No file of `gold/ard`,
`gold/ars` or `gold/build.json` holds `/root/`, `/mnt/`, `/tmp/`, the name
of the scratch folder or a date. `work/` holds `job.json` with absolute
paths and `meta.json` with seconds; neither is listed in `build.json`, as
the kit README says.

#### R4 The reviewer's recount

A script of the reviewer reads the example, the two ARD files of b1 and the
exceptions file, and compares with its own code (`float`, half a unit of
the last printed decimal, then the decimals of the pattern).

```text
rows: python 4238 R 4238 same keys: True
engines: disagreements 0 largest relative difference 2.40e-13
embedded results: 3735 with an empty raw value: 1
python {'as printed': 3711, 'coarse': 1, 'differ': 23, 'absent': 1}
R      {'as printed': 3711, 'coarse': 1, 'differ': 23, 'absent': 1}
our rows the reference does not list: 504 {...PlacHigh: 21, ...PlacLow: 21, ...PlacHigh: 186, ...PlacLow: 180, An08_02_ChgBl_Summ_ByTrt: 96}
value_of_other_result entries whose embedded value is our value of the other active arm: 22
ADSL subjects: 254 safety: 254 ITT: 254 same subjects in both sets: True
by arm: [86, 84, 84]   Hispanic or Latino by arm: [3, 6, 3]
Xanomeline Low Dose  heights n 84 mean 163.4333333 sorted 41st..45th [162.6, 162.6, 162.6, 162.6, 162.6]
Xanomeline High Dose heights n 84 mean 165.8202381 63rd, 64th [172.7, 173.0] | ages 21st, 22nd [70.0, 71.0]
```

How tightly the 3,711 are compared: 1,079 are whole-number counts and equal
exactly; 427 are 0.0 on our side; for 541 the half unit granted is at most
1e-6 of the value, for 894 between 1e-6 and 1e-3, for 770 more than 1e-3.
The last are values the reference prints with few digits. 400 of our values
differ from the embedded one by more than a relative 1e-6 and are equal
only at what the reference prints. That is the comparison PLAN.md section
4.6 asks for ("at the reference's printed precision"); it is said here so
that the number is read rightly.

#### R6 Planted defects of the reviewer

Judged by `build.judge` and `results.agreement`, the functions the gate
calls, on the rows of b1.

Rows changed after the engines:

| Defect | In one engine | In both |
| --- | --- | --- |
| low and high dose exchanged in one analysis (sex counts; the mean of age; serious events; the minimum of the vital signs) | P2 fails, engines disagree (on 4, 2, 4, 76 values) | P2 fails (4, 3, 4 unexplained; 76 fewer reproduced) |
| the same in `An03_04_Ethnic_Summ_ByTrt` | P2 fails: 8 entries "listed as an exception, but it is reproduced" | the same |
| a row the reference lists is deleted | P2 fails, engines disagree | P2 fails |
| 50 rows the reference does not list are deleted | engines disagree on 50 | nothing fails |
| every one of the 504 unlisted results set to 0.5 | - | nothing fails |
| a count made null; a mean off by a relative 3e-9 | P2 fails, engines disagree | - |
| a mean off by a relative 5e-10 | nothing fails (inside 1e-9) | - |
| a minimum printed as "52" (pattern XX) off by 0.4 | - | nothing fails (inside half a unit) |

Defects in the Python engine (monkey-patched, real data):

```text
C1 denominator always that of the first group (305 values change): P2 passes: False; engines disagree on 305
C3 n of a continuous summary counts missing values too (50 values change): P2 passes: False; engines disagree on 50
C4 count.subjects counts the empty text as a value (0 values change): P2 passes: True; engines disagree on 0
C5 quantiles without averaging (SAS QNTLDEF=3): 69 values change; P2 passes: False; new differences {'Median': 24, 'Q3': 24, 'Q1': 20}; age Q1 high dose now 70.0 (embedded 70)
   embedded Q1, Q3 and medians: 774; that need a class under the SAS default: 2; under QNTLDEF=3: 69
C6 population of a Fisher test = the analysis set, not limited by the data subset: 255 values change; P2 passes: False; engines disagree on 255
   An07_01_TEAE_Comp_ByTrt_PlacLow embedded '0.0065331294' I13: 0.006533129364777608 set only: 1.5005196151289333e-44
```

C6 shows that all five Fisher p-values the example embeds with a value
separate rule I13 from the nearest other reading. C5 is used in F9.

Defects in the R engine's code (a patched copy of `r/specfirstr` under
`<scratch>`, run by `rengine.run` on the pilot), against the unchanged
Python rows:

| Defect in R | Engines disagree on | P2 for the R rows |
| --- | --- | --- |
| unchanged copy | 0 | passes |
| the groups of a defined grouping get each other's IDs | 3,252 | fails |
| the population of a Fisher test ignores the data subset | 255 | fails |
| a condition on another dataset is ignored (rule I4) | the R engine stops: "218 subjects with a record and 86 in the population" | - |
| sd with the denominator n | 258 | fails |
| quantile type 7 whatever the option says | 106 | fails |
| Welch's test in place of the analysis of variance | 2 | fails |
| count.subjects counts the empty text | 0 | passes |
| NE is false for a missing value | 0 | passes |
| chi-square with continuity correction | 0 | passes |
| Fisher test simulated (B = 2000) | 0 | passes |

The last four are what the pilot data cannot show, beyond what the report
lists: no analysis variable of a count is missing; no column under NE has a
missing value; every chi-square table is larger than 2 x 2, where R applies
no correction; every Fisher table is 2 x 2, where R never simulates. For
these four the vectors and unit tests are the only check (F11). On the
vectors a simulated or one-sided Fisher test in R fails 6 cases each, and
ties left out in Python fail 13 of 14.

#### R7 Both engines at the edges of rules I1 to I15

65 variants of the made-up study of `tests/toy_results.py`, each run by
both engines and compared with `results.agreement`. In 45 the two give the
same rows; 4 are refused by both (a number column compared with `61,0` or
with the empty text, an analysis set on two datasets for a Fisher test, an
infinite value); 16 are in F5. They agree on: every
comparator with a missing value, on text and on numbers (rule I3); text
order with mixed case and a letter outside ASCII; a date and a Boolean
column; NOT of a condition on another dataset and a nested AND, OR, NOT
over two datasets (I4, I5); a record without a subject key in both
datasets; a subject with two ADSL records; data-driven groups on ordinary
numbers, on text with blanks, special characters and letters outside the
BMP, on the text "NA" among other values, on a column that is all missing;
a data-driven grouping read from another dataset; overlapping defined
groups; an analysis set nobody is in; tests with a data-driven compared
grouping; the population of rule I13 with OR at the top and with nested AND
and NOT; a percent with a data-driven denominator and with a denominator
that has no grouping. Where they do not agree: F5.

#### R8 The methods on the reviewer's inputs

```text
summary.continuous, 600 random samples (ties, decimals, missing values, n 1 to 40, both definitions):
  largest relative difference Python against R 2.2e-16, against exact fractions 8.3e-16
test.fisher.exact, 490 random tables (370 larger than 2 x 2; empty cells, symmetric tables):
  largest relative difference against fisher.test 2.3e-12; against exact fractions (304 tables) 1.2e-14
test.chisq, 300 tables: Python against R 1.9e-14, against the finite series 3.8e-14; smallest p 5.3e-131
test.anova.oneway, 300 cases: Python against R 2.3e-13
3 x 3 tables of 254 subjects: [[20, 40, 26], [25, 35, 24], [22, 38, 24]]: enumeration 0.9170897792546375 in 2.7 s; fisher.test 0.9170897792574392
```

By hand, from the definitions: the sd of 1 to 7 (the root of 28/6), the
quartiles of the eight values under both definitions and of the eleven
heights, 13 of 86, the chi-square of the 2 x 2 and 2 x 3 tables
(p = exp(-8/3) for the second), the two-group analysis of variance
(1 - sqrt(6.4/8.4)), 27/4096 for the three groups of three, 17/35 for the
first Fisher table. All agree with the vector files.

#### R9 Hand-over, the published data, the issue draft, clean-room scans

The hand-over to R with one thing changed on the way (a monkey-patched
`handover_text`): one age + 1; numbers rounded to 15 digits; one term in
lower case; two ADSL rows exchanged; a missing AVAL written as 0; a
trailing blank added. In all six `rengine.data_problems` names the column
and the build would stop. 3,737 values of `ADVS.CHG` need more than 15
digits; none is lost.

The Python engine on Pilot 7's own ADaM files (`gold/reference/adam` of the
build) in place of the built ones: 4,238 rows, every value exactly equal;
the fingerprints of the 23 columns are equal. So the sentence of the issue
draft that names Pilot 7's files as the data holds.

The table of the issue draft, made again from the example, the exceptions
file and the ARD: 25 rows, 0 differ (raw value, formatted value, groups,
value from the data at 10 digits). 23 organ classes and 230 terms; one
embedded result in each of the four Fisher analyses by class and term. The
CSR copy that lies next to the example prints, in Table 14-2.01: Hispanic
3, 6, 3; height mean 162.6, 163.4, 165.8; height median 162.6, 162.6,
165.1. The draft's numbers are right.

Clean room: 371 tracked files, the largest is PLAN.md. The diff adds 41
files: 16 Python, 8 YAML, 8 JSON, 5 R, 2 Markdown, 1 shell script and its
recorded output. Of the 533 distinct embedded raw values with 9 or more
digits, tracked files hold: the 9 of the exceptions (in `exceptions.yaml`
and in the issue draft, where they are needed, and in the gate log of
base-0); 2 in the gate log and the report of real-2 (the two results "at
the edge"); 4 in `tests/unit/test_results.py` and 1 in a vector of the
display rule (F10). No tracked file holds something like a subject number
of the pilot. The eleven heights of a summary vector are plausible heights
(10 of the 11 values occur in ADSL) but not eleven consecutive subjects;
no pair of pilot counts equals the (61, 74) of the Fisher vector that has
the pilot's arm sizes. R files: F7.

#### R10 The graph before and after the fixes N3 and N4

```text
edges old 3975 new 3975 same pairs: True
nodes old 805 new 805 identical: True
coverage identical: True
edges that differ: 148 by type: {'derives_from': 148}; fields that differ: {('source',): 148}
of them, edges from an ADaM column to a column of its own dataset: 148
```

#### R11, R12

The pinned schema names the problem for: an analysis without `methodId` or
`name`, an unknown key, a raw value or a condition value that is a number,
an unknown comparator, `resultsByGroup` as text, a grouping without
`dataDriven`. It has no problem with an event whose `analyses` are left
out; `ars.index` then gives an event with no analysis, and the gate would
fail on the count of embedded results. `specfirst check` on a copy of b1 with
one line taken out of the Python ARD: exit 1, "changed since the build".

The ARS file compiled from std-1's base decisions: 44 analyses, no problem
in `ars.index`, 9 operations bound, 12 analyses with
`quantile_definition` from `programmingCode`, and it fits the pinned
schema. The sentence of the report holds.

## Findings

### F1 (not blocking, for the owner) 3,711 is "as printed"; at the precision the check asks for it is 3,710

The gate text asks for "at least 3,711 of the 3,735". The gate counts as
reproduced what agrees within half a unit of the last printed decimal: the
comparison of the spike, and so the meaning the number had when the plan
was written. One of the 3,711 (the first quartile of age, "70" against
70.5) does not agree at the decimals of its pattern; the check asks for a
class for it, and it has one. So one result is counted as reproduced and
as a difference: 3,711 + 25 is 3,736. By the check's own measure 3,710 are
reproduced and 25 are classified; the issue draft says 3,710.

The report, ADR-002 (decision 6) and the state file say all of this. The
gate was not changed and passes by the plan's own measure, so nothing
blocks. The plan's numbers (E2 to E4, the gate text, section 14) are the
owner's to revise.

### F2 (not blocking) The check accepts proofs that prove nothing

`results._proof_problem` checks the sentence a proof states. For three of
the kinds the sentence can be true and prove nothing (R5):

```text
A3  value_of_other_result names the placebo arm: P2 check passes: True
A8  age Q1 as no_alternative on the option sd_denominator (which has one value): passes: True
A9  height mean (high dose), an exchanged value, as same_under_every on quantile_definition: passes: True
A10 the same as no_alternative on quantile_definition: passes: True
A11 no_records with a zero count of another analysis (race, placebo): passes: True
```

- `value_of_other_result` takes any other result with the embedded value.
  A3: the count of Hispanic or Latino subjects in the low dose arm
  (embedded 3, ours 6), "proven" by the placebo count, which is also 3. For
  an embedded 0, 1 or 3 the pilot ARD has many rows that fit.
- `same_under_every` and `no_alternative` hold for any operation the named
  option cannot change. A mean is the same under every quantile
  definition; that says nothing about the reference.
- `no_records` takes any count that is 0.
  `test_results.py::test_a_result_without_a_value_and_without_records`
  itself proves a missing result for the class GI with the count of the
  term MI in the class CARD.

The nine other changes behave as they should (an entry removed, another
embedded text, another class, an entry for a reproduced result,
`same_under_every` for the age quartile, `alternative` r7 for it,
`no_records` without a count or with a count that is not 0).

The 25 entries that are committed do not use these holes: each of the 22
names the same analysis and operation in the other active arm (checked by
the reviewer's script, and D1 of the gate shows that all 22 are reproduced
when the arms are exchanged); the two quantile entries name the option
that matters; the two counts of the `no_records` entry are those of the
term in the two arms. So "0 unexplained" stands for the pilot. It would
not stand by itself for the next reference: real-3 meets the formatted
values and real-4 the CSR.

Fix: `value_of_other_result` must name a result of the same analysis and
operation that differs in one group of one grouping; `same_under_every`
and `no_alternative` only where some value of the option changes some
result of that operation; `no_records` only with counts of the cell's own
groups, one per compared group. Plant A3, A8, A9 and A11 as tests.

### F3 (not blocking) R's fisher.test does not use the tolerance of statement 5 for tables larger than 2 x 2

`test.fisher.exact`, statement 5: "'Not larger' allows a relative excess of
1e-7, as R's fisher.test does". That is what R does for a 2 x 2 table. For
larger tables its tolerance is wider. The reviewer searched the 2 x 3
tables of 12 to 105 subjects (rows of at least 2) for two tables with the
same margins whose probabilities differ by a relative 1e-7 to 3.6e-7,
stopped at the sixth pair, confirmed each ratio in exact fractions, and
ran both implementations with the less probable table as the observed one:

```text
[[0, 6, 20], [8, 27, 40]]:   ratio 1 + 2.666e-07: enumeration 0.06040878692449231, fisher.test 0.06533690837383269
[[4, 8, 30], [0, 6, 56]]:    ratio 1 + 3.209e-07: enumeration 0.009798846806875698, fisher.test 0.011455024125087577
[[4, 9, 30], [0, 5, 56]]:    ratio 1 + 3.209e-07: enumeration 0.002820436337498024, fisher.test 0.0035861957426922
[[27, 15, 6], [0, 15, 41]]:  ratio 1 + 1.169e-07: enumeration 1.2195957080824101e-14, fisher.test 1.3623367277605544e-14
[[1, 6, 20], [10, 28, 40]]:  ratio 1 + 2.666e-07: enumeration 0.1282455463122018, fisher.test 0.13531681960680528
[[5, 0, 40], [10, 27, 20]]:  ratio 1 + 2.666e-07: enumeration 5.724148010367068e-10, fisher.test 6.358880701965926e-10
```

In each case the difference is the probability of the one other table, and
5 to 21 percent of the p-value. The other table is the more probable one,
so the enumeration gives the exact sum and `fisher.test` does not. Two
controls: with a ratio of 1 + 7.552e-07 or 1 + 8.593e-07 (six tables) the
two agree to 1.7e-13; with 1 + 5.524e-09 (six tables) they agree to 2.5e-13
and both count the more probable table, as statement 5 says. So R's limit
for larger tables lies between 3.2e-7 and 7.6e-7.

Statement 6 is true of one implementation as well. A 3 x 4 table of 143
subjects, `[[12, 12, 12, 12], [12, 12, 12, 12], [11, 12, 12, 12]]`: the
enumeration refuses after 5 seconds ("more than 10000000 tables"),
`fisher.test` gives 1 at once. `methods.MethodError` is not among the
errors `build.build` catches, so the build then ends in a traceback, not
in "FAIL".

Such tables are rare (the search found none with fewer than 101
subjects), the pilot has none, and a case would stop the gate by rule R11,
not pass.
But a registry statement says what R does and R does otherwise, and when
it happens nobody is told which engine follows the registry. real-4 has 59
Fisher tests on 3 x 3 tables.

Fix: say in statements 5 and 6 which implementation they describe and what
R does; add one of the tables above as a vector with the exact value; let
the R implementation follow the registry for larger tables (its own sum
when a table falls into the window, or the enumeration ported); catch
`MethodError` in `build.build`.

### F4 (not blocking) The Python sd of equal values is not always 0, and the engines then disagree

`methods.summary_continuous` takes the mean as the exact sum divided by n,
rounded once. For three values of 0.1 that is 0.10000000000000002, and the
sd is not 0. R gives 0.

```text
66 cells of 2 to 10 equal values (0.1, 36.6, 162.6, 70.3, 1.1, 98.6, 0.3, 5.0, 100.0, 37.2, 0.07):
Python sd not 0: 4; R sd not 0: 0
   value 0.1  n 3 Python sd 1.6996749443881478e-17 R sd 0
   value 98.6 n 3 Python sd 1.7404671430534633e-14 R sd 0
through the engines, three ages of 0.1 in one arm:
   ard:A_AGE/M_CONT_sd/Arm_A: Python 1.6996749443881478e-17, R 0, relative difference 1.0e+00
```

Three subjects with the same temperature of 98.6 in one cell are an
ordinary input. `results.agreement` has a relative tolerance only, so the
gate would stop on it. By statement 4 of the entry the result is 0.

Fix: sd is 0 when the smallest and the largest value are equal, decided by
comparing the values, as statement 5 of `test.anova.oneway` does; a
statement and a vector for it.

### F5 (not blocking) Inputs on which the two engines differ or only one stops

From R7. Each either stops the build or shows as a disagreement; none
gives a wrong number in silence.

| Input | Python | R |
| --- | --- | --- |
| a data-driven group on the number 1e15, 1e16 or 1e22 | group `1000000000000000` | group `1e+15` |
| the numbers 0.0 and -0.0 in a grouping variable | one group `0`, count 4 | groups `0` and `-0`, count 2 each |
| the number 5e-324 as a group | `5e-324` | `4.94065645841247e-324` |
| a text column whose every value is the text "NA" | a group `NA` | jsonlite reads missing values; the column fingerprint differs and the build stops |
| a control character (U+0001, U+001F) in a group value | a row | invalid JSON; a `JSONDecodeError`, which the build does not catch |
| a number column compared with `0x3D` | refused | 61 |
| a number column compared with `6_1`, or with `nan` | 61, or nothing matches | refused |
| a text column compared with the JSON number 1.0 (only without a schema) | the text `1.0` | the text `1` |
| the mean of 1e20, 1 and -1e20 | 0.3333333333333333 | 0 |
| an analysis of variance of (1, 2, 3) and (1e9 + 1, 1e9 + 2, 1e9 + 3) | 2.666666666666666e-36 | 2.666665692748943e-36 (3.7e-7 apart; 6/F^2 is 2.6667e-36) |
| an analysis of variance with a group that holds 0.3 and 0.1 + 0.2 | 1.39e-63 | 3.96e-63 |

The first and fourth rows are the ones a real study could meet: a column
of "NA" for a region or for "not applicable" stops the build with "the R
engine read other values".

Fix: read the hand-over with `simplifyVector = FALSE` and convert by kind;
escape every control character in `json_string` (see F7); one rule for the
text of a number as a group value, in the README and in both engines; say
in rule I3 how a number is written.

### F6 (not blocking) What the agreement of the engines does not prove

The report says the greater part: both engines get the binding and the
data from the same Python code. In full, what is done once, in Python, for
both: the binding rules B1 to B3 and the resolved options; the choice of
the columns; the kind of each column, the missing values made one, dates
and Booleans as text (rule I1). `engine.R` is the same design as `ard.py`
in another language, function by function; what is independent is the
arithmetic of the methods and the coding of each rule. So agreement shows
that neither side slipped in the coding (R6) and that the arithmetic is
right; it does not show that rules I1 to I15 read ARS rightly.

For the 504 results the reference does not list this is all there is, and
it cannot see what both lack: 50 of these rows deleted from both ARDs, or
all of them set to 0.5 in both, pass every check (R6). Nothing in the gate
fixes the number of rows; test A6 prints 4,238 and does not assert it.

Rule I13, on which 408 of the 504 rest, is well supported by the
reference: all five embedded Fisher p-values with a value differ under the
nearest other reading (C6).

Fix: assert the rows per analysis in A6 or in the kit, so that a change
shows; real-3 will compare more of them with the formatted values.

### F7 (not blocking) Five statements of util.R stand in siera's readARS.R, and no test reads R files

The report: "No R code was taken from siera, cards or cardx. Test A5
compares Python files only". `third_party/SOURCES.md`: "no code or
template of theirs is copied into this repository". The reviewer compared
the lines of the five R files (more than 30 characters, white space and
comments left out) with the 878 R files of the cached sources:

```text
r/specfirstr/R/engine.R: 247 lines, shared 0      r/specfirstr/R/methods.R: 33 lines, shared 0
r/specfirstr/R/vectors.R: 27 lines, shared 0      r/specfirstr/run.R: 12 lines, shared 1 (commandArgs)
r/specfirstr/R/util.R: 32 lines, shared 5
  16 x <- gsub("\n", "\\n", x, fixed = TRUE)      siera:R/readARS.R:632
  17 x <- gsub("\r", "\\r", x, fixed = TRUE)      siera:R/readARS.R:633
  18 x <- gsub("\t", "\\t", x, fixed = TRUE)      siera:R/readARS.R:634
```

The two other shared lines of `util.R` are one-line idioms found in
unrelated files: the definition of `%||%` (Pilot 7, pharma-skills) and the
line of `json_scalar` that writes true or false (a test file of yamaa).

`json_string` in `util.R` (lines 13 to 20) and `.escape_single_quote` in
siera's `R/readARS.R` (lines 629 to 634) both begin with the same five
statements in the same order: the backslash, the quote, the line feed, the
carriage return, the tab. Three are the same letter for letter; the first
differs by `enc2utf8(x)`, the second by which quote it escapes. After that
the two functions go different ways.

The reviewer cannot tell a copy from two people writing the usual escape:
it is the obvious way to write it. But by the measure of test A5 (more
than 2 shared lines with a file of a cached source) `util.R` would fail if
A5 read R files, and lesson 26 shows what was done when a Python file
stood at 3. siera is MIT, so nothing that may not be redistributed is in
the repository. It does not block because no taking is shown; it is listed
because rule 1 of section 2.1 has no exceptions and here the claim rests
on a sentence, not on a check.

Fix: let A5 compare the R files of `r/specfirstr` with the R files of the
cache; write `json_string` anew so that it escapes every control character
(which F5 needs anyway), or record siera in `SOURCES.md`.

### F8 (not blocking, for the owner) ADR-002 takes a third way, and four of its sentences say more than its evidence

PLAN.md section 13.3 gives two ways: wrap siera, or our own on cards and
cardx. The ADR takes a third: our own on R's `stats`. It says so itself,
first among its points for the owner. The decision not to wrap siera
follows from T1 to T3. For the decision against cards and cardx:

- "its analysis of variance needs two packages outside the lock": that is
  `ard_stats_aov`. T4 of the same output shows that
  `ard_stats_oneway_test(..., var.equal = TRUE)` runs, and that is the same
  F test. The chi-square and the Fisher wrapper run too. What is left of
  the argument: the wrappers add no method, cost time (2.4 s against
  0.06 s for 200 tests; the R engine as a whole takes 2 s), and the
  descriptive defaults (quantile type 2 only, proportions) would have to
  be overridden.
- "cardx's tests are wrappers of ... `stats::oneway.test`; our engine calls
  the `stats` functions directly": ours calls `anova(lm())`.
- T2, "does not know 8 of the variant's value sources": the output counts
  8 analyses.
- T2, "siera's Fisher template gives an odds ratio and its interval, not a
  p-value": true (`06_fishers_exact/method.json` and `template.R` in the
  cache), but the recorded output does not show it. Its line "a Fisher test
  with a p-value among them: False" tests whether a method of the variant
  has "fisher" in its name.

Fix: reword the four sentences. The choice itself is the owner's.

### F9 (not blocking, for the owner) The classes: 24 are well supported, the empty p-value is the weakest

- The 22 exchanged values: `reference_error` is right. Besides the proofs:
  D1 (exchanging the arms reproduces all 22) and the CSR next to the
  example (R9).
- The median of height (162.2 against 162.6): right. The 41st to 45th of
  the 84 values are all 162.6, so no definition gives another value, and
  the CSR prints 162.6.
- The first quartile of age (70 against 70.5): defensible, and better than
  its proof shows. `no_alternative` looks at the two definitions of the
  registry. A third one gives exactly 70: no averaging when n * p is whole
  (SAS QNTLDEF=3, R type 1). But the example does not follow that one: of
  the 69 embedded quartiles and medians where the two differ, it has the
  averaged value in 68 and the other in this one (C5). So the example is
  at odds with itself, which is the meaning of `reference_error`. The
  entry's `sources` could say this.
- The empty p-value: the example lists a result without a value; our rule
  I9 gives no row for a term that does not occur in the two arms. Neither
  side has a value. Section 4.8 defines `reference_error` as "the
  reference contradicts its own data or documents"; this is closer to a
  difference of rule (which groups give results) than to a contradiction.
  E3 counted it as "1 p-value is empty", not as an error.

### F10 (not blocking) Small things in the texts

- `docs/state/real.md`, "For other tracks": the three methods of std-1 are
  said to be bound "by the names of their operations (rule B3)". Two of
  them (`Mth_Count`, `Mth_ContSumm`) are bound by rule B2 first: their
  description is `Method registry: <id>`. The result is the same.
- `docs/state/real.md`, "Passed": the entry of real-2 does not name the
  commit; that of real-1 does.
- The report, "The merge of main": "The gate below ran on the merged
  tree". The gate is above.
- `README.md`, "Status": lists base-0, real-1 and real-2 as passed; std-1,
  which is merged, is missing.
- `third_party/SOURCES.md`, note on ars: "nothing from either repository
  is committed or redistributed". Since real-2, 25 embedded values of the
  example are in `exceptions.yaml` and in the issue draft, and three more
  are in tests (`0.5934357753`, `9.5960516021` and `0.07719298250000001`
  in `test_results.py`; the first also in a vector of the display rule).
  They are single numbers, and the 25 are needed to name the differences;
  the note should say so.
- `standard/methods/README.md`, rule I3: the sentence in brackets says
  that EQ with the empty text is true for a missing value. Both engines
  treat the empty text that way under IN, NE and NOTIN as well (R7).
- The registry: a vector that cites a statement need not test it.
  Statement 6 of the Fisher test is cited by six vectors; its second
  sentence (the refusal) is tested by a unit test, for Python only (F3).
- ADR-002, decision 6, and the exceptions file: "every quantile
  definition" means the two of the registry (see F9).

### F11 (not blocking) The planted defects: one is broader than the case it stands for, and more is untested on the pilot than is listed

- D1 exchanges the two arms in every analysis: 1,898 differences. The case
  of E3 and of section 9.5 is an exchange in one analysis. The reviewer's
  single exchanges are caught (R6); one of them belongs in D1 (lesson 9).
- The four lines of R6 that the pilot cannot show. The report lists two
  such limits (the two sets, three data subsets). In particular no Fisher
  table of the pilot is larger than 2 x 2: for the claim "exact beyond
  2 x 2" the eight vectors are the whole evidence in the gate.
- The R side of rule I3 has no test in the repository: the comparison of
  numbers, NE, NOTIN and the ordered comparisons with a missing value are
  tested for `ard.compare` only. The toy event and the pilot compare no
  number, and use NE only on a column without missing values. The
  reviewer's cases agree (R7); ten of them as a test would close it.

### F12 (not blocking) Two results are equal only by the allowance of 1e-9

The gate prints them ("equal only at the edge of the allowance: 2"):
9.5960516021 against 9.596051602049998, and 0.07719298250000001 against
0.0771929824561402. The second differs by a relative 5.7e-10: not the
floating error of two correct computations, but a reference value rounded
to ten decimals. `results.py` and the README give the allowance the first
meaning. It is a matter of wording; the count is right either way.

## The ten questions

1. The gate and the gate text. Each statement is proven by a check that
   fails when it does not hold: check 11 with the two thresholds of
   `gates._results` (3,735 embedded and at least 3,711 reproduced, for
   both engines, with 0 unexplained and the agreement), check 8 (P1, which
   covers the two ARD files and the ARS file), check 13 (D1 to D5 must
   each run and pass). "Reproduced" is "as printed", half a unit of the
   last printed decimal plus a relative 1e-9; it is sound as the plan's
   own measure and loose where the reference prints few digits (R4).
   3,711 means what the report says (F1). "0 unexplained" is real for the
   pilot: the 25 proofs hold, are checked on every run for both engines,
   and the reviewer checked each from the data. A wrong entry could pass
   in three ways (F2). The classes: F9.
2. Rule R11. Two implementations of the methods and two codings of the
   rules; one binding, one preparation of the data, one design (F6). The
   agreement check is sound: the same IDs, every stamp, null only against
   null, relative 1e-9 with nothing below it (which is why F4 stops it).
   The hand-over cannot lose or change a value unseen: six plants, all
   seen (R9), and jsonlite's own misreading of "NA" is seen too (F5). What
   the fingerprints cannot show is whether Python read the Parquet file
   rightly; the report says so.
3. Planted defects. D2 to D5 are the real cases, with their limits stated;
   D1 is broader than its case (F11). The reviewer's plants: R5, R6, F2,
   F11.
4. The registry. The statements say what both implementations do, except
   statements 5 and 6 of the Fisher test for R (F3) and statement 4 of the
   summary for Python on equal values (F4). The vectors are right (R8).
   The enumeration is exact; it agrees with `fisher.test` on 370 larger
   tables of the reviewer and differs on six found by search (F3). Left to
   floating error: F3, F4, and the last three rows of F5.
5. Rules I1 to I15. Implemented as written in both engines; of 65 edge
   cases 45 give the same rows, 4 are refused by both and 16 are in F5;
   one sentence of I3 says less than both engines do (F10). No input was
   found where both engines give the same wrong result.
6. P1 and canonical output. The two ARD files and the ARS file are
   deterministic, sorted and canonical, and hold no path and no time (R3).
   The R ARD is written by Python from the rows R printed with 17 digits;
   whole-number means are whole numbers there and floats in the Python
   ARD, which the comparison treats as one value.
7. Clean room and scope. No study data, document or example file is
   committed; the values that are quoted are listed in R9 and F10. No file
   of siera, cards or cardx is committed; five statements are in question
   (F7). `SOURCES.md` is right except for its note on ars (F10). `PLAN.md`
   (SHA-256 `234a642a...2e4c`, as the report says), `standard/schemas/` and
   `env/` are not in the diff. Nothing of real-3 is in the diff. Whether
   anything was posted cannot be seen from here; the draft says it was
   not, and `origin` is the owner's private repository, where
   `track/real` stands at `1e0f164`.
8. Claims. The gate log is the log of this code (R2); the clone itself
   was gone. The report quotes it faithfully and names what it leaves out.
   Every number of the report, ADR-002, the state file and the issue draft
   that was checked agrees with the code and the runs; the sentences that
   say more than the evidence are in F3, F8 and F10. The decision of
   ADR-002 not to wrap siera follows from its evidence; the decision
   against cards and cardx is a choice (F8). The issue draft is accurate
   in every number (R9).
9. N1 to N7. All seven are fixed as the report says. N1: A4 changes all
   202 columns (131 rolled, 70 emptied, 1 filled), no dataset changes
   (R1). N3 and N4: the same pairs, nodes and coverage; 148 places changed,
   all within a dataset (R10); three unit tests hold the reviewer's cases.
   N5: found by the root element; the data check passes on 373 files.
   N6: a unit test. N2 and N7: the wording of ADR-001. The gate of real-1
   passed at `f357e74` on a clean clone: the log is in
   `build/gates/real-1/clean-clone.log` and holds the lines the report
   quotes. Nothing was broken.
10. The merge. Six files differ from both parents: the three with
    conflicts, `CLAUDE.md` (59 lines), `tests/unit/test_gates.py` (the new
    test) and `SOURCES.md` (merged without conflict). Both gates, both sets
    of commands and both sets of lessons are there; the lessons of real-2
    are 23 to 26 and every reference to them was renumbered. No file of
    std-1 is changed in the diff `main..track/real`, and `main` is an
    ancestor of `track/real`: `main` can move forward to it without a
    merge commit.

## Not checked

- The clean clone of the gate run: gone before the review (R2). A fresh
  install and a fresh fetch by the reviewer (no network).
- The two CI runs, and whether anything was posted.
- The owner's copy of the plan outside the worktree.
- The text that will replace the three placeholder lines of the report.
- The 51 tests of std-1's checkers, beyond that they pass in the gate.
- `registry.json` by reading; the gate and a unit test compare it with the
  YAML entries.
- Fisher's exact test on tables with more than about a million tables to
  sum, apart from two 3 x 3 tables of 254 subjects and the refusal.
- The engines on the tiny study of std-1 (the report says they were not
  run on it).

Verdict: PASS
