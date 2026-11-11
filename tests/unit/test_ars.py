"""Reading an ARS reporting event: its index, what it reads, and its binding to the registry."""

from __future__ import annotations

import pytest
import toy_results as toy

from specfirst.machine import ars, registry


@pytest.fixture(scope="module")
def known(root):
    return registry.load(root)


def test_a_sound_event_has_no_problems_and_is_indexed():
    event = ars.index(toy.event_data())
    assert event.problems == []
    assert list(event.analyses)[:2] == ["A_N", "A_SEX"]
    assert event.operations["M_CAT_pct"][0] == "M_CAT"
    assert event.used_methods() == ["M_ANOVA", "M_CAT", "M_CHISQ", "M_CONT", "M_FISHER", "M_N"]
    assert [g["groupingId"] for g in event.groupings_of(event.analyses["A_SOC"])] == [
        "ARM", "SOC", "PT"]


@pytest.mark.parametrize(
    ("change", "problem"),
    [
        (lambda d: d["analyses"].append(dict(d["analyses"][0])), "analysis 'A_N' is defined twice"),
        (lambda d: d["analyses"][0].update(analysisSetId="NONE"),
         "analysis 'A_N': analysisSetId 'NONE' is not defined"),
        (lambda d: d["analyses"][5].update(dataSubsetId="NONE"),
         "analysis 'A_TEAE': dataSubsetId 'NONE' is not defined"),
        (lambda d: d["analyses"][0]["orderedGroupings"][0].update(groupingId="NONE"),
         "analysis 'A_N': grouping 'NONE' is not defined"),
        (lambda d: d["analyses"][1]["orderedGroupings"][1].update(order=1),
         "analysis 'A_SEX': two groupings have the order 1"),
        (lambda d: d["analyses"][1]["referencedAnalysisOperations"][1].update(analysisId="X"),
         "analysis 'A_SEX': references analysis 'X', which is not defined"),
        (lambda d: d["analysisSets"][0]["condition"].update(comparator="LIKE"),
         "analysis set 'SAF': unknown comparator 'LIKE'"),
        (lambda d: d["analysisSets"][0]["condition"].update(value=["Y", "N"]),
         "analysis set 'SAF': EQ needs exactly one value, found 2"),
        (lambda d: d["dataSubsets"][1]["compoundExpression"].update(logicalOperator="XOR"),
         "data subset 'TEAE_AB': unknown logical operator 'XOR'"),
        (lambda d: d["dataSubsets"][1]["compoundExpression"].update(logicalOperator="NOT"),
         "data subset 'TEAE_AB': NOT has 2 where clauses"),
        (lambda d: d["analysisGroupings"][0]["groups"][0].pop("condition"),
         "group 'Arm_A': needs a condition or a compound expression, and not both"),
        (lambda d: d["analysisGroupings"][2].update(dataDriven=False),
         "grouping 'SOC' is not data-driven and lists no group"),
        (lambda d: d["analysisGroupings"][0].update(dataDriven=True),
         "grouping 'ARM' is data-driven and lists groups"),
        (lambda d: d["methods"][1]["operations"].append(dict(d["methods"][0]["operations"][0])),
         "operation 'M_N_n' is defined in two methods"),
    ],
)
def test_planted_defects_of_an_event_are_named(change, problem):
    data = toy.event_data()
    change(data)
    assert problem in ars.index(data).problems


def test_what_an_analysis_reads():
    event = ars.index(toy.event_data())
    assert ars.reads(event, "A_SOC_P", "USUBJID") == [
        ("grouping", "ADAE", "AESOC"), ("grouping", "ADSL", "ARM"),
        ("key", "ADAE", "USUBJID"), ("key", "ADSL", "USUBJID"),
        ("set", "ADSL", "SAFFL"), ("subset", "ADAE", "TRTEMFL"), ("subset", "ADSL", "ARM"),
        ("variable", "ADAE", "USUBJID"),
    ]
    assert ars.columns(event, "USUBJID") == {
        "ADAE": ["AEDECOD", "AESOC", "TRTEMFL", "USUBJID"],
        "ADSL": ["AGE", "ARM", "SAFFL", "SEX", "USUBJID"],
    }


