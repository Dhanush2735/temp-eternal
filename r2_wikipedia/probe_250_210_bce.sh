#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT="$(python3 "$ROOT/r2_wikipedia/probe_script_archive.py" "$(basename "$0")")"
eval "$SCRIPT"
