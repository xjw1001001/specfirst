# Issue #27 AE by organ class and term: the pairs that occur, not every pair: report

Date: 2026-11-18. Branch: `track/real`. Issue #27 of
`xjw1001001/specfirst`, filed by the owner the same day: "[machine] AE by
SOC and PT: SOC and PT are two independent groupings, so the engine
computes every SOC x PT pair". The route is ADR-011.

## Verdict

- The analysis by term of `tfl-ae-soc-pt` now gives arms x the pairs of
  organ class and term that occur: 150 and 600 counts on the two cases of
  the issue, where it gave 1,500 and 12,000. Its total column and the
  analysis by organ class follow. A build of the larger case takes 0.2 s
  instead of about 65 s.
- The route is ADR-011: the two term groupings stay data-driven, as the
  house template and CDISC's example have them, and only data-driven
  groupings on ADSL get their groups listed before the engines run. No
  file under `standard/`, no engine and no rule changed.
- Both engines give the same rows (rule R11): 1,772 results on the larger
  case, 0 disagree.
- The vector failed before the change (4 of 4, and the final file 3 of 3
  without R) and passes after it (4 of 4).
- Generated kits are the same bytes before and after (kits 1 to 4 of the
  seed `gen-2a`, 511 files); no task folder of a reader changes.
  CDISCPILOT01 does not go through the changed code.
- Gates on clean clones: running when this was written (next sections).
- Review: not yet done when this was written.

## What the issue shows, and where it came from

The repro of the issue (invented data, seeded; stage T: ADSL and ADAE
given; `tfl-ae-soc-pt` the only output), run on `main` = `3fbe162` with
the locked environment of this worktree, under the heavy lock. The script
is the issue's, with two additions: it prints the rows per analysis and the
grids, and it writes the compiled ARS file and layout to a scratch file.

```text
$ flock /run/lock/specfirst-heavy.lock python repro.py /mnt/d/trial_work/specfirst-real compiled.json
300 records, 10 SOCs x 50 PTs, 50 SOC/PT pairs occur: An_AESOCPT_Pt has 1500 count results; 1.1 s; failure=None; rows per analysis {'An_AESOCPT_Any': 6, 'An_AESOCPT_Any_Tot': 2, 'An_AESOCPT_N': 3, 'An_AESOCPT_N_Tot': 1, 'An_AESOCPT_Pt': 3000, 'An_AESOCPT_Pt_Tot': 1000, 'An_AESOCPT_Soc': 60, 'An_AESOCPT_Soc_Tot': 20}; grids []; not produced {'Out_AESOCPT': "display: analysis 'An_AESOCPT_Soc' is grouped by ['Grp_TRT01A', 'Grp_AESOC'], its column by Grp_TRT01A"}
1500 records, 20 SOCs x 200 PTs, 200 SOC/PT pairs occur: An_AESOCPT_Pt has 12000 count results; 61.6 s; failure=None; rows per analysis {'An_AESOCPT_Any': 6, 'An_AESOCPT_Any_Tot': 2, 'An_AESOCPT_N': 3, 'An_AESOCPT_N_Tot': 1, 'An_AESOCPT_Pt': 24000, 'An_AESOCPT_Pt_Tot': 8000, 'An_AESOCPT_Soc': 120, 'An_AESOCPT_Soc_Tot': 40}; grids []; not produced {'Out_AESOCPT': "display: analysis 'An_AESOCPT_Soc' is grouped by ['Grp_TRT01A', 'Grp_AESOC'], its column by Grp_TRT01A"}
```

The counts are the issue's (1,500 and 12,000); the time of the larger case
was 61.6 s here, 41.2 s on the machine of the issue. The total column
(`An_AESOCPT_Pt_Tot`) is crossed the same way: 500 and 4,000 counts where
50 and 200 pairs occur. The output `Out_AESOCPT` builds no grid: its
layout (draft 0, `nesting`) is not a kind `specfirst.gen.display` builds.

The compiled groupings and analyses of the table (from the scratch file):

