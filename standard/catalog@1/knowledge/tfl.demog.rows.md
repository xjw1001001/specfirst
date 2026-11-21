# Which characteristics does the demographics table show, in which order? (`tfl.demog.rows`)

The list fixes the rows of the demographics table and their order. A characteristic left
out of the list is not shown.

## Where it is stated

- SAP: section on demographics and baseline characteristics, usually a sentence or a bullet
  list of the characteristics summarized.
- SAP table shells: the row labels of the demographics table, top to bottom.
- Protocol: statistical section, in general words ("age, sex, race and other
  characteristics").

## Words to look for

- `stated_list`: "the following will be summarized: age, sex, race, ...". The slot `rows`
  names each characteristic by its variable, in the stated order: age in years is AGE, age
  group AGEGR1, sex SEX, race RACEGR1, ethnicity ETHNIC, baseline height HEIGHTBL, baseline
  weight WEIGHTBL, baseline body mass index BMIBL.

## Traps

- Age and age group are two rows. "Age (years)" with descriptive statistics is AGE; "age
  category" or "<65, >=65" is AGEGR1. Include each only if the text has it.
- Race is the row RACEGR1 whether or not small categories are pooled (`demo.race.pooling`).
- Only the eight characteristics above can be rows. Others (country, disease history,
  baseline scores) cannot be expressed; report them with the answer, do not drop them
  silently.
- Take the order from the shell if there is one, otherwise from the order of the sentence.
- Silent documents, or only "demographics will be summarized": do not guess a list.
  This entry has no house default; a person must be asked.
