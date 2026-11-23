"""A kit of a generated study (PLAN.md sections 6.4, 6.7 and 8), for the slice of ADR-005.

    <kit>/
      kit.yaml                  the manifest: id, tier, archetype, split, generator,
                                pins, the properties, the SHA-256 of every file
      study.json                the manifest of the generated data (stages S2 to S4)
      inputs/data/sdtm/         the visible SDTM, with its Define-XML
      inputs/house/             the house standard: document, parent specs, templates
      inputs/docs/              protocol.md and sap.md in natural form (document IDs
                                protocol and sap)
      gold/design.yaml  probes.jsonl  truth/     from the generator of the data
      gold/decisions.jsonl      the decision vector: value, status, class, statement,
                                citations, binds, identifiable
      gold/docs/                protocol.md and sap.md in standard form (protocol-standard,
                                sap-standard); natural.json, where every paragraph of the
                                natural form came from
      gold/oracle.yaml          the answers of the oracle; gold/summary.md, one page
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

The decisions come first (section 6.4, stage S1 before S3; gen-2b,
docs/decisions/ADR-023.md): the decision vector of a kit is drawn from its
design and seed, and the data are generated for it, the probes planted to
separate its decisions (`study.generate` with the vector).

`generate` writes a kit only when it has the properties P2 to P4 and its two
result engines agree. P4 includes: every decision that the output reads is
separated on the twin, unless another decision of the kit makes its
alternatives give the same output on any data of the design that follow
SDTMIG v3.4 (`probes.REACHES`). A kit in which one is not separated is not
written; no other vector is drawn for it.
A kit that cannot be written leaves no folder. `generate_checked` builds the
kit a second time in a process of its own and compares every hash (P1).

Documents (stage S6, specfirst.gen.documents). The tier of the documents of
kit n of a set is `documents.TIER_PLAN`; a kit of its own draws full or
standard from its seed. The natural form comes from the store of model text
(specfirst.gen.natural); the manifest counts its paragraphs by where they
came from, and lists the probes of the visible data and of the twin.

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
from specfirst.compile import compiler, versions
from specfirst.compile import house as houses
from specfirst.gen import (
    GENERATOR,
    decisions,
    documents,
    gold,
    pgfix,
    probes,
    reference,
    study,
    verify,
)
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream, seed_sha256
from specfirst.machine import registry as registries
from specfirst.machine import runner
from specfirst.machine.canonical import sha256_file, write_json

Out = Callable[[str], None]
FORMAT = 1
MANIFEST = "kit.yaml"
SLICE = "ae-summary-first"
APART_ZONE = "Pacific/Kiritimati"
MAX_DESIGNS = 50
# The split of the kits of a set, by their number: four train, three dev, three test.
SPLIT_PLAN = ("train", "train", "train", "train", "dev", "dev", "dev", "test", "test", "test")
IDENTIFIABILITY = "gold/identifiability.json"
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


def draw_values(catalog: catalogs.Catalog, house: houses.House, design: dict, seed: str,
                split: str, given: dict[str, str]) -> dict[str, dict]:
    """Stage S1: the decision vector of a kit, drawn from its design and seed before any
    data exist; `given` fixes the decisions of its scenario."""
    return decisions.sample(catalog, house, design, probes.Parameters.of(design).as_record(),
                            Stream(seed, "decisions", designs.study_id(design), 0),
                            split, given=given)


def unfollowed(values: dict[str, dict]) -> dict[str, dict]:
    """Planted defect (gate gen-2b, rule R5): the vector that the probes of gen-2a were built
    for whatever a kit decided. The count probes then hold for the safety set grouped by
    actual treatment from DM.ACTARM at one decimal, and a planted subject may stop before
    the visits that the kit's analysis set asks for."""
    changed = {**values, "tfl.population": {"rule": "safety"},
               "pop.safety.grouping": {"rule": "actual"},
               "trt.actual.source": {"rule": "dm_actarm"}}
    changed["tfl.percent.format"] = {**values["tfl.percent.format"], "decimals": 1}
    return changed


