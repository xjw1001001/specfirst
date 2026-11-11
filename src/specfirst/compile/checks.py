"""The checkers of the std-1 gate (PLAN.md section 13.4).

Each checker returns a list of problems; an empty list means it passes.
Every one has planted-defect tests in tests/defects/ (rule R5).

    catalog_problems     entries fit the schema and each other
    source_problems      every entry cites a public source that exists
    probe_problems       every pair of alternatives has a probe
    wording_problems     phrasings keep the slots; reading notes cover the alternatives
    roundtrip_problems   decisions -> statements -> decisions is exact and unique
    template_problems    the parameters decisions set are the ones templates read
    house_problems       the house standard fits the catalog; STANDARD.md is its rendering
    compile_all          every alternative compiles
    yamaa_problems       compiled ADaM specs pass `yamaa check`
    run_problems         compiled ADaM specs run on the tiny study
    ars_problems         a compiled ARS file fits the ARS schema and its own references
    layout_problems      a layout and its ARS file name the same analyses
"""

from __future__ import annotations

import copy
import hashlib
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path

import yaml
from jsonschema import validators

from specfirst import schemas, sources
from specfirst.compile import house as house_module
from specfirst.compile import predicate, tiny
from specfirst.compile.catalog import Catalog
from specfirst.compile.compiler import (
    ARS_LISTS,
    Compiled,
    CompileError,
    compile_decisions,
    compile_template,
    relative_reference,
)
from specfirst.compile.house import House
from specfirst.compile.slots import SCALARS, Slot, SlotError, check_value
from specfirst.compile.standard_form import (
    StandardForm,
    StandardFormError,
    decision_record,
)
from specfirst.compile.standard_form import compile_template as statement_template
from specfirst.compile.standard_form import template_problems as statement_problems
from specfirst.compile.template import TemplateError, evaluate, names_used

MINIMUM_ENTRIES = 40  # PLAN.md section 13.4
PROBE_KINDS = ("record", "structural", "design")
# Where the specs of a variant read SDTM and write ADaM, relative to their
# folder <out>/v<nnn>/adam: the SDTM data are shared, the ADaM data are not.
VARIANT_SDTM = "../../sdtm"
VARIANT_ADAM = "../data"
ARS_SCHEMA = ("ars", "project/jsonschema/ars_ldm.schema.json")
_PLACEHOLDER = re.compile(r"\{([a-z][a-z0-9_]*)\}")
NOTE_HEADINGS = ("## Where it is stated", "## Words to look for", "## Traps")


# -- catalog -----------------------------------------------------------------


def catalog_problems(catalog: Catalog, root: Path) -> list[str]:
    """Entries fit the schema, the registries and each other."""
    problems = list(catalog.load_problems)
    if len(catalog.entries) < MINIMUM_ENTRIES:
        problems.append(f"{len(catalog.entries)} entries; the plan asks for {MINIMUM_ENTRIES}")
    phrases: dict[str, str] = {}
    for unit in catalog.units.values():
        if unit.kind not in ("module", "table_family"):
            problems.append(f"unit {unit.id}: unknown kind '{unit.kind}'")
        if not unit.title:
            problems.append(f"unit {unit.id}: no title")
        if unit.kind == "table_family":
            if not unit.phrase:
                problems.append(f"unit {unit.id}: a table family needs a phrase")
            for other, phrase in phrases.items():
                if unit.phrase and (phrase.startswith(unit.phrase)
                                    or unit.phrase.startswith(phrase)):
                    problems.append(f"units {other} and {unit.id}: "
                                    "one phrase starts with the other")
            phrases[unit.id] = unit.phrase
    skeletons: dict[str, str] = {}
    for entry in catalog.entries.values():
        where = entry.id
        for problem in schemas.problems("catalog-entry", entry.raw, root=root):
            problems.append(f"{where}: schema: {problem}")
        for unit in entry.units:
            if unit not in catalog.units:
                problems.append(f"{where}: unknown unit '{unit}'")
            elif entry.per_family and catalog.units[unit].kind != "table_family":
                problems.append(f"{where}: `units` lists {unit}, which is not a table family")
        try:
            used = predicate.names(predicate.parse(entry.applies_when))
            for name in sorted(used - set(catalog.design_features)):
                problems.append(f"{where}: applies_when names the unknown feature '{name}'")
        except predicate.PredicateError as error:
            problems.append(f"{where}: applies_when: {error}")
        ids = [alternative.id for alternative in entry.alternatives]
        if len(set(ids)) != len(ids):
            problems.append(f"{where}: an alternative ID is used twice")
        defaults = (entry.house_default.values() if isinstance(entry.house_default, dict)
                    else [entry.house_default])
        for default in defaults:
            if default is not None and default not in ids:
                problems.append(f"{where}: the house default '{default}' is not an alternative")
        if isinstance(entry.house_default, dict) and set(entry.house_default) != set(entry.units):
            problems.append(f"{where}: a default per unit must name every unit of `units`")
        for alternative in entry.alternatives:
            problems += statement_problems(entry, alternative)
            for slot in alternative.slots:
                for example in slot.examples:
                    try:
                        check_value(slot, example)
                    except SlotError as error:
                        problems.append(f"{where}/{alternative.id}: example: {error}")
            try:
                skeleton = statement_template(alternative).skeleton()
            except StandardFormError:
                continue
            if skeleton in skeletons:
                problems.append(
                    f"{where}/{alternative.id}: the same sentence as {skeletons[skeleton]}"
                )
            skeletons[skeleton] = f"{where}/{alternative.id}"
        for name in ("compile", "phrasings", "reading"):
            relative = getattr(entry, name)
            if relative and not (catalog.directory / relative).is_file():
                problems.append(f"{where}: {name} file {relative} is missing")
        try:
            fragments = compile_template(catalog, entry.id)
        except CompileError as error:
            problems += [f"{where}: {problem}" for problem in error.problems]
            continue
        if sorted(fragments) != sorted(ids):
            problems.append(
                f"{where}: the compile template must have exactly the alternatives {ids}"
            )
    return problems


