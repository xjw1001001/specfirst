"""The checks of the gate gen-2a (PLAN.md section 13.5, docs/decisions/ADR-005.md).

The gate of gen-2, limited to the one output of the slice:

    10 kits pass P1 to P4. Every applicable decision is separated on the
    twin. The engines agree.

The ten kits are the kits 1 to 10 of the set of the development seed
`SEED`. Each is written twice, by two processes of their own that differ in
what a build must not depend on (the seed of Python's string hashes, the
time zone, the locale, the working folder); the two must be the same bytes,
the manifest included (P1). A kit is written only when it has P2 to P4 and
its engines agree; the gate decides all of that again from the files of
each kit (`kits.check`), with a new hand calculation and a new mutation.

Each check first fails on planted defects (rule R5); only then does it
count. The kits are written into a scratch folder under the system's
temporary folder and removed after the last check.
"""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import decisions, gold, kits, probes, study, verify
from specfirst.gen import design as designs
from specfirst.machine import results
from specfirst.machine.canonical import read_jsonl, write_json, write_jsonl

Out = Callable[[str], None]

# The seed of the gate. It is a development seed and may be read by anyone; the
# seed of a set with dev or test kits is never written into the repository.
SEED = "gen-2a"
COUNT = 10
# The kit the defects are planted in: its scenario is the house standard for the columns
# of the table (the safety set by actual treatment), so the log of probes claims a probe
# for every decision that a planted defect touches.
PLANTED = 10
# The machine is shared: no more than this many builds at once (docs/lessons.md, lesson 32).
MAX_WORKERS = 4


def scratch_dir() -> Path:
    return Path(tempfile.mkdtemp(prefix="specfirst-gen2a-"))


def kit_folder(folder: Path, number: int, build: str = "first") -> Path:
    return folder / build / f"kit-{number:03d}"


def write_all(root: Path, folder: Path, numbers: range, seed: str = SEED) -> dict[tuple, str]:
    """Write every kit twice, each build by a process of its own; returns what failed.

    The first build has the hash seed 1 and the time zone and locale of the
    gate; the second has the hash seed 2, another time zone and the C
    locale. Each has a working folder of its own.
    """
    jobs = [(number, build) for number in numbers for build in ("first", "second")]

    def run(job: tuple[int, str]) -> str:
        number, build = job
        try:
            kits.generate_apart(root, kits.kit_seed(seed, number),
                                kit_folder(folder, number, build), kits.split_of(number),
                                number=number, hash_seed="1" if build == "first" else "2",
                                zone=None if build == "first" else kits.APART_ZONE)
        except kits.KitError as error:
            return str(error)
        return ""

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        failed = list(pool.map(run, jobs))
    return {job: problem for job, problem in zip(jobs, failed, strict=True) if problem}


# ---- kits: P1 to P4 ----------------------------------------------------------------------


def planted_p1(root: Path, out: Out, folder: Path, seed: str) -> bool:
    """Two builds that differ must be seen: a clock in the data, a folder in the manifest.

    The planted builds are made like the honest ones, both engines included,
    so that what differs is what was planted.
    """
    number, split = 1, kits.split_of(1)
    honest = kits.kit_hashes(kit_folder(folder, number))
    for planted, what in (("clock", "a build that stamps its data with a time that depends "
                                    "on its process"),
                          ("folder", "a build whose manifest names the folder it was built in")):
        try:
            other = kits.generate_apart(root, kits.kit_seed(seed, number),
                                        folder / "planted" / planted, split, number=number,
                                        planted=planted, hash_seed="3")
        except kits.KitError as error:
            out(f"the planted build could not be made: {error}")
            return False
        differ = kits.hash_differences(honest, other)
        if planted == "folder" and differ != [f"{kits.MANIFEST}: the hashes differ"]:
            out(f"the comparison did not see {what} alone, but {differ[:3]}")
            return False
        if planted == "clock" and not any(line.startswith("inputs/data/sdtm/") for line in differ):
            out(f"the comparison did not see {what}")
            return False
        out(f"planted defect: {what}: {len(differ)} files differ, for example {differ[-1]}")
    return True


