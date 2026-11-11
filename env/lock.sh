#!/usr/bin/env bash
# Rewrite the lock files from env/requirements.in, env/r-packages.txt and
# env/apt-packages.txt. Run it on purpose only, on the reference platform
# (Ubuntu 24.04, x86_64), and commit the result.
#
#   env/requirements.lock  exact Python versions with hashes (written by uv)
#   env/r-packages.lock    exact R versions from the snapshot in env/r-repo.txt
#   env/system.lock        versions of the system packages, for information
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
# shellcheck disable=SC1091
. scripts/env.sh

tool="$(mktemp -d)"
trap 'rm -rf "$tool"' EXIT
python3 -m venv "$tool/venv"
"$tool/venv/bin/python" -m pip install --quiet --disable-pip-version-check uv
"$tool/venv/bin/uv" pip compile env/requirements.in \
  --python "$(command -v python3)" \
  --generate-hashes \
  --no-annotate \
  --custom-compile-command "bash env/lock.sh" \
  --output-file env/requirements.lock

mkdir -p "$R_LIBS_USER"
Rscript --vanilla env/install_r.R --write-lock

{
  echo "# Versions of the system packages when the locks were written (Ubuntu 24.04)."
  echo "# For information: specfirst doctor prints a note when one differs."
  grep -v '^#' env/apt-packages.txt | sort | while read -r name; do
    [ -n "$name" ] && printf '%s %s\n' "$name" "$(dpkg-query -W -f='${Version}' "$name")"
  done
} > env/system.lock
echo "locks written: env/requirements.lock env/r-packages.lock env/system.lock"
