#!/bin/bash
# The four ways scripts/clean_clone_gate.sh ends, and finding N2 of base-0.
# Run from the base checkout under the heavy lock. Logs go to $out.
set -u
cd /mnt/d/trial_work/specfirst || exit 1
out=/root/scratch/clone-cleanup
rm -rf "$out"; mkdir -p "$out"
s=scripts/clean_clone_gate.sh
clones() { ls -d /tmp/specfirst-clean-* 2>/dev/null | wc -l; }
from_log() { sed -n 's#^clone: *\(/tmp/specfirst-clean-[A-Za-z0-9]*\)/specfirst$#\1#p' "$1" | head -1; }
gone() { if [ -e "$1" ]; then echo "folder still there: $1"; else echo "folder gone: $1"; fi; }

echo "== commit: $(git log -1 --format='%h %s' 2>/dev/null || echo '(git log not available under WSL here)')"
echo "== T0 syntax"
bash -n "$s" && echo "bash -n: ok"
if command -v shellcheck >/dev/null; then shellcheck "$s" && echo "shellcheck: ok"; else echo "shellcheck: not installed"; fi

echo; echo "== T1 a name that is not a plain folder name"
bash "$s" '../x'; echo "exit $?"
bash "$s" '.hidden'; echo "exit $?"

echo; echo "== T2 FAIL (a commit that does not exist); clones before: $(clones)"
bash "$s" clone-test-fail "" no-such-commit > /dev/null 2>&1; echo "exit $?"
cp build/gates/clone-test-fail/clean-clone.log "$out/T2-fail.log"
tail -3 "$out/T2-fail.log"; gone "$(from_log "$out/T2-fail.log")"; echo "clones after: $(clones)"

echo; echo "== T3 FAIL with SPECFIRST_KEEP_CLONE=1; clones before: $(clones)"
SPECFIRST_KEEP_CLONE=1 bash "$s" clone-test-keep "" no-such-commit > /dev/null 2>&1; echo "exit $?"
cp build/gates/clone-test-keep/clean-clone.log "$out/T3-keep.log"
tail -2 "$out/T3-keep.log"; kept="$(from_log "$out/T3-keep.log")"
if [ -d "$kept" ]; then echo "folder kept: $kept"; rm -rf "$kept"; echo "removed by this test"; else echo "folder missing: $kept"; fi
echo "clones after: $(clones)"

echo; echo "== T4 TERM while a step runs; clones before: $(clones)"
bash "$s" clone-test-term > /dev/null 2>&1 &
pid=$!
log=build/gates/clone-test-term/clean-clone.log
for _ in $(seq 1 60); do [ -n "$(from_log "$log" 2>/dev/null)" ] && break; sleep 1; done
sleep 3
echo "sending TERM to the script at: $(grep '^\$ ' "$log" | tail -1)"
kill -TERM "$pid"; wait "$pid"; echo "exit $?"
sleep 2
cp "$log" "$out/T4-term.log"
tail -2 "$out/T4-term.log"; gone "$(from_log "$out/T4-term.log")"; echo "clones after: $(clones)"

echo; echo "== T5 PASS: gate base-0, with SPECFIRST_ROOT set to another worktree (N2); clones before: $(clones)"
SPECFIRST_ROOT=/mnt/d/trial_work/specfirst-gen bash "$s" base-0 > /dev/null 2>&1; echo "exit $?"
sleep 2
cp build/gates/base-0/clean-clone.log "$out/T5-pass.log"
grep -E '^(repository|commit):' "$out/T5-pass.log"
tail -5 "$out/T5-pass.log"; gone "$(from_log "$out/T5-pass.log")"
ls build/gates/base-0/clone/
echo "clones after: $(clones)"
rm -rf build/gates/clone-test-fail build/gates/clone-test-keep build/gates/clone-test-term
echo "== done"
