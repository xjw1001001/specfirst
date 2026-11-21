# Review of catalog-2b (ADR-020, part 2 of 3), pass 1

Reviewer: a fresh-context reviewer (rule R7), read only. Scope: commit
`3405070` on `track/std`, `git diff 9dc6b20 3405070` (88 files, 2019
insertions, 446 deletions). Version 2 is a draft; the slice of ADR-005 stays
on version 1. Read: CLAUDE.md, ADR-020 (decision 7, the owner's answer,
"Carried out / catalog-2b"), standard/BACKLOG.yaml, standard/catalog@2/
migration.yaml, docs/reports/catalog-2b.md, issues #1 to #24 and #33 (saved
JSON, body and comments), and the whole diff. No file was changed but this
one; nothing was committed; no model was called.

## Commands and output (R8)

Windows git, read only:

```text
$ git diff --stat 9dc6b20 3405070        (last line)
 88 files changed, 2019 insertions(+), 446 deletions(-)
$ git diff --stat 9dc6b20 3405070 -- standard/catalog@1 standard/houses/open-default@1 \
    standard/schemas standard/versions.yaml src/specfirst/gen src/specfirst/harness src/specfirst/score
(no output)
$ git rev-parse 3405070:standard/catalog@1 3405070:standard/houses/open-default@1 \
    3405070:standard/catalog@2 3405070:standard/houses/open-default@2
a25d42c08d37352131b9320a62c7fa2ce266cb9b
7ac0f4fc4d76333817b6e3edf21e156afec38ef4
10a3a0123d5e9b91526e51f5967205c1cb6a03b0
c64ca96a00aed1f4794724289a384fa2396bb12b
PS> git diff 9dc6b20 3405070 | Select-String <a Windows user folder, its WSL mount, token, secret, password>
0 lines
PS> bytes above 127 in the UTF-8 text of the same diff
0
```

WSL, light commands only (no build), on a clone of the commit, from a
scratch script outside the repository:

```text
$ git clone -q --no-local /mnt/d/trial_work/specfirst/.git /tmp/rv2b-3405070
$ git -C /tmp/rv2b-3405070 checkout -q 3405070
$ cd /mnt/d/trial_work/specfirst-std && . scripts/env.sh
$ export SPECFIRST_ROOT=/tmp/rv2b-3405070 PYTHONPATH=/tmp/rv2b-3405070/src; cd /tmp/rv2b-3405070
$ specfirst catalog --catalog catalog@2 --house open-default@2 | tail -5
compile templates on their examples: 0 problems
probes: every pair of alternatives, every slot: 0 problems
structural probes separate for any data: 0 problems
phrasings and reading notes: 0 problems
parameters set and read: 0 problems
$ specfirst catalog --sources --catalog catalog@2 --house open-default@2 | tail -3
43 entries, 0 without a public source
109 citations: 60 to pinned sources, checked on the fetch cache (45 with a text that must stand in the file); 49 to published documents, judged and not checked by script
public sources: 0 problems
$ specfirst catalog --roundtrip --catalog catalog@2 --house open-default@2 | tail -3
253 statements rendered and parsed back, for 139 alternatives (entry, unit and alternative)
round trip decisions to statements to decisions: 0 problems
document round trip on 61 decisions: 0 problems
$ specfirst house --catalog catalog@2 --house open-default@2 | tail -2
house standard open-default@2: 56 defaults, 4 decisions without a default, 3 parent specs, 4 table families
house standard: 0 problems
$ specfirst house | tail -2
house standard open-default@1: 58 defaults, 4 decisions without a default, 3 parent specs, 4 table families
house standard: 0 problems
$ python - <<'EOF'   # frozen, migration, backlog, defaults and templates checks
for name in ("frozen_check", "migration_check", "backlog_check", "defaults_check", "templates_check"):
    getattr(specfirst.compile.gate, name)(Path("."), print)
EOF
catalog@1: frozen 2026-11-17, tree a25d42c08d37352131b9320a62c7fa2ce266cb9b (frozen as a25d42c08d37352131b9320a62c7fa2ce266cb9b)
catalog@2: draft 2026-11-21, tree 10a3a0123d5e9b91526e51f5967205c1cb6a03b0
open-default@1: frozen 2026-11-17, tree 7ac0f4fc4d76333817b6e3edf21e156afec38ef4 (frozen as 7ac0f4fc4d76333817b6e3edf21e156afec38ef4)
open-default@2: draft 2026-11-21, tree c64ca96a00aed1f4794724289a384fa2396bb12b
default pair: catalog@1, open-default@1; 0 labels named by the kits of the repository
frozen versions: 0 problems
catalog@1 to catalog@2: 96 and 97 alternatives; 4 added, 3 removed, 30 changed in meaning; units 0 added, 1 removed; 38 lines in migration.yaml
migration: 0 problems
standard/BACKLOG.yaml: 66 records for 26 issues; 42 accepted, 9 done, 15 waits
backlog: 0 problems
open-default@2 for catalog@2: 61 questions (entry and unit), 56 defaults, 1 by design, 4 stated as none
defaults: 0 problems
catalog@2 and open-default@2: every directive of the compile and house templates read whole; directives $get, $if, $for, $dict, $pick, $concat, $fn
templates: 0 problems
```

The Python tree hashes of the two drafts equal git's (`10a3a01`, `c64ca96`).

yamaa's own rule on key values, read in the fetch cache (read only):

```text
$ sed -n 55,72p /root/.local/share/specfirst/cache/yamaa/rules/output.md   (excerpt)
### OUTPUT-3. Every artifact row's combined key values are non-missing and unique
...
Fails: `duplicate_key`, `missing_key`.
$ grep -n -i "null\|missing" /root/.local/share/specfirst/cache/yamaa/rules/windows.md   (excerpt)
202:Evidence: ... windows.json::numbering_and_rank_order_integers_above_2_53_exactly_with_missing_values_last_in_one_missing_partition, ...
```

A probe of the parents on a changed tiny study (units in VSSTRESU, a visit
UNSCHEDULED with a planned day, a SCREEN FAILURE, adverse events whose
sequence and date orders differ; three yamaa builds under /tmp) was written
but not run: run without the lock it was refused by the session's permission
check, and under the lock it could not start:

```text
$ flock -w 10 /run/lock/specfirst-heavy.lock taskset -c 0-3 python probe.py /tmp/rv2b-3405070
probe not run: the heavy lock is held (exit 1)
```

