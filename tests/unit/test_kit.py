"""Kits: the manifest, assembling from the fetch cache, and what may be in git."""

from __future__ import annotations

import pytest
import toy_kit
import yaml

from specfirst import kit as kits
from specfirst import sources

SHA = "a" * 64


def manifest(**changes) -> dict:
    data = {
        "kit": 0, "id": "demo", "title": "Demo", "tier": "C",
        "pins": {"engines": {"yamaa": "0.7.0"}, "sources": {"p7": "b" * 40}},
        "build": {"project": "gold/spec/project.yaml", "sdtm": "inputs/data/sdtm",
                  "reference": "gold/reference/adam"},
        "documents": [{"id": "sap", "file": "inputs/docs/sap.pdf", "cited_as": ["x/SAP.pdf"]}],
        "files": [
            {"path": "gold/spec/project.yaml", "source": "p7", "from": "a/project.yaml",
             "sha256": SHA},
            {"path": "inputs/data/sdtm/dm.parquet", "source": "p7", "from": "a/dm.parquet",
             "sha256": SHA},
            {"path": "gold/reference/adam/adsl.parquet", "source": "p7", "from": "a/adsl.parquet",
             "sha256": SHA},
            {"path": "inputs/docs/sap.pdf", "source": "p7", "from": "a/SAP.pdf", "sha256": SHA},
        ],
    }
    data.update(changes)
    return data


def test_valid_manifest():
    kit = kits.parse_kit(manifest())
    assert (kit.id, kit.tier, kit.sdtm, kit.claims) == ("demo", "C", "inputs/data/sdtm", None)
    assert kit.document("x/SAP.pdf").id == "sap" and kit.document("unknown.pdf") is None
    assert kit.trace_gaps == {}


def with_file(**changes):
    entry = {"path": "inputs/docs/new.pdf", "source": "p7", "from": "a/new.pdf", "sha256": SHA}
    entry.update(changes)
    return manifest(files=[*manifest()["files"], entry])


@pytest.mark.parametrize(
    ("data", "message"),
    [
        (manifest(kit=1), "manifest format"),
        (manifest(tier="D"), "tier"),
        (manifest(id="Demo Kit"), "id: must match"),
        (manifest(pins={"engines": {}, "sources": {"p7": "b" * 40}}), "pins.engines"),
        (manifest(pins={"engines": {"yamaa": "0.7.0"}, "sources": {"p7": "main"}}), "40 lower"),
        (with_file(path="docs/new.pdf"), "must be under one of"),
        (with_file(path="../outside.pdf"), "must be relative"),
        (with_file(path="inputs/docs/sap.pdf"), "listed twice"),
        (with_file(sha256="123"), "64 lower-case hex"),
        (with_file(source="other"), "no commit under pins.sources"),
        (with_file(**{"from": "/etc/passwd"}), "'from' must be relative"),
        (manifest(documents=[{"id": "sap", "file": "inputs/docs/gone.pdf"}]), "not in the list"),
        (manifest(build={"project": "gold/spec/none.yaml", "sdtm": "inputs/data/sdtm",
                         "reference": "gold/reference/adam"}), "build.project"),
        (manifest(build={"project": "gold/spec/project.yaml", "sdtm": "gold/reference/adam",
                         "reference": "gold/reference/adam"}), "belong under inputs/"),
        (manifest(trace_gaps={"adam:ADSL.X": ""}), "trace_gaps"),
        (manifest(files=[]), "lists no file"),
    ],
)
def test_manifest_problems_are_reported(data, message):
    with pytest.raises(kits.KitError, match=message):
        kits.parse_kit(data)


