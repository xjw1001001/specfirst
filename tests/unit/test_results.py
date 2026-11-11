"""P2 for results, the exceptions and rule R11: planted differences must be seen (rule R5).

The rows are those of the made-up study of tests/toy_results.py. A reference
is made from them: the reporting event with our own results embedded, and
then changed by hand, the way a real reference differs.
"""

from __future__ import annotations

import copy

import pytest
import toy_results as toy

from specfirst.machine import ars, registry, results
from specfirst.machine.results import state


@pytest.fixture(scope="module")
def rows(root):
    return toy.run(root)


@pytest.fixture(scope="module")
def known(root):
    return registry.load(root)


def reference(rows, change=None, decimals=10) -> ars.Event:
    """The toy event with our results embedded, printed with some decimals, then changed."""
    data = results.with_results(ars.index(toy.event_data()), list(rows.values()))
    for analysis in data["analyses"]:
        for result in analysis["results"]:
            if "rawValue" in result and "." in result["rawValue"]:
                text = f"{float(result['rawValue']):.{decimals}f}".rstrip("0").rstrip(".")
                result["rawValue"] = text
    if change:
        change({(a["id"], r["operationId"], tuple(
            g.get("groupId") or g.get("groupValue") or "*" for g in r.get("resultGroups", []))): r
            for a in data["analyses"] for r in a["results"]})
    return ars.index(data)


def alternative_for(root):
    def build(method_id, option, value):
        return toy.run(root, binding={"options": {method_id: {option: value}}})

    return build


def check(root, known, rows, event, entries):
    comparison = results.compare_reference(event, rows)
    lines, problems = results.check_exceptions(comparison, entries, rows, known,
                                               alternative_for(root))
    return comparison, lines, problems


# ---- the comparison ----------------------------------------------------------------


def test_printed_precision_and_the_precision_of_the_pattern():
    assert state("15.1163", 15.116279069767442) == "match"
    assert state("15.1163", 15.1164) == "differ"
    assert state("86", 86) == "match" and state("86", 87) == "differ"
    assert state("", 1.0) == "differ" and state("1.0", None) == "differ"
    assert state("", None) == "match"  # neither side has a value
    assert state("abc", 1.0) == "differ" and state("NaN", 1.0) == "differ"
    # Trailing zeros dropped: "70" for a value shown with one decimal. Half a unit of
    # the printed value would hide 70.5; the pattern says one decimal at least.
    assert state("70", 70.5) == "edge"  # as printed, and on the boundary at that
    assert state("70", 70.5, decimals=1) == "coarse"
    assert state("70", 70.04, decimals=1) == "match"
    assert state("1", 0.99996, decimals=4) == "match"
    assert state("1", 0.9, decimals=4) == "coarse"
    assert state("1", 0.4, decimals=4) == "differ"
    # More printed decimals than the pattern shows: the printed ones count.
    assert state("0.5934357753", 0.59343577534, decimals=4) == "match"
    assert state("0.5934357753", 0.5934359, decimals=4) == "differ"
    # Full precision on both sides: rounding of the last digits is no edge.
    assert state("3.5714285714285716", 3.571428571428571) == "match"
    # On the boundary by more than rounding: equal only by the allowance.
    assert state("9.5960516021", 9.596051602049998) == "edge"
    assert state("0.07719298250000001", 0.0771929824561402) == "edge"
    assert results.equal("70", 70.5) and not results.equal("70", 70.5, decimals=1)
    assert [results.pattern_decimals(p) for p in ("XX.X", "(XX.XX)", "X.XXXX", "(N=XX)", None)] \
        == [1, 2, 4, 0, 0]


def test_our_own_results_are_reproduced(root, known, rows):
    comparison, lines, problems = check(root, known, rows, reference(rows), [])
    assert (comparison.total, comparison.reproduced) == (67, 67)
    assert comparison.open == {} and problems == [] and lines == []
    assert comparison.extra == {} and comparison.edge == []
    # 13 of them have no value on either side: arm C has no subject.
    assert sum(1 for item in comparison.reference.values() if item.printed == "") == 13


