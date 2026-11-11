# Kits

One folder per kit (PLAN.md section 8).

- A kit of real data or real documents (tiers B and C) is a manifest only:
  `kit.yaml` and a README. Its files stay in the fetch cache and are
  assembled into `build/kits/<id>/` by `specfirst kit assemble <id>`, each
  checked against its pinned SHA-256. `cdiscpilot01` is the first.
- Small generated fixtures (tier A) may be committed here with their data.
  There is none yet.

A test and the gate of real-1 look for study data and study documents in
git (`specfirst.kit.tracked_data_problems`). They fail on: any file other
than `kit.yaml` and `README.md` in a kit folder of tier B or C; a file with
the suffix of a data or document format (Parquet, XPT, CSV, PDF and so on);
a Define-XML or other ODM file; and a file that is byte for byte one a kit
manifest or `third_party/sources.yaml` pins, under any name. They cannot
see a document that was retyped or converted to another format.
