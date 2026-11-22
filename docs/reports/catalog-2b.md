# catalog-2b: the content of catalog@2 and open-default@2 (ADR-020, part 2 of 3)

Work package catalog@2, track std, part catalog-2b: decision 7 of ADR-020 as
the owner answered it on 2026-11-21 (A to questions 1, 2, 3 and 5). Part
catalog-2a (the structure) merged first; part catalog-2c (the slice moved to
version 2) follows. The slice stays on (`catalog@1`, `open-default@1`) in
this part: generated kits, the reader's tasks and the kept run are unchanged.

## What changed, by issue

The column "Backlog" gives the status of each record after the freeze: a
record accepted for version 2 is done at the freeze commit.

| Issue | catalog@2 | open-default@2 | Backlog |
| --- | --- | --- | --- |
| #1 | `tfl.percent.format`: the slot `decimals` (0 to 2) in both alternatives; a probe varies it | default `one_decimal_always`, 1 decimal, for the three families (the ARS example) | i01.zero-shown, i01.decimals-slot done; i01.below-one waits |
| #2 | the FDA wording in the reading note, marked ambiguous; FDA and admiral citations | default by design: randomized and dosed when `design.randomized`, dosed otherwise | i02.* done |
| #3 | `ae.teae.end/end_of_study` removed with its two probes | default `last_dose_plus_days`, 30 days (admiral's template) | i03.* done |
| #4 | the three edge rules of emergence as fixed rules with anchors; the doubled "For every alternative:" gone | the fixed rules anchored in STANDARD.md | i04.fixed-rules done |
| #5 | `ae.teae.start/by_time_when_collected`, its fragment, phrasing and probe `ae_timed_before_timed_first_dose` | | i05.date-time done |
| #6 | the definitions say where a value timed after the dose on the first dose day goes; `demo.baseline.record` states that it agrees with ADVS | default `last_on_or_before_first_dose_date` for ADVS (admiral); post-baseline time-aware in the ADVS parent | i06.* done |
| #7 | the source of `lt65_ge65` (the ARS grouping) | default `lt65_ge65` | i07.age-default done; i07.fda-bands waits |
| #8 | the FDA citation "pooled active arms" removed | a total column in the demographics table only | i08.* done |
| #9 | `soc_alpha_pt_descending_in_column` replaces `descending_frequency_highest_dose`; citations fixed; "alphabetical" defined; probes for the new pairs | the layout reads the column | i09.* done |
| #10 | the randomized subject as a fixed rule, from the disposition record RANDOMIZED first; mITT named in the definition | RANDFL by that rule (a lookup keyed by STUDYID for the study-level fallback), RANDDT | i10.* done |
| #11 | | default `last_record` (admiral) | i11.last-record done |
| #12 | BMIBL not rounded in ADSL; the units stated | | i12.bmi-unrounded done |
| #13 | rows SERIOUS_RELATED, FATAL_RELATED, DOSE_MODIFIED; `standard_rows` in the order of the ARS example with serious related; "fatal" defined | their data subsets | i13.* done; i13.severity-rows waits |
| #14 | the FDA guide as Version 2.0 (April 2025); five citations with section, table and page | | i14.fda-guide done |
| #15 | | STANDARD.md anchored by entry ID, with status, scope, order of precedence, a source line per statement, terms, conventions, conformance rules and a change log | i15.citable-document done |
| #17 | the status words with no status for a screen failure (fixed rule); `bds.eot.record` states AVISITN 9999 and carries the unit | AEBODSYS; PARAM with the unit, AVALU; first occurrence by date then sequence; the conformance rules in STANDARD.md | i17.conformance, i17.screen-failure, i17.eot-record done; i17.positions-refused, i17.dtype-null, i17.dose-order wait |
| #18 | boundary words in the statements of `ae.teae.end`, `bds.baseline.rule`, `demo.age.groups`; fixed rules; the list of terms | the terms printed once | i18.* done |
| #20 | (2a: the entry schema v1, the `$fn` list) | the sources of every alternative printed | i20.alternative-sources done |
| #21 | `demo.race.pooling/fixed_groups` replaces `pooled_below_count`; the unscheduled visit as a fixed rule (no VISITDY, or UNSCHED in VISIT); the reading note of `tfl.population` names which sources use which set (the kept answers of N1 are in ADR-020) | `_SCHED` by the fixed rule | i21.race-map, i21.unscheduled, i21.unscheduled-house, i21.kept-answers done; i21.no-visitdy waits |
| #22 | `tfl.quantile.definition` for the demographics table only; its probe needs quartiles; "(R type 2)" in the statement | the vital signs templates fix `sas5` | i22.quantiles done |
| #23 | items 9 to 11: worsening as a fixed rule; ICH M11 words in the reading notes; the meaning of halfway | | i23.reading-words done; the rest waits |
| #24 | `trt.end.source/last_ex_record_end` and its probe | | i24.last-end-any-record done |
| #33 | | the label and time-of-day rules in STANDARD.md; the check of carried labels; `specfirst.compile.attributes` | i33.* done |

