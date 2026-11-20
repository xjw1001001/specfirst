# The R result engine: an ARS reporting event and ADaM data in, ARD rows out.
#
# It follows the numbered rules I1 to I15 of standard/methods/README.md, as the
# Python engine in src/specfirst/machine/ard.py does, and must give the same
# rows (rule R11). The comments name the rules. What an operation computes is
# in methods.R.

by_id <- function(items) {
  out <- list()
  for (item in items) out[[item$id]] <- item
  out
}

# ---- data (rule I1) ---------------------------------------------------------------

# One dataset as the Python side handed it over: a JSON file with one array
# per column. Numbers are doubles with NA for a missing value; everything else
# is text with "" for a missing value. The file is read without jsonlite's
# simplification, which takes the text "NA" for a missing value; every column
# is then converted by its kind.
read_handover <- function(path) {
  h <- jsonlite::fromJSON(path, simplifyVector = FALSE)
  columns <- list()
  kinds <- character(0)
  for (column in h$columns) {
    given <- column$values
    if (length(given) != h$rows) {
      fail("dataset ", h$dataset, ", column ", column$name, ": ", length(given),
           " values for ", h$rows, " rows")
    }
    absent <- vapply(given, is.null, TRUE)
    if (column$kind == "number") {
      values <- rep(NA_real_, length(given))
      values[!absent] <- vapply(given[!absent], as.numeric, 0)
    } else {
      values <- rep("", length(given))
      values[!absent] <- vapply(given[!absent], as.character, "")
    }
    columns[[column$name]] <- values
    kinds[[column$name]] <- column$kind
  }
  list(name = h$dataset, rows = h$rows, columns = columns, kinds = kinds)
}

eng_table <- function(eng, dataset) {
  if (is.null(eng$tables[[dataset]])) fail("dataset ", dataset, " was not handed to the engine")
  eng$tables[[dataset]]
}

eng_column <- function(eng, dataset, name) {
  table <- eng_table(eng, dataset)
  if (is.null(table$columns[[name]])) fail("dataset ", dataset, " has no column ", name)
  list(values = table$columns[[name]], kind = table$kinds[[name]])
}

# A column as text; numbers are written as group values are.
eng_text <- function(eng, dataset, name) {
  key <- paste(dataset, name, sep = ".")
  if (is.null(eng$texts[[key]])) {
    column <- eng_column(eng, dataset, name)
    eng$texts[[key]] <- if (column$kind == "number") number_text(column$values) else column$values
  }
  eng$texts[[key]]
}

eng_numbers <- function(eng, dataset, name) {
  column <- eng_column(eng, dataset, name)
  if (column$kind != "number") {
    fail(dataset, ".", name, " holds text; this method needs numbers")
  }
  column$values
}

# ---- where clauses (rules I3 to I5) ---------------------------------------------------

compare_values <- function(values, kind, comparator, wanted) {
  if (kind == "number") {
    numbers <- condition_numbers(wanted)
    ok <- !is.na(values)
    return(switch(comparator,
      EQ = ok & values == numbers[1],
      NE = !(ok & values == numbers[1]),
      IN = values %in% numbers,
      NOTIN = !(values %in% numbers),
      GT = ok & values > numbers[1],
      GE = ok & values >= numbers[1],
      LT = ok & values < numbers[1],
      LE = ok & values <= numbers[1],
      fail("unknown comparator ", comparator)))
  }
  texts <- as.character(wanted)
  here <- values != ""  # an ordered comparison with a missing value is false
  switch(comparator,
    EQ = values == texts[1],
    NE = values != texts[1],
    IN = values %in% texts,
    NOTIN = !(values %in% texts),
    GT = here & values > texts[1],
    GE = here & values >= texts[1],
    LT = here & values < texts[1],
    LE = here & values <= texts[1],
    fail("unknown comparator ", comparator))
}

clause_conditions <- function(clause) {
  out <- list()
  if (!is.null(clause$condition)) out <- list(clause$condition)
  for (inner in clause$compoundExpression$whereClauses) {
    out <- c(out, clause_conditions(inner))
  }
  out
}

