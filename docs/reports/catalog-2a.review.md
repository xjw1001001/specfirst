# catalog-2a: review

Reviewer: a fresh-context reviewer (rule R7), 2026-11-21. Work package
catalog@2, part catalog-2a (ADR-020, decisions 1 to 6 and 9), branch
`track/std` at `24cc6ac`, against `main` at `325a8f2` (merged into the
branch at `218dbd7`; `c5548c2` is the ADR proposal). `869b8c0` holds the
work; `24cc6ac` adds only schema example files:

```text
$ git diff --stat 869b8c0 24cc6ac
 .../examples/catalog-entry.v1.examples.json        | 34 ++++++++++++++++++++++
 .../schemas/examples/house-defaults.examples.json  | 16 ++++++++++
 2 files changed, 50 insertions(+)
```

Read: CLAUDE.md; ADR-020 at `24cc6ac` (decisions 1 to 9, the owner's
answer, the amendment of decision 8, "Carried out / catalog-2a"); PLAN.md
sections 2 and 5.1; the diff `325a8f2..24cc6ac` (406 files); the draft
docs/reports/catalog-2a.md of the working tree (not judged: it is not
committed). The uncommitted catalog-2b work of the working tree is not
reviewed.

## Pass 1

### How the checks were run

A clone in the Linux file system, `git clone -q --no-local
/mnt/d/trial_work/specfirst/.git /tmp/rv-cat2a/specfirst`, checked out at
`24cc6ac`, and one at `325a8f2` for the overview comparison. The
environment of the worktree (`. scripts/env.sh`), `SPECFIRST_ROOT=<clone>`,
`PYTHONPATH=<clone>/src`. Only light commands (seconds, nothing built): my
own Python scripts, kept outside the repository, that call the functions of
the clone on copies of `standard/` under /tmp; `specfirst catalog`,
`specfirst house`. No gate, no test suite, no kit build was run: the unit
tests and the gates are those of the clean-clone logs. What each script
does is said with its result.

### 1. Version 1 is byte for byte the frozen one

```text
$ git rev-parse HEAD:standard/catalog@1 catalog@1:standard/catalog \
    HEAD:standard/houses/open-default@1 catalog@1:standard/houses/open-default@1
a25d42c08d37352131b9320a62c7fa2ce266cb9b
a25d42c08d37352131b9320a62c7fa2ce266cb9b
7ac0f4fc4d76333817b6e3edf21e156afec38ef4
7ac0f4fc4d76333817b6e3edf21e156afec38ef4
$ git diff --name-status 325a8f2 24cc6ac -- standard/schemas standard/houses/open-default@1
A	standard/schemas/catalog-entry.v1.schema.json
A	standard/schemas/examples/catalog-entry.v1.examples.json
A	standard/schemas/examples/house-defaults.examples.json
A	standard/schemas/house-defaults.schema.json
$ git ls-tree -r HEAD standard/catalog@1 standard/houses/open-default@1 | awk '{print $1}' | sort | uniq -c
    191 100644
```

The rename shows as 0-line renames in `git diff --stat 325a8f2 24cc6ac`,
`standard/catalog` no longer exists, no existing schema changed. Right.

### 2. The tree hash and the check "frozen"

The Python hash equals git's on all four folders of the clone:

```text
python: versions.tree_hash(versions.folder(root, label))
catalog@1 a25d42c08d37352131b9320a62c7fa2ce266cb9b
open-default@1 7ac0f4fc4d76333817b6e3edf21e156afec38ef4
catalog@2 aa60e2719af5ecf037bc68740cd5b43080eceb6c      (= git rev-parse HEAD:standard/catalog@2)
open-default@2 d25fef130cdbb377a73ecec3150c55a1ed235e65 (= git rev-parse HEAD:standard/houses/open-default@2)
```

The sort order (a name sorts as `name/` for a folder) is git's, and the unit
test holds it against `git write-tree` on a folder where `a-b` sorts before
the folder `a`. The plants of tests/defects/test_versions_checkers.py,
called directly on fresh copies (script: import the test module, run each
`DEFECTS` plant, then `all_problems`):

