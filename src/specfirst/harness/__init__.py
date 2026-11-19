"""The reader harness of read-2a (PLAN.md sections 11.1 to 11.3; docs/decisions/ADR-010.md).

    task       the task folder of a reading task: inputs of a kit, the standard,
               the knowledge under test, TASK.md, the two tools, an empty out/
    knowledge  the `core-reader` skill and the reading notes v0 of the units,
               rendered from the catalog; the leak check of section 11.4
    oracle     `specfirst ask`: answers from the oracle file of a kit, logged
    outputs    whether out/decisions.jsonl, questions.jsonl, unmapped.jsonl are valid
    canary     the canary strings of a run and the scan of a transcript and a workspace
    record     the run record: tokens, turns, time, dollars, the budget
    adapter    the Claude Code CLI (`claude -p`), and the stub reader that speaks its
               stream-json for tests and for the gate
    runs       a run of an arm (S, R or C) on a kit, and the check of a recorded run
    gate       `specfirst gate read-2a`
    command    `specfirst run ...` and `specfirst ask ...`

A reading task never holds gold, twins, seeds, the oracle file or the store
of model text (section 11.2). The reader works in the task folder; the
harness keeps what the reader must not see in the run folder, outside it.
"""
