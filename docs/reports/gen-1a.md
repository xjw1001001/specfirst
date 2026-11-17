# gen-1a SDTM generator for PG-FIX, slice "adverse event summary first": report

Date: 2026-11-17. Branch: `track/gen`. Part gen-1a of ADR-005, decision 1.
Depends on base-0 (passed) and a draft of std-1; the catalog was frozen as
`catalog@1` (version 1) while the part was written, and the gate ran on
that version.

## Verdict

The gate passed. `scripts/clean_clone_gate.sh gen-1a` exited 0 on a clean
clone of commit `39ff635`, after a fresh install (CORE included) and a
fresh fetch: 8 of 8 checks. The complete output is in
`docs/reports/gen-1a.gate.log` (181 lines); the section "The gate" below
quotes it.

- CDISC CORE v1.0.0 ran on the 20 datasets of the ten seeds (visible and
  twin, 11 domains each): 1,825 findings, each read against the list of
  explained findings, 0 unexplained, and no entry of the list unused.
- Generating again gives identical hashes: 510 files per build, the
  manifests included, the second build made by a process of its own.
- Every pair of alternatives of every decision of the slice that applies
  has a probe in the twin that was found again in the SDTM: 32 pairs in
  the three designs without an efficacy set, 35 in the other seven.
- Ten planted defects inside the gate were each seen by the check they
  were planted for (rule R5).

What the gate does not prove: that the output of the slice differs between
two alternatives. That needs both built, which is gen-2a; the section
"What the probes prove, and what they do not" says what was done about it
here. Five things are for the owner, at the end.

The independent review (rule R7) is in `docs/reports/gen-1a.review.md`.
Pass 1, before the gate, did not sign: four findings blocked. Pass 2 read
the code of `39ff635`, the gate log, this report and the reports of CORE,
and signed: "Verdict of pass 2: SIGNED", with eight new findings that do
not block (section "Review"). They are not fixed here, so that the code of
the merge is the code that passed the gate; `docs/state/gen.md` lists them
for the first commit of gen-2a. With gate and review passed, `track/gen`
merges to `main` and both are pushed (section 2.4).

## What gen-1a asks for, and where it stands

ADR-005, decision 1: "Design model and sampler for PG-FIX. Subject process.
SDTM writers for DM, DS, EX and AE and the datasets CORE requires with
them. Probe recipes for the decisions of the slice." Gate: "The gate of
gen-1 for these datasets and these decisions."

| Item | State | Where |
| --- | --- | --- |
| CDISC CORE in the environment, pinned; an ADR for the change of `env/` | done: CORE v1.0.0 from source at the commit of its tag, in a virtual environment of its own built from a lock with hashes; the doctor checks both | `docs/decisions/ADR-006.md`; `env/core-source.txt`, `env/core-requirements.in`, `.lock`, `env/core-sdist.txt`; `src/specfirst/cdisccore.py` |
| Design model `design.yaml`, terms after USDM v4; sampler for the archetype PG-FIX (section 6.2) | done: 2 to 4 arms with a placebo control, ratio 1:1 or 2:1, fixed duration, visits with windows, three epochs; the ten design features of the catalog are computed from the design | `src/specfirst/gen/design.py`, `pgfix.py` |
| Subject process (stage S2): enrolment, arm, exposure, dropout, adverse events; simple, documented, seeded | done: the models are stated at the top of the module; every random number comes from a stream named by the seed and a path | `src/specfirst/gen/subjects.py`, `rng.py`, `terms.py` |
| SDTM writers for DM, DS, EX, AE and the datasets CORE requires, with Define-XML (stage S4); the code general, limited by a list of domains | done: DM, DS, EX, AE, and SE, SV, VS, TA, TE, TV, TS; Dataset-JSON v1.1 and Parquet; Define-XML v2.1. SV and VS are written already: the parent specs of the house standard read both for the populations of the slice | `src/specfirst/gen/sdtm.py` (`SLICE_DOMAINS`), `datasetjson.py`, `define.py`, `study.py` |
| Probe recipes for every decision of the slice (section 6.5); the twin gets all, the visible data a sampled part; `probes.jsonl` logs them | done: 28 probes for the 22 catalog entries of the four units; a finder per probe reads each one back from the SDTM that was written | `src/specfirst/gen/probes.py`, `present.py` |
| Gate `gen-1a`: environment first; 10 seeds pass CORE with no unexplained error; identical hashes; a probe in the twin for every pair of alternatives; each check has failed on a planted defect (rule R5) | done: 8 checks, 10 planted defects inside the gate and more in the unit tests | `src/specfirst/gates.py`, `src/specfirst/gen/gate.py`, `core_findings.yaml` |
| The catalog version in everything generated | done: `specfirst-m1 1`, as the standard form names `catalog@1`, in the design, the log of probes, the truth files, every Dataset-JSON file, the Define-XML, the schema note of every Parquet file and the manifest; a design of another catalog version is refused | `study.catalog_label`; `test_gen_gate.py::test_everything_generated_names_the_catalog_version` |
| Sealed seeds stay outside the repository (section 6.7) | done: `--seed-file` refuses a file inside any checkout; a manifest holds the SHA-256 of the seed file, never the seed. The ten gate seeds are development seeds | `src/specfirst/gen/command.py` |
| `specfirst gen` | done: `gen design`, `gen study`, `gen check` | `src/specfirst/cli.py`, `gen/command.py` |

`PLAN.md` and `standard/schemas/` are not changed. `env/` is changed by
ADR-006: four new files, and `install.sh`, `lock.sh` and `README.md`;
`env/requirements.lock`, `env/r-packages.lock` and `env/system.lock` are
byte for byte as before.

Not in gen-1a, by its definition: the other three table families and their
decisions, the gold decisions and the builds (gen-2a), the documents
(gen-3a). gen-2a was not started.

