#!/bin/bash
# The ways scripts/clean_clone_gate.sh ends, and finding N2 of base-0.
# Run from the base checkout under the heavy lock; nothing else may run a
# clean-clone gate meanwhile. Logs go to $out.
set -u
cd /mnt/d/trial_work/specfirst || exit 1
out=/root/scratch/clone-cleanup
rm -rf "$out"; mkdir -p "$out"
s=scripts/clean_clone_gate.sh
clones() { ls -d /tmp/specfirst-clean-* 2>/dev/null | wc -l; }
from_log() { sed -n 's#^clone: *\(/.*/specfirst-clean-[A-Za-z0-9]*\)/specfirst$#\1#p' "$1" | head -1; }
gone() { if [ -e "$1" ]; then echo "folder still there: $1"; else echo "folder gone: $1"; fi; }
wait_for() { # <log> <pattern>: wait until the log has a line with the pattern
  for _ in $(seq 1 900); do grep -q -- "$2" "$1" 2>/dev/null && return 0; sleep 1; done
  return 1
}

echo "== commit: $(git log -1 --format='%h %s' 2>/dev/null || echo '(no git log)')"
echo "== T0 syntax"
bash -n "$s" && echo "bash -n: ok"
if command -v shellcheck >/dev/null; then shellcheck "$s" && echo "shellcheck: ok"; else echo "shellcheck: not installed"; fi

echo; echo "== T1 names that are not plain folder names, and a folder that cannot be used"
for name in '../x' '.hidden' '-h'; do bash "$s" "$name"; echo "exit $?"; done
TMPDIR=/no/such/folder bash "$s" clone-test-tmp; echo "exit $?"

echo; echo "== T2 FAIL at the checkout (a commit that does not exist), with a stale clone/ from an earlier run; clones before: $(clones)"
mkdir -p build/gates/clone-test-fail/clone && echo old > build/gates/clone-test-fail/clone/gate.log
bash "$s" clone-test-fail "" no-such-commit > /dev/null 2>&1; echo "exit $?"
cp build/gates/clone-test-fail/clean-clone.log "$out/T2-fail.log"
tail -4 "$out/T2-fail.log"; gone "$(from_log "$out/T2-fail.log")"
if [ -e build/gates/clone-test-fail/clone ]; then echo "stale clone/ still there"; else echo "stale clone/ removed"; fi
echo "clones after: $(clones)"

echo; echo "== T3 FAIL with SPECFIRST_KEEP_CLONE=1; clones before: $(clones)"
SPECFIRST_KEEP_CLONE=1 bash "$s" clone-test-keep "" no-such-commit > /dev/null 2>&1; echo "exit $?"
cp build/gates/clone-test-keep/clean-clone.log "$out/T3-keep.log"
tail -2 "$out/T3-keep.log"; kept="$(from_log "$out/T3-keep.log")"
if [ -d "$kept" ]; then echo "folder kept: $kept"; rm -rf "$kept"; echo "removed by this test"; else echo "folder missing: $kept"; fi
echo "clones after: $(clones)"

echo; echo "== T4 a relative TMPDIR, FAIL at the checkout"
mkdir -p /root/scratch/reltmp
(cd /root/scratch && TMPDIR=reltmp bash /mnt/d/trial_work/specfirst/"$s" clone-test-rel "" no-such-commit > /dev/null 2>&1; echo "exit $?")
cp build/gates/clone-test-rel/clean-clone.log "$out/T4-rel.log"
grep '^clone:' "$out/T4-rel.log"; tail -1 "$out/T4-rel.log"
echo "left in /root/scratch/reltmp: $(ls /root/scratch/reltmp | wc -l)"; rmdir /root/scratch/reltmp

echo; echo "== T5 mktemp fails (TMPDIR=/proc)"
TMPDIR=/proc bash "$s" clone-test-mktemp > /dev/null 2>&1; echo "exit $?"
tail -2 build/gates/clone-test-mktemp/clean-clone.log

echo; echo "== T6 TERM to the script alone, during git clone; clones before: $(clones)"
bash "$s" clone-test-term > /dev/null 2>&1 &
pid=$!
log=build/gates/clone-test-term/clean-clone.log
wait_for "$log" '^\$ git clone'
echo "sending TERM to the script (pid) at: $(grep '^\$ ' "$log" | tail -1)"
kill -TERM "$pid"; wait "$pid"; echo "exit $?"
cp "$log" "$out/T6-term.log"
tail -2 "$out/T6-term.log"; gone "$(from_log "$out/T6-term.log")"; echo "clones after: $(clones)"

# A job started with & in a shell without job control ignores INT from the
# start, and bash cannot trap a signal ignored on entry. With job control
# (set -m) the job has its own process group and the usual dispositions, as
# a command started from a terminal has.
for sig in INT HUP; do
  echo; echo "== T7-$sig $sig to the whole process group, during the gate step of base-0; clones before: $(clones)"
  rm -f build/gates/base-0/clean-clone.log
  set -m
  bash "$s" base-0 > /dev/null 2>&1 &
  pid=$!
  set +m
  log=build/gates/base-0/clean-clone.log
  sleep 2; wait_for "$log" '^\$ specfirst gate base-0'; sleep 20
  echo "process group of the script: $(ps -o pgid= -p "$pid" | tr -d ' ') (pid $pid)"
  echo "sending $sig to the process group at: $(grep '^\$ ' "$log" | tail -1)"
  kill -"$sig" -- -"$pid"; wait "$pid"; echo "exit $?"
  cp "$log" "$out/T7-$sig.log"
  tail -3 "$out/T7-$sig.log"; gone "$(from_log "$out/T7-$sig.log")"
  ls build/gates/base-0/clone/; echo "clones after: $(clones)"
done

echo; echo "== T8 PASS of gate base-0: SPECFIRST_ROOT set to another worktree (N2), and the caller's output closed after one byte; clones before: $(clones)"
SPECFIRST_ROOT=/mnt/d/trial_work/specfirst-gen bash "$s" base-0 > >(head -c 1 > /dev/null) 2>&1; echo "exit $?"
cp build/gates/base-0/clean-clone.log "$out/T8-pass.log"
grep -E '^(repository|commit):' "$out/T8-pass.log"
tail -5 "$out/T8-pass.log"; gone "$(from_log "$out/T8-pass.log")"
ls build/gates/base-0/clone/
echo "clones after: $(clones)"
rm -rf build/gates/clone-test-fail build/gates/clone-test-keep build/gates/clone-test-term \
  build/gates/clone-test-rel build/gates/clone-test-mktemp build/gates/clone-test-tmp
echo "== done"