def planted_p2(out: Out, kit_dir: Path) -> bool:
    """The comparison with the hand calculation must see a wrong cell and a wrong rule."""
    design = designs.load(kit_dir / "gold" / "design.yaml")
    records = kits.read_decisions(kit_dir)
    values = decisions.as_values(records)
    arms = gold.arms_of(design, values)
    tables = study.read_tables(kit_dir, "twin")
    made = verify.grid_of(kit_dir, "twin")
    if verify.p2(tables, values, arms, made):
        out("the grid of the kit does not equal its reference: nothing can be planted")
        return False
    broken = copy.deepcopy(made)
    cell = broken["rows"][1]["cells"][0]
    cell["text"] = cell["text"].replace(cell["text"][0], "9" if cell["text"][0] != "9" else "8", 1)
    found = verify.p2(tables, values, arms, broken)
    if len(found) != 1:
        out(f"the comparison did not report one changed cell, but {found[:3]}")
        return False
    out(f"planted defect: one changed cell of the grid: {found[0]}")
    # A machine that follows another rule than the decision states: the grid of the gold
    # decisions against the hand calculation of a vector with one decision changed.
    seen = 0
    for entry_id, other in (("tfl.population", [{"rule": "randomized"}, {"rule": "safety"}]),
                            ("ae.teae.start", [{"rule": "at_or_after_first_dose_time"},
                                               {"rule": "on_or_after_first_dose_date"}]),
                            ("pop.safety.rule", [{"rule": "randomized_and_dosed"},
                                                 {"rule": "at_least_one_dose"}])):
        value = next(v for v in other if v["rule"] != values[entry_id]["rule"])
        found = verify.p2(tables, {**values, entry_id: value}, arms, made)
        if found:
            seen += 1
            out(f"planted defect: the hand calculation follows {entry_id} = {value['rule']}, "
                f"the grid {values[entry_id]['rule']}: {len(found)} differences, for example "
                f"{found[0]}")
    if seen < 2:
        out("the comparison did not see a grid built by another rule than the reference")
        return False
    return _shell_defect_seen(kit_dir, out)


def _shell_defect_seen(kit_dir: Path, out: Out) -> bool:
    """A mock shell that shows a number must be reported."""
    copy_of = Path(tempfile.mkdtemp(prefix="specfirst-gen2a-shell-"))
    try:
        target = copy_of / gold.PLACES["twin"][1] / gold.GRID
        shutil.copytree(kit_dir / gold.PLACES["twin"][1] / gold.GRID, target)
        path = next(target.glob("*.shell.json"))
        with open(path, encoding="ascii") as handle:
            shell = json.load(handle)
        shell["rows"][1]["cells"][0]["text"] = "12 ( 37.5)"
        write_json(path, shell)
        found = verify.shell_problems(copy_of, "twin")
    finally:
        shutil.rmtree(copy_of, ignore_errors=True)
    if len(found) != 1:
        out(f"the check did not report a mock shell with a number, but {found[:2]}")
        return False
    out(f"planted defect: a mock shell that shows a number: {found[0][:110]}")
    return True


