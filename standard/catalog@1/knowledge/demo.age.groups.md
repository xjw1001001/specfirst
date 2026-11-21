# Which age groups are used? (`demo.age.groups`)

The answer fixes the age group of each subject, hence the rows of the age group block of the
demographics table and any analysis by age group.

## Where it is stated

- SAP: section on demographics and baseline characteristics; section on subgroups.
- SAP table shells: the row labels under "Age group".
- Protocol: rarely, unless age is a stratification factor or a planned subgroup.

## Words to look for

- `lt65_65to80_gt80`: three groups "<65, 65-80, >80", "below 65, 65 to 80, above 80 years".
- `lt65_ge65`: two groups "<65 and >=65", "under 65 versus 65 and older", "elderly (65 years
  and above) versus younger subjects".
- `stated_cuts`: any other grouping, for example "<18, 18 to <65, >=65" or "<40, >=40". The
  slot `cuts` lists, in ascending order, the ages at which a group starts (18 and 65 in the
  first example, 40 in the second).

## Traps

- Read the limits exactly. In `lt65_65to80_gt80` an age of exactly 80 is in 65-80. Under
  `stated_cuts` an age equal to a cut is in the group that starts there.
- "65 to <80, >=80" or "65-79, >=80" is not the three-group alternative; it is `stated_cuts`
  with 65 and 80.
- There is always one more group below the first cut. In a study of adults, groups written
  "18-64, 65-74, >=75" are the cuts 65 and 75; do not add the lowest eligible age as a cut.
- Age groups used to stratify the randomization need not be the groups of the table.
- Silent documents: use the house default `lt65_65to80_gt80` and cite the house standard.