def test_the_id_of_an_embedded_result_is_the_id_of_our_row(rows):
    event = reference(rows)
    assert set(results.embedded(event)) <= set(rows)
    item = results.embedded(event)["ard:A_SOC_P/M_FISHER_p/*/=CARD"]
    assert (item.printed, item.decimals, item.analysis_id) == ("1", 4, "A_SOC_P")
    data = copy.deepcopy(event.data)
    data["analyses"][0]["results"][0]["resultGroups"].append({"groupingId": "SEX", "groupId": "x"})
    with pytest.raises(results.ResultsError, match="names the grouping SEX"):
        results.embedded(ars.index(data))
    data = copy.deepcopy(event.data)
    data["analyses"][0]["results"].append(data["analyses"][0]["results"][0])
    with pytest.raises(results.ResultsError, match="two results for ard:A_N/M_N_n/Arm_A"):
        results.embedded(ars.index(data))


# ---- planted differences and their proofs ---------------------------------------------


def exchange(found):
    """The reference has the counts of arm A and arm B exchanged, as in E3."""
    a, b = found[("A_N", "M_N_n", ("Arm_A",))], found[("A_N", "M_N_n", ("Arm_B",))]
    a["rawValue"], b["rawValue"] = b["rawValue"], a["rawValue"]


EXCHANGED = [
    {"result": "ard:A_N/M_N_n/Arm_A", "embedded": "3", "class": "reference_error",
     "proof": {"kind": "value_of_other_result", "result": "ard:A_N/M_N_n/Arm_B"}},
    {"result": "ard:A_N/M_N_n/Arm_B", "embedded": "4", "class": "reference_error",
     "proof": {"kind": "value_of_other_result", "result": "ard:A_N/M_N_n/Arm_A"}},
]


def test_a_difference_needs_an_entry_and_an_entry_needs_a_difference(root, known, rows):
    event = reference(rows, exchange)
    comparison, _, problems = check(root, known, rows, event, [])
    assert comparison.reproduced == 65 and sorted(comparison.differing) == [
        "ard:A_N/M_N_n/Arm_A", "ard:A_N/M_N_n/Arm_B"]
    assert problems == [
        "ard:A_N/M_N_n/Arm_A: embedded 3, ours 4: a difference with no class",
        "ard:A_N/M_N_n/Arm_B: embedded 4, ours 3: a difference with no class"]
    assert results.exchanged(event, comparison, rows) == {"ARM": 2}
    _, lines, problems = check(root, known, rows, event, EXCHANGED)
    assert problems == [] and lines == [
        "  explained:   2 reference_error, proof value_of_other_result"]
    # The same entries against a reference that has no such difference.
    _, _, problems = check(root, known, rows, reference(rows), EXCHANGED)
    assert problems == [
        f"ard:A_N/M_N_n/Arm_{arm}: listed as an exception, but it is reproduced or not a result "
        "of the reference" for arm in "AB"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"embedded": "5"}, "the entry says the reference embeds '5', it embeds '3'"),
        ({"proof": {"kind": "value_of_other_result", "result": "ard:A_N/M_N_n/Arm_C"}},
         "the embedded value 3 is not our value of ard:A_N/M_N_n/Arm_C (0)"),
        ({"proof": {"kind": "value_of_other_result", "result": "ard:A_N/M_N_n/Arm_A"}},
         "is not another of our results"),
        ({"class": "rule_choice"}, "proves a reference_error only"),
        ({"proof": {"kind": "no_records", "zero": ["ard:A_N/M_N_n/Arm_C"]}},
         "the reference embeds the value 3"),
        ({"proof": {"kind": "same_under_every", "method": "summary.continuous",
                    "option": "quantile_definition"}},
         "method summary.continuous does not compute this result"),
        ({"proof": {"kind": "alternative", "method": "count.subjects", "option": "distinct",
                    "value": True}}, "the registry has no option count.subjects.distinct"),
    ],
)
def test_a_proof_that_does_not_hold_fails(root, known, rows, change, message):
    entries = [{**EXCHANGED[0], **change}, EXCHANGED[1]]
    _, _, problems = check(root, known, rows, reference(rows, exchange), entries)
    assert len(problems) == 1 and message in problems[0], problems