def planted_p3(root: Path, out: Out, kit_dir: Path, catalog: catalogs.Catalog) -> bool:
    """The trace check must see a cut path, a missing decision and a wrong record."""
    records = kits.read_decisions(kit_dir)
    place = gold.PLACES["twin"][1]
    cases = (
        ("a cell that lost a shows edge", "edges.jsonl",
         lambda lines: _without_first(lines, lambda e: e["type"] == "shows")),
        ("an analysis that lost a reads edge", "edges.jsonl",
         lambda lines: _without_first(lines, lambda e: e["type"] == "reads"
                                      and e["to"].endswith(".TRTEMFL"))),
        ("a column that lost its derivation from SDTM", "edges.jsonl",
         lambda lines: [e for e in lines if not (e["type"] == "derives_from"
                                                 and e["from"] == "adam:ADAE.USUBJID")]),
        ("a decision without a node", "nodes.jsonl",
         lambda lines: _without_first(lines, lambda n: n["id"].startswith("decision:")
                                      and n["id"] != "decision:trt.planned.source")),
    )
    for what, name, change in cases:
        copy_of = Path(tempfile.mkdtemp(prefix="specfirst-gen2a-p3-"))
        try:
            shutil.copytree(kit_dir / place, copy_of / place)
            shutil.copytree(kit_dir / gold.PLACES["twin"][0], copy_of / gold.PLACES["twin"][0])
            path = copy_of / place / gold.GRAPH / name
            lines = read_jsonl(path)
            changed = change(lines)
            if len(changed) == len(lines):
                out(f"nothing to plant for: {what}")
                return False
            write_jsonl(path, changed)
            _, found = verify.p3(root, copy_of, "twin", records, catalog)
        finally:
            shutil.rmtree(copy_of, ignore_errors=True)
        if not found:
            out(f"the trace check did not see {what}")
            return False
        out(f"planted defect: {what}: {len(found)} problems, for example {found[0][:120]}")
    return True


def _without_first(lines: list[dict], test: Callable[[dict], bool]) -> list[dict]:
    for position, line in enumerate(lines):
        if test(line):
            return lines[:position] + lines[position + 1:]
    return lines


def kits_check(root: Path, out: Out, folder: Path, seed: str = SEED,
               count: int = COUNT) -> bool:
    """Ten kits pass P1 to P4: written twice, compared, and decided again from their files."""
    catalog = catalogs.load(catalogs.default_dir(root))
    numbers = range(1, count + 1)
    failed = write_all(root, folder, numbers, seed)
    for (number, build), problem in sorted(failed.items()):
        out(f"kit {number}, {build} build: not written: {problem[:1500]}")
    if failed:
        return False
    planted = kit_folder(folder, min(PLANTED, count))
    if not (planted_p1(root, out, folder, seed) and planted_p2(out, planted)
            and planted_p3(root, out, planted, catalog)):
        return False
    ok = True
    ids = []
    for number in numbers:
        kit_dir = kit_folder(folder, number)
        manifest = kits.read_manifest(kit_dir)
        ids.append(manifest["id"])
        differ = kits.hash_differences(kits.kit_hashes(kit_dir),
                                       kits.kit_hashes(kit_folder(folder, number, "second")))
        drawn = manifest["decisions"]["vectors_drawn_before"]
        out(f"kit {number}: study {manifest['study']['id']}, {manifest['study']['arms']} arms, "
            f"split {manifest['split']}, scenario {manifest['decisions']['scenario']} "
            f"{manifest['decisions']['given'] or '(all drawn)'}; decision vectors drawn "
            f"before this one: {len(drawn)}")
        for item in drawn:
            out(f"  vector {item['attempt']} was drawn again: {'; '.join(item['reasons'])[:300]}")
        out(f"  P1: {len(manifest['files']) + 1} files of two builds by two processes, the "
            f"manifest included: {len(differ)} differ")
        problems = [f"P1: {problem}" for problem in differ]
        problems += kits.check(root, kit_dir, out)
        for problem in problems[:20]:
            out(f"  PROBLEM kit {number}: {problem[:400]}")
        ok = ok and not problems
    if len(set(ids)) != len(ids):
        out(f"two kits have the same ID: {sorted(ids)}")
        ok = False
    out(f"{count} kits of the set '{seed}': P1 to P4 "
        f"{'hold for every kit' if ok else 'FAIL'}")
    return ok


# ---- separation ----------------------------------------------------------------------------


def _matrices(folder: Path, count: int) -> dict[int, dict]:
    found = {}
    for number in range(1, count + 1):
        with open(kit_folder(folder, number) / kits.IDENTIFIABILITY, encoding="ascii") as handle:
            found[number] = json.load(handle)
    return found