```text
clean copy: {'frozen': 0, 'migration': 0, 'backlog': 0, 'defaults': 0, 'templates': 0}
[frozen] one byte changed in a file of catalog@1: 1 problems; named: True
[frozen] a file added to open-default@1: 1 problems; named: True
[frozen] a kit that names a draft version: 2 problems; named: True
[frozen] a folder that versions.yaml does not list: 1 problems; named: True
[migration] a definition changed without a line: 1 problems; named: True
[migration] a line for an alternative that did not change: 2 problems; named: True
[migration] a line with no accepted record: 2 problems; named: True
[backlog] a record with an unknown status: 2 problems; named: True
[backlog] an issue without a record: 1 problems; named: True
[backlog] a record accepted for a frozen version: 1 problems; named: True
[defaults] an entry without an item: 1 problems; named: True
[defaults] a default that is not an alternative: 1 problems; named: True
[defaults] a case that names an unknown feature: 1 problems; named: True
[defaults] a last case with `when`: 1 problems; named: True
[templates] an unknown helper in a branch no example reaches: 1 problems; named: True
```

Ways it could pass or fail wrongly, each on a copy of `standard/`
(script: plant, then `versions.frozen_problems`; long hashes and messages
cut with "..." here and in section 5):

```text
a) a byte of catalog@1 changed and versions.yaml given the new tree: []
b) an empty folder added to catalog@1 (git keeps none): []
c) an ignored file (__pycache__/x.pyc) in catalog@1: ['catalog@1: the folder standard/catalog@1 has the tree c6ee197e..., frozen as a25d42c0...']
d) CRLF line ends in open-default@1/house.yaml: ['open-default@1: ... has the tree 8186668a..., frozen as 7ac0f4fc...']
e) catalog@1 set to draft in versions.yaml: ["the default pair: names 'catalog@1', a draft version; ..."]
f) versions.yaml says open-default@2 needs catalog@1 (house.yaml says 2): []
$ git update-index --chmod=+x standard/catalog@1/README.md; git rev-parse $(git write-tree):standard/catalog@1
198bd455ca6c79e191ba4e0218f64b353dcc355f
python tree_hash of the folder on disk: a25d42c08d37352131b9320a62c7fa2ce266cb9b; frozen_problems: []
(index restored in the throwaway clone afterwards)
```

b, c and d are right or fail safe (an ignored or CRLF file is a false
alarm, not a false pass). a and the mode change are false passes: F1. f:
F2.

### 3. Version 2 is version 1 with the defaults moved

Output condensed to one line per kind of file:

```text
$ git diff --stat=120 24cc6ac:standard/catalog@1 24cc6ac:standard/catalog@2
 README.md | 36 ++++----, catalog.yaml | 13 +++--, migration.yaml | 13 +++,
 42 entries/*.yaml | 1 - each, entries/tfl.population.yaml | 5 -----
 46 files changed, 41 insertions(+), 68 deletions(-)
$ git diff -U0 ... -- entries | grep '^[-+][^-+]' | grep -v '^-house_default:'
-  tfl-demographics: randomized
-  tfl-ae-summary: safety
-  tfl-ae-soc-pt: safety
-  tfl-vitals-by-visit: safety            (the four lines of the house_default mapping of tfl.population)
$ git diff --stat=120 24cc6ac:standard/houses/open-default@1 24cc6ac:standard/houses/open-default@2
 README.md | 10 ++++++----, STANDARD.md | 8 ++++----, defaults.yaml | 91 +++, house.yaml | 15 +++++++--------
```

STANDARD.md differs in its four header lines only, so every rendered
default statement is the same. catalog.yaml adds `version: 2` and
`entry_schema: catalog-entry.v1` and changes the header comment; nothing
else. An independent read (script: each `house_default` of the 43 entry
files of catalog@1, per (entry, unit) of `Catalog.keys()`, against the
items of defaults.yaml read as YAML):

```text
62 (entry, unit) pairs of catalog@1 compared, 0 differ; units in defaults.yaml that the entry does not have: []
open-default@1 default_values: {}
```

The meaning hash, from the gate log build/gates/catalog-2a/clean-clone.log
(clean clone of `24cc6ac`, PASS):

```text
catalog@1 to catalog@2: 96 and 96 alternatives; 0 added, 0 removed, 0 changed in meaning; units 0 added, 0 removed; 0 lines in migration.yaml
open-default@2 for catalog@2: 62 questions (entry and unit), 58 defaults, 0 by design, 4 stated as none
```

And the hash does see a change of one fragment (script: a key added to the
fragment `no_end` of catalog@2/templates/ae.teae.end.yaml):

```text
before: Differences(added=set(), removed=set(), changed=set(), units_added=set(), units_removed=set())
after changing the fragment of no_end : ['ae.teae.end/no_end']
```

Every template has only the top-level keys `entry` and `alternatives`, so
nothing of a template lies outside the hashed fragments. Right.

### 4. The loaders and the old path

The default pair is `catalog@1`, `open-default@1`
(versions.py:37-39). The kept task's 44 catalog files against the files a
task now copies (script: every `standard/catalog/...` key of
src/specfirst/harness/kept/R-task-04119188ff71/task.json against the SHA-256
of the same name under `standard/catalog@1/`):

