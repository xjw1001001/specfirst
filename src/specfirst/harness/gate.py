"""The checks of `specfirst gate read-2a` (ADR-005, decision 1; docs/decisions/ADR-010.md,
decision 9).

Gate of the part: "A dry run of each arm on one train kit ends within budget
with valid output files. The canary scan is clean." The train kit is kit 4
of the seed of the gate gen-2a (train, the ask demo), written again by a
process of its own into a folder outside every checkout. No check calls a
model (rule R4): the dry run of arm R made with the model is kept in
src/specfirst/harness/kept/ and checked from its record; arms S and C, and
arm R with the stub reader, run live.

    skills       core-reader and the reading notes v0: rendered, Agent Skills, no leak
    kit          kit 4 of the gate seed, written again; its gold built again
    task         the task folder: deterministic, only what a reader may see
    oracle       `specfirst ask` answers exactly what the oracle file lists, logged
    adapter      the command line and the deny rules of a reader
    budget       the record of a run against its budget
    outputs      the validation of out/
    canary       the canaries of each protected kind are found; allowed text is not
    arm S, arm C the dry runs, live; their scores are reported
    arm R, stub  the adapter with the stub reader, live; the stub run kept and checked,
                 with the plants of the binding of a kept run (ADR-017, decision 7)
    arm R        the dry run of arm R, kept: its task, by bytes where the slice reaches
                 and by version where it does not (ADR-017), budget, files, scan; its score

Each check first shows that it fails on what it is for (rule R5).
"""

from __future__ import annotations

import copy
import dataclasses
import json
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.gen import documents as gendocs
from specfirst.gen import gate2, natural
from specfirst.gen import kits as genkits
from specfirst.harness import adapter, binding, canary, knowledge, oracle, outputs, record, runs
from specfirst.harness import task as tasks
from specfirst.machine.canonical import json_text, sha256_file

Out = Callable[[str], None]
NUMBER = 4  # kit 4 of a set: train, the ask demo (gen-3a, documents.TIER_PLAN)
SEED = genkits.kit_seed(gate2.SEED, NUMBER)
_STATE: dict[str, Path] = {}


def _scratch() -> Path:
    if "scratch" not in _STATE:
        _STATE["scratch"] = Path(tempfile.mkdtemp(prefix="specfirst-read2a-"))
    return _STATE["scratch"]


def _kit(root: Path) -> Path:
    """Kit 4 of the gate seed, written once per process by a process of its own."""
    if "kit" not in _STATE:
        folder = _scratch() / "kits" / f"kit-{NUMBER:03d}"
        genkits.generate_apart(root, SEED, folder, genkits.split_of(NUMBER), number=NUMBER,
                               hash_seed="1", zone=None)
        _STATE["kit"] = folder
    return _STATE["kit"]


def cleanup() -> None:
    if "scratch" in _STATE:
        shutil.rmtree(_STATE["scratch"], ignore_errors=True)
    _STATE.clear()


def _holds(out: Out, name: str, problems: list[str]) -> bool:
    """A planted defect counts when the check finds it."""
    out(f"  planted, {name}: " + (f"found ({problems[0]})" if problems else "NOT FOUND"))
    return bool(problems)


# ---- skills ------------------------------------------------------------------------------


def skills(root: Path, out: Out) -> bool:
    kit = _kit(root)
    secrets = knowledge.secrets_of(kit, SEED)
    paragraphs = knowledge.store_paragraphs(natural.store_dir())
    found = knowledge.problems(root, secrets, paragraphs)
    for name in (tasks.CORE, *knowledge.UNITS):
        text = tasks.skill_path(root, name).read_text(encoding="ascii")
        out(f"skill {name}: {len(text.splitlines())} lines, "
            + ("rendered from the catalog" if name in knowledge.UNITS else "written by hand"))
    out(f"leak check: {len(secrets)} kit, study and subject IDs and the seed of kit {NUMBER}; "
        f"{len(paragraphs)} paragraphs of the store")
    for problem in found:
        out(f"  {problem}")
    unit = knowledge.UNITS[0]
    manifest = genkits.read_manifest(kit)
    subjects = [secret for secret in secrets if secret not in (
        SEED, str(manifest["id"]), str(manifest["study"]["id"]))]

    def planted_skills(change: Callable[[str], str], name: str = unit) -> list[str]:
        """knowledge.problems on a copy of the catalog and the skills, one SKILL.md
        changed: the check itself, not a stand-in for it."""
        copy_root = _scratch() / f"skills-root-{len(list(_scratch().glob('skills-root-*')))}"
        shutil.copytree(catalogs.default_dir(root), catalogs.default_dir(copy_root))
        shutil.copytree(root / tasks.SKILLS, copy_root / tasks.SKILLS)
        path = tasks.skill_path(copy_root, name)
        path.write_text(change(path.read_text(encoding="ascii")), encoding="ascii")
        return knowledge.problems(copy_root, secrets, paragraphs)

    def only(problems: list[str], words: str) -> list[str]:
        """The problems of a plant that name what was planted, nothing else."""
        return [problem for problem in problems if words in problem]

    planted = [
        _holds(out, "a skill that names the kit", only(planted_skills(
            lambda text: text + f"\nSee kit {manifest['id']}.\n"), f"'{manifest['id']}'")),
        _holds(out, f"a skill that names the subject {subjects[0]}", [
            problem for problem in planted_skills(
                lambda text: text + f"\nSubject {subjects[0]} is an example.\n")
            if f"'{subjects[0]}'" in problem]),
        _holds(out, "a skill that quotes the store", only(planted_skills(
            lambda text: text + "\n" + max(paragraphs, key=len) + "\n"),
            "quotes the paragraph")),
        _holds(out, "notes that are not their rendering", only(planted_skills(
            lambda text: text.replace("Alternatives:", "Choices:", 1)), "not the rendering")),
        _holds(out, "a SKILL.md without a name", only(planted_skills(
            lambda text: text.replace(f"name: {unit}\n", "", 1)), "front matter names")),
        _holds(out, "core-reader without a description", only(planted_skills(
            lambda text: text.replace("description: ", "summary: ", 1), tasks.CORE),
            "no description")),
    ]
    out(f"skills: {'no problem' if not found else f'{len(found)} problems'}")
    return not found and all(planted)


