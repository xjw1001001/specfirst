# Are race categories regrouped? (`demo.race.pooling`)

The answer decides whether the race rows of the demographics table show every collected
category or regroup them by a stated map (RACEGR1).

## Where it is stated

- SAP: section on demographics and baseline characteristics; footnotes of the table shell.
- Protocol: almost never.
- Usually unstated; a regrouping is the exception.

## Words to look for

- `not_pooled`: "race will be summarized as collected", "all race categories are presented",
  a shell that lists every category of the case report form.
- `fixed_groups`: "race will be grouped as White and Non-white", "categories: White, Black,
  Other", a shell with fewer race rows than the case report form has values. The slot `map`
  lists each named value with its group, and `other` is the group of every other value.

## Traps

- Pooling below a count ("categories with fewer than 5 subjects will be combined") matches no
  alternative of this version (catalog@1 had one without a public source, removed in
  catalog@2). Report the passage.
- A regrouping that gives no group for the values it does not name leaves `other` open:
  report that it is missing instead of choosing one.
- The map names the collected values of RACE as SDTM writes them (WHITE, BLACK OR AFRICAN
  AMERICAN), not the labels of a table.
- Pooling by a percentage matches no alternative. Report the passage.
- Silent documents: use the house default and cite the house standard.
