"""The design model: what `design.yaml` holds (PLAN.md section 6.2).

`design.yaml` is the generator's internal description of a study. The
reader agent never sees it. Its terms follow USDM v4 where USDM has the
concept, so that import and export can be added later:

    study                  name (the study identifier), label, studyPhase
    studyDesign            model, blindingSchema, population
      studyInterventions   name, label, role, type and how it is given
      arms                 StudyArm: name, label, description, type; in the
                           order in which the protocol lists them
      epochs, elements     StudyEpoch and StudyElement
      encounters           Encounter: the visits, each with its planned day
                           and window (USDM keeps these in Timing)
      activities           what is measured at which encounters
      analysisPopulations  AnalysisPopulation: which analysis sets exist

Three parts have no USDM class; they are the generator's own:

    studyDesign.randomization   allocation ratio and block size
    sites                       study sites with their share of enrolment
    collection                  what the case report form collects (layer L2
                                is a placeholder in M1)
    process                     parameters of the subject process (stage S2)

How an arm maps to SDTM: `name` is ARMCD, `description` is ARM, `label` is
the short label a decode list in a SAP would give the arm.
"""

from __future__ import annotations

from pathlib import Path

import yaml

FORMAT = 1

EPOCHS = ("SCREENING", "TREATMENT", "FOLLOW-UP")
POPULATIONS = ("RANDOMIZED", "SAFETY", "EFFICACY")
PLACEBO_ROLE = "Placebo Comparator"


class DesignError(ValueError):
    """The design cannot be used."""


def load(path: Path) -> dict:
    with open(path, encoding="ascii") as handle:
        design = yaml.safe_load(handle)
    found = problems(design)
    if found:
        raise DesignError(f"{path}: " + "; ".join(found))
    return design


def dump(design: dict) -> str:
    """The canonical text of a design: the same design gives the same bytes."""
    return yaml.safe_dump(design, sort_keys=False, default_flow_style=False,
                          allow_unicode=False, width=100)


def study_id(design: dict) -> str:
    return str(design["study"]["name"])


def arms(design: dict) -> list[dict]:
    """The arms in the order in which the protocol lists them."""
    return list(design["studyDesign"]["arms"])


def arm(design: dict, name: str) -> dict:
    for item in arms(design):
        if item["name"] == name:
            return item
    raise KeyError(name)


def intervention(design: dict, name: str) -> dict:
    for item in design["studyDesign"]["studyInterventions"]:
        if item["name"] == name:
            return item
    raise KeyError(name)


def is_placebo(design: dict, arm_name: str) -> bool:
    item = arm(design, arm_name)
    return intervention(design, item["studyInterventionId"])["role"] == PLACEBO_ROLE


def dose_order(design: dict) -> list[str]:
    """Arm names in ascending order of dose, with placebo first."""
    listed = arms(design)
    keyed = sorted(
        range(len(listed)),
        key=lambda i: (not is_placebo(design, listed[i]["name"]), listed[i]["dose"], i))
    return [listed[i]["name"] for i in keyed]


def encounters(design: dict) -> list[dict]:
    """The planned visits, by visit number."""
    return sorted(design["studyDesign"]["encounters"], key=lambda e: e["visitNumber"])


def encounter(design: dict, name: str) -> dict:
    for item in design["studyDesign"]["encounters"]:
        if item["name"] == name:
            return item
    raise KeyError(name)


def vital_signs(design: dict) -> list[dict]:
    """The vital sign tests the study measures; empty when it measures none."""
    for activity in design["studyDesign"].get("activities") or []:
        if activity.get("name") == "VITAL SIGNS":
            return list(activity.get("tests") or [])
    return []


def treatment_days(design: dict) -> int:
    """The planned number of dosing days: day 1 to the day before the last treatment visit."""
    last = max(e["plannedDay"] for e in encounters(design) if e["epochId"] == "TREATMENT")
    return last - 1


def follow_up_days(design: dict) -> int:
    """Planned days from the last dose to the follow-up visit."""
    planned = [e["plannedDay"] for e in encounters(design) if e["epochId"] == "FOLLOW-UP"]
    return (planned[0] - 1 - treatment_days(design)) if planned else 0


