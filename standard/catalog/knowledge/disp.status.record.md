# Which record gives the end-of-study status? (`disp.status.record`)

The chosen record gives the end-of-study date and the status completed, discontinued or
ongoing. Rules that fall back on the end-of-study date use the same record.

## Where it is stated

- SAP: section on subject disposition, and definitions of study completion.
- Protocol: sections on completion, discontinuation of treatment and withdrawal from study.
- The choice of record is rarely spelled out; look for whether the study collects separate
  end-of-treatment and end-of-study forms.

## Words to look for

- `disposition_event`: one completion or discontinuation form per subject, "study completion
  status as recorded on the end-of-study page", no split between treatment and study.
- `disposition_event_by_subcategory`: separate records for end of treatment and end of
  study, "disposition is summarized separately for treatment and for study". The slot
  `subcategory` is the subcategory text of the end-of-study record, for example END OF STUDY.

## Traps

- Discontinuation of treatment is not discontinuation from the study. With both collected,
  the plain rule takes the last disposition event by sequence number, which may be either.
- Protocol milestones such as informed consent or randomization are not disposition events
  and never compete.
- Status is COMPLETED only for the term COMPLETED; any other term gives DISCONTINUED, and a
  subject with no such record is ONGOING.
- The subcategory is compared exactly. Use the text the documents or annotated forms give;
  if none is given, report that instead of inventing one.
- Silent documents: use the house default `disposition_event` and cite the house standard.