```text
44 files of standard/catalog/ in the kept task, 0 differ from standard/catalog@1/ of 24cc6ac
```

The task builder copies `catalog.directory/<rest>` to `standard/catalog/<rest>`
(harness/task.py:195-202): the path in the task is unchanged. The old path
in code, tests and other maintained files (hits condensed to file and
lines, my notes in parentheses):

```text
$ git grep -n -E 'standard/catalog([^@]|$)|standard\\catalog' 24cc6ac -- ':!docs/reports' ':!docs/decisions' ':!src/specfirst/harness/kept' ':!docs/lessons.md'
src/specfirst/compile/versions.py:177   (the check that the old folder is gone)
src/specfirst/harness/task.py:10,56,58,59,195,250   (the path inside a task folder: right)
standard/houses/open-default@1/ars/demographics.yaml:3   (frozen; a comment)
standard/houses/open-default@2/ars/demographics.yaml:3   (a comment, F11)
standard/schemas/catalog-entry.schema.json:5   (unchanged schema; a description)
third_party/SOURCES.md:25   (F5)
```

No pathlib form (`/ "catalog"`) is left outside versions.py:176. Nothing
reads a wrong folder today. One call site of the defaults was not moved
(F3), and the gen, read and score loaders take no label (F4).

### 5. Refusals

```text
script: houses.load_pair(root, catalog, house)
('catalog@2', None) -> HouseError house: open-default@1 needs catalog@1, not catalog@2; ...
('catalog@1', 'open-default@2') -> HouseError house: open-default@2 needs catalog@2, not catalog@1; ...
('catalog@2', 'open-default@1') -> HouseError house: open-default@1 needs catalog@1, not catalog@2; ...
(None, 'open-default@2') -> catalog@2 open-default@2
(None, None) -> catalog@1 open-default@1
script: harness.task.kit_catalog(root, manifest)
{catalog: {version: '2'}, house: open-default@1} -> TaskError the kit: names 'catalog@2', a draft version; ...
{catalog: {version: '1'}, house: open-default@2} -> TaskError the kit: names 'open-default@2', a draft version; ...
{catalog: {version: '1'}, house: open-default@1} -> catalog@1
$ specfirst house --write --house open-default@1
open-default@1 is frozen: its STANDARD.md is not written again (ADR-020)
exit 1
$ specfirst house --house open-default@2
house standard open-default@2: 58 defaults, 4 decisions without a default, 3 parent specs, 4 table families
house standard: 0 problems
exit 0
$ specfirst catalog --catalog catalog@2
  File ".../src/specfirst/compile/house.py", line 138, in require_fit
specfirst.compile.house.HouseError: house: open-default@1 needs catalog@1, not catalog@2; ...
exit 1
```

Refused as decision 3 and "Carried out" say. The last one is a traceback
(F7). No test covers the task builder's or the generator's refusal or
`house --write` on a frozen house (F6).

### 6. The gate catalog-2a

src/specfirst/gates.py `_catalog2`: environment, pins, lint, unit tests,
frozen, the seven checks of std-1 on (`catalog@2`, `open-default@2`),
migration, backlog, defaults, templates, ASCII. That is decision 9. Each
new check fails on its plants (section 2 above). The directives of
`checks.DIRECTIVES` are exactly those of the evaluator
(compile/template.py:170-216: `$get`, `$if`, `$for`, `$dict`, `$pick`,
`$concat`, `$fn`). The clean-clone log of `24cc6ac` reports `GATE
catalog-2a: PASS`, 17 checks, `1292 passed, 30 deselected`; the std-1 log
of the same commit reports `GATE std-1: PASS` with `catalog specfirst-m1 1`
and `house standard open-default@1: 58 defaults, 4 decisions without a
default`. Two limits: the check "defaults" proves resolution structurally,
not on sampled designs (F9), and the check "backlog" counts issues, not
items (F10).

### 7. The backlog

I mapped every cell of the two tables of decision 7 to standard/BACKLOG.yaml
by hand: each has a record, with these exceptions (F10): the "Waits" row
"entries for the pilot's efficacy decisions" is recorded as
`i28.real-kit-pins` with another layer, target, kind and owner; #6's C item
is recorded without its second half. Statuses follow the owner's answers:
the eight defaults of question 2 are `accepted` for `open-default@2`
(i01.zero-shown, i02.safety-by-design, i03.window-default,
i06.one-baseline-rule, i07.age-default, i08.total-demographics,
i11.last-record, i13.standard-rows); the four items of question 3
(i03.end-of-study-removed, i09.sort-replaced, i21.race-map,
i10.randomized-from-ds) are `accepted` for `catalog@2`; the waits of the
second table are `waits` with `for` and `reason`. The 9 `done` records
(i18.meaning-hash, i20.entry-format, i20.fn-list, i20.house-values,
i21.kept-answers, i28.defaults-move, i28.version-rules, i28.backlog-file,
i28.freeze-status) are all things 2a did. Nothing else is claimed done.

