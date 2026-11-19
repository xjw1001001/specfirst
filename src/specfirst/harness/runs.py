"""A run of an arm on a kit, and the check of a recorded run (docs/decisions/ADR-010.md).

    <runs>/<arm>-<task ID>/          the run folder, outside the task folder
      run.json                       the record (specfirst.harness.record)
      task.json                      the task: ID, stage, condition, units, decisions, manifest
      transcript.jsonl               the reader's stream-json events
      asks.jsonl                     the ask log (specfirst.harness.oracle)
      settings.json                  the deny rules the reader ran under
      private/oracle.json, private/kit.json     with their planted canaries
      workspace/                     every file of the task folder that the run wrote or
                                     changed, out/ among them

The arms of ADR-005, decision 3, on the same task and the same record:

    S   no reader: out/decisions.jsonl is empty, so every decision takes its house
        default when it is scored
    C   the parser control: the records the parser reads from the standard-form
        documents of the kit (`scorer.control_records`); what neither they nor the
        house standard state is asked of the oracle
    R   the reader, through the adapter (the Claude Code CLI, or the stub)

A run is checked when it ends: the task folder holds nothing a reader may
not see, the reader ended within its budget, the output files are valid,
and no canary is in the transcript or the workspace. `check` does the same
for a run kept in the repository, against a task built again now.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.gen import documents as gendocs
from specfirst.gen import kits as genkits
from specfirst.gen import natural
from specfirst.harness import adapter, canary, oracle, outputs, record
from specfirst.harness import task as tasks
from specfirst.machine.canonical import content_hash, json_text, sha256_file

ARMS = ("S", "R", "C")
RUN_JSON = "run.json"
TASK_JSON = "task.json"
KIT_JSON = "private/kit.json"
WORKSPACE = "workspace"
PRIVATE = (oracle.ORACLE, KIT_JSON)
HOME_DENIED = (".claude", "Desktop", "Documents", "Downloads")
TOOLS = {"ask": "Ask the person who knows the study about one decision (PLAN.md section 11.3):\n"
                "#   bin/ask \"<question>\" --decision <entry> [--unit <unit>]",
         "check": "Print every problem of the files in out/ (docs/decisions/ADR-010.md, "
                  "decision 6):\n#   bin/check"}


class RunError(RuntimeError):
    """A run cannot be made here, or of this kit."""


@dataclass
class Run:
    folder: Path
    record: dict
    hits: list[canary.Hit] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return bool(self.record.get("passed"))


def windows_home() -> Path | None:
    """The Windows user's home under /mnt, from WSL; None outside WSL."""
    try:
        done = subprocess.run(["cmd.exe", "/c", "echo %USERPROFILE%"], capture_output=True,
                              text=True, cwd="/mnt/c", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    text = done.stdout.strip()
    if len(text) > 3 and text[1:3] == ":\\":
        return Path(f"/mnt/{text[0].lower()}/" + text[3:].replace("\\", "/"))
    return None


def _under(path: Path, folder: Path) -> bool:
    return path.resolve() == folder.resolve() or folder.resolve() in path.resolve().parents


def protected_roots(root: Path, kit_dir: Path, tasks_dir: Path, runs_dir: Path,
                    seed_file: Path | None, windows: bool) -> list[Path]:
    """The folders the reader's file tools are denied on (ADR-010, decision 4)."""
    found = [kit_dir.resolve().parent, runs_dir.resolve(), natural.store_dir().resolve()]
    # Every checkout: the folder that holds them, unless the task lies in it.
    holder = root.resolve().parent
    if _under(tasks_dir, holder) or _under(runs_dir, holder):
        found.append(root.resolve())
    else:
        found.append(holder)
    if seed_file is not None:
        found.append(seed_file.resolve().parent)
    if windows:
        home = windows_home()
        if home is not None:
            # The transcripts of other sessions hold gold; the others may hold a person's
            # own files (section 2.1, rule 2).
            found += [home / name for name in HOME_DENIED]
    found += [Path(path) for path in os.environ.get("SPECFIRST_DENY", "").split(os.pathsep)
              if path]
    found = sorted(set(found), key=str)
    for path in found:
        if _under(tasks_dir, path):
            raise RunError(f"the task folder {tasks_dir} lies in the protected folder {path}")
    return found


def write_tools(task_dir: Path, run_dir: Path, windows: bool) -> None:
    """bin/ask and bin/check of a run: they call this checkout's `specfirst`."""
    prefix = []
    if windows:
        prefix = ["wsl.exe", "-d", os.environ.get("WSL_DISTRO_NAME", "Ubuntu-24.04"), "--"]
    python = [*prefix, sys.executable, "-m", "specfirst"]
    # The run and the task come after the reader's own arguments: the last one wins, so
    # a reader cannot point a tool at another folder.
    fixed = ["--run", str(run_dir), "--task", str(task_dir)]
    lines = {"ask": ([*python, "ask"], fixed), "check": ([*python, "run", "validate"], fixed)}
    for name, (line, after) in lines.items():
        path = task_dir / tasks.BIN / name
        path.parent.mkdir(parents=True, exist_ok=True)
        quoted = " ".join(_quote(part) for part in line)
        tail = " ".join(_quote(part) for part in after)
        path.write_text("#!/usr/bin/env bash\n"
                        f"# {TOOLS[name]}\n"
                        "export MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*'\n"
                        f"exec {quoted} \"$@\" {tail}\n", encoding="ascii", newline="\n")
        path.chmod(0o755)


def _quote(part: str) -> str:
    return "'" + part.replace("'", "'\"'\"'") + "'"


def task_texts(task: tasks.Task) -> list[str]:
    """The text files of a task as it was built: read before the reader runs, or from a
    task built again. What the reader writes is never among them."""
    found = []
    for relative, sha in sorted(task.manifest.items()):
        path = task.folder / relative
        if path.is_file() and sha256_file(path) == sha:
            text = canary.read_text(path)
            if text is not None:
                found.append(text)
    return found


def store_prose(store: Path) -> list[str]:
    """Every paragraph the store of model text holds: each attempt, accepted or not, and
    the filler."""
    found = []
    for name in ("paragraphs.jsonl", "filler.jsonl"):
        path = store / name
        if not path.is_file():
            continue
        for line in path.read_text(encoding="ascii").splitlines():
            if line.strip():
                record = json.loads(line)
                found += [attempt["text"] for attempt in record.get("attempts") or []
                          if attempt.get("text")]
                if record.get("text"):
                    found.append(record["text"])
    return found


def own_records(catalog, written: list[dict]) -> list[dict]:
    """The reader's records as the catalog renders them: entry, unit, a valid value, its
    status and class, and the statement the harness renders from the value. Nothing the
    reader typed itself (its statement, its quotes) is in them."""
    from specfirst.compile.standard_form import StandardForm, StandardFormError

    form = StandardForm(catalog)
    found = []
    for item in written:
        try:
            statement = form.render(str(item.get("id")), str(item.get("unit")), item["value"])
        except (StandardFormError, KeyError, TypeError, ValueError):
            continue
        found.append({"id": item["id"], "unit": item["unit"], "value": item["value"],
                      "status": item.get("status") if item.get("status") in (
                          "stated", "default", "asked") else None,
                      "class": item.get("class") if item.get("class") in (
                          "document_rule", "house_default", "study_input") else None,
                      "statement": statement})
    return found


def kit_canaries(root: Path, kit_dir: Path, texts: list[str], arm: str, kit_sha: str,
                 seed: str | None, written: list[dict] | None = None) -> canary.Canaries:
    """The canaries of a run of an arm on a kit (ADR-010, decision 5). `texts` are the
    files of the task as it was built (`task_texts`); `written` the decision records the
    reader wrote, of which only what the catalog renders is allowed (`own_records`)."""
    reads = {f"gold/docs/{doc}.md" for doc in ("protocol", "sap")} if arm == "C" else set()
    files = genkits.read_manifest(kit_dir).get("files") or {}
    sources = [(f"kit:{genkits.MANIFEST}", kit_dir / genkits.MANIFEST)]
    sources += [(f"kit:{path}", kit_dir / path) for path in sorted(files)
                if not str(path).startswith("inputs/") and path not in reads]
    store = natural.store_dir()
    sources += [(f"store:{path.relative_to(store).as_posix()}", path)
                for path in sorted(store.rglob("*")) if path.is_file()]
    allowed = list(texts)
    answers = [item["answer"] for item in gendocs.read_oracle(kit_dir).get("answers") or []]
    allowed += [oracle.ANSWER.format(answer=answer) for answer in answers]
    allowed += [oracle.NO_ANSWER, oracle.UNKNOWN]
    gold = genkits.read_decisions(kit_dir)
    allowed += canary.reader_views(gold, tuple(tasks.DOCUMENTS))
    if arm == "C":
        allowed += [(kit_dir / path).read_text(encoding="ascii") for path in sorted(reads)]
    atoms = [str(r.get("statement")) for r in gold if r.get("statement")] + answers
    # The prose of the store (every attempt and the filler) is prose of the kind a reader
    # writes in its own words; what only the store holds is the record around it.
    atoms += store_prose(store)
    if written:
        own = own_records(catalogs.load(catalogs.default_dir(root)), written)
        allowed += canary.reader_views(own, tuple(tasks.DOCUMENTS))
        atoms += [r["statement"] for r in own]
    always = [(f"planted:{name}", canary.planted(kit_sha, name)) for name in PRIVATE]
    if seed:
        always.append(("seed", seed))
    return canary.build(sources, allowed, atoms, always)


def changed_files(task: tasks.Task) -> list[str]:
    """The files of a task folder that a run wrote or changed (bin/ is the run's)."""
    now = tasks.manifest(task.folder)
    found = [path for path, sha in now.items() if task.manifest.get(path) != sha]
    out = task.folder / tasks.OUT
    found += [path.relative_to(task.folder).as_posix() for path in sorted(out.rglob("*"))
              if path.is_file()]
    return sorted(set(found))


def _result_event(text: str) -> dict:
    return {"type": "result", "subtype": "success", "is_error": False, "duration_ms": 0,
            "duration_api_ms": 0, "num_turns": 0, "result": text, "session_id": "harness",
            "total_cost_usd": 0, "usage": {"input_tokens": 0, "output_tokens": 0,
                                           "cache_creation_input_tokens": 0,
                                           "cache_read_input_tokens": 0},
            "modelUsage": {}, "permission_denials": []}


def _no_reader(run_dir: Path, text: str, started: float) -> adapter.Outcome:
    event = _result_event(text)
    (run_dir / adapter.TRANSCRIPT).write_text(json_text(event) + "\n", encoding="ascii",
                                              newline="\n")
    return adapter.Outcome([], event, 1, time.monotonic() - started, False, 0)


def _write_out(task: tasks.Task, records: list[dict]) -> None:
    out = task.folder / tasks.OUT
    (out / "decisions.jsonl").write_text("".join(json_text(r) + "\n" for r in records),
                                         encoding="ascii", newline="\n")
    (out / "unmapped.jsonl").write_text("", encoding="ascii", newline="\n")


def _control(root: Path, kit_dir: Path, task: tasks.Task, run_dir: Path, catalog,
             stage: str) -> tuple[list[dict], object]:
    from specfirst.score import kit as kits
    from specfirst.score import scorer

    kit = kits.load(kit_dir)
    machine = kits.machine_of(root, kit)
    records, documents = scorer.control_records(machine, kits.case(kit, machine.catalog, stage))
    wanted = set(task.keys)
    records = [r for r in records if (r["id"], r["unit"]) in wanted]
    for item in records:
        if item.get("status") == "asked":
            oracle.ask(catalog, run_dir, task.folder, item["id"],
                       f"What does the study decide for {item['id']}?", item["unit"])
    return records, documents


def run(root: Path, kit_dir: Path, arm: str, tasks_dir: Path, runs_dir: Path,
        stage: str = "C", condition: str = "notes", reader: adapter.Reader | None = None,
        seed: str | None = None, seed_file: Path | None = None,
        budget: record.Budget | None = None, env: dict[str, str] | None = None,
        name: str | None = None) -> Run:
    """Run an arm on a kit: build the task, run the arm, check and record the run."""
    if arm not in ARMS:
        raise RunError(f"an arm is one of {', '.join(ARMS)}, not '{arm}'")
    for folder in (tasks_dir, runs_dir, kit_dir):
        home = tasks.inside_checkout(folder)
        if home is not None:
            raise RunError(f"{folder} lies inside the checkout {home} (PLAN.md section 11.2)")
    manifest = genkits.read_manifest(kit_dir)
    if seed is not None and genkits.seed_sha256(seed) != manifest.get("seed_sha256"):
        raise RunError("the seed given is not the seed of the kit (its SHA-256 differs)")
    catalog = catalogs.load(catalogs.default_dir(root))
    reader = (reader or adapter.default_reader()) if arm == "R" else None
    budget = budget or record.BUDGETS[arm]
    windows = bool(reader and reader.windows)
    protected = protected_roots(root, kit_dir, tasks_dir, runs_dir, seed_file, windows)
    task = tasks.build(root, kit_dir, tasks_dir, stage, condition)
    run_dir = runs_dir / (name or f"{arm}-{task.id}")
    shutil.rmtree(run_dir, ignore_errors=True)
    run_dir.mkdir(parents=True)
    kit_sha = sha256_file(kit_dir / genkits.MANIFEST)
    oracle.write_oracle(kit_dir, run_dir, canary.planted(kit_sha, oracle.ORACLE))
    (run_dir / KIT_JSON).write_text(json.dumps({"kit": str(kit_dir), "canary": canary.planted(
        kit_sha, KIT_JSON)}, indent=1, sort_keys=True) + "\n", encoding="ascii", newline="\n")
    (run_dir / TASK_JSON).write_text(json.dumps({
        "id": task.id, "stage": stage, "condition": condition, "units": list(task.units),
        "keys": [list(key) for key in task.keys], "manifest": task.manifest}, indent=1,
        sort_keys=True) + "\n", encoding="ascii", newline="\n")
    write_tools(task.folder, run_dir, windows)
    (task.folder / tasks.OUT / "questions.jsonl").write_text("", encoding="ascii")
    settings_value = adapter.settings(protected, windows)
    texts = task_texts(task)  # before the reader writes anything
    started = time.monotonic()
    documents = outputs.task_documents(task.folder)
    if arm == "R":
        assert reader is not None
        outcome = adapter.run(reader, task.folder, run_dir, settings_value, budget, env)
    elif arm == "S":
        _write_out(task, [])
        outcome = _no_reader(run_dir, "arm S: no record; every decision takes its house "
                             "default", started)
    else:
        records, documents = _control(root, kit_dir, task, run_dir, catalog, stage)
        _write_out(task, records)
        outcome = _no_reader(run_dir, f"arm C: {len(records)} records from the standard-form "
                             "documents and the house standard", started)
    changed = changed_files(task)
    for relative in changed:
        target = run_dir / WORKSPACE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(task.folder / relative, target)
    asks = oracle.read_asks(run_dir)
    invalid = outputs.problems(task.folder / tasks.OUT, catalog, task.keys, documents, asks)
    canaries = kit_canaries(root, kit_dir, texts, arm, kit_sha, seed,
                            outputs.read(task.folder / tasks.OUT, "decisions.jsonl"))
    hits = (canary.scan_transcript(canaries, run_dir / adapter.TRANSCRIPT)
            + canary.scan_files(canaries, run_dir / WORKSPACE, changed))
    folder_problems = tasks.problems(task.folder, kit_dir)
    result = outcome.result or {}
    made = {
        "record": record.RECORD,
        "run": run_dir.name,
        "arm": arm,
        "stage": stage,
        "condition": condition,
        "task": {"id": task.id, "manifest_sha256": content_hash(task.manifest),
                 "units": list(task.units), "decisions": len(task.keys),
                 "knowledge": task.knowledge},
        "kit": {"id": manifest["id"], "split": manifest["split"],
                "generator": manifest["generator"], "kit_yaml_sha256": kit_sha,
                "seed_checked": seed is not None},
        "reader": {
            "adapter": "none" if reader is None else ("stub" if reader.stub else "claude-code"),
            "argv": outcome.argv, "model": reader.model if reader else None,
            "cli_version": outcome.init.get("claude_code_version"),
            "api_key_source": outcome.init.get("apiKeySource"),
            "models_used": sorted(record.tokens_by_model(result)),
            "deny": sorted(adapter.denied_roots(settings_value)) if reader else [],
            "command_problems": adapter.command_problems(
                outcome.argv, settings_value, protected, windows) if reader else []},
        "budget": record.budget_dict(budget),
        "cost": record.cost(outcome.result, outcome.wall_seconds,
                            reader.model if reader else record.MODEL),
        "end": {"result": outcome.result is not None,
                "is_error": bool(result.get("is_error")),
                "message": str(result.get("result") or "")[:500],
                "stopped": outcome.stopped, "returncode": outcome.returncode,
                "events": outcome.events,
                "permission_denials": result.get("permission_denials") or [],
                "stderr": outcome.stderr[-1000:] if outcome.stderr else ""},
        "outputs": {name: _file_line(task.folder / tasks.OUT / name) for name in tasks.OUTPUTS},
        "asks": [{key: item.get(key) for key in ("decision", "unit", "answered")}
                 for item in asks],
        "workspace": changed,
        "task_problems": folder_problems,
        "valid": not invalid,
        "problems": invalid,
        "canary": {"count": len(canaries), "sources": canaries.sources(),
                   "hits": [hit.line() for hit in hits]},
    }
    made["over_budget"] = record.over_budget(made)
    made["passed"] = not (made["over_budget"] or invalid or hits or folder_problems
                          or made["reader"]["command_problems"])
    (run_dir / RUN_JSON).write_text(json.dumps(made, indent=1, sort_keys=True) + "\n",
                                    encoding="utf-8", newline="\n")
    return Run(run_dir, made, hits)


def _file_line(path: Path) -> dict:
    if not path.is_file():
        return {"lines": None, "sha256": None}
    text = path.read_bytes().decode("utf-8", errors="replace")
    return {"lines": sum(1 for line in text.splitlines() if line.strip()),
            "sha256": sha256_file(path)}


def lines(made: Run) -> list[str]:
    """What a run prints."""
    rec = made.record
    spent = rec["cost"]
    tokens = spent["tokens"]
    out = [f"run {rec['run']}: arm {rec['arm']}, stage {rec['stage']}, condition "
           f"{rec['condition']}, kit {rec['kit']['id']} ({rec['kit']['split']}), task "
           f"{rec['task']['id']} ({rec['task']['decisions']} decisions)",
           f"  reader: {rec['reader']['adapter']}"
           + (f", model {rec['reader']['model']}, used {rec['reader']['models_used']}, "
              f"CLI {rec['reader']['cli_version']}" if rec["reader"]["model"] else ""),
           f"  cost: {spent['turns']} turns, {spent['wall_seconds']} s wall, "
           f"{spent['api_seconds']} s API, tokens in {tokens['input']} out {tokens['output']} "
           f"cache write {tokens['cache_write']} cache read {tokens['cache_read']}, "
           f"USD {spent['usd']:.4f} (CLI: {spent['usd_cli']})",
           f"  budget: {rec['budget']}: "
           + ("within" if not rec["over_budget"] else "; ".join(rec["over_budget"])),
           "  outputs: " + ", ".join(f"{name} {item['lines']} lines"
                                     for name, item in rec["outputs"].items()),
           f"  asks: {len(rec['asks'])}, answered {sum(1 for a in rec['asks'] if a['answered'])}"
           + "".join(f"; {a['decision']} ({a['unit']})" for a in rec["asks"]),
           "  output files: " + ("valid" if rec["valid"] else
                                  f"{len(rec['problems'])} problems"),
           *[f"    {problem}" for problem in rec["problems"][:20]],
           "  task folder: " + ("holds only what a reader may see" if not rec["task_problems"]
                                 else "; ".join(rec["task_problems"][:5])),
           f"  canary scan: {rec['canary']['count']} canaries from "
           f"{len(rec['canary']['sources'])} files; "
           + ("clean" if not rec["canary"]["hits"] else
              f"{len(rec['canary']['hits'])} hits"),
           *[f"    {hit}" for hit in rec["canary"]["hits"][:20]]]
    if rec["reader"].get("command_problems"):
        out += [f"  command: {problem}" for problem in rec["reader"]["command_problems"]]
    if rec["end"].get("permission_denials"):
        out.append(f"  permission denials: {len(rec['end']['permission_denials'])}")
    out.append(f"  RUN {rec['run']}: {'PASS' if rec['passed'] else 'FAIL'}")
    return out


# ---- the isolation probe (ADR-010, decisions 4 and 8) -----------------------------------

PROBE = ("This is a check of the permissions you run under, not a reading task. Do each "
         "step below once, in order, and try no other way to reach these files. {steps} "
         "Then reply with one line per step: its number, and 'denied' or 'done'. Do not "
         "repeat the contents of any file.")


def probe_targets(root: Path, kit_dir: Path, run_dir: Path) -> list[Path]:
    """The protected files the probe tries to read: gold and the oracle of the kit, the
    store of model text, the run's own copy of the oracle."""
    return [kit_dir / "gold" / "oracle.yaml", kit_dir / "gold" / "decisions.jsonl",
            natural.store_dir() / "paragraphs.jsonl", run_dir / oracle.ORACLE]


def probe(root: Path, kit_dir: Path, tasks_dir: Path, runs_dir: Path,
          reader: adapter.Reader | None = None, stage: str = "C",
          condition: str = "notes") -> tuple[Run, list[str]]:
    """Ask the reader to run `bin/check`, which it may, and then to read every protected
    file of `probe_targets`, by its file tools and by Bash. The probe passes when no
    canary reaches the transcript, `bin/check` was not denied, and every other attempt
    was."""
    reader = reader or adapter.default_reader()
    task = tasks.build(root, kit_dir, tasks_dir, stage, condition)
    name = f"probe-{task.id}"
    targets = probe_targets(root, kit_dir, runs_dir / name)
    shown = [adapter.windows_path(path) if reader.windows else str(path) for path in targets]
    bash = shown[-1].replace("\\", "/")
    if reader.windows and len(bash) > 2 and bash[1] == ":":
        bash = f"/{bash[0].lower()}{bash[2:]}"
    steps = ["1. Run the Bash command: bin/check"]
    steps += [f"{n}. Read the file {path} with the Read tool." for n, path in
              enumerate(shown, start=2)]
    steps += [f"{len(shown) + 2}. Run the Bash command: cat '{bash}'",
              f"{len(shown) + 3}. Run the Bash command: bin/check; cat '{bash}'"]
    asked = adapter.Reader(reader.argv, reader.model, PROBE.format(steps=" ".join(steps)))
    made = run(root, kit_dir, "R", tasks_dir, runs_dir, stage, condition, asked,
               budget=record.BUDGETS["probe"], name=name)
    forbidden = len(steps) - 1
    denials = made.record["end"]["permission_denials"]
    allowed_denied = [item for item in denials if isinstance(item, dict) and str(
        (item.get("tool_input") or {}).get("command", "")).strip() == "bin/check"]
    found = []
    if made.hits:
        found.append(f"{len(made.hits)} canaries reached the transcript or the workspace")
    if allowed_denied:
        found.append("bin/check, which the reader may run, was denied")
    if len(denials) - len(allowed_denied) < forbidden:
        found.append(f"{len(denials) - len(allowed_denied)} attempts were denied of "
                     f"{forbidden}")
    found += [f"budget: {problem}" for problem in made.record["over_budget"]]
    return made, found


# ---- a run kept in the repository, and its check ----------------------------------------

STORE = Path(__file__).resolve().parent / "kept"
KEPT = (RUN_JSON, TASK_JSON, oracle.ASKS, adapter.TRANSCRIPT)


def _redact(value: object, pairs: list[tuple[str, str]]) -> object:
    if isinstance(value, str):
        for old, new in pairs:
            value = value.replace(old, new)
        return value
    if isinstance(value, dict):
        return {_redact(key, pairs): _redact(item, pairs) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, pairs) for item in value]
    return value


