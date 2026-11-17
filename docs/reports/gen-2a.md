# gen-2a Gold and verification, slice "adverse event summary first": report

Date: 2026-11-17. Branch: `track/gen`. Part gen-2a of ADR-005, decision 1.
Depends on gen-1a, std-1 after N1 (`catalog@1`) and real-3a, all on `main`
at `843c890`.

## Verdict

The gate script passed, twice: `scripts/clean_clone_gate.sh gen-2a` exited
0 on a clean clone of commit `3c503de`, and again on a clean clone of
`f2dac3b`, which holds what was changed after pass 1 of the review. Each
time after a fresh install and a fresh fetch, each time 13 of 13 checks.
The complete output of the second run is `docs/reports/gen-2a.gate.log`
(398 lines); the section "The gate" quotes it. The numbers below are
the same in both runs, but for the planted defects: 17 in the first.

- Ten kits were each written twice by processes of their own: 1,216 files,
  none differs (P1).
- Every cell of every grid equals a hand calculation that shares nothing
  with the machine: 422 cells of the gold grids, visible and twin, and the
  grids of 509 mutated builds (P2).
- Every cell that prints a number has a complete path to SDTM columns and
  a decision behind it (P3).
- In every kit every applicable decision is separated on the twin, and
  over the ten kits every pair of alternatives of every decision is
  separated somewhere. One decision cannot be: `date.studyday.origin`,
  which no cell of this output reads. It is recorded as `unseparated`
  (P4).
- The Python engine and the R engine agree on all 766 results.
- 21 planted defects inside the gate were each seen by the check they
  were planted for (rule R5).
- The gate of gen-1a passes again on the same commit, CORE included, after
  the findings of its review were settled. A first attempt at one of them
  failed that gate and was corrected (lesson 40).

What the gate does not prove, said here and under "Limits": "applicable"
is read as "the log of probes claims a probe for it under the decisions of
the kit"; a decision that the output reads without such a claim may stay
unseparated in a kit, and the log lists each case. Three points are for
the owner, at the end.

The independent review (rule R7) is in `docs/reports/gen-2a.review.md`.
Pass 1 did not sign: one finding blocks (G1, the reading of "applicable"
above), and the reviewer says the choice it leaves is the owner's. The
section "Review" says what the review found and what was done about it.
By PLAN.md section 2.3 the part has not passed until the review is signed.

## What gen-2a asks for, and where it stands

ADR-005, decision 1: "Sample decisions of the slice within the house
standard. Compile. Build with both engines on the visible data and on the
twin. Splits." Gate: "The gate of gen-2 for the one output: 10 kits pass P1
to P4, every applicable decision of the slice is separated on the twin, the
engines agree."

| Item | State | Where |
| --- | --- | --- |
| The eight findings of pass 2 of the gen-1a review, first | done in the first two commits; the gate of gen-1a passes again | section "The first commits" |
| Decisions of the slice sampled within `open-default@1` at `catalog@1`, with the field `reaches` of the log of probes | done: 22 entries of four units; every decision is the house default or, with a chance of 0.45, another alternative; ten scenarios so that a set of kits reads every decision | `src/specfirst/gen/decisions.py` |
| Compile | done, with the compiler of std-1; the specs of a kit name the house standard that the kit ships | `gold.compile_records` |
| Build with both engines, on the visible data and on the twin | done: yamaa through the runner of the machine, the Python and the R result engine, a grid with its mock shell and pages, the trace graph | `src/specfirst/gen/gold.py`, `display.py` |
| P1 to P4 | done; what each means for a generated kit is in the section "The four properties" | `verify.py`, `reference.py`, `kits.py` |
| Manifest | done: `kit.yaml` with the hash of every file | `kits.generate` |
| Splits (section 6.7) | done: by the place of a kit in its set; held-out factors; the seed never in a file | `kits.py`, `decisions.HELD_OUT` |
| The separation proof: both alternatives built on the twin | done, for every decision of every kit: section "Separation" | `verify.mutate` |
| The open point on yamaa's `not_before` | settled by experiment: section "not_before" | `tests/unit/test_gen_gold.py` |
| Gate `gen-2a`; each new check fails on a planted defect first | done: 13 checks, 21 planted defects inside the gate | `src/specfirst/gates.py`, `gen/gate2.py` |
| `specfirst gen kit`, `gen kits`, `gen verify` | done | `gen/command.py` |

`PLAN.md`, `standard/schemas/` and the catalog are not changed. Changed
outside the track's own folder, each for a reason ADR-007 gives: the method
registry (one new display rule, one option), and two words in
`specfirst.machine.lineage`.

Not in gen-2a: documents in natural form (gen-3a), the scorer (read-1a),
the other three table families. None was started.

## The first commits: the findings of the gen-1a review

| Finding | What was done |
| --- | --- |
| F22 `reaches` promises less than it reads | `REACHES` is now a condition on the decision vector that `probes.reaches` evaluates: the rows a difference needs, the exact length of the window for `trt.end.source`, and the two interplays. The first mutations then corrected five more claims (lesson 43). |
| F27 `repeated_key` compares the number only | It compares the subjects as the kind `probe` does: every issue a detail row that names its subject, and the subjects exactly those of the repeated records. Planted: a finding of the right size about other subjects. |
| F27 `term_problems` joins the two codelists of DSDECOD; no COUNTRY; no study codelists | The codelist of DSDECOD follows DSCAT; DM.COUNTRY and the codelists of the study (arms, elements, causality, treatment names) are checked. Three planted values inside the gate. |
| F28 `GENERATOR` unchanged | `gen-1a.2` with the first commit, `gen-2a.1` now. |
| F28 the epoch of the event of `no_exposure_end_date` | A record after the end of the participation is in FOLLOW-UP. The first attempt left the epoch empty; the gate of gen-1a failed on it (below). |
| F24 TAETORD of a screening element without an arm | Empty: TAETORD is the order within the planned arm, and such a subject has none. |
| F28 no check reads `env/lock.sh` | `specfirst doctor` reads it: every lock has its command, with its input, its output and hashes. Planted: the script as it was committed before the review. |
| F28 the message "clone kept" | The script says that the clone does not last. |
| F26 the reason of `probe-dosed-but-not-randomized` | It says that SDTMIG v3.4 does not allow the record. |
| F21, F23 cancellations | Not removed from the data. A kit whose claimed pairs do not separate is not written (section "Separation"); what a scorer must know is in `docs/state/gen.md`. |

