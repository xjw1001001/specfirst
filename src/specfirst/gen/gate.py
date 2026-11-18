"""The checks of the gate gen-1a (PLAN.md section 13.5, docs/decisions/ADR-005.md).

The gate of gen-1, for the datasets and the decisions of the slice:

    for 10 seeds, visible and twin SDTM pass CDISC CORE with no unexplained
    error; generating again gives identical hashes; probes.jsonl shows at
    least one probe in the twin for every pair of alternatives.

"Generating again" is done by a process of its own, with another seed for
Python's string hashes, another time zone, the C locale and another working
folder; the manifest of a study is compared like every other file.

A fourth check stands beside CORE: CORE 1.0.0 does not report a value
outside its codelist, so the gate compares every controlled term that was
written with the terminology package that CORE ships.

Each check first fails on planted defects (rule R5); only then does it
count. The studies are generated in a scratch folder under the system's
temporary folder and removed afterwards.

A finding of CORE is explained when `core_findings.yaml` names its rule
and the condition written there holds for this finding. Everything else is
unexplained and fails the gate.
"""

from __future__ import annotations

import copy
import os
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

import specfirst
from specfirst import cdisccore
from specfirst.compile import catalog as catalogs
from specfirst.gen import datasetjson, pgfix, present, probes, sdtm, study, terms
from specfirst.gen import design as designs
from specfirst.machine import canonical
from specfirst.paths import build_dir

Out = Callable[[str], None]

# The seeds of the gate. They are development seeds and may be read by anyone;
# seeds of dev, test and sealed kits are never written into the repository.
SEEDS = tuple(f"gen-1a-{number}" for number in range(1, 11))
FINDINGS_FILE = Path(__file__).with_name("core_findings.yaml")
STANDARD = "SDTMIG V3.4"
DEFINE_VERSION = "2.1.0"


def scratch_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="specfirst-gen1a-"))


def generate_all(root: Path, folder: Path, seeds: tuple[str, ...] = SEEDS) -> dict[str, dict]:
    """One study per seed in `folder/<seed>`; returns the manifests."""
    catalog = catalogs.load(catalogs.default_dir(root))
    manifests = {}
    for seed in seeds:
        design = pgfix.sample(seed, study.catalog_label(catalog))
        manifests[seed] = study.generate(root, design, seed, folder / seed)
    return manifests


# -- determinism ---------------------------------------------------------------


def hash_differences(first: dict[str, str], second: dict[str, str]) -> list[str]:
    """Files that two builds of one study do not share byte for byte."""
    problems = [f"{name}: only in one build" for name in sorted(set(first) ^ set(second))]
    problems += [f"{name}: the hashes differ" for name in sorted(set(first) & set(second))
                 if first[name] != second[name]]
    return problems


def build_hashes(folder: Path) -> dict[str, str]:
    """SHA-256 of every file of a study folder, the manifest included."""
    return {**study.file_hashes(folder),
            "study.json": canonical.sha256_file(folder / "study.json")}


# The second build of the gate runs in a process of its own. It differs from
# the gate's process in what a build must not depend on: the seed of Python's
# string hashes, the time zone, the locale and the working folder.
APART_ZONE = "Pacific/Kiritimati"


def other_hash_seed() -> str:
    """A PYTHONHASHSEED that the running process does not have."""
    return "1" if os.environ.get("PYTHONHASHSEED") != "1" else "2"


def generate_apart(root: Path, folder: Path, seeds: tuple[str, ...], hash_seed: str,
                   planted: bool = False) -> dict[str, dict[str, str]]:
    """`generate_all` in a process of its own; returns the hashes of every study.

    `planted` makes the build depend on the hash seed of its process, as a
    writer does that walks a set of texts.
    """
    folder.mkdir(parents=True, exist_ok=True)
    package = str(Path(specfirst.__file__).resolve().parents[1])
    paths = [package, os.environ.get("PYTHONPATH", "")]
    env = {**os.environ, "PYTHONHASHSEED": hash_seed, "TZ": APART_ZONE, "LC_ALL": "C",
           "PYTHONPATH": os.pathsep.join(path for path in paths if path)}
    argv = [sys.executable, "-B", "-m", "specfirst.gen.gate", str(root.resolve()),
            str(folder.resolve()), "planted" if planted else "honest", *seeds]
    done = subprocess.run(argv, cwd=folder, env=env, capture_output=True, text=True)
    if done.returncode != 0:
        raise RuntimeError("a build in a process of its own failed: "
                           + (done.stderr or done.stdout).strip()[-600:])
    return {seed: build_hashes(folder / seed) for seed in seeds}


