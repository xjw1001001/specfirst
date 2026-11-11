# real-2 Result engines: report

Date: 2026-11-11. Branch: `track/real`. Depends on real-1 (passed).

## Verdict

The gate passed. `scripts/clean_clone_gate.sh real-2` exited 0 on a clean
clone of commit `1e0f164`, after a fresh install and a fresh fetch: 15 of 15
checks. The complete output is in `docs/reports/real-2.gate.log` (385
lines); the section "The gate" below quotes it.

- Both engines reproduce 3,711 of the 3,735 results embedded in CDISC's ARS
  example, as printed. Nothing is unexplained: the 25 results that differ
  each have a class and a proof that the check verifies.
- The Python and the R engine agree on all 4,238 results; the largest
  relative difference is 2.4e-13 (allowed: 1e-9).
- P1: 26 of 26 built files have the same SHA-256 in two builds.
- The four planted defects of the plan are caught, in the comparison with
  the reference and in the comparison of the two engines.
- The Python engine runs the 31 analyses in 0.46 seconds.

Three things differ from what the plan expected, and are for the owner
(ADR-002): the R engine does not go through cards and cardx; 25 results
need a class where evidence E3 counts 24; and with R's quantile definition
97 results differ where E4 counts 49.

The independent review (rule R7) is in `docs/reports/real-2.review.md`. Its
verdict is PASS, in one pass, with twelve findings that do not block
(section "Review"). They are not fixed here, so that the code of the merge
is the code that passed the gate; `docs/state/real.md` lists them for the
first commit of real-3. With gate and review passed, `track/real` merges to
`main` and both are pushed (section 2.4); the git history and
`docs/state/real.md` record the merge.

## What real-2 asks for, and where it stands

| Item of PLAN.md section 13.3 | State | Where |
| --- | --- | --- |
| ADR-002: the R engine wraps siera, or is our own on cards and cardx | done: our own, on R's `stats` package; siera was tried first (rule R2) | `docs/decisions/ADR-002.md`; `evidence/adr002_siera_trial.sh` and `.out` |
| Method registry v0: count of subjects, percent with a referenced denominator, continuous summary, chi-square, one-way ANOVA, Fisher exact, and the display rule "round half away from zero"; numbered semantics, test vectors, cross-references | done: 7 entries, 42 statements, 77 vectors | `standard/methods/`; `tests/methods/`; gate checks 4 and 6 |
| Fisher exact must be exact for tables larger than 2 x 2: the enumeration in Python, checked against R's `fisher.test` (E27) | done | `specfirst.machine.methods.fisher_exact_p`; test `fisher-r` in gate check 6 |
| ARD format and canonical writer | done: the ARD schema v0 unchanged, rows sorted by ID, canonical JSON lines | `specfirst.machine.ard`, `results.write_ard`; `standard/methods/README.md` |
| Validate ARS files against the schema generated from the ARS model | done: the pinned example and the built ARS file, in the build and in the check | `kit.yaml` (`results[].schema`); gate check 11 |
| Python engine: rewrite the spike (about 3 minutes; target under 10 seconds) | done: 0.4 seconds | `specfirst.machine.ard`; test A6-engine in gate check 12 |
| R engine: the same ARS, the same registry | done | `r/specfirstr/`; `specfirst.machine.rengine` |
| `gold/exceptions.yaml` for the pilot: the 24 results of E3, each with its class and proof | done: 25 entries, the 24 of E3 and one more | `kits/cdiscpilot01/gold/exceptions.yaml`; gate check 11 |
| Our gold ARS carries regenerated results | done: `gold/ars/<id>.json` of a build, raw values only | `results.with_results`; gate check 11 |
| Draft the issue text for the ARS repository. Do not post it | done: a draft, not posted | `docs/upstream/ars-issue-common-safety-displays.md` |
| Register the gate as `real-2` | done: 15 checks | `src/specfirst/gates.py` |

`PLAN.md`, `standard/schemas/` and `env/` are not changed. The owner's copy
of the plan (`D:\trial_work\plan\PLAN.md`) had the SHA-256 of the
repository's `PLAN.md` when the work began
(`234a642a...2e4c`).

## The gate

Gate text of PLAN.md section 13.3: both engines reproduce at least 3,711 of
the 3,735 embedded results, with 0 unexplained. The engines agree on every
result (relative tolerance 1e-9). P1 passes. Planted defects are caught:
exchanged arm labels, a wrong analysis set, a changed quantile definition, a
dropped data subset.

Command, run in Ubuntu 24.04 under WSL2 as root, in the worktree of
`track/real`:

```text
$ bash scripts/clean_clone_gate.sh real-2 /mnt/d/trial_work/specfirst/.git 1e0f164
```

`1e0f164` was the HEAD of `track/real`. The script clones the repository
with `git clone --no-local` into a new folder under `/tmp`, checks out the
commit, and puts the Python environment, the R library and the fetch cache
of the clone under the same new folder. It then runs `env/install.sh`,
`specfirst fetch` and `specfirst gate real-2 --clean`.

The gate has fifteen checks. The plan's gate text is checks 8 (P1), 11
(both engines against the embedded results, with nothing unexplained, and
against each other) and 13 (the planted defects). Check 11 fails unless
each engine reproduces at least 3,711 of 3,735. The others: drift first
(rule R3), the pins, lint, the registry and its `registry.json`, the unit
tests, the method vectors in both engines, every check of the gate of
real-1 (kit, P2 for ADaM, trace, pilot tests), the speed of the Python
engine (A6), a second verification of the fetch cache (lesson 13), and the
ASCII check. Check 13 runs the folder `tests/defects`: the 5 tests of
real-2 and, since the merge of `main`, the 51 of std-1's checkers.

