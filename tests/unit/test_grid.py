"""Layout spec v0, the grid builder, the mock shell, the page and the comparison with a
reference's formatted values, on the made-up output of tests/toy_displays.py.

Every check is first shown to pass on the unchanged inputs and then to fail
on a planted defect (rule R5).
"""

from __future__ import annotations

import copy

import pytest
import toy_displays as displays
import toy_results as toy

from specfirst import schemas
from specfirst.machine import ars, grid, layout, methods, render, results


@pytest.fixture(scope="module")
def event():
    return ars.index(displays.event_data())


@pytest.fixture(scope="module")
def rows(root):
    return toy.run(root, displays.event_data())


@pytest.fixture(scope="module")
def spec():
    return layout.parse(displays.layout_data())


@pytest.fixture(scope="module")
def made(event, spec, rows):
    return grid.build(event, spec, rows)


def texts(value: dict) -> list[list[str]]:
    return [[cell["text"] for cell in row["cells"]] for row in value["rows"]]


# ---- the layout ------------------------------------------------------------------


def test_a_layout_is_read_and_fits_its_event(event, spec):
    assert (spec.output, spec.grouping, spec.missing) == (displays.OUTPUT, "ARM", "")
    assert [block.kind for block in spec.blocks] == ["header", "analyses"]
    assert [part.name for part in spec.blocks[1].parts] == ["n", "pct"]
    assert spec.blocks[1].analyses == (("A_AE", None), ("A_TEAE", "Treatment-emergent"))
    assert layout.problems(spec, event) == []
    # A pattern comes from the layout, else from the ARS operation.
    n, pct = spec.blocks[1].parts
    assert (layout.pattern_of(event, n), layout.pattern_of(event, pct)) == ("XX", "( XX.X)")
    assert layout.template_names("{n} ({pct}) of {N}") == ["n", "pct", "N"]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: d.update(layout=1), "expected `layout: 0`"),
        (lambda d: d.update(colour="red"), "unknown key 'colour'"),
        (lambda d: d.pop("output"), "'output' must name the ARS output"),
        (lambda d: d["columns"].pop("grouping"), "'columns' must name its 'grouping'"),
        (lambda d: d["columns"].update(values=["A", "A"]), "a value is listed twice"),
        (lambda d: d.update(rows=[]), "'rows' must list at least one block"),
        (lambda d: d["rows"][0].update(kind="footer"), "needs a 'kind' out of header, analyses"),
        (lambda d: d["rows"][1].update(cell="{n} {percent}"), "each part stands once"),
        (lambda d: d["rows"][1].update(cell="{n} {n} {pct}"), "each part stands once"),
        (lambda d: d["rows"][1].update(cell="{n:>3} {pct}"), "write a part as {name}"),
        (lambda d: d["rows"][1].update(cell="{n} {pct"), "cell template"),
        (lambda d: d["rows"][0]["parts"]["N"].pop("analysis"),
         "a part of a header names its analysis"),
        (lambda d: d["rows"][1]["parts"]["n"].update(pattern="XX (XX.X)"),
         "exactly one mask"),
        (lambda d: d["rows"][1]["parts"]["n"].update(decimals=1), "needs an 'operation'"),
        (lambda d: d["rows"][1].update(analyses=["A_AE", "A_AE"]), "is listed twice"),
        (lambda d: d["rows"][1].update(analyses=[]), "lists no analysis"),
        (lambda d: d["rows"][1].update(section="@header"), "is that of a header block"),
        (lambda d: d["rows"][1].update(indent=-1), "'indent' must be a whole number"),
        (lambda d: d.update(titles="Table 1"), "titles: must be a list of texts"),
    ],
)
def test_a_layout_that_is_not_of_the_format_is_refused(change, message):
    data = displays.layout_data()
    change(data)
    with pytest.raises(layout.LayoutError, match=message):
        layout.parse(data)


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda d: d.update(output="Out_X"), "the output 'Out_X' is not in the reporting event"),
        (lambda d: d["columns"].update(grouping="TRT"), "the column grouping 'TRT' is not"),
        (lambda d: d["columns"].update(values=["A"]), "is for a data-driven grouping"),
        (lambda d: d["columns"]["labels"].update(Arm_X="x"), "'Arm_X' is not a group of ARM"),
        (lambda d: d["rows"][1].update(analyses=["A_NONE"]), "the analysis 'A_NONE' is not"),
        (lambda d: d["rows"][1]["parts"]["n"].update(operation="M_CONT_mean"),
         "'M_CONT_mean' is not an operation of its method"),
        # A_SEX has two groupings: layout v0 has no row for it.
        (lambda d: d["rows"][1].update(analyses=["A_SEX"]), "whose only grouping is the column"),
        (lambda d: d["rows"][1]["parts"]["n"].pop("pattern"),
         "neither the layout nor the ARS operation gives a pattern"),
    ],
)
def test_a_layout_that_does_not_fit_its_event_is_refused(event, change, message):
    data = displays.layout_data()
    change(data)
    spec = layout.parse(data)
    assert any(message in problem for problem in layout.problems(spec, event))
    with pytest.raises(grid.GridError, match="does not fit the reporting event"):
        grid.plan(event, spec)


