"""The review page (issue #31, ADR-022): a Review in, one HTML file out.

The page has no script, loads nothing and states no date, so the same build
gives the same bytes (rule R4). A panel is a `<section class="panel">`
shown by CSS when it is the target of the address or holds it; a cell's own
block in it shows only when it is the target. A fold is `<details>`.

The kinds of an edge stay apart (PLAN.md section 4.2): every judged edge
carries the class `judged` and the words "awaiting approval" until a person
approves it; a decision that the data do not separate carries `unseparated`;
one with another class of a P4 run carries `tested`; one that no P4 run
reached carries `not-tested`.
"""

from __future__ import annotations

from html import escape

from specfirst.viewer import model

STYLE = """
body { font-family: Georgia, serif; margin: 1.5em; margin-right: 47%; color: #111; }
h1 { font-size: 1.4em; } h2 { font-size: 1.2em; margin-top: 2em; } h3 { font-size: 1em; }
code, pre { font-family: "Courier New", monospace; font-size: 0.85em; }
pre { white-space: pre-wrap; background: #f6f6f6; padding: 0.5em; }
table.grid { border-collapse: collapse; margin: 0.5em 0; }
table.grid th, table.grid td { padding: 0.1em 0.8em; vertical-align: top; }
table.grid td { text-align: center; white-space: pre; font-family: "Courier New", monospace; }
table.grid th.stub { text-align: left; font-weight: normal; }
table.sheet { border-collapse: collapse; font-size: 0.85em; }
table.sheet th, table.sheet td { border: 1px solid #bbb; padding: 0.2em 0.4em;
  vertical-align: top; }
a.number { color: #00e; }
.panel { display: none; position: fixed; top: 0; right: 0; width: 45%; height: 100%;
  overflow: auto; box-sizing: border-box; padding: 1em; background: #fff;
  border-left: 3px solid #333; font-size: 0.9em; }
.panel:target, .panel:has(:target) { display: block; }
.cell { display: none; background: #fff8dc; padding: 0.5em; border: 1px solid #cb9; }
.cell:target { display: block; }
.kind { font-size: 0.8em; padding: 0 0.3em; border-radius: 0.2em; white-space: nowrap; }
.executed { background: #d8f0d8; border: 1px solid #393; }
.static { background: #d8e4f8; border: 1px solid #36a; }
.judged { background: #fde8c8; border: 1px dashed #c60; }
.unseparated { background: #f8d0d0; border: 1px solid #a00; }
.tested { background: #e0f4e8; border: 1px solid #296; }
.not-tested { background: #e8e8e8; border: 1px dotted #666; }
.house-default { background: #eef; border: 1px solid #88a; }
.study-customized { background: #fee; border: 1px solid #a88; }
"""

LEGEND = (
    ("executed", "proven by execution: the grid builder put the result in the cell, the "
                 "engine computed it"),
    ("static", "static: read from the specification or the ARS file by a script"),
    ("judged", "judged: a citation; a script checks only that its quote stands in the "
               "document; a person must approve that it supports the decision"),
    ("unseparated", "not proven by the data: P4 finds another value of the decision that "
                    "gives the same results"),
    ("tested", "tested by P4: a run of the decision's other values on the data gives its "
               "class (separated, inert, or separated at dataset level only)"),
    ("not-tested", "not tested: no P4 run reaches the decision"),
)


def _kind(name: str, text: str | None = None) -> str:
    css = name.replace(" ", "-")
    return f'<span class="kind {escape(css)}">{escape(text or name)}</span>'


def _anchor(prefix: str, key: str) -> str:
    return prefix + key.replace(" ", "_")


def _citation(item: model.Citation) -> str:
    approval = (f"approved by {escape(item.approved_by)}" if item.approved_by
                else "awaiting approval")
    if not item.text:
        return (f'<li class="citation">{_kind("judged")} <code>{escape(item.target)}</code> '
                f"({escape(item.origin)}; it names a span and carries no quote to check; "
                f"{approval})</li>")
    if item.verified:
        found = "a script finds the quote in the document"
    elif item.checkable:
        found = "a script does not find the quote in the document"
    else:
        found = "no document of the kit: no script checks it"
    return (f'<li class="citation">{_kind("judged")} <code>{escape(item.target)}</code>: '
            f"&ldquo;{escape(item.text)}&rdquo; ({escape(item.origin)}; {found}; "
            f"{approval})</li>")