```text
Grp_TRT01A ADSL TRT01A dataDriven=True groups=0
Grp_Total_AESOCPT ADSL TRT01A dataDriven=False groups=1
Grp_AESOC ADAE AESOC dataDriven=True groups=0
Grp_AEDECOD ADAE AEDECOD dataDriven=True groups=0
An_AESOCPT_N ['Grp_TRT01A'] None
An_AESOCPT_N_Tot ['Grp_Total_AESOCPT'] None
An_AESOCPT_Any ['Grp_TRT01A'] Dss_TEAE
An_AESOCPT_Any_Tot ['Grp_Total_AESOCPT'] Dss_TEAE
An_AESOCPT_Soc ['Grp_TRT01A', 'Grp_AESOC'] Dss_TEAE
An_AESOCPT_Soc_Tot ['Grp_Total_AESOCPT', 'Grp_AESOC'] Dss_TEAE
An_AESOCPT_Pt ['Grp_TRT01A', 'Grp_AESOC', 'Grp_AEDECOD'] Dss_TEAE
An_AESOCPT_Pt_Tot ['Grp_Total_AESOCPT', 'Grp_AESOC', 'Grp_AEDECOD'] Dss_TEAE
```

The compiled file keeps organ class and term data-driven, as the house
template says ("as in the CDISC ARS example"). Rule I9 gives several
data-driven groupings "the combinations of values that occur together on
a record, not every combination", and both engines do that
(`ard.Engine.cells`, `cells` in `r/specfirstr/R/engine.R`). The cross
product came from `specfirst.gen.gold.resolve_groupings` (ADR-007,
decision 1), which replaced every data-driven grouping by the list of its
values in the analysis set before the engines ran; with listed groups rule
I10 takes every combination. The scorer's build
(`specfirst.score.candidate.Machine`) and the gold of a generated kit
(`specfirst.gen.gold.show`) both go through it.

## What the public ARS model offers (rule R2)

Read in the pinned repository `ars` in the fetch cache (read only), at
its pin:

```text
$ git -C "$SPECFIRST_CACHE/ars" rev-parse HEAD
2c9b4b68724386e8f91dc576724855af7fafac65
$ cd "$SPECFIRST_CACHE/ars" && grep -n -i "nest\|hierarch\|parent\|depend\|subClause\|sub_clause\|level" model/ars_ldm.yaml | head -40
55:  NestedList:
60:  LevelOrder:
61:    description: An abstract class containing attributes used to position class instances within a hierarchical tree.
64:      - level
71:      - LevelOrder
128:      - LevelOrder
163:      (`subClauseId`) as the sub-clause in a compound expression.
166:      - LevelOrder
168:      - subClauseId
170:      subClauseId:
173:  SubClause:
179:      (containing a `subClauseId`).
182:      - LevelOrder
186:      subClauseId:
196:      `ReferencedWhereClause` (containing a `subClauseId`).
224:      An `AnalysisSet` referenced by identifier (`subClauseId`) as the
228:      subClauseId:
238:      (containing a `subClauseId` indicating the `id` of the referenced
259:    description:  A `DataSubset` referenced by identifier (`subClauseId`) as the sub-clause of a compound expression.
262:      subClauseId:
272:      (containing a `subClauseId` indicating the `id` of the referenced
303:    description: A `Group` referenced by identifier (`subClauseId`) as the sub-clause of a compound expression.
306:      subClauseId:
316:      (containing a `subClauseId` indicating the `id` of the referenced
794:    range: NestedList
878:  level:
879:    description: The level of the entry within a hierarchical structure.
881:      - 1 is the top level.
892:    range: NestedList
990:  subClauseId:
1016:    range: SubClause
1120:    description: The role that the referenced operation's result plays in the calculation of the result of the parent operation.
1161:    # TODO: restrict to formal references to attributes of instances of the parent Analysis class.
```

The class blocks, printed with
`awk -v c="  $c:" '$0==c{p=1;print;next} p&&/^  [A-Za-z]/{p=0} p' model/ars_ldm.yaml`
for each class:

```text
  GroupingFactor:
    description: A factor used to subdivide either the subject population or data records in an analysis dataset for analysis.
    is_a: NamedObject
    slots:
      - id
      - groupingDataset
      - groupingVariable
      - dataDriven
      - groups
  Group:
    description: A subdivision of the subject population or analysis dataset record set based on a defined factor.
    is_a: NamedObject
    slots:
      - id
    mixins:
      - WhereClause
    slot_usage:
      compoundExpression:
        range: CompoundGroupExpression
  OrderedGroupingFactor:
    description: A reference to a defined factor by which subjects or data records are grouped for the analysis, ordered with respect to other grouping factors.
    slots:
      - order
      - groupingId
      - resultsByGroup
  ReferencedGroup:
    description: A `Group` referenced by identifier (`subClauseId`) as the sub-clause of a compound expression.
    is_a: ReferencedWhereClause
    slot_usage:
      subClauseId:
        range: Group
  ResultGroup:
    description: For the specified grouping factor, an indication of the specific group of subjects or data records associated with the analysis result.
    slots:
      - groupingId
      - groupId
      - groupValue
```