Output. Lines are quoted as printed from `docs/reports/real-2.gate.log`
(385 lines). `[...]` marks where lines of the full log are left out: the
three git commands that make the clone and the commit line they print, the
line that names the R library and the line that it matches the lock, the
lines of `specfirst doctor`, the pin listings with the line that names the
cache, pytest's progress dots, 20 of the 26 hash lines of P1, the per-dataset
lines of P2, of the trace, of the claims and of the tests A1 to A3.

```text
clean clone gate real-2
repository: /mnt/d/trial_work/specfirst/.git
commit:     1e0f164
clone:      /tmp/specfirst-clean-ZCcz7L/specfirst
environment and cache: /tmp/specfirst-clean-ZCcz7L/env
[...]
$ bash env/install.sh
python environment: /tmp/specfirst-clean-ZCcz7L/env/venv-specfirst-1711249203
[...]
R packages: 99 wanted, 99 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
[...]
doctor: ok

$ specfirst fetch
[...]
fetch: every pin verified

$ specfirst gate real-2 --clean
gate real-2 at commit 1e0f164ec986710dd8a291eabce21c0621ba4a44 (clean)

== [1/15] environment: specfirst doctor
[...]
doctor: ok
-- PASS environment (0.3 s)

== [2/15] pins: specfirst fetch --verify
[...]
fetch: every pin verified
-- PASS pins (1.0 s)

== [3/15] lint: ruff check .
All checks passed!
-- PASS lint (0.0 s)

== [4/15] registry: specfirst methods
count.subjects                     descriptive  4 statements  python+r operations: n; options: -
display.round.half_away_from_zero  display      5 statements  python   operations: text; options: -
percent.subjects                   descriptive  6 statements  python+r operations: pct; options: -
summary.continuous                 descriptive  9 statements  python+r operations: n, mean, sd, median, q1, q3, min, max; options: quantile_definition=sas5, sd_denominator=n_minus_1
test.anova.oneway                  test         5 statements  python+r operations: p_value; options: -
test.chisq                         test         6 statements  python+r operations: p_value; options: correction=none
test.fisher.exact                  test         7 statements  python+r operations: p_value; options: alternative=two_sided
methods: 7 entries
-- PASS registry (0.0 s)

== [5/15] unit tests: pytest -m "not evidence" -q
[...]
674 passed, 19 deselected in 44.39s
-- PASS unit tests (44.8 s)

== [6/15] method vectors: SPECFIRST_STRICT=1 pytest tests/methods -s -q

--- python-vectors
Python implementations: 77 cases of 7 methods, 0 differences
.
--- r-vectors
R implementations: 60 cases of 6 methods, 0 differences
.
--- exact-arithmetic
expected values computed again in exact arithmetic: 60 cases, 0 differences; written by hand: 17 cases (the display rule)
.
--- fisher-r
2 x 3 2 x 3                                                   enumeration 0.13419913419913376    fisher.test 0.13419913419913387
3 x 3 3 x 3                                                   enumeration 0.2671753203049479     fisher.test 0.26717532030494506
3 x 3 3 x 3 of the size of a laboratory shift table           enumeration 0.4464490858573885     fisher.test 0.44644908585743115
3 x 3 3 x 3 with tables of equal probability                  enumeration 0.999999999999996      fisher.test 0.9999999999999984
3 x 3 rows and columns of zeros are left out                  enumeration 0.4857142857142849     fisher.test 0.4857142857142856
2 x 4 2 x 4                                                   enumeration 0.4587455887765525     fisher.test 0.4587455887765442
4 x 2 4 x 2: the same table turned                            enumeration 0.4587455887765526     fisher.test 0.4587455887765442
4 x 3 4 x 3                                                   enumeration 0.4410161267304116     fisher.test 0.44101612673041296
..
5 passed in 0.80s
-- PASS method vectors (0.9 s)

== [7/15] kit: specfirst kit assemble cdiscpilot01
study data in git (E20): 371 maintained files checked, 0 problems
kit cdiscpilot01: 66 files match their pinned SHA-256 (26 inputs, 40 gold) in /tmp/specfirst-clean-ZCcz7L/specfirst/build/kits/cdiscpilot01
-- PASS kit (0.1 s)

== [8/15] P1 determinism: specfirst check cdiscpilot01 --twice (its first part)
build into build/p1/cdiscpilot01/first: exit 0 (build cdiscpilot01: 10 datasets, 805 nodes, 3975 edges, 26 files in /tmp/specfirst-clean-ZCcz7L/specfirst/build/p1/cdiscpilot01/first)
build into build/p1/cdiscpilot01/second: exit 0 (build cdiscpilot01: 10 datasets, 805 nodes, 3975 edges, 26 files in /tmp/specfirst-clean-ZCcz7L/specfirst/build/p1/cdiscpilot01/second)
same      76c528ce523c6a13 76c528ce523c6a13 gold/ard/common-safety-displays.jsonl
same      de20ea90cae0946d de20ea90cae0946d gold/ard/common-safety-displays.r.jsonl
same      a3d51da218b6839e a3d51da218b6839e gold/ars/common-safety-displays.json
[...]
same      356127185426e1e0 356127185426e1e0 gold/graph/coverage.json
same      592bfd74d71f43e3 592bfd74d71f43e3 gold/graph/edges.jsonl
same      45af1a74e0a35c89 45af1a74e0a35c89 gold/graph/nodes.jsonl
[...]
P1 determinism: 26 of 26 files have the same SHA-256 in both builds
-- PASS P1 determinism (38.8 s)

== [9/15] P2 reproduction: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its second part)
[...]
TOTAL cells=9119605 mismatched=0
numbers equal within the tolerance but not exactly: 1869 cells, largest difference 4.5e-13
storage type only, same values (reference -> built): large_string -> string in 221 columns
P2 reproduction: 10 of 10 datasets equal their reference (numeric tolerance 1e-10)
-- PASS P2 reproduction (0.4 s)

== [10/15] trace: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its third part)
dataset   columns to SDTM by rows literal  gaps
[...]
TOTAL         415     413      14       2     0
to SDTM: reaches SDTM columns through derives_from. by rows: those of them whose own rule reads no column
and that reach SDTM only through a filter on rows (of a row template or of the specification).
nodes: L0 279, L3 111, L4 415
edges: cites 706, derives_from 3269
cites edges: 706 imported, 0 with a verified quote, 0 approved by a person
literal columns sit on rows of: adam:ADSL (2)
[...]
trace: complete
-- PASS trace (0.8 s)

== [11/15] results: specfirst check cdiscpilot01 --build build/p1/cdiscpilot01/first (its last part)
ARS schema (gold/spec/ars/ars_ldm.schema.json): gold/spec/ars/common-safety-displays.json fits; gold/ars/common-safety-displays.json fits
results common-safety-displays, Python engine: 3735 embedded results, 3711 reproduced as printed, 23 with another value, 1 without a result of ours
  reproduced as printed, but not at the precision of the result pattern: 1 (each needs a class, like the others)
    ard:An03_01_Age_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_5_Q1/AnlsGrouping_01_Trt_3: embedded 70, ours 70.5
  equal only at the edge of the allowance: 2
    ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_3_SD/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_2/AnlsGrouping_09_Visit_04: embedded 9.5960516021, ours 9.596051602049998
    ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_2_Mean/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_4/AnlsGrouping_09_Visit_09: embedded 0.07719298250000001, ours 0.0771929824561402
  explained:   1 reference_error, proof no_alternative
  explained:   1 reference_error, proof no_records
  explained:   1 reference_error, proof same_under_every
  explained:  22 reference_error, proof value_of_other_result
results common-safety-displays, Python engine: 0 unexplained
results common-safety-displays, R engine: 3735 embedded results, 3711 reproduced as printed, 23 with another value, 1 without a result of ours
  reproduced as printed, but not at the precision of the result pattern: 1 (each needs a class, like the others)
    ard:An03_01_Age_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_5_Q1/AnlsGrouping_01_Trt_3: embedded 70, ours 70.5
  equal only at the edge of the allowance: 2
    ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_3_SD/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_2/AnlsGrouping_09_Visit_04: embedded 9.5960516021, ours 9.596051602049998
    ard:An08_02_ChgBl_Summ_ByTrt/Mth02_ContVar_Summ_ByGrp_2_Mean/AnlsGrouping_01_Trt_1/AnlsGrouping_08_Param_4/AnlsGrouping_09_Visit_09: embedded 0.07719298250000001, ours 0.0771929824561402
  explained:   1 reference_error, proof no_alternative
  explained:   1 reference_error, proof no_records
  explained:   1 reference_error, proof same_under_every
  explained:  22 reference_error, proof value_of_other_result
results common-safety-displays, R engine: 0 unexplained
results common-safety-displays: 504 results of ours that the reference does not list: An07_09_Soc_Comp_ByTrt_PlacHigh 21, An07_09_Soc_Comp_ByTrt_PlacLow 21, An07_10_SocPt_Comp_ByTrt_PlacHigh 186, An07_10_SocPt_Comp_ByTrt_PlacLow 180, An08_02_ChgBl_Summ_ByTrt 96
results common-safety-displays: gold/ars/common-safety-displays.json carries the 4238 results of the Python ARD as raw values
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
results: pass
-- PASS results (2.5 s)

== [12/15] pilot tests: SPECFIRST_STRICT=1 pytest tests/pilot -s -q

--- A1-resolve
[...]
Pilot 7 pins yamaa at git revision c039509082b545fe913c00d1686426c3d245778c (cdiscpilot01/program/adam/python/requirements.txt)
snapshots were made with yamaa 0.7.0 built from git revision c039509082b545fe913c00d1686426c3d245778c
installed: yamaa 0.7.0 (wheel)
.
--- A2-runner
[...]
.
--- A3-lineage
[...]
.
--- A4-unread
SDTM columns with a node in the graph: 111; without one: 202, every one of them changed (1 all missing, filled, 70 constant, emptied, 131 rolled)
ADaM datasets that changed: none
.
--- A5-adapted
recorded as adapted: src/specfirst/machine/lineage.py shares 73 lines with cached sources
recorded as adapted: src/specfirst/machine/runner.py shares 3 lines with cached sources
compared 76 Python files of ours with 673 of p7, yamaa, p6, ars; the most lines a file that is not recorded shares: 1 (allowed: 2)
.
--- A6-engine
Python engine: 31 analyses on 23 columns of ADAE, ADSL, ADVS: 4238 rows in 0.46 s (the spike: about 3 minutes; the target: under 10 seconds)
embedded results: 3735; reproduced as printed: 3711
.
6 passed in 51.24s
-- PASS pilot tests (51.5 s)

== [13/15] planted defects: SPECFIRST_STRICT=1 pytest tests/defects -s -q

--- D1-arms
unchanged: 3711 of 3735 reproduced, 25 explained, check passes: True
low and high dose exchanged: check passes: False; 1836 of 3735 reproduced; 1898 other values, of which 1896 are our value of the other arm
entries with the proof value_of_other_result that are reproduced now: 22 of 22
.
--- D2-set
unchanged: 3711 of 3735 reproduced, 25 explained, check passes: True
safety set read from EFFFL: check passes: False; 2754 of 3735 reproduced; differences in 28 analyses
intent-to-treat set in place of the safety set: 0 results change (both sets hold the same subjects in the pilot: not separable on these data)
.
--- D3-quantile
unchanged: 3711 of 3735 reproduced, 25 explained, check passes: True
quantile definition r7: check passes: False; 3662 of 3735 reproduced as printed, 49 fewer (E4: 49); at the precision of the result pattern 97 new differences: {'Q1': 45, 'Q3': 52}
.
--- D4-subset
unchanged: 3711 of 3735 reproduced, 25 explained, check passes: True
An07_01_TEAE_Summ_ByTrt without its data subset: check passes: False; new differences 4
each of the 18 analyses with a data subset, one at a time:
  caught: 15
  changes no result: 1 (An08_01_Obs_Summ_ByTrt)
  changes only results the reference does not list: 2 (An07_09_Soc_Comp_ByTrt_PlacLow, An08_02_ChgBl_Summ_ByTrt)
.
--- D5-engines
unchanged: engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
R engine alone, low and high dose exchanged: 1930 results disagree
R engine alone, safety set read from EFFFL: 1287 results disagree
R engine alone, quantile definition r7: 2160 results disagree
R engine alone, An07_01_TEAE_Summ_ByTrt without its data subset: 4 results disagree
....................................................
56 passed in 89.71s (0:01:29)
-- PASS planted defects (90.0 s)

== [14/15] cache untouched: specfirst fetch --verify
[...]
fetch: every pin verified
-- PASS cache untouched (0.1 s)

== [15/15] ASCII: python -m specfirst.asciicheck
ASCII check: 371 files checked, 0 with non-ASCII bytes
-- PASS ASCII (0.0 s)

PASS  environment          0.3 s
PASS  pins                 1.0 s
PASS  lint                 0.0 s
PASS  registry             0.0 s
PASS  unit tests          44.8 s
PASS  method vectors       0.9 s
PASS  kit                  0.1 s
PASS  P1 determinism      38.8 s
PASS  P2 reproduction      0.4 s
PASS  trace                0.8 s
PASS  results              2.5 s
PASS  pilot tests         51.5 s
PASS  planted defects     90.0 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-2: PASS

clean clone gate real-2: PASS (clone kept in /tmp/specfirst-clean-ZCcz7L/specfirst until /tmp is cleared)
```

