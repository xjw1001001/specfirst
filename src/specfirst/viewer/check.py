"""The checks of the review page and of the acceptance of issue #31 (ADR-022).

`page_problems`: the page loads nothing and runs nothing (no script, no
handler, no frame, no image, no style that imports, no link outside the
page, no refresh); every link is to an anchor of the page, and every anchor
is there once; every citation is drawn judged, approved or awaiting
approval, and never executed or static; every decision is drawn with the
P4 class the review gives it.

`acceptance`: on the outputs the acceptance names, every printed number
opens a panel; every panel reaches SDTM columns, and a citation or a house
default; the sheet lists every study-level decision (every record, every
entry of the catalog the kit names that applies, every binding and layout of
the kit).

What they cannot see: whether a sentence of a panel is right is not held
here; the sentences are those of the scripts of issue #29, whose results
equal the ARD. A citation that a script finds is not thereby approved
(PLAN.md section 4.2).
"""

from __future__ import annotations

import re
from collections import Counter
from html.parser import HTMLParser

from specfirst.viewer import model

# What a page that loads or runs nothing must not hold (the review of real-3a, F6).
FORBIDDEN_TAGS = ("script", "iframe", "frame", "img", "object", "embed", "link", "base",
                  "audio", "video", "source", "form", "input")
FORBIDDEN_TEXT = ("@import", "url(", "javascript:", "http-equiv")


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags: Counter = Counter()
        self.handlers: list[str] = []
        self.hrefs: list[str] = []
        self.ids: list[str] = []
        self.citations: list[list[str]] = []  # the classes of the kinds in each citation
        self.decisions: list[tuple[str, list[str]]] = []  # (key, classes of its kinds)
        self.texts: list[str] = []
        # The open <li> and <tr> elements: (role, kinds); role citation, decision or "".
        self._open: list[tuple[str, str, list[str]]] = []

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        values = dict(attrs)
        self.handlers += [name for name, _ in attrs if name.lower().startswith("on")]
        if "href" in values:
            self.hrefs.append(str(values["href"]))
        for name in ("src", "action", "srcset", "data"):
            if name in values:
                self.hrefs.append(str(values[name]))
        if "id" in values:
            self.ids.append(str(values["id"]))
        classes = str(values.get("class") or "").split()
        if tag in ("li", "tr"):
            role = "citation" if "citation" in classes else (
                "decision" if "decision" in classes else "")
            self._open.append((role, str(values.get("data-key") or ""), []))
        if "kind" in classes:
            kinds = [c for c in classes if c != "kind"]
            for role, _, held in reversed(self._open):  # the nearest citation or decision
                if role:
                    held += kinds
                    break

    def handle_endtag(self, tag):
        if tag not in ("li", "tr") or not self._open:
            return
        role, key, kinds = self._open.pop()
        if role == "citation":
            self.citations.append(kinds)
        elif role == "decision":
            self.decisions.append((key, kinds))

    def handle_data(self, data):
        self.texts.append(data)


def page_problems(text: str, review: model.Review | None = None) -> list[str]:
    """Why a review page is not a page that loads nothing and draws every kind apart."""
    found = []
    parser = _Page()
    parser.feed(text)
    parser.close()
    found += [f"the page has a <{tag}>" for tag in FORBIDDEN_TAGS if parser.tags[tag]]
    found += [f"the page has the handler '{name}'" for name in sorted(set(parser.handlers))]
    lowered = text.lower()
    found += [f"the page holds '{word}'" for word in FORBIDDEN_TEXT if word in lowered]
    if re.search(r"<meta[^>]*refresh", lowered):
        found.append("the page refreshes itself")
    ids = Counter(parser.ids)
    found += [f"the anchor '{name}' stands {count} times" for name, count in sorted(ids.items())
              if count > 1]
    for href in sorted(set(parser.hrefs)):
        if not href.startswith("#"):
            found.append(f"the link '{href}' leaves the page")
        elif href[1:] not in ids:
            found.append(f"the link '{href}' has no anchor on the page")
    for number, kinds in enumerate(parser.citations, start=1):
        if kinds != ["judged"]:
            found.append(f"citation {number} is drawn {', '.join(kinds) or 'without a kind'}, "
                         "not judged")
    words = " ".join(parser.texts)
    count = len(parser.citations)
    marked = words.count("awaiting approval") + len(re.findall(r"approved by \S", words))
    if count and marked < count:
        found.append(f"{count} citations, {marked} of them marked awaiting approval or "
                     "approved by a person")
    if review is not None:
        wanted = {key: view.p4 for key, view in review.decisions.items()}
        for key, kinds in parser.decisions:
            if key not in wanted:
                continue
            p4 = wanted[key]
            if p4 == model.UNSEPARATED and "unseparated" not in kinds:
                found.append(f"the decision {key} is unseparated and not drawn so")
            if p4 == model.NOT_TESTED and "not-tested" not in kinds:
                found.append(f"the decision {key} is not tested and not drawn so")
            if p4 not in (model.UNSEPARATED, model.NOT_TESTED) and (
                    "unseparated" in kinds or "not-tested" in kinds):
                found.append(f"the decision {key} has the P4 class {p4} and is drawn otherwise")
    return found


