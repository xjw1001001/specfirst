"""A made-up reporting event on made-up data, for the tests of the result engines.

Everything here is invented: eight subjects in two arms, a few adverse
events, and an ARS reporting event with one analysis per kind of method.
The expected values in the tests are worked out by hand from these tables.

    ADSL  S1 to S8. S8 is not in the safety set. S4 has no age.
          Arm A: S1 to S4. Arm B: S5 to S8. No subject is in arm C.
    ADAE  S1 has two records of one event and one event that is not
          treatment-emergent; S6 has an event whose flag is missing; S8 has
          an event but is not in the safety set.
"""

from __future__ import annotations

import copy

import pyarrow as pa

from specfirst.machine import ard, ars, registry, results

ADSL = {
    "USUBJID": ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8"],
    "ARM": ["A", "A", "A", "A", "B", "B", "B", "B"],
    "SAFFL": ["Y", "Y", "Y", "Y", "Y", "Y", "Y", "N"],
    "SEX": ["F", "F", "M", "M", "F", "M", "M", None],
    "AGE": [61.0, 70.0, 55.0, None, 64.0, 72.0, 80.0, 50.0],
}
ADAE = {
    "USUBJID": ["S1", "S1", "S1", "S2", "S5", "S6", "S6", "S8"],
    "TRTEMFL": ["Y", "Y", "N", "Y", "Y", "Y", None, "Y"],
    "AESOC": ["CARD", "CARD", "SKIN", "SKIN", "CARD", "SKIN", "GI", "CARD"],
    "AEDECOD": ["AF", "AF", "RASH", "RASH", "MI", "RASH", "NAUSEA", "AF"],
}


def condition(dataset: str, variable: str, comparator: str, *values: str) -> dict:
    return {"condition": {"dataset": dataset, "variable": variable, "comparator": comparator,
                          "value": list(values)}}


def group(group_id: str, dataset: str, variable: str, value: str) -> dict:
    return {"id": group_id, "name": group_id, **condition(dataset, variable, "EQ", value)}


def operation(operation_id: str, name: str, order: int, **more) -> dict:
    return {"id": operation_id, "name": name, "order": order, **more}


def analysis(analysis_id: str, method: str, dataset: str, variable: str, groupings: list,
             **more) -> dict:
    return {
        "id": analysis_id, "name": analysis_id, "methodId": method, "dataset": dataset,
        "variable": variable, "reason": {"controlledTerm": "SPECIFIED IN SAP"},
        "purpose": {"controlledTerm": "PRIMARY OUTCOME MEASURE"},
        "orderedGroupings": [{"order": n, "groupingId": grouping, "resultsByGroup": by}
                             for n, (grouping, by) in enumerate(groupings, start=1)],
        **more,
    }


def percent_of(own: str, denominator: str) -> dict:
    return {"referencedAnalysisOperations": [
        {"referencedOperationRelationshipId": "M_CAT_pct_NUM", "analysisId": own},
        {"referencedOperationRelationshipId": "M_CAT_pct_DEN", "analysisId": denominator}]}