# ---- the grid and the shell --------------------------------------------------------


def test_the_grid_shows_every_result_by_its_pattern(root, event, spec, made):
    assert grid.grid_problems(made, root) == []
    assert made["output_id"] == displays.OUTPUT
    # Titles in the order of the display; a global section is taken by its ID.
    assert made["titles"] == ["Table 1 <draft>", "Safety set"]
    assert made["footnotes"] == ["N = subjects.", "Counted once."]
    assert made["columns"] == [{"id": "c1", "label": "Arm A"}, {"id": "c2", "label": "Arm B"},
                               {"id": "c3", "label": "Arm_C"}]
    assert texts(made) == displays.TEXTS
    assert [(row["id"], row["label"], row.get("section")) for row in made["rows"]] == [
        ("r1", "Subjects, n (%)", "@header"), ("r2", "With an adverse event", None),
        ("r3", "Treatment-emergent", None)]
    cell = made["rows"][2]["cells"][1]
    assert cell == {"id": "cell:Out_AE/r3/c2", "column": "c2", "text": "2 ( 66.7)",
                    "ard": ["ard:A_TEAE/M_CAT_n/Arm_B", "ard:A_TEAE/M_CAT_pct/Arm_B"]}
    assert all(grid.numeric(cell) for row in made["rows"] for cell in row["cells"])


def test_a_missing_value_and_the_options_of_a_layout(event, rows):
    data = displays.layout_data()
    data.update(missing="-", titles=["Only this"], footnotes=[])
    data["rows"][0]["label"] = "Subjects"
    data["rows"][1].update(section="Events", indent=1)
    made = grid.build(event, layout.parse(data), rows)
    assert texts(made)[1] == ["2 ( 50.0)", "2 ( 66.7)", "0 -"]
    assert (made["titles"], made["footnotes"]) == (["Only this"], [])
    assert made["rows"][0]["label"] == "Subjects"
    assert (made["rows"][1]["section"], made["rows"][1]["indent"]) == ("Events", 1)


def test_the_shell_is_the_grid_without_results(root, event, spec, made):
    shell = grid.shell(event, spec)
    assert grid.grid_problems(shell, root) == []
    assert texts(shell) == [["(N=xx)"] * 3, ["xx ( xx.x)"] * 3, ["xx ( xx.x)"] * 3]
    assert not any(grid.numeric(cell) for row in shell["rows"] for cell in row["cells"])
    # Everything but the cell texts is that of the grid, the ARD rows included.
    for value in (shell, copy.deepcopy(made)):
        for row in value["rows"]:
            for cell in row["cells"]:
                cell["text"] = ""
    assert shell == copy.deepcopy(shell) and texts(shell) == [[""] * 3] * 3
    plain = copy.deepcopy(made)
    for row in plain["rows"]:
        for cell in row["cells"]:
            cell["text"] = ""
    assert shell == plain


