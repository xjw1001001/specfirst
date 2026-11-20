"""The reader harness of read-2a (specfirst.harness; docs/decisions/ADR-010.md).

One kit is written once for the module, without the R engine: kit 4 of a set
of a seed of its own (train, the ask demo). The tests hold what must be true
of every kit, and each check against a planted defect (rule R5). No test
calls a model: arm R runs the stub reader.
"""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

import pytest

from specfirst.compile import catalog as catalogs
from specfirst.gen import kits as genkits
from specfirst.gen import natural
from specfirst.harness import (
    adapter,
    binding,
    canary,
    gate,
    knowledge,
    oracle,
    outputs,
    record,
    runs,
)
from specfirst.harness import task as tasks

SEED = "unit-harness"
NUMBER = 4


@pytest.fixture(scope="module")
def kit_dir(root, tmp_path_factory):
    out = tmp_path_factory.mktemp("harness-kits") / f"kit-{NUMBER:03d}"
    genkits.generate(root, genkits.kit_seed(SEED, NUMBER), out, genkits.split_of(NUMBER),
                     with_r=False, number=NUMBER)
    return out


@pytest.fixture(scope="module")
def scratch(tmp_path_factory):
    return tmp_path_factory.mktemp("harness-scratch")


@pytest.fixture(scope="module")
def made(root, kit_dir, scratch):
    return tasks.build(root, kit_dir, scratch / "tasks")


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


# ---- canary ----------------------------------------------------------------------------


def test_a_long_line_gives_pieces_and_a_short_one_none():
    assert canary.pieces("short line") == []
    assert canary.pieces("x" * 30) == ["x" * 30]
    long = "".join(chr(ord("a") + n % 26) for n in range(200))
    assert canary.pieces(long) == [long[0:80], long[80:160], long[160:200]]


def test_the_finder_finds_every_string_that_stands_in_a_text():
    items = ["the quick brown fox jumps over", "a lazy dog sleeps under the tree",
             "the quick brown fox runs away now"]
    finder = canary.Finder(items)
    assert finder.found("so the quick brown fox runs away now, said he") == {items[2]}
    assert finder.found("nothing here at all, nothing at all") == set()


def test_what_a_reader_may_read_or_write_is_no_canary(tmp_path):
    source = tmp_path / "gold.txt"
    source.write_text("a line that only gold has, nowhere else\n"
                      "[1/s1] The statement that a reader writes itself.\n"
                      "a line that the task folder holds as well\n", encoding="ascii")
    found = canary.build([("gold", source)], ["here: a line that the task folder holds as well"],
                         ["The statement that a reader writes itself."],
                         [("seed", "seed-1")])
    assert sorted(item.text for item in found.items.values()) == [
        "a line that only gold has, nowhere else", "seed-1"]


def test_the_scan_decodes_the_events_of_a_transcript(tmp_path):
    source = tmp_path / "gold.jsonl"
    source.write_text('{"binds":["adam:ADSL.TRT01P"],"id":"x.y","quote":"say \\"hi\\""}\n',
                      encoding="ascii")
    found = canary.build([("gold", source)], [], [], [])
    transcript = tmp_path / "t.jsonl"
    event = {"type": "user", "message": {"content": [
        {"type": "tool_result", "content": "1\t" + source.read_text(encoding="ascii")}]}}
    transcript.write_text(json.dumps(event) + "\n" + json.dumps({"type": "result"}) + "\n",
                          encoding="ascii")
    hits = canary.scan_transcript(found, transcript)
    assert [hit.where for hit in hits] == ["transcript:1"]


def test_a_planted_canary_is_a_function_of_the_kit_and_the_file():
    assert canary.planted("a" * 64, "private/oracle.json") == canary.planted(
        "a" * 64, "private/oracle.json")
    assert canary.planted("a" * 64, "private/oracle.json") != canary.planted(
        "b" * 64, "private/oracle.json")


# ---- record ----------------------------------------------------------------------------


def test_a_model_id_with_a_date_takes_the_price_of_its_name():
    assert record.price("claude-haiku-4-5-20251001") == record.PRICES["claude-haiku-4-5"]
    assert record.price("claude-opus-5-5") == record.PRICES["claude-opus-5-5"]
    assert record.price("claude-unknown") is None


