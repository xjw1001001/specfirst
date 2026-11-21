"""The static check that a recomputation script calls no part of the engine (ADR-021, decision 5).

Per script: its imports (Python) or calls (R) are in an allow-list; nothing
that runs other code (exec, eval, source, system, ...), reads another kind of
file or walks the file system; no path in a text; the only files it names are
the ADaM datasets of its plan; and every number in it is a number the ARS
states for the analysis or one of a few small constants. So no line of the
engine and no number of the ARD can stand in a script.
"""

from __future__ import annotations

import ast
import csv
import io
import subprocess
from pathlib import Path

PY_IMPORTS = {"sys": None, "itertools": {"product"}, "pathlib": {"Path"}, "numpy": None,
              "pandas": None, "scipy": {"stats"}}
PY_NAMES = {"exec", "eval", "compile", "open", "__import__", "getattr", "setattr", "delattr",
            "globals", "locals", "vars", "input", "breakpoint", "help", "exit", "quit",
            "memoryview", "classmethod", "staticmethod", "type", "super"}
PY_ATTRIBUTES = {
    # other readers and writers than the Parquet reader and the CSV of the output
    "read_csv", "read_json", "read_pickle", "read_table", "read_excel", "read_sql",
    "read_fwf", "read_html", "read_xml", "read_feather", "read_orc", "read_sas",
    "read_spss", "read_stata", "read_hdf", "read_clipboard", "load", "loadtxt", "genfromtxt",
    "fromfile", "to_pickle", "to_parquet", "to_json", "tofile", "save", "savez",
    # walking the file system
    "parent", "parents", "resolve", "absolute", "cwd", "home", "glob", "rglob", "iterdir",
    "expanduser", "joinpath", "with_name", "read_text", "read_bytes", "open", "readlink",
    # the interpreter's insides
    "system", "popen", "modules", "path", "meta_path", "__dict__", "__globals__",
    "__builtins__", "__subclasses__", "__getattribute__", "__code__", "__class__", "f_globals"}
SMALL = {0.0, 1.0, 2.0, 100.0, 0.25, 0.5, 0.75, float("inf")}  # inf: R's Inf, no data
FILE_LIKE = (".parquet", ".csv", ".json", ".jsonl", ".py", ".r", ".txt", ".yaml", ".yml", ".rds",
             ".rdata", ".xpt", ".sas7bdat")

R_PACKAGES = {"utils", "stats", "emmeans", "mmrm", "coin"}
R_QUALIFIED = {("utils", "read.csv"), ("utils", "write.csv"), ("stats", "complete.cases"),
               ("stats", "fisher.test"), ("stats", "lm"), ("stats", "pnorm"),
               ("emmeans", "emmeans"), ("emmeans", "contrast"), ("coin", "cmh_test"),
               ("coin", "pvalue"), ("mmrm", "mmrm"), ("mmrm", "mmrm_control")}
R_BASE = {"commandArgs", "file.path", "as.numeric", "ifelse", "is.na", "sprintf", "cbind",
          "stopifnot", "all", "rowSums", "factor", "apply", "colnames", "levels", "unique",
          "order", "data.frame", "sapply", "seq_len", "nrow", "colSums", "rbind", "min", "dim",
          "any", "stop", "paste0", "anyDuplicated", "interaction", "names", "which", "table",
          "droplevels", "sort", "length", "nlevels", "list", "match", "summary", "update",
          "as.data.frame", "setdiff", "c", "us", "toep", "abs", "as.character", "return",
          "num"}  # num: the script's own writer of a number
R_FORBIDDEN = {"source", "sys.source", "eval", "evalq", "parse", "str2lang", "str2expression",
               "system", "system2", "shell", "Sys.setenv", ".libPaths", "library", "require",
               "loadNamespace", "requireNamespace", "attachNamespace", "get", "get0", "mget",
               "match.fun", "do.call", "dyn.load", "library.dynam", "readRDS", "load", "file",
               "readLines", "scan", "dirname", "normalizePath", "list.files", "setwd", "getwd",
               "Recall", "environment", "sys.function", "body", "assign", ".Internal",
               ".Call", ".External", "pipe", "url", "download.file"}
R_TOKENS = """
files <- commandArgs(trailingOnly = TRUE)
for (f in files) {
  d <- utils::getParseData(parse(f, keep.source = TRUE))
  d <- d[d$terminal, c("token", "text")]
  utils::write.csv(cbind(file = f, d), stdout(), row.names = FALSE)
}
"""


def file_problem(text: str, datasets: list[str], suffix: str) -> str | None:
    if "/" in text or "\\" in text:
        return f"a path in the text {text!r}"
    if text.lower().endswith(FILE_LIKE) and text not in {f"{d}{suffix}" for d in datasets}:
        return f"a file other than the ADaM datasets of the plan: {text!r}"
    return None


def python_problems(text: str, datasets: list[str], numbers: set[float]) -> list[str]:
    problems: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        return [f"not Python: {error}"]
    allowed = SMALL | numbers
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in PY_IMPORTS or (PY_IMPORTS[top] is not None and alias.name != top):
                    problems.append(f"line {node.lineno}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = PY_IMPORTS.get(module, set()) if module in PY_IMPORTS else set()
            if module not in PY_IMPORTS or node.level or names is None or \
                    any(alias.name not in names for alias in node.names):
                problems.append(f"line {node.lineno}: from {module} import "
                                + ", ".join(a.name for a in node.names))
        elif isinstance(node, ast.Name) and node.id in PY_NAMES:
            problems.append(f"line {node.lineno}: the name {node.id}")
        elif isinstance(node, ast.Attribute) and node.attr in PY_ATTRIBUTES:
            problems.append(f"line {node.lineno}: the attribute {node.attr}")
        elif isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, str):
                found = file_problem(value, datasets, ".parquet")
                if found:
                    problems.append(f"line {node.lineno}: {found}")
            elif isinstance(value, int | float) and not isinstance(value, bool) and \
                    float(value) not in allowed:
                problems.append(f"line {node.lineno}: the number {value!r}, which the ARS "
                                "does not state for the analysis")
    return problems