# -- sources -----------------------------------------------------------------


def source_problems(catalog: Catalog, root: Path, cache: Path | None = None) -> list[str]:
    """Every entry cites at least one public source, and the citation can be followed.

    With `cache` (the fetch cache), a pinned source is checked on the fetched
    files: its path exists and its `find` text stands in the file.
    """
    problems = []
    manifest = sources.load_manifest(sources.manifest_path(root))
    pinned = {source.name for source in manifest.sources}
    used: set[str] = set()
    for key, source in catalog.sources.items():
        kind = source.get("kind")
        if kind == "pinned":
            if source.get("source") not in pinned:
                problems.append(f"sources.yaml: {key} names no source of third_party/sources.yaml")
        elif kind == "document":
            if not str(source.get("url", "")).startswith("https://"):
                problems.append(f"sources.yaml: {key} needs an https URL")
            if not source.get("version") or not source.get("confirmed"):
                problems.append(f"sources.yaml: {key} needs a version and how it was confirmed")
        else:
            problems.append(f"sources.yaml: {key} has the unknown kind '{kind}'")
        if not source.get("title"):
            problems.append(f"sources.yaml: {key} has no title")
    for entry in catalog.entries.values():
        if not entry.sources:
            problems.append(f"{entry.id}: no public source")
        cited = [(entry.id, s) for s in entry.sources]
        for alternative in entry.alternatives:
            cited += [(f"{entry.id}/{alternative.id}", s) for s in alternative.sources]
        for where, source in cited:
            ref = source.get("ref")
            if ref not in catalog.sources:
                problems.append(f"{where}: the source '{ref}' is not in sources.yaml")
                continue
            used.add(ref)
            known = catalog.sources[ref]
            if known.get("kind") != "pinned":
                if "path" in source:
                    problems.append(f"{where}: only a pinned source has a path ({ref})")
                continue
            if not source.get("path"):
                problems.append(f"{where}: the pinned source '{ref}' needs a path")
                continue
            if cache is None:
                continue
            path = cache / str(known.get("source")) / source["path"]
            if not path.is_file():
                problems.append(f"{where}: {ref} has no file {source['path']}")
            elif source.get("find") and source["find"].encode("ascii") not in path.read_bytes():
                problems.append(
                    f"{where}: '{source['find']}' does not stand in {ref}:{source['path']}"
                )
    for key in sorted(set(catalog.sources) - used):
        problems.append(f"sources.yaml: {key} is cited by no entry")
    return problems


# -- probes ------------------------------------------------------------------


def probe_problems(catalog: Catalog) -> list[str]:
    """Every pair of alternatives and every slot of an entry has a probe (rule 5 of 5.2)."""
    problems = []
    mentioned: dict[str, set[str]] = {}
    for probe_id, probe in catalog.probes.items():
        if probe.get("kind") not in PROBE_KINDS:
            problems.append(f"probe {probe_id}: unknown kind '{probe.get('kind')}'")
        if not probe.get("recipe"):
            problems.append(f"probe {probe_id}: no recipe")
        if probe.get("kind") == "record" and not probe.get("domains"):
            problems.append(f"probe {probe_id}: a record probe names its SDTM domains")
        entries = (set(probe.get("separates") or {}) | set(probe.get("varies") or {})
                   | set(probe.get("stresses") or []))
        if not entries:
            problems.append(f"probe {probe_id}: it serves no entry")
        for entry_id in entries:
            mentioned.setdefault(entry_id, set()).add(probe_id)
            if entry_id not in catalog.entries:
                problems.append(f"probe {probe_id}: unknown entry '{entry_id}'")
    for entry in catalog.entries.values():
        listed = set(entry.probes)
        for probe_id in sorted(listed - set(catalog.probes)):
            problems.append(f"{entry.id}: the probe '{probe_id}' is not in probes.yaml")
        for probe_id in sorted(mentioned.get(entry.id, set()) - listed):
            problems.append(
                f"{entry.id}: probes.yaml gives it '{probe_id}', the entry does not list it"
            )
        for probe_id in sorted((listed & set(catalog.probes)) - mentioned.get(entry.id, set())):
            problems.append(f"{entry.id}: the probe '{probe_id}' does not serve this entry")
        ids = [alternative.id for alternative in entry.alternatives]
        covered: set[frozenset] = set()
        varied: set[str] = set()
        for probe_id in listed & set(catalog.probes):
            probe = catalog.probes[probe_id]
            pairs = (probe.get("separates") or {}).get(entry.id)
            if pairs == "all":
                covered |= {frozenset(pair) for pair in combinations(ids, 2)}
            else:
                for pair in pairs or []:
                    if len(pair) != 2 or not set(pair) <= set(ids) or pair[0] == pair[1]:
                        problems.append(f"probe {probe_id}: {pair} is not a pair of {entry.id}")
                    else:
                        covered.add(frozenset(pair))
            slots = (probe.get("varies") or {}).get(entry.id) or []
            known = {slot.name for alternative in entry.alternatives for slot in alternative.slots}
            for name in slots:
                if name not in known:
                    problems.append(f"probe {probe_id}: {entry.id} has no slot '{name}'")
            varied |= set(slots)
        for first, second in combinations(ids, 2):
            if frozenset((first, second)) not in covered:
                problems.append(f"{entry.id}: no probe separates {first} from {second}")
        for alternative in entry.alternatives:
            for slot in alternative.slots:
                if slot.name not in varied:
                    problems.append(
                        f"{entry.id}/{alternative.id}: no probe varies the slot '{slot.name}'"
                    )
    return problems


