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
  # Statement 10: equal values have no spread, whatever the rounding of the mean.
  spread <- if (n < 2) NA_real_ else if (min(x) == max(x)) 0 else stats::sd(x)
  list(n = n, mean = mean(x), sd = spread, median = q[2], q1 = q[1], q3 = q[3], min = min(x),
       max = max(x))
}

# A table of counts without the rows and columns whose total is 0.
reduced_table <- function(table) {
  if (length(table) == 0) return(matrix(0, 0, 0))
  if (any(is.na(table)) || any(table < 0) || any(table != round(table))) {
    fail("a table holds counts")
  }
  table[rowSums(table) > 0, colSums(table) > 0, drop = FALSE]
}

# test.cmh (statements of standard/methods/test.cmh.yaml)
#
#   strata: a list of count matrices, one per stratum, the same rows (the compared
#   groups) and columns (the values of the analysis variable, increasing)
#   values: those values, for table scores
#
# The algebra is written out here, as the statements give it: the base R
# mantelhaen.test gives the general association only.
m_cmh_p <- function(strata, values = NULL, statistic = "general_association",
                    scores = "table") {
  if (!statistic %in% c("general_association", "row_mean_scores")) {
    fail("test.cmh: unknown statistic '", statistic, "'")
  }
  if (!scores %in% c("table", "rank")) fail("test.cmh: unknown scores '", scores, "'")
  if (length(strata) == 0) return(NA_real_)
  shape <- dim(strata[[1]])
  for (table in strata) {
    if (!identical(dim(table), shape)) fail("test.cmh: the tables of the strata must have the same shape")
    if (any(is.na(table)) || any(table < 0) || any(table != round(table))) fail("test.cmh: a table holds counts")
  }
  if (statistic == "row_mean_scores" && scores == "table") {
    if (is.null(values) || length(values) != shape[2] || anyNA(values) || !all(is.finite(values))) {
      fail("test.cmh: table scores need one value per column, a number")
    }
  }
  total <- Reduce(`+`, strata)
  rows <- which(rowSums(total) > 0)
  columns <- which(colSums(total) > 0)
  r <- length(rows)
  k <- length(columns)
  if (r < 2 || k < 2) return(NA_real_)
  picked <- cbind(diag(r - 1), 0)
  g_sum <- NULL
  w_sum <- NULL
  for (table in strata) {
    x <- table[rows, columns, drop = FALSE]
    n <- sum(x)
    if (n < 2) next
    p <- rowSums(x) / n
    q <- colSums(x) / n
    mean <- n * kronecker(p, q)
    cov <- n * n / (n - 1) * kronecker(diag(p, r) - outer(p, p), diag(q, k) - outer(q, q))
    if (statistic == "general_association") {
      b <- kronecker(picked, cbind(diag(k - 1), 0))
    } else {
      if (scores == "table") {
        a <- as.numeric(values[columns])
      } else {
        totals <- colSums(x)
        a <- cumsum(totals) - totals + (totals + 1) / 2
      }
      b <- kronecker(picked, matrix(a, nrow = 1))
    }
    g <- b %*% (as.numeric(t(x)) - mean)  # the counts row by row (statement 3)
    w <- b %*% cov %*% t(b)
    g_sum <- if (is.null(g_sum)) g else g_sum + g
    w_sum <- if (is.null(w_sum)) w else w_sum + w
  }
  if (is.null(g_sum)) return(NA_real_)
  # Statement 4: the rank and the Moore-Penrose inverse with one tolerance.
  s <- svd(w_sum)
  tolerance <- max(s$d) * max(dim(w_sum)) * 2^-52
  kept <- s$d > tolerance
  df <- sum(kept)
  if (df == 0) return(NA_real_)
  inverse <- s$v[, kept, drop = FALSE] %*% (t(s$u[, kept, drop = FALSE]) / s$d[kept])
  statistic_value <- as.numeric(t(g_sum) %*% inverse %*% g_sum)
  stats::pchisq(statistic_value, df, lower.tail = FALSE)
}

