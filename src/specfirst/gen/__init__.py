"""The generator of Tier A studies (PLAN.md section 6).

    design.py     the design model: what design.yaml holds, its features
    pgfix.py      the archetype PG-FIX: preset, ranges, sampler (stage S1)
    rng.py        seeded random streams that do not depend on a library version
    subjects.py   the subject process: latent truth per subject (stage S2)
    probes.py     probe recipes: plant them, find them again in SDTM (stage S3)
    sdtm.py       SDTM domains from the latent truth (stage S4)
    datasetjson.py, define.py   Dataset-JSON 1.1 and Define-XML 2.1 writers
    study.py      one study folder: visible data, twin, probes.jsonl, manifest
    gate.py       the checks of the gate gen-1a
    decisions.py  the decisions of a study, sampled within the house standard (stage S1)
    gold.py       gold from decisions: specs, ADaM, results, grid, graph (stage S5)
    display.py    the grid of a compiled house layout (layout draft 0)
    reference.py  the reference of a generated study: the output calculated by hand
    verify.py     the properties P2, P3 and P4 of a kit (stage S7)
    kits.py       one kit: data, decisions, gold, twin, manifest; P1; splits
    gate2.py      the checks of the gate gen-2a
    documents.py  protocol and SAP, standard and natural form; tiers; oracle (stage S6)
    natural.py    the natural form: the store of model text, slot and read-back checks
    gate3.py      the checks of the gate gen-3a

Everything here is a pure function of the generator version, the design and
the seed (rule R4): no clock, no unseeded randomness, sorted outputs.
"""

# The version of the generator. Change it whenever the same design and seed
# would give other bytes; every generated file names it. catalog-2c.1: the slice on
# catalog@2 and open-default@2 (ADR-020, decision 8 as amended).
GENERATOR = "catalog-2c.1"