def r_tokens(paths: list[Path]) -> dict[str, list[tuple[str, str]]]:
    """The terminal tokens of R files, by file, from R's own parser."""
    done = subprocess.run(["Rscript", "--vanilla", "-e", R_TOKENS, *map(str, paths)],
                          capture_output=True, text=True, timeout=300)
    found: dict[str, list[tuple[str, str]]] = {str(p): [] for p in paths}
    if done.returncode != 0:
        for p in paths:
            found[str(p)] = [("ERROR", done.stderr.strip()[-500:])]
        return found
    for row in csv.DictReader(io.StringIO(done.stdout)):
        found.setdefault(row["file"], []).append((row["token"], row["text"]))
    return found


def r_problems(tokens: list[tuple[str, str]], datasets: list[str], numbers: set[float]
               ) -> list[str]:
    problems: list[str] = []
    allowed = SMALL | numbers
    for i, (token, text) in enumerate(tokens):
        if token == "ERROR":
            return [f"not R: {text}"]
        if token == "SYMBOL_PACKAGE" and text not in R_PACKAGES:
            problems.append(f"the package {text}")
        elif token == "SYMBOL_FUNCTION_CALL":
            qualified = i >= 2 and tokens[i - 1][0] in ("NS_GET", "NS_GET_INT")
            if qualified:
                if tokens[i - 1][0] == "NS_GET_INT" or (tokens[i - 2][1], text) not in R_QUALIFIED:
                    problems.append(f"the call {tokens[i - 2][1]}{tokens[i - 1][1]}{text}")
            elif text not in R_BASE:
                problems.append(f"the call {text}")
        elif token in ("SYMBOL", "SYMBOL_FUNCTION_CALL", "SYMBOL_SUB") and text in R_FORBIDDEN:
            problems.append(f"the name {text}")
        elif token == "STR_CONST":
            value = text[1:-1]
            found = file_problem(value, datasets, ".csv")
            if found:
                problems.append(found)
        elif token == "NUM_CONST":
            value = text.rstrip("L")
            try:
                number = float(value)
            except ValueError:
                continue  # TRUE, FALSE, NA, Inf
            if number not in allowed:
                problems.append(f"the number {text}, which the ARS does not state for the "
                                "analysis")
    for token, text in tokens:
        if token == "SYMBOL_FUNCTION_CALL" and text in R_FORBIDDEN:
            problems.append(f"the call {text}")
    return sorted(set(problems))


# What the generator may import of specfirst: the kit manifest, the paths, the canonical
# writers and itself. Nothing that computes a result (ADR-021, decision 5).
GENERATOR_IMPORTS = ("specfirst.recompute", "specfirst.kit", "specfirst.paths",
                     "specfirst.machine.canonical")


def import_problems(path: Path, bundle: bool) -> list[str]:
    """The imports of a module of the generator (bundle False: of specfirst only those of
    GENERATOR_IMPORTS) or of a standalone file (bundle True: the standard library and
    pyarrow only)."""
    import sys

    names: list[tuple[int, str]] = []
    for node in ast.walk(ast.parse(path.read_text(encoding="ascii"))):
        if isinstance(node, ast.Import):
            names += [(node.lineno, alias.name) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                names.append((node.lineno, "." * node.level + module))
            elif module == "specfirst":
                names += [(node.lineno, f"specfirst.{alias.name}") for alias in node.names
                          if alias.name != "__version__"]
            else:
                names.append((node.lineno, module))
    problems = []
    for line, name in names:
        top = name.split(".")[0]
        if bundle:
            if top not in sys.stdlib_module_names and top != "pyarrow" and \
                    name != "__future__":
                problems.append(f"{path.name}:{line}: import {name}")
        elif name.startswith(".") or (top == "specfirst" and not any(
                name == allowed or name.startswith(allowed + ".")
                for allowed in GENERATOR_IMPORTS)):
            problems.append(f"{path.name}:{line}: import {name}")
    return problems


def generator_problems(package: Path) -> list[str]:
    """specfirst/recompute imports nothing of the engine; its standalone files nothing of
    specfirst at all (seal.py, bundle/*.py)."""
    problems: list[str] = []
    for path in sorted(package.glob("*.py")):
        problems += import_problems(path, bundle=path.name == "seal.py")
    for path in sorted((package / "bundle").glob("*.py")):
        problems += import_problems(path, bundle=True)
    return problems


def check(bundle: Path, plan: dict, numbers: dict[tuple[str, str], set[float]]
          ) -> dict[str, list[str]]:
    """Problems per analysis ID (`<event>/<analysis>`); an empty list for a sound script."""
    found: dict[str, list[str]] = {}
    covered = [entry for entry in plan["analyses"] if "not_covered" not in entry]
    r_files = [bundle / e["file"] for e in covered if e["language"] == "r"]
    tokens = r_tokens(r_files) if r_files else {}
    for entry in covered:
        name = f"{entry['event']}/{entry['analysis']}"
        allowed = numbers.get((entry["event"], entry["analysis"]), set())
        path = bundle / entry["file"]
        if entry["language"] == "python":
            found[name] = python_problems(path.read_text(encoding="ascii"), entry["datasets"],
                                          allowed)
        else:
            found[name] = r_problems(tokens.get(str(path), []), entry["datasets"], allowed)
    return found
