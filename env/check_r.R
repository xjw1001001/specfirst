# Rscript --vanilla env/check_r.R <package>...  load each package and print its version
# Rscript --vanilla env/check_r.R --list        print the project library as name<TAB>version
#
# Exit status 1 when a package does not load. Used by `specfirst doctor` and
# by the gates.

args <- commandArgs(trailingOnly = TRUE)
lib <- Sys.getenv("SPECFIRST_R_LIBS")
if (!nzchar(lib) || !dir.exists(lib)) {
  cat("no project library: SPECFIRST_R_LIBS is not set or is not a folder;",
      "source scripts/env.sh and run make install\n")
  quit(status = 1)
}
# The project library and R's own library only: no user or site library.
.libPaths(lib, include.site = FALSE)

if (identical(args, "--list")) {
  ip <- installed.packages(lib.loc = lib)
  o <- order(ip[, "Package"], method = "radix")
  cat(sprintf("%s\t%s\n", ip[o, "Package"], ip[o, "Version"]), sep = "")
  quit(status = 0)
}

cat(R.version.string, "\n", sep = "")
cat("library paths: ", paste(.libPaths(), collapse = " : "), "\n", sep = "")
failed <- character()
for (p in args) {
  ok <- tryCatch(
    {
      suppressPackageStartupMessages(library(p, character.only = TRUE))
      TRUE
    },
    error = function(e) {
      cat("  ", conditionMessage(e), "\n", sep = "")
      FALSE
    }
  )
  cat(sprintf("%-10s %s\n", p, if (ok) as.character(packageVersion(p)) else "FAILED TO LOAD"))
  if (!ok) failed <- c(failed, p)
}
if (!length(args) || length(failed)) {
  cat(sprintf("R loads %d of %d packages\n", length(args) - length(failed), length(args)))
  quit(status = 1)
}
cat(sprintf("R loads %d of %d packages\n", length(args), length(args)))