def _hash_stamp(people: list) -> str:
    """Planted defect: a time stamp that depends on the seed of Python's string hashes."""
    number = hash("specfirst") % 86400
    return f"2001-01-01T{number // 3600:02d}:{number // 60 % 60:02d}:{number % 60:02d}"


def main(argv: list[str]) -> int:
    """The build that `generate_apart` starts: `<root> <folder> honest|planted <seed>...`."""
    root, folder, mode, *seeds = argv
    if mode == "planted":
        study.data_stamp = _hash_stamp
    generate_all(Path(root), Path(folder), tuple(seeds))
    return 0


def determinism_check(root: Path, out: Out, folder: Path,
                      seeds: tuple[str, ...] = SEEDS) -> bool:
    """Generate every study twice and compare the hashes of all files, the manifest included.

    The first build is made by the gate's process, the second by a process
    of its own (`generate_apart`).
    """
    catalog = catalogs.load(catalogs.default_dir(root))
    label = study.catalog_label(catalog)
    planted_in = folder / "planted"

    # Planted defect: a build that stamps its files with another time than the
    # study date, as a writer that reads the clock would.
    design = pgfix.sample(seeds[0], label)
    study.generate(root, design, seeds[0], planted_in / "honest")
    stamp = study.data_stamp
    study.data_stamp = lambda people: "2001-01-01T00:00:01"
    try:
        study.generate(root, design, seeds[0], planted_in / "clocked")
    finally:
        study.data_stamp = stamp
    honest = build_hashes(planted_in / "honest")
    planted = hash_differences(honest, build_hashes(planted_in / "clocked"))
    if not planted:
        out("the comparison did not see a build that stamps its files with another time")
        return False
    out(f"planted defect: a build with another time stamp differs in {len(planted)} files, "
        f"for example {planted[0]}")

    # Planted defect: a manifest that differs while every other file is the same.
    shutil.copytree(planted_in / "honest", planted_in / "manifest")
    manifest = study.read_manifest(planted_in / "manifest")
    manifest["counts"]["twin"]["subjects"] += 1
    canonical.write_json(planted_in / "manifest" / "study.json", manifest)
    planted = hash_differences(honest, build_hashes(planted_in / "manifest"))
    if planted != ["study.json: the hashes differ"]:
        out(f"the comparison did not see a manifest that alone differs, but {planted[:3]}")
        return False
    out(f"planted defect: a study whose manifest alone differs: {planted[0]}")

    # Planted defect: a build that depends on the seed of Python's string
    # hashes, made by two processes with two seeds.
    one = generate_apart(root, planted_in / "hash-1", seeds[:1], "1", planted=True)
    two = generate_apart(root, planted_in / "hash-2", seeds[:1], "2", planted=True)
    planted = hash_differences(one[seeds[0]], two[seeds[0]])
    if not planted:
        out("the comparison did not see a build that depends on the hash seed of its process")
        return False
    out(f"planted defect: a build that depends on the hash seed of its process, made by two "
        f"processes: differs in {len(planted)} files")

    manifests = generate_all(root, folder / "first", seeds)
    hash_seed = other_hash_seed()
    second = generate_apart(root, folder / "second", seeds, hash_seed)
    problems = []
    files = 0
    for seed in seeds:
        first = build_hashes(folder / "first" / seed)
        files += len(first)
        problems += [f"seed {seed}: {problem}" for problem in
                     hash_differences(first, second[seed])]
        problems += [f"seed {seed}: manifest: {problem}" for problem in hash_differences(
            manifests[seed]["files"], study.file_hashes(folder / "first" / seed))]
        if design_text(root, seed) != (folder / "first" / seed / "gold" / "design.yaml") \
                .read_text(encoding="ascii").split("\n", 2)[2]:
            problems.append(f"seed {seed}: the design written is not the design sampled")
    for problem in problems[:20]:
        out(problem)
    subjects = sum(m["counts"][which]["subjects"] for m in manifests.values()
                   for which in ("visible", "twin"))
    out(f"{len(seeds)} seeds, each generated twice, by this process and by a process of its "
        f"own (hash seed {hash_seed}, time zone {APART_ZONE}, locale C, its own working "
        f"folder): {files} files and {subjects} subjects per build, the manifests included, "
        f"catalog {label}")
    out(f"identical hashes: {len(problems)} problems")
    return not problems


def design_text(root: Path, seed: str) -> str:
    catalog = catalogs.load(catalogs.default_dir(root))
    return designs.dump(pgfix.sample(seed, study.catalog_label(catalog)))


# -- CDISC CORE ----------------------------------------------------------------


