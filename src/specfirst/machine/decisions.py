"""The decision records of a kit of real data, held against its reporting events.

PLAN.md sections 4.3 and 10, ADR-012 (decision 2), ADR-015. The efficacy
tables of the pilot need decisions that `catalog@1` does not hold yet. They
are written as decision records of the kit (`build.decisions` in kit.yaml,
one record per line), with IDs `custom:<slug>`, until `catalog@2` has
entries for them. The reporting event of the kit is our own file, written
from those decisions, and no compiler joins the two yet. So this module
holds them together:

- every record fits decision-record.schema.json, and its ID is custom and
  used once;
- every element a record `binds` is in a reporting event of the kit: an
  analysis, an analysis set, a data subset, a grouping or a method;
- where a decision sets an option of the method registry (`PARAMETERS`),
  every analysis it binds resolves that option to the decision's value;
- the visit of the LS means of the mixed model (`LAST_VISIT`): on the
  model records of every analysis the decision binds, the last visit, in
  the order models.R gives the visits, is the one the decision names.

A changed parameter in the reporting event, or a changed value in a record,
is seen by the rule of `PARAMETERS`; tests/unit/test_efficacy.py plants both, and
tests/defects (D9-efficacy) plants the first on the pilot.

The last rule closes G2 of the review of real-5b (the owner's answer of
2026-11-20, ADR-015): with the visits taken from AVISIT, text, Week 8 is
the last visit, and the LS means of Week 8 stood in the table "to Week 24"
with every option as its decision says. It needs the built ADaM data: the
gate's check `decisions` hands them over (specfirst.machine.build).

What it does not hold (review of real-5a, F4; review of real-5b, F5): the
values of the records that set no registry option are held against
nothing here: of real-5a the analysis set, the visit record, the baseline
rows and the decimals; of real-5b the records of the mixed model
(custom:eff-mmrm-records) and of CIBIC+ (custom:eff-cibic-records), the
categories and their denominator (custom:eff-cibic-categories) and the
two display records (custom:eff-mmrm-display, custom:eff-cibic-display);
and a record's binds are held only for existence and for the options it
sets. Since real-5b the proofs of the CSR's exceptions ask that every
decision an entry names binds an analysis of the cell or its method, and
an other analysis of a proof may differ only in the options its decisions
set, and not in those whose values are columns (K1, specfirst.machine.csr).
A record in conflict keeps the value the build uses until a person
decides; the owner decided those of the pilot on 2026-11-20 (ADR-015).
"""

from __future__ import annotations

import html
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

from specfirst import schemas
from specfirst.machine import ard, ars
from specfirst.machine.registry import Registry

# Decision -> {key of its value: the registry option it sets}. The custom
# decisions of real-5a and real-5b that the method registry reads (ADR-015 and its
# amendment of real-5b).
PARAMETERS: dict[str, dict[str, str]] = {
    "custom:eff-model-terms": {"factors": "factors", "covariates": "covariates"},
    "custom:eff-dose-response": {"rule": "model", "dose": "dose"},
    "custom:eff-pairwise": {"df": "df", "confidence_level": "confidence_level"},
    "custom:eff-lsmeans-weights": {"rule": "weights"},
    "custom:eff-mmrm-terms": {"factors": "factors", "covariates": "covariates",
                              "visit": "visit", "by_visit": "by_visit",
                              "treatment_by_visit": "treatment_by_visit"},
    "custom:eff-mmrm-covariance": {"rule": "covariance"},
    "custom:eff-mmrm-df": {"rule": "df"},
    "custom:eff-mmrm-visit": {"rule": "at"},
    "custom:eff-cmh": {"rule": "statistic", "scores": "scores", "strata": "strata"},
}

# The decision whose rule `last` names the visit of the LS means: `label` is a column of
# the model records and `last` its value on every model record of the last visit (review
# of real-5b, G2; the owner's answer of 2026-11-20).
LAST_VISIT = "custom:eff-mmrm-visit"


def load(path: Path) -> list[dict]:
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def _squeeze(text: str) -> str:
    return "".join(html.unescape(str(text)).split())