def planted_separation(root: Path, out: Out, kit_dir: Path) -> bool:
    """The mutation must see a claim that does not hold, and a twin that lost a probe."""
    catalog = catalogs.load(catalogs.default_dir(root))
    house = houses.load(houses.default_dir(root))
    design = designs.load(kit_dir / "gold" / "design.yaml")
    records = kits.read_decisions(kit_dir)
    log = study.read_probes(kit_dir)
    with open(kit_dir / gold.PLACES["twin"][1] / gold.GRAPH / "coverage.json",
              encoding="ascii") as handle:
        reached = json.load(handle)["decisions"]

    def run(source: Path, reach_tables: dict | None = None) -> tuple[dict, list[str], list[str]]:
        scratch = Path(tempfile.mkdtemp(prefix="specfirst-gen2a-planted-"))
        try:
            return verify.mutate(root, catalog, house, source, "twin", design, records, reached,
                                 log, study.read_tables(source, "twin"), scratch, reach_tables)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    # A log that claims what the output does not read: the study day of an event.
    claims = {entry_id: reach for line in log if line["data"] == "twin"
              for entry_id, reach in line["reaches"].items()}
    claims["date.studyday.origin"] = {"when": {"always": True}}
    _, defects, unfit = run(kit_dir, claims)
    if not any("date.studyday.origin" in line for line in unfit) or not any(
            "date.studyday.origin" in line for line in defects):
        out("the mutation did not see a claim of the log that does not hold")
        return False
    out("planted defect: a log of probes that claims a difference for date.studyday.origin: "
        f"{next(line for line in unfit if 'date.studyday.origin' in line)[:150]}")

    # A twin whose planted subjects lost their adverse events: no event on the day of the
    # first dose is left, and none with a partial start date in the month of the dose.
    planted = {subject for line in log if line["data"] == "twin" for subject in line["subjects"]}
    copy_of = Path(tempfile.mkdtemp(prefix="specfirst-gen2a-twin-"))
    try:
        place = gold.PLACES["twin"][0]
        shutil.copytree(kit_dir / place, copy_of / place)
        shutil.copytree(kit_dir / gold.HOUSE, copy_of / gold.HOUSE)
        tables = study.read_tables(copy_of, "twin")
        tables["AE"] = [row for row in tables["AE"] if row["USUBJID"] not in planted]
        stamp = datasetjson_stamp(copy_of / place / "dm.json")
        study.write_dataset(copy_of / place, design, tables,
                            study.catalog_label(catalog), stamp)
        matrix, defects, unfit = run(copy_of)
    finally:
        shutil.rmtree(copy_of, ignore_errors=True)
    item = next(item for item in matrix["decisions"] if item["id"] == "ae.teae.start")
    if item["identifiable"] != "unseparated" or not any("ae.teae.start" in line
                                                        for line in unfit):
        out("the mutation did not see a twin whose probes for ae.teae.start lost their events: "
            f"{item['identifiable']}, {unfit[:2]}, {defects[:2]}")
        return False
    out(f"planted defect: the {len(planted)} planted subjects of the twin lost their adverse "
        f"events: ae.teae.start is {item['identifiable']}, and the kit is unfit in "
        f"{len(unfit)} claims, for example: "
        f"{next(line for line in unfit if 'ae.teae.start' in line)[:110]}")
    return True


def datasetjson_stamp(path: Path) -> str:
    with open(path, encoding="ascii") as handle:
        return str(json.load(handle)["datasetJSONCreationDateTime"])