A grouping has one variable; an analysis orders its groupings and says
per grouping whether results are by group; nothing makes one grouping
depend on another. `LevelOrder` places a where clause or a list item in a
tree; `NestedList` is the list of contents. A defined group may be a
compound expression with references to other groups, so a group on a pair
can be written as a listed group.

How CDISC's two examples use groupings (a Python script that reads
`workfiles/examples/ARS v1/*.json` and prints, per grouping, its dataset,
variable, `dataDriven`, the number of listed groups and the datasets of
the analyses that use it):

```text
== Common Safety Displays.json
  AnlsGrouping_01_Trt              ADSL.TRT01A     dataDriven=False groups=3 analysis datasets=['ADAE', 'ADSL', 'ADVS']
  AnlsGrouping_02_Sex              ADSL.SEX        dataDriven=False groups=2 analysis datasets=['ADSL']
  AnlsGrouping_03_AgeGp            ADSL.AGEGR1     dataDriven=False groups=2 analysis datasets=['ADSL']
  AnlsGrouping_04_Race             ADSL.RACE       dataDriven=False groups=9 analysis datasets=['ADSL']
  AnlsGrouping_05_Ethnic           ADSL.ETHNIC     dataDriven=False groups=2 analysis datasets=['ADSL']
  AnlsGrouping_06_Soc              ADAE.AESOC      dataDriven=True  groups=0 analysis datasets=['ADAE']
  AnlsGrouping_07_Pt               ADAE.AEDECOD    dataDriven=True  groups=0 analysis datasets=['ADAE']
  AnlsGrouping_08_Param            ADVS.PARAMCD    dataDriven=False groups=4 analysis datasets=['ADVS']
  AnlsGrouping_09_Visit            ADVS.AVISIT     dataDriven=False groups=11 analysis datasets=['ADVS']
== FDA Standard Safety Tables and Figures.json
  AG_TRT                           ADSL.TRT01A     dataDriven=False groups=3 analysis datasets=['ADSL']
  AG_SEX                           ADSL.SEX        dataDriven=False groups=2 analysis datasets=['ADSL']
  AG_AGEGR2                        ADSL.AGEGR2     dataDriven=False groups=2 analysis datasets=['ADSL']
  AG_AGEGR3                        ADSL.AGEGR3     dataDriven=False groups=3 analysis datasets=['ADSL']
  AG_RACE                          ADSL.RACE       dataDriven=False groups=5 analysis datasets=['ADSL']
  AG_ETHNIC                        ADSL.ETHNIC     dataDriven=False groups=2 analysis datasets=['ADSL']
```

And its analyses by organ class and term (results per operation, distinct
organ class or organ class and term combinations among the results, arms):

```text
analysis An07_09_Soc_Summ_ByTrt groupings [('AnlsGrouping_01_Trt', True), ('AnlsGrouping_06_Soc', True)] results per op {'Mth01_CatVar_Summ_ByGrp_1_n': 69, 'Mth01_CatVar_Summ_ByGrp_2_pct': 69} row combos 23 arms 3
analysis An07_09_Soc_Comp_ByTrt_PlacLow groupings [('AnlsGrouping_01_Trt', False), ('AnlsGrouping_06_Soc', True)] results per op {'Mth03_CatVar_Comp_FishEx_1_pval': 1} row combos 1 arms 1
analysis An07_09_Soc_Comp_ByTrt_PlacHigh groupings [('AnlsGrouping_01_Trt', False), ('AnlsGrouping_06_Soc', True)] results per op {'Mth03_CatVar_Comp_FishEx_1_pval': 1} row combos 1 arms 1
analysis An07_10_SocPt_Summ_ByTrt groupings [('AnlsGrouping_01_Trt', True), ('AnlsGrouping_06_Soc', True), ('AnlsGrouping_07_Pt', True)] results per op {'Mth01_CatVar_Summ_ByGrp_1_n': 690, 'Mth01_CatVar_Summ_ByGrp_2_pct': 690} row combos 230 arms 3
analysis An07_10_SocPt_Comp_ByTrt_PlacLow groupings [('AnlsGrouping_01_Trt', False), ('AnlsGrouping_06_Soc', True), ('AnlsGrouping_07_Pt', True)] results per op {'Mth03_CatVar_Comp_FishEx_1_pval': 1} row combos 1 arms 1
analysis An07_10_SocPt_Comp_ByTrt_PlacHigh groupings [('AnlsGrouping_01_Trt', False), ('AnlsGrouping_06_Soc', True), ('AnlsGrouping_07_Pt', True)] results per op {'Mth03_CatVar_Comp_FishEx_1_pval': 1} row combos 1 arms 1
```