def acceptance(review: model.Review, text: str, outputs: tuple[str, ...]) -> tuple[list[str],
                                                                                    list[str]]:
    """The acceptance of issue #31 on `outputs`: the lines of the report and the problems."""
    lines, found = [], []
    anchors = set(re.findall(r'id="(c-[^"]+)"', text))
    links = set(re.findall(r'href="#(c-[^"]+)"', text))
    for output in outputs:
        view = next((o for o in review.outputs if o.id == output), None)
        if view is None:
            found.append(f"{output}: not an output of the review")
            continue
        numbers = opened = reached = supported = 0
        for row in view.grid["rows"]:
            for cell in row["cells"]:
                if not any(character.isdigit() for character in cell["text"]):
                    continue
                numbers += 1
                anchor = "c-" + cell["id"].replace(" ", "_")
                shown = review.cells.get(cell["id"])
                if shown is None or anchor not in anchors or anchor not in links:
                    found.append(f"{cell['id']}: prints {cell['text']!r} and opens no panel")
                    continue
                opened += 1
                if _reaches_sdtm(review, shown):
                    reached += 1
                else:
                    found.append(f"{cell['id']}: its panel reaches no SDTM column through every "
                                 "column it reads")
                if _supported(review, shown):
                    supported += 1
                else:
                    found.append(f"{cell['id']}: its panel reaches no citation and no house "
                                 "default")
        lines.append(f"{output}: {numbers} printed numbers; {opened} open a panel; {reached} "
                     f"reach SDTM; {supported} reach a citation or a house default")
    listed = {line.key for line in review.sheet}
    missing = [key for key in review.decisions if key not in listed]
    found += [f"the sheet does not list the decision {key}" for key in missing]
    by_kind = Counter(line.kind for line in review.sheet)
    lines.append("sheet: " + ", ".join(f"{count} {kind}" for kind, count in sorted(
        by_kind.items())) + f"; {len(review.decisions) - len(missing)} of "
        f"{len(review.decisions)} records listed")
    return lines, found


def _reaches_sdtm(review: model.Review, cell: model.CellView) -> bool:
    """Every analysis behind the cell reads columns that are nodes; every one of them reaches
    SDTM columns through its derives_from edges, or is a literal that coverage.json records
    (built on rows only, PLAN.md 4.6); and together they reach SDTM. A column that coverage.json
    records as reaching SDTM and whose edges reach none is a broken path."""
    reached = set()
    for key in cell.analyses:
        analysis = review.analyses.get(key)
        if analysis is None or not analysis.columns:
            return False
        for column, _ in analysis.columns:
            view = review.columns.get(column)
            if view is None or view.terminal == "gap":
                return False
            if not view.sdtm and view.terminal != "literal":
                return False
            reached |= set(view.sdtm)
    return bool(reached)


def _supported(review: model.Review, cell: model.CellView) -> bool:
    """A citation of an analysis behind the cell or of a column it reads, a decision record
    with a citation, or a decision that is the house default."""
    for key in cell.analyses:
        analysis = review.analyses.get(key)
        if analysis is None:
            continue
        if analysis.cites:
            return True
        for decision in analysis.decisions:
            view = review.decisions[decision]
            if view.citations or view.mark == model.HOUSE_DEFAULT:
                return True
        if any(review.columns.get(column) and review.columns[column].cites
               for column, _ in analysis.columns):
            return True
    return False
