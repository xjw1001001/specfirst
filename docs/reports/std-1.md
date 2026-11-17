# std-1 Catalog, standard form, compiler, house standard: report

Date: 2026-11-11. Branch: `track/std`. Work stops here at owner node N1.

## Verdict

The gate passed. `scripts/clean_clone_gate.sh std-1` exited 0 on a clean
clone of commit `f86fe0f`, after a fresh install and a fresh fetch.
The complete output is in `docs/reports/std-1.gate.log`; the section "The
gate" quotes it.

This was the third gate run. The first one passed at commit `9a4b09f`. The
independent reviewer then found no blocking defect, ten major ones and six
minor ones (section "Review"). They were fixed, `main` (real-1) was merged
into the branch, and the gate passed again at `4002fc1`. The reviewer's
second pass left two major and three minor findings; four of the five were
fixed, and the gate was run a third time on the commit that holds
everything.

The independent review (rule R7) is in `docs/reports/std-1.review.md`.
Its verdict is PASS in both passes: the first on commit `9a4b09f`, the
second on `4002fc1`. What the second pass still found was fixed in
`f86fe0f`, the commit of the gate; the reviewer did not see those last
fixes (section "Review").

At the date of this report nothing was frozen: the catalog had the version
`draft-1`. The section "After node N1" at the end tells what happened
since. std-2 was not started.

## What std-1 asks for, and where it stands

| Item of PLAN.md section 13.4 | State | Where |
| --- | --- | --- |
| Schemas for catalog entries and decision records | catalog entry: new, version 0. Decision record: version 0 of base-0, unchanged; a change is proposed, not made | `standard/schemas/catalog-entry.schema.json`; ADR-004, "The four open schema points" |
| Entries for the M1 families, at least 40 | 43 entries, 62 questions when an entry is counted once per unit, 96 alternatives | `standard/catalog/entries/`; one page: `docs/reports/std-1.catalog.md` |
| Alternatives with statement templates | done; every statement renders and parses back | gate check 7 |
| A house default or none | 58 defaults, 4 questions without one | `standard/houses/open-default@1/STANDARD.md` |
| Public sources | every entry has at least one; 3 alternatives have none of their own and are listed | gate check 6; `unsourced_alternatives` in `catalog.yaml` |
| A compile template per entry | done: yamaa fragments, or parameters of the ARS and layout templates | `standard/catalog/templates/` |
| Phrasings | three per alternative (plain, formal, brief), each with the slots of its statement | `standard/catalog/phrasings/` |
| Reading notes | one file per entry | `standard/catalog/knowledge/` |
| Probe recipes | 50 probes; every pair of alternatives and every slot has one | `standard/catalog/probes.yaml`; gate check 5 |
| The compiler: decisions to yamaa, ARS and layout | done; layout is a draft until real-3 fixes the format | `src/specfirst/compile/compiler.py` |
| The standard-form renderer and parser | done, for statements and for documents with anchors | `src/specfirst/compile/standard_form.py` |
| House standard `open-default@1`: standards document, parent yamaa specs, ARS and layout templates | done | `standard/houses/open-default@1/` |
| Gate registered as `std-1`, planted defects for each new checker (R5) | done | `src/specfirst/gates.py`; `tests/defects/test_std1_checkers.py` |

## The gate

Gate text of PLAN.md section 13.4: the round trip decisions to statements to
decisions is exact for every alternative; compiled fragments pass `yamaa
check` and the ARS schema; every entry has at least one public source.

Command, run in Ubuntu 24.04 under WSL2 as root, in the worktree:

```text
$ bash scripts/clean_clone_gate.sh std-1
```

The script clones the repository with `git clone --no-local` into a new
folder under `/tmp`, checks out the commit, creates the Python environment,
the R library and the fetch cache of the clone under the same new folder,
and runs `specfirst gate std-1 --clean`. Output (the lines of the checks
that are new in std-1 in full; the others shortened; the whole log is
`docs/reports/std-1.gate.log`):

