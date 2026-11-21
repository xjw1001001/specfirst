# catalog-2a: the versions of the standard (ADR-020, part 1 of 3)

Work package catalog@2, track std, part catalog-2a: the structure of
`catalog@2` and `open-default@2` (ADR-020, decisions 1 to 6 and 9). The
owner approved ADR-020 on 2026-11-21 (A to questions 1, 2, 3 and 5, B to
question 4). This part changes no meaning: version 2 holds the content of
version 1 with the defaults moved into the house. Parts catalog-2b (the
content of decision 7) and catalog-2c (the slice moved to version 2) follow.

## What changed

| Where | What |
| --- | --- |
| `standard/catalog/` | renamed `standard/catalog@1/` with `git mv`; no byte changed (its tree is the tag's, below) |
| `standard/catalog@2/` | new, a draft: the files of `catalog@1` with `house_default` taken out of the 43 entries; `catalog.yaml` names version 2 and `entry_schema: catalog-entry.v1`; `migration.yaml` with no change; README.md for version 2 |
| `standard/houses/open-default@2/` | new, a draft: the files of `open-default@1`; `house.yaml` names `catalog_version: 2` and `defaults: defaults.yaml` (no `default_values`); `defaults.yaml` holds the 62 defaults of version 1 (58 alternatives, 4 stated null); STANDARD.md rendered for version 2 |
| `standard/versions.yaml` | new: the four versions, their status, date, what froze them, and the trees of the frozen ones |
| `standard/BACKLOG.yaml` | new: 60 records for #1 to #24, #28 and #33, from the two tables of ADR-020, decision 7, after the owner's answers |
| `standard/schemas/` | added `catalog-entry.v1.schema.json` and `house-defaults.schema.json`, each with its examples; no schema file changed |
| `src/specfirst/compile/versions.py` | new: labels and folders, git's tree hash in Python, the check "frozen", the refusal of a draft label |
| `src/specfirst/compile/migration.py` | new: the meaning of an alternative as a hash, the check of a migration file, a record mapped to the next version |
| `src/specfirst/compile/backlog.py` | new: the check of the backlog and the lines of `specfirst status` |
| `src/specfirst/compile/catalog.py`, `house.py` | loaders by label; a catalog names its entry schema; a house reads `defaults.yaml`, resolves a default by design from the design features, and fits only the catalog version it needs |
| `src/specfirst/compile/checks.py`, `gate.py`, `src/specfirst/gates.py` | the checks of std-1 take a pair of labels; checks "defaults" and "templates" (every directive and `$fn` of every template read whole); the gate `catalog-2a` |
| `src/specfirst/cli.py` | `--catalog` and `--house` for `catalog`, `house`, `compile`, `render`, `parse`; `house --write` refuses a frozen house |
| `src/specfirst/harness/task.py`, `pilot.py`, `harness/gate.py`, `gen/kits.py`, `gen/decisions.py` | a task copies the catalog its kit names to `standard/catalog/` of the task; a kit or a task that names a draft is refused; the pilot task names the house it loads; the generator passes the design features to the defaults |
| PLAN.md | one comment line in section 5.1 (approved with question 5) |
| CLAUDE.md, docs/state/std.md | the versioned folders, the labels, the gate |

## Evidence

### catalog@1 and open-default@1 do not change

```text
$ git write-tree --prefix=standard/catalog@1/          # after git mv, in the index
a25d42c08d37352131b9320a62c7fa2ce266cb9b
$ git rev-parse catalog@1:standard/catalog catalog@1:standard/houses/open-default@1
a25d42c08d37352131b9320a62c7fa2ce266cb9b
7ac0f4fc4d76333817b6e3edf21e156afec38ef4
```

The gate check "frozen" computes the same two trees in Python from the files
on disk (`versions.tree_hash`), and `tests/unit/test_versions.py` holds the
function against `git write-tree` on a small folder (a file name that sorts
before a folder of the same stem, an empty file, an empty folder) and pins
both trees (`versions.PINNED`).

### The checks of the versions, on the commit of the gate

From the log of the gate `catalog-2a` on a clean clone of `24cc6ac`
(docs/reports/catalog-2a.catalog-2a.24cc6ac.gate.log):

```text
== [5/17] frozen: specfirst.compile.gate.frozen_check
catalog@1: frozen 2026-11-17, tree a25d42c08d37352131b9320a62c7fa2ce266cb9b (frozen as a25d42c08d37352131b9320a62c7fa2ce266cb9b)
catalog@2: draft 2026-11-21, tree aa60e2719af5ecf037bc68740cd5b43080eceb6c
open-default@1: frozen 2026-11-17, tree 7ac0f4fc4d76333817b6e3edf21e156afec38ef4 (frozen as 7ac0f4fc4d76333817b6e3edf21e156afec38ef4)
open-default@2: draft 2026-11-21, tree d25fef130cdbb377a73ecec3150c55a1ed235e65
default pair: catalog@1, open-default@1; 0 labels named by the kits of the repository
frozen versions: 0 problems
== [13/17] migration: specfirst.compile.gate.migration_check: catalog@1 to catalog@2
catalog@1 to catalog@2: 96 and 96 alternatives; 0 added, 0 removed, 0 changed in meaning; units 0 added, 0 removed; 0 lines in migration.yaml
migration: 0 problems
```

Version 2 means what version 1 means: no alternative changes in meaning,
and the defaults of `open-default@2` are those of version 1 (58 defaults, 4
stated as none; the house check renders and parses both documents).

### Planted defects (rule R5)

`tests/defects/test_versions_checkers.py`: each check fails first on its
plants. frozen: one byte changed in a file of `catalog@1`; a file added to
`open-default@1`; a frozen folder changed with its line of versions.yaml; a
folder whose files are another version; a house that versions.yaml pairs
with another catalog; a kit that names a draft version; a folder that
versions.yaml does not list. migration: a definition changed without a line;
a line for an alternative that did not change; a line with no accepted
record. backlog: an unknown status; an issue without a record; a record
accepted for a frozen version. defaults: an entry without an item; a
default that is not an alternative; a unit the entry does not have; an
entry per table family without an item; a case that names an unknown
feature; a last case with `when`. templates: an unknown helper in a branch
no example reaches. The schemas: five planted invalid examples each
(`tests/unit/test_schemas.py`). The refusals: a task and a generated kit
that name a draft, `house --write` on a frozen house, a pair that does not
fit (`tests/unit/test_versions.py`).

### Generated kits are the same bytes

Kits 1 to 4 of the seed `gen-2a`, written on clones of `main` (`325a8f2`)
and of `869b8c0` (the code of this part; `24cc6ac` and `78c9084` change no
code the generator runs), in the Linux file system, inside the heavy lock:

```text
$ python -m specfirst gen kits --out main --count 4 --seed gen-2a     # clone of 325a8f2
kit 1 of the set: sfpbt5zj, train, 127 files; 14 of 22 decisions separated on the twin
kit 2 of the set: sfmyncmq, train, 127 files; 15 of 22 decisions separated on the twin
kit 3 of the set: sfg5vbvq, train, 126 files; 15 of 21 decisions separated on the twin
kit 4 of the set: sfrrl2uh, train, 127 files; 14 of 22 decisions separated on the twin
$ python -m specfirst gen kits --out c2a --count 4 --seed gen-2a      # clone of 869b8c0
(the same four lines)
$ find c2a -type f | wc -l
511
$ diff -r main c2a && echo identical
identical
$ sha256sum c2a/kit-00?/kit.yaml
a5a1da67d4dac93017a3364ba86f00177e59210aa16059b683996b293489e177  c2a/kit-001/kit.yaml
79e43bbd9a826cf9ddad47d197e543122ebdcfeba4fcb128432e9d8997640976  c2a/kit-002/kit.yaml
46dfe55ee714fe83ee9b9d27748fcacd6f19611ce0d047685045d432bae86c52  c2a/kit-003/kit.yaml
75addb7d7b70d358e3f740be3eab1338c22c83a6149121987aa0bd7fe090bfbc  c2a/kit-004/kit.yaml
```

The kept dry run of arm R is bound by bytes to the 44 files of
`standard/catalog/` of its task: the task builder copies them from
`standard/catalog@1/`, the same bytes (the review compared them).

### Gates on clean clones

Each gate on a fresh clone with a fresh install and fetch, one at a time
under the heavy lock, on at most four processors:

```text
$ flock /run/lock/specfirst-heavy.lock taskset -c 0-3 bash scripts/clean_clone_gate.sh <wp> /mnt/d/trial_work/specfirst/.git <commit>
```

| Gate | Commit | Unit tests | Result | Log |
| --- | --- | --- | --- | --- |
| catalog-2a | 24cc6ac | 1292 passed, 30 deselected | GATE catalog-2a: PASS (17 checks) | docs/reports/catalog-2a.catalog-2a.24cc6ac.gate.log |
| std-1 | 24cc6ac | 1292 passed, 30 deselected | GATE std-1: PASS | docs/reports/catalog-2a.std-1.24cc6ac.gate.log |
| gen-2a | 24cc6ac | 1292 passed, 30 deselected | GATE gen-2a: PASS | docs/reports/catalog-2a.gen-2a.gate.log |
| gen-3a | 24cc6ac | 1292 passed, 30 deselected | GATE gen-3a: PASS | docs/reports/catalog-2a.gen-3a.gate.log |
| read-1a | 24cc6ac | 1292 passed, 30 deselected | GATE read-1a: PASS | docs/reports/catalog-2a.read-1a.gate.log |
| read-2a | 24cc6ac | 1292 passed, 30 deselected | GATE read-2a: PASS (19 checks; "arm R, kept dry run" among them: the kept run R-task-04119188ff71 still checks) | docs/reports/catalog-2a.read-2a.gate.log |
| catalog-2a | 78c9084 | 1301 passed, 30 deselected | GATE catalog-2a: PASS (17 checks) | docs/reports/catalog-2a.catalog-2a.gate.log |
| std-1 | 78c9084 | 1301 passed, 30 deselected | GATE std-1: PASS | docs/reports/catalog-2a.std-1.gate.log |

`78c9084` carries the findings of the review's pass 1: the version checks,
the commands' error messages, the tests (nine more) and documents. It
changes no code that the generator or the reader harness runs, so the gates
gen-2a, gen-3a, read-1a and read-2a on `24cc6ac` stand for it; catalog-2a
and std-1 ran again. Each log names its commit in its head, and none holds
a local user path or a byte that is not ASCII.

Left out, with the reason (ADR-020, consequences): gen-1a, real-2, real-3a
and real-5b. Their own checks read no catalog and no house (gen-1a's
generator code path is the one gen-2a runs, and the real kit names no
catalog); their unit-test check is the suite that every gate above ran.

## Review

docs/reports/catalog-2a.review.md, a fresh-context reviewer (rule R7):
pass 1 on `24cc6ac` signed with findings F1 to F11, none blocking; pass 2 on
`78c9084` and the eight gate logs signed. F1, F2, F4 to F7 and F10 are fixed
in `78c9084`; F8 and F11 in part (a mapping as a `$fn` name still raises a
TypeError, which cannot let a gate pass wrongly; a stale comment of
`open-default@2` goes with catalog-2b). F3 (the reader's skills read the
defaults from the catalog) moves to catalog-2c, which moves the default
pair; F9 (defaults by design in STANDARD.md and in the scorers) to
catalog-2b and catalog-2c. Two notes of pass 2 go with the later parts:
G1, the pinned versions must be listed, frozen and on disk with their pinned
tree by the check itself, not only because they are the default pair
(catalog-2c at the latest); G2, the time-aware post-baseline of #6 is done
in the ADVS parent of `open-default@2`, so its record is a house record.