class Quotes:
    """The texts of a kit's documents, to check a quote by script (issue #31): a PDF by
    poppler's pdftotext, an XML or text file as it is (its entities read); blanks do not
    count. A quote is found when it stands in the text of its document."""

    def __init__(self, documents: dict[str, Path]):
        self.documents = documents  # document ID -> file
        self._texts: dict[str, str | None] = {}

    def text(self, doc_id: str) -> str | None:
        if doc_id not in self._texts:
            path = self.documents.get(doc_id)
            if path is None or not path.is_file():
                self._texts[doc_id] = None
            elif path.suffix.lower() == ".pdf":
                if shutil.which("pdftotext") is None:
                    raise ValueError("pdftotext is not installed; it comes with poppler")
                done = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                                      capture_output=True, text=True, encoding="utf-8",
                                      errors="replace", check=False)
                if done.returncode != 0:
                    raise ValueError(f"pdftotext exited {done.returncode} on {path.name}")
                self._texts[doc_id] = _squeeze(done.stdout)
            else:
                self._texts[doc_id] = _squeeze(path.read_text(encoding="utf-8",
                                                              errors="replace"))
        return self._texts[doc_id]

    def knows(self, doc_id: str) -> bool:
        """The citation names a document whose text a script can read."""
        return doc_id in self.documents

    def found(self, doc_id: str, quote: str) -> bool:
        text = self.text(doc_id)
        return bool(text) and bool(_squeeze(quote)) and _squeeze(quote) in (text or "")


# The document a default cites: the house standard the kit names, as its STANDARD.md states
# every default (specfirst.compile.house, DOCUMENT_ID).
HOUSE_DOCUMENT = "house"
# Sources a record may cite that are no document of a kit, so that no script checks their
# quotes; any other name is a problem (a document misnamed). The owner's answers of
# 2026-11-20 (ADR-015, "The owner's answers (2026-11-20)").
OTHER_SOURCES = {"answers": "the owner's answers (ADR-015)"}


def kit_quotes(root: Path, kit, folder: Path) -> Quotes:
    """The documents of a kit whose quotes a script checks: its documents in the build, and
    the standards document of the house it names (`house`, its STANDARD.md)."""
    documents = {doc.id: folder / doc.file for doc in kit.documents}
    if kit.standard is not None:
        from specfirst.compile import house as houses

        documents[HOUSE_DOCUMENT] = houses.default_dir(root, kit.standard[1]) / "STANDARD.md"
    return Quotes(documents)


def _normal(value: object) -> str:
    return json.dumps(value, sort_keys=True)


def house_values(catalog, house, entry_id: str, unit: str) -> list[dict]:
    """The values of the house's default for an entry and unit: one, or one per case of a
    default by design (each with its `when`); empty where the house has no default."""
    from specfirst.compile import house as houses

    entry = catalog.entry(entry_id)
    if house.defaults_file is None:
        found = houses.default_value(catalog, house, entry_id, unit)
        return [found] if found is not None else []
    made = []
    for case in houses.choices(house, entry_id, unit, entry.per_family):
        if case.get("rule") is not None:
            made.append({"rule": case["rule"], **(case.get("values") or {})})
    return made


def house_sources(catalog, house, entry_id: str, unit: str, value: dict) -> list[str]:
    """The sources the house gives for its default of an entry and unit, where the value is
    that default (of one of its cases): `ref path: where`, in the house's order."""
    from specfirst.compile import house as houses

    if house.defaults_file is None:
        return []
    said = []
    for case in houses.choices(house, entry_id, unit, catalog.entry(entry_id).per_family):
        if case.get("rule") is None or _normal(
                {"rule": case["rule"], **(case.get("values") or {})}) != _normal(value):
            continue
        for source in case.get("sources") or []:
            where = " ".join(str(source.get(key)) for key in ("ref", "path", "where")
                             if source.get(key))
            said.append(where)
    return said


def catalog_problems(record: dict, catalog, house) -> list[str]:
    """Why a record of the catalog the kit names does not fit it (issue #31, ADR-022): its
    entry and unit, its value (an alternative with its slots), its statement (the one the
    catalog renders), and a `default` that is not the house's default."""
    from specfirst.compile.standard_form import StandardForm, StandardFormError

    name, unit = str(record.get("id")), str(record.get("unit"))
    try:
        entry = catalog.entry(name)
    except KeyError:
        return [f"{name}: no entry of {catalog.directory.name}"]
    if unit not in entry.units:
        return [f"{name}: the unit {unit} is not one of the entry's ({', '.join(entry.units)})"]
    form = StandardForm(catalog)
    try:
        form.check_value(name, unit, record.get("value") or {})
        statement = form.render(name, unit, record.get("value") or {})
    except StandardFormError as error:
        return [f"{name} ({unit}): its value is not an alternative of the entry: {error}"]
    found = []
    if record.get("statement") != statement:
        found.append(f"{name} ({unit}): the statement is not the one the catalog renders: "
                     f"{statement!r}")
    if record.get("status") == "default" and _normal(record.get("value")) not in {
            _normal(value) for value in house_values(catalog, house, name, unit)}:
        found.append(f"{name} ({unit}): status default, and the value is not the house's "
                     "default")
    return found