def test_the_pilot_kit_is_pinned_like_the_sources(root):
    kit = kits.load_kit(root, "cdiscpilot01")
    assert kit.tier == "C" and len(kit.files) == 70
    manifest_of_sources = sources.load_manifest(sources.manifest_path(root))
    assert kits.pin_problems(kit, manifest_of_sources) == []
    # 64 files of Pilot 7; the ARS example, the schema of the ARS model and the example's
    # table shells from CDISC (the review of real-3a, F1); the CSR of Pilot 6, the
    # reference of the efficacy grids (real-5a).
    assert sorted(entry.path for entry in kit.files if entry.source == "ars") == [
        "gold/reference/shells/AE_Summary_Table_Shell.pdf",
        "gold/reference/shells/Vitals_Obs_ChgBaseline_Table_Shell.pdf",
        "gold/reference/shells/Vitals_Obs_ChgBaseline_Table_Shell_vertical.pdf",
        "gold/spec/ars/ars_ldm.schema.json", "gold/spec/ars/common-safety-displays.json"]
    shells = {display.output: display.shell for spec in kit.results for display in spec.displays
              if display.shell}
    assert shells == {
        "Out14-3-1-1": "gold/reference/shells/AE_Summary_Table_Shell.pdf",
        "Out14-3-3-1a": "gold/reference/shells/Vitals_Obs_ChgBaseline_Table_Shell.pdf",
        "Out14-3-3-1b": "gold/reference/shells/Vitals_Obs_ChgBaseline_Table_Shell_vertical.pdf"}
    assert {entry.source for entry in kit.files} == {"p7", "ars", "p6"}
    assert [entry.path for entry in kit.files if entry.source == "p6"] == [
        "gold/reference/csr/CSR.pdf"]
    inputs = [entry.path for entry in kit.files if entry.path.startswith("inputs/")]
    assert len(inputs) == 26  # 22 SDTM datasets, their Define-XML, and 3 documents
    # No reference data, specification or claim is among the inputs.
    assert not any("adam" in path and path.endswith(".parquet") for path in inputs)
    assert [doc.id for doc in kit.documents] == ["sap", "dataguide", "define-adam", "define-sdtm"]
    # The ARS example is the file PLAN.md appendix A pins by its hash.
    example = next(entry for entry in kit.files if entry.path.endswith("displays.json"))
    assert example.sha256 in {pin.sha256 for pin in manifest_of_sources.files}
    assert [spec.id for spec in kit.results] == ["common-safety-displays", "efficacy-adas",
                                                 "efficacy-cibic"]
    assert kit.results[0].ars == example.path and kit.exceptions == "gold/exceptions.yaml"
    assert (root / "kits" / "cdiscpilot01" / kit.exceptions).is_file()
    # real-5a: the reporting event is our own file; each grid has its CSR table.
    efficacy = kit.results[1]
    assert efficacy.ars == "gold/events/efficacy-adas.json" and efficacy.ars in kit.own_files()
    assert [(d.output, d.reference.page, d.reference.table) for d in efficacy.displays] == [
        ("Out14-3-01", 49, "14-3.01"), ("Out14-3-03", 51, "14-3.03"),
        ("Out14-3-05", 53, "14-3.05"), ("Out14-3-11", 59, "14-3.11")]
    # real-5b: CIBIC+ in an event of its own.
    cibic = kit.results[2]
    assert cibic.ars == "gold/events/efficacy-cibic.json" and cibic.ars in kit.own_files()
    assert [(d.output, d.reference.page, d.reference.table) for d in cibic.displays] == [
        ("Out14-3-13", 61, "14-3.13")]
    # Issue #31: the records of the demographics and AE tables over the standard it names.
    assert kit.decisions == ("gold/decisions/efficacy.jsonl", "gold/decisions/safety.jsonl")
    assert set(kit.decisions) <= set(kit.own_files())
    assert kit.standard == ("catalog@2", "open-default@2")
    assert all((root / "kits" / "cdiscpilot01" / name).is_file() for name in kit.own_files())


def test_the_own_files_of_the_pilot_kit_can_be_read(root):
    """The exceptions file and the layouts of the pilot are read as a build reads them. An edit
    that joined two entries of the exceptions file passed the unit suite (real-3); only the
    tests that need the fetch cache read the file."""
    from specfirst.machine import csr, results
    from specfirst.machine import layout as layouts

    kit = kits.load_kit(root, "cdiscpilot01")
    folder = root / "kits" / "cdiscpilot01"
    listed = results.load_exceptions(folder / kit.exceptions)
    formats = results.load_formats(folder / kit.exceptions)
    cells = csr.load_exceptions(folder / kit.exceptions)
    assert set(listed) == {"common-safety-displays"} and len(listed["common-safety-displays"]) == 25
    assert set(formats) == {"common-safety-displays"}
    kinds = [entry["proof"]["kind"] for entry in formats["common-safety-displays"].values()]
    assert (kinds.count("not_its_own_pattern"), kinds.count("half_in_floating_error")) == (120, 4)
    assert set(cells) <= {d.output for spec in kit.results for d in spec.displays}
    outputs = [layouts.read(folder / d.layout).output for spec in kit.results
               for d in spec.displays]
    assert outputs == [d.output for spec in kit.results for d in spec.displays]


