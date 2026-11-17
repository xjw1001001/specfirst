"""The checks of the gate gen-1a (PLAN.md section 13.5, docs/decisions/ADR-005.md).

The gate of gen-1, for the datasets and the decisions of the slice:

    for 10 seeds, visible and twin SDTM pass CDISC CORE with no unexplained
    error; generating again gives identical hashes; probes.jsonl shows at
    least one probe in the twin for every pair of alternatives.

Each of the three checks first fails on planted defects (rule R5); only
then does it count. The studies are generated in a scratch folder under the
system's temporary folder and removed afterwards.

A finding of CORE is explained when `core_findings.yaml` names its rule
and the condition written there holds for this finding. Everything else is
unexplained and fails the gate.
"""

from __future__ import annotations

import copy
import os
import shutil
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

from specfirst import cdisccore
from specfirst.compile import catalog as catalogs
from specfirst.gen import datasetjson, pgfix, present, probes, sdtm, study
from specfirst.gen import design as designs

Out = Callable[[str], None]

# The seeds of the gate. They are development seeds and may be read by anyone;
# seeds of dev, test and sealed kits are never written into the repository.
SEEDS = tuple(f"gen-1a-{number}" for number in range(1, 11))
FINDINGS_FILE = Path(__file__).with_name("core_findings.yaml")
STANDARD = "SDTMIG V3.4"


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


def determinism_check(root: Path, out: Out, folder: Path,
                      seeds: tuple[str, ...] = SEEDS) -> bool:
    """Generate every study twice, into two folders, and compare the hashes of all files."""
    catalog = catalogs.load(catalogs.default_dir(root))
    label = study.catalog_label(catalog)

    # Planted defect: a build that stamps its files with another time than the
    # study date, as a writer that reads the clock would.
    design = pgfix.sample(seeds[0], label)
    honest = study.generate(root, design, seeds[0], folder / "planted" / "honest")
    stamp = study.data_stamp
    study.data_stamp = lambda people: "2001-01-01T00:00:01"
    try:
        clocked = study.generate(root, design, seeds[0], folder / "planted" / "clocked")
    finally:
        study.data_stamp = stamp
    planted = hash_differences(honest["files"], clocked["files"])
    if not planted:
        out("the comparison did not see a build that stamps its files with another time")
        return False
    out(f"planted defect: a build with another time stamp differs in {len(planted)} files, "
        f"for example {planted[0]}")

    first = generate_all(root, folder / "first", seeds)
    second = generate_all(root, folder / "second", seeds)
    problems = []
    files = 0
    for seed in seeds:
        files += len(first[seed]["files"])
        problems += [f"seed {seed}: {problem}" for problem in
                     hash_differences(first[seed]["files"], second[seed]["files"])]
        if design_text(root, seed) != (folder / "first" / seed / "gold" / "design.yaml") \
                .read_text(encoding="ascii").split("\n", 2)[2]:
            problems.append(f"seed {seed}: the design written is not the design sampled")
    for problem in problems[:20]:
        out(problem)
    subjects = sum(m["counts"][which]["subjects"] for m in first.values()
                   for which in ("visible", "twin"))
    out(f"{len(seeds)} seeds, each generated twice into its own folder: {files} files and "
        f"{subjects} subjects per build, catalog {label}")
    out(f"identical hashes: {len(problems)} problems")
    return not problems


def design_text(root: Path, seed: str) -> str:
    catalog = catalogs.load(catalogs.default_dir(root))
    return designs.dump(pgfix.sample(seed, study.catalog_label(catalog)))


# -- CDISC CORE ----------------------------------------------------------------


def load_explained(path: Path = FINDINGS_FILE) -> dict:
    with open(path, encoding="ascii") as handle:
        return yaml.safe_load(handle)


def _holds(entry: dict, finding: cdisccore.Finding, records: int | None,
           owners: dict[str, set[str]]) -> bool:
    """Whether an entry of core_findings.yaml explains one finding."""
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
        return records is not None and finding.count == records
    if kind == "study":
        return finding.count == 1 and not finding.subjects
    if kind == "probe":
        allowed = set().union(*(owners.get(probe, set()) for probe in entry["probes"]))
        return bool(finding.subjects) and set(finding.subjects) <= allowed
    raise ValueError(f"core_findings.yaml: unknown kind '{kind}'")


def classify(report: cdisccore.Report, explained: dict, tables: dict[str, list[dict]],
             log: list[dict], which: str) -> tuple[dict[str, int], list[str]]:
    """Findings per explanation, and the unexplained ones as readable lines."""
    owners: dict[str, set[str]] = {}
    for record in log:
        if record["data"] == which:
            owners.setdefault(record["probe"], set()).update(record["subjects"])
    used: dict[str, int] = {}
    unexplained = []
    for finding in report.findings:
        records = len(tables[finding.dataset]) if finding.dataset in tables else None
        for entry in explained["explained"]:
            if _holds(entry, finding, records, owners):
                used[entry["id"]] = used.get(entry["id"], 0) + 1
                break
        else:
            subjects = ", ".join(finding.subjects[:3])
            unexplained.append(
                f"{finding.rule} {finding.dataset or '-'} ({finding.status.lower()}, "
                f"{finding.count} issues{', ' + subjects if subjects else ''}): "
                f"{finding.message[:140]}")
    return used, unexplained


# A run of CORE needs up to this much memory with the pool size of the runner.
CORE_RUN_MEMORY_MB = 3000