## Findings N1 to N7 of real-1

The second pass of the review of real-1 left seven findings that did not
block. They are fixed in the first commit of real-2, `f357e74`.

| # | Finding | What was done |
| --- | --- | --- |
| N1 | Test A4 rolled 202 SDTM columns, but a roll changes only the 131 with more than one value | A4 now changes every one: 131 rolled, 70 constant columns emptied, 1 all-missing column filled. No ADaM dataset changes. |
| N2 | P1 compares two folders of one checkout | ADR-001 item 4 says so, and why the gate cannot compare against a recorded hash. |
| N3 | The place of an edge fell outside the stated rule in two cases | The walk of `graph._trace_column` goes level by level, and a column taken through a lookup over the dataset itself is cited at the rule that names it. On the pilot: the same 3,975 pairs of nodes; 148 edges cite another line, all through lookups over `SELF`; nodes and coverage unchanged. Two unit tests have the reviewer's cases. |
| N4 | `value` counted a top-level `filter` as part of a column's rule | A filter on rows is context, like a row template. A unit test has the case. |
| N5 | An ODM file in git was seen only as `.xml`, in ASCII or UTF-8, near its start | It is found by its root element, under any name, in UTF-8 or UTF-16. `kits/README.md` says what is still not seen (compressed, other encodings). |
| N6 | Two time zones at one instant were "storage type only" | Each time zone is a kind of its own. |
| N7 | Two sentences of ADR-001 item 5 | Reworded: what the plan says about the tolerance, and "every cell that is not missing on both sides". |

