"""Scoring: reading score, build score, attribution, planted defects (read-1).

PLAN.md section 9. read-1a (ADR-005) has the scorer for the slice "adverse
event summary first":

    reading     a candidate's decision records against gold (section 9.1)
    build       what two builds give, compared: the scores of ADR-005,
                decision 4 (section 9.2)
    attribute   the layer and the decision that own a wrong cell (9.4)
    candidate   build a decision vector on a dataset, as gen-2a builds gold
    scorer      a candidate on a case; the arms S and C
    defects     the planted defects of section 9.5 that apply to the slice
    hand        HAND01, a study small enough to check by hand
    kit         a generated kit as a case; a set of kits scored
    pilot       CDISCPILOT01, report only
    gate        the checks of `specfirst gate read-1a`

The choices are in docs/decisions/ADR-008.md.
"""
