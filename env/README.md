# Environment

Linux with Python and R side by side (PLAN.md section 2.4). The reference
platform is Ubuntu 24.04 on x86_64, also under WSL2. Rule R3: everything is
pinned.

| File | What it pins | Written by |
| --- | --- | --- |
| `apt-packages.txt` | the system packages: Python 3.12, poppler, git, compilers | hand |
| `r-version.txt` | the exact R version, installed from CRAN's repository for Ubuntu | hand |
| `system.lock` | versions of the system packages. R and its recommended packages (`r-*`) are pins: `system.sh` installs them, `specfirst doctor` fails on a difference. The rest is information | `lock.sh` |
| `requirements.in` | the top-level Python requirements | hand |
| `requirements.lock` | every Python package: exact version and hashes | `lock.sh` (uv) |
| `r-packages.txt` | the R packages the project loads | hand |
| `r-repo.txt` | the dated CRAN snapshot they come from | hand |
| `r-packages.lock` | every R package in the project library: exact version | `lock.sh` |

R's base and recommended packages (Matrix, MASS, mgcv and the like) come
with the pinned R. Everything else is in the project library, and the R
scripts load from those two places only, never from a personal library.

## Install

```bash
sudo bash env/system.sh    # once per machine
make install               # env/install.sh: virtual environment and R library, then specfirst doctor
```

`install.sh` installs exactly what the locks list: Python wheels with
`--require-hashes`, R packages from the dated snapshot, and it stops when
the result differs from a lock. `specfirst doctor` repeats that comparison
at any time.

## Where things go

`scripts/env.sh` decides. By default everything is inside the checkout:
`.venv`, `.r-lib` and `third_party/cache`, all ignored by git. With
`SPECFIRST_HOME` set, or when the checkout is on a Windows drive under WSL,
they go to `$SPECFIRST_HOME` (default `~/.local/share/specfirst`): one
virtual environment per checkout, one R library and one fetch cache shared
by all checkouts and worktrees.

## Changing the environment

Edit `requirements.in`, `r-packages.txt` or `r-repo.txt`, run `make lock`
on the reference platform, run `make install` and the gate, and commit the
new locks with the change that needs them.

For another R version, or newer builds of R's recommended packages: edit
`r-version.txt`, run `sudo SPECFIRST_RELOCK=1 bash env/system.sh`, then
`make lock` as above. Without `SPECFIRST_RELOCK=1`, `system.sh` installs
exactly the `r-cran-*` versions of `system.lock`.

An install never resolves versions by itself: `install_r.R` stops when
`r-packages.lock` is missing, and pip installs with `--require-hashes`.

## Not here yet

The container definition that PLAN.md section 12 lists under `env/` comes
with the container isolation of M2 (section 11.2).
