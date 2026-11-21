# Is there a display threshold for preferred terms? (`tfl.ae.socpt.threshold`)

The answer decides whether rare preferred terms are left out of the adverse event table by
system organ class and preferred term.

## Where it is stated

- SAP: adverse event section, where the tables are described ("common adverse events").
- SAP table shells: the title of the table ("... in at least 5% of subjects in any group").
- Protocol: never. The main table usually has no threshold.

## Words to look for

- `none`: "all treatment-emergent adverse events are summarized by system organ class and
  preferred term", no cut-off in the title.
- `min_percent_any_arm`: "preferred terms reported by at least 5% of subjects in any
  treatment group", "events occurring in 5% or more of subjects in either arm". The slot
  `percent` is the stated percentage.

## Traps

- "At least 5%" includes 5. "More than 5%" does not, and matches no alternative as written;
  report the passage if the limit is exclusive.
- The test is per arm, on the percentage at full precision: a term at 4.96% is below 5 even
  though it displays as 5.0. A threshold on the total column is another rule.
- Many SAPs plan a full table and a separate table of common events. This entry is about the
  main table of the family; a threshold that belongs only to an extra table does not apply.
- A system organ class is shown when one of its terms is shown, and its own row still counts
  every subject with an event in the class.
- Silent documents: use the house default and cite the house standard.
