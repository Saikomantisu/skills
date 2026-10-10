#!/usr/bin/env bash
# Set up every skill on this machine: link the ones in this repo, then install
# the third-party ones recorded in skill-lock.json.
set -euo pipefail

DIR=$(cd "$(dirname "$0")" && pwd)
"$DIR/link-skills.sh"
"$DIR/install-third-party.sh"