690 counts = 3 arms x 230 pairs: the shape the issue asks for, from a
defined treatment grouping and two data-driven term groupings. The engines
of real-2 reproduce these results (gate real-2, "results").

## The change (commit `e00bbb7`)

ADR-011 chooses option 3 of three (nesting in the ARS file, one grouping
on the pair, or the term groupings left data-driven): it changes nothing
under `standard/`, no rule and no engine, and is the model of CDISC's
example.

- `src/specfirst/gen/gold.py`: `resolve_groupings` lists the groups of a
  data-driven grouping only when its dataset is `SUBJECT_DATASET` = ADSL.
  The module docstring says why, and what happens to the others.
- `src/specfirst/gen/display.py`: the message for a column whose grouping
  is still data-driven says that only groupings on ADSL are listed.
- `src/specfirst/score/candidate.py`: one comment.
- `tests/unit/test_soc_pt_pairs.py`: the vector (next section).
- `CLAUDE.md` (the line on listed groups, still 59 lines),
  `docs/lessons.md` (lesson 61), ADR-011, this report.

Nothing under `standard/`, `r/specfirstr/`, `src/specfirst/machine/` or
`env/` changed:

```text
$ git diff --stat 3fbe162 e00bbb7
 CLAUDE.md                        |   2 +-
 docs/lessons.md                  |   1 +
 src/specfirst/gen/display.py     |   5 +-
 src/specfirst/gen/gold.py        |  34 +++++---
 src/specfirst/score/candidate.py |   2 +-
 tests/unit/test_soc_pt_pairs.py  | 165 +++++++++++++++++++++++++++++++++++++++
 6 files changed, 195 insertions(+), 14 deletions(-)
```

## The vector, before and after (rule R5)

`tests/unit/test_soc_pt_pairs.py` takes the case of the issue at its two
sizes (10 organ classes x 5 terms with 300 records; 20 x 10 with 1,500;
300 subjects in three arms; seed 1) through the scorer's build
(`Machine.build`, stage T), as the issue's script does. Four tests:

- `test_the_term_counts_are_arms_times_the_pairs_that_occur[10x5]` and
  `[20x10]`: the counts of `An_AESOCPT_Pt` are arms x the pairs that occur,
  no more; each count equals the number of subjects of its arm with a
  record of its pair, counted by the test from the invented records; the
  total column (`An_AESOCPT_Pt_Tot`) has one count per pair; the analysis
  by organ class has arms x the organ classes that occur.
- `test_population_groupings_are_listed_and_record_groupings_are_not`: the
  treatment grouping is listed, the two term groupings are not, and the
  compiled file keeps all three data-driven.
- `test_the_r_engine_gives_the_same_rows_on_the_pairs` (needs R; skipped
  where Rscript is missing, as in CI): the event with its groups listed
  goes through both engines on the larger case; every row agrees (rule
  R11), and the R engine too has arms x pairs counts.

Before the change. First the test file as first written (without the
total column), in the worktree on `3fbe162`, all four tests:

```text
$ python -m pytest tests/unit/test_soc_pt_pairs.py -s -q -p no:cacheprovider

300 records, 10 SOCs x 50 PTs, 50 SOC/PT pairs occur: An_AESOCPT_Pt has 1500 count results; build 2.0 s
F
1500 records, 20 SOCs x 200 PTs, 200 SOC/PT pairs occur: An_AESOCPT_Pt has 12000 count results; build 65.5 s
FF
E       AssertionError: assert 1500 == (3 * 50)
E       AssertionError: assert 12000 == (3 * 200)
E       AssertionError: assert not ({'Grp_AEDECOD', 'Grp_AESOC', 'Grp_TRT01A', 'Grp_Total_AESOCPT'} & {'Grp_AEDECOD', 'Grp_AESOC'})
E       AssertionError: assert 12000 == (3 * 200)
FAILED tests/unit/test_soc_pt_pairs.py::test_the_term_counts_are_arms_times_the_pairs_that_occur[10x5]
FAILED tests/unit/test_soc_pt_pairs.py::test_the_term_counts_are_arms_times_the_pairs_that_occur[20x10]
FAILED tests/unit/test_soc_pt_pairs.py::test_population_groupings_are_listed_and_record_groupings_are_not
FAILED tests/unit/test_soc_pt_pairs.py::test_the_r_engine_gives_the_same_rows_on_the_pairs
4 failed in 256.69s (0:04:16)
exit 1
```

