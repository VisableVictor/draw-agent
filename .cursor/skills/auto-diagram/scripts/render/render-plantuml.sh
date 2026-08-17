#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo "Usage: render-plantuml.sh <input.puml> [output.svg]"
  exit 2
fi

INPUT_FILE="$1"
OUTPUT_FILE="${2:-${INPUT_FILE%.*}.svg}"
OUTPUT_DIR="$(dirname "$OUTPUT_FILE")"
BASE_NAME="$(basename "$INPUT_FILE")"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: file not found: $INPUT_FILE"
  exit 2
fi

if command -v plantuml >/dev/null 2>&1; then
  plantuml -tsvg -o "$OUTPUT_DIR" "$INPUT_FILE"
  GENERATED_FILE="$OUTPUT_DIR/${BASE_NAME%.*}.svg"
elif [ -n "${PLANTUML_JAR:-}" ] && command -v java >/dev/null 2>&1; then
  java -jar "$PLANTUML_JAR" -tsvg -o "$OUTPUT_DIR" "$INPUT_FILE"
  GENERATED_FILE="$OUTPUT_DIR/${BASE_NAME%.*}.svg"
else
  echo "Error: PlantUML renderer not found. Install 'plantuml' or set PLANTUML_JAR."
  exit 3
fi

if [ "$GENERATED_FILE" != "$OUTPUT_FILE" ]; then
  mv "$GENERATED_FILE" "$OUTPUT_FILE"
fi

node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" "$OUTPUT_FILE"
node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" --verify "$OUTPUT_FILE"
echo "Rendered: $OUTPUT_FILE"
