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
  if (method == "test.fisher.exact") return(list(p_value = m_fisher_p(table_of(input$table))))
  if (method == "test.anova.oneway") {
    return(list(p_value = m_anova_oneway_p(lapply(input$groups, values_of))))
  }
  fail("the R engine does not implement ", method)
}

run_vectors <- function(in_path, out_path) {
  files <- jsonlite::fromJSON(in_path, simplifyVector = FALSE)
  lines <- character(0)
  for (file in files) {
    for (i in seq_along(file$cases)) {
      case <- file$cases[[i]]
      result <- vector_result(file$method, case$input, case$options %||% list())
      fields <- vapply(names(result), function(name) {
        value <- result[[name]]
        if (is.nan(value)) value <- NA_real_
        paste0(json_string(name), ":", json_scalar(value))
      }, "")
      lines <- c(lines, paste0("{\"method\":", json_string(file$method), ",\"case\":", i - 1,
                               ",\"result\":{", paste(fields, collapse = ","), "}}"))
    }
  }
  writeLines(lines, out_path)
  cat(sprintf("R vectors: %d cases of %d methods\n", length(lines), length(files)))
}
