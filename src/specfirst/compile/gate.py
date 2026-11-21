"""The checks of `specfirst gate std-1` (PLAN.md section 13.4).

Gate: the round trip decisions to statements to decisions is exact for every
alternative; compiled fragments pass `yamaa check` and the ARS schema; every
entry has at least one public source. Each function prints what it counted,
so the gate log is the evidence of the report (rule R8).

Each check takes a pair of version labels (ADR-020): without them, the
default pair of specfirst.compile.versions. The gates catalog-2a and
catalog-2b run them on (catalog@2, open-default@2), with the checks of the
versions themselves at the end of this module.
"""

from __future__ import annotations

import atexit
import shutil
import tempfile
from collections.abc import Callable
from pathlib import Path

from specfirst.compile import backlog, checks, migration, tiny, versions
from specfirst.compile import catalog as catalog_module
from specfirst.compile import house as house_module
from specfirst.paths import cache_dir

Out = Callable[[str], None]


def _report(out: Out, problems: list[str], limit: int = 40) -> bool:
    for problem in problems[:limit]:
        out(f"  problem: {problem}")
    if len(problems) > limit:
        out(f"  ... and {len(problems) - limit} more")
    return not problems


def _load(root: Path, pair: tuple[str | None, str | None] = (None, None)):
    """The catalog and the house of a pair of labels; a house that does not fit is refused."""
    return house_module.load_pair(root, *pair)


def catalog_check(root: Path, out: Out, pair: tuple = (None, None)) -> bool:
    catalog, house = _load(root, pair)
    alternatives = sum(len(entry.alternatives) for entry in catalog.entries.values())
    out(f"catalog {catalog.name} {catalog.version}: {len(catalog.entries)} entries, "
        f"{len(catalog.keys())} questions (entry and unit), {alternatives} alternatives, "
        f"{len(catalog.units)} units, {len(catalog.probes)} probes")
    passed = True
    for name, problems in (
        ("schema and cross-references", checks.catalog_problems(catalog, root)),
        ("compile templates on their examples", checks.evaluate_examples(catalog)),
        ("probes: every pair of alternatives, every slot", checks.probe_problems(catalog)),
        ("structural probes separate for any data",
         checks.structural_probe_problems(catalog, house)),
        ("phrasings and reading notes", checks.wording_problems(catalog)),
        ("parameters set and read", checks.template_problems(catalog, house)),
    ):
        out(f"{name}: {len(problems)} problems")
        passed = _report(out, problems) and passed
    return passed


def sources_check(root: Path, out: Out, pair: tuple = (None, None)) -> bool:
    catalog, _ = _load(root, pair)
    cache = cache_dir(root)
    if not cache.is_dir():
        out(f"no fetch cache at {cache}: run `specfirst fetch`")
        return False
    problems = checks.source_problems(catalog, root, cache)
    cited = [source for entry in catalog.entries.values() for source in entry.sources]
    pinned = [s for s in cited if catalog.sources.get(s.get("ref"), {}).get("kind") == "pinned"]
    found = [s for s in pinned if s.get("find")]
    without = [entry.id for entry in catalog.entries.values() if not entry.sources]
    out(f"{len(catalog.entries)} entries, {len(without)} without a public source")
    out(f"{len(cited)} citations: {len(pinned)} to pinned sources, checked on the fetch cache "
        f"({len(found)} with a text that must stand in the file); "
        f"{len(cited) - len(pinned)} to published documents, judged and not checked by script")
    out(f"public sources: {len(problems)} problems")
    return _report(out, problems)


def roundtrip_check(root: Path, out: Out, pair: tuple = (None, None)) -> bool:
    catalog, house = _load(root, pair)
    problems, tried = checks.roundtrip_problems(catalog)
    alternatives = sum(len(e.alternatives) * len(e.units) for e in catalog.entries.values())
    out(f"{tried} statements rendered and parsed back, for {alternatives} alternatives "
        "(entry, unit and alternative)")
    out(f"round trip decisions to statements to decisions: {len(problems)} problems")
    passed = _report(out, problems)
    base = checks.base_vector(catalog, house)
    document = checks.document_problems(catalog, base)
    out(f"document round trip on {len(base)} decisions: {len(document)} problems")
    return _report(out, document) and passed


