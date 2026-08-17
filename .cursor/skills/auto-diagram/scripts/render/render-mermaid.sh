#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 3 ]; then
  echo "Usage: render-mermaid.sh <input.mmd> [output.svg] [background]"
  exit 2
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${INPUT_FILE%.*}.svg}"
BACKGROUND="${3:-transparent}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: file not found: $INPUT_FILE"
  exit 2
fi

if ! command -v mmdc >/dev/null 2>&1; then
  echo "Error: 'mmdc' not found. Install Mermaid CLI or provide a compatible renderer."
  exit 3
fi

mmdc -i "$INPUT_FILE" -o "$OUTPUT_FILE" -b "$BACKGROUND"
node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" "$OUTPUT_FILE"
node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" --verify "$OUTPUT_FILE"
echo "Rendered: $OUTPUT_FILE"