def coverage(catalog: catalogs.Catalog, folder: Path, count: int) -> tuple[list[str], list[str]]:
    """Over the kits of the gate: where every pair of alternatives of every decision of
    the slice is separated. Returns the lines of the table and the holes.

    A hole: a decision that no kit separates; a pair of alternatives that no
    kit separates; a decision with several alternatives that is applicable
    and separated in no kit (it would be separated by luck only); a decision
    the log says the output never reads that a kit reads or separates.
    """
    matrices = _matrices(folder, count)
    lines, holes = [], []
    entries: dict[str, catalogs.Entry] = {}
    for number in matrices:
        design = designs.load(kit_folder(folder, number) / "gold" / "design.yaml")
        entries.update({entry.id: entry for entry in decisions.entries(catalog, design)})
    lines.append(f"{'decision':24s} {'in':>3s} {'read':>4s} {'appl':>4s} {'sep':>4s}  "
                 "pairs of alternatives: kits that separate each")
    for entry_id in [e for e in catalog.entries if e in entries]:
        entry = entries[entry_id]
        items = {number: item for number, matrix in matrices.items()
                 for item in matrix["decisions"] if item["id"] == entry_id}
        never = probes.REACHES[entry_id]["when"] == {"never": True}
        rules = [alternative.id for alternative in entry.alternatives]
        wanted = list(combinations(rules, 2))
        where: dict[tuple[str, str], list[int]] = {pair: [] for pair in wanted}
        slots: list[int] = []
        for number, item in items.items():
            for pair in item["pairs"]:
                first, second = pair["first"].split("(")[0], pair["second"].split("(")[0]
                key = next((p for p in wanted if set(p) == {first, second}), None)
                if pair["separated"] and key is not None:
                    where[key].append(number)
                elif pair["separated"] and first == second:
                    slots.append(number)
        cells = "; ".join(f"{a}|{b}: {','.join(map(str, kits_)) or 'NONE'}"
                          for (a, b), kits_ in where.items())
        if not wanted:
            cells = ("one alternative; kits that separate values of its slot: "
                     f"{','.join(map(str, sorted(set(slots)))) or 'NONE'}")
        lines.append(
            f"{entry_id:24s} {len(items):3d} "
            f"{sum(1 for i in items.values() if i['read']):4d} "
            f"{sum(1 for i in items.values() if i['applicable']):4d} "
            f"{sum(1 for i in items.values() if i['identifiable'] == 'separated'):4d}  {cells}")
        separated = [n for n, i in items.items() if i["identifiable"] == "separated"]
        if never:
            if separated or any(i["read"] for i in items.values()):
                holes.append(f"{entry_id}: the log says the output never reads it, and a kit "
                             "reads or separates it")
            continue
        if not separated:
            holes.append(f"{entry_id}: separated in no kit")
        if wanted and not any(i["applicable"] and i["identifiable"] == "separated"
                              for i in items.values()):
            holes.append(f"{entry_id}: in no kit does the log of probes claim a probe for "
                         "it and the twin separate it")
        holes += [f"{entry_id}: {a} and {b} are separated in no kit"
                  for (a, b), kits_ in where.items() if not kits_]
        if not wanted and not slots:
            holes.append(f"{entry_id}: no kit separates two values of its slot")
    return lines, holes