## Departures put to the owner

Three approved items are built otherwise or wait; the review (pass 1, F2)
asked that the owner hear of them before the freeze:

1. #17: a VS dataset with several positions or time points is not refused
   (i17.positions-refused waits for std-2). The refusal reads VSPOS and
   VSTPT, and the generated VS has no VSTPT.
2. #17: DTYPE is not null on collected records (i17.dtype-null waits for
   std-2). DTYPE is a key of ADVS, and yamaa refuses a missing key value.
3. #21: a visit is unscheduled when VISITDY is missing or VISIT contains
   UNSCHED, always (i21.unscheduled, as built). The approved fallback for an
   SDTM without the variable VISITDY needs a build that knows the SDTM's
   columns (i21.no-visitdy waits for std-2).

The owner's answer (2026-11-21, through the base session, in translation):
"Accept all three as built (Recommended)", option A: items 1 and 2 are
recorded as waiting for std-2, and item 3 takes admiral's reading. ADR-020
records it ("The owner's answer on the three departures"). Version 2 is
frozen as built.

## Evidence

### catalog@1 and open-default@1 do not change

From the log of the gate `catalog-2b` on a clean clone of `937ae95`
(docs/reports/catalog-2b.catalog-2b.gate.log):

```text
== [5/17] frozen: specfirst.compile.gate.frozen_check
catalog@1: frozen 2026-11-17, tree a25d42c08d37352131b9320a62c7fa2ce266cb9b (frozen as a25d42c08d37352131b9320a62c7fa2ce266cb9b)
catalog@2: draft 2026-11-21, tree ec704801f2ab16942826251e2dfcd5ef6ed0d938
open-default@1: frozen 2026-11-17, tree 7ac0f4fc4d76333817b6e3edf21e156afec38ef4 (frozen as 7ac0f4fc4d76333817b6e3edf21e156afec38ef4)
open-default@2: draft 2026-11-21, tree eaa67f26537d39dca902385ff4f451a94dcf9e46
default pair: catalog@1, open-default@1; 0 labels named by the kits of the repository
frozen versions: 0 problems
```

### The checks of version 2

The same log, the checks on (`catalog@2`, `open-default@2`):

```text
== [6/17] catalog: specfirst catalog --catalog catalog@2 --house open-default@2
catalog specfirst-m1 2: 43 entries, 61 questions (entry and unit), 97 alternatives, 9 units, 51 probes
schema and cross-references: 0 problems
compile templates on their examples: 0 problems
probes: every pair of alternatives, every slot: 0 problems
structural probes separate for any data: 0 problems
phrasings and reading notes: 0 problems
parameters set and read: 0 problems
== [7/17] public sources: specfirst catalog --sources --catalog catalog@2 --house open-default@2
43 entries, 0 without a public source
109 citations: 60 to pinned sources, checked on the fetch cache (45 with a text that must stand in the file); 49 to published documents, judged and not checked by script
== [8/17] round trip: specfirst catalog --roundtrip --catalog catalog@2 --house open-default@2
253 statements rendered and parsed back, for 139 alternatives (entry, unit and alternative)
round trip decisions to statements to decisions: 0 problems
document round trip on 61 decisions: 0 problems
== [9/17] yamaa check: specfirst catalog --yamaa --catalog catalog@2 --house open-default@2
113 decision vectors (the base and one changed decision each), 113 compiled
48 distinct sets of ADaM specs, 144 entry specs checked by yamaa (each with its house parent and one fragment per decision)
yamaa check: 0 problems
== [10/17] yamaa run: specfirst catalog --run --catalog catalog@2 --house open-default@2
48 distinct sets of ADaM specs, 144 datasets built by yamaa on the tiny study of specfirst.compile.tiny (4 subjects; this shows that the specs run, not that their values are right)
yamaa run: 0 problems
== [11/17] ARS schema: specfirst catalog --tables --catalog catalog@2 --house open-default@2
65 distinct ARS files with their layouts checked: schema, references, and that layouts and ARS name the same analyses
ARS schema and layouts: 0 problems
== [12/17] house standard: specfirst house --catalog catalog@2 --house open-default@2
house standard open-default@2: 56 defaults, 4 decisions without a default, 3 parent specs, 4 table families
house standard: 0 problems
== [13/17] migration: specfirst.compile.gate.migration_check: catalog@1 to catalog@2
catalog@1 to catalog@2: 96 and 97 alternatives; 4 added, 3 removed, 33 changed in meaning; units 0 added, 1 removed; 49 lines in migration.yaml
migration: 0 problems
== [14/17] backlog: specfirst.compile.gate.backlog_check
standard/BACKLOG.yaml: 72 records for 26 issues; 45 accepted, 10 done, 17 waits
== [15/17] defaults: specfirst.compile.gate.defaults_check: open-default@2
open-default@2 for catalog@2: 61 questions (entry and unit), 56 defaults, 1 by design, 4 stated as none
== [16/17] templates: specfirst.compile.gate.templates_check: catalog@2, open-default@2
catalog@2 and open-default@2: every directive of the compile and house templates read whole; directives $get, $if, $for, $dict, $pick, $concat, $fn
templates: 0 problems
```

