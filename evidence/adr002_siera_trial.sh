#!/usr/bin/env bash
# Evidence for ADR-002: can siera 0.5.6 be the R result engine?
#
# Usage, after `. scripts/env.sh` and `specfirst build cdiscpilot01`:
#   bash evidence/adr002_siera_trial.sh build/kits/cdiscpilot01/gold/data/adam <scratch folder>
#
# It reads the fetch cache and the ADaM folder and writes only into the
# scratch folder. Recorded output: evidence/adr002_siera_trial.out.
#
#   T1  siera on CDISC's ARS example, as fetched
#   T2  siera on its own variant of that example (in the pinned repository)
#   T3  the scripts of T2 on the pilot ADaM, against the results CDISC embeds
#   T4  what cards and cardx give for the methods of the registry, and at what cost
set -u
adam="${1:?usage: adr002_siera_trial.sh <adam folder> <scratch folder>}"
work="${2:?usage: adr002_siera_trial.sh <adam folder> <scratch folder>}"
: "${SPECFIRST_CACHE:?run . scripts/env.sh first}" "${SPECFIRST_R_LIBS:?run . scripts/env.sh first}"
export PYTHONDONTWRITEBYTECODE=1
example="$SPECFIRST_CACHE/ars/workfiles/examples/ARS v1/Common Safety Displays.json"
variant="$SPECFIRST_CACHE/siera/inst/extdata/Common_Safety_Displays_cards.json"
rm -rf "$work"
mkdir -p "$work/adam" "$work/cdisc" "$work/cards" "$work/run"

python - "$adam" "$work/adam" <<'PY'
import sys
import pyarrow.csv as pc
import pyarrow.parquet as pq
for name in ("adsl", "adae", "advs"):
    pc.write_csv(pq.read_table(f"{sys.argv[1]}/{name}.parquet"), f"{sys.argv[2]}/{name.upper()}.csv")
PY

cat > "$work/generate.R" <<'RS'
.libPaths(Sys.getenv("SPECFIRST_R_LIBS"), include.site = FALSE)
args <- commandArgs(trailingOnly = TRUE)
messages <- character(0)
tryCatch(
  withCallingHandlers(
    siera::readARS(args[1], args[2], args[3]),
    warning = function(w) {
      messages <<- c(messages, gsub("\\s+", " ", conditionMessage(w)))
      invokeRestart("muffleWarning")
    }),
  error = function(e) cat("ERROR:", conditionMessage(e), "\n"))
skipped <- grep("does not have any AnalysisMethodCode", messages, value = TRUE)
unknown <- grep("references unknown valueSource", messages, value = TRUE)
analysis <- function(x, pattern) unique(sub(pattern, "\\1", x))
cat("scripts written:", length(list.files(args[2], pattern = "[.]R$")), "\n")
cat("warnings:", length(messages), "\n")
cat("analyses whose method has no code for siera (no code is generated for them):",
    length(analysis(skipped, ".*linked to Analysis \"([^\"]+)\".*")), "\n")
cat("analyses whose code template names a value source siera does not know:",
    length(analysis(unknown, ".*for Analysis ([^:]+):.*")), "\n")
cat("other warnings:", length(messages) - length(skipped) - length(unknown), "\n")
RS

echo "packages: $(Rscript --vanilla -e '.libPaths(Sys.getenv("SPECFIRST_R_LIBS"), include.site = FALSE); cat("siera", as.character(packageVersion("siera")), "cards", as.character(packageVersion("cards")), "cardx", as.character(packageVersion("cardx")))')"
echo
echo "== T1 siera::readARS on CDISC's example (31 analyses)"
Rscript --vanilla "$work/generate.R" "$example" "$work/cdisc" "$work/adam" 2>&1 | grep -v '^$'
echo "lines that compute something in the generated scripts (cards::, cardx::, stats::): $(cat "$work"/cdisc/*.R | grep -c -E 'cards::|cardx::|stats::')"
echo "the generated script carries a time stamp: $(grep -c 'Date created' "$work/cdisc/ARD_Out14-1-1.R") line"

