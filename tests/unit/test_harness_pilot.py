"""The pilot as a reading task (specfirst.harness.pilot; ADR-005, decision 5).

A folder of the shape the pilot gets (tier C: the SAP alone, anchored by
page and paragraph; the ADaM of stage T; a key outside inputs/) is made here
by hand from invented text, so that no test needs the fetch cache or holds a
line of CDISC's SAP. The folder written from the cache is tested in
tests/score/test_score_pilot.py. Each check has a planted defect (rule R5).
No test calls a model: arm R runs the stub reader.
"""

from __future__ import annotations

import json
import shutil

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import yaml

from specfirst.compile import catalog as catalogs
from specfirst.compile import checks
from specfirst.compile import house as houses
from specfirst.compile.standard_form import StandardForm
from specfirst.gen import gold as kitgold
from specfirst.harness import adapter, outputs, pilot, record, runs
from specfirst.harness import task as tasks
from specfirst.machine.canonical import sha256_file
from specfirst.score import pilot as scorepilot
from specfirst.score.candidate import Machine

TEXT = ("CDISC SDTM/ADaM Pilot Project\n\nTitle of the plan\nsecond line\n\f"
        "Header\n\n  The safety population is every subject who took a dose.\n"
        "Percentages use one decimal.\n\n\f\f"
        "Last page " + chr(233) + " text" + chr(7) + "\n")
ANCHORED = ("[1/p1] CDISC SDTM/ADaM Pilot Project\n\n"
            "[1/p2] Title of the plan\nsecond line\n\n"
            "[2/p1] Header\n\n"
            "[2/p2] The safety population is every subject who took a dose.\n"
            "Percentages use one decimal.\n\n"
            "[4/p1] Last page  text\n")
KEY_LINE = "row Any adverse event, column Placebo: 65 ( 75.6), as the example formats it"
ENTRY = "tfl.percent.format"
UNIT = "tfl-ae-summary"


@pytest.fixture(scope="module")
def catalog(root):
    return catalogs.load(catalogs.default_dir(root))