def structural_probe_problems(catalog: Catalog, house: House) -> list[str]:
    """A structural probe that names no condition separates its pairs for any data.

    The check compiles the base decisions with each alternative of a claimed
    pair: the ARS or layout files must differ. A probe whose claim holds only
    beside another decision says so in `needs`, and one that needs a
    property of the design has the kind `design`; neither is compiled here.
    """
    problems = []
    base = base_vector(catalog, house)
    reference = "house"
    cache: dict[str, dict] = {}

    def tables(entry_id: str, unit: str, rule: str) -> dict:
        label = f"{entry_id}|{unit}|{rule}"
        if label not in cache:
            alternative = catalog.entry(entry_id).alternative(rule)
            value = {"rule": rule, **{s.name: s.examples[0] for s in alternative.slots}}
            records = [{**r, "value": value} if (r["id"], r["unit"]) == (entry_id, unit) else r
                       for r in base]
            try:
                files = compile_decisions(catalog, house, records, reference).files
            except CompileError as error:
                problems.append(f"{entry_id}/{rule}: {error.problems[0]}")
                files = {}
            cache[label] = {p: t for p, t in files.items() if not p.startswith("adam/")}
        return cache[label]

    for probe_id, probe in catalog.probes.items():
        if probe.get("kind") != "structural" or probe.get("needs"):
            continue
        for entry_id, pairs in (probe.get("separates") or {}).items():
            if entry_id not in catalog.entries:
                continue
            entry = catalog.entry(entry_id)
            ids = [alternative.id for alternative in entry.alternatives]
            claimed = list(combinations(ids, 2)) if pairs == "all" else \
                [tuple(pair) for pair in pairs or [] if set(pair) <= set(ids)]
            for first, second in claimed:
                if not any(tables(entry_id, unit, first) != tables(entry_id, unit, second)
                           for unit in entry.units):
                    problems.append(
                        f"probe {probe_id}: {entry_id}: {first} and {second} compile to the "
                        "same table files; name what the probe needs, or plant a record"
                    )
    return problems


# -- phrasings and reading notes ---------------------------------------------


def wording_problems(catalog: Catalog) -> list[str]:
    """Phrasings keep every slot of their statement; reading notes cover every alternative."""
    problems = []
    families: tuple[str, ...] | None = None
    for entry in catalog.entries.values():
        try:
            raw = catalog.read_yaml(entry.phrasings)
        except (OSError, yaml.YAMLError) as error:
            problems.append(f"{entry.id}: phrasings: {error}")
            raw = None
        if isinstance(raw, dict):
            if raw.get("entry") != entry.id:
                problems.append(f"{entry.id}: {entry.phrasings} is for '{raw.get('entry')}'")
            given = raw.get("alternatives") or {}
            for alternative in entry.alternatives:
                texts = given.get(alternative.id)
                if not isinstance(texts, dict) or len(texts) < 2:
                    problems.append(f"{entry.id}/{alternative.id}: needs at least two phrasings")
                    continue
                if families is None:
                    families = tuple(texts)
                if tuple(texts) != families:
                    problems.append(
                        f"{entry.id}/{alternative.id}: phrasing families must be {list(families)}"
                    )
                wanted = sorted(_PLACEHOLDER.findall(alternative.statement))
                seen = set()
                for family, text in texts.items():
                    label = f"{entry.id}/{alternative.id}/{family}"
                    if not isinstance(text, str) or not text.isascii() or "\n" in text.strip():
                        problems.append(f"{label}: a phrasing is one line of ASCII")
                        continue
                    if sorted(_PLACEHOLDER.findall(text)) != wanted:
                        problems.append(
                            f"{label}: the phrasing must use exactly the slots {wanted}"
                        )
                    if text.strip() == alternative.statement or text in seen:
                        problems.append(f"{label}: the phrasing repeats another sentence")
                    seen.add(text)
            for extra in sorted(set(given) - {a.id for a in entry.alternatives}):
                problems.append(f"{entry.id}: phrasings for the unknown alternative '{extra}'")
        elif raw is not None:
            problems.append(f"{entry.id}: {entry.phrasings} is not a mapping")
        note = catalog.directory / entry.reading
        if not note.is_file():
            continue  # catalog_problems reports the missing file
        text = note.read_text(encoding="utf-8", errors="replace")
        for heading in NOTE_HEADINGS:
            if heading not in text:
                problems.append(f"{entry.id}: the reading notes lack the heading '{heading}'")
        if f"`{entry.id}`" not in text:
            problems.append(f"{entry.id}: the reading notes do not name the entry")
        for alternative in entry.alternatives:
            if f"`{alternative.id}`" not in text:
                problems.append(f"{entry.id}: the reading notes do not cover `{alternative.id}`")
    return problems