def with_results(**changes) -> dict:
    files = [*manifest()["files"],
             {"path": "gold/spec/ars/event.json", "source": "p7", "from": "a/event.json",
              "sha256": SHA}]
    entry = {"id": "event", "ars": "gold/spec/ars/event.json"}
    entry.update(changes)
    return manifest(files=files, results=[entry])


def test_result_sets_and_the_exceptions_file_of_a_kit():
    kit = kits.parse_kit(with_results(binding={"options": {"summary.continuous": {
        "quantile_definition": "sas5"}}}))
    assert kit.results == (kits.ResultSet("event", "gold/spec/ars/event.json", None, "USUBJID", {
        "options": {"summary.continuous": {"quantile_definition": "sas5"}}}),)
    assert kit.exceptions is None
    build = {**manifest()["build"], "exceptions": "gold/exceptions.yaml"}
    assert kits.parse_kit(manifest(build=build)).exceptions == "gold/exceptions.yaml"
    for data, message in (
        (with_results(ars="gold/spec/ars/none.json"),
         "ars 'gold/spec/ars/none.json' is neither in"),
        (with_results(schema="gold/spec/ars/schema.json"), "schema 'gold/spec/ars/schema.json'"),
        (with_results(id="Event 1"), "'id' must match"),
        (with_results(binding={"methods": {}}), "'binding' may hold 'operations' and 'options'"),
        (with_results(subject_key=""), "'subject_key' must name a column"),
        (with_results(engine="r"), "unknown key engine"),
        (manifest(build={**build, "exceptions": "gold/spec/exceptions.yaml"}),
         "must be a file of our own under gold/"),
        (manifest(build={**build, "exceptions": "exceptions.yaml"}), "under gold/"),
    ):
        with pytest.raises(kits.KitError, match=message):
            kits.parse_kit(data)
    twice = with_results()
    twice["results"].append(dict(twice["results"][0]))
    with pytest.raises(kits.KitError, match="id 'event' is used twice"):
        kits.parse_kit(twice)


def test_an_event_of_our_own_a_csr_reference_and_decision_records():
    """real-5a (ADR-015): our own reporting event, a CSR table per output, decisions."""
    files = [*manifest()["files"], {"path": "gold/reference/csr/CSR.pdf", "source": "p7",
                                    "from": "a/CSR.pdf", "sha256": SHA}]
    build = {**manifest()["build"], "decisions": "gold/decisions/d.jsonl"}

    def made(**output) -> dict:
        entry = {"id": "eff", "ars": "gold/events/eff.json",
                 "outputs": [{"id": "Out1", "layout": "gold/layout/Out1.yaml", **output}]}
        return manifest(files=files, build=build, results=[entry])

    kit = kits.parse_kit(made(reference={"csr": "gold/reference/csr/CSR.pdf", "page": 49,
                                         "table": "14-3.01"}))
    assert kit.results[0].displays[0].reference == kits.CsrTable(
        "gold/reference/csr/CSR.pdf", 49, "14-3.01")
    assert kit.own_files() == ["gold/decisions/d.jsonl", "gold/events/eff.json",
                               "gold/layout/Out1.yaml"]
    assert kits.parse_kit(made()).results[0].displays[0].reference is None
    for data, message in (
        (made(reference={"csr": "gold/reference/csr/other.pdf", "page": 49, "table": "1"}),
         "a reference names the 'csr'"),
        (made(reference={"csr": "gold/reference/csr/CSR.pdf", "page": 0, "table": "1"}),
         "a reference names the 'csr'"),
        (made(reference={"csr": "gold/reference/csr/CSR.pdf", "page": 1}),
         "a reference names the 'csr'"),
        (made(note="x"), "may name its 'reference'"),
        (manifest(files=files, build={**build, "decisions": "gold/spec/d.jsonl"}),
         "build.decisions: must be a file of our own"),
        (manifest(files=files, results=[{"id": "eff", "ars": "gold/reference/csr/eff.json"}]),
         "is neither in the list of files nor a file of our own"),
    ):
        with pytest.raises(kits.KitError, match=message):
            kits.parse_kit(data)