def model_records(engine: ard.Engine, analysis: dict, options: dict) -> np.ndarray:
    """The records of the mixed model of an analysis, as models.R takes them.

    Statement 1 of model.mmrm.lsmeans and mmrm_frame in r/specfirstr/R/models.R:
    the records of the analysis set and the data subset with a value of the
    analysis variable, the visit column, the subject key and every factor and
    covariate, in a group of every grouping of the analysis.
    """
    dataset = analysis["dataset"]
    keep = np.ones(engine.table(dataset).rows, dtype=bool)
    if analysis.get("analysisSetId"):
        keep &= engine.where(dataset, engine.event.sets[analysis["analysisSetId"]])
    if analysis.get("dataSubsetId"):
        keep &= engine.where(dataset, engine.event.subsets[analysis["dataSubsetId"]])
    names = [analysis["variable"], engine.subject_key, *options.get("visit", []),
             *options.get("factors", []), *options.get("covariates", [])]
    for name in names:
        values, kind = engine.column(dataset, name)
        keep &= ~np.isnan(values) if kind == "number" else values != ""
    rows = np.flatnonzero(keep)
    for entry in engine.event.groupings_of(analysis):
        inside = np.zeros(len(rows), dtype=bool)
        for _, _, member in engine.members(dataset, engine.event.groupings[entry["groupingId"]],
                                           rows):
            inside |= member
        rows = rows[inside]
    return rows


def last_visit(engine: ard.Engine, analysis: dict, options: dict,
               label: str) -> tuple[str, list[str]]:
    """The last visit of the model records of an analysis and the labels on its records.

    Statement 2 of model.mmrm.lsmeans: the visits in the order of the visit
    column, as numbers when it holds numbers, else by their characters (R's
    radix sort, the order of Python's for ASCII text); `at: last` takes the
    last of them. The visit is given as text, as a group value is (rule I9).
    """
    dataset = analysis["dataset"]
    rows = model_records(engine, analysis, options)
    if not len(rows):
        return "", []
    name = options["visit"][0]
    values = engine.column(dataset, name)[0][rows]
    last = max(values.tolist())
    at_last = rows[values == last]
    labels = engine.text(dataset, label)[at_last]
    return engine.text(dataset, name)[at_last][0], sorted(set(labels.tolist()))


def _last_visit_problems(record: dict, elements: dict, engines: dict) -> tuple[int, list[str]]:
    """The record of the visit of the LS means against the model records it binds."""
    value = record.get("value") or {}
    if value.get("rule") != "last":
        return 0, []
    label, wanted = value.get("label"), value.get("last")
    if not isinstance(label, str) or not isinstance(wanted, str):
        return 0, [f"{LAST_VISIT}: the rule last names no visit (a column `label` and its "
                   f"value `last`)"]
    held, found = 0, []
    for element in record.get("binds") or []:
        if element not in elements:
            continue
        event, binding = elements[element]
        analysis_id = element[len("ars:"):]
        analysis = event.analyses.get(analysis_id)
        engine = engines.get(id(event))
        if analysis is None or engine is None:
            found.append(f"{LAST_VISIT}: {element} is no analysis with data to hold its last "
                         f"visit against")
            continue
        chosen = [options for options in binding.options.get(analysis_id, {}).values()
                  if options.get("visit")]
        if not chosen:
            found.append(f"{LAST_VISIT}: {element} has no option visit")
            continue
        try:
            visit, labels = last_visit(engine, analysis, chosen[0], label)
        except ard.EngineError as error:
            found.append(f"{LAST_VISIT}: {element}: {error}")
            continue
        held += 1
        if labels != [wanted]:
            found.append(f"{LAST_VISIT}: the last visit of the model records of {element} is "
                         f"{chosen[0]['visit'][0]} = {visit!r}, where {label} is "
                         f"{labels or 'missing'}; the decision names {label} = {wanted!r}")
    return held, found