# -- round trip --------------------------------------------------------------

_HARD_TEXT = ('A, b; c.', "Day 1 (pre-dose) and 2", "x = 'y' <0.001", "Baseline is the value")


def _samples(slot: Slot) -> list:
    """Values that try a slot: its examples and, where the slot allows them, awkward ones."""
    values = list(slot.examples)
    scalar = slot.item_type or (slot.type if slot.type in SCALARS else None)
    extra: list = []
    if slot.choices is not None:
        extra = [slot.choices[0], slot.choices[-1]]
    elif scalar == "text":
        extra = list(_HARD_TEXT)
    elif scalar == "int":
        extra = [0, 1, 7, 100, 12345]
    elif scalar == "number":
        extra = [0, 0.5, 12.25, 100]
    elif scalar == "name":
        extra = ["A", "AB_C1", "DM.ARM"]
    if slot.type == "records":
        hard = {name: {"text": _HARD_TEXT[0], "int": 7, "number": 0.5, "name": "AB"}[kind]
                for name, kind in slot.fields}
        candidates = [[hard], [hard, {**hard, **{n: _HARD_TEXT[1] for n, k in slot.fields
                                                 if k == "text"}}]]
        if all(kind != "text" for _, kind in slot.fields):
            candidates = [[hard]]
    elif slot.item_type:
        candidates = [[item] for item in extra] + [extra[:3]]
    else:
        candidates = extra
    for candidate in candidates:
        try:
            check_value(slot, candidate)
        except SlotError:
            continue
        if candidate not in values:
            values.append(candidate)
    return values


def decision_samples(catalog: Catalog) -> list[tuple[str, str, dict]]:
    """Every (entry, unit, value) the round trip is run on."""
    samples = []
    for entry in catalog.entries.values():
        for alternative in entry.alternatives:
            columns = [_samples(slot) for slot in alternative.slots]
            rows = max([len(column) for column in columns] or [1])
            for unit in entry.units:
                for row in range(rows):
                    value = {"rule": alternative.id}
                    for slot, column in zip(alternative.slots, columns, strict=True):
                        value[slot.name] = column[row % len(column)]
                    samples.append((entry.id, unit, value))
    return samples


def roundtrip_problems(catalog: Catalog) -> tuple[list[str], int]:
    """Decisions to statements to decisions is exact, and no statement fits two decisions.

    Returns the problems and the number of statements tried.
    """
    form = StandardForm(catalog)
    problems = []
    samples = decision_samples(catalog)
    tried: set[tuple[str, str]] = set()
    for entry_id, unit, value in samples:
        label = f"{entry_id}/{value['rule']} ({unit})"
        try:
            statement = form.render(entry_id, unit, value)
        except StandardFormError as error:
            problems.append(f"{label}: cannot render: {error}")
            continue
        tried.add((entry_id, value["rule"]))
        found = form.matches(statement)
        if found != [(entry_id, unit, value)]:
            names = [f"{e}/{v['rule']} ({u})" for e, u, v in found] or ["nothing"]
            exact = (entry_id, unit, value) in found
            reason = "ambiguous" if exact else "not exact"
            problems.append(f"{label}: {reason}: '{statement}' parses to {', '.join(names)}")
    for entry in catalog.entries.values():
        for alternative in entry.alternatives:
            if (entry.id, alternative.id) not in tried:
                problems.append(f"{entry.id}/{alternative.id}: no statement was tried")
    return problems, len(samples)


def document_problems(catalog: Catalog, records: list[dict], doc: str = "sap") -> list[str]:
    """A standard-form document of the records parses back to the same records."""
    form = StandardForm(catalog)
    try:
        text = form.render_document(doc, "Standard form", records)
        parsed_doc, parsed = form.parse_document(text)
    except StandardFormError as error:
        return [f"document round trip: {error}"]
    problems = []
    wanted = [(r["id"], r["unit"], r["value"]) for r in form.order(records)]
    if [(r["id"], r["unit"], r["value"]) for r in parsed] != wanted or parsed_doc != doc:
        problems.append("document round trip: the parsed decisions differ from the rendered ones")
    for item in parsed:
        record = decision_record(item, doc, "stated", "document_rule")
        for problem in schemas.problems("decision-record", record, root=None):
            problems.append(f"document round trip: {item['id']}: {problem}")
    return problems


# -- parameters and house ----------------------------------------------------


def _produced(catalog: Catalog) -> dict[str, dict[str, set[str]]]:
    """scope ('' or a table family) -> parameter -> the entries that set it."""
    produced: dict[str, dict[str, set[str]]] = {}
    for entry in catalog.entries.values():
        try:
            alternatives = compile_template(catalog, entry.id)
        except CompileError:
            continue
        for unit in entry.units:
            known = catalog.units.get(unit)
            scope = unit if known is not None and known.kind == "table_family" else ""
            for body in alternatives.values():
                for name in ((body or {}).get("params") or {}):
                    produced.setdefault(scope, {}).setdefault(name, set()).add(entry.id)
    return produced