def test_dollars_are_computed_from_the_tokens():
    result = {"usage": {"cache_creation": {"ephemeral_1h_input_tokens": 0}},
              "modelUsage": {"claude-opus-5-5": {"inputTokens": 1_000_000,
                                                 "outputTokens": 1_000_000,
                                                 "cacheCreationInputTokens": 1_000_000,
                                                 "cacheReadInputTokens": 1_000_000}}}
    assert record.dollars(result) == (4.0 + 20.0 + 5.0 + 0.2, [])
    result["usage"]["cache_creation"]["ephemeral_1h_input_tokens"] = 1
    assert record.dollars(result)[0] == pytest.approx(4.0 + 20.0 + 8.0 + 0.2)
    assert record.dollars({"modelUsage": {"other": {"inputTokens": 5}}}) == (0.0, ["other"])


def test_a_record_over_any_limit_is_over_budget():
    honest = gate._honest_record()
    assert record.over_budget(honest) == []
    for path, value in ((("cost", "turns"), 101), (("cost", "usd"), 11.0),
                        (("cost", "wall_seconds"), 99999), (("end", "is_error"), True),
                        (("end", "stopped"), True), (("end", "result"), False)):
        planted = copy.deepcopy(honest)
        planted[path[0]][path[1]] = value
        assert record.over_budget(planted), path


# ---- adapter ---------------------------------------------------------------------------


def test_the_command_line_and_the_settings_are_those_of_adr_010(tmp_path):
    protected = [tmp_path / "kits", tmp_path / "runs"]
    for windows, reader in ((False, adapter.Reader(("claude",))),
                            (True, adapter.Reader(("node.exe", "cli.js")))):
        value = adapter.settings(protected, windows)
        argv = adapter.command(reader, tmp_path / "settings.json", record.BUDGETS["R"])
        assert adapter.command_problems(argv, value, protected, windows) == []
        assert argv[argv.index("--model") + 1] == "claude-opus-5-5"
        assert argv[argv.index("--max-turns") + 1] == "100"
    fewer = {"permissions": {"deny": value["permissions"]["deny"][5:]}}
    assert adapter.command_problems(argv, fewer, protected, True)
    assert adapter.command_problems([*argv, "--add-dir", "/"], value, protected, True)


def test_a_windows_path_of_a_drive_and_of_the_wsl_share(monkeypatch):
    monkeypatch.setenv("WSL_DISTRO_NAME", "Ubuntu-24.04")
    assert adapter.windows_path(Path("/mnt/c/Users/x/task")) == "C:\\Users\\x\\task"
    assert adapter.rule_paths(Path("/mnt/d/work"), True) == ["//d/work", "//D:/work"]
    assert adapter.rule_paths(Path("/root/kits"), True) == [
        "//wsl.localhost/Ubuntu-24.04/root/kits", "//wsl$/Ubuntu-24.04/root/kits"]


def test_the_stub_refuses_a_command_line_that_is_not_the_adapters(tmp_path, capsys):
    from specfirst.harness import stub

    settings = tmp_path / "settings.json"
    settings.write_text(json.dumps(adapter.settings([tmp_path / "kits"], False)),
                        encoding="ascii")
    argv = adapter.command(adapter.Reader(("x",)), settings, record.BUDGETS["R"])[1:]
    stub.main([part for part in argv if part != "--strict-mcp-config"])
    result = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert result["is_error"] and "not the adapter's" in result["result"]


# ---- task --------------------------------------------------------------------------------


def test_a_task_is_deterministic_and_holds_only_what_a_reader_may_see(root, kit_dir, made,
                                                                      scratch):
    again = tasks.build(root, kit_dir, scratch / "tasks-again")
    assert (again.id, again.manifest) == (made.id, made.manifest)
    assert tasks.problems(made.folder, kit_dir) == []
    assert not any(path.startswith(("gold", "twin")) or path in ("kit.yaml", "study.json")
                   for path in made.manifest)
    assert made.knowledge == sorted(f"knowledge/{name}/SKILL.md" for name in
                                    (tasks.CORE, *made.units))
    assert len(made.keys) == 22
    kit_id = genkits.read_manifest(kit_dir)["id"]
    assert kit_id not in (made.folder / tasks.TASK_FILE).read_text(encoding="ascii")


