"""Rerun the evidence spikes on the fetch cache (PLAN.md section 3.1).

Slow (about 7 minutes) and needs `specfirst fetch`, so these tests carry the
marker `evidence`: `make test` leaves them out, `specfirst gate base-0` runs
them. A missing prerequisite skips the test, except under SPECFIRST_STRICT=1
(set by the gate), where it fails: a gate never passes by skipping.
"""

from __future__ import annotations

import os

import pytest
from evidence_cases import CASES, Env, EvidenceError

from specfirst.paths import build_dir, cache_dir, repo_root

pytestmark = pytest.mark.evidence


@pytest.fixture(scope="session")
def env(tmp_path_factory) -> Env:
    root = repo_root()
    return Env(root=root, cache=cache_dir(root), work=tmp_path_factory.mktemp("evidence"))


@pytest.mark.parametrize("case", CASES, ids=[case.id for case in CASES])
def test_evidence(case, env):
    try:
        out = case.run(env)
    except EvidenceError as error:
        if os.environ.get("SPECFIRST_STRICT") == "1":
            pytest.fail(str(error))
        pytest.skip(str(error))
    saved = build_dir(env.root) / "evidence"
    saved.mkdir(parents=True, exist_ok=True)
    (saved / f"{case.id}.txt").write_text(out, encoding="utf-8", newline="\n")
    print(f"\n--- {case.id}: {case.shows}\n{out.rstrip()}")
    problems = case.check(out)
    assert not problems, "\n".join(problems)
