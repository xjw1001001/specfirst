"""The static check of a recomputation script (ADR-021, decision 5).

Per script, on its syntax tree (Python) or on the tokens of R's own parser:

- Python: its imports, the builtins it names and the attributes it takes are
  in allow-lists, and it names no dunder; R: its calls are in an allow-list,
  it names nothing that runs other code (source, eval, get, ...), calls no
  string and hands no string to apply or sapply, and uses no qualified
  function or file.path as a value.
- Its only reads are of the ADaM datasets of its plan, in the folder of its
  first argument, in one fixed form: `pd.read_parquet(adam / "<d>.parquet")`
  with `adam` bound once to `Path(sys.argv[1])`, or
  `utils::read.csv(file.path(adam, "<d>.csv"), ...)` with `adam <- args[1]`.
- No text holds a path, "..", a file name other than those datasets, or a
  number; every number is one the ARS states for the analysis or one of a
  few small constants.

What it holds is the form of the scripts, the routes we know: a script that
computes an ARD number from the allowed constants, or a route not listed
here, passes it. It is a check of generated code, not a proof; the scripts
are short so that a statistician can read them.
"""

from __future__ import annotations

import ast
import csv
import io
import subprocess
from pathlib import Path

PY_IMPORTS = {"sys": None, "itertools": {"product"}, "pathlib": {"Path"}, "numpy": None,
              "pandas": None, "scipy": {"stats"}}
# The builtins a script may name; any other name must be bound in the script itself.
PY_BUILTINS = {"abs", "all", "any", "bool", "dict", "enumerate", "float", "int", "len", "list",
               "map", "max", "min", "object", "range", "repr", "set", "sorted", "str", "sum",
               "tuple", "zip"}
# The attributes a script may take: those of the templates (pywrite) and nothing else.
PY_ATTRIBUTES = {
    "DataFrame", "all", "append", "argv", "array", "chi2_contingency", "dropna", "f_oneway",
    "fillna", "index", "isin", "items", "loc", "max", "mean", "min", "nunique", "pvalue",
    "quantile", "read_parquet", "shape", "sort", "std", "sum", "to_csv", "to_numpy", "tolist",
    "values"}
# The one binding of the data folder, and the one form of a read.
PY_ADAM = "adam, out = Path(sys.argv[1]), sys.argv[2]"
PY_ADAM_TREE = ast.dump(ast.parse(PY_ADAM).body[0])
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
R_APPLY = {"apply", "sapply"}  # their function argument may be no string (R looks a name up)
R_AS_VALUE = {"file.path", "commandArgs"}  # functions that must not be handed on as a value
R_OPEN = {"(", "[", "{"}
R_CLOSE = {")", "]", "}"}
R_TOKENS = """
files <- commandArgs(trailingOnly = TRUE)
for (f in files) {
  d <- utils::getParseData(parse(f, keep.source = TRUE))
  d <- d[d$terminal, c("token", "text")]
  utils::write.csv(cbind(file = f, d), stdout(), row.names = FALSE)
}
"""


def text_problem(text: str, datasets: list[str], suffix: str, allowed: set[float]
                 ) -> str | None:
    """A text constant holds no path, no parent folder, no other file and no number."""
    if "/" in text or "\\" in text:
        return f"a path in the text {text!r}"
    if ".." in text:
        return f"a parent folder in the text {text!r}"
    if text.lower().endswith(FILE_LIKE) and text not in {f"{d}{suffix}" for d in datasets}:
        return f"a file other than the ADaM datasets of the plan: {text!r}"
    try:
        number = float(text)
    except ValueError:
        return None
    if number not in allowed:
        return f"the number {text!r} in a text, which the ARS does not state for the analysis"
    return None


def bound_names(tree: ast.AST) -> set[str]:
    """The names a Python script binds itself: assignments, loop and comprehension targets,
    arguments, functions and imports."""
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            found.add(node.id)
        elif isinstance(node, ast.arg):
            found.add(node.arg)
        elif isinstance(node, ast.FunctionDef):
            found.add(node.name)
        elif isinstance(node, ast.alias):
            found.add((node.asname or node.name).split(".")[0])
    return found


def python_read(node: ast.Call, files: set[str]) -> bool:
    """`<frame>.read_parquet(adam / "<dataset>.parquet")`, the one form of a read."""
    if node.keywords or len(node.args) != 1:
        return False
    arg = node.args[0]
    return isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Div) and \
        isinstance(arg.left, ast.Name) and arg.left.id == "adam" and \
        isinstance(arg.right, ast.Constant) and arg.right.value in files