## The gate

Gate text of PLAN.md section 13.5 (gen-1), which ADR-005 limits to the
datasets and decisions of the slice: "for 10 seeds, visible and twin SDTM
pass CORE with no unexplained error. Regenerating gives identical hashes.
`probes.jsonl` shows at least one probe in the twin for every pair of
alternatives."

Command, run in Ubuntu 24.04 under WSL2 as root, from the worktree of
`track/gen`, inside the lock that all sessions use for heavy runs (lesson
32):

```text
$ flock /run/lock/specfirst-heavy.lock bash scripts/clean_clone_gate.sh gen-1a /mnt/d/trial_work/specfirst/.git 39ff635
```

It held the lock from 13:04:07 to 13:22:09 and exited 0. The script clones
the repository, checks out the commit, installs everything new under the
same temporary folder and fetches the pinned sources new; nothing of the
worktree's environment is reused. From its output:

```text
clean clone gate gen-1a
repository: /mnt/d/trial_work/specfirst/.git
commit:     39ff635
clone:      /tmp/specfirst-clean-CTanbE/specfirst
environment and cache: /tmp/specfirst-clean-CTanbE/env
...
$ bash env/install.sh
python environment: /tmp/specfirst-clean-CTanbE/env/venv-specfirst-1532074759
R library: /tmp/specfirst-clean-CTanbE/env/r-lib
R packages: 99 wanted, 99 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
R library matches the lock: 99 packages in /tmp/specfirst-clean-CTanbE/env/r-lib
CDISC CORE v1.0.0: /tmp/specfirst-clean-CTanbE/env/core/f3282a0d870b-d90ef34c553d
source: fetched f3282a0d870bbdf57e326e9992cceea3ed0d9af5
...
CDISC CORE v1.0.0 at f3282a0d870b: 0 differ
system lock: 32 packages recorded, 0 differ
doctor: ok
...
$ specfirst gate gen-1a --clean
gate gen-1a at commit 39ff635c614031a89c44e9ab533f9674219b761b (clean)
```

The eight checks:

```text
== [1/8] environment: specfirst doctor
...
CDISC CORE v1.0.0 at f3282a0d870b: 0 differ
system lock: 32 packages recorded, 0 differ
doctor: ok
-- PASS environment (0.3 s)

== [2/8] lint: ruff check .
All checks passed!
-- PASS lint (0.0 s)

== [3/8] unit tests: pytest -m "not evidence" -q
...
908 passed, 22 deselected in 58.14s
-- PASS unit tests (58.5 s)

== [4/8] identical hashes: specfirst.gen.gate.determinism: 10 seeds, generated twice
planted defect: a build with another time stamp differs in 25 files, for example inputs/data/sdtm/ae.json: the hashes differ
planted defect: a study whose manifest alone differs: study.json: the hashes differ
planted defect: a build that depends on the hash seed of its process, made by two processes: differs in 25 files
10 seeds, each generated twice, by this process and by a process of its own (hash seed 1, time zone Pacific/Kiritimati, locale C, its own working folder): 510 files and 2799 subjects per build, the manifests included, catalog specfirst-m1 1
identical hashes: 0 problems
-- PASS identical hashes (7.7 s)

== [5/8] CDISC CORE: specfirst.gen.gate.core: visible and twin of the 10 seeds
CDISC CORE v1.0.0 at f3282a0d870b, SDTMIG V3.4, Define-XML 2.1.0, terminology sdtmct-2025-09-26; explained findings: core_findings.yaml, 18 entries
planted defect: two events of one subject with the same AESEQ: reported by CORE and unexplained: CORE-000544 AE (issue reported, 2 issues, SFATXTPG-101-001): AESEQ must be a unique number per USUBJID per domain, or a
planted defect: an actual arm that no probe planted: reported by CORE and unexplained: CORE-000655 DM (issue reported, 2 issues, SFATXTPG-101-002, SFATXTPG-102-016): Values between ARMCD and ACTARMCD are not
21 reports of CORE are kept in core/ beside this log
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
-- PASS CDISC CORE (881.4 s)

== [6/8] controlled terms: specfirst.gen.gate.controlled_terms: values against the CT package of CORE
CT package sdtmct-2025-09-26 of the pinned CORE: 1181 codelists
planted defect: SEX = X and AESEV = TERRIBLE are reported: DM.SEX = 'X' SFATXTPG-101-001: not a term of SEX
planted defect: another code for SEX F in the package: SEX: 'F' is C00000 in the package, C16576 here
95 terms of 22 codelists and the trial summary parameters agree with the package; 709791 values of controlled variables in 20 datasets checked: 0 problems
-- PASS controlled terms (0.6 s)

== [7/8] probes: specfirst.gen.gate.probe_coverage: every pair of alternatives
planted defect: the records of a logged probe are removed from the data: 2 problems, for example: ae.teae.start: on_or_after_first_dose_date and at_or_after_first_dose_time: every probe that should separate them is missing from the data (ae_on_firs
planted defect: a probe is left out of the log: probe two_disposition_events: the twin does not carry it
planted defect: one serious event less in the calibrated arm: probe statistic_at_rounding_half: arm PBO: the data give 32, 18 and 1 subjects, the log says 32, 18 and 2
seed gen-1a-1: 21 decisions apply, 32 pairs of alternatives; twin: 26 of 26 probes logged and found in the data; visible: 14 probes logged and found; 0 problems
seed gen-1a-2: 22 decisions apply, 35 pairs of alternatives; twin: 28 of 28 probes logged and found in the data; visible: 14 probes logged and found; 0 problems
... (8 more seeds: 21 or 22 decisions, 32 or 35 pairs, every probe of the twin found, 13 to 20 probes in the visible data, 0 problems)
units of the slice: mod-treatment, mod-populations, mod-ae-emergence, tfl-ae-summary
-- PASS probes (0.6 s)

== [8/8] ASCII: python -m specfirst.asciicheck
ASCII check: 421 files checked, 0 with non-ASCII bytes
-- PASS ASCII (0.0 s)

PASS  environment          0.3 s
PASS  lint                 0.0 s
PASS  unit tests          58.5 s
PASS  identical hashes      7.7 s
PASS  CDISC CORE         881.4 s
PASS  controlled terms      0.6 s
PASS  probes               0.6 s
PASS  ASCII                0.0 s
GATE gen-1a: PASS

clean clone gate gen-1a: PASS (clone kept in /tmp/specfirst-clean-CTanbE/specfirst until /tmp is cleared)
```

