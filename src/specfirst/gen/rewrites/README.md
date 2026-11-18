# The store of model text (gen-3a)

The natural form of the documents of the kits of the gate (PLAN.md section
6.6; docs/decisions/ADR-009.md). Written by a model once, checked by
scripts, read by the generator. No gate calls a model.

| File | One line per |
| --- | --- |
| `paragraphs.jsonl` | statement: its decision, every attempt (text, the call that wrote it, the problems of the slot check, the verifier's pick and the call that read it) and the accepted attempt |
| `filler.jsonl` | neutral filler paragraph, with the verifier's answer that it states none of the decisions of the slice |
| `calls.jsonl` | model call: role, model, items, tokens, tool uses and seconds as the Agent tool reported them, the SHA-256 of the request and of the answer |

Rules:

- Append only. An accepted attempt is never changed or removed: kits name
  the SHA-256 of every paragraph they use (`gold/docs/natural.json`).
- A statement is accepted when an attempt passes the slot check and the
  verifier, a fresh context that sees the paragraph, the question and the
  alternatives but not the statement, picks its alternative. After three
  failed attempts the phrasing template of the catalog (`plain`) becomes
  the next attempt and is read back the same way.
- Only the statements of kits from a development seed belong here. The
  statements of dev, test and sealed kits go to a store outside every
  checkout (`SPECFIRST_REWRITES`).
- The text is ASCII and MIT, like the rest of the repository.

The loop, one step at a time (`specfirst gen natural --help`):

```text
specfirst gen natural requests --kits KITS --out rewrite.request.json
  (a rewriter writes rewrite.answer.json)
specfirst gen natural propose rewrite.answer.json --kits KITS --call rewrite-1 \
    --request rewrite.request.json --tokens N --tool-uses N --seconds N
specfirst gen natural readback-requests --out readback.request.json
  (a verifier, a new context, writes readback.answer.json)
specfirst gen natural readback readback.answer.json --call readback-1 \
    --request readback.request.json --tokens N --tool-uses N --seconds N
specfirst gen natural status --kits KITS
```

Then write the kits again: they take the accepted texts.
