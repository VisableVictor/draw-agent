#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: validate-graphviz.sh <input.dot>"
  exit 2
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: file not found: $INPUT_FILE"
  exit 2
fi

if ! grep -Eq '^\s*(digraph|graph)\b' "$INPUT_FILE"; then
  echo "Error: DOT file must start with 'digraph' or 'graph'."
  exit 1
fi

if command -v dot >/dev/null 2>&1; then
  dot -Tsvg "$INPUT_FILE" >/dev/null
  echo "Graphviz validation passed."
else
  echo "DOT structure looks plausible. Full validation skipped because 'dot' is not installed."
fi