(Lines that only give a folder or a note are left out here; the log has
them.) The freeze commit moves the 45 accepted records to done; the 17 that
wait name the work package that takes them.

### Planted defects (rule R5)

`tests/defects/test_catalog2_checkers.py`, each on a copy of `standard/`
that passes clean first: a reading note that names a house default; a fixed
rule ID that is a unit; a fixed rule ID used twice; a fixed rule and a
default that cite an unknown source; a term added without a line of
migration.yaml; a term that names no entry; a carried variable labelled by
the parent; a house document that drops a fixed rule, has its cases out of
order, or states the cases of a default by design otherwise.
`tests/unit/test_catalog2.py`: the parser refuses a fixed rule stated
otherwise, cases out of order, an anchor that names another entry, a
changed line, a positional anchor in a document anchored by entry, a fixed
rule without its anchor or in the section of another unit, and
`parse_document` on a document with cases. Each new check was seen to fail
on its plant before it counted.

### The parents of open-default@2 on changed data

`tests/unit/test_house2_on_tiny.py` builds (`catalog@2`, `open-default@2`)
on copies of the tiny study changed so that the rules this part added are
reached: RANDFL from the disposition record and, without one, from the
planned arm; one PARAM per PARAMCD, with its unit, and AVALU; no end of
study status for a screen failure; AEBODSYS carried; the first occurrence by
date, then sequence. The changes are chosen so that the rules of version 1
would give other values; the test builds version 2 only.

### Generated kits are the same bytes

Kits 1 to 4 of the seed `gen-2a`, written on clones of `main` before part
catalog-2a (`325a8f2`; the same kits as those of `869b8c0`, the code merged
in `9dc6b20`) and of `937ae95`, in the Linux file system, inside the heavy
lock:

```text
$ python -m specfirst gen kits --out c2b2 --count 4 --seed gen-2a     # clone of 937ae95
kit 1 of the set: sfpbt5zj, train, 127 files; 14 of 22 decisions separated on the twin
kit 2 of the set: sfmyncmq, train, 127 files; 15 of 22 decisions separated on the twin
kit 3 of the set: sfg5vbvq, train, 126 files; 15 of 21 decisions separated on the twin
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin
$ find c2b2 -type f | wc -l
511
$ diff -r main c2b2 && echo identical
identical
$ sha256sum c2b2/kit-00?/kit.yaml
a5a1da67d4dac93017a3364ba86f00177e59210aa16059b683996b293489e177  c2b2/kit-001/kit.yaml
79e43bbd9a826cf9ddad47d197e543122ebdcfeba4fcb128432e9d8997640976  c2b2/kit-002/kit.yaml
46dfe55ee714fe83ee9b9d27748fcacd6f19611ce0d047685045d432bae86c52  c2b2/kit-003/kit.yaml
75addb7d7b70d358e3f740be3eab1338c22c83a6149121987aa0bd7fe090bfbc  c2b2/kit-004/kit.yaml
```

The slice stays on version 1 in this part, so the kits, the reader's tasks
and the kept dry run of arm R do not move.

### Gates on clean clones