# ---- the kit and the task ----------------------------------------------------------------


def kit(root: Path, out: Out) -> bool:
    from specfirst.score import kit as kits

    folder = _kit(root)
    manifest = genkits.read_manifest(folder)
    out(f"kit {NUMBER} of the set of the seed '{gate2.SEED}': {manifest['id']}, split "
        f"{manifest['split']}, generator {manifest['generator']}, tier "
        f"{manifest['documents']['tier']}, kit.yaml {sha256_file(folder / 'kit.yaml')[:16]}")
    loaded = kits.load(folder)
    machine = kits.machine_of(root, loaded)
    problems = kits.gold_problems(machine, loaded)
    for problem in problems:
        out(f"  {problem}")
    out(f"the gold built again is the gold of the kit: {'yes' if not problems else 'no'}")
    return manifest["split"] == "train" and not problems


def task(root: Path, out: Out) -> bool:
    folder = _kit(root)
    first = tasks.build(root, folder, _scratch() / "tasks-a")
    second = tasks.build(root, folder, _scratch() / "tasks-b")
    same = first.id == second.id and first.manifest == second.manifest
    out(f"task {first.id}: {len(first.manifest)} files, {len(first.keys)} decisions of "
        f"{', '.join(first.units)}; built twice in two folders: "
        + ("the same files" if same else "DIFFERENT"))
    found = tasks.problems(first.folder, folder)
    for problem in found:
        out(f"  {problem}")
    secrets = task_secrets(knowledge.secrets_of(folder, SEED))
    named = knowledge.leaks((first.folder / tasks.TASK_FILE).read_text(encoding="ascii"),
                            secrets, [])
    out("TASK.md names no kit and no seed" if not named else f"TASK.md {named}")
    staged = tasks.build(root, folder, _scratch() / "tasks-t", stage="T", condition="catalog")
    t_found = tasks.problems(staged.folder, folder)
    out(f"stage T, condition catalog: task {staged.id}, {len(staged.keys)} decisions of "
        f"{', '.join(staged.units)}, knowledge {staged.knowledge}, ADaM of gold "
        f"{sorted(p for p in staged.manifest if p.startswith(tasks.ADAM))}; "
        + ("only what a reader may see" if not t_found else "; ".join(t_found)))
    planted_dir = _scratch() / "tasks-planted"
    shutil.copytree(first.folder, planted_dir, dirs_exist_ok=True)
    shutil.copyfile(folder / "gold" / "oracle.yaml", planted_dir / "inputs" / "docs" / "o.yaml")
    leaked = tasks.problems(planted_dir, folder)
    extra = _scratch() / "tasks-extra"
    shutil.copytree(first.folder, extra, dirs_exist_ok=True)
    (extra / "notes.txt").write_text("x\n", encoding="ascii")
    planted = [
        _holds(out, "the oracle file of the kit in a task", leaked),
        _holds(out, "a file outside the allow list", tasks.problems(extra, folder)),
        _holds(out, "a TASK.md that names the kit", knowledge.leaks(
            (first.folder / tasks.TASK_FILE).read_text(encoding="ascii")
            + f"\nThis is kit {genkits.read_manifest(folder)['id']}.\n", secrets, [])),
        _holds(out, "a TASK.md that names the seed", knowledge.leaks(
            (first.folder / tasks.TASK_FILE).read_text(encoding="ascii")
            + f"\nSeed: {SEED}\n", secrets, [])),
    ]
    staged_ok = staged.units == ("tfl-ae-summary",) and staged.knowledge == [
        f"{tasks.KNOWLEDGE}/{tasks.CORE}/SKILL.md"]
    return same and not found and not named and not t_found and staged_ok and all(planted)


def task_secrets(secrets: list[str]) -> list[str]:
    """What TASK.md may not name: the kit ID (lower case) and the seed. The study ID and
    the subject IDs stand in the data and the documents of every task."""
    return [secret for secret in secrets if secret == SEED or secret.islower()]


# ---- the oracle --------------------------------------------------------------------------


def _ask_everything(catalog, run_dir: Path, task_dir: Path, decision: str, question: str,
                    unit: str | None = None) -> tuple[str, bool]:
    """Planted defect: an oracle that answers every decision."""
    oracle.ask(catalog, run_dir, task_dir, decision, question, unit)
    return "Answer: whatever you like", True


def oracle_problems(root: Path, kit_dir: Path, ask: Callable, where: Path) -> tuple[
        list[str], list[str]]:
    """Ask about every decision of the task, and about an entry the catalog lacks; the
    oracle must answer exactly the decisions its file lists, and log every ask."""
    catalog = catalogs.load(catalogs.default_dir(root))
    made = tasks.build(root, kit_dir, where / "tasks")
    run_dir = where / "run"
    shutil.rmtree(run_dir, ignore_errors=True)
    oracle.write_oracle(kit_dir, run_dir, "canary")
    listed = {(item["decision"], item["unit"]): item["answer"]
              for item in oracle.answers(run_dir)}
    (made.folder / tasks.OUT / "questions.jsonl").unlink(missing_ok=True)
    found, seen = [], []
    for entry, unit in [*made.keys, ("no.such.entry", "mod-treatment")]:
        text, answered = ask(catalog, run_dir, made.folder, entry, f"What is {entry}?", unit)
        seen.append(f"{entry} ({unit}): {'answered' if answered else 'no answer'}")
        if answered != ((entry, unit) in listed):
            found.append(f"{entry} ({unit}): answered {answered}, the oracle lists it "
                         f"{(entry, unit) in listed}")
        elif answered and text != oracle.ANSWER.format(answer=listed[(entry, unit)]):
            found.append(f"{entry} ({unit}): the answer is not the oracle's")
    asks = oracle.read_asks(run_dir)
    if len(asks) != len(made.keys) + 1:
        found.append(f"the ask log has {len(asks)} lines for {len(made.keys) + 1} asks")
    given = outputs.read(made.folder / tasks.OUT, "questions.jsonl")
    if [(r["decision"], r["unit"], r["question"]) for r in given] != [
            (a["decision"], a["unit"], a["question"]) for a in asks]:
        found.append("out/questions.jsonl is not the ask log")
    return found, seen


