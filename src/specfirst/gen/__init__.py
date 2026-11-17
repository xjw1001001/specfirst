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

Everything here is a pure function of the generator version, the design and
the seed (rule R4): no clock, no unseeded randomness, sorted outputs.
"""

# The version of the generator. Change it whenever the same design and seed
# would give other bytes; every generated file names it.
GENERATOR = "gen-1a.1"