```text
clean clone gate std-1
repository: /mnt/d/trial_work/specfirst/.git
commit:     f86fe0fb7639756238cdad99264ac9c804dac76b
clone:      /tmp/specfirst-clean-LU5j4i/specfirst
environment and cache: /tmp/specfirst-clean-LU5j4i/env

$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /tmp/specfirst-clean-LU5j4i/specfirst

$ git -C /tmp/specfirst-clean-LU5j4i/specfirst checkout --quiet --detach f86fe0fb7639756238cdad99264ac9c804dac76b

$ git -C /tmp/specfirst-clean-LU5j4i/specfirst log -1 --format=%H %s
f86fe0fb7639756238cdad99264ac9c804dac76b std-1: second pass of the review (PASS) and what followed from it

$ bash env/install.sh
[...]
$ specfirst fetch
[...]
$ specfirst gate std-1 --clean
gate std-1 at commit f86fe0fb7639756238cdad99264ac9c804dac76b (clean)

== [1/12] environment: specfirst doctor
doctor: ok
-- PASS environment (0.3 s)
== [2/12] pins: specfirst fetch --verify
fetch: every pin verified
-- PASS pins (1.2 s)
== [3/12] lint: ruff check .
All checks passed!
-- PASS lint (0.0 s)
== [4/12] unit tests: pytest -m "not evidence" -q
543 passed, 13 deselected in 35.27s
-- PASS unit tests (35.5 s)
== [5/12] catalog: specfirst catalog
catalog specfirst-m1 draft-1: 43 entries, 62 questions (entry and unit), 96 alternatives, 9 units, 50 probes
schema and cross-references: 0 problems
compile templates on their examples: 0 problems
probes: every pair of alternatives, every slot: 0 problems
structural probes separate for any data: 0 problems
phrasings and reading notes: 0 problems
parameters set and read: 0 problems
-- PASS catalog (0.5 s)

== [6/12] public sources: specfirst catalog --sources
43 entries, 0 without a public source
104 citations: 59 to pinned sources, checked on the fetch cache (44 with a text that must stand in the file); 45 to published documents, judged and not checked by script
public sources: 0 problems
-- PASS public sources (0.0 s)

== [7/12] round trip: specfirst catalog --roundtrip
243 statements rendered and parsed back, for 140 alternatives (entry, unit and alternative)
round trip decisions to statements to decisions: 0 problems
document round trip on 62 decisions: 0 problems
-- PASS round trip (0.0 s)

== [8/12] yamaa check: specfirst catalog --yamaa
compiled files and built datasets: /tmp/specfirst-std1-gqxd4hlw (removed when the command ends)
106 decision vectors (the base and one changed decision each), 106 compiled
  note: tfl.pvalue.format/four_decimals #1: shows only beside another decision, for example tfl.tests.include/anova_chisq #1
every alternative compiles and changes the compiled files: 0 problems
47 distinct sets of ADaM specs, 141 entry specs checked by yamaa (each with its house parent and one fragment per decision)
yamaa check: 0 problems
-- PASS yamaa check (8.0 s)

== [9/12] yamaa run: specfirst catalog --run
106 decision vectors, compiled by an earlier check
47 distinct sets of ADaM specs, 141 datasets built by yamaa on the tiny study of specfirst.compile.tiny (4 subjects; this shows that the specs run, not that their values are right)
yamaa run: 0 problems
-- PASS yamaa run (5.7 s)

== [10/12] ARS schema: specfirst catalog --tables
106 decision vectors, compiled by an earlier check
ARS schema: project/jsonschema/ars_ldm.schema.json of the pinned source 'ars'
negative controls: 3 schema defects planted in the base ARS file, 3 reported
59 distinct ARS files with their layouts checked: schema, references, and that layouts and ARS name the same analyses
ARS schema and layouts: 0 problems
-- PASS ARS schema (0.6 s)

== [11/12] house standard: specfirst house
house standard open-default@1: 58 defaults, 4 decisions without a default, 3 parent specs, 4 table families
house standard: 0 problems
-- PASS house standard (0.0 s)

== [12/12] ASCII: python -m specfirst.asciicheck
ASCII check: 328 files checked, 0 with non-ASCII bytes
-- PASS ASCII (0.0 s)

PASS  environment          0.3 s
PASS  pins                 1.2 s
PASS  lint                 0.0 s
PASS  unit tests          35.5 s
PASS  catalog              0.5 s
PASS  public sources       0.0 s
PASS  round trip           0.0 s
PASS  yamaa check          8.0 s
PASS  yamaa run            5.7 s
PASS  ARS schema           0.6 s
PASS  house standard       0.0 s
PASS  ASCII                0.0 s
GATE std-1: PASS

clean clone gate std-1: PASS (clone kept in /tmp/specfirst-clean-LU5j4i/specfirst until /tmp is cleared)
```