# The records of `dataset` that fulfil a where clause.
where_mask <- function(eng, dataset, clause) {
  condition <- clause$condition
  if (!is.null(condition)) {
    source <- condition$dataset
    column <- eng_column(eng, source, condition$variable)
    if (!all(vapply(condition$value, is.character, TRUE))) {
      fail("a condition on ", source, ".", condition$variable, " has a value that is not text")
    }
    mask <- compare_values(column$values, column$kind, condition$comparator,
                           unlist(condition$value))
    if (source == dataset) return(mask)
    # Rule I4: it holds for at least one record of the same subject there.
    subjects <- unique(eng_text(eng, source, eng$subject_key)[mask])
    return(eng_text(eng, dataset, eng$subject_key) %in% subjects[subjects != ""])
  }
  compound <- clause$compoundExpression
  parts <- lapply(compound$whereClauses, function(inner) where_mask(eng, dataset, inner))
  switch(compound$logicalOperator,
    AND = Reduce(`&`, parts),
    OR = Reduce(`|`, parts),
    NOT = !parts[[1]],
    fail("unknown logical operator ", compound$logicalOperator))
}

# The parts a where clause joins with AND at its top; the clause itself otherwise.
and_parts <- function(clause) {
  compound <- clause$compoundExpression
  if (!is.null(compound) && identical(compound$logicalOperator, "AND")) {
    return(do.call(c, lapply(compound$whereClauses, and_parts)))
  }
  list(clause)
}

# ---- groupings (rules I7 to I10) --------------------------------------------------------

# The grouping variable as text on every record of `dataset` (rule I9).
group_values <- function(eng, dataset, grouping) {
  key <- paste(dataset, grouping$id, sep = "\x1f")
  if (!is.null(eng$group_values[[key]])) return(eng$group_values[[key]])
  source <- grouping$groupingDataset
  variable <- grouping$groupingVariable
  if (source == dataset) {
    values <- eng_text(eng, dataset, variable)
  } else {
    keys <- eng_text(eng, source, eng$subject_key)
    there <- eng_text(eng, source, variable)
    first <- match(keys, keys)
    if (any(there != there[first])) {
      fail("grouping '", grouping$id, "': a subject has two values of ", source, ".", variable)
    }
    values <- there[match(eng_text(eng, dataset, eng$subject_key), keys)]
    values[is.na(values)] <- ""
  }
  eng$group_values[[key]] <- values
  values
}

# The groups of a grouping on some records: kind, key and a mask over `rows`.
members <- function(eng, dataset, grouping, rows) {
  if (isTRUE(grouping$dataDriven)) {
    values <- group_values(eng, dataset, grouping)[rows]
    keys <- sort(unique(values[values != ""]), method = "radix")
    return(lapply(keys, function(key) list(kind = "value", key = key, mask = values == key)))
  }
  lapply(grouping$groups, function(group) {
    list(kind = "id", key = group$id, mask = where_mask(eng, dataset, group)[rows])
  })
}

# Every cell of an analysis: its groups and its records (rule I10).
cells <- function(eng, dataset, rows, by) {
  fixed <- list()
  driven <- list()
  for (entry in by) {
    if (isTRUE(entry$grouping$dataDriven)) {
      entry$values <- group_values(eng, dataset, entry$grouping)[rows]
      driven[[length(driven) + 1]] <- entry
    } else {
      entry$groups <- members(eng, dataset, entry$grouping, rows)
      fixed[[length(fixed) + 1]] <- entry
    }
  }
  combinations <- matrix(character(0), nrow = 1, ncol = 0)
  if (length(driven) > 0) {
    here <- Reduce(`&`, lapply(driven, function(d) d$values != ""))
    combinations <- unique(do.call(cbind, lapply(driven, function(d) d$values[here])))
  }
  choices <- list(integer(0))
  for (entry in fixed) {
    choices <- do.call(c, lapply(choices, function(choice) {
      lapply(seq_along(entry$groups), function(i) c(choice, i))
    }))
  }
  found <- list()
  for (choice in choices) {
    mask <- rep(TRUE, length(rows))
    labels <- list()
    for (k in seq_along(fixed)) {
      group <- fixed[[k]]$groups[[choice[k]]]
      mask <- mask & group$mask
      labels[[length(labels) + 1]] <- list(n = fixed[[k]]$n, grouping = fixed[[k]]$grouping$id,
                                           kind = group$kind, key = group$key)
    }
    for (row in seq_len(nrow(combinations))) {
      inner <- mask
      cell_labels <- labels
      for (k in seq_along(driven)) {
        inner <- inner & driven[[k]]$values == combinations[row, k]
        cell_labels[[length(cell_labels) + 1]] <- list(
          n = driven[[k]]$n, grouping = driven[[k]]$grouping$id, kind = "value",
          key = combinations[row, k])
      }
      found[[length(found) + 1]] <- list(labels = cell_labels, rows = rows[inner])
    }
  }
  found
}

