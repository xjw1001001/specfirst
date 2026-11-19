"""The table by system organ class and preferred term counts the pairs that occur (issue #27).

Each preferred term lies in one organ class. The compiled ARS file of
`tfl-ae-soc-pt` groups the analysis by preferred term by treatment, AESOC
and AEDECOD; the two term groupings are data-driven, as in CDISC's example
"Common Safety Displays", so rule I9 gives the combinations that occur
together on a record. The listing of groups before the engines run
(`specfirst.gen.gold.resolve_groupings`) once listed the term groupings
too, and rule I10 then crossed every organ class with every term: arms x
SOCs x PTs results, most of them of a pair that cannot occur
(docs/decisions/ADR-011.md).

The data are invented and seeded, the case of the issue at its two sizes:
stage T (ADSL and ADAE given), every term in one organ class, the table by
organ class and term the only output.
"""

from __future__ import annotations

import json
import random
import time

import pytest

from specfirst.compile import checks
from specfirst.gen import gold
from specfirst.machine import ard, ars, rengine, results
from specfirst.machine import registry as registries
from specfirst.score.candidate import Data, Machine

ARMS = ["Placebo", "Drug 10 mg", "Drug 20 mg"]
DESIGN = [{"code": arm, "dose": float(dose), "names": [arm]}
          for arm, dose in zip(ARMS, (0, 10, 20), strict=True)]
UNIT = "tfl-ae-soc-pt"
TERMS = "An_AESOCPT_Pt"  # the analysis by organ class and preferred term
CLASSES = "An_AESOCPT_Soc"  # the analysis by organ class
# The two sizes of the issue: organ classes, terms per class, adverse event records.
SIZES = [(10, 5, 300), (20, 10, 1500)]


def invented(n_soc: int, per_soc: int, n_ae: int, n_subj: int = 300, seed: int = 1):
    """ADSL and ADAE of an invented study, seeded; each term in one organ class."""
    import pyarrow as pa

    rnd = random.Random(seed)
    subjects = [f"S{i:04d}" for i in range(n_subj)]
    arm_of = {subject: ARMS[i % 3] for i, subject in enumerate(subjects)}
    adsl = pa.table({"USUBJID": subjects, "SAFFL": ["Y"] * n_subj,
                     "TRT01A": [arm_of[subject] for subject in subjects]})
    terms = [(f"SOC {i:02d}", f"PT {i:02d}-{j:02d}") for i in range(n_soc)
             for j in range(per_soc)]
    events = [(rnd.choice(subjects), *rnd.choice(terms)) for _ in range(n_ae)]
    adae = pa.table({"USUBJID": [e[0] for e in events], "TRTEMFL": ["Y"] * n_ae,
                     "AESOC": [e[1] for e in events], "AEDECOD": [e[2] for e in events]})
    return adsl, adae, events, arm_of


@pytest.fixture(scope="module")
def machine(root):
    return Machine(root, datasets=("ADSL", "ADAE"))


@pytest.fixture(scope="module")
def records(machine):
    """The base vector with the table by organ class and term as its only output."""
    found = []
    for record in checks.base_vector(machine.catalog, machine.house):
        kind = machine.catalog.units[record["unit"]].kind
        if kind == "table_family" and record["unit"] != UNIT:
            if record["id"] == "tfl.output.include":
                found.append({**record, "value": {"rule": "not_included"}})
            continue
        found.append(record)
    return found


def _cells(build, analysis_id: str) -> dict[tuple, int]:
    """The subject counts of an analysis: (treatment group, organ class[, term]) -> n."""
    found = {}
    for row in build.ard.values():
        if row["analysis_id"] != analysis_id or row["method_id"] != "count.subjects":
            continue
        key = []
        for n in (1, 2, 3):
            grouping = row.get(f"group{n}_groupingId")
            if grouping is None:
                break
            if f"group{n}_groupValue" in row:
                key.append(row[f"group{n}_groupValue"])
            else:  # a listed group: its name is the value it stands for
                key.append(build.groups[(grouping, row[f"group{n}_groupId"])]["name"])
        found[tuple(key)] = row["raw_value"]
    return found