def test_columns_of_a_data_driven_grouping(root):
    """The columns are the values the results have, or those the layout lists, in its order."""
    data = displays.event_data()
    grouping = next(g for g in data["analysisGroupings"] if g["id"] == "ARM")
    grouping.update(dataDriven=True)
    del grouping["groups"]
    for analysis in data["analyses"]:  # arm C has no subject: no test compares three groups
        if analysis["id"] == "A_SOC_P":
            analysis["dataSubsetId"] = "TEAE"
    data["dataSubsets"] = [s for s in data["dataSubsets"] if s["id"] == "TEAE"]
    event = ars.index(data)
    rows = toy.run(root, data)
    given = displays.layout_data()
    given["columns"] = {"grouping": "ARM"}
    made = grid.build(event, layout.parse(given), rows)
    assert [column["label"] for column in made["columns"]] == ["A", "B"]
    assert texts(made) == [row[:2] for row in displays.TEXTS]
    assert made["rows"][1]["cells"][1]["ard"][0] == "ard:A_AE/M_CAT_n/=B"
    given["columns"] = {"grouping": "ARM", "values": ["B", "A"], "labels": {"B": "Arm B"}}
    turned = grid.build(event, layout.parse(given), rows)
    assert [column["label"] for column in turned["columns"]] == ["Arm B", "A"]
    assert texts(turned) == [row[1::-1] for row in displays.TEXTS]
    # A shell has no results to take the values from: the layout must list them.
    assert texts(grid.shell(event, layout.parse(given)))[0] == ["(N=xx)", "(N=xx)"]
    given["columns"] = {"grouping": "ARM"}
    with pytest.raises(grid.GridError, match="the layout must list its values"):
        grid.shell(event, layout.parse(given))
    # A value the layout lists and the results do not have is a result that is missing.
    given["columns"] = {"grouping": "ARM", "values": ["A", "Z"]}
    with pytest.raises(grid.GridError, match="5 results of the layout are not in the ARD, for "
                                             "example ard:A_AE/M_CAT_n/=Z"):
        grid.build(event, layout.parse(given), rows)


def test_what_is_not_a_grid(root, made):
    def problems(change):
        value = copy.deepcopy(made)
        change(value)
        return grid.grid_problems(value, root)

    assert problems(lambda g: g["rows"][1]["cells"][0].pop("ard")) != []  # the schema
    assert "not numbered c1, c2" in problems(lambda g: g["columns"][0].update(id="c9"))[0]
    assert "not numbered r1, r2" in problems(lambda g: g["rows"][1].update(id="r7"))[0]
    assert "not one per column" in problems(lambda g: g["rows"][1]["cells"].pop())[0]
    assert "is not that of its row and column" in problems(
        lambda g: g["rows"][1]["cells"][0].update(id="cell:Out_AE/r3/c1"))[0]
    assert schemas.problems("grid", made, root=root) == []


# ---- the comparison with a reference ------------------------------------------------


def compared(event, spec, made, rows, explained=None):
    return grid.compare_reference(event, spec, made, rows, explained or {})


def test_our_own_grid_equals_a_reference_made_from_it(spec, made, rows):
    found = compared(displays.reference(rows), spec, made, rows)
    assert (found.cells, found.results, found.equal) == (9, 15, 7)
    # Arm C has no percent: neither side has a formatted value, so its two cells in the
    # rows of events are not compared; they are counted.
    assert found.no_reference == ["ard:A_AE/M_CAT_pct/Arm_C", "ard:A_TEAE/M_CAT_pct/Arm_C"]
    assert found.problems == [] and found.differing == {}
    assert found.lines()[0] == (
        "grid Out_AE: 9 cells show 15 results; 7 cells equal the reference's formatted "
        "values, 0 differ, 0 of them with one class")


def test_a_formatted_value_that_differs_has_no_class(spec, made, rows):
    def change(found):
        found[("A_TEAE", "M_CAT_pct", ("Arm_A",))]["formattedValue"] = "( 50.1)"

    found = compared(displays.reference(rows, change=change), spec, made, rows)
    assert found.equal == 6 and found.differing == {
        "cell:Out_AE/r3/c1": ("2 ( 50.0)", "2 ( 50.1)")}
    assert len(found.problems) == 1 and (
        "a difference with no class: ard:A_TEAE/M_CAT_pct/Arm_A is shown as '( 50.0)', the "
        "reference has '( 50.1)', and the result has no classified difference"
        in found.problems[0])