def test_a_task_with_a_file_of_gold_or_an_extra_file_is_refused(kit_dir, made, tmp_path):
    copied = tmp_path / "task"
    shutil.copytree(made.folder, copied)
    shutil.copyfile(kit_dir / "gold" / "decisions.jsonl", copied / "inputs" / "docs" / "d.jsonl")
    (copied / "extra.md").write_text("x\n", encoding="ascii")
    found = tasks.problems(copied, kit_dir)
    assert any("gold/decisions.jsonl" in problem for problem in found)
    assert any(problem.startswith("extra.md") for problem in found)


def test_stage_t_gives_the_table_decisions_and_the_adam_of_gold(root, kit_dir, scratch):
    staged = tasks.build(root, kit_dir, scratch / "tasks-t", stage="T", condition="catalog")
    assert staged.units == ("tfl-ae-summary",) and len(staged.keys) == 7
    assert sorted(p for p in staged.manifest if p.startswith(tasks.ADAM)) == [
        "inputs/data/adam/adae.parquet", "inputs/data/adam/adsl.parquet"]
    assert not any(p.startswith(tasks.SDTM) for p in staged.manifest)
    assert tasks.problems(staged.folder, kit_dir) == []


def test_a_task_folder_inside_a_checkout_is_refused(root, kit_dir):
    with pytest.raises(tasks.TaskError):
        tasks.build(root, kit_dir, root / "build" / "tasks")


# ---- oracle ------------------------------------------------------------------------------


def test_the_oracle_answers_exactly_what_its_file_lists(root, kit_dir, tmp_path):
    found, seen = gate.oracle_problems(root, kit_dir, oracle.ask, tmp_path / "honest")
    assert found == []
    assert any(line.endswith(": answered") for line in seen)
    planted, _ = gate.oracle_problems(root, kit_dir, gate._ask_everything, tmp_path / "planted")
    assert planted


# ---- outputs -----------------------------------------------------------------------------


def test_the_output_files_of_a_reader_that_reads_gold_right_are_valid(kit_dir, made, catalog,
                                                                       tmp_path):
    records = gate.reader_records(kit_dir, made.keys)
    asks = [{"decision": r["id"], "unit": r["unit"], "question": "q"} for r in records
            if r["status"] == "asked"]
    for name, lines in (("decisions.jsonl", records), ("questions.jsonl", asks),
                        ("unmapped.jsonl", [])):
        (tmp_path / name).write_text("".join(json.dumps(r) + "\n" for r in lines),
                                     encoding="ascii")
    documents = outputs.task_documents(made.folder)
    assert outputs.problems(tmp_path, catalog, made.keys, documents, asks) == []
    planted = copy.deepcopy(records)
    planted[0]["identifiable"] = "separated"
    planted[1]["value"] = {"rule": "nonsense"}
    (tmp_path / "decisions.jsonl").write_text("".join(json.dumps(r) + "\n" for r in planted),
                                              encoding="ascii")
    found = outputs.problems(tmp_path, catalog, made.keys, documents, asks)
    assert any("identifiable" in problem for problem in found)
    assert any("not one of" in problem for problem in found)
    (tmp_path / "unmapped.jsonl").unlink()
    assert "unmapped.jsonl: missing" in outputs.problems(tmp_path, catalog, made.keys,
                                                         documents, asks)


# ---- knowledge ---------------------------------------------------------------------------


def test_the_reading_notes_are_their_rendering_and_leak_nothing(root, kit_dir):
    secrets = knowledge.secrets_of(kit_dir, genkits.kit_seed(SEED, NUMBER))
    paragraphs = knowledge.store_paragraphs(natural.store_dir())
    assert knowledge.problems(root, secrets, paragraphs) == []
    text = tasks.skill_path(root, "mod-treatment").read_text(encoding="ascii")
    assert knowledge.leaks(text + f" see {secrets[0]}", secrets, paragraphs)
    assert knowledge.format_problems("mod-treatment", text.replace("name: mod-treatment\n", ""))


