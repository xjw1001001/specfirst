#!/usr/bin/env bash
# Evidence for ADR-003: what the rounding of tfrmt would do to the results of
# the pilot.
#
# Usage, after `. scripts/env.sh` and a build of the kit:
#   bash evidence/adr003_rounding.sh <build folder> <scratch folder>
#
# tfrmt shows a number through R's own `format(round(x, digits), nsmall =
# digits)` (R/apply_frmt_methods.R at commit 8feb95a of
# GSK-Biostatistics/tfrmt, read on 2026-11-17) and has no option for the
# rounding rule. tfrmt itself is not installed: it is not among the locked R
# packages. This script runs that one expression of base R on every result of
# the pilot that the ARS example shows with decimals, and compares the text
# with the registry's display.round.half_away_from_zero and with the
# formatted value the example embeds. It reads the build and writes only into
# the scratch folder. Recorded output: evidence/adr003_rounding.out.
set -u
build="${1:?usage: adr003_rounding.sh <build folder> <scratch folder>}"
work="${2:?usage: adr003_rounding.sh <build folder> <scratch folder>}"
: "${SPECFIRST_R_LIBS:?run . scripts/env.sh first}"
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$work"

python - "$build" "$work/values.json" <<'PY'
import json
import sys

from specfirst.machine import ars, results
from specfirst.machine.canonical import read_jsonl

build = sys.argv[1]
event = ars.index(ars.read(f"{build}/gold/spec/ars/common-safety-displays.json"))
rows = read_jsonl(f"{build}/gold/ard/common-safety-displays.jsonl")
values = []
for row in rows:
    pattern = event.operations[row["operation_id"]][1].get("resultPattern")
    decimals = results.pattern_decimals(pattern)
    if decimals and row["raw_value"] is not None:
        values.append({"id": row["id"], "value": row["raw_value"], "decimals": decimals})
with open(sys.argv[2], "w", encoding="ascii") as handle:
    json.dump(values, handle)
print(f"results of the pilot with a value and a pattern with decimals: {len(values)} of {len(rows)}")
PY

Rscript --vanilla -e '
.libPaths(Sys.getenv("SPECFIRST_R_LIBS"), include.site = FALSE)
args <- commandArgs(trailingOnly = TRUE)
values <- jsonlite::fromJSON(args[1], simplifyVector = FALSE)
texts <- vapply(values, function(v) {
  trimws(format(round(as.numeric(v$value), v$decimals), decimal.mark = ".", nsmall = v$decimals))
}, "")
writeLines(jsonlite::toJSON(texts), args[2])
cat("R", paste(R.version$major, R.version$minor, sep = "."),
    ": format(round(x, digits), nsmall = digits) on", length(texts), "values\n")
' "$work/values.json" "$work/r.json"

python - "$build" "$work/values.json" "$work/r.json" <<'PY'
import json
import sys
from decimal import Decimal

from specfirst.machine import ars, methods, results

build = sys.argv[1]
values = json.load(open(sys.argv[2], encoding="ascii"))
in_r = json.load(open(sys.argv[3], encoding="ascii"))
event = ars.index(ars.read(f"{build}/gold/spec/ars/common-safety-displays.json"))
embedded = results.embedded(event)
differ, exponent, on_a_half, with_reference, reference_ours, reference_r = [], 0, 0, 0, 0, 0
for item, theirs in zip(values, in_r, strict=True):
    ours = methods.round_half_away(item["value"], item["decimals"])
    scaled = Decimal(repr(item["value"])) * 10 ** item["decimals"]
    on_a_half += scaled % 1 == Decimal("0.5")
    if ours == theirs:
        continue
    if "e" in theirs:
        # format() of one small value writes an exponent (9e-04). tfrmt formats the
        # values of a column at once, so this says nothing about tfrmt.
        exponent += 1
        continue
    formatted = embedded[item["id"]].formatted if item["id"] in embedded else None
    differ.append((item["id"], item["value"], ours, theirs, formatted))
    if formatted is not None:
        with_reference += 1
        reference_ours += formatted.strip("() ").replace(" ", "") == ours
        reference_r += formatted.strip("() ").replace(" ", "") == theirs
print(f"values that lie exactly on a half at their displayed decimals: {on_a_half}")
print(f"values that R's round shows as another number than half away from zero: {len(differ)}")
print(f"  of them the example formats: {with_reference}; its text is ours for {reference_ours}, "
      f"R's for {reference_r}")
for key, value, ours, theirs, formatted in differ:
    print(f"  {key}: value {value!r}: half away {ours}, R {theirs}, the example {formatted!r}")
print(f"not counted: {exponent} small values that format() writes with an exponent when it is "
      "given one value at a time")
PY