def test_proofs_that_rest_on_a_method_option(root, known, rows):
    q1, median = "ard:A_AGE/M_CONT_q1/Arm_A", "ard:A_AGE/M_CONT_median/Arm_A"

    def other_values(found):
        found[("A_AGE", "M_CONT_q1", ("Arm_A",))]["rawValue"] = "58"  # what R's default gives
        found[("A_AGE", "M_CONT_median", ("Arm_A",))]["rawValue"] = "60"  # what nothing gives

    event = reference(rows, other_values)
    option = {"method": "summary.continuous", "option": "quantile_definition"}
    entries = [
        # The reference follows another alternative of the decision: a rule_choice.
        {"result": q1, "embedded": "58", "class": "rule_choice",
         "proof": {"kind": "alternative", **option, "value": "r7"}},
        # No alternative gives 60: the median is 61 under both definitions.
        {"result": median, "embedded": "60", "class": "reference_error",
         "proof": {"kind": "same_under_every", **option}},
    ]
    _, lines, problems = check(root, known, rows, event, entries)
    assert problems == [] and len(lines) == 2
    # The proofs exchanged: neither holds.
    swapped = [{**entries[0], "class": "reference_error",
                "proof": {"kind": "same_under_every", **option}},
               {**entries[1], "class": "rule_choice",
                "proof": {"kind": "alternative", **option, "value": "r7"}}]
    _, _, problems = check(root, known, rows, event, swapped)
    assert len(problems) == 2
    assert any("with quantile_definition = r7 our value is 58.0, not 55.0" in p for p in problems)
    assert any("with quantile_definition = r7 our value is 61.0, not the embedded 60" in p
               for p in problems)


def test_no_alternative_needs_the_rest_of_the_cell_to_agree(root, known, rows):
    """The proof of a value that no listed alternative gives, in a cell that is otherwise ours."""
    option = {"kind": "no_alternative", "method": "summary.continuous",
              "option": "quantile_definition"}

    def changed(**values):
        def change(found):
            for name, text in values.items():
                found[("A_AGE", f"M_CONT_{name}", ("Arm_A",))]["rawValue"] = text
        return reference(rows, change)

    def entry(name, text):
        return {"result": f"ard:A_AGE/M_CONT_{name}/Arm_A", "embedded": text,
                "class": "reference_error", "proof": option}

    # The median is 61 under both definitions: no alternative gives 60.
    assert check(root, known, rows, changed(median="60"), [entry("median", "60")])[2] == []
    # The first quartile is 55 by the SAS default and 58 by R's: 58 is an alternative.
    _, _, problems = check(root, known, rows, changed(q1="58"), [entry("q1", "58")])
    assert len(problems) == 1 and "our value is the embedded 58" in problems[0]
    # When the mean of the cell differs too, the data may not be the same.
    _, _, problems = check(root, known, rows, changed(median="60", mean="99"),
                           [entry("median", "60")])
    assert any("ard:A_AGE/M_CONT_mean/Arm_A, of the same cell, is not reproduced either" in p
               for p in problems)


def test_a_result_without_a_value_and_without_records(root, known, rows):
    data = results.with_results(ars.index(toy.event_data()), list(rows.values()))
    # A group the reference lists and we do not have: no flagged record has this class.
    next(a for a in data["analyses"] if a["id"] == "A_SOC_P")["results"].append({
        "operationId": "M_FISHER_p", "rawValue": "", "resultGroups": [
            {"groupingId": "ARM"}, {"groupingId": "SOC", "groupValue": "GI"}]})
    event = ars.index(data)
    key = "ard:A_SOC_P/M_FISHER_p/*/=GI"
    comparison = results.compare_reference(event, rows)
    assert comparison.absent == {key: ""}
    entry = {"result": key, "embedded": "", "class": "reference_error",
             "proof": {"kind": "no_records", "zero": ["ard:A_SOC/M_CAT_n/Arm_A/=CARD/=MI"]}}
    assert check(root, known, rows, event, [entry])[2] == []
    for zero, message in (([], "names no count"),
                          (["ard:A_SOC/M_CAT_n/Arm_A/=CARD/=AF"], "is not a count of 0")):
        bad = {**entry, "proof": {"kind": "no_records", "zero": zero}}
        assert message in check(root, known, rows, event, [bad])[2][0]