# ---- runs ----------------------------------------------------------------------------------


def test_arm_s_and_arm_c_run_through_the_harness(root, kit_dir, scratch):
    seed = genkits.kit_seed(SEED, NUMBER)
    standard = runs.run(root, kit_dir, "S", scratch / "tasks", scratch / "runs", seed=seed)
    assert standard.passed, runs.lines(standard)
    assert standard.record["outputs"]["decisions.jsonl"]["lines"] == 0
    control = runs.run(root, kit_dir, "C", scratch / "tasks", scratch / "runs", seed=seed)
    assert control.passed, runs.lines(control)
    asked = {(a["decision"], a["unit"]) for a in control.record["asks"]}
    listed = {(a["decision"], a["unit"]) for a in oracle.answers(control.folder)}
    assert asked == listed


def test_arm_r_with_the_stub_reader_and_its_kept_run(root, kit_dir, scratch):
    seed = genkits.kit_seed(SEED, NUMBER)
    keys = tasks.build(root, kit_dir, scratch / "tasks").keys
    plan = gate.stub_plan(kit_dir, keys, scratch / "stub")
    made = runs.run(root, kit_dir, "R", scratch / "tasks", scratch / "runs",
                    reader=adapter.stub_reader(), seed=seed,
                    env={"SPECFIRST_STUB_PLAN": str(plan)}, name="R-stub")
    assert made.passed, runs.lines(made)
    assert made.record["reader"]["adapter"] == "stub"
    assert made.record["cost"]["usd"] > 0
    asked = {(r["id"], r["unit"]) for r in gate.reader_records(kit_dir, keys)
             if r["status"] == "asked"}
    assert asked and {(a["decision"], a["unit"]) for a in made.record["asks"]
                      if a["answered"]} == asked
    kept = runs.keep(made, scratch / "tasks" / made.record["task"]["id"], kit_dir, root,
                     scratch / "kept")
    text = (kept / adapter.TRANSCRIPT).read_text(encoding="ascii")
    assert str(scratch) not in text and "<task>" in text
    found, hits, _ = runs.check(root, kept, kit_dir, scratch / "tasks-kept", seed)
    assert (found, hits) == ([], [])
    leaked = scratch / "kept-leak"
    shutil.copytree(kept, leaked)
    with open(leaked / adapter.TRANSCRIPT, "a", encoding="ascii") as handle:
        handle.write(json.dumps({"type": "user", "message": {"content": [{
            "type": "tool_result", "content": (kit_dir / "gold" / "summary.md").read_text(
                encoding="ascii")}]}}) + "\n")
    assert runs.check(root, leaked, kit_dir, scratch / "tasks-kept", seed)[1]


def test_a_reader_that_reads_gold_is_caught_by_the_scan(root, kit_dir, scratch):
    plan = scratch / "leak-plan.json"
    plan.write_text(json.dumps({"read": [str(kit_dir / "gold" / "decisions.jsonl")],
                                "records": [], "unmapped": []}), encoding="ascii")
    made = runs.run(root, kit_dir, "R", scratch / "tasks", scratch / "runs",
                    reader=adapter.stub_reader(), env={"SPECFIRST_STUB_PLAN": str(plan)},
                    name="R-leak")
    assert not made.passed and made.hits
    assert any(hit.canary.source.startswith("kit:gold/decisions.jsonl") for hit in made.hits)


def test_a_reader_that_runs_too_long_is_stopped(root, kit_dir, scratch):
    plan = scratch / "slow-plan.json"
    plan.write_text(json.dumps({"sleep": 30, "records": [], "unmapped": []}), encoding="ascii")
    made = runs.run(root, kit_dir, "R", scratch / "tasks", scratch / "runs",
                    reader=adapter.stub_reader(), env={"SPECFIRST_STUB_PLAN": str(plan)},
                    budget=record.Budget(10, 3, 1.0), name="R-slow")
    assert made.record["end"]["stopped"] and not made.passed
    assert any("time limit" in problem for problem in made.record["over_budget"])


