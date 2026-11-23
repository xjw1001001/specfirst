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
# ends, whether the gate passed, failed or was stopped by HUP, INT or TERM
# (sent to the script or to its process group), the gate's own folder of the
# clone (build/gates/<wp>/: gate.log and what the gate keeps there) is copied
# to build/gates/<wp>/clone/ here, and the new folder is deleted.
# SPECFIRST_KEEP_CLONE=1 keeps it. A signal sent to the script alone acts
# after the step in progress, which can be the whole gate. KILL, or the end
# of the WSL instance, leaves the folder until /tmp is cleared at the next
# start. Under WSL that start can be days away while sessions keep the
# instance running (docs/lessons.md, lessons 39 and 73).
set -uo pipefail

wp="${1:-}"
if [ -z "$wp" ]; then
  echo "usage: scripts/clean_clone_gate.sh <wp> [<repository> [<commit or branch>]]" >&2
  exit 2
fi
# The name becomes a folder here that the script writes and deletes in, and
# the argument of `specfirst gate` (a leading - would be an option).
case "$wp" in
  .* | -* | *[!A-Za-z0-9._-]*)
    echo "not a work package name: $wp" >&2
    exit 2
    ;;
esac
here="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly wp here

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

# The folder that holds the new folder: absolute, and read once (a relative
# TMPDIR is taken from the caller's folder).
base="$(cd "${TMPDIR:-/tmp}" 2>/dev/null && pwd -P)" || {
  echo "cannot use the folder ${TMPDIR:-/tmp}" >&2
  exit 2
}
readonly base

mkdir -p "$here/build/gates/$wp"
rm -rf "$here/build/gates/$wp/clone"
log="$here/build/gates/$wp/clean-clone.log"
# tee ignores the signals that stop the script, and with -p it keeps writing
# the log when the caller's output closes: the lines of finish reach the log.
exec > >(trap '' HUP INT TERM; exec tee -p "$log") 2>&1
teepid=$!
readonly teepid

keep="${SPECFIRST_KEEP_CLONE:-0}"
readonly keep
work=""
clone=""

# Runs once, however the script ends. A signal ends the script through exit,
# so that this runs then too: bash runs it after the command in progress.
# A second signal is ignored while it runs.
finish() {
  local code=$?
  trap '' HUP INT TERM PIPE
  trap - EXIT
  cd "$here" || cd / || true
  if [ -n "$clone" ] && [ -d "$clone/build/gates/$wp" ]; then
    if cp -r "$clone/build/gates/$wp" "$here/build/gates/$wp/clone"; then
      echo "copied: the clone's build/gates/$wp/ to build/gates/$wp/clone/ here"
    fi
  fi
  if [ -z "$work" ]; then
    :
  elif [ "$keep" = 1 ]; then
    echo "clone kept (SPECFIRST_KEEP_CLONE=1): $work"
  else
    case "$work" in
      "$base"/specfirst-clean-??????)
        rm -rf --one-file-system "$work"
        if [ -e "$work" ]; then
          echo "clone NOT deleted: $work"
        else
          echo "clone deleted: $work"
        fi
        ;;
      *)
        echo "clone NOT deleted (not a folder of this script): $work"
        ;;
    esac
  fi
  # tee writes the last lines before the caller can read the log.
  exec >&- 2>&-
  wait "$teepid" 2>/dev/null
  exit "$code"
}
trap finish EXIT
trap 'exit 129' HUP
trap 'exit 130' INT
trap 'exit 143' TERM

work="$(mktemp -d "$base/specfirst-clean-XXXXXX")" || exit 2
clone="$work/specfirst"
readonly work clone

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