def _p4(text: str) -> str:
    if text == model.UNSEPARATED:
        return _kind("unseparated", "not proven by the data: unseparated")
    if text == model.NOT_TESTED:
        return _kind("not-tested")
    return _kind("tested", f"P4: {text}")


def _decision(view: model.DecisionView, via: str = "") -> str:
    parts = [f'<li class="decision" data-key="{escape(view.key)}">'
             f'<a href="#{escape(_anchor("s-", view.key))}"><b>{escape(view.key)}</b></a> '
             f"{_kind(view.mark)} {_p4(view.p4)}{via}<br>{escape(view.statement)}",
             f"<br>status {escape(view.status)}, class "
             f"{escape(view.klass or 'none (a person decides)')}; value "
             f"<code>{escape(view.value)}</code>; in {escape(view.source)}"]
    if view.citations:
        parts.append("<ul>" + "".join(_citation(c) for c in view.citations) + "</ul>")
    else:
        parts.append("<br>No citation.")
    if view.mark == model.HOUSE_DEFAULT:
        parts.append("<br>The house's source for its default: " + (
            "; ".join(escape(s) for s in view.house_sources) if view.house_sources
            else "the house gives none") + ".")
    if view.alternatives:
        parts.append("<br>Alternatives not chosen:<ul>" + "".join(
            f"<li>{escape(text)}</li>" for text in view.alternatives) + "</ul>")
    elif view.id.startswith("custom:"):
        parts.append("<br>Alternatives not chosen: none listed; a custom record (the catalog "
                     "has no entry for it).")
    return "".join(parts) + "</li>"


def _via(bound: str, read: str) -> str:
    if bound == read:
        return f"<br>It binds <code>{escape(bound)}</code>, which the analysis reads."
    return (f"<br>It binds <code>{escape(bound)}</code>, from which "
            f"<code>{escape(read)}</code>, which the analysis reads, derives.")


def _column(review: model.Review, column_id: str, roles: list[str]) -> str:
    view = review.columns.get(column_id)
    if view is None:
        return (f"<li><code>{escape(column_id)}</code> ({escape(', '.join(roles))}): no node "
                "in the graph</li>")
    why = (", ".join(f'<a href="#{escape(_anchor("s-", key))}">{escape(key)}</a>'
                     for key in view.decisions)
           if view.decisions else "no decision record binds it: the ARS analysis names it and "
                                  "the study spec builds it")
    out = [f"<li><code>{escape(column_id)}</code> {escape(view.label)} "
           f"({escape(', '.join(roles))}) {_kind('static', 'reads')}",
           f"<br>Why this column: {why}."]
    out.append(_derivation(view))
    chain, seen, queue = [], {column_id}, list(view.derives)
    while queue:
        name = queue.pop(0)
        if name in seen:
            continue
        seen.add(name)
        other = review.columns.get(name)
        if other is None or name.startswith("sdtm:"):
            continue
        chain.append(f"<li><code>{escape(name)}</code> {escape(other.label)}"
                     f"{_derivation(other)}</li>")
        queue += other.derives
    if chain:
        out.append(f"<br>It derives from {_kind('static', 'derives_from')}:<ul>"
                   + "".join(chain) + "</ul>")
    out.append("<br>Down to SDTM: " + (
        ", ".join(f"<code>{escape(s)}</code>" for s in view.sdtm)
        or ("no SDTM column: a literal of the study spec, built on rows only"
            if view.terminal == "literal" else "no SDTM column")) + ".")
    if view.cites:
        out.append("<br>Citations of the column:<ul>"
                   + "".join(_citation(c) for c in view.cites) + "</ul>")
    return "".join(out) + "</li>"


def _derivation(view: model.ColumnView) -> str:
    said = []
    if view.comment:
        said.append(f"<br>Its derivation, in the study spec's words (the Define-XML comment): "
                    f"&ldquo;{escape(view.comment)}&rdquo;")
    if view.rule:
        said.append(f"<br>The rule that runs ({escape(view.source)}): "
                    f"<code>{escape(view.rule)}</code>")
    elif view.source:
        said.append(f"<br>Defined at {escape(view.source)}.")
    return "".join(said)