# ---- tests (rules I12 and I13) ----------------------------------------------------------

# The population of an occurrence test (rule I13): its dataset, its records,
# and the size of every group of the compared grouping.
population <- function(eng, analysis, grouping) {
  if (!is.null(eng$populations[[analysis$id]])) return(eng$populations[[analysis$id]])
  where <- paste0("analysis '", analysis$id, "'")
  if (is.null(analysis$analysisSetId)) fail(where, ": an occurrence test needs an analysis set")
  chosen <- eng$sets[[analysis$analysisSetId]]
  datasets <- unique(vapply(clause_conditions(chosen), function(c) c$dataset, ""))
  if (length(datasets) != 1) fail(where, ": the analysis set must be on one dataset")
  source <- datasets[1]
  keep <- where_mask(eng, source, chosen)
  if (!is.null(analysis$dataSubsetId)) {
    for (part in and_parts(eng$subsets[[analysis$dataSubsetId]])) {
      named <- unique(vapply(clause_conditions(part), function(c) c$dataset, ""))
      if (length(named) == 1 && named == source) keep <- keep & where_mask(eng, source, part)
    }
  }
  rows <- which(keep)
  everyone <- eng_text(eng, source, eng$subject_key)[rows]
  groups <- lapply(members(eng, source, grouping, rows), function(member) {
    list(kind = member$kind, key = member$key, size = m_count_subjects(everyone[member$mask]))
  })
  eng$populations[[analysis$id]] <- list(source = source, rows = rows, groups = groups)
  eng$populations[[analysis$id]]
}

# The table of a chi-square or Fisher test on the records of one cell (rule I12).
test_table <- function(eng, analysis, rows, compared) {
  dataset <- analysis$dataset
  variable <- analysis$variable
  where <- paste0("analysis '", analysis$id, "'")
  subjects <- eng_text(eng, dataset, variable)[rows]
  if (length(compared) == 2) {
    first <- members(eng, dataset, compared[[1]], rows)
    second <- members(eng, dataset, compared[[2]], rows)
    table <- matrix(0, nrow = length(first), ncol = length(second))
    for (i in seq_along(first)) {
      for (j in seq_along(second)) {
        table[i, j] <- m_count_subjects(subjects[first[[i]]$mask & second[[j]]$mask])
      }
    }
    return(table)
  }
  if (length(compared) != 1) {
    fail(where, ": a test on a table compares one or two groupings, found ", length(compared))
  }
  if (variable != eng$subject_key) {
    fail(where, ": an occurrence test counts subjects, so the analysis variable must be ",
         eng$subject_key)
  }
  grouping <- compared[[1]]
  lines <- list()
  for (group in population(eng, analysis, grouping)$groups) {
    if (group$size == 0) next
    if (group$kind == "value") {
      here <- group_values(eng, dataset, grouping)[rows] == group$key
    } else {
      defined <- Filter(function(g) g$id == group$key, grouping$groups)[[1]]
      here <- where_mask(eng, dataset, defined)[rows]
    }
    occurred <- m_count_subjects(subjects[here])
    if (occurred > group$size) {
      fail(where, ": group ", group$key, " has ", occurred, " subjects with a record and ",
           group$size, " in the population")
    }
    lines[[length(lines) + 1]] <- c(occurred, group$size - occurred)
  }
  if (length(lines) == 0) return(matrix(0, nrow = 0, ncol = 2))
  do.call(rbind, lines)
}

# ---- analyses ---------------------------------------------------------------------------

