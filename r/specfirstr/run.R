#!/usr/bin/env Rscript
# The R result engine, from the command line.
#
#   Rscript --vanilla r/specfirstr/run.R <job.json>        run a job (the build writes it)
#   Rscript --vanilla r/specfirstr/run.R --vectors <in.json> <out.json>
#                                                          run the method vectors
#
# The code is sourced from this folder. It is not installed as a package:
# `specfirst doctor` counts any package outside env/r-packages.lock as drift.
# Only base R and jsonlite are used, and emmeans and car for the model-based methods
# (models.R, ADR-015), from the locked library alone (lesson 6).

lib <- Sys.getenv("SPECFIRST_R_LIBS")
if (!nzchar(lib)) stop("SPECFIRST_R_LIBS is not set; run `. scripts/env.sh` first", call. = FALSE)
.libPaths(lib, include.site = FALSE)
# Text is compared and sorted by code point, as the Python engine does.
invisible(Sys.setlocale("LC_COLLATE", "C"))
options(warn = 1, scipen = 0, digits = 15)

script <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
here <- dirname(normalizePath(script))
for (name in c("util.R", "methods.R", "models.R", "engine.R", "vectors.R")) {
  sys.source(file.path(here, "R", name), envir = globalenv())
}

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 3 && args[1] == "--vectors") {
  run_vectors(args[2], args[3])
} else if (length(args) == 1) {
  run_job(args[1])
} else {
  stop("usage: run.R <job.json> | run.R --vectors <in.json> <out.json>", call. = FALSE)
}