def template_problems(catalog: Catalog, house: House) -> list[str]:
    """Every parameter a decision sets is read by a template, and the reverse."""
    problems = []
    produced = _produced(catalog)
    shared = produced.get("", {})
    read_shared: set[str] = set()
    for scope, names in produced.items():
        for name, entries in names.items():
            if len(entries) > 1 or (scope and name in shared):
                problems.append(f"parameter '{name}' is set by more than one entry")
    families = house.ars.get("families") or {}
    for unit in catalog.units.values():
        if unit.kind != "table_family":
            continue
        if unit.id not in families or unit.id not in (house.layout.get("families") or {}):
            problems.append(f"house: no ARS or layout template for {unit.id}")
            continue
        try:
            ars = house.read(families[unit.id])
            layout = house.read(house.layout["families"][unit.id])
        except (OSError, yaml.YAMLError) as error:
            problems.append(f"house: {unit.id}: {error}")
            continue
        defined = set(ars.get("define") or {})
        used = (names_used({k: v for k, v in ars.items()}) | names_used(layout)) - defined
        own = produced.get(unit.id, {})
        for name in sorted(used - set(own) - set(shared)):
            problems.append(f"house: {unit.id}: no decision sets the parameter '{name}'")
        for name in sorted(set(own) - used - {"included"}):
            problems.append(
                f"house: {unit.id}: no template reads '{name}' ({sorted(own[name])[0]})"
            )
        if "included" not in own:
            problems.append(f"house: {unit.id}: no decision says whether the output is included")
        read_shared |= used & set(shared)
    for name in sorted(set(shared) - read_shared):
        problems.append(f"house: no template reads '{name}' ({sorted(shared[name])[0]})")
    return problems


def house_problems(catalog: Catalog, house: House, root: Path) -> list[str]:
    """The house standard fits the catalog, and STANDARD.md is rendered from the two."""
    problems = []
    if house.catalog != catalog.name:
        problems.append(f"house: made for the catalog '{house.catalog}', not '{catalog.name}'")
    for entry_id in house.default_values:
        if entry_id not in catalog.entries:
            problems.append(f"house: default_values names the unknown entry '{entry_id}'")
    form = StandardForm(catalog)
    try:
        defaults = house_module.defaults(catalog, house)
        for record in defaults:
            form.check_value(record["id"], record["unit"], record["value"])
        text = house_module.standards_document(catalog, house)
        records = house_module.default_decisions(catalog, house)
    except (StandardFormError, KeyError) as error:
        return problems + [f"house: defaults: {error}"]
    document = house.directory / str(house.raw.get("document", ""))
    if not document.is_file():
        problems.append(f"house: {document.name} is missing")
    elif document.read_text(encoding="utf-8", errors="replace") != text:
        problems.append(f"house: {document.name} differs from its rendering; "
                        "run `specfirst house --write`")
    if [(r["id"], r["unit"], r["value"]) for r in records] != \
            [(r["id"], r["unit"], r["value"]) for r in form.order(defaults)]:
        problems.append("house: the parsed standards document differs from the defaults")
    for record in records:
        for problem in schemas.problems("decision-record", record, root=root):
            problems.append(f"house: default {record['id']}: {problem}")
    for dataset, meta in house.adam.items():
        if not (house.directory / str(meta.get("parent", ""))).is_file():
            problems.append(f"house: the parent spec of {dataset} is missing")
        for entry_id in meta.get("optional") or []:
            if entry_id not in catalog.entries:
                problems.append(f"house: {dataset}: optional names the unknown entry '{entry_id}'")
    for relative in [house.ars.get("common"), *(house.ars.get("families") or {}).values(),
                     *(house.layout.get("families") or {}).values()]:
        if not relative or not (house.directory / relative).is_file():
            problems.append(f"house: the template {relative} is missing")
    return problems


# -- compile -----------------------------------------------------------------


@dataclass
class Variant:
    """One decision vector and what it compiles to."""

    label: str
    records: list[dict]
    compiled: Compiled | None = None
    problems: list[str] = field(default_factory=list)


def base_vector(catalog: Catalog, house: House) -> list[dict]:
    """The house defaults, and the first example of the first alternative where there is none."""
    records = house_module.defaults(catalog, house)
    have = {(record["id"], record["unit"]) for record in records}
    for entry_id, unit in catalog.keys():
        if (entry_id, unit) in have:
            continue
        alternative = catalog.entry(entry_id).alternatives[0]
        value = {"rule": alternative.id, **{s.name: s.examples[0] for s in alternative.slots}}
        records.append({"id": entry_id, "unit": unit, "value": value})
    order = catalog.keys()
    return sorted(records, key=lambda record: order.index((record["id"], record["unit"])))