The parents were therefore judged by reading them (item 5 below); pass 2 may
run the probe under the lock.

The gate log of a clean clone of `3405070`, the only final one at the time of
writing:

```text
build/gates/catalog-2b/clean-clone.log: commit:     3405070
1322 passed, 30 deselected in 564.78s (0:09:24)
113 decision vectors (the base and one changed decision each), 113 compiled
48 distinct sets of ADaM specs, 144 datasets built by yamaa on the tiny study of specfirst.compile.tiny (4 subjects; ...)
GATE catalog-2b: PASS
```

The logs of std-1, gen-2a, gen-3a, read-1a and read-2a in build/gates/ are
still those of earlier commits (`78c9084`, `24cc6ac`); pass 2 reads them.

## Findings

### F1 (blocking): the reading notes of catalog@2 name the defaults of open-default@1

`standard/catalog@2/knowledge/`: 30 notes end with "Silent documents: use the
house default `<alternative>` and cite the house standard", the defaults of
open-default@1. Five of them are not the defaults of open-default@2, the house
catalog@2 is paired with:

| Note, line | Says | open-default@2 |
| --- | --- | --- |
| pop.safety.rule.md:36 | `at_least_one_dose` | by design: `randomized_and_dosed` when `design.randomized` |
| bds.baseline.rule.md:34 | `last_before_first_dose` | `last_on_or_before_first_dose_date` (#6) |
| bds.window.tiebreak.md:32, and :24-26 ("choose `closest_then_earlier`, the house default") | `closest_then_earlier` | `last_record` (#11) |
| demo.age.groups.md:30 | `lt65_65to80_gt80` | `lt65_ge65` (#7) |
| tfl.columns.total.md:31 | `all_arms` | `all_arms` for the demographics table only, `none` for the three others (#8) |

pop.safety.rule.md was edited in this commit and kept its line; 8 other notes
were changed to "use the house default and cite the house standard". The notes
are what a reader reads (the reader's skills are rendered from them in
catalog-2c), so a reader on a silent document would state a default that the
house document contradicts. The knowledge is outside the meaning hash, and
catalog@2 freezes after this review: once frozen, the fix is catalog@3.
tfl.population.md:35-37 also names defaults per family (they agree with
version 2, but defaults are the house's since decision 2).

Fix: drop the alternative from every "use the house default" line of
catalog@2, rewrite bds.window.tiebreak.md:24-26 without naming a default, and
consider a catalog check (with a plant) that a reading note of a catalog with
`entry_schema: catalog-entry.v1` names no alternative as the house default.

### F2 (should fix): three departures from the approved table of decision 7 are not put to the owner, and two backlog reasons are inaccurate

The owner approved decision 7 as proposed (question 1, A) and the freeze
follows this review without the owner (question 5, A). Three items were
carried out otherwise; ADR-020 "Carried out / catalog-2b" records them, but
neither the report nor a question names them as departures:

1. #17 "a VS with several positions or time points per visit refused" waits
   for std-2 (`i17.positions-refused`). The deferral is defensible: the tiny
   study holds neither VSPOS nor VSTPT, and the run check compiles without the
   SDTM's columns, so a parent that reads VSTPT fails there. But the reason at
   standard/BACKLOG.yaml:140 says "which the generated and the tiny SDTM do not
   hold (VSTPT)": the generated VS holds VSPOS (src/specfirst/gen/sdtm.py:577)
   and lacks VSTPT. STANDARD.md states the rule as it is (line 442), so the
   reduction is not silent in the document, only in the data.
2. #17 "DTYPE null on collected records" waits (`i17.dtype-null`). The reason
   holds: DTYPE is a key of ADVS (advs.yaml `keys`), and yamaa's OUTPUT-3
   refuses a missing key value (`missing_key`, quoted above). A sequence key
   (ASEQ) would lift it; std-2 is a fair place.
3. #21: decision 7 says "a visit is unscheduled when VISITDY is missing, or, in
   an SDTM without VISITDY, when VISIT contains UNSCHED" (the issue: "Add 'or
   VISIT contains UNSCHED' for SDTM without VISITDY"). The fixed rule
   (entries/bds.unscheduled.use.yaml:10-15) and the parent
   (adam/advs.yaml:223) apply the VISIT test always, and an SDTM without the
   variable VISITDY, the case the fallback was asked for, is left to the
   SDTM-aware compile of ADR-014. The two readings differ for a visit with a
   planned day whose name contains UNSCHED, and the approved fallback is not
   delivered for its own case. The record `i21.unscheduled`
   (BACKLOG.yaml:188-190) still gives the approved wording as its reason.

Fix: correct the two reasons (BACKLOG.yaml:140 and :190); add a `waits`
record for the VISIT fallback of an SDTM without VISITDY; list the three
departures in the report for the base session to confirm with the owner, or
not, before the freeze.

### F3 (should fix): house changes without a record of the house layer

Decision 4 steps a house on any change of a parent or a template, and the
house has no migration file: the backlog is its only record. These changes of
open-default@2 have no record of layer `house` for open-default@2; they are
covered only by catalog records:

- adam/advs.yaml:217-226, `_SCHED` with the VISIT test (`i21.unscheduled`,
  layer catalog);
- ars/vitals-by-visit.yaml:124-129 and layout/vitals-by-visit.yaml:36,
  `quantile_definition` fixed to `sas5` (`i22.quantiles`, layer catalog);
- layout/ae-soc-pt.yaml:44-47, the sort `column` (`i09.sort-replaced`, layer
  catalog).

Fix: one house record each (or one per issue), `version: open-default@2`.

### F4 (should fix): post-baseline is stated three ways

- catalog.yaml:38-40, the term "post-baseline": "on that date and timed after
  the first dose". The definitions (bds.baseline.rule: "timed at or after the
  dose"; scheduled_baseline_visit: "its time is not earlier") and the parent
  (advs.yaml:236, `_ADTM >= TRTSDTM`) put a value timed at the dose time in
  post-baseline. The term should say "at or after".
- entries/bds.window.table.yaml:43, the notes of all three alternatives: "A
  record is post-baseline when its date is after the treatment start date."
  Under `bds.baseline.rule/last_before_first_dose` (and
  `scheduled_baseline_visit`) that is no longer true; STANDARD.md:199 prints it
  as the meaning of `[bds.window.table]`. A change of these notes is in the
  meaning hash: three migration lines (backlog `i06.post-time-aware` or
  `i06.first-dose-day`).
- adam/advs.yaml:15, the header still says "post-baseline a row dated after the
  treatment start date" (comment only).

### F5 (should fix): a "Source:" line names the sources of the entry as the sources of the statement

src/specfirst/compile/house.py:361 prints `alternative.sources or
entry.sources`. When the default alternative has no sources of its own, the
line lists the entry's, and the preface (STANDARD.md:14) calls them "the public
sources of the statement". Several support another alternative:
`[bds.window.tiebreak]` (last record, STANDARD.md:203-207) cites "the benchmark
of closest visit selection"; `[bds.baseline.rule]` (by date, :189-193) cites
"baseline defined as the value of a named visit"; `[ae.teae.start]` (by date,
:159-163) cites "comparison of date and time"; `[demo.race.pooling]` (not
pooled, :133-135) cites the pooled race group. #15 asked for a source line "that
lets a reader judge a default". Fix: label the fallback "Sources of the entry:"
(and say so in the preface), or give the default alternatives their own
sources. Minor: `cited()` (house.py:274) squeezes blanks inside quoted text, so
the ARS value `(  0.0)` prints as `( 0.0)` (STANDARD.md:257, 259 and four more).

### F6 (should fix): the house's choice for randomized studies cites the sentence the catalog calls ambiguous

defaults.yaml:23-26 gives `randomized_and_dosed` for `design.randomized` with
one source, the FDA guide section 2.1.1 ("exposed to at least one dose of
randomized treatment"); knowledge/pop.safety.rule.md:19-22 (this commit) calls
that wording ambiguous between the two alternatives. #2 based the
recommendation on that sentence and on the pilot's SAFFL. Fix: add the pilot's
SAFFL (`p7`, cdiscpilot01/spec/yamaa/adsl.yaml, the pinned find "Y if
ITTFL='Y' and TRTSDT ne missing", already a source of the entry) to the choice,
or word the FDA citation as one reading.

### F7 (should fix): three new branches of checks have no planted defect (R5)

- checks.py:697-700, a source of a default whose `ref` is not in sources.yaml
  (item 6, "the sources of defaults"): no plant in tests/defects/.
- checks.py:191-193, the sources of fixed rules read by the check "public
  sources": no plant (an unknown `ref`, or a pinned `find` not in the file).
- checks.py:82, a fixed rule ID equal to a unit of its entry: the plant covers
  "used twice" only.

The other new checks fail on plants: terms (test_catalog2_checkers.py),
fixed rule ID twice (:94-97), cases and fixed rules stated, carried
labels (:98-102), G1 pinned versions (test_versions_checkers.py:97-101,
162-167), `$fn` as a mapping (:104-108, 213-214). (The line numbers of
test_catalog2_checkers.py: terms :90-93, cases and fixed rules :52-78.)

### F8 (should fix): the parser accepts mixed anchors and drops a case-shaped line silently

src/specfirst/compile/standard_form.py:413-514 (`parse_full`). Each line is
judged alone, so:

- a positional document may hold entry anchors, fixed rules and cases (the
  renderer refuses them, :325-326; the parser does not);
- any line `[<entry>/<n>] <statement>` is taken as a case (:487-493), and
  `parse_document` (:402-411) returns without it and without an error. In a
  positional document, or for an entry whose default is not by design, a
  statement then disappears from the records (callers: score/scorer.py:258,
  gen/documents.py:280 and :577, score/hand.py:283, cli.py:254);
- a fixed rule is not checked against the section of its entry's unit, and a
  fixed rule's text without its anchor is not flagged (:455 tests statements
  only). For STANDARD.md the house check catches both through the rendering;
  for other documents nothing does.

Fix: one anchor style per document; refuse fixed rules and cases in a
positional document; refuse a case of an entry when `parse_document` (not
`parse_full`) is asked, or return it. Reader citations do resolve:
score/reading.py:98-112 finds `[<anchor>] ` at the start of a line, which
holds for `[ae.teae.start/no_start_date]` and `[pop.safety.rule/1]`; a
citation of `pop.safety.rule` without its case does not resolve, as intended.

### F9 (should fix): PARAM is derived per record, so one PARAMCD can have two PARAMs

adam/advs.yaml:131-153: PARAM is "VSTEST (VSSTRESU)" when the record has a unit
and VSTEST alone when it has none. A not-done record (VSSTRESN and VSSTRESU
null) is common in a real VS; its PARAM then differs from the other records of
the same VSTESTCD, which breaks the one-to-one PARAMCD and PARAM of ADaMIG.
The tables group by PARAMCD (ars/vitals-by-visit.yaml:46-59), so no number
changes; the dataset does. The generated VS always has a unit
(gen/sdtm.py:579), and the tiny VS never has one, so no check sees it. Fix:
take the unit per parameter (a lookup keyed by STUDYID and VSTESTCD of the
first non-missing VSSTRESU), or state the per-record rule and its effect in the
conformance rule (house.yaml:86).

### F10 (should fix): the report has no evidence yet

docs/reports/catalog-2b.md:37-39: "(Filled in from the commands and gate
logs below.)" R8 needs the commands and their output: the gates on clean
clones, the comparison of kits 1 to 4 of seed gen-2a (511 files, `diff -r`),
the unit suite. The table says "done" for records whose status is `accepted`.

### F11 (note): the defined terms are outside the meaning hash

catalog.yaml:16-40. A term "has the meaning the named entry gives it, in every
statement", but no alternative's meaning and no check across versions covers
`terms`. Nothing is hidden at this step (all terms are new and restate hashed
text), but a changed term in catalog@3 would pass the check "migration".
Compare `terms` between versions, with a migration line per changed term.

### F12 (note): the freeze cannot use `specfirst house --write`

house.py:288-300 renders the status from standard/versions.yaml ("frozen on
<date>" once frozen), and cli.py:196-199 refuses `--write` for a frozen house.
The freeze commit must write STANDARD.md with the frozen status line by
calling `house.standards_document` directly (or the command must allow the
freeze), and then compute the tree.

### F13 (note): the tiny study does not reach the new branches

The run check passed (144 datasets), but the tiny study has no unit in
VSSTRESU (tiny.py:118, `""`), no visit whose name contains UNSCHED with a
planned day, no SCREEN FAILURE, and no two treatment-emergent events of one
term whose sequence and date orders differ, so PARAM with a unit, the VISIT
test of `_SCHED`, EOSSTT null and the AOCC order are not run. Under version 2
only S1 is randomized (S1 has the one DS record RANDOMIZED, so S2 and S3 fall
under the study-level rule), while the docstring (tiny.py:6-10) calls S2 and S3
randomized. A missing ASTDT sorts last in the AOCC windows (yamaa's default,
quoted above); the conformance rule (house.yaml:85) does not say so.

### F14 (note): smaller points

- `{decimals} decimals` renders "have 1 decimals" (STANDARD.md:253, 315, 357);
  the alternatives keep the IDs `one_decimal_*` with a slot of 0 to 2 (ADR-020
  records the choice).
- The fixed rules of `pop.randomized.rule`, `disp.status.record` and
  `bds.unscheduled.use` are carried out only in the parents of open-default@2
  (adsl.yaml:131-142 and :162-173, advs.yaml:217-226), not in the catalog's
  templates; a second house must carry them out again, and no check says so.
- Rules the parents still fix and STANDARD.md does not list: ANL01FL on the
  baseline and end-of-treatment rows, AVISIT `Baseline` with AVISITN 0, CHG on
  post-baseline rows only (#17, "General").
- `specfirst.compile.attributes`: `compare` takes `Attribute`s whose `kind`
  for a reference is not defined, and nothing builds them from a reference
  dataset yet (ADR-020 says no build calls it); `carried_label_problems` skips a
  variable that gen.sdtm does not list, and covers the parents, not the
  catalog's fragments.
- `evidence: cited` is missing on three citations that carry claims of the
  owner-side review: entries/demo.bmi.rule.yaml:26 (the ad_advs.R part; sources.yaml
  says only two admiral files were read), entries/tfl.ae.socpt.sort.yaml:38
  and entries/tfl.percent.format.yaml:40 (p6, no `find`). The sort citation
  also keeps "(PLAN.md, E25)", which reproduced the cells of 14-5.01, for the
  term order the review found.
- #24 also asked for a build check (no subject with a treatment start date)
  and a probe with EXDOSE missing on every record; decision 7 does not take
  them, and the backlog has no record for them.

## What I checked and found right

1. Decision 7, first table. Every row is done in catalog@2 or open-default@2
   as approved, or waits with a record, except the three departures of F2:
   #1 (slot `decimals` 0 to 2, default `one_decimal_always` with 1, a probe
   varies it), #2 (cases by design; the FDA wording in the reading note,
   marked ambiguous), #3 (`end_of_study` and its two probes gone; 30 days),
   #4 (four fixed rules with anchors; "For every alternative:" printed once per
   entry), #5 (`by_time_when_collected`, fragment, phrasings, probe
   `ae_timed_before_timed_first_dose`; the pairs of both probes are right), #6
   (default by date for ADVS, the ADSL rule unchanged and said to agree; every
   definition says where a dose-day value timed after the dose goes; `_POST`
   time-aware and equal to `not _PRE` on the dose day under the time rule), #7,
   #8 (the "pooled active arms" citation gone; a total in demographics only),
   #9 (the new alternative, its slot and probes; both citations fixed;
   "alphabetical" defined), #10 (fixed rule, mITT named, RANDFL and RANDDT),
   #11, #12, #13 (three choices, the standard rows in the ARS order with serious
   related, fatal defined; the subsets), #14, #15, #17 (all but the two waits),
   #18, #20, #21 (but the reading of F2), #22 (single unit, `needs` on its probe,
   "(R type 2)"; the vitals templates fix `sas5`), #23 items 9 to 11 (the
   halfway note matches machine/methods.py:322, `Decimal(repr(value))`), #24,
   #33. Each change was compared with its issue's own text.