The gate of real-1 passed again with these changes, on a clean clone of
`f357e74`:

```text
$ bash scripts/clean_clone_gate.sh real-1 /mnt/d/trial_work/specfirst/.git f357e74
[...]
gate real-1 at commit f357e748c854600fc6f10d161042ea61d8717a05 (clean)
[...]
344 passed, 13 deselected in 9.73s
[...]
P1 determinism: 23 of 23 files have the same SHA-256 in both builds
[...]
TOTAL cells=9119605 mismatched=0
[...]
TOTAL         415     413      14       2     0
[...]
SDTM columns with a node in the graph: 111; without one: 202, every one of them changed (1 all missing, filled, 70 constant, emptied, 131 rolled)
ADaM datasets that changed: none
[...]
PASS  environment          0.3 s
PASS  pins                 0.8 s
PASS  lint                 0.0 s
PASS  unit tests           9.9 s
PASS  kit                  0.1 s
PASS  P1 determinism      28.4 s
PASS  P2 reproduction      0.5 s
PASS  trace                0.8 s
PASS  pilot tests         49.6 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-1: PASS
```

The gate of real-2 repeats every check of real-1 (a unit test asserts it),
so the run above is not the only evidence.

## ADR-002 in short

siera 0.5.6 was tried first (`evidence/adr002_siera_trial.sh`, output in
`evidence/adr002_siera_trial.out`):

