# gen-3a Documents, slice "adverse event summary first": report

Date: 2026-11-18. Branch: `track/gen`. Part gen-3a of ADR-005, decision 1.
Depends on gen-2a (on `main` since `d5c7e50`). `main` was `b5ccb77` when the
part began; `track/gen` was brought to it first (a fast forward).
Choices: docs/decisions/ADR-009.md. Review: docs/reports/gen-3a.review.md.

## Verdict

The gate script passed: `scripts/clean_clone_gate.sh gen-3a` exited 0 on a
clean clone of `901be3d`, after a fresh install and a fresh fetch, 15 of 15
checks in 511 seconds. Its full output is `docs/reports/gen-3a.gate.log`
(296 lines); the section "The gate" quotes it. The gates gen-2a and read-1a passed on clean clones of the same
commit: 13 of 13 checks in 747 seconds, and 14 of 14 in 1,157 seconds
(`docs/reports/gen-3a.gen-2a.gate.log`, 399 lines;
`docs/reports/gen-3a.read-1a.gate.log`, 685 lines).

- The parser recovers 100% of the decisions of every kit: 286 decisions in
  ten kits, from the two standard-form documents of each kit, with the
  house standard for the defaults and the oracle for the asked decisions.
- Every natural document passes the slot check and the read-back check:
  182 decision paragraphs and 40 filler paragraphs in 20 natural
  documents.
- A planted bad rewrite (80 changed to 85 in the paragraph of the age
  groups) is rejected three times: by the slot check and by the read-back
  check in a kit, and by the loop when a rewriter proposes it.
- Each kit lists its visible probes in `kit.yaml` (12 to 20 per kit), and
  each is found again in the visible data.
- 18 planted defects inside the gate were each reported by the check they
  were planted for (rule R5).

Model use for the documents: three calls to subagents on Sonnet 5.5,
190,881 tokens in all, 62 seconds. Nothing fell back to a phrasing
template. The independent review used 1,075,749 tokens of the session's own model
(Opus 5.5) in three runs, as reported (section "Review"). The executor's
own session is not counted here.

The review did not sign pass 1 (four blocking findings, all settled since,
see "Review"); it signed pass 2 on `901be3d`. Two of its questions are the owner's; the
part is not merged until they are answered (section "For the owner").

## What was built

Stage S6 of the generator, for the 22 decisions of the slice and the other
decisions a kit of the slice holds (the defaults of `mod-demographics`, the
three outputs that are not included): 28 or 29 decisions per kit.

| Module | What it does |
| --- | --- |
| `specfirst.gen.documents` | the protocol and the SAP of a kit, each in standard form (`gold/docs/`) and in natural form (`inputs/docs/`); the tiers; `gold/oracle.yaml`; `gold/docs/natural.json`; `gold/summary.md`; `problems`, the checks of a written kit by name |
| `specfirst.gen.natural` | the store of model text (`src/specfirst/gen/rewrites/`); the slot check (`token_groups`, `slot_problems`); the read-back (`readback_request`, `readback`, `Store.readbacks`, `paragraph_problems`); the fallback to the phrasing template |
| `specfirst.gen.gate3` | the checks of `specfirst gate gen-3a`, each with its planted defects |
| `specfirst.gen.kits` | S6 in `_attempt`; `kit.yaml` gets `documents` and `probes`; `check` runs every check of `documents.problems` |
| `specfirst.score.scorer`, `.kit`, `.defects` | the scorer reads the four documents and the oracle; the parser control reads both standard-form documents and asks the oracle for what neither they nor the house standard decide; two plants of read-1a choose their decision so that they work on every tier |
| `specfirst gen natural` | `requests`, `propose`, `readback-requests`, `readback`, `status`: the loop of section 6.6, one step at a time |

`GENERATOR` is `gen-3a.2`. The decision vectors of a seed did not change:
the ten kits of the gate seed are the studies of gen-2a with the same
decisions (kit 4, for example, is `SFRRL2UH` with the vector it had).

A kit now holds:

```text
inputs/docs/protocol.md   inputs/docs/sap.md        natural form (IDs protocol, sap)
gold/docs/protocol.md     gold/docs/sap.md          standard form (protocol-standard, sap-standard)
gold/docs/natural.json    gold/oracle.yaml          gold/summary.md
kit.yaml: documents (tier, files, stated, asked, paragraphs by source), probes (visible, twin)
```