def test_decision_files_and_the_standard_of_a_kit():
    """Issue #31 (ADR-022): a list of decision files, and the catalog and house it names."""
    files = [*manifest()["files"]]
    build = {**manifest()["build"], "decisions": ["gold/decisions/a.jsonl",
                                                  "gold/decisions/b.jsonl"]}
    kit = kits.parse_kit(manifest(files=files, build=build,
                                  standard={"catalog": "catalog@2", "house": "open-default@2"}))
    assert kit.decisions == ("gold/decisions/a.jsonl", "gold/decisions/b.jsonl")
    assert kit.standard == ("catalog@2", "open-default@2")
    assert set(kit.decisions) <= set(kit.own_files())
    # One file, as before; no standard.
    one = kits.parse_kit(manifest(build={**build, "decisions": "gold/decisions/a.jsonl"}))
    assert (one.decisions, one.standard) == (("gold/decisions/a.jsonl",), None)
    for data, message in (
        (manifest(build={**build, "decisions": ["gold/decisions/a.jsonl",
                                                "gold/decisions/a.jsonl"]}), "each once"),
        (manifest(build={**build, "decisions": []}), "or a list of such files"),
        (manifest(build={**build, "decisions": ["gold/spec/a.jsonl"]}), "a file of our own"),
        (manifest(standard={"catalog": "catalog@2"}), "names the 'catalog' and the 'house'"),
        (manifest(standard={"catalog": "open-default@2", "house": "open-default@2"}),
         "names the 'catalog' and the 'house'"),
        (manifest(standard={"catalog": "catalog@two", "house": "open-default@2"}),
         "names the 'catalog' and the 'house'"),
    ):
        with pytest.raises(kits.KitError, match=message):
            kits.parse_kit(data)


@pytest.fixture
def toy(tmp_path, root, monkeypatch):
    pytest.importorskip("pyarrow")
    monkeypatch.delenv("SPECFIRST_CACHE", raising=False)
    return toy_kit.make(tmp_path, root, engine_version="0.0.0")


def test_assemble_copies_exactly_the_pinned_files(toy):
    kit = kits.load_kit(toy, "toy")
    dest = kits.assembled_dir(toy, "toy")
    assert kits.assemble(toy, kit) == []
    found = {p.relative_to(dest).as_posix() for p in dest.rglob("*") if p.is_file()}
    assert found == kit.paths() | {"kit.yaml"}
    assert kits.verify_assembled(kit, dest) == []
    lines: list[str] = []
    assert kits.run_assemble(toy, "toy", lines.append) == 0
    assert "10 files match their pinned SHA-256 (4 inputs, 6 gold)" in lines[-1]


def test_a_changed_source_file_is_refused(toy):
    kit = kits.load_kit(toy, "toy")
    (toy / "third_party/cache/toy/docs/sap.md").write_text("changed\n", encoding="ascii")
    problems = kits.assemble(toy, kit)
    assert problems == ["inputs/docs/sap.md: toy:docs/sap.md does not have the pinned SHA-256"]
    assert not (kits.assembled_dir(toy, "toy") / "inputs/docs/sap.md").exists()
    lines: list[str] = []
    assert kits.run_assemble(toy, "toy", lines.append) == 1


def test_a_missing_source_file_is_refused(toy):
    kit = kits.load_kit(toy, "toy")
    (toy / "third_party/cache/toy/data/sdtm/dm.parquet").unlink()
    assert kits.assemble(toy, kit) == [
        "inputs/data/sdtm/dm.parquet: toy:data/sdtm/dm.parquet is not in the fetch cache"
    ]


def test_a_stray_or_changed_file_in_the_assembled_kit_is_found(toy):
    kit = kits.load_kit(toy, "toy")
    dest = kits.assembled_dir(toy, "toy")
    assert kits.assemble(toy, kit) == []
    (dest / "inputs/docs/leaked-gold.md").write_text("gold\n", encoding="ascii")
    (dest / "gold/claims/adsl-claims.json").write_text("{}\n", encoding="ascii")
    assert kits.verify_assembled(kit, dest) == [
        "gold/claims/adsl-claims.json: SHA-256 is not the pinned one",
        "inputs/docs/leaked-gold.md: not in the manifest",
    ]
    # Assembling again restores the changed file and still reports the stray one.
    assert kits.assemble(toy, kit) == ["inputs/docs/leaked-gold.md: not in the manifest"]