What the numbers say:

- Round trip. Every alternative of every entry is rendered for every unit
  and for several slot values (its examples and awkward ones: text with
  commas, semicolons and quotes of the sentence, lists of one item) and
  parsed back. The parser must return exactly the decision that was
  rendered and no other: a statement that fits two templates is a problem.
- yamaa check. A changed decision gives a new set of ADaM specs only when
  it is an ADaM decision, so 106 decision vectors give 47 distinct sets.
  Each set has three entry specs (ADSL, ADAE, ADVS), each composed of the
  house parent and one fragment per decision: 141 checks.
- yamaa run. The same 141 specs are built on a study of four subjects.
  This is not in the gate text. `yamaa check` reads no data, and during
  std-1 all 141 specs passed it while one fragment could not run (lesson
  17).
- ARS schema. The 106 vectors give 59 distinct ARS files. Each is checked
  against the JSON Schema of the pinned ARS repository and for references
  that the schema cannot see; each layout must name the analyses of its
  ARS file and no other. Three planted schema defects are reported.
- Public sources. 59 citations name a file of a pinned source; the file
  must be in the fetch cache, and for 44 of them a quoted text must stand
  in it. 45 citations name a published document. A script cannot check
  those; see "Public sources" below.

## The catalog in numbers

| Unit | Entries | Alternatives | Without a default |
| --- | --- | --- | --- |
| mod-treatment | 6 | 15 | 0 |
| mod-populations | 5 | 10 | 1 (`pop.efficacy.rule`) |
| mod-demographics | 4 | 9 | 0 |
| mod-ae-emergence | 4 | 9 | 1 (`ae.related.values`) |
| mod-bds-visits | 5 | 13 | 0 |
| table families: entries that several families answer | 8 | 18 | 0 |
| tfl-demographics | 5 | 10 | 1 (`tfl.demog.rows`) |
| tfl-ae-summary | 1 | 2 | 0 |
| tfl-ae-soc-pt | 3 | 7 | 0 |
| tfl-vitals-by-visit | 2 | 3 | 1 (`tfl.vs.scope`) |
| total | 43 | 96 | 4 |

Against appendix B (46 entries): four entries and two alternatives are
left out and one entry is added. Every change is in ADR-004, item 7, and in
the last section of `docs/reports/std-1.catalog.md`.

## Public sources

Rule 3 of section 2.1 asks that names and rules come from public standards
and that each entry cites its source. How each kind was confirmed:

| Kind | Citations | How confirmed |
| --- | --- | --- |
| A file of a pinned source (yamaa, Pilot 7, ARS, Pilot 6) | 59 | by the gate, on the fetch cache: the file exists; for 44 a quoted text stands in it |
| admiral, functions `derive_var_trtemfl` and `derive_vars_dt` | 4 of the 8 to admiral | read in this session (source on GitHub, main branch, 2026-11-11) |
| ICH E9 | 3 | read in this session (the guideline from database.ich.org, sections 5.2.1 to 5.2.3 and 6.3) after the reviewer doubted two section numbers; both were wrong and are corrected |
| ADaMIG 1.3, OCCDS 1.1, SDTMIG 3.4, ICH E3, the FDA guide, the R and SAS manuals, other admiral functions | the rest of 45 | cited from the published text; not fetched in this session |