def separation_check(root: Path, out: Out, folder: Path, count: int = COUNT) -> bool:
    """Every applicable decision of the slice is separated on the twin, in every kit; and
    over the ten kits the matrix has no hole."""
    catalog = catalogs.load(catalogs.default_dir(root))
    if not planted_separation(root, out, kit_folder(folder, min(PLANTED, count))):
        return False
    matrices = _matrices(folder, count)
    ok = True
    for number, matrix in matrices.items():
        summary = matrix["summary"]
        bad = summary["applicable_and_unseparated"]
        out(f"kit {number}: {summary['decisions']} decisions, {summary['read']} read by the "
            f"output, {summary['applicable']} applicable (the log claims a probe for every "
            f"pair), {len(summary['separated'])} separated; applicable and unseparated: "
            f"{', '.join(bad) or 'none'}")
        out(f"  unseparated, not read: {', '.join(summary['unseparated_not_read']) or 'none'}; "
            f"unseparated, read, no probe claimed: "
            f"{', '.join(summary['unseparated_read']) or 'none'}")
        ok = ok and not bad
    lines, holes = coverage(catalog, folder, count)
    # Planted: a matrix without the kits that separate a pair must show a hole.
    short = Path(tempfile.mkdtemp(prefix="specfirst-gen2a-holes-"))
    try:
        for number, matrix in matrices.items():
            broken = copy.deepcopy(matrix)
            for item in broken["decisions"]:
                if item["id"] == "ae.teae.end":
                    for pair in item["pairs"]:
                        pair["separated"] = False
                    item["identifiable"] = "unseparated"
            path = kit_folder(short, number) / kits.IDENTIFIABILITY
            write_json(path, broken)
            target = kit_folder(short, number) / "gold" / "design.yaml"
            shutil.copyfile(kit_folder(folder, number) / "gold" / "design.yaml", target)
        _, planted = coverage(catalog, short, count)
    finally:
        shutil.rmtree(short, ignore_errors=True)
    if not any(line.startswith("ae.teae.end: separated in no kit") for line in planted):
        out("the coverage did not see a decision that no kit separates")
        return False
    out(f"planted defect: matrices in which no kit separates ae.teae.end: {len(planted)} "
        f"holes, for example: {planted[0]}")
    for line in lines:
        out(line)
    for hole in holes:
        out(f"HOLE {hole}")
    never = sorted(entry_id for entry_id, reach in probes.REACHES.items()
                   if reach["when"] == {"never": True})
    out(f"not applicable to this output, and unseparated for the slice (PLAN.md section 4.7): "
        f"{', '.join(never)}")
    out(f"separation: {len(holes)} holes in the matrix of {count} kits; every applicable "
        f"decision is {'separated' if ok else 'NOT separated'} on the twin of its kit")
    return ok and not holes


# ---- engines ---------------------------------------------------------------------------------


def engines_check(root: Path, out: Out, folder: Path, count: int = COUNT) -> bool:
    """The two result engines agree on every result of every kit, visible and twin."""
    ok = True
    total = 0
    first = None
    for number in range(1, count + 1):
        for which, (_, place) in gold.PLACES.items():
            base = kit_folder(folder, number) / place / gold.ARD
            ours = read_jsonl(base / f"{gold.EVENT}.jsonl")
            theirs = read_jsonl(base / f"{gold.EVENT}.r.jsonl")
            if first is None:
                first = (ours, theirs)
            lines, disagreements = results.agreement(results.by_id(ours), results.by_id(theirs))
            problems = [*results.ard_problems(ours, root), *results.ard_problems(theirs, root),
                        *disagreements]
            total += len(ours)
            for problem in problems[:10]:
                out(f"kit {number} {which}: {problem}")
            ok = ok and not problems and len(ours) == len(theirs) > 0
    # Planted: a result of the R engine that differs, and one it lacks.
    ours, theirs = first
    broken = copy.deepcopy(theirs)
    row = next(r for r in broken if isinstance(r["raw_value"], int | float) and r["raw_value"])
    row["raw_value"] = row["raw_value"] + 1
    _, planted = results.agreement(results.by_id(ours), results.by_id(broken))
    _, missing = results.agreement(results.by_id(ours), results.by_id(theirs[1:]))
    if not planted or not missing:
        out("the comparison did not see a result that differs or one that is missing")
        return False
    out(f"planted defect: a result of the R engine that differs: {planted[0][:120]}")
    out(f"planted defect: a result the R engine lacks: {missing[0][:120]}")
    out(f"the Python engine and the R engine agree on {total} results of {2 * count} builds "
        f"({count} kits, visible and twin): {'yes' if ok else 'NO'}")
    return ok


# ---- splits ----------------------------------------------------------------------------------


