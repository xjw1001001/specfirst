"""The recomputation scripts of issue #29 (ADR-021) on a toy event: generation, the static
check, the sealed run, the comparison, and the generator's independence of the engine.

No fetch cache is needed. The tests that run R are skipped when Rscript is missing.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from specfirst.recompute import common, pywrite, rwrite, static
from specfirst.recompute import run as recompute_run
from specfirst.recompute.bundle import compare
from specfirst.recompute.reading import Event, NotCovered, decisions_binding, first_sentence

PACKAGE = Path(__file__).resolve().parents[2] / "src" / "specfirst" / "recompute"
HAVE_R = shutil.which("Rscript") is not None

REGISTRY = json.loads((Path(__file__).resolve().parents[2] / "standard" / "methods"
                       / "registry.json").read_text(encoding="ascii"))["methods"]


def cond(dataset, variable, comparator, *values):
    return {"condition": {"dataset": dataset, "variable": variable, "comparator": comparator,
                          "value": list(values)}}


def toy_event() -> dict:
    arm = [{"id": f"Arm_{a}", "name": a, "order": i, **cond("ADSL", "ARM", "EQ", a)}
           for i, a in enumerate(("A", "B"), start=1)]
    sex = [{"id": f"Sex_{s}", "name": s, "order": i, **cond("ADSL", "SEX", "EQ", s)}
           for i, s in enumerate(("M", "F"), start=1)]
    return {
        "id": "toy", "analysisSets": [{"id": "Set", "name": "Safety", **cond("ADSL", "SAFFL",
                                                                             "EQ", "Y")}],
        "dataSubsets": [{"id": "Old", "name": "60 or more", **cond("ADSL", "AGE", "GE", "60")}],
        "analysisGroupings": [
            {"id": "G_Arm", "name": "Arm", "groupingDataset": "ADSL", "groupingVariable": "ARM",
             "dataDriven": False, "groups": arm},
            {"id": "G_Sex", "name": "Sex", "groupingDataset": "ADSL", "groupingVariable": "SEX",
             "dataDriven": False, "groups": sex},
            {"id": "G_Race", "name": "Race", "groupingDataset": "ADSL",
             "groupingVariable": "RACE", "dataDriven": True},
        ],
        "methods": [
            {"id": "M_N", "description": "Method registry: count.subjects",
             "operations": [{"id": "M_N_1", "name": "Count of subjects", "order": 1}]},
            {"id": "M_Cat", "description": "by names (rule B3)", "operations": [
                {"id": "M_Cat_1", "name": "Count of subjects", "order": 1},
                {"id": "M_Cat_2", "name": "Percent of subjects", "order": 2,
                 "referencedOperationRelationships": [
                     {"id": "M_Cat_2_NUM", "referencedOperationRole": {"controlledTerm":
                                                                      "NUMERATOR"},
                      "operationId": "M_Cat_1"},
                     {"id": "M_Cat_2_DEN", "referencedOperationRole": {"controlledTerm":
                                                                      "DENOMINATOR"},
                      "operationId": "M_N_1"}]}]},
            {"id": "M_Sum", "description": "Method registry: summary.continuous", "operations": [
                {"id": f"M_Sum_{i}", "name": name, "order": i} for i, name in enumerate(
                    ("Count of non-missing values", "Mean", "Standard deviation", "Median",
                     "First quartile", "Third quartile", "Minimum", "Maximum"), start=1)]},
            {"id": "M_Chi", "description": "Method registry: test.chisq",
             "operations": [{"id": "M_Chi_1", "name": "P-value", "order": 1}]},
        ],
        "analyses": [
            {"id": "An_N", "name": "N", "dataset": "ADSL", "variable": "USUBJID",
             "analysisSetId": "Set", "methodId": "M_N",
             "orderedGroupings": [{"order": 1, "groupingId": "G_Arm", "resultsByGroup": True}]},
            {"id": "An_Sex", "name": "Sex", "dataset": "ADSL", "variable": "USUBJID",
             "analysisSetId": "Set", "methodId": "M_Cat",
             "orderedGroupings": [{"order": 1, "groupingId": "G_Arm", "resultsByGroup": True},
                                  {"order": 2, "groupingId": "G_Sex", "resultsByGroup": True}],
             "referencedAnalysisOperations": [
                 {"referencedOperationRelationshipId": "M_Cat_2_NUM", "analysisId": "An_Sex"},
                 {"referencedOperationRelationshipId": "M_Cat_2_DEN", "analysisId": "An_N"}]},
            {"id": "An_Race", "name": "Race", "dataset": "ADSL", "variable": "USUBJID",
             "analysisSetId": "Set", "dataSubsetId": "Old", "methodId": "M_N",
             "orderedGroupings": [{"order": 1, "groupingId": "G_Arm", "resultsByGroup": True},
                                  {"order": 2, "groupingId": "G_Race", "resultsByGroup": True}]},
            {"id": "An_Age", "name": "Age", "dataset": "ADSL", "variable": "AGE",
             "analysisSetId": "Set", "methodId": "M_Sum",
             "orderedGroupings": [{"order": 1, "groupingId": "G_Arm", "resultsByGroup": True}],
             "programmingCode": {"context": "specfirst method registry", "parameters": [
                 {"name": "quantile_definition", "value": ["r7"]}]}},
            {"id": "An_Chi", "name": "Arm by sex", "dataset": "ADSL", "variable": "USUBJID",
             "analysisSetId": "Set", "methodId": "M_Chi",
             "orderedGroupings": [{"order": 1, "groupingId": "G_Arm", "resultsByGroup": False},
                                  {"order": 2, "groupingId": "G_Sex", "resultsByGroup": False}]},
        ],
    }


ADSL = {
    "USUBJID": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"],
    "SAFFL": ["Y", "Y", "Y", "Y", "Y", "Y", "Y", "N", None],
    "ARM": ["A", "A", "A", "B", "B", "B", "B", "A", "B"],
    "SEX": ["M", "F", "F", "M", "M", "F", "M", "M", "F"],
    "RACE": ["W", "", "B", "W", "W", None, "B", "W", "W"],
    "AGE": [70.0, 55.0, 61.0, 64.0, None, 80.0, 59.0, 66.0, 71.0],
}
TYPES = {"USUBJID": "text", "SAFFL": "text", "ARM": "text", "SEX": "text", "RACE": "text",
         "AGE": "number"}


def types(dataset: str, column: str) -> str:
    return TYPES.get(column, "absent") if dataset == "ADSL" else "absent"


@pytest.fixture
def event() -> Event:
    return Event(toy_event(), "toy", REGISTRY, {})


def write(event: Event, analysis_id: str, decisions: list[dict] | None = None) -> str:
    analysis = event.analysis(analysis_id)
    writer = pywrite.PyWriter(analysis, "toykit", REGISTRY,
                              common.Decisions(by_element=decisions_binding(decisions or [])),
                              types, "USUBJID", {"pandas": "x", "numpy": "y", "scipy": "z"},
                              event.analysis)
    return writer.write()[0]


def run_python(tmp_path: Path, text: str) -> dict[tuple[str, ...], str]:
    adam = tmp_path / "adam"
    adam.mkdir(exist_ok=True)
    pq.write_table(pa.table(ADSL), adam / "adsl.parquet")
    script, out = tmp_path / "script.py", tmp_path / "out.csv"
    script.write_text(text, encoding="ascii")
    shutil.copyfile(PACKAGE / "seal.py", tmp_path / "seal.py")
    done = subprocess.run([sys.executable, "-I", str(tmp_path / "seal.py"), str(script),
                           str(adam), str(out)], capture_output=True, text=True, cwd=tmp_path)
    assert done.returncode == 0, done.stderr
    lines = out.read_text(encoding="ascii").splitlines()[1:]
    return {tuple(line.split(",")[:-1]): line.split(",")[-1] for line in lines}


def test_binding_and_options(event):
    sex = event.analysis("An_Sex")
    assert [(op.method, op.operation) for op in sex.operations] == [
        ("count.subjects", "n"), ("percent.subjects", "pct")]  # rule B3
    assert sex.operations[1].denominator == ("An_N", "M_N_1")
    age = event.analysis("An_Age")
    assert age.options["summary.continuous"]["quantile_definition"] == "r7"
    assert age.option_sources["summary.continuous"]["quantile_definition"] == \
        "the analysis's programmingCode"
    bound = Event(toy_event(), "toy", REGISTRY, {"options": {"summary.continuous": {
        "quantile_definition": "sas5"}}})
    assert bound.analysis("An_N").options == {"count.subjects": {}}
    data = toy_event()
    data["analyses"][3]["programmingCode"]["parameters"][0]["value"] = ["r9"]
    with pytest.raises(NotCovered):
        Event(data, "toy", REGISTRY, {}).analysis("An_Age")


def test_first_sentence():
    assert first_sentence("The set is A. Then more. ") == "The set is A."
    assert first_sentence("No stop") == "No stop"


def test_count_and_percent(event, tmp_path):
    rows = run_python(tmp_path, write(event, "An_Sex"))
    # Safety: S1..S7; arm A: S1 M, S2 F, S3 F; arm B: S4 M, S5 M, S6 F, S7 M.
    assert rows[("M_Cat_1", "Arm_A", "Sex_M")] == "1.0"
    assert rows[("M_Cat_1", "Arm_B", "Sex_M")] == "3.0"
    assert float(rows[("M_Cat_2", "Arm_A", "Sex_F")]) == 100 * 2 / 3
    assert float(rows[("M_Cat_2", "Arm_B", "Sex_F")]) == 25.0
    assert len(rows) == 8


def test_data_driven_and_subset(event, tmp_path):
    rows = run_python(tmp_path, write(event, "An_Race"))
    # Age 60 or more and safety: S1 (A, W), S3 (A, B), S4 (B, W), S6 (B, missing race).
    assert rows == {("M_N_1", "Arm_A", "=B"): "1.0", ("M_N_1", "Arm_A", "=W"): "1.0",
                    ("M_N_1", "Arm_B", "=B"): "0.0", ("M_N_1", "Arm_B", "=W"): "1.0"}


def test_summary_r7(event, tmp_path):
    rows = run_python(tmp_path, write(event, "An_Age"))
    # Arm A: 70, 55, 61; arm B: 64, 80, 59 (S5 missing).
    assert rows[("M_Sum_1", "Arm_A")] == "3.0"
    assert float(rows[("M_Sum_5", "Arm_A")]) == 58.0  # r7: 55 + 0.5 * (61 - 55)
    assert float(rows[("M_Sum_6", "Arm_B")]) == 72.0  # r7: 64 + 0.5 * (80 - 64)
    assert float(rows[("M_Sum_4", "Arm_B")]) == 64.0


def test_chisq(event, tmp_path):
    from scipy import stats

    rows = run_python(tmp_path, write(event, "An_Chi"))
    expected = stats.chi2_contingency([[1, 2], [3, 1]], correction=False).pvalue
    assert float(rows[("M_Chi_1", "*", "*")]) == pytest.approx(expected, rel=1e-15)


def test_decision_comments(event):
    records = [{"id": "custom:toy-set", "status": "stated", "binds": ["ars:Set", "ars:G_Arm"],
                "statement": "The safety set is SAFFL = Y. A second sentence."}]
    text = write(event, "An_N", records)
    assert "# custom:toy-set (stated): The safety set is SAFFL = Y." in text
    assert "A second sentence" not in text
    assert text.count("custom:toy-set (stated)") == 1  # above the first step it binds
    assert "decision custom:toy-set" in text  # named again at the grouping


PY_HEAD = ("import sys\nfrom pathlib import Path\n\nimport numpy as np\nimport pandas as pd\n\n"
           "adam, out = Path(sys.argv[1]), sys.argv[2]\n"
           "adsl = pd.read_parquet(adam / 'adsl.parquet')\n")


def test_static_check_python():
    allowed = {54.0}
    good = PY_HEAD + ("y = len(adsl) + 54\nz = np.sort(np.array([1, 2]))\n"
                      "pd.DataFrame([], columns=['v'], dtype=object).to_csv(out, index=False)\n")
    assert static.python_problems(good, ["adsl"], allowed) == []
    planted = {
        "import specfirst": "import specfirst\n",
        "from specfirst.machine import ard": "from specfirst.machine import ard\n",
        "open": "data = open('x')\n",
        "a path": "p = 'build/kits/x'\n",
        "the ARD": "p = 'efficacy-adas.jsonl'\n",
        "another dataset": "x = pd.read_parquet(adam / 'adae.parquet')\n",
        "a pasted number": "x = 2.3290884\n",
        "exec": "exec('1')\n",
        "walking up": "p = Path(sys.argv[1]).parent\n",
        "another reader": "x = pd.read_csv('adsl.csv')\n",
        "importlib": "import importlib\n",
        # the routes of the review of issue #29, pass 1 (F1)
        "a number in a text": "x = float('2.3290884')\n",
        "a parent folder": "x = pd.read_parquet(adam / '..' / 'adsl.parquet')\n",
        "the root": "r = Path(sys.argv[1]).anchor\n",
        "__builtins__": "__builtins__['exec']('1')\n",
        "a separator from chr": "s = chr(ord('0') - 1)\n",
        "memmap": "x = np.memmap(adam / 'adsl.parquet')\n",
        "pandas.eval": "x = pd.eval('1 + 1')\n",
        "a file name in two parts": "p = adam / ('efficacy-adas.js' + 'onl')\n",
        "the data folder bound again": "adam = Path(sys.argv[2])\n",
        "the data folder handed on": "p = adam\n",
        "__file__": "p = __file__\n",
        "a bytes path": "p = b'x'\n",
        "a read with options": "x = pd.read_parquet(adam / 'adsl.parquet', filesystem=None)\n",
    }
    for name, text in planted.items():
        assert static.python_problems(PY_HEAD + text, ["adsl"], allowed), name


def test_static_check_r_tokens():
    good = [("SYMBOL_PACKAGE", "stats"), ("NS_GET", "::"), ("SYMBOL_FUNCTION_CALL", "lm"),
            ("STR_CONST", '"adsl.csv"'), ("NUM_CONST", "95"), ("NUM_CONST", "TRUE")]
    assert static.r_problems(good, ["adsl"], {95.0}) == []
    planted = {
        "source": [("SYMBOL_FUNCTION_CALL", "source"), ("STR_CONST", '"models.R"')],
        "a package": [("SYMBOL_PACKAGE", "specfirstr"), ("NS_GET", "::"),
                      ("SYMBOL_FUNCTION_CALL", "run")],
        "an unknown call": [("SYMBOL_FUNCTION_CALL", "readLines")],
        "do.call": [("SYMBOL", "do.call")],
        "a path": [("STR_CONST", '"/mnt/d/x"')],
        "a pasted number": [("NUM_CONST", "1.7352")],
        "an internal call": [("SYMBOL_PACKAGE", "stats"), ("NS_GET_INT", ":::"),
                             ("SYMBOL_FUNCTION_CALL", "lm")],
        "an escape": [("STR_CONST", '"\\x2e\\x2e"')],
    }
    for name, tokens in planted.items():
        assert static.r_problems(tokens, ["adsl"], {95.0}), name


R_HEAD = ('args <- commandArgs(trailingOnly = TRUE)\nadam <- args[1]\n'
          'adsl <- utils::read.csv(file.path(adam, "adsl.csv"), colClasses = "character", '
          'na.strings = "")\n')


@pytest.mark.skipif(not HAVE_R, reason="Rscript is not installed")
def test_static_check_r_parse(tmp_path):
    good = R_HEAD + ('x <- sapply(adsl$AGE, function(v) as.numeric(v) + 95)\n'
                     'utils::write.csv(data.frame(value = x), args[2], row.names = FALSE)\n')
    planted = {
        "source": 'source("y.R")\n',
        # the routes of the review of issue #29, pass 1 (F1)
        "a function named by a string, handed to sapply": 'x <- sapply("y.R", "source")\n',
        "a string handed to apply": 'x <- apply(adsl, 1, "print")\n',
        "a call of a string": '"source"("y.R")\n',
        "a number in a text": 'x <- as.numeric("1.7352")\n',
        "the ARD from the root": 'd <- utils::read.csv(file.path("", "tmp", "e.jsonl"))\n',
        "a read of another dataset": 'd <- utils::read.csv(file.path(adam, "adae.csv"))\n',
        "a read without file.path": 'd <- utils::read.csv(args[1])\n',
        "a reader as a value": 'f <- utils::read.csv\n',
        "file.path as a value": 'f <- file.path\n',
        "the data folder walked up": 'adam <- dirname(args[1])\n',
        "the data folder bound again": 'adam <- args[2]\n',
        "the data folder handed on": 'p <- paste0(adam, "x")\n',
        "a parent folder": 'p <- c("..", "x")\n',
    }
    paths = [tmp_path / "good.R"]
    paths[0].write_text(good, encoding="ascii")
    for i, text in enumerate(planted.values()):
        paths.append(tmp_path / f"p{i}.R")
        paths[-1].write_text(R_HEAD + text, encoding="ascii")
    tokens = static.r_tokens(paths)
    assert static.r_problems(tokens[str(paths[0])], ["adsl"], {95.0}) == []
    for name, path in zip(planted, paths[1:], strict=True):
        assert static.r_problems(tokens[str(path)], ["adsl"], {95.0}), name


def test_seal_refuses_the_engine(tmp_path):
    shutil.copyfile(PACKAGE / "seal.py", tmp_path / "seal.py")
    (tmp_path / "bad.py").write_text("import specfirst\n", encoding="ascii")
    (tmp_path / "good.py").write_text("import sys\nprint(sys.argv[1])\n", encoding="ascii")
    run = [sys.executable, "-I", str(tmp_path / "seal.py")]
    bad = subprocess.run([*run, str(tmp_path / "bad.py")], capture_output=True, text=True)
    assert bad.returncode != 0 and "refused by the sealed run" in bad.stderr
    good = subprocess.run([*run, str(tmp_path / "good.py"), "hello"], capture_output=True,
                          text=True)
    assert good.returncode == 0 and good.stdout.strip() == "hello"
    # The review of issue #29, pass 1 (F1): the hook of meta_path removed before the import;
    # the audit hook still refuses it.
    (tmp_path / "past.py").write_text(
        "import sys\nsys.meta_path[:] = [f for f in sys.meta_path\n"
        "                 if type(f).__name__ != 'Refuse']\nimport specfirst\n",
        encoding="ascii")
    past = subprocess.run([*run, str(tmp_path / "past.py")], capture_output=True, text=True)
    assert past.returncode != 0 and "refused by the sealed run" in past.stderr
    # An open by Python in a fenced folder is refused; outside it, it is not.
    fenced, free = tmp_path / "checkout", tmp_path / "data"
    for folder in (fenced, free):
        folder.mkdir()
        (folder / "x.txt").write_text("x\n", encoding="ascii")
    (tmp_path / "read.py").write_text("import sys\nprint(open(sys.argv[1]).read().strip())\n",
                                      encoding="ascii")
    env = {"PATH": os.environ.get("PATH", ""), "SPECFIRST_SEAL_FENCE": str(fenced)}
    inside = subprocess.run([*run, str(tmp_path / "read.py"), str(fenced / "x.txt")],
                            capture_output=True, text=True, env=env)
    assert inside.returncode != 0 and "refused by the sealed run: an open" in inside.stderr
    outside = subprocess.run([*run, str(tmp_path / "read.py"), str(free / "x.txt")],
                             capture_output=True, text=True, env=env)
    assert outside.returncode == 0 and outside.stdout.strip() == "x"


def test_compare(tmp_path):
    bundle, outputs, ard = tmp_path / "b", tmp_path / "o", tmp_path / "a"
    for folder in (bundle, outputs / "e", ard):
        folder.mkdir(parents=True)
    ops = {"N": {"result": "integer"}, "P": {"result": "number"}}
    entries = [{"analysis": name, "event": "e", "groupings": ["G"], "operations": ops,
                "tolerance": 1e-9} for name in ("Ok", "Off", "Lost", "More", "None")]
    entries.append({"analysis": "Skip", "event": "e", "not_covered": "no template"})
    (bundle / "plan.json").write_text(json.dumps({"kit": "k", "analyses": entries}),
                                      encoding="ascii")
    rows = []
    for name in ("Ok", "Off", "Lost", "More", "None"):
        rows += [{"analysis_id": name, "operation_id": "N", "group1_groupId": "A",
                  "raw_value": 3},
                 {"analysis_id": name, "operation_id": "P", "group1_groupValue": "x y",
                  "raw_value": 0.123456789}]
    (ard / "e.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="ascii")
    head = "operation_id,group1,value\n"
    (outputs / "e" / "Ok.csv").write_text(head + "N,A,3.0\nP,=x y,0.12345678900000001\n",
                                          encoding="ascii")
    (outputs / "e" / "Off.csv").write_text(head + "N,A,3.0\nP,=x y,0.1234567901\n",
                                           encoding="ascii")
    (outputs / "e" / "Lost.csv").write_text(head + "N,A,3.0\n", encoding="ascii")
    (outputs / "e" / "More.csv").write_text(head + "N,A,3.0\nP,=x y,0.123456789\nN,B,1\n",
                                            encoding="ascii")
    report = compare.compare(bundle, outputs, ard)
    status = {line["analysis"]: line["status"] for line in report["analyses"]}
    assert status == {"Ok": "reproduced", "Off": "differs", "Lost": "differs",
                      "More": "differs", "None": "differs", "Skip": "not covered"}
    assert report["counts"] == {"reproduced": 1, "differs": 4, "not covered": 1}
    assert any("script 0.1234567901" in line for line in compare.text_lines(report))


def test_compare_vacuous_and_failed(tmp_path):
    """The review of issue #29, pass 1: F2 (no ARD row; ARD rows of more groupings than the
    plan reads; two ARD rows of one key), F3 (a script that failed after its output) and F4
    (the absolute 1e-12 only where the ARD's value is 0)."""
    bundle, outputs, ard = tmp_path / "b", tmp_path / "o", tmp_path / "a"
    for folder in (bundle, outputs / "e", ard):
        folder.mkdir(parents=True)
    ops = {"P": {"result": "number"}}
    names = ("Empty", "Wide", "Twice", "Failed", "Tiny", "Zero")
    entries = [{"analysis": n, "event": "e", "groupings": ["G"], "operations": ops,
                "tolerance": 1e-9} for n in names]
    evidence = [{"evidence": "E9", "table": "T", "where": "not built"}]
    (bundle / "plan.json").write_text(json.dumps({"kit": "k", "analyses": entries,
                                                  "evidence": evidence}), encoding="ascii")
    rows = [
        {"analysis_id": "Wide", "operation_id": "P", "group1_groupId": "A",
         "group2_groupingId": "G2", "group2_groupId": "X", "raw_value": 1.5},
        {"analysis_id": "Wide", "operation_id": "P", "group1_groupId": "A",
         "group2_groupingId": "G2", "group2_groupId": "Y", "raw_value": 1.5},
        {"analysis_id": "Twice", "operation_id": "P", "group1_groupId": "A", "raw_value": 1.5},
        {"analysis_id": "Twice", "operation_id": "P", "group1_groupId": "A", "raw_value": 1.5},
        {"analysis_id": "Failed", "operation_id": "P", "group1_groupId": "A", "raw_value": 1.5},
        {"analysis_id": "Tiny", "operation_id": "P", "group1_groupId": "A", "raw_value": 1e-13},
        {"analysis_id": "Zero", "operation_id": "P", "group1_groupId": "A", "raw_value": 0.0},
    ]
    (ard / "e.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="ascii")
    head = "operation_id,group1,value\n"
    (outputs / "e" / "Empty.csv").write_text(head, encoding="ascii")
    for name in ("Wide", "Twice", "Failed"):
        (outputs / "e" / f"{name}.csv").write_text(head + "P,A,1.5\n", encoding="ascii")
    (outputs / "e" / "Failed.failed").write_text("exit 3\n", encoding="ascii")
    (outputs / "e" / "Tiny.csv").write_text(head + "P,A,9e-13\n", encoding="ascii")
    (outputs / "e" / "Zero.csv").write_text(head + "P,A,1e-15\n", encoding="ascii")
    report = compare.compare(bundle, outputs, ard)
    status = {line["analysis"]: line["status"] for line in report["analyses"]}
    assert status == {"Empty": "differs", "Wide": "differs", "Twice": "differs",
                      "Failed": "differs", "Tiny": "differs", "Zero": "reproduced"}
    reasons = {line["analysis"]: line.get("reason", "") for line in report["analyses"]}
    assert "no row" in reasons["Empty"] and "more groupings" in reasons["Wide"]
    assert "two ARD rows" in reasons["Twice"] and "the script failed: exit 3" in reasons["Failed"]
    assert compare.text_lines(report)[-1] == "E9 T: not built"


def test_generator_is_independent_of_the_engine():
    """The generator and the bundle's files import nothing of the engine (ADR-021)."""
    assert static.generator_problems(PACKAGE) == []
    planted = PACKAGE.parent / "machine" / "build.py"  # an engine module, read as a plant
    assert static.import_problems(planted, bundle=False)


def test_writers_refuse_what_they_do_not_cover(event):
    data = toy_event()
    data["analyses"][0]["orderedGroupings"][0]["resultsByGroup"] = False
    analysis = Event(data, "toy", REGISTRY, {}).analysis("An_N")
    writer = pywrite.PyWriter(analysis, "k", REGISTRY, common.Decisions(), types, "USUBJID", {},
                              event.analysis)
    with pytest.raises(NotCovered):
        writer.write()
    with pytest.raises(NotCovered):
        rwrite.RWriter(event.analysis("An_N"), "k", REGISTRY, common.Decisions(), types,
                       "USUBJID", {}).write()


def test_sealed_environment(tmp_path):
    env = recompute_run.sealed_env(tmp_path)
    assert set(env) <= {"PATH", "HOME", "TMPDIR", "LC_ALL", "LANG", "OMP_NUM_THREADS",
                        "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "R_LIBS_USER"}
    assert not any(key.startswith(("SPECFIRST", "PYTHON")) for key in env)
    fenced = recompute_run.sealed_env(tmp_path, fence=(tmp_path / "a", tmp_path / "b"))
    assert fenced["SPECFIRST_SEAL_FENCE"].split(os.pathsep) == \
        [str((tmp_path / "a").resolve()), str((tmp_path / "b").resolve())]