def test_operations_are_bound_by_the_three_rules(known):
    event = ars.index(toy.event_data())
    binding = ars.bind(event, known)
    # B3: a descriptive operation by the name ARS gives it.
    assert binding.operations["M_CAT_n"] == ("count.subjects", "n")
    assert binding.operations["M_CAT_pct"] == ("percent.subjects", "pct")
    assert binding.operations["M_CONT_q3"] == ("summary.continuous", "q3")
    # B2: "P-value" is the name of three tests; the method's description says which.
    assert binding.operations["M_FISHER_p"] == ("test.fisher.exact", "p_value")
    assert binding.operations["M_CHISQ_p"] == ("test.chisq", "p_value")
    # B1: what the caller gives wins.
    given = {"operations": {"M_FISHER_p": {"method": "test.chisq", "operation": "p_value"}}}
    assert ars.bind(event, known, given).operations["M_FISHER_p"] == ("test.chisq", "p_value")
    # Options: the defaults of the registry, per analysis and method.
    assert binding.options["A_AGE"] == {"summary.continuous": {
        "quantile_definition": "sas5", "sd_denominator": "n_minus_1"}}
    assert binding.options["A_SEX"] == {"count.subjects": {}, "percent.subjects": {}}
    record = binding.record()
    assert record["operations"]["M_N_n"] == {"method": "count.subjects", "operation": "n"}


@pytest.mark.parametrize(
    ("given", "change", "message"),
    [
        ({"operations": {"M_NONE_x": {"method": "count.subjects", "operation": "n"}}}, None,
         "no such ARS operation: M_NONE_x"),
        ({"operations": {"M_N_n": {"method": "count.subjects", "operation": "mean"}}}, None,
         "has no operation 'mean'"),
        ({"operations": {"M_N_n": {"method": "count.records", "operation": "n"}}}, None,
         "no method 'count.records' in the registry"),
        ({"options": {"summary.continuous": {"quantile_definition": "sas4"}}}, None,
         "'sas4' is not one of"),
        ({"options": {"count.subjects": {"distinct": True}}}, None, "has no option distinct"),
        ({"methods": {}}, None, "unknown key methods"),
        (None, lambda d: d["methods"][4].update(description="Method registry: test.fisher"),
         "operation 'M_CHISQ_p' ('P-value') of method 'M_CHISQ' is not bound"),
        (None, lambda d: d["methods"][4].update(description="Method registry: count.subjects"),
         "registry entry 'count.subjects' has no operation that takes the name 'P-value'"),
        (None, lambda d: d["methods"][0]["operations"][0].update(name="Number of subjects"),
         "operation 'M_N_n' ('Number of subjects') of method 'M_N' is not bound"),
        (None, lambda d: d["analyses"][2].update(programmingCode={
            "context": ars.REGISTRY_CONTEXT,
            "parameters": [{"name": "trim", "value": ["1"]}]}),
         "parameter 'trim' must be one option of one of its methods"),
    ],
)
def test_a_binding_that_does_not_hold_is_refused(known, given, change, message):
    data = toy.event_data()
    if change:
        change(data)
    with pytest.raises(ars.ArsError) as error:
        ars.bind(ars.index(data), known, given)
    assert message in str(error.value)


def test_parameters_of_another_context_are_not_options(known):
    data = toy.event_data()
    data["analyses"][2]["programmingCode"] = {
        "context": "SAS Version 9.4", "parameters": [{"name": "quantile_definition",
                                                      "value": ["r7"]}]}
    binding = ars.bind(ars.index(data), known)
    assert binding.options["A_AGE"]["summary.continuous"]["quantile_definition"] == "sas5"


def test_the_schema_check_names_what_does_not_fit():
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#", "type": "object",
        "required": ["id", "name"], "additionalProperties": False,
        "properties": {"id": {"type": "string"}, "name": {"type": "string"},
                       "version": {"type": "integer"}},
    }
    assert ars.schema_problems({"id": "X", "name": "x", "version": 1}, schema) == []
    problems = ars.schema_problems({"id": 1, "version": "1", "extra": True}, schema)
    assert len(problems) == 4 and any("'name' is a required property" in p for p in problems)
