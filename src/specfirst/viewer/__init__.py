"""The review view of a built kit (issue #31, ADR-022; PLAN.md section 7.5).

One static page per kit, build/kits/<kit>/viewer/index.html, that answers a
reviewer's questions in their order, with the layout out of the way:

- the calculation first: per output, its analyses in sentences and the
  recomputation of each (issue #29); the grid, its titles and footnotes are
  folded;
- every printed number is a link to a side panel: the analysis in sentences
  (who, which records, which groups, which statistic, its options and where
  each comes from); the decision records that bind it, each with its
  standard-form sentence, the alternatives not chosen, its citations and
  whether its value is the house default or customized for the study; the
  ADaM columns it reads, each with why (the decision that binds it) and its
  derivation as the study spec words it, followed down to SDTM; and the
  recomputation of its analysis with the script that ran;
- the study decision sheet: every decision record of the kit, every entry
  of the kit's catalog that applies to the study, the kit's bindings and the
  layout settings, each marked `house default` or `study customized`.

Edges are drawn in five kinds and never merged: executed, static, judged
(a citation: awaiting approval until a person approves it), not proven by
the data (a decision whose P4 class is `unseparated`) and not tested (no P4
run reaches it).

The page has no script and fetches nothing: a panel opens by its anchor and
CSS `:target`, a fold is `<details>`. The same build gives the same bytes.
`specfirst.viewer.check` holds the page and the acceptance of issue #31.
"""

from specfirst.viewer.model import Review, load
from specfirst.viewer.page import html

__all__ = ["Review", "html", "load"]