pair_strings <- function(groups) {
  kept <- Filter(function(g) g$kind != "all", groups)
  sort(vapply(kept, function(g) paste(g$grouping, g$kind, g$key, sep = "\x1f"), ""),
       method = "radix")
}

new_result <- function(analysis_id, operation_id, groups, method_id, options_hash, value) {
  groups <- groups[order(vapply(groups, function(g) g$n, 0))]
  pairs <- pair_strings(groups)
  list(analysis_id = analysis_id, operation_id = operation_id, groups = groups,
       method_id = method_id, options_hash = options_hash, value = value, pairs = pairs,
       cell = paste(pairs, collapse = "\x1e"))
}

analysis_results <- function(eng, analysis_id) {
  if (is.null(eng$results[[analysis_id]])) {
    if (analysis_id %in% eng$running) {
      fail("analyses reference each other in a circle: ",
           paste(c(eng$running, analysis_id), collapse = " -> "))
    }
    if (is.null(eng$analyses[[analysis_id]])) fail("no analysis '", analysis_id, "'")
    eng$running <- c(eng$running, analysis_id)
    eng$results[[analysis_id]] <- run_analysis(eng, eng$analyses[[analysis_id]])
    eng$running <- eng$running[-length(eng$running)]
  }
  eng$results[[analysis_id]]
}

# The result an operation references in a role, for one cell (percent.subjects).
referenced <- function(eng, analysis, operation, role, groups, own) {
  where <- paste0("analysis '", analysis$id, "', operation '", operation$id, "'")
  relationships <- Filter(
    function(r) identical(r$referencedOperationRole$controlledTerm, role),
    operation$referencedOperationRelationships)
  if (length(relationships) != 1) {
    fail(where, ": needs one referenced operation with the role ", role)
  }
  targets <- Filter(
    function(r) identical(r$referencedOperationRelationshipId, relationships[[1]]$id),
    analysis$referencedAnalysisOperations)
  if (length(targets) != 1) {
    fail(where, ": the analysis does not say which analysis gives the ", role)
  }
  target <- targets[[1]]$analysisId
  pool <- if (target == analysis$id) own else analysis_results(eng, target)
  wanted <- relationships[[1]]$operationId
  cell <- pair_strings(groups)
  cell_key <- paste(cell, collapse = "\x1e")
  fits <- list()
  for (result in pool) {
    if (result$operation_id != wanted) next
    if (role == "NUMERATOR") {  # in the same cell
      if (result$cell == cell_key) fits[[length(fits) + 1]] <- result
    } else if (all(result$pairs %in% cell)) {  # its groups are all groups of the cell
      fits[[length(fits) + 1]] <- result
    }
  }
  if (length(fits) != 1) {
    fail(where, ": ", length(fits), " results of ", target, ".", wanted, " fit the cell as ", role)
  }
  fits[[1]]$value
}