def oracle_check(root: Path, out: Out) -> bool:
    folder = _kit(root)
    listed = [(item["decision"], item["unit"])
              for item in gendocs.read_oracle(folder).get("answers") or []]
    out(f"the oracle file of kit {NUMBER} lists {len(listed)} decisions: "
        + ", ".join(f"{d} ({u})" for d, u in listed))
    found, seen = oracle_problems(root, folder, oracle.ask, _scratch() / "oracle")
    answered = [line for line in seen if line.endswith(": answered")]
    out(f"asked about {len(seen)} decisions (every decision of the task and one entry the "
        f"catalog lacks): answered {len(answered)}: {', '.join(answered)}")
    for problem in found:
        out(f"  {problem}")
    planted, _ = oracle_problems(root, folder, _ask_everything, _scratch() / "oracle-planted")
    return not found and len(listed) == len(answered) > 0 and _holds(
        out, "an oracle that answers every decision", planted)


# ---- the adapter -------------------------------------------------------------------------


def adapter_check(root: Path, out: Out) -> bool:
    scratch = _scratch()
    protected = [scratch / "kits", scratch / "runs", natural.store_dir(), root.parent]
    tools_dir = scratch / "tasks" / "task-x" / tasks.BIN
    budget_r = record.BUDGETS["R"]
    passed = True
    for windows, reader in ((True, adapter.Reader(("node.exe", "cli.js"))),
                            (False, adapter.Reader(("claude",)))):
        value = adapter.settings(protected, windows, tools_dir)
        argv = adapter.command(reader, scratch / "settings.json", budget_r)
        found = adapter.command_problems(argv, value, protected, windows, tools_dir, budget_r)
        out(f"{'Windows' if windows else 'Linux'} reader: {len(argv)} arguments, "
            f"{len(value['permissions']['deny'])} deny rules on "
            f"{len(adapter.denied_roots(value))} folders: "
            + ("as ADR-010 says" if not found else "; ".join(found)))
        passed = passed and not found
    out("command: " + " ".join(json.dumps(part) if " " in part or not part else part
                               for part in adapter.command(
                                   adapter.Reader(("claude",)), Path("<run>/settings.json"),
                                   record.BUDGETS["R"])))
    value = adapter.settings(protected, True, tools_dir)
    argv = adapter.command(adapter.Reader(("node.exe", "cli.js")), scratch / "settings.json",
                           budget_r)
    fewer = copy.deepcopy(value)
    fewer["permissions"]["deny"] = [rule for rule in fewer["permissions"]["deny"]
                                    if not rule.startswith("Read(")
                                    or adapter.rule_paths(protected[2], True)[0] not in rule]
    open_tools = adapter.settings(protected, True)

    def problems(argv_: list[str], value_: dict) -> list[str]:
        return adapter.command_problems(argv_, value_, protected, True, tools_dir, budget_r)

    planted = [
        _holds(out, "settings without the deny rule of the store", problems(argv, fewer)),
        _holds(out, "settings that let the reader write bin/", problems(argv, open_tools)),
        _holds(out, "no --strict-mcp-config", problems(
            [part for part in argv if part != "--strict-mcp-config"], value)),
        _holds(out, "an --add-dir", problems([*argv, "--add-dir", "/"], value)),
        _holds(out, "another model", problems(
            [("claude-sonnet-5-5" if part == record.MODEL else part) for part in argv], value)),
        _holds(out, "Bash allowed for every command", problems(
            [part.replace("Bash(bin/ask:*)", "Bash") for part in argv], value)),
        _holds(out, "--max-turns over the budget", problems(
            [("500" if part == str(budget_r.turns) else part) for part in argv], value)),
    ]
    return passed and all(planted)


# ---- the record against its budget -------------------------------------------------------


def _honest_record() -> dict:
    result = {"type": "result", "is_error": False, "num_turns": 40, "duration_api_ms": 600000,
              "result": "done", "total_cost_usd": 3.2,
              "usage": {"input_tokens": 2000, "output_tokens": 40000,
                        "cache_creation_input_tokens": 150000,
                        "cache_read_input_tokens": 4000000,
                        "cache_creation": {"ephemeral_1h_input_tokens": 0}},
              "modelUsage": {record.MODEL: {"inputTokens": 2000, "outputTokens": 40000,
                                            "cacheCreationInputTokens": 150000,
                                            "cacheReadInputTokens": 4000000}}}
    return {"budget": record.budget_dict(record.BUDGETS["R"]),
            "cost": record.cost(result, 1200.0),
            "end": {"result": True, "is_error": False, "stopped": False}}


def budget(root: Path, out: Out) -> bool:
    honest = _honest_record()
    found = record.over_budget(honest)
    spent = honest["cost"]
    out(f"a run of 40 turns, 1200 s, 2,000 input, 40,000 output, 150,000 cache write and "
        f"4,000,000 cache read tokens of {record.MODEL}: USD {spent['usd']:.2f} against the "
        f"budget {record.BUDGETS['R']}: " + ("within" if not found else "; ".join(found)))

    def changed(path: tuple[str, str], value: object) -> dict:
        made = copy.deepcopy(honest)
        made[path[0]][path[1]] = value
        return made

    unpriced = copy.deepcopy(honest)
    unpriced["cost"]["unpriced_models"] = ["claude-unknown-9"]
    planted = [
        _holds(out, "101 turns", record.over_budget(changed(("cost", "turns"), 101))),
        _holds(out, "46 minutes", record.over_budget(changed(("cost", "wall_seconds"), 2760))),
        _holds(out, "USD 10.01", record.over_budget(changed(("cost", "usd"), 10.01))),
        _holds(out, "an error at the end", record.over_budget(changed(("end", "is_error"),
                                                                      True))),
        _holds(out, "stopped at the time limit", record.over_budget(changed(("end", "stopped"),
                                                                            True))),
        _holds(out, "no result event", record.over_budget(changed(("end", "result"), False))),
        _holds(out, "a model without a price", record.over_budget(unpriced)),
    ]
    return not found and spent["usd"] > 0 and all(planted)


