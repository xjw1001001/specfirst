"""The documents of a kit: protocol and SAP, in standard form and in natural form
(PLAN.md section 6.6, stage S6; docs/decisions/ADR-009.md).

    gold/docs/protocol.md       standard form, document ID protocol-standard
    gold/docs/sap.md            standard form, document ID sap-standard
    inputs/docs/protocol.md     natural form, document ID protocol
    inputs/docs/sap.md          natural form, document ID sap
    gold/docs/natural.json      where every paragraph of the natural form came from
    gold/oracle.yaml            the answers of the oracle (section 11.3)
    gold/summary.md             one page about the kit, for people

Every decision the documents state is stated once, in the document of its
entry (`home_of`). The standard form has one anchored statement per decision
(ADR-004, decision 2): the parser reads it back without a model. The natural
form has the same decisions as paragraphs of ordinary prose, taken from the
store of model text (`specfirst.gen.natural`), in sections of a protocol and
of a SAP, in an order drawn from the seed of the kit, with the design of the
study and with neutral filler. Every paragraph of its body starts with an
anchor `[<section>/p<n>]`.

Tiers (section 6.6), by the number of a kit in its set (`TIER_PLAN`):

    full       every decision of the kit is stated, house defaults included
    standard   the decisions that differ from the house default are stated
    ask        as standard; the decisions of the slice without a house
               default are left out and the oracle answers them

A stated decision cites the standard-form statement first, then the natural
paragraph. A default cites the house standard. An asked decision cites
nothing; `gold/oracle.yaml` holds its answer.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.compile.standard_form import StandardForm
from specfirst.gen import design as designs
from specfirst.gen import natural, sdtm
from specfirst.gen.rng import Stream

TIERS = ("full", "standard", "ask")
# The tier of the documents of the kits of a set, by their number (ADR-009, decision 4).
TIER_PLAN = ("full", "standard", "full", "ask", "standard", "full", "ask", "standard", "full",
             "standard")
NATURAL = {"protocol": "inputs/docs/protocol.md", "sap": "inputs/docs/sap.md"}
STANDARD = {"protocol": "gold/docs/protocol.md", "sap": "gold/docs/sap.md"}
RECORD = "gold/docs/natural.json"
ORACLE = "gold/oracle.yaml"
SUMMARY = "gold/summary.md"
FORMAT = 1
TITLES = {"protocol": "Clinical study protocol", "sap": "Statistical analysis plan"}
FILLER_SECTIONS = 2  # filler sections per natural document


def standard_id(doc: str) -> str:
    return f"{doc}-standard"


def tier_of(seed: str, number: int | None) -> str:
    """The tier of a kit: by its number in a set, or full or standard drawn from its seed."""
    if number is not None:
        return TIER_PLAN[(number - 1) % len(TIER_PLAN)]
    return ("full", "standard")[Stream(seed, "documents", "tier").below(2)]


# Where a decision is stated: the document, and the section of its natural form.
_PROTOCOL_SECTIONS = {"pop.randomized.rule": "sets", "pop.safety.rule": "sets",
                      "pop.efficacy.rule": "sets", "ae.related.values": "ae"}
_SAP_SECTIONS = {
    "pop.safety.grouping": "groups", "disp.status.record": "disposition",
    "trt.planned.source": "treatment", "trt.actual.source": "treatment",
    "trt.start.source": "treatment", "trt.end.source": "treatment",
    "trt.date.imputation": "treatment", "date.studyday.origin": "treatment",
    "ae.start.imputation": "ae", "ae.teae.start": "ae", "ae.teae.end": "ae",
    "demo.age.groups": "baseline", "demo.race.pooling": "baseline",
    "demo.baseline.record": "baseline", "demo.bmi.rule": "baseline",
    "tfl.output.include": "outputs",
}
# The sections of a natural document: key, heading, parent. Empty sections are left out.
SECTIONS = {
    "protocol": (("synopsis", "Synopsis", None), ("design", "Study design", None),
                 ("treatment", "Study treatment", None), ("assessments", "Assessments", None),
                 ("vitals", "Vital signs", "assessments"),
                 ("ae", "Adverse events", "assessments"),
                 ("disposition", "Disposition", "assessments"),
                 ("statistics", "Statistical considerations", None),
                 ("sets", "Analysis sets", "statistics")),
    "sap": (("intro", "Introduction", None), ("groups", "Treatment groups", None),
            ("treatment", "Study treatment and study days", None),
            ("disposition", "Disposition", None), ("ae", "Adverse events", None),
            ("baseline", "Baseline characteristics", None),
            ("outputs", "Planned outputs", None),
            ("tables", "Summary of adverse events", "outputs")),
}
# The neutral filler sections a rewriter writes once (specfirst.gen.natural, filler).
FILLER = {
    "protocol": ("Background", "Ethics", "Confidentiality", "Monitoring", "Publication"),
    "sap": ("Data handling", "Software", "Quality control", "Changes to the planned analyses",
            "Interim analyses"),
}


def home_of(entry_id: str) -> tuple[str, str]:
    """The document and the section of the natural form that state a decision."""
    if entry_id in _PROTOCOL_SECTIONS:
        return "protocol", _PROTOCOL_SECTIONS[entry_id]
    if entry_id in _SAP_SECTIONS:
        return "sap", _SAP_SECTIONS[entry_id]
    if entry_id.startswith("tfl."):
        return "sap", "tables"
    raise KeyError(f"no document states the decision {entry_id}")


def filler_wanted() -> list[dict]:
    """The filler paragraphs the store needs, one per heading."""
    return [{"key": f"filler-{doc}-{index}", "document": doc, "heading": heading}
            for doc, headings in FILLER.items() for index, heading in enumerate(headings, 1)]


# ---- statuses ------------------------------------------------------------------------------


def without_default(catalog: catalogs.Catalog, house: houses.House, listed: list[dict],
                    units: tuple[str, ...]) -> set[tuple[str, str]]:
    """The decisions of the scope that have no house default."""
    base = {(r["id"], r["unit"]) for r in houses.default_decisions(catalog, house)}
    return {(r["id"], r["unit"]) for r in listed
            if r["unit"] in units and (r["id"], r["unit"]) not in base}


def statuses(catalog: catalogs.Catalog, house: houses.House, listed: list[dict], tier: str,
             units: tuple[str, ...]) -> dict[tuple[str, str], str]:
    """stated, default or asked, for every decision of a vector, under a tier."""
    if tier not in TIERS:
        raise ValueError(f"a tier is one of {', '.join(TIERS)}, not '{tier}'")
    base = {(r["id"], r["unit"]): r["value"] for r in houses.default_decisions(catalog, house)}
    asked = without_default(catalog, house, listed, units) if tier == "ask" else set()
    found = {}
    for record in listed:
        key = (record["id"], record["unit"])
        if key in asked:
            found[key] = "asked"
        elif tier == "full" or base.get(key) != record["value"]:
            found[key] = "stated"
        else:
            found[key] = "default"
    return found


# ---- the design, in words ------------------------------------------------------------------

_FREQUENCY = {"QD": "once daily", "BID": "twice daily", "QW": "once weekly"}
_SETS = {"RANDOMIZED": "the randomized set", "SAFETY": "the safety set",
         "EFFICACY": "the efficacy-evaluable set"}


def _series(items: list[str]) -> str:
    if len(items) <= 2:
        return " and ".join(items)
    return ", ".join(items[:-1]) + ", and " + items[-1]


def design_paragraphs(design: dict) -> dict[str, list[str]]:
    """The paragraphs of the protocol that describe the design, by section. They state
    no decision; a reader needs them (the order of the arms above all, ADR-007)."""
    body = design["studyDesign"]
    study = design["study"]
    population = body["population"]
    arms = designs.arms(design)
    ratio = ":".join(str(part) for part in body["randomization"]["allocationRatio"])
    phase = " ".join(word.upper() if set(word) <= set("ivx") else word
                     for word in study["studyPhase"].lower().split())
    synopsis = (f"This protocol describes study {designs.study_id(design)}, \"{study['label']}\". "
                f"It is a {phase} with a {body['model'].lower()} design, "
                f"{body['blindingSchema'].lower()}, and plans to enrol "
                f"{population['plannedEnrollmentNumber']} subjects aged "
                f"{population['plannedAge']['minValue']} to "
                f"{population['plannedAge']['maxValue']} years.")
    listing = [f"Subjects are randomized to {len(arms)} arms in the ratio {ratio}. The protocol "
               "lists the arms in this order:"]
    for arm in arms:
        item = designs.intervention(design, arm["studyInterventionId"])
        listing.append(
            f"- Arm {arm['name']} ({arm['label']}): {arm['description']}; study treatment "
            f"{sdtm.treatment_name(design, arm['studyInterventionId'])}, "
            f"{arm['dose']:g} {item['unit']} per dose; {arm['plannedNumber']} subjects planned.")
    visits = [f"{encounter['label']} (day {encounter['plannedDay']})"
              for encounter in body["encounters"]]
    schedule = f"The schedule of visits is {_series(visits)}."
    if (design.get("collection") or {}).get("visits", {}).get("unscheduled"):
        schedule += " Unscheduled visits may take place at any time."
    interventions = body["studyInterventions"]
    first = interventions[0]
    treatment = (f"Study treatment is given as {first['doseForm'].lower()}s by the "
                 f"{first['route'].lower()} route, "
                 f"{_FREQUENCY.get(first['frequency'], first['frequency'])}, and its intake is "
                 "recorded on exposure records.")
    if (design.get("collection") or {}).get("exposure", {}).get("firstDoseTime"):
        treatment += " The time of the first dose is recorded."
    all_visits = [encounter["name"] for encounter in body["encounters"]]
    names = {encounter["name"]: encounter["label"] for encounter in body["encounters"]}
    tests = []
    for activity in body.get("activities") or []:
        for test in activity.get("tests") or []:
            at = test.get("encounterIds") or []
            where = "at every visit" if at == all_visits else "at " + _series(
                [names[name] for name in at])
            tests.append(f"{test['test']} ({test['testCode']}, {test['unit']}) {where}")
    vitals = [f"Vital signs are measured as follows: {'; '.join(tests)}."] if tests else []
    collection = design.get("collection") or {}
    events = collection.get("adverseEvents") or {}
    adverse = []
    if events:
        adverse.append(
            "Adverse events are recorded throughout the study and coded with the dictionary "
            f"{events['dictionary']}. For each event the investigator assesses its relation to "
            "study treatment on the scale " + ", ".join(f'"{value}"' for value in
                                                        events["causality"]) + ".")
    disposition = []
    sub = (collection.get("disposition") or {}).get("subcategories") or {}
    if sub:
        disposition.append(
            "The end of study treatment and the end of participation in the study are each "
            f"recorded as a disposition event, with the subcategories \"{sub['treatment']}\" "
            f"and \"{sub['study']}\" respectively.")
    sets = [_SETS[p["name"]] for p in body.get("analysisPopulations") or [] if p["name"] in _SETS]
    statistics = [f"The analyses use {_series(sets)}."] if sets else []
    return {"synopsis": [synopsis], "design": ["\n".join(listing), schedule],
            "treatment": [treatment], "vitals": vitals, "ae": adverse,
            "disposition": disposition, "sets": statistics}


def sap_paragraphs(design: dict, tier: str, house: houses.House) -> dict[str, list[str]]:
    intro = (f"This statistical analysis plan describes the analyses of study "
             f"{designs.study_id(design)}. The design of the study, its arms in the order of the "
             "protocol and its schedule of visits are those of the protocol.")
    intro += (" This plan and the protocol together state every convention that the "
              "analyses follow." if tier == "full" else
              f" Where neither this plan nor the protocol states a convention, the house "
              f"standard {house.label} applies.")
    return {"intro": [intro]}


# ---- writing the documents -----------------------------------------------------------------


def write(catalog: catalogs.Catalog, house: houses.House, design: dict, listed: list[dict],
          tier: str, units: tuple[str, ...], stream: Stream, kit_dir: Path,
          store: natural.Store | None = None) -> tuple[list[dict], dict]:
    """Write the documents of a kit for a decision vector. Returns the decision records
    with status, class, statement and citations, and what the manifest says of them.

    `listed` holds `id`, `unit` and `value` of every decision of the kit.
    """
    store = store or natural.Store.load()
    form = StandardForm(catalog)
    state = statuses(catalog, house, listed, tier, units)
    base = {(r["id"], r["unit"]): r for r in houses.default_decisions(catalog, house)}
    statements = {(r["id"], r["unit"]): form.render(r["id"], r["unit"], r["value"])
                  for r in listed}
    stated = [r for r in listed if state[(r["id"], r["unit"])] == "stated"]
    study = designs.study_id(design)

    # The standard form: one document per home, read back by the parser.
    standard_cite: dict[tuple[str, str], dict] = {}
    texts: dict[str, str] = {}
    for doc in ("protocol", "sap"):
        mine = [r for r in stated if home_of(r["id"])[0] == doc]
        preface = (f"This document states, one statement each, the decisions of study {study} "
                   f"that its {TITLES[doc].lower()} states, in the standard form of the decision "
                   "catalog. It is gold: a reader gets the natural form.",)
        text = form.render_document(standard_id(doc), f"{TITLES[doc]} of study {study}: "
                                    "standard form", mine, preface)
        name, parsed = form.parse_document(text)
        if name != standard_id(doc) or {(p["id"], p["unit"]): p["value"] for p in parsed} != {
                (r["id"], r["unit"]): r["value"] for r in mine}:
            raise ValueError(f"{doc}: the standard form does not read back as its decisions")
        for item in parsed:
            standard_cite[(item["id"], item["unit"])] = {
                "doc": standard_id(doc), "anchor": item["anchor"], "quote": item["statement"]}
        texts[STANDARD[doc]] = text

    # The natural form.
    natural_cite: dict[tuple[str, str], dict] = {}
    record = {"natural": FORMAT, "tier": tier, "documents": {}}
    sources = {"model": 0, "template": 0, "missing": 0}
    fixed = {"protocol": design_paragraphs(design), "sap": sap_paragraphs(design, tier, house)}
    filler = store.accepted_filler()
    for doc in ("protocol", "sap"):
        draw = stream.child(doc)
        by_section: dict[str, list[dict]] = {key: [] for key, _, _ in SECTIONS[doc]}
        for section, paragraphs in fixed[doc].items():
            by_section[section] += [{"kind": "design", "text": text} for text in paragraphs]
        mine = [r for r in stated if home_of(r["id"])[0] == doc]
        decided: dict[str, list[dict]] = {}
        for item in mine:
            key = (item["id"], item["unit"])
            accepted = store.accepted(statements[key])
            if accepted is not None:
                text, source = accepted["text"], ("template" if accepted["by"] == "template"
                                                  else "model")
                attempt = accepted["n"]
            else:
                text = natural.phrasing(catalog, item["id"], item["unit"], item["value"])
                source, attempt = "missing", None
            sources[source] += 1
            decided.setdefault(home_of(item["id"])[1], []).append({
                "kind": "decision", "text": text, "entry": item["id"], "unit": item["unit"],
                "statement_key": natural.key_of(statements[key]), "source": source,
                "attempt": attempt})
        for section, items in decided.items():
            by_section[section] += draw.child(section).shuffled(
                sorted(items, key=lambda one: (one["entry"], one["unit"])))
        named = [item["key"] for item in filler_wanted() if item["document"] == doc]
        by_key = {one["key"]: one for one in filler}
        mine_filler = [by_key[key] for key in named if key in by_key]
        chosen = draw.child("filler").sample(mine_filler, min(FILLER_SECTIONS, len(mine_filler)))
        sections = list(SECTIONS[doc]) + [
            (f"filler{index}", one["heading"], None) for index, one in enumerate(chosen)]
        for index, one in enumerate(chosen):
            by_section[f"filler{index}"] = [{"kind": "filler", "text": one["text"],
                                             "filler_key": one["key"]}]
        text, placed = _natural_text(doc, design, sections, by_section)
        texts[NATURAL[doc]] = text
        for item in placed:
            item["sha256"] = natural.sha256_text(item.pop("body"))
            if item["kind"] == "decision":
                natural_cite[(item["entry"], item["unit"])] = {
                    "doc": doc, "anchor": item["anchor"], "quote": item.pop("quote")}
            else:
                item.pop("quote")
        record["documents"][doc] = {"file": NATURAL[doc], "sha256": natural.sha256_text(text),
                                    "paragraphs": placed}

    # The records.
    records = []
    asked = []
    for item in listed:
        key = (item["id"], item["unit"])
        status = state[key]
        if status == "default":
            default = base[key]
            records.append({name: default[name] for name in
                            ("id", "unit", "value", "status", "class", "statement",
                             "citations")})
            continue
        found = {"id": item["id"], "unit": item["unit"], "value": item["value"],
                 "status": status, "statement": statements[key]}
        if status == "asked":
            found["class"] = "study_input"
            asked.append({"decision": item["id"], "unit": item["unit"], "value": item["value"],
                          "answer": statements[key]})
        else:
            found["class"] = "document_rule"
            found["citations"] = [standard_cite[key], natural_cite[key]]
        records.append(found)

    for relative, text in texts.items():
        path = kit_dir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="ascii", newline="\n")
    _write_json(kit_dir / RECORD, record)
    oracle = {"oracle": FORMAT, "rule": "The oracle answers a decision only when it has no "
              "house default and the documents do not state it (PLAN.md section 11.3).",
              "answers": asked}
    (kit_dir / ORACLE).write_text(yaml.safe_dump(oracle, sort_keys=False, width=10_000),
                                  encoding="ascii", newline="\n")
    manifest = {"tier": tier,
                "natural": dict(NATURAL), "standard": dict(STANDARD),
                "record": RECORD, "oracle": ORACLE, "summary": SUMMARY,
                "stated": sum(1 for s in state.values() if s == "stated"),
                "asked": [a["decision"] for a in asked],
                "paragraphs": sources}
    return records, manifest


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=1, sort_keys=True, ensure_ascii=True) + "\n",
                    encoding="ascii", newline="\n")


def _natural_text(doc: str, design: dict, sections: list[tuple],
                  by_section: dict[str, list[dict]]) -> tuple[str, list[dict]]:
    """The Markdown of a natural document, and every paragraph with its anchor."""
    study = design["study"]
    lines = [f"# {TITLES[doc]}", "", f"Study {designs.study_id(design)}: {study['label']}", "",
             f"Document ID: {doc}", ""]
    placed: list[dict] = []
    children: dict[str, list[str]] = {}
    for key, _, parent in sections:
        if parent:
            children.setdefault(parent, []).append(key)

    def filled(key: str) -> bool:
        return bool(by_section.get(key)) or any(filled(child) for child in children.get(key, []))

    top = 0
    for key, heading, parent in sections:
        if parent or not filled(key):
            continue
        top += 1
        _section(lines, placed, f"{top}", "##", heading, by_section.get(key, []))
        sub = 0
        for child_key, child_heading, child_parent in sections:
            if child_parent == key and filled(child_key):
                sub += 1
                _section(lines, placed, f"{top}.{sub}", "###", child_heading,
                         by_section.get(child_key, []))
    return "\n".join(lines), placed


def _section(lines: list[str], placed: list[dict], number: str, mark: str, heading: str,
             paragraphs: list[dict]) -> None:
    lines += [f"{mark} {number} {heading}", ""]
    for index, paragraph in enumerate(paragraphs, start=1):
        anchor = f"{number}/p{index}"
        lines += [f"[{anchor}] {paragraph['text']}", ""]
        placed.append({"anchor": anchor, **{k: v for k, v in paragraph.items() if k != "text"},
                       "body": paragraph["text"], "quote": paragraph["text"]})


# ---- reading the documents of a written kit --------------------------------------------------


def read_texts(kit_dir: Path) -> dict[str, str]:
    """The four documents of a kit, by document ID."""
    found = {}
    for doc in ("protocol", "sap"):
        found[doc] = (kit_dir / NATURAL[doc]).read_text(encoding="ascii")
        found[standard_id(doc)] = (kit_dir / STANDARD[doc]).read_text(encoding="ascii")
    return found


def read_record(kit_dir: Path) -> dict:
    with open(kit_dir / RECORD, encoding="ascii") as handle:
        return json.load(handle)


def read_oracle(kit_dir: Path) -> dict:
    with open(kit_dir / ORACLE, encoding="ascii") as handle:
        return yaml.safe_load(handle)


def paragraphs(text: str) -> dict[str, str]:
    """The paragraphs of a natural document, by anchor: the text after the anchor, with
    the lines that follow it up to the next empty line."""
    found: dict[str, str] = {}
    lines = text.split("\n")
    for number, line in enumerate(lines):
        if line.startswith("[") and "] " in line:
            anchor = line[1:line.index("] ")]
            taken = [line[line.index("] ") + 2:]]
            for later in lines[number + 1:]:
                if not later.strip():
                    break
                taken.append(later)
            found[anchor] = "\n".join(taken)
    return found


# ---- the summary page ----------------------------------------------------------------------

MAX_LINES, MAX_WIDTH = 60, 100
_TWIN = {"separated": "yes", "unseparated": "no"}


def summary(manifest: dict, design: dict, records: list[dict], visible: list[str],
            twin: list[str]) -> str:
    """One page about a kit, for people (ADR-009, decision 9)."""
    documents = manifest["documents"]
    sources = documents["paragraphs"]
    lines = [f"# Kit {manifest['id']}: summary", "",
             f"Study {manifest['study']['id']}, archetype {manifest['archetype']}, split "
             f"{manifest['split']}, generator {manifest['generator']}.",
             "Arms in protocol order: " + ", ".join(
                 f"{arm['name']} ({arm['label']}, dose {arm['dose']:g})"
                 for arm in designs.arms(design)) + ".",
             f"Documents: tier {documents['tier']}; {documents['stated']} decisions stated, "
             f"{len(documents['asked'])} asked; natural paragraphs from the model "
             f"{sources['model']}, phrasing template {sources['template']}, missing "
             f"{sources['missing']}.",
             f"Probes: {len(twin)} in the twin, {len(visible)} of them in the visible data.", "",
             "Where: the natural paragraph (its standard-form anchor). Twin: separated there.",
             "", "| Decision | Value | Status | Where | Twin |", "| --- | --- | --- | --- | --- |"]
    for record in records:
        cited = record.get("citations") or []
        where = (f"{cited[1]['doc']} {cited[1]['anchor']} ({cited[0]['anchor']})"
                 if len(cited) > 1 else f"{cited[0]['doc']} {cited[0]['anchor']}"
                 if cited else "")
        unit = f" ({record['unit']})" if record["id"] == "tfl.output.include" else ""
        lines.append(f"| {record['id']}{unit} | {record['value']['rule']} | {record['status']} | "
                     f"{where or 'oracle'} | {_TWIN.get(record.get('identifiable'), '-')} |")
    lines += ["", "Visible probes: " + ", ".join(visible) + "."]
    wrapped = []
    for line in lines:
        while len(line) > MAX_WIDTH and not line.startswith("|"):
            cut = line.rfind(" ", 0, MAX_WIDTH)
            wrapped.append(line[:cut])
            line = line[cut + 1:]
        wrapped.append(line)
    return "\n".join(wrapped) + "\n"


def summary_problems(text: str, records: list[dict]) -> list[str]:
    """Why a summary is not one page that names every decision of its kit."""
    lines = text.rstrip("\n").split("\n")
    problems = []
    if len(lines) > MAX_LINES:
        problems.append(f"the summary has {len(lines)} lines, more than {MAX_LINES}")
    long = [line for line in lines if len(line) > MAX_WIDTH]
    if long:
        problems.append(f"{len(long)} lines of the summary are too long")
    for record in records:
        unit = f" ({record['unit']})" if record["id"] == "tfl.output.include" else ""
        if not any(line.startswith(f"| {record['id']}{unit} |") for line in lines):
            problems.append(f"the summary does not name {record['id']}{unit}")
    return problems


# ---- the checks of the documents of a written kit --------------------------------------------

CHECKS = ("parser", "slots", "readback", "layout", "tiers", "citations", "probes", "summary")


def problems(catalog: catalogs.Catalog, house: houses.House, kit_dir: Path, manifest: dict,
             records: list[dict], design: dict, log: list[dict],
             store: natural.Store | None = None) -> tuple[dict[str, list[str]], dict]:
    """Why the documents of a written kit are not what section 6.6 asks, by check, and
    what was counted.

    parser     every standard-form document parses; it states exactly the
               records that are stated in it, at the anchors they cite; with
               the house standard and the oracle every decision is recovered
    slots      every decision paragraph keeps the tokens of its statement
    readback   every decision paragraph is a text that the store read back as
               the alternative of its decision; every filler paragraph was read
               back as stating nothing
    layout     the record of the natural form names every paragraph with its
               hash; the design paragraphs are those of the design
    tiers      the statuses and classes of the tier; the oracle answers
               exactly the asked decisions
    citations  every quote stands inside the span of its anchor
    probes     the kit lists the probes of its log by dataset, and every
               visible probe is found in the visible data
    summary    one page that names every decision
    """
    from specfirst.compile.standard_form import StandardFormError
    from specfirst.gen import present, study
    from specfirst.score.reading import Documents

    store = store or natural.Store.load()
    units = tuple(manifest.get("units") or ())
    found: dict[str, list[str]] = {name: [] for name in CHECKS}
    counted = {"decisions": len(records), "recovered": 0, "paragraphs": 0, "filler": 0,
               "citations": 0, "visible probes": 0}
    try:
        texts = read_texts(kit_dir)
        record = read_record(kit_dir)
        oracle = read_oracle(kit_dir)
    except (OSError, ValueError, yaml.YAMLError) as error:
        found["layout"].append(f"the documents cannot be read: {error}")
        return found, counted
    by_key = {(r["id"], r["unit"]): r for r in records}
    form = StandardForm(catalog)

    # parser
    parsed_keys: dict[tuple[str, str], str] = {}
    for doc in ("protocol", "sap"):
        try:
            name, parsed = form.parse_document(texts[standard_id(doc)])
        except StandardFormError as error:
            found["parser"].append(f"{STANDARD[doc]}: {error}")
            continue
        if name != standard_id(doc):
            found["parser"].append(f"{STANDARD[doc]}: its ID is {name}, not {standard_id(doc)}")
        for item in parsed:
            key = (item["id"], item["unit"])
            parsed_keys[key] = doc
            gold = by_key.get(key)
            wanted = {"doc": standard_id(doc), "anchor": item["anchor"],
                      "quote": item["statement"]}
            if gold is None or gold["status"] != "stated" or gold["value"] != item["value"]:
                found["parser"].append(f"{STANDARD[doc]} [{item['anchor']}] states {key[0]} "
                                       f"as {item['value']}; the record is "
                                       f"{(gold or {}).get('status')} {(gold or {}).get('value')}")
            elif (gold.get("citations") or [None])[0] != wanted:
                found["parser"].append(f"{key[0]}: the record does not cite "
                                       f"{wanted['doc']}#{wanted['anchor']} first")
    defaults = {(r["id"], r["unit"]): r["value"] for r in houses.default_decisions(catalog, house)}
    answers = {(a["decision"], a["unit"]): a for a in oracle.get("answers") or []}
    for key, gold in by_key.items():
        if gold["status"] == "stated":
            ok = parsed_keys.get(key) == home_of(key[0])[0]
        elif gold["status"] == "default":
            ok = defaults.get(key) == gold["value"] and key not in parsed_keys
        else:
            ok = key in answers and answers[key]["value"] == gold["value"]
        counted["recovered"] += ok
        if not ok:
            found["parser"].append(f"{key[0]} ({key[1]}, {gold['status']}): not recovered from "
                                   "the documents, the house standard and the oracle")

    # layout, slots and read-back
    stated = {key for key, r in by_key.items() if r["status"] == "stated"}
    placed: dict[tuple[str, str], tuple[str, str]] = {}
    tier = (manifest.get("documents") or {}).get("tier")
    fixed = {"protocol": design_paragraphs(design), "sap": sap_paragraphs(design, tier, house)}
    filler = {one["key"]: one for one in store.accepted_filler()}
    for doc in ("protocol", "sap"):
        listed = (record.get("documents") or {}).get(doc) or {}
        text = texts[doc]
        anchored = paragraphs(text)
        if listed.get("sha256") != natural.sha256_text(text):
            found["layout"].append(f"{NATURAL[doc]}: not the text natural.json names")
        if [item["anchor"] for item in listed.get("paragraphs") or []] != list(anchored):
            found["layout"].append(f"{NATURAL[doc]}: its anchors are not those of natural.json")
        if f"Document ID: {doc}" not in text.split("\n"):
            found["layout"].append(f"{NATURAL[doc]}: no line 'Document ID: {doc}'")
        designed = [body for bodies in fixed[doc].values() for body in bodies]
        fillers = sum(1 for item in listed.get("paragraphs") or [] if item["kind"] == "filler")
        if fillers != FILLER_SECTIONS:
            found["layout"].append(f"{NATURAL[doc]}: {fillers} filler paragraphs, the generator "
                                   f"writes {FILLER_SECTIONS}")
        for item in listed.get("paragraphs") or []:
            body = anchored.get(item["anchor"])
            if body is None:
                continue
            if item.get("sha256") != natural.sha256_text(body):
                found["layout"].append(f"{doc}#{item['anchor']}: not the text natural.json "
                                       "hashes")
            if item["kind"] == "design":
                if body not in designed:
                    found["layout"].append(f"{doc}#{item['anchor']}: a design paragraph that "
                                           "the design does not give")
            elif item["kind"] == "filler":
                counted["filler"] += 1
                stored = filler.get(item.get("filler_key"))
                if stored is None or stored["text"] != body:
                    found["readback"].append(f"{doc}#{item['anchor']}: filler that the store "
                                             "did not read back as stating nothing")
            elif item["kind"] == "decision":
                key = (item.get("entry"), item.get("unit"))
                if key not in stated or home_of(key[0])[0] != doc:
                    found["layout"].append(f"{doc}#{item['anchor']}: a paragraph of {key[0]}, "
                                           f"which is not stated in {doc}")
                    continue
                counted["paragraphs"] += 1
                if key in placed:
                    found["layout"].append(f"{key[0]}: two paragraphs")
                placed[key] = (doc, item["anchor"])
                if item.get("source") == "missing":
                    found["readback"].append(f"{doc}#{item['anchor']} ({key[0]}): the store has "
                                             "no accepted text for its statement")
                for problem in natural.paragraph_problems(catalog, store, by_key[key], body):
                    kind = "slots" if problem.startswith("slot check") else "readback"
                    found[kind].append(f"{doc}#{item['anchor']} ({key[0]}): {problem}")
            else:
                found["layout"].append(f"{doc}#{item['anchor']}: unknown kind {item['kind']}")
    for key in sorted(stated - set(placed)):
        found["layout"].append(f"{key[0]} ({key[1]}): stated, and no natural paragraph states it")
    for key, (doc, anchor) in placed.items():
        cited = by_key[key].get("citations") or []
        if len(cited) < 2 or (cited[1]["doc"], cited[1]["anchor"]) != (doc, anchor):
            found["layout"].append(f"{key[0]}: the record does not cite {doc}#{anchor} second")

    # tiers
    if tier not in TIERS:
        found["tiers"].append(f"kit.yaml names no tier of the documents ({tier!r})")
    else:
        listed = [{"id": r["id"], "unit": r["unit"], "value": r["value"]} for r in records]
        wanted = statuses(catalog, house, listed, tier, units)
        for key, gold in by_key.items():
            if gold["status"] != wanted[key]:
                found["tiers"].append(f"{key[0]} ({key[1]}): {gold['status']}, the tier "
                                      f"{tier} asks {wanted[key]}")
            klass = {"stated": "document_rule", "default": "house_default",
                     "asked": "study_input"}.get(gold["status"])
            if gold.get("class") != klass:
                found["tiers"].append(f"{key[0]}: class {gold.get('class')}, not {klass}")
            docs = [c["doc"] for c in gold.get("citations") or []]
            if gold["status"] == "default" and docs != [houses.DOCUMENT_ID]:
                found["tiers"].append(f"{key[0]}: a default that cites {docs}")
            if gold["status"] == "asked" and docs:
                found["tiers"].append(f"{key[0]}: an asked decision that cites {docs}")
        asked = {key for key, gold in by_key.items() if gold["status"] == "asked"}
        if tier == "ask" and not asked:
            found["tiers"].append("a kit of the ask demo asks nothing")
        if set(answers) != asked:
            found["tiers"].append(f"the oracle answers {sorted(answers)}, the asked decisions "
                                  f"are {sorted(asked)}")
        for key in asked & set(answers):
            if answers[key]["answer"] != by_key[key]["statement"]:
                found["tiers"].append(f"{key[0]}: the oracle's answer is not its statement")
        noted = manifest.get("documents") or {}
        if noted.get("asked") != [a["decision"] for a in oracle.get("answers") or []] or \
                noted.get("stated") != len(stated):
            found["tiers"].append("kit.yaml counts other stated or asked decisions")

    # citations
    shelf = Documents({**texts, houses.DOCUMENT_ID: (kit_dir / "inputs" / "house" /
                                                     "STANDARD.md").read_text(encoding="ascii")})
    for gold in records:
        for citation in gold.get("citations") or []:
            counted["citations"] += 1
            if not shelf.in_span(citation["doc"], citation["anchor"], citation["quote"]):
                found["citations"].append(f"{gold['id']} ({gold['unit']}): the quote does not "
                                          f"stand at {citation['doc']}#{citation['anchor']}")

    # probes
    lists = {which: sorted({line["probe"] for line in log if line["data"] == which})
             for which in ("visible", "twin")}
    if manifest.get("probes") != lists:
        found["probes"].append("kit.yaml does not list the probes of the log by dataset")
    if not lists["visible"]:
        found["probes"].append("the kit has no visible probe")
    _, _, missing = present.coverage(catalog, design, log, study.read_tables(kit_dir, "visible"),
                                     "visible")
    found["probes"] += [f"visible data: {problem}" for problem in missing
                        if problem.startswith("probe ")]
    counted["visible probes"] = len(lists["visible"])

    # summary
    try:
        found["summary"] = summary_problems((kit_dir / SUMMARY).read_text(encoding="ascii"),
                                            records)
    except OSError as error:
        found["summary"] = [f"no summary: {error}"]
    return found, counted
