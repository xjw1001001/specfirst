"""Run one Python recomputation script with the engine out of reach (issue #29, ADR-021).

    python -I seal.py <script> <arguments of the script> ...

Copied next to the script into a fresh folder by `specfirst.recompute.run`
and run as a program, never imported. It refuses every import of specfirst
or yamaa, runs the script, and fails when any module of them was loaded.
It is part of the check, not of the bundle a reviewer runs.
"""

import importlib.abc
import runpy
import sys

REFUSED = ("specfirst", "yamaa")


class Refuse(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in REFUSED:
            raise ImportError(f"refused by the sealed run: {name}")
        return None


if __name__ == "__main__":
    sys.meta_path.insert(0, Refuse())
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    runpy.run_path(script, run_name="__main__")
    loaded = sorted(name for name in sys.modules if name.split(".")[0] in REFUSED)
    if loaded:
        sys.exit("sealed run: engine modules were loaded: " + ", ".join(loaded))