@pytest.mark.parametrize("n_soc, per_soc, n_ae", SIZES, ids=["10x5", "20x10"])
def test_the_term_counts_are_arms_times_the_pairs_that_occur(machine, records, n_soc, per_soc,
                                                             n_ae):
    adsl, adae, events, arm_of = invented(n_soc, per_soc, n_ae)
    started = time.perf_counter()
    build = machine.build(records, Data(f"issue27/{n_soc}x{per_soc}",
                                        adam={"ADSL": adsl, "ADAE": adae}), DESIGN)
    took = time.perf_counter() - started
    assert build.failure is None, build.failure
    pairs = sorted({(soc, pt) for _, soc, pt in events})
    classes = sorted({soc for _, soc, _ in events})
    terms = _cells(build, TERMS)
    print(f"\n{n_ae} records, {n_soc} SOCs x {n_soc * per_soc} PTs, {len(pairs)} SOC/PT pairs "
          f"occur: {TERMS} has {len(terms)} count results; build {took:.1f} s")
    # The vector of the issue: one count per arm and pair that occurs, no more.
    assert len(terms) == len(ARMS) * len(pairs)
    # Each count is the number of subjects of the arm with a record of the pair.
    expected = {(arm, soc, pt): len({s for s, c, p in events if (c, p) == (soc, pt)
                                     and arm_of[s] == arm})
                for arm in ARMS for soc, pt in pairs}
    assert terms == expected
    # The total column: one count per pair that occurs.
    assert _cells(build, TERMS + "_Tot") == {
        ("Total", soc, pt): len({s for s, c, p in events if (c, p) == (soc, pt)})
        for soc, pt in pairs}
    # The level above: one count per arm and organ class that occurs.
    assert _cells(build, CLASSES) == {
        (arm, soc): len({s for s, c, _ in events if c == soc and arm_of[s] == arm})
        for arm in ARMS for soc in classes}


def test_population_groupings_are_listed_and_record_groupings_are_not(machine, records):
    """Treatment subdivides the subject population: its groups are listed, so that an
    arm without a record still has a count. Organ class and term subdivide records:
    they stay data-driven."""
    adsl, adae, _, _ = invented(*SIZES[0])
    build = machine.build(records, Data("issue27/10x5", adam={"ADSL": adsl, "ADAE": adae}),
                          DESIGN)
    listed = {grouping for grouping, _ in build.groups}
    assert "Grp_TRT01A" in listed
    assert not listed & {"Grp_AESOC", "Grp_AEDECOD"}
    compiled = {g["id"]: g for g in build.ars["analysisGroupings"]}
    assert all(compiled[g]["dataDriven"] for g in ("Grp_TRT01A", "Grp_AESOC", "Grp_AEDECOD"))


def test_the_r_engine_gives_the_same_rows_on_the_pairs(root, machine, records, tmp_path):
    """Rule R11 on the larger case: both engines run the event with its groups listed."""
    if not rengine.available():
        pytest.skip("Rscript is not installed")
    adsl, adae, events, _ = invented(*SIZES[1])
    compiled = machine.compile(records)
    event = ars.index(compiled.ars)
    given = {"ADSL": adsl, "ADAE": adae}
    tables = {dataset: ard.table_from_arrow(dataset, given[dataset].select(names))
              for dataset, names in ars.columns(event, gold.SUBJECT_KEY).items()}
    listed = gold.resolve_groupings(compiled.ars, tables, compiled.layouts, DESIGN)
    event, binding, ours = gold.python_results(root, listed, tables)
    path = tmp_path / "event.json"
    path.write_text(json.dumps(event.data), encoding="ascii")
    theirs, meta, _ = rengine.run(root, tmp_path / "work", path,
                                  registries.json_path(root), binding, tables, gold.SUBJECT_KEY)
    assert rengine.data_problems(meta, tables) == []
    lines, problems = results.agreement(results.by_id(ours), results.by_id(theirs))
    assert problems == [], problems[:5]
    pairs = {(soc, pt) for _, soc, pt in events}
    counts = [row for row in theirs
              if row["analysis_id"] == TERMS and row["method_id"] == "count.subjects"]
    assert len(counts) == len(ARMS) * len(pairs)
    print("\n" + lines[0])
