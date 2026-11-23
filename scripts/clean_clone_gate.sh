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
#
# The clone with its environment and cache takes about 5 GB. When the script
# ends, whether the gate passed, failed or was stopped, the gate's own folder
# of the clone (build/gates/<wp>/: gate.log and what the gate keeps there) is
# copied to build/gates/<wp>/clone/ here, and the new folder is deleted.
# SPECFIRST_KEEP_CLONE=1 keeps it. Under WSL /tmp is cleared only when the
# instance restarts, and sessions can keep it running for days
# (docs/lessons.md, lessons 39 and 73).
set -uo pipefail

wp="${1:-}"
if [ -z "$wp" ]; then
  echo "usage: scripts/clean_clone_gate.sh <wp> [<repository> [<commit or branch>]]" >&2
  exit 2
fi
# The name becomes a folder here that the script writes and deletes in.
case "$wp" in
  .* | *[!A-Za-z0-9._-]*)
    echo "not a work package name: $wp" >&2
    exit 2
    ;;
esac
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

keep="${SPECFIRST_KEEP_CLONE:-0}"
work="$(mktemp -d "${TMPDIR:-/tmp}/specfirst-clean-XXXXXX")" || exit 2
clone="$work/specfirst"

# Runs once, however the script ends. A signal ends the script through exit,
# so that this runs then too (bash runs it after the command in progress).
finish() {
  local code=$?
  trap - EXIT
  cd "$here" || cd / || true
  if [ -d "$clone/build/gates/$wp" ]; then
    rm -rf "$here/build/gates/$wp/clone"
    if cp -r "$clone/build/gates/$wp" "$here/build/gates/$wp/clone"; then
      echo "copied: the clone's build/gates/$wp/ to build/gates/$wp/clone/ here"
    fi
  fi
  if [ "$keep" = 1 ]; then
    echo "clone kept (SPECFIRST_KEEP_CLONE=1): $work"
  else
    case "$work" in
      "${TMPDIR:-/tmp}"/specfirst-clean-??????)
        if rm -rf --one-file-system "$work"; then
          echo "clone deleted: $work"
        else
          echo "clone NOT deleted: $work"
        fi
        ;;
    esac
  fi
  exit "$code"
}
trap finish EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

# Nothing from the calling environment may leak into the clone.
for name in $(env | sed -n 's/^\(PIP_[A-Za-z0-9_]*\)=.*/\1/p'); do
  unset "$name"
done
unset SPECFIRST_CACHE _SPECFIRST_OWNS_CACHE SPECFIRST_VENV SPECFIRST_ROOT SPECFIRST_R_LIBS
unset SPECFIRST_CORE SPECFIRST_CORE_URL SPECFIRST_REWRITES
unset R_LIBS_USER VIRTUAL_ENV PYTHONPATH PYTHONHOME GIT_DIR GIT_WORK_TREE
unset SPECFIRST_KEEP_CLONE
export SPECFIRST_HOME="$work/env"

step() {
  echo
  echo "\$ $*"
  "$@"
  local code=$?
  if [ "$code" -ne 0 ]; then
    echo "clean clone gate $wp: FAIL ('$*' exited $code; clone: $clone)"
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
echo "The log is in build/gates/$wp/ here; the clone is deleted now unless"
echo "SPECFIRST_KEEP_CLONE=1 (docs/lessons.md, lesson 73)."