def redactions(task_dir: Path, run_dir: Path, kit_dir: Path, root: Path) -> list[tuple[str, str]]:
    """The local paths of a run and what a kept run says instead, longest first."""
    pairs = []
    for path, name in ((task_dir, "<task>"), (run_dir, "<run>"), (kit_dir, "<kit>"),
                       (root, "<checkout>")):
        posix = path.resolve().as_posix()
        forms = {posix, adapter.windows_path(path)}
        if posix.startswith("/mnt/") and len(posix) > 6 and posix[6] == "/":
            forms |= {adapter.windows_path(path).replace("\\", "/"), posix[4:]}
        pairs += [(form, name) for form in forms]
    home = windows_home()
    if home is not None:
        posix = home.as_posix()
        win = adapter.windows_path(home)
        pairs += [(form, "<home>") for form in {posix, win, win.replace("\\", "/"),
                                                posix[4:]}]
    # The CLI names a folder of its own by the path of the task with every ':' and '\'
    # as '-' (the slug of its project memory).
    pairs += [(slug(form), f"<{name.strip('<>')}-slug>") for form, name in list(pairs)
              if ":\\" in form]
    return sorted(set(pairs), key=lambda pair: -len(pair[0]))


def slug(windows: str) -> str:
    return windows.replace(":", "-").replace("\\", "-")


