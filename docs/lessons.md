# Lessons

Each failure once, with the check that now catches it (PLAN.md section 2.4).

| # | Found in | What went wrong, or would have | The check that catches it |
| --- | --- | --- | --- |
| 1 | base-0 | The machine had no WSL Linux distribution, only Docker Desktop's internal one, although the plan assumes WSL2. | `specfirst doctor` fails when Python, R or poppler is missing. The owner chose to install Ubuntu 24.04 (ADR-000). |
| 2 | base-0 | Git for Windows sets `core.autocrlf=true` system-wide. A checkout would get CRLF line endings, which breaks shell scripts and changes file hashes under Linux. | `.gitattributes` forces LF; `tests/unit/test_layout.py::test_text_files_have_lf_endings` fails on any CR in a maintained file. |
| 3 | base-0 | The `pdftotext` on the Windows path is Xpdf 4.00 from Git for Windows, not poppler. The CSR parsers were written against poppler 24.02 layout output. | `specfirst doctor` fails when `pdftotext -v` does not name poppler. Seen for real: with Xpdf's text the E27 test fails on its counts. |
| 4 | base-0 | The folder the session started in also holds `reference/` (employer material). A repository rooted there could have committed it. | The repository is a separate folder; `/reference/` is in `.gitignore`; `.claude/settings.json` denies reading it; `tests/unit/test_layout.py` checks both. |
| 5 | base-0 | The yamaa run of E1 writes `<dataset>-yamaa.parquet` into the data folder of the clone. | The E1 test works on a copy; `specfirst fetch --verify` fails when a cached source is not clean (`tests/unit/test_fetch.py::test_added_file_in_the_cache_fails`). |