### 8. Credentials, paths, names, ASCII

Script on the clone over the 406 files of `git diff --name-only 325a8f2
24cc6ac`:

```text
grep -n -I -E 'C:\\Users|/mnt/c/Users|/home/[a-z]|ghp_|github_pat_|sk-ant|AKIA|BEGIN [A-Z ]*PRIVATE|<e-mail pattern>'   (no line)
grep -l -P '[^\x00-\x7F]'   (no file)
git diff 325a8f2 24cc6ac | grep -i -E '^\+.*(qq\.com|users\\|/users/|\bInc\b|\bLtd\b|GmbH|employer)'   (no line)
```

The gate's ASCII check: `825 files checked, 0 with non-ASCII bytes`. The
organisations the diff names are those of public standards and sources
(CDISC, FDA, admiral and the like); no person is named. CLAUDE.md is 59
lines. Right.

### 9. Findings

F1. SHOULD FIX. src/specfirst/compile/versions.py:160-169 and
tests/unit/test_versions.py:31-36. The check "frozen" compares a folder
with the `tree` of standard/versions.yaml, the file that sits beside it:
a frozen folder edited together with its `tree` line passes (case a), and
so does a mode-only change (every file is hashed as 100644). Nothing else
pins the frozen trees:

```text
$ git grep -n -e a25d42c0 -e 7ac0f4fc 24cc6ac -- src tests scripts Makefile standard
24cc6ac:standard/versions.yaml:15:    tree: a25d42c08d37352131b9320a62c7fa2ce266cb9b
24cc6ac:standard/versions.yaml:26:    tree: 7ac0f4fc4d76333817b6e3edf21e156afec38ef4
```

"Carried out" says that the recorded trees "are those of the tag"; no
script checks it. Fix: a unit test that holds the frozen entries of
versions.yaml (label, status, tree) against literals, extended at each
freeze; and, where git and the tag are present, the gate check compares
with `git rev-parse catalog@1:standard/catalog` and
`catalog@1:standard/houses/open-default@1`. The mode bit is a stated
choice of "Carried out"; say in the report that a mode change is not seen.

F2. SHOULD FIX. versions.py:136-180 and 228-235; catalog.py
`Catalog.label`; house.py `House.label`. A label is taken from the files
inside a folder (`version` of catalog.yaml, `house`/`version` of
house.yaml), never compared with the folder's name or with versions.yaml.
On a copy with `catalog@3` and `open-default@3` copied from version 2 and
listed as drafts:

```text
folder catalog@3 loads as catalog@2 from catalog@3
house folder open-default@3 loads as open-default@2 with catalog@2 from catalog@2
frozen_problems: []
```

A kit built from such a folder would name the label of another version.
Likewise the `catalog` of a house in versions.yaml is never compared with
`catalog_version` of house.yaml or `catalog` of defaults.yaml (case f
passes), and `versions.pair_problems` is never called (dead code). Fix: in
`frozen_problems`, load each listed version and require folder name =
label and versions.yaml `catalog` = `house.catalog_label`; use or remove
`pair_problems`.

F3. SHOULD FIX. src/specfirst/harness/knowledge.py:68. The skills
(`specfirst run skills --write`) mark "the house default" from
`entry.default_for(unit)`, that is from the catalog entry. A catalog@2
entry has none, so rendered from catalog@2 every SKILL.md would say "House
default: none" without an error, and the skills check compares the file
with the same rendering. Not reached in 2a (the skills render the default
catalog, catalog@1), but this is the part that moves the defaults, and
decision 2 lists the call sites. Fix: take the default from
`houses.default_value` with the house of the pair, or refuse a catalog
without defaults there until catalog-2c.

