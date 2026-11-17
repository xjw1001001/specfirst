# Kits

One folder per kit (PLAN.md section 8).

- A kit of real data or real documents (tiers B and C) holds a manifest,
  `kit.yaml`, a README, and the files of our own that its manifest names:
  `gold/exceptions.yaml`, with the classified differences from the kit's
  references (PLAN.md section 4.8), and one layout per output that is built
  as a grid (PLAN.md section 7.4). The kit's
  data and documents stay in the fetch cache and are assembled into
  `build/kits/<id>/` by `specfirst kit assemble <id>`, each checked against
  its pinned SHA-256. `cdiscpilot01` is the first.
- Small generated fixtures (tier A) may be committed here with their data.
  There is none yet.
- A generated kit (tier A) is written by `specfirst gen kit` or `gen kits`
  into a folder outside the repository. Its manifest is a `kit.yaml` of
  format 1 (`specfirst.gen.kits`; docs/state/gen.md has the tree), not the
  format of a kit of real data. The seed of a dev, test or sealed kit is a
  secret, because gold can be rebuilt from it: it comes from a file outside
  every checkout, and no kit holds it.

A test and the gate of real-1 look for study data and study documents in
git (`specfirst.kit.tracked_data_problems`). They fail on: any file other
than `kit.yaml`, `README.md` and the named files of our own in a kit folder
of tier B or C; a file with
the suffix of a data or document format (Parquet, XPT, CSV, PDF and so on);
a Define-XML or other ODM file, which is an XML document whose root element
is `ODM`, in UTF-8 or UTF-16, under any name; and a file that is byte for
byte one a kit manifest or `third_party/sources.yaml` pins, under any name.
They cannot see a document that was retyped, compressed, or converted to
another format or encoding.