def exchange(found):
    """The reference has the event counts of arm A and arm B exchanged, raw and formatted."""
    a = found[("A_TEAE", "M_CAT_n", ("Arm_A",))]
    b = found[("A_TEAE", "M_CAT_n", ("Arm_B",))]
    a["rawValue"], a["formattedValue"] = "5", "5"
    b["rawValue"], b["formattedValue"] = "7", "7"


def test_a_cell_differs_by_a_result_that_has_a_class(spec, made, rows):
    """The class of a cell is that of the result it shows, when the display explains the rest."""
    event = displays.reference(rows, change=exchange)
    both = {"ard:A_TEAE/M_CAT_n/Arm_A": "reference_error",
            "ard:A_TEAE/M_CAT_n/Arm_B": "reference_error"}
    found = compared(event, spec, made, rows, both)
    assert found.problems == [] and found.equal == 5
    assert found.classified == {"reference_error": 2}
    assert "  2 cells differ by a result classed reference_error" in found.lines()
    # One of the two results has no class: its cell has none.
    found = compared(event, spec, made, rows, {"ard:A_TEAE/M_CAT_n/Arm_A": "reference_error"})
    assert len(found.problems) == 1 and "cell:Out_AE/r3/c2" in found.problems[0]

    # The result has a class, but the reference's text is not its own raw value under
    # the pattern: the difference is one of display, and that has no class.
    def other_text(found):
        exchange(found)
        found[("A_TEAE", "M_CAT_n", ("Arm_A",))]["formattedValue"] = "5.0"

    found = compared(displays.reference(rows, change=other_text), spec, made, rows, both)
    assert len(found.problems) == 1 and (
        "the reference's formatted value '5.0' is not its raw value 5 under the pattern 'XX'"
        in found.problems[0])


def test_a_difference_of_display_only_has_the_class_of_its_entry(spec, made, rows):
    """Issue #31: the reference's raw value is ours, its formatted value is not that raw value
    under its own pattern. With an entry of `formats`, the cell has the entry's class; the
    proof fails when the raw values differ, or when the entry's text is not the reference's."""
    def own_text(found):
        found[("A_TEAE", "M_CAT_n", ("Arm_A",))]["formattedValue"] = "2.0"

    event = displays.reference(rows, change=own_text)
    entry = {"result": "ard:A_TEAE/M_CAT_n/Arm_A", "formatted": "2.0",
             "class": "reference_error", "proof": {"kind": "not_its_own_pattern"}}
    found = compared(event, spec, made, rows)
    assert len(found.problems) == 1 and found.formats_used == set()
    found = grid.compare_reference(event, spec, made, rows, {}, {entry["result"]: entry})
    assert found.problems == [] and found.classified == {"reference_error": 1}
    assert found.formats_used == {"ard:A_TEAE/M_CAT_n/Arm_A"}
    # The entry's text is not the reference's.
    found = grid.compare_reference(event, spec, made, rows, {}, {
        entry["result"]: {**entry, "formatted": "2.00"}})
    assert len(found.problems) == 1 and "the exceptions give the formatted value '2.00'" in \
        found.problems[0]

    # The raw values differ: that is a difference of the result, not of its display.
    def other_value(found):
        found[("A_TEAE", "M_CAT_n", ("Arm_A",))].update(rawValue="3", formattedValue="2.0")

    found = grid.compare_reference(displays.reference(rows, change=other_value), spec, made,
                                   rows, {}, {entry["result"]: entry})
    assert len(found.problems) == 1 and "the values differ, not their display" in \
        found.problems[0]