def variants(catalog: Catalog, house: House) -> list[Variant]:
    """The base vector, then one vector per alternative and example with one decision changed."""
    base = base_vector(catalog, house)
    found = [Variant("base", base)]
    for entry in catalog.entries.values():
        for unit in entry.units:
            for alternative in entry.alternatives:
                rows = max([len(slot.examples) for slot in alternative.slots] or [1])
                for row in range(rows):
                    value = {"rule": alternative.id}
                    for slot in alternative.slots:
                        value[slot.name] = slot.examples[row % len(slot.examples)]
                    current = next(r for r in base if (r["id"], r["unit"]) == (entry.id, unit))
                    if current["value"] == value:
                        continue
                    records = [
                        {**r, "value": value} if (r["id"], r["unit"]) == (entry.id, unit) else r
                        for r in base
                    ]
                    scope = f" ({unit})" if entry.per_family else ""
                    found.append(Variant(f"{entry.id}/{alternative.id}{scope} #{row + 1}", records))
    return found


def house_reference(house: House, out_dir: Path) -> str:
    """The house folder as the specs of a variant name it.

    `yamaa_problems` writes each variant to its own folder `<out_dir>/v<nnn>`,
    so the path is relative to `<out_dir>/v<nnn>/adam`.
    """
    return relative_reference(house.directory, out_dir / "v000" / "adam")


def compile_all(catalog: Catalog, house: House, out_dir: Path) -> list[Variant]:
    """Compile every variant. A variant that fails keeps its problems."""
    found = variants(catalog, house)
    house_ref = house_reference(house, out_dir)
    for variant in found:
        try:
            variant.compiled = compile_decisions(catalog, house, variant.records, house_ref,
                                                 sdtm_dir=VARIANT_SDTM, adam_dir=VARIANT_ADAM)
        except CompileError as error:
            variant.problems = [f"{variant.label}: {problem}" for problem in error.problems]
        except (TemplateError, KeyError, TypeError) as error:
            variant.problems = [f"{variant.label}: {type(error).__name__}: {error}"]
    return found


def _changed(base: list[dict], records: list[dict]) -> tuple[tuple[str, str], dict]:
    """The one decision in which a variant differs from the base vector."""
    for old, new in zip(base, records, strict=True):
        if old["value"] != new["value"]:
            return (new["id"], new["unit"]), new["value"]
    raise ValueError("the variant equals the base vector")


def shown_with(catalog: Catalog, house: House, found: list[Variant], variant: Variant,
               house_ref: str) -> str | None:
    """A second changed decision under which the variant's own change shows, or None.

    Some decisions change the compiled files only beside another decision: a
    p-value format shows only when the table compares treatments.
    """
    base = found[0].records
    key, value = _changed(base, variant.records)
    for other in found[1:]:
        if other.compiled is None or other is variant:
            continue
        other_key, _ = _changed(base, other.records)
        if other_key == key:
            continue
        both = [{**r, "value": value} if (r["id"], r["unit"]) == key else r
                for r in other.records]
        try:
            compiled = compile_decisions(catalog, house, both, house_ref,
                                         sdtm_dir=VARIANT_SDTM, adam_dir=VARIANT_ADAM)
        except CompileError:
            continue
        if compiled.files != other.compiled.files:
            return other.label
    return None


def coverage_problems(catalog: Catalog, house: House, found: list[Variant],
                      house_ref: str) -> tuple[list[str], list[str]]:
    """Every alternative was compiled, and each one changes what is compiled.

    Returns the problems and notes. A note names a decision whose change
    shows only beside another changed decision.
    """
    problems = [problem for variant in found for problem in variant.problems]
    notes: list[str] = []
    base = found[0].compiled
    if base is None:
        return problems, notes
    compiled = {(record["id"], record["value"]["rule"]) for variant in found
                if variant.compiled is not None for record in variant.records}
    for entry in catalog.entries.values():
        for alternative in entry.alternatives:
            if (entry.id, alternative.id) not in compiled:
                problems.append(f"{entry.id}/{alternative.id}: never compiled")
    for variant in found[1:]:
        if variant.compiled is None or variant.compiled.files != base.files:
            continue
        beside = shown_with(catalog, house, found, variant, house_ref)
        if beside is None:
            problems.append(f"{variant.label}: compiles to the same files as the base decisions, "
                            "whatever other decision changes with it")
        else:
            notes.append(f"{variant.label}: shows only beside another decision, "
                         f"for example {beside}")
    return problems, notes


def _adam_key(compiled: Compiled) -> str:
    text = "".join(f"{path}\n{body}" for path, body in sorted(compiled.files.items())
                   if path.startswith("adam/"))
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def distinct_adam(found: list[Variant], out_dir: Path) -> list[tuple[Variant, Path]]:
    """The variants whose ADaM files differ from every earlier one, each with its folder."""
    seen: set[str] = set()
    distinct = []
    for variant in found:
        if variant.compiled is None:
            continue
        key = _adam_key(variant.compiled)
        if key not in seen:
            seen.add(key)
            distinct.append((variant, out_dir / f"v{len(seen):03d}"))
    return distinct


def yamaa_problems(found: list[Variant], out_dir: Path,
                   check: Callable[[Path], list[str]] | None = None) -> tuple[list[str], int]:
    """Compiled ADaM specs pass `yamaa check`. Returns the problems and the specs checked.

    Variants whose ADaM files are identical are checked once.
    """
    check = check or yamaa_check
    problems: list[str] = []
    checked = 0
    for variant, folder in distinct_adam(found, out_dir):
        variant.compiled.write(folder)
        for dataset in variant.compiled.datasets:
            checked += 1
            for issue in check(folder / "adam" / f"{dataset.lower()}.yaml"):
                problems.append(f"{variant.label}: {dataset}: {issue}")
    return problems, checked


