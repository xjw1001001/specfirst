#!/usr/bin/env bash
# Create the Python environment and the R library of this checkout from the
# lock files, then run `specfirst doctor`.
#
# System packages come first (once per machine, as root): env/system.sh.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
# shellcheck disable=SC1091
. scripts/env.sh

python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else "Python 3.12 or later is required")'

echo "python environment: $SPECFIRST_VENV"
if [ ! -x "$SPECFIRST_VENV/bin/python" ]; then
  python3 -m venv "$SPECFIRST_VENV"
fi
pip_install() {
  "$SPECFIRST_VENV/bin/python" -m pip install --quiet --disable-pip-version-check --no-deps "$@"
}
# Exact versions with hashes, wheels only: nothing is resolved or built here.
pip_install --require-hashes --only-binary=:all: -r env/requirements.lock
pip_install --no-build-isolation -e .

echo "R library: $SPECFIRST_R_LIBS"
mkdir -p "$SPECFIRST_R_LIBS"
Rscript --vanilla env/install_r.R

# shellcheck disable=SC1091
. scripts/env.sh
specfirst doctor
