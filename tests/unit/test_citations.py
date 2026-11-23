"""The page references of an ARS file as candidate `cites` edges (issue #31, ADR-022).

On the made-up output of tests/toy_displays.py: the analysis A_AE names page 2 of the
kit's SAP, its method M_CAT names page 3, and A_AE also names a page of a CSR the kit does
not hold; A_TEAE names a section of the SAP without a page. The pages are given as text by
hand. The edges must be judged, imported and unapproved; a quote is verified only where the
label stands on its page, or anywhere in the document for a reference without a page (rule
R5: the label of page 3 is not there, and that edge says so).
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import toy_displays as displays
import toy_results as toy

from specfirst import schemas
from specfirst.machine import ars, graph, grid, layout

PAGES = {2: "6. ANALYSIS POPULATIONS\nThe safety population ...", 3: "8. EFFICACY\n..."}


@dataclass(frozen=True)
class Document:
    id: str
    file: str
    cited_as: tuple[str, ...]


@dataclass(frozen=True)
class File:
    path: str
    sha256: str


class Kit:
    documents = (Document("sap", "inputs/docs/sap.pdf", ("SAP_X",)),)
    files = (File("inputs/docs/sap.pdf", "0" * 64),)

    def document(self, name: str):
        return next((d for d in self.documents if name == d.file or name in d.cited_as), None)


def ref(document: str, label: str, page: int | None) -> dict:
    page_ref = {"refType": "PhysicalRef", "label": label}
    if page is not None:
        page_ref["pageNumbers"] = [page]
    return {"referenceDocumentId": document, "pageRefs": [page_ref]}


def traced(root, tmp_path):
    data = displays.event_data()
    for analysis in data["analyses"]:
        if analysis["id"] == "A_AE":
            analysis["documentRefs"] = [ref("SAP_X", "6. ANALYSIS POPULATIONS", 2),
                                        ref("CSR_X", "Table 14-1", 40)]
        if analysis["id"] == "A_TEAE":
            analysis["documentRefs"] = [ref("SAP_X", "8. EFFICACY", None)]
    for method in data["methods"]:
        if method["id"] == "M_CAT":
            method["documentRefs"] = [ref("SAP_X", "7. GENERAL CONSIDERATIONS", 3)]
    (tmp_path / "event.json").write_text(json.dumps(data, indent=1), encoding="ascii")
    event = ars.index(data)
    rows = toy.run(root, data)
    made = grid.build(event, layout.parse(displays.layout_data()), rows)
    shown = graph.Display(grid=made, grid_file="gold/grid/Out_AE.json", event=event,
                          ars_file="event.json", ard_file="gold/ard/toy.jsonl",
                          rows=list(rows.values()), subject_key="USUBJID")
    result = graph.Graph(nodes=[], edges=[], coverage={"columns": []})
    graph.add_displays(result, tmp_path, [shown])
    asked = []

    def page_text(path, page):
        asked.append((path.name, page))
        return "\n".join(PAGES.values()) if page is None else PAGES[page]

    graph.add_citations(result, Kit(), tmp_path, [shown], page_text)
    return result, asked


def test_page_references_become_judged_imported_unapproved_edges(root, tmp_path):
    result, asked = traced(root, tmp_path)
    cites = {(edge["from"], edge["to"]): edge for edge in result.edges if edge["type"] == "cites"}
    populations = "doc:sap#2/6.%20ANALYSIS%20POPULATIONS"
    general = "doc:sap#3/7.%20GENERAL%20CONSIDERATIONS"
    efficacy = "doc:sap#8.%20EFFICACY"
    # The analysis's own reference, and its method's for every analysis of that method.
    assert sorted(cites) == [("ars:A_AE", populations), ("ars:A_AE", general),
                             ("ars:A_TEAE", general), ("ars:A_TEAE", efficacy)]
    for edge in cites.values():
        assert (edge["proof"], edge["origin"], edge["approved_by"]) == (
            "judged", "imported", None)
    # The label of page 2 stands there; that of page 3 does not.
    assert cites[("ars:A_AE", populations)]["quote_verified"] is True
    assert cites[("ars:A_AE", general)]["quote_verified"] is False
    # A reference without a page names the document as a whole; its label stands in it.
    assert cites[("ars:A_TEAE", efficacy)]["quote_verified"] is True
    span = next(node for node in result.nodes if node["id"] == populations)
    assert (span["layer"], span["kind"], span["label"]) == ("L0", "span",
                                                            "6. ANALYSIS POPULATIONS")
    # A page, or the whole document, is read once, however many edges it has.
    assert sorted(asked, key=str) == [("sap.pdf", 2), ("sap.pdf", 3), ("sap.pdf", None)]
    assert result.coverage["documents"] == {
        "cites_edges_of_analyses": 4, "quotes_verified": 2, "edges_to_a_whole_document": 1,
        "references_not_to_kit_documents": {"CSR_X": 1}}
    for part, records in (("node", result.nodes), ("edge", result.edges)):
        validator = schemas.validator("graph", part, root)
        assert [error.message for record in records
                for error in validator.iter_errors(record)] == []