# ---- the output files --------------------------------------------------------------------


def reader_records(kit_dir: Path, keys: tuple[tuple[str, str], ...]) -> list[dict]:
    """The records a reader that reads gold right writes: gold, its natural and house
    citations only, without the fields of the machine."""
    found = []
    for item in genkits.read_decisions(kit_dir):
        if (item["id"], item["unit"]) not in keys:
            continue
        made = {key: item[key] for key in ("id", "unit", "value", "status", "class",
                                           "statement") if key in item}
        cited = [c for c in item.get("citations") or [] if c.get("doc") in tasks.DOCUMENTS]
        if cited:
            made["citations"] = cited
        found.append(made)
    return found


def outputs_check(root: Path, out: Out) -> bool:
    folder = _kit(root)
    catalog = catalogs.load(catalogs.default_dir(root))
    made = tasks.build(root, folder, _scratch() / "tasks-out")
    documents = outputs.task_documents(made.folder)
    records = reader_records(folder, made.keys)
    asks = [{"decision": d, "unit": u, "question": "q"} for d, u in
            [(r["id"], r["unit"]) for r in records if r["status"] == "asked"]]

    def problems_of(decisions: list, questions: list, unmapped: list,
                    missing: str = "") -> list[str]:
        where = _scratch() / "out-check"
        shutil.rmtree(where, ignore_errors=True)
        where.mkdir(parents=True)
        for name, lines in (("decisions.jsonl", decisions), ("questions.jsonl", questions),
                            ("unmapped.jsonl", unmapped)):
            if name != missing:
                (where / name).write_text("".join(
                    (line if isinstance(line, str) else json.dumps(line)) + "\n"
                    for line in lines), encoding="utf-8")
        return outputs.problems(where, catalog, made.keys, documents, asks)

    unmapped = [{"doc": "sap", "anchor": "5/p1", "quote": "x", "note": "software"}]
    honest = problems_of(records, asks, unmapped)
    out(f"the output files of a reader that reads gold right: {len(records)} records, "
        f"{len(asks)} questions, 1 unmapped: "
        + ("valid" if not honest else "; ".join(honest[:3])))

    def one(change: Callable[[dict], None], index: int = 0) -> list[dict]:
        changed = copy.deepcopy(records)
        change(changed[index])
        return changed

    stated = next(n for n, r in enumerate(records) if r.get("status") == "stated")
    sloted = next(n for n, r in enumerate(records) if len(r["value"]) > 1)
    cases = {
        "a line that is not JSON": (["{not json"] + records, asks, unmapped),
        "a record without a status": (one(lambda r: r.pop("status")), asks, unmapped),
        "a decision the task does not ask for": (
            records + [{**records[0], "id": "demo.age.groups", "unit": "mod-demographics"}],
            asks, unmapped),
        "a second record of a decision": (records + [records[0]], asks, unmapped),
        "binds filled": (one(lambda r: r.update(binds=["adam:ADSL.TRT01P"])), asks, unmapped),
        "identifiable filled": (one(lambda r: r.update(identifiable="separated")), asks,
                                unmapped),
        "an alternative the entry lacks": (one(lambda r: r["value"].update(rule="nonsense")),
                                           asks, unmapped),
        "a slot left out": (one(lambda r: r["value"].pop(sorted(set(r["value"]) - {"rule"})[0]),
                                sloted), asks, unmapped),
        "a citation of another document": (one(lambda r: r["citations"][0].update(
            doc="sap-standard"), stated), asks, unmapped),
        "a citation of an anchor that is not there": (one(lambda r: r["citations"][0].update(
            anchor="99/p9"), stated), asks, unmapped),
        "a question about no entry": (records, asks + [{"decision": "no.such", "unit": None,
                                                        "question": "q"}], unmapped),
        "questions that are not the ask log": (records, asks[:-1], unmapped),
        "an unmapped anchor that is not there": (records, asks, [{"doc": "sap",
                                                                  "anchor": "99/p1"}]),
    }
    planted = [_holds(out, name, problems_of(*given)) for name, given in cases.items()]
    planted.append(_holds(out, "no unmapped.jsonl", problems_of(records, asks, unmapped,
                                                                 "unmapped.jsonl")))
    return not honest and all(planted)


# ---- the canary scan ---------------------------------------------------------------------


