# Small helpers of the R result engine: text, hashes, JSON lines.
# Base R and jsonlite only: these are among the locked packages (env/r-packages.lock).

`%||%` <- function(a, b) if (is.null(a)) b else a

fail <- function(...) stop(paste0(...), call. = FALSE)

# SHA-256 of a text, as lower-case hex (tools::sha256sum takes bytes since R 4.5).
sha256_text <- function(text) {
  unname(tools::sha256sum(bytes = charToRaw(enc2utf8(text))))
}

# One text as a JSON string. What JSON does not allow inside a string is
# escaped by code point: the quotation mark (34), the backslash (92) and every
# control character below 32. Everything else is written as it is, in UTF-8.
json_string <- function(text) {
  if (length(text) != 1 || is.na(text)) fail("a JSON string is made from one text")
  codes <- utf8ToInt(enc2utf8(text))
  if (anyNA(codes)) fail("a text is not valid UTF-8")
  if (length(codes) == 0) return(strrep(intToUtf8(34L), 2))
  parts <- intToUtf8(codes, multiple = TRUE)
  special <- codes == 34L | codes == 92L
  parts[special] <- paste0(intToUtf8(92L), parts[special])
  control <- codes < 32L
  parts[control] <- sprintf("%su%04x", intToUtf8(92L), codes[control])
  paste0(intToUtf8(34L), paste(parts, collapse = ""), intToUtf8(34L))
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
    if (is.list(value)) {  # the columns of a model (ADR-015): a list of texts
      items <- vapply(value, function(item) json_string(as.character(item)), "")
      return(paste0(json_string(key), ":[", paste(items, collapse = ","), "]"))
    }
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

# Numbers read from their decimal text. jsonlite rounds correctly; R's own
# as.numeric does not always, for a text of 17 digits.
numbers_of <- function(texts) {
  as.numeric(jsonlite::fromJSON(paste0("[", paste(texts, collapse = ","), "]")))
}

# A number as the text of a group value (standard/methods/README.md, rule I9):
# zero is "0"; any other whole number has all its digits and neither a decimal
# point nor an exponent; any other number is the shortest decimal that reads
# back as the same number, written as Python writes it.
number_text <- function(x) {
  out <- rep("", length(x))
  ok <- !is.na(x)
  if (any(ok & !is.finite(x))) fail("a number that is not finite cannot be a group value")
  whole <- ok & x == round(x)
  out[whole] <- sprintf("%.0f", x[whole])
  out[ok & x == 0] <- "0"
  todo <- which(ok & !whole)
  for (digits in 1:17) {
    if (length(todo) == 0) break
    texts <- sprintf("%.*g", digits, x[todo])
    found <- numbers_of(texts) == x[todo]
    out[todo[found]] <- texts[found]
    todo <- todo[!found]
  }
  if (length(todo) > 0) fail("a number has no decimal text of 17 digits that reads back")
  out
}

# The numbers a condition compares a number column with (rule I3). ARS writes
# every value as text; a number is written as in JSON: an optional minus sign,
# digits without a leading zero, an optional fraction, an optional exponent.
NUMBER_TEXT <- "^-?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?$"

condition_numbers <- function(wanted) {
  if (length(wanted) == 0 || !is.character(wanted) || !all(grepl(NUMBER_TEXT, wanted))) {
    fail("a number column is compared with ", paste(wanted, collapse = ", "),
         "; a number is written as in JSON")
  }
  numbers <- numbers_of(wanted)
  if (!all(is.finite(numbers))) {
    fail("a number column is compared with ", paste(wanted, collapse = ", "),
         ", which is not a finite number")
  }
  numbers
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