The gate of gen-1a, on a clean clone, twice:

First on a clean clone of `2a09187`, the commit with the findings. It
failed in one check of eight:

```text
$ flock /run/lock/specfirst-heavy.lock bash scripts/clean_clone_gate.sh gen-1a
...
seed gen-1a-9 twin   : 562 rules (314 passed, 191 not applicable, 19 with issues, 38 not executable); 95 findings, 1 unexplained
  unexplained: CORE-000701 AE (issue reported, 2 issues, SFH7ULLD-102-040, SFH7ULLD-103-008): EPOCH is missing for clinical subject-level observation.
seed gen-1a-10 visible: 562 rules (320 passed, 191 not applicable, 13 with issues, 38 not executable); 89 findings, 1 unexplained
  unexplained: CORE-000701 AE (issue reported, 1 issues, SFTN76GA-104-005): EPOCH is missing for clinical subject-level observation.
...
PASS  environment          0.3 s
PASS  lint                 0.0 s
PASS  unit tests          60.3 s
PASS  identical hashes      7.8 s
FAIL  CDISC CORE         888.9 s
PASS  controlled terms      0.7 s
PASS  probes               0.6 s
PASS  ASCII                0.0 s
GATE gen-1a: FAIL
clean clone gate gen-1a: FAIL ('specfirst gate gen-1a --clean' exited 1; clone: /tmp/specfirst-clean-0C6Pzo/specfirst, which does not last)
```

Every twin, and the visible data where they carry one of the two probes,
had one unexplained finding: the two planted events that start after the
end of the participation, whose epoch that commit left empty. CORE asks
for an epoch on every subject-level record. The complete log of this run
was overwritten by the next one; the lines above are from the output of
the command. The second planted event of F28 is not an edge case to hide
behind an entry of `core_findings.yaml`: the epoch was wrong before
(TREATMENT) and wrong after (empty). Commit `3944407` gives such a record
the epoch FOLLOW-UP (lesson 40).

Then on a clean clone of `3c503de`, which holds all the code of gen-2a,
and once more on a clean clone of `f2dac3b`, after the changes that
followed the review (finding G8 changed the field `reaches` of the log of
probes). Both runs passed, 8 of 8 checks, each after a fresh install and
a fresh fetch. The complete output of the last run is
`docs/reports/gen-2a.gen-1a.gate.log` (188 lines):

```text
$ flock /run/lock/specfirst-heavy.lock bash scripts/clean_clone_gate.sh gen-1a
clean clone gate gen-1a
commit:     f2dac3b07f6614c37de47233e0edfe135574fc65
...
lock script: env/lock.sh writes 4 lock files, 0 problems
doctor: ok
...
gate gen-1a at commit f2dac3b07f6614c37de47233e0edfe135574fc65 (clean)
...
945 passed, 22 deselected in 138.97s (0:02:18)
...
10 seeds, each generated twice, by this process and by a process of its own (hash seed 1, time zone Pacific/Kiritimati, locale C, its own working folder): 510 files and 2799 subjects per build, the manifests included, catalog specfirst-m1 1
identical hashes: 0 problems
...
seed gen-1a-1 visible: 562 rules (323 passed, 191 not applicable, 10 with issues, 38 not executable); 86 findings, 0 unexplained
seed gen-1a-1 twin   : 562 rules (315 passed, 191 not applicable, 18 with issues, 38 not executable); 94 findings, 0 unexplained
... (18 more lines, one per dataset: 84 to 94 findings, 0 unexplained in each)
findings by explanation, over all runs:
    660  engine-invalid-operator (cannot_run)
    280  engine-unknown-rule-type (cannot_run)
    120  engine-unknown-operation (cannot_run)
     40  engine-unsupported-attribute (cannot_run)
    180  engine-join-type (cannot_run)
     40  engine-list-startswith (cannot_run)
    220  split-dataset-name (dataset)
     20  sv-has-no-sequence-number (repeated_key)
     20  no-findings-about-domain (every_record)
     20  treatment-emergence-is-a-decision (every_record)
     20  trial-design-domains-not-in-the-study (every_record)
     20  define-xml-not-seen-by-the-rule (every_record)
     40  invented-drug-has-no-code (study)
     16  probe-randomized-never-dosed (probe)
     48  probe-dosed-but-not-randomized (probe)
     17  probe-first-exposure-date-differs (probe)
     32  probe-actual-arm-differs (probe)
     32  probe-event-after-end-of-study (probe)
every report names the datasets handed over with their numbers of records, Define-XML 2.1.0 and the terminology sdtmct-2025-09-26
CORE on 20 datasets (10 seeds, visible and twin): no unexplained finding; the pinned source is unchanged
...
planted defect: a milestone term in a disposition event, COUNTRY = XXX and AEREL = MAYBE are reported: DS.DSDECOD = 'RANDOMIZED' SFATXTPG-101-001 of a record with DSCAT 'DISPOSITION EVENT': not a term of NCOMPLT
95 terms of 22 codelists and the trial summary parameters agree with the package; 755202 values of controlled variables in 20 datasets checked, the country codes and the codelists of each study included: 0 problems
...
PASS  environment          0.3 s
PASS  lint                 0.0 s
PASS  unit tests         139.3 s
PASS  identical hashes      7.8 s
PASS  CDISC CORE         889.8 s
PASS  controlled terms      0.7 s
PASS  probes               0.6 s
PASS  ASCII                0.0 s
GATE gen-1a: PASS

clean clone gate gen-1a: PASS (clone: /tmp/specfirst-clean-KYSJkM/specfirst)
```

The findings are those of the gate of gen-1a, entry by entry: 1,825 in
all, none unexplained, no entry unused. The finding of `repeated_key`
(CORE-000544 on SV) now passes on its subjects, not only on its number.
The check of controlled terms reads 755,202 values where it read 709,791:
the country codes and the codelists of each study are new. The 21 reports
of CORE of this run are kept outside the repository
(`/root/scratch-gen2a/gate-gen-1a/core/` on the WSL machine).

## The gate

Gate text of PLAN.md section 13.5 (gen-2), which ADR-005 limits to the one
output: "10 kits pass P1 to P4. Every applicable decision is separated on
the twin. The engines agree."