def _panel(review: model.Review, view: model.AnalysisView) -> str:
    out = [f'<section class="panel" id="{escape(_anchor("a-", view.key))}">',
           f"<h2>{escape(view.id)}</h2><p>{escape(view.name)} (reporting event "
           f"{escape(view.event)})</p>"]
    for cell in sorted((c for c in review.cells.values() if c.analysis == view.key),
                       key=lambda c: c.id):
        rows = "".join(
            f"<li><code>{escape(key)}</code>: operation {escape(op)}, value "
            f"<code>{escape(value)}</code></li>" for key, op, value in cell.results)
        others = [k for k in cell.analyses if k != view.key]
        more = ("<br>Also computed from: " + ", ".join(
            f'<a href="#{escape(_anchor("a-", k))}">{escape(k)}</a>' for k in others)
            + " (a denominator).") if others else ""
        out.append(f'<div class="cell" id="{escape(_anchor("c-", cell.id))}"><b>'
                   f"{escape(cell.text)}</b> in {escape(cell.output)}, row "
                   f"{escape(cell.row)}, column {escape(cell.column)} {_kind('executed')}"
                   f"<ul>{rows}</ul>{more}</div>")
    out.append("<h3>1. The analysis</h3><ul>"
               + "".join(f"<li>{escape(s)}</li>" for s in view.sentences) + "</ul>")
    if view.options:
        out.append("<p>Its options:</p><ul>"
                   + "".join(f"<li>{escape(o)}</li>" for o in view.options) + "</ul>")
    if view.cites:
        out.append("<p>Where the ARS file says it comes from:</p><ul>"
                   + "".join(_citation(c) for c in view.cites) + "</ul>")
    out.append("<h3>2. The decisions behind it</h3>")
    if view.decisions:
        out.append("<p>Of the analysis and its elements:</p><ul>" + "".join(
            _decision(review.decisions[key]) for key in view.decisions) + "</ul>")
    else:
        out.append("<p>No decision record of the kit binds this analysis or its elements.</p>")
    if view.column_decisions:
        out.append("<p>Of the columns it reads, and of the columns those derive from:</p><ul>"
                   + "".join(_decision(review.decisions[key], _via(bound, read))
                             for key, bound, read in view.column_decisions) + "</ul>")
    out.append("<h3>3. The ADaM columns it reads</h3><ul>"
               + "".join(_column(review, column, roles) for column, roles in view.columns)
               + "</ul>")
    out.append("<h3>4. The recomputation</h3>")
    if view.recompute is None:
        out.append("<p>No recomputation of this analysis (specfirst recompute).</p>")
    else:
        item = view.recompute
        detail = ", ".join(f"{k} {item[k]}" for k in sorted(item)
                           if k not in ("analysis", "event", "status"))
        out.append(f"<p><b>{escape(str(item['status']))}</b> ({escape(detail)}); a standalone "
                   "script, run sealed on the reference ADaM (issue #29).</p>")
    if view.script is not None:
        out.append(f"<details><summary>The script that ran: {escape(view.script[0])}"
                   f"</summary><pre>{escape(view.script[1])}</pre></details>")
    out.append("</section>")
    return "\n".join(out)


def _grid(review: model.Review, output: model.OutputView) -> str:
    grid = output.grid
    out = ['<table class="grid"><thead><tr><th class="stub"></th>']
    out += [f"<th>{escape(column['label'])}</th>" for column in grid["columns"]]
    out.append("</tr></thead><tbody>")
    for row in grid["rows"]:
        label = ("&nbsp;" * 3 * int(row.get("indent", 0))) + escape(row["label"])
        out.append(f'<tr><th class="stub">{label}</th>')
        for cell in row["cells"]:
            if cell["id"] in review.cells:
                out.append(f'<td><a class="number" href="#{escape(_anchor("c-", cell["id"]))}">'
                           f"{escape(cell['text'])}</a></td>")
            else:
                out.append(f"<td>{escape(cell['text'])}</td>")
        out.append("</tr>")
    out.append("</tbody></table>")
    return "".join(out)