F4. SHOULD FIX (record). Two sentences of the approved decisions are not
carried out and "Carried out / catalog-2a" does not say so: (a) decision 3,
"Every command and function that loads a catalog or a house takes a
label": only `catalog`, `house`, `compile`, `render` and `parse` do; gen
(gen/kits.py:274-275, gen/gate*.py, gen/study.py), the harness
(harness/runs.py, knowledge.py, pilot.py, command.py) and the scorer
(score/candidate.py:383-384, hand.py, kit.py, scorer.py) load
`default_dir(root)` and do not read the labels of the kit they score; (b)
decision 4, "Two pairs are comparable on a kit only when every decision of
the kit is kept by both migration files; a script decides it": there is no
such function (`git grep -i -E "comparable|kept by both" 24cc6ac -- src
tests`: nothing). Neither is wrong while one pair is in use. Fix: say in
ADR-020 "Carried out" (or a backlog record `waits: catalog-2c`) that both
come with catalog-2c, or add them.

F5. SHOULD FIX. third_party/SOURCES.md:25 and :27. The idiom records still
name `standard/catalog/templates/*.yaml`, which no longer exists, and only
`open-default@1`; the copies in standard/catalog@2/templates/ and
standard/houses/open-default@2/{adam,ars}/ are not named (PLAN.md 2.1, rule
1). Fix: `standard/catalog@<n>/templates/*.yaml`,
`standard/houses/open-default@<n>/adam/*.yaml` and `.../ars/*.yaml`.

F6. SHOULD FIX (rule R5). The refusals of decision 1 outside the gate have
no test: `harness.task.kit_catalog` (task.py:131-142), the generator's
(gen/kits.py:276-279) and `specfirst house --write` on a frozen house
(cli.py:195). They work (section 5), but a guard counts once it has failed
on a plant. A test of `kit_catalog` with a draft label and one of `_house`
are cheap; the generator's guard is reachable only through
`DEFAULT_CATALOG`, which the check "frozen" already holds.

F7. NOTE. cli.py. A pair that does not fit ends in a traceback
(`specfirst catalog --catalog catalog@2`, `specfirst house --catalog
catalog@2`); a catalog alone takes the default house, unlike a house alone,
which CLAUDE.md states only for the house. `_house --write` with a label
that versions.yaml does not list raises KeyError (cli.py:195).
compile/gate.py:196-205 calls `versions.folder` before `frozen_problems`,
so a malformed label in versions.yaml stops the check with a VersionError
instead of a problem line. Fix: catch HouseError and VersionError in the
CLI and in `frozen_check`.

F8. NOTE. compile/checks.py:594-653. A per-family entry missing from
defaults.yaml is reported, once per unit, as "an entry with `units` has
one item per unit, and only such an entry" instead of "no item"; a unit
under `units` that the entry does not have is ignored silently (none
today). The plant "a default that is not an alternative" asserts only the
substring "ae.teae.end". `template_directive_problems` raises TypeError on
a `$fn` whose value is a mapping.

F9. NOTE, for catalog-2b (no effect in 2a: no default has `cases`).
house.py:207-232: without design features a default by design is left out
of both `defaults()` and `without_default()`, so STANDARD.md would neither
state the default of #2 nor list it under "Decisions without a default",
and `specfirst compile --defaults` (cli.py:211-213) drops it silently;
score/candidate.py:280 and score/hand.py:243 and 270 call `default_value`
without features and would raise. The check "defaults" proves that every
design resolves by its structure (known features, last case without
`when`), not by evaluating the cases on the designs the sampler draws, as
decision 9 words it; enough while `when` names catalog features only, but
the report should say so.

F10. NOTE. standard/BACKLOG.yaml. `i28.real-kit-pins` stands for the
decision 7 row "entries for the pilot's efficacy decisions (`custom:eff-*`)
| real-4, std-2" but records layer `code`, target `kits/cdiscpilot01`, kind
"name the pair", `for: real-4`; the row is new catalog entries for real-4
and std-2. `i06.first-dose-day` leaves out "the time rule, when chosen,
also makes post-baseline time-aware". The check "backlog" proves one
record per issue, not one per item (decision 9 says item).

F11. NOTE. docs/state/std.md at `24cc6ac`, "Open", still says "ADR-020
proposed, phase 1 only ... Nothing is carried out until the base session
relays the answer"; the report draft says the state file was updated.
standard/houses/open-default@2/ars/demographics.yaml:3 keeps "see
standard/catalog/templates/" (fixable in the draft). The overview of
catalog@1 (`specfirst catalog --overview`) now prints a default that one
ID gives to every unit once per unit: 16 lines differ from `325a8f2`, for
example "Default: `all_arms` for tfl-demographics; `all_arms` for
tfl-ae-summary; ..."; harmless (docs/reports/std-1.catalog.md is
historical).

### For the merge

