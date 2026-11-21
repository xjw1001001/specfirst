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
  overall incidence", "most frequent first over all treatment groups", for organ classes and
  terms alike.
- `soc_alpha_pt_descending_in_column`: "organ classes alphabetically, preferred terms by
  decreasing frequency in the high dose group", "within each body system, terms by descending
  incidence in the total column". The slot `column` is the arm's label, or Total.

## Traps

- "By decreasing frequency" with no column named does not say which column drives the order;
  report that the column is not stated.
- Sorting by the risk difference (the FDA guide, section 2.2) matches no alternative of this
  version; report the passage.
- Frequency is the number of subjects, not of events; a tie is broken alphabetically.
  Preferred terms are sorted within their system organ class in every alternative.
- Alphabetical order compares the upper-cased text, then the text itself.
- A fixed, internationally agreed order of organ classes is not alphabetical order.
- Silent documents: use the house default and cite the house standard.
