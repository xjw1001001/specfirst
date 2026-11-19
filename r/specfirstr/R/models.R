# The model-based methods of the method registry (PLAN.md section 7.3): R only.
#
#   model.ancova.lsmeans         least-squares means by treatment group
#   model.ancova.pairwise        each group against a reference group
#   model.ancova.dose_response   the test of a dose-response trend
#
# One function per registry entry, following its numbered semantics
# (standard/methods/model.ancova.*.yaml). The fit is stats::lm; the LS means,
# their differences and their confidence limits come from emmeans; the F test
# of the dose term of the continuous model from car::Anova with Type III sums
# of squares, as the analysis results metadata of the pilot ask of SAS PROC GLM.
# All three packages are in the lock (env/r-packages.lock, env/system.lock).
#
# The expected values of the vectors are not computed here: tests/methods/oracle.py
# computes them again with exact fractions and the closed form of the t
# distribution (ADR-015).
#
# A missing result is NA. A group is named by its ID; `groups` lists the IDs of
# the treatment grouping in its order.

MODEL_METHODS <- c("model.ancova.lsmeans", "model.ancova.pairwise",
                   "model.ancova.dose_response")

# Statements 1 and 2 of model.ancova.lsmeans: the model records and the terms.
#   y: the analysis variable, numbers with NA
#   group: the group ID of every record, NA or "" for none
#   factors: named list of text columns ("" or NA is missing)
#   covariates: named list of number columns
model_frame <- function(y, group, groups, factors, covariates) {
  if (length(intersect(names(factors), names(covariates))) > 0) {
    fail("a column is both a factor and a covariate of the model")
  }
  keep <- !is.na(y) & !is.na(group) & group != ""
  for (values in factors) keep <- keep & !is.na(values) & values != ""
  for (values in covariates) keep <- keep & !is.na(values)
  frame <- data.frame(.y = as.numeric(y[keep]))
  frame$.g <- factor(group[keep], levels = groups)
  terms <- character(0)
  k <- 0
  for (name in names(factors)) {
    k <- k + 1
    values <- as.character(factors[[name]][keep])
    levels <- sort(unique(values), method = "radix")
    if (length(levels) < 2) next  # a factor with one level is left out
    column <- paste0(".f", k)
    frame[[column]] <- factor(values, levels = levels)
    terms <- c(terms, column)
  }
  k <- 0
  for (name in names(covariates)) {
    k <- k + 1
    column <- paste0(".c", k)
    frame[[column]] <- as.numeric(covariates[[name]][keep])
    terms <- c(terms, column)
  }
  list(frame = frame, keep = keep, terms = terms)
}

model_fit <- function(frame, lead, terms) {
  rhs <- paste(c(lead, terms), collapse = " + ")
  stats::lm(stats::as.formula(paste(".y ~", rhs)), data = frame)
}

# The rows of an emmeans summary by their first column, with the limits under
# one name whatever the degrees of freedom.
emm_table <- function(object, level, tests) {
  s <- as.data.frame(summary(object, infer = c(TRUE, tests), level = level / 100))
  names(s)[names(s) %in% c("lower.CL", "asymp.LCL")] <- "lower"
  names(s)[names(s) %in% c("upper.CL", "asymp.UCL")] <- "upper"
  rownames(s) <- as.character(s[[1]])
  s
}

model_emmeans <- function(fit, frame, weights, df) {
  emm <- emmeans::emmeans(fit, specs = ".g", weights = weights, data = frame)
  if (df == "asymptotic") emm <- update(emm, df = Inf)
  emm
}

# Statement 8 of model.ancova.lsmeans: no residual degrees of freedom, no results.
model_usable <- function(m) {
  nrow(m$frame) > 0 && length(unique(as.character(m$frame$.g))) >= 1
}

na_by_group <- function(ids, operations) {
  out <- list()
  for (id in ids) out[[id]] <- stats::setNames(as.list(rep(NA_real_, length(operations))),
                                               operations)
  out
}

value_of <- function(table, row, column) {
  if (!row %in% rownames(table)) return(NA_real_)
  value <- table[row, column]
  if (is.null(value) || length(value) != 1 || !is.finite(value)) NA_real_ else unname(value)
}

# model.ancova.lsmeans: one result per group, list(id = list(lsmean, se, lower_cl, upper_cl)).
m_ancova_lsmeans <- function(y, group, groups, factors = list(), covariates = list(),
                             weights = "equal", df = "residual", confidence_level = 95) {
  operations <- c("lsmean", "se", "lower_cl", "upper_cl")
  out <- na_by_group(groups, operations)
  m <- model_frame(y, group, groups, factors, covariates)
  if (!model_usable(m)) return(out)
  fit <- model_fit(m$frame, ".g", m$terms)
  if (fit$df.residual < 1) return(out)
  table <- emm_table(model_emmeans(fit, m$frame, weights, df), confidence_level, FALSE)
  for (id in groups) {
    out[[id]] <- list(lsmean = value_of(table, id, "emmean"), se = value_of(table, id, "SE"),
                      lower_cl = value_of(table, id, "lower"),
                      upper_cl = value_of(table, id, "upper"))
  }
  out
}

