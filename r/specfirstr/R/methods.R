# The R implementations of the method registry (PLAN.md section 7.3).
#
# One function per registry entry of standard/methods/, following its numbered
# semantics. The arithmetic comes from R's own stats package: quantile types 2
# and 7, chisq.test, fisher.test, and the F test of anova(lm()). The Python
# implementations in src/specfirst/machine/methods.py are written from the
# definitions, so that the two engines do not share an implementation (rule
# R11). Both are tested on the vectors in tests/methods/.
#
# A missing result is NA.

present <- function(values) {
  if (is.character(values)) values[!is.na(values) & values != ""] else values[!is.na(values)]
}

# count.subjects
m_count_subjects <- function(values) {
  length(unique(present(values)))
}

# percent.subjects
m_percent <- function(numerator, denominator) {
  if (is.na(numerator) || is.na(denominator) || denominator == 0) return(NA_real_)
  100 * numerator / denominator
}

# summary.continuous
QUANTILE_TYPES <- c(sas5 = 2L, r7 = 7L)

m_summary_continuous <- function(values, quantile_definition = "sas5",
                                 sd_denominator = "n_minus_1") {
  if (!quantile_definition %in% names(QUANTILE_TYPES)) {
    fail("unknown quantile definition '", quantile_definition, "'")
  }
  if (sd_denominator != "n_minus_1") fail("unknown sd denominator '", sd_denominator, "'")
  x <- as.numeric(present(values))
  n <- length(x)
  if (n == 0) {
    return(list(n = 0L, mean = NA_real_, sd = NA_real_, median = NA_real_, q1 = NA_real_,
                q3 = NA_real_, min = NA_real_, max = NA_real_))
  }
  q <- stats::quantile(x, c(0.25, 0.5, 0.75), type = QUANTILE_TYPES[[quantile_definition]],
                       names = FALSE)
  list(n = n, mean = mean(x), sd = if (n > 1) stats::sd(x) else NA_real_, median = q[2],
       q1 = q[1], q3 = q[3], min = min(x), max = max(x))
}

# A table of counts without the rows and columns whose total is 0.
reduced_table <- function(table) {
  if (length(table) == 0) return(matrix(0, 0, 0))
  if (any(is.na(table)) || any(table < 0) || any(table != round(table))) {
    fail("a table holds counts")
  }
  table[rowSums(table) > 0, colSums(table) > 0, drop = FALSE]
}

# test.chisq
m_chisq_p <- function(table) {
  t <- reduced_table(table)
  if (nrow(t) < 2 || ncol(t) < 2) return(NA_real_)
  suppressWarnings(stats::chisq.test(t, correct = FALSE))$p.value
}

# test.fisher.exact. fisher.test sums over every table (the network algorithm
# FEXACT for more than 2 x 2). It fails when its workspace is too small; a
# larger one is tried once, and after that the error stands: no simulation.
m_fisher_p <- function(table) {
  t <- reduced_table(table)
  if (nrow(t) < 2 || ncol(t) < 2) return(NA_real_)
  p <- tryCatch(stats::fisher.test(t)$p.value, error = function(e) NULL)
  if (is.null(p)) {
    p <- tryCatch(stats::fisher.test(t, workspace = 2e7)$p.value, error = function(e) {
      fail("test.fisher.exact: fisher.test could not sum this table (", conditionMessage(e),
           "); the method does not approximate")
    })
  }
  min(1, p)
}

# test.anova.oneway
m_anova_oneway_p <- function(groups) {
  groups <- lapply(groups, function(g) as.numeric(present(g)))
  groups <- groups[lengths(groups) > 0]
  k <- length(groups)
  n <- sum(lengths(groups))
  if (k < 2 || n - k < 1) return(NA_real_)
  if (all(vapply(groups, function(g) min(g) == max(g), TRUE))) {  # statement 5: SSW is 0
    firsts <- vapply(groups, function(g) g[1], 0)
    return(if (length(unique(firsts)) > 1) 0 else NA_real_)
  }
  y <- unlist(groups)
  g <- factor(rep(seq_len(k), lengths(groups)))
  stats::anova(stats::lm(y ~ g))[["Pr(>F)"]][1]
}
