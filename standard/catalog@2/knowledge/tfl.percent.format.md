# How are percentages displayed? (`tfl.percent.format`)

The answer decides how many decimals a percentage has, and what a cell with a count of
zero shows: the count alone, or the count with its percentage. It is given once per table
family.

## Where it is stated

- SAP: general conventions for tables and the notes to the table shells.
- Protocol: never.
- Often unstated, or visible only in the layout of a shell.

## Words to look for

- The decimals: "percentages are shown to one decimal place", "rounded to the nearest whole
  percent" (0 decimals), "xx.x" or "xx" in the shells.
- `one_decimal_zero_blank`: "no percentage is shown for a count of zero", shell cells
  written "0" where others are "xx (xx.x)".
- `one_decimal_always`: zero cells written "0 (0.0)", or "a percentage is always
  displayed".

## Traps

- The IDs of the alternatives say "one decimal" for historical reasons (catalog@1); from
  catalog@2 the decimals are the slot `decimals`, 0 to 2.
- "One decimal place" alone does not say what happens at zero. Use the house default for
  the zero, take the decimals from the document, and say that only the decimals were
  stated.
- One document may use whole numbers in one table and one decimal in another (the pilot:
  Table 14-2.01 and Table 14-5.01): the decision is per table family.
- Special displays such as "(<1%)" for a small percentage that rounds to 0, or "100" without
  a decimal, are not covered; report them.
- A shell is a layout sketch: "xx (xx.x)" in every cell does not prove that a zero count gets
  a percentage.
- Silent documents: use the house default and cite the house standard.
