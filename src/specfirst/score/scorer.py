"""Score a candidate on a case: reading score, build score, attribution (PLAN.md section 9).

A case is one study to score on: its gold decision records, its datasets
(the visible data and the twin), the arms of its design, its documents and
the units that are scored. A candidate is a list of decision records, with
the questions it asked and what it listed as unmapped.

The arms that need no reader (ADR-005, decision 3):

    S   the standard alone: no record. Every decision of the scope takes
        its house default; one without a default stays open, and what the
        build needs it for is pending (ADR-014): left out of the build, and
        its gold cells counted apart, neither right nor wrong.
    C   the control of section 9.3: the parser on the standard-form
        document that `specfirst render` writes for the stated decisions,
        and on the house standards document for the defaults. It must
        score 100%; if it does not, the kit or the scorer is wrong. A case
        that ships standard-form documents (a generated kit: the protocol
        and the SAP in gold/docs/) is read from them. A decision that no
        document states and that has no house default is asked, and the
        oracle of the case answers it (section 11.3; ADR-009, decision 4).

Stages (ADR-005, decision 2). In the chain (`C`) both vectors are built
from SDTM. In stage `T` both are built on the ADaM datasets of gold: the
table decisions alone are read, and no analysis dataset can differ.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable
from dataclasses import dataclass, field

from specfirst.compile import house as houses
from specfirst.compile.standard_form import StandardForm, decision_record
from specfirst.machine.canonical import content_hash
from specfirst.score import attribute, build, reading
from specfirst.score.candidate import Arms, Build, Data, Hooks, Key, Machine, pending_cells, vector

STAGES = ("C", "T")
CONTROL_DOCUMENT, CONTROL_TITLE = "sap", "Standard form"


class ScoreError(RuntimeError):
    """The case cannot be scored: its gold does not build."""


@dataclass(frozen=True)
class Case:
    id: str
    units: tuple[str, ...]  # the units that are scored
    gold: list[dict]  # gold decision records, of every unit the build needs
    # The arms of the protocol for a decision vector: a decision can change the text
    # that names an arm in a treatment column, never the arms (ADR-007, decision 2).
    arms: Callable[[list[dict]], Arms]
    data: dict[str, Data]  # visible, twin -> the dataset
    documents: reading.Documents = field(default_factory=reading.Documents)
    stage: str = "C"
    # The IDs of the standard-form documents of the study, when the case ships them.
    standard_form: str | tuple[str, ...] | None = None
    # The other values a study of this design can decide for a decision (a kit knows
    # its design); None: the planted defects take an alternative without a slot.
    variants: Callable[[Key], list[dict]] | None = None
    # What the oracle answers when asked (section 11.3): decision -> value.
    oracle: dict[Key, dict] = field(default_factory=dict)

    def gold_vector(self) -> list[dict]:
        return [{"id": r["id"], "unit": r["unit"], "value": r["value"]} for r in self.gold
                if r.get("value") is not None]


@dataclass
class Result:
    case: str
    arm: str
    stage: str
    reading: reading.Reading
    builds: dict[str, build.BuildScore]
    owners: dict[str, list[attribute.Owner]]
    axes: dict[str, list[attribute.AxisOwner]]
    # Decisions with a wrong value that own no wrong cell and no axis. `silent`: the
    # gold vector with this one value gives the gold tables on every dataset, so these
    # data cannot show the error (docs/state/gen.md; section 9.3). `behind`: alone it
    # changes cells (their number per dataset); here another owner stands before it.
    silent: list[Key] = field(default_factory=list)
    behind: dict[Key, dict[str, int]] = field(default_factory=dict)
    # Decisions without a value that the build needs (ADR-014): per dataset, the gold
    # cells that wait for each. Such a decision is neither silent nor behind.
    pending: dict[Key, dict[str, int]] = field(default_factory=dict)

    @property
    def perfect(self) -> bool:
        return self.reading.perfect and all(score.perfect for score in self.builds.values())


def staged(machine: Machine, case: Case, name: str) -> tuple[Data, Build]:
    """The dataset both vectors are built on in the stage of the case, and the gold build."""
    data = case.data[name]
    records = case.gold_vector()
    gold = machine.build(records, data, case.arms(records))
    if not gold.ok or gold.not_produced:
        raise ScoreError(f"{case.id}, {name}: the gold decisions do not build: "
                         f"{gold.failure or gold.not_produced}")
    if case.stage == "T":
        # The ADaM of gold is named by the gold vector: a build is known by the name
        # of its data, and two gold vectors on one dataset give two sets of ADaM.
        data = Data(f"{data.name}/T/{content_hash(records)[:12]}", adam=gold.adam)
        gold = machine.build(records, data, case.arms(records))
    return data, gold


def run(machine: Machine, case: Case, candidate: list[dict], arm: str = "R",
        asked: set[Key] | None = None, unmapped: set[tuple[str, str]] | None = None,
        hooks: Hooks | None = None, documents: reading.Documents | None = None,
        prove: bool = True) -> Result:
    """Score the records of a candidate on a case.

    `hooks` plants a defect in the candidate's builds. With `prove`, every
    claim of the attribution is run: the candidate is built again with
    decisions at their gold values, and an owner is a claim that held.
    Without `asked`, a record of the candidate with the status `asked` counts
    as asked (the arms and the plants of the scorer); a run of a reader gives
    the questions it asked, and then only they count.
    """
    if asked is None:
        asked = {(str(r.get("id")), str(r.get("unit"))) for r in candidate
                 if r.get("status") == "asked"}
    if case.stage not in STAGES:
        raise ScoreError(f"unknown stage '{case.stage}'")
    modules = [unit for unit in case.units
               if machine.catalog.units[unit].kind != "table_family"]
    if case.stage == "T" and modules:
        raise ScoreError(f"stage T reads table decisions only; the case scores "
                         f"{', '.join(modules)}")
    defaults = {(r["id"], r["unit"]): r
                for r in houses.default_decisions(machine.catalog, machine.house)}
    read = reading.score(case.gold, candidate, defaults, case.units,
                         documents or case.documents, asked, unmapped, set())
    ours = vector(machine.catalog, machine.house, case.gold, candidate, case.units)
    builds, owners, axes = {}, {}, {}
    waiting: dict[Key, dict[str, int]] = {}
    for name in case.data:
        data, gold = staged(machine, case, name)
        made = machine.build(ours, data, case.arms(ours), hooks)
        cells = pending_cells(gold, made)
        for keys in made.pending.values():
            for key in keys:
                waiting.setdefault(key, {other: 0 for other in case.data})
        for keys in cells.values():
            for key in keys:
                waiting[key][name] += 1
        scored = build.score(name, gold.grids, made.grids, made.ok, made.failure,
                             made.not_produced, cells)
        other_axes = [(output.output, axis) for output in scored.outputs if output.produced
                      for axis, equal in (("rows", output.rows_equal),
                                          ("columns", output.columns_equal)) if not equal]
        rebuild = (lambda records, data=data: machine.build(
            records, data, case.arms(records), hooks)) if prove else None
        owners[name], axes[name] = attribute.attribute(machine, gold, made, scored.wrong(),
                                                       other_axes, rebuild)
        builds[name] = scored
    # A claim that failed when it was run owns nothing: its decision is listed below.
    owning = {key for name in case.data for owner in [*owners[name], *axes[name]]
              if owner.confirmed is not False for key in owner.decisions}
    silent, behind = [], {}
    values = {(r["id"], r["unit"]): r["value"] for r in ours}
    for item in read.wrong():
        if item.key in owning or item.key in waiting:
            continue
        changed = _alone(machine, case, item.key, values.get(item.key))
        if any(changed.values()):
            behind[item.key] = changed
        else:
            silent.append(item.key)
    return Result(case.id, arm, case.stage, read, builds, owners, axes, silent, behind,
                  dict(sorted(waiting.items())))


def _alone(machine: Machine, case: Case, key: Key, value: object) -> dict[str, int]:
    """What one value changes when every other decision is gold: per dataset, the
    gold cells that are then wrong, plus one for each axis that is then another
    (the mutation of property P4, for one decision and one value)."""
    records = [r for r in case.gold_vector() if (r["id"], r["unit"]) != key]
    if value is not None:
        records.append({"id": key[0], "unit": key[1], "value": value})
    order = {k: n for n, k in enumerate(machine.catalog.keys())}
    records.sort(key=lambda r: order[(r["id"], r["unit"])])
    changed = {}
    for name in case.data:
        data, gold = staged(machine, case, name)
        made = machine.build(records, data, case.arms(records))
        scored = build.score(name, gold.grids, made.grids, made.ok, made.failure,
                             made.not_produced)
        changed[name] = len(scored.wrong()) + sum(
            (not output.rows_equal) + (not output.columns_equal)
            for output in scored.outputs if output.produced)
    return changed


def separation(machine: Machine, case: Case, datasets: tuple[str, ...] | None = None,
               first_only: bool = False) -> dict[Key, list[tuple[dict, dict[str, int]]]]:
    """What every other value of every decision of the scope changes, alone, on gold.

    The other values are those of `compiler.other_values`: each alternative
    of the entry with the examples of its slots, and each list of the gold
    value with one item left out. This is the identifiability matrix of
    section 6.5, by mutation (property P4), for the outputs of the case. A
    decision is separated on a dataset when one of these values changes a
    cell or an axis there; a value under which the build stops changes
    every cell. With `first_only` the walk of a decision ends at the first
    value that changes something.
    """
    from specfirst.compile import compiler

    wanted = case if datasets is None else dataclasses.replace(
        case, data={name: case.data[name] for name in datasets})
    found: dict[Key, list[tuple[dict, dict[str, int]]]] = {}
    for record in case.gold:
        if record.get("unit") not in case.units or record.get("value") is None:
            continue
        key = (record["id"], record["unit"])
        found[key] = []
        for value in compiler.other_values(machine.catalog, record["id"], record["value"]):
            changed = _alone(machine, wanted, key, value)
            found[key].append((value, changed))
            if first_only and any(changed.values()):
                break
    return found


def standard_alone(machine: Machine, case: Case, prove: bool = True) -> Result:
    """Arm S: the house standard alone. No decision is given."""
    return run(machine, case, [], arm="S", prove=prove)


def control_records(machine: Machine, case: Case) -> tuple[list[dict], reading.Documents]:
    """Arm C: what the parser reads from the standard-form documents of the gold decisions.

    The stated decisions are read by the parser of `specfirst parse` from
    the standard-form document of the case; a case without one gets the
    document that `specfirst render` writes for its stated decisions. The
    defaults are the records of the house standards document. Returns the
    records and the documents they cite.
    """
    form = StandardForm(machine.catalog)
    if case.standard_form is not None:
        names = ((case.standard_form,) if isinstance(case.standard_form, str)
                 else tuple(case.standard_form))
        texts = {name: case.documents.texts[name] for name in names}
    else:
        stated = [{"id": r["id"], "unit": r["unit"], "value": r["value"]} for r in case.gold
                  if r.get("status") == "stated" and r.get("value") is not None]
        texts = {CONTROL_DOCUMENT: form.render_document(CONTROL_DOCUMENT, CONTROL_TITLE,
                                                        stated)}
    records = []
    read = {}
    for text in texts.values():
        doc, parsed = form.parse_document(text)
        read[doc] = text
        records += [decision_record(item, doc, "stated", "document_rule") for item in parsed]
    have = {(r["id"], r["unit"]) for r in records}
    wanted = {(r["id"], r["unit"]) for r in case.gold if r.get("status") == "default"}
    defaults = houses.default_decisions(machine.catalog, machine.house)
    records += [r for r in defaults if (r["id"], r["unit"]) in wanted - have]
    # What neither the documents nor the house standard decide is asked; the oracle
    # answers it, as the oracle file of the case holds the answer.
    known = have | {(r["id"], r["unit"]) for r in defaults}
    for key in sorted({(r["id"], r["unit"]) for r in case.gold} - known):
        if key in case.oracle:
            value = case.oracle[key]
            records.append({"id": key[0], "unit": key[1], "value": value, "status": "asked",
                            "class": "study_input",
                            "statement": form.render(key[0], key[1], value)})
    documents = reading.Documents({
        houses.DOCUMENT_ID: houses.standards_document(machine.catalog, machine.house),
        **case.documents.texts, **read})
    return records, documents


def control(machine: Machine, case: Case, prove: bool = True) -> Result:
    """Arm C on a case."""
    records, documents = control_records(machine, case)
    return run(machine, case, records, arm="C", documents=documents, prove=prove)