No finding is blocking: version 1 is the tag's to the byte, version 2 is
version 1 with the defaults moved and nothing else, the default pair and
the task's catalog bytes are unchanged, the refusals hold, and every new
check fails on its plants. F1 to F6 should be fixed or answered before the
merge; a change of code or tests for them needs pass 2 to look at it. Pass
2 also covers the clean-clone logs of gen-2a, gen-3a, read-1a and read-2a
on `24cc6ac` (gen-2a was still running when this pass ended) and the final
report. This signature covers `24cc6ac` and the two finished logs
(catalog-2a, std-1).

Verdict: SIGNED

## Pass 2

Reviewer: the same fresh-context reviewer, 2026-11-21. Under review: the
fix commit `78c9084` on `track/std` (`git diff 24cc6ac 78c9084`, 11 files,
212 insertions, 24 deletions); the six gate logs of `24cc6ac`, copied to
docs/reports/catalog-2a.*.gate.log; the clean-clone logs of catalog-2a and
std-1 on `78c9084` (build/gates/<wp>/clean-clone.log); and the draft
docs/reports/catalog-2a.md (uncommitted, read, not judged as a commit). The
uncommitted catalog-2b work of the working tree is not reviewed. Checks as
in pass 1: a fresh clone at `78c9084` under /tmp, light scripts on copies of
`standard/`, `specfirst catalog` and `specfirst house`; no gate, no test
suite, no kit build.

### The findings of pass 1

```text
$ git diff --stat 24cc6ac 78c9084
 docs/decisions/ADR-020.md | 17 +, docs/state/std.md | 13 +-, src/specfirst/cli.py | 17 +-,
 compile/checks.py | 7 +, compile/gate.py | 7 +-, compile/migration.py | 19 +,
 compile/versions.py | 54 +-, standard/BACKLOG.yaml | 6 +,
 tests/defects/test_versions_checkers.py | 35 +-, tests/unit/test_versions.py | 57 +,
 third_party/SOURCES.md | 4 +-          (condensed to one line per group)
```

F1, fixed. `versions.PINNED` holds the trees of catalog@1 and open-default@1,
`frozen_problems` fails when versions.yaml records another tree for a
pinned label, a unit test holds PINNED against the two literals, and the
plant "a frozen folder changed with its line of versions.yaml" is new.
ADR-020 "Carried out" now says that a mode-only change is not seen. On the
clone (script: plant on a copy, then `versions.frozen_problems`):

```text
a) byte changed, versions.yaml given the new tree: ['catalog@1: standard/versions.yaml records the tree 529c8a53..., the code pins a25d42c0...: a frozen version does not change']
b) byte changed, catalog@1 set to draft, tree line kept: ["the default pair: names 'catalog@1', a draft version; ..."]
c) catalog@1 folder and line removed: ["open-default@1: needs the catalog 'catalog@1', which standard/versions.yaml does not list", "the default pair: names 'catalog@1', which standard/versions.yaml does not list"]
```

a was the false pass of pass 1. b and c still fail today, but only through
the default pair: new note G1.

F2, fixed. `_label_problems` (versions.py) checks the version a folder's
catalog.yaml or house.yaml says against the folder's label, and the house's
`catalog_version` against the `catalog` of versions.yaml.
`pair_problems` is gone. Two plants are new. On the clone, with catalog@3 and
open-default@3 copied from version 2 and listed as drafts:

```text
catalog@3: its catalog.yaml says version 2, not catalog@3
open-default@3: its house.yaml says open-default@2, not open-default@3
open-default@3: its house.yaml needs catalog@2, standard/versions.yaml says catalog@3
f) versions.yaml pairs open-default@2 with catalog@1: ['open-default@2: its house.yaml needs catalog@2, standard/versions.yaml says catalog@1']
pair_problems still defined: False
```

F3, moved to catalog-2c. ADR-020 "Carried out" says that catalog-2c moves the
default pair "and with it the rendering of the reader's skills
(`harness/knowledge.py` reads the defaults of the catalog, which version 2
no longer holds)". I accept this: the skills render the default catalog,
which stays catalog@1 until catalog-2c.

F4, fixed. (a) ADR-020 "Carried out" now says that the commands of the
generator, the reader harness and the scorer take the default pair and get
no `--catalog` or `--house`, and why. (b) `migration.comparable` (records,
new catalog) lists every decision that the step does not keep. A rename
without a change of meaning, and a `custom:` record, are kept. A unit test
covers a kept record, a renamed one, a custom one and a removed one. On the
clone, the 58 defaults of open-default@1 against catalog@2:

```text
comparable(defaults of open-default@1, catalog@2): []
```

The docstring says that a step of the house is judged apart, since a house
has no migration file. That is a fair reading of "both migration files".