def _reference_file(kit_dir: Path, which: str, tables: reference.Tables,
                    values: dict[str, dict], arms: list[dict]) -> Path:
    found = reference.table(tables, values, [
        reference.Arm(arm["code"], arm["dose"], tuple(arm["names"])) for arm in arms])
    path = kit_dir / gold.PLACES[which][1] / REFERENCE / f"{decisions.OUTPUT_UNIT}.json"
    write_json(path, reference.as_record(found))
    return path


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
             design: dict, values: dict[str, dict], log: list[dict], with_r: bool,
             tier: str, stream: Stream) -> tuple[dict, list[str], list[str]]:
    """Build one decision vector into the kit folder. Returns what the manifest says of
    the properties (and of the documents), the defects found, and why the vector does not
    fit the data."""
    listed = decisions.vector(catalog, house, design, values)
    records, written = documents.write(catalog, house, design, listed, tier,
                                       decisions.SLICE_UNITS, stream, kit_dir)
    try:
        compiled = gold.compile_records(catalog, house, records, bind=True)
    except compiler.CompileError as error:
        return {}, ["cannot compile: " + "; ".join(error.problems)], []
    manifest = compiled.manifest()
    binds = {(item["id"], item["unit"]): item["binds"] for item in manifest["decisions"]}
    gold.write_spec(kit_dir / gold.SPEC, compiled)
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
    properties["documents"] = written
    return properties, defects, unfit


def generate(root: Path, seed: str, out: Path, split: str = "train", with_r: bool = True,
             say: Out = lambda line: None, number: int | None = None,
             tier: str | None = None) -> dict:
    """Write one kit into `out` and return its manifest. Raises `KitError`.

    `number` is the number of the kit in a set; it gives the scenario of the
    kit and the tier of its documents. A kit of its own draws both from its
    seed; `tier` names the tier instead. A kit that cannot be written leaves
    nothing behind: the folder is removed.
    """
    if split not in decisions.SPLITS:
        raise KitError(f"a split is one of {', '.join(decisions.SPLITS)}, not '{split}'")
    if tier is not None and tier not in documents.TIERS:
        raise KitError(f"a tier is one of {', '.join(documents.TIERS)}, not '{tier}'")
    if out.exists() and any(out.iterdir()):
        raise KitError(f"{out} is not empty")
    try:
        return _generate(root, seed, out, split, with_r, say, number,
                         tier or documents.tier_of(seed, number))
    except Exception:
        shutil.rmtree(out, ignore_errors=True)
        raise


def _generate(root: Path, seed: str, out: Path, split: str, with_r: bool, say: Out,
              number: int | None, tier: str) -> dict:
    catalog = catalogs.load(catalogs.default_dir(root))
    house = houses.load(houses.default_dir(root))
    try:  # a kit names frozen versions only (ADR-020, decision 1)
        versions.require_usable(root, [catalog.label, house.label], "a generated kit")
    except versions.VersionError as error:
        raise KitError(str(error)) from None
    label = study.catalog_label(catalog)
    scenario_number = scenario_of(seed, number)
    scenario = decisions.SCENARIOS[scenario_number]
    design, designs_drawn = sample_design(seed, label, split, scenario)
    # Stage S1: the decision vector, from the design alone. Then the data, made for it.
    values = draw_values(catalog, house, design, seed, split, scenario["values"])
    generated = study.generate(root, design, seed, out, values=values)
    gold.copy_house(house, out)
    log = study.read_probes(out)
    properties, defects, unfit = _attempt(
        root, catalog, house, out, design, values, log, with_r, tier,
        Stream(seed, "documents", designs.study_id(design), 0))
    if defects:
        raise KitError(f"study {designs.study_id(design)}: {len(defects)} defects: "
                       + "; ".join(defects[:6]))
    if unfit:
        named = sorted({line.split(":")[0] for line in unfit})
        raise KitError(f"study {designs.study_id(design)}: the twin does not separate "
                       f"{len(unfit)} pairs of alternatives that the output reads and that "
                       "no other decision makes equal: " + "; ".join(unfit[:6])
                       + f" (decisions: {', '.join(named)})")
    shutil.rmtree(out / "work", ignore_errors=True)
    import pyarrow

    written = properties.pop("documents")

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
        "decisions": {"file": gold.DECISIONS,
                      "scenario": scenario_number + 1, "given": scenario["values"]},
        "documents": written,
        "probes": probe_lists(log),
        "properties": properties,
    }
    records = read_decisions(out)
    (out / documents.SUMMARY).write_text(
        documents.summary(manifest, design, records, manifest["probes"]["visible"],
                          manifest["probes"]["twin"]), encoding="ascii", newline="\n")
    manifest["files"] = all_files(out)
    write_manifest(out, manifest)
    return manifest