run_analysis <- function(eng, analysis) {
  dataset <- analysis$dataset
  variable <- analysis$variable
  where <- paste0("analysis '", analysis$id, "'")
  keep <- rep(TRUE, eng_table(eng, dataset)$rows)  # rule I6
  if (!is.null(analysis$analysisSetId)) {
    keep <- keep & where_mask(eng, dataset, eng$sets[[analysis$analysisSetId]])
  }
  if (!is.null(analysis$dataSubsetId)) {
    keep <- keep & where_mask(eng, dataset, eng$subsets[[analysis$dataSubsetId]])
  }
  rows <- which(keep)
  ordered <- analysis$orderedGroupings
  if (length(ordered) > 0) {
    ordered <- ordered[order(vapply(ordered, function(g) as.numeric(g$order %||% 0), 0))]
  }
  by <- list()
  compared <- list()
  compared_labels <- list()
  for (n in seq_along(ordered)) {
    grouping <- eng$groupings[[ordered[[n]]$groupingId]]
    if (isTRUE(ordered[[n]]$resultsByGroup)) {
      by[[length(by) + 1]] <- list(n = n, grouping = grouping)
    } else {
      compared[[length(compared) + 1]] <- grouping
      compared_labels[[length(compared_labels) + 1]] <- list(
        n = n, grouping = grouping$id, kind = "all", key = NA_character_)
    }
  }
  operations <- eng$methods[[analysis$methodId]]$operations
  operations <- operations[order(vapply(operations, function(o) as.numeric(o$order %||% 0), 0),
                                 vapply(operations, function(o) o$id, ""), method = "radix")]
  options <- eng$binding$options[[analysis$id]]
  bound <- lapply(operations, function(operation) {
    entry <- eng$binding$operations[[operation$id]]
    if (is.null(entry)) fail(where, ": operation ", operation$id, " is not bound")
    list(operation = operation, method = entry$method, name = entry$operation,
         hash = sha256_text(canonical_options(options[[entry$method]])))
  })
  kinds <- vapply(bound, function(item) eng$registry$methods[[item$method]]$kind, "")
  if (any(kinds == "model")) {
    if (length(unique(vapply(bound, function(item) item$method, ""))) != 1) {
      fail(where, ": a model-based analysis binds the operations of one registry method")
    }
    return(run_model(eng, analysis, rows, ordered, bound, options[[bound[[1]]$method]]))
  }
  found <- list()
  percents <- list()
  for (cell in cells(eng, dataset, rows, by)) {
    summary <- NULL
    for (item in bound) {
      groups <- cell$labels
      method <- item$method
      if (method == "count.subjects") {
        value <- m_count_subjects(eng_text(eng, dataset, variable)[cell$rows])
      } else if (method == "summary.continuous") {
        if (is.null(summary)) {
          summary <- do.call(m_summary_continuous, c(
            list(eng_numbers(eng, dataset, variable)[cell$rows]), options[[method]]))
        }
        value <- summary[[item$name]]
      } else if (method == "percent.subjects") {
        percents[[length(percents) + 1]] <- list(groups = groups, item = item)
        next
      } else if (method %in% c("test.chisq", "test.fisher.exact")) {
        table <- test_table(eng, analysis, cell$rows, compared)
        value <- if (method == "test.chisq") m_chisq_p(table) else m_fisher_p(table)
        groups <- c(groups, compared_labels)
      } else if (method == "test.anova.oneway") {
        if (length(compared) != 1) {
          fail(where, ": the analysis of variance compares one grouping, found ",
               length(compared))
        }
        numbers <- eng_numbers(eng, dataset, variable)[cell$rows]
        value <- m_anova_oneway_p(lapply(
          members(eng, dataset, compared[[1]], cell$rows), function(m) numbers[m$mask]))
        groups <- c(groups, compared_labels)
      } else {
        fail(where, ": the R engine does not know ", method)
      }
      if (is.nan(value)) value <- NA_real_
      if (!is.na(value) && !is.finite(value)) {
        fail(where, ", operation ", item$operation$id, ": the result is ", value)
      }
      found[[length(found) + 1]] <- new_result(analysis$id, item$operation$id, groups, method,
                                               item$hash, value)
    }
  }
  for (entry in percents) {
    operation <- entry$item$operation
    numerator <- referenced(eng, analysis, operation, "NUMERATOR", entry$groups, found)
    denominator <- referenced(eng, analysis, operation, "DENOMINATOR", entry$groups, found)
    found[[length(found) + 1]] <- new_result(
      analysis$id, operation$id, entry$groups, "percent.subjects", entry$item$hash,
      m_percent(as.numeric(numerator), as.numeric(denominator)))
  }
  found
}

# ---- model-based analyses (rules I16 to I19; R only) --------------------------------------