F5, fixed. third_party/SOURCES.md:25 and :27 now name
`standard/houses/open-default@<n>/adam/*.yaml`,
`standard/catalog@<n>/templates/*.yaml` and
`standard/houses/open-default@<n>/ars/*.yaml`, and say that version 2 is a
copy of version 1 with changes of our own. `git grep -E
'standard/catalog([^@]|$)' 78c9084 -- third_party` finds nothing.

F6, fixed. tests/unit/test_versions.py has two new tests. The first,
`test_a_task_and_a_kit_refuse_a_draft_version`, checks `kit_catalog` with
a draft label, and also `kits._generate` on a copy where catalog@1 is set
to draft. The second, `test_house_write_refuses_a_frozen_house`, checks
`house --write` and a pair that does not fit, through `cli.main`. The unit
tests went from 1292 to 1301: 5 new plants and 4 new tests.

F7, fixed. `cli.main` catches CatalogError, HouseError and VersionError
around the handlers of `catalog`, `house`, `compile`, `render` and `parse`.
`_house --write` refuses a label that versions.yaml does not list.
`frozen_check` no longer stops on a malformed label. On the clone:

```text
$ specfirst catalog --catalog catalog@2
cannot load the catalog and the house: house: open-default@1 needs catalog@1, not catalog@2; ...
exit 1
$ specfirst house --write --house open-default@1
open-default@1 is frozen or not listed in standard/versions.yaml: its STANDARD.md is not written (ADR-020)
exit 1
$ specfirst catalog --catalog catalog@9
cannot load the catalog and the house: no catalog at /tmp/rv-cat2a-p2/specfirst/standard/catalog@9
exit 1
```

F8, fixed in part. A per-family entry with no item now gets "no item", and
a unit the entry does not have is named once. Both have new plants, and the
weak assertion is now the full message. The `$fn` part is not fixed: a
`$fn` whose value is a mapping still raises.

```text
a $fn whose value is a mapping: TypeError unhashable type: 'dict'
```

That leaves it a note. The gate stops with an exception, so it cannot pass
wrongly. It can be fixed with 2b.

F9, for catalog-2b, as the coordinator says. Still open there.

