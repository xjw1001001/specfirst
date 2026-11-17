"""A kit of a generated study (PLAN.md sections 6.4, 6.7 and 8), for the slice of ADR-005.

    <kit>/
      kit.yaml                  the manifest: id, tier, archetype, split, generator,
                                pins, the properties, the SHA-256 of every file
      study.json                the manifest of the generated data (stages S2 to S4)
      inputs/data/sdtm/         the visible SDTM, with its Define-XML
      inputs/house/             the house standard: document, parent specs, templates
      gold/design.yaml  probes.jsonl  truth/     from the generator of the data
      gold/decisions.jsonl      the decision vector: value, status, class, statement,
                                citation, binds, identifiable
      gold/docs/sap.md          the stated decisions in standard form
      gold/spec/                compiled: adam/ (yamaa specs and their project),
                                ars/reporting-event.json, layout/, compile.json
      gold/resolved/  data/adam/  ars/  ard/  grid/  out/  graph/
                                built on the visible data
      gold/reference/           the hand calculation of the output (P2)
      gold/identifiability.json the matrix of the twin (P4)
      twin/data/sdtm/  twin/truth/      the hidden second dataset
      twin/gold/                its gold: data/adam/, ars/, ard/, grid/, out/, graph/,
                                reference/

Everything is a pure function of the generator version, the catalog, the
house standard, the seed and the split. No file holds a seed, a clock or a
path of the machine it was made on.

`generate` writes a kit only when it has the properties P2 to P4 and its two
result engines agree. A decision vector whose kit leaves a pair of
alternatives that the log of probes claims unseparated on the twin is drawn
again, up to `MAX_ATTEMPTS` times; the manifest says how often. A kit that
cannot be written leaves no folder. `generate_checked` builds the kit a
second time in a process of its own and compares every hash (P1).

Splits. A set of kits is generated from one seed; kit n has the seed
"<seed>/kit-<n>" and the split `SPLIT_PLAN` gives its place. The seed of a
set with dev or test kits is a secret (section 8): it comes from a file
outside every checkout (`specfirst gen kits --seed-file`). A sealed kit is
generated at exam time, one at a time, with `--split sealed`; only a sealed
kit may have what `decisions.HELD_OUT` names.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

import yaml

import specfirst
from specfirst.compile import catalog as catalogs
from specfirst.compile import compiler
from specfirst.compile import house as houses
from specfirst.gen import GENERATOR, decisions, gold, pgfix, probes, reference, study, verify
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream, seed_sha256
from specfirst.machine import registry as registries
from specfirst.machine import runner
from specfirst.machine.canonical import sha256_file, write_json

Out = Callable[[str], None]
FORMAT = 1
MANIFEST = "kit.yaml"
SLICE = "ae-summary-first"
MAX_ATTEMPTS = 12
APART_ZONE = "Pacific/Kiritimati"
MAX_DESIGNS = 50
# The split of the kits of a set, by their number: four train, three dev, three test.
SPLIT_PLAN = ("train", "train", "train", "train", "dev", "dev", "dev", "test", "test", "test")
IDENTIFIABILITY = "gold/identifiability.json"
DOCUMENT = f"gold/docs/{decisions.DOCUMENT}.md"
REFERENCE = "reference"


class KitError(RuntimeError):
    """The kit cannot be written: it fails a property, or its inputs are unusable."""


def kit_seed(seed: str, number: int) -> str:
    return f"{seed}/kit-{number}"


def split_of(number: int) -> str:
    """The split of kit `number` of a set, counted from 1."""
    return SPLIT_PLAN[(number - 1) % len(SPLIT_PLAN)]


def scenario_of(seed: str, number: int | None) -> int:
    """The scenario of a kit: by its number in a set, or drawn from its seed."""
    count = len(decisions.SCENARIOS)
    if number is not None:
        return (number - 1) % count
    return Stream(seed, "scenario").below(count)


def sample_design(seed: str, label: str, split: str, scenario: dict) -> tuple[dict, int]:
    """The design of a kit, and how many designs were drawn before it.

    A design that cannot carry the scenario of the kit is drawn again, and
    so is a design that an exam holds out, unless the kit is sealed.
    """
    for number in range(MAX_DESIGNS):
        design = pgfix.sample(seed if number == 0 else f"{seed}/design-{number}", label)
        if not decisions.scenario_fits(scenario, design):
            continue
        if split == "sealed" or not decisions.held_out_design(design):
            return design, number
    raise KitError(f"no design for the scenario after {MAX_DESIGNS} draws")


def _reference_file(kit_dir: Path, which: str, tables: reference.Tables,
                    values: dict[str, dict], arms: list[dict]) -> Path:
    found = reference.table(tables, values, [
        reference.Arm(arm["code"], arm["dose"], tuple(arm["names"])) for arm in arms])
    path = kit_dir / gold.PLACES[which][1] / REFERENCE / f"{decisions.OUTPUT_UNIT}.json"
    write_json(path, reference.as_record(found))
    return path


def _clear_gold(kit_dir: Path) -> None:
    """Remove what an attempt wrote, and keep what the generator of the data wrote."""
    for relative in ("gold/spec", "gold/docs", gold.DECISIONS, IDENTIFIABILITY, "twin/gold",
                     "work", *(f"gold/{name}" for name in (
                         gold.RESOLVED, "data", gold.ARS_OUT, gold.ARD, gold.GRID, gold.PAGES,
                         gold.GRAPH, REFERENCE))):
        target = kit_dir / relative
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()


def all_files(kit_dir: Path) -> dict[str, str]:
    """SHA-256 of every file of a kit folder but its manifest, by path."""
    return {path.relative_to(kit_dir).as_posix(): sha256_file(path)
            for path in sorted(kit_dir.rglob("*"))
            if path.is_file() and path.relative_to(kit_dir).as_posix() != MANIFEST}


def read_manifest(kit_dir: Path) -> dict:
    with open(kit_dir / MANIFEST, encoding="ascii") as handle:
        return yaml.safe_load(handle)


def read_decisions(kit_dir: Path) -> list[dict]:
    from specfirst.machine.canonical import read_jsonl

    return read_jsonl(kit_dir / gold.DECISIONS)


def _attempt(root: Path, catalog: catalogs.Catalog, house: houses.House, kit_dir: Path,
             design: dict, values: dict[str, dict], log: list[dict],
             with_r: bool) -> tuple[dict, list[str], list[str]]:
    """Build one decision vector into the kit folder. Returns what the manifest says of
    the properties, the defects found, and why the vector does not fit the data."""
    records, document = decisions.records(catalog, house, design, values)
    try:
        compiled = gold.compile_records(catalog, house, records, bind=True)
    except compiler.CompileError as error:
        return {}, ["cannot compile: " + "; ".join(error.problems)], []
    manifest = compiled.manifest()
    binds = {(item["id"], item["unit"]): item["binds"] for item in manifest["decisions"]}
    gold.write_spec(kit_dir / gold.SPEC, compiled)
    path = kit_dir / DOCUMENT
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="ascii", newline="\n")
    arms = gold.arms_of(design, values)
    defects: list[str] = []
    properties: dict = {}
    reach: dict = {}
    for which in gold.PLACES:
        tables = study.read_tables(kit_dir, which)
        try:
            shown, _, record = gold.build(root, catalog, kit_dir, which, compiled, records, arms,
                                          with_r=with_r)
        except gold.GoldError as error:
            return {}, [f"{which}: cannot be built: {error}"], []
        made = next(iter(shown.grids.values()), None)
        _reference_file(kit_dir, which, tables, values, arms)
        differ = verify.p2(tables, values, arms, made)
        defects += [f"{which}: P2: {problem}" for problem in differ]
        defects += [f"{which}: {problem}" for problem in verify.shell_problems(kit_dir, which)]
        lines, problems = verify.p3(root, kit_dir, which, records, catalog)
        defects += [f"{which}: P3: {problem}" for problem in problems]
        engines = record.get("engines") or {}
        if with_r and not engines.get("agree"):
            defects += [f"{which}: the engines disagree: {problem}"
                        for problem in engines.get("disagreements", ["no comparison"])]
        cells = sum(len(row["cells"]) for row in made["rows"]) if made else 0
        properties[which] = {
            "subjects": record["datasets"].get("ADSL"), "events": record["datasets"].get("ADAE"),
            "results": record["results"], "cells": cells,
            "cells_equal_to_the_reference": cells - len(differ),
            "engines_agree": bool(engines.get("agree")) if with_r else None,
            "R": record.get("r"),
            "trace": lines[-2] if len(lines) >= 2 else "",
        }
        reach[which] = record["reach"]
    if defects:
        return properties, defects, []
    scratch = Path(tempfile.mkdtemp(prefix="specfirst-kit-"))
    try:
        matrix, problems, unfit = verify.mutate(
            root, catalog, house, kit_dir, "twin", design, records, reach["twin"], log,
            study.read_tables(kit_dir, "twin"), scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    defects += [f"twin: P4: {problem}" for problem in problems]
    write_json(kit_dir / IDENTIFIABILITY, matrix)
    states = verify.identifiable(matrix)
    final = [{**record, "binds": [bind for bind in binds.get((record["id"], record["unit"]), [])
                                  if not bind.startswith("layout:")],
              **({"identifiable": states[(record["id"], record["unit"])]}
                 if (record["id"], record["unit"]) in states else {})}
             for record in records]
    gold.write_decisions(kit_dir, final)
    properties["identifiability"] = matrix["summary"]
    return properties, defects, unfit


def generate(root: Path, seed: str, out: Path, split: str = "train", with_r: bool = True,
             say: Out = lambda line: None, number: int | None = None) -> dict:
    """Write one kit into `out` and return its manifest. Raises `KitError`.

    `number` is the number of the kit in a set; it gives the scenario of the
    kit. A kit of its own draws its scenario from its seed. A kit that
    cannot be written leaves nothing behind: the folder is removed.
    """
    if split not in decisions.SPLITS:
        raise KitError(f"a split is one of {', '.join(decisions.SPLITS)}, not '{split}'")
    if out.exists() and any(out.iterdir()):
        raise KitError(f"{out} is not empty")
    try:
        return _generate(root, seed, out, split, with_r, say, number)
    except Exception:
        shutil.rmtree(out, ignore_errors=True)
        raise


def _generate(root: Path, seed: str, out: Path, split: str, with_r: bool, say: Out,
              number: int | None) -> dict:
    catalog = catalogs.load(catalogs.default_dir(root))
    house = houses.load(houses.default_dir(root))
    label = study.catalog_label(catalog)
    scenario_number = scenario_of(seed, number)
    scenario = decisions.SCENARIOS[scenario_number]
    design, designs_drawn = sample_design(seed, label, split, scenario)
    generated = study.generate(root, design, seed, out)
    gold.copy_house(house, out)
    log = study.read_probes(out)
    parameters = probes.Parameters.of(design).as_record()
    rejected: list[dict] = []
    for attempt in range(MAX_ATTEMPTS):
        _clear_gold(out)
        values = decisions.sample(catalog, house, design, parameters,
                                  Stream(seed, "decisions", designs.study_id(design), attempt),
                                  split, given=scenario["values"])
        properties, defects, unfit = _attempt(root, catalog, house, out, design, values, log,
                                              with_r)
        if defects:
            shown = "; ".join(defects[:6])
            raise KitError(f"study {designs.study_id(design)}, decision vector {attempt}: "
                           f"{len(defects)} defects: {shown}")
        if not unfit:
            break
        rejected.append({"attempt": attempt, "reasons": unfit})
        say(f"study {designs.study_id(design)}: decision vector {attempt} drawn again: "
            + "; ".join(unfit))
    else:
        raise KitError(f"study {designs.study_id(design)}: no decision vector of "
                       f"{MAX_ATTEMPTS} separates every pair of alternatives that the log "
                       "of probes claims: " + "; ".join(rejected[-1]["reasons"]))
    shutil.rmtree(out / "work", ignore_errors=True)
    import pyarrow

    manifest = {
        "kit": FORMAT,
        "id": designs.study_id(design).lower(),
        "title": design["study"]["label"],
        "tier": "A",
        "archetype": design["archetype"],
        "slice": SLICE,
        "split": split,
        "generator": GENERATOR,
        "catalog": {"name": catalog.name, "version": catalog.version},
        "house": house.label,
        "seed_sha256": seed_sha256(seed),
        "pins": {
            "engines": {runner.ENGINE: runner.engine_version(), "pyarrow": pyarrow.__version__,
                        "R": properties["visible"]["R"]},
            "registry_sha256": sha256_file(registries.json_path(root)),
        },
        "study": {"id": designs.study_id(design), "arms": len(designs.arms(design)),
                  "designs_drawn_before": designs_drawn, "domains": generated["domains"],
                  "visible_share": generated["visible_share"]},
        "units": list(decisions.SLICE_UNITS),
        "datasets": list(gold.SLICE_DATASETS),
        "outputs": [{"unit": decisions.OUTPUT_UNIT,
                     "id": "Out_AESUM"}],
        "decisions": {"file": gold.DECISIONS, "document": DOCUMENT,
                      "scenario": scenario_number + 1, "given": scenario["values"],
                      "vectors_drawn_before": rejected},
        "properties": properties,
        "files": all_files(out),
    }
    write_manifest(out, manifest)
    return manifest


def write_manifest(kit_dir: Path, manifest: dict) -> None:
    (kit_dir / MANIFEST).write_text(
        yaml.safe_dump(manifest, sort_keys=False, default_flow_style=False, width=10_000,
                       allow_unicode=False), encoding="ascii", newline="\n")


# ---- a written kit, checked again ----------------------------------------------------------


def check(root: Path, kit_dir: Path, say: Out = lambda line: None,
          mutation: bool = True, engines: bool = True) -> list[str]:
    """Why a kit folder is not a kit with the properties its manifest states.

    Everything is decided again from the files of the kit: the hashes; the
    decision records and the document that states them; P2, by a new hand
    calculation from the SDTM rows; P3, from the graph files; the agreement
    of the two ARD files; and P4, by a new mutation on the twin, which must
    give the matrix the kit holds. A kit that was written without the R
    engine is a problem unless `engines` is False.
    """
    from specfirst import schemas
    from specfirst.compile.standard_form import StandardForm, StandardFormError
    from specfirst.machine import results
    from specfirst.machine.canonical import read_jsonl

    catalog = catalogs.load(catalogs.default_dir(root))
    house = houses.load(houses.default_dir(root))
    try:
        manifest = read_manifest(kit_dir)
    except (OSError, yaml.YAMLError) as error:
        return [f"no usable {MANIFEST}: {error}"]
    problems = [f"file {problem}" for problem in
                hash_differences(manifest.get("files") or {}, all_files(kit_dir))]
    wanted = {"kit": FORMAT, "tier": "A", "generator": GENERATOR, "house": house.label,
              "catalog": {"name": catalog.name, "version": catalog.version}}
    problems += [f"{MANIFEST}: '{key}' is {manifest.get(key)!r}, this checkout has {value!r}"
                 for key, value in wanted.items() if manifest.get(key) != value]
    if manifest.get("split") not in decisions.SPLITS:
        problems.append(f"{MANIFEST}: no split")
    if problems:
        return problems
    design = designs.load(kit_dir / "gold" / "design.yaml")
    records = read_decisions(kit_dir)
    values = decisions.as_values(records)
    arms = gold.arms_of(design, values)
    log = study.read_probes(kit_dir)

    # The decision records, and the documents they cite.
    for record in records:
        problems += [f"decision {record.get('id')}: {problem}"
                     for problem in schemas.problems("decision-record", record, root=root)]
    form = StandardForm(catalog)
    try:
        doc, parsed = form.parse_document((kit_dir / DOCUMENT).read_text(encoding="ascii"))
    except (OSError, StandardFormError) as error:
        doc, parsed = "", []
        problems.append(f"{DOCUMENT}: {error}")
    stated = {(r["id"], r["unit"]): r["value"] for r in records if r["status"] == "stated"}
    if {(item["id"], item["unit"]): item["value"] for item in parsed} != stated:
        problems.append(f"{DOCUMENT}: the parser does not read back the stated decisions")
    defaults = {(r["id"], r["unit"]): r["value"] for r in houses.default_decisions(catalog, house)}
    for record in records:
        key = (record["id"], record["unit"])
        cited = {citation["doc"] for citation in record.get("citations") or []}
        if record["status"] == "default" and (defaults.get(key) != record["value"]
                                              or cited != {houses.DOCUMENT_ID}):
            problems.append(f"decision {key[0]}: not the default of the house standard")
        if record["status"] == "stated" and (cited != {doc} or defaults.get(key)
                                             == record["value"]):
            problems.append(f"decision {key[0]}: stated, but it is the house default or cites "
                            "another document")
    if held_out(design, values) and manifest["split"] != "sealed":
        problems.append(f"a {manifest['split']} kit has a factor that an exam holds out")
    say(f"kit {manifest['id']} ({manifest['split']}): {len(manifest['files'])} files have the "
        f"hashes of {MANIFEST}; {len(records)} decision records fit the schema, {len(stated)} "
        f"stated in {DOCUMENT} and read back by the parser")

    reached = {}
    for which, (_, place) in gold.PLACES.items():
        tables = study.read_tables(kit_dir, which)
        made = verify.grid_of(kit_dir, which)
        differ = verify.p2(tables, values, arms, made)
        problems += [f"{which}: P2: {problem}" for problem in differ]
        path = kit_dir / place / REFERENCE / f"{decisions.OUTPUT_UNIT}.json"
        with open(path, encoding="ascii") as handle:
            kept = json.load(handle)
        again = reference.as_record(reference.table(tables, values, [
            reference.Arm(arm["code"], arm["dose"], tuple(arm["names"])) for arm in arms]))
        if kept != json.loads(json.dumps(again)):
            problems.append(f"{which}: the reference file is not the hand calculation")
        problems += [f"{which}: {problem}" for problem in verify.shell_problems(kit_dir, which)]
        lines, found = verify.p3(root, kit_dir, which, records, catalog)
        problems += [f"{which}: P3: {problem}" for problem in found]
        ard = kit_dir / place / gold.ARD
        if (ard / f"{gold.EVENT}.r.jsonl").is_file():
            rows = {name: results.by_id(read_jsonl(ard / f"{gold.EVENT}{end}"))
                    for name, end in (("Python", ".jsonl"), ("R", ".r.jsonl"))}
            agreement, disagreements = results.agreement(rows["Python"], rows["R"])
            problems += [f"{which}: the engines disagree: {problem}"
                         for problem in disagreements]
        else:
            agreement = ["the kit was written without the R engine"]
            if engines:
                problems.append(f"{which}: the kit has no results of the R engine")
        cells = sum(len(row["cells"]) for row in made["rows"]) if made else 0
        traced = next((line for line in lines if line.startswith("grid ")), "")
        say(f"  {which}: P2 {cells - len(differ)} of {cells} cells equal the hand calculation; "
            f"P3 {traced}; {'; '.join(agreement)}")
        with open(kit_dir / place / gold.GRAPH / "coverage.json", encoding="ascii") as handle:
            reached[which] = json.load(handle)["decisions"]
    if mutation:
        scratch = Path(tempfile.mkdtemp(prefix="specfirst-kit-check-"))
        try:
            matrix, defects, unfit = verify.mutate(
                root, catalog, house, kit_dir, "twin", design, records, reached["twin"], log,
                study.read_tables(kit_dir, "twin"), scratch)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
        problems += [f"twin: P4: {problem}" for problem in [*defects, *unfit]]
        with open(kit_dir / IDENTIFIABILITY, encoding="ascii") as handle:
            if json.load(handle) != json.loads(json.dumps(matrix)):
                problems.append(f"{IDENTIFIABILITY} is not the matrix a new mutation gives")
        if manifest["properties"].get("identifiability") != json.loads(json.dumps(
                matrix["summary"])):
            problems.append(f"{MANIFEST}: the identifiability summary is not that of a new "
                            "mutation")
        states = verify.identifiable(matrix)
        problems += [f"decision {r['id']}: 'identifiable' is not what the matrix says"
                     for r in records if states.get((r["id"], r["unit"])) != r.get("identifiable")
                     and (r["id"], r["unit"]) in states]
        summary = matrix["summary"]
        say(f"  twin: P4 {summary['builds']} builds of {summary['decisions']} decisions: "
            f"{len(summary['separated'])} separated, {summary['applicable']} applicable, "
            f"{len(summary['applicable_and_unseparated'])} applicable and unseparated; not "
            f"read: {', '.join(summary['unseparated_not_read']) or 'none'}; read without a "
            f"probe: {', '.join(summary['unseparated_read']) or 'none'}")
    return problems


def held_out(design: dict, values: dict[str, dict]) -> bool:
    """Whether a kit has a factor that an exam holds out (PLAN.md section 6.7)."""
    return decisions.held_out_design(design) or decisions.held_out_combination(values)


def generate_set(root: Path, seed: str, count: int, out: Path, say: Out = print,
                 first: int = 1) -> list[dict]:
    """Write the kits `first` to `first + count - 1` of the set of a seed, each checked (P1)."""
    manifests = []
    for number in range(first, first + count):
        manifest = generate_checked(root, kit_seed(seed, number), out / f"kit-{number:03d}",
                                    split_of(number), say=say, number=number)
        manifests.append(manifest)
        summary = manifest["properties"]["identifiability"]
        say(f"kit {number} of the set: {manifest['id']}, {manifest['split']}, "
            f"{len(manifest['files'])} files; {len(summary['separated'])} of "
            f"{summary['decisions']} decisions separated on the twin")
    return manifests


# ---- P1 ----------------------------------------------------------------------------------


def hash_differences(first: dict[str, str], second: dict[str, str]) -> list[str]:
    problems = [f"{name}: only in one build" for name in sorted(set(first) ^ set(second))]
    problems += [f"{name}: the hashes differ" for name in sorted(set(first) & set(second))
                 if first[name] != second[name]]
    return problems


def kit_hashes(kit_dir: Path) -> dict[str, str]:
    """SHA-256 of every file of a kit, the manifest included."""
    return {**all_files(kit_dir), MANIFEST: sha256_file(kit_dir / MANIFEST)}


def generate_apart(root: Path, seed: str, out: Path, split: str, with_r: bool = True,
                   planted: str = "", number: int | None = None,
                   hash_seed: str | None = None, zone: str | None = APART_ZONE) -> dict[str, str]:
    """`generate` in a process of its own; returns the hashes of the kit it wrote.

    The process has another seed for Python's string hashes, another time
    zone, the C locale and another working folder than this one. The seed
    of the kit goes through standard input, not through the command line.
    `planted` names a defect that the process plants in its build.
    """
    out.parent.mkdir(parents=True, exist_ok=True)
    package = str(Path(specfirst.__file__).resolve().parents[1])
    paths = [package, os.environ.get("PYTHONPATH", "")]
    if hash_seed is None:
        hash_seed = "1" if os.environ.get("PYTHONHASHSEED") != "1" else "2"
    env = {**os.environ, "PYTHONHASHSEED": hash_seed,
           "PYTHONPATH": os.pathsep.join(path for path in paths if path)}
    if zone:   # another time zone and the C locale; None keeps those of this process
        env.update({"TZ": zone, "LC_ALL": "C"})
    job = {"root": str(root.resolve()), "seed": seed, "out": str(out.resolve()), "split": split,
           "with_r": with_r, "planted": planted, "number": number}
    done = subprocess.run([sys.executable, "-B", "-m", "specfirst.gen.kits"], cwd=out.parent,
                          env=env, input=json.dumps(job), capture_output=True, text=True)
    if done.returncode != 0:
        raise KitError("a build in a process of its own failed: "
                       + (done.stderr or done.stdout).strip()[-800:])
    return kit_hashes(out)


def generate_checked(root: Path, seed: str, out: Path, split: str = "train",
                     say: Out = lambda line: None, number: int | None = None) -> dict:
    """Write a kit and build it again in a process of its own: the two must be the same
    bytes (P1). The kit is removed when they are not."""
    manifest = generate(root, seed, out, split, say=say, number=number)
    scratch = Path(tempfile.mkdtemp(prefix="specfirst-kit-p1-"))
    try:
        second = generate_apart(root, seed, scratch / "second", split, number=number)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    problems = hash_differences(kit_hashes(out), second)
    if problems:
        shutil.rmtree(out, ignore_errors=True)
        raise KitError(f"P1: two builds of the kit differ in {len(problems)} files, for example "
                       f"{problems[0]}")
    return manifest


def _planted_clock(people: list) -> str:
    """Planted defect: a time stamp that depends on the seed of Python's string hashes."""
    number = hash("specfirst") % 86400
    return f"2001-01-01T{number // 3600:02d}:{number // 60 % 60:02d}:{number % 60:02d}"


def main() -> int:
    """The build that `generate_apart` starts: the job is JSON on standard input."""
    job = json.loads(sys.stdin.read())
    if job.get("planted") == "clock":
        study.data_stamp = _planted_clock
    elif job.get("planted") == "folder":
        # A manifest that names the folder it was built in.
        original = yaml.safe_dump

        def dump(data: object, **options: object) -> str:
            if isinstance(data, dict) and data.get("kit") == FORMAT:
                data = {**data, "built_in": job["out"]}
            return original(data, **options)

        yaml.safe_dump = dump
    try:
        generate(Path(job["root"]), job["seed"], Path(job["out"]), job["split"],
                 with_r=job.get("with_r", True), number=job.get("number"),
                 say=lambda line: print(line, file=sys.stderr))
    except KitError as error:
        print(f"cannot write the kit: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
