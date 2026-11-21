# Who is efficacy-evaluable? (`pop.efficacy.rule`)

The answer fixes who is in the efficacy-evaluable set, a subset of the safety set, and so
the subjects and column counts of every output on that set.

## Where it is stated

- SAP: section on analysis populations, under names such as efficacy-evaluable, evaluable,
  completers or modified intent-to-treat.
- Protocol: statistical section, "analysis populations".
- The set has no standard definition, so it must be read from the documents.

## Words to look for

- `baseline_and_postbaseline`: "subjects with a baseline and at least one post-baseline
  measurement of ...". The slot `test` is the test code of the vital sign named there
  (systolic blood pressure gives SYSBP, weight gives WEIGHT).
- `attended_visit`: "subjects who attended the Week 8 visit", "subjects who completed the
  Week 24 visit", "completers through Week 24". The slot `visit` is the visit name as the
  schedule of assessments writes it.

## Traps

- Baseline is a value on or before the treatment start date; post-baseline is a value dated
  after it. A value on the day of the first dose is baseline, not post-baseline.
- "Completed the study" or "completed treatment" is a disposition status, not attendance of
  a named visit. Attended means that the subject visits data hold a record of that visit.
- Both alternatives start from the safety set. Sets built on protocol deviations, compliance
  limits or an assessment that is not a vital sign match no alternative; report the passage.
- The visit name is compared exactly with the collected visit name; copy it as written.
- Silent documents: this entry has no house default. Do not guess; a person must be asked.
