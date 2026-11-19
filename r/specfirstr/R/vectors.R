# Run the method vectors of tests/methods/ through the R implementations.
#
# In: one JSON file, a list of {"method", "cases": [{"input", "options"}, ...]}.
# Out: the same list with, per case, what the R implementation gives. The
# Python test compares it with the expected values of the vectors.

values_of <- function(items) {
  # A JSON array as a vector: numbers with NA, or text with NA, for null.
  if (length(items) == 0) return(numeric(0))
  if (any(vapply(items, is.character, TRUE))) {
    return(vapply(items, function(v) if (is.null(v)) NA_character_ else as.character(v), ""))
  }
  vapply(items, function(v) if (is.null(v)) NA_real_ else as.numeric(v), 0)
}

table_of <- function(rows) {
  if (length(rows) == 0) return(matrix(0, 0, 0))
  do.call(rbind, lapply(rows, function(row) as.numeric(unlist(row))))
}

scalar_of <- function(value) if (is.null(value)) NA_real_ else as.numeric(value)

vector_result <- function(method, input, options) {
  if (method == "count.subjects") {
    return(list(n = m_count_subjects(values_of(input$values))))
  }
  if (method == "percent.subjects") {
    return(list(pct = m_percent(scalar_of(input$numerator), scalar_of(input$denominator))))
  }
  if (method == "summary.continuous") {
    return(do.call(m_summary_continuous, c(list(values_of(input$values)), options)))
  }
  if (method == "test.chisq") return(list(p_value = m_chisq_p(table_of(input$table))))
  if (method == "test.fisher.exact") {
    limit <- input$max_tables %||% FISHER_MAX_TABLES  # a test may ask for a lower limit
    return(list(p_value = m_fisher_p(table_of(input$table), limit)))
  }
  if (method == "stats::fisher.test") {
    # Not a registry method: R's own function, as a second opinion (tests/methods, fisher-r).
    return(list(p_value = stats::fisher.test(reduced_table(table_of(input$table)))$p.value))
  }
  if (method == "test.anova.oneway") {
    return(list(p_value = m_anova_oneway_p(lapply(input$groups, values_of))))
  }
  if (method %in% MODEL_METHODS) return(model_vector(method, input, options))
  fail("the R engine does not implement ", method)
}

# A vector of a model-based method: the columns the options name, taken from the input.
model_vector <- function(method, input, options) {
  columns <- function(kind) {
    out <- list()
    for (name in unlist(options[[kind]])) out[[name]] <- values_of(input[[kind]][[name]])
    out
  }
  y <- values_of(input$y)
  group <- values_of(input$group)
  groups <- unlist(input$groups)
  factors <- columns("factors")
  covariates <- columns("covariates")
  df <- options$df %||% "residual"
  level <- as.numeric(options$confidence_level %||% 95)
  if (method == "model.ancova.lsmeans") {
    by_group <- m_ancova_lsmeans(y, group, groups, factors, covariates,
                                 options$weights %||% "equal", df, level)
  } else if (method == "model.ancova.pairwise") {
    by_group <- m_ancova_pairwise(y, group, groups, options$reference, factors, covariates,
                                  df, level)
  } else {
    return(m_ancova_dose_response(y, group, groups, values_of(input$dose), factors, covariates,
                                  options$dose %||% "grouping_value",
                                  options$model %||% "continuous_dose", df))
  }
  # One mapping per operation, from group to value.
  operations <- names(by_group[[1]])
  out <- list()
  for (operation in operations) {
    out[[operation]] <- lapply(by_group, function(values) values[[operation]])
  }
  out
}

# A result of a vector as JSON: a number, or a mapping of a group to a number.
json_result <- function(value) {
  if (is.list(value)) {
    keys <- names(value)
    parts <- vapply(keys, function(key) {
      v <- value[[key]]
      if (is.nan(v)) v <- NA_real_
      paste0(json_string(key), ":", json_scalar(v))
    }, "")
    return(paste0("{", paste(parts, collapse = ","), "}"))
  }
  if (is.nan(value)) value <- NA_real_
  json_scalar(value)
}

run_vectors <- function(in_path, out_path) {
  files <- jsonlite::fromJSON(in_path, simplifyVector = FALSE)
  lines <- character(0)
  for (file in files) {
    for (i in seq_along(file$cases)) {
      case <- file$cases[[i]]
      result <- vector_result(file$method, case$input, case$options %||% list())
      fields <- vapply(names(result), function(name) {
        paste0(json_string(name), ":", json_result(result[[name]]))
      }, "")
      lines <- c(lines, paste0("{\"method\":", json_string(file$method), ",\"case\":", i - 1,
                               ",\"result\":{", paste(fields, collapse = ","), "}}"))
    }
  }
  writeLines(lines, out_path)
  cat(sprintf("R vectors: %d cases of %d methods\n", length(lines), length(files)))
}
