#!/usr/bin/env bash
# Installs the offline toolchain into the repo: .venv (uv) and Piper voice models.
set -euo pipefail
cd "$(dirname "$0")/.."
UV_PYTHON_PREFERENCE=only-managed uv sync --python 3.12 --quiet
for v in "$@"; do
  [ -f "voices/$v.onnx" ] || .venv/bin/python -m piper.download_voices --download-dir voices "$v"
done
