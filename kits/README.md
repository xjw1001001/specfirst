# Kits

One folder per kit (PLAN.md section 8).

- A kit of real data or real documents (tiers B and C) is a manifest only:
  `kit.yaml` and a README. Its files stay in the fetch cache and are
  assembled into `build/kits/<id>/` by `specfirst kit assemble <id>`, each
  checked against its pinned SHA-256. `cdiscpilot01` is the first.
- Small generated fixtures (tier A) may be committed here with their data.
  There is none yet.

A test and the gate of real-1 fail when study data or a study document
appears in git (`specfirst.kit.tracked_data_problems`).