Command, run in Ubuntu 24.04 under WSL2 as root, from the worktree of
`track/gen`, inside the lock that all sessions use for heavy runs. The
script clones the repository, checks out the commit, installs everything
new under one temporary folder and fetches the pinned sources new; the
wrapper copies the log out of the clone in the same command (lesson 39):

```text
$ flock /run/lock/specfirst-heavy.lock bash scripts/clean_clone_gate.sh gen-2a
clean clone gate gen-2a
repository: /mnt/d/trial_work/specfirst/.git
commit:     f2dac3b07f6614c37de47233e0edfe135574fc65
clone:      /tmp/specfirst-clean-uaKxeJ/specfirst
environment and cache: /tmp/specfirst-clean-uaKxeJ/env
...
$ bash env/install.sh
...
CDISC CORE v1.0.0 at f3282a0d870b: 0 differ
system lock: 32 packages recorded, 0 differ
lock script: env/lock.sh writes 4 lock files, 0 problems
doctor: ok

$ specfirst fetch
...
fetch: every pin verified

$ specfirst gate gen-2a --clean
gate gen-2a at commit f2dac3b07f6614c37de47233e0edfe135574fc65 (clean)
```

It exited 0: 13 of 13 checks. The complete output is
`docs/reports/gen-2a.gate.log` (398 lines). This is the run on
`f2dac3b`; the run on `3c503de`, before the review, passed the same 13
checks with the same numbers (its log is in the repository at commit
`ce70734`). The checks that gen-2a adds, with their planted defects:

```text
== [5/13] unit tests: pytest -m "not evidence" -q
945 passed, 22 deselected in 138.22s (0:02:18)
-- PASS unit tests (138.6 s)

== [6/13] method vectors: SPECFIRST_STRICT=1 pytest tests/methods -s -q
...
6 passed in 1.25s
-- PASS method vectors (1.4 s)

== [7/13] pilot tests: SPECFIRST_STRICT=1 pytest tests/pilot -s -q
...
6 passed in 45.80s
-- PASS pilot tests (46.0 s)

== [8/13] kits: specfirst.gen.gate2.kits_pass: 10 kits, each written twice; P1 to P4
planted defect: a build that stamps its data with a time that depends on its process: 26 files differ, for example twin/data/sdtm/vs.json: the hashes differ
planted defect: a build whose manifest names the folder it was built in: 1 files differ, for example kit.yaml: the hashes differ
planted defect: one changed cell of the grid: row 'Any adverse event', column 'Placebo': the grid '99 ( 81.2)', the reference '39 ( 81.2)'
planted defect: the hand calculation follows tfl.population = randomized, the grid safety: 1 differences, for example columns: the grid ['Placebo', 'ZQR-654 5 mg once daily', 'Total'], the reference ['Placebo', 'Active', 'Total']
planted defect: the hand calculation follows ae.teae.start = at_or_after_first_dose_time, the grid on_or_after_first_dose_date: 2 differences, for example row 'Any adverse event', column 'ZQR-654 5 mg once daily': the grid '56 ( 74.7)', the reference '54 ( 72.0)'
planted defect: the hand calculation follows pop.safety.rule = randomized_and_dosed, the grid at_least_one_dose: 8 differences, for example row 'header', column 'ZQR-654 5 mg once daily': the grid '(N=75)', the reference '(N=74)'
planted defect: a mock shell that shows a number: cell:Out_AESUM/r2/c1: the mock shell shows a number: '12 ( 37.5)'
planted defect: a cell that lost a shows edge: 2 problems, for example cell:Out_AESUM/r1/c1: its shows edges are not the ARD rows of the cell
planted defect: an analysis that lost a reads edge: 1 problems, for example ars:An_AESUM_ANY: its reads edges are not the columns the ARS file names: ['adam:ADAE.TRTEMFL']
planted defect: a column that lost its derivation from SDTM: 17 problems, for example adam:ADAE.USUBJID: no derives_from path to an SDTM column
planted defect: a decision without a node: 2 problems, for example edge decides decision:ae.related.values -> adam:ADAE.RELGR1: decision:ae.related.values is not a node
kit 1: study SFPBT5ZJ, 4 arms, split train, scenario 1 (all drawn); decision vectors drawn before this one: 0
  P1: 122 files of two builds by two processes, the manifest included: 0 differ
kit sfpbt5zj (train): 121 files have the hashes of kit.yaml; 29 decision records fit the schema, 13 stated in gold/docs/sap.md and read back by the parser
  visible: P2 30 of 30 cells equal the hand calculation; P3 grid Out_AESUM: 30 cells, 30 print a number; 30 of the 30 cells with results have a complete path to SDTM columns; engines: 55 results in both, 0 disagree; largest relative difference 0.0e+00 (allowed 1e-09)
  twin: P2 30 of 30 cells equal the hand calculation; P3 grid Out_AESUM: 30 cells, 30 print a number; 30 of the 30 cells with results have a complete path to SDTM columns; engines: 55 results in both, 0 disagree; largest relative difference 0.0e+00 (allowed 1e-09)
  twin: P4 53 builds of 22 decisions: 14 separated, 12 applicable, 0 applicable and unseparated; not read: date.studyday.origin, disp.status.record, pop.efficacy.rule, pop.randomized.rule, trt.actual.source, trt.end.source; read without a probe: pop.safety.grouping, pop.safety.rule
kit 2: study SFMYNCMQ, 3 arms, split train, scenario 2 {'tfl.population': 'randomized'}; decision vectors drawn before this one: 0
... (kits 2 to 10: the same six lines each; in every kit 0 files differ, every cell equals the hand calculation, 0 results disagree, 0 decisions are applicable and unseparated)
kit 10: study SF4TVBDP, 2 arms, split test, scenario 10 {'tfl.population': 'safety', 'pop.safety.grouping': 'actual', 'trt.actual.source': 'dm_actarm'}; decision vectors drawn before this one: 0
...
10 kits of the set 'gen-2a': P1 to P4 hold for every kit
-- PASS kits (140.7 s)

== [9/13] separation: specfirst.gen.gate2.separation: every applicable decision, and the matrix of the 10 kits
planted defect: a log of probes that claims a difference for date.studyday.origin: date.studyday.origin: the log of probes claims that dm_rfstdtc and treatment_start differ in the output under these decisions; the two builds are the 
planted defect: the 28 planted subjects of the twin lost their adverse events: ae.teae.start is unseparated, and the kit is unfit in 8 claims, for example: ae.teae.start: the log of probes claims that on_or_after_first_dose_date and at_or_after_first_dose_time diffe
planted defect: a kit whose matrix, decision record and manifest call date.studyday.origin separated, with the hashes written again: the check without a mutation reports 0 problems, a new mutation 3: gold/identifiability.json is not the matrix a new mutation gives; kit.yaml: the identifiability summary is not that of a new mutation; decision date.studyday.origin: 'identifiable' is not what the matrix says
kit 1: 22 decisions, 16 read by the output, 12 applicable (the log claims a probe for every pair), 14 separated; applicable and unseparated: none
... (two lines per kit; the table of the section "Separation")
planted defect: matrices in which no kit separates ae.teae.end: 5 holes, for example: ae.teae.end: separated in no kit
...
separation: 0 holes in the matrix of 10 kits; every applicable decision is separated on the twin of its kit
-- PASS separation (20.1 s)

== [10/13] engines: specfirst.gen.gate2.engines: the Python and the R engine on every result
planted defect: a result of the R engine that differs: ard:An_AESUM_ANY/Mth_CatSumm_n/Grp_TRT01P_1: Python 39, R 40, relative difference 2.5e-02
planted defect: a result the R engine lacks: ard:An_AESUM_ANY/Mth_CatSumm_n/Grp_TRT01P_1: only the Python engine has it
the Python engine and the R engine agree on 766 results of 20 builds (10 kits, visible and twin): yes
-- PASS engines (0.1 s)

== [11/13] splits: specfirst.gen.gate2.splits: the splits of section 6.7
planted defect: a document of the kit that holds the seed: kit 1: gold/docs/sap.md holds the seed
planted defect: a manifest with the split dev: kit 1: split dev, the plan gives train
planted defect: a manifest with the hash of another seed: kit 1: seed_sha256 is not the hash of its seed
planted defect: the vector of kit 1 with {'tfl.columns.total': 'none', 'tfl.columns.arms': 'protocol_order'}: held out, a train kit must not have it
200 vectors drawn for a train kit: none has the held-out combination; of 200 for a sealed kit: 83 have it
splits of the 10 kits by their place in the set: train 4, dev 3, test 3, sealed 0; held out for an exam: an allocation ratio other than 1 to 1, and the combination {'tfl.columns.total': 'none', 'tfl.columns.arms': 'protocol_order'}; 0 problems
-- PASS splits (1.1 s)
...
PASS  environment          0.4 s
PASS  pins                 0.5 s
PASS  lint                 0.0 s
PASS  registry             0.0 s
PASS  unit tests         138.6 s
PASS  method vectors       1.4 s
PASS  pilot tests         46.0 s
PASS  kits               140.7 s
PASS  separation          20.1 s
PASS  engines              0.1 s
PASS  splits               1.1 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE gen-2a: PASS

clean clone gate gen-2a: PASS (clone: /tmp/specfirst-clean-uaKxeJ/specfirst)
```

