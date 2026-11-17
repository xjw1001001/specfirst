# Track gen

Result: generated studies for the parallel-group design PG-FIX (PLAN.md
section 13.5).

## Passed

- Nothing yet. gen-1a is written and pushed on `track/gen`; its gate has
  not run to its end (see Open).

## Open

Where gen-1a stands (ADR-005, decision 1), written on 2026-11-17 before a
restart of the owner's machine:

- Written and pushed: CDISC CORE in the environment (ADR-006), the design
  model and the sampler for PG-FIX, the subject process, SDTM for eleven
  domains with Define-XML, the probe recipes of the slice with a check that
  finds each probe again in the data, the gate `gen-1a`, `specfirst gen`.
- Checked: GitHub CI is green on `85b5c7e` (ASCII, ruff, every unit test,
  108 of them new). The two gate checks that need no CORE ("identical
  hashes", "probes") passed for the ten gate seeds on a scratch Python
  environment under Windows, which is not the reference platform.
- Not checked: `specfirst gate gen-1a` has not run to its end. CORE ran by
  hand on one generated study (one seed, visible and twin); the list of
  findings the gate accepts (`src/specfirst/gen/core_findings.yaml`) rests
  on that one study. One finding of that run is still unexplained: rule
  CORE-000239 reported two subjects of the twin, one planted by the probe
  `rfxstdtc_differs_from_exposure`; the other was not looked up (probably
  the probe `partial_exposure_date`).
- Not done: the clean-clone gate, the report docs/reports/gen-1a.md, the
  signed review. A first pass of the review was started before the gate;
  if docs/reports/gen-1a.review.md is missing or stops in the middle, start
  the review again.
- `env/core-requirements.lock` was resolved with uv under Windows for Linux
  (WSL had no network). Run `make lock` under WSL when it has a network
  and compare.
- The merge waits for `scripts/clean_clone_gate.sh gen-1a`: this part
  changes `env/`, and a fresh install is what proves that.

How the day went wrong, for whoever resumes: WSL lost its outbound TCP at
about 10:20; at 11:16 a scratch loop of this session started eight CORE
runs at once and the machine ran out of memory (docs/lessons.md, lesson
32); afterwards the WSL instance was stopped every minute or two until the
owner restarted WSL at 11:40.

## Next

- With WSL up: `specfirst doctor`; then the gate on a clone in the Linux
  file system with the installed environment, inside
  `flock /run/lock/specfirst-heavy.lock`; read every unexplained finding
  of CORE before adding it to `core_findings.yaml`; then the report and the
  review.
- With the network back: `scripts/clean_clone_gate.sh gen-1a` inside the
  same lock, then merge `main` into `track/gen` (the catalog may be frozen
  as version 1 by then: generate again, the files name the catalog), merge
  to `main`, push, CI.
- Then gen-2a (needs gen-1a, std-1 after N1 and real-3a) and gen-3a, then
  the rest of gen-1, gen-2 and gen-3.

## Handed over by base-0

- CDISC CORE: installed by gen-1a through `env/` (docs/decisions/ADR-006.md).