@pytest.fixture(scope="module")
def real_dir(root, tmp_path_factory):
    """A folder of the shape `pilot.write` makes, from invented text."""
    out = tmp_path_factory.mktemp("pilot-real") / "toy"
    sap = out / tasks.DOCUMENTS["sap"]
    sap.parent.mkdir(parents=True)
    sap.write_text(pilot.anchored(TEXT), encoding="ascii", newline="\n")
    kitgold.copy_house(houses.load(houses.default_dir(root)), out)
    for name in ("adsl", "adae"):
        path = out / pilot.ADAM / f"{name}.parquet"
        path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.table({"USUBJID": ["S1"], "SAFFL": ["Y"]}), path)
    (out / pilot.KEY).parent.mkdir(parents=True)
    (out / pilot.KEY).write_text(json.dumps({"rows": [KEY_LINE]}, indent=1) + "\n",
                                 encoding="ascii")
    (out / "gold" / "oracle.yaml").write_text("answers: []\n", encoding="ascii")
    (out / "gold" / "decisions.jsonl").write_text("", encoding="ascii")
    files = {path.relative_to(out).as_posix(): sha256_file(path)
             for path in sorted(out.rglob("*")) if path.is_file()}
    manifest = {"kit": 1, "id": "toy-real", "tier": tasks.REAL_TIER, "split": pilot.SPLIT,
                "generator": pilot.GENERATOR, "units": list(pilot.UNITS), "files": files}
    (out / "kit.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="ascii")
    return out


def stated(root, catalog, anchor: str = "2/p2", doc: str = "sap") -> dict:
    """A record of the percent format at its house default, citing the toy SAP."""
    machine = Machine(root)
    value = next(r["value"] for r in checks.base_vector(machine.catalog, machine.house)
                 if (r["id"], r["unit"]) == (ENTRY, UNIT))
    return {"id": ENTRY, "unit": UNIT, "value": value, "status": "stated",
            "class": "document_rule",
            "statement": StandardForm(catalog).render(ENTRY, UNIT, value),
            "citations": [{"doc": doc, "anchor": anchor,
                           "quote": "Percentages use one decimal."}]}


def test_every_paragraph_gets_its_page_and_number_and_only_ascii_is_kept():
    assert pilot.anchored(TEXT) == ANCHORED
    documents = outputs.Documents({"sap": ANCHORED})
    assert documents.span("sap", "2/p2") == ("The safety population is every subject who "
                                             "took a dose. Percentages use one decimal.")
    # A page without text (page 3) has no anchor; the numbers count pages of the PDF.
    assert documents.span("sap", "3/p1") is None
    assert documents.span("sap", "4/p1") == "Last page text"


def test_a_real_task_holds_the_sap_alone_at_stage_t(root, real_dir, tmp_path):
    made = tasks.build(root, real_dir, tmp_path / "tasks", "T")
    assert not (made.folder / tasks.DOCUMENTS["protocol"]).exists()
    assert (made.folder / tasks.DOCUMENTS["sap"]).read_text(encoding="ascii") == ANCHORED
    assert made.units == (UNIT,)
    assert len(made.keys) == 7 and all(unit == UNIT for _, unit in made.keys)
    assert sorted(p for p in made.manifest if p.startswith(tasks.ADAM)) == [
        f"{tasks.ADAM}/adae.parquet", f"{tasks.ADAM}/adsl.parquet"]
    text = (made.folder / tasks.TASK_FILE).read_text(encoding="ascii")
    assert "You read the statistical analysis plan of one clinical study and" in text
    assert "`[12/p3]`" in text and "The protocol is not given." in text
    assert "protocol.md" not in text and "4.1/p2" not in text
    assert tasks.problems(made.folder, real_dir) == []
    # Planted: the key in the task folder.
    leaked = made.folder / "inputs" / "docs" / "key.json"
    shutil.copyfile(real_dir / pilot.KEY, leaked)
    assert tasks.problems(made.folder, real_dir) == [
        f"inputs/docs/key.json: the file {pilot.KEY} of the kit"]


def test_a_real_task_is_stage_t_and_a_generated_kit_has_both_documents(root, real_dir,
                                                                       tmp_path):
    with pytest.raises(tasks.TaskError, match="stage T"):
        tasks.build(root, real_dir, tmp_path / "tasks", "C")
    generated = tmp_path / "generated"
    shutil.copytree(real_dir, generated)
    manifest = yaml.safe_load((generated / "kit.yaml").read_text(encoding="ascii"))
    manifest["tier"] = "A"
    (generated / "kit.yaml").write_text(yaml.safe_dump(manifest), encoding="ascii")
    with pytest.raises(tasks.TaskError, match="lacks a document"):
        tasks.build(root, generated, tmp_path / "tasks", "T")


def test_task_md_of_a_real_study_differs_from_a_kits_only_where_it_must(root, catalog,
                                                                        monkeypatch):
    units = (UNIT,)
    keys = tasks.keys_of(catalog, units)
    knowledge = ["knowledge/core-reader/SKILL.md"]
    kit = tasks.render(catalog, units, keys, "T", knowledge).split("\n")
    real = tasks.render_real(catalog, units, keys, ("sap",), knowledge).split("\n")
    assert sorted(set(kit) - set(real)) == sorted([
        "You read the protocol and the statistical analysis plan of one clinical study and",
        "- `inputs/docs/protocol.md` (document ID `protocol`) and `inputs/docs/sap.md`",
        "  (document ID `sap`): the documents of the study. Every paragraph starts with its",
        "  anchor in brackets, for example `[4.1/p2]`.",
        next(line for line in kit if '"anchor": "4.1/p2"' in line),
        next(line for line in kit if '"anchor": "5/p1"' in line)])
    # Planted: the kit text changed where the real one swaps it.
    monkeypatch.setattr(tasks, "render", lambda *a: "\n".join(kit).replace(
        "for example `[4.1/p2]`", "for example `[4.2/p1]`"))
    with pytest.raises(tasks.TaskError, match="the text of a kit task changed"):
        tasks.render_real(catalog, units, keys, ("sap",), knowledge)


def test_a_real_task_cites_only_the_documents_it_has(root, real_dir, catalog, tmp_path):
    made = tasks.build(root, real_dir, tmp_path / "tasks", "T")
    documents = outputs.task_documents(made.folder)
    assert sorted(documents.texts) == ["house", "sap"]
    good = stated(root, catalog)
    assert outputs.decision_problems([(1, good)], catalog, made.keys, documents) == []
    for doc, anchor, problem in (("protocol", "2/p2", "cites the document 'protocol'"),
                                 ("sap", "3/p1", "has no anchor '3/p1'")):
        bad = stated(root, catalog, anchor, doc)
        found = outputs.decision_problems([(1, bad)], catalog, made.keys, documents)
        assert len(found) == 1 and problem in found[0]


def _plan(where, records, **more) -> str:
    plan = {"records": records, "unmapped": [], "check": True, "asks": [],
            "usage": {"input_tokens": 10, "output_tokens": 20,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
            "model_usage": {record.MODEL: {"inputTokens": 10, "outputTokens": 20,
                                           "cacheCreationInputTokens": 0,
                                           "cacheReadInputTokens": 0}}, **more}
    path = where / "plan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(plan), encoding="utf-8")
    return str(path)


def test_arm_r_on_a_real_study_with_the_stub_reader(root, real_dir, catalog, tmp_path):
    asks = [{"decision": ENTRY, "unit": UNIT, "question": "Which percent format?"}]
    plan = _plan(tmp_path / "clean", [stated(root, catalog)], asks=asks)
    made = runs.run(root, real_dir, "R", tmp_path / "tasks", tmp_path / "runs", "T",
                    reader=adapter.stub_reader(), env={"SPECFIRST_STUB_PLAN": plan},
                    name="R-stub")
    assert made.passed, runs.lines(made)
    assert made.record["kit"]["split"] == pilot.SPLIT and made.record["stage"] == "T"
    assert made.record["asks"] == [{"decision": ENTRY, "unit": UNIT, "answered": False}]
    assert f"kit:{pilot.KEY}" in made.record["canary"]["sources"]
    assert pilot.records_of(made.folder) == [stated(root, catalog)]
    # Planted: a reader that reads the key.
    plan = _plan(tmp_path / "leak", [stated(root, catalog)], read=[str(real_dir / pilot.KEY)])
    leaked = runs.run(root, real_dir, "R", tmp_path / "tasks", tmp_path / "runs", "T",
                      reader=adapter.stub_reader(), env={"SPECFIRST_STUB_PLAN": plan},
                      name="R-leak")
    assert not leaked.passed
    assert any(pilot.KEY in hit for hit in leaked.record["canary"]["hits"])


def test_the_pilot_folder_is_refused_inside_a_checkout(root):
    with pytest.raises(pilot.PilotTaskError, match="outside every checkout"):
        pilot.write(root, root / "build" / "pilot-folder")
    assert not (root / "build" / "pilot-folder").exists()


def test_only_a_pilot_folder_is_ever_replaced(root, real_dir, tmp_path):
    """`--folder` names what is deleted and written again: a missing or empty folder, or a
    pilot folder, never anything else (review of slice-ae-summary, finding 4)."""
    assert pilot.not_replaceable(tmp_path / "new") is None
    (tmp_path / "empty").mkdir()
    assert pilot.not_replaceable(tmp_path / "empty") is None
    written = tmp_path / "written"
    shutil.copytree(real_dir, written)
    assert pilot.not_replaceable(written) is None  # its generator is pilot-1
    # Planted: a folder of something else (the kits and the logs, say), and a file.
    other = tmp_path / "other"
    other.mkdir()
    (other / "keep.txt").write_text("keep", encoding="ascii")
    assert "not a pilot folder" in pilot.not_replaceable(other)
    with pytest.raises(pilot.PilotTaskError, match="not a pilot folder"):
        pilot.write(root, other)
    assert (other / "keep.txt").read_text(encoding="ascii") == "keep"
    assert "is a file" in pilot.not_replaceable(other / "keep.txt")
    manifest = yaml.safe_load((written / "kit.yaml").read_text(encoding="ascii"))
    manifest["generator"] = "gen-3a.2"
    (written / "kit.yaml").write_text(yaml.safe_dump(manifest), encoding="ascii")
    assert "not a pilot folder" in pilot.not_replaceable(written)


def test_the_pilot_report_takes_a_run_on_the_pilot_only(root, tmp_path):
    """A run of another kit holds that kit's values: it is refused before its records are
    read, and so is a run of arm C (review of slice-ae-summary, finding 5)."""
    for name, kit, arm in (("dev", {"id": "sfdevkit", "split": "dev"}, "R"),
                           ("control", {"id": "cdiscpilot01", "split": pilot.SPLIT}, "C")):
        run = tmp_path / name
        (run / "workspace" / "out").mkdir(parents=True)
        (run / "run.json").write_text(json.dumps({"arm": arm, "kit": kit}), encoding="utf-8")
        (run / "workspace" / "out" / "decisions.jsonl").write_text(
            json.dumps({"id": ENTRY, "unit": UNIT, "value": {"rule": "secret"}}) + "\n",
            encoding="utf-8")
        with pytest.raises(pilot.PilotTaskError, match="not a run of arm S or R on the pilot"):
            pilot.score(root, run)
    with pytest.raises(pilot.PilotTaskError, match="no readable run.json"):
        pilot.score(root, tmp_path / "missing")


def test_the_records_of_a_run_are_listed_with_their_quotes_cut_short():
    long = "word " * 40
    said = pilot.record_lines([{"id": ENTRY, "unit": UNIT, "value": {"rule": "x"},
                                "status": "stated",
                                "citations": [{"doc": "sap", "anchor": "2/p2", "quote": long}]}])
    assert said[0] == "the reader's records: 1"
    quote = said[1].split('[2/p2] "')[1].removesuffix('"')
    assert len(quote) == 60 and quote.endswith("...")


def test_arm_r_on_the_pilot_takes_the_readers_table_decisions_only(root):
    machine = Machine(root)
    standard = scorepilot.standard_vector(machine)
    given = [{"id": "tfl.columns.total", "unit": UNIT, "value": {"rule": "none"}},
             {"id": "ae.teae.end", "unit": "mod-ae-emergence", "value": {"rule": "x"}},
             {"id": ENTRY, "unit": UNIT, "value": None}]
    vector = scorepilot.given_vector(machine, given)
    changed = [(a["id"], b["value"]) for a, b in zip(standard, vector, strict=True)
               if a["value"] != b["value"]]
    assert changed == [("tfl.columns.total", {"rule": "none"})]
    assert scorepilot.given_vector(machine, []) == standard