def splits_check(root: Path, out: Out, folder: Path, seed: str = SEED,
                 count: int = COUNT) -> bool:
    """The splits of section 6.7: every kit has the split of its place in the set; no kit
    holds a seed; no train, dev or test kit has what an exam holds out."""
    catalog = catalogs.load(catalogs.default_dir(root))
    house = houses.load(houses.default_dir(root))
    problems = []
    tally: dict[str, int] = {}
    for number in range(1, count + 1):
        kit_dir = kit_folder(folder, number)
        manifest = kits.read_manifest(kit_dir)
        tally[manifest["split"]] = tally.get(manifest["split"], 0) + 1
        if manifest["split"] != kits.split_of(number):
            problems.append(f"kit {number}: split {manifest['split']}, the plan gives "
                            f"{kits.split_of(number)}")
        design = designs.load(kit_dir / "gold" / "design.yaml")
        values = decisions.as_values(kits.read_decisions(kit_dir))
        if kits.held_out(design, values):
            problems.append(f"kit {number}: a {manifest['split']} kit with a held-out factor")
        secrets = [kits.kit_seed(seed, number).encode("ascii")]
        for path in sorted(kit_dir.rglob("*")):
            if path.is_file() and any(secret in path.read_bytes() for secret in secrets):
                problems.append(f"kit {number}: {path.relative_to(kit_dir)} holds the seed")
        from specfirst.gen.rng import seed_sha256

        if manifest["seed_sha256"] != seed_sha256(kits.kit_seed(seed, number)):
            problems.append(f"kit {number}: seed_sha256 is not the hash of its seed")
    # Planted: a seed in a file, and a vector that an exam holds out.
    kit_dir = kit_folder(folder, 1)
    design = designs.load(kit_dir / "gold" / "design.yaml")
    values = decisions.as_values(kits.read_decisions(kit_dir))
    held = {**values, **{entry_id: {"rule": rule}
                         for entry_id, rule in decisions.HELD_OUT["combination"].items()}}
    if not kits.held_out(design, held) or kits.held_out(design, values):
        out("the check does not tell a held-out combination from the vector of kit 1")
        return False
    out(f"planted defect: the vector of kit 1 with {decisions.HELD_OUT['combination']}: "
        "held out, a train kit must not have it")
    parameters = probes.Parameters.of(design).as_record()
    from specfirst.gen.rng import Stream

    drawn = [decisions.sample(catalog, house, design, parameters, Stream("splits", number),
                              "train", stated_share=0.9) for number in range(200)]
    sealed = [decisions.sample(catalog, house, design, parameters, Stream("splits", number),
                               "sealed", stated_share=0.9) for number in range(200)]
    if any(decisions.held_out_combination(v) for v in drawn) or not any(
            decisions.held_out_combination(v) for v in sealed):
        out("the sampler does not keep the held-out combination for sealed kits")
        return False
    out("200 vectors drawn for a train kit: none has the held-out combination; of 200 for a "
        f"sealed kit: {sum(1 for v in sealed if decisions.held_out_combination(v))} have it")
    for problem in problems:
        out(problem)
    out(f"splits of the {count} kits by their place in the set: "
        + ", ".join(f"{name} {tally.get(name, 0)}" for name in decisions.SPLITS)
        + f"; held out for an exam: {decisions.HELD_OUT['design']}, and the combination "
        f"{decisions.HELD_OUT['combination']}; {len(problems)} problems")
    return not problems


# ---- one scratch folder for the checks -----------------------------------------------------


class Scratch:
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


def _written(folder: Path) -> bool:
    return (kit_folder(folder, COUNT) / kits.MANIFEST).is_file()


def kits_pass(root: Path, out: Out) -> bool:
    return kits_check(root, out, SCRATCH.get())


def separation(root: Path, out: Out) -> bool:
    if not _written(SCRATCH.get()):
        out("the kits of the gate were not written")
        return False
    return separation_check(root, out, SCRATCH.get())


def engines(root: Path, out: Out) -> bool:
    if not _written(SCRATCH.get()):
        out("the kits of the gate were not written")
        return False
    return engines_check(root, out, SCRATCH.get())


def splits(root: Path, out: Out) -> bool:
    try:
        if not _written(SCRATCH.get()):
            out("the kits of the gate were not written")
            return False
        return splits_check(root, out, SCRATCH.get())
    finally:
        SCRATCH.remove()

