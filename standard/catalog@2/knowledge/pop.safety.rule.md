# Who is in the safety set? (`pop.safety.rule`)

The answer fixes the subjects and the column counts of every safety output. The alternatives
differ only for a subject who was dosed without being randomized.

## Where it is stated

- SAP: section on analysis populations or analysis sets.
- Protocol: statistical section, definition of the safety population.
- Almost always stated; the wording is usually close to ICH E9 section 6.3 (subjects who
  received at least one dose).

## Words to look for

- `at_least_one_dose`: "all subjects who received at least one dose of study treatment", "all
  treated subjects", "all subjects exposed to study drug".
- `randomized_and_dosed`: "all randomized subjects who received at least one dose",
  "randomized and treated subjects".
- Ambiguous between the two: "all subjects exposed to at least one dose of randomized
  treatment" (the FDA guide, section 2.1.1). "Randomized treatment" may mean the trial's
  treatment rather than a test of randomization; report the passage and say which reading
  was taken.
- A protocol written to ICH M11 says "participant" for subject and "study intervention" for
  study treatment: "all participants who received at least one dose of study intervention".

## Traps

- The word "randomized" in the sentence is the whole difference. It means assigned to an arm:
  a planned arm code that is neither screen failure nor not assigned. Pick by the text, even
  though both alternatives give the same set when nobody was dosed without randomization.
- "Received a dose" means that the subject has a treatment start date (`trt.start.source`,
  `trt.date.imputation`). Dispensing of study drug alone is not a dose.
- Added conditions such as "and at least one post-dose safety assessment" match no
  alternative; report the passage.
- Whether the set is grouped as treated or as randomized is `pop.safety.grouping`.
- Silent documents: use the house default and cite the house standard.
