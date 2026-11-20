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
  every analysis it binds resolves that option to the decision's value.

A changed parameter in the reporting event, or a changed value in a record,
is seen by the last rule; tests/unit/test_efficacy.py plants both, and
tests/defects (D9-efficacy) plants the first on the pilot.

What it does not hold (review of real-5a, F4): the values of the records
that set no registry option (the analysis set, the visit record, the
baseline rows, the decimals) are held against nothing here, nor
elsewhere: the proofs of the CSR's exceptions ask only that the decision
they name exists (review of real-5a, G3). A record in
conflict keeps the value the build uses until a person decides.
"""

from __future__ import annotations

import json
from pathlib import Path

from specfirst import schemas
from specfirst.machine import ars
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


def load(path: Path) -> list[dict]:
    with open(path, encoding="ascii") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def problems(root: Path, records: list[dict], events: list[tuple[ars.Event, ars.Binding]],
             registry: Registry) -> tuple[list[str], list[str]]:
    """Lines to print and the problems of the records against the events."""
    lines, found = [], []
    seen: set[str] = set()
    elements: dict[str, tuple[ars.Event, ars.Binding]] = {}
    for event, binding in events:
        for kind in ("analyses", "sets", "subsets", "groupings", "methods"):
            for key in getattr(event, kind):
                elements[f"ars:{key}"] = (event, binding)
    checked = 0
    for record in records:
        name = str(record.get("id"))
        found += [f"{name}: {problem}" for problem in
                  schemas.problems("decision-record", record, root=root)]
        if not name.startswith("custom:"):
            found.append(f"{name}: a decision outside catalog@1 has a custom ID (section 10)")
        if name in seen:
            found.append(f"{name}: two records")
        seen.add(name)
        bound = list(record.get("binds") or [])
        found += [f"{name}: binds {key}, which no reporting event of the kit has"
                  for key in bound if key not in elements]
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
    lines.append(f"decisions: {len(records)} records, {len(seen)} IDs; {checked} options of "
                 f"analyses held against the decisions that set them; {len(found)} problems")
    return lines, found
