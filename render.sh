#!/usr/bin/env bash
# Renders a song: ./render.sh songs/<slug>
set -euo pipefail
cd "$(dirname "$0")"
song="${1:?Användning: ./render.sh songs/<slug>}"
voices=$(grep -E '^voice:' "$song/lyrics.yaml" 2>/dev/null | awk '{print $2}' || true)
tools/setup.sh $voices
PYTHONPATH=tools .venv/bin/python -m songcoder "$song"