def test_the_exceptions_file_is_checked_when_it_is_read(tmp_path):
    path = tmp_path / "exceptions.yaml"

    def load(text):
        path.write_text(text, encoding="ascii")
        return results.load_exceptions(path)

    good = ("exceptions: 0\nresults:\n  toy:\n    - result: \"ard:A/n\"\n      embedded: \"3\"\n"
            "      class: reference_error\n      proof: {kind: no_records, zero: []}\n")
    assert list(load(good)) == ["toy"]
    for text, message in (
        ("exceptions: 1\nresults: {}\n", "expected `exceptions: 0`"),
        ("exceptions: 0\nresults: []\n", "'results' must map"),
        (good.replace("reference_error", "typo"), "'class' must be one of"),
        (good.replace("no_records", "trust_me"), "'proof' needs a 'kind' out of"),
        (good.replace('"ard:A/n"', '"A/n"'), "'result' must be the ID of an ARD row"),
        (good.replace('embedded: "3"', "embedded: 3"), "'embedded' must be the reference's value"),
        (good + "      because: x\n", "unknown key because"),
        (good + good.split("toy:\n")[1], "listed twice"),
    ):
        with pytest.raises(results.ResultsError, match=message):
            load(text)


# ---- rule R11 ----------------------------------------------------------------------


def test_the_engines_agree_only_within_the_tolerance(rows):
    other = copy.deepcopy(rows)
    lines, problems = results.agreement(rows, other)
    assert problems == [] and lines == [
        "engines: 67 results in both, 0 disagree; largest relative difference 0.0e+00 "
        "(allowed 1e-09)"]
    key = "ard:A_AGE/M_CONT_mean/Arm_A"
    other[key]["raw_value"] = 62.0 * (1 + 5e-10)
    assert results.agreement(rows, other)[1] == []
    other[key]["raw_value"] = 62.0 * (1 + 2e-9)
    assert "relative difference 2.0e-09" in results.agreement(rows, other)[1][0]
    other[key]["raw_value"] = None
    assert results.agreement(rows, other)[1] == [f"{key}: Python 62.0, R None"]
    other = copy.deepcopy(rows)
    other[key]["method_options_hash"] = "0" * 64
    assert results.agreement(rows, other)[1] == [f"{key}: the two engines stamp it differently"]
    del other[key]
    other["ard:X/n"] = {"id": "ard:X/n", "raw_value": 1}
    assert results.agreement(rows, other)[1] == [
        f"{key}: only the Python engine has it", "ard:X/n: only the R engine has it"]
    # A count as a whole number in one engine and as a float in the other is one value.
    other = copy.deepcopy(rows)
    other["ard:A_N/M_N_n/Arm_A"]["raw_value"] = 4.0
    assert results.agreement(rows, other)[1] == []


# ---- files -------------------------------------------------------------------------


def test_an_ard_file_is_checked_before_it_is_written(root, rows, tmp_path):
    ordered = list(rows.values())
    results.write_ard(tmp_path / "ard.jsonl", ordered, root)
    text = (tmp_path / "ard.jsonl").read_text("ascii")
    assert text.count("\n") == 67 and text.startswith('{"analysis_id":"A_AGE"')
    with pytest.raises(results.ResultsError, match="not sorted by id"):
        results.write_ard(tmp_path / "bad.jsonl", ordered[::-1], root)
    spoiled = [dict(ordered[0], raw_value="62.0"), *ordered[1:]]
    with pytest.raises(results.ResultsError, match="is not of type"):
        results.write_ard(tmp_path / "bad.jsonl", spoiled, root)
    with pytest.raises(results.ResultsError, match="is used 2 times"):
        results.write_ard(tmp_path / "bad.jsonl", [ordered[0], *ordered], root)
    assert not (tmp_path / "bad.jsonl").exists()


def test_the_event_with_our_results_carries_raw_values_only(rows):
    data = results.with_results(ars.index(toy.event_data()), list(rows.values()))
    carried = [r for a in data["analyses"] for r in a["results"]]
    assert len(carried) == 67 and all("formattedValue" not in r for r in carried)
    by_key = {(a["id"], r["operationId"], tuple(
        g.get("groupId") or g.get("groupValue") or "*" for g in r.get("resultGroups", []))): r
        for a in data["analyses"] for r in a["results"]}
    assert by_key[("A_N", "M_N_n", ("Arm_A",))]["rawValue"] == "4"
    assert by_key[("A_SEX", "M_CAT_pct", ("Arm_B", "Sex_F"))]["rawValue"] == repr(100 / 3)
    assert "rawValue" not in by_key[("A_SEX", "M_CAT_pct", ("Arm_C", "Sex_F"))]
    assert by_key[("A_SOC_P", "M_FISHER_p", ("*", "CARD"))]["resultGroups"] == [
        {"groupingId": "ARM"}, {"groupingId": "SOC", "groupValue": "CARD"}]
    assert results.raw_text(None) is None and results.raw_text(0.1) == "0.1"