Over the ten kits, from the log:

| | |
| --- | --- |
| Files compared between the two builds of a kit (P1) | 1,216 in all, 121 or 122 per kit; 0 differ |
| Cells of the gold grids held against the hand calculation (P2) | 422, visible and twin; all equal |
| Mutated builds on the twins (P4), each also held against the hand calculation | 509 |
| Results on which the two engines agree | 766 of 766 |
| Decision vectors drawn again because a claimed pair was not separated | 0 |
| Planted defects inside the gate, each seen by its check | 21 |

How the gate reads its text:

- "10 kits pass P1 to P4": check 8. The kits are written by 20 processes
  of their own, four at a time; every first build has ended before a
  second build starts. A kit is written only when its own build
  has P2 to P4; the gate then decides all of it again from the files of
  the kit (`kits.check`): the hashes, the decision records and the parser,
  a new hand calculation, the graph files, and a new mutation whose matrix
  must be the one in the kit.
- "Every applicable decision is separated on the twin": check 9, with the
  reading of "applicable" of ADR-007, decision 6. It also asks that the
  matrix of the ten kits has no hole.
- "The engines agree": check 10, and inside check 8 per kit.
- The splits are not in the gate text of the plan; check 11 holds what
  section 6.7 asks of this part.
- Checks 4, 6 and 7 are there because gen-2a changed the method registry
  and the column lineage of the machine. The grids of the pilot kit are
  not built in this gate: `display.pattern` keeps its default, and its 22
  vectors and the unit tests of the grid pass. The gate of real-3a was
  run once more for it (section "The pilot kit").

## The pilot kit

gen-2a changed two modules that the pilot kit is built with:
`specfirst.machine.methods` (the rounding behind `display.pattern`) and
`specfirst.machine.lineage`. The gate of real-3a was therefore run once
more, on a clean clone of the same commit. The complete output is
`docs/reports/gen-2a.real-3a.gate.log` (468 lines):

```text
$ flock /run/lock/specfirst-heavy.lock bash scripts/clean_clone_gate.sh real-3a
clean clone gate real-3a
commit:     3c503debbf8724d5b371e2e292cff13f904771d7
...
P1 determinism: 30 of 30 files have the same SHA-256 in both builds
TOTAL cells=9119605 mismatched=0
grid Out14-3-1-1: 27 cells, 27 print a number; 27 of the 27 cells with results have a complete path to SDTM columns
results common-safety-displays, engines: 4238 results in both, 0 disagree; largest relative difference 2.4e-13 (allowed 1e-09)
grid Out14-3-1-1: 27 cells show 51 results; 27 cells equal the reference's formatted values, 0 differ, 0 of them with one class
...
PASS  environment          0.3 s
PASS  pins                 0.7 s
PASS  lint                 0.0 s
PASS  registry             0.0 s
PASS  unit tests         133.2 s
PASS  method vectors       1.3 s
PASS  kit                  0.1 s
PASS  P1 determinism      31.9 s
PASS  P2 reproduction      0.3 s
PASS  trace                0.8 s
PASS  results              2.5 s
PASS  grids                2.1 s
PASS  pilot tests         46.2 s
PASS  planted defects     53.0 s
PASS  cache untouched      0.1 s
PASS  ASCII                0.0 s
GATE real-3a: PASS

clean clone gate real-3a: PASS (clone: /tmp/specfirst-clean-e1t45U/specfirst)
```

