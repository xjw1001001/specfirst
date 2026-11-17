# Track gen

Result: generated studies for the parallel-group design PG-FIX (PLAN.md
section 13.5), first for the slice "adverse event summary first" (ADR-005).

## Passed

- gen-1a (2026-11-17): CDISC CORE in the environment (ADR-006); the design
  model and the sampler for PG-FIX; the subject process; SDTM for eleven
  domains with Define-XML; 28 probes for the 22 decisions of the slice,
  each read back from the data; the gate `gen-1a`; `specfirst gen`.
  Gate: `scripts/clean_clone_gate.sh gen-1a` exited 0 on a clean clone of
  `39ff635`, 8 of 8 checks (docs/reports/gen-1a.gate.log): CORE on the 20
  datasets of ten seeds with 1,825 findings, none unexplained; identical
  hashes from two processes; a probe in the twin for each of the 32 or 35
  pairs of alternatives.
  Report: docs/reports/gen-1a.md. Review: docs/reports/gen-1a.review.md,
  signed in its second pass, with eight findings that do not block (F21
  to F28; below).

## Open

What gen-2a meets first (docs/reports/gen-1a.md, "What the probes prove"
and "Limits"):

- The gate of gen-1a proves that every probe is in the SDTM of the twin
  with what its alternatives need to differ. It does not build both
  alternatives. gen-2a owes that proof ("every applicable decision of the
  slice is separated on the twin"). A hand experiment with a reference
  implementation says the output differs for every pair at the house
  defaults in the ten gate twins, except where the next three points say
  otherwise.
- Every line of `gold/probes.jsonl` has a field `reaches`: under which
  values of other decisions a difference reaches the adverse event summary.
  Five decisions reach it only under another decision's value
  (`trt.planned.source`, `trt.end.source`, `pop.randomized.rule`,
  `pop.efficacy.rule`, `disp.status.record`), three only when the table
  shows a certain row (`ae.related.values`, `tfl.percent.format`,
  `tfl.rounding.rule`); `date.studyday.origin` never does and is
  `unseparated` for this slice (section 4.7). Sample the decisions of a
  kit with that field, or the matrix of section 6.5 has holes.
- `ae.teae.end`: the events are planted around a window of N days, N being
  the follow-up length of the design (`parameters.window_days` in the
  log). A kit must take that number for the slot `days`.
- The count probes hold under the decisions named in `detail.assumes` of
  their log lines.
- `disp.status.record`: the two alternatives pick the same record unless
  the subcategory is that of the treatment record (see "For the std
  track"). A kit that names the study participation record does not
  separate the decision.
- Values of one slot are not pairs of alternatives, and the planted
  subjects for two values often cancel in one arm: a wrong `test` of
  `pop.randomized.rule` is invisible in the table on the randomized set in
  125 of 200 twins, a wrong `test` of `pop.efficacy.rule` in 52 of 109, a
  wrong `visit` (first against second visit after day 1) in 5 of 97.
  read-1a should know this as well.
- The hand experiment follows the text of the catalog entries, not the
  engine. Open since pass 1 of the review: what yamaa's `not_before` does
  with a partial start date in a month before the treatment start. If it
  moves every earlier date up to the treatment start, the pair
  first_of_month_not_before_first_dose | not_completed of
  `ae.start.imputation` is not separated by its two probes.
- Cancellation between planted subjects is removed where it was found (the
  analysis sets; the end of emergence). Planted subjects share few arms and
  the table counts subjects: check each kit, do not assume. One case is
  known and not fixed: with `tfl.population` = efficacy, the pair of
  `pop.efficacy.rule` gives the same table in 4 of 109 twins when the
  visit of attended_visit is the first one after day 1.

Found by pass 2 of the review after the gate, and left as they are so that
the code of the merge is the code that passed the gate. They are for the
first commit of gen-2a:

- `reaches` says `always` for the decisions that act through one event;
  that assumes a table with the row ANY. It says "an emergence window" for
  `trt.end.source`, which needs a window of exactly N days. Two interplays
  are not in it: the pair first_of_month_not_before_first_dose |
  first_of_month of `ae.start.imputation` is lost under `ae.teae.start` =
  at_or_after_first_dose_time, and no_end | end_of_study of `ae.teae.end`
  under `disp.status.record` with the subcategory of the treatment record.
- `gate._holds`, kind `repeated_key`: it compares the number of issues
  only. A finding of the right size that names other subjects would be
  explained. Compare the subjects as the kind `probe` does.
- `gate.term_problems` accepts a milestone term in a disposition event (it
  joins the two codelists of DSDECOD) and does not look at COUNTRY or at
  the codelists of the study itself.
- `GENERATOR` is still "gen-1a.1" although the recipes changed after the
  first push: no study of that version was ever kept, but the next change
  of a recipe must change the name.
- The event of `no_exposure_end_date` lies after the subject left the
  study and has the epoch TREATMENT (`sdtm.epoch_of` takes the last
  element of the subject).
- The screening element of a subject without an arm has TAETORD 1 in SE.
  The rule of CORE that compares TAETORD with TA cannot run (CORE-002101),
  so nothing reports it; decide what such an element should carry.
- No test or gate check reads `env/lock.sh`: the broken script of pass 1
  passed `bash -n` and everything else. `scripts/clean_clone_gate.sh`
  still says "clone kept ... until /tmp is cleared" (lesson 39).

For the std track:

- The recipe of the probe `two_disposition_events` gives a subject whose
  last disposition event is the study participation record, so
  `disposition_event` and `disposition_event_by_subcategory` pick the same
  record unless the subcategory is that of the treatment record.
- `tfl.population` has the alternative `efficacy` in every design; in a
  design without that set it cannot be built. The generator claims no pair
  with it there. The catalog has no applicability per alternative.
- The probe `dosed_but_not_randomized` is a DM record that four rules of
  CORE for SDTMIG v3.4 do not allow (CORE-000192, CORE-000758,
  CORE-000927, CORE-002099): no planned arm, the reason NOT ASSIGNED, an
  actual arm and a reference period. The gate accepts the four findings
  as planted. The recipe of the catalog ("ARMCD is NOTASSGN") is older
  than v3.4: can the probe be a conformant record? Until that is settled
  the reason of the entry `probe-dosed-but-not-randomized` in
  `core_findings.yaml` should say that the rules refuse the record
  (review finding F26).

For the owner (docs/reports/gen-1a.md, "For the owner"): ADR-006 is
proposed and stands unless the owner objects; the slice has no TI dataset.

Not done, and not part of gen-1a: strata, endpoints and analysis timing in
the design model; eligibility criteria and TI; the probes of the other
three table families; domains beyond the eleven.

## Next

- gen-2a (needs gen-1a, std-1 after N1, real-3a: all on `main` now): sample
  decisions of the slice within the house standard, compile, build with
  both engines on the visible data and on the twin, P1 to P4, splits.
  Start from `specfirst gen study` and `specfirst.gen.study.read_tables`;
  the Parquet files of a study have the names the parent specs expect.
- Then gen-3a, then the rest of gen-1, gen-2 and gen-3.

How to run things:

- After merging `main`: `make install` once; `specfirst doctor` must say
  "CDISC CORE v1.0.0 at f3282a0d870b: 0 differ".
- `specfirst gate gen-1a` takes about 20 minutes, nearly all of it CORE
  (20 runs, each about 80 seconds and up to 3 GB). The WSL machine is
  shared: wrap every gate, test suite or generator run in
  `flock /run/lock/specfirst-heavy.lock <command>` and never start runs of
  CORE by hand in parallel (lesson 32).
- The gate keeps the reports of CORE in `build/gates/gen-1a/core/`. Read a
  finding there before adding it to
  `src/specfirst/gen/core_findings.yaml`; an entry that no finding needs
  fails the gate. In a clean clone that folder is under `/tmp`, which WSL
  clears when the instance restarts, a minute after the last command:
  copy the reports out in the same command (lesson 39).
- A new release of CORE is a new pin (`env/core-source.txt`), `make lock`,
  `make install`, and a new reading of that list.

## Handed over by base-0

- CDISC CORE: installed by gen-1a through `env/` (docs/decisions/ADR-006.md).
