"""The archetype PG-FIX and its sampler (PLAN.md section 6.2, stage S1).

PG-FIX is a preset of design features plus the ranges the sampler may
vary: a randomized, parallel-group, placebo-controlled study of fixed
duration with continuous measurements at visits that have windows. Its
public anchor is CDISCPILOT01; nothing is taken from that study.

Preset (the same in every sampled design):

    allocation          randomized, permuted blocks
    model               parallel groups
    control             placebo
    treatment duration  fixed; one tablet a day
    epochs              screening, treatment, follow-up
    schedule            visits on target days, each with a window
    measurements        vital signs at every visit
    populations         all randomized and safety

Ranges (`RANGES` below is what the sampler draws from).

Two properties of every sampled design exist for the probes of the catalog
(section 6.5), because a design is shared by the visible data and the twin:

- The protocol lists the arms in another order than ascending dose with
  placebo first (probe `arms_listed_out_of_dose_order`).
- The planned number of subjects of every arm is a multiple of 16. A count
  of m subjects among 16 m is 6.25 percent, a value exactly halfway between
  two displayed values (probe `statistic_at_rounding_half`).
"""

from __future__ import annotations

import datetime

from specfirst.gen import GENERATOR, terms
from specfirst.gen.rng import Stream

ARCHETYPE = "PG-FIX"

RANGES: dict[str, object] = {
    "active_arms": (1, 3),                        # dose levels of one drug, besides placebo
    "dose_ladders": ((5, 10, 20), (10, 20, 40), (25, 50, 100), (50, 100, 200)),  # mg
    "arm_size": (16, 32, 48),                     # planned subjects per allocation unit
    "double_active_share": 0.25,                  # two arms only: 2 to 1 for the drug
    "treatment_weeks": (4, 8, 12, 24),
    "visit_interval_weeks": (2, 4),
    "visit_window_days": (2, 3),
    "screening_days": (14, 21, 28),
    "follow_up_days": (7, 14, 28, 30),
    "sites": (3, 8),
    "countries": (1, 3),
    "start_year": (2019, 2023),
    "enrolment_per_week": (3.0, 8.0),
    "screen_failure_rate": (0.05, 0.20),
    "discontinuation_placebo": (0.05, 0.15),
    "discontinuation_active_extra": (0.00, 0.10),
    "events_per_subject": (0.8, 2.2),
    "dose_effect_on_events": (0.15, 0.60),
    "pretreatment_event_rate": (0.03, 0.12),
    "efficacy_set_share": 0.5,
    "temperature_share": 0.5,
    "phases": ("PHASE II TRIAL", "PHASE III TRIAL"),
    "drug_prefixes": ("SFX", "ZQR", "MVK", "KRD", "PLV", "TNB"),
}

_DOSE_LABELS = {1: ("Active",), 2: ("Low Dose", "High Dose"),
                3: ("Low Dose", "Medium Dose", "High Dose")}
_BASE32 = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _between(rng: Stream, low: float, high: float, digits: int = 3) -> float:
    return round(low + (high - low) * rng.uniform(), digits)


def _protocol_order(rng: Stream, actives: list[str], placebo: str) -> list[str]:
    """An order of the arms that is not ascending dose with placebo first."""
    options = [[*actives, placebo], [*reversed(actives), placebo]]
    if len(actives) > 1:
        options.append([placebo, *reversed(actives)])
    unique = [list(option) for option in dict.fromkeys(tuple(option) for option in options)]
    return rng.choice(unique)