def test_the_tool_wrappers_call_the_harness_and_keep_msys_from_rewriting_paths(made, tmp_path):
    folder = tmp_path / "task"
    shutil.copytree(made.folder, folder)
    runs.write_tools(folder, tmp_path / "run", windows=True)
    text = (folder / "bin" / "ask").read_text(encoding="ascii")
    assert "MSYS_NO_PATHCONV=1" in text and "'wsl.exe'" in text and "'ask'" in text
    # The run and the task come last: a reader cannot point the tool at another folder.
    assert text.index('"$@"') < text.index("'--run'") < text.index("'--task'")
    runs.write_tools(folder, tmp_path / "run", windows=False)
    assert "wsl.exe" not in (folder / "bin" / "check").read_text(encoding="ascii")


def test_what_the_reader_writes_into_out_is_scanned_not_allowed(root, kit_dir, scratch):
    """The canaries come from the task as it was built: a line of gold that the reader
    copies into out/ is a hit (an earlier version took the task folder after the run, out/
    included, as the text a reader may read)."""
    line = (kit_dir / "gold" / "decisions.jsonl").read_text(encoding="ascii").splitlines()[0]
    plan = scratch / "copy-plan.json"
    plan.write_text(json.dumps({"records": [], "unmapped": [],
                                "write": {"out/notes.txt": f"copied: {line}\n"}}),
                    encoding="ascii")
    made = runs.run(root, kit_dir, "R", scratch / "tasks", scratch / "runs",
                    reader=adapter.stub_reader(), env={"SPECFIRST_STUB_PLAN": str(plan)},
                    name="R-copy")
    assert any(hit.where == "workspace:out/notes.txt" for hit in made.hits)


def _store_value(made_task, kit_dir):
    """A value that a statement of the store holds, for a decision of the task, other
    than the kit's gold value, whose slot texts the task holds (a reader could have them
    from its task)."""
    gold = {(r["id"], r["unit"]): r["value"] for r in genkits.read_decisions(kit_dir)}
    known = canary.squeeze("\n".join(runs.task_texts(made_task)))
    for line in (natural.store_dir() / "paragraphs.jsonl").read_text(
            encoding="ascii").splitlines():
        item = json.loads(line)
        key = (item["entry"], item["unit"])
        if key in made_task.keys and item["value"] != gold.get(key) and len(
                item["value"]) > 1 and all(canary.squeeze(text) in known
                                           for text in runs._texts_of(item["value"])):
            return key, item["value"], item["statement"]
    raise AssertionError("no such statement in the store")


def test_a_wrong_value_that_the_store_states_is_no_canary(root, kit_dir, made, catalog):
    key, value, statement = _store_value(made, kit_dir)
    kit_sha = runs.sha256_file(kit_dir / "kit.yaml")
    written = [{"id": key[0], "unit": key[1], "value": value, "status": "stated",
                "class": "document_rule", "statement": statement}]
    line = json.dumps(written[0], sort_keys=True)
    plain = runs.kit_canaries(root, kit_dir, runs.task_texts(made), "R", kit_sha, None)
    assert plain.find(line), "the case exists: without the reader's records it is a hit"
    own = runs.kit_canaries(root, kit_dir, runs.task_texts(made), "R", kit_sha, None,
                            written)
    assert own.find(line) == []
    # What the reader typed itself is not allowed: a quote that copies the store is a hit.
    copied = [{**written[0], "citations": [{"doc": "sap", "anchor": "1/p1", "quote": (
        natural.store_dir() / "paragraphs.jsonl").read_text(encoding="ascii")[:400]}]}]
    assert runs.kit_canaries(root, kit_dir, runs.task_texts(made), "R", kit_sha, None,
                             copied).find(copied[0]["citations"][0]["quote"])


# ---- the findings of the review of read-2a ------------------------------------------------