echo
echo "== T2 siera::readARS on siera's own variant of the example"
python - "$example" "$variant" <<'PY'
import json, sys
ours, theirs = (json.load(open(path, encoding="utf-8")) for path in sys.argv[1:3])
a, b = ({x["id"]: x for x in event["analyses"]} for event in (ours, theirs))
print("analyses:", len(b), "of the", len(a), "of CDISC's example; left out:", len(set(a) - set(b)))
print("   left out:", ", ".join(sorted(set(a) - set(b))))
print("analyses given another method:", sum(1 for k in set(a) & set(b) if a[k]["methodId"] != b[k]["methodId"]))
print("methods with R code in the file:", sum(1 for m in theirs["methods"] if (m.get("codeTemplate") or {}).get("code")),
      "of", len(theirs["methods"]), "; a Fisher test with a p-value among them:",
      any("fisher" in m["name"].lower() for m in theirs["methods"]))
print("results embedded in the variant:", sum(len(x.get("results", [])) for x in theirs["analyses"]))
PY
Rscript --vanilla "$work/generate.R" "$variant" "$work/cards" "$work/adam" 2>&1 | grep -v '^$'
echo "packages the generated scripts attach: $(grep -h -o 'library([a-z.A-Z]*)' "$work"/cards/*.R | sort -u | tr '\n' ' ')"
echo "of these, not among the locked R packages: $(for p in $(grep -h -o 'library([a-z.A-Z]*)' "$work"/cards/*.R | sort -u | sed 's/library(\(.*\))/\1/'); do grep -q "^$p " env/r-packages.lock 2>/dev/null || [ -d "/usr/lib/R/library/$p" ] || printf '%s ' "$p"; done)"

echo
echo "== T3 the scripts of T2 on the pilot ADaM"
cat > "$work/run.R" <<'RS'
.libPaths(Sys.getenv("SPECFIRST_R_LIBS"), include.site = FALSE)
args <- commandArgs(trailingOnly = TRUE)
env <- new.env()
ok <- tryCatch({ suppressMessages(sys.source(args[1], envir = env)); TRUE },
               error = function(e) { cat("  ERROR:", gsub("\\s+", " ", conditionMessage(e)), "\n"); FALSE })