The pilot kit is built as before: the same 30 files, the same 27 cells,
the same trace. The changes after the review (`f2dac3b`) touch no module
of the machine, so this gate was not run a third time.

## What was built

One kit is one folder (`docs/state/gen.md` has the tree). The pipeline is
that of PLAN.md section 6.4:

- S1, decisions (`decisions.sample`). The vector holds the 21 or 22
  entries of the slice that apply to the design. A decision that equals
  the house default has the status `default` and cites the standards
  document of the house; any other is `stated` and cites
  `gold/docs/sap.md`, a standard-form document that gen-2a renders and
  that the parser reads back. The slots of an alternative take values
  that fit the design: the emergence window is the follow-up length, the
  vital sign of a population rule is one the study measures.
- S2 to S4, data: `specfirst gen study` of gen-1a, unchanged in what it
  writes but for the two corrections above.
- S5, gold (`gold.build`): compile; yamaa through `runner.run_project`;
  the groups of the treatment grouping listed from the ADaM data; the
  Python engine and the R engine; the grid and its mock shell; the graph
  with `decides` edges from every decision to the elements it sets.
- S7, twin and verify: the same on the twin; P2, P3, P4; the manifest. A
  kit that fails a property is not written: its folder is removed.

Numbers: about 3,200 lines of Python in seven new modules; 28 unit tests
in four new files and 7 more in files of gen-1a (943 unit tests in all at
the first gate run, 908 at the gate of gen-1a).

Three things had to be built that the plan does not name, because three
parts met here for the first time (ADR-007):

1. The engines give a data-driven grouping no result for a group without
   records. The house templates make the treatment grouping data-driven.
   `gold.resolve_groupings` lists the groups first.
2. The compiled layout is "layout draft 0"; the grid builder of real-3a
   reads layout spec v0, which cannot carry a total column, a column rule,
   a rounding rule or a rule for a count of zero. `specfirst.gen.display`
   builds the grid of a draft 0 layout.
3. The catalog offers rounding half to even; nothing implemented it.
   `display.round.half_even` is a new registry entry.

## The four properties, for a generated kit

| Property | What is checked | Planted defects (rule R5) |
| --- | --- | --- |
| P1 determinism | Every kit is written twice, by two processes: hash seed 1 against 2, the time zone and locale of the gate against Pacific/Kiritimati and the C locale, two working folders. Every file is compared by SHA-256, `kit.yaml` included. | A build that stamps its data with a time that depends on its process; a build whose manifest names its folder (it must differ in `kit.yaml` and in nothing else). |
| P2 reproduction | The reference of a generated study is a hand calculation (`gen/reference.py`): SDTM rows and decision values in, the texts of the table out, about 460 lines that share nothing with the compiler, the templates, yamaa, the engines, the registry or the grid builder. Every cell, the columns and the rows of the grid must equal it: on the visible data, on the twin, and for every mutated build of P4. | One changed cell; a grid built by another rule than the reference follows, for three decisions; a mock shell that shows a number. On the tiny hand-made study the unit tests compare 224 decision vectors. |
| P3 traceability | `graph.check_graph` with no accepted gap; `graph.check_cells`: every cell that prints a number has a complete path to SDTM columns; the `reads` edges of every analysis are what the ARS file names; every decision has a node, and every numeric cell an analysis that a decision sets. | A cell without a `shows` edge; an analysis without a `reads` edge; a column without its derivation; a decision without a node. |
| P4 identifiability | Mutation on the twin: every alternative of every decision is compiled and built, and the grids are compared pair by pair (section "Separation"). The matrix of a kit counts because a new mutation gives it again. | A log of probes that claims a difference for `date.studyday.origin`; a twin whose planted subjects lost their events; a kit whose matrix, decision record and manifest call an unseparated decision separated, with the hashes written again; matrices in which no kit separates a decision. |
| Engines (R11) | The ARD of the Python engine and of the R engine, row by row, for every kit, visible and twin. | A result that differs; a result that is missing. |
| Splits (section 6.7) | Every kit has the split of its place in the set and the hash of its seed; no file of a kit holds the seed; no train, dev or test kit has a held-out factor. | A document of the kit that holds the seed; a manifest with another split; a manifest with the hash of another seed; a vector with the held-out combination. |

P3 in a kit of one output: most columns of ADSL are read by no cell. The
check reports how many ADaM columns are on the way of a cell and does not
fail on the others; "no spec element is unused" (section 4.6) can only be
asked when all four table families are built.

## Separation

The gate of gen-1a proved that every probe is in the SDTM of the twin. It
did not build two alternatives. gen-2a does, in every kit
(`verify.mutate`): for each of the 21 or 22 decisions of the kit, every
alternative is compiled and built on the twin, with slot values that fit
the design, and the grids are compared pair by pair. A decision with three
alternatives gives three builds and three pairs. Each build is also held
against the hand calculation of its own vector.

Three things are recorded per decision (`gold/identifiability.json`):

- read: the output reads an element the decision sets. Static, from the
  compile and the lineage, not from the data.
- applicable: the log of probes claims a probe for every pair of the gold
  value with another alternative, under the other decisions of this kit
  (the field `reaches`).
- separated: every such pair gives another grid.

A kit in which a claimed pair gives the same grid is not written. A
decision that is not read must change nothing; a change is a defect.

From the gate log, the matrix of the ten kits. "in": kits whose design has
the decision; "read", "appl", "sep": kits in which it is read, applicable,
separated; then, per pair of alternatives, the kits that separate it:

```text
decision                  in read appl  sep  pairs of alternatives: kits that separate each
trt.planned.source        10    9    9    9  dm_arm|dm_armcd_map: 1,2,3,4,5,6,7,8,9
trt.actual.source         10    2    2    2  dm_actarm|first_ex_treatment: 3,10; dm_actarm|same_as_planned: 3,10; first_ex_treatment|same_as_planned: 3,10
trt.start.source          10   10    8   10  first_ex_with_dose|first_ex_record: 1,2,3,4,5,6,7,8,9,10; first_ex_with_dose|dm_rfxstdtc: 1,2,3,4,5,6,7,8,9,10; first_ex_record|dm_rfxstdtc: 1,2,3,4,5,6,7,8,9,10
trt.end.source            10    3    2    2  last_ex_end_date|last_ex_start_date: 3,7,9; last_ex_end_date|ds_date_when_ex_missing: 3,7; last_ex_start_date|ds_date_when_ex_missing: 3,7,9
trt.date.imputation       10   10    8   10  not_completed|first_day_of_month: 1,2,3,4,5,6,7,8,9,10
date.studyday.origin      10    0    0    0  treatment_start|dm_rfstdtc: NONE
pop.randomized.rule       10    3    3    3  all_randomized|randomized_with_postbaseline: 2,5,8
pop.safety.rule           10    7    1    1  at_least_one_dose|randomized_and_dosed: 10
pop.safety.grouping       10    5    3    3  actual|planned: 6,7,10
pop.efficacy.rule          6    2    2    2  baseline_and_postbaseline|attended_visit: 4,9
disp.status.record        10    3    3    3  disposition_event|disposition_event_by_subcategory: 5,7,8
ae.start.imputation       10   10    8   10  first_of_month_not_before_first_dose|first_of_month: 1,2,3,4,5,6,7,8,9,10; first_of_month_not_before_first_dose|not_completed: 1,2,3,4,5,6,7,8,9,10; first_of_month|not_completed: 1,2,3,4,5,6,7,8,9,10
ae.teae.start             10   10    8   10  on_or_after_first_dose_date|at_or_after_first_dose_time: 1,2,3,4,5,6,7,8,9,10
ae.teae.end               10   10    8   10  no_end|last_dose_plus_days: 1,2,3,4,5,6,7,8,9,10; no_end|end_of_study: 1,2,3,4,5,6,7,8,9,10; last_dose_plus_days|end_of_study: 1,2,3,4,5,6,7,8,9,10
ae.related.values         10    8    0    6  one alternative; kits that separate values of its slot: 1,2,4,5,6,10
tfl.output.include        10   10   10   10  included|not_included: 1,2,3,4,5,6,7,8,9,10
tfl.population            10   10   10   10  safety|randomized: 1,2,3,4,5,6,7,8,9,10; safety|efficacy: 1,2,4,7,9,10; randomized|efficacy: 1,2,4,7,9,10
tfl.columns.arms          10   10   10   10  ascending_dose_placebo_first|protocol_order: 1,2,3,4,5,6,7,8,9,10
tfl.columns.total         10   10   10   10  all_arms|none: 1,2,3,4,5,6,7,8,9,10; all_arms|active_arms: 1,2,3,4,5,6,7,8,9,10; none|active_arms: 1,2,3,4,5,6,7,8,9,10
tfl.percent.format        10   10   10   10  one_decimal_zero_blank|one_decimal_always: 1,2,3,4,5,6,7,8,9,10
tfl.rounding.rule         10   10    1    8  half_away_from_zero|half_even: 1,2,3,5,6,7,8,10
tfl.ae.summary.rows       10   10   10   10  standard_rows|stated_rows: 1,2,3,4,5,6,7,8,9,10
not applicable to this output, and unseparated for the slice (PLAN.md section 4.7): date.studyday.origin
separation: 0 holes in the matrix of 10 kits; every applicable decision is separated on the twin of its kit
```

How to read it:

- In every kit, every applicable decision is separated: that is the gate
  text, and no kit needed a second decision vector for it.
- Every pair of alternatives of every decision is separated in at least
  one kit, and every decision is applicable and separated in at least one
  kit, except `date.studyday.origin`.
- `date.studyday.origin` is read by no cell in any kit: the adverse event
  summary shows no study day. It is `unseparated` in every kit, with the
  reason "the output does not read what the decision sets", and the
  mutation confirms that changing it changes nothing. It is not passed as
  proven; a table family that shows a study day will separate it.
- Decisions that are read in fewer kits than ten are read only under
  another decision's value, for example planned treatment (9 kits), the
  treatment end date (3), the rule of the randomized set (3), of the
  efficacy-evaluable set (2), the end-of-study record (3). The scenarios of a set exist so
  that each is read and claimed in some kit (`decisions.SCENARIOS`); the
  matrix above is the proof for this set.
- "sep" above "appl": a decision can be separated without a claim. The
  rounding rule is applicable in kit 10 only, whose scenario is the one
  the calibrated counts are made for; it is separated in seven more kits,
  where a percentage of some column lies on a half as well. It is not
  separated in kits 4 and 9, on the efficacy-evaluable set.
- `pop.safety.rule` is the thinnest row: read in 7 kits, separated in 1.
  Its probe, the subject who is dosed without being randomized, has no
  planned treatment, so it stands in a column only where the table groups
  by actual treatment from DM or from the exposure records. Scenario 10
  is there for it.
- `ae.related.values` has one alternative. The matrix changes the values
  of its slot instead: six kits separate them; in the others the table
  does not show the row, or the causality scale of the study has two
  values and the list can only be the one it is.

What the first mutations corrected. The field `reaches` was a prediction
of gen-1a that nothing had built. Run on the first trial kits, five of its
claims did not hold, each for a reason that can be said in a sentence
(lesson 43); the conditions in `probes.REACHES` are corrected, and a claim
that fails now stops the kit. Three earlier readings of gen-1a were
confirmed: the two interplays of F22 (the pair of the two day-completions
is lost under emergence by time; no end against end of study is lost when
the treatment record is the end-of-study record), and the need for a
window of exactly the follow-up length.

## not_before

The review of gen-1a left open what yamaa's `not_before` does with a
partial start date in a month before the treatment start. If it moved
every earlier date up to the treatment start, the pair
first_of_month_not_before_first_dose against not_completed of
`ae.start.imputation` would not be separated by its two probes.

The experiment: the twin of kit 1 of the gate carries both probes of the
entry. The three alternatives were built on it by the machine, and the two
planted events read from the ADaM dataset that yamaa built (a scratch
script of the session, not kept; it calls `gold.Workbench.show` and prints
`ASTDT`, `ASTDTF`, `TRTSDT` and `TRTEMFL` of ADAE):