# model.ancova.pairwise: one result per group but the reference, the group minus the reference.
m_ancova_pairwise <- function(y, group, groups, reference, factors = list(),
                              covariates = list(), df = "residual", confidence_level = 95) {
  if (!reference %in% groups) fail("the reference group ", reference, " is not a group")
  operations <- c("estimate", "se", "lower_cl", "upper_cl", "p_value")
  others <- setdiff(groups, reference)
  out <- na_by_group(others, operations)
  m <- model_frame(y, group, groups, factors, covariates)
  if (!model_usable(m) || !reference %in% as.character(m$frame$.g)) return(out)
  fit <- model_fit(m$frame, ".g", m$terms)
  if (fit$df.residual < 1) return(out)
  # Statement 3: the difference does not depend on the weights of the LS means.
  emm <- model_emmeans(fit, m$frame, "equal", df)
  present <- as.character(as.data.frame(summary(emm))[[1]])
  if (length(present) < 2 || !reference %in% present) return(out)
  contrasts <- emmeans::contrast(emm, method = "trt.vs.ctrl", ref = match(reference, present),
                                 adjust = "none")
  table <- emm_table(contrasts, confidence_level, TRUE)
  for (id in others) {
    row <- paste(id, "-", reference)
    out[[id]] <- list(estimate = value_of(table, row, "estimate"),
                      se = value_of(table, row, "SE"),
                      lower_cl = value_of(table, row, "lower"),
                      upper_cl = value_of(table, row, "upper"),
                      p_value = value_of(table, row, "p.value"))
  }
  out
}

# model.ancova.dose_response: list(p_value, estimate).
#   dose_values: the value of the grouping variable on every record (statement 2,
#   grouping_value); NULL when the option is group_rank.
m_ancova_dose_response <- function(y, group, groups, dose_values = NULL, factors = list(),
                                   covariates = list(), dose = "grouping_value",
                                   model = "continuous_dose", df = "residual") {
  out <- list(p_value = NA_real_, estimate = NA_real_)
  m <- model_frame(y, group, groups, factors, covariates)
  if (!model_usable(m)) return(out)
  levels_present <- groups[groups %in% as.character(m$frame$.g)]
  if (length(levels_present) < 2) return(out)
  # Statement 2: the dose of a record.
  if (dose == "grouping_value") {
    if (is.null(dose_values)) fail("model.ancova.dose_response: the doses are not given")
    doses <- as.numeric(dose_values[m$keep])
    if (anyNA(doses)) fail("model.ancova.dose_response: a record has no dose")
    by_group <- tapply(doses, as.character(m$frame$.g), function(d) unique(d))
    if (any(lengths(by_group) != 1)) {
      fail("model.ancova.dose_response: the dose is not the same on every record of a group")
    }
    group_dose <- unlist(by_group)[levels_present]
  } else if (dose == "group_rank") {
    group_dose <- stats::setNames(as.numeric(match(levels_present, groups)), levels_present)
    doses <- unname(group_dose[as.character(m$frame$.g)])
  } else {
    fail("unknown dose '", dose, "'")
  }
  if (length(unique(group_dose)) < 2) return(out)
  if (model == "continuous_dose") {
    frame <- m$frame
    frame$.d <- doses
    fit <- model_fit(frame, ".d", m$terms)
    if (fit$df.residual < 1 || is.na(stats::coef(fit)[[".d"]])) return(out)
    aliased <- anyNA(stats::coef(fit))
    if (aliased) {
      # Statement 6: b is estimable only when the dose is not a combination of the
      # other columns of the design; lm keeps the first of two aliased columns.
      without <- model_fit(frame, "1", m$terms)
      if (fit$rank != without$rank + 1) return(out)
    }
    estimate <- unname(stats::coef(fit)[[".d"]])
    se <- sqrt(stats::vcov(fit)[".d", ".d"])
    if (df == "asymptotic") {
      p <- 2 * stats::pnorm(-abs(estimate / se))
    } else if (aliased) {
      # car::Anova refuses aliased coefficients; the t test of b is the same test.
      p <- 2 * stats::pt(-abs(estimate / se), fit$df.residual)
    } else {
      p <- car::Anova(fit, type = 3)[".d", "Pr(>F)"]
    }
    return(list(p_value = unname(p), estimate = estimate))
  }
  if (model != "linear_contrast") fail("unknown model '", model, "'")
  fit <- model_fit(m$frame, ".g", m$terms)
  if (fit$df.residual < 1) return(out)
  emm <- model_emmeans(fit, m$frame, "equal", df)
  present <- as.character(as.data.frame(summary(emm))[[1]])
  coefficients <- unname(group_dose[present] - mean(group_dose[present]))
  table <- emm_table(emmeans::contrast(emm, method = list(linear = coefficients)), 95, TRUE)
  list(p_value = value_of(table, "linear", "p.value"),
       estimate = value_of(table, "linear", "estimate"))
}
