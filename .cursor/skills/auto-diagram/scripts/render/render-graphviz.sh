#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo "Usage: render-graphviz.sh <input.dot> [output.svg]"
  exit 2
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${INPUT_FILE%.*}.svg}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: file not found: $INPUT_FILE"
  exit 2
fi

if ! command -v dot >/dev/null 2>&1; then
  echo "Error: 'dot' not found. Install Graphviz to render DOT diagrams."
  exit 3
fi

dot -Tsvg "$INPUT_FILE" -o "$OUTPUT_FILE"
node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" "$OUTPUT_FILE"
node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" --verify "$OUTPUT_FILE"
echo "Rendered: $OUTPUT_FILE"