# The model of an analysis is fitted once, to its analysis records (rule I6). Its one
# grouping is the treatment: the group of a record is the group whose where clause it
# fulfils (rule I8), or its value (rule I9). Results are per group of the grouping, or
# one for the analysis when the grouping is compared (resultsByGroup false).
run_model <- function(eng, analysis, rows, ordered, bound, options) {
  dataset <- analysis$dataset
  method <- bound[[1]]$method
  where <- paste0("analysis '", analysis$id, "'")
  if (length(ordered) != 1) {
    fail(where, ": a model-based analysis has one grouping, the treatment; found ",
         length(ordered))
  }
  grouping <- eng$groupings[[ordered[[1]]$groupingId]]
  split <- isTRUE(ordered[[1]]$resultsByGroup)
  if (method == "model.ancova.dose_response" && split) {
    fail(where, ": the dose-response test compares its grouping (resultsByGroup false)")
  }
  if (method != "model.ancova.dose_response" && !split) {
    fail(where, ": ", method, " gives results by group (resultsByGroup true)")
  }
  groups <- members(eng, dataset, grouping, rows)
  ids <- vapply(groups, function(g) g$key, "")
  group <- rep(NA_character_, length(rows))
  for (g in groups) {
    if (any(!is.na(group[g$mask]))) fail(where, ": a record belongs to two groups of ", grouping$id)
    group[g$mask] <- g$key
  }
  y <- eng_numbers(eng, dataset, analysis$variable)[rows]
  factors <- list()
  for (name in unlist(options$factors)) factors[[name]] <- eng_text(eng, dataset, name)[rows]
  covariates <- list()
  for (name in unlist(options$covariates)) {
    covariates[[name]] <- eng_numbers(eng, dataset, name)[rows]
  }
  df <- options$df %||% "residual"
  level <- as.numeric(options$confidence_level %||% 95)
  label <- function(g) list(n = 1, grouping = grouping$id, kind = g$kind, key = g$key)
  found <- list()
  add <- function(groups_of, value_of) {
    for (item in bound) {
      value <- value_of(item$name)
      if (is.nan(value)) value <- NA_real_
      found[[length(found) + 1]] <<- new_result(analysis$id, item$operation$id, groups_of,
                                                method, item$hash, value)
    }
  }
  if (method == "model.ancova.dose_response") {
    doses <- NULL
    if ((options$dose %||% "grouping_value") == "grouping_value") {
      source <- eng_column(eng, grouping$groupingDataset, grouping$groupingVariable)
      if (source$kind != "number") {
        fail(where, ": the dose is the value of ", grouping$groupingDataset, ".",
             grouping$groupingVariable, ", which holds text")
      }
      texts <- group_values(eng, dataset, grouping)[rows]
      doses <- rep(NA_real_, length(texts))
      if (any(texts != "")) doses[texts != ""] <- numbers_of(texts[texts != ""])
    }
    result <- m_ancova_dose_response(y, group, ids, doses, factors, covariates,
                                     options$dose %||% "grouping_value",
                                     options$model %||% "continuous_dose", df)
    add(list(list(n = 1, grouping = grouping$id, kind = "all", key = NA_character_)),
        function(name) result[[name]])
    return(found)
  }
  if (method == "model.ancova.lsmeans") {
    result <- m_ancova_lsmeans(y, group, ids, factors, covariates,
                               options$weights %||% "equal", df, level)
    for (g in groups) add(list(label(g)), function(name) result[[g$key]][[name]])
    return(found)
  }
  if (method == "model.ancova.pairwise") {
    if (!options$reference %in% ids) {
      fail(where, ": the reference group ", options$reference, " is not a group of ",
           grouping$id)
    }
    result <- m_ancova_pairwise(y, group, ids, options$reference, factors, covariates, df,
                                level)
    for (g in groups) {
      if (g$key == options$reference) next
      add(list(label(g)), function(name) result[[g$key]][[name]])
    }
    return(found)
  }
  fail(where, ": the R engine does not know ", method)
}

# ---- the registry and the job -----------------------------------------------------------

# What the job binds must be in the registry, with an R implementation and
# with options the registry knows.
check_binding <- function(registry, binding) {
  for (operation_id in names(binding$operations)) {
    entry <- binding$operations[[operation_id]]
    method <- registry$methods[[entry$method]]
    if (is.null(method)) fail("operation ", operation_id, ": no method ", entry$method)
    if (is.null(method$operations[[entry$operation]])) {
      fail("method ", entry$method, " has no operation ", entry$operation)
    }
    if (!"r" %in% unlist(method$implementations)) {
      fail("method ", entry$method, " has no R implementation")
    }
  }
  for (analysis_id in names(binding$options)) {
    for (method_id in names(binding$options[[analysis_id]])) {
      method <- registry$methods[[method_id]]
      given <- binding$options[[analysis_id]][[method_id]]
      if (!setequal(names(given), names(method$options))) {
        fail("analysis ", analysis_id, ": the options of ", method_id, " are not those of ",
             "the registry")
      }
      for (name in names(given)) {
        takes <- method$options[[name]]$takes
        if (!is.null(takes)) {  # columns, or a group: stated by the analysis (ADR-015)
          if (!all(vapply(given[[name]], is.character, TRUE))) {
            fail("analysis ", analysis_id, ", method ", method_id, ": option ", name,
                 " is not text")
          }
          next
        }
        if (!given[[name]] %in% unlist(method$options[[name]]$values)) {
          fail("analysis ", analysis_id, ", method ", method_id, ": option ", name, " = ",
               given[[name]], " is not in the registry")
        }
      }
    }
  }
}

