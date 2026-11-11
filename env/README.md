# Environment

Linux with Python and R side by side (PLAN.md section 2.4). The reference
platform is Ubuntu 24.04 on x86_64, also under WSL2. Rule R3: everything is
pinned.

| File | What it pins | Written by |
| --- | --- | --- |
| `apt-packages.txt` | the system packages: Python 3.12, R, poppler, git, compilers | hand |
| `system.lock` | their versions when the locks were written (information) | `lock.sh` |
| `requirements.in` | the top-level Python requirements | hand |
| `requirements.lock` | every Python package: exact version and hashes | `lock.sh` (uv) |
| `r-packages.txt` | the R packages the project loads | hand |
| `r-repo.txt` | the dated CRAN snapshot they come from | hand |
| `r-packages.lock` | every R package in the project library: exact version | `lock.sh` |

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

## Not here yet

The container definition that PLAN.md section 12 lists under `env/` comes
with the container isolation of M2 (section 11.2).