Three designs have no efficacy-evaluable set (seeds 1, 3 and 10): there
`pop.efficacy.rule` does not apply and `tfl.population` has two
alternatives instead of three, which gives 21 decisions, 32 pairs and 26
probes instead of 22, 35 and 28.

The clone did not outlive the day: `/tmp` of the WSL machine is cleared
when the instance restarts, and it restarted a minute or two after the
gate, as it does whenever no command is running. The 21 reports of CORE
that the gate had kept beside its log went with it (lesson 39). The check
"CDISC CORE" was therefore run once more from the worktree, whose code is
that of the commit, with the reports kept under `/root`:

```text
$ flock /run/lock/specfirst-heavy.lock python -B core_again.py /root/scratch-gen1a/again /root/scratch-gen1a/gatecore
lock held at 2026-11-17 13:25:25
CDISC CORE v1.0.0 at f3282a0d870b, SDTMIG V3.4, Define-XML 2.1.0, terminology sdtmct-2025-09-26; explained findings: core_findings.yaml, 18 entries
...
21 reports of CORE are kept in gatecore/ beside this log
seed gen-1a-1 visible: 562 rules (323 passed, 191 not applicable, 10 with issues, 38 not executable); 86 findings, 0 unexplained
...
CORE on 20 datasets (10 seeds, visible and twin): no unexplained finding; the pinned source is unchanged
check CDISC CORE: PASS after 876 s
studies: 510 files, SHA-256 over all their hashes b056b77b47d3672bb7a85f6a405fae4f83b4b70262d55c76c36af7790e27b0a1
```

`core_again.py` is a scratch script of the session, not kept: it calls
`specfirst.gen.gate.core_check`, the function behind check 5, with a
folder for the reports. Its complete output is
`docs/reports/gen-1a.core.log`. The 45 lines the check prints are those of
the gate log, lines 96 to 140, but for the name of the folder: the same
planted defects, the same numbers for each of the 20 datasets, the same
table of findings by explanation. These 21 reports, not those of the gate
run, are what the reviewer read in pass 2 and what
`src/specfirst/gen/core_findings.yaml` was held against. The reports are
1 to 2 MB each and are not in the repository; `specfirst gate gen-1a`
writes them again into `build/gates/gen-1a/core/`.

## Other commands of this report

`make lock` on the reference platform, on a copy of `env/` and `scripts/`
of the worktree (review finding F1; the lock of CORE had first been
resolved under Windows):

```text
$ cp -r env scripts /tmp/specfirst-lockcheck/ && cd /tmp/specfirst-lockcheck && bash env/lock.sh
...
R packages: 99 wanted, 0 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
wrote /tmp/specfirst-lockcheck/env/r-packages.lock (99 packages)
R library matches the lock: 99 packages in /root/.local/share/specfirst/r-lib
locks written: env/requirements.lock env/core-requirements.lock env/r-packages.lock env/system.lock
lock.sh exit: 0
$ for f in requirements.lock core-requirements.lock r-packages.lock system.lock; do cmp -s env/$f /mnt/d/trial_work/specfirst-gen/env/$f && echo "same      env/$f"; done
same      env/requirements.lock
same      env/core-requirements.lock
same      env/r-packages.lock
same      env/system.lock
```

The doctor of the worktree, before the gate (the gate log has the doctor of
the clean clone):

```text
$ specfirst doctor
python     3.12.3  (/root/.local/share/specfirst/venv-specfirst-gen-4183890014/bin/python)
python lock: 23 packages pinned, 0 differ
R          R version 4.6.2 (2026-10-29) -- "Diversified Portfolio"
R lock: 99 packages pinned, 0 differ
pdftotext  pdftotext version 24.02.0
git        git version 2.43.0
CDISC CORE v1.0.0 at f3282a0d870b: 0 differ
system lock: 32 packages recorded, 0 differ
doctor: ok
```

Scratch runs that are named in this report and are not part of the gate
(Windows, the scratch environment of the session; their scripts are not
kept): 1,500 seeds generated in memory with every probe found again
("1500 seeds in 205 s; subjects per dataset 39 to 275; failures: {}"), and
the reviewer's pair experiment repeated on the ten gate twins.

## What was built

A study is one folder:

```text
gold/design.yaml            the sampled design (never shown to a reader)
gold/probes.jsonl           one line per probe and dataset
gold/truth/subjects.jsonl   the latent truth of the visible subjects
inputs/data/sdtm/           the visible SDTM: 11 datasets as Dataset-JSON and Parquet, define.xml
twin/data/sdtm/             the twin: the same design, other subjects, every probe
twin/truth/subjects.jsonl
study.json                  the manifest: generator, catalog, hashes of all files, hash of the seed
```

- The sampler draws a design from the seed: study code and drug name
  (invented), 2 to 4 arms in multiples of 16 subjects, the protocol order
  of the arms different from the dose order, visits, windows, follow-up,
  rates. `design.problems` checks a design before anything is generated.
- The base process enrols subjects until the planned number is randomized.
  It has no edge cases on purpose: every randomized subject is dosed as
  planned, has complete dates and no event after the last dose. Edge cases
  come from the probes only, so `probes.jsonl` says exactly where each is.
