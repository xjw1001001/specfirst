"""The decisions of a generated study (PLAN.md section 6.4, stage S1), for the slice.

The generator plays the study's statistician: it makes the decisions of the
study within one house standard. A decision either takes the house default
or states another alternative of its catalog entry.

    variants      what a study of a design can decide for an entry: every
                  alternative, each with the slot values that fit the design
                  (the length of the emergence window is the follow-up length,
                  the vital sign of a population rule is one the study measures)
    sample        the decision vector of one kit
    vector        the vector as (id, unit, value) for every decision of a kit; the
                  documents of a kit make the records (specfirst.gen.documents)

The scope is a list of units (the slice of ADR-005: three modules and the
adverse event summary). What the vector holds beyond the units:

- `tfl.output.include` of every other table family, as "not included": a
  kit of the slice plans one output;
- the decisions of the modules that only build variables of ADSL
  (mod-demographics), at the house default: the dataset cannot be compiled
  without them.

The decisions of mod-bds-visits are left out: no output of the slice reads
ADVS, and a kit of the slice does not build it (`specfirst.gen.gold`).

Sampling uses the field `reaches` of the log of probes: under which other
decisions the difference between two alternatives reaches the output. A
vector is sampled so that the decisions it makes can be told apart on the
twin: the constraints of `fits` are the interplays that `reaches` names.
Whether they are in fact told apart is decided by building (stage S7,
`specfirst.gen.verify`); a vector that fails there is sampled again.

Splits (section 6.7): an exam holds out factors, not only seeds. `HELD_OUT`
names a design variation and a combination of alternatives that no train,
dev or test kit has; a sealed kit may have them.
"""

from __future__ import annotations

from specfirst.compile import catalog as catalogs
from specfirst.compile import house as houses
from specfirst.gen import design as designs
from specfirst.gen import probes
from specfirst.gen.rng import Stream

OUTPUT_UNIT = "tfl-ae-summary"
SLICE_UNITS = probes.SLICE_UNITS
# Modules whose decisions a kit of the slice takes at the house default: they build
# variables of a dataset the slice needs and reach none of its outputs.
DEFAULT_UNITS = ("mod-demographics",)
SPLITS = ("train", "dev", "test", "sealed")

# The chance that a decision of a kit is another alternative than the house default.
STATED_SHARE = 0.45
# What an exam holds out (PLAN.md section 6.7): no train, dev or test kit has these. The
# combination is of two stated alternatives: under open-default@2 a table has no total
# column by default, so the total over all arms stands where "none" stood under
# open-default@1.
HELD_OUT = {
    "design": "an allocation ratio other than 1 to 1",
    "combination": {"tfl.columns.total": "all_arms", "tfl.columns.arms": "protocol_order"},
}


# The scenarios of a set of kits: decisions that kit n of a set is given, so that over a
# set every decision of the slice is read by the output of some kit, with a probe behind
# it (`probes.REACHES`). The other decisions of a kit are drawn. A scenario may need a
# design: an efficacy-evaluable set, or three arms (the planned placebo arm of a design
# with two arms holds a subject who was dosed with the other treatment).
SCENARIOS: tuple[dict, ...] = (
    {"values": {}},
    {"values": {"tfl.population": "randomized"}, "arms": 3},
    {"values": {"ae.teae.end": "last_dose_plus_days"}},
    {"values": {"tfl.population": "efficacy"}, "feature": "design.has_efficacy_set"},
    {"values": {"ae.teae.end": "no_end"}},
    {"values": {"pop.safety.grouping": "planned"}, "arms": 3},
    {"values": {"ae.teae.end": "last_dose_plus_days",
                "trt.end.source": "ds_date_when_ex_missing"}},
    {"values": {"tfl.population": "randomized", "ae.teae.end": "no_end"}},
    {"values": {"tfl.population": "efficacy", "ae.teae.end": "last_dose_plus_days"},
     "feature": "design.has_efficacy_set"},
    {"values": {"tfl.population": "safety", "pop.safety.grouping": "actual",
                "trt.actual.source": "dm_actarm"}},
)


def scenario_fits(scenario: dict, design: dict) -> bool:
    """Whether a design can carry a scenario."""
    if len(designs.arms(design)) < scenario.get("arms", 0):
        return False
    return not scenario.get("feature") or designs.features(design)[scenario["feature"]]


class DecisionError(ValueError):
    """The decisions of a study cannot be sampled or written."""


Values = dict[str, dict]


def held_out_design(design: dict) -> bool:
    ratio = design["studyDesign"]["randomization"]["allocationRatio"]
    return len(set(ratio)) > 1


def held_out_combination(values: Values) -> bool:
    return all((values.get(entry_id) or {}).get("rule") == rule
               for entry_id, rule in HELD_OUT["combination"].items())


