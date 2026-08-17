#!/bin/bash
set -euo pipefail

if [ $# -ne 1 ]; then
  echo "Usage: validate-plantuml.sh <input.puml>"
  exit 2
fi

INPUT_FILE="$1"

if [ ! -f "$INPUT_FILE" ]; then
  echo "Error: file not found: $INPUT_FILE"
  exit 2
fi

if ! grep -q '@startuml' "$INPUT_FILE" || ! grep -q '@enduml' "$INPUT_FILE"; then
  echo "Error: PlantUML file must contain @startuml and @enduml."
  exit 1
fi

if command -v plantuml >/dev/null 2>&1; then
  plantuml -checkonly "$INPUT_FILE"
  echo "PlantUML validation passed."
elif [ -n "${PLANTUML_JAR:-}" ] && command -v java >/dev/null 2>&1; then
  java -jar "$PLANTUML_JAR" -checkonly "$INPUT_FILE"
  echo "PlantUML validation passed."
else
  echo "PlantUML markers are present. Full validation skipped because no renderer is installed."
fi
