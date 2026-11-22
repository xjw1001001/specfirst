# Who is in the randomized set? (`pop.randomized.rule`)

The answer fixes the subjects and the column counts of every output on the randomized set,
which documents usually call the intent-to-treat set or the full analysis set.

## Where it is stated

- SAP: section on analysis populations or analysis sets.
- Protocol: statistical section, "analysis populations".
- Almost always stated, under names such as ITT, FAS, randomized set or all randomized.

## Words to look for

- `all_randomized`: "all randomized subjects", "all subjects assigned to a treatment arm",
  "regardless of whether study treatment was received".
- `randomized_with_postbaseline`: "randomized subjects with at least one post-baseline
  assessment of ...", often called modified intent-to-treat. The slot `test` is the test code
  of the vital sign named in that sentence (systolic blood pressure gives SYSBP).

## Traps

- "Randomized and received at least one dose" is a dosing condition, not a post-baseline
  value. It matches no alternative here; report the passage (compare `pop.safety.rule`).
- Post-baseline means dated after the treatment start date. A value on the day of the first
  dose does not count, and "after randomization" is not the same condition.
- The second alternative needs a vital sign. If the required assessment is a questionnaire,
  a laboratory test or "any efficacy assessment", report the passage.
- When the SAP defines both an all-randomized set and a narrower evaluable set, this entry is
  the all-randomized one; the narrower set belongs to `pop.efficacy.rule`.
- Silent documents: use the house default and cite the house standard.