def placebo_label(design: dict, values: Values) -> str:
    """How the treatment columns name the placebo arm under a decision vector.

    The control of a total column over the active arms "is named by its
    treatment label as the treatment columns show it" (tfl.columns.total).
    """
    placebo = designs.arm(design, designs.dose_order(design)[0])
    by_actual = values["tfl.population"]["rule"] == "safety" and \
        values["pop.safety.grouping"]["rule"] == "actual"
    actual = values["trt.actual.source"]["rule"]
    if by_actual and actual == "first_ex_treatment":
        return "PLACEBO"
    if by_actual and actual == "dm_actarm":
        return placebo["description"]
    return placebo["label"] if values["trt.planned.source"]["rule"] == "dm_armcd_map" \
        else placebo["description"]


def related_values(design: dict, cut: int | None = None) -> list[str]:
    """The causality values that count as related: the scale from position `cut` on."""
    scale = list(design["collection"]["adverseEvents"]["causality"])
    cut = (len(scale) + 1) // 2 if cut is None else cut
    return scale[cut:]


def variants(entry: catalogs.Entry, design: dict, parameters: dict) -> list[dict]:
    """The values a study of this design can decide for an entry, in catalog order.

    One value per alternative: the slots have the value that fits the design
    and that the probes of the entry are built around. `slot_values` lists
    the other values a slot can take.
    """
    found = []
    for rule in probes.alternatives_of(entry, design):
        value: dict = {"rule": rule}
        for name, options in slot_values(entry.id, rule, design, parameters).items():
            value[name] = options[0]
        found.append(value)
    return found


def slot_values(entry_id: str, rule: str, design: dict, parameters: dict) -> dict[str, list]:
    """For an alternative with slots: slot -> the values a study of this design can state.

    The first value is the one the probes separate the alternative with.
    """
    key = (entry_id, rule)
    if key == ("trt.planned.source", "dm_armcd_map"):
        return {"map": [[{"code": arm["name"], "label": arm["label"]}
                         for arm in designs.arms(design)]]}
    if key == ("pop.randomized.rule", "randomized_with_postbaseline"):
        return {"test": list(parameters["tests"])}
    if key == ("pop.efficacy.rule", "baseline_and_postbaseline"):
        return {"test": list(parameters["tests"])}
    if key == ("pop.efficacy.rule", "attended_visit"):
        return {"visit": list(parameters["visits"])}
    if key == ("disp.status.record", "disposition_event_by_subcategory"):
        return {"subcategory": [parameters["treatment_subcategory"],
                                parameters["study_subcategory"]]}
    if key == ("ae.teae.end", "last_dose_plus_days"):
        return {"days": [parameters["window_days"]]}
    if key == ("ae.related.values", "stated_list"):
        scale = list(design["collection"]["adverseEvents"]["causality"])
        middle = (len(scale) + 1) // 2
        cuts = [middle, *[cut for cut in range(1, len(scale)) if cut != middle]]
        return {"values": [scale[cut:] for cut in cuts]}
    if key == ("tfl.columns.total", "active_arms"):
        placebo = designs.arm(design, designs.dose_order(design)[0])
        return {"control": [placebo["description"]]}
    if key == ("tfl.ae.summary.rows", "stated_rows"):
        return {"rows": [["ANY", "SERIOUS", "FATAL"], ["ANY", "RELATED", "FATAL"],
                         ["FATAL", "SERIOUS", "RELATED", "ANY"], ["ANY", "FATAL"],
                         ["ANY", "SERIOUS", "SERIOUS_RELATED", "DOSE_MODIFIED", "FATAL"],
                         ["ANY", "RELATED", "FATAL", "FATAL_RELATED"]]}
    if entry_id == "tfl.percent.format":
        # Any number of decimals separates the two alternatives at a count of zero.
        return {"decimals": [1, 0, 2]}
    return {}


def entries(catalog: catalogs.Catalog, design: dict,
            units: tuple[str, ...] = SLICE_UNITS) -> list[catalogs.Entry]:
    """The entries of the units that a study of this design decides."""
    return probes.slice_entries(catalog, design, units)


def defaults(catalog: catalogs.Catalog, house: houses.House, design: dict) -> Values:
    """The house default of every entry of the slice that has one, for this design."""
    found = {}
    for entry in entries(catalog, design):
        unit = OUTPUT_UNIT if entry.per_family else entry.units[0]
        value = houses.default_value(catalog, house, entry.id, unit, designs.features(design))
        if value is not None:
            found[entry.id] = value
    return found