def load_explained(path: Path = FINDINGS_FILE) -> dict:
    with open(path, encoding="ascii") as handle:
        return yaml.safe_load(handle)


def _holds(entry: dict, finding: cdisccore.Finding, rows: list[dict] | None,
           owners: dict[str, set[str]]) -> bool:
    """Whether an entry of core_findings.yaml explains one finding.

    `rows` are the records of the dataset the finding names, or None when
    the study has no such dataset.
    """
    if finding.rule not in entry["rules"]:
        return False
    if entry.get("datasets") and finding.dataset not in entry["datasets"]:
        return False
    kind = entry["kind"]
    if kind == "cannot_run":
        text = " ".join(str(example.get("values", "")) + " " + str(example.get("message", ""))
                        for example in finding.examples) + " " + finding.message
        return finding.status == cdisccore.EXECUTION_ERROR and entry["text"] in text
    if finding.status != cdisccore.ISSUE:
        return False
    if kind == "dataset":
        return finding.count == 1 and not finding.subjects
    if kind == "every_record":
        return rows is not None and finding.count == len(rows)
    if kind == "repeated_key":
        if rows is None:
            return False
        # As for a probe: every issue is a detail row that names a subject, and the
        # subjects are exactly those of the records with a repeated key. The number
        # alone would explain a finding of the right size about other records.
        keys = [tuple(row.get(name) for name in entry["key"]) for row in rows]
        counts: dict[tuple, int] = {}
        for key in keys:
            counts[key] = counts.get(key, 0) + 1
        repeated = sum(number for number in counts.values() if number > 1)
        subjects = {row.get("USUBJID") for row, key in zip(rows, keys, strict=True)
                    if counts[key] > 1}
        return repeated > 0 and finding.count == repeated == finding.listed == finding.named \
            and set(finding.subjects) == subjects
    if kind == "study":
        return finding.count == 1 and not finding.subjects
    if kind == "probe":
        # Every issue must be a detail row that names a subject: otherwise the
        # subjects that happen to be listed would explain issues nobody saw.
        allowed = set().union(*(owners.get(probe, set()) for probe in entry["probes"]))
        return bool(finding.subjects) and set(finding.subjects) <= allowed \
            and finding.count == finding.listed == finding.named
    raise ValueError(f"core_findings.yaml: unknown kind '{kind}'")


def describe(finding: cdisccore.Finding) -> str:
    """One finding as a line of a gate log."""
    subjects = ", ".join(finding.subjects[:3])
    more = f" and {len(finding.subjects) - 3} more" if len(finding.subjects) > 3 else ""
    return (f"{finding.rule} {finding.dataset or '-'} ({finding.status.lower()}, "
            f"{finding.count} issues{', ' + subjects + more if subjects else ''}): "
            f"{finding.message[:140]}")


def classify(report: cdisccore.Report, explained: dict, tables: dict[str, list[dict]],
             log: list[dict], which: str) -> tuple[dict[str, int], list[cdisccore.Finding]]:
    """How many findings each explanation covers, and the findings that none covers."""
    owners: dict[str, set[str]] = {}
    for record in log:
        if record["data"] == which:
            owners.setdefault(record["probe"], set()).update(record["subjects"])
    used: dict[str, int] = {}
    unexplained = []
    for finding in report.findings:
        rows = tables.get(finding.dataset)
        for entry in explained["explained"]:
            if _holds(entry, finding, rows, owners):
                used[entry["id"]] = used.get(entry["id"], 0) + 1
                break
        else:
            unexplained.append(finding)
    return used, unexplained


# A run of CORE needs up to this much memory with the pool size of the runner.
CORE_RUN_MEMORY_MB = 3000
# The machine is shared: no more than this many worker processes at once, over
# all runs of CORE that the gate has started.
MAX_WORKERS = 4


