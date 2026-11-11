#!/usr/bin/env bash
# Create the git worktree of a track: the sibling folder <repo>-<track> on
# branch track/<track> (PLAN.md section 2.4). The worktree shares the fetch
# cache of the main checkout.
#
# Usage: scripts/worktree.sh <base|real|std|gen|read>
#
# Always use the same git for a checkout and its worktrees (see CLAUDE.md):
# a worktree made by Windows git records Windows paths, one made by Linux
# git records Linux paths, and neither can use the other's.
set -euo pipefail

track="${1:-}"
case "$track" in
  base|real|std|gen|read) ;;
  *) echo "usage: scripts/worktree.sh <base|real|std|gen|read>" >&2; exit 2 ;;
esac

main="$(git worktree list --porcelain | sed -n '1s/^worktree //p')"
name="$(basename "$main")"
dest="$(dirname "$main")/$name-$track"
branch="track/$track"

if [ -e "$dest" ]; then
  echo "already there: $dest"
  exit 0
fi
if git show-ref --verify --quiet "refs/heads/$branch"; then
  git worktree add "$dest" "$branch"
else
  git worktree add -b "$branch" "$dest" main
fi
mkdir -p "$dest/third_party"
printf '%s\n' "../../$name/third_party/cache" > "$dest/third_party/cache-location"
echo "worktree: $dest on branch $branch"
echo "next: cd $dest && make install"