def run_problems(found: list[Variant], out_dir: Path,
                 run: Callable[[Path], list[str]] | None = None) -> tuple[list[str], int]:
    """Compiled ADaM specs run on the tiny study. Returns the problems and the specs run.

    `yamaa check` reads no data, so a spec can pass it and still fail when
    its inputs are bound (docs/lessons.md). This check builds every distinct
    set of ADaM specs on the hand-made study of `specfirst.compile.tiny`.
    It proves that the specs run, not that their values are right.
    """
    run = run or yamaa_run
    tiny.write(out_dir / "sdtm")
    problems: list[str] = []
    ran = 0
    for variant, folder in distinct_adam(found, out_dir):
        variant.compiled.write(folder)
        (folder / "data").mkdir(parents=True, exist_ok=True)
        for dataset in variant.compiled.datasets:
            ran += 1
            issues = run(folder / "adam" / f"{dataset.lower()}.yaml")
            problems += [f"{variant.label}: {dataset}: {issue}" for issue in issues]
            if issues:
                break  # the later datasets read this one
    return problems, ran


def _issues(table: object) -> list[str]:
    import pyarrow

    return [
        f"{row.get('condition')} at {Path(str(row.get('file'))).name}:{row.get('line')}: "
        f"{row.get('message')}"
        for row in pyarrow.table(table).to_pylist()
    ]


def yamaa_run(spec: Path) -> list[str]:
    """Run one specification and save its dataset; the issues as text."""
    import yamaa  # the engine is imported only where a spec is run

    try:
        result = yamaa.spec(str(spec)).run()
        issues = _issues(result.issues)
        if result.status != "succeeded":
            return issues or [f"run {result.status}"]
        result.save()
    except yamaa.Error as error:
        return [f"run refused: {error}"]
    return issues


def yamaa_check(spec: Path) -> list[str]:
    """The issues `yamaa check` reports for one specification, as text."""
    import yamaa  # the engine is imported only where a spec is checked

    try:
        result = yamaa.spec(str(spec)).check()
    except yamaa.Error as error:
        return [f"check refused: {error}"]
    issues = _issues(result.issues)
    if result.status != "succeeded" and not issues:
        issues.append(f"check {result.status}")
    return issues


def load_ars_schema(cache: Path) -> dict:
    path = cache / ARS_SCHEMA[0] / ARS_SCHEMA[1]
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def ars_problems(doc: dict, schema: dict) -> list[str]:
    """An ARS document fits the ARS JSON Schema, and every ID it names exists once."""
    validator = validators.validator_for(schema)(schema)
    problems = [
        f"schema: {'/'.join(str(p) for p in error.path) or '<root>'}: {error.message[:200]}"
        for error in sorted(validator.iter_errors(doc), key=lambda e: [str(p) for p in e.path])
    ]
    ids: dict[str, set[str]] = {}
    for name in ARS_LISTS:
        listed = [element.get("id") for element in doc.get(name) or []]
        for element_id in sorted({i for i in listed if listed.count(i) > 1}):
            problems.append(f"{name}: the ID '{element_id}' is used twice")
        ids[name] = set(listed)
    operations = {
        relationship.get("id"): method.get("id")
        for method in doc.get("methods") or []
        for operation in method.get("operations") or []
        for relationship in operation.get("referencedOperationRelationships") or []
    }
    operation_method = {
        operation.get("id"): method.get("id")
        for method in doc.get("methods") or []
        for operation in method.get("operations") or []
    }
    referenced_operation = {
        relationship.get("id"): relationship.get("operationId")
        for method in doc.get("methods") or []
        for operation in method.get("operations") or []
        for relationship in operation.get("referencedOperationRelationships") or []
    }
    for relationship, operation in sorted(referenced_operation.items()):
        if operation not in operation_method:
            problems.append(f"relationship {relationship}: the operation '{operation}' "
                            "is not defined")
    by_id = {analysis.get("id"): analysis for analysis in doc.get("analyses") or []}

    def groupings(analysis: dict) -> list:
        return [g.get("groupingId") for g in analysis.get("orderedGroupings") or []]

    for analysis in doc.get("analyses") or []:
        where = f"analysis {analysis.get('id')}"
        for key, name in (("analysisSetId", "analysisSets"), ("dataSubsetId", "dataSubsets"),
                          ("methodId", "methods")):
            if analysis.get(key) is not None and analysis[key] not in ids[name]:
                problems.append(f"{where}: {key} '{analysis[key]}' is not defined")
        for grouping in analysis.get("orderedGroupings") or []:
            if grouping.get("groupingId") not in ids["analysisGroupings"]:
                problems.append(f"{where}: grouping '{grouping.get('groupingId')}' is not defined")
        for reference in analysis.get("referencedAnalysisOperations") or []:
            if reference.get("analysisId") not in ids["analyses"]:
                problems.append(
                    f"{where}: refers to the unknown analysis '{reference.get('analysisId')}'"
                )
            relationship = reference.get("referencedOperationRelationshipId")
            if operations.get(relationship) != analysis.get("methodId"):
                problems.append(f"{where}: its method has no relationship '{relationship}'")
            other = by_id.get(reference.get("analysisId"))
            if other is None:
                continue
            # The analysis that gives a numerator or a denominator holds the
            # operation, has the same analysis set and the same leading (subject)
            # groupings: a Total percentage divides by the Total count.
            operation = referenced_operation.get(relationship)
            if operation in operation_method and \
                    operation_method[operation] != other.get("methodId"):
                problems.append(f"{where}: '{other.get('id')}' has no operation '{operation}'")
            if other.get("analysisSetId") != analysis.get("analysisSetId"):
                problems.append(f"{where}: '{other.get('id')}' is on another analysis set")
            theirs = groupings(other)
            if not theirs or groupings(analysis)[:len(theirs)] != theirs:
                problems.append(f"{where}: '{other.get('id')}' has other subject groupings")

    def walk(items: list, where: str) -> None:
        for item in items:
            if "analysisId" in item and item["analysisId"] not in ids["analyses"]:
                problems.append(f"{where}: lists the unknown analysis '{item['analysisId']}'")
            if "outputId" in item and item["outputId"] not in ids["outputs"]:
                problems.append(f"{where}: lists the unknown output '{item['outputId']}'")
            walk(((item.get("sublist") or {}).get("listItems")) or [], where)

    walk(doc.get("mainListOfContents", {}).get("contentsList", {}).get("listItems") or [],
         "mainListOfContents")
    return problems