(The `E` lines are the first line of each assertion; the R test failed on
its count after the agreement of the two engines had passed: before the
change both engines computed the same 12,000 crossed counts.)

Then the final test file, copied into a clone of `3fbe162`, the three
Python tests (the R test is unchanged from the run above):

```text
$ git log --oneline -1
3fbe162 Merge track/gen: part gen-3a of ADR-005 (gate passed, review signed, owner's answers recorded)
$ PYTHONPATH=<clone>/src python -m pytest tests/unit/test_soc_pt_pairs.py -s -q -p no:cacheprovider -k 'not r_engine'
300 records, 10 SOCs x 50 PTs, 50 SOC/PT pairs occur: An_AESOCPT_Pt has 1500 count results; build 1.3 s
1500 records, 20 SOCs x 200 PTs, 200 SOC/PT pairs occur: An_AESOCPT_Pt has 12000 count results; build 65.7 s
E       AssertionError: assert 1500 == (3 * 50)
E       AssertionError: assert 12000 == (3 * 200)
E       AssertionError: assert not ({'Grp_AEDECOD', 'Grp_AESOC', 'Grp_TRT01A', 'Grp_Total_AESOCPT'} & {'Grp_AEDECOD', 'Grp_AESOC'})
FAILED tests/unit/test_soc_pt_pairs.py::test_the_term_counts_are_arms_times_the_pairs_that_occur[10x5]
FAILED tests/unit/test_soc_pt_pairs.py::test_the_term_counts_are_arms_times_the_pairs_that_occur[20x10]
FAILED tests/unit/test_soc_pt_pairs.py::test_population_groupings_are_listed_and_record_groupings_are_not
3 failed, 1 deselected in 67.87s (0:01:07)
exit 1
```

After the change, in a clone of `e00bbb7`, all four tests:

```text
$ git log --oneline -1
e00bbb7 issue #27: organ class and term stay data-driven; only groupings on ADSL are listed
$ PYTHONPATH=<clone>/src python -m pytest tests/unit/test_soc_pt_pairs.py -s -q -p no:cacheprovider

300 records, 10 SOCs x 50 PTs, 50 SOC/PT pairs occur: An_AESOCPT_Pt has 150 count results; build 0.1 s
.
1500 records, 20 SOCs x 200 PTs, 200 SOC/PT pairs occur: An_AESOCPT_Pt has 600 count results; build 0.2 s
..
engines: 1772 results in both, 0 disagree; largest relative difference 0.0e+00 (allowed 1e-09)
.
4 passed in 2.72s
exit 0
```

1,772 is every result of the event on the larger case: 6 + 2 + 3 + 1
(any event, the column counts) + 1,200 + 400 (by term, with the total
column; counts and percents) + 120 + 40 (by organ class).

## Build times, before and after

The issue's repro on a clone of `e00bbb7`:

```text
$ python repro.py <clone of e00bbb7>
300 records, 10 SOCs x 50 PTs, 50 SOC/PT pairs occur: An_AESOCPT_Pt has 150 count results; -0.9 s; failure=None; rows per analysis {'An_AESOCPT_Any': 6, 'An_AESOCPT_Any_Tot': 2, 'An_AESOCPT_N': 3, 'An_AESOCPT_N_Tot': 1, 'An_AESOCPT_Pt': 300, 'An_AESOCPT_Pt_Tot': 100, 'An_AESOCPT_Soc': 60, 'An_AESOCPT_Soc_Tot': 20}; grids []; not produced {'Out_AESOCPT': "display: analysis 'An_AESOCPT_Soc' is grouped by ['Grp_TRT01A', 'Grp_AESOC'], its column by Grp_TRT01A"}
1500 records, 20 SOCs x 200 PTs, 200 SOC/PT pairs occur: An_AESOCPT_Pt has 600 count results; 0.2 s; failure=None; rows per analysis {'An_AESOCPT_Any': 6, 'An_AESOCPT_Any_Tot': 2, 'An_AESOCPT_N': 3, 'An_AESOCPT_N_Tot': 1, 'An_AESOCPT_Pt': 1200, 'An_AESOCPT_Pt_Tot': 400, 'An_AESOCPT_Soc': 120, 'An_AESOCPT_Soc_Tot': 40}; grids []; not produced {'Out_AESOCPT': "display: analysis 'An_AESOCPT_Soc' is grouped by ['Grp_TRT01A', 'Grp_AESOC'], its column by Grp_TRT01A"}
exit 0
```

