# Small helpers of the R result engine: text, hashes, JSON lines.
# Base R and jsonlite only: these are among the locked packages (env/r-packages.lock).

`%||%` <- function(a, b) if (is.null(a)) b else a

fail <- function(...) stop(paste0(...), call. = FALSE)

# SHA-256 of a text, as lower-case hex (tools::sha256sum takes bytes since R 4.5).
sha256_text <- function(text) {
  unname(tools::sha256sum(bytes = charToRaw(enc2utf8(text))))
}

json_string <- function(x) {
  x <- gsub("\\", "\\\\", enc2utf8(x), fixed = TRUE)
  x <- gsub("\"", "\\\"", x, fixed = TRUE)
  x <- gsub("\n", "\\n", x, fixed = TRUE)
  x <- gsub("\r", "\\r", x, fixed = TRUE)
  x <- gsub("\t", "\\t", x, fixed = TRUE)
  paste0("\"", x, "\"")
}

# One scalar as JSON. Whole numbers of a count are written without a decimal point.
json_scalar <- function(value) {
  if (is.null(value) || (length(value) == 1 && is.na(value))) return("null")
  if (is.character(value)) return(json_string(value))
  if (is.logical(value)) return(if (value) "true" else "false")
  if (is.integer(value)) return(sprintf("%d", value))
  if (!is.finite(value)) fail("a result is ", value)
  sprintf("%.17g", value)
}

# Canonical JSON of the options of a method: keys sorted, no spaces. The same
# bytes as specfirst.machine.canonical.json_text gives, for text, whole
# numbers and true or false, which is all an option may hold.
canonical_options <- function(options) {
  if (length(options) == 0) return("{}")
  keys <- sort(names(options), method = "radix")
  parts <- vapply(keys, function(key) {
    value <- options[[key]]
    if (is.double(value) && value == round(value)) value <- as.integer(value)
    if (is.double(value)) fail("option '", key, "' is not text, a whole number, true or false")
    paste0(json_string(key), ":", json_scalar(value))
  }, "")
  paste0("{", paste(parts, collapse = ","), "}")
}

# Percent-encode everything but letters, digits and - . _ ~ (as Python's
# urllib.parse.quote with safe = "" does), byte by byte in UTF-8.
encode_part <- function(text) {
  bytes <- charToRaw(enc2utf8(text))
  if (length(bytes) == 0) return("")
  values <- as.integer(bytes)
  keep <- (values >= 48 & values <= 57) | (values >= 65 & values <= 90) |
    (values >= 97 & values <= 122) | values %in% c(45L, 46L, 95L, 126L)
  out <- sprintf("%%%02X", values)
  out[keep] <- vapply(bytes[keep], rawToChar, "")
  paste(out, collapse = "")
}

# A number as the text of a group value: 8 for 8.0, otherwise 17 significant
# digits cut to the shortest text that reads back as the same number.
number_text <- function(x) {
  out <- rep("", length(x))
  ok <- !is.na(x)
  whole <- ok & x == round(x) & abs(x) < 1e15
  out[whole] <- sprintf("%.0f", x[whole])
  rest <- which(ok & !whole)
  for (i in rest) {
    for (digits in 15:17) {
      text <- sprintf("%.*g", digits, x[i])
      if (jsonlite::fromJSON(paste0("[", text, "]")) == x[i]) break
    }
    out[i] <- text
  }
  out
}

# The fingerprint of a column as this engine read it: the values as text,
# joined by the unit separator. The Python side computes the same from the
# Parquet data, so the two engines can show they saw the same values.
column_fingerprint <- function(values, kind) {
  text <- if (kind == "number") {
    ifelse(is.na(values), "NA", sprintf("%.17g", values))
  } else {
    values
  }
  sha256_text(paste(text, collapse = "\x1f"))
}