def test_a_pin_that_differs_from_sources_yaml_is_a_problem(toy):
    kit = kits.load_kit(toy, "toy")
    path = toy / "third_party/sources.yaml"
    path.write_text(path.read_text("ascii").replace(toy_kit.COMMIT, "f" * 40), "ascii")
    problems = kits.assemble(toy, kit)
    assert len(problems) == 1 and "sources.yaml pins " + "f" * 40 in problems[0]


def test_lock_rewrites_the_hashes_and_keeps_the_head(toy):
    path = kits.manifest_path(toy, "toy")
    before = path.read_text("ascii")
    assert kits.lock(toy, "toy") == []
    assert path.read_text("ascii") == before
    (toy / "third_party/cache/toy/docs/sap.md").write_text("a new plan\n", encoding="ascii")
    assert kits.lock(toy, "toy") == ["inputs/docs/sap.md"]
    after = path.read_text("ascii")
    assert after != before and after.startswith("# A made-up kit for the tests.\n")
    assert kits.assemble(toy, kits.load_kit(toy, "toy")) == []


def test_files_block_is_valid_yaml_and_sorted():
    entries = [kits.KitFile("inputs/b c.txt", "p7", "x/b c.txt", SHA),
               kits.KitFile("inputs/a.txt", "p7", "x/a.txt", SHA)]
    data = yaml.safe_load(kits.files_block(entries))
    assert [entry["path"] for entry in data["files"]] == ["inputs/a.txt", "inputs/b c.txt"]
    assert data["files"][1]["from"] == "x/b c.txt"


def test_study_data_and_documents_may_not_be_in_git(toy, root):
    # The made-up kit is tier A in one checkout and tier C in another.
    assert kits.tracked_data_problems(toy, ["kits/toy/kit.yaml", "kits/toy/data/dm.parquet"]) == []
    as_real = toy_kit.make(toy / "real", root, tier="C", engine_version="0.0.0")
    problems = kits.tracked_data_problems(
        as_real,
        ["kits/toy/kit.yaml", "kits/toy/README.md", "kits/toy/inputs/data/sdtm/dm.parquet",
         "docs/CSR.pdf", "src/specfirst/cli.py", "kits/README.md"],
    )
    assert problems == [
        "kits/toy/inputs/data/sdtm/dm.parquet: a tier C kit folder holds kit.yaml, README.md "
        "and the files of our own its manifest names (the exceptions, the layouts), nothing "
        "else",
        "docs/CSR.pdf: study data or a study document in git",
    ]


def test_a_kit_folder_may_hold_the_exceptions_file_its_manifest_names(toy, root):
    real = toy_kit.make(toy / "real", root, tier="C", engine_version="0.0.0")
    manifest_file = real / "kits/toy/kit.yaml"
    text = manifest_file.read_text("ascii")
    names = ["kits/toy/kit.yaml", "kits/toy/gold/exceptions.yaml", "kits/toy/gold/other.yaml"]
    # Not named by the manifest: refused like any other file.
    assert len(kits.tracked_data_problems(real, names)) == 2
    manifest_file.write_text(text.replace(
        "  claims: gold/claims\n", "  claims: gold/claims\n  exceptions: gold/exceptions.yaml\n"),
        encoding="ascii")
    problems = kits.tracked_data_problems(real, names)
    assert len(problems) == 1 and problems[0].startswith("kits/toy/gold/other.yaml:")
    # Assembling copies it next to the manifest, and fails when it is not there.
    kit = kits.load_kit(real, "toy")
    assert kits.assemble(real, kit) == [
        "gold/exceptions.yaml: named by the manifest, but not in kits/toy/"]
    (real / "kits/toy/gold").mkdir()
    (real / "kits/toy/gold/exceptions.yaml").write_text("exceptions: 0\nresults: {}\n", "ascii")
    assert kits.assemble(real, kit) == []
    assert (kits.assembled_dir(real, "toy") / "gold/exceptions.yaml").is_file()


