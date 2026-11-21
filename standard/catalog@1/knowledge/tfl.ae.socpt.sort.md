# How are system organ classes and preferred terms sorted? (`tfl.ae.socpt.sort`)

The answer fixes the order of the rows of the adverse event table by system organ class and
preferred term. The counts do not change.

## Where it is stated

- SAP: adverse event section or general conventions for tables.
- SAP table shells: a note under the adverse event table ("sorted by ...").
- Protocol: never. Often stated, but the column that drives the order is often left out.

## Words to look for

- `alphabetical`: "system organ classes and preferred terms in alphabetical order".
- `descending_frequency_total`: "by decreasing frequency in the total column", "by descending
  overall incidence", "most frequent first over all treatment groups".
- `descending_frequency_highest_dose`: "by decreasing frequency in the highest dose group",
  "sorted by incidence in the high dose arm".

## Traps

- "By decreasing frequency" with no column named does not choose between the two frequency
  alternatives; report that the column is not stated.
- Mixed rules are common and match no alternative: organ classes alphabetical with terms by
  frequency, or sorting by the frequency in one named active arm. Report the passage.
- Frequency is the number of subjects, not of events; a tie is broken alphabetically.
  Preferred terms are sorted within their system organ class in every alternative.
- A fixed, internationally agreed order of organ classes is not alphabetical order.
- Silent documents: use the house default `alphabetical` and cite the house standard.