EVENT = {
    "id": "TOY", "name": "Toy reporting event", "version": 1,
    "mainListOfContents": {"name": "contents", "contentsList": {"listItems": []}},
    "analysisSets": [{"id": "SAF", "name": "Safety set", **condition("ADSL", "SAFFL", "EQ", "Y")}],
    "dataSubsets": [
        {"id": "TEAE", "name": "Treatment-emergent", **condition("ADAE", "TRTEMFL", "EQ", "Y")},
        {"id": "TEAE_AB", "name": "Treatment-emergent, arms A and B", "compoundExpression": {
            "logicalOperator": "AND", "whereClauses": [
                condition("ADAE", "TRTEMFL", "EQ", "Y"),
                condition("ADSL", "ARM", "IN", "A", "B")]}},
    ],
    "analysisGroupings": [
        {"id": "ARM", "name": "Arm", "groupingDataset": "ADSL", "groupingVariable": "ARM",
         "dataDriven": False,
         "groups": [group("Arm_A", "ADSL", "ARM", "A"), group("Arm_B", "ADSL", "ARM", "B"),
                    group("Arm_C", "ADSL", "ARM", "C")]},
        {"id": "SEX", "name": "Sex", "groupingDataset": "ADSL", "groupingVariable": "SEX",
         "dataDriven": False,
         "groups": [group("Sex_F", "ADSL", "SEX", "F"), group("Sex_M", "ADSL", "SEX", "M")]},
        {"id": "SOC", "name": "Organ class", "groupingDataset": "ADAE",
         "groupingVariable": "AESOC", "dataDriven": True},
        {"id": "PT", "name": "Term", "groupingDataset": "ADAE", "groupingVariable": "AEDECOD",
         "dataDriven": True},
    ],
    "methods": [
        {"id": "M_N", "name": "Count", "operations": [operation("M_N_n", "Count of subjects", 1)]},
        {"id": "M_CAT", "name": "Categorical summary", "operations": [
            operation("M_CAT_n", "Count of subjects", 1),
            operation("M_CAT_pct", "Percent of subjects", 2, referencedOperationRelationships=[
                {"id": "M_CAT_pct_NUM", "referencedOperationRole": {"controlledTerm": "NUMERATOR"},
                 "operationId": "M_CAT_n"},
                {"id": "M_CAT_pct_DEN",
                 "referencedOperationRole": {"controlledTerm": "DENOMINATOR"},
                 "operationId": "M_N_n"}])]},
        {"id": "M_CONT", "name": "Continuous summary", "operations": [
            operation("M_CONT_n", "Count of non-missing values", 1),
            operation("M_CONT_mean", "Mean", 2), operation("M_CONT_sd", "Standard deviation", 3),
            operation("M_CONT_median", "Median", 4), operation("M_CONT_q1", "First quartile", 5),
            operation("M_CONT_q3", "Third quartile", 6), operation("M_CONT_min", "Minimum", 7),
            operation("M_CONT_max", "Maximum", 8)]},
        {"id": "M_ANOVA", "name": "ANOVA", "description": "Method registry: test.anova.oneway",
         "operations": [operation("M_ANOVA_p", "P-value", 1, resultPattern="X.XXXX")]},
        {"id": "M_CHISQ", "name": "Chi-square", "description": "Method registry: test.chisq",
         "operations": [operation("M_CHISQ_p", "P-value", 1, resultPattern="X.XXXX")]},
        {"id": "M_FISHER", "name": "Fisher", "description": "Method registry: test.fisher.exact",
         "operations": [operation("M_FISHER_p", "P-value", 1, resultPattern="X.XXXX")]},
    ],
    "analyses": [
        analysis("A_N", "M_N", "ADSL", "USUBJID", [("ARM", True)], analysisSetId="SAF"),
        analysis("A_SEX", "M_CAT", "ADSL", "USUBJID", [("ARM", True), ("SEX", True)],
                 analysisSetId="SAF", **percent_of("A_SEX", "A_N")),
        analysis("A_AGE", "M_CONT", "ADSL", "AGE", [("ARM", True)], analysisSetId="SAF"),
        analysis("A_AGE_P", "M_ANOVA", "ADSL", "AGE", [("ARM", False)], analysisSetId="SAF"),
        analysis("A_SEX_P", "M_CHISQ", "ADSL", "USUBJID", [("ARM", False), ("SEX", False)],
                 analysisSetId="SAF"),
        analysis("A_TEAE", "M_CAT", "ADAE", "USUBJID", [("ARM", True)], analysisSetId="SAF",
                 dataSubsetId="TEAE", **percent_of("A_TEAE", "A_N")),
        analysis("A_SOC", "M_CAT", "ADAE", "USUBJID", [("ARM", True), ("SOC", True), ("PT", True)],
                 analysisSetId="SAF", dataSubsetId="TEAE", **percent_of("A_SOC", "A_N")),
        analysis("A_SOC_P", "M_FISHER", "ADAE", "USUBJID", [("ARM", False), ("SOC", True)],
                 analysisSetId="SAF", dataSubsetId="TEAE_AB"),
    ],
}


def event_data() -> dict:
    return copy.deepcopy(EVENT)


def tables(adsl: dict | None = None, adae: dict | None = None) -> dict[str, ard.Table]:
    return {
        "ADSL": ard.table_from_arrow("ADSL", pa.table(adsl or ADSL)),
        "ADAE": ard.table_from_arrow("ADAE", pa.table(adae or ADAE)),
    }


def engine(root, data: dict | None = None, binding: dict | None = None,
           given: dict[str, ard.Table] | None = None) -> ard.Engine:
    """The Python engine on the toy event, not yet run."""
    event = ars.index(data or event_data())
    assert event.problems == [], event.problems
    known = registry.load(root)
    return ard.Engine(event, known, ars.bind(event, known, binding), given or tables())


def run(root, data: dict | None = None, binding: dict | None = None,
        given: dict[str, ard.Table] | None = None) -> dict[str, dict]:
    """The Python engine on the toy event: ARD rows by ID."""
    return {row["id"]: row for row in engine(root, data, binding, given).run()}


def evidence(root, data: dict | None = None,
             given: dict[str, ard.Table] | None = None) -> results.Evidence:
    """What a proof may ask for on the toy study, as specfirst.machine.build gives it for a kit."""
    made = engine(root, data, None, given)

    def alternative(method_id: str, option: str, value: object) -> dict[str, dict]:
        return run(root, data, {"options": {method_id: {option: value}}}, given)

    return results.Evidence(alternative, made.cell_values, made.compared_groups)