def test_study_data_under_another_name_or_suffix_is_found(toy, root):
    """The cases a list of suffixes misses (review of real-1, finding F5)."""
    import shutil

    real = toy_kit.make(toy / "real", root, tier="C", engine_version="0.0.0")
    cache = real / "third_party/cache/toy"
    (real / "tests/data").mkdir(parents=True)
    (real / "docs").mkdir()
    # A pinned claims file and a pinned document, committed under other names.
    shutil.copyfile(cache / "review/adsl-claims.json", real / "tests/data/expected.json")
    shutil.copyfile(cache / "docs/sap.md", real / "docs/notes.txt")
    # The Define-XML, edited, so that no hash matches.
    define = (cache / "define/define-sdtm.xml").read_text("ascii").replace("AGE", "AGEX")
    (real / "docs/define.xml").write_text(define, encoding="ascii")
    (real / "docs/layout.xml").write_text("<svg></svg>\n", encoding="ascii")
    (real / "docs/own.json").write_text('{"ours": true}\n', encoding="ascii")
    names = ["tests/data/expected.json", "docs/notes.txt", "docs/define.xml", "docs/layout.xml",
             "docs/own.json", "data/adsl.rds", "data/dm.feather", "data/adsl.TSV",
             "kits/toy/kit.yaml"]
    assert kits.tracked_data_problems(real, names) == [
        "tests/data/expected.json: byte for byte gold/claims/adsl-claims.json of kit toy, "
        "which stays in the fetch cache",
        "docs/notes.txt: byte for byte inputs/docs/sap.md of kit toy, which stays in the "
        "fetch cache",
        "docs/define.xml: a Define-XML or other ODM file in git",
        "data/adsl.rds: study data or a study document in git",
        "data/dm.feather: study data or a study document in git",
        "data/adsl.TSV: study data or a study document in git",
    ]
    # A known limit: a document retyped or converted is not seen.
    (real / "docs/sap-retyped.txt").write_text("Subjects are grouped by age.\n", encoding="ascii")
    assert kits.tracked_data_problems(real, ["docs/sap-retyped.txt"]) == []


def test_an_odm_file_is_found_by_its_root_element(toy, root):
    """Review of real-1, finding N5: another suffix, UTF-16, a long comment before the root."""
    real = toy_kit.make(toy / "real", root, tier="C", engine_version="0.0.0")
    define = (real / "third_party/cache/toy/define/define-sdtm.xml").read_text("ascii")
    define = define.replace("AGE", "AGEX")  # edited, so that no hash matches
    head, mark, rest = define.partition("<ODM>")
    assert mark
    docs = real / "docs"
    docs.mkdir()
    (docs / "define.txt").write_text(define, encoding="ascii")
    (docs / "define-utf16.xml").write_bytes(define.encode("utf-16"))
    (docs / "define-utf16-no-mark.dat").write_bytes(define.encode("utf-16-le"))
    (docs / "define-utf8-mark.xml").write_bytes(define.encode("utf-8-sig"))
    (docs / "define-late.xml").write_text(
        f"{head}<!-- {'x' * 70000} -->\n<!DOCTYPE ODM>\n{mark}{rest}", encoding="ascii")
    (docs / "define-prefixed.xml").write_text(
        define.replace("<ODM>", '<odm:ODM xmlns:odm="http://www.cdisc.org/ns/odm/v1.3">')
        .replace("</ODM>", "</odm:ODM>"), encoding="ascii")
    found = ["docs/define.txt", "docs/define-utf16.xml", "docs/define-utf16-no-mark.dat",
             "docs/define-utf8-mark.xml", "docs/define-late.xml", "docs/define-prefixed.xml"]
    # Not ODM files: text about one, an XML file that names ODM in a comment, another root.
    (docs / "about-odm.md").write_text("An ODM file starts like this:\n<ODM>\n", encoding="ascii")
    (docs / "layout.xml").write_text(
        '<?xml version="1.0"?>\n<!-- not <ODM> -->\n<svg></svg>\n', encoding="ascii")
    (docs / "odmlike.xml").write_text("<ODMX></ODMX>\n", encoding="ascii")
    others = ["docs/about-odm.md", "docs/layout.xml", "docs/odmlike.xml"]
    assert kits.tracked_data_problems(real, [*found, *others]) == [
        f"{name}: a Define-XML or other ODM file in git" for name in found]
    # A known limit: a compressed copy is not seen.
    import gzip

    (docs / "define.xml.gz").write_bytes(gzip.compress(define.encode("ascii"), mtime=0))
    assert kits.tracked_data_problems(real, ["docs/define.xml.gz"]) == []


def test_the_repository_tracks_no_study_data(root):
    from specfirst import asciicheck

    assert kits.tracked_data_problems(root, asciicheck.maintained_files(root)) == []