def test_a_cell_with_two_classes_has_none(spec, made, rows):
    def change(found):
        exchange(found)
        pct = found[("A_TEAE", "M_CAT_pct", ("Arm_A",))]
        pct["rawValue"], pct["formattedValue"] = "62.5", "( 62.5)"

    found = compared(displays.reference(rows, change=change), spec, made, rows, {
        "ard:A_TEAE/M_CAT_n/Arm_A": "reference_error",
        "ard:A_TEAE/M_CAT_n/Arm_B": "reference_error",
        "ard:A_TEAE/M_CAT_pct/Arm_A": "rule_choice"})
    assert len(found.problems) == 1
    assert "its parts have the classes reference_error, rule_choice" in found.problems[0]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda g: g["rows"][2]["cells"][0].update(text="3 ( 75.0)"),
         "the text '3 ( 75.0)' is not what the layout and the ARD give"),
        (lambda g: g["rows"][2]["cells"][0].update(ard=["ard:A_AE/M_CAT_n/Arm_A",
                                                        "ard:A_AE/M_CAT_pct/Arm_A"]),
         "its ARD rows are not those the layout shows there"),
        (lambda g: g["rows"].pop(), "the grid has 2 rows, the layout gives 3"),
        (lambda g: g["rows"][1].update(label="Events"), "the label is not that of the layout"),
        (lambda g: g["columns"][0].update(label="Arm B"),
         "the columns of the grid are not those of the layout"),
        (lambda g: g["titles"].append("Draft"),
         "the titles or the footnotes of the grid are not those of the layout"),
        (lambda g: g["footnotes"].pop(),
         "the titles or the footnotes of the grid are not those of the layout"),
    ],
)
def test_a_grid_that_was_changed_after_it_was_built_does_not_pass(spec, made, rows, change,
                                                                  message):
    value = copy.deepcopy(made)
    change(value)
    found = compared(displays.reference(rows), spec, value, rows)
    assert any(message in problem for problem in found.problems), found.problems


def test_planted_layouts_are_seen(event, rows):
    """A layout that shows something else than the reference: every case must be seen."""
    reference = displays.reference(rows)

    def judged(change):
        data = displays.layout_data()
        change(data)
        spec = layout.parse(data)
        return grid.compare_reference(reference, spec, grid.build(event, spec, rows), rows, {})

    assert judged(lambda d: None).problems == []
    # A row left out: the reference formats results of the output that no cell shows.
    found = judged(lambda d: d["rows"][1].update(analyses=["A_AE"]))
    assert len(found.problems) == 5  # 3 counts and the 2 percents that have a value
    assert all("and no cell shows it" in problem for problem in found.problems)
    # The header left out.
    found = judged(lambda d: d["rows"].pop(0))
    assert [p.split(":")[1] for p in found.problems] == ["A_N/M_N_n/Arm_A", "A_N/M_N_n/Arm_B",
                                                         "A_N/M_N_n/Arm_C"]
    # Another pattern.
    assert len(judged(lambda d: d["rows"][1]["parts"]["pct"].update(
        pattern="(XX.X)")).differing) == 4
    assert len(judged(lambda d: d["rows"][1]["parts"]["pct"].update(
        pattern="( XX)")).differing) == 4
    found = judged(lambda d: d["rows"][0]["parts"]["N"].update(pattern="N=XX"))
    assert len(found.differing) == 3 and len(found.problems) == 3
    # The rows in another order than the reference lists the analyses.
    found = judged(lambda d: d["rows"][1].update(analyses=["A_TEAE", "A_AE"]))
    assert found.problems == ["the rows show the analyses in the order A_N, A_TEAE, A_AE; the "
                              "reference lists them as A_N, A_AE, A_TEAE"]
    # What a reference cannot show: it formats results, not cells. The parts of a cell
    # in another order, or with other text between them, pass. This is a limit of the
    # check, stated here so that it is not taken for a proof (lesson 24).
    for template in ("{pct} {n}", "{n}/{pct}"):
        found = judged(lambda d, t=template: d["rows"][1].update(cell=t))
        assert found.problems == [] and found.differing == {} and found.equal == 7


def test_a_result_the_ard_lacks_is_a_problem_not_a_crash(event, spec, made, rows):
    fewer = {key: row for key, row in rows.items() if key != "ard:A_TEAE/M_CAT_n/Arm_A"}
    with pytest.raises(grid.GridError, match="1 results of the layout are not in the ARD"):
        grid.build(event, spec, fewer)
    found = compared(displays.reference(rows), spec, made, fewer)
    assert ("ard:A_TEAE/M_CAT_n/Arm_A: the layout shows it, the ARD does not have it"
            in found.problems)