def test_lines_of_gold_in_a_text_slot_stay_canaries(root, kit_dir, made):
    """H1: a slot of text holds what the reader typed; a line of gold written there
    allows nothing, while a slot value that the task holds does."""
    kit_sha = runs.sha256_file(kit_dir / "kit.yaml")
    texts = runs.task_texts(made)
    plain = runs.kit_canaries(root, kit_dir, texts, "R", kit_sha, None)
    lines = [item.text for item in plain.items.values()
             if item.source.startswith("kit:gold/summary.md") and '"' not in item.text][:3]
    assert len(lines) == 3
    slotted = [{"id": "ae.related.values", "unit": "mod-ae-emergence",
                "value": {"rule": "stated_list", "values": lines}, "status": "stated",
                "class": "document_rule"}]
    found = runs.kit_canaries(root, kit_dir, texts, "R", kit_sha, None, slotted)
    assert all(found.find(line) for line in lines)
    catalog = catalogs.load(catalogs.default_dir(root))
    assert runs.own_records(catalog, slotted, "\n".join(texts)) == []
    held = [{**slotted[0], "value": {"rule": "stated_list", "values": ["RELATED"]}}]
    assert len(runs.own_records(catalog, held, "\n".join(texts))) == 1


def test_a_reader_that_rewrites_its_tools_fails_its_run(root, kit_dir, scratch):
    """H2: bin/ is denied to the tools that write, and held after the run."""
    plan = scratch / "rewrite-plan.json"
    plan.write_text(json.dumps({"records": [], "unmapped": [],
                                "write": {"bin/check": "#!/usr/bin/env bash\necho hi\n"}}),
                    encoding="ascii")
    made = runs.run(root, kit_dir, "R", scratch / "tasks", scratch / "runs",
                    reader=adapter.stub_reader(), env={"SPECFIRST_STUB_PLAN": str(plan)},
                    name="R-rewrite")
    assert made.record["tools_changed"] == ["bin/check"] and not made.passed
    settings = json.loads((made.folder / adapter.SETTINGS).read_text(encoding="ascii"))
    tools_dir = scratch / "tasks" / made.record["task"]["id"] / "bin"
    assert adapter.rule_paths(tools_dir, False)[0] in adapter.denied_roots(
        settings, adapter.WRITE_TOOLS)
    open_settings = adapter.settings([scratch / "kits"], False)
    argv = adapter.command(adapter.Reader(("claude",)), scratch / "s.json", record.BUDGETS["R"])
    assert any("write the tools" in problem for problem in adapter.command_problems(
        argv, open_settings, [scratch / "kits"], False, tools_dir))


def test_the_deny_list_is_never_narrowed(root, kit_dir, scratch, monkeypatch):
    """H4: a task or run folder in the folder that holds the checkouts is refused, and so
    is a Windows reader whose home cannot be found."""
    with pytest.raises(runs.RunError):
        runs.protected_roots(root, kit_dir, root.parent / "tasks-x", scratch / "runs", None,
                             False)
    monkeypatch.setattr(runs, "windows_home", lambda: None)
    with pytest.raises(runs.RunError):
        runs.protected_roots(root, kit_dir, scratch / "tasks", scratch / "runs", None, True)
    found = runs.protected_roots(root, kit_dir, scratch / "tasks", scratch / "runs", None,
                                 False, scratch / "tasks" / "task-none")
    assert root.resolve().parent in found
    assert all(path.parent != (scratch / "tasks").resolve() or path.name != "task-none"
               for path in found)


def test_a_kept_run_is_held_against_its_transcript(root, kit_dir, scratch):
    """H5: budget and cost raised together, a cost that is not the transcript's, a
    transcript that writes bin/: each fails the check of a kept run."""
    seed = genkits.kit_seed(SEED, NUMBER)
    keys = tasks.build(root, kit_dir, scratch / "tasks").keys
    plan = gate.stub_plan(kit_dir, keys, scratch / "stub-h5")
    made = runs.run(root, kit_dir, "R", scratch / "tasks", scratch / "runs",
                    reader=adapter.stub_reader(), seed=seed,
                    env={"SPECFIRST_STUB_PLAN": str(plan)}, name="R-h5")
    kept = runs.keep(made, scratch / "tasks" / made.record["task"]["id"], kit_dir, root,
                     scratch / "kept-h5")
    assert runs.kept_problems(json.loads((kept / runs.RUN_JSON).read_text()), kept) == []
    raised = json.loads((kept / runs.RUN_JSON).read_text())
    raised["budget"]["usd"], raised["cost"]["usd"] = 100.0, 99.0
    found = runs.kept_problems(raised, kept)
    assert any("not the budget" in p for p in found) and any("usd" in p for p in found)
    with open(kept / adapter.TRANSCRIPT, "a", encoding="ascii") as handle:
        handle.write(json.dumps({"type": "assistant", "message": {"content": [{
            "type": "tool_use", "name": "Edit", "id": "t",
            "input": {"file_path": "<task>/bin/ask"}}]}}) + "\n")
    assert any(p.startswith("tools:") for p in runs.kept_problems(
        json.loads((kept / runs.RUN_JSON).read_text()), kept))