def python_problems(text: str, datasets: list[str], numbers: set[float]) -> list[str]:
    problems: list[str] = []
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        return [f"not Python: {error}"]
    allowed = SMALL | numbers
    files = {f"{d.lower()}.parquet" for d in datasets}
    bound = bound_names(tree)
    parent = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}

    def statement(node: ast.AST) -> ast.AST:
        while not isinstance(node, ast.stmt):
            node = parent[node]
        return node

    for node in ast.walk(tree):
        line = f"line {getattr(node, 'lineno', '?')}"
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in PY_IMPORTS or (PY_IMPORTS[top] is not None and alias.name != top):
                    problems.append(f"{line}: import {alias.name}")
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names = PY_IMPORTS.get(module, set()) if module in PY_IMPORTS else set()
            if module not in PY_IMPORTS or node.level or names is None or \
                    any(alias.name not in names for alias in node.names):
                problems.append(f"{line}: from {module} import "
                                + ", ".join(a.name for a in node.names))
        elif isinstance(node, ast.Name):
            if node.id.startswith("__"):
                problems.append(f"{line}: the name {node.id}")
            elif isinstance(node.ctx, ast.Load) and node.id not in bound | PY_BUILTINS:
                problems.append(f"{line}: the name {node.id}")
            elif node.id == "adam":
                if isinstance(node.ctx, ast.Store):
                    if ast.dump(statement(node)) != PY_ADAM_TREE:
                        problems.append(f"{line}: the data folder bound otherwise than "
                                        f"`{PY_ADAM}`")
                elif not (isinstance(parent[node], ast.BinOp) and
                          isinstance(parent[parent[node]], ast.Call) and
                          isinstance(parent[parent[node]].func, ast.Attribute) and
                          parent[parent[node]].func.attr == "read_parquet" and
                          python_read(parent[parent[node]], files)):
                    problems.append(f"{line}: the data folder used otherwise than in a read "
                                    "of a dataset of the plan")
        elif isinstance(node, ast.Attribute):
            if node.attr not in PY_ATTRIBUTES:
                problems.append(f"{line}: the attribute {node.attr}")
            elif node.attr == "read_parquet" and not (
                    isinstance(parent[node], ast.Call) and parent[node].func is node and
                    python_read(parent[node], files)):
                problems.append(f"{line}: a read other than `adam / \"<dataset>.parquet\"` of "
                                "a dataset of the plan")
        elif isinstance(node, ast.Constant):
            value = node.value
            if isinstance(value, str):
                found = text_problem(value, datasets, ".parquet", allowed)
                if found:
                    problems.append(f"{line}: {found}")
            elif isinstance(value, bytes):
                problems.append(f"{line}: a bytes constant")
            elif isinstance(value, int | float) and not isinstance(value, bool) and \
                    float(value) not in allowed:
                problems.append(f"{line}: the number {value!r}, which the ARS "
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


def r_depth_one_strings(tokens: list[tuple[str, str]], start: int) -> list[str]:
    """The string constants at depth 1 of the call whose name is at `start`."""
    found, depth = [], 0
    for kind, text in tokens[start + 1:]:
        if text in R_OPEN or kind == "LBB":
            depth += 2 if kind == "LBB" else 1
        elif text in R_CLOSE:
            depth -= 1
            if depth <= 0:
                break
        elif depth == 1 and kind == "STR_CONST":
            found.append(text)
    return found


def r_problems(tokens: list[tuple[str, str]], datasets: list[str], numbers: set[float]
               ) -> list[str]:
    problems: list[str] = []
    allowed = SMALL | numbers
    files = {f"{d.lower()}.csv" for d in datasets}
    tokens = [(kind, text) for kind, text in tokens if kind != "COMMENT"]

    def at(i: int) -> tuple[str, str]:
        return tokens[i] if 0 <= i < len(tokens) else ("", "")

    for i, (token, text) in enumerate(tokens):
        if token == "ERROR":
            return [f"not R: {text}"]
        if token == "SYMBOL_PACKAGE" and text not in R_PACKAGES:
            problems.append(f"the package {text}")
        elif token in ("NS_GET", "NS_GET_INT") and at(i + 1)[0] != "SYMBOL_FUNCTION_CALL":
            problems.append(f"the function {at(i - 1)[1]}{text}{at(i + 1)[1]} used as a value")
        elif token == "SYMBOL_FUNCTION_CALL":
            qualified = i >= 2 and tokens[i - 1][0] in ("NS_GET", "NS_GET_INT")
            if qualified:
                if tokens[i - 1][0] == "NS_GET_INT" or (tokens[i - 2][1], text) not in R_QUALIFIED:
                    problems.append(f"the call {tokens[i - 2][1]}{tokens[i - 1][1]}{text}")
            elif text not in R_BASE:
                problems.append(f"the call {text}")
            if text == "read.csv" and [at(i + 1)[1], at(i + 2)[1]] != ["(", "file.path"]:
                problems.append("a read other than `read.csv(file.path(adam, ...))`")
            if text == "file.path" and not (
                    [t for _, t in tokens[i + 1:i + 4]] == ["(", "adam", ","] and
                    at(i + 4)[0] == "STR_CONST" and at(i + 4)[1][1:-1] in files and
                    at(i + 5)[1] == ")"):
                problems.append("a file other than `file.path(adam, \"<dataset>.csv\")` of a "
                                "dataset of the plan")
            if text in R_APPLY:
                for string in r_depth_one_strings(tokens, i):
                    problems.append(f"the string {string} handed to {text}")
        elif token in ("SYMBOL", "SYMBOL_FUNCTION_CALL", "SYMBOL_SUB") and text in R_FORBIDDEN:
            problems.append(f"the name {text}")
        elif token == "SYMBOL" and text in R_AS_VALUE:
            problems.append(f"the function {text} used as a value")
        elif token == "SYMBOL" and text == "adam":
            assigned = [t for _, t in tokens[i + 1:i + 6]] == ["<-", "args", "[", "1", "]"] \
                and at(i - 1)[1] not in ("$", "@")
            read = [at(i - 2)[1], at(i - 1)[1]] == ["file.path", "("]
            if not (assigned or read):
                problems.append("the data folder used otherwise than in `adam <- args[1]` and "
                                "`file.path(adam, ...)`")
        elif token == "STR_CONST":
            value = text[1:-1]
            found = text_problem(value, datasets, ".csv", allowed)
            if found:
                problems.append(found)
            if value in R_FORBIDDEN:
                problems.append(f"the function {value} named by a string")
            if at(i + 1)[1] == "(":
                problems.append(f"the call of the string {text}")
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