```text
== T1 siera::readARS on CDISC's example (31 analyses)
scripts written: 5
warnings: 62
analyses whose method has no code for siera (no code is generated for them): 31
analyses whose code template names a value source siera does not know: 6
other warnings: 0
lines that compute something in the generated scripts (cards::, cardx::, stats::): 0
[...]
== T3 the scripts of T2 on the pilot ADaM
[...]
ARD_Out14-1-1:
  ERROR: The packages "broom.helpers" (>= 1.17.0) and "parameters" (>= 0.20.2) are required.
[...]
the 3735 results CDISC embeds: {'equal': 2029, 'not computed': 1693, 'other value': 13}
[...]
200 Fisher tests: cardx 2.4 s, stats::fisher.test 0.06 s
```

siera generates R scripts from R code that the ARS file must carry; CDISC's
example carries none. The R engine is therefore our own, in `r/specfirstr/`.
It takes its arithmetic from R's `stats` package (the functions cardx
wraps), uses base R and jsonlite only, and is sourced, not installed. The
ADR lists four points for the owner; the first is that this is not "on
cards and cardx" as section 7.1 words it.

## The method registry

```text
$ specfirst methods
count.subjects                     descriptive  4 statements  python+r operations: n; options: -
display.round.half_away_from_zero  display      5 statements  python   operations: text; options: -
percent.subjects                   descriptive  6 statements  python+r operations: pct; options: -
summary.continuous                 descriptive  9 statements  python+r operations: n, mean, sd, median, q1, q3, min, max; options: quantile_definition=sas5, sd_denominator=n_minus_1
test.anova.oneway                  test         5 statements  python+r operations: p_value; options: -
test.chisq                         test         6 statements  python+r operations: p_value; options: correction=none
test.fisher.exact                  test         7 statements  python+r operations: p_value; options: alternative=two_sided
methods: 7 entries
```

- Semantics are numbered statements; a vector names the statements it
  exercises, and a test fails when a statement has no vector (two
  statements of `percent.subjects` are about which results are referenced
  and are tested with the engine).
- The expected values of the vectors do not come from the engines:
  `tests/methods/oracle.py` computes 60 of the 77 cases again with
  fractions and closed forms; the 17 cases of the display rule are written
  by hand.
- The Python methods are written from the definitions; the R methods call
  `stats::quantile` (types 2 and 7), `sd`, `chisq.test`, `fisher.test` and
  `anova(lm())`. Gate check 6 runs both on the vectors, to a relative
  1e-12.
- Fisher's exact test: the Python enumeration sums over every table with
  the observed margins. On the eight vectors larger than 2 x 2 it agrees
  with R's `fisher.test` (the lines are in the gate output above).
  SciPy's `fisher_exact` is not used (E27).
- The display rule has a Python implementation only (ADR-002, decision 3).

## The engines

Both follow the rules I1 to I15 of `standard/methods/README.md`, which
write down what ARS leaves to code: missing values in conditions, how a
condition on another dataset applies, which groups give results, how a
test gets its table, and the denominator of a test of occurrence. An ARS
operation is bound to a registry operation by the rules B1 to B3; the kit
binds the three tests of CDISC's example, whose operations are all called
"P-value", and states the SAS quantile definition.

On the example (31 analyses, 23 columns of ADSL, ADAE and ADVS) each engine
gives 4,238 rows. 3,734 of them are results the example embeds; 504 are
not: the Fisher tests for every organ class and preferred term, where the
example embeds one each (42 and 366 rows), and the baseline cells of
change from baseline, which have no record (96 rows: a count of 0 and
missing statistics).

The R engine cannot read Parquet or YAML with the locked library. It is
handed the 23 columns as JSON and the registry as `registry.json`, and the
build fails unless the SHA-256 of every column as R read it equals what the
Python side computes from the Parquet data.

## P2 for results: 3,711, and 25 differences

The example drops trailing zeros from its raw values. The comparison of
evidence E2, half a unit of the last printed decimal, therefore accepts
70.5 for "70" and anything above 0.5 for a p-value printed as "1". The
check compares in two steps (ADR-002, decision 6): as printed, which is
what "reproduced" counts and what the gate's 3,711 means; and at the
decimals of the operation's `resultPattern`. A result that passes the
first step only needs a class like any other difference.

- Both engines reproduce 3,711 of 3,735 as printed: the count of E2.
- 25 results need a class: 23 with another value, 1 without a result of
  ours, and 1 that is reproduced as printed only. Evidence E3 has 24. The
  25th is the first quartile of age in the high dose arm: embedded 70
  (formatted 70.0), from the data 70.5 by the SAS default.
- With R's quantile definition 3,662 are reproduced as printed, 49 fewer,
  as E4 says; at the precision of the pattern 97 results differ.
- Two more results are equal only on the edge of the allowance; the gate
  prints them.

`kits/cdiscpilot01/gold/exceptions.yaml` gives each of the 25 the class
`reference_error` and a proof that the check verifies on every run:

| Results | Proof kind | What the check verifies |
| --- | --- | --- |
| 22: counts and percents of ethnicity and of three race groups, two means of height | `value_of_other_result` | the embedded value is our value of the other active arm |
| 1: median of height, low dose (162.2 against 162.6) | `same_under_every` | our value is the same under both quantile definitions, and never the embedded one |
| 1: first quartile of age, high dose (70 against 70.5) | `no_alternative` | under no quantile definition is our value the embedded one, and the seven other statistics of the same cell are reproduced |
| 1: the Fisher p-value for WOUND HAEMORRHAGE, placebo against low dose (empty) | `no_records` | the reference embeds no value, the engines give no result, and the counts of that term in the two arms are 0 |