def canary_check(root: Path, out: Out) -> bool:
    folder = _kit(root)
    made = tasks.build(root, folder, _scratch() / "tasks-canary")
    kit_sha = sha256_file(folder / genkits.MANIFEST)
    found = runs.kit_canaries(root, folder, runs.task_texts(made), "R", kit_sha, SEED)
    counts = found.sources()
    kinds = {}
    for label, count in counts.items():
        kind = label.split(":")[0] + ":" + "/".join(label.split(":", 1)[-1].split("/")[:2])
        kinds[kind] = kinds.get(kind, 0) + count
    out(f"{len(found)} canaries from {len(counts)} sources: "
        + ", ".join(f"{kind} {count}" for kind, count in sorted(kinds.items())))
    events = _scratch() / "canary"
    events.mkdir(parents=True, exist_ok=True)

    def read_event(text: str) -> dict:
        return {"type": "user", "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t", "content": text}]}}

    def scan(lines: list[dict], name: str) -> list[canary.Hit]:
        path = events / name
        path.write_text("".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8")
        return canary.scan_transcript(found, path)

    store = natural.store_dir()
    private = _scratch() / "canary-run"
    oracle.write_oracle(folder, private, canary.planted(kit_sha, oracle.ORACLE))
    reads = {
        "gold/decisions.jsonl": folder / "gold" / "decisions.jsonl",
        "gold/docs/sap.md": folder / "gold" / "docs" / "sap.md",
        "gold/oracle.yaml": folder / "gold" / "oracle.yaml",
        "gold/summary.md": folder / "gold" / "summary.md",
        "twin/data/sdtm/ae.json": folder / "twin" / "data" / "sdtm" / "ae.json",
        "twin/gold/ard/reporting-event.jsonl":
            folder / "twin" / "gold" / "ard" / "reporting-event.jsonl",
        "kit.yaml": folder / "kit.yaml",
        "store paragraphs.jsonl": store / "paragraphs.jsonl",
        "the run's private/oracle.json": private / oracle.ORACLE,
    }
    planted = []
    for name, path in reads.items():
        hits = scan([read_event(path.read_text(encoding="utf-8"))], "read.jsonl")
        planted.append(_holds(out, f"a transcript that read {name}",
                              [f"{len(hits)} canaries, e.g. {hits[0].canary.source}"]
                              if hits else []))
    seed_hits = scan([{"type": "assistant", "message": {"content": [
        {"type": "text", "text": f"The seed was {SEED}."}]}}], "seed.jsonl")
    planted.append(_holds(out, "a transcript that names the seed",
                          [hit.line() for hit in seed_hits]))
    workspace = _scratch() / "canary-workspace"
    (workspace / "out").mkdir(parents=True, exist_ok=True)
    line = (folder / "gold" / "decisions.jsonl").read_text(encoding="ascii").splitlines()[0]
    (workspace / "out" / "notes.txt").write_text(f"copied: {line}\n", encoding="ascii")
    planted.append(_holds(out, "a workspace file with a line of gold", [
        hit.line() for hit in canary.scan_files(found, workspace, ["out/notes.txt"])]))
    # What a reader may read and write: the task, the oracle's answers, gold as a reader
    # writes it, the statements. None of it is a canary.
    allowed = []
    for path in sorted(made.folder.rglob("*")):
        if path.is_file():
            text = canary.read_text(path)
            if text is not None:
                allowed.append(read_event(text))
    answers = [item["answer"] for item in oracle.answers(private)]
    records = reader_records(folder, made.keys)
    allowed += [read_event(oracle.ANSWER.format(answer=a)) for a in answers]
    allowed += [read_event(json.dumps(r)) for r in records]
    allowed += [read_event("\n".join(json.dumps(r, sort_keys=True) for r in records))]
    allowed += [read_event("\n".join(json_text(r) for r in records))]
    allowed += [{"type": "assistant", "message": {"content": [{"type": "text", "text": (
        f"The oracle's answer: {a} So I record it.")}]}} for a in answers]
    allowed += [{"type": "assistant", "message": {"content": [{"type": "text", "text": (
        f"I will write: {r['statement']}")}]}} for r in records]
    clean = scan(allowed, "allowed.jsonl")
    out(f"a transcript of {len(allowed)} events with every file of the task, the oracle's "
        f"answers, the records of a reader that reads gold right and their statements: "
        + ("no canary" if not clean else f"{len(clean)} canaries, e.g. {clean[0].line()}"))
    # A reader that writes a wrong value which a statement of the store holds: its record,
    # as the catalog renders it, is no canary; a quote it typed from the store is.
    gold = {(r["id"], r["unit"]): r["value"] for r in genkits.read_decisions(folder)}
    store_items = [json.loads(line) for line in (store / "paragraphs.jsonl").read_text(
        encoding="ascii").splitlines() if line.strip()]
    known = canary.squeeze("\n".join(runs.task_texts(made)))
    item = next(i for i in store_items if (i["entry"], i["unit"]) in made.keys
                and i["value"] != gold.get((i["entry"], i["unit"])) and len(i["value"]) > 1
                and all(canary.squeeze(text) in known for text in runs._texts_of(i["value"])))
    written = [{"id": item["entry"], "unit": item["unit"], "value": item["value"],
                "status": "stated", "class": "document_rule", "statement": item["statement"]}]
    line = json.dumps(written[0], sort_keys=True)
    texts = runs.task_texts(made)
    own = runs.kit_canaries(root, folder, texts, "R", kit_sha, SEED, written)
    out(f"a reader that writes {item['entry']} ({item['unit']}) as {item['value']}, a value "
        "that a statement of the store holds: "
        + ("no canary" if not own.find(line) else f"{len(own.find(line))} canaries"))
    typed = [{**written[0], "statement": (store / "paragraphs.jsonl").read_text(
        encoding="ascii")[:300]}]
    planted += [
        _holds(out, "the same record judged without the reader's records (the case exists)",
               [c.source for c in found.find(line)]),
        _holds(out, "a statement typed from the store", [c.source for c in runs.kit_canaries(
            root, folder, texts, "R", kit_sha, SEED, typed).find(typed[0]["statement"])]),
    ]
    # A reader that writes lines of gold into a text slot of a valid record: the slot holds
    # what it typed, so the lines stay canaries (review of read-2a, finding H1).
    quote_free = [item.text for item in found.items.values()
                  if item.source.startswith("kit:gold/summary.md") and '"' not in item.text
                  and "|" in item.text][:3]
    slotted = [{"id": "ae.related.values", "unit": "mod-ae-emergence",
                "value": {"rule": "stated_list", "values": quote_free}, "status": "stated",
                "class": "document_rule", "statement": "x"}]
    slot_canaries = runs.kit_canaries(root, folder, texts, "R", kit_sha, SEED, slotted)
    planted.append(_holds(out, f"{len(quote_free)} lines of gold/summary.md as the values of "
                          "ae.related.values", [line_ for line_ in quote_free
                                                if slot_canaries.find(line_)]
                          if len(quote_free) == 3 and all(
                              slot_canaries.find(line_) for line_ in quote_free) else []))
    return not clean and not own.find(line) and all(planted) and len(found) > 0


# ---- the dry runs ------------------------------------------------------------------------


def _report(out: Out, made: runs.Run, root: Path, kit_dir: Path) -> None:
    for line in runs.lines(made):
        out(line)
    out("score (report only):")
    for line in runs.score(root, kit_dir, made.folder):
        out(f"  {line}")


def _arm(arm: str) -> Callable[[Path, Out], bool]:
    def check(root: Path, out: Out) -> bool:
        folder = _kit(root)
        made = runs.run(root, folder, arm, _scratch() / "tasks", _scratch() / "runs",
                        seed=SEED)
        _report(out, made, root, folder)
        return made.passed
    return check


def arm_s(root: Path, out: Out) -> bool:
    return _arm("S")(root, out)


def arm_c(root: Path, out: Out) -> bool:
    return _arm("C")(root, out)


def stub_plan(kit_dir: Path, keys: tuple[tuple[str, str], ...], where: Path) -> Path:
    """A plan for the stub reader: the records of a reader that reads gold right, the
    asks of the decisions gold marks asked, and bin/check."""
    records = reader_records(kit_dir, keys)
    plan = {"records": records, "unmapped": [], "check": True,
            "asks": [{"decision": r["id"], "unit": r["unit"],
                      "question": f"What does the study decide for {r['id']}?"}
                     for r in records if r["status"] == "asked"],
            "usage": {"input_tokens": 10, "output_tokens": 20,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
            "model_usage": {record.MODEL: {"inputTokens": 10, "outputTokens": 20,
                                           "cacheCreationInputTokens": 0,
                                           "cacheReadInputTokens": 0}}}
    path = where / "stub-plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return path


def arm_r_stub(root: Path, out: Out) -> bool:
    folder = _kit(root)
    keys = tasks.build(root, folder, _scratch() / "tasks").keys
    plan = stub_plan(folder, keys, _scratch() / "stub")
    made = runs.run(root, folder, "R", _scratch() / "tasks", _scratch() / "runs",
                    reader=adapter.stub_reader(), seed=SEED,
                    env={"SPECFIRST_STUB_PLAN": str(plan)}, name="R-stub")
    _report(out, made, root, folder)
    wanted = {(r["id"], r["unit"]) for r in reader_records(folder, keys)
              if r["status"] == "asked"}
    answered = {(a["decision"], a["unit"]) for a in made.record["asks"] if a["answered"]}
    out(f"the stub asked through bin/ask about {sorted(answered)}; gold marks asked "
        f"{sorted(wanted)}")
    # The check of a kept run, on the stub run kept into a scratch store.
    store = _scratch() / "kept"
    kept = runs.keep(made, _scratch() / "tasks" / made.record["task"]["id"], folder, root,
                     store)
    found, hits, _ = runs.check(root, kept, folder, _scratch() / "tasks-kept", SEED)
    out("the stub run kept and checked again: "
        + ("no problem" if not (found or hits) else "; ".join(found + [h.line() for h in hits])))
    changed = _scratch() / "kept-planted"
    shutil.copytree(kept, changed, dirs_exist_ok=True)
    told = json.loads((changed / runs.TASK_JSON).read_text(encoding="ascii"))
    told["manifest"][tasks.TASK_FILE] = "0" * 64
    (changed / runs.TASK_JSON).write_text(json.dumps(told), encoding="ascii")
    leaked = _scratch() / "kept-leak"
    shutil.copytree(kept, leaked, dirs_exist_ok=True)
    with open(leaked / adapter.TRANSCRIPT, "a", encoding="ascii") as handle:
        handle.write(json.dumps({"type": "user", "message": {"content": [
            {"type": "tool_result", "content": (folder / "gold" / "summary.md").read_text(
                encoding="ascii")}]}}) + "\n")
    over = _scratch() / "kept-over"
    shutil.copytree(kept, over, dirs_exist_ok=True)
    rec = json.loads((over / runs.RUN_JSON).read_text(encoding="ascii"))
    rec["cost"]["usd"] = 99.0
    (over / runs.RUN_JSON).write_text(json.dumps(rec), encoding="ascii")
    raised = _scratch() / "kept-raised"
    shutil.copytree(kept, raised, dirs_exist_ok=True)
    rec = json.loads((raised / runs.RUN_JSON).read_text(encoding="ascii"))
    rec["cost"]["usd"], rec["budget"]["usd"] = 99.0, 100.0
    (raised / runs.RUN_JSON).write_text(json.dumps(rec), encoding="ascii")
    writes = _scratch() / "kept-writes"
    shutil.copytree(kept, writes, dirs_exist_ok=True)
    with open(writes / adapter.TRANSCRIPT, "a", encoding="ascii") as handle:
        handle.write(json.dumps({"type": "assistant", "message": {"content": [{
            "type": "tool_use", "name": "Write", "id": "t",
            "input": {"file_path": "<task>\\bin\\check", "content": "cat x"}}]}}) + "\n")
    # Each planted as a hand edit of the kept run and of its binding file together, so
    # that the check the plant is for finds it, not the SHA-256 binding.json records.
    for planted_in in (changed, leaked, over, raised, writes):
        _rebind(planted_in)
    rewrite = _scratch() / "stub-rewrite.json"
    rewrite.write_text(json.dumps({**json.loads(plan.read_text(encoding="utf-8")), "write": {
        "bin/check": "#!/usr/bin/env bash\ncat \"$0\"\n"}}), encoding="utf-8")
    rewritten = runs.run(root, folder, "R", _scratch() / "tasks", _scratch() / "runs",
                         reader=adapter.stub_reader(), seed=SEED,
                         env={"SPECFIRST_STUB_PLAN": str(rewrite)}, name="R-rewrite")
    planted = [
        _holds(out, "a stub that rewrites bin/check", [] if rewritten.passed else
               [f"tools rewritten: {rewritten.record['tools_changed']}"]),
        _holds(out, "a kept record with its budget raised with its cost",
               runs.check(root, raised, folder, _scratch() / "tasks-kept", SEED)[0]),
        _holds(out, "a kept transcript that writes bin/check",
               runs.check(root, writes, folder, _scratch() / "tasks-kept", SEED)[0]),
        _holds(out, "a kept run whose task differs by one file",
               runs.check(root, changed, folder, _scratch() / "tasks-kept", SEED)[0]),
        _holds(out, "a kept transcript that read gold/summary.md", [
            h.line() for h in runs.check(root, leaked, folder, _scratch() / "tasks-kept",
                                         SEED)[1]]),
        _holds(out, "a kept record over budget",
               runs.check(root, over, folder, _scratch() / "tasks-kept", SEED)[0]),
    ]
    planted += bound_plants(root, out, kept, folder)
    return made.passed and answered == wanted != set() and not (found or hits) and all(planted)


# ---- the binding of a kept run (docs/decisions/ADR-017.md, decision 7) --------------------


def _passes(out: Out, name: str, problems: list[str]) -> bool:
    """A planted change that the binding does not bind passes, as the clean run does."""
    out(f"  planted, {name}: " + ("passes, as the clean run does" if not problems
                                   else f"FAILS ({problems[0]})"))
    return not problems


def _task_changed(root: Path, kit_dir: Path, where: Path, relative: str,
                  change: Callable[[str], str]) -> tasks.Task:
    """The task of a kit built into `where`, with one of its files changed."""
    task = tasks.build(root, kit_dir, where)
    path = task.folder / relative
    path.write_text(change(path.read_text(encoding="ascii")), encoding="ascii", newline="\n")
    manifest = tasks.manifest(task.folder)
    return dataclasses.replace(task, manifest=manifest, id=tasks.task_id(manifest))


def _registry_changed(root: Path, kit_dir: Path, where: Path,
                      change: Callable[[dict], None]) -> tasks.Task:
    """The task of a kit built into `where`, with its registry.json changed."""
    def edit(text: str) -> str:
        data = json.loads(text)
        change(data)
        return json_text(data) + "\n"
    return _task_changed(root, kit_dir, where, binding.REGISTRY, edit)


def _kit_changed(kit_dir: Path, name: str, change: Callable[[Path, dict], None]) -> Path:
    """A copy of the kit, its files and its kit.yaml changed."""
    copy_of = _scratch() / "kits-planted" / name
    shutil.rmtree(copy_of, ignore_errors=True)
    shutil.copytree(kit_dir, copy_of)
    manifest = genkits.read_manifest(copy_of)
    change(copy_of, manifest)
    genkits.write_manifest(copy_of, manifest)
    return copy_of


def _kept_changed(kept: Path, name: str, change: Callable[[Path], None],
                  rebind: bool = True) -> Path:
    """A copy of a kept run, changed; with `rebind`, its binding file records the
    changed files, as a hand edit of the run and of its binding file would."""
    copy_of = _scratch() / "kept-bound" / name
    shutil.rmtree(copy_of, ignore_errors=True)
    shutil.copytree(kept, copy_of)
    change(copy_of)
    if rebind:
        _rebind(copy_of)
    return copy_of


def _rebind(kept: Path) -> None:
    """The binding file of a kept run made again for the files it holds now."""
    made = binding.read(kept) or {}
    made["files"] = binding.kept_files(kept)
    binding.save(kept, made)


def _decisions_changed(change: Callable[[list[dict]], list[dict]]) -> Callable[[Path], None]:
    def edit(kept: Path) -> None:
        path = kept / runs.WORKSPACE / tasks.OUT / "decisions.jsonl"
        lines = [json.loads(line) for line in path.read_text(encoding="ascii").splitlines()
                 if line.strip()]
        path.write_text("".join(json.dumps(line, sort_keys=True) + "\n"
                                for line in change(lines)), encoding="ascii", newline="\n")
    return edit


def _other_percent_format(lines: list[dict]) -> list[dict]:
    changed = copy.deepcopy(lines)
    for line in changed:
        if line.get("id") == "tfl.percent.format":
            rule = line["value"]["rule"]
            line["value"]["rule"] = ("one_decimal_always" if rule != "one_decimal_always"
                                     else "one_decimal_zero_blank")
    return changed


def bound_plants(root: Path, out: Out, kept: Path, kit_dir: Path,
                 seed: str | None = SEED) -> list[bool]:
    """The plants of ADR-017, decision 7, on the stub run kept into a scratch store: each
    change the binding binds fails the check, each change it does not bind passes."""
    where = _scratch() / "tasks-bound"

    def check(kept_: Path = kept, kit_: Path = kit_dir,
              task: tasks.Task | None = None) -> list[str]:
        found, hits = runs.held(root, kept_, kit_, task or tasks.build(root, kit_, where),
                                seed)
        return found + [hit.line() for hit in hits]

    def reached_changed(data: dict) -> None:
        data["methods"]["count.subjects"]["title"] += " (planted)"

    def model_added(data: dict) -> None:
        added = copy.deepcopy(data["methods"]["model.ancova.lsmeans"])
        added["id"] = "model.planted"
        data["methods"]["model.planted"] = added

    def kit_file(folder: Path, manifest: dict) -> None:
        path = folder / "gold" / "design.yaml"
        path.write_text(path.read_text(encoding="ascii") + "# planted\n", encoding="ascii",
                        newline="\n")
        manifest["files"]["gold/design.yaml"] = sha256_file(path)

    def engines(folder: Path, manifest: dict) -> None:
        manifest["pins"]["engines"] = {name: f"{version}-planted" for name, version in
                                       manifest["pins"]["engines"].items()}

    added = _registry_changed(root, kit_dir, _scratch() / "tasks-added", model_added)

    def registry_pin(folder: Path, manifest: dict) -> None:
        manifest["pins"]["registry_sha256"] = added.manifest[binding.REGISTRY]

    def without_entry(folder: Path) -> None:
        made = binding.read(folder) or {}
        del made["registry"]["reached"]["count.subjects"]
        binding.save(folder, made)

    def private_leak(folder: Path) -> None:
        made = json.loads((folder / runs.RUN_JSON).read_text(encoding="ascii"))
        with open(folder / adapter.TRANSCRIPT, "a", encoding="ascii") as handle:
            handle.write(json.dumps({"type": "user", "message": {"content": [{
                "type": "tool_result", "content": canary.planted(
                    made["kit"]["kit_yaml_sha256"], oracle.ORACLE)}]}}) + "\n")

    def record_changed(change: Callable[[dict], None]) -> Callable[[Path], None]:
        def edit(folder: Path) -> None:
            made = json.loads((folder / runs.RUN_JSON).read_text(encoding="ascii"))
            change(made)
            (folder / runs.RUN_JSON).write_text(json.dumps(made, indent=1, sort_keys=True)
                                                + "\n", encoding="ascii", newline="\n")
        return edit

    def message(made: dict) -> None:
        made["end"]["message"] = f"{made['end']['message']} (planted)"

    def outputs_named(made: dict) -> None:
        made["outputs"]["decisions.jsonl"]["sha256"] = "0" * 64

    def kit_key(folder: Path) -> None:
        private_leak(folder)
        record_changed(lambda made: made["kit"].update(kit_yaml_sha256="0" * 64))(folder)

    def kit_file_alone(folder: Path, manifest: dict) -> None:
        path = folder / "gold" / "design.yaml"
        path.write_text(path.read_text(encoding="ascii") + "# planted\n", encoding="ascii",
                        newline="\n")

    def entry_more(folder: Path) -> None:
        made = binding.read(folder) or {}
        made["registry"]["reached"]["test.chisq"] = "0" * 64
        binding.save(folder, made)

    skill = f"{tasks.KNOWLEDGE}/{tasks.CORE}/SKILL.md"
    other_engines = _kit_changed(kit_dir, "engines", engines)
    return [
        _holds(out, f"a file of the task built now changed ({skill}), the kept run as it is",
               check(task=_task_changed(root, kit_dir, _scratch() / "tasks-skill", skill,
                                        lambda text: text + "\nPlanted.\n"))),
        _holds(out, "a kept record edited where no other check reads, its binding file not "
               "made again", check(kept_=_kept_changed(kept, "edited", record_changed(message),
                                                       rebind=False))),
        _holds(out, "a kept record that names other outputs than the transcript writes, its "
               "binding file made again", check(kept_=_kept_changed(
                   kept, "named", record_changed(outputs_named)))),
        _holds(out, "an entry the slice reaches, changed (count.subjects)", check(
            task=_registry_changed(root, kit_dir, _scratch() / "tasks-reached",
                                   reached_changed))),
        _holds(out, "a file of the kit changed (gold/design.yaml, and its line in kit.yaml)",
               check(kit_=_kit_changed(kit_dir, "file", kit_file))),
        _holds(out, "a file of the kit changed (gold/design.yaml), and not its line in kit.yaml",
               check(kit_=_kit_changed(kit_dir, "file-alone", kit_file_alone))),
        _holds(out, "a binding file that holds an entry the slice does not reach (test.chisq)",
               check(kept_=_kept_changed(kept, "more", entry_more, rebind=False))),
        _holds(out, "a kept run without binding.json", check(kept_=_kept_changed(
            kept, "unbound", lambda folder: (folder / binding.BINDING).unlink(),
            rebind=False))),
        _holds(out, "a binding file whose entries lack count.subjects, which the slice "
               "reaches", check(kept_=_kept_changed(kept, "lacking", without_entry,
                                                    rebind=False))),
        _holds(out, "a kept decisions.jsonl with one record left out (K4), its binding file "
               "made again", check(kept_=_kept_changed(kept, "left-out", _decisions_changed(
                   lambda lines: lines[:-1])))),
        _holds(out, "a kept decisions.jsonl with tfl.percent.format changed to the other "
               "valid value (K4), its binding file made again", check(kept_=_kept_changed(
                   kept, "percent", _decisions_changed(_other_percent_format)))),
        _passes(out, "an entry of kind model added to the registry, and registry_sha256 of "
                "kit.yaml with it", check(kit_=_kit_changed(kit_dir, "registry", registry_pin),
                                          task=added)),
        _passes(out, "the versions of the engines changed in `pins` of kit.yaml",
                check(kit_=other_engines)),
        _holds(out, "the versions of the engines changed in `pins` of kit.yaml, and a kept "
               "transcript that holds the canary of the run's private/oracle.json", check(
                   kept_=_kept_changed(kept, "private", private_leak), kit_=other_engines)),
        _holds(out, "that canary in a kept transcript, and the record's kit.yaml SHA-256 "
               "edited, its binding file made again", check(
                   kept_=_kept_changed(kept, "kit-key", kit_key))),
    ]


def kept_runs() -> list[Path]:
    return sorted(path for path in runs.STORE.glob("R-*") if (path / runs.RUN_JSON).is_file())


def arm_r(root: Path, out: Out) -> bool:
    folder = _kit(root)
    kept = kept_runs()
    if not kept:
        out(f"no dry run of arm R is kept in {runs.STORE.relative_to(root).as_posix()}: it "
            "needs the Claude Code CLI logged in (docs/decisions/ADR-010.md, For the owner)")
        return False
    passed = True
    for path in kept:
        made = json.loads((path / runs.RUN_JSON).read_text(encoding="ascii"))
        found, hits, rebuilt = runs.check(root, path, folder, _scratch() / "tasks-r", SEED)
        spent = made["cost"]
        out(f"kept run {path.name}: arm {made['arm']}, reader {made['reader']['adapter']}, "
            f"model {made['reader']['model']}, used {made['reader']['models_used']}, "
            f"CLI {made['reader']['cli_version']}")
        bound = not any(line.startswith(("task:", "registry:", "kit:", "binding:", "kept:"))
                        for line in found)
        out(f"  task {made['task']['id']}, built again now: {rebuilt.id}"
            + (", the same on every bound part (ADR-017)" if bound else
               ", NOT the same on every bound part"))
        out(f"  cost: {spent['turns']} turns, {spent['wall_seconds']} s, tokens "
            f"{spent['tokens']}, USD {spent['usd']:.4f} (CLI {spent['usd_cli']}); budget "
            f"{made['budget']}")
        out(f"  asks: {[(a['decision'], a['unit'], a['answered']) for a in made['asks']]}")
        out(f"  permission denials: {len(made['end']['permission_denials'])}")
        for line in found + [hit.line() for hit in hits]:
            out(f"  {line}")
        out("  a task that agrees with the task it read on every bound part, within budget, "
            "valid output files that are the run's own, canary scan clean against the "
            "canaries of the kit written now: " + ("yes" if not (found or hits) else "NO"))
        out("  score (report only):")
        for line in runs.score(root, folder, path):
            out(f"    {line}")
        passed = passed and not (found or hits) and made["reader"]["adapter"] == "claude-code"
    return passed


def done(root: Path, out: Out) -> bool:
    """The last check: the scratch folder of the gate (kit, tasks, runs) is removed."""
    cleanup()
    out("the kit, the tasks and the runs of the gate are removed")
    return True
