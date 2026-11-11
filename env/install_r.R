# Install the R packages of env/r-packages.txt, with everything they need,
# into the project library (SPECFIRST_R_LIBS, set by scripts/env.sh) from the
# dated repository snapshot named in env/r-repo.txt. Then compare the
# library with env/r-packages.lock.
#
#   Rscript --vanilla env/install_r.R               install what the lock lists, verify
#   Rscript --vanilla env/install_r.R --write-lock  resolve from r-packages.txt, rewrite the lock
#
# The base and the recommended packages (Matrix, MASS, mgcv, ...) come with
# the R installation, whose version env/r-version.txt pins: CRAN's current
# versions of them often need an R newer than the released one. Everything
# else comes from the snapshot and is in the lock.

args <- commandArgs(trailingOnly = TRUE)
file_arg <- sub("^--file=", "", grep("^--file=", commandArgs(FALSE), value = TRUE)[1])
env_dir <- dirname(normalizePath(file_arg))

read_lines <- function(name) {
  x <- trimws(sub("#.*$", "", readLines(file.path(env_dir, name), warn = FALSE)))
  x[nzchar(x)]
}

lib <- Sys.getenv("SPECFIRST_R_LIBS")
if (!nzchar(lib)) stop("SPECFIRST_R_LIBS is not set; source scripts/env.sh first")
dir.create(lib, recursive = TRUE, showWarnings = FALSE)
# The project library and R's own library only: no user or site library.
.libPaths(lib, include.site = FALSE)

repo <- read_lines("r-repo.txt")[1]
options(
  repos = c(CRAN = repo),
  # The snapshot serves Linux binaries only to a client that names its R
  # version and platform.
  HTTPUserAgent = sprintf(
    "R/%s R (%s)", getRversion(),
    paste(getRversion(), R.version$platform, R.version$arch, R.version$os)
  ),
  Ncpus = max(1L, parallel::detectCores() - 1L),
  timeout = 900
)

in_library <- function() {
  ip <- installed.packages(lib.loc = lib)
  stats::setNames(ip[, "Version"], ip[, "Package"])
}

lock_file <- file.path(env_dir, "r-packages.lock")
write_lock <- "--write-lock" %in% args || !file.exists(lock_file)

if (write_lock) {
  wanted <- read_lines("r-packages.txt")
  db <- available.packages()
  missing <- setdiff(wanted, rownames(db))
  if (length(missing)) stop("not in the repository: ", paste(missing, collapse = ", "))
  deps <- tools::package_dependencies(
    wanted, db = db, which = c("Depends", "Imports", "LinkingTo"), recursive = TRUE
  )
  with_r <- rownames(installed.packages(lib.loc = .Library, priority = c("base", "recommended")))
  target <- sort(setdiff(unique(c(wanted, unlist(deps))), with_r), method = "radix")
  gone <- setdiff(target, rownames(db))
  if (length(gone)) {
    stop("not available for ", R.version.string, ": ", paste(gone, collapse = ", "))
  }
  versions <- stats::setNames(db[target, "Version"], target)
} else {
  rows <- strsplit(read_lines("r-packages.lock"), "[[:space:]]+")
  versions <- stats::setNames(vapply(rows, `[`, "", 2), vapply(rows, `[`, "", 1))
  target <- names(versions)
}

have <- in_library()
todo <- target[is.na(have[target]) | have[target] != versions[target]]
cat(sprintf("R packages: %d wanted, %d to install from %s\n", length(target), length(todo), repo))
if (length(todo)) install.packages(todo, lib = lib, dependencies = FALSE, quiet = TRUE)

have <- in_library()
wrong <- target[is.na(have[target]) | have[target] != versions[target]]
if (length(wrong)) {
  for (p in wrong) {
    cat(sprintf("  %s: installed %s, expected %s\n", p, have[p], versions[p]))
  }
  stop("the R library does not match ", if (write_lock) "the repository" else "env/r-packages.lock")
}

if (write_lock) {
  lines <- c(
    sprintf("# R packages of the project library, from %s", repo),
    sprintf("# Resolved with %s on %s. Written by env/install_r.R --write-lock.",
            R.version.string, R.version$platform),
    sprintf("%s %s", target, versions[target])
  )
  con <- file(lock_file, open = "wb")
  writeLines(lines, con, sep = "\n")
  close(con)
  cat(sprintf("wrote %s (%d packages)\n", lock_file, length(target)))
}
cat(sprintf("R library matches the lock: %d packages in %s\n", length(target), lib))
