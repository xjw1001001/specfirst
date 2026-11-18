#!/usr/bin/env bash
# Run a gate the way PLAN.md section 13 asks for it: on a clean clone, with
# a fresh install and a fresh fetch.
#
# Usage: scripts/clean_clone_gate.sh <wp> [<repository> [<commit or branch>]]
#
# The default is this checkout's repository at its current HEAD commit, so
# commit first: uncommitted changes are not in the clone. The clone goes to
# a new folder under ${TMPDIR:-/tmp}. Nothing of this checkout's environment
# is reused: the Python environment, the R library and the fetch cache of
# the clone are created under the same new folder, wherever that folder is.
# The gate runs with --clean, so it fails if the clone has uncommitted
# changes. Everything printed is also written to
# build/gates/<wp>/clean-clone.log here.
set -uo pipefail

wp="${1:-}"
if [ -z "$wp" ]; then
  echo "usage: scripts/clean_clone_gate.sh <wp> [<repository> [<commit or branch>]]" >&2
  exit 2
fi
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# git in this checkout, whatever SPECFIRST_ROOT the caller has set. It also
# works in a worktree that the other operating system's git made (see
# specfirst.paths.git_env).
in_checkout() {
  (
    cd "$here" || exit 1
    eval "$(SPECFIRST_ROOT="$here" PYTHONPATH="$here/src" python3 -m specfirst.paths)" || exit 1
    git "$@"
  )
}
repository="${2:-$(in_checkout rev-parse --path-format=absolute --git-common-dir)}"
ref="${3:-$(in_checkout rev-parse HEAD)}"
if [ -z "$repository" ] || [ -z "$ref" ]; then
  echo "cannot find the repository or the commit of $here" >&2
  exit 2
fi

mkdir -p "$here/build/gates/$wp"
log="$here/build/gates/$wp/clean-clone.log"
exec > >(tee "$log") 2>&1

work="$(mktemp -d "${TMPDIR:-/tmp}/specfirst-clean-XXXXXX")"
clone="$work/specfirst"

# Nothing from the calling environment may leak into the clone.
for name in $(env | sed -n 's/^\(PIP_[A-Za-z0-9_]*\)=.*/\1/p'); do
  unset "$name"
done
unset SPECFIRST_CACHE _SPECFIRST_OWNS_CACHE SPECFIRST_VENV SPECFIRST_ROOT SPECFIRST_R_LIBS
unset SPECFIRST_CORE SPECFIRST_CORE_URL
unset R_LIBS_USER VIRTUAL_ENV PYTHONPATH PYTHONHOME GIT_DIR GIT_WORK_TREE
export SPECFIRST_HOME="$work/env"

step() {
  echo
  echo "\$ $*"
  "$@"
  local code=$?
  if [ "$code" -ne 0 ]; then
    echo "clean clone gate $wp: FAIL ('$*' exited $code; clone: $clone, which does not last)"
    exit "$code"
  fi
}

echo "clean clone gate $wp"
echo "repository: $repository"
echo "commit:     $ref"
echo "clone:      $clone"
echo "environment and cache: $SPECFIRST_HOME"
step git clone --quiet --no-local "$repository" "$clone"
step git -C "$clone" checkout --quiet --detach "$ref"
step git -C "$clone" log -1 --format='%H %s'
cd "$clone" || exit 1
step bash env/install.sh
# shellcheck disable=SC1091
. scripts/env.sh
step specfirst fetch
step specfirst gate "$wp" --clean
echo
echo "clean clone gate $wp: PASS (clone: $clone)"
echo "The clone does not last: under WSL /tmp is cleared when the instance restarts, about a"
echo "minute after the last command ends. Copy what must be kept in the same command that"
echo "runs this script (docs/lessons.md, lesson 39). The log is in build/gates/$wp/ here."
