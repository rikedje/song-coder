#!/usr/bin/env bash
# Regenerates cover + ID3 tags for already rendered songs, without re-rendering audio.
# ./tag.sh songs/<slug> [songs/<slug> ...]   (no arguments = all songs)
set -euo pipefail
cd "$(dirname "$0")"
tools/setup.sh
songs=("$@")
[ ${#songs[@]} -gt 0 ] || songs=(songs/*/)
for s in "${songs[@]}"; do
  PYTHONPATH=tools .venv/bin/python -m songcoder --tags "${s%/}"
done
