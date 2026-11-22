"""Run one Python recomputation script with the engine out of reach (issue #29, ADR-021).

    python -I seal.py <script> <arguments of the script> ...

Copied next to the script into a fresh folder by `specfirst.recompute.run`
and run as a program, never imported. Before the script runs it installs an
audit hook (PEP 578), which no code can remove afterwards: the hook refuses
the import of any module of specfirst or yamaa, and every open by Python of a
file under the folders of SPECFIRST_SEAL_FENCE (the checkout and the build,
which hold the engine, the built ADaM and the ARD). Then it runs the script
and, whatever the script raised, fails when a module of specfirst or yamaa
was loaded.

What it does not hold: a read that does not go through Python's open (a
library's own C code, such as pyarrow's Parquet reader), and R, which has no
such hook; for those the static check pins the form of every read. It is
part of the check, not of the bundle a reviewer runs.
"""

import importlib.abc
import os
import runpy
import sys

REFUSED = ("specfirst", "yamaa")
FENCE = tuple(os.path.abspath(p) + os.sep
              for p in os.environ.get("SPECFIRST_SEAL_FENCE", "").split(os.pathsep) if p)


def fenced(path) -> bool:
    if isinstance(path, int):
        return False  # a file descriptor: its open was audited when it was made
    try:
        text = os.path.abspath(os.fsdecode(path))
    except (TypeError, ValueError):
        return True
    return any(text == p.rstrip(os.sep) or text.startswith(p) for p in FENCE)


def audit(event, args):
    if event == "import" and str(args[0]).split(".")[0] in REFUSED:
        raise ImportError(f"refused by the sealed run: {args[0]}")
    if event == "open" and FENCE and fenced(args[0]):
        raise PermissionError(f"refused by the sealed run: an open of {args[0]}")


class Refuse(importlib.abc.MetaPathFinder):
    def find_spec(self, name, path=None, target=None):
        if name.split(".")[0] in REFUSED:
            raise ImportError(f"refused by the sealed run: {name}")
        return None


def loaded() -> list[str]:
    return sorted(name for name in sys.modules if name.split(".")[0] in REFUSED)


if __name__ == "__main__":
    sys.addaudithook(audit)
    sys.meta_path.insert(0, Refuse())
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    try:
        runpy.run_path(script, run_name="__main__")
    finally:
        if loaded():
            sys.exit("sealed run: engine modules were loaded: " + ", ".join(loaded()))
