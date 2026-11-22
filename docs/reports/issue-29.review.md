# Issue #29 A standalone recomputation script per analysis: independent review, pass 1 (code)

Reviewed: the work on issue #29 ("A generated, standalone recomputation
script per analysis") on branch `track/real`, as it is at `694709b`.

- The diff `9dc6b20..694709b`. `9dc6b20` is `main` and the parent of
  `694709b`; the work is that one commit (20 files, 3354 insertions, 5
  deletions): `src/specfirst/recompute/`, the command `specfirst
  recompute`, the gate `issue-29`, `tests/unit/test_recompute.py`,
  `tests/recompute/test_recompute_pilot.py`, ADR-021, the section "Handed
  over by issue #29" of docs/state/real.md, one line of CLAUDE.md and the
  skeleton of docs/reports/issue-29.md. The worktree was clean at
  `694709b` before and after the reviewer's runs (`git status --short`
  prints nothing).
- The files the findings quote, as committed at `694709b`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/recompute/static.py` | 232 | `2142911b793686812ced237757ad4f49b3d00f8f2e5394b00778aef815b48a4e` |
  | `src/specfirst/recompute/run.py` | 239 | `e0a3abe490927001c24130cdf8b3e1068ddf50b7b31b3f16c026a81c44913870` |
  | `src/specfirst/recompute/seal.py` | 32 | `34658353100cabd515be5fe73d959edba65ad60af858a2dc3d6f6a73f9d57c55` |
  | `src/specfirst/recompute/bundle/compare.py` | 143 | `bcbf729c04a79e772789753bc5461d5a056c70a86c975636b5adec7ea96870e1` |
  | `src/specfirst/recompute/reading.py` | 302 | `2acd936561a4b9e91f0d440b8bca1835e3786a604b965adaf11d84cb1a6934c4` |
  | `src/specfirst/recompute/pywrite.py` | 357 | `4a26c128cf93b0ea85dd91ddf20ad97c6a73c1c070a1ca0ecfaf7ff01ccbdcad` |
  | `src/specfirst/recompute/rwrite.py` | 503 | `7666f2236153d54f6c2e433ac369dd005a18dfe75d86bf92645e4a3affd1cb50` |
  | `src/specfirst/recompute/generate.py` | 270 | `04696e27c907e21c0936177c9b3430f587a41c8158ccb130566aeedf4e9224b8` |
  | `src/specfirst/gates.py` | 1006 | `bde60e06ffdc4155c459d36f96c9b96eebff033e6c3257817f8d309c13614193` |
  | `tests/recompute/test_recompute_pilot.py` | 362 | `c100a4129a375a7c0daa382dd7734fc349e5015c1baa1ba97360f040a58de0db` |
  | `tests/unit/test_recompute.py` | 330 | `d3f8a7406f3051a46085d21c53b3d73ec3246dcadd2c62328c8af0304312db14` |
  | `docs/decisions/ADR-021.md` | 173 | `15214a20d33112fc5530aa11e7e97574267f1700c1c675509729b8563715ad6f` |
  | `docs/state/real.md` | 575 | `a8b5704404211e0866c3067613d4fff95ccf53176162889dfdbde4388c35bcd9` |

- Pass 2, part 1: the fix of the findings, commit `b43c336` ("the findings
  of the review, pass 1 (F1 to F5)"), child of `694709b`; the diff
  `694709b..b43c336` (11 files, 587 insertions, 144 deletions). It changes
  no file under `standard/`, `kits/` or PLAN.md, and not `pywrite.py`,
  `rwrite.py` or `reading.py`, so the 69 scripts are the same text as at
  `694709b`. The files the updated findings quote, as committed at
  `b43c336`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/recompute/static.py` | 363 | `572ac12b5d29b76ad275e1be5e91cd75ffaba5b59c5012927bd29b684df6c7b3` |
  | `src/specfirst/recompute/seal.py` | 67 | `92154389864621258e875110e0cac988abdb84eacc6cbafcd05852734be3615e` |
  | `src/specfirst/recompute/run.py` | 251 | `a026198946ca806275b6ba280eb0c706aee14cc3191957e55465ff2d0d238621` |
  | `src/specfirst/recompute/bundle/compare.py` | 168 | `229cd73f55d0d35bb55c26e1a94b84c511a80cbd5f8ef76cd390c62283a9c620` |
  | `src/specfirst/recompute/generate.py` | 299 | `32d51363088592036f5b0f4bec616b4354e087978ed4614675158ab305fe0393` |
  | `src/specfirst/gates.py` | 1009 | `4f27402433915e10b89bc0ed6d6b7cfd5a3e665a6c6b3f19cc0835b364e74cf8` |
  | `tests/recompute/test_recompute_pilot.py` | 418 | `37bc88ae74f6c5a79d816f035e96b5dbf3274fbff6ae42743c48f2f2717d5e1a` |
  | `tests/unit/test_recompute.py` | 448 | `71d2f85b8a4c61107bdd7fd2b12a9f8f4cf3353bdd6b75343435893fbb847979` |
  | `docs/decisions/ADR-021.md` | 200 | `3f0a69919638bab0cd3bb39bc594b6ff571f06cc948d29ca1105867d85f8238e` |
  | `docs/state/real.md` | 581 | `a71047238f68ac948afebfae7869b658ce93b8ea55561602176a15428791ff75` |

- Pass 2, F1 again: commit `0e06dd4` ("F1 of the review, pass 2 (N1, N2,
  RN1 to RN3)"), child of `b43c336`; the diff `b43c336..0e06dd4` (6 files:
  static.py, run.py, gates.py, ADR-021, both test files). No writer, nothing
  under `standard/` or `kits/`, not PLAN.md. The files F1 quotes, at
  `0e06dd4`:

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/recompute/static.py` | 430 | `196f95c781d615121f7df2edbc2cb33d679b5863cf7a7ac0d3624dd9f75e5ea8` |
  | `src/specfirst/recompute/run.py` | 252 | `8abbaee3e65898bee7a2a1c8036a654aa6e3c26734fc8bc690c39c05f0b2fe22` |
  | `src/specfirst/gates.py` | 1009 | `b9306f588377fd59a586380104df28cc6c76b95ed4c96f15540397cb27a7d31e` |
  | `tests/recompute/test_recompute_pilot.py` | 434 | `814ee2c9d818409780351e62770199f31ebe155f667cab6d9bd01e8f894505dd` |
  | `tests/unit/test_recompute.py` | 473 | `04f7cea0efb64b5473f5032263b7d29de9b67ecec145229a179fedd6d6d462b9` |
  | `docs/decisions/ADR-021.md` | 205 | `bb3eaa449b80a3fadab6777937b4d28b100c8f168e5783e5ef9f0f9f0360296d` |

- F1 at `ae07c86` ("F1 of the review, pass 2 at 0e06dd4 (N2c, the
  writes)"), child of `0e06dd4`; the diff `0e06dd4..ae07c86` (4 files:
  static.py, ADR-021, both test files):

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/recompute/static.py` | 453 | `3aeba20aed778c4fd4013bc3246658f2f87a7c8ea4e051616a1792180963cc27` |
  | `docs/decisions/ADR-021.md` | 210 | `db3bd23fe811ae223e1dea3c461ea445ae706ac7e6e4535412fbcab305ae5a03` |
  | `tests/recompute/test_recompute_pilot.py` | 441 | `ab317a0307fb19beaa856794bd294cadc8c4209daede4cf99cf0067590d95963` |
  | `tests/unit/test_recompute.py` | 486 | `4b170bdba7c933c2420811627925607ca21fb8e51beeb18b81be08255f018fab` |