```text
$ flock /run/lock/specfirst-heavy.lock python notbefore.py /root/scratch-gen2a/gate2/first/kit-001
== first_of_month_not_before_first_dose
  partial_ae_start_in_month_of_first_dose: AESTDTC 2022-03, RFXSTDTC 2022-03-19T08:45: yamaa ASTDT 2022-03-19 ASTDTF D TRTSDT 2022-03-19 TRTEMFL Y; hand calculation ASTDT 2022-03-19 emergent True
  partial_ae_start_before_month_of_first_dose: AESTDTC 2022-02, RFXSTDTC 2022-03-01T11:00: yamaa ASTDT 2022-02-01 ASTDTF D TRTSDT 2022-03-01 TRTEMFL None; hand calculation ASTDT 2022-02-01 emergent False
== first_of_month
  partial_ae_start_in_month_of_first_dose: AESTDTC 2022-03, RFXSTDTC 2022-03-19T08:45: yamaa ASTDT 2022-03-01 ASTDTF D TRTSDT 2022-03-19 TRTEMFL None; hand calculation ASTDT 2022-03-01 emergent False
  partial_ae_start_before_month_of_first_dose: AESTDTC 2022-02, RFXSTDTC 2022-03-01T11:00: yamaa ASTDT 2022-02-01 ASTDTF D TRTSDT 2022-03-01 TRTEMFL None; hand calculation ASTDT 2022-02-01 emergent False
== not_completed
  partial_ae_start_in_month_of_first_dose: AESTDTC 2022-03, RFXSTDTC 2022-03-19T08:45: yamaa ASTDT None ASTDTF None TRTSDT 2022-03-19 TRTEMFL Y; hand calculation ASTDT None emergent True
  partial_ae_start_before_month_of_first_dose: AESTDTC 2022-02, RFXSTDTC 2022-03-01T11:00: yamaa ASTDT None ASTDTF None TRTSDT 2022-03-01 TRTEMFL Y; hand calculation ASTDT None emergent True
```