result_row <- function(result) {
  parts <- c(encode_part(result$analysis_id), encode_part(result$operation_id))
  fields <- c(paste0("\"analysis_id\":", json_string(result$analysis_id)),
              paste0("\"operation_id\":", json_string(result$operation_id)))
  for (group in result$groups) {
    fields <- c(fields, paste0("\"group", group$n, "_groupingId\":", json_string(group$grouping)))
    if (group$kind == "id") {
      fields <- c(fields, paste0("\"group", group$n, "_groupId\":", json_string(group$key)))
      parts <- c(parts, encode_part(group$key))
    } else if (group$kind == "value") {
      fields <- c(fields, paste0("\"group", group$n, "_groupValue\":", json_string(group$key)))
      parts <- c(parts, paste0("=", encode_part(group$key)))
    } else {
      parts <- c(parts, "*")
    }
  }
  id <- paste0("ard:", paste(parts, collapse = "/"))
  fields <- c(fields, paste0("\"id\":", json_string(id)),
              paste0("\"method_id\":", json_string(result$method_id)),
              paste0("\"method_options_hash\":", json_string(result$options_hash)),
              paste0("\"raw_value\":", json_scalar(result$value)))
  list(id = id, line = paste0("{", paste(fields, collapse = ","), "}"))
}

# Run a job: read the ARS file, the registry and the data, write the rows.
run_job <- function(job_path) {
  started <- proc.time()[["elapsed"]]
  job <- jsonlite::fromJSON(job_path, simplifyVector = FALSE)
  event <- jsonlite::fromJSON(job$ars, simplifyVector = FALSE)
  registry <- jsonlite::fromJSON(job$registry, simplifyVector = FALSE)
  check_binding(registry, job$binding)
  eng <- new.env()
  eng$subject_key <- job$subject_key
  eng$binding <- job$binding
  eng$registry <- registry
  eng$analyses <- by_id(event$analyses)
  eng$methods <- by_id(event$methods)
  eng$sets <- by_id(event$analysisSets)
  eng$subsets <- by_id(event$dataSubsets)
  eng$groupings <- by_id(event$analysisGroupings)
  eng$tables <- lapply(job$data, read_handover)
  eng$texts <- list()
  eng$group_values <- list()
  eng$populations <- list()
  eng$results <- list()
  eng$running <- character(0)
  rows <- list()
  for (analysis in event$analyses) {
    rows <- c(rows, lapply(analysis_results(eng, analysis$id), result_row))
  }
  ids <- vapply(rows, function(row) row$id, "")
  if (anyDuplicated(ids)) fail("two results have the ID ", ids[anyDuplicated(ids)])
  lines <- vapply(rows, function(row) row$line, "")[order(ids, method = "radix")]
  con <- file(job$out, open = "wb")
  writeLines(enc2utf8(lines), con, sep = "\n", useBytes = TRUE)
  close(con)
  fingerprints <- list()
  for (table in eng$tables) {
    for (name in names(table$columns)) {
      fingerprints[[paste(table$name, name, sep = ".")]] <-
        column_fingerprint(table$columns[[name]], table$kinds[[name]])
    }
  }
  meta <- list(engine = "r", r = paste(R.version$major, R.version$minor, sep = "."),
               rows = length(lines), columns = fingerprints,
               seconds = round(proc.time()[["elapsed"]] - started, 2))
  writeLines(jsonlite::toJSON(meta, auto_unbox = TRUE), job$meta)
  cat(sprintf("R engine: %d analyses, %d rows, %.1f s\n", length(event$analyses),
              length(lines), meta$seconds))
}