def core_workers(available_mb: int | None = None, processors: int | None = None) -> int:
    """How many runs of CORE the gate starts at once.

    At most MAX_WORKERS worker processes in all, and within half of the free
    memory. Other sessions share the machine: too many runs at once once
    exhausted its memory, and the kernel ended processes of every session
    (docs/lessons.md, lesson 32).
    """
    if available_mb is None:
        available_mb = available_memory_mb()
    if processors is None:
        processors = os.cpu_count() or 1
    by_rule = MAX_WORKERS // cdisccore.POOL_SIZE
    by_memory = (available_mb // 2) // CORE_RUN_MEMORY_MB
    by_processors = processors // (2 * cdisccore.POOL_SIZE)
    return max(1, min(by_rule, by_memory, by_processors))


def available_memory_mb() -> int:
    """MemAvailable of /proc/meminfo; a small number where there is no such file."""
    try:
        with open("/proc/meminfo", encoding="ascii") as handle:
            for line in handle:
                if line.startswith("MemAvailable:"):
                    return int(line.split()[1]) // 1024
    except OSError:
        pass
    return 2 * CORE_RUN_MEMORY_MB


def run_core(root: Path, folder: Path, which: str) -> cdisccore.Report:
    place = folder / study.PLACES[which]
    datasets = sorted(place.glob("*.json"))
    return cdisccore.validate(root, datasets, folder / "core" / which,
                              define=place / "define.xml")


def report_problems(root: Path, report: cdisccore.Report,
                    tables: dict[str, list[dict]]) -> list[str]:
    """Why a report is not one of the pinned CORE on these datasets.

    `tables` are the datasets that were handed to CORE. The report must
    name each of them with its number of records and no other, the
    Define-XML that CORE read, and the controlled terminology package that
    the Define-XML names.
    """
    pin = cdisccore.read_pin(root)
    problems = []
    if report.engine != pin.version:
        problems.append(f"the report is of CORE {report.engine}, the pin is {pin.version}")
    if report.standard != STANDARD:
        problems.append(f"the report is for {report.standard}, not {STANDARD}")
    if len(report.rules) < 100:
        problems.append(f"only {len(report.rules)} rules ran")
    handed = {name: len(rows) for name, rows in tables.items()}
    if report.records != handed:
        names = sorted(name for name in set(handed) | set(report.records)
                       if handed.get(name) != report.records.get(name))
        problems.append("CORE did not read the datasets as they were handed over: "
                        + ", ".join(f"{name} {report.records.get(name, 'not read')} of "
                                    f"{handed.get(name, 'no')} records" for name in names))
    if report.define != DEFINE_VERSION:
        problems.append(f"CORE read the Define-XML as '{report.define}', not {DEFINE_VERSION}")
    if report.terminology != f"sdtmct-{terms.CT_PACKAGE}":
        problems.append(f"CORE used the terminology '{report.terminology}', not "
                        f"sdtmct-{terms.CT_PACKAGE}")
    return problems


def _rewrite(place: Path, change: Callable[[dict[str, list[dict]]], None], design: dict,
             label: str, stamp: str) -> None:
    """Change the rows of a study copy and write its datasets again."""
    tables = {}
    for domain in sdtm.ORDER:
        path = place / f"{domain.lower()}.json"
        if path.is_file():
            tables[domain] = datasetjson.read_rows(path)[1]
    change(tables)
    study.write_dataset(place, design, tables, label, stamp)


# The rules of CORE that must report the two planted defects.
RULE_SEQUENCE = "CORE-000544"            # --SEQ is unique within a subject
RULES_ARM = ("CORE-000655", "CORE-000656")   # planned and actual arm agree


def planted_core_defects(root: Path, out: Out, source: Path, folder: Path, explained: dict,
                         design: dict, label: str) -> bool:
    """CORE and the list of explained findings must catch two planted defects.

    Both are planted in subjects that no probe touched, in a copy of a twin:

    - Two adverse events of one subject get the same AESEQ. CORE must report
      it, and the entry that explains the same rule for the dataset SV must
      not cover the dataset AE.
    - One subject gets another actual arm than the planned one. CORE reports
      that for a probe as well; the explanation by the probe must not cover
      a subject the probe did not plant.

    A finding counts as the planted one only when it names the rule, the
    dataset and the subject.
    """
    copy_of = folder / "planted-core"
    shutil.copytree(source, copy_of)
    shutil.rmtree(copy_of / "core", ignore_errors=True)
    place = copy_of / study.PLACES["twin"]
    log = study.read_probes(copy_of)
    planted = {s for r in log if r["data"] == "twin" for s in r["subjects"]}
    chosen: dict[str, str] = {}

    def change(tables: dict[str, list[dict]]) -> None:
        events: dict[str, list[dict]] = {}
        for row in tables["AE"]:
            if row["USUBJID"] not in planted:
                events.setdefault(row["USUBJID"], []).append(row)
        chosen["sequence"] = next(s for s, rows in sorted(events.items()) if len(rows) >= 2)
        first, second = events[chosen["sequence"]][:2]
        second["AESEQ"] = first["AESEQ"]
        row = next(r for r in tables["DM"] if r["USUBJID"] not in planted and r["ARMCD"]
                   and r["ACTARMCD"] and r["USUBJID"] != chosen["sequence"])
        other = next(a for a in designs.arms(design) if a["name"] != row["ARMCD"])
        row["ACTARMCD"], row["ACTARM"] = other["name"], other["description"]
        chosen["arm"] = row["USUBJID"]

    _rewrite(place, change, design, label, datasetjson_stamp(place / "dm.json"))
    report = run_core(root, copy_of, "twin")
    tables = study.read_tables(copy_of, "twin")
    wrong = report_problems(root, report, tables)
    if wrong:
        out(f"the report of the planted study does not count: {wrong[0]}")
        return False
    _, unexplained = classify(report, explained, tables, log, "twin")
    sequence = [f for f in unexplained if f.rule == RULE_SEQUENCE and f.dataset == "AE"
                and chosen["sequence"] in f.subjects]
    arm = [f for f in unexplained if f.rule in RULES_ARM and f.dataset == "DM"
           and chosen["arm"] in f.subjects]
    if not sequence or not arm:
        out(f"the check did not report both planted defects as unexplained findings "
            f"(the same AESEQ twice for {chosen['sequence']}: {len(sequence)}; another actual "
            f"arm for {chosen['arm']}: {len(arm)}). Unexplained findings of the run:")
        for finding in unexplained[:10]:
            out(f"  {describe(finding)}")
        return False
    out(f"planted defect: two events of one subject with the same AESEQ: reported by CORE and "
        f"unexplained: {describe(sequence[0])[:120]}")
    out(f"planted defect: an actual arm that no probe planted: reported by CORE and "
        f"unexplained: {describe(arm[0])[:120]}")
    return True


def _keep(report: Path, keep: Path | None, name: str) -> int:
    """Copy a report of CORE into the folder that outlives the gate; 1 when it was copied."""
    if keep is None or not report.is_file():
        return 0
    keep.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(report, keep / name)
    return 1


def datasetjson_stamp(path: Path) -> str:
    import json

    with open(path, encoding="ascii") as handle:
        return str(json.load(handle)["datasetJSONCreationDateTime"])


def core_check(root: Path, out: Out, folder: Path, seeds: tuple[str, ...] = SEEDS,
               keep: Path | None = None) -> bool:
    """Visible and twin SDTM of every seed pass CORE with no unexplained finding.

    The reports of CORE are copied to `keep`, whatever the check says: the
    scratch folder is removed after the gate, and a report is the evidence
    for every line the check prints.
    """
    catalog = catalogs.load(catalogs.default_dir(root))
    label = study.catalog_label(catalog)
    explained = load_explained()
    pin = cdisccore.read_pin(root)
    out(f"CDISC CORE {pin.tag} at {pin.commit[:12]}, {STANDARD}, Define-XML {DEFINE_VERSION}, "
        f"terminology sdtmct-{terms.CT_PACKAGE}; explained findings: {FINDINGS_FILE.name}, "
        f"{len(explained['explained'])} entries")
    studies = folder / "first"
    if not studies.is_dir():
        generate_all(root, studies, seeds)
    first_design = pgfix.sample(seeds[0], label)
    seen = planted_core_defects(root, out, studies / seeds[0], folder, explained, first_design,
                                label)
    kept = _keep(folder / "planted-core" / "core" / "twin.json", keep, "planted-twin.json")
    if not seen:
        return False

    jobs = [(seed, which) for seed in seeds for which in study.PLACES]
    workers = core_workers()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        reports = list(pool.map(lambda job: run_core(root, studies / job[0], job[1]), jobs))
    for seed, which in jobs:
        kept += _keep(studies / seed / "core" / f"{which}.json", keep, f"{seed}-{which}.json")
    if keep is not None:
        out(f"{kept} reports of CORE are kept in {keep.name}/ beside this log")
    ok = True
    totals: dict[str, int] = {}
    for (seed, which), report in zip(jobs, reports, strict=True):
        log = study.read_probes(studies / seed)
        tables = study.read_tables(studies / seed, which)
        used, findings = classify(report, explained, tables, log, which)
        unexplained = report_problems(root, report, tables) + [describe(f) for f in findings]
        for key, count in used.items():
            totals[key] = totals.get(key, 0) + count
        counts = report.counts()
        out(f"seed {seed} {which:7s}: {len(report.rules)} rules "
            f"({counts.get('SUCCESS', 0)} passed, {counts.get('SKIPPED', 0)} not applicable, "
            f"{counts.get(cdisccore.ISSUE, 0)} with issues, "
            f"{counts.get(cdisccore.EXECUTION_ERROR, 0)} not executable); "
            f"{len(report.findings)} findings, {len(unexplained)} unexplained")
        for line in unexplained[:15]:
            out(f"  unexplained: {line}")
        ok = ok and not unexplained
    out("findings by explanation, over all runs:")
    for entry in explained["explained"]:
        out(f"  {totals.get(entry['id'], 0):5d}  {entry['id']} ({entry['kind']})")
    unused = [entry["id"] for entry in explained["explained"] if entry["id"] not in totals]
    if unused:
        out(f"explanations that no finding needed: {', '.join(unused)}")
        ok = False
    drift = cdisccore.drift(root)
    for problem in drift:
        out(f"after the runs: {problem}")
    out(f"every report names the datasets handed over with their numbers of records, "
        f"Define-XML {DEFINE_VERSION} and the terminology sdtmct-{terms.CT_PACKAGE}"
        if ok else "some report does not count or has an unexplained finding")
    out(f"CORE on {len(jobs)} datasets ({len(seeds)} seeds, visible and twin): "
        f"{'no' if ok else 'some'} unexplained finding; the pinned source is "
        f"{'unchanged' if not drift else 'CHANGED'}")
    return ok and not drift


# -- controlled terms ----------------------------------------------------------


def package_problems(package: dict[str, dict]) -> list[str]:
    """Why the terms the generator carries are not terms of a CT package.

    `package` is what `cdisccore.terminology` reads from the cache of CORE:
    NCI code of a codelist -> its name, whether it is extensible, its terms.
    """
    problems = []
    for name, codelist in terms.CT.items():
        theirs = package.get(codelist["code"])
        if theirs is None:
            problems.append(f"{name}: the package has no codelist {codelist['code']}")
            continue
        if theirs["name"] != name or bool(theirs["extensible"]) != codelist["extensible"]:
            problems.append(f"{name}: the package calls {codelist['code']} {theirs['name']}, "
                            f"extensible {theirs['extensible']}")
        for value, code in codelist["terms"].items():
            if theirs["terms"].get(value) != code:
                problems.append(f"{name}: '{value}' is {theirs['terms'].get(value)} in the "
                                f"package, {code} here")
    codes, names = package.get("C66738", {}), package.get("C67152", {})
    for code, (name, concept) in terms.TS_PARAMETERS.items():
        if codes.get("terms", {}).get(code) != concept or \
                names.get("terms", {}).get(name) != concept:
            problems.append(f"trial summary parameter {code} ({name}) is not {concept} in the "
                            "package")
    return problems


# The codelist of DSDECOD by the category of the record (SDTMIG v3.4, DS).
DSDECOD_CODELIST = {"DISPOSITION EVENT": "NCOMPLT", "PROTOCOL MILESTONE": "PROTMLST"}


def term_problems(tables: dict[str, list[dict]], package: dict[str, dict],
                  study: dict[str, dict] | None = None) -> tuple[int, list[str]]:
    """Values checked, and values of controlled variables that their codelist does not hold.

    CORE 1.0.0 does not report a value outside a codelist (a planted SEX of
    X passes it), so the gate checks the values itself:

    - a variable with a codelist of CDISC CT, against the package that CORE
      ships. DSDECOD has two: the reasons for non-completion for a
      disposition event, the milestones for a protocol milestone;
    - DM.COUNTRY, against the country codes of `terms.COUNTRIES` (ISO 3166-1
      alpha-3; the package holds no country codes);
    - with `study` (`sdtm.study_codelists`), a variable with a codelist of
      the study (arms, elements, causality, treatment names), against that.
    """
    def allowed(name: str) -> set[str]:
        return set(package[terms.CT[name]["code"]]["terms"])

    def of_study(name: str) -> set[str] | None:
        if study is None or name not in study or name in ("TSPARMCD", "TSPARM"):
            return None
        return set(study[name].get("decode") or study[name].get("values") or ())

    checked = 0
    problems = []
    for domain_name, rows in tables.items():
        for variable in sdtm.DOMAINS[domain_name].variables:
            fixed: set[str] | None = None
            if variable.codelist == "DSDECOD":
                by_category = {category: allowed(name)
                               for category, name in DSDECOD_CODELIST.items()}
            elif variable.codelist in terms.CT:
                fixed, listed = allowed(variable.codelist), variable.codelist
            elif (domain_name, variable.name) == ("DM", "COUNTRY"):
                fixed, listed = set(terms.COUNTRIES), "the country codes of the generator"
            elif variable.codelist and of_study(variable.codelist) is not None:
                fixed = of_study(variable.codelist)
                listed = f"the study codelist {variable.codelist}"
            else:
                continue
            for row in rows:
                value = row[variable.name]
                if value is None:
                    continue
                checked += 1
                if fixed is None:
                    listed = DSDECOD_CODELIST.get(row.get("DSCAT"), "no codelist")
                    good = by_category.get(row.get("DSCAT"), set())
                else:
                    good = fixed
                if value not in good:
                    where = row.get("USUBJID") or ""
                    of = f" of a record with DSCAT '{row.get('DSCAT')}'" if fixed is None else ""
                    problems.append(f"{domain_name}.{variable.name} = '{value}' {where}{of}: "
                                    f"not a term of {listed}")
    by_code: dict[str, set[str]] = {}
    for codelist in package.values():
        for value, code in codelist["terms"].items():
            by_code.setdefault(code, set()).add(value)
    parameters = package.get("C66738", {}).get("terms", {})
    for row in tables.get("TS", []):
        checked += 1
        if terms.TS_PARAMETERS.get(row["TSPARMCD"], ("", ""))[1] != parameters.get(
                row["TSPARMCD"]):
            problems.append(f"TS.TSPARMCD = '{row['TSPARMCD']}': not a parameter of the package")
        if row["TSVCDREF"] == "CDISC CT" and row["TSVAL"] not in by_code.get(row["TSVALCD"], ()):
            problems.append(f"TS: {row['TSVALCD']} is not the code of '{row['TSVAL']}' "
                            f"({row['TSPARMCD']})")
    return checked, problems


def terms_check(root: Path, out: Out, folder: Path, seeds: tuple[str, ...] = SEEDS) -> bool:
    """Every controlled term written is a term of the CT package that CORE ships."""
    name = f"sdtmct-{terms.CT_PACKAGE}"
    package = cdisccore.terminology(root, name)
    out(f"CT package {name} of the pinned CORE: {len(package)} codelists")
    studies = folder / "first"
    if not studies.is_dir():
        generate_all(root, studies, seeds)

    catalog = catalogs.load(catalogs.default_dir(root))
    label = study.catalog_label(catalog)

    def lists_of(seed: str, tables: dict[str, list[dict]]) -> dict[str, dict]:
        return sdtm.study_codelists(pgfix.sample(seed, label), tables)

    # Planted defects: a value outside its codelist, and a term with a wrong code.
    first = study.read_tables(studies / seeds[0], "twin")
    broken = copy.deepcopy(first)
    broken["DM"][0]["SEX"] = "X"
    broken["AE"][0]["AESEV"] = "TERRIBLE"
    _, planted = term_problems(broken, package, lists_of(seeds[0], first))
    if len(planted) != 2:
        out(f"the check did not report the two planted values, but {planted[:3]}")
        return False
    out(f"planted defect: SEX = X and AESEV = TERRIBLE are reported: {planted[0][:80]}")
    # Planted defects: a milestone term in a disposition event, a country that is none,
    # a causality outside the scale of the study.
    broken = copy.deepcopy(first)
    event = next(row for row in broken["DS"] if row["DSCAT"] == "DISPOSITION EVENT")
    event["DSDECOD"] = "RANDOMIZED"
    broken["DM"][0]["COUNTRY"] = "XXX"
    broken["AE"][0]["AEREL"] = "MAYBE"
    _, planted = term_problems(broken, package, lists_of(seeds[0], first))
    if len(planted) != 3:
        out(f"the check did not report the three planted values, but {planted[:4]}")
        return False
    out("planted defect: a milestone term in a disposition event, COUNTRY = XXX and AEREL = "
        f"MAYBE are reported: {next(p for p in planted if 'DSDECOD' in p)[:110]}")
    wrong = copy.deepcopy(package)
    wrong[terms.CT["SEX"]["code"]]["terms"]["F"] = "C00000"
    if not package_problems(wrong):
        out("the check did not see a term whose code differs from the package")
        return False
    out(f"planted defect: another code for SEX F in the package: {package_problems(wrong)[0]}")

    problems = package_problems(package)
    total = 0
    for seed in seeds:
        for which in study.PLACES:
            tables = study.read_tables(studies / seed, which)
            checked, found = term_problems(tables, package, lists_of(seed, tables))
            total += checked
            problems += [f"seed {seed} {which}: {problem}" for problem in found]
    for problem in problems[:20]:
        out(problem)
    listed = sum(len(c["terms"]) for c in terms.CT.values()) + len(terms.TS_PARAMETERS)
    out(f"{listed} terms of {len(terms.CT)} codelists and the trial summary parameters agree "
        f"with the package; {total} values of controlled variables in {2 * len(seeds)} "
        f"datasets checked, the country codes and the codelists of each study included: "
        f"{len(problems)} problems")
    return not problems


# -- probes --------------------------------------------------------------------


def planted_probe_defects(out: Out, catalog: catalogs.Catalog, design: dict, log: list[dict],
                          tables: dict[str, list[dict]]) -> bool:
    """The coverage check must see a probe that is not in the data, and a missing log line."""
    target = next(r for r in log if r["data"] == "twin"
                  and r["probe"] == "ae_on_first_dose_date_without_time")
    subject = target["subjects"][0]
    broken = copy.deepcopy(tables)
    broken["AE"] = [row for row in broken["AE"] if row["USUBJID"] != subject]
    _, _, problems = present.coverage(catalog, design, log, broken)
    if not any("ae.teae.start" in problem for problem in problems):
        out("the check did not see a probe whose records were removed from the data")
        return False
    out(f"planted defect: the records of a logged probe are removed from the data: "
        f"{len(problems)} problems, for example: {problems[-1][:150]}")
    shorter = [r for r in log if r["probe"] != "two_disposition_events"]
    _, _, problems = present.coverage(catalog, design, shorter, tables)
    if not any("disp.status.record" in problem for problem in problems):
        out("the check did not see a pair of alternatives without a probe in the log")
        return False
    out(f"planted defect: a probe is left out of the log: {problems[0][:150]}")
    counts = copy.deepcopy(tables)
    record = next(r for r in log if r["data"] == "twin"
                  and r["probe"] == "statistic_at_rounding_half")
    arm = record["detail"]["arm"]
    victim = next(row for row in counts["AE"] if row["AESER"] == "Y" and any(
        dm["USUBJID"] == row["USUBJID"] and dm["ACTARMCD"] == arm for dm in counts["DM"]))
    for row in counts["AE"]:
        if row["USUBJID"] == victim["USUBJID"]:
            row["AESER"] = "N"
    _, _, problems = present.coverage(catalog, design, log, counts)
    if not any("tfl.rounding.rule" in problem for problem in problems):
        out("the check did not see counts that are no longer at a rounding half")
        return False
    out(f"planted defect: one serious event less in the calibrated arm: {problems[0][:150]}")
    return True


def probes_check(root: Path, out: Out, folder: Path, seeds: tuple[str, ...] = SEEDS) -> bool:
    """probes.jsonl shows a probe in the twin for every pair of alternatives of the slice."""
    catalog = catalogs.load(catalogs.default_dir(root))
    label = study.catalog_label(catalog)
    studies = folder / "first"
    if not studies.is_dir():
        generate_all(root, studies, seeds)
    first = pgfix.sample(seeds[0], label)
    if not planted_probe_defects(out, catalog, first, study.read_probes(studies / seeds[0]),
                                 study.read_tables(studies / seeds[0], "twin")):
        return False
    ok = True
    for seed in seeds:
        design = pgfix.sample(seed, label)
        log = study.read_probes(studies / seed)
        named = {record["catalog"] for record in log}
        pairs, checked, problems = present.coverage(
            catalog, design, log, study.read_tables(studies / seed, "twin"))
        if named != {label}:
            problems.append(f"the log names the catalog {sorted(named)}, not '{label}'")
        visible = [r for r in log if r["data"] == "visible"]
        _, _, missing = present.coverage(catalog, design, log,
                                         study.read_tables(studies / seed, "visible"), "visible")
        found = [p for p in missing if p.startswith("probe ")]
        problems += [f"visible data: {problem}" for problem in found]
        needed = probes.needed(catalog, design)
        out(f"seed {seed}: {len(probes.slice_entries(catalog, design))} decisions apply, "
            f"{pairs} pairs of alternatives; twin: {checked} of {len(needed)} probes logged and "
            f"found in the data; visible: {len(visible)} probes logged and found; "
            f"{len(problems)} problems")
        for problem in problems[:15]:
            out(f"  {problem}")
        ok = ok and not problems
    out(f"units of the slice: {', '.join(probes.SLICE_UNITS)}")
    return ok


# -- one scratch folder for the three checks -----------------------------------


class Scratch:
    """The folder that the checks of one gate run share; removed at the end."""

    def __init__(self) -> None:
        self.folder: Path | None = None

    def get(self) -> Path:
        if self.folder is None:
            self.folder = scratch_dir()
        return self.folder

    def remove(self) -> None:
        if self.folder is not None:
            shutil.rmtree(self.folder, ignore_errors=True)
            self.folder = None


SCRATCH = Scratch()


def determinism(root: Path, out: Out) -> bool:
    return determinism_check(root, out, SCRATCH.get())


def core(root: Path, out: Out) -> bool:
    return core_check(root, out, SCRATCH.get(),
                      keep=build_dir(root) / "gates" / "gen-1a" / "core")


def controlled_terms(root: Path, out: Out) -> bool:
    return terms_check(root, out, SCRATCH.get())


def probe_coverage(root: Path, out: Out) -> bool:
    try:
        return probes_check(root, out, SCRATCH.get())
    finally:
        SCRATCH.remove()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