Tiers by the number of a kit in its set: full in kits 1, 3, 6, 9; standard
in 2, 5, 8, 10; the ask demo in 4 and 7, which here both leave out
`ae.related.values` and `pop.efficacy.rule`.

## How the model was reached, and what it cost

ADR-009, decision 1. The route that section 11.1 names for the reader is
`claude -p`. The CLI on this machine is the npm package, and it is not
logged in:

```text
PS> "Reply with the single word OK." | claude -p --model haiku --output-format json --system-prompt "You answer briefly." --strict-mcp-config --disallowedTools "Bash,Edit,..."
{"type":"result","subtype":"success","is_error":true,"duration_ms":2213,"duration_api_ms":0,"num_turns":1,
 "result":"Invalid API key - Please run /login", ... "total_cost_usd":0,"usage":{"input_tokens":0, ... "output_tokens":0, ...}}
```

(The CLI writes a middle dot where this ASCII file has a hyphen.) Logging
in handles a credential and is the owner's act, so this part used
subagents of its own Claude Code session (the Agent tool, model option
`sonnet`), on the subscription the session already runs on. Every request,
answer file and final message of a subagent is in
`src/specfirst/gen/rewrites/calls/`, named by its SHA-256 in `calls.jsonl`.

| Call | Role | Items | Tokens | Tool uses | Seconds | Result |
| --- | --- | --- | --- | --- | --- | --- |
| rewrite-1 | rewriter (Sonnet 5.5, fresh context) | 61 statements, 10 filler headings | 64,268 | 2 | 36 | 61 of 61 pass the slot check |
| readback-1 | verifier (Sonnet 5.5, a new fresh context) | 61 paragraphs, 10 filler paragraphs | 74,146 | 2 | 21 | 61 of 61 read back as their alternative; 10 of 10 filler state nothing |
| readback-2 | verifier (Sonnet 5.5, a new fresh context) | 1 paragraph, read again (review D3) | 52,467 | 2 | 5 | read back as the alternative `none`, "not the abstention answer" |
| total | | | 190,881 | 6 | 62 | no regeneration, no fallback |

The token counts are what the Agent tool reported for each subagent: all
tokens of the call, the request file included. The probe of the CLI cost
nothing.

```text
$ specfirst gen natural requests --kits /root/scratch-gen3a/kits0 --out .../rewrite-1.request.json
.../rewrite-1.request.json: 61 paragraphs, 10 filler
$ specfirst gen natural propose rewrite-1.answer.json --kits ... --call rewrite-1 --request rewrite-1.request.json --tokens 64268 --tool-uses 2 --seconds 36
05a0409aec2f78dc tfl.output.include: attempt 1: slots ok
... (61 lines "slots ok")
filler-protocol-1: filler: ok
... (10 lines)
store .../src/specfirst/gen/rewrites: 61 statements, 0 accepted (0 by the phrasing template), 61 open; 0 of 10 filler paragraphs accepted; 1 calls, 64268 tokens
the kits state 61 statements; without an accepted text: 61
$ specfirst gen natural readback-requests --kits ... --out .../readback-1.request.json
.../readback-1.request.json: 61 items, 10 filler
$ specfirst gen natural readback readback-1.answer.json --kits ... --call readback-1 --request readback-1.request.json --tokens 74146 --tool-uses 2 --seconds 21
... (61 lines "read back as <alternative>: ACCEPTED")
filler-protocol-1: filler read back as stating nothing
... (10 lines)
store .../src/specfirst/gen/rewrites: 61 statements, 61 accepted (0 by the phrasing template), 0 open; 10 of 10 filler paragraphs accepted; 2 calls, 138414 tokens
the kits state 61 statements; without an accepted text: 0
$ specfirst gen natural readback readback-2.answer.json --kits ... --call readback-2 --request readback-2.request.json --tokens 52467 --tool-uses 2 --seconds 5 --message readback-2.message.txt
5875cc9d5d85dbf2 tfl.columns.total: attempt 1: read back as none: ACCEPTED
store .../src/specfirst/gen/rewrites: 61 statements, 61 accepted (0 by the phrasing template), 0 open; 10 of 10 filler paragraphs accepted; 3 calls, 190881 tokens
the kits state 61 statements; without an accepted text: 0
```