The repro times with the wall clock (`time.time()`), and the clock of the
Linux machine was stepped back during the first build: "-0.9 s" is no
time. The test times the same builds with `time.perf_counter()`:

| Case | Counts by term, before | after | Build before (perf_counter) | after |
| --- | --- | --- | --- | --- |
| 10 x 5, 300 records, 50 pairs | 1,500 | 150 | 2.0 s; 1.3 s | 0.1 s |
| 20 x 10, 1,500 records, 200 pairs | 12,000 | 600 | 65.5 s; 65.7 s | 0.2 s |

The two times before are the two runs above; the first build of a run
also compiles the decisions, which the second size then takes from the
cache of the machine. The issue's repro gave 1.1 s and 61.6 s before
(wall clock, first section). With the R engine, the four tests took 257 s
before and 2.7 s after.

## Generated kits and the task folder of a reader

Kits 1 to 4 of the seed `gen-2a` (kit 4 is the one read-2a uses), written
with a clone of `3fbe162` and again with a clone of `e00bbb7`, with the
environment of this worktree, under the heavy lock:

```text
$ python -m specfirst gen kits --out kits-main --count 4 --seed gen-2a     # clone of 3fbe162
kit 1 of the set: sfpbt5zj, train, 127 files; 14 of 22 decisions separated on the twin
kit 2 of the set: sfmyncmq, train, 127 files; 15 of 22 decisions separated on the twin
kit 3 of the set: sfg5vbvq, train, 126 files; 15 of 21 decisions separated on the twin
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin
exit 0 after 419 s
$ python -m specfirst gen kits --out kits-after --count 4 --seed gen-2a    # clone of e00bbb7
kit 1 of the set: sfpbt5zj, train, 127 files; 14 of 22 decisions separated on the twin
kit 2 of the set: sfmyncmq, train, 127 files; 15 of 22 decisions separated on the twin
kit 3 of the set: sfg5vbvq, train, 126 files; 15 of 21 decisions separated on the twin
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin
exit 0 after 103 s
$ diff -r kits-main kits-after && echo identical
identical
exit 0
$ find kits-main -type f | wc -l; find kits-after -type f | wc -l
511
511
$ sha256sum kits-*/kit-00?/kit.yaml
947f40b73a1078be6b299753315e83f828794bdd88e8366a1c8ecc2addb4f0bd  kits-after/kit-001/kit.yaml
7602f342569f61f46feca20a47625beec1ffa56ba71afde2f33274ff50f1f6af  kits-after/kit-002/kit.yaml
a91624ae4b2bca1b13ce40d0bd94c22119ca5389c04f7b0b11935f586337e218  kits-after/kit-003/kit.yaml
e23d3a9099492e0e6978b6a107fc3fb6648dafdc0e9f5de8334e9eeb0e95bd18  kits-after/kit-004/kit.yaml
947f40b73a1078be6b299753315e83f828794bdd88e8366a1c8ecc2addb4f0bd  kits-main/kit-001/kit.yaml
7602f342569f61f46feca20a47625beec1ffa56ba71afde2f33274ff50f1f6af  kits-main/kit-002/kit.yaml
a91624ae4b2bca1b13ce40d0bd94c22119ca5389c04f7b0b11935f586337e218  kits-main/kit-003/kit.yaml
e23d3a9099492e0e6978b6a107fc3fb6648dafdc0e9f5de8334e9eeb0e95bd18  kits-main/kit-004/kit.yaml
```

(The two times are not a comparison: nothing here measured why the first
run took longer.) The kit
manifest holds the SHA-256 of every file of its kit, and all 511 files are
the same bytes. Why: a kit of the slice compiles the adverse event summary
only, whose one data-driven grouping is the treatment grouping on ADSL,
listed as before.

For read-2a: a task folder holds the catalog, the method registry, the
schemas, the skills and a generated kit. This change touches none of the
first four, and the kits are the same bytes, so no task folder changes.

## Gates on clean clones

Running when this was written: `scripts/clean_clone_gate.sh` for real-2,
real-3a, gen-2a, gen-3a and read-1a on commit `c7f09a0` (`e00bbb7` with
`main` = `5b8ff85` merged in; `5b8ff85` changes README.md and ADR-012
only), one at a time under the heavy lock, on at most four processors.

## Review

Not yet done when this was written.
