# Which causality values count as related to study treatment? (`ae.related.values`)

The list decides which events count as related, as in the related row of the adverse event
summary table. An event whose causality value is not in the list is not related.

## Where it is stated

- SAP: adverse event section, definition of a treatment-related or drug-related event.
- Protocol: adverse event section, the causality (relationship) categories the investigator
  chooses from; the case report form shows the exact values.
- The scale differs from study to study, so it must be read from the documents.

## Words to look for

- `stated_list`: "related events are those assessed as possibly, probably or definitely
  related", "events with a relationship of related", "related includes ...". The slot
  `values` is the list of collected causality values that count, as the study collects them.
- A protocol written to ICH M11 says "participant" for subject and "study intervention" for
  study treatment; read them as the same words.

## Traps

- Values are compared exactly with the collected causality. Use the wording of the collected
  scale (for example POSSIBLE, not "possibly related") when the documents show it; if only
  the prose form is given, say so in the answer.
- Many SAPs count an event with missing causality as related. A list of values cannot
  express that; report the sentence with the answer.
- "Unlikely related" is the usual boundary case. Include it only if the text does.
- A two-level scale (related, not related) still needs the list; it then has one value.
- Silent documents: this entry has no house default. Do not guess from the scale;
  a person must be asked.
