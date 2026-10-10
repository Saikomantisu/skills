#!/usr/bin/env bash
# Third-party skills are managed with `npx skills ... -g`. This links its
# global lock file to skill-lock.json in this repo, then installs any skill in
# it that is missing on this machine.
# Safe to rerun.
set -euo pipefail

REPO=$(cd "$(dirname "$0")/.." && pwd)
LOCK="$REPO/skill-lock.json"
# agents `npx skills` installs for (Pi reads ~/.agents/skills on its own)
AGENTS=(claude-code codex hermes-agent)

# point the `npx skills` global lock at the one in this repo
if [ -n "${XDG_STATE_HOME:-}" ]; then
  global="$XDG_STATE_HOME/skills/.skill-lock.json"
else
  global=~/.agents/.skill-lock.json
fi
if [ "$(readlink "$global" 2>/dev/null)" != "$LOCK" ]; then
  mkdir -p "$(dirname "$global")"
  if [ -e "$global" ] && [ ! -L "$global" ]; then
    mv "$global" "$global.bak" && echo "moved existing $global to $global.bak" >&2
  fi
  ln -sfn "$LOCK" "$global"
fi

# install skills from the lock that this machine doesn't have yet
export DISABLE_TELEMETRY=1
missing=$(jq -r '.skills | to_entries[] | "\(.value.sourceUrl) \(.key)"' "$LOCK" |
  while read -r url name; do [ -e ~/.agents/skills/"$name" ] || echo "$url $name"; done)
for url in $(echo "$missing" | awk 'NF {print $1}' | sort -u); do
  names=$(echo "$missing" | awk -v u="$url" '$1 == u {print $2}' | xargs)
  echo "installing from $url: $names"
  # shellcheck disable=SC2086
  npx -y skills add "$url" -g -y -a "${AGENTS[@]}" --skill $names
done

echo "third-party: $(jq -r '.skills | keys[]' "$LOCK" | xargs)"