def _output(review: model.Review, output: model.OutputView) -> str:
    grid = output.grid
    title = " ".join(grid.get("titles") or [output.id])
    out = [f'<section class="output" id="{escape(_anchor("o-", output.id))}">',
           f"<h2>{escape(output.id)}: {escape(title)}</h2>",
           "<h3>The calculation</h3><ol>"]
    for key in output.analyses:
        view = review.analyses[key]
        status = view.recompute["status"] if view.recompute else "not recomputed"
        out.append(f'<li><a href="#{escape(_anchor("a-", key))}">{escape(view.id)}</a>: '
                   f"{escape(view.name)}. {escape(view.sentences[0])} "
                   f"Recomputed: <b>{escape(str(status))}</b>.</li>")
    out.append("</ol>")
    out.append(f"<details><summary>The grid (folded): {len(grid['rows'])} rows; every number "
               f"opens its panel</summary>{_grid(review, output)}</details>")
    texts = "".join(f"<li>{escape(t)}</li>" for t in [*grid.get("titles", []),
                                                      *grid.get("footnotes", [])])
    out.append(f"<details><summary>Titles and footnotes (folded)</summary><ul>{texts}</ul>"
               "</details>")
    out.append("<details><summary>RTF (folded)</summary><p>Not built: the machine renders a "
               "grid to HTML only (specfirst.machine.render).</p></details>")
    out.append("</section>")
    return "\n".join(out)


def _sheet(review: model.Review) -> str:
    out = ['<section id="sheet"><h2>The study decision sheet</h2>',
           "<p>Every decision of the study, for the person who accepts or changes it: the "
           "kit's decision records, the entries of the catalog the kit names that no record "
           "takes, the kit's bindings and the layouts. Marked house default or study "
           "customized; every citation is judged and awaits approval.</p>",
           '<table class="sheet"><thead><tr><th>kind</th><th>decision</th><th>unit</th>'
           "<th>statement</th><th>status</th><th>class</th><th>mark</th><th>citations</th>"
           "<th>P4</th><th>cells</th></tr></thead><tbody>"]
    for line in review.sheet:
        cites = "<ul>" + "".join(_citation(c) for c in line.citations) + "</ul>" \
            if line.citations else ""
        out.append(f'<tr class="decision" id="{escape(_anchor("s-", line.key))}" '
                   f'data-key="{escape(line.key)}"><td>{escape(line.kind)}</td>'
                   f"<td>{escape(line.key)}</td>"
                   f"<td>{escape(line.unit)}</td><td>{escape(line.text)}</td>"
                   f"<td>{escape(line.status)}</td><td>{escape(line.klass)}</td>"
                   f"<td>{_kind(line.mark)}</td><td>{cites}</td><td>{_p4(line.p4)}</td>"
                   f"<td>{line.cells}</td></tr>")
    out.append("</tbody></table></section>")
    return "\n".join(out)


def html(review: model.Review) -> str:
    """The page of a review."""
    standard = (f"catalog {review.standard[0]}, house {review.standard[1]}"
                if review.standard else "no catalog named by the kit")
    head = ['<!DOCTYPE html>', '<html lang="en"><head><meta charset="utf-8">',
            f"<title>Review of {escape(review.kit)}</title><style>{STYLE}</style></head><body>",
            f"<h1>Review of the kit {escape(review.kit)}</h1>",
            f"<p>The calculation first. Standard: {escape(standard)}. Click a number for its "
            "panel. The kinds of an edge:</p><ul>"]
    head += [f"<li>{_kind(name)} {escape(text)}</li>" for name, text in LEGEND]
    head.append("</ul><p>Outputs: " + ", ".join(
        f'<a href="#{escape(_anchor("o-", o.id))}">{escape(o.id)}</a>' for o in review.outputs)
        + '; <a href="#sheet">the study decision sheet</a>.</p>')
    if review.problems:
        head.append("<p>What the review could not read:</p><ul>"
                    + "".join(f"<li>{escape(p)}</li>" for p in review.problems) + "</ul>")
    body = [_output(review, output) for output in review.outputs]
    body.append(_sheet(review))
    panels = [_panel(review, review.analyses[key]) for key in sorted(review.analyses)]
    return "\n".join([*head, *body, *panels, "</body></html>"]) + "\n"