def fits(values: Values, parameters: dict) -> list[str]:
    """Why a vector cannot tell its own decisions apart on the twin, as far as the log says.

    Each line is an interplay of `probes.REACHES`: a decision of the vector
    that the output reads, with an alternative that gives the same output
    under the other decisions of the vector.
    """
    problems = []
    rows = probes.shown_rows(values.get("tfl.ae.summary.rows"))
    if "ANY" not in rows:
        problems.append("the table does not show the row ANY: the decisions that act through "
                        "one planted event change nothing")
    if "FATAL" not in rows:
        problems.append("the table does not show the row FATAL: no count of zero separates "
                        "tfl.percent.format")
    start = values["ae.start.imputation"]["rule"]
    if values["ae.teae.start"]["rule"] == "at_or_after_first_dose_time" and \
            start != "not_completed":
        problems.append("ae.start.imputation: with emergence by the time of the first dose the "
                        "two completions to a day give the same table")
    record = values["disp.status.record"]
    end = values["ae.teae.end"]["rule"]
    read = end == "last_dose_plus_days" and values["trt.end.source"]["rule"] \
        == "ds_date_when_ex_missing"
    if record.get("subcategory") == parameters["treatment_subcategory"]:
        # Only the planted subject has a treatment record. With it as the end-of-study
        # record no other subject has an end-of-study date: the disposition date never
        # stands in for a missing exposure end date.
        problems.append("disp.status.record: with the treatment record as the end-of-study "
                        "record nearly no subject has an end-of-study date, and the decisions "
                        "that read that date cannot be told apart")
    elif read and record.get("subcategory") == parameters["study_subcategory"]:
        problems.append("disp.status.record: the study participation record is the last "
                        "disposition event of every subject")
    return problems


def sample(catalog: catalogs.Catalog, house: houses.House, design: dict, parameters: dict,
           rng: Stream, split: str = "train", stated_share: float = STATED_SHARE,
           given: dict[str, str] | None = None) -> Values:
    """The decision vector of one kit: entry -> value, for the entries of the slice.

    Every decision is the house default, or with the chance `stated_share`
    another alternative; `given` (entry -> alternative) fixes the decisions
    of a scenario. A vector that `fits` refuses, or that an exam holds out,
    is drawn again, from the same stream.
    """
    given = given or {}
    if split not in SPLITS:
        raise DecisionError(f"a split is one of {', '.join(SPLITS)}, not '{split}'")
    base = defaults(catalog, house, design)
    for attempt in range(200):
        draw = rng.child("vector", attempt)
        values: Values = {}
        for entry in entries(catalog, design):
            options = variants(entry, design, parameters)
            default = base.get(entry.id)
            # Another alternative, or the default's with other slot values: under
            # open-default@2 the default window is 30 days, and a study may state one
            # of its follow-up length.
            others = [value for value in options if default is None or value != default]
            stream = draw.child(entry.id)
            if entry.id == "tfl.output.include":
                value = default
            elif entry.id in given:
                found = [option for option in options if option["rule"] == given[entry.id]]
                if not found:
                    raise DecisionError(f"{entry.id}: a study of this design cannot decide "
                                        f"'{given[entry.id]}'")
                value = dict(found[0])
            elif default is None or (others and stream.chance(stated_share)):
                value = dict(stream.choice(others))
                slots = slot_values(entry.id, value["rule"], design, parameters)
                for name, choices in slots.items():
                    value[name] = stream.child(name).choice(choices)
            else:
                value = default
            values[entry.id] = value
        total = values.get("tfl.columns.total")
        if total and total["rule"] == "active_arms":
            total["control"] = placebo_label(design, values)
        if fits(values, parameters):
            continue
        if split != "sealed" and held_out_combination(values):
            continue
        return values
    raise DecisionError("no decision vector fits the data after 200 draws")


def vector(catalog: catalogs.Catalog, house: houses.House, design: dict,
           values: Values) -> list[dict]:
    """A vector of the slice as (id, unit, value) for every decision the kit makes.

    The decisions of the slice as sampled; the decisions of `DEFAULT_UNITS`
    at the house default; and the other outputs of the house, not included.
    """
    found = []
    features = designs.features(design)
    from specfirst.compile import predicate

    for entry_id, unit in catalog.keys():
        entry = catalog.entry(entry_id)
        if not predicate.evaluate(predicate.parse(entry.applies_when), features):
            continue
        kind = catalog.units[unit].kind
        if entry_id in values and (unit == OUTPUT_UNIT or (kind == "module"
                                                           and unit in SLICE_UNITS)):
            found.append({"id": entry_id, "unit": unit, "value": values[entry_id]})
        elif unit in DEFAULT_UNITS:
            value = houses.default_value(catalog, house, entry_id, unit, features)
            if value is None:
                raise DecisionError(f"{entry_id}: the slice needs a house default for it")
            found.append({"id": entry_id, "unit": unit, "value": value})
        elif entry_id == "tfl.output.include" and kind == "table_family":
            found.append({"id": entry_id, "unit": unit, "value": {"rule": "not_included"}})
    return found


def as_values(records: list[dict]) -> Values:
    """Decision records as entry -> value, a table family entry by the output of the slice."""
    values = {}
    for record in records:
        entry_unit_is_family = record["unit"].startswith("tfl-")
        if record.get("value") is None or (entry_unit_is_family and record["unit"] != OUTPUT_UNIT):
            continue
        values[record["id"]] = record["value"]
    return values