def keep(made: Run, task_dir: Path, kit_dir: Path, root: Path, store: Path = STORE) -> Path:
    """Copy a run into the store of kept runs: its record, task, ask log, transcript and
    workspace, in ASCII, with the local paths replaced."""
    pairs = redactions(task_dir, made.folder, kit_dir, root)
    target = store / made.folder.name
    shutil.rmtree(target, ignore_errors=True)
    target.mkdir(parents=True)
    names = [name for name in KEPT if (made.folder / name).is_file()]
    names += [path.relative_to(made.folder).as_posix() for path in sorted(
        (made.folder / WORKSPACE).rglob("*")) if path.is_file()]
    for name in names:
        source = made.folder / name
        text = source.read_bytes().decode("utf-8", errors="replace")
        if name.endswith(".jsonl"):
            kept = "".join(json.dumps(_redact(json.loads(line), pairs), sort_keys=True,
                                      ensure_ascii=True) + "\n"
                           for line in text.splitlines() if line.strip())
        elif name.endswith(".json"):
            kept = json.dumps(_redact(json.loads(text), pairs), indent=1, sort_keys=True,
                              ensure_ascii=True) + "\n"
        else:
            kept = str(_redact(text, pairs))
            kept = kept.encode("ascii", errors="backslashreplace").decode("ascii")
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        (target / name).write_text(kept, encoding="ascii", newline="\n")
    return target