def test_the_ids_of_the_plan_are_the_ids_of_the_engine(event, spec, rows):
    planned = grid.plan(event, spec, rows)
    shown = {item.ard for row in planned.rows for cell in row.cells for item in cell.shown}
    assert len(shown) == 15 and shown <= set(rows)
    analysis = event.analyses["A_SOC"]
    assert grid.ard_id(event, analysis, "M_CAT_n", {
        "ARM": ("id", "Arm_A"), "SOC": ("value", "CARD / x"), "PT": ("value", "AF")}) == (
            "ard:A_SOC/M_CAT_n/Arm_A/=CARD%20%2F%20x/=AF")
    assert grid.ard_id(event, event.analyses["A_AGE_P"], "M_ANOVA_p", {}) == (
        "ard:A_AGE_P/M_ANOVA_p/*")
    assert results.reference_id(event, event.analyses["A_N"], {
        "operationId": "M_N_n", "resultGroups": [{"groupingId": "ARM", "groupId": "Arm_A"}]}
    ) == grid.ard_id(event, event.analyses["A_N"], "M_N_n", {"ARM": ("id", "Arm_A")})


# ---- the page ----------------------------------------------------------------------


def test_the_page_is_a_projection_of_the_grid(event, spec, made):
    page = render.html(made)
    assert render.projection_problems(made, page) == []
    assert page == render.html(copy.deepcopy(made))  # the same grid, the same bytes
    assert "<script" not in page and "http" not in page
    assert "Table 1 &lt;draft&gt;" in page  # text is escaped
    assert '<td data-cell="cell:Out_AE/r2/c3">0 </td>' in page  # blanks are kept
    # The header row stands in the table header, the others in the body.
    head, body = page.split("</thead>")
    assert 'data-row="r1"' in head and 'data-row="r2"' in body and 'data-row="r1"' not in body
    shell = grid.shell(event, spec)
    assert render.projection_problems(shell, render.html(shell)) == []
    assert render.projection_problems(shell, page) != []


@pytest.mark.parametrize(
    ("old", "new", "message"),
    [
        ("2 ( 66.7)</td>", "2 ( 66.8)</td>", "the page has '2 ( 66.8)', the grid '2 ( 66.7)'"),
        ("<tfoot>", "<p>Total: 4</p><tfoot>", "text on the page that is not of the grid"),
        ("</body>", '<script src="x.js"></script></body>',
         "the page refers to something outside itself: <script>"),
        ('<td data-cell="cell:Out_AE/r2/c3">0 </td>', "", "cell cell:Out_AE/r2/c3: the page has"),
        ("Arm A</th>", "Arm Z</th>", "column c1: the page has 'Arm Z'"),
        ("</tr>\n</tbody>", '<td data-cell="cell:Out_AE/r9/c1">9</td></tr>\n</tbody>',
         "on the page, not in the grid"),
    ],
)
def test_a_page_that_says_something_else_is_seen(made, old, new, message):
    page = render.html(made)
    assert old in page
    problems = render.projection_problems(made, page.replace(old, new, 1))
    assert any(message in problem for problem in problems), problems


def test_a_page_with_spanners_and_sections(made):
    value = copy.deepcopy(made)
    value["columns"][0]["spanner"] = value["columns"][1]["spanner"] = "Active"
    value["rows"][1]["section"] = value["rows"][2]["section"] = "Events"
    value["rows"][2]["indent"] = 1
    page = render.html(value)
    assert '<th class="spanner" colspan="2">Active</th><th class="spanner" colspan="1"></th>' \
        in page
    assert 'data-section="1">Events</th>' in page and "padding-left: 2.7em" in page
    assert render.projection_problems(value, page) == []
    # The heading is held against the grid like any other text (real-5a).
    wrong = page.replace('data-section="1">Events</th>', 'data-section="1">Other</th>')
    assert any("section 1: the page has 'Other'" in problem
               for problem in render.projection_problems(value, wrong))
    # A row after the section has none: a separator, and no heading, stands before it.
    extra = copy.deepcopy(value["rows"][1])
    extra.pop("section")
    extra["id"] = "r4"
    for cell in extra["cells"]:
        cell["id"] = cell["id"].replace("/r2/", "/r4/")
    value["rows"].append(extra)
    page = render.html(value)
    assert page.count('<tr class="section"></tr>') == 1
    assert render.projection_problems(value, page) == []


# ---- display.pattern, beyond its vectors ---------------------------------------------