F10, fixed. Two new records. `i28.efficacy-entries` (catalog layer, entries
for the pilot's efficacy decisions, waits for real-4 and std-2) is the row of
decision 7; `i28.real-kit-pins` stays as an extra record.
`i06.post-time-aware` holds the second half of #6. The gate log of
`78c9084` reads `standard/BACKLOG.yaml: 62 records for 26 issues; 40
accepted, 9 done, 13 waits` and `backlog: 0 problems`. New note G2 is on
the layer of `i06.post-time-aware`. That the check counts issues, not
items, stays as it is; I did the mapping by hand in pass 1.

F11, fixed in part. docs/state/std.md "Next" now describes ADR-020 as
approved, with its three parts, and the default pair until catalog-2c.
standard/houses/open-default@2/ars/demographics.yaml:3 still reads "see
standard/catalog/templates/". It is a comment in a draft, and 2b can fix
it. The overview needs no change.

### New findings

G1. NOTE, for catalog-2c at the latest. src/specfirst/compile/versions.py
`frozen_problems`. PINNED binds the `tree` line of versions.yaml, not the
folder. For a pinned label the folder is compared only while its status is
`frozen`, and a pinned label is not required to be listed at all. Cases b
and c above fail today only because catalog@1 and open-default@1 are the
default pair. Once catalog-2c moves the default pair, a pinned version set
to `draft` and then changed, or removed with its folder, would pass the
check. Fix: for every label of PINNED, require that it is listed, frozen,
and that `tree_hash(folder) == PINNED[label]`. The fix is small and should
land before or with catalog-2c.

G2. NOTE, for catalog-2b. standard/BACKLOG.yaml `i06.post-time-aware` has
layer `house`, target `adam/advs.yaml`, and is accepted for
`open-default@2`. Decision 7 puts this half of #6 under "C". Suppose 2b
makes post-baseline time-aware in the fragment of the time alternative of
`bds.baseline.rule`, which is a catalog change in meaning. Then its line in
catalog@2/migration.yaml must name a record accepted for catalog@2, and
`i06.first-dose-day` would serve. If 2b does it in the house parent spec,
the record is right as it stands.

### The gate logs

The six logs of `24cc6ac` (docs/reports/catalog-2a.<gate>.gate.log), heads
and results:

```text
catalog-2a  commit: 24cc6ac  1292 passed, 30 deselected  GATE catalog-2a: PASS (17 checks)
std-1       commit: 24cc6ac  1292 passed, 30 deselected  GATE std-1: PASS
gen-2a      commit: 24cc6ac  1292 passed, 30 deselected  GATE gen-2a: PASS
gen-3a      commit: 24cc6ac  1292 passed, 30 deselected  GATE gen-3a: PASS
read-1a     commit: 24cc6ac  1292 passed, 30 deselected  GATE read-1a: PASS
read-2a     commit: 24cc6ac  1292 passed, 30 deselected  GATE read-2a: PASS ("PASS  arm R, kept dry run")
```

"PASS unchanged" (ADR-020, consequences): each log against the newest log
of the same gate on `main`. The comparison is a script that removes
commits, clone paths, times, test counts and progress dots from both logs,
then runs diff:

```text
gen-2a  vs main:issue-30.gen-2a.merged (db68baf): 10 lines differ: the commit subject, the timings of two
        sub-runs, "compared 168 Python files of ours" (163 on main: the new modules), the ASCII count
gen-3a  vs main:issue-30.gen-3a (8154075): 4 lines differ: the commit subject, the ASCII count
read-2a vs main:real-5b-answers.read-2a (4660e8c): 4 lines differ: the commit subject, the ASCII count
read-1a vs main:adr-017.read-1a (13b946e): 26 lines differ: the commit subject, one timing, the ASCII
        count, and the kit.yaml hash of the 10 kits of the seed gen-2a
```

The kit.yaml hashes of read-1a differ from that older log because
standard/methods changed on `main` after it (real-5b, edeea2c), and a
change there changes `registry_sha256` in every kit.yaml (CLAUDE.md). The
read-1a log of `24cc6ac` gives `kit.yaml a5a1da67d4dac930`,
`79e43bbd9a826cf9`, `46dfe55ee714fe83`, `75addb7d7b70d358` for kits 1 to 4.
These are the first 16 digits of the SHA-256 that the draft report gives
for the kits written on clones of `325a8f2` and `869b8c0` (`diff -r`:
identical, 511 files). Every count, cell, probe and separation line of the
four gates is the same as on `main`.

The two logs of `78c9084`, both final (head `commit:     78c9084`, last
line `clean clone gate <wp>: PASS`):

```text
build/gates/catalog-2a/clean-clone.log  1301 passed, 30 deselected; frozen: 0 problems; migration: 0 changed in meaning;
                                        backlog: 62 records, 0 problems; defaults: 58 defaults, 4 stated as none; GATE catalog-2a: PASS
build/gates/std-1/clean-clone.log       1301 passed, 30 deselected; catalog specfirst-m1 1; house standard open-default@1:
                                        58 defaults, 4 decisions without a default; GATE std-1: PASS
```

gen-2a, gen-3a, read-1a and read-2a were not run again on `78c9084`. No
code path of theirs changes. The functions the commit changes are called
only from compile/versions.py, migration.py, checks.py, gate.py and
gates.py. `defaults_problems` runs only for a house with defaults.yaml, and
the new `try` of `cli.main` wraps only the handlers of `catalog`, `house`,
`compile`, `render` and `parse` (`gen`, `score` and `run` return before
it):

```text
$ git grep -n -E 'frozen_problems|_label_problems|PINNED|comparable\(|defaults_problems|frozen_check' 78c9084 -- src \
    | grep -v -E 'compile/(versions|migration|checks|gate)\.py|gates\.py'
(only kit.py's own PINNED_AREAS)
```

The whole unit suite, which the fix does change, ran in both gates of
`78c9084`. ADR-020 lets a part leave such gates out "with the reason in the
report".

The fix commit is ASCII (`git diff 24cc6ac 78c9084 | LC_ALL=C grep -c
$'[\x80-\xff]'`: 0). It adds no path, token or name. CLAUDE.md is still 59
lines.

### The draft report

The draft docs/reports/catalog-2a.md matches the commits and the logs above
in what it states. It has the trees, the frozen and migration lines, the
plants (those of `78c9084` included), the kits written twice with
`diff -r`, and the table of the six gates on `24cc6ac`. Before the merge it
needs three things:

- the rows for catalog-2a and std-1 on `78c9084`, with their logs copied
  next to the others;
- the reason the other four gates are not run on `78c9084` (above);
- a line on F3 and F9 (moved to catalog-2c and catalog-2b) and on the notes
  G1 and G2.

A commit that changes only the report and the log copies needs no further
pass.

### For the merge

Every finding of pass 1 is fixed, or moved with its reason written down
(F3, F9), or a note that can wait (the `$fn` part of F8, the comment part of
F11). G1 and G2 are notes for later parts. Nothing is blocking. This
signature covers `78c9084`, the six logs of `24cc6ac` and the two logs of
`78c9084`.

Verdict: SIGNED