- F1 at `22c2932`, child of `ae07c86`, the commit the author intends to
  merge; the diff `ae07c86..22c2932` (4 files: static.py, ADR-021, both
  test files; 24 insertions, 4 deletions):

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/recompute/static.py` | 464 | `08e798fa1c808475a151e5e3a22b4c55d1890c31d5375f8d093a88fe3e29e2cb` |
  | `docs/decisions/ADR-021.md` | 211 | `f5865002762a97e3a135fcd08bfd6b44e78b1533d5e2e84315baf90830a8900c` |

- Pass 2, part 2: commit `c5afc28` (the report and the five gate logs on
  top of `22c2932`; documents only: the diff `22c2932..c5afc28` names the
  report, the five logs and docs/state/real.md, nothing else):

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `docs/reports/issue-29.md` | 433 | `8f7874ef8f3d2134c2d3f5903838090c6279a05d78b6befc981a48143b98a47d` |
  | `docs/reports/issue-29.clean-clone.gate.log` | 363 | `587dd64c9ccb502e4be53066de9670c55a1998a65cb80e6a3efdd596887f7bae` |
  | `docs/reports/issue-29.real-5a.gate.log` | 750 | `83d7e9a252898f680e0731a42a5ea0ed9d790ef5de49091dfd143c652ed7f5c3` |
  | `docs/reports/issue-29.real-5b.gate.log` | 702 | `afde077841c4847441b01efcfbb243a13830c381a15c4676522cc112f42e74e3` |
  | `docs/reports/issue-29.real-2.gate.log` | 618 | `508fcc18cd620aec6fb525869875f64a9fcfccfa5dcb81b249e72abbff192d46` |
  | `docs/reports/issue-29.real-3a.gate.log` | 680 | `1f0b028d64f0b3fcece3a4a3a78c6b8ce12a0807794e5fa84f4eab470586bbb0` |
  | `docs/state/real.md` | 590 | `e0cb507fd22af096dd71f89a9c1e1721ae7ba5a925893ba37c7470b5119b562f` |

- Final: commit `0ae9b24` on `track/real`, documents only on top of the
  merge `711c032` (`main` `6cdeded`, catalog-2b, merged into `c5afc28`;
  parents `c5afc28` and `6cdeded`). Reviewed of the merge: its diff in
  src/specfirst/cli.py and src/specfirst/gates.py; of `0ae9b24`: the six
  logs of the clean clones of `711c032`, the report's new section "On the
  merge with main", its updated verdict bullet, review section and section
  "The gates on clean clones", and the state entry. `git diff --name-only
  711c032 0ae9b24` names those eight files only; nothing under `src/`,
  `tests/`, `r/`, `env/`, `standard/` or `kits/`, and not PLAN.md.

  | File | Lines | SHA-256 |
  | --- | --- | --- |
  | `src/specfirst/cli.py` | 342 | `4b7135650732d594251311c860e407842bee7a2940ce90aa3d5176f91cab9b23` |
  | `src/specfirst/gates.py` | 1013 | `d14f2821c0645b28820a73dcd5197893c43ff1bc258fe064f1f649158f4acbfa` |
  | `docs/reports/issue-29.md` | 481 | `d99ffd19872fa7dd4291a5b4f7d1ef223aa619955c66cf7452aa340d5ed573cb` |
  | `docs/reports/issue-29.merged.clean-clone.gate.log` | 363 | `c8c5d97f729a366d50e41ae3532a1a3a29417d0eaee0e18950e7b87ef6af5198` |
  | `docs/reports/issue-29.merged.real-5a.gate.log` | 750 | `0cd36ef5df133f0bd67e8fb95990fbd0770444b665be4c3d8bc4c44519913b4d` |
  | `docs/reports/issue-29.merged.real-5b.gate.log` | 702 | `5fff73d3d16805bd0f32e1c85d5c0715700ec1c3cc971951a7b24519b551fc7c` |
  | `docs/reports/issue-29.merged.real-2.gate.log` | 618 | `a24ef8b8a9f4ea6758dce51a4c0f20f4380e8752f48b68fc94d298e3c3e67c43` |
  | `docs/reports/issue-29.merged.real-3a.gate.log` | 680 | `8099e11ee796055ea8221e87f2312ffe8356af3caf6c0200bcb8596d278d141d` |
  | `docs/reports/issue-29.merged.catalog-2b.gate.log` | 221 | `987f5288735192c099586d8de378ed3a424958ab5ecf38e5f89b595c646b97af` |
  | `docs/state/real.md` | 592 | `56ee4b084aae56fc1721f48a1c88acc26c387317e60d57074dea6aabdfcecffa` |

Date: 2026-11-21.

Reviewer: an independent agent with a fresh context that did not write the
work (rule R7). Correctness only, no style remarks. This is pass 1, of the
code; the report and the gate logs are pass 2. The reviewer changed no
tracked file, made no commit and wrote this file only. Nothing was pushed,
posted or closed; no package was installed; no model was called; nothing
was written into the fetch cache. Every planted change stood in the
reviewer's own clone (`<clone>` below, a `git clone --no-local` of the
repository on the Linux file system, detached at `694709b`) or in a
scratch folder.

## Outcome

Final (`0ae9b24`): SIGNED. No finding blocks and none is open but the
residuals ADR-021 decision 5 names itself (F1). The merge `711c032` changes
src/specfirst/cli.py and src/specfirst/gates.py by exactly main's catalog-2b
change (`git diff c5afc28 711c032` equals `git diff 9dc6b20 6cdeded` there,
line for line: the parser's `parse_full` and its line "left out", and the
gate catalog-2b), and keeps issue-29's own change of the two files whole
(`git diff 6cdeded 711c032` equals `git diff 9dc6b20 c5afc28` there); main
changes nothing under `standard/methods/`, `kits/`, `r/`, `env/`,
`src/specfirst/machine/` or `src/specfirst/recompute/` (R16). The six logs
start "gate <wp> at commit 711c032d3c3a186640414c23e242a3ea2fdee98b
(clean)", have 12, 18, 19, 15, 16 and 17 PASS lines and no FAIL for
issue-29, real-5a, real-5b, real-2, real-3a and catalog-2b, hold "GATE
<wp>: PASS" and the clean clone's PASS line, and each counts "1353 passed,
36 deselected" (36 more than at `22c2932`, as the report says). They are
ASCII and hold no credential, token or user path; each names the
repository by its path as before (G3). The gate issue-29 on the merge
prints the same 11 result lines as on `22c2932` (the recompute's 69 of 69,
the static check, the independence lines, the three planted breaks, the
export), 69 `reproduced` lines and the same 32 lines of plants, and "6
passed in 18.91s". The report's new text matches the logs; its only lines
that no log holds are the loop's "exit 0 after <n> s", which it now says
come from the loop (G1 answered), and it says the log of the run on
`694709b` was not kept (G2 answered). The state entry says what the logs
show.

Pass 2, part 2 (`c5afc28`, the report and the gate logs at `22c2932`): no
finding blocks. Each log starts "gate <wp> at commit
22c2932c017fc828c567263f91ed94a061371531 (clean)" and has 12, 18, 19, 15
and 16 PASS lines and no FAIL for issue-29, real-5a, real-5b, real-2 and
real-3a, "GATE <wp>: PASS", and "1317 passed, 36 deselected" in its unit
tests (R15). Of the report's eight text blocks, every line is in a log but
the command lines (written with `<repository>`) and the five lines "<gate>
exit 0 after <n> s" of the gate loop (G1). The two scripts the report
quotes are byte for byte those `22c2932` generates (R15). Its numbers hold
against the logs: 69 `reproduced` lines; the largest relative difference
2.4e-13, of `An07_09_Soc_Comp_ByTrt_PlacHigh`, a Fisher test; 42 Python
and 27 R; recompute 13.5 s; "6 passed in 18.82s" for the plants; 36, 106
and 3 ARD rows of the planted breaks; the export's four lines. Its account
of the review matches this file. No credential or token is in the logs and
no user folder; each names the repository it clones from by its path on
the machine, as the committed logs of earlier gates do (G3). The diff
`9dc6b20..c5afc28` touches nothing under `standard/`, `env/` or `kits/`, and
not PLAN.md. G1 and G2 are text and do not block. The final verdict waits
for the coordinator's last commit: the merge of `main` (`711c032`, with
catalog-2b) and the six gate logs of its clean clones; that review will
look at the merge's diff in cli.py and gates.py and those logs only.

F1 at `22c2932`: closed under the coordinator's stopping rule. M3 and its
kin are refused (a `Match` statement, a store into an attribute), so are
seven other ways to bind `sys` (`with ... as`, a walrus, `del`, a
comprehension target, a lambda argument, a `for` target, a type
parameter), and the 69 scripts pass the static check, 69 of 69 (R14). The
reviewer found no further route in this pass. What remains is what
decision 5 names itself: a number of the ARD computed from the allowed
constants, a route not named, and a sealed run that does not confine R or
pyarrow's reader. No sentence of decision 5 or static.py now claims more
than R14 shows. With F2 to F5 closed in part 1, no finding is open; the
verdict waits for part 2 (the report and the gate logs).

F1 at `ae07c86`: N2c, its kin and the writes elsewhere are refused, and the
69 scripts pass the static check, 69 of 69 (R13). One residual route
remains, not blocking: a `match` statement whose capture pattern binds
`sys` to a function of the script's own, whose attribute `argv` the script
sets (`f.argv = ['', <a climbing path>, sys.argv[2]]`); the template's line
then binds `adam` to another folder and the one allowed read reads the
built ADaM: `reproduced` (a control with a folder that does not exist fails
with FileNotFoundError on that folder, so the read did move). Two sentences
claim it is held: decision 5's "none of the names the templates use (Path,
sys, ...) is bound but in the templates' own lines" and its "Each call of
the one reader ... in the folder of the first argument" (static.py's
docstring says both too). No template writes `match` or stores an
attribute, so refusing `ast.Match` and attribute stores costs a line each.
By the coordinator's stopping rule this is recorded under F1 as a
residual. The verdict waits for part 2.

F1 again (`0e06dd4`): narrowed further, still open by one route, not
blocking. The five routes of pass 2 (N1, N2, RN1 to RN3) are refused by the
static check, and the 69 scripts pass it, 69 of 69 (R12). One new route
passes all three checks: `from pathlib import Path as Q` with a function of
the script's own named `Path` that climbs from the data folder (N2c), so
the template's line `adam, out = Path(sys.argv[1]), sys.argv[2]` binds
`adam` to the built ADaM and the one allowed read reads it: `reproduced`.
Three R tries pass the static check but fail when run (a computed function
name handed to `sapply` before a function written in place; `update()` of
a list; `lm(..., na.action = <computed name>)`). The reworded sentences are
true but for N2c, which "`adam` bound once by the line that names `Path`"
and "(Path is named nowhere else)" do not see. Details in F1.

Pass 2, part 1 (`b43c336`): F2, F3, F4 and F5 are closed; each fix was
re-run against the reviewer's own plants (R9, R10) and the commit adds them
as plants of its own (tests/unit, RC5, RC6). F1 is narrowed and stays open,
not blocking: every route of pass 1 is now refused (R9; S1 and S4 by the
audit hook and the fence, the rest by the static check), but five new
routes, each as deliberate as those of pass 1, pass the static check, the
sealed run and the comparison (R10: the data folder moved by `sys.argv` or
by rebinding `Path`, in Python; a function named by a computed string and
handed to `sapply`, in R, which sources the engine or reads the ARD). The
new general words of ADR-021 decision 5 ("they are not a proof ... a route
that is not named passes them") are true; four specific sentences still say
more than the checks hold (F1, pass 2). The 69 scripts are unchanged and
hold none of these constructs. At `b43c336` the reviewer's own recompute
gives 69 of 69 reproduced and PASS, tests/unit/test_recompute.py 16 passed,
tests/recompute 6 passed (R11); ruff and the ASCII check pass (R10). The
verdict stays open until part 2 (the report and the gate logs).

Pass 1 (`694709b`): no finding blocks. The five findings (F1 to F5) are not blocking; F1 and
F5 are words of ADR-021 and of printed lines that claim more than the code
holds, and should be corrected before the merge (the reviewer re-checks
them in pass 2). Each point of the brief, with the reviewer's own evidence:

1. Scope. `git diff --name-only 9dc6b20 694709b -- standard kits PLAN.md`
   names no file: nothing under `standard/` (schemas, `catalog@1`, the
   houses, the method registry and registry.json included), nothing of the
   kit, not PLAN.md. No ADR needed the owner first.
2. Independence. The generator imports, of specfirst, only
   `specfirst.recompute`, `kit`, `paths` and `machine.canonical`, and,
   transitively, no engine module: importing `recompute.generate`, `run`
   and `static` loads exactly `specfirst`, `specfirst.kit`,
   `specfirst.sources`, `specfirst.machine` (its `__init__` is a docstring),
   `specfirst.machine.canonical`, `specfirst.paths` and
   `specfirst.recompute.*` (R3). The generator reads the ARS, kit.yaml, the
   decision records and registry.json as data; it copies the gold ARD into
   the bundle and reads nothing of it; `numbers_of` takes numbers from where
   clauses and options only, never from results the ARS file embeds. The 69
   generated scripts call no part of the engine: the reviewer read one
   script of each of the ten templates in full and scanned all 69 (R4: no
   construct of F1 in any). The static check and the sealed run catch the
   direct routes (RC5, the unit tests) but not deliberate ones: 13 planted
   scripts pass the static check, and four pass the static check, the
   sealed run and the comparison, among them one that copies the ARD and
   computes nothing (F1).
3. The scripts recompute. They read the ADaM they are handed: one AGE of
   the ADSL copy changed by 1 makes the age summary differ in 2 of 24 rows,
   every CHG of the ADQSADAS copy plus 1 makes the Week 24 LS means differ
   in 9 of 12 rows (the standard errors stay) (R6, D1 and D2). The sealed
   run hands copies of the reference ADaM, `gold/reference/adam` of the
   build, each checked against the SHA-256 of kit.yaml through
   manifest.json, not the built ADaM. The generator's reading matches
   standard/methods/README.md on every point the pilot needs, read rule by
   rule: B1 (kit binding by operation ID), B2 (`Method registry: <id>`),
   B3 (exactly one descriptive operation by name); options in rising
   weight (registry default, kit binding, `programmingCode` with the
   context `specfirst method registry`); I3 (numbers as numbers, the empty
   text as missing, NE and NOTIN true for a missing value, comparisons
   false), I4 (another dataset by the subject key, at least one record),
   I5, I8 (every listed group), I9 and I10 (the combinations that occur on
   the analysis records, crossed with every defined group), I12a to I12d,
   I13 (the analysis set's one dataset, the AND parts of the subset on it),
   I15, I17 to I19. The numbers the semantics fix are right: SAS
   definition 5 is numpy's `averaged_inverted_cdf` (R type 2, statement 7
   of `summary.continuous`) and R type 7 is `linear`; CMH row
   mean scores with table scores is `coin::cmh_test` on an ordered response
   with the values as scores, general association on a nominal one; the
   LS-means weights are the option's value passed to `emmeans` (`weights =
   "proportional"` on the three LSM analyses, which state it in
   `programmingCode`); the Fisher population is ADSL with SAFFL = Y and
   TRT01A in the two compared arms, the TRTEMFL part left out (read in the
   generated script of `An07_09_Soc_Comp_ByTrt_PlacLow`).
4. The comparison. Rows are matched by operation and group parts, a count
   (`result` integer) exactly, other values within a relative 1e-9 (1e-6
   for the mixed model) or an absolute 1e-12, missing only against
   missing; a lost row, an added row and a script without output give
   `differs` (RC6, the unit test), and so does a row written twice (read in
   `judge`). Three edges: an
   analysis with no row on either side is `reproduced` (F2), a plan with
   fewer groupings than the ARD rows collapses them (F2), a script that
   fails after writing its output is `reproduced` in report.json (F3); and
   the absolute 1e-12 holds at every magnitude (F4). None of these occurs
   on the pilot: every analysis has at least one row, the largest relative
   difference of the 69 is 2.4e-13.
5. The planted breaks. RC2 replaces `weights = weights, data = frame` in
   `model_emmeans` of a copy of r/specfirstr/R/models.R by `weights =
   "equal"`; the LS means use it and the pairwise comparisons already pass
   "equal", so exactly the LS means change: 36 ARD rows, none shown by a
   cell of a built grid, and the scripts give `differs` for the three LSM
   analyses and `reproduced` for the 66 others. R11 cannot see it (R
   only). RC3 swaps the quantile definition in both engines (Python by
   monkeypatching `methods.quantile`, which `summary_continuous` calls
   through the module; R by `QUANTILE_TYPES`): 106 rows change, the engines
   agree on all, the four analyses with quartiles differ. RC4 swaps the
   CMH statistic in both engines: 3 rows change, the engines agree, the
   three CMH analyses differ. ADR-021 decision 7 is true as stated (R2).
   The owner's Q2 speaks of "a CMH-scores defect"; RC4 plants the
   statistic, not the option `scores` (table against rank). ADR-021 says
   so plainly and the design was accepted as sent; a plant of `scores`
   would be the closer reading if that is what was meant (for the report
   to say). Pass 2: decision 7 now says the statistic, not the option
   `scores`, is swapped, as in the design the owner accepted.
6. The gate. Its checks are those of ADR-021 decision 9, in that order.
   `recompute` passes only when the report counts exactly
   `{"reproduced": 69}` and the static check, the sealed runs and the
   comparison have nothing (`RECOMPUTE_ANALYSES`; RC1 asserts 69 too); an
   analysis not covered, added or lost fails it. `planted break` runs
   tests/recompute strictly with the six IDs RC1 to RC6 required
   (`junit_problems`: a required ID that did not run, failed or was skipped
   fails the check; the test names are `test_recompute[RC1-unplanted]` and
   so on). `independence` fails on a static problem, a generator import or
   a sealed failure; `export` on other bytes of the bundle generated again,
   on another output or report of `run_all.sh`. Each check fails on the
   defects its tests plant (rule R5); F1 lists the defects in its scope it
   does not see.
7. Determinism and hygiene. No clock or randomness reaches an output
   (`time.monotonic` only times the gate's log lines); outputs follow the
   order of the ARS groups, data-driven values sorted, R's `order` under
   `LC_ALL=C.UTF-8`; the bundle generated again from the same build has
   the same bytes, 78 of 78 files (R7). The 20 changed files are ASCII;
   `python -m specfirst.asciicheck`: 851 files, 0 with non-ASCII bytes;
   `ruff check src tests`: all checks passed (R8). No local user path,
   credential or token in the diff (a search for user folders, drive
   paths, "token", "password", "secret" and key prefixes finds only
   pre-existing CLAUDE.md text and the identifier `token` of the R
   parser). The bundle holds 42 Python and 27 R scripts, adam_csv.py,
   compare.py, the three gold ARD files, plan.json, manifest.json,
   README.txt and run_all.sh: no ADaM, no CSV, no subject-level record
   (Q3).
8. ADR-021 against the code. Decisions 1, 3, 4, 7, 8 and 9 are what the
   code does; on the pilot a script has 20 to 50 lines of code without
   comments, median 30, as decision 3 says (R4). Decision 5 claims more
   than the checks hold (F1). Decision 6: "a script that fails is
   `differs`" holds only when it wrote no output (F3); "an absolute 1e-12
   near 0" is an absolute 1e-12 everywhere (F4). Decision 2: "Their content
   is covered" is true of E25 and only in part of E24 (F5).

## Findings

### F1 (not blocking) The three checks of "no part of the engine" hold the direct routes only

ADR-021 decision 5 says the static check refuses "nothing that runs other
code, reads another kind of file or walks the file system; no path in a
text; the only files named are the ADaM datasets of the plan; every number
is one the ARS states ..., so no number of the ARD can stand in a script",
and that the engine's R code "is reachable only by a path, which the static
check refuses". The docstring of static.py ends "So no line of the engine
and no number of the ARD can stand in a script"; that of run.py says "a
script could reach it only by a path, which the static check refuses"; the
command prints "static check: 69 of 69 scripts call no part of the engine".

What the code holds: Python imports and R calls by name against
allow-lists, but Python names and attributes against a deny-list, and in
both languages only literal tokens: a string containing "/" or "\", a
string ending in a file suffix, a numeric literal. Planted into real
generated scripts (the age summary `An03_01_Age_Summ_ByTrt`, the Week 24 LS
means `An_ADAS_W24_LSM`), with the analysis's own numbers, these pass
`static.python_problems` and `static.r_problems` (R5):

- Python: a number of the ARD in a string (`float("...")`); the built ADaM
  by `adam / ".." / ".." / ... / "adsl.parquet"`; the root from
  `Path(sys.argv[1]).anchor`; `__builtins__["exec"](...)`; a "/" from
  `chr(ord("0") - 1)`; `numpy.memmap` of any file; `pandas.eval`; a file
  name in two parts (`"efficacy-adas.js" + "onl"`).
- R: `sapply(<path>, "source")` and `apply(..., 1, "source")` (a function
  named by a string, which R looks up); `"source"(<path>)` (R's parser
  gives the name as `STR_CONST`, not a call); a number in a string through
  `as.numeric`; `utils::read.csv` of the ARD by `file.path("", "tmp", ...,
  paste0("efficacy-adas.js", "onl"))`.

The sealed run sets the environment and the working folder; it does not
confine what a script reads. The interpreter is the project's environment,
in which `specfirst` is importable (`python -I -B -c "import specfirst"`
prints the worktree's `src/specfirst/__init__.py`, the editable install),
so seal.py rests on its `meta_path` hook alone; a script can remove the
hook, import the engine and drop it from `sys.modules` before seal.py
looks; and seal.py's last check does not run when a script raises
`SystemExit` (read in seal.py). R has no barrier at all. Run sealed exactly
as the gate runs them (`run.run_one`, then the bundle's compare.py), four
planted scripts pass the static check, the sealed run and the comparison
(R6):

- S1: the age summary imports `specfirst.machine.methods` past seal.py
  (its log: "engine loaded from <clone>/src/specfirst/machine/methods.py"):
  `reproduced`, 24 rows;
- S2: the age summary reads the built ADaM, `build/kits/cdiscpilot01/
  gold/data/adam/adsl.parquet`, by `..` steps: `reproduced`;
- S3: the LS means source `r/specfirstr/R/models.R` (its log prints the
  path): `reproduced`, 12 rows;
- S4: a script for the age summary that computes nothing and writes the
  ARD's own rows, read from `build/kits/cdiscpilot01/gold/ard/`:
  `reproduced`, 24 rows.

Why it does not block: every route above is deliberate, none is a mistake
a template would make, and the checks fail on every direct route (an
import, `open`, a literal path, a pasted number, `source`, `library`,
`:::`; RC5 and the unit tests). The 69 scripts of this commit hold none of
the constructs (R4: no string constant that reads as a number the ARS does
not state for the analysis, no `__builtins__`, `chr`, `ord`, `__file__`,
`anchor`, `eval`, `query`, `memmap`, no string `".."`, no string in call
position, no string argument of `apply` or `sapply`), and the generator
reads nothing of the ARD. So the issue's requirement holds for this work;
what does not hold is the claim that the machine checks prove it.

What to change: say what the checks hold (ADR-021 decision 5, the
docstrings of static.py and run.py, the handover in docs/state/real.md, the
printed "call no part of the engine", which could read "pass the static
check"): literal imports, calls, file names, paths and numbers; a sealed
environment that refuses a plain import, not a confinement. Or close the
routes found here, which costs a few lines: refuse the Python names
`__builtins__`, `chr`, `ord`, `__file__` and the attributes `anchor`,
`eval`, `query`, `memmap`; refuse the string `".."` and a string constant
that reads as a number the ARS does not state; in R refuse a `STR_CONST`
followed by `(` and a string argument of `apply` and `sapply`. Neither
closes every route (a deny-list cannot); the words should say so.

Pass 2 (`b43c336`): narrowed, still open, not blocking. The static check now
allow-lists Python builtins and attributes, refuses dunders, pins every read
to `pd.read_parquet(adam / "<d>.parquet")` and `utils::read.csv(file.path(adam,
"<d>.csv"), ...)`, and refuses texts with "..", a backslash or an unstated
number, a call of a string, a string constant at depth 1 of `apply` or
`sapply`, a forbidden name in a string and a function used as a value.
seal.py's audit hook refuses the import of specfirst or yamaa and every
Python open in the checkout and the build, and its last check runs in a
`finally`. Every route of pass 1 is refused (R9): P1 to P7 and R1 to R5 by
the static check (P8 only binds a name in two parts, which no allowed
reader can use); S1 by the audit hook ("refused by the sealed run:
specfirst.machine.methods") and S4 by the fence ("an open of
.../gold/ard/common-safety-displays.jsonl"); S2 and S3 still run sealed
(pyarrow's reader and R are not fenced, as decision 5 now says) but the
static check refuses them. Five new routes pass the static check, the
sealed run with the fence of `run.recompute`, and the comparison (R10):

- N1 (Python): `s = sys.argv[1][0]`, then `sys.argv[1] = s + "tmp" + s +
  ...` before the template's own `adam, out = Path(sys.argv[1]),
  sys.argv[2]`: the age summary reads the built ADaM,
  `build/kits/cdiscpilot01/gold/data/adam/adsl.parquet`, in the one allowed
  form; pyarrow's reader is not fenced: `reproduced`, 24 rows;
- N2 (Python): `P = Path` and `Path = lambda p: P(p) / ('.' + '.') / ...`:
  the same read, the same result;
- RN1 (R): `s <- sprintf("%.1s", args[1])` (the first character of the
  data folder, "/"), then `sapply(paste0(s, "tmp", ..., "models.", "R"),
  paste0("sou", "rce"))`: the Week 24 LS means source
  `r/specfirstr/R/models.R` (the log prints the path): `reproduced`, 12
  rows;
- RN2 (R): the same with `f <- paste0("sou", "rce")` and `sapply(path, f)`;
- RN3 (R): `sapply(<path of gold/ard/efficacy-adas.jsonl>, paste0("read",
  "Lines"))` reads the ARD (the log prints its line count, 331), and the
  script still gives its rows: `reproduced`.

N3, a number of the ARD built from digits (`float('1' + '.' + str(2 + 2)
...)`), passes too; decision 5 now names that route ("computes a number of
the ARD from the allowed constants"), so it is not counted against the
words. A fifth R try, `update(list(call = paste0("sou", "rce")), file =
path)`, is refused (the argument name `file`) and fails when run. The
general words of decision 5 ("What these checks hold is the form of a
script and the routes they name; they are not a proof ... a route that is
not named passes them") are true. These sentences are not:

- ADR-021 decision 5: in R "no string is called or handed to apply or
  sapply" (only a string constant is refused; RN1 and RN2 hand a computed
  string), and "Every read has one form, of an ADaM dataset of the plan in
  the folder of the first argument" (N1 and N2 read another folder in that
  form; RN3 reads the ARD by another function);
- run.py's docstring: "the static check holds every read of a script to the
  ADaM datasets of its plan in the data folder" (N1, N2, RN3);
- the line RC5 prints: "not held by the sealed run, held by the static check
  above: a read by pyarrow's own code (the built ADaM by parent folders) and
  any read or source in R" (N1 and N2 for pyarrow; RN1 to RN3 for R);
- the line the gate's check `independence` prints: "read only the ADaM
  datasets of their plan from the data folder" (the same routes).

The 69 scripts are the same text as in pass 1 (no writer changed), so R4's
scan stands for them, and none stores into `sys.argv`, rebinds an imported
name, calls `sprintf` on a string, or hands `apply` or `sapply` anything but
an inline `function` (read in pywrite.py and rwrite.py). Cheap closures, if
the author prefers them to words: refuse a store into `sys.argv` and the
rebinding of a name an import binds (Python); require the function argument
of `apply` and `sapply` to be an inline `function(...)`, and refuse `args`
assigned anywhere but `args <- commandArgs(trailingOnly = TRUE)` (R).
Either way the four sentences above need to match what the checks hold.

F1 again (`0e06dd4`): narrowed further, still open by one route, not
blocking. The static check now reads `sys` only as `sys.argv[1]` or
`sys.argv[2]`, refuses rebinding an imported name, `Path` outside the line
that binds `adam`, an argument named `adam`, `global` and `nonlocal`; in R
it requires a function written in place as the last argument of `apply`
and `sapply`, a formula written in place as the first argument of `lm`,
`mmrm` and `cmh_test`, only `df = ...` in `update`, `args` bound only by the
template and read only as `args[1]` or `args[2]`, and no formal or argument
named `adam` or `args`. RC5 and tests/unit plant N1, N2 and RN1 to RN3 and
their kin. On a bundle generated by `0e06dd4` (R12):

- the 69 scripts pass the static check, 69 of 69;
- N1, N2, RN1, RN2, RN3 are refused ("sys used otherwise than as
  `sys.argv[1]` or `sys.argv[2]`, read"; "Path used otherwise than in ...";
  "the function of sapply is not written in place");
- N2c passes the static check, the sealed run and the comparison:
  `from pathlib import Path` replaced by `from pathlib import Path as Q`
  and `def Path(p): return Q(p) / ('.' + '.') / ('.' + '.') / 'review29' /
  'build' / 'kits' / 'cdiscpilot01' / 'gold' / 'data' / 'adam'`. `Path` is
  then a name the script binds by `def`, not an imported one, the line that
  binds `adam` has the template's exact syntax tree, and the read is the one
  allowed form; pyarrow's reader is not fenced: `reproduced`. The same with
  `class Path` is refused (a class name is not a bound name for the check);
- RV1 `sapply(<path>, paste0("sou", "rce"), function(z) z)`, RV2
  `update(list(call = list(paste0("sou", "rce"), <path>)), df = 1)` and RV3
  `stats::lm(CHG ~ TRT, data = d, na.action = paste0("sou", "rce"))` pass
  the static check and fail when run (`source` has no `...` and no use for
  a function or a data frame; R's `source` formals are listed in R12):
  `differs`. The reviewer found no function reachable this way that reads
  a file or runs one with such an argument; it is not a proof either;
- writes are not held: a Python `to_csv` or an R `utils::write.csv` to a
  path built from `sys.argv[1][0]` or `sprintf("%.1s", args[1])` writes
  outside the sealed folder (refused here only because the planted name
  ends in `.csv`; another name passes). A write brings no number in, so it
  is no route to the ARD; noted because the fence and decision 5 speak of
  reads.

The reworded sentences (decision 5 "Each call of the one reader of each
language has one form ...", under its caveat; run.py "as far as a check of
the form holds"; RC5's "not held by the sealed run: a read by pyarrow's own
code, and R; there only the static check's form of a read stands"; the
gate's "call their reader only in the one form of a read of a dataset of
their plan") are true, except that N2c reads in that form from another
folder than the first argument's, against decision 5's "`adam` bound once
by the line that names `Path`" and static.py's "(Path is named nowhere
else)". Cheap closure: require `from pathlib import Path` with no alias
(and the template's aliases `np`, `pd` only), and refuse any `def`, class
or other binding of the names the template uses (`Path`, `sys`, `pd`,
`np`, `stats`, `product`, `adam`, `out`, `num`). The 69 scripts hold none of
this (no `def` but `num`, no import alias but `np` and `pd`).

F1 at `ae07c86`: one residual, not blocking. The static check now takes only
the templates' six import statements (compared as syntax trees), no class,
no binding of `Path`, `sys`, `pd`, `np`, `stats`, `product`, `adam`, `out` or
`num` but the template's binding line and its `def num` (syntax tree), and
one write per language, `.to_csv(out, index=False)` and
`utils::write.csv(rows, args[2], ...)`. On a bundle generated by `ae07c86`
(R13): the 69 scripts pass, 69 of 69; N2c, `Path` imported under another
name, N1, a second `def num`, a Python write elsewhere and an R write
elsewhere are refused. Passed and harmless: a second write to `out` (the
last one stands), and a reserved name bound by a `match` capture to a
value of no use (`case num:`, `case adam:` before the binding line).
Passed and not harmless, the residual:

- M3: `s = sys.argv[1][0]`, `here = sys.argv[1] + s + '.' + '.' + s + '.'
  + '.' + s + 'review29' + ... + 'adam'`, `o = sys.argv[2]`, `def f():
  pass`, `f.argv = ['', here, o]`, `match f: case sys: pass`, then the
  template's `adam, out = Path(sys.argv[1]), sys.argv[2]`. A capture pattern
  binds by a name that is not an `ast.Name` node, and an attribute store
  `f.argv = ...` takes an allowed attribute, so the static check sees
  neither; `sys` is then the function, the line that binds `adam` has the
  template's syntax tree, and `pd.read_parquet(adam / "adsl.parquet")`
  reads `build/kits/cdiscpilot01/gold/data/adam/adsl.parquet` (pyarrow, not
  fenced): `reproduced`. The control, the same with `'nowhere'` for
  `'build'`, fails with FileNotFoundError on
  `.../review29/nowhere/kits/cdiscpilot01/gold/data/adam/adsl.parquet`.

Sentences that claim M3 is held: ADR-021 decision 5, "none of the names the
templates use (Path, sys, pd, np, stats, product, adam, out, num) is bound
but in the templates' own lines" and "Each call of the one reader of each
language has one form, of an ADaM dataset of the plan in the folder of the
first argument"; static.py's docstring says both ("binds none of the names
the templates use ... but in the templates' own lines"; "Each call of its
one reader has one form, a dataset of its plan in the folder of its first
argument"). No template writes a `match` statement or stores an attribute,
so `ast.Match` and an `ast.Attribute` in a store context can each be
refused in a line (`MatchAs`, `MatchStar` and `MatchMapping` are the
capture forms). Otherwise the sentences need "except ...". The reviewer
found no route in R at `ae07c86`: the reads and the write are pinned, a
computed function name reaches no reader (RV1 to RV3, R12), and `args` and
`adam` are pinned.

F1 at `22c2932`: closed. The static check refuses a `Match` statement or
clause, `Try`, `TryStar`, an `ExceptHandler`, a type alias or type
parameter, and a store or delete into an attribute; decision 5 and
static.py's docstring name these rules ("no match, try or type parameter
written and no attribute stored into"). On a bundle generated by `22c2932`
(R14): the 69 scripts pass, 69 of 69; M3 is refused ("a Match statement or
clause"; "a store into the attribute argv"), and so are its two halves
alone and the other ways to bind `sys` the reviewer tried (`with f() as
sys`, `(sys := 1)`, `del sys`, `[1 for sys in [1]]`, `lambda sys: sys`,
`for sys in [1]`, `def g[sys](x)`). Under the coordinator's stopping rule
(a further deliberate route is a documented residual; a sentence that
claims it is held is fixed) the reviewer stopped here. The residuals are
the ones decision 5 states: a number of the ARD computed from the allowed
constants (N3), a route not named, and a sealed run that confines neither R
nor pyarrow's reader (S2, S3, N1 and RN1 to RN3 run sealed when the static
check is set aside). Its sentences on the form of a read and on the names
the templates bind are true of every route the review tried.

### F2 (not blocking) compare.py reports `reproduced` with no rows, and with rows it never compared

`judge` builds `expected = {ard_key(row, groupings): row ...}` with
`groupings = len(entry["groupings"])`, the generator's reading. On a toy
plan (R5, C1 and C3):

- an analysis with no ARD row and an output with its header only:
  `reproduced`, "0 rows";
- a plan with one grouping and ARD rows with two (`group2_groupId` X and
  Y): `ard_key` ignores the second part, the dict keeps one of the two
  rows, and the script's single row equal to it is `reproduced`, "1 rows".

Two ARD rows with one key would collapse the same way. On the pilot none
occurs: the fewest rows of an analysis are 1 (the tests), and the plan's
groupings come from the same ARS file as the engine's. A wrong reading of
the groupings by the generator would show as a lost or added row in almost
every case, but not in all. Fix: `differs` when an analysis has no ARD
row, when an ARD row has a `group<n>_groupingId` beyond the plan's
groupings, or when two ARD rows have one key.

Pass 2 (`b43c336`): closed. `judge` gives `differs` for an analysis without
ARD rows, for ARD rows with a `group<n>_groupingId` beyond the plan's
groupings, and for two ARD rows of one key. The reviewer's C1 and C3 are
now `differs` ("the ARD has no row of the analysis"; "ARD rows of more
groupings than the plan reads: ['group2_groupingId']") (R9);
`test_compare_vacuous_and_failed` and RC6 (an analysis whose ARD rows were
removed) plant the three cases.

### F3 (not blocking) A script that fails after writing its output is `reproduced`

`run_one` deletes the target before the run and returns the failure, but a
script that writes its output and then exits with an error leaves the
output in place, and compare.py judges it like any other: the age summary
followed by `raise SystemExit(3)` gives `run_one` "exit 3" and `reproduced`
(R6, C2). The run as a whole fails (`Result.passed` needs no sealed
failure, and `report_lines` adds "sealed run failed"), so the gate cannot
pass on it; but report.json and report.txt, the per-analysis report, say
`reproduced`, while ADR-021 decision 6 says "a script that fails is
`differs`". (In the reviewer's own run, run_all.sh's `set -eu` stops before
the comparison.) Fix: remove the output of a failed script, or hand the
failures to compare.py.

Pass 2 (`b43c336`): closed. `run_one` removes the output of a failed script
and writes `<analysis>.failed` with the reason, which `judge` reads first.
The reviewer's C2 now gives `run_one` "exit 3", no output kept, and
`differs`: "the script failed: exit 3" (R10). The script now writes into
its own sealed folder and run.py copies the output out only when it
exists; a stale `.failed` cannot survive, since `run_bundle` removes
`out/` first.

### F4 (not blocking) The absolute 1e-12 holds at every magnitude

`same` accepts `gap <= ABSOLUTE or gap <= tolerance * max(...)`, so any two
values within 1e-12 are the same, whatever their size: 1e-13 against 9e-13
is `reproduced`, with "largest relative difference 8.9e-01" printed (R5,
C4). ADR-021 decision 6 says "an absolute 1e-12 near 0". On the pilot 5 ARD
values lie between 0 and 1e-3, all Fisher p-values, the smallest 4.0e-05,
where the allowance is a relative 2.5e-8 instead of 1e-9; the largest
relative difference of the 69 analyses is 2.4e-13 (R4), so nothing is
hidden here. A p-value can be far below 1e-12 on other data. Either say
"an absolute 1e-12 at any size", or allow the absolute part only where the
ARD's value is 0.

Pass 2 (`b43c336`): closed. `same` allows the absolute 1e-12 only where the
ARD's value is 0, and a relative 1e-9 (1e-6 for the mixed model)
otherwise; decision 6 and compare.py's docstring say so. C4 is now
`differs` (R9). On the pilot this costs nothing: the ARD has 858 values
equal to 0 and no non-zero value below 1e-9 (R10), so no value that ought
to be 0 and came out as a rounding residue is held to the relative test.

### F5 (not blocking) "Its content is covered" is true of E25 and only in part of E24

ADR-021 decision 2 and the line `specfirst recompute` prints for E24 (run.py
`EVIDENCE_TABLES`): "its content is covered by the demographics analyses of
CDISC's example, Out14-1-1, on ADSL". E24 (PLAN.md section 3: 244 printed
cells of CSR 14-2.01) is computed by evidence/csr_demog_spike.py on ADSL
with ITTFL = Y, with rows for MMSE (MMSETOT), the duration of disease
(DURDSGR1, DURDIS), the years of education (EDUCLVL), weight (WEIGHTBL), BMI
(BMIBLGR1, BMIBL) and race as an "origin" grouping. The kit's demographics
analyses (An03_01 to An03_06) are on the safety set and read AGE, AGEGR1,
SEX, ETHNIC, RACE and HEIGHTBL. So E24's content is covered in part (age,
age group, sex, height; race by another grouping). E25's spike groups by
AEBODSYS and the example by AESOC; the two are equal on all 1,191 ADAE
records (R4), so that line holds. The owner's answer to Q1 sets the scope
(the 69 analyses first), so nothing is missing from the work; the words
must not tell the owner that 14-2.01 is covered. Also, the three lines E24
to E26 are printed by the command only: report.txt, report.json and the
bundle's README.txt carry none (R4), while decision 2 says "the report
gives it a line 'not built'"; for docs/reports/issue-29.md it holds once
the command's output is in it.

Pass 2 (`b43c336`): closed. The E24 line reads "covered in part: its rows
of age, age group, sex, race and height are recomputed ... on the safety
population and race by another grouping; its ITT population and its rows
of MMSE, duration of disease, education, weight and BMI are not"; E25 names
AESOC equal to AEBODSYS; decision 2 says the same. The three lines moved to
`generate.EVIDENCE_TABLES`, plan.json carries them, compare.py writes them
into report.json and report.txt, and README.txt lists them (R10: plan.json
of a bundle generated by `b43c336` has E24, E25, E26, and `text_lines`
prints them).

### G1 (not blocking) The durations of the five clean-clone runs stand in no log

Pass 2, part 2. The report's section "The gates on clean clones" gives
"issue-29 exit 0 after 743 s", "real-5a exit 0 after 1231 s", and so on.
These lines come from the loop that ran the five gates, and no committed
log holds them: each log ends with the gate's own summary and the clean
clone's closing lines, with the time of each check but no total (R15).
The result they report, exit 0, the logs do show ("GATE <wp>: PASS" and
the clean clone's "PASS" line, five times). The seconds are the run's
cost, not evidence of a result. Rule R8 asks for the output: a line in the
report saying where these come from, or the loop's output kept, settles
it.

Final (`0ae9b24`): answered. "The gates on clean clones" now says "The exit
codes and seconds below are the lines of the loop that ran the five gates,
which is not a committed file; each log shows its own checks and verdict",
and "On the merge with main" says the same of its six ("the seconds are
again the loop's").

### G2 (not blocking) The run on `694709b` is stated, not shown

The same section says "The gate issue-29 passed on a clean clone of
`694709b` too (12 of 12, 1170 s)". No committed log holds that run; the
logs are of `22c2932`. The report says "only the runs on `22c2932` count",
and nothing rests on the earlier run, so it is history, not evidence. The
sentence could say that its log was not kept.

Final (`0ae9b24`): answered: "its log was not kept, the run on `22c2932`
wrote over it"; "only the runs on `22c2932` and on the merge below count".

### G3 (not blocking) The logs name the repository by its path on the machine

Each of the five logs has `repository: /mnt/<drive>/<folder>/specfirst/.git`
(written so here) and the `git clone` line from it. The path names a
drive and a working folder, no user and no home folder, and the committed logs of earlier
gates have the same line (for example base-0.gate.log,
catalog-2a.catalog-2a.gate.log, adr-017.read-2a.gate.log); the report
itself writes `<repository>`. No credential, token or user path is in any
of the five logs (R15).

## What was read

`CLAUDE.md`; docs/state/real.md (all, the new section in detail);
ADR-021 in full; the skeleton docs/reports/issue-29.md;
standard/methods/README.md in full (B1 to B3, I1 to I19);
standard/methods/registry.json, the semantics and options of the ten
entries the scripts use; kits/cdiscpilot01/kit.yaml, gold/events/
(efficacy-adas.json, efficacy-cibic.json: every analysis, set, subset and
grouping), gold/decisions/efficacy.jsonl (ids, status, binds); the ARS
example's analyses, sets, subsets and groupings in the fetch cache (read
only); docs/reports/issue-30.review.md (the form). In full: every file of
src/specfirst/recompute/, the diff of gates.py and cli.py,
tests/unit/test_recompute.py, tests/recompute/test_recompute_pilot.py. In
part: gates.py (`junit_problems`, `_pytest`, `run_gate`, `_first_build`),
machine/ard.py (`population`, `population_groups`, `counts`),
r/specfirstr/R/models.R (`model_emmeans`, the LS means and pairwise
functions), r/specfirstr/R/methods.R (`QUANTILE_TYPES`, the CMH guard),
machine/methods.py (`quantile`, `cmh_p` and their callers), kit.py,
sources.py, paths.py and machine/canonical.py (imports), pyproject.toml
(pytest options), evidence/csr_demog_spike.py and csr_ae_spike.py, PLAN.md
lines of E24 to E26. Generated scripts read in full: the count of the
safety set, the age summary, the organ class and term percentages, a
chi-square, an ANOVA, the Fisher test by organ class, a CMH test, the
Week 24 LS means, a dose response, a mixed-model comparison.

Pass 2, part 1: the diff `694709b..b43c336` in full (static.py, seal.py,
run.py, compare.py and generate.py whole at `b43c336`; ADR-021 decisions 2,
5, 6 and 7; docs/state/real.md; gates.py; both test files).

## What was run

All Linux commands ran in Ubuntu 24.04 under WSL2 as root, from script
files kept outside the repository, after the worktree's `scripts/env.sh`,
with `PYTHONPATH=<clone>/src` and `PYTHONDONTWRITEBYTECODE=1`; each run
prints the module file it loaded (`<clone>/src/specfirst/__init__.py`).
Python 3.12.3, R 4.6.2. The build, the recompute run and both test files
(R1, R2) ran in one acquisition of `flock /run/lock/specfirst-heavy.lock`
under `taskset -c 0-3`. The reads and plants R3 to R8 run single
processes for seconds (at most one script at a time, no build, no test
suite, no gate) and ran under `taskset -c 0-3` outside the lock while
other sessions' gates held it; so did R9 and R10 of pass 2, while the
clean-clone gates of `b43c336` held it.

| # | What | Result |
| --- | --- | --- |
| R1 | `specfirst kit assemble`, `build`, `recompute cdiscpilot01` in `<clone>` | 69 scripts of 69; 69 reproduced; PASS |
| R2 | `pytest tests/unit/test_recompute.py`; `SPECFIRST_STRICT=1 SPECFIRST_RECOMPUTE_REUSE=1 pytest -s tests/recompute` | 15 passed; 6 passed, the plants' lines as quoted in point 5 |
| R3 | the generator's imports, transitively; `specfirst` under `python -I` | no engine module; the worktree's editable install |
| R4 | facts of the run and the bundle; a scan of the 69 scripts | rows, differences, sizes, small values; 0 odd constructs; AEBODSYS = AESOC |
| R5 | 13 static plants; 3 comparison plants on a toy plan | 13 pass the static check; C1, C3, C4 `reproduced` |
| R6 | sealed-run plants S1 to S4, C2; data plants D1, D2 | S1 to S4 pass and are `reproduced`; C2 `reproduced`; D1, D2 `differs` |
| R7 | the bundle generated again from the same build | 78 of 78 files, the same bytes |
| R8 | ruff, the ASCII check, `specfirst fetch --verify`, `git status` | all pass; the worktree clean |
| R9 | pass 2, `<clone>` at `b43c336`: the pass-1 static plants and comparison plants again | P1 to P7, R1 to R5 refused (P8 binds a name only); C1, C3, C4 `differs` |
| R10 | pass 2: a bundle generated by `b43c336`; new routes N1 to N3, RN1 to RN4 and the pass-1 routes S1 to S4 run sealed with the fence; C2; ruff, ASCII | N1, N2, N3, RN1, RN2, RN3 pass all three; S1, S4 refused when run; C2 `differs`; ruff and ASCII pass |
| R11 | pass 2: `specfirst recompute`, tests/unit/test_recompute.py, tests/recompute at `b43c336` | 69 reproduced, PASS; 16 passed; 6 passed |
| R12 | F1 again, `<clone>` at `0e06dd4`: the 69 scripts; N1, N2, RN1 to RN3; new tries N2b to N2d, RV1 to RV4, PV1; R's formals | 69 of 69 pass; N1, N2, RN1 to RN3 refused; N2c passes all three; RV1 to RV3 pass the static check and fail when run |
| R13 | F1 at `ae07c86`: the 69 scripts; N2c and kin, the writes, `def num`, match captures, M3 and its control | 69 of 69 pass; N2c, N2b, N1, D1, W2, RW1 refused; M1, M2, W1 pass and are harmless; M3 passes all three; its control fails on the missing folder |
| R14 | F1 at `22c2932`: the 69 scripts; M3 and its halves; seven other bindings of `sys` | 69 of 69 pass; all ten refused |
| R15 | part 2, `c5afc28`: the five logs (header, results, unit tests, last lines, bytes); the report's text blocks against them; the quoted scripts against those `22c2932` generates; a search of the logs for paths and credentials; the scope of `9dc6b20..c5afc28` | as quoted in the Outcome; G1, G2, G3 |
| R16 | final, `0ae9b24`: the merge's diff in cli.py and gates.py against both sides; main's reach; the six merged logs; the report's new section against them; the result lines of the gate issue-29 on both commits | as quoted in the Outcome |

### R1 Build and recompute

```text
$ python -m specfirst kit assemble cdiscpilot01
kit cdiscpilot01: 67 files match their pinned SHA-256 (26 inputs, 41 gold) in <clone>/build/kits/cdiscpilot01
$ python -m specfirst build cdiscpilot01          # exit 0, 25 s
build cdiscpilot01: 10 datasets, 1576 nodes, 5251 edges, 56 files in <clone>/build/kits/cdiscpilot01
$ python -m specfirst recompute cdiscpilot01      # exit 0, 13 s
recompute cdiscpilot01: 69 scripts of 69 analyses written to <clone>/build/recompute/cdiscpilot01/bundle
reproduced   common-safety-displays/An01_05_SAF_Summ_ByTrt: 3 rows, largest relative difference 0.0e+00
reproduced   common-safety-displays/An03_01_Age_Summ_ByTrt: 24 rows, largest relative difference 1.1e-16
...  (69 lines "reproduced" in all)
reproduced   efficacy-cibic/An_CIBIC_W24_Cmh: 1 rows, largest relative difference 1.8e-15
cdiscpilot01: 69 analyses: reproduced 69
static check: 69 of 69 scripts call no part of the engine
E24 CSR 14-2.01 (demographics): not built as a CSR table (real-4); its content is covered by the demographics analyses of CDISC's example, Out14-1-1, on ADSL
E25 CSR 14-5.01 (adverse events by organ class and term): not built as a CSR table (real-4); its content is covered by the analyses of Out14-3-2-1, on ADAE
E26 CSR 14-6.06 (Hy's law shifts, CMH): not built: no ARS analysis in the kit (real-5); its method, test.cmh, is covered by CSR 14-3.13
recompute cdiscpilot01: PASS
```

### R2 The two test files

```text
$ python -m pytest -q -p no:cacheprovider tests/unit/test_recompute.py
15 passed in 4.00s
$ SPECFIRST_STRICT=1 SPECFIRST_RECOMPUTE_REUSE=1 python -m pytest -s -q -p no:cacheprovider tests/recompute
cdiscpilot01: 69 analyses: reproduced 69
planted: the ANCOVA LS means with equal weights where the analysis states proportional: 36 ARD rows change, 0 of them shown by a cell of a built grid; the scripts: 3 analyses differ: efficacy-adas/An_ADAS_W08_LSM, efficacy-adas/An_ADAS_W16_LSM, efficacy-adas/An_ADAS_W24_LSM
planted: quartiles by R type 7 in both engines: 106 ARD rows change, the engines disagree on 0; the scripts: 4 analyses differ: common-safety-displays/An03_01_Age_Summ_ByTrt, common-safety-displays/An03_06_Height_Summ_ByTrt, common-safety-displays/An08_01_Obs_Summ_ByTrt, common-safety-displays/An08_02_ChgBl_Summ_ByTrt
planted: CMH general association in both engines: 3 ARD rows change, the engines disagree on 0; the scripts: 3 analyses differ: efficacy-cibic/An_CIBIC_W08_Cmh, efficacy-cibic/An_CIBIC_W16_Cmh, efficacy-cibic/An_CIBIC_W24_Cmh
planted in An03_01_Age_Summ_ByTrt: an import of the engine: ['line 11: import specfirst']
planted in An03_01_Age_Summ_ByTrt: the ARD read: ["line 18: a file other than the ADaM datasets of the plan: 'common-safety-displays.jsonl'"]
planted in An03_01_Age_Summ_ByTrt: the built ADaM by a path: ["line 18: a path in the text '../data/adam/adsl.parquet'"]
planted in An03_01_Age_Summ_ByTrt: a number of the ARD: ['line 40: the number 1.4885404260186454, which the ARS does not state for the analysis']
planted in An_ADAS_W24_LSM: a source of the engine: ["a path in the text 'r/specfirstr/R/models.R'"]
planted in An_ADAS_W24_LSM: a library: ['the call library']
planted in An_ADAS_W24_LSM: a number of the ARD: ['the number 1.4885404260186454, which the ARS does not state for the analysis']
planted in An03_01_Age_Summ_ByTrt: the sealed run: ImportError: refused by the sealed run: specfirst
planted in the scripts' outputs: common-safety-displays/An03_01_Age_Summ_ByTrt, efficacy-adas/An_ADAS_W24_LSM, efficacy-adas/An_ADAS_W24_PwPbo, efficacy-adas/An_EFF_N differ
6 passed in 19.85s
```

### R3 The generator's imports

```text
$ python -c 'import specfirst.recompute.generate, specfirst.recompute.run, specfirst.recompute.static; <list the new modules>'
specfirst modules loaded: ['specfirst', 'specfirst.kit', 'specfirst.machine', 'specfirst.machine.canonical', 'specfirst.paths', 'specfirst.recompute', 'specfirst.recompute.bundle', 'specfirst.recompute.bundle.compare', 'specfirst.recompute.common', 'specfirst.recompute.generate', 'specfirst.recompute.pywrite', 'specfirst.recompute.reading', 'specfirst.recompute.run', 'specfirst.recompute.rwrite', 'specfirst.recompute.static', 'specfirst.sources']
third-party top-level modules loaded: ['_cython_3_1_4', 'cython_runtime', 'yaml']
$ python -I -B -c "import specfirst, sys; print(specfirst.__file__)"
<worktree>/src/specfirst/__init__.py
```

### R4 Facts and the scan of the scripts

A script of the reviewer over `<clone>/build/recompute/cdiscpilot01`:

```text
counts: {'reproduced': 69}
fewest rows: [(1, 'common-safety-displays/An03_01_Age_Comp_ByTrt'), (1, 'common-safety-displays/An03_02_AgeGrp_Comp_ByTrt'), ...]
largest relative differences: [(2.401077967338003e-13, 'An07_09_Soc_Comp_ByTrt_PlacHigh'), (2.0421657304109583e-13, 'An07_10_SocPt_Comp_ByTrt_PlacLow'), ...]
checks: passed True static problems 0 of 69 sealed failures {}
plan: Counter({'python': 42, 'r': 27}) Counter({'descriptive': 36, 'test.fisher.exact': 6, 'model.ancova.pairwise': 6, 'test.chisq': 4, 'model.mmrm.pairwise': 4, 'model.ancova.dose_response': 3, 'model.ancova.lsmeans': 3, 'test.cmh': 3, 'test.anova.oneway': 2, 'model.mmrm.lsmeans': 2})
ARD values with 0 < |v| < 1e-3: 5 [(4.0193647697156345e-05, 'ard:An07_09_Soc_Comp_ByTrt_PlacLow/Mth03_CatVar_Comp_FishEx_1_pval/*/=GENERAL%20DISORDERS%20AND%20ADMINISTRATION%20SITE%20CONDITIONS'), (0.0004807430203325017, ...), (0.0008117583686003774, ...), (0.0008117583686003774, ...), (0.0008701331713502653, ...)]
bundle files: 78 Counter({'.py': 44, '.R': 27, '.jsonl': 3, '.json': 2, '.txt': 1, '.sh': 1})
bundle top level: ['README.txt', 'adam_csv.py', 'ard', 'compare.py', 'manifest.json', 'plan.json', 'run_all.sh', 'scripts']
code lines: min (20, 'An01_05_SAF_Summ_ByTrt') median (30, 'An_ADAS_W08_LSM') max (50, 'An08_02_ChgBl_Summ_ByTrt')
odd constructs in the 69 scripts: 0 []
ADAE records: 1191 with AEBODSYS != AESOC: 0
$ grep -c E26 run/report.txt run/report.json bundle/README.txt
run/report.txt:0
run/report.json:0
bundle/README.txt:0
```

"Odd constructs" are, per script: a string constant that reads as a JSON
number not among the numbers the ARS states for the analysis (or the
check's small constants); in Python the names `__builtins__`, `chr`, `ord`,
`__file__`, the attributes `anchor`, `eval`, `query`, `memmap`, the string
`".."`; in R (R's parser) a string constant followed by `(`, the string
`".."`, a string argument of `apply` or `sapply`.

### R5 Static plants and comparison plants

Each static plant is one replacement in the generated script, checked with
the numbers of `run.analysis_numbers` for that analysis; the unplanted
scripts give no problem.

```text
unplanted python: []
P1 a number of the ARD in a string: passes the static check
P2 the built ADaM by '..' steps (no slash): passes the static check
P3 the file-system root from Path.anchor: passes the static check
P4 exec through __builtins__: passes the static check
P5 a slash from chr and ord: passes the static check
P6 the bytes of any file by numpy.memmap: passes the static check
P7 pandas.eval: passes the static check
P8 a file name split in two: passes the static check
unplanted R: []
R1 source() named by a string through sapply: passes the static check
R2 a number of the ARD in a string: passes the static check
R3 the ARD read as CSV by an absolute path made by file.path: passes the static check
R4 a function called by a string literal: passes the static check
R5 apply with a string FUN: passes the static check
$ Rscript --vanilla -e 'd <- utils::getParseData(parse(text = "\"source\"(x)\n`source`(y)\n", keep.source = TRUE)); print(d[d$terminal, c("token", "text")])'
                  token     text
1             STR_CONST "source"
...
14 SYMBOL_FUNCTION_CALL `source`
```

The comparison plants run the bundle's compare.py on a toy plan of three
analyses (C1 an empty analysis, C3 a plan of one grouping against ARD rows
of two, C4 a p-value of 1e-13 recomputed as 9e-13):

```text
{"analysis": "Empty", "event": "e", "largest": 0.0, "rows": 0, "status": "reproduced"}
{"analysis": "Fewer", "event": "e", "largest": 0.0, "rows": 1, "status": "reproduced"}
{"analysis": "Tiny", "event": "e", "largest": 0.888888888888889, "rows": 1, "status": "reproduced"}
k: 3 analyses: reproduced 3
```

### R6 Sealed-run plants and data plants

A copy of the bundle; each planted script replaces the generated one and is
run by `run.run_one` on copies made by `run.data_folder` (the gate's own
functions), then judged by `run.compare` (the bundle's compare.py) against
the bundle's gold ARD:

```text
S4 the ARD copied, no computation: static check: []
S1 the engine imported past seal.py: static check: []
S2 the built ADaM read by '..' steps: static check: []
S3 the engine's R code sourced: static check: []
S4 the ARD copied, no computation: sealed run: passed; log: ''
   compare: reproduced (24 rows)
S1 the engine imported past seal.py: sealed run: passed; log: 'engine loaded from <clone>/src/specfirst/machine/methods.py'
   compare: reproduced (24 rows)
S2 the built ADaM read by '..' steps: sealed run: passed; log: ''
   compare: reproduced (24 rows)
S3 the engine's R code sourced: sealed run: passed; log: '[1] "<clone>/r/specfirstr/R/models.R"'
   compare: reproduced (12 rows)
C2 a script that writes its output, then exits 3: run_one: 'exit 3'; compare: reproduced
D1 one AGE of the ADSL copy + 1: run_one None; compare differs, 2 of 24 rows differ
D2 every CHG of the ADQSADAS CSV copy + 1 (8628 values): run_one None; compare differs, 9 of 12 rows differ
exit 0
```

S1 sets `sys.dont_write_bytecode` and imports from `<clone>/src`, so
nothing was written into the worktree.

### R7 The bundle generated again

```text
recompute cdiscpilot01: 69 scripts of 69 analyses written to <scratch>/again
files: 78 78 same bytes: True
manifest generator: {"clean":true,"commit":"694709b913808decdefaf71d2136695946ac37eb","specfirst":"0.0.0"}
```

### R8 Lint, ASCII, cache, worktree

```text
$ python -m ruff check --no-cache src tests
All checks passed!
$ python -m specfirst.asciicheck
ASCII check: 851 files checked, 0 with non-ASCII bytes
$ python -m specfirst fetch --verify
...
fetch: every pin verified
$ git -C <worktree> status --short      (before this file was written)
(nothing)
```

### R9 Pass 2: the pass-1 plants against `b43c336`

`<clone>` checked out at `b43c336` (`git log --oneline -1`: "b43c336
issue-29: the findings of the review, pass 1 (F1 to F5)"); the same scripts
as R5, on the same generated scripts (no writer changed):

```text
unplanted python: []
P1 a number of the ARD in a string: CAUGHT line 40: the number '75.20930232558139' in a text, which the ARS does not state for the analysis
P2 the built ADaM by '..' steps (no slash): CAUGHT line 18: a read other than `adam / "<dataset>.parquet"` of a dataset of the plan
P3 the file-system root from Path.anchor: CAUGHT line 18: a read other than `adam / "<dataset>.parquet"` of a dataset of the plan
P4 exec through __builtins__: CAUGHT line 11: the name __builtins__
P5 a slash from chr and ord: CAUGHT line 11: the name chr
P6 the bytes of any file by numpy.memmap: CAUGHT line 12: the attribute memmap
P7 pandas.eval: CAUGHT line 12: the attribute eval
P8 a file name split in two: passes the static check
unplanted R: []
R1 source() named by a string through sapply: CAUGHT a file other than `file.path(adam, "<dataset>.csv")` of a dataset of the plan
R2 a number of the ARD in a string: CAUGHT the number '1.4885404260186454' in a text, which the ARS does not state for the analysis
R3 the ARD read as CSV by an absolute path made by file.path: CAUGHT a file other than `file.path(adam, "<dataset>.csv")` of a dataset of the plan
R4 a function called by a string literal: CAUGHT a file other than `file.path(adam, "<dataset>.csv")` of a dataset of the plan
R5 apply with a string FUN: CAUGHT a file other than `file.path(adam, "<dataset>.csv")` of a dataset of the plan
{"analysis": "Empty", "event": "e", "reason": "the ARD has no row of the analysis", "status": "differs"}
{"analysis": "Fewer", "event": "e", "reason": "ARD rows of more groupings than the plan reads: ['group2_groupingId']", "status": "differs"}
{"analysis": "Tiny", "differ": [{"ard": 1e-13, "row": ["P", "*"], "script": 9e-13}], "event": "e", "rows": 1, "status": "differs"}
k: 3 analyses: differs 3
```

P8 is `name = "efficacy-adas.js" + "onl"` alone: a text bound to a name,
with no reader allowed to take it.

### R10 Pass 2: new routes, and the pass-1 routes run sealed

A script of the reviewer generates the bundle with `b43c336` from the build
of `<clone>`, then plants each route into the age summary (Python) or the
Week 24 LS means (R), checks it with `static.python_problems` or
`static.r_problems` and the analysis's numbers, runs it by `run.run_one`
with the fence `run.recompute` passes, `(root, build)`, and judges it by
the bundle's compare.py. For S1 to S4 the static check is set aside (it
refuses them, R9) to see the sealed run alone.

```text
plan evidence: ['E24', 'E25', 'E26']
unplanted: []
N1 the data folder moved by sys.argv to the built ADaM: static: []
N2 Path rebound to climb by '.' + '.': static: []
N3 a number of the ARD built from digits: static: []
RN1 source by a computed name handed to sapply: static: []
RN2 source by a name held in a variable: static: []
RN3 the ARD read by readLines named by a computed string: static: []
RN4 source by update() of a list whose call is a computed name: static: ['the name file']
N1 the data folder moved by sys.argv to the built ADaM: sealed: passed; compare: reproduced (24 rows)
N2 Path rebound to climb by '.' + '.': sealed: passed; compare: reproduced (24 rows)
N3 a number of the ARD built from digits: sealed: passed; compare: reproduced (24 rows)
S1 the import past seal.py's meta_path hook: sealed: failed: ImportError: refused by the sealed run: specfirst.machine.methods; compare: differs (24 rows)
S2 the built ADaM by '..': sealed: passed; compare: reproduced (24 rows)
S4 the ARD opened by Python: sealed: failed: PermissionError: refused by the sealed run: an open of <clone>/build/kits/cdiscpilot01/gold/ard/common-safety-displays.jsonl; compare: differs (24 rows)
RN1 source by a computed name handed to sapply: sealed: passed; compare: reproduced (12 rows); log: [1] "<clone>/r/specfirstr/R/models.R"
RN2 source by a name held in a variable: sealed: passed; compare: reproduced (12 rows); log: [1] "<clone>/r/specfirstr/R/models.R"
RN3 the ARD read by readLines named by a computed string: sealed: passed; compare: reproduced (12 rows); log: [1] 331
RN4 source by update() of a list whose call is a computed name: sealed: failed: Execution halted; compare: differs (12 rows); log: Error in eval(call, parent.frame()) : attempt to apply non-function
S3 source handed to sapply as a string: sealed: passed; compare: reproduced (12 rows); log: [1] "<clone>/r/specfirstr/R/models.R"
C2 output, then exit 3: run_one 'exit 3'; output kept: False; compare: differs: the script failed: exit 3
unplanted age summary with the fence: run_one None; compare reproduced
report evidence lines: ["E24 CSR 14-2.01 (demographics): not built as a CSR table (real-4); covered in part: its rows of age, age group, sex, race and height are recomputed by the demographics analyses of CDISC's example (Out14-1-1), on the safety population and race by another grouping; its ITT population and its rows of MMSE, duration of disease, education, weight and BMI are not", "E25 ...", "E26 ..."]
exit 0
$ <the ARD files of that bundle: values equal to 0, non-zero values below 1e-9>
ARD values equal to 0: 858 ; nonzero below 1e-9: 0 []
$ python -m ruff check --no-cache src tests
All checks passed!
$ python -m specfirst.asciicheck
ASCII check: 851 files checked, 0 with non-ASCII bytes
```

S1's planted import of `<clone>/src` sets `sys.dont_write_bytecode` first,
and no plant wrote into the worktree. The plants in full: N1 inserts `s =
sys.argv[1][0]` and `sys.argv[1] = s + "tmp" + s + "review29" + s + "build"
+ s + "kits" + s + "cdiscpilot01" + s + "gold" + s + "data" + s + "adam"`
before the template's binding of `adam`; N2 inserts `P = Path` and `Path =
lambda p: P(p) / ('.' + '.') / ('.' + '.') / 'review29' / 'build' / 'kits' /
'cdiscpilot01' / 'gold' / 'data' / 'adam'`; RN1 inserts, after `adam <-
args[1]`, `s <- sprintf("%.1s", args[1])`, `loaded <- sapply(paste0(s,
"tmp", s, "review29", s, "r", s, "specfirstr", s, "R", s, "models.", "R"),
paste0("sou", "rce"))` and `colnames(loaded)`; RN3 the same `s` and `lines
<- sapply(paste0(s, "tmp", ..., s, "ard", s, "efficacy-adas.js", "onl"),
paste0("read", "Lines"))` and `length(lines)`.

### R11 Pass 2: the reviewer's recompute and test runs at `b43c336`

In one acquisition of `flock /run/lock/specfirst-heavy.lock`, under
`taskset -c 0-3`, in `<clone>` at `b43c336` (the build of R1; no engine or
kit file changed between the two commits):

```text
$ python -m specfirst recompute cdiscpilot01          # exit 0
recompute cdiscpilot01: 69 scripts of 69 analyses written to <clone>/build/recompute/cdiscpilot01/bundle
cdiscpilot01: 69 analyses: reproduced 69
E24 CSR 14-2.01 (demographics): not built as a CSR table (real-4); covered in part: ... are not
E25 CSR 14-5.01 (adverse events by organ class and term): not built as a CSR table (real-4); its content is recomputed by the analyses of CDISC's example Out14-3-2-1, on ADAE (AESOC, equal to AEBODSYS on every record)
E26 CSR 14-6.06 (Hy's law shifts, CMH): not built: no ARS analysis in the kit (real-5); its method, test.cmh, is recomputed for CSR 14-3.13
static check: 69 of 69 scripts pass it (imports, calls, reads, texts and numbers; ADR-021, decision 5)
recompute cdiscpilot01: PASS
$ python -m pytest -q -p no:cacheprovider tests/unit/test_recompute.py
16 passed in 3.91s
$ SPECFIRST_STRICT=1 SPECFIRST_RECOMPUTE_REUSE=1 python -m pytest -s -q -p no:cacheprovider tests/recompute
planted: the ANCOVA LS means with equal weights ...: 36 ARD rows change, 0 of them shown by a cell of a built grid; the scripts: 3 analyses differ: ...W08_LSM, ...W16_LSM, ...W24_LSM
planted: quartiles by R type 7 in both engines: 106 ARD rows change, the engines disagree on 0; the scripts: 4 analyses differ
planted: CMH general association in both engines: 3 ARD rows change, the engines disagree on 0; the scripts: 3 analyses differ
planted in An03_01_Age_Summ_ByTrt: ... (12 static plants, each with its problem)
planted in An_ADAS_W24_LSM: ... (8 static plants, each with its problem)
planted in An03_01_Age_Summ_ByTrt: the sealed run, an import of the engine: ImportError: refused by the sealed run: specfirst
planted in An03_01_Age_Summ_ByTrt: the sealed run, an import past the hook of meta_path: ImportError: refused by the sealed run: specfirst.machine.methods
planted in An03_01_Age_Summ_ByTrt: the sealed run, an open of the ARD: PermissionError: refused by the sealed run: an open of <clone>/build/kits/cdiscpilot01/gold/ard/common-safety-displays.jsonl
not held by the sealed run, held by the static check above: a read by pyarrow's own code (the built ADaM by parent folders) and any read or source in R
planted in the scripts' outputs: common-safety-displays/An03_01_Age_Summ_ByTrt, common-safety-displays/An03_06_Height_Summ_ByTrt, efficacy-adas/An_ADAS_W24_LSM, efficacy-adas/An_ADAS_W24_PwPbo, efficacy-adas/An_EFF_N, efficacy-cibic/An_CIBIC_EFF_N differ
6 passed in 19.88s
```

The line "not held by the sealed run, held by the static check above: ...
any read or source in R" is one of the four sentences of F1 (pass 2) that
R10 contradicts.

### R12 F1 again: `0e06dd4`

`<clone>` checked out at `0e06dd4` (`git rev-parse HEAD`:
`0e06dd49364c808834c2682b60dce620b4e4a799`, `git status --short` empty).
A script of the reviewer generates the bundle with `0e06dd4` from the build
of `<clone>`, runs `static.check` on all scripts, and plants and runs each
route as in R10 (`run.run_one` with the fence `(root, build)`, then the
bundle's compare.py). Single processes, outside the lock, under `taskset -c
0-3` while the clean-clone gates of `0e06dd4` held it.

```text
commit 0e06dd4: the 69 scripts: 69 of 69 pass the static check
N1 the data folder moved by sys.argv: static: ['line 18: sys used otherwise than as `sys.argv[1]` or `sys.argv[2]`, read']
N2 Path rebound: static: ['line 17: Path used otherwise than in `adam, out = Path(sys.argv[1]), sys.argv[2]`', 'line 18: the imported name Path bound again']
N2b Path imported under another name: static: []
PV1 sys.argv[1] read, then a write to a computed path outside the data folder: static: ["line 19: a file other than the ADaM datasets of the plan: 'written-by-python.csv'"]
RN1 source by a computed name handed to sapply: static: ['the function of sapply is not written in place: `function(...)`']
RN2 the name in a variable: static: ['the function of sapply is not written in place: `function(...)`']
RN3 readLines by a computed name: static: ['the function of sapply is not written in place: `function(...)`']
RV1 a computed name, then a function written in place as the last argument: static: []
RV2 update() of a list holding a computed name and a path, with df only: static: []
RV3 lm() with na.action a computed name: static: []
RV4 a write to a computed path outside the sealed folder: static: ["a file other than the ADaM datasets of the plan: 'written-by-r.csv'"]
N1 the data folder moved by sys.argv: sealed: passed; compare: reproduced
N2 Path rebound: sealed: failed: FileNotFoundError: <tmp>/review29-data-.../adam/../adsl.parquet; compare: differs
N2b Path imported under another name: sealed: passed; compare: reproduced
PV1 ...: sealed: passed; compare: reproduced
RN1 ...: sealed: passed; compare: reproduced
RN2 ...: sealed: passed; compare: reproduced
RN3 ...: sealed: passed; compare: reproduced
RV1 ...: sealed: failed: Execution halted; compare: differs
RV2 ...: sealed: failed: Execution halted; compare: differs
RV3 ...: sealed: failed: Execution halted; compare: differs
RV4 ...: sealed: passed; compare: reproduced
written-by-python.csv exists: True
written-by-r.csv exists: True
exit 0
N2c Path imported as Q, and a function named Path: static: []
   sealed: passed; compare: reproduced
N2d Path imported as Q, and a class named Path: static: ['line 22: the name Path']
   sealed: passed; compare: reproduced
exit 0
$ Rscript --vanilla <reviewer's check of R functions>
source formals: file local echo print.eval exprs spaced verbose prompt.echo max.deparse.length width.cutoff deparseCtrl chdir catch.aborts encoding continue.echo skip.echo keep.source
readLines formals: con n ok warn encoding skipNul
contrast.emmGrid: fn = paste(method, "emmc", sep = "."); method = get(fn)
mmrm_control: assert(check_function(start, args = "..."), check_numeric(start, ...
```

The sealed runs of the refused routes show what the sealed run alone holds:
N1 and RN1 to RN3 still run and are `reproduced` (pyarrow and R are not
fenced), N2 fails because its lambda climbs one folder only, and N2b only
adds an unused name. N2b and N2d's sealed results are those of scripts the
static check passes (N2b) or refuses (N2d). `emmeans::contrast` looks a
method up only with the suffix `.emmc`, and `mmrm_control` takes `start`
only as a function or numbers, so neither turns a computed name into
`source`.

### R13 F1 at `ae07c86`

`<clone>` checked out at `ae07c86` (`git rev-parse HEAD`:
`ae07c86c0a2ac345c3c502556d415afbc2f729fe`, `git status --short` empty);
the same method as R12, single processes outside the lock:

```text
commit ae07c86: the 69 scripts: 69 of 69 pass the static check
N2c Path imported as Q, a function named Path: static: ["line 12: the import `from pathlib import Path as Q`, which is not one of the templates'", 'line 15: the name Path of the template bound again']
N2b Path imported again as Q: static: ["line 13: the import `from pathlib import Path as Q`, which is not one of the templates'"]
N1 sys.argv rewritten: static: ['line 18: sys used otherwise than as `sys.argv[1]` or `sys.argv[2]`, read']
M1 a reserved name bound by a match capture (case num): static: []
M2 a reserved name bound by a match capture (case adam), after the binding: static: []
W1 a second write, to out: static: []
W2 a write elsewhere: static: ['line 50: a write other than `.to_csv(out, index=False)`']
D1 another def num: static: ['line 21: the name num of the template bound again']
RW1 a write elsewhere: static: ['a write other than that of the output, `write.csv(rows, args[2], ...)`']
N2c ...: sealed: passed; compare: reproduced        (sealed run alone; the static check refuses it)
M2 ...: sealed: passed; compare: reproduced
exit 0
M3 sys bound by a match capture to a function whose attribute argv is set: static: []
   sealed: passed; compare: reproduced
exit 0
M3-control (a folder that does not exist) ...: static: []
   sealed: failed: FileNotFoundError: <tmp>/review29-data-.../adam/../../review29/nowhere/kits/cdiscpilot01/gold/data/adam/adsl.parquet; compare: differs
exit 0
```

M2 binds `adam` to 1 before the template's line binds it again, so it reads
the data folder as usual.

### R14 F1 at `22c2932`

`<clone>` checked out at `22c2932` (`git rev-parse HEAD`:
`22c2932c017fc828c567263f91ed94a061371531`, `git status --short` empty);
the same method, the static check only, single processes outside the lock:

```text
commit 22c2932: the 69 scripts: 69 of 69 pass the static check
M3 match capture of sys, f.argv set: static: ['line 27: a Match statement or clause', 'line 26: a store into the attribute argv']
M3b the capture alone: static: ['line 26: a Match statement or clause']
M3c the attribute store alone: static: ['line 26: a store into the attribute argv']
B1 with ... as sys: static: ['line 17: the name sys of the template bound again', 'line 17: the name f']
B2 walrus sys: static: ['line 17: the name sys of the template bound again']
B3 del sys: static: ['line 17: the name sys of the template bound again']
B4 comprehension target sys: static: ['line 17: the name sys of the template bound again']
B5 lambda argument sys: static: ['line 17: sys used otherwise than as `sys.argv[1]` or `sys.argv[2]`, read', 'line 17: the name sys of the template as an argument']
B6 for sys in: static: ['line 17: the name sys of the template bound again']
B7 a type parameter named sys: static: ['line 17: a TypeVar statement or clause']
exit 0
```

### R15 Part 2: the report and the five logs of `c5afc28`

A script of the reviewer, run in the worktree at `c5afc28` (Windows
Python, reading only), takes each log, and each `text` block of
docs/reports/issue-29.md:

```text
issue-29: 29799 bytes, non-ASCII 0; head ['gate issue-29 at commit 22c2932c017fc828c567263f91ed94a061371531 (clean)']; summary 12 PASS, 0 FAIL; unit [('1317', '36')]
real-5a: 66335 bytes, non-ASCII 0; head ['gate real-5a at commit 22c2932c017fc828c567263f91ed94a061371531 (clean)']; summary 18 PASS, 0 FAIL; unit [('1317', '36')]
real-5b: 62410 bytes, non-ASCII 0; head ['gate real-5b at commit 22c2932c017fc828c567263f91ed94a061371531 (clean)']; summary 19 PASS, 0 FAIL; unit [('1317', '36')]
real-2: 56074 bytes, non-ASCII 0; head ['gate real-2 at commit 22c2932c017fc828c567263f91ed94a061371531 (clean)']; summary 15 PASS, 0 FAIL; unit [('1317', '36')]
real-3a: 60947 bytes, non-ASCII 0; head ['gate real-3a at commit 22c2932c017fc828c567263f91ed94a061371531 (clean)']; summary 16 PASS, 0 FAIL; unit [('1317', '36')]
block 1: 33 lines, 0 not in a log
block 2: 1 lines, 0 not in a log
block 3: 3 lines, 0 not in a log
block 4: 4 lines, 0 not in a log
block 5: 15 lines, 1 not in a log
   missing: $ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh issue-29 <repository> 22c2932
block 6: 5 lines, 0 not in a log
block 7: 3 lines, 0 not in a log
block 8: 6 lines, 6 not in a log
   missing: $ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh <gate> <repository> 22c2932
   missing: issue-29 exit 0 after 743 s
   missing: real-5a exit 0 after 1231 s
   missing: real-5b exit 0 after 924 s
   missing: real-2 exit 0 after 899 s
   missing: real-3a exit 0 after 945 s
reproduced lines: 69 largest: (2.4e-13, 'common-safety-displays/An07_09_Soc_Comp_ByTrt_PlacHigh')
issue-29: 2 lines with a path or credential pattern
    repository: <repository>
    $ git clone --quiet --no-local <repository> /tmp/specfirst-clean-g1agKZ/specfirst
(the same two lines, with their own clone folders, in each of the other four logs)
$ grep -n "passed in" docs/reports/issue-29.clean-clone.gate.log
318:6 passed in 18.82s
```

The search pattern: drive paths, `/home/`, `/root/`, `/users/`, the
local user's number, "token", "password", "passwd", "secret", `ghp_`,
`github_pat`, "api key", "bearer", "authorization", and e-mail
addresses. The two quoted scripts, read out of the report and held against
the scripts of the bundle `22c2932` generated in `<clone>` (R14):

```text
scripts/common-safety-displays/An03_01_Age_Summ_ByTrt.py identical: True 50 50
scripts/efficacy-adas/An_ADAS_W24_LSM.R identical: True 66 66
```

`git diff --name-only 9dc6b20 c5afc28` names CLAUDE.md, ADR-021, the
report and its five logs, docs/state/real.md, cli.py, gates.py, the files
of `src/specfirst/recompute/` and the two test files; nothing under
`standard/`, `env/` or `kits/`, not PLAN.md. `git diff --name-only 22c2932
c5afc28` names only the report, the five logs and docs/state/real.md. The
new "Passed" entry of docs/state/real.md says what the logs show.

### R16 Final: the merge `711c032` and the six logs of `0ae9b24`

In the worktree at `0ae9b24` (Windows git and Python, reading only):

```text
$ git diff 9dc6b20 6cdeded -- src/specfirst/cli.py src/specfirst/gates.py   (main's side)
$ git diff c5afc28 711c032 -- src/specfirst/cli.py src/specfirst/gates.py   (what the merge brought)
  (their +/- lines compared)
merge's change of cli.py and gates.py = main's catalog-2b change
$ git diff 9dc6b20 c5afc28 -- ...   against   git diff 6cdeded 711c032 -- ...
issue-29's change of cli.py and gates.py kept whole by the merge
$ git diff --name-only 9dc6b20 6cdeded -- standard/methods kits src/specfirst/recompute src/specfirst/machine r env
(nothing)
$ git diff --name-only 711c032 0ae9b24 -- src tests r env standard kits PLAN.md | wc -l
0
clean-clone: 363 lines, non-ASCII 0; ['gate issue-29 at commit 711c032d3c3a186640414c23e242a3ea2fdee98b (clean)']; 12 PASS, 0 FAIL; unit [('1353', '36')]; ['clean clone gate issue-29', 'GATE issue-29: PASS', 'clean clone gate issue-29: PASS (clone: /tmp/specfirst-clean-qIOhYb/specfirst)']
real-5a: 750 lines, non-ASCII 0; ['gate real-5a at commit 711c032d3c3a186640414c23e242a3ea2fdee98b (clean)']; 18 PASS, 0 FAIL; unit [('1353', '36')]; [..., 'GATE real-5a: PASS', 'clean clone gate real-5a: PASS (...)']
real-5b: 702 lines, non-ASCII 0; [... 711c032 ... (clean)]; 19 PASS, 0 FAIL; unit [('1353', '36')]; [..., 'GATE real-5b: PASS', ...]
real-2: 618 lines, non-ASCII 0; [... 711c032 ... (clean)]; 15 PASS, 0 FAIL; unit [('1353', '36')]; [..., 'GATE real-2: PASS', ...]
real-3a: 680 lines, non-ASCII 0; [... 711c032 ... (clean)]; 16 PASS, 0 FAIL; unit [('1353', '36')]; [..., 'GATE real-3a: PASS', ...]
catalog-2b: 221 lines, non-ASCII 0; [... 711c032 ... (clean)]; 17 PASS, 0 FAIL; unit [('1353', '36')]; [..., 'GATE catalog-2b: PASS', ...]
section 'On the merge with main' found: True 36 lines
merge block 1: 7 lines, 7 not in a merged log      (the command and the loop's six "exit 0 after <n> s")
issue-29 merged log: '69 analyses: reproduced 69' lines: 1 ; 'passed in' lines: ['6 passed in 18.91s']
<each of the six logs>: 2 lines with the pattern: repository: <repository> | $ git clone --quiet --no-local <repository> /tmp/specfirst-clean-.../specfirst
$ <the lines planted:, static check, sealed runs, generator:, export:, "cdiscpilot01: 69" of the gate issue-29, on 22c2932 and on 711c032, clone folders written <clone>>
11
11
the same result lines on 22c2932 and on 711c032
$ grep -c "^reproduced" docs/reports/issue-29.merged.clean-clone.gate.log
69
$ grep -c "^planted in" docs/reports/issue-29.merged.clean-clone.gate.log docs/reports/issue-29.clean-clone.gate.log
docs/reports/issue-29.merged.clean-clone.gate.log:32
docs/reports/issue-29.clean-clone.gate.log:32
```

Verdict: SIGNED
