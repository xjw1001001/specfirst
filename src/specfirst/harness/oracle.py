"""`specfirst ask`: the oracle of PLAN.md section 11.3 (docs/decisions/ADR-010.md, decision 3).

The reader asks with `bin/ask "<question>" --decision <entry> [--unit <unit>]`;
the wrapper runs `specfirst ask` with the run folder and the task folder.
The oracle answers from the run's copy of the kit's `gold/oracle.yaml`
(`private/oracle.json`, written by the run outside the task folder), and
only a decision that the file lists: one that has no house default and
that the documents do not state (ADR-009, decision 4). Any other decision
gets no answer. Every ask is written to the run's `asks.jsonl`, which the
scorer reads (`scorer.run(asked=...)`), and to the task's
`out/questions.jsonl`.
"""

from __future__ import annotations

import json
from pathlib import Path

from specfirst.compile.catalog import Catalog
from specfirst.gen import documents as gendocs
from specfirst.harness import task as tasks

ORACLE = "private/oracle.json"
ASKS = "asks.jsonl"
ANSWER = "Answer: {answer}"
NO_ANSWER = ("No answer. The person who knows the study answers only about a decision "
             "that has no house default and that the documents do not state.")
UNKNOWN = "No answer. The catalog has no entry '{decision}'."


def write_oracle(kit_dir: Path, run_dir: Path, canary: str) -> Path:
    """The run's copy of the answers of a kit's oracle, with its planted canary."""
    answers = [{"decision": item["decision"], "unit": item["unit"], "answer": item["answer"]}
               for item in gendocs.read_oracle(kit_dir).get("answers") or []]
    path = run_dir / ORACLE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"canary": canary, "answers": answers}, indent=1,
                               sort_keys=True) + "\n", encoding="ascii", newline="\n")
    return path


def answers(run_dir: Path) -> list[dict]:
    with open(run_dir / ORACLE, encoding="ascii") as handle:
        return json.load(handle)["answers"]


def _append(path: Path, record: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="ascii", newline="\n") as handle:
        handle.write(json.dumps(record, sort_keys=True, ensure_ascii=True) + "\n")


def read_asks(run_dir: Path) -> list[dict]:
    path = run_dir / ASKS
    if not path.is_file():
        return []
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def ask(catalog: Catalog, run_dir: Path, task_dir: Path, decision: str, question: str,
        unit: str | None = None) -> tuple[str, bool]:
    """Answer one question and log it. Returns the text the reader gets, and whether
    the oracle answered."""
    entry = catalog.entries.get(decision)
    if unit is None and entry is not None and len(entry.units) == 1:
        unit = entry.units[0]
    found = [item for item in answers(run_dir) if item["decision"] == decision
             and (item["unit"] == unit or (unit is None and entry is not None))]
    if entry is None:
        text, answered = UNKNOWN.format(decision=decision), False
    elif len(found) == 1:
        text, answered, unit = ANSWER.format(answer=found[0]["answer"]), True, found[0]["unit"]
    else:
        text, answered = NO_ANSWER, False
    logged = read_asks(run_dir)
    _append(run_dir / ASKS, {"n": len(logged) + 1, "decision": decision, "unit": unit,
                             "question": question, "answered": answered})
    _append(task_dir / tasks.OUT / "questions.jsonl",
            {"decision": decision, "unit": unit, "question": question})
    return text, answered
