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

model_emmeans <- function(fit, frame, weights, df, specs = ".g") {
  # nesting = NULL: a factor nested in the groups leaves the LS means not estimable
  # (statements 4 and 7), so missing; emmeans would otherwise average within the
  # groups (review of real-5a, F5).
  emm <- emmeans::emmeans(fit, specs = specs, weights = weights, data = frame, nesting = NULL)
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
  present <- unique(as.character(m$frame$.g))
  if (length(present) == 1) {
    # One group with model records: no group term to fit; its LS mean is the
    # prediction of the model without it (statement 4; review of real-5a, F5).
    fit <- model_fit(m$frame, "1", m$terms)
    if (fit$df.residual < 1) return(out)
    table <- emm_table(model_emmeans(fit, m$frame, weights, df, specs = ~1), confidence_level,
                       FALSE)
    row <- rownames(table)[1]
    out[[present]] <- list(lsmean = value_of(table, row, "emmean"),
                           se = value_of(table, row, "SE"),
                           lower_cl = value_of(table, row, "lower"),
                           upper_cl = value_of(table, row, "upper"))
    return(out)
  }
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
  if (length(unique(as.character(m$frame$.g))) < 2) return(out)  # only the reference
  fit <- model_fit(m$frame, ".g", m$terms)
  if (fit$df.residual < 1) return(out)
  # Statement 3: the difference does not depend on the weights of the LS means.
  emm <- model_emmeans(fit, m$frame, "equal", df)
  present <- as.character(as.data.frame(summary(emm))[[1]])
  if (length(present) < 2 || !reference %in% present) return(out)
  # The contrasts are named by position: an ID may hold "-", and emmeans would
  # write "(Grp-2) - (Grp-1)" (review of real-5a, F5).
  coefficients <- list()
  for (id in setdiff(present, reference)) {
    coefficients[[paste0("c", match(id, present))]] <-
      as.numeric(present == id) - as.numeric(present == reference)
  }
  contrasts <- emmeans::contrast(emm, method = coefficients, adjust = "none")
  table <- emm_table(contrasts, confidence_level, TRUE)
  for (id in others) {
    row <- paste0("c", match(id, present))
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

# ---- the mixed model for repeated measures (amendment of real-5b to ADR-015) ----------
#
#   model.mmrm.lsmeans    least-squares means by treatment group
#   model.mmrm.pairwise   each group against a reference group
#
# The fit is mmrm (restricted maximum likelihood); the LS means and their
# differences come from emmeans on that fit, which takes the degrees of freedom
# and, for kenward_roger_linear, the adjusted covariance from it. The optimizer
# is nlminb: mmrm's default, L-BFGS-B, stops before the maximum, which moves
# standard errors in the fifth digit (statement 5). The expected values of
# the vectors come from tests/methods/oracle_mmrm.py, not from mmrm.

MODEL_METHODS <- c(MODEL_METHODS, "model.mmrm.lsmeans", "model.mmrm.pairwise")

# Statements 1 to 3 of model.mmrm.lsmeans: the model records, the visits, the terms.
mmrm_frame <- function(y, group, groups, visit, subject, factors, covariates, by_visit) {
  if (length(intersect(names(factors), names(covariates))) > 0) {
    fail("a column is both a factor and a covariate of the model")
  }
  if (!all(by_visit %in% c(names(factors), names(covariates)))) {
    fail("a column of by_visit is not a factor or a covariate of the model")
  }
  keep <- !is.na(y) & !is.na(group) & group != "" & group %in% groups &
    !is.na(visit) & as.character(visit) != "" & !is.na(subject) & subject != ""
  for (values in factors) keep <- keep & !is.na(values) & values != ""
  for (values in covariates) keep <- keep & !is.na(values)
  pairs <- paste(subject[keep], as.character(visit[keep]), sep = "\x1f")
  if (anyDuplicated(pairs) > 0) fail("two model records of one subject at one visit")
  frame <- data.frame(.y = as.numeric(y[keep]))
  frame$.g <- factor(group[keep], levels = groups[groups %in% group[keep]])
  visits <- if (is.numeric(visit)) sort(unique(visit[keep])) else sort(unique(visit[keep]), method = "radix")
  frame$.v <- factor(as.character(visit[keep]), levels = as.character(visits))
  frame$.s <- factor(subject[keep])
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
    if (name %in% by_visit) terms <- c(terms, paste0(column, ":.v"))
  }
  k <- 0
  for (name in names(covariates)) {
    k <- k + 1
    column <- paste0(".c", k)
    frame[[column]] <- as.numeric(covariates[[name]][keep])
    terms <- c(terms, column)
    if (name %in% by_visit) terms <- c(terms, paste0(column, ":.v"))
  }
  list(frame = frame, terms = terms, visits = as.character(visits))
}

# Statements 3 to 5: the fit, or NULL when it gives missing results.
mmrm_fit <- function(m, treatment_by_visit, covariance, df) {
  if (nrow(m$frame) == 0) return(NULL)
  lead <- c(".g", ".v", if (treatment_by_visit == "yes") ".g:.v")
  fixed <- paste(".y ~", paste(c(lead, m$terms), collapse = " + "))
  design <- stats::model.matrix(stats::as.formula(fixed), data = m$frame)
  if (qr(design)$rank < ncol(design)) return(NULL)
  structure <- switch(covariance, unstructured = "us", toeplitz = "toep",
                      fail("unknown covariance '", covariance, "'"))
  formula <- stats::as.formula(paste0(fixed, " + ", structure, "(.v | .s)"))
  control <- if (df == "kenward_roger_linear") {
    mmrm::mmrm_control(method = "Kenward-Roger", vcov = "Kenward-Roger-Linear",
                       optimizer = "nlminb")
  } else if (df == "satterthwaite") {
    mmrm::mmrm_control(method = "Satterthwaite", optimizer = "nlminb")
  } else {
    fail("unknown df '", df, "'")
  }
  fit <- tryCatch(mmrm::mmrm(formula, data = m$frame, reml = TRUE, control = control),
                  error = function(e) NULL)
  if (is.null(fit) || !isTRUE(attr(fit, "converged"))) return(NULL)
  fit
}

# Statement 6: the LS means at the last visit or averaged over the visits.
mmrm_emmeans <- function(fit, m, at) {
  if (at == "last") {
    grid <- list(.v = utils::tail(m$visits, 1))
    return(suppressMessages(emmeans::emmeans(fit, specs = ".g", by = ".v", at = grid,
                                             weights = "equal")))
  }
  if (at != "average") fail("unknown at '", at, "'")
  suppressMessages(emmeans::emmeans(fit, specs = ".g", weights = "equal"))
}

m_mmrm_lsmeans <- function(y, group, groups, visit, subject, factors = list(),
                           covariates = list(), by_visit = character(0),
                           treatment_by_visit = "yes", covariance = "unstructured",
                           df = "kenward_roger_linear", at = "last", confidence_level = 95) {
  operations <- c("lsmean", "se", "lower_cl", "upper_cl")
  out <- na_by_group(groups, operations)
  m <- mmrm_frame(y, group, groups, visit, subject, factors, covariates, by_visit)
  fit <- mmrm_fit(m, treatment_by_visit, covariance, df)
  if (is.null(fit)) return(out)
  table <- emm_table(mmrm_emmeans(fit, m, at), confidence_level, FALSE)
  for (id in groups) {
    out[[id]] <- list(lsmean = value_of(table, id, "emmean"), se = value_of(table, id, "SE"),
                      lower_cl = value_of(table, id, "lower"),
                      upper_cl = value_of(table, id, "upper"))
  }
  out
}

m_mmrm_pairwise <- function(y, group, groups, visit, subject, reference, factors = list(),
                            covariates = list(), by_visit = character(0),
                            treatment_by_visit = "yes", covariance = "unstructured",
                            df = "kenward_roger_linear", at = "last", confidence_level = 95) {
  if (!reference %in% groups) fail("the reference group ", reference, " is not a group")
  operations <- c("estimate", "se", "lower_cl", "upper_cl", "p_value")
  others <- setdiff(groups, reference)
  out <- na_by_group(others, operations)
  m <- mmrm_frame(y, group, groups, visit, subject, factors, covariates, by_visit)
  if (!reference %in% levels(m$frame$.g)) return(out)
  fit <- mmrm_fit(m, treatment_by_visit, covariance, df)
  if (is.null(fit)) return(out)
  emm <- mmrm_emmeans(fit, m, at)
  present <- levels(m$frame$.g)
  # The contrasts are named by position, not by the group IDs, which may hold "-".
  coefficients <- list()
  for (id in setdiff(present, reference)) {
    weights <- as.numeric(present == id) - as.numeric(present == reference)
    coefficients[[paste0("c", match(id, present))]] <- weights
  }
  table <- emm_table(emmeans::contrast(emm, method = coefficients, adjust = "none"),
                     confidence_level, TRUE)
  for (id in setdiff(present, reference)) {
    row <- paste0("c", match(id, present))
    out[[id]] <- list(estimate = value_of(table, row, "estimate"),
                      se = value_of(table, row, "SE"),
                      lower_cl = value_of(table, row, "lower"),
                      upper_cl = value_of(table, row, "upper"),
                      p_value = value_of(table, row, "p.value"))
  }
  out
}