def _stub_kept(root, kit_dir, scratch, name):
    seed = genkits.kit_seed(SEED, NUMBER)
    keys = tasks.build(root, kit_dir, scratch / "tasks").keys
    plan = gate.stub_plan(kit_dir, keys, scratch / f"stub-{name}")
    made = runs.run(root, kit_dir, "R", scratch / "tasks", scratch / "runs",
                    reader=adapter.stub_reader(), seed=seed,
                    env={"SPECFIRST_STUB_PLAN": str(plan)}, name=f"R-{name}")
    assert made.passed, runs.lines(made)
    return runs.keep(made, scratch / "tasks" / made.record["task"]["id"], kit_dir, root,
                     scratch / f"kept-{name}"), seed


def test_a_kept_run_is_bound_as_adr_017_says(root, kit_dir, scratch):
    """ADR-017: keep writes binding.json; the slice reaches the entries of its gold and of
    its cells, no model; every plant of decision 7 fails or passes as it should."""
    kept, seed = _stub_kept(root, kit_dir, scratch, "bound")
    bound = binding.read(kept)
    reached = set(bound["registry"]["reached"])
    assert {"count.subjects", "percent.subjects", "display.pattern"} <= reached
    assert any(name.startswith("display.round.") for name in reached)
    assert not any(name.startswith(("model.", "test.")) for name in reached)
    assert bound["files"] == binding.kept_files(kept) and binding.BINDING not in bound["files"]
    assert binding.REGISTRY not in json.dumps(bound["task"])
    assert runs.check(root, kept, kit_dir, scratch / "tasks-bound", seed)[:2] == ([], [])
    said: list[str] = []
    try:
        planted = gate.bound_plants(root, said.append, kept, kit_dir, seed)
    finally:
        gate.cleanup()
    assert len(planted) == 9 and all(planted), said


def _event(kind: str, block: dict) -> str:
    return json.dumps({"type": kind, "message": {"content": [block]}}) + "\n"