def sample(seed: str, catalog: str) -> dict:
    """A design of the archetype, drawn from the seed. `catalog` is its name and version."""
    rng = Stream(seed, "design", ARCHETYPE)
    ranges = RANGES

    study_code = "SF" + "".join(rng.choice(_BASE32) for _ in range(6))
    prefix = rng.choice(ranges["drug_prefixes"])
    drug = f"{prefix}-{rng.between(101, 899)}"
    count = rng.between(*ranges["active_arms"])
    doses = list(rng.choice(ranges["dose_ladders"])[:count])
    size = rng.choice(ranges["arm_size"])

    placebo = {"name": "PBO", "label": "Placebo", "description": "Placebo",
               "type": "Placebo Control Arm", "studyInterventionId": "PLACEBO", "dose": 0}
    actives = [{"name": f"{prefix}{dose}", "label": label,
                "description": f"{drug} {dose} mg once daily",
                "type": "Investigational Arm", "studyInterventionId": drug, "dose": dose}
               for dose, label in zip(doses, _DOSE_LABELS[count], strict=True)]
    by_name = {a["name"]: a for a in (placebo, *actives)}
    order = _protocol_order(rng.child("order"), [a["name"] for a in actives], "PBO")
    double_active = count == 1 and rng.chance(ranges["double_active_share"])
    ratio = [2 if double_active and name != "PBO" else 1 for name in order]
    arms = [{**by_name[name], "plannedNumber": size * share}
            for name, share in zip(order, ratio, strict=True)]

    weeks = rng.choice(ranges["treatment_weeks"])
    interval = rng.choice([i for i in ranges["visit_interval_weeks"] if i <= weeks])
    window = rng.choice(ranges["visit_window_days"])
    screening = rng.choice(ranges["screening_days"])
    follow_up = rng.choice(ranges["follow_up_days"])
    encounters = [
        {"name": "V1", "label": "SCREENING", "visitNumber": 1, "epochId": "SCREENING",
         "plannedDay": -screening, "windowLower": 0, "windowUpper": screening - 1},
        {"name": "V2", "label": "BASELINE", "visitNumber": 2, "epochId": "TREATMENT",
         "plannedDay": 1, "windowLower": 0, "windowUpper": 0},
    ]
    for number, week in enumerate(range(interval, weeks + 1, interval), start=3):
        encounters.append(
            {"name": f"V{number}", "label": f"WEEK {week}", "visitNumber": number,
             "epochId": "TREATMENT", "plannedDay": 7 * week + 1,
             "windowLower": window, "windowUpper": window})
    encounters.append(
        {"name": f"V{len(encounters) + 1}", "label": "FOLLOW-UP",
         "visitNumber": len(encounters) + 1, "epochId": "FOLLOW-UP",
         "plannedDay": 7 * weeks + 1 + follow_up, "windowLower": window, "windowUpper": window})

    codes = ["SYSBP", "DIABP", "PULSE", "WEIGHT", "HEIGHT"]
    if rng.chance(ranges["temperature_share"]):
        codes.append("TEMP")
    tests = [{"testCode": code, "test": terms.VITAL_SIGNS[code]["test"],
              "unit": terms.VITAL_SIGNS[code]["unit"],
              "decimals": terms.VITAL_SIGNS[code]["decimals"],
              "encounterIds": ["V1"] if code == "HEIGHT" else [e["name"] for e in encounters]}
             for code in codes]

    populations = [
        {"name": "RANDOMIZED", "text": "All randomized subjects"},
        {"name": "SAFETY", "text": "Subjects who received study treatment"},
    ]
    if rng.chance(ranges["efficacy_set_share"]):
        populations.append({"name": "EFFICACY", "text": "Subjects evaluable for efficacy"})

    site_count = rng.between(*ranges["sites"])
    countries = rng.sample(terms.COUNTRIES, rng.between(*ranges["countries"]))
    sites = [{"name": str(101 + i), "country": countries[i % len(countries)],
              "weight": rng.between(1, 4)} for i in range(site_count)]

    year = rng.between(*ranges["start_year"])
    start = datetime.date(year, 1, 1) + datetime.timedelta(days=rng.between(0, 364))
    scale = rng.choice(sorted(terms.CAUSALITY_SCALES))
    placebo_stop = _between(rng, *ranges["discontinuation_placebo"])

    return {
        "design": 1,
        "archetype": ARCHETYPE,
        "generator": GENERATOR,
        "catalog": catalog,
        "study": {
            "name": study_code,
            "label": (f"A Randomized, Double-Blind, Placebo-Controlled, Parallel-Group Study "
                      f"of {drug} Given Once Daily for {weeks} Weeks in Adults"),
            "studyPhase": rng.choice(ranges["phases"]),
            "startDate": start.isoformat(),
        },
        "studyDesign": {
            "model": "PARALLEL",
            "blindingSchema": "DOUBLE BLIND",
            "randomization": {"allocationRatio": ratio, "blockSize": 2 * sum(ratio)},
            "population": {"plannedEnrollmentNumber": sum(a["plannedNumber"] for a in arms),
                           "plannedAge": {"minValue": 18, "maxValue": 80}},
            "studyInterventions": [
                {"name": drug, "label": drug, "role": "Experimental Intervention",
                 "type": "DRUG", "doseForm": "TABLET", "route": "ORAL", "frequency": "QD",
                 "unit": "mg"},
                {"name": "PLACEBO", "label": "Placebo", "role": "Placebo Comparator",
                 "type": "DRUG", "doseForm": "TABLET", "route": "ORAL", "frequency": "QD",
                 "unit": "mg"},
            ],
            "arms": arms,
            "epochs": [
                {"name": "SCREENING", "type": "Screening Epoch"},
                {"name": "TREATMENT", "type": "Treatment Epoch"},
                {"name": "FOLLOW-UP", "type": "Follow-Up Epoch"},
            ],
            "elements": [
                {"name": "SCRN", "label": "Screening", "epochId": "SCREENING"},
                *({"name": f"T{a['name']}"[:8], "label": a["description"],
                   "epochId": "TREATMENT", "armId": a["name"]} for a in arms),
                {"name": "FUP", "label": "Follow-up", "epochId": "FOLLOW-UP"},
            ],
            "encounters": encounters,
            "activities": [{"name": "VITAL SIGNS", "tests": tests}],
            "analysisPopulations": populations,
        },
        "sites": sites,
        "collection": {
            "adverseEvents": {"causality": list(terms.CAUSALITY_SCALES[scale]),
                              "dictionary": terms.AE_DICTIONARY},
            "disposition": {"subcategories": {"treatment": "STUDY TREATMENT",
                                              "study": "STUDY PARTICIPATION"}},
            "exposure": {"firstDoseTime": True},
            "visits": {"unscheduled": True},
        },
        "process": {
            "enrolmentPerWeek": _between(rng, *ranges["enrolment_per_week"], digits=1),
            "screenFailureRate": _between(rng, *ranges["screen_failure_rate"]),
            "discontinuation": {
                "placebo": placebo_stop,
                "active": round(placebo_stop
                                + _between(rng, *ranges["discontinuation_active_extra"]), 3),
            },
            "adverseEvents": {
                "eventsPerSubject": _between(rng, *ranges["events_per_subject"], digits=2),
                "doseEffect": _between(rng, *ranges["dose_effect_on_events"], digits=2),
                "pretreatmentRate": _between(rng, *ranges["pretreatment_event_rate"]),
            },
        },
    }
