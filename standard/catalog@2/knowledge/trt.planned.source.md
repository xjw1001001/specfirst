# Where does planned treatment come from? (`trt.planned.source`)

The answer fixes the planned treatment label of each subject. That label names the treatment
columns and groups every analysis done by planned treatment.

## Where it is stated

- Protocol: study design and treatment arms, randomization section (the list of arms).
- SAP: section on treatment groups or display conventions; column headers of the table shells.
- Often unstated: documents name the arms in prose and do not say how the label is obtained.

## Words to look for

- `dm_arm`: "planned treatment is the arm assigned at randomization", "as randomized", arm
  names used in tables exactly as the protocol lists the arms, with no relabelling rule.
- `dm_armcd_map`: an explicit list or table that pairs arm codes with display labels, such as
  "A = Drug X 10 mg, B = Placebo" or "treatment groups will be labelled as follows". The slot
  `map` is that list: one code and label pair per arm, copied as written.

## Traps

- Choose `dm_armcd_map` only when the text gives both codes and labels. Do not invent codes
  from arm names, and do not shorten or reword the labels.
- Under the map a code that is not listed gives no planned treatment. Copy every arm, placebo
  included; do not add entries for screen failures or subjects not assigned.
- Pooled groups such as "all active" or "total" are columns (`tfl.columns.total`), not map
  rows. Wording on the treatment actually received belongs to `trt.actual.source`.
- Silent documents: use the house default and cite the house standard. Do not guess
  a map from the data.
