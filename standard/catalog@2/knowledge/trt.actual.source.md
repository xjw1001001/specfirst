# Where does actual treatment come from? (`trt.actual.source`)

The answer fixes the treatment a subject counts under whenever an analysis groups by actual
treatment. It matters only for subjects dosed with something other than their planned arm.

## Where it is stated

- SAP: section on analysis sets ("analyzed according to the treatment actually received") and
  any paragraph on dosing errors or treatment misallocation.
- Protocol: statistical section, definition of the safety population.
- Often only "as treated" is written, with no rule for how the actual treatment is found.

## Words to look for

- `dm_actarm`: "actual treatment arm", "the treatment the subject actually received" as
  recorded for the subject as a whole, "actual arm" with no rule based on single doses.
- `first_ex_treatment`: "the first treatment received", "the treatment given at the first
  dose", "based on the first administration of study drug".
- `same_as_planned`: "actual treatment is set equal to planned treatment", "treatment received
  is taken to be the treatment assigned", "actual treatment is assumed to be as randomized".

## Traps

- "As treated" alone answers `pop.safety.grouping` (group by actual treatment), not this
  entry. With no derivation rule stated, this entry is silent.
- "As randomized" said of the efficacy analyses only does not mean `same_as_planned`; that
  alternative needs a statement that actual treatment itself equals planned treatment.
- "First" in `first_ex_treatment` is the exposure record with the earliest start date, and
  the lowest sequence number on a tie.
- Rules such as "the treatment received for most of the study" or "the highest dose received"
  match no alternative. Report the passage instead of picking the nearest one.
- Silent documents: use the house default and cite the house standard.
