# gen-3a Documents, slice "adverse event summary first": independent review

Rule R7 of PLAN.md. Reviewer: an agent with a fresh context that did not
write the work. Date: 2026-11-18. Correctness only, no style.

Reviewed: branch `track/gen`, commits `a315689` (the part) and `b55db77`
(the fix of the span plant and of one kit test, after the clean-clone gate
on `a315689` failed in its unit tests), base `b5ccb77` (main). `git diff
b5ccb77 a315689` is 28 files, 4589 lines in, 167 out; `b55db77` changes
`src/specfirst/score/defects.py` and `tests/unit/test_score_kit.py` only.
While I worked the author changed the worktree: first the two files of
`b55db77` (I read that diff before and after it was committed; it is the
same), at the end `docs/lessons.md` (not committed, not reviewed).

Result: NOT SIGNED. Four findings block (D1 to D4); D1 is settled by
`b55db77` once its clean-clone gate passes, and is listed so the record is
whole. Eight do not block (D5 to D12). The gate checks of gen-3a do what
the gate text asks and each fails on its plants; the 61 accepted
paragraphs are faithful to their statements and the 10 filler paragraphs
are neutral. What blocks: a check of the gate read-1a that the new tiers
make fail (D2), one read-back that cannot tell agreement from abstention
(D3), and a sentence of the natural SAP that contradicts what the protocol
states (D4).

## How the review was done

- Windows git for the diff and the history, always with `git -C
  D:\trial_work\specfirst-gen` or `git show <commit>:<path>`. Nothing was
  read, listed or searched outside the worktree, my scratch folder and
  `/root/scratch-gen3a/` of the WSL machine (the author's scratch: read,
  never written). `reference/` was not touched.
- No heavy command: no test suite, no gate, no kit written, no build, no
  CORE run. Every probe below calls pure functions of the commit (parsers,
  `control_records`, `reading.score`, `token_groups`, `slot_problems`) on
  files that exist, in one process, under WSL with `scripts/env.sh`. So
  none took the lock. The unit tests and the gate checks are taken from
  the author's clean-clone log of `a315689`, quoted below.
- No file of the repository was changed but this one. Nothing committed.
  My scripts (`r1.py` to `r4.py`) are in my scratch folder and are not
  kept; each is described where its output is quoted.

## What I read

- `CLAUDE.md`; `PLAN.md` sections 2.2, 2.3, 4.3 to 4.5, 6.4 to 6.7, 8, 9.1
  to 9.5, 11.1 to 11.3, 13.5 and 13.6; `ADR-005` (decision 1); `ADR-009`
  (all); `ADR-004` decision 2 and the schema points; `ADR-007` decisions 6
  to 10; `ADR-008` (all); `docs/state/gen.md`, `docs/state/read.md`;
  `docs/lessons.md` lessons 28, 39, 46, 47, 53 to 57.
- In full: `src/specfirst/gen/natural.py`, `documents.py`, `gate3.py`; the
  diffs of `gates.py`, `gen/kits.py`, `gen/decisions.py`, `gen/command.py`,
  `gen/gate2.py`, `score/scorer.py`, `score/kit.py`, `score/defects.py`,
  `scripts/clean_clone_gate.sh`; `score/reading.py` (score, effective,
  Documents); `score/command.py` (the call of `scorer.run`);
  `tests/unit/test_gen_natural.py` and the diff of `test_score_kit.py`.
- The store: all of `paragraphs.jsonl` (61 records, every attempt), all of
  `filler.jsonl` (10), `calls.jsonl`, the four call files and the README.
- The 22 statement templates of the slice in `standard/catalog/entries/`.
- The author's logs: `/root/scratch-gen3a/gate3_dev.log` (dev run) and
  `build/gates/gen-3a/clean-clone.log` (clean clone of `a315689`); the
  author's dev kits `/root/scratch-gen3a/kits0/kit-001` to `kit-010`.
  These kits were written before the store was filled (their paragraphs
  are phrasing templates, marked `missing`), so I used them only for what
  ADR-009 decision 10 says does not change with the store: the decision
  vectors, the tiers, the statuses and the citations of the standard form.
  Their study IDs are those of the clean-clone log (sfpbt5zj, sfmyncmq,
  ...).

