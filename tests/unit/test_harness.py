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
from specfirst.harness import adapter, canary, gate, knowledge, oracle, outputs, record, runs
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
