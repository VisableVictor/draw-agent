#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: validate-mermaid.sh <input.mmd>"
  exit 2
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: file not found: $INPUT_FILE"
  exit 2
fi

if ! grep -Eq '^```mermaid|^flowchart |^sequenceDiagram|^stateDiagram|^classDiagram|^erDiagram|^gantt|^mindmap' "$INPUT_FILE"; then
  echo "Error: input does not look like Mermaid content."
  exit 1
fi

if command -v mmdc >/dev/null 2>&1; then
  TMP_OUT="$(mktemp /tmp/auto-diagram-mermaid-XXXXXX.svg)"
  trap 'rm -f "$TMP_OUT"' EXIT
  mmdc -i "$INPUT_FILE" -o "$TMP_OUT" >/dev/null 2>&1
  echo "Mermaid validation passed."
else
  echo "Mermaid syntax appears plausible. Full validation skipped because 'mmdc' is not installed."
fi