def check(root: Path, kept: Path, kit_dir: Path, tasks_dir: Path,
          seed: str | None = None) -> tuple[list[str], list[canary.Hit], tasks.Task]:
    """Hold a kept run against a task built again now from the same kit: the task is the
    one the run read; the run ended within budget; its output files are valid; no
    canary of the kit as written now is in its transcript or workspace."""
    made = json.loads((kept / RUN_JSON).read_text(encoding="ascii"))
    told = json.loads((kept / TASK_JSON).read_text(encoding="ascii"))
    catalog = catalogs.load(catalogs.default_dir(root))
    task = tasks.build(root, kit_dir, tasks_dir, made["stage"], made["condition"])
    found = []
    if task.manifest != told["manifest"]:
        differ = sorted(set(task.manifest) ^ set(told["manifest"]) | {
            path for path in set(task.manifest) & set(told["manifest"])
            if task.manifest[path] != told["manifest"][path]})
        found.append(f"task: built again, {len(differ)} files differ from the task the run "
                     f"read, for example {', '.join(differ[:3])}")
    kit_sha = sha256_file(kit_dir / genkits.MANIFEST)
    if made["kit"]["kit_yaml_sha256"] != kit_sha:
        found.append("kit: kit.yaml is not the one the run read")
    found += [f"budget: {problem}" for problem in record.over_budget(made)]
    if made["arm"] == "R" and made["reader"]["adapter"] == "claude-code" and (
            record.MODEL not in made["reader"]["models_used"]):
        found.append(f"reader: {record.MODEL} is not among the models used "
                     f"{made['reader']['models_used']}")
    found += [f"command: {problem}" for problem in made["reader"].get("command_problems", [])]
    asks = oracle.read_asks(kept)
    found += [f"outputs: {problem}" for problem in outputs.problems(
        kept / WORKSPACE / tasks.OUT, catalog, task.keys, outputs.task_documents(task.folder),
        asks)]
    canaries = kit_canaries(root, kit_dir, task_texts(task), made["arm"], kit_sha, seed,
                            outputs.read(kept / WORKSPACE / tasks.OUT, "decisions.jsonl"))
    names = [path.relative_to(kept / WORKSPACE).as_posix()
             for path in sorted((kept / WORKSPACE).rglob("*")) if path.is_file()]
    hits = (canary.scan_transcript(canaries, kept / adapter.TRANSCRIPT)
            + canary.scan_files(canaries, kept / WORKSPACE, names))
    return found, hits, task


def score(root: Path, kit_dir: Path, folder: Path) -> list[str]:
    """The score of a run (kept or not) on its kit, with the questions it asked."""
    from specfirst.score import kit as kits
    from specfirst.score import report, scorer
    from specfirst.score.reading import ask_keys, unmapped_keys

    made = json.loads((folder / RUN_JSON).read_text(encoding="utf-8"))
    kit = kits.load(kit_dir)
    machine = kits.machine_of(root, kit)
    problems = kits.gold_problems(machine, kit)
    if problems:
        return [f"problem: {problem}" for problem in problems] + [
            "the scorer's build of the gold decisions is not the gold of the kit: no score"]
    case = kits.case(kit, machine.catalog, made["stage"])
    out = folder / WORKSPACE / tasks.OUT
    units = {entry.id: entry.units for entry in machine.catalog.entries.values()}
    result = scorer.run(machine, case, outputs.read(out, "decisions.jsonl"), arm=made["arm"],
                        asked=ask_keys(oracle.read_asks(folder), units),
                        unmapped=unmapped_keys(outputs.read(out, "unmapped.jsonl")))
    return report.lines(result)
