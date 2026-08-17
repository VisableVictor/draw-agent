#!/usr/bin/env python3
"""Block SVG edge segments that ride along node/group/stage borders.

This catches a common report-quality issue that basic crossing checks miss:
an arrow path may not enter a box interior, but it still visually merges with
the box/container border because a segment runs on the same x/y line for a
meaningful distance.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from svg_quality_lib import (
    RectBox,
    classes_of,
    collect_group_boxes,
    collect_nodes,
    collect_stage_boxes,
    parse_svg_path_segments,
)


TOLERANCE = 2.0
MIN_OVERLAP = 24.0


def is_edge_element(el: ET.Element) -> bool:
    return el.tag.endswith("path") and "ad-edge" in classes_of(el)


def overlap_1d(a1: float, a2: float, b1: float, b2: float) -> float:
    low = max(min(a1, a2), min(b1, b2))
    high = min(max(a1, a2), max(b1, b2))
    return max(0.0, high - low)


def collect_border_graze_errors(
    root: ET.Element,
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    targets: list[tuple[str, RectBox]] = []
    for node in collect_nodes(root):
        targets.append(("node", node))
    for group_id, box in collect_group_boxes(root).items():
        targets.append(("group", RectBox(group_id, box.x, box.y, box.width, box.height)))
    for stage_id, box in collect_stage_boxes(root).items():
        targets.append(("stage", RectBox(stage_id, box.x, box.y, box.width, box.height)))

    warned_unsupported = False

    for el in root.iter():
        if not is_edge_element(el):
            continue

        path_d = el.get("d") or ""
        segments, unsupported = parse_svg_path_segments(path_d)
        if unsupported:
            if not warned_unsupported:
                warnings.append(
                    "Some edge paths use unsupported curve commands; border-clearance checks were skipped for those paths."
                )
                warned_unsupported = True
            continue

        for start, end in segments:
            x1, y1 = start
            x2, y2 = end

            if abs(y1 - y2) < 1e-6:
                y = y1
                for target_kind, box in targets:
                    for side_name, side_y in (("top", box.y), ("bottom", box.bottom)):
                        if abs(y - side_y) > TOLERANCE:
                            continue
                        overlap = overlap_1d(x1, x2, box.x, box.right)
                        if overlap >= MIN_OVERLAP:
                            errors.append(
                                f"Edge segment hugs {target_kind} '{box.node_id}' {side_name} border for {overlap:.1f}px; reroute with visible clearance."
                            )
            elif abs(x1 - x2) < 1e-6:
                x = x1
                for target_kind, box in targets:
                    for side_name, side_x in (("left", box.x), ("right", box.right)):
                        if abs(x - side_x) > TOLERANCE:
                            continue
                        overlap = overlap_1d(y1, y2, box.y, box.bottom)
                        if overlap >= MIN_OVERLAP:
                            errors.append(
                                f"Edge segment hugs {target_kind} '{box.node_id}' {side_name} border for {overlap:.1f}px; reroute with visible clearance."
                            )

    return list(dict.fromkeys(errors)), list(dict.fromkeys(warnings))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check-svg-edge-clearance.py <svg-file>")
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

    errors, warnings = collect_border_graze_errors(root)

    print(f"Edge Clearance: {path}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    if not errors and not warnings:
        print("OK: Edge clearance check found no border-grazing segments.")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