def test_out_is_written_again_from_the_transcript(tmp_path):
    """K4: Write, Edit and MultiEdit of out/ without an error, in order; a use with an
    error result is not carried out; bin/ask appends the ask of the log where its answer
    is shown; an edit that does not apply, or an ask the transcript does not show, is
    named."""
    asks = [{"n": 1, "decision": "pop.efficacy.rule", "unit": "mod-populations",
             "question": "Which?", "answered": True}]
    texts = binding.ask_texts(asks, [{"decision": "pop.efficacy.rule",
                                      "unit": "mod-populations", "answer": "All."}], set())
    assert texts == ["Answer: All."]
    lines = [
        _event("assistant", {"type": "tool_use", "id": "a", "name": "Bash",
                             "input": {"command": "bin/ask ..."}}),
        _event("user", {"type": "tool_result", "tool_use_id": "a",
                        "content": "Answer: All.\n"}),
        _event("assistant", {"type": "tool_use", "id": "w", "name": "Write", "input": {
            "file_path": "<task>\\out\\decisions.jsonl", "content": "{\"a\": 1}\n"}}),
        _event("user", {"type": "tool_result", "tool_use_id": "w", "content": "ok"}),
        _event("assistant", {"type": "tool_use", "id": "x", "name": "Write", "input": {
            "file_path": "<task>/out/unmapped.jsonl", "content": "{\"b\": 2}\n"}}),
        _event("user", {"type": "tool_result", "tool_use_id": "x", "content": "denied",
                        "is_error": True}),
        _event("assistant", {"type": "tool_use", "id": "e", "name": "Edit", "input": {
            "file_path": "out/decisions.jsonl", "old_string": "1", "new_string": "3"}}),
        _event("user", {"type": "tool_result", "tool_use_id": "e", "content": [
            {"type": "text", "text": "ok"}]}),
        _event("assistant", {"type": "tool_use", "id": "m", "name": "MultiEdit", "input": {
            "file_path": "<task>/out/decisions.jsonl", "edits": [
                {"old_string": "a", "new_string": "c"}, {"old_string": "3", "new_string": "4"}]}}),
        _event("user", {"type": "tool_result", "tool_use_id": "m", "content": "ok"}),
        _event("assistant", {"type": "tool_use", "id": "o", "name": "Write", "input": {
            "file_path": "<task>/notes.md", "content": "x"}}),
        _event("user", {"type": "tool_result", "tool_use_id": "o", "content": "ok"}),
    ]
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text("".join(lines), encoding="ascii")
    files, problems = binding.replay(transcript, asks, texts)
    assert problems == []
    assert files == {"out/decisions.jsonl": "{\"c\": 4}\n", "out/questions.jsonl": json.dumps(
        {"decision": "pop.efficacy.rule", "question": "Which?", "unit": "mod-populations"},
        sort_keys=True) + "\n"}
    transcript.write_text("".join(lines[2:4] + [_event("assistant", {
        "type": "tool_use", "id": "f", "name": "Edit", "input": {
            "file_path": "<task>/out/decisions.jsonl", "old_string": "zz", "new_string": "y"}}),
        _event("user", {"type": "tool_result", "tool_use_id": "f", "content": "ok"})]),
        encoding="ascii")
    files, problems = binding.replay(transcript, asks, texts)
    assert any("does not apply" in p for p in problems)
    assert any(p.startswith("asks: ask 1") for p in problems)
    assert any("show 0 answers" in p for p in problems)
    # An ask the log leaves out, which the transcript shows, is named too.
    transcript.write_text("".join(lines), encoding="ascii")
    assert binding.replay(transcript, [], [])[1] == [
        "asks: the Bash results of the transcript show 1 answers of `specfirst ask`, the ask "
        "log 0"]
    assert binding.out_path("<task>/out/../bin/check") is None
    assert binding.out_path("C:\\elsewhere\\out\\x") is None


def test_a_run_kept_before_adr_017_is_bound_once_and_only_as_it_was(root, kit_dir, scratch):
    """Decision 6: `runs.bind` writes the binding file of a kept run that has none, the
    same file `keep` writes; it refuses a run that has one, and a run whose kept outputs
    are not what its transcript wrote."""
    kept, seed = _stub_kept(root, kit_dir, scratch, "before")
    written = (kept / binding.BINDING).read_text(encoding="ascii")
    (kept / binding.BINDING).unlink()
    assert runs.check(root, kept, kit_dir, scratch / "tasks-bind", seed)[0][0].startswith(
        "binding: no binding.json")
    path, refused = runs.bind(root, kept, kit_dir, scratch / "tasks-bind")
    assert refused == [] and path.read_text(encoding="ascii") == written
    assert runs.bind(root, kept, kit_dir, scratch / "tasks-bind")[1][0].endswith(
        "already")
    (kept / binding.BINDING).unlink()
    out = kept / runs.WORKSPACE / tasks.OUT / "decisions.jsonl"
    out.write_text("".join(out.read_text(encoding="ascii").splitlines(keepends=True)[:-1]),
                   encoding="ascii", newline="\n")
    path, refused = runs.bind(root, kept, kit_dir, scratch / "tasks-bind")
    assert path is None and any("decisions.jsonl" in line for line in refused)


def test_cache_writes_are_priced_as_the_model_usage_splits_them():
    """H9: one-hour and five-minute writes of one model, each at its price."""
    result = {"usage": {"cache_creation": {"ephemeral_1h_input_tokens": 1}},
              "modelUsage": {"claude-opus-5-5": {
                  "cacheCreationInputTokens": 2_000_000,
                  "cacheCreationEphemeral1hInputTokens": 1_000_000,
                  "cacheCreationEphemeral5mInputTokens": 1_000_000}}}
    assert record.dollars(result) == (8.0 + 5.0, [])