_COMPILED: dict[str, tuple[list[checks.Variant], Path]] = {}


def _variants(root: Path, out: Out, pair: tuple = (None, None)
              ) -> tuple[list[checks.Variant], Path]:
    """Every decision vector, compiled once per process and checkout.

    The files go to a new folder under the system's temporary folder, not
    into the checkout: yamaa refuses to save a dataset on a Windows drive
    under WSL (`target_changed`), and the checkout of this project is on one.
    """
    key = f"{root} {pair[0] or versions.DEFAULT_CATALOG} {pair[1] or versions.DEFAULT_HOUSE}"
    if key not in _COMPILED:
        catalog, house = _load(root, pair)
        work = Path(tempfile.mkdtemp(prefix="specfirst-std1-"))
        atexit.register(shutil.rmtree, work, ignore_errors=True)
        out(f"compiled files and built datasets: {work} (removed when the command ends)")
        found = checks.compile_all(catalog, house, work)
        reference = checks.house_reference(house, work)
        problems, notes = checks.coverage_problems(catalog, house, found, reference)
        compiled = sum(1 for variant in found if variant.compiled is not None)
        out(f"{len(found)} decision vectors (the base and one changed decision each), "
            f"{compiled} compiled")
        for note in notes:
            out(f"  note: {note}")
        out(f"every alternative compiles and changes the compiled files: "
            f"{len(problems)} problems")
        _report(out, problems)
        _COMPILED[key] = (found if not problems else [], work)
    else:
        out(f"{len(_COMPILED[key][0])} decision vectors, compiled by an earlier check")
    return _COMPILED[key]


def yamaa_check(root: Path, out: Out, pair: tuple = (None, None)) -> bool:
    found, work = _variants(root, out, pair)
    if not found:
        return False
    problems, checked = checks.yamaa_problems(found, work)
    out(f"{len(checks.distinct_adam(found, work))} distinct sets of ADaM specs, "
        f"{checked} entry specs checked by yamaa "
        "(each with its house parent and one fragment per decision)")
    out(f"yamaa check: {len(problems)} problems")
    return _report(out, problems)


def run_check(root: Path, out: Out, pair: tuple = (None, None)) -> bool:
    found, work = _variants(root, out, pair)
    if not found:
        return False
    problems, ran = checks.run_problems(found, work)
    out(f"{len(checks.distinct_adam(found, work))} distinct sets of ADaM specs, "
        f"{ran} datasets built by yamaa on the tiny study of specfirst.compile.tiny "
        f"({len(tiny.DM)} subjects; this shows that the specs run, not that their values "
        "are right)")
    out(f"yamaa run: {len(problems)} problems")
    return _report(out, problems)


def tables_check(root: Path, out: Out, pair: tuple = (None, None)) -> bool:
    found, _ = _variants(root, out, pair)
    if not found:
        return False
    cache = cache_dir(root)
    schema_path = cache / checks.ARS_SCHEMA[0] / checks.ARS_SCHEMA[1]
    if not schema_path.is_file():
        out(f"no ARS schema at {schema_path}: run `specfirst fetch`")
        return False
    schema = checks.load_ars_schema(cache)
    problems, distinct = checks.table_problems(found, schema)
    out(f"ARS schema: {checks.ARS_SCHEMA[1]} of the pinned source '{checks.ARS_SCHEMA[0]}'")
    missed = checks.ars_schema_control(found[0].compiled.ars, schema)
    out(f"negative controls: {len(checks.ARS_CONTROLS)} schema defects planted in the base "
        f"ARS file, {len(checks.ARS_CONTROLS) - len(missed)} reported")
    problems = missed + problems
    out(f"{distinct} distinct ARS files with their layouts checked: schema, references, "
        "and that layouts and ARS name the same analyses")
    out(f"ARS schema and layouts: {len(problems)} problems")
    return _report(out, problems)