2. Meaning. The check "migration" passes; I found no line whose backlog record
   is wrong (pop.safety.rule changes by its notes under #10, not_pooled by its
   question under #21, and so on). The house changes outside the hash are
   recorded but for F3.
3. Standard form. Positional rendering is unchanged in code
   (standard_form.py:376-399 builds the same lines when `anchors="position"`),
   STANDARD.md of open-default@1 equals its rendering (test_catalog2.py:71-75
   and `specfirst house`), and catalog@1 and open-default@1 keep their trees.
   The parser refuses a fixed rule stated otherwise, cases out of order, an
   anchor that names another entry, and a malformed anchored line (plants in
   test_catalog2.py:54-68); for its gaps see F8.
4. STANDARD.md. Status, scope, order of precedence (PLAN.md section 17,
   decision 17 says the same), terms, conventions, sources, fixed rules,
   cases, conformance rules and change log are rendered from house.yaml,
   defaults.yaml, catalog.yaml and versions.yaml. The conventions agree with
   the code where code exists: n non-missing and SD with n - 1, none for
   n = 1 (machine/methods.py:82-100), a blank cell for a missing result
   (machine/layout.py:402); no grid builder sorts organ classes and terms yet,
   so "alphabetical" binds no code today. The conformance lines agree with the
   parents, but for F9.
5. Parents. RANDFL: the subject's DS record RANDOMIZED, else N when the study
   has one (lookup keyed by STUDYID, adsl.yaml:35-47 and :131-142), else the
   ARMCD test; RANDDT from that record. EOSSTT: SCREEN FAILURE gives null before
   COMPLETED and DISCONTINUED, ONGOING without a record (adsl.yaml:162-173).
   AEBODSYS carried with its SDTMIG label. AOCC by ASTDT then AESEQ (missing
   last). PARAM and AVALU (but F9); the end-of-treatment record carries
   VSSTRESU (templates/bds.eot.record.yaml:16-18). `_POST` (advs.yaml:236)
   matches the three definitions. `_SCHED` matches the fixed rule.
6. Checks and plants: see F7 for the three missing plants; the others fail on
   their plants.
7. Citations. The check "public sources" passes on the pair (45 pinned `find`
   texts stand in their files, the ARS `(  0.0)`, `AnlsGrouping_03_AgeGp`,
   `AnalysisSet_01_ITT` and `AnlsGrouping_07_Pt` among them). The FDA guide is
   Version 2.0 with `confirmed` still "cited"; every FDA citation names a
   section, table or page that its issue gives; the SDTMIG claim of #10 is
   marked cited, as the issue says it was not opened. For gaps see F6 and F14.
8. Version 1 unchanged (trees above; the check "frozen" passes, the pins of G1
   hold); the slice's code (gen, harness, score) untouched; the unit suite on a
   clean clone gave 1322 passed, 30 deselected. The comparison of kits 1 to 4
   (511 files) I did not repeat; F10 asks for it in the report.
10. No credential, local user path or non-ASCII byte in the diff.

## What catalog-2c must do because of 2b (item 9; not defects of 2b)

- Removed alternative `ae.teae.end/end_of_study`: gen/decisions.py:73, :77 and
  :223; gen/probes.py:142, :158 and the recipes of
  `ae_starts_after_end_of_study` and `ae_between_window_end_and_end_of_study`
  (:619-627, :755-756); gen/present.py:492-493; gen/core_findings.yaml:195;
  gen/reference.py:323; the store of natural-form texts keeps its old text
  (append only).
- Rows of the AE summary: gen/reference.py:49-52 (five codes in the old order),
  :397; gen/probes.py:184-190 (`_ALL_ROWS`); gen/decisions.py:179-180 and
  :213-214; score/pilot.py:74-77 (ARS analyses to row codes): SERIOUS_RELATED
  in `standard_rows`, FATAL before DISCONTINUATION, and labels and counts for
  SERIOUS_RELATED, FATAL_RELATED and DOSE_MODIFIED.
- Percentages: gen/reference.py:387-389 assumes one decimal; the value now
  carries `decimals`; harness/gate.py:769-770 flips the rule without the slot.
  The house default shows zero as `0 (0.0)`, so the gold grids change.
- New alternatives of the slice's units need probe recipes and decision
  vectors: `ae.teae.start/by_time_when_collected`
  (`ae_timed_before_timed_first_dose`), `trt.end.source/last_ex_record_end`
  (`undosed_record_after_last_dose`), the new rows, the randomization rule.
- Defaults by design: `house.defaults()` leaves `pop.safety.rule` out without
  design features; gen.gold, score/hand.py (HAND01) and the harness must pass
  the features to `house.default_decisions(..., features)`, and gold cites
  `pop.safety.rule/1` or `/2`.
- New defaults in the slice: emergence ends 30 days after the treatment end
  date, the safety set randomized and dosed, the new rows and the zero
  percentages: HAND01's table, the gold of every kit and the kept run change.
- Parents: generated studies carry a DS record RANDOMIZED (gen/subjects.py:321),
  so RANDFL is read from DS; generated screen failures carry SCREEN FAILURE
  (gen/subjects.py:312-313), so their EOSSTT becomes null; RANDDT, AEBODSYS and
  AVALU are new columns and PARAM gains the unit (gen/define.py and the gold
  ADaM bytes change); AOCC flags may move; BMIBL is no longer rounded.
- The reader: harness/task.py:246 tells the reader that the house document
  numbers its statements (`[1/s3]`); version 2 anchors by entry, with fixed
  rules a `conflict` may cite and cases by design. harness/knowledge.py reads
  the defaults of the catalog (2a). The reading notes after F1.
- Natural-form texts for the statements of the slice that change: ae.teae.end
  (`last_dose_plus_days`, "that day included"), tfl.percent.format (both,
  `{decimals}`), tfl.ae.summary.rows (`standard_rows`), and the new
  alternatives the generator may draw.

Verdict: NOT SIGNED (pass 1)

## Pass 2

Scope: `git diff 3405070 9c565c8` on `track/std`: `937ae95` (the fixes of
F1, F3 to F9, F11, F13 and F14; 52 files) and `9c565c8` (the report's evidence
and six gate logs; F10). F2 is with the owner. Read only, as in pass 1; no
model call; no test run by me (the heavy lock was held, and the gate logs
below ran the suite).

### Commands and output (R8)

```text
$ git log --oneline -3
9c565c8 catalog-2b: the report's evidence and six gate logs on 937ae95
937ae95 catalog-2b: the findings of the review, pass 1 (F1, F3 to F9, F11, F13, F14)
3405070 catalog-2b: the content of catalog@2 and open-default@2 (ADR-020, decision 7; draft)
$ git grep -n -E "house default|default \`" 9c565c8 -- standard/catalog@2/knowledge   (summary)
45 matching lines: "use the house default (and cite the house standard)", "take the default of the output's family" or "has no house default"; none names an alternative
$ git grep -n "1 decimals" 9c565c8 -- standard/houses/open-default@2/STANDARD.md
STANDARD.md:253, :315, :357 (unchanged)
$ git grep -n "the generated and the tiny SDTM do not hold" 9c565c8 -- docs standard
docs/decisions/ADR-020.md:499
```

WSL, light commands only, on a clone of `9c565c8` (scratch script outside
the repository, as in pass 1):

```text
$ git clone -q --no-local /mnt/d/trial_work/specfirst/.git /tmp/rv2b-9c565c8 && git -C /tmp/rv2b-9c565c8 checkout -q 9c565c8
$ specfirst catalog --catalog catalog@2 --house open-default@2 | tail -3
structural probes separate for any data: 0 problems
phrasings and reading notes: 0 problems
parameters set and read: 0 problems
$ specfirst catalog --sources ... | tail -1
public sources: 0 problems
$ specfirst catalog --roundtrip ... | tail -2
round trip decisions to statements to decisions: 0 problems
document round trip on 61 decisions: 0 problems
$ specfirst house --catalog catalog@2 --house open-default@2 | tail -1
house standard: 0 problems
$ specfirst house | tail -1          (open-default@1)
house standard: 0 problems
$ python (gate.frozen_check, migration_check, backlog_check, defaults_check, templates_check)
catalog@1: frozen 2026-11-17, tree a25d42c08d37352131b9320a62c7fa2ce266cb9b (frozen as a25d42c08d37352131b9320a62c7fa2ce266cb9b)
catalog@2: draft 2026-11-21, tree ec704801f2ab16942826251e2dfcd5ef6ed0d938
open-default@1: frozen 2026-11-17, tree 7ac0f4fc4d76333817b6e3edf21e156afec38ef4 (frozen as 7ac0f4fc4d76333817b6e3edf21e156afec38ef4)
open-default@2: draft 2026-11-21, tree eaa67f26537d39dca902385ff4f451a94dcf9e46
frozen versions: 0 problems
catalog@1 to catalog@2: 96 and 97 alternatives; 4 added, 3 removed, 33 changed in meaning; units 0 added, 1 removed; 49 lines in migration.yaml
migration: 0 problems
standard/BACKLOG.yaml: 72 records for 26 issues; 45 accepted, 10 done, 17 waits
backlog: 0 problems
defaults: 0 problems
templates: 0 problems
$ python (two plants of mine on the parser)
positional document with a case line: refused: line 16: the anchor 1/s2 is by position, the document's anchors are by entry
entry document with a case of trt.start.source: parse_full accepted it
```

The six gate logs committed in `9c565c8` (docs/reports/catalog-2b.<wp>.gate.log):

```text
catalog-2b: commit: 937ae95 | 1336 passed, 30 deselected | GATE catalog-2b: PASS
std-1:      commit: 937ae95 | 1336 passed, 30 deselected | GATE std-1: PASS
gen-2a:     commit: 937ae95 | 1336 passed, 30 deselected | GATE gen-2a: PASS
gen-3a:     commit: 937ae95 | 1336 passed, 30 deselected | GATE gen-3a: PASS
read-1a:    commit: 937ae95 | 1336 passed, 30 deselected | GATE read-1a: PASS
read-2a:    commit: 937ae95 | 1336 passed, 30 deselected | GATE read-2a: PASS ("arm R" among its checks)
```

`9c565c8` changes only docs/reports/, so the gates on `937ae95` stand for it.

### The findings of pass 1

| Finding | State | What I checked |
| --- | --- | --- |
| F1 (blocking) | fixed | Every "Silent documents" line of catalog@2 says "use the house default" without an alternative; bds.window.tiebreak.md:24-26 says "take the tie rule of the house standard"; tfl.population.md:35-36 no longer names the defaults. A catalog check (checks.py, for a catalog without defaults in its entries) fails on a planted note (test_catalog2_checkers.py, "a reading note that names a house default"). |
| F2 | pending (owner) | The two backlog reasons are corrected (BACKLOG.yaml, i17.positions-refused, i21.unscheduled "as built"); `i21.no-visitdy` waits for std-2; `i21.unscheduled-house` added; the report lists the three departures under "Departures put to the owner". The owner's answer is not in yet. |
| F3 | fixed | `i09.layout-column`, `i21.unscheduled-house`, `i22.vitals-fixed`, each of layer house for open-default@2. |
| F4 | fixed | The term (catalog.yaml:38-40) and the notes of bds.window.table say "timed at or after a timed first dose", as the definitions and advs.yaml `_POST` do; three migration lines for bds.window.table (`i06.first-dose-day`); the ADVS header says the same. |
| F5 | fixed | house.py prints the alternative's own sources, or "the sources of the entry, ..." (52 lines of STANDARD.md), and the preface says what such a line is; `cited()` keeps the text of a citation, so `(  0.0)` stands as the ARS writes it. |
| F6 | fixed | defaults.yaml cites the pilot's SAFFL (`p7`, with its find) first and calls the FDA sentence "one reading of an ambiguous sentence". |
| F7 | fixed | Plants for a fixed rule ID that is a unit, a fixed rule that cites an unknown source (check "public sources"), and a default that cites an unknown source (house check). |
| F8 | fixed | One anchor style per document; a fixed rule stands in a section of its entry's unit and never without its anchor; `parse_document` refuses a document with cases, and `specfirst parse` reads with `parse_full` and says what it left out. Plants in test_catalog2.py for each. My own plant: a case line in a positional document is refused. |
| F9 | fixed | advs.yaml takes PARAM's unit from a lookup `VS_UNIT` keyed by STUDYID and the test code (the first non-missing VSSTRESU); test_house2_on_tiny.py builds a VS whose SYSBP record 4 has no unit and finds one PARAM per PARAMCD and AVALU null on that record. |
| F10 | fixed | The report's Evidence section shows the frozen trees, every check of version 2, the plants, the tests on changed tiny data, the kits of seed gen-2a (511 files, `diff -r` identical, kit.yaml hashes) and the six gates. |
| F11 | fixed | migration.py compares `terms` between versions; migration.yaml has a line per added term (`i18.terms`); a plant adds a term without a line. |
| F12 | pending (freeze) | Not changed: `house --write` still refuses a frozen house while the status line reads versions.yaml (cli.py:196-199, house.py:288-300). The freeze commit must render STANDARD.md through the function; the report says the freeze commit re-renders the documents of version 2. |
| F13 | fixed in part | tiny.py says that under open-default@2 only S1 is randomized; test_house2_on_tiny.py reaches RANDFL from DS and from the planned arm, PARAM and AVALU, EOSSTT null for a screen failure, AEBODSYS and the AOCC order by date. The VISIT test of `_SCHED` (a visit with a planned day whose name contains UNSCHED) is still reached by no test; the missing-ASTDT order is now a conformance rule (house.yaml), not tested. |
| F14 | fixed in part | Three citations marked `evidence: cited`, "(PLAN.md, E25)" dropped from the term order; the conformance rules gain the baseline record, CHG, ANL01FL and the missing-ASTDT order; ADR-020 records that the parents carry out three fixed rules; `i24.build-check` (done earlier, score/candidate.py:208-221) and `i24.probe-no-exdose` (waits). Left as they were: "have 1 decimals" (STANDARD.md:253, 315, 357) and the points on `specfirst.compile.attributes`. |

### New findings (pass 2)

#### F15 (note): small remainders of the fixes

- docs/decisions/ADR-020.md:497-500 ("Carried out / catalog-2b") still says
  that the generated and the tiny SDTM do not hold VSPOS and VSTPT; the
  backlog and the report now say it right (the generated VS holds VSPOS).
- house.yaml:86 (STANDARD.md:442) still says "PARAM is the test name with
  its standard unit": since F9 it is the first non-missing standard unit of
  the test in the study, and AVALU is the record's own. `VS_UNIT` orders by
  VSSEQ alone (advs.yaml, intermediates), so when two subjects' first
  records of a test carry different units, which one wins rests on the input
  order; ordering by USUBJID too would name it.
- `parse_full` accepts a case of an entry whose default is not by design
  (my plant above). For STANDARD.md the house check still fails on it (the
  single statement goes missing and the file differs from its rendering);
  `parse_document` refuses any case. A check that only entries with a
  default by design have cases would close it.
- The pin of the pilot's SAFFL in defaults.yaml (`find`) is checked by no
  script: defaults_problems checks the `ref` only. The same text is checked
  as a source of the entry.
- The new check of reading notes matches "house default" followed by a
  backtick only. "the house takes the randomized set"
  (tfl.population.md:31) and "this entry has no house default" (four notes)
  still state what open-default@2 holds; they agree with it.
- The report's table still says "done" for records whose status is
  `accepted`; the freeze commit moves them to done.
- STANDARD.md:29 renders "(as bds.baseline.rule says) (`bds.baseline.rule`)".

None of these changes a number, a default or a check result.

### Nothing the fixes broke that I found

- catalog@1 and open-default@1 keep their trees (pinned and recorded), and
  STANDARD.md of open-default@1 still equals its rendering.
- The slice's code (gen, harness, score) is untouched by both commits; the
  gates gen-2a, gen-3a, read-1a and read-2a pass on `937ae95`, with arm R's
  kept run, and the kits of seed gen-2a are the same bytes as main's.
- The stricter parser reads every document the gates read: positional
  documents keep one style, and the house documents of both versions parse.
- The migration check of version 2 now needs 49 lines; all name accepted
  records.
- Both commits are ASCII (the gate's ASCII check: 840 files, 0 with
  non-ASCII bytes) and hold no local user path.

### Verdict

Nothing blocking is left. F2 waits for the owner's answer on the three
departures, and F12 belongs to the freeze commit. I sign on the condition
that the owner accepts the three departures of F2 as the report lists them.
If the owner rejects one, the work it names changes, and that change needs
another review before the freeze.

Verdict: SIGNED (pass 2, conditional on the owner's answer to F2)

## Pass 3

Scope: `git diff 9c565c8 66f558d` (13 files, 60 insertions, 30 deletions):
the answers to F15 and to the rest of F13 and F14, before the freeze. Read
only; no model call.

### Commands and output (R8)

```text
$ git diff --stat 9c565c8 66f558d        (last line)
 13 files changed, 60 insertions(+), 30 deletions(-)
$ git grep -n -E "house default\W*\`|house takes|this entry has no house default" 66f558d -- standard/catalog@2/knowledge
(no output)
```

WSL, light commands only, on a clone of `66f558d` (scratch script outside
the repository):

```text
$ git clone -q --no-local /mnt/d/trial_work/specfirst/.git /tmp/rv2b-66f558d && git -C /tmp/rv2b-66f558d checkout -q 66f558d
$ specfirst catalog --catalog catalog@2 --house open-default@2 | tail -2
phrasings and reading notes: 0 problems
parameters set and read: 0 problems
$ specfirst catalog --sources ... | tail -1
public sources: 0 problems
$ specfirst catalog --roundtrip ... | tail -3
253 statements rendered and parsed back, for 139 alternatives (entry, unit and alternative)
round trip decisions to statements to decisions: 0 problems
document round trip on 61 decisions: 0 problems
$ specfirst house --catalog catalog@2 --house open-default@2 | tail -1
house standard: 0 problems
$ specfirst house | tail -1          (open-default@1)
house standard: 0 problems
$ python (gate.frozen_check, migration_check, backlog_check, defaults_check, templates_check)
frozen versions: 0 problems
catalog@1 to catalog@2: 96 and 97 alternatives; 4 added, 3 removed, 33 changed in meaning; units 0 added, 1 removed; 49 lines in migration.yaml
migration: 0 problems
backlog: 0 problems
defaults: 0 problems
templates: 0 problems
$ flock -w 10 /run/lock/specfirst-heavy.lock taskset -c 0-3 python -m pytest -q \
    tests/unit/test_house2_on_tiny.py tests/unit/test_catalog2.py tests/defects/test_catalog2_checkers.py
exit 1   (the lock is held by a gate; the tests were not run by me)
```

For the tests, the report and the coordinator say that 73 targeted tests
pass, ruff and the ASCII check are clean, and a planted `_SCHED` that reads
`_VISITDY IS NOT NULL` alone fails the new test. I did not repeat those
runs; the gates of the freeze commit will.

### The items of this commit

| Item | State | What I checked |
| --- | --- | --- |
| F14, "have 1 decimals" | fixed | Both statements of `tfl.percent.format` read "The number of decimals of percentages in {output} is {decimals}, ..."; the six phrasings follow; STANDARD.md:253, 315, 357 read "... is 1, ...". The alternatives were already lines of migration.yaml (`i01.decimals-slot`), so no line is added, and the migration check still passes. |
| F15, the term | fixed | catalog.yaml and STANDARD.md:29 name `bds.baseline.rule` once. |
| F15, the reading notes | fixed | ae.related.values, pop.efficacy.rule and tfl.vs.scope say "when the house standard states no default for this entry"; tfl.population.md names which public sources use which set, and leaves the choice to the house standard. No note of catalog@2 states a choice of this house (the grep above). |
| F15, `VS_UNIT` | fixed | `order_by: [VS.USUBJID, VS.VSSEQ]` (advs.yaml), and the conformance rule (house.yaml, STANDARD.md:442) says "the first non-missing standard unit of the test in the study, by subject and sequence number", and that AVALU is the record's own unit. |
| F15, ADR-020 | fixed | ADR-020:497-500: the generated SDTM holds VSPOS but no VSTPT, the tiny SDTM neither. |
| F15, the report's table | fixed | A sentence says that the "Backlog" column gives the status after the freeze. |
| F13, `_SCHED` | fixed | test_house2_on_tiny.py gives S1's record 5 (`UNSCHEDULED 3.1`) a planned day of 17 and asserts that it has no AVISIT, while records 4 and 6 keep WEEK 2 and WEEK 4. The record is post-baseline (2024-03-26), so only `_SCHED` can withhold its analysis visit under `nominal_visit`. |
| F15, `parse_full` accepts a case of a default not by design | note, left | The house check fails on it for STANDARD.md, and `parse_document` refuses any case. |
| F15, the pilot SAFFL `find` in defaults.yaml | note, left | No script checks it. The same text is checked as a source of the entry. |
| F14, `specfirst.compile.attributes` | note, left | As in pass 1. |
| F12 | pending (freeze) | The freeze commit renders STANDARD.md through `house.standards_document`, as the coordinator describes it. |
| F2 | pending (owner) | Unchanged. |

### New findings (pass 3)

None. The fixes touch no code under src/, no file of version 1 and nothing
of the slice. I found nothing they broke.

### Verdict

Nothing blocking is left. Two items are open: F2 waits for the owner, and
F12 belongs to the freeze commit, which I will look at when it comes. The
signature of pass 2 stands, on the same condition.

Verdict: SIGNED (pass 3, conditional on the owner's answer to F2)

## Pass 4 (the freeze, 5d48e21)

Scope: `git diff 66f558d 5d48e21` (11 files, 127 insertions, 73 deletions):
the owner's answer on F2 and the freeze of `catalog@2` and `open-default@2`
(F12). Read only; no model call; no test run by me.

### Commands and output (R8)

Windows git, read only:

```text
$ git diff --stat 66f558d 5d48e21        (last line)
 11 files changed, 127 insertions(+), 73 deletions(-)
$ git rev-parse 5d48e21:standard/catalog@2 5d48e21:standard/houses/open-default@2 \
    5d48e21:standard/catalog@1 5d48e21:standard/houses/open-default@1
1a3dcc6575849a57f47257b8daaf5eb30d995be9
550cb664b4d64a304f9d14bbd995379d16602601
a25d42c08d37352131b9320a62c7fa2ce266cb9b
7ac0f4fc4d76333817b6e3edf21e156afec38ef4
PS> standard/BACKLOG.yaml: the 45 removed lines, with "status: accepted" read as "status: done",
    equal the 45 added lines
True
PS> in 5d48e21:standard/BACKLOG.yaml: "status: accepted" 0, "status: done" 55, "status: waits" 17
$ git grep -n -i draft 5d48e21 -- standard/catalog@2 standard/houses/open-default@2 docs/state/std.md   (excerpt)
docs/state/std.md:100:  `open-default@1`) and version 2 is a draft no kit may name.
(the other hits are "layout draft 0", which is a format version, not a status)
```

WSL, light commands only, on a clone of `5d48e21` (scratch script outside
the repository):

```text
$ specfirst catalog --catalog catalog@2 --house open-default@2 | tail -1
parameters set and read: 0 problems
$ specfirst catalog --sources ... | tail -1
public sources: 0 problems
$ specfirst catalog --roundtrip ... | tail -1
document round trip on 61 decisions: 0 problems
$ specfirst house --catalog catalog@2 --house open-default@2 | tail -1
house standard: 0 problems
$ specfirst house | tail -1          (open-default@1)
house standard: 0 problems
$ specfirst house --write --house open-default@2      (on the scratch clone)
open-default@2 is frozen or not listed in standard/versions.yaml: its STANDARD.md is not written (ADR-020)
exit 1
$ git -C /tmp/rv2b-5d48e21 status --short
(no output)
$ python (gate.frozen_check, migration_check, backlog_check, defaults_check, templates_check)
catalog@1: frozen 2026-11-17, tree a25d42c08d37352131b9320a62c7fa2ce266cb9b (frozen as a25d42c08d37352131b9320a62c7fa2ce266cb9b)
catalog@2: frozen 2026-11-21, tree 1a3dcc6575849a57f47257b8daaf5eb30d995be9 (frozen as 1a3dcc6575849a57f47257b8daaf5eb30d995be9)
open-default@1: frozen 2026-11-17, tree 7ac0f4fc4d76333817b6e3edf21e156afec38ef4 (frozen as 7ac0f4fc4d76333817b6e3edf21e156afec38ef4)
open-default@2: frozen 2026-11-21, tree 550cb664b4d64a304f9d14bbd995379d16602601 (frozen as 550cb664b4d64a304f9d14bbd995379d16602601)
default pair: catalog@1, open-default@1; 0 labels named by the kits of the repository
frozen versions: 0 problems
catalog@1 to catalog@2: 96 and 97 alternatives; 4 added, 3 removed, 33 changed in meaning; units 0 added, 1 removed; 49 lines in migration.yaml
migration: 0 problems
standard/BACKLOG.yaml: 72 records for 26 issues; 55 done, 17 waits
backlog: 0 problems
defaults: 0 problems
templates: 0 problems
```

### What I checked

| Item | State | What I checked |
| --- | --- | --- |
| F2 | resolved | ADR-020, "The owner's answer on the three departures (2026-11-21)": option A, "Accept all three as built". Items 1 and 2 of #17 wait for std-2, and #21 takes admiral's reading. The report quotes the same answer under "Departures put to the owner". The backlog records (`i17.positions-refused`, `i17.dtype-null`, `i21.unscheduled` "as built", `i21.no-visitdy`) agree with it. |
| F12 | fixed | STANDARD.md of open-default@2 changes in its status line only ("Status: frozen on 2026-11-21."). The house check, which compares the file with its rendering from versions.yaml, passes. `house --write` refuses the frozen house, and the refusal left the clone clean. |
| The trees | right | versions.yaml and `versions.PINNED` hold the same trees for catalog@2 and open-default@2. They equal git's trees of 5d48e21, and the check "frozen" computes them in Python. The trees of version 1 are unchanged. |
| The backlog | right | The 45 accepted records are done, with no other change to any line. No record is left accepted, so the check "backlog" holds that no record is accepted for a frozen version. The plant for that case now sets one record back to accepted for open-default@2, and the message names it. |
| The tests | right | The tests that needed a draft build one in a copy of standard/ (`_drafted` in test_versions.py, and the plant `_kit_names_draft`). Each still proves the refusal of a draft. Each also shows that the frozen version 2 may now be named (`require_usable`, `task.kit_catalog`). The pin test names all four trees. |
| The slice | unchanged | The default pair stays (`catalog@1`, `open-default@1`) (`versions.DEFAULT_CATALOG`, `DEFAULT_HOUSE`), and the repository's kits name no label. The commit touches no file of catalog@1, open-default@1, gen, harness or score. |

### On the gates left out

I agree with not running gen-2a, gen-3a, read-1a and read-2a again on
5d48e21:
- The freeze changes no file the slice reads, and in code it adds only two entries to `versions.PINNED`.
- Within the slice, `versions.yaml` matters only through the labels its kits name, which are version 1.
- The kept run of arm R is bound by bytes to catalog@1, the house of version 1 and the record schema, all unchanged.
- These four gates passed on 937ae95, and nothing they read has changed since.

What the freeze can reach (the version tests and the checks "frozen" and
"backlog") is run by the unit suite and by the gates catalog-2b and std-1
on clean clones of 5d48e21. Their GATE lines had not come in when I wrote
this.

### Findings (pass 4)

#### F16 (note): the handover still calls version 2 a draft

docs/state/std.md:100 says "version 2 is a draft no kit may name". The
file lies outside the frozen folders; the merge can update it.
standard/houses/open-default@2/README.md still says that STANDARD.md is
"Rendered by `specfirst house --write`". That holds for a draft, and the
README is now frozen as it is. Neither changes a check or a default.

### Verdict

Nothing blocking is left. The owner accepted the three departures (F2), and
the freeze renders the status line through its function (F12). I sign on
the condition that the gates catalog-2b and std-1 pass on clean clones of
5d48e21 and that their logs, committed with the merge, show it. If either
fails, the change that makes it pass needs another look before the merge.

Verdict: SIGNED (pass 4, conditional on the gates catalog-2b and std-1 on 5d48e21)