if (ok && exists("ARD", envir = env)) {
  ard <- get("ARD", envir = env)
  cat("  ARD rows:", nrow(ard), "\n")
  flat <- function(x) vapply(x, function(v) if (is.null(v) || length(v) == 0 || is.function(v)) NA_character_ else
    if (is.numeric(v)) sprintf("%.17g", v[[1]]) else as.character(v[[1]]), character(1))
  ard <- ard[, setdiff(names(ard), c("fmt_fun", "warning", "error")), drop = FALSE]
  out <- as.data.frame(lapply(ard, function(col) if (is.list(col)) flat(col) else as.character(col)),
                       stringsAsFactors = FALSE)
  write.csv(out, args[2], row.names = FALSE, na = "")
}
RS
echo "(for this trial only, the scripts are changed to read the CSV files with base R and not to"
echo " attach readr and parameters, which are not installed; nothing else is changed)"
for script in "$work"/cards/*.R; do
  name=$(basename "$script" .R)
  sed -e '/library(readr)/d' -e '/library(parameters)/d' \
      -e "s/readr::read_csv(\('[^']*'\),/utils::read.csv(\1, stringsAsFactors = FALSE, na.strings = '', check.names = FALSE,/" \
      -e '/show_col_types = FALSE,/d' -e 's/progress = FALSE) |>/strip.white = FALSE) |>/' \
      "$script" > "$work/run/$name.R"
  echo "$name:"
  Rscript --vanilla "$work/run.R" "$work/run/$name.R" "$work/run/$name.csv" 2>&1 | grep -E '^  (ERROR|ARD rows)'
done
python - "$work/run" "$example" <<'PY'
import csv, json, sys
from collections import Counter
from pathlib import Path
run, event = Path(sys.argv[1]), json.load(open(sys.argv[2], encoding="utf-8"))
got = {}
for path in sorted(run.glob("*.csv")):
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            groups = frozenset((row[f"group{n}_groupingId"], row.get(f"group{n}_groupId") or row.get(f"group{n}_groupValue") or None)
                               for n in (1, 2, 3) if row.get(f"group{n}_groupingId"))
            if row.get("operationid"):
                got[(row["AnalysisId"], row["operationid"], groups)] = row["stat"]
def close(raw, value):
    try:
        r, v = float(raw), float(value)
    except (TypeError, ValueError):
        return False
    decimals = len(raw.split(".")[1]) if "." in raw else 0
    return abs(r - v) <= 0.5 * 10 ** (-decimals) + 1e-9
total, percent = Counter(), Counter()
for analysis in event["analyses"]:
    for result in analysis.get("results", []):
        key = (analysis["id"], result["operationId"], frozenset(
            (g["groupingId"], g.get("groupId") or g.get("groupValue")) for g in result.get("resultGroups", [])))
        state = "not computed" if key not in got else "equal" if close(result["rawValue"], got[key]) else "other value"
        total[state] += 1
        if state == "other value" and result["operationId"].endswith("_pct"):
            percent[close(result["rawValue"], 100 * float(got[key]))] += 1
print("the", sum(total.values()), "results CDISC embeds:", dict(sorted(total.items())))
print("other values that are a percent, and equal after multiplying ours by 100:", percent[True], "of", sum(percent.values()))
PY

echo
echo "== T4 cards and cardx for the methods of the registry"
cat > "$work/cardx.R" <<'RS'
.libPaths(Sys.getenv("SPECFIRST_R_LIBS"), include.site = FALSE)
set.seed(1)
d <- data.frame(arm = rep(c("A", "B", "C"), each = 30), y = rnorm(90),
                x = sample(c("no", "yes"), 90, replace = TRUE))
try_it <- function(name, expr) {
  out <- tryCatch({ force(expr); "runs" }, error = function(e) paste("fails:", gsub("\\s+", " ", conditionMessage(e))))
  cat(sprintf("%-34s %s\n", name, out))
}
try_it("cardx::ard_stats_aov", cardx::ard_stats_aov(y ~ arm, data = d))
try_it("cardx::ard_stats_oneway_test", cardx::ard_stats_oneway_test(y ~ arm, data = d, var.equal = TRUE))
try_it("cardx::ard_stats_chisq_test", cardx::ard_stats_chisq_test(d, by = "arm", variables = "x"))
try_it("cardx::ard_stats_fisher_test", cardx::ard_stats_fisher_test(d, by = "arm", variables = "x"))
s <- cards::ard_summary(d, variables = "y")
q <- unlist(s$stat[s$stat_name %in% c("p25", "p75")])
cat("cards::ard_summary quartiles equal quantile type 2 (the SAS default):",
    isTRUE(all.equal(unname(q), unname(quantile(d$y, c(.25, .75), type = 2)))),
    "; type 7 (the R default):", isTRUE(all.equal(unname(q), unname(quantile(d$y, c(.25, .75), type = 7)))), "\n")
t <- cards::ard_tabulate(d, variables = "x")
cat("cards::ard_tabulate gives p as a proportion, not a percent:", all(unlist(t$stat[t$stat_name == "p"]) <= 1), "\n")
two <- d[d$arm != "C", ]
n <- 200
t_cardx <- system.time(for (i in seq_len(n)) cardx::ard_stats_fisher_test(two, by = "arm", variables = "x"))[["elapsed"]]
t_stats <- system.time(for (i in seq_len(n)) stats::fisher.test(two$x, two$arm)$p.value)[["elapsed"]]
cat(sprintf("%d Fisher tests: cardx %.1f s, stats::fisher.test %.2f s\n", n, t_cardx, t_stats))
RS
Rscript --vanilla "$work/cardx.R" 2>&1 | grep -v '^$'