def house_check(root: Path, out: Out, pair: tuple = (None, None)) -> bool:
    catalog, house = _load(root, pair)
    problems = checks.house_problems(catalog, house, root)
    defaults = house_module.defaults(catalog, house)
    out(f"house standard {house.label}: {len(defaults)} defaults, "
        f"{len(house_module.without_default(catalog, house))} decisions without a default, "
        f"{len(house.adam)} parent specs, {len(house.ars.get('families') or {})} table families")
    out(f"house standard: {len(problems)} problems")
    return _report(out, problems)


# -- the versions of the standard (ADR-020) ----------------------------------

# The pair the gates catalog-2a and catalog-2b check, and the version before it.
NEXT = ("catalog@2", "open-default@2")
BEFORE = "catalog@1"


def frozen_check(root: Path, out: Out) -> bool:
    """Every frozen folder has its tree; the default pair is frozen; no draft is named."""
    known = versions.load(root)
    for label, version in known.items():
        tree = versions.tree_hash(versions.folder(root, label)) \
            if versions.folder(root, label).is_dir() else ""
        out(f"{label}: {version.status}" + (f" {version.date}" if version.date else "")
            + f", tree {tree or 'none'}"
            + (f" (frozen as {version.tree})" if version.status == "frozen" else ""))
    problems = versions.frozen_problems(root)
    out(f"default pair: {versions.DEFAULT_CATALOG}, {versions.DEFAULT_HOUSE}; "
        f"{len(versions.kits_named(root))} labels named by the kits of the repository")
    out(f"frozen versions: {len(problems)} problems")
    return _report(out, problems)


def migration_check(root: Path, out: Out, pair: tuple = NEXT, before: str = BEFORE) -> bool:
    old = catalog_module.load(catalog_module.default_dir(root, before))
    new = catalog_module.load(catalog_module.default_dir(root, pair[0]))
    diff = migration.differences(old, new)
    lines = migration.read(new).get("changes") or []
    out(f"{before} to {pair[0]}: {len(migration.meanings(old))} and "
        f"{len(migration.meanings(new))} alternatives; {len(diff.added)} added, "
        f"{len(diff.removed)} removed, {len(diff.changed)} changed in meaning; units "
        f"{len(diff.units_added)} added, {len(diff.units_removed)} removed; "
        f"{len(lines)} lines in {migration.FILE}")
    problems = migration.problems(old, new, backlog.accepted_for(backlog.load(root), pair[0]))
    out(f"migration: {len(problems)} problems")
    return _report(out, problems)


def backlog_check(root: Path, out: Out) -> bool:
    records = backlog.load(root)
    by_status = {status: sum(1 for r in records if r.get("status") == status)
                 for status in backlog.STATUSES}
    out(f"{backlog.FILE}: {len(records)} records for {len({r.get('issue') for r in records})} "
        "issues; " + ", ".join(f"{n} {s}" for s, n in by_status.items() if n))
    problems = backlog.problems(root)
    out(f"backlog: {len(problems)} problems")
    return _report(out, problems)


def defaults_check(root: Path, out: Out, pair: tuple = NEXT) -> bool:
    catalog, house = _load(root, pair)
    problems = checks.defaults_problems(catalog, house, root)
    by_design = [key for key in catalog.keys() if house_module.by_design(catalog, house, *key)]
    out(f"{house.label} for {catalog.label}: {len(catalog.keys())} questions (entry and unit), "
        f"{len(house_module.defaults(catalog, house))} defaults, {len(by_design)} by design, "
        f"{len(house_module.without_default(catalog, house))} stated as none")
    out(f"defaults: {len(problems)} problems")
    return _report(out, problems)


def templates_check(root: Path, out: Out, pair: tuple = NEXT) -> bool:
    catalog, house = _load(root, pair)
    problems = checks.template_directive_problems(catalog, house)
    out(f"{catalog.label} and {house.label}: every directive of the compile and house "
        f"templates read whole; directives {', '.join(checks.DIRECTIVES)}")
    out(f"templates: {len(problems)} problems")
    return _report(out, problems)