@pytest.mark.parametrize("pattern", ["", "n", "XX XX", "XX.X (XX)", "x.x", None, 5])
def test_a_pattern_without_exactly_one_mask_is_refused(pattern):
    with pytest.raises(methods.MethodError):
        methods.pattern_text(1.0, pattern)


def test_a_mask_with_a_trailing_point_is_a_mask_and_a_point():
    assert methods.pattern_mask("XX.") == ("", "XX", ".")
    assert methods.pattern_text(5, "XX.") == "5."


def test_one_result_may_stand_twice_in_a_cell_under_two_patterns(root, event, rows):
    data = displays.layout_data()
    data["rows"][1].update(cell="{n} of {again}", parts={
        "n": {"operation": "M_CAT_n", "pattern": "XX"},
        "again": {"operation": "M_CAT_n", "pattern": "XX.X"}})
    spec = layout.parse(data)
    made = grid.build(event, spec, rows)
    assert grid.grid_problems(made, root) == []
    assert made["rows"][1]["cells"][0] == {
        "id": "cell:Out_AE/r2/c1", "column": "c1", "text": "2 of  2.0",
        "ard": ["ard:A_AE/M_CAT_n/Arm_A"]}


# ---- the built display of one output, as `specfirst check` judges it -------------------


def judged_display(root, reference, spec, rows, made, shell, pages=None, other_rows=None):
    from specfirst.machine import build

    pages = pages or {"": render.html(made), ".shell": render.html(shell)}
    return build.display_problems(root, reference, spec, made, shell, pages, rows,
                                  rows if other_rows is None else other_rows, {})


def test_the_built_display_of_an_output_and_what_must_not_pass(root, event, spec, made, rows):
    shell = grid.shell(event, spec)
    reference = displays.reference(rows)
    compared, problems = judged_display(root, reference, spec, rows, made, shell)
    assert problems == [] and (compared.cells, compared.equal) == (9, 7)

    def problems_with(**changed):
        given = {"made": made, "shell": shell, **changed}
        return judged_display(root, reference, spec, rows, **given)[1]

    # The second engine at the other side of a rounding: 200 / 3 against a value that is
    # the same within 1e-9 and is shown as 66.6.
    other = {key: dict(row) for key, row in rows.items()}
    other["ard:A_TEAE/M_CAT_pct/Arm_B"]["raw_value"] = 66.64999999999
    assert results.agreement(rows, other, tolerance=1e-3)[1] == []
    assert problems_with(other_rows=other) == [
        "the rows of the second engine give another grid: a value at the edge of a rounding, "
        "or a result one engine lacks"]
    fewer = {key: row for key, row in rows.items() if key != "ard:A_TEAE/M_CAT_pct/Arm_B"}
    assert "1 results of the layout are not in the ARD" in problems_with(other_rows=fewer)[0]
    # A shell that shows a number, or that is not the shell of this layout.
    numbered = copy.deepcopy(shell)
    numbered["rows"][1]["cells"][0]["text"] = "2 ( xx.x)"
    assert problems_with(shell=numbered, pages={
        "": render.html(made), ".shell": render.html(numbered)}) == [
            "the mock shell is not what the layout gives",
            "cell:Out_AE/r2/c1: the mock shell shows a number: '2 ( xx.x)'"]
    relabelled = copy.deepcopy(shell)
    relabelled["rows"][1]["label"] = "Events"
    assert problems_with(shell=relabelled, pages={
        "": render.html(made), ".shell": render.html(relabelled)}) == [
            "the mock shell is not what the layout gives"]
    # A page that is not the page of its grid.
    said = problems_with(pages={"": render.html(shell), ".shell": render.html(shell)})
    assert said and all(problem.startswith("page Out_AE.html: ") for problem in said)
    said = problems_with(pages={"": render.html(made), ".shell": render.html(made)})
    assert said and all(problem.startswith("page Out_AE.shell.html: ") for problem in said)
    # A grid file that is not a grid is reported before anything is compared.
    broken = copy.deepcopy(made)
    del broken["rows"][0]["cells"][0]["ard"]
    compared, said = judged_display(root, reference, spec, rows, broken, shell)
    assert compared.cells == 0 and said and said[0].startswith("grid: ")