The last row is a limit. Those citations name the place (a section, a
variable, a function) and are believable, but nobody opened the document
in this work package. `standard/catalog/sources.yaml` marks each source
with `confirmed: read` or `confirmed: cited`. admiral is not among the
pinned sources of appendix A; pinning it would let the gate check its
citations too.

Three alternatives have no public source of their own (`pooled_below_count`
of `demo.race.pooling`, `end_of_study` of `ae.teae.end`,
`descending_frequency_highest_dose` of `tfl.ae.socpt.sort`). They come from
the seed list of appendix B. The owner decides whether each stays.

## Reading guide for the owner (node N1)

Section 2.3: at N1 the owner decides the decision catalog, the standard
form and the house standard for the M1 families. Three files hold all of
it; the rest of the diff is machinery that the gate checks.

1. `standard/houses/open-default@1/STANDARD.md` (225 lines). The
   house standard: 58 defaults, each one sentence of the standard form with
   its anchor, and under it what the sentence means. Read every line: a
   default here is what a study gets when its documents are silent. The
   end of the file lists the four questions that have no default.
2. `docs/reports/std-1.catalog.md` (637 lines). The whole catalog on
   one page: per entry the question, every alternative with its statement
   and meaning, the default, the slots, the sources and the probes. Read
   the statements as a reviewer of a study would: is each sentence one a
   statistician would sign, and are the alternatives the ones real
   documents choose between? The last two sections list what has no public
   source of its own and what was left out.
3. `docs/decisions/ADR-004.md` (217 lines). The choices behind the
   formats, everything that departs from appendix B (item 7), and the four
   schema points.

Questions that need the owner's word. Each has what was delivered; a short
answer per number is enough.

| # | Question | Delivered |
| --- | --- | --- |
| 1 | Analysis set of the demographics table when the documents are silent | the randomized set; the three safety tables use the safety set (appendix B: safety for all) |
| 2 | Analysis visits when the documents give no window table | the collected visit (appendix B: protocol windows, which a house standard cannot supply) |
| 3 | `pop.efficacy.rule` | no default: both alternatives name a study measure or a visit |
| 4 | Left out: `ae.teae.worsening`, `ae.severity.worst`, `ae.occurrence.flags`, `disp.reason.source`; the mean of pre-dose values as baseline; the average of a window | each with its reason in `catalog.yaml`; they return with the data or the table family that makes them identifiable |
| 5 | Three alternatives without a public source of their own | kept and listed; drop them or keep them as the plan's own |
| 6 | Baseline of a parameter, default "last before the first dose": a value on the first dose day counts unless both times were collected and the value is not earlier | as stated; a value on that day timed after the dose is then neither baseline nor post-baseline |
| 7 | Baseline weight and height of ADSL: the last value on or before the treatment start date, by date | differs from the rule of ADVS in question 6; one rule for both may be wanted |
| 8 | Treatment emergence: an event without a start date is emergent; one that ended before treatment is not; a subject without treatment has none | as admiral's `derive_var_trtemfl` |
| 9 | Partial exposure dates, default: not completed and left out of the treatment dates | the other alternative completes with the first day of the month, end dates too |
| 10 | Randomized: DM.ARMCD present and not SCRNFAIL or NOTASSGN. Unscheduled visit: VISITDY missing. A record with a dose: EXDOSE above zero, or zero with PLACEBO in EXTRT | fixed in the notes of the entries; generated studies must follow them |
| 11 | Age groups of the default: below 65, 65 to 80, above 80 | the groups of the pilot |
| 12 | A total column in all four tables by default | appendix B; the pilot CSR has one in the demographics table only |
| 13 | The four schema points of ADR-000 item 7 | a recommendation each in ADR-004; none applied |
| 14 | The entry format: `units`, typed slots, structured sources, data templates in place of Jinja | ADR-004, items 1 to 3 |

