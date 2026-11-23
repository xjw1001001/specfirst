"""One generated study: visible data, twin, log of probes, manifest (stages S2 to S4).

    <study>/
      study.json                    manifest: versions and the SHA-256 of every file
      gold/design.yaml              the design; the reader never sees it
      gold/probes.jsonl             every planted probe, in the visible data and in the twin
      gold/truth/subjects.jsonl     latent truth of the visible data, for audit
      inputs/data/sdtm/             the visible SDTM: <domain>.parquet, <domain>.json
                                    (Dataset-JSON) and define.xml
      twin/data/sdtm/               the hidden second dataset: same design, another seed
      twin/truth/subjects.jsonl     latent truth of the twin

The folder names are those of the kit format (PLAN.md section 8); gen-2
adds the decision records, the gold results and kit.yaml. Everything is a
pure function of the generator version, the design, the decision vector and
the seed (section 6.4: the decisions come first, stage S1, and the probes
are planted for them, stage S3; gen-2b). A kit gives its vector; a study of
its own draws one from its seed (`own_values`). The manifest names the
vector and holds the SHA-256 of the seed, never the seed (section 6.7).
JSON, JSONL and Parquet go through the canonical writers of the machine
(`specfirst.machine.canonical`).
"""

from __future__ import annotations

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from specfirst.compile import catalog as catalogs
from specfirst.gen import GENERATOR, datasetjson, decisions, define, probes, sdtm, subjects
from specfirst.gen import design as designs
from specfirst.gen.rng import Stream, seed_sha256
from specfirst.machine import canonical

VISIBLE = "inputs/data/sdtm"
TWIN = "twin/data/sdtm"
PLACES = {"visible": VISIBLE, "twin": TWIN}
# The share of the record probes that the visible data carry (section 6.5).
VISIBLE_SHARE = 0.5
# Numeric SDTM variables that the house specs read as floating point numbers.
_PARQUET_FLOAT = {"AGE", "VISITDY"}


class StudyError(RuntimeError):
    """The study cannot be generated."""


def catalog_label(catalog: catalogs.Catalog) -> str:
    """How every generated file names the catalog it was made for."""
    return f"{catalog.name} {catalog.version}"


def system(catalog: str) -> dict:
    """What wrote a file: the generator and the catalog version its probes come from."""
    return {"name": "specfirst generator", "version": f"{GENERATOR} catalog {catalog}"}


def own_values(catalog: catalogs.Catalog, design: dict, seed: str,
               root: Path | None = None) -> dict[str, dict]:
    """The decision vector of a study of its own (no kit gives it one): drawn from the seed
    within the default house standard of the checkout `root` (None: this package's), as
    a kit of that study without a scenario draws its vector."""
    from specfirst.compile import house as houses

    house = houses.load(houses.default_dir(root))
    return decisions.sample(catalog, house, design, probes.Parameters.of(design).as_record(),
                            Stream(seed, "decisions", designs.study_id(design), 0))


def simulate(design: dict, catalog: catalogs.Catalog, seed: str, which: str,
             visible_share: float = VISIBLE_SHARE, values: dict[str, dict] | None = None,
             ) -> tuple[list[subjects.Subject], list[dict]]:
    """The subjects of one dataset and the log of the probes planted in it, for the
    decision vector `values` (stage S3 after S1); without one, the vector of a study of
    its own (`own_values`)."""
    if which not in PLACES:
        raise StudyError(f"a study has the datasets {sorted(PLACES)}, not '{which}'")
    if values is None:
        values = own_values(catalog, design, seed)
    rng = Stream(seed, "study", designs.study_id(design), which)
    ctx = subjects.Context.of(design)
    share = 1.0 if which == "twin" else visible_share
    picked = probes.chosen(catalog, design, rng.child("probes"), share)
    people = subjects.base_subjects(ctx, rng.child("base"), probes.spared_arm(design, picked))
    planted = probes.plant(ctx, catalog, people, rng.child("probes"), picked, values)
    subjects.assign_identifiers(design, people)
    return people, probes.log(design, catalog, which, planted, people, values)


def _arrow(domain: sdtm.Domain, rows: list[dict], note: dict) -> pa.Table:
    columns = {}
    for variable in domain.variables:
        values = [row[variable.name] for row in rows]
        if variable.kind == "float" or variable.name in _PARQUET_FLOAT:
            kind = pa.float64()
            values = [None if v is None else float(v) for v in values]
        elif variable.kind == "integer":
            kind = pa.int64()
        else:
            kind = pa.string()
        columns[variable.name] = pa.array(values, type=kind)
    metadata = {b"specfirst": canonical.json_text(note).encode("ascii")}
    return canonical.canonical_table(pa.table(columns)).replace_schema_metadata(metadata)


