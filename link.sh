#!/usr/bin/env bash
# Symlink every skill in this repo into each agent's global skills directory,
# and remove links that point at skills which no longer exist here.
# Safe to rerun.
set -euo pipefail

REPO=$(cd "$(dirname "$0")" && pwd)
TARGETS=(
  ~/.claude/skills
  ~/.agents/skills
  ~/.codex/skills
  ~/.pi/agent/skills
  ~/.hermes/skills
)

for target in "${TARGETS[@]}"; do
  [ -d "$target" ] || continue

  # drop stale links into this repo (renamed or deleted skills)
  for link in "$target"/*; do
    [ -L "$link" ] || continue
    dest=$(readlink "$link")
    [[ $dest == "$REPO"/* && ! -e $dest ]] && rm "$link" && echo "removed stale $link"
  done

  for skill in "$REPO"/*/SKILL.md; do
    dir=$(dirname "$skill"); name=$(basename "$dir")
    link="$target/$name"
    if [ -e "$link" ] && [ ! -L "$link" ]; then
      echo "skip $link (a real folder is already there)" >&2
      continue
    fi
    ln -sfn "$dir" "$link"
  done
done

echo "linked: $(for s in "$REPO"/*/SKILL.md; do basename "$(dirname "$s")"; done | xargs)"