After the owner's answers the agent edits the entries, runs `specfirst
house --write` and the gate, sets the catalog version to 1 and tags
`catalog@1`.

## Limits

- The compiled specs are shown to run, and for 50 cases to give the value
  their statement speaks of, on a hand-made study of four subjects. That
  is not a proof on real or generated data. std-2 checks the fragments by
  result on the pilot; gen-2 checks P4 on the twin.
- The layout files are a draft. real-3 fixes the layout format (ADR-003).
- The treatment columns are data-driven. "Ascending dose" and "protocol
  order" are rules that the grid builder must resolve from the design.
- Published documents other than ICH E9 and two admiral functions were not
  opened (section "Public sources").
- yamaa's lint is not run on compiled files.
- Phrasings are checked for their slots only. That each means exactly what
  its statement means is a judgement; the reviewer sampled it.
- Known limits of the house specs are listed in `docs/state/std.md`.

## Review

A fresh-context agent that did not write the work reviewed it twice. Its
text is `docs/reports/std-1.review.md`; nothing in it was edited by the
author.

First pass, commit `9a4b09f`: verdict PASS, no blocking finding, ten major
and six minor. What was done about each, in commit `4002fc1`:

| # | Finding | What was done |
| --- | --- | --- |
| 1 | The state file named a report, a gate log and a review that were not committed | they are committed with this report |
| 2 | The check "yamaa run" crashed in a checkout on a Windows drive | the checks build in a temporary folder; a refusal of the engine is a problem, not a crash; run again in the worktree |
| 3 | One partial exposure date could void the treatment dates of a dosed subject | a partial date takes part only as far as `trt.date.imputation` completes it; statements and definitions changed; the end date reads records with a dose |
| 4 | The baseline weight on a tie did not follow its definition | the definitions of "last" now say what the order does |
| 5 | The binds were neither complete nor sound | binds are proven by mutation (`compiler.bind_tables`) |
| 6 | The probe of the column order separated nothing for the usual design | probes have the kinds record, structural and design; a structural claim is compiled |
| 7 | The ARS check missed a wrong denominator and an unknown operation | the check follows numerator and denominator references |
| 8 | Only the base decisions were compared with their statements | 50 cases build a tiny study with a changed decision and compare a value |
| 9 | The document parser dropped an indented or bulleted statement | a line with an anchor, or with a statement and no anchor, is an error |
| 10 | Result patterns in the ARS file contradicted the decimals of the layout | the ARS file holds no result pattern; the layout alone holds display formats |
| 11 to 16 | Citations, a missing inclusion decision, tables that contradict themselves, the catalog line, two inaccuracies, defaults a statistician may not expect | corrected; ICH E9 was read and two section numbers were wrong; the defaults are listed for the owner in the reading guide and in `docs/state/std.md` |

Second pass, commit `4002fc1`: verdict PASS. Findings 2, 4, 7 and 10 to 15
fixed; 6 fixed in the catalog; 1 open until this report is committed. Left
or new: two major (17, 18) and three minor (19, 20, 21). In commit
`f86fe0f`:

| # | Finding of the second pass | What was done |
| --- | --- | --- |
| 17 | A date with a missing part in the middle (`2024---15`) still counted as complete | a date text takes part when it reads YYYY-MM-DD, or YYYY-MM for the month rule; the tiny study has such a record |
| 18 | A bind was proven against the examples only; a list of rows bound nothing | each list of the value is also tried with one item left out |
| 19 | The structural probe check cannot see a claim that fails for a given design | left open; recorded in `docs/state/std.md`. The kind `design` exists for such a probe |
| 20 | Four further planted template defects passed all tests | ten more cases on a tiny study with a fourth subject |
| 21 | A statement without its anchor was skipped | it is an error |

The fixes of the second table came after the signed second pass. The gate
of this report ran on the commit that holds them; the reviewer did not
read them.

## What the session learned

`docs/lessons.md`, lessons 17 to 22: `yamaa check` reads no data; one ID
with two meanings; a rule read on data before it is trusted; a gate run
where the work is done; minimum and maximum of date texts; binds proven by
mutation.

## GitHub and CI

`track/std` at `f86fe0f` was pushed to the owner's private repository
`xjw1001001/specfirst`. CI (tests, lint, ASCII check) succeeded on that
commit: run 43088197844,
https://github.com/xjw1001001/specfirst/actions/runs/43088197844.

CI does not run the gate: it has no fetch cache. The test of the ARS schema
skips there; the gate runs the same control on the pinned schema.

The merge of `track/std` into `main` and the CI run of `main` come after
this report; the git history and `docs/state/std.md` record the merge.

## Size and budget

220 files changed against `main` before the merge of this branch, 13,887
lines added: 43 entries with their templates, phrasings and notes (172
files), the house standard, eleven Python modules of
`src/specfirst/compile/` and their tests. One session, within the estimate
of two to three (section 13.1).

## After node N1

Added on 2026-11-17. The sections above are the report of 2026-11-11; nothing
in them was changed except the pointer to this section in the verdict.

- The owner answered the 14 questions on 2026-11-17: "as delivered" for
  every one, and provisional. Asked separately, the owner confirmed the
  freeze the same day. The record, with the owner's words in translation
  and what the answer does not cover, is in `docs/decisions/ADR-004.md`,
  section "Node N1: the owner's answer".
- No entry, alternative, default or statement changed. `catalog.yaml` says
  that the three alternatives without a public source of their own are
  kept as the plan's own.
- `main` with real-2 and ADR-005 was merged into the branch first.
- The catalog is version 1 and the tag `catalog@1` marks it. STANDARD.md
  and `docs/reports/std-1.catalog.md` were rendered again; only the
  version in their head lines changed.
- Schema point 3 (which records must cite) was not applied: std-2 does it.
  std-2 was not started.

The gate on the frozen catalog: a clean clone of commit `12d0ce3`,
a fresh install and a fresh fetch. It ran inside the lock that the
sessions on the owner's machine share for heavy runs, on four processors.
The lines below are the commands and the checks; the complete output is
in `docs/reports/std-1.n1.gate.log`.

```
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh std-1
clean clone gate std-1
commit:     12d0ce3cb05705f5284556178263b3a4cfe74a53
$ git clone --quiet --no-local /mnt/d/trial_work/specfirst/.git /tmp/specfirst-clean-RwjDWq/specfirst
$ git -C /tmp/specfirst-clean-RwjDWq/specfirst checkout --quiet --detach 12d0ce3cb05705f5284556178263b3a4cfe74a53
$ git -C /tmp/specfirst-clean-RwjDWq/specfirst log -1 --format=%H %s
12d0ce3cb05705f5284556178263b3a4cfe74a53 std-1: catalog frozen as catalog@1 (version 1) on the owner's word at node N1
$ bash env/install.sh
R packages: 99 wanted, 99 to install from https://packagemanager.posit.co/cran/__linux__/noble/2026-11-10
R library matches the lock: 99 packages in /tmp/specfirst-clean-RwjDWq/env/r-lib
doctor: ok
$ specfirst fetch
$ specfirst gate std-1 --clean
gate std-1 at commit 12d0ce3cb05705f5284556178263b3a4cfe74a53 (clean)
doctor: ok
-- PASS environment (0.2 s)
-- PASS pins (0.8 s)
-- PASS lint (0.0 s)
674 passed, 19 deselected in 37.77s
-- PASS unit tests (38.1 s)
-- PASS catalog (0.5 s)
-- PASS public sources (0.0 s)
-- PASS round trip (0.0 s)
-- PASS yamaa check (7.7 s)
-- PASS yamaa run (5.2 s)
-- PASS ARS schema (0.6 s)
-- PASS house standard (0.0 s)
-- PASS ASCII (0.0 s)
GATE std-1: PASS
clean clone gate std-1: PASS (clone kept in /tmp/specfirst-clean-RwjDWq/specfirst until /tmp is cleared)
```