The classes are the executor's reading and are for the owner to confirm.
What supports them beyond the proofs is in the `sources` of each entry:
the pilot ADSL in both engines, and CSR Table 14-2.01 for the Hispanic
counts and the height statistics (evidence E3 and E24).

## Planted defects

`tests/defects/test_defects.py`, gate check 13. Each defect is planted in
CDISC's example or in the kit's binding, run by the real engines on the
ADaM datasets the kit builds, and judged by the functions the gate calls.
Every case first shows that the unchanged inputs pass.

| Test | Defect | Outcome |
| --- | --- | --- |
| D1-arms | the low dose and the high dose group exchange their conditions | fails the check: 1,836 of 3,735 reproduced; of 1,898 other values, 1,896 are our value of the other arm; the 22 exchanged results of E3 are reproduced now, and the check says their entries are stale |
| D2-set | the safety set reads `EFFFL` | fails the check: 2,754 reproduced; differences in 28 analyses, all of that set |
| D3-quantile | `quantile_definition: r7` | fails the check: 49 fewer reproduced as printed (E4), 97 new differences, all first or third quartiles of `summary.continuous`; the options hash marks exactly the rows of that method |
| D4-subset | `An07_01_TEAE_Summ_ByTrt` loses its data subset | fails the check: 4 new differences, all in that analysis |
| D5-engines | each of the four in the R engine's input alone | the engines disagree: 1,930, 1,287, 2,160 and 4 results |

What the pilot data cannot show is printed, not counted as caught:

- The intent-to-treat set in place of the safety set changes no result:
  both hold the same 254 subjects.
- Of the 18 analyses with a data subset, dropping it is caught for 15. For
  one it changes no result (`An08_01_Obs_Summ_ByTrt`: on these data the
  listed visits hold analysis records only). For two it changes only
  results the reference does not list (`An07_09_Soc_Comp_ByTrt_PlacLow`,
  `An08_02_ChgBl_Summ_ByTrt`). The test fails if a defect changes a result
  the reference lists and passes the check.

This sorting found the hole of the two-step comparison above: in its first
form D4 asserted that all 18 are caught (lessons 23 and 24).

Unit tests plant the smaller cases on a made-up study (8 subjects, 8
analyses): 14 defects of a reporting event, 10 bindings that must be
refused, 11 inputs the engine must refuse, differences without an entry,
entries without a difference, 7 proofs that do not hold, a stale
`registry.json`, and disagreeing engines.

## What the checks do not cover

- P2 for results sees what the reference embeds. The 504 results beyond it
  rest on the agreement of the two engines.
- Both engines get the binding and the data from the same Python code. The
  column fingerprints show that R read the same values; they do not show
  that Python read the Parquet file rightly (P2 for ADaM does, cell by
  cell, with the same pyarrow).
- The classes of the 25 differences are judged; the proofs show what the
  entries say, not that "reference_error" is the right word.
- The CSR figures in the `sources` of the exceptions are those of PLAN.md
  E3 and E24; this work package did not read the CSR again.
- No R code was taken from siera, cards or cardx. Test A5 compares Python
  files only; the R files were written for this work package.
- CI has no R and no fetch cache: there the R tests are skipped and the
  gate checks 6 (in part), 7 to 14 do not run.

## The merge of `main`

`main` moved while real-2 was under way: std-1 merged (`2cb4c63`). It is
merged into `track/real` in `1e0f164`; the conflicts were in
`docs/lessons.md` (the lessons of real-2 are 23 to 26), `src/specfirst/cli.py`
and `src/specfirst/gates.py` (both gates kept). The gate above ran on the
merged tree. The ARS file std-1 compiles from its base decision vector (44
analyses) has no problem for `specfirst.machine.ars.index` and binds
completely by the rules B2 and B3; the engines were not run on it.

## Review

The reviewer, an agent with a fresh context that did not write the work,
read the diff `main..track/real` at `1e0f164` (69 files) against PLAN.md,
and this report, the gate log and the state file as they stood before this
section was written. It ran the gate in the worktree (15 of 15; the same
output as the gate log, apart from 16 lines that must differ), counted the
embedded results again with code of its own (3,735 embedded, 3,711
reproduced as printed, 23 with another value, 1 without a result of ours,
504 beyond the reference), checked each of the 25 entries of the exceptions
file from the pilot ADSL and the example, built twice more in other folders
(26 files, the same hashes as the clean clone), changed 14 entries of the
exceptions file, planted defects in the rows and in the code of both
engines, and ran both engines on 65 made-up inputs at the edges of the
rules I1 to I15. Verdict: PASS. It covers commit `1e0f164` and the three
files as the reviewer read them; their SHA-256 are in the review.

What it found:

- The gate statement holds in every check the reviewer made. The 25
  entries of the exceptions file are right. The 220 lines this report
  quotes from the gate log are in the log, in order. N1 to N7 are fixed as
  the section above says, and nothing of real-1 was broken. `PLAN.md`,
  `standard/schemas/` and `env/` are not in the diff, and nothing of real-3
  is.
- One sentence of this report was wrong and is corrected: "The merge of
  `main`" said the gate "below" (F10). The reviewer has not read the
  corrected sentence, the last paragraph of the verdict, this section or
  the section "GitHub and CI"; they were written after the review.