- Of the 28 probes of the slice, 22 add subjects of their own, 2 calibrate
  counts in the placebo arm (a percentage exactly at a rounding half, a
  category with a zero count), 1 is a property of the base data, 1
  follows from the design and 2 from the shape of the output. Planted
  subjects are numbered with the others in the order of consent; their
  kind shows only in gold.
- The twin is generated from the same design with another stream and
  carries every probe that applies to the design. In the visible data
  each planted or count probe is there with a chance of one half.
- Every file is written by the canonical writers of `specfirst.machine`;
  the time stamp in a file is the last study date, never the clock.

Numbers: 5,250 lines of Python in `src/specfirst/gen/` and
`src/specfirst/cdisccore.py`; 133 unit tests in six new files. In memory,
1,500 further seeds were generated with both datasets each and every probe
was found again in every one (39 to 275 subjects per dataset; no failure;
a scratch run under Windows, not part of the gate).

## What the probes prove, and what they do not

PLAN.md section 6.5 defines a probe as "a planted subject or record on
which two alternatives of one decision give different results". The gate of
gen-1 asks for less: `probes.jsonl` must show a probe in the twin for every
pair of alternatives. gen-1a has no compiler and no engine in its gate, so
its check "probes" proves three things and no more:

1. Every probe the catalog asks for in this design is logged for the twin,
   once (`present.coverage`: "the twin does not carry it", "logged n
   times").
2. Every logged probe is found again in the SDTM that was written, with
   everything its alternatives need to differ: the pattern and, where the
   difference shows only through an adverse event, that event
   (`present.find`, one finder per probe).
3. Every pair of alternatives of every decision of the slice that applies
   to the design has such a probe. Which pairs a probe separates is read
   from the catalog, not from the log.

It does not prove that the output differs: that needs both alternatives
compiled and built, which is the gate of gen-2a ("every applicable decision
of the slice is separated on the twin"). The first pass of the review did
that proof by hand, with a reference implementation of the house specs
(scratch files of the reviewer), and found five probes that changed no
result and one cancellation (findings F2 and F3, lesson 37). After the
fixes the same experiment was repeated by the author on the ten gate twins,
and by the reviewer in pass 2 with the same output:

| Decision | Pairs | The adverse event summary differs at the house defaults |
| --- | --- | --- |
| `trt.actual.source` | 3 | in 10 of 10 twins, every pair |
| `trt.start.source` | 3 | in 10 of 10, every pair (pass 1: one pair in 0 of 10) |
| `trt.date.imputation` | 1 | in 10 of 10 (pass 1: 0 of 10) |
| `pop.safety.rule`, `pop.safety.grouping` | 1 each | in 10 of 10 |
| `ae.start.imputation` | 3 | in 10 of 10, every pair |
| `ae.teae.start` | 1 | in 10 of 10 |
| `ae.teae.end` | 3 | in 10 of 10 for a window of N days, N being the follow-up length of the design (see Limits) |
| `tfl.population` | 1 or 3 | in 10 of 10; with `efficacy` in the 7 twins that have that set (pass 1: safety against randomized the same in one twin) |
| `tfl.columns.total`, `tfl.ae.summary.rows`, `tfl.percent.format`, `tfl.rounding.rule` | 3, 1, 1, 1 | in 10 of 10 |
| `trt.planned.source` | 1 | only when the table reads planned treatment |
| `trt.end.source` | 3 | only with `ae.teae.end` = last_dose_plus_days |
| `pop.randomized.rule` | 1 | only with `tfl.population` = randomized |
| `pop.efficacy.rule` | 1 | only with `tfl.population` = efficacy |
| `disp.status.record` | 1 | only with `ae.teae.end` = end_of_study, and only for the subcategory of the treatment record |
| `date.studyday.origin` | 1 | never: no row of the table reads a study day (ADAE differs in 10 of 10) |

The last six rows are the catalog, not the generator: under the house
defaults the adverse event summary does not read those values. Every line
of `probes.jsonl` now says so in a field `reaches`, per decision: `always`,
`any_of` with the values of other decisions under which the difference
reaches the output, or `never`. gen-2a can predict its identifiability
matrix from that field and must sample decisions accordingly;
`date.studyday.origin` is `unseparated` for this slice in the sense of
section 4.7 until an output shows a study day.

## CDISC CORE: what "no unexplained error" means here

CORE v1.0.0 has 562 rules for SDTMIG v3.4. On every generated dataset, and
on the public CDISC pilot datasets alike, it cannot execute 38 of them and
six report whatever the data hold. "Pass CORE" can therefore not mean "no
finding". The gate reads every finding of every report (a finding is a
rule and a dataset) and accepts it only when an entry of
`src/specfirst/gen/core_findings.yaml` names the rule and the condition of
the entry holds for this finding:

| Kind | Condition | Entries |
| --- | --- | --- |
| `cannot_run` | status EXECUTION ERROR and the error text of the entry: the engine failed, the data were not judged | 6 entries, 38 rules |
| `dataset` | one issue for a dataset as a whole, no record | CORE-000510 (split datasets) |
| `every_record` | the rule reports every record of the named dataset | CORE-000757 (EX), CORE-002034, CORE-002056, CORE-002084 (AE) |
| `repeated_key` | as many issues as the dataset has records of subjects with more than one record (the check compares the number, not the subjects) | CORE-000544 on SV, which has no sequence number |
| `study` | one issue for the study, no subject | CORE-000735, CORE-002081 (the invented drug has no code) |
| `probe` | every issue is a record of a subject that one of the named probes planted in that dataset | 5 entries, 10 rules |

What the 38 rules would have looked at, from pass 2 of the review (F24):
MedDRA terms, codes and version (13 rules; the event dictionary is the
generator's own, so these would report every event if they ran); codes of
the trial summary in SRS, NDF-RT, MED-RT and SNOMED (10); country codes in
DM and TS (3); race and ethnicity options, variable lengths and file tags
from the Define-XML (4); the versions in TS (2); FDA's desired trial
summary parameters (2); extended terms of extensible codelists and LOINC
(2); and two that touch every record: CORE-002121, the ISO 8601 form of
every date value, on all 11 datasets, and CORE-002101, TAETORD against TA,
on 9. So "passes CORE" says nothing about the form of a date as such,
about TAETORD or about a country code. The reviewer looked at these three
in the 20 datasets himself: all 199,315 date values have an ISO 8601
form, the six country codes are valid, and SE.TAETORD is the order of TA
for every subject with a planned arm. One thing a rule might report if it
ran: the screening element of a subject without an arm (342 screen
failures, 12 not assigned) carries TAETORD 1.

Everything else fails the gate, and so does an entry that no finding
needed. A report counts only when it names the pinned engine, the
standard, the datasets that were handed over with their numbers of
records, Define-XML 2.1.0 and the terminology package that the Define-XML
names.

Over the 20 reports of the gate: 1,825 findings (84 to 94 per dataset),
all explained; 1,320 of them are the 38 rules that cannot run, on every
dataset or once per run; 220 are the rule about split datasets, once per
dataset file and run. The 145 findings of the kind `probe` are the ones
the generator causes on purpose, for example a subject who is dosed
without being randomized (four rules of DM report that subject), or an
event after the end of the study. They are in every twin and in the
visible data only where the sampled part includes the probe, which is why
a twin always has 18 rules with issues and the visible data 8 to 18.

Two planted defects prove the check on a copy of the twin of the first
seed, both in subjects that no probe planted: two events of one subject
with the same AESEQ, and another actual arm than the planned one. CORE
must report both, and the list must not explain them: the entry that
explains the same rule for SV must not cover AE, and the entry that
explains an arm mismatch for the probe must not cover another subject. A
finding counts as the planted one only when it names the rule, the dataset
and the subject (lesson 36).

CORE 1.0.0, run this way, reports no value outside its codelist (lesson
36). The observation was made early in the day and is repeated here with
its output: eight defects planted in the twin of the first seed, in
subjects that no probe touched, one run of CORE, and every finding that is
new or changed against the report of the unchanged twin. The script is a
scratch file of the session and is not kept.

```text
$ flock /run/lock/specfirst-heavy.lock python -B defect_try.py /root/scratch-gen1a/again gen-1a-1
planted: {'SEX=X': 'SFATXTPG-101-001', 'AGEU': 'SFATXTPG-101-003', 'bad date': 'SFATXTPG-101-004'}
planted: {'duplicate AESEQ': 'SFATXTPG-101-001', 'end before start': 'SFATXTPG-101-002', 'AETERM empty': 'SFATXTPG-101-003', 'AESER=MAYBE': 'SFATXTPG-101-003', 'AESEV=TERRIBLE': 'SFATXTPG-101-003'}
statuses before: {'EXECUTION ERROR': 38, 'ISSUE REPORTED': 18, 'SKIPPED': 191, 'SUCCESS': 315}
statuses after:  {'EXECUTION ERROR': 38, 'ISSUE REPORTED': 26, 'SKIPPED': 191, 'SUCCESS': 307}
CORE-000087 AE ISSUE REPORTED: count 0 -> 1; new subjects ['SFATXTPG-101-003']; variables ('AESER', 'AETERM'); AESER is populated, but not equal to 'N' or 'Y'.
CORE-000138 AE ISSUE REPORTED: count 0 -> 2; new subjects ['SFATXTPG-101-004']; variables ('AESTDTC', 'AESTDY', 'RFSTDTC'); AESTDY is populated but either AESTDTC or RFSTDTC in the DM dataset does not contain a complete date value.
... (CORE-000138 for DS, EX, SE and SV, CORE-000139 for AE, EX, SE and SV, CORE-000354 for VS: the same subject and the same date)
CORE-000266 AE ISSUE REPORTED: count 0 -> 1; new subjects ['SFATXTPG-101-003']; variables ('AESCAN', 'AESCONG', 'AESDISAB', 'AESDTH', 'AESER', 'AESHOSP', 'AESLIFE', 'AESMIE', 'AESOD', 'AETERM'); AESER is not equal to 'N', but none of the seriousness events categories (...
CORE-000356 AE ISSUE REPORTED: count 0 -> 1; new subjects []; variables ('variable_name', 'variable_value'); Required variable has a missing value.
CORE-000544 AE ISSUE REPORTED: count 0 -> 2; new subjects ['SFATXTPG-101-001']; variables ('DOMAIN', 'POOLID'); AESEQ must be a unique number per USUBJID per domain, or a unique number per POOLID per domain, including when the domain is split into multiple files
CORE-000553 AE ISSUE REPORTED: count 0 -> 1; new subjects ['SFATXTPG-101-002']; variables ('$val_endy', 'AEENDTC', 'AEENDY', 'RFSTDTC'); AEENDY is not calculated correctly even though the date portion of AEENDTC is complete and the date portion of RFSTDTC is complete.
CORE-000718 AE ISSUE REPORTED: count 0 -> 1; new subjects ['SFATXTPG-101-002']; variables ('AEENDTC', 'AESTDTC'); AESTDTC falls after AEENDTC.
CORE-002034 AE ISSUE REPORTED: count 150 -> 149; new subjects []; variables ('AESTDTC', 'AETERM', 'AETRTEM'); Missing treatment-emergent flag (AETRTEM) for the Adverse Event.
```

Reported: the invalid date, the event that ends before it starts, the
missing term, the repeated sequence number, and AESER = MAYBE, which two
rules about that one variable name. Not reported by any rule: SEX = X,
AGEU = FORTNIGHTS and AESEV = TERRIBLE. No finding of DM is new, and the
subject with the two wrong terms of AE is named for AESER and AETERM only.
(CORE-002034 lost one record: the event without a term.) The gate
therefore has a check of its own beside CORE, "controlled terms": every
value of a variable with a codelist, and every code of the trial summary,
is looked up in the terminology package that CORE ships. The two defects
the gate plants in CORE are two that CORE does report.

## Limits

Section 6.8 applies: the studies are built for decision coverage, not for
clinical realism. Beyond that:

- The emergence window. The three probes of `ae.teae.end` put their events
  N, N + 1 and N + 2 days after the last dose and 2 days after the end of
  the study, N being the follow-up length of the design (7, 14, 28 or 30
  days). `probes.jsonl` gives N as `parameters.window_days`. A kit whose
  SAP names a window far from N has data that do not separate the decision
  (30 days against no end, in a design with N = 7 or 14: nothing differs).
  gen-2 must sample the number of days to fit, so in every kit that
  separates the decision the window of the SAP equals the follow-up length
  of the protocol. The same holds for `trt.end.source`, more strictly: its
  pair last_ex_end_date against ds_date_when_ex_missing differs in the
  table for a window of exactly N days and no longer for N + 2 (the
  reviewer, pass 2, 200 twins).
- The rows of the table. Where the log says that a difference `always`
  reaches the output, it assumes a table that shows the row for any
  adverse event, as both alternatives of `tfl.ae.summary.rows` can. With
  the rows RELATED and FATAL alone nothing differs for the decisions that
  act through one event (the reviewer, pass 2). The log names the rows a
  probe needs only for the count probes and for `ae.related.values`.
- `disp.status.record`. The planted subject has the end of treatment first
  and the end of the study last, as the recipe of the catalog says. "The
  last disposition event" and "the event with the subcategory STUDY
  PARTICIPATION" are then the same record, for every subject. The pair is
  separated only when the decision names the subcategory of the treatment
  record. The recipe comes from std-1; the finding goes to the std track.
- The count probes hold under conditions that the log now names in
  `detail.assumes`: `tfl.population` = safety, `pop.safety.grouping` =
  actual, `trt.actual.source` = dm_actarm, and rows that show ANY or
  SERIOUS (rounding) or FATAL (the zero count). Under
  `trt.actual.source` = first_ex_treatment a planted subject joins the
  placebo group and its count is no multiple of 16 any more.
- Every twin has a placebo arm of 16 k treated subjects of whom exactly k
  have a serious event and 5 k, 9 k or 13 k have any event on or after
  the first dose, and in which nobody dies. Someone who knew that could
  tell a twin from other data; the visible data carry the calibration
  only when the sampled part includes the probe.
- In a design without an efficacy-evaluable set the alternative `efficacy`
  of `tfl.population` cannot be built; the log claims no pair with it
  there. The catalog has no applicability per alternative.
- Cancellation between planted subjects was looked for and removed in two
  places (the analysis sets, lesson 37; the end of emergence, where the
  subject without an exposure end date now has the only serious event of a
  planted subject). It is not absent: planted subjects share few arms, and
  the table counts subjects. Pass 2 of the review found a third case, not
  fixed here: with `tfl.population` = efficacy, the pair
  baseline_and_postbaseline against attended_visit of `pop.efficacy.rule`
  gives the same table in 4 of 109 twins with an efficacy set when the
  visit is the first one after day 1 (two planted subjects enter the set
  and two leave it, in one arm; none of the gate twins). gen-2a is the
  check, and must reject or regenerate such a kit.
- Values of a slot. The gate of gen-1 asks for pairs of alternatives. Two
  values of one slot of one alternative are another matter, and often give
  the same table, because the two subjects planted for the two values
  cancel in one arm (pass 2 of the review): the test of
  `pop.randomized.rule`, SYSBP against WEIGHT, with the table on the
  randomized set, in 125 of 200 twins; the test of `pop.efficacy.rule`
  with the table on the efficacy set in 52 of 109; its visit, the first
  against the second visit after day 1, in 5 of 97. In such a twin a wrong
  value of the slot does not show in the table. The log repeats what the
  catalog says a probe varies; it does not promise more.
- The hand experiment behind the table above follows the text of the
  catalog entries, not the engine. One reading is open since pass 1: what
  yamaa's `not_before` does with a partial start date in a month before
  the treatment start. The reviewer took the text of
  `ae.start.imputation` ("when it falls in that month"). If the engine
  moves every earlier date up to the treatment start, the pair
  first_of_month_not_before_first_dose against not_completed is not
  separated by its two probes.
- CDISC CORE 1.0.0 cannot execute 38 of its 562 rules for SDTMIG v3.4 and
  reports no value outside a codelist. The gate's own check of controlled
  terms covers the variables with a codelist in the generator's metadata,
  against the terminology package that CORE ships; it does not replace a
  validator.
- No TI dataset: the design model has no eligibility criteria. PLAN.md
  section 13.5 asks for "the trial design datasets CORE expects"; CORE's
  only rule on the matter (CORE-002056, an FDA rule) reports every domain
  the guide knows and the study lacks, with or without TI. TI comes with
  the rest of gen-1. This is a decision of the author that the owner may
  overrule.
- The design model has no strata, no endpoints and no analysis timing
  (section 6.2 names them). The slice does not read them; the rest of
  gen-1 needs them.
- The bytes of a study are promised for the pinned platform. Three
  distributions of the random streams go through the C library's
  logarithm, cosine and exponential; the gate compares builds of one
  machine. For the ten gate seeds the reviewer's build under Windows had
  the same bytes as the one under Linux; that is an observation, not a
  promise.
- The seed of a kit is a file outside every checkout; `seed_sha256` of the
  manifest is the SHA-256 of that file. The ten gate seeds are development
  seeds and are in the code.

## The day, for the record

- WSL lost its outbound TCP at about 10:20 and was unstable until the
  owner restarted WSL (11:40) and then Windows (11:54). In between, the
  lock of CORE was resolved with uv on the Windows side for Linux, and the
  unit tests ran in a scratch environment under Windows. After the
  network was back, `bash env/lock.sh` in WSL wrote all four locks byte
  for byte as committed.
- At 11:16 a scratch loop of this session started eight runs of CORE at
  once. CORE starts one worker per processor; the machine ran out of
  memory and the kernel ended processes of two other sessions as well
  (lesson 32). Since then the runner passes a pool size of 1, the gate
  starts at most four workers within half of the free memory, and every
  heavy run of every session waits for one lock.
- The official executable of CORE was downloaded and never run: the
  session's permission policy refused to execute a downloaded binary. CORE
  runs from source instead (ADR-006).

## The merge of `main`

`main` moved twice while the part was written: std-1 froze the catalog as
version 1 at node N1 (`f560171`), and real-3a merged (`38ba7af`). Both are
merged into `track/gen` in `18c23c8`, before the gate. The four files that
both tracks edit had conflicts (`CLAUDE.md`, `docs/lessons.md`,
`src/specfirst/cli.py`, `src/specfirst/gates.py`); both sides are kept.
real-3a took the lessons 27 to 31 first, so those of gen-1a are 32 to 38
(`11fec2c`); lesson 39 was added after the gate. The first pass of the
review was written before the renumbering and cites them as 27 to 33.

Nothing in the generator names a catalog version. Every generated file
carries what the catalog of the checkout says: `specfirst-m1 draft-1`
before the merge, `specfirst-m1 1` since, the way the standard form writes
`catalog@1` ("Catalog: specfirst-m1 1"). The gate ran after the merge, so
every number of this report is for `catalog@1`.

## Review

The independent review (rule R7) is in `docs/reports/gen-1a.review.md`. It
had two passes.

Pass 1 read commit `ec07012`, before the gate had run, and did not sign:
four findings blocked (F1 to F4), sixteen did not. The reviewer built a
reference implementation of the house specs for the slice and compared the
alternatives of every decision on the ten gate twins; that experiment found
what the gate could not (lessons 37 and 38). What was done about each
finding, all before the gate of this report:

| Finding | What was done |
| --- | --- |
| F1 `env/lock.sh` could not write the lock of CORE (blocked) | Fixed: its line continuations were broken. `bash env/lock.sh` in WSL then wrote all four locks byte for byte as committed. |
| F2 five probes of the treatment dates and the study day changed no result (blocked) | Each recipe adds the event that makes its alternatives differ, and its finder asks for the event. `date.studyday.origin` reaches no row of the table: the log says `never`. |
| F3 the probe of `tfl.population` cancelled in one gate twin (blocked) | The never-dosed subject is planned for the arm that the switched subject left; a test builds 60 designs with three or four arms and compares the counts of the two sets. |
| F4 the list of accepted CORE findings rested on one study, one finding open (blocked) | CORE ran on all ten seeds; every entry was read against the reports. CORE-000239 also reports the probe `partial_exposure_date_not_earliest` (the rule takes the minimum of the date texts); CORE-000544 on SV reports the subjects with more than one visit, not every record. |
| F5 seven decisions reach the table only under another decision's value | The field `reaches` in every log line. |
| F6 two recipes separate only for some values of a slot | The window probe has two subjects, so a window of N and of N + 1 days differ in the table. The rest is a limit, stated above and in the handover; the disposition recipe goes to the std track. |
| F7 pairs with `efficacy` claimed in a design without that set | Not claimed any more (`probes.alternatives_of`). |
| F8 the count probes hold under fewer decisions than the log said | `detail.assumes` names all of them. |
| F9 finders found patterns that do not separate | The finders ask for what the alternatives need (a dose, the time in EX, an event that is not over); twelve planted defects where the pattern is still there. |
| F10 the check trusted the log for which pairs a probe separates | The pairs come from the catalog; a log that claims other pairs is a problem. |
| F11 the gate did not ask that the twin carries every probe | It does. |
| F12 a report of CORE was not tied to the datasets; both builds in one process; the manifest not compared | The report must name the datasets with their numbers of records, Define-XML 2.1.0 and the terminology; the second build is made by a process of its own; the manifest is compared. |
| F13 "explained" wider than its reason in three places | A probe explains a finding only when every issue is a record of a planted subject; the two rules about every record are bound to AE; the missing TI is stated, here and in the list. |
| F14 ADR-006 and the code | Decision 7 says what the code does and the gate checks it in the report; pip is named; the doctor compares `env/core-requirements.in` with CORE's own list. |
| F15 `rng.py` claimed more than it gives | The module says what holds: the same bytes on the pinned platform. |
| F16 the documented models left out what the code does | Deaths, the action DRUG WITHDRAWN and the follow-up rules are in the module text; the calibrated placebo arm is under Limits. |
| F17 the hash of the seed was not the hash of the seed file | A seed file is taken byte for byte; a file inside any checkout is refused. |
| F18 records | `third_party/SOURCES.md` has a row for the codes in `sdtm.py`. |
| F19 scope | No strata, endpoints or TI in gen-1a: stated under Limits and for the owner. |
| F20 two small things in the data | A planted event outside the treatment period has the action NOT APPLICABLE. The event after the end of the study is intended. |

One more cancellation was found by the author when the reviewer's
experiment was repeated on the new recipes: between a window of N + 1 days
and the end of the study, the subject without an exposure end date and the
subject with an event between the two changed in opposite directions, and
in 7 of the 10 twins they share an arm. The first now has the only serious
event of a planted subject, so the count of serious events differs.

Pass 2 read the code of `39ff635` while the gate ran (part A), then the
gate log, this report and the handover (part B1), then the 21 reports of
CORE (part B2). Verdict: SIGNED, no blocking finding. What it established
that the author could not:

- The pair experiment, repeated with the reviewer's own scripts, gives the
  author's output byte for byte; every claim of the field `reaches` was
  checked on the ten gate twins and on 200 further twins.
- `core_findings.yaml` against the reports: judged again under Windows
  from the 20 reports and from studies generated there, 1,825 findings,
  all explained by the entries the gate log counts. The rows CORE-000544
  reports on SV are exactly the records of subjects with more than one
  visit in 20 of 20 reports; in all 505 findings with issues the number of
  issues equals the number of detail rows.
- The ten gate studies are byte for byte the same under Linux with Python
  3.12 and under Windows with Python 3.13: the reviewer's 510 files give
  the combined hash that the second CORE run printed for its own.

Its eight new findings, none blocking, and where each stands:

| Finding | Where it stands |
| --- | --- |
| F21 one more cancellation: `pop.efficacy.rule` on the efficacy set, 4 of 109 twins | not fixed; under Limits and in the handover |
| F22 `reaches` promises less than it reads: `always` needs the row ANY, `trt.end.source` needs a window of exactly N days, two interplays are missing | not fixed; under Limits and in the handover |
| F23 two values of one slot often give the same table | not fixed; under Limits and in the handover |
| F24 the report gave the number of the rules CORE cannot run, not their subjects | in this report now, section on CORE |
| F25 the claim that CORE reports no value outside its codelist holds as far as the reports show | this report quotes a run with planted values; the reviewer did not repeat it |
| F26 the record of the probe `dosed_but_not_randomized` is one that four rules for v3.4 do not allow, not an edge case of conformant data | for the owner and the std track, below and in the handover |
| F27 `repeated_key` compares the number of issues only; the check of controlled terms joins the two codelists of DSDECOD and skips COUNTRY and the codelists of the study | in the handover |
| F28 small things: `GENERATOR` unchanged, the epoch of one planted event, no test for `env/lock.sh`, the message of `clean_clone_gate.sh` | in the handover |

## GitHub and CI

`track/gen` is pushed to the owner's private repository. CI
(`.github/workflows/ci.yml`: the ASCII check, lint, the unit tests, on
GitHub's runner, which has no R, no fetch cache and no CORE) ran on every
push of the branch. On `39ff635`, the commit of the gate:

```text
run 44143376376 on track/gen at 39ff635: completed, success
ASCII check: 421 files checked, 0 with non-ASCII bytes
All checks passed!
889 passed, 19 skipped, 22 deselected in 99.67s (0:01:39)
```

The 19 skipped tests need R; in the gate, where R is installed, the same
selection gives 908 passed and none skipped. No unit test needs CORE: the
parts of the gate that decide are tested on planted values, and CORE itself
runs in the gate only. The earlier runs:

```text
run 44128793331 on track/gen at 9ee274b: completed, failure
run 44129757623 on track/gen at 85b5c7e: completed, success
run 44130529296 on track/gen at ec07012: completed, success
```

The failure was one test of the generator that looked for a text with a
space in a file the canonical writer writes without one; `85b5c7e` reads
the file as JSON instead.

The runs on the commit that holds this report and on `main` after the
merge cannot be in it; they are in GitHub, and the session reports them
when it hands the work back.

## For the owner

1. ADR-006 (CDISC CORE in the environment) is "proposed" and says that it
   stands unless the owner objects. It changes `env/`, which every track
   installs from: after this merge every checkout needs `make install`
   once (about 180 MB of downloads; 1 GB on disk, shared by all
   checkouts). Whether silence is approval is the owner's call.
2. No TI dataset in gen-1a (see Limits). Say so if the slice should carry
   an invented list of eligibility criteria now.
3. `date.studyday.origin` cannot be separated by the adverse event
   summary: no row reads a study day. For this slice it is `unseparated`
   (section 4.7); gen-2a will report it so.
4. For the std track: the recipe of the probe `two_disposition_events`
   separates `disp.status.record` only for the subcategory of the
   treatment record (see Limits), and `tfl.population` has an alternative
   (`efficacy`) that cannot be built in a design without that set.
5. The probe `dosed_but_not_randomized` (it separates the two rules of the
   safety set) is a DM record that four rules of CORE for SDTMIG v3.4 do
   not allow: no planned arm, the reason NOT ASSIGNED, and an actual arm
   with a reference period. The gate accepts those four findings as
   planted. The recipe of the catalog ("ARMCD is NOTASSGN") is older than
   v3.4; whether the probe can be a conformant record is a question for
   the std track (review finding F26).

## Files

- Environment: `env/core-source.txt`, `env/core-requirements.in`,
  `env/core-requirements.lock`, `env/core-sdist.txt`, `env/install.sh`,
  `env/lock.sh`, `env/README.md`, `scripts/env.sh`,
  `scripts/clean_clone_gate.sh`, `.gitignore`; `docs/decisions/ADR-006.md`.
- Code: `src/specfirst/cdisccore.py`, `src/specfirst/gen/` (13 modules and
  `core_findings.yaml`), and small changes in `src/specfirst/cli.py`,
  `doctor.py` and `gates.py`.
- Tests: `tests/unit/test_cdisccore.py`, `test_gen_rng.py`,
  `test_gen_design.py`, `test_gen_subjects.py`, `test_gen_probes.py`,
  `test_gen_gate.py`.
- Records: `third_party/SOURCES.md` (CORE and the standards of generated
  data), `docs/lessons.md` (lessons 32 to 39), `docs/state/gen.md`,
  `CLAUDE.md` (one command line, one gotcha), this report,
  `docs/reports/gen-1a.gate.log`, `docs/reports/gen-1a.core.log`,
  `docs/reports/gen-1a.review.md`.