def problems(root: Path, records: list[dict], events: list[tuple[ars.Event, ars.Binding]],
             registry: Registry, engines: list[ard.Engine] | None = None,
             standard: tuple | None = None, columns: set[str] | None = None,
             quotes: Quotes | None = None) -> tuple[list[str], list[str]]:
    """Lines to print and the problems of the records against the events.

    `engines` are the Python engines of the events, in their order, on the
    built ADaM data; the visit of the LS means is held on them (`LAST_VISIT`).
    `standard`: the (catalog, house) the kit names; with it, a record may have
    the ID of an entry of that catalog, and it must fit the entry
    (`catalog_problems`). `columns`: the ADaM columns of the build
    (`adam:<DATASET>.<COLUMN>`), which a record may bind besides the ARS
    elements and outputs of the events. `quotes`: the texts of the kit's
    documents; every citation's quote must stand in its document, and a
    stated record cites at least one (issue #31).

    What this does not hold (ADR-022): a catalog record of the reference
    build is held for its form, its binds, its quotes and its house default,
    not by result: whether the reference build does what the value says is
    std-2's check (PLAN.md section 13.4), not this one.
    """
    lines, found = [], []
    seen: set[str] = set()
    elements: dict[str, tuple[ars.Event, ars.Binding]] = {}
    for event, binding in events:
        for kind in ("analyses", "sets", "subsets", "groupings", "methods"):
            for key in getattr(event, kind):
                elements[f"ars:{key}"] = (event, binding)
        for key in ars.outputs(event):
            elements[f"ars:{key}"] = (event, binding)
    checked = quoted = 0
    unchecked: dict[str, int] = {}  # source that is no document of the kit -> citations
    for record in records:
        name = str(record.get("id"))
        found += [f"{name}: {problem}" for problem in
                  schemas.problems("decision-record", record, root=root)]
        if not name.startswith("custom:"):
            if standard is None:
                found.append(f"{name}: a decision outside catalog@1 has a custom ID (section 10)")
            else:
                found += catalog_problems(record, *standard)
        key = name if name.startswith("custom:") else f"{name} ({record.get('unit')})"
        if key in seen:
            found.append(f"{key}: two records")
        seen.add(key)
        bound = list(record.get("binds") or [])
        found += [f"{name}: binds {element}, which no reporting event of the kit has, nor its "
                  "built ADaM" for element in bound
                  if element not in elements and element not in (columns or set())]
        if quotes is not None:
            cited = record.get("citations") or []
            if record.get("status") == "stated" and not cited:
                found.append(f"{key}: stated, and it cites nothing")
            for citation in cited:
                doc = str(citation.get("doc"))
                if not quotes.knows(doc):
                    # Another source, such as the owner's answers (doc `answers`, ADR-015):
                    # no document of the kit, and no script checks it.
                    if doc in OTHER_SOURCES:
                        unchecked[doc] = unchecked.get(doc, 0) + 1
                    else:
                        found.append(f"{key}: cites {doc}, which is neither a document of the "
                                     "kit, nor the house standard, nor a source the check knows")
                    continue
                quoted += 1
                if not quotes.found(doc, str(citation.get("quote") or "")):
                    found.append(f"{key}: the quote {citation.get('quote')!r} does not stand in "
                                 f"the document {doc}")
        for key, option in PARAMETERS.get(name, {}).items():
            wanted = (record.get("value") or {}).get(key)
            resolved = []
            for element in bound:
                if element not in elements:
                    continue
                event, binding = elements[element]
                for method_id, chosen in binding.options.get(element[len("ars:"):], {}).items():
                    if option in registry.method(method_id).options:
                        resolved.append((element, chosen[option]))
            if not resolved:
                found.append(f"{name}: no analysis it binds has the option {option}")
            for element, value in resolved:
                checked += 1
                if value != wanted:
                    found.append(f"{name}: {element} has {option} = {value!r}, the decision "
                                 f"{key} = {wanted!r}")
    missing = sorted(set(PARAMETERS) - seen)
    found += [f"{name}: no record, and the reporting event needs it" for name in missing]
    held = 0
    for record in records:
        if record.get("id") != LAST_VISIT:
            continue
        if engines is None:
            found.append(f"{LAST_VISIT}: the last visit is held on the built data, and none "
                         f"was handed over")
            continue
        by_event = {id(event): engine for (event, _), engine in zip(events, engines, strict=True)}
        count, more = _last_visit_problems(record, elements, by_event)
        held += count
        found += more
    lines.append(f"decisions: {len(records)} records, {len(seen)} IDs; {checked} options of "
                 f"analyses held against the decisions that set them; the last visit held on "
                 f"the model records of {held} analyses; {quoted} quotes held against their "
                 f"documents; {len(found)} problems")
    if unchecked:
        lines.append("decisions: citations of sources that are no document of the kit, not "
                     "checked by script: " + ", ".join(f"{doc} {count}" for doc, count in
                                                       sorted(unchecked.items())))
    return lines, found
