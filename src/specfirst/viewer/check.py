"""The checks of the review page and of the acceptance of issue #31 (ADR-022).

`page_problems`: the page loads nothing and runs nothing (no script, no
handler, no frame, no image, no style that imports, no link outside the
page, no refresh); every link is to an anchor of the page, and every anchor
is there once; every citation is drawn judged and says, in its own words,
that it awaits approval or who approved it, and is never drawn executed or
static; every decision is drawn with the P4 class the review gives it.

`acceptance`: on the outputs the acceptance names, every printed number
opens a panel; every panel reaches SDTM columns, and a citation or a house
default; every decision record behind the number is drawn in its panel; the
sheet lists every study-level decision (every record, every entry of the
catalog the kit names that applies). Each is decided on the review the page
is written from and then read back from the page itself: the SDTM columns
in the panels' lines "Down to SDTM", the citations and the house defaults
drawn in the panels, the decision blocks of the panels by their key, the
rows of the sheet by their key (the review of issue #31, F3).

What they cannot see: whether a sentence of a panel is right is not held
here; the sentences are those of the scripts of issue #29, whose results
equal the ARD. A citation that a script finds is not thereby approved
(PLAN.md section 4.2).
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser

from specfirst.viewer import model

# What a page that loads or runs nothing must not hold (the review of real-3a, F6).
FORBIDDEN_TAGS = ("script", "iframe", "frame", "img", "object", "embed", "link", "base",
                  "audio", "video", "source", "form", "input", "svg", "image", "use", "picture",
                  "track")
FORBIDDEN_TEXT = ("@import", "url(", "image-set(", "javascript:", "http-equiv")
# Attributes that fetch, on any element: each must be a link to an anchor of the page (the
# review of real-3, F3: background, poster and xlink:href passed).
LINK_ATTRIBUTES = ("href", "src", "action", "srcset", "data", "background", "poster",
                   "xlink:href", "formaction", "lowsrc", "dynsrc", "ping")
APPROVAL = re.compile(r"awaiting approval|approved by \S")


class _Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags: Counter = Counter()
        self.handlers: list[str] = []
        self.hrefs: list[str] = []
        self.ids: list[str] = []
        # Each citation: the classes of its kinds and its own words.
        self.citations: list[tuple[list[str], str]] = []
        self.decisions: list[tuple[str, list[str]]] = []  # (key, classes of its kinds)
        self.texts: list[str] = []
        # The open <li> and <tr> elements: (role, key, kinds, words); role citation,
        # decision or "".
        self._open: list[tuple[str, str, list[str], list[str]]] = []

    def _nearest(self):
        return next((item for item in reversed(self._open) if item[0]), None)

    def handle_starttag(self, tag, attrs):
        self.tags[tag] += 1
        values = dict(attrs)
        self.handlers += [name for name, _ in attrs if name.lower().startswith("on")]
        self.hrefs += [str(value) for name, value in attrs if name.lower() in LINK_ATTRIBUTES]
        if "id" in values:
            self.ids.append(str(values["id"]))
        classes = str(values.get("class") or "").split()
        if tag in ("li", "tr"):
            role = "citation" if "citation" in classes else (
                "decision" if "decision" in classes else "")
            self._open.append((role, str(values.get("data-key") or ""), [], []))
        if "kind" in classes:
            nearest = self._nearest()
            if nearest is not None:
                nearest[2].extend(c for c in classes if c != "kind")

    def handle_endtag(self, tag):
        if tag not in ("li", "tr") or not self._open:
            return
        role, key, kinds, words = self._open.pop()
        if role == "citation":
            self.citations.append((kinds, "".join(words)))
        elif role == "decision":
            self.decisions.append((key, kinds))

    def handle_data(self, data):
        self.texts.append(data)
        nearest = self._nearest()
        if nearest is not None and nearest[0] == "citation":
            nearest[3].append(data)


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
    for number, (kinds, words) in enumerate(parser.citations, start=1):
        if kinds != ["judged"]:
            found.append(f"citation {number} is drawn {', '.join(kinds) or 'without a kind'}, "
                         "not judged")
        if not APPROVAL.search(words):
            found.append(f"citation {number} is not marked awaiting approval or approved by a "
                         "person")
    if review is not None:
        wanted = {key: view.p4 for key, view in review.decisions.items()}
        for key, kinds in parser.decisions:
            if key not in wanted:
                continue
            p4 = wanted[key]
            if p4 == model.UNSEPARATED and "unseparated" not in kinds:
                found.append(f"the decision {key} is unseparated and not drawn so")
            elif p4 == model.NOT_TESTED and "not-tested" not in kinds:
                found.append(f"the decision {key} is not tested and not drawn so")
            elif p4 not in (model.UNSEPARATED, model.NOT_TESTED) and "tested" not in kinds:
                found.append(f"the decision {key} has the P4 class {p4} and is drawn otherwise")
    return found


# What the acceptance reads back from the page (page.py writes them so).
_PANEL = re.compile(r'<section class="panel" id="([^"]+)">(.*?)</section>', re.S)
_CELL = re.compile(r'<div class="cell" id="([^"]+)">')
_LINK = re.compile(r'href="#(c-[^"]+)"')
_SDTM = re.compile(r"Down to SDTM: ((?:<code>[^<]*</code>(?:, )?)+)")
_CODE = re.compile(r"<code>([^<]*)</code>")
_BLOCK = re.compile(r'<li class="decision" data-key="([^"]*)">')
_SHEET = re.compile(r'<section id="sheet">(.*?)</section>', re.S)
_ROW = re.compile(r'<tr class="decision" id="[^"]*" data-key="([^"]*)">')
_HOUSE = 'class="kind house-default"'


@dataclass
class _Drawn:
    """What the page draws, by anchor and key."""

    panels: dict[str, str]  # panel anchor -> its HTML
    cells: dict[str, str]  # cell block anchor -> the anchor of the panel that holds it
    links: set[str]  # the cell anchors a number links to
    sdtm: dict[str, set[str]]  # panel anchor -> the SDTM columns its lines "Down to SDTM" name
    blocks: dict[str, set[str]]  # panel anchor -> the keys of its decision blocks
    sheet: set[str]  # the keys of the rows of the sheet


def _drawn(text: str) -> _Drawn:
    panels = {unescape(m.group(1)): m.group(2) for m in _PANEL.finditer(text)}
    cells = {unescape(m.group(1)): anchor for anchor, body in panels.items()
             for m in _CELL.finditer(body)}
    sdtm = {anchor: {unescape(code) for line in _SDTM.findall(body)
                     for code in _CODE.findall(line)} for anchor, body in panels.items()}
    blocks = {anchor: {unescape(key) for key in _BLOCK.findall(body)}
              for anchor, body in panels.items()}
    sheet = _SHEET.search(text)
    return _Drawn(panels, cells, {unescape(link) for link in _LINK.findall(text)}, sdtm, blocks,
                  {unescape(key) for key in _ROW.findall(sheet.group(1))} if sheet else set())


def _anchor(prefix: str, key: str) -> str:
    return prefix + key.replace(" ", "_")  # as page.py writes it


def acceptance(review: model.Review, text: str, outputs: tuple[str, ...]) -> tuple[list[str],
                                                                                    list[str]]:
    """The acceptance of issue #31 on `outputs`: the lines of the report and the problems."""
    lines, found = [], []
    drawn = _drawn(text)
    for output in outputs:
        view = next((o for o in review.outputs if o.id == output), None)
        if view is None:
            found.append(f"{output}: not an output of the review")
            continue
        numbers = opened = reached = supported = complete = 0
        for row in view.grid["rows"]:
            for cell in row["cells"]:
                if not any(character.isdigit() for character in cell["text"]):
                    continue
                numbers += 1
                anchor = _anchor("c-", cell["id"])
                shown = review.cells.get(cell["id"])
                if shown is None or anchor not in drawn.cells or anchor not in drawn.links:
                    found.append(f"{cell['id']}: prints {cell['text']!r} and opens no panel")
                    continue
                opened += 1
                panels = [_anchor("a-", key) for key in shown.analyses]
                if _reaches_sdtm(review, shown) and _sdtm_drawn(review, shown, drawn, panels):
                    reached += 1
                else:
                    found.append(f"{cell['id']}: its panel reaches no SDTM column through every "
                                 "column it reads")
                if _supported(review, shown) and any(
                        '<li class="citation">' in drawn.panels.get(name, "")
                        or _HOUSE in drawn.panels.get(name, "") for name in panels):
                    supported += 1
                else:
                    found.append(f"{cell['id']}: its panel reaches no citation and no house "
                                 "default")
                blocks = set().union(*(drawn.blocks.get(name, set()) for name in panels))
                missing = [record for key in shown.analyses if key in review.analyses
                           for record in model.behind(review.analyses[key])
                           if record not in blocks]
                if missing:
                    found.append(f"{cell['id']}: its panel does not draw the decision "
                                 f"{missing[0]}")
                else:
                    complete += 1
        lines.append(f"{output}: {numbers} printed numbers; {opened} open a panel; {reached} "
                     f"reach SDTM; {supported} reach a citation or a house default; {complete} "
                     "draw every decision behind them")
    missing = [key for key in review.decisions if key not in drawn.sheet]
    found += [f"the sheet does not list the decision {key}" for key in missing]
    # Every entry of the catalog the kit names, for every unit: a record, or an entry
    # without one (the study-level decisions the study has not written down yet).
    found += [f"the sheet does not list the entry {key} of the catalog"
              for key in review.catalog_keys if key not in drawn.sheet]
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


def _sdtm_drawn(review: model.Review, cell: model.CellView, drawn: _Drawn,
                panels: list[str]) -> bool:
    """The page names, in the lines "Down to SDTM" of the cell's panels, every SDTM column
    the columns read reach."""
    wanted = {code for key in cell.analyses for column, _ in review.analyses[key].columns
              for code in review.columns[column].sdtm}
    shown = set().union(*(drawn.sdtm.get(name, set()) for name in panels))
    return bool(wanted) and wanted <= shown


def _supported(review: model.Review, cell: model.CellView) -> bool:
    """A citation of an analysis behind the cell or of a column it reads, a decision record
    behind it with a citation, or one that is the house default."""
    for key in cell.analyses:
        analysis = review.analyses.get(key)
        if analysis is None:
            continue
        if analysis.cites:
            return True
        for decision in model.behind(analysis):
            view = review.decisions[decision]
            if view.citations or view.mark == model.HOUSE_DEFAULT:
                return True
        if any(review.columns.get(column) and review.columns[column].cites
               for column, _ in analysis.columns):
            return True
    return False