def features(design: dict) -> dict[str, bool]:
    """The design features that `applies_when` may name (standard/catalog/catalog.yaml)."""
    body = design["studyDesign"]
    populations = {p["name"] for p in body.get("analysisPopulations") or []}
    collection = design.get("collection") or {}
    has_vitals = bool(vital_signs(design))
    return {
        "design.always": True,
        "design.randomized": bool(body.get("randomization")),
        "design.multiple_arms": len(body["arms"]) >= 2,
        "design.has_exposure": bool(body.get("studyInterventions")),
        "design.has_efficacy_set": "EFFICACY" in populations,
        "design.collects_adverse_events": "adverseEvents" in collection,
        "design.collects_vital_signs": has_vitals,
        "design.has_bds_parameters": has_vitals,
        "design.fixed_visits": bool(body.get("encounters")),
        "design.unscheduled_visits": bool((collection.get("visits") or {}).get("unscheduled")),
    }


def problems(design: object) -> list[str]:
    """Why a design cannot be used. An empty list means it can."""
    if not isinstance(design, dict):
        return ["the design is not a mapping"]
    found: list[str] = []
    if design.get("design") != FORMAT:
        found.append(f"'design' must be {FORMAT}, the version of the format")
    for key in ("archetype", "generator", "catalog"):
        if not isinstance(design.get(key), str) or not design.get(key):
            found.append(f"'{key}' is missing")
    study = design.get("study")
    if not isinstance(study, dict) or not study.get("name") or not study.get("startDate"):
        found.append("'study' needs a name and a startDate")
    body = design.get("studyDesign")
    if not isinstance(body, dict):
        return [*found, "'studyDesign' is missing"]
    interventions = {i.get("name"): i for i in body.get("studyInterventions") or []}
    if not interventions:
        found.append("studyDesign.studyInterventions is empty")
    listed = body.get("arms") or []
    if not 1 <= len(listed) <= 4:
        found.append("a design has 1 to 4 arms")
    names = [a.get("name") for a in listed]
    if len(set(names)) != len(names):
        found.append("arm names must differ")
    for item in listed:
        where = f"arm '{item.get('name')}'"
        for key in ("name", "label", "description", "type", "studyInterventionId"):
            if not item.get(key):
                found.append(f"{where}: '{key}' is missing")
        if item.get("studyInterventionId") not in interventions:
            found.append(f"{where}: unknown intervention '{item.get('studyInterventionId')}'")
        if not isinstance(item.get("dose"), int | float) or item["dose"] < 0:
            found.append(f"{where}: 'dose' must be a number, 0 for placebo")
        if not isinstance(item.get("plannedNumber"), int) or item["plannedNumber"] < 1:
            found.append(f"{where}: 'plannedNumber' must be a positive integer")
        if len(str(item.get("name", ""))) > 20:
            found.append(f"{where}: an arm code has at most 20 characters")
    randomization = body.get("randomization")
    if randomization is not None:
        ratio = randomization.get("allocationRatio") or []
        if len(ratio) != len(listed) or any(not isinstance(r, int) or r < 1 for r in ratio):
            found.append("randomization.allocationRatio needs one positive integer per arm")
    epochs = [e.get("name") for e in body.get("epochs") or []]
    if any(name not in EPOCHS for name in epochs) or "TREATMENT" not in epochs:
        found.append(f"epochs are taken from {', '.join(EPOCHS)} and include TREATMENT")
    visits = body.get("encounters") or []
    numbers = [e.get("visitNumber") for e in visits]
    if len(set(numbers)) != len(numbers):
        found.append("visit numbers must differ")
    for item in visits:
        where = f"encounter '{item.get('name')}'"
        if item.get("epochId") not in epochs:
            found.append(f"{where}: unknown epoch '{item.get('epochId')}'")
        for key in ("plannedDay", "windowLower", "windowUpper"):
            if not isinstance(item.get(key), int):
                found.append(f"{where}: '{key}' must be an integer")
        if item.get("plannedDay") == 0:
            found.append(f"{where}: there is no study day 0")
    if not any(e.get("plannedDay") == 1 for e in visits):
        found.append("one encounter is planned on study day 1")
    for population in body.get("analysisPopulations") or []:
        if population.get("name") not in POPULATIONS:
            found.append(f"unknown analysis population '{population.get('name')}'")
    if not design.get("sites"):
        found.append("'sites' is empty")
    if not isinstance(design.get("process"), dict):
        found.append("'process' is missing")
    return found
