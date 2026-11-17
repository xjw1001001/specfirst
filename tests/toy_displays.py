"""A made-up output for the tests of layouts, grids, pages and the trace of cells.

The reporting event is that of tests/toy_results.py with one analysis and
one output added: a summary of adverse events by arm, with the number of
subjects in the header. The expected texts in the tests are worked out by
hand from the tables there.

    arm                    A          B          C
    subjects of the set    4          3          0
    with an event          S1, S2     S5, S6     -
    treatment-emergent     S1, S2     S5, S6     -
"""

from __future__ import annotations

import copy

import toy_results as toy

from specfirst.machine import ars, methods, results

OUTPUT = "Out_AE"
LAYOUT = {
    "layout": 0,
    "output": OUTPUT,
    "columns": {"grouping": "ARM", "labels": {"Arm_A": "Arm A", "Arm_B": "Arm B"}},
    "rows": [
        {"kind": "header", "cell": "{N}",
         "parts": {"N": {"analysis": "A_N", "operation": "M_N_n", "pattern": "(N=XX)"}}},
        {"kind": "analyses", "cell": "{n} {pct}",
         "parts": {"n": {"operation": "M_CAT_n", "pattern": "XX"},
                   "pct": {"operation": "M_CAT_pct"}},
         "analyses": ["A_AE", {"id": "A_TEAE", "label": "Treatment-emergent"}]},
    ],
}
# What the grid of LAYOUT shows, row by row: arm C has no subject, so its
# percent has no value and is shown as the layout's text for a missing value.
TEXTS = [["(N=4)", "(N=3)", "(N=0)"],
         ["2 ( 50.0)", "2 ( 66.7)", "0 "],
         ["2 ( 50.0)", "2 ( 66.7)", "0 "]]


def event_data() -> dict:
    """The toy event with the analysis A_AE and the output Out_AE."""
    data = toy.event_data()
    data["analyses"].append(toy.analysis(
        "A_AE", "M_CAT", "ADAE", "USUBJID", [("ARM", True)], analysisSetId="SAF",
        label="With an adverse event", **toy.percent_of("A_AE", "A_N")))
    for method in data["methods"]:
        for operation in method["operations"]:
            if operation["id"] == "M_CAT_pct":
                operation["resultPattern"] = "( XX.X)"
    data["globalDisplaySections"] = [
        {"sectionType": "Title", "subSections": [{"id": "G_Title", "text": "Safety set"}]}]
    data["outputs"] = [{
        "id": OUTPUT, "name": "Adverse events", "version": 1,
        "displays": [{"order": 1, "display": {
            "id": "Disp_AE", "name": "Adverse events", "version": 1,
            "displaySections": [
                {"sectionType": "Title", "orderedSubSections": [
                    {"order": 2, "subSectionId": "G_Title"},
                    {"order": 1, "subSection": {"id": "T1", "text": "Table 1 <draft>"}}]},
                {"sectionType": "Footnote", "orderedSubSections": [
                    {"order": 1, "subSection": {"id": "F1", "text": "Counted once."}}]},
                {"sectionType": "Abbreviation", "orderedSubSections": [
                    {"order": 1, "subSection": {"id": "A1", "text": "N = subjects."}}]},
                {"sectionType": "Rowlabel Header", "orderedSubSections": [
                    {"order": 1, "subSection": {"id": "R1", "text": "Subjects, n (%)"}}]},
            ]}}],
    }]
    data["mainListOfContents"] = {"name": "contents", "contentsList": {"listItems": [
        {"name": "Adverse events", "level": 1, "order": 1, "outputId": OUTPUT,
         "sublist": {"listItems": [
             {"name": "Subjects", "level": 2, "order": 1, "analysisId": "A_N"},
             {"name": "Events", "level": 2, "order": 2, "sublist": {"listItems": [
                 {"name": "Any", "level": 3, "order": 1, "analysisId": "A_AE"},
                 {"name": "Emergent", "level": 3, "order": 2, "analysisId": "A_TEAE"}]}}]}},
        {"name": "Sex", "level": 1, "order": 2, "analysisId": "A_SEX"}]}}
    return data


def layout_data() -> dict:
    return copy.deepcopy(LAYOUT)


def reference(rows: dict[str, dict], data: dict | None = None, change=None) -> ars.Event:
    """The event with our results embedded as a reference would have them: a raw
    value and, for an operation with a pattern, the value shown by that pattern."""
    patterns = {"M_N_n": "(N=XX)", "M_CAT_n": "XX", "M_CAT_pct": "( XX.X)"}
    listed = results.with_results(ars.index(data or event_data()), list(rows.values()))
    by_key = {}
    for analysis in listed["analyses"]:
        for result in analysis["results"]:
            key = (analysis["id"], result["operationId"], tuple(
                group.get("groupId") or group.get("groupValue") or "*"
                for group in result.get("resultGroups", [])))
            by_key[key] = result
            pattern = patterns.get(result["operationId"])
            if pattern and "rawValue" in result:
                result["formattedValue"] = methods.pattern_text(float(result["rawValue"]), pattern)
    if change:
        change(by_key)
    return ars.index(listed)
