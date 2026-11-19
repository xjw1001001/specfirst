---
name: core-reader
description: The shared procedure of the reader agent. How to read a protocol and a statistical analysis plan against the decision catalog, find where each decision is stated, quote it, record it as a decision record, apply the silence rule (the house default), ask what nobody states, list what the catalog lacks, and check the output files. Read it before the reading notes of any unit.
---

# The reader's procedure (core-reader)

You turn the free text of a study's documents into decision records: one
record per catalog question, with the alternative the study chose, its
slots, where the documents say so, and how sure that is. A machine compiles
the records into analysis datasets and tables, so a record is either right
or wrong; there is no partial credit for a near value.

## 1. Read

1. Read the task file. It lists the questions to answer, as pairs of a
   catalog entry and a unit, and the files you have.
2. Read both documents of the study from start to end before you record
   anything. A decision can be stated anywhere: in the synopsis, in a
   section about the analysis sets, in a section about one table, in a
   footnote-like sentence after a design description. The protocol and the
   statistical analysis plan together are the source; neither alone.
3. Read the house standard. It states one default for every question that
   has one, each as a numbered statement.
4. For each question, read its catalog entry: the question, the
   alternatives, the statement template of each alternative and its slots,
   and the meaning of the alternative when the entry gives one. Then read the
   reading notes of its unit, when the task gives them.

## 2. Locate and quote

For each question, find the paragraph that decides it.

- A paragraph decides a question when it says which alternative holds, in
  any wording. Match on meaning, not on the words of the template: "will be
  taken to be", "is defined as", "comprises", "consists of" all state a rule.
- Note the anchor at the start of the paragraph, for example `[4.1/p2]`,
  and the document ID (`protocol` or `sap`).
- Quote words copied exactly from that paragraph: enough to show the
  decision (a clause or a sentence), never words from another paragraph.
  Do not fix spelling, case or punctuation in a quote.
- A paragraph that describes the design (the arms, the visits, the scales
  of a variable) does not decide an analysis convention by itself, but it
  gives the values a slot needs: the arm codes, the visit names, the
  causality values.

## 3. Record

Write one JSON object per line in `out/decisions.jsonl`.

- `id` and `unit`: the pair from the task.
- `value`: `{"rule": "<alternative ID>", ...}` with every slot of that
  alternative and no other key. Slot values are copied from the document as
  written: codes and labels in their case, numbers as numbers, lists in the
  order the document gives them.
- `statement`: the statement template of the alternative with its slots
  filled. It is the standard form of the decision.
- `status` and `class`:

  | The documents | The house standard | status | class | cite |
  | --- | --- | --- | --- | --- |
  | state it | (any) | `stated` | `document_rule` | the paragraph |
  | are silent | has a default | `default` | `house_default` | the house statement |
  | are silent | has no default | `asked` | `study_input` | nothing |

- `citations`: a list of `{"doc", "anchor", "quote"}`. A stated decision
  cites the paragraph that states it; a default cites the numbered statement
  of the house standard (`doc` is `house`, the anchor as `1/s3`, the quote
  is the statement).
- Never write `binds` or `identifiable`: the compiler and the machine fill
  them.
- A question that does not apply to the study (the study has nothing it
  asks about, for example no efficacy-evaluable set) gets no record.

## 4. The silence rule

When neither document states a decision, the house default holds. Silence
is not a conflict and not a reason to guess: take the default, cite the
house standard, status `default`. Do not take a default when a document
states the decision in other words; read again before you conclude that
the documents are silent. A statement in one document is not cancelled by
the other document's silence.

If the two documents state two different alternatives, record what the
statistical analysis plan states, and say so in `out/unmapped.jsonl` with
both anchors.

## 5. Ask

When the documents are silent and the house standard has no default, the
study must say. Ask once per decision:

    bin/ask "<one plain question>" --decision <entry> --unit <unit>

Then record the answer as the value, status `asked`, class `study_input`,
with no citation. Do not ask about a decision that a document states or
that has a default: every question is counted, and a question that was not
needed counts against you. Do not guess a value you could have asked for.

## 6. List what is unmapped

A paragraph that states an analysis convention which no catalog question
asks about goes into `out/unmapped.jsonl`: `{"doc", "anchor", "quote",
"note"}`, where `note` says in a few words what it decides. Design
description, background, software, quality control and plans for changes
are not conventions; leave them out. When nothing is unmapped, write an
empty file.

## 7. Check

Run `bin/check`. It prints every problem of the three files: a line that is
not JSON, a value that is not one of the entry's alternatives or lacks a
slot, a citation of an anchor that does not exist, a question you were not
asked to answer. Fix each and run it again until it prints no problem. Then
reply with the single word: done.
