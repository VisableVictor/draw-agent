#!/usr/bin/env python3
"""Soft visual-hierarchy checks for auto-diagram SVGs.

Reports:
- WARNING: likely hierarchy / readability issues
- DESIGN_HINT: softer suggestions for emphasis and narrative clarity

It exits non-zero only for usage / parse failures unless
AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING=1 is set and warnings are found.
"""

from __future__ import annotations

import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from svg_quality_lib import classes_of, collect_nodes, parse_path_endpoints


def collect_edge_directions(root: ET.Element) -> list[tuple[str, float, float]]:
    directions: list[tuple[str, float, float]] = []
    for el in root.iter():
        if not el.tag.endswith("path") or "ad-edge" not in classes_of(el):
            continue

        parsed = parse_path_endpoints(el.get("d") or "")
        if parsed is None:
            continue

        start, end = parsed
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        if abs(dx) >= abs(dy):
            directions.append(("horizontal", dx, dy))
        else:
            directions.append(("vertical", dx, dy))
    return directions


def coeff_of_variation(values: list[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    if mean == 0:
        return 0.0
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return math.sqrt(variance) / mean


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check-visual-hierarchy.py <svg-file>")
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: File not found: {path}")
        return 2

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        print(f"ERROR: XML parse failed: {exc}")
        return 1

    warnings: list[str] = []
    hints: list[str] = []

    nodes = collect_nodes(root)
    core_nodes = [node for node in nodes if node.box_kind == "node"]
    annotation_nodes = [
        node for node in nodes if node.box_kind == "annotation" or node.role == "annotation"
    ]

    if not any(node.role for node in nodes):
        hints.append(
            "No data-role metadata found; add data-role='primary|secondary|support|annotation' for stronger hierarchy validation."
        )
    if not any(node.flow_level for node in nodes):
        hints.append(
            "No data-flow-level metadata found; add data-flow-level='core|branch|aux' to validate main-path salience more accurately."
        )

    if len(core_nodes) >= 4:
        area_cv = coeff_of_variation([node.area for node in core_nodes])
        if area_cv < 0.12:
            hints.append(
                "Core nodes are visually very uniform; consider creating clearer primary vs support weight differences."
            )

    if any(node.role for node in nodes):
        primary_count = sum(1 for node in nodes if node.role == "primary")
        if primary_count > max(1, math.ceil(len(nodes) / 3)):
            warnings.append(
                f"There are {primary_count} primary nodes among {len(nodes)} nodes; too many focal points may flatten hierarchy."
            )

    if core_nodes and annotation_nodes:
        annotation_ratio = sum(node.area for node in annotation_nodes) / max(
            1.0, sum(node.area for node in core_nodes)
        )
        if annotation_ratio > 0.38:
            warnings.append(
                f"Annotation / note area is heavy ({annotation_ratio:.2f}x of core node area); supporting cards may compete with the main story."
            )
        elif annotation_ratio > 0.22:
            hints.append(
                f"Annotation / note area is noticeable ({annotation_ratio:.2f}x of core node area); check that support content does not overshadow the main path."
            )

    directions = collect_edge_directions(root)
    horizontal = [item for item in directions if item[0] == "horizontal"]
    vertical = [item for item in directions if item[0] == "vertical"]
    if len(horizontal) >= 3:
        ltr = sum(1 for _, dx, _ in horizontal if dx > 0)
        rtl = sum(1 for _, dx, _ in horizontal if dx < 0)
        if ltr > 0 and rtl > 0:
            warnings.append(
                "Horizontal edge directions are mixed; the reading path may feel indecisive left-to-right."
            )
    if len(vertical) >= 3:
        down = sum(1 for _, _, dy in vertical if dy > 0)
        up = sum(1 for _, _, dy in vertical if dy < 0)
        if down > 0 and up > 0:
            warnings.append(
                "Vertical edge directions are mixed; the reading path may feel indecisive top-to-bottom."
            )

    if core_nodes and not any(node.role == "primary" for node in nodes):
        if coeff_of_variation([node.area for node in core_nodes]) < 0.18:
            hints.append(
                "No explicit primary node is visible and box sizes are close; consider highlighting the core module or core decision layer."
            )

    print(f"Visual Hierarchy: {path}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    if hints:
        for hint in hints:
            print(f"DESIGN_HINT: {hint}")
    if not warnings and not hints:
        print("OK: Visual hierarchy checks found no obvious emphasis or narrative issues.")

    strict_mode = os.getenv("AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING") or os.getenv(
        "AUTO" + "_" + "DIAGRAM" + "_FAIL_ON_DESIGN_WARNING"
    )
    if warnings and strict_mode == "1":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
