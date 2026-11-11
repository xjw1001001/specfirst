#!/usr/bin/env bash
# Run a gate the way PLAN.md section 13 asks for it: on a clean clone, with
# a fresh install and a fresh fetch.
#
# Usage: scripts/clean_clone_gate.sh <wp> [<repository> [<commit or branch>]]
#
# The default is this repository at its current HEAD commit, so commit
# first: uncommitted changes are not in the clone. The clone goes to a new
# folder under ${TMPDIR:-/tmp}. Nothing of this checkout's environment is
# reused: the clone gets its own .venv, .r-lib and third_party/cache.
# Everything printed is also written to build/gates/<wp>/clean-clone.log
# here.
set -uo pipefail

wp="${1:-}"
if [ -z "$wp" ]; then
  echo "usage: scripts/clean_clone_gate.sh <wp> [<repository> [<commit or branch>]]" >&2
  exit 2
fi
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
repository="${2:-$here}"
ref="${3:-$(git -C "$here" rev-parse HEAD)}"

mkdir -p "$here/build/gates/$wp"
log="$here/build/gates/$wp/clean-clone.log"
exec > >(tee "$log") 2>&1

work="$(mktemp -d "${TMPDIR:-/tmp}/specfirst-clean-XXXXXX")"
clone="$work/specfirst"
unset SPECFIRST_HOME SPECFIRST_CACHE _SPECFIRST_OWNS_CACHE SPECFIRST_VENV SPECFIRST_ROOT
unset SPECFIRST_R_LIBS R_LIBS_USER VIRTUAL_ENV

step() {
  echo
  echo "\$ $*"
  "$@"
  local code=$?
  if [ "$code" -ne 0 ]; then
    echo "clean clone gate $wp: FAIL ('$*' exited $code; clone kept in $clone)"
    exit "$code"
  fi
}

echo "clean clone gate $wp"
echo "repository: $repository"
echo "commit:     $ref"
echo "clone:      $clone"
step git clone --quiet --no-local "$repository" "$clone"
step git -C "$clone" checkout --quiet --detach "$ref"
step git -C "$clone" log -1 --format='%H %s'
cd "$clone" || exit 1
step bash env/install.sh
# shellcheck disable=SC1091
. scripts/env.sh
step specfirst fetch
step specfirst gate "$wp"
echo
echo "clean clone gate $wp: PASS (clone kept in $clone)"