def probe_lists(log: list[dict]) -> dict[str, list[str]]:
    """The probes of the log of a kit, by dataset (section 6.5: the visible data carry a
    part of them, recorded in the kit)."""
    return {which: sorted({line["probe"] for line in log if line["data"] == which})
            for which in gold.PLACES}


def write_manifest(kit_dir: Path, manifest: dict) -> None:
    (kit_dir / MANIFEST).write_text(
        yaml.safe_dump(manifest, sort_keys=False, default_flow_style=False, width=10_000,
                       allow_unicode=False), encoding="ascii", newline="\n")


# ---- a written kit, checked again ----------------------------------------------------------


def check(root: Path, kit_dir: Path, say: Out = lambda line: None,
          mutation: bool = True, engines: bool = True) -> list[str]:
    """Why a kit folder is not a kit with the properties its manifest states.

    Everything is decided again from the files of the kit: the hashes; the
    decision records and the documents that state them (every check of
    `documents.problems`); P2, by a new hand
    calculation from the SDTM rows; P3, from the graph files; the agreement
    of the two ARD files; and P4, by a new mutation on the twin, which must
    give the matrix the kit holds. A kit that was written without the R
    engine is a problem unless `engines` is False.
    """
    from specfirst import schemas
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
    found, counted = documents.problems(catalog, house, kit_dir, manifest, records, design, log)
    problems += [f"documents, {check}: {problem}" for check, items in found.items()
                 for problem in items]
    if held_out(design, values) and manifest["split"] != "sealed":
        problems.append(f"a {manifest['split']} kit has a factor that an exam holds out")
    say(f"kit {manifest['id']} ({manifest['split']}): {len(manifest['files'])} files have the "
        f"hashes of {MANIFEST}; {len(records)} decision records fit the schema; documents "
        f"of the tier {manifest['documents']['tier']}: {counted['recovered']} of "
        f"{counted['decisions']} decisions recovered by the parser with the house standard "
        f"and the oracle, {counted['paragraphs']} natural paragraphs pass the slot and "
        f"read-back checks, {counted['citations']} citations stand at their anchors, "
        f"{counted['visible probes']} visible probes found")

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
            f"read: {', '.join(summary['unseparated_not_read']) or 'none'}; read, and equal "
            f"under the other decisions on any data: "
            f"{', '.join(summary['unseparated_read']) or 'none'}")
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
                   hash_seed: str | None = None, zone: str | None = APART_ZONE,
                   tier: str | None = None) -> dict[str, str]:
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
           "with_r": with_r, "planted": planted, "number": number, "tier": tier}
    done = subprocess.run([sys.executable, "-B", "-m", "specfirst.gen.kits"], cwd=out.parent,
                          env=env, input=json.dumps(job), capture_output=True, text=True)
    if done.returncode != 0:
        raise KitError("a build in a process of its own failed: "
                       + (done.stderr or done.stdout).strip()[-800:])
    return kit_hashes(out)


def generate_checked(root: Path, seed: str, out: Path, split: str = "train",
                     say: Out = lambda line: None, number: int | None = None,
                     tier: str | None = None) -> dict:
    """Write a kit and build it again in a process of its own: the two must be the same
    bytes (P1). The kit is removed when they are not."""
    manifest = generate(root, seed, out, split, say=say, number=number, tier=tier)
    scratch = Path(tempfile.mkdtemp(prefix="specfirst-kit-p1-"))
    try:
        second = generate_apart(root, seed, scratch / "second", split, number=number,
                                tier=tier)
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
    elif job.get("planted") == "unfollowed":
        # Probes that do not follow the decisions of the kit (gen-2a's generator).
        original_generate = study.generate

        def generate_unfollowed(*args: object, values: dict | None = None,
                                **options: object) -> dict:
            return original_generate(*args, values=unfollowed(values), **options)

        study.generate = generate_unfollowed
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
                 say=lambda line: print(line, file=sys.stderr), tier=job.get("tier"))
    except KitError as error:
        print(f"cannot write the kit: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