What the verifier is shown, for one item (`calls/readback-1.request.json`
has them all): the paragraph, the question of its entry and the
alternatives, under an opaque ID; never the statement or the value.

```text
{"item": "r00ec5a3ef6d5",
 "paragraph": "The treatment-emergent period has no end date.",
 "question": "When does treatment emergence end?",
 "alternatives": [{"id": "no_end", "rule": "Treatment emergence has no end date."},
   {"id": "last_dose_plus_days", "rule": "Treatment emergence ends <days> days after the treatment end date.", "meaning": "..."},
   {"id": "end_of_study", "rule": "Treatment emergence ends at the end-of-study date.", "meaning": "..."}]}
```

The first read-back was told to answer `none` for "none of them", and `none`
is also the ID of an alternative of `tfl.columns.total` ("There is no total
column"). For that one paragraph the pick `none` could not tell agreement
from abstention (lesson 57; review D3). The abstention is now `(none)`; the
call log names the abstention of every call, and a pick equal to it counts
for nothing. A new verifier read the paragraph again under the new rule
(`readback-2`) and picked the alternative `none`, saying "not the abstention
answer".

## The two checks of section 6.6

- Slots (ADR-009, decision 7). The tokens of a statement come in groups:
  one per slot (its scalars), the numbers of the template text with their
  unit words, the names (variable names, words in capitals such as
  `OTHER`), the name of the output. A group keeps its order; groups may
  stand in any order. A token with a capital letter keeps its case. The
  paragraph may hold no number and no word in capitals that the statement
  lacks. Two versions came before this one: the first asked the whole
  statement in its order and failed a phrasing template of the catalog
  ("The reference start date of the subject (DM.RFSTDTC) counts as study
  day 1.", lesson 56); the second ignored case and extra words, and the
  review found nine rewrites that change the meaning and passed it (D5).
  This version refuses five of them; the four that add an ordinary word
  ("14 working days", "WEEK 4 or a later visit", "Active Placebo", "other
  than Placebo and Low Dose") pass both checks, and ADR-009 names them as
  the known limit. The unit tests hold every phrasing family of the
  catalog (plain, formal, brief) for every alternative of the slice
  against the check: the fallback always passes it.
- Read-back. The verifier's pick is held against exactly the text a kit
  uses, by its SHA-256. A paragraph changed after its read-back has none.

## The gate

`scripts/clean_clone_gate.sh gen-3a` on a clean clone of `901be3d`, from
`docs/reports/gen-3a.gate.log` (cut to the lines that carry the result;
the log has every line):

```text
clean clone gate gen-3a
commit:     901be3dce07663a9475f34ad4bfb734ec0297760
$ bash env/install.sh
$ specfirst fetch
...
== [4/15] unit tests: pytest -m "not evidence" -q
1055 passed, 23 deselected in 343.68s (0:05:43)
== [5/15] kits: specfirst.gen.gate3.kits_written: the 10 kits of the seed of the gate gen-2a, each by a process of its own; the tiers of their documents
tiers of the documents: full, standard, full, ask, standard, full, ask, standard, full, standard; kits of the ask demo: 2
== [6/15] parser
planted defect in kit 1: the standard-form SAP without the statement of trt.planned.source: the check reports it: trt.planned.source (mod-treatment, stated): not recovered from the documents, the house standard and the oracle
planted defect in kit 1: the standard-form SAP states the other rounding rule: the check reports it: gold/docs/sap.md [6/s6] states tfl.rounding.rule as {'rule': 'half_even'}; the record is stated {'rule': 'half_away_from_zero'}
kit 1 (full): 29 of 29 decisions recovered from the standard-form documents, the house standard and the oracle; 0 problems
... (kits 2 to 10: 29, 28, 29, 28, 28, 29, 28, 29, 29 of as many; 0 problems)
== [7/15] slots
planted defect in kit 1: the variable name DM.ARM taken out of the paragraph of trt.planned.source: the check reports it: sap#3/p6 (trt.planned.source): slot check: 'DM.ARM' is not in the paragraph
planted defect in kit 1: the numbers 65 and 80 exchanged in the paragraph of demo.age.groups: the check reports it: sap#6/p1 (demo.age.groups): slot check: '80' is out of the order of the statement
kit 1 (full): 29 decision paragraphs keep the tokens of their statements; 0 problems
... (kits 2 to 10: 12, 28, 10, 11, 28, 11, 13, 29, 11; 0 problems)
== [8/15] read-back
planted defect in kit 1: the store says the verifier read the paragraph of tfl.rounding.rule as half_even: the check reports it: sap#7.1/p1 (tfl.rounding.rule): read-back: read back as half_even, the decision is half_away_from_zero
planted defect in kit 1: the store has no read-back of the paragraph of tfl.rounding.rule: the check reports it: sap#7.1/p1 (tfl.rounding.rule): read-back: no read-back of this text in the store
planted defect in kit 1: the filler paragraph sap#8/p1 is not the text the store read back: the check reports it: sap#8/p1: filler that the store did not read back as stating nothing
kit 1 (full): 29 decision paragraphs read back as their alternative, 4 filler paragraphs as stating nothing; 0 problems
... (kits 2 to 10 likewise; 0 problems)
the store: 61 statements, 61 accepted, 0 of them by the phrasing template; 10 filler paragraphs; 3 model calls
== [9/15] bad rewrite
planted defect in kit 1: the paragraph sap#6/p1 of demo.age.groups with 80 changed to 85: the check reports it: sap#6/p1 (demo.age.groups): slot check: '80' stands 1 times in the paragraph, the statement has it 2 times
planted defect in kit 1: the same rewrite, held against the read-back: the check reports it: sap#6/p1 (demo.age.groups): read-back: no read-back of this text in the store
planted bad rewrite proposed to the loop: df8653d2f4260e7e demo.age.groups: attempt 1: SLOTS: the number 85 is not in the statement; '80' stands 1 times in the paragraph, the statement has it 2 times; not accepted and not sent to the verifier: yes
== [10/15] tiers
planted defect in kit 4: a kit of the ask demo whose oracle answers nothing: the check reports it: the oracle answers [], the asked decisions are [('ae.related.values', 'mod-ae-emergence'), ('pop.efficacy.rule', 'mod-populations')]
planted defect in kit 1: a kit of the tier full that leaves one house default to the house standard: the check reports it: trt.planned.source (mod-treatment): default, the tier full asks stated
... (kits 1 to 10: 0 problems)
kit 4: the ask demo leaves out pop.efficacy.rule, ae.related.values; the oracle answers them
kit 7: the ask demo leaves out pop.efficacy.rule, ae.related.values; the oracle answers them
== [11/15] anchors
planted defect in kit 2: the natural citation of trt.planned.source names the next paragraph: the check reports it: trt.planned.source (mod-treatment): the quote does not stand at sap#3/p3
planted defect in kit 2: the paragraph of trt.planned.source changed after natural.json was written: the check reports it: inputs/docs/sap.md: not the text natural.json names
kit 1 (full): 58 citations stand at their anchors; 0 problems
... (kits 2 to 10: 41, 56, 37, 39, 56, 38, 41, 58, 40; natural.json names every paragraph; 0 problems)
== [12/15] visible probes
planted defect in kit 1: kit.yaml lists ae_on_first_dose_date_without_time as visible: the check reports it: kit.yaml does not list the probes of the log by dataset
planted defect in kit 1: the log and kit.yaml claim ae_on_first_dose_date_without_time for the visible data: the check reports it: visible data: probe ae_on_first_dose_date_without_time: the data cannot be read for this probe: KeyError: 'SFPBT5ZJ-101-060'
kit 1 (full): 19 visible probes listed and found in the visible data; 0 problems
... (kits 2 to 10: 20, 15, 17, 19, 12, 14, 13, 17, 16; 0 problems)
== [13/15] summary
planted defect in kit 1: the summary without the line of trt.planned.source: the check reports it: the summary does not name trt.planned.source
planted defect in kit 1: the summary 30 lines longer: the check reports it: the summary has 80 lines, more than 60
... (kits 1 to 10: one page, every decision named; 0 problems)
PASS  environment 0.4 s   PASS  pins 0.8 s        PASS  lint 0.0 s       PASS  unit tests 344.3 s
PASS  kits 40.9 s         PASS  parser 0.9 s      PASS  slots 0.3 s      PASS  read-back 0.3 s
PASS  bad rewrite 0.2 s   PASS  tiers 0.3 s       PASS  anchors 0.3 s    PASS  visible probes 0.3 s
PASS  summary 0.3 s       PASS  cache untouched 0.1 s                    PASS  ASCII 0.0 s
GATE gen-3a: PASS
clean clone gate gen-3a: PASS (clone: /tmp/specfirst-clean-VnR6xi/specfirst)
```

Earlier runs of this gate on a clean clone: `a315689` failed in its unit
tests (two tests of the scorer on kit 7 of a set, which had become a kit
of the ask demo; lesson 58), `b55db77` passed 15 of 15; the review then
changed the documents (D4) and the checks (D5 to D7), and `901be3d` is the
run above.

## The gates gen-2a and read-1a

Both on clean clones of `901be3d`, run by `scripts/clean_clone_gate.sh`
one after the other, each log copied out of the clone by the script
(lesson 39). Cut to the lines that carry the result.

gen-2a (`docs/reports/gen-3a.gen-2a.gate.log`): the kits are the kits of
gen-3a, each written twice; their check now holds the documents too.

```text
commit:     901be3dce07663a9475f34ad4bfb734ec0297760
== [5/13] unit tests: pytest -m "not evidence" -q
1055 passed, 23 deselected in 343.87s (0:05:43)
== [8/13] kits: specfirst.gen.gate2.kits_pass: 10 kits, each written twice; P1 to P4
kit 1: study SFPBT5ZJ, 4 arms, split train, scenario 1 (all drawn); decision vectors drawn before this one: 0
  P1: 128 files of two builds by two processes, the manifest included: 0 differ
kit sfpbt5zj (train): 127 files have the hashes of kit.yaml; 29 decision records fit the schema; documents of the tier full: 29 of 29 decisions recovered by the parser with the house standard and the oracle, 29 natural paragraphs pass the slot and read-back checks, 58 citations stand at their anchors, 19 visible probes found
...
10 kits of the set 'gen-2a': P1 to P4 hold for every kit
== [9/13] separation
separation: 0 holes in the matrix of 10 kits; every applicable decision is separated on the twin of its kit
== [10/13] engines
the Python engine and the R engine agree on 766 results of 20 builds (10 kits, visible and twin): yes
== [11/13] splits
planted defect: a document of the kit that holds the seed: kit 1: inputs/docs/sap.md holds the seed
GATE gen-2a: PASS
clean clone gate gen-2a: PASS (clone: /tmp/specfirst-clean-oTKyGT/specfirst)
```

read-1a (`docs/reports/gen-3a.read-1a.gate.log`): the scorer on the same
ten kits, the two of the ask demo (kits 4 and 7) among them.

```text
commit:     901be3dce07663a9475f34ad4bfb734ec0297760
1055 passed, 23 deselected in 339.32s (0:05:39)
parser control on HAND01, stage C: 100%
parser control on HAND01, stage T: 100%
every defect that applies is planted on HAND01, detected and attributed: yes
(kit 4, ask)  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 20 of 20; span 20 of 20; ... strict 1 of 1 ...
(kit 7, ask)  arm C, stage C: 22 decisions: value 22 of 22; status 22 of 22; quote 20 of 20; span 20 of 20; ...
  planted in the gold of the kit: the first cell of the twin's grid reads '(N=48)9': the gold check fails: yes
  planted in the document: the statement [1/s2] of trt.actual.source is taken out: the control is not 100%; wrong by value: trt.actual.source: the control fails: yes
  planted in the matrix: the pair of tfl.population with randomized says the opposite: the comparison with the matrix fails: yes
  S11-quote (L0): detected and attributed on 10 kits;
  S12-span (L0): detected and attributed on 10 kits;
gold built again is the gold of the kit: 10 of 10 kits
parser control 100% in both stages: 10 of 10 kits
every defect that applies is detected and attributed on at least one kit: yes
GATE read-1a: PASS
clean clone gate read-1a: PASS (clone: /tmp/specfirst-clean-8wxLI5/specfirst)
```

In the two kits of the ask demo, the control asks the oracle for the two
decisions the documents leave out and has them right by value and by
status; they are not scored on quote and span (section 4.5: a
`study_input` is scored as a question asked). The planted document of the
kit check takes out a decision that differs from the house default; on
`b55db77` it took out `trt.planned.source` at its default in kit 1, and the
check could not fail (review, D2; lesson 59).

## Review

An agent with a fresh context that did not write the work
(`docs/reports/gen-3a.review.md`, rule R7), on the session's model (Opus
5.5).

- Pass 1, on `a315689` and `b55db77`: NOT SIGNED. Blocking: D1 (`a315689`
  failed its own clean-clone gate), D2 (the planted document of the gate
  read-1a could not fail on a kit of the tier full), D3 (one read-back
  could not tell agreement from abstention), D4 (the natural SAP
  contradicted the protocol in the tiers standard and ask). Not blocking:
  D5 to D12. Two questions for the owner.
- The findings were answered in `901be3d` (commit message and ADR-009 name
  each), and the paragraph of D3 was read again (`readback-2`).
- Pass 2, on `901be3d`, after reading the three gate logs above: SIGNED.
  D1 to D7 and D11 settled; D8 left to read-2a (docs/state/gen.md); D9 is
  the first limit below; D10 is question 5 for the owner. Three new
  findings, none blocking: D13, the answer template of the read-back
  request still writes `none`; D14, a real abstention `(none)` counts
  neither as agreement nor as failure, so the loop would never fall back to
  the phrasing template for it (it fails closed: such a statement stays
  `missing` and its kit fails the gate; the store of the gate has no
  abstention); D15, the new checks of two filler sections and of 100
  characters per summary line have no planted defect yet. All three are
  booked in docs/state/gen.md, "Open", to be settled before the loop runs
  for another seed; settling them now would change code after the gates
  and the review.

The reviewer's tokens, as the Agent tool reported each run (a resumed run
counts the reviewer's earlier context again): pass 1 321,058 (73 tool
uses, 956 s); pass 2 in two runs, 364,109 (12 tool uses, 145 s) and
390,582 (23 tool uses, 3,811 s, most of it waiting for the gates).

## Limits

- The rewrites stay close to the standard form: 38 of 61 are within a
  difflib ratio of 0.9 of their statement, two equal it (review, D9). Most
  change the tense and the order of a clause ("Safety analyses will group
  subjects by planned treatment."). The rewriter was told to keep every
  value in the order of the statement and to drop nothing, and it chose to
  change little. Section 6.6 says the natural form "measures robustness to
  wording"; these texts measure little of it, and the read-back of such a
  paragraph is near trivial. All 61 were read back right on the first try,
  so the regeneration and the fallback ran only in unit tests and in the
  planted defects of the gate.
- One rewrite per statement: kits that state a decision the same way share
  its paragraph (ADR-009, Consequences).
- What neither check sees: an ordinary word added to a value or a rule
  (ADR-009, decision 7). The 61 accepted paragraphs were read against their
  statements by the executor and by the reviewer; none adds anything.
- The rewriter and the verifier are subagents of the executor's session;
  their answers reach the store through files the executor hands on, and
  their transcripts are not kept (question 5 for the owner). The final
  messages of the first two calls were kept after the fact.
- The store covers the 61 statements of the ten kits of the gate seed. A
  kit of another seed gets the phrasing template for a statement the store
  lacks, marked `missing`, and fails the gate gen-3a until the loop has run
  for it. Kits 5 to 10 of the gate seed carry the splits dev and test, but
  their statements are in the store: they are no dev or test kits for
  scoring (review, D7).
- The design text of the natural protocol (arms, schedule, vital signs,
  causality scale, disposition) is written by a script and not read back.
- gen-1a was not run again: the only change to its files is the name of the
  generator in them.

## For the owner

1. The Claude Code CLI on this machine (`claude` from npm, 2.0.29) is not
   logged in. read-2a needs `claude -p` for the reader (section 11.1); the
   login is yours. gen-3a did not need it.
2. The ask demo is in kits 4 (train) and 7 (dev) of every set. Section 13.6
   runs the demo in read-3 "on two kits": two dev kits would be the other
   choice.
3. Freer rewrites, more than one per statement, and a phrasing family held
   out for an exam: for the full gen-3, at about 140,000 tokens per round of
   60 statements (rewrite and read-back).
4. From the review (ADR-009, "For the owner", item 4): the parser control
   now asks the oracle for what neither the standard-form documents nor the
   house standard decide. Recommendation: approve; no control can score
   100% on a kit of the ask demo otherwise.
5. From the review (item 5): does a read-back by a subagent of the
   executor's own session, with its request, answer and final message kept
   but no transcript, count as the "verifier agent with a fresh context" of
   section 6.6? Recommendation: accept it for the slice; a script adapter
   (`claude -p`, item 1) takes the executor out of the path once the CLI is
   logged in.
