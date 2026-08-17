#!/bin/bash
set -euo pipefail

export PYTHONDONTWRITEBYTECODE=1

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
  echo "Usage: export-diagram.sh <svg-file> [png-width]"
  exit 2
fi

SVG_FILE="$1"
PNG_WIDTH="${2:-1920}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
PNG_FILE="${SVG_FILE%.svg}.png"
RASTER_BASE="$(mktemp "${TMPDIR:-/tmp}/auto-diagram-raster-XXXXXX")"
RASTER_SVG="${RASTER_BASE}.svg"
mv "$RASTER_BASE" "$RASTER_SVG"

cleanup() {
  rm -f "$RASTER_SVG"
}

trap cleanup EXIT

if [ ! -f "$SVG_FILE" ]; then
  echo "Error: file not found: $SVG_FILE"
  exit 2
fi

node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/svg/auto-fit-svg-text.py" "$SVG_FILE"
node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" "$SVG_FILE"
node "$ROOT_DIR/scripts/svg/stabilize-svg.cjs" --verify "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/check-svg-attribution.py" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/lint-svg-diagram.py" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/check-svg-edge-clearance.py" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/check-svg-node-padding.py" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/check-svg-page-chrome.py" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/check-layout-rhythm.py" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/check-visual-hierarchy.py" "$SVG_FILE"
python3 -B "$ROOT_DIR/scripts/quality/check-svg-legend-semantics.py" "$SVG_FILE"
xmllint --noout "$SVG_FILE"
node "$ROOT_DIR/scripts/svg/materialize-css-vars.cjs" "$SVG_FILE" "$RASTER_SVG"
xmllint --noout "$RASTER_SVG"
rsvg-convert -w "$PNG_WIDTH" "$RASTER_SVG" -o "$PNG_FILE"

echo "Exported: $PNG_FILE"
echo "Manual review required: visually confirm text bounds, border clearance, arrow sizing, and presentation readability before delivery."