def write_parquet(path: Path, table: pa.Table) -> None:
    """Parquet as `specfirst.machine.canonical.write_parquet` writes it, with the schema note.

    The canonical writer drops schema metadata; a generated dataset keeps
    one key that names the generator and the catalog. Every other option is
    the canonical one, so the bytes are fixed under the pinned pyarrow.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, path, version="2.6", data_page_version="1.0", compression="zstd",
                   compression_level=3, use_dictionary=True, write_statistics=True,
                   row_group_size=1 << 20, store_schema=True)


def write_dataset(folder: Path, design: dict, tables: dict[str, list[dict]], catalog: str,
                  stamp: str) -> None:
    """Write every domain as Parquet and Dataset-JSON, and the Define-XML that describes them."""
    folder.mkdir(parents=True, exist_ok=True)
    study = designs.study_id(design)
    made_by = system(catalog)
    note = {"generator": GENERATOR, "catalog": catalog, "study": study}
    for name, rows in tables.items():
        domain = sdtm.DOMAINS[name]
        write_parquet(folder / f"{name.lower()}.parquet", _arrow(domain, rows, note))
        text = datasetjson.render(domain, rows, study, stamp, made_by)
        (folder / f"{name.lower()}.json").write_text(text, encoding="ascii", newline="\n")
    text = define.render(
        study, design["study"]["label"], tables, sdtm.study_codelists(design, tables), stamp,
        made_by, f"Generated by specfirst {GENERATOR} for the catalog {catalog}")
    (folder / "define.xml").write_text(text, encoding="ascii", newline="\n")


def data_stamp(people: list[subjects.Subject]) -> str:
    """The creation time written into the files: the last study date, never the clock."""
    last = max(s.end_of_study for s in people if s.end_of_study is not None)
    return f"{last.isoformat()}T00:00:00"


def file_hashes(folder: Path) -> dict[str, str]:
    """SHA-256 of every file of a study folder but the manifest and CORE reports, by path."""
    return {path.relative_to(folder).as_posix(): canonical.sha256_file(path)
            for path in sorted(folder.rglob("*"))
            if path.is_file() and path.name != "study.json"
            and path.relative_to(folder).parts[0] != "core"}


def generate(root: Path, design: dict, seed: str, out: Path,
             domains: tuple[str, ...] = sdtm.SLICE_DOMAINS,
             visible_share: float = VISIBLE_SHARE,
             values: dict[str, dict] | None = None) -> dict:
    """Write one study folder and return its manifest. The probes are planted for the
    decision vector `values` (a kit's); without one, for the vector of a study of its own
    (`own_values`). The manifest names the vector."""
    catalog = catalogs.load(catalogs.default_dir(root))
    label = catalog_label(catalog)
    if design.get("catalog") != label:
        raise StudyError(f"the design was sampled for the catalog '{design.get('catalog')}'; "
                         f"this checkout has '{label}'. Sample the design again.")
    found = designs.problems(design)
    if found:
        raise StudyError("; ".join(found))
    if values is None:
        values = own_values(catalog, design, seed, root)
    out.mkdir(parents=True, exist_ok=True)
    (out / "gold").mkdir(exist_ok=True)
    header = (f"# design.yaml of the study {designs.study_id(design)}: generated by specfirst "
              f"{GENERATOR}\n# for the catalog {label}. Gold: never shown to a reader.\n")
    (out / "gold" / "design.yaml").write_text(header + designs.dump(design), encoding="ascii",
                                              newline="\n")
    log: list[dict] = []
    counts = {}
    for which, place in PLACES.items():
        people, planted = simulate(design, catalog, seed, which, visible_share, values)
        tables = sdtm.build(design, people, domains)
        write_dataset(out / place, design, tables, label, data_stamp(people))
        truth = out / ("gold" if which == "visible" else "twin") / "truth" / "subjects.jsonl"
        canonical.write_jsonl(truth, [{"catalog": label, "generator": GENERATOR,
                                       **subjects.as_record(person)} for person in people])
        log += planted
        counts[which] = {"subjects": len(people),
                         "records": {name: len(rows) for name, rows in tables.items()}}
    canonical.write_jsonl(out / "gold" / "probes.jsonl", log)
    manifest = {
        "generator": GENERATOR,
        "catalog": {"name": catalog.name, "version": catalog.version},
        "archetype": design["archetype"],
        "study": designs.study_id(design),
        "seed_sha256": seed_sha256(seed),
        "sdtmig": sdtm.SDTMIG_VERSION,
        "domains": [name for name in sdtm.ORDER if name in domains],
        "visible_share": visible_share,
        "decisions": {key: values[key] for key in sorted(values)},
        "counts": counts,
        "files": file_hashes(out),
    }
    canonical.write_json(out / "study.json", manifest)
    return manifest


def read_manifest(folder: Path) -> dict:
    with open(folder / "study.json", encoding="ascii") as handle:
        return json.load(handle)


def read_probes(folder: Path) -> list[dict]:
    return canonical.read_jsonl(folder / "gold" / "probes.jsonl")


def read_tables(folder: Path, which: str) -> dict[str, list[dict]]:
    """The SDTM of a study as rows, read back from the Dataset-JSON files."""
    place = folder / PLACES[which]
    tables = {}
    for name in sdtm.ORDER:
        path = place / f"{name.lower()}.json"
        if path.is_file():
            tables[name] = datasetjson.read_rows(path)[1]
    return tables