def core_workers(available_mb: int | None = None, processors: int | None = None) -> int:
    """How many runs of CORE the gate starts at once: within half of the free memory.

    Other sessions share the machine. Too many runs at once once exhausted
    its memory and the kernel ended their processes (docs/lessons.md).
    """
    if available_mb is None:
        available_mb = available_memory_mb()
    if processors is None:
        processors = os.cpu_count() or 1
    by_memory = (available_mb // 2) // CORE_RUN_MEMORY_MB
    by_processors = processors // (2 * cdisccore.POOL_SIZE)
    return max(1, min(4, by_memory, by_processors))


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


def report_problems(root: Path, report: cdisccore.Report) -> list[str]:
    """Why a report is not one of the pinned CORE on the standard of the generator."""
    pin = cdisccore.read_pin(root)
    problems = []
    if report.engine != pin.version:
        problems.append(f"the report is of CORE {report.engine}, the pin is {pin.version}")
    if report.standard != STANDARD:
        problems.append(f"the report is for {report.standard}, not {STANDARD}")
    if len(report.rules) < 100:
        problems.append(f"only {len(report.rules)} rules ran")
    return problems


def _rewrite(place: Path, name: str, change: Callable[[list[dict]], None], design: dict,
             label: str, people_stamp: str) -> None:
    """Change the rows of one dataset of a study copy and write the dataset again."""
    tables = {}
    for domain in sdtm.ORDER:
        path = place / f"{domain.lower()}.json"
        if path.is_file():
            tables[domain] = datasetjson.read_rows(path)[1]
    change(tables[name])
    study.write_dataset(place, design, tables, label, people_stamp)


def planted_core_defects(root: Path, out: Out, source: Path, folder: Path, explained: dict,
                         design: dict, label: str) -> bool:
    """CORE and the list of explained findings must catch two planted defects."""
    copy_of = folder / "planted-core"
    shutil.copytree(source, copy_of)
    place = copy_of / study.PLACES["twin"]
    log = study.read_probes(copy_of)
    planted = {s for r in log if r["data"] == "twin" for s in r["subjects"]}
    dm = datasetjson.read_rows(place / "dm.json")[1]
    plain = [r["USUBJID"] for r in dm
             if r["USUBJID"] not in planted and r["ARMCD"] and r["ACTARMCD"]]
    wrong_sex, wrong_arm = plain[0], plain[1]
    other = next(a["name"] for a in designs.arms(design)
                 if a["name"] != next(r for r in dm if r["USUBJID"] == wrong_arm)["ARMCD"])

    def change(rows: list[dict]) -> None:
        for row in rows:
            if row["USUBJID"] == wrong_sex:
                row["SEX"] = "X"            # not a term of the codelist SEX
            if row["USUBJID"] == wrong_arm:  # an actual arm that no probe planted
                row["ACTARMCD"] = other
                row["ACTARM"] = designs.arm(design, other)["description"]

    stamp = datasetjson_stamp(place / "dm.json")
    _rewrite(place, "DM", change, design, label, stamp)
    report = run_core(root, copy_of, "twin")
    tables = study.read_tables(copy_of, "twin")
    _, unexplained = classify(report, explained, tables, log, "twin")
    seen_sex = [line for line in unexplained if wrong_sex in line]
    seen_arm = [line for line in unexplained if wrong_arm in line]
    if not seen_sex or not seen_arm:
        out("the check did not report both planted defects as unexplained findings:")
        for line in unexplained[:10]:
            out(f"  {line}")
        return False
    out(f"planted defect: SEX = X for one subject is reported and unexplained: "
        f"{seen_sex[0][:110]}")
    out(f"planted defect: an actual arm that no probe planted is reported and unexplained: "
        f"{seen_arm[0][:110]}")
    return True


def datasetjson_stamp(path: Path) -> str:
    import json

    with open(path, encoding="ascii") as handle:
        return str(json.load(handle)["datasetJSONCreationDateTime"])


def core_check(root: Path, out: Out, folder: Path, seeds: tuple[str, ...] = SEEDS) -> bool:
    """Visible and twin SDTM of every seed pass CORE with no unexplained finding."""
    catalog = catalogs.load(catalogs.default_dir(root))
    label = study.catalog_label(catalog)
    explained = load_explained()
    pin = cdisccore.read_pin(root)
    out(f"CDISC CORE {pin.tag} at {pin.commit[:12]}, {STANDARD}, Define-XML "
        f"{'2.1'}; explained findings: {FINDINGS_FILE.name}, "
        f"{len(explained['explained'])} entries")
    studies = folder / "first"
    if not studies.is_dir():
        generate_all(root, studies, seeds)
    first_design = pgfix.sample(seeds[0], label)
    if not planted_core_defects(root, out, studies / seeds[0], folder, explained, first_design,
                                label):
        return False

    jobs = [(seed, which) for seed in seeds for which in study.PLACES]
    workers = core_workers()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        reports = list(pool.map(lambda job: run_core(root, studies / job[0], job[1]), jobs))
    ok = True
    totals: dict[str, int] = {}
    for (seed, which), report in zip(jobs, reports, strict=True):
        log = study.read_probes(studies / seed)
        tables = study.read_tables(studies / seed, which)
        used, unexplained = classify(report, explained, tables, log, which)
        unexplained = report_problems(root, report) + unexplained
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
    out(f"CORE on {len(jobs)} datasets ({len(seeds)} seeds, visible and twin): "
        f"{'no' if ok else 'some'} unexplained finding; the pinned source is "
        f"{'unchanged' if not drift else 'CHANGED'}")
    return ok and not drift


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
    return core_check(root, out, SCRATCH.get())


def probe_coverage(root: Path, out: Out) -> bool:
    try:
        return probes_check(root, out, SCRATCH.get())
    finally:
        SCRATCH.remove()
