"""Standalone recomputation scripts, one per analysis (issue #29, ADR-021).

From a kit's ARS analyses, their decision records and the method registry,
`specfirst recompute <kit>` writes one short script per analysis, in Python
or R, that recomputes the analysis's results from the reference ADaM with
standard packages only. The scripts import, source and read no part of the
specfirst engine (static.py and seal.py check it; see there what they do not
hold): the package that writes them reads the ARS file, kit.yaml, the decision
records and registry.json as plain data and imports nothing of the engine's
computation (`specfirst.machine.ars`, `ard`, `methods`, `rengine`, `build`,
`results`, ...). The scripts' results are compared with the gold ARD at full
precision, and each analysis is reported `reproduced`, `differs` or
`not covered`.

    reading    the generator's own reading of an ARS reporting event
    pywrite    the Python scripts (descriptive methods, chi-square, ANOVA)
    rwrite     the R scripts (Fisher, CMH, ANCOVA, the mixed model)
    generate   the bundle: scripts, plan, ARD rows, manifest, README
    static     the static check of a script: imports, calls, reads, texts, numbers
    run        the sealed run of a bundle and its report
    bundle/    the standalone files the bundle carries (no specfirst import)
"""