# test.chisq
m_chisq_p <- function(table) {
  t <- reduced_table(table)
  if (nrow(t) < 2 || ncol(t) < 2) return(NA_real_)
  suppressWarnings(stats::chisq.test(t, correct = FALSE))$p.value
}

# test.fisher.exact
#
# A 2 x 2 table goes to stats::fisher.test, which sums the probabilities that
# are not larger than the observed one by more than a relative 1e-7: the
# allowance of statement 5.
#
# A larger table is summed here. fisher.test (the network algorithm FEXACT)
# allows a wider excess for it, so it counts a table that statement 5 leaves
# out (statement 8; review of real-2, finding F3). The sum is over every table
# with the observed margins, and more than FISHER_MAX_TABLES tables are
# refused (statement 6).
FISHER_RELATIVE_EXCESS <- 1e-7
FISHER_MAX_TABLES <- 1e7

m_fisher_p <- function(table, max_tables = FISHER_MAX_TABLES) {
  t <- reduced_table(table)
  if (nrow(t) < 2 || ncol(t) < 2) return(NA_real_)
  if (nrow(t) == 2 && ncol(t) == 2) return(min(1, stats::fisher.test(t)$p.value))
  min(1, fisher_sum(t, max_tables))
}

# The sum of statement 4. The tables are walked row by row and cell by cell.
# The last cell of a row and the whole last row are what is left; the largest
# row and the largest column are put last, so that the cells that are walked
# are bounded by the smaller totals. The last free cell of the walk is taken
# for all its values at once.
fisher_sum <- function(t, max_tables) {
  t <- t[order(rowSums(t)), order(colSums(t)), drop = FALSE]
  row_totals <- rowSums(t)
  nr <- nrow(t)
  nc <- ncol(t)
  total <- sum(t)
  log_factorial <- c(0, cumsum(log(seq_len(total))))  # element k + 1 is log(k!)
  constant <- sum(log_factorial[row_totals + 1]) + sum(log_factorial[colSums(t) + 1]) -
    log_factorial[total + 1]
  limit <- constant - sum(log_factorial[t + 1]) + log1p(FISHER_RELATIVE_EXCESS)
  state <- new.env()
  state$sum <- 0
  state$tables <- 0
  # i, j: the cell to fill. left: what every column still has to take.
  # cells: the sum of log(count!) over the cells filled so far.
  walk <- function(i, j, left_in_row, left, cells) {
    # What the later columns can still take bounds this cell from below.
    lowest <- max(0, left_in_row - sum(left[(j + 1):nc]))
    highest <- min(left_in_row, left[j])
    if (lowest > highest) return(invisible(NULL))
    counts <- lowest:highest
    if (i == nr - 1 && j == nc - 1) {
      rest <- left_in_row - counts  # the last cell of this row
      last_row <- log_factorial[left[j] - counts + 1] + log_factorial[left[nc] - rest + 1]
      if (nc > 2) last_row <- last_row + sum(log_factorial[left[seq_len(nc - 2)] + 1])
      log_probability <- constant - cells - log_factorial[counts + 1] -
        log_factorial[rest + 1] - last_row
      state$tables <- state$tables + length(counts)
      if (state$tables > max_tables) {
        fail("test.fisher.exact: more than ", format(max_tables, scientific = FALSE),
             " tables to sum; the method does not approximate")
      }
      state$sum <- state$sum + sum(exp(log_probability[log_probability <= limit]))
      return(invisible(NULL))
    }
    for (count in counts) {
      after <- left
      after[j] <- left[j] - count
      if (j == nc - 1) {  # the last cell of a row is what the row has left
        rest <- left_in_row - count
        after[nc] <- left[nc] - rest
        walk(i + 1, 1, row_totals[i + 1], after,
             cells + log_factorial[count + 1] + log_factorial[rest + 1])
      } else {
        walk(i, j + 1, left_in_row - count, after, cells + log_factorial[count + 1])
      }
    }
    invisible(NULL)
  }
  walk(1, 1, row_totals[1], colSums(t), 0)
  state$sum
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
