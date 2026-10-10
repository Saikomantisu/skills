#!/usr/bin/env bash
# Symlink every skill in this repo into each agent's global skills directory,
# and remove links that point at skills which no longer exist here.
# Each entry is a symlink into this repo, so edits are live everywhere.
# Re-run after adding, removing or renaming a skill.
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
TARGETS=(
  ~/.claude/skills
  ~/.agents/skills
  ~/.codex/skills
  ~/.pi/agent/skills
  ~/.hermes/skills
)

for target in "${TARGETS[@]}"; do
  [ -d "$target" ] || continue

  # a target that is itself a link into this repo would get links written back
  # into the working copy
  case "$(readlink -f "$target")" in
    "$REPO" | "$REPO"/*)
      echo "skip $target (it is a symlink into this repo)" >&2
      continue
      ;;
  esac

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