yamaa 0.7.0 moves a partial start up to the treatment start only when the
treatment start lies in the month of the partial date (2022-03 becomes
2022-03-19). A partial date in an earlier month keeps the first day of its
own month (2022-02 stays 2022-02-01, before the treatment start of
2022-03-01), and the event is not treatment-emergent. That is what the
statement of the entry says ("or with the treatment start date when it
falls in that month"), and what the hand experiment of the gen-1a review
assumed. So:

| Pair of `ae.start.imputation` | Event in the month of the first dose | Event in an earlier month |
| --- | --- | --- |
| first_of_month_not_before_first_dose against first_of_month | emergent against not emergent: separated | the same |
| first_of_month_not_before_first_dose against not_completed | the same (both emergent) | not emergent against emergent: separated |
| first_of_month against not_completed | separated | separated |

The pair in question is separated, by the probe of the earlier month. The
matrix of the gate shows it in all ten kits. The experiment is kept as a
unit test on the tiny study with two added events
(`tests/unit/test_gen_gold.py::test_not_before_moves_a_partial_start_only_within_its_month`),
so a new version of yamaa that reads `not_before` otherwise fails a test.

## Limits

- Section 6.8 applies: the studies are built for decision coverage.
- "Applicable" is read as "the log of probes claims a probe for every pair
  of the gold value with another alternative under the decisions of the
  kit" (ADR-007, decision 6). A decision the output reads without such a
  claim is built and recorded as it comes out. In the ten kits of the gate
  that leaves, read and unseparated: `tfl.rounding.rule` in the kits on the
  efficacy-evaluable set (the calibrated counts hold for the safety set by
  actual treatment), `pop.safety.rule` where the table does not group by
  actual treatment (its planted subject has no planned treatment),
  `pop.safety.grouping` where actual treatment is the same as planned, and
  `trt.end.source` in one kit on the efficacy-evaluable set (its planted
  subject stops early). The log of the gate lists them per kit.
- `date.studyday.origin` is unseparated in every kit of this slice: no
  cell reads a study day.
- `disp.status.record`: a gold vector never names the treatment record,
  and names the study participation record only where the output does not
  read the decision. The decision is separated from `disposition_event`
  towards the treatment record only. This is the recipe of the catalog
  (for the std track).
- The matrix changes one decision at a time and mutates a slot to one
  value. Two wrong decisions, or two values of a slot, can give the same
  table (F23 of the gen-1a review).
- The matrix is that of the twin. The visible data carry about half of
  the probes; no matrix is computed for them.
- P2 holds the table and nothing else. No ADaM value and no ARD value
  that no cell shows is held against anything: ASTDY under
  `date.studyday.origin` is the example. And where a kit leaves a decision
  unseparated, P2 cannot see a machine that ignores it: on the twin of kit
  9 a build that rounds half away from zero although the kit states half
  to even passes P2 (the reviewer's experiment D).
- P3 is checked without "no spec element is unused" (section 4.6). With
  one output most columns of ADSL are read by no cell; the check reports
  how many ADaM columns are on the way of a cell and fails on no other.
  The full gen-2, with four table families, owes it.
- The order of the columns is taken from the design: the catalog
  alternative `protocol_order` has no slot for the order of the arms. The
  hand calculation gets the arms, with the texts that can name each in a
  treatment column, from `gold.arms_of`, the function the machine uses,
  and `reference.column_order` is the rule of `gold.order_values` written
  a second time. For this one rule the reference is a copy with a shared
  input: an arm named wrongly there stands last in both. The labels of
  the rows and of the total column are copied from the house layout
  template.
- The reference follows the words of the catalog entries. Five readings
  are marked in the module: a partial exposure start date is ordered as
  its text when the first exposure record is looked for; the first
  alternative of `ae.start.imputation` (section "not_before"); a partial
  end date of an event is no end "before the treatment start date"; when
  an event has no analysis start date and ended before the treatment
  start, the end decides; a subject of the analysis set without a
  treatment in the grouping stands in no column, the total included, and
  an arm without a subject in the set has no column. The last one is why
  `pop.safety.rule` cannot be separated on a table by planned treatment.
  A wrong reading that the machine shares would not show.
- The hand calculation and the grid builder agree on the form of a cell
  ("12 ( 37.5)") by construction.
- What the sampler never draws (`decisions.slot_values`, `decisions.fits`).
  A stated list of rows is one of four, each with ANY and FATAL and none
  with DISCONTINUATION; an emergence window is always the follow-up length
  of the design; `disp.status.record` as above. So the conditions of
  `probes.REACHES` on the rows hold in every kit that is written, and a
  reader is never scored on a table of "any event and serious events"
  alone or on a window of another length. The machine and the hand
  calculation agree on such vectors too (the reviewer's experiment C: 940
  random vectors on six twins, about three quarters of them vectors the
  sampler refuses).
- `gold/docs/sap.md` is the standard form of the stated decisions. It is
  not the protocol and SAP of gen-3a.
- The seed of the gate is a development seed. No seed file for a set with
  dev and test kits exists yet.

## Review

The independent review (rule R7) is in `docs/reports/gen-2a.review.md`.

Pass 1 read commit `ce70734` (the code of `3c503de`, on which the gates
ran) with the gate logs, this report and the handover. Verdict: NOT
SIGNED. One finding blocks (G1), seven do not (G2 to G8). What the
reviewer established that the author could not:

- A count by hand of the reviewer's own, 110 lines that import nothing of
  specfirst, equals the twin of kit 9 in 24 of 24 cells.
- 940 decision vectors drawn at random, most of them vectors the sampler
  never draws, built by the machine on six twins: 940 grids equal the hand
  calculation.
- Defects planted in the machine (a window one day longer or shorter, a
  strict comparison in the compiled spec, the rounding rule ignored, the
  columns reversed, the zero rule turned round, an event missing, another
  rule of the safety set) are seen by P2 wherever the kit separates the
  decision, and not where it does not.
- Kit 9 of the gate, built again by the reviewer twenty minutes later in
  another process and folder, is the kept kit byte for byte.
- Every claim of `probes.REACHES` held on every vector that the sampler
  can draw (6,068 pairs on 366 vectors); four claims were false on
  vectors it refuses (G8).

| Finding | What was done |
| --- | --- |
| G1 "applicable" is what the generator claims: the gate passes kits in which a decision that the output reads, and that data could separate, is not separated on the twin (blocks) | Open. The finding is right about what the gate proves: see "Limits". The reviewer names two ways to settle it and says the choice is the owner's: the owner approves the reading of ADR-007, decision 6, for this slice; or the probes follow the decisions of the kit (stage S3 after S1) and the gate fails on a read decision that data could separate. Put to the owner on 2026-11-17. Nothing is merged before the answer. |
| G2 P3 without "no spec element is unused"; P2 holds the table only | Both are under "Limits" now, with the reviewer's experiment: a machine that ignores the rounding rule passes P2 on the twin of kit 9. |
| G3 the hand calculation shares a little with the machine; three readings not marked | The module text says what is shared (the arms and their names from `gold.arms_of`, the column order written a second time, the labels copied). The three readings are marked `READING` in `reference.py`, and all five are under "Limits". No behaviour changed. |
| G4 four checks had no planted defect in the repository | `gate2.planted_splits`: a document that holds the seed, a manifest with another split, a manifest with the hash of another seed, each in a copy of kit 1; each must be reported alone. `gate2.planted_matrix`: a copy of the kit whose matrix, decision record and manifest call `date.studyday.origin` separated, with the hashes written again; the check without a mutation must report nothing and a new mutation exactly the three differences. Both run in the gate and in the unit tests. |
| G5 values the sampler never draws were not under the limits | They are. |
| G6 the two builds of P1 ran at the same moment | `gate2.write_all` ends every first build before a second build starts. |
| G7 records | 943, not 942. `kits.generate` removes the folder of a kit that cannot be written, with a test. The line "Passed" of the handover is true once the review is signed; the merge waits for that. |
| G8 a false claim for `disp.status.record` on vectors the sampler refuses | `REACHES` does not claim the pair when the end-of-study record is the one with the subcategory of the study participation; a test. The log of probes carries the table, so `GENERATOR` is `gen-2a.2`. |

The code changed after the first gate run (G4, G6, G7, G8, the comments of
G3), so the gates were run again: section "The gate".

## GitHub and CI

`track/gen` is pushed to the owner's private repository. CI
(`.github/workflows/ci.yml`: the ASCII check, lint, the unit tests, on
GitHub's runner, which has no R, no fetch cache and no CORE) ran on the
push of `ce70734`, which holds the code of the gate (`3c503de`) and the
first form of this report:

```text
run 44178069250 on track/gen at ce70734: completed, success
ASCII check: 441 files checked, 0 with non-ASCII bytes
All checks passed!
924 passed, 19 skipped, 22 deselected in 188.07s (0:03:08)
```

The 19 skipped tests need R; in the gate, where R is installed, the same
selection gives 943 passed and none skipped. The unit tests that build a
kit do it without R (`with_r=False`), so they run on GitHub's runner too;
the agreement of the engines is decided in the gate only.

The runs on the commit that holds this report and on `main` after the
merge cannot be in it; they are in GitHub, and the session reports them
when it hands the work back.

## For the owner

1. ADR-007 holds the choices of this part; it stands unless the owner
   objects. Its five points for the owner are about what other tracks own:
   the listed groups (or a change of rule I9 of the engines), the layout
   format of the house templates, the order of the arms, the new registry
   entry, and the reading of "applicable".
2. A seed file for the first set with dev and test kits: who makes it and
   where it is kept (outside every checkout). Until then every kit is a
   development kit.
3. `tfl.rounding.rule` cannot be separated in a kit that is not on the
   safety set grouped by actual treatment, because the data of a kit do
   not follow its decisions. Making the calibrated counts follow the
   analysis set of the kit is possible (stage S3 after S1) and was not
   done.

## Files

- Code: `src/specfirst/gen/decisions.py`, `gold.py`, `display.py`,
  `reference.py`, `verify.py`, `kits.py`, `gate2.py`; changes in
  `gen/probes.py`, `sdtm.py`, `gate.py`, `command.py`, `__init__.py`,
  `core_findings.yaml`; `src/specfirst/gates.py`, `cli.py`, `doctor.py`;
  `src/specfirst/machine/methods.py`, `lineage.py`.
- Standard: `standard/methods/display.round.half_even.yaml`,
  `display.pattern.yaml`, `registry.json`, `README.md`.
- Tests: `tests/unit/test_gen_reference.py`, `test_gen_gold.py`,
  `test_gen_decisions.py`, `test_gen_kits.py`; additions in
  `test_gen_gate.py`, `test_gen_probes.py`, `test_gen_subjects.py`,
  `test_doctor.py`, `test_registry.py`; `tests/methods/`.
- Records: `docs/decisions/ADR-007.md`, `docs/lessons.md` (lessons 40 to
  46), `docs/state/gen.md`, `CLAUDE.md`, `kits/README.md`,
  `scripts/clean_clone_gate.sh`, this report,
  `docs/reports/gen-2a.gate.log`, `docs/reports/gen-2a.gen-1a.gate.log`,
  `docs/reports/gen-2a.real-3a.gate.log`, `docs/reports/gen-2a.review.md`.