Each gate on a fresh clone with a fresh install and fetch, one at a time
under the heavy lock, on at most four processors:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh <wp> /mnt/d/trial_work/specfirst/.git 937ae95
```

| Gate | Commit | Unit tests | Result | Log |
| --- | --- | --- | --- | --- |
| catalog-2b | 937ae95 | 1336 passed, 30 deselected | GATE catalog-2b: PASS (17 checks) | docs/reports/catalog-2b.catalog-2b.gate.log |
| std-1 | 937ae95 | 1336 passed, 30 deselected | GATE std-1: PASS | docs/reports/catalog-2b.std-1.gate.log |
| gen-2a | 937ae95 | 1336 passed, 30 deselected | GATE gen-2a: PASS | docs/reports/catalog-2b.gen-2a.gate.log |
| gen-3a | 937ae95 | 1336 passed, 30 deselected | GATE gen-3a: PASS | docs/reports/catalog-2b.gen-3a.gate.log |
| read-1a | 937ae95 | 1336 passed, 30 deselected | GATE read-1a: PASS | docs/reports/catalog-2b.read-1a.gate.log |
| read-2a | 937ae95 | 1336 passed, 30 deselected | GATE read-2a: PASS (19 checks; "arm R, kept dry run" among them: the kept run R-task-04119188ff71 still checks) | docs/reports/catalog-2b.read-2a.gate.log |

The freeze commit changes versions.yaml, the pinned trees, the status of
the backlog records and the rendered documents of version 2; the gates
`catalog-2b` and `std-1` run again on it.

### The freeze

After the owner's answer on the three departures, commit `5d48e21` freezes
version 2: `standard/versions.yaml` gives `catalog@2` and `open-default@2`
the status `frozen` with their trees, `versions.PINNED` holds the same
trees, the header of catalog.yaml and the README of `catalog@2` say frozen,
STANDARD.md of `open-default@2` is rendered again (its status line only),
and the 45 backlog records accepted for version 2 are done. Seven tests
that needed version 2 to be a draft now build one in a copy of
`standard/`. The trees are git's:

```text
$ git rev-parse 5d48e21:standard/catalog@2 5d48e21:standard/houses/open-default@2
1a3dcc6575849a57f47257b8daaf5eb30d995be9
550cb664b4d64a304f9d14bbd995379d16602601
```

From the log of the gate `catalog-2b` on a clean clone of `5d48e21`
(docs/reports/catalog-2b.freeze.catalog-2b.gate.log):

```text
== [4/17] unit tests: pytest -m "not evidence" -q
1337 passed, 30 deselected in 489.07s (0:08:09)
== [5/17] frozen: specfirst.compile.gate.frozen_check
catalog@2: frozen 2026-11-21, tree 1a3dcc6575849a57f47257b8daaf5eb30d995be9 (frozen as 1a3dcc6575849a57f47257b8daaf5eb30d995be9)
open-default@2: frozen 2026-11-21, tree 550cb664b4d64a304f9d14bbd995379d16602601 (frozen as 550cb664b4d64a304f9d14bbd995379d16602601)
frozen versions: 0 problems
== [6/17] catalog: specfirst catalog --catalog catalog@2 --house open-default@2
catalog specfirst-m1 2: 43 entries, 61 questions (entry and unit), 97 alternatives, 9 units, 51 probes
== [14/17] backlog: specfirst.compile.gate.backlog_check
backlog: 0 problems
GATE catalog-2b: PASS
```

| Gate | Commit | Unit tests | Result | Log |
| --- | --- | --- | --- | --- |
| catalog-2b | 5d48e21 | 1337 passed, 30 deselected | GATE catalog-2b: PASS (17 checks) | docs/reports/catalog-2b.freeze.catalog-2b.gate.log |
| std-1 | 5d48e21 | 1337 passed, 30 deselected | GATE std-1: PASS | docs/reports/catalog-2b.freeze.std-1.gate.log |

The gates gen-2a, gen-3a, read-1a and read-2a are not run again: the
freeze changes no file the slice reads (the slice names `catalog@1` and
`open-default@1`), and in code it adds two entries to `versions.PINNED`;
they passed on `937ae95` above. The merge into main is tagged `catalog@2`
and `open-default@2`.

### Review

`docs/reports/catalog-2b.review.md`: pass 1 not signed (F1 blocking, F2 to
F10 to fix, F11 to F14 notes). `937ae95` answers F1, F3 to F9, F11, F13
and F14; F2 is the three departures above, put to the owner; F10 is this
section. Pass 2 signed, on the condition of the owner's answer to F2, with
one new note (F15). The commit after it answers F15 and the rest of F13
and F14 before the freeze: a statement of `tfl.percent.format` that reads
for 0, 1 and 2 decimals; a term that named its entry twice; four reading
notes that stated this house's choices; the unit of a parameter taken by
subject, then sequence number, not by the order of the input, and the
conformance rule that says so; a test of a visit named unscheduled that
has a planned day. Pass 3 signed, on the same condition. The owner
accepted the three departures as built, which answers F2. Pass 4, on the
freeze commit `5d48e21`, signed on the condition that the gates
`catalog-2b` and `std-1` pass on it; they do (above). Its note F16:
docs/state/std.md still called version 2 a draft (fixed with the merge),
and the README of `open-default@2` says STANDARD.md is "Rendered by
`specfirst house --write`", which holds while a house is a draft; the
README is frozen with that wording, and neither changes a check or a
default.