## What I ran, with the key output

A. The scope of the change.

```text
$ git diff --stat b5ccb77 a315689 -- PLAN.md standard/ env/ third_party/
(no output: nothing changed there)
$ git show a315689:CLAUDE.md | wc -l
59
```

B. The clean-clone gate on `a315689` (`build/gates/gen-3a/clean-clone.log`,
the author's run; summary and the lines of the checks).

```text
FAILED tests/unit/test_score_kit.py::test_the_parser_control_scores_100_percent_on_the_kit
       (assert (20, 20) == (22, 22): quote and span of the two asked decisions)
FAILED tests/unit/test_score_kit.py::test_no_planted_defect_fails_on_the_kit_and_the_matrix_agrees
       (AssertionError: S12-span: 'not planted' == 'passed')
2 failed, 1048 passed, 23 deselected in 349.31s
planted defect in kit 1: the standard-form SAP without the statement of trt.planned.source: the check reports it
planted defect in kit 1: the standard-form SAP states the other rounding rule: the check reports it
planted defect in kit 1: the variable name DM.ARM taken out of the paragraph of trt.planned.source: the check reports it
planted defect in kit 1: the numbers 65 and 80 exchanged in the paragraph of demo.age.groups: the check reports it: ... '80' is out of the order of the statement
planted defect in kit 1: the store says the verifier read the paragraph of tfl.rounding.rule as half_even: the check reports it
planted defect in kit 1: the store has no read-back of the paragraph of tfl.rounding.rule: the check reports it
planted defect in kit 1: the filler paragraph sap#8/p1 is not the text the store read back: the check reports it
the store: 61 statements, 61 accepted, 0 of them by the phrasing template; 10 filler paragraphs; 2 model calls
planted defect in kit 1: the paragraph sap#6/p1 of demo.age.groups with 80 changed to 85: the check reports it: ... '80' stands 1 times in the paragraph, the statement has it 2 times
planted defect in kit 1: the same rewrite, held against the read-back: the check reports it: ... no read-back of this text in the store
planted defect in kit 4: a kit of the ask demo whose oracle answers nothing: the check reports it
planted defect in kit 1: a kit of the tier full that leaves one house default to the house standard: the check reports it
planted defect in kit 2: the natural citation of trt.planned.source names the next paragraph: the check reports it
planted defect in kit 2: the paragraph of trt.planned.source changed after natural.json was written: the check reports it
planted defect in kit 1: kit.yaml lists ae_on_first_dose_date_without_time as visible: the check reports it
planted defect in kit 1: the log and kit.yaml claim ae_on_first_dose_date_without_time for the visible data: the check reports it: ... KeyError: 'SFPBT5ZJ-101-060'
planted defect in kit 1: the summary without the line of trt.planned.source: the check reports it
planted defect in kit 1: the summary 30 lines longer: the check reports it
[every kit, every check: 0 problems; kit 1 (full): 29 of 29 decisions recovered ...]
ASCII check: 479 files checked, 0 with non-ASCII bytes
FAIL unit tests; PASS kits, parser, slots, read-back, bad rewrite, tiers, anchors, visible probes, summary
GATE gen-3a: FAIL
```

C. The store against its call files (Python on the Windows side, reading
the committed files only).

```text
sha256 of the four call files = request_sha256 / answer_sha256 of calls.jsonl: equal (4 of 4)
rewrite-1: answer keys == request keys == store keys (61); every attempt text and filler text = the answer: bad 0
readback-1: every store pick = the answer's pick for item_of(entry, text); every item's paragraph = the attempt text: bad 0 of 61
readback-1 filler answers: every 'states' is []
picks equal to 'none' or '(none)': [{'item': 'rc04e6216ef90', 'pick': 'none'}]
  -> NONE item -> tfl.columns.total {'rule': 'none'} The adverse event summary table will not include a total column.
readback-1.request.json rules[0]: "... If the paragraph states none of them, or more than one, answer 'none'."
```

D. `r1.py`: the statuses of the ten dev kits against the house defaults,
and the first stated decision of the slice of each kit (the decision that
check 2 of `specfirst.score.kit.planted` takes out). Cut to what matters.

```text
kit-001 full:  first stated in slice: trt.planned.source equals house default: True  doc sap-standard
kit-002 standard: first stated in slice: trt.planned.source equals house default: False
kit-003 full:  first stated in slice: trt.planned.source equals house default: True
kit-004 ask:   pop.randomized.rule stated {"rule": "randomized_with_postbaseline", "test": "SYSBP"} (protocol; default all_randomized)
               pop.efficacy.rule asked; ae.related.values asked
kit-007 ask:   pop.safety.rule stated {"rule": "randomized_and_dosed"} (protocol; default at_least_one_dose)
kit-010 standard: pop.randomized.rule stated {"rule": "randomized_with_postbaseline", "test": "SYSBP"} (protocol)
kit-002 standard, kit-003 full: tfl.columns.total stated {"rule": "none"}
```

E. `r2.py`: check 2 of `kits.planted` (read-1a) up to the build, with the
functions the scorer uses (`scorer.control_records`, then `reading.score`
with the arguments `scorer.run` gives it; no build, so no attribution).

```text
kit-001 tier full: control reading perfect on the kit: True; taken out: trt.planned.source (house default: True); reading perfect: False; wrong by value: none; its marks: {'value': True, 'status': False, 'quote': True, 'span': False}; check 2 'ok': False
kit-002 tier standard: ... taken out: trt.planned.source (house default: False); wrong by value: ['trt.planned.source']; check 2 'ok': True
kit-003 tier full: ... (house default: True); wrong by value: none; check 2 'ok': False
kit-007 tier ask: ... (house default: False); wrong by value: ['trt.planned.source']; check 2 'ok': True
```

F. `r3.py`: rewrites that change the meaning, against `slot_problems` on
`token_groups` (the accepted-style text of each passes too).

```text
ae.related.values ['RELATED']                     PASSES <- ... when its causality is one of PROBABLY RELATED.
ae.related.values ['PROBABLY RELATED','RELATED']  PASSES <- ... one of PROBABLY RELATED, NOT RELATED.
ae.related.values ['POSSIBLE','PROBABLE']         PASSES <- ... one of possible, probable.
tfl.ae.summary.rows [FATAL,SERIOUS,RELATED,ANY]   PASSES <- ... the rows FATAL, SERIOUS, RELATED, in this order, without any other row.
ae.teae.end 30                                    PASSES <- ... will end 30 days after the treatment end date plus 2 days.
ae.teae.end 14                                    PASSES <- ... will end 14 working days after the treatment end date.
pop.efficacy.rule WEEK 4                          PASSES <- ... who attended the visit WEEK 4 or a later visit.
trt.planned.source ZQR5 Active, PBO Placebo       PASSES <- ... ZQR5 means Active; PBO means Active Placebo.
tfl.columns.total active_arms Placebo             PASSES <- ... other than Placebo and Low Dose.
```

G. `r4.py`: the 61 accepted paragraphs under a stricter reading than the
gate's: every token with the case of the statement, no number and no
upper-case word that the statement lacks, the statement the rendering of
the stored value, the pick the alternative.

```text
store /mnt/d/trial_work/specfirst-gen/src/specfirst/gen/rewrites 61 statements, 10 filler
accepted paragraphs with a problem of the stricter reading: 0
filler with a digit: []
all store text ASCII: True
```

H. How far the rewrites are from their statements (difflib ratio, quotes
and case aside).

```text
identical (quotes and case aside): 2  ratio>=0.9: 36  of 61
median similarity 0.919 min 0.404
```

I also read every accepted paragraph against its statement and every
filler paragraph by eye (point 7 of the brief): none changes the meaning,
none adds a rule; the filler states no decision of the slice and fits the
designs (PG-FIX is always double blind, so the filler "Interim analyses"
does not contradict a design). Two paragraphs are the statement word for
word (`trt.planned.source` dm_arm, `trt.actual.source` dm_actarm).

## Findings

### D1. `a315689` fails its own gate on a clean clone (blocks; settled by `b55db77` when its gate passes)

What is wrong: kit 7 of a set is now a kit of the ask demo. Two tests of
`tests/unit/test_score_kit.py` fail on it: the test counted every decision
of the scope on quote and span (the two asked decisions are `study_input`
and are not scored there), and the plant S12-span looked for a second
decision only in the document of the first cited decision, which in that
kit is the protocol with one stated decision.

Evidence: B. `GATE gen-3a: FAIL`, `2 failed, 1048 passed`.

`b55db77`: `_span` now takes the first decision that shares its document
with another (a `for ... else` over `_cited`); the test counts the asked
decisions apart and asks that the asks are exact. I read both; they are
right. The plant is still what ADR-008 decision 7 says (a citation that
names the anchor of another decision, quote unchanged).

What settles it: the clean-clone log of gen-3a on `b55db77` with `GATE
gen-3a: PASS`. It was running when I finished.

### D2. Read-1a's check "a document without one statement" cannot fail on a kit of the tier full (blocks)

What is wrong: the gate read-1a scores the ten kits of the gate seed and
runs `kits.planted` on the first kit that passes
(`score/kit.py:720`). Its check 2 takes out the standard-form statement of
the first stated decision of the slice and asks that the control is not
100% and that this decision is wrong by value
(`score/kit.py:655-663`, `ok = not result.perfect and stated["id"] in
wrong`). In a kit of the tier full every decision is stated, house
defaults included. When the decision taken out has the house default as
its value, the control leaves it out (`control_records` adds a default only
for gold records with the status `default`, `scorer.py:248`), the reading
score lets the house default stand in for it (`reading.effective`), and the
value is right. The control is then not 100% (status and span are wrong),
but the decision is not in `wrong()`, and the check prints "the control
fails: NO".

Evidence: D and E. Kit 1 of the gate set is full; its first stated
decision of the slice is `trt.planned.source` = `dm_arm`, the house
default; E computes `ok` False on kit 1 and on kit 3, True on kits 2 and 7.
Unless kit 1 fails `score_kit` for another reason, kit 1 is the kit the
gate read-1a plants in, and `kits_scored.score_set` returns False. The unit
test of this check (`test_the_checks_of_a_kit_fail_on_their_planted_defects`)
runs on kit 7 (ask), where the decision differs from the default, so the
unit tests do not see it. Neither commit touches this check. I did not run
the gate read-1a (it holds the lock for most of an hour and was queued).

Why it blocks: "The gates gen-2a and read-1a must still pass." The check
also no longer says what it is for on half the kits: in a full kit, a
reader that drops a statement whose value is the default is wrong in status
and citation, not in value.

What would settle it: the plant takes a stated decision whose value
differs from the house default or that has none (for example
`ae.related.values`, stated in every full and standard kit), or the check
accepts a decision that is wrong in any scored dimension; then the
clean-clone log of read-1a on the commit that does it, with "the control
fails: yes" on the planted document. If the log of read-1a on `b55db77`
shows the check passing, write down which kit it planted in; the check is
still blind on kits 1 and 3.

### D3. One recorded read-back cannot tell agreement from abstention (blocks)

What is wrong: the verifier of `readback-1` was told: "If the paragraph
states none of them, or more than one, answer 'none'." The catalog has an
alternative with the ID `none` (`tfl.columns.total`). For the paragraph
"The adverse event summary table will not include a total column." (store
key `5875cc9d5d85dbf2`, item `rc04e6216ef90`) the verifier answered
`none`, and the store records it as agreeing with the alternative `none`.
Lesson 57 names this exactly ("An abstention on the same paragraph would
have been read as agreement") and changes the marker to `(none)`
(`natural.py:62`) for later calls; the one read-back made under the old
rule was not made again. That it "meant the alternative" rests on the
meaning of the paragraph, not on the verifier's answer: the transcript is
not kept and the answer file holds the pick only.

Evidence: C. Kits 2 and 3 of the gate set state `tfl.columns.total` =
`none` (D); for them the read-back check passes on this record.

Why it blocks: for this paragraph the read-back check could not fail:
either thing the verifier could have meant is recorded as a pass. The gate
text asks that every natural document passes the read-back check.

What would settle it: one new read-back of that paragraph under the
`(none)` rule, recorded in the store with its call (the loop has no step
for it: `propose` ignores an accepted record, and an attempt holds one
read-back; a list of read-backs per attempt, or a new attempt with the
same text, would do, and `paragraph_problems` already takes any agreeing
read-back of the same text). Or the owner accepts the record as it is.

### D4. The natural SAP contradicts the protocol in kits of the tiers standard and ask (blocks)

What is wrong: the introduction of the natural SAP is a design paragraph
written by `sap_paragraphs` (`documents.py:239-246`). In the tiers standard
and ask it says: "Where this plan states no convention, the house standard
open-default@1 applies." The decisions of the analysis sets and of related
events are stated in the protocol, not in the SAP (ADR-009 decision 2).
Where the protocol states an analysis set rule that differs from the house
default, the SAP read as written gives the house default for it: two
documents of the kit say two things. In the tier full it says "This plan
states every convention that the analyses follow.", which is not true of
the SAP either (the protocol holds the analysis sets and the related
values), though it contradicts no value.

Evidence: D. Kit 4 (ask): the protocol states the randomized set as every
randomized subject with a post-baseline value of SYSBP; the house default
is every randomized subject; the SAP states no convention for it. The same
for `pop.randomized.rule` in kit 10 (standard) and `pop.safety.rule` in
kit 7 (ask). The natural texts of kit 4 (`/root/scratch-gen3a/kits0/
kit-004/inputs/docs/sap.md`, `[1/p1]`) show the sentence; the design
paragraphs do not depend on the store, so the commit writes the same.
Design paragraphs are not read back by the verifier and are checked only
against `design_paragraphs` and `sap_paragraphs` themselves (`layout`),
so no check of the gate can see this.

Why it blocks: M1 documents are not to contradict each other (section
6.6; contradictions are M2), and section 4.5 sends documents that
contradict each other to a person before any class is given. A reader
that reports `conflict` for these decisions, or takes the house default,
follows the documents and is scored wrong against a gold of `stated`. The
gold of three of the ten kits rests on reading past a sentence of the kit.

What would settle it: words that cover both documents, for example
"Where neither this plan nor the protocol states a convention, the house
standard ... applies." and "This plan and the protocol state every
convention ...", a new `GENERATOR`, and the three gates again on a clean
clone.

### D5. The slot check lets meaning changes through (does not block)

What is wrong: `slot_problems` lower-cases the paragraph and finds each
token as a whole word anywhere after the previous token of its group
(`natural.py:261-312`). A value can therefore be "found" in an ordinary
word ("related to study treatment" holds the value RELATED; "without any
other row" holds the row ANY), the case of a value that the data compare
exactly is not kept, and nothing is asked of what the paragraph adds: a
number, a value, a word inside a value. The read-back cannot help where
the meaning is in a slot value: the verifier is told that "values in angle
brackets may be any value", and `ae.related.values` has one alternative.

Evidence: F, nine rewrites that change the meaning and pass. G: all 61
accepted paragraphs pass the stricter reading, so no kit of the gate is
wrong. The grouping of lesson 56 is sound for the slice: no alternative of
the slice has two numeric slots, so no exchange of numbers between groups
can go unseen; the order inside a group is kept (the gate's plant 65/80
and the unit tests show it).

What would settle it (before rewrites that move further from the standard
form, full gen-3): match the scalars of text slots with their case;
consume each match so that one word serves one token; refuse a number, a
quoted or upper-case value that the statement lacks; plant the cases of F
in the unit tests.

### D6. Rule R4 and R3: what a kit is made from is not named, and the gates read the environment (does not block)

What is wrong: the store is chosen by `SPECFIRST_REWRITES`
(`natural.py:100-103`). `documents.write` (via `kits._attempt`, no store
given), `documents.problems`, `gate3.readback` (`gate3.py:274`) and the gen
and score gates that write kits all read it; `generate_apart` passes the
environment on. Only `scripts/clean_clone_gate.sh` unsets it. The handover
asks to set it for dev and test kits, so a `specfirst gate gen-3a` (or
gen-2a, read-1a) in such a shell writes and judges the gate's kits from
another store. A kit names the SHA-256 of every paragraph it used
(`natural.json`), but not the store: `kit.yaml` has no pin of it, and the
filler of every kit is drawn from all accepted filler
(`documents.py:293`, `sample`), so one filler paragraph added to the
append-only store changes the bytes of every kit with the same
`GENERATOR`, against the rule of the handover ("Change GENERATOR with any
change that gives other bytes").

What would settle it: the gates pass `natural.STORE` explicitly (or refuse
to run with the variable set); `kit.yaml` pins the SHA-256 of the store's
files (or of the filler population and the texts used).

### D7. The loop writes the statements of any kit into the repository (does not block)

What is wrong: `specfirst gen natural requests|propose --kits DIR` writes
into `natural.Store.load()` (`gen/command.py:236`), the repository's store
unless `SPECFIRST_REWRITES` is set. Nothing checks the split of the kits
or where the store is. Run on dev, test or sealed kits without the
variable, it puts their decision vectors (the statements) into a tracked
file; section 8 makes them secrets. The seed file has such a guard; the
store has a sentence in ADR-009 decision 5. Also: kits 5 to 10 of the gate
set carry the splits dev and test while their statements are now in the
repository verbatim (they could be derived from the committed seed before;
nothing new leaks), and the store maps every natural paragraph of every
kit that uses it back to its statement.

What would settle it: refuse `requests`/`propose` for a kit whose split is
not train when the store lies inside a checkout (the gate seed being the
one stated exception); in read-2a, deny the store to the reader and put
it under the canary scan (section 11.2); never score on kits 5 to 10 of
the gate seed as dev or test kits.

### D8. `scorer.run` counts a candidate's own `asked` status as asked by default (does not block)

What is wrong: `scorer.run(..., asked=None)` now fills `asked` from the
records with the status `asked` (`scorer.py:120-122`). For the arms and
the plants that is what is wanted. For a reader it would credit a value
of a `study_input` that nobody asked for (section 4.5: "as a question
asked, not as a guess").

Evidence: the command line is safe: `specfirst score kit --decisions`
always passes `ask_keys(_jsonl(args.questions), ...)`, and `_jsonl(None)`
is `[]`, so `asked` is an empty set without `--questions`. read-1a is not
weakened: no caller of `run` with a reader exists yet.

What would settle it: read-2a's harness passes the questions; better,
`run` with `arm="R"` refuses `asked=None`.

### D9. Most rewrites are the statement with one word changed (does not block)

H: 38 of the 61 accepted paragraphs are within 0.9 of their statement,
two equal to it. The read-back of such a paragraph is near trivial and the
natural form measures little robustness to wording. ADR-009 states one
rewrite per statement as a known limit; the number belongs in the report
of the part and in the reading of the first scores (read-3).

### D10. The provenance of the model text rests on the executor (does not block; see the question for the owner)

C shows that the store, the call files and `calls.jsonl` agree to the
byte, and that the read-back request holds no statement and no gold value
(the 43 statements found in it are the rule texts of alternatives without
slots, shown for every alternative alike). Nothing shows who wrote the two
answer files: the subagents' transcripts and final messages are not kept,
and the verifier was a subagent of the session that wrote the work, with
access to the store that held the statements (ADR-009, Consequences).
`tool_uses: 2` for each call is consistent with reading the request and
writing the answer, and no more.

### D11. Smaller points (do not block)

- `summary_problems` allows lines of 140 characters; ADR-009 decision 9
  says 100 (the summaries I saw keep 100).
- The gate prints the number of filler paragraphs and holds it against
  nothing: a store without filler gives kits without filler sections and
  the gate passes (section 6.6 asks for them).
- The second plant of "visible probes" is found through the path "the data
  cannot be read for this probe: KeyError" (the probe's subject is not in
  the visible data), not through a missing record of a subject that is
  there. It is a detection, on the easier case.
- The summary shows the rule of each value, not its slots (WEEK 4, 30
  days, the related values); the owner's sample at N3 reads the pairs, so
  it does not need them, but "every decision with its value" would be the
  page for people.

### D12. What I found right

- The gate checks what its text says: the parser recovers every decision
  (stated from the standard form at the cited anchor, default from the
  house, asked from the oracle) and nothing else is stated; every decision
  paragraph passes the slot check, and its exact text (by hash) has a
  recorded pick equal to the gold alternative; every filler paragraph is a
  stored text read back as stating nothing; a changed number is refused by
  the slot check, by the read-back (no read-back of that text) and by the
  loop (not sent to the verifier); `kit.yaml` lists the probes of the log
  by dataset and each visible probe is found. Each check failed on its
  plants first (B), and each plant fails for the reason it names.
- A decision paragraph cannot hide: `natural.json` must name every anchor
  of the document in order, a design paragraph must be one of the design,
  a filler paragraph one of the store, and every stated decision must have
  its paragraph, cited second.
- Tiers, statuses and classes follow section 6.6 and 4.5 (full: all
  `stated`/`document_rule`; standard: defaults cite the house; ask: the
  decisions without a house default are `asked`/`study_input`, no
  citation, in no document, answered by `gold/oracle.yaml` with the value
  and its statement), and the ask demo is in two kits (4 and 7).
- A reader's citation into the natural form can be scored: gold cites the
  natural paragraph second, and `reading.Documents.span` reads `[4.1/p2]`
  anchors as it reads the standard form's.
- No model is called by any gate, kit or check; no clock; the order of
  sections and filler is drawn from the kit's seed.
- `PLAN.md`, `standard/`, `env/`, `third_party/` unchanged; ASCII check
  clean; `CLAUDE.md` 59 lines; no seed file of a dev or test kit
  committed.

## Questions for the owner

1. The parser control now asks the oracle (`scorer.control_records`,
   ADR-009 decision 4). That changes what "the parser control scores
   100%" means in the gate of read-1a, whose reading you approved, for
   the kits of the ask demo: arm C becomes "the parser on the
   standard-form documents, the house standard and the oracle". A part
   reading another part's gate text by its own code is the case of lesson
   47. Recommendation: approve it; without it no control can score 100% on
   a kit of the ask demo, and the oracle answers only what the documents
   and the house leave open, as section 11.3 says.
2. The rewriter and the verifier are subagents of the executor's own
   session; their answers reach the store through files the executor
   hands on, and their transcripts are not kept (D10). Does that count as
   the "verifier agent with a fresh context" of section 6.6?
   Recommendation: accept it for the slice; from the next call on, keep
   each subagent's final message (or its transcript) beside its answer
   file and name its hash in `calls.jsonl`, and make the read-back of D3
   that way.

Verdict: NOT SIGNED (blocking: D1, D2, D3, D4)