- Twelve findings, none blocking. They are not fixed here: a fix changes
  code and needs its own gate run. They are listed in `docs/state/real.md`
  for the first commit of real-3, as N1 to N7 of real-1 were for real-2.
  F1, F8 and F9 are for the owner.

| # | Finding | Effect on the pilot |
| --- | --- | --- |
| F1 | 3,711 is "reproduced as printed", the comparison of E2. At the decimals of the pattern 3,710 are reproduced and 25 have a class: the first quartile of age ("70" against 70.5) is counted on both sides, so 3,711 + 25 is 3,736. | The gate passes by the plan's own measure and was not changed. The numbers of the plan (E2 to E4, the gate text, section 14) are the owner's to revise. |
| F2 | The check of the proofs accepts proofs that prove nothing: `value_of_other_result` with any other result that has the embedded value; `same_under_every` and `no_alternative` for an option that cannot change the operation; `no_records` with any count that is 0. | None of the 25 entries uses these holes (the reviewer checked each), so "0 unexplained" stands. It would not stand by itself for the next reference: the formatted values in real-3, the CSR in real-4. |
| F3 | Statement 5 of `test.fisher.exact` says R's `fisher.test` allows a relative excess of 1e-7. For tables larger than 2 x 2 R allows more (between 3.2e-7 and 7.6e-7): on six 2 x 3 tables found by search the two differ by 5 to 21 percent of the p-value, and the enumeration is the exact one. Statement 6 (more than 10,000,000 tables are refused) holds for Python only, and the build does not catch the refusal. | None: every Fisher table of the pilot is 2 x 2. Such a table would stop the gate by rule R11, not pass. real-4 has 59 Fisher tests on 3 x 3 tables. |
| F4 | The Python standard deviation of a cell whose values are all equal is not always 0 (three values of 0.1, or of 98.6); R gives 0, and the engines then disagree. | None: no such cell. It would stop the gate, not pass. |
| F5 | 16 of the 65 made-up inputs: the engines differ, or only one stops. Among them a text column whose every value is the text "NA" (jsonlite reads missing values; the build stops on the fingerprint), a number as the value of a data-driven group (1e15), a control character in a group value. | None. Each stops the build or shows as a disagreement; none gives a wrong number in silence. |
| F6 | What the agreement of the engines does not prove: the binding, the choice of the columns and the preparation of the data are done once, in Python, for both, and `engine.R` has the design of `ard.py`. The 504 results beyond the reference rest on the agreement alone, and nothing asserts the number of rows (A6 prints 4,238). | The section "What the checks do not cover" says the greater part. Rule I13, on which 408 of the 504 rest, is well supported: the five Fisher p-values the example embeds with a value all differ under the nearest other reading. |
| F7 | `json_string` in `r/specfirstr/R/util.R` begins with the same five statements as `.escape_single_quote` in siera's `R/readARS.R`, three of them letter for letter. A5 reads Python files only. The reviewer cannot tell a copy from the usual way to write an escape. | siera is MIT; nothing that may not be redistributed is in the repository. See the note below the table. |
| F8 | ADR-002 takes neither way of section 13.3 but a third (our own on R's `stats`), and says so. Four of its sentences say more than its evidence; see the note below the table. | The decision not to wrap siera follows from T1 to T3. The decision against cards and cardx is a choice, and the owner's. |
| F9 | The classes. The 22 exchanged values and the median of height: `reference_error` is right. The first quartile of age: defensible. A third definition (no averaging; SAS QNTLDEF=3, R type 1) gives exactly 70, but the example has the averaged value in 68 of the 69 embedded quartiles and medians where the two differ, so it is at odds with itself. The empty p-value: the weakest; closer to a difference of rule than to a contradiction, and E3 counted it as "1 p-value is empty". | The classes are for the owner to confirm, as the section "P2 for results" says. |
| F10 | Small things in the texts: two in the state file and one in this report (corrected in the commit that adds them); `README.md` does not list std-1 as passed; the note on ars in `third_party/SOURCES.md` says nothing of it is committed, while 25 embedded values are in the exceptions file and the issue draft and three in tests; rule I3 of the registry README says less than both engines do; "every quantile definition" means the two of the registry. | Wording. |
| F11 | D1 exchanges the two arms in every analysis; the case of E3 is an exchange in one analysis (the reviewer's single exchanges are caught). The pilot cannot show four more things than this report lists: a missing analysis variable of a count; NE on a column with a missing value; the continuity correction of a chi-square test; a Fisher table larger than 2 x 2, for which the eight vectors are the whole evidence in the gate. The R side of rule I3 has no test. | The reviewer's cases agree in both engines. |
| F12 | Of the two results "equal only at the edge of the allowance", one differs by a relative 5.7e-10: a reference value rounded to ten decimals, not the floating error the code and the README name as the reason for the allowance. | Wording; the count is right. |

Notes of the executor on two findings:

- F7. The record of the executor's session shows that, for the trial of
  ADR-002, it printed lines 1 to 140 of siera's `R/readARS.R` and no other
  line of that file; the function in question is at lines 629 to 634.
  `json_string` was written as the usual way to escape a JSON string. That
  is a statement, not a check: the sentence "No R code was taken from
  siera, cards or cardx" in the section "What the checks do not cover"
  rests on no test. The fix is listed: A5 reads the R files too, and
  `json_string` is written anew so that it escapes every control character
  (F5 needs that anyway).
- F8. What the four sentences of ADR-002 should say. (a) "its analysis of
  variance needs two packages outside the lock" is true of
  `cardx::ard_stats_aov` only; `ard_stats_oneway_test(var.equal = TRUE)`,
  the same F test, runs with the locked library (T4), as do the chi-square
  and the Fisher wrapper. What is left against cards and cardx: the
  wrappers add no method, they cost time (2.4 s against 0.06 s for 200
  tests), and the descriptive defaults would have to be overridden. (b) Our
  engine calls `anova(lm())` for the analysis of variance, not the
  `stats::oneway.test` that cardx wraps; the sentence "the functions cardx
  wraps" in the section "ADR-002 in short" has the same fault. (c) T2: the
  output counts 8 analyses, not 8 value sources. (d) That siera's Fisher
  template gives an odds ratio is true of the cached files; the recorded
  output does not show it. ADR-002 itself is not changed in this commit.

## GitHub and CI

`track/real` is pushed to the owner's private repository at `1e0f164`.

No result of CI is claimed here. The push started run 43095936482 at 20:25
UTC on 2026-11-11. At 21:18 UTC it was still queued and had no job, while
GitHub's status page showed an open incident ("Impact across multiple
GitHub products including Actions, Pages, and Copilot products", opened
20:48 UTC; at 21:07 UTC: the backlog of Actions jobs is being processed).
The run before it on this branch (43081461489, on the last commit of
real-1) and the run on `main` at `2cb4c63` (43088686921, std-1) succeeded.

What CI runs (`.github/workflows/ci.yml`: the ASCII check, lint, the unit
tests) was therefore run by hand, in the worktree at `1e0f164` with the
documents of this commit as they stood but for this section, in the
environment from the lock file, with no `Rscript` on the path and no fetch
cache, as on GitHub's runner. The output, complete but for pytest's first
lines of progress dots (the script keeps the last 12 lines pytest prints):

```text
Rscript on the path: none
python: /root/.local/share/specfirst/venv-specfirst-real-17298088/bin/python
== ASCII check
ASCII check: 374 files checked, 0 with non-ASCII bytes
exit 0
== Lint
All checks passed!
exit 0
== Unit tests
.....................................ss................................. [ 74%]
........................................................................ [ 85%]
........................................................................ [ 96%]
..........................                                               [100%]
=========================== short test summary info ============================
SKIPPED [1] tests/defects/test_std1_checkers.py:393: no fetch cache: `specfirst gate std-1` runs this control on the real schema
SKIPPED [2] tests/methods/test_methods.py:79: Rscript is not installed
SKIPPED [1] tests/unit/test_ard.py:268: Rscript is not installed
SKIPPED [3] tests/unit/test_build.py:273: Rscript is not installed
SKIPPED [1] tests/unit/test_rengine.py:58: Rscript is not installed
SKIPPED [1] tests/unit/test_rengine.py:83: Rscript is not installed
665 passed, 9 skipped, 19 deselected in 241.44s (0:04:01)
pytest exit 0
```

This is not a run on GitHub: it shows that the three steps pass on this
tree without R and without the cache, not that the workflow does. The eight tests that need R are skipped there and run in the gate
(checks 5 and 6). The ASCII check was repeated on the final text of the
documents.

After the review this branch gains one commit, with five files only: this
report, the gate log, the state file, the review, and ADR-001, whose status
paragraph now records that the owner approved the kit layout additions of
its item 3 on 2026-11-11 (finding F12 of the review of real-1). Code,
tests, scripts, the registry, the schemas, `env/`, ADR-002 and the lessons
are those of `1e0f164`.

## Files

| Path | Content |
| --- | --- |
| `docs/decisions/ADR-002.md` | the decisions |
| `standard/methods/` | 7 registry entries, `registry.json`, the README with the rules B1 to B3 and I1 to I15 |
| `src/specfirst/machine/` | `registry.py`, `methods.py`, `ars.py`, `ard.py`, `rengine.py`, `results.py`; `build.py` with the results |
| `r/specfirstr/` | `run.R`, `R/util.R`, `R/methods.R`, `R/engine.R`, `R/vectors.R` |
| `kits/cdiscpilot01/` | `kit.yaml` with the result set; `gold/exceptions.yaml` |
| `src/specfirst/gates.py`, `cli.py`, `kit.py` | gate `real-2`; `specfirst methods`; result sets and the exceptions file of a kit |
| `tests/methods/` | 7 vector files, `oracle.py`, `test_methods.py` |
| `tests/defects/test_defects.py` | D1 to D5 |
| `tests/unit/` | `test_registry.py`, `test_method_functions.py`, `test_ars.py`, `test_ard.py`, `test_rengine.py`, `test_results.py`; additions to `test_build.py`, `test_kit.py`, `test_gates.py`, `test_graph.py`, `test_compare.py` |
| `tests/toy_results.py`, `tests/toy_kit.py` | the made-up study and reporting events of the unit tests |
| `tests/pilot/test_pilot.py` | A4 as changed for N1; A6-engine |
| `evidence/adr002_siera_trial.sh`, `.out` | the trial behind ADR-002 |
| `docs/upstream/ars-issue-common-safety-displays.md` | the draft of the issue; not posted |
| `docs/reports/real-2.gate.log` | the complete output of the gate on the clean clone |
| `docs/reports/real-2.review.md` | the independent review |
| `docs/state/real.md` | the state of the track: what passed, what is open, the findings F1 to F12, what real-3 is handed |
| `docs/decisions/ADR-001.md` | items 4 to 6 reworded for N2 and N7; the owner's approval of item 3 |