def _first_condition(doc: dict) -> dict:
    return doc["analysisSets"][0]["condition"]


ARS_CONTROLS: tuple[tuple[str, Callable[[dict], None]], ...] = (
    ("a comparator outside the controlled terms",
     lambda doc: _first_condition(doc).__setitem__("comparator", "EQUALS")),
    ("an analysis without its required name",
     lambda doc: doc["analyses"][0].__delitem__("name")),
    ("a field the model does not have",
     lambda doc: doc["analyses"][0].__setitem__("confidence", 1)),
)


def ars_schema_control(doc: dict, schema: dict) -> list[str]:
    """Negative controls for the schema check (rule R5): planted defects must be reported.

    Each control changes a copy of a valid document so that it breaks the
    ARS schema. Returns the controls the check did not report; an empty
    list means the schema check can fail.
    """
    missed = []
    for label, plant in ARS_CONTROLS:
        planted = copy.deepcopy(doc)
        plant(planted)
        if not any(problem.startswith("schema:") for problem in ars_problems(planted, schema)):
            missed.append(f"control not reported: {label}")
    return missed


def _strings(node: object) -> list[str]:
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        return [text for child in node.values() for text in _strings(child)]
    if isinstance(node, list):
        return [text for child in node for text in _strings(child)]
    return []


def layout_problems(compiled: Compiled) -> list[str]:
    """Layouts and the ARS file name the same analyses and groupings (P3: nothing unused)."""
    doc = compiled.ars or {}
    analyses = {analysis["id"] for analysis in doc.get("analyses") or []}
    groupings = {grouping["id"] for grouping in doc.get("analysisGroupings") or []}
    outputs = {output["id"] for output in doc.get("outputs") or []}
    problems = []
    named: set[str] = set()
    for unit, layout in sorted(compiled.layouts.items()):
        for part in ("output", "columns", "rows", "formats"):
            if layout.get(part) in (None, {}, []):
                problems.append(f"layout {unit}: the part '{part}' is missing")
        if (layout.get("output") or {}).get("id") not in outputs:
            problems.append(f"layout {unit}: its output is not in the ARS file")
        for text in _strings(layout):
            if text.startswith("An_"):
                named.add(text)
                if text not in analyses:
                    problems.append(f"layout {unit}: the analysis '{text}' is not in the ARS file")
            elif text.startswith("Grp_") and text not in groupings:
                problems.append(f"layout {unit}: the grouping '{text}' is not in the ARS file")
    for analysis_id in sorted(analyses - named):
        problems.append(f"ARS: no layout shows the analysis '{analysis_id}'")
    return problems


def table_problems(found: list[Variant], schema: dict) -> tuple[list[str], int]:
    """ARS and layout checks on every distinct compiled ARS file. Returns problems and count."""
    problems: list[str] = []
    seen: set[str] = set()
    for variant in found:
        if variant.compiled is None or variant.compiled.ars is None:
            continue
        key = hashlib.sha256(
            "".join(body for path, body in sorted(variant.compiled.files.items())
                    if not path.startswith("adam/")).encode("ascii")
        ).hexdigest()
        if key in seen:
            continue
        seen.add(key)
        both = ars_problems(variant.compiled.ars, schema) + layout_problems(variant.compiled)
        for problem in both:
            problems.append(f"{variant.label}: {problem}")
    return problems, len(seen)


def evaluate_examples(catalog: Catalog) -> list[str]:
    """Every compile template evaluates on every example of its alternative."""
    problems = []
    for entry in catalog.entries.values():
        try:
            alternatives = compile_template(catalog, entry.id)
        except CompileError as error:
            problems += error.problems
            continue
        for alternative in entry.alternatives:
            rows = max([len(slot.examples) for slot in alternative.slots] or [1])
            for row in range(rows):
                scope = {s.name: s.examples[row % len(s.examples)] for s in alternative.slots}
                try:
                    evaluate(alternatives.get(alternative.id) or {}, scope)
                except TemplateError as error:
                    problems.append(f"{entry.id}/{alternative.id}: {error}")
    return problems
