#!/usr/bin/env python3
"""Lint SVG diagrams produced by auto-diagram.

Checks:
- XML parseability
- marker/id reference validity
- oversized arrowhead markers
- overlap among node and annotation boxes using auto-diagram class conventions
- unsafe micro-gutters between neighboring boxes
- explicit or inferred group/stage containment overflow
- edge labels colliding with titles, boxes, or other edge labels
- straight edge segments crossing diagram-box interiors
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from svg_quality_lib import (
    NodeBox,
    RectBox,
    boxes_overlap,
    classes_of,
    collect_edge_label_boxes,
    collect_group_boxes,
    collect_group_title_boxes,
    collect_ids,
    collect_markers,
    collect_nodes,
    collect_stage_boxes,
    collect_url_refs,
    horizontal_gap,
    parse_float,
    parse_path_endpoints,
    parse_svg_path_segments,
    point_hits_box,
    vertical_gap,
)


def is_edge_element(el: ET.Element) -> bool:
    return el.tag.endswith("path") and "ad-edge" in classes_of(el)


def box_role_name(box: NodeBox) -> str:
    return "annotation" if box.box_kind == "annotation" or box.role == "annotation" else "node"


def segment_crosses_rect_interior(
    start: tuple[float, float], end: tuple[float, float], rect: RectBox
) -> bool:
    inset_rect = rect.inset(6.0)
    if inset_rect.width <= 0 or inset_rect.height <= 0:
        return False

    x1, y1 = start
    x2, y2 = end

    if abs(x1 - x2) < 1e-6:
        x = x1
        if not (inset_rect.x < x < inset_rect.right):
            return False
        low_y = min(y1, y2)
        high_y = max(y1, y2)
        return high_y > inset_rect.y and low_y < inset_rect.bottom

    if abs(y1 - y2) < 1e-6:
        y = y1
        if not (inset_rect.y < y < inset_rect.bottom):
            return False
        low_x = min(x1, x2)
        high_x = max(x1, x2)
        return high_x > inset_rect.x and low_x < inset_rect.right

    return False


def collect_box_collision_errors(boxes: list[NodeBox]) -> list[str]:
    errors: list[str] = []
    for idx, left in enumerate(boxes):
        for right in boxes[idx + 1 :]:
            if boxes_overlap(left, right):
                errors.append(
                    f"{box_role_name(left).title()} '{left.node_id}' overlaps {box_role_name(right)} '{right.node_id}'."
                )
    return errors


def collect_box_clearance_errors(boxes: list[NodeBox]) -> list[str]:
    errors: list[str] = []
    for idx, left in enumerate(boxes):
        for right in boxes[idx + 1 :]:
            x_overlap = min(left.right, right.right) - max(left.x, right.x)
            y_overlap = min(left.bottom, right.bottom) - max(left.y, right.y)
            gap_x = horizontal_gap(left, right)
            gap_y = vertical_gap(left, right)

            if y_overlap > min(left.height, right.height) * 0.30 and 0.0 <= gap_x < 10.0:
                errors.append(
                    f"{box_role_name(left).title()} '{left.node_id}' and {box_role_name(right)} '{right.node_id}' are too close horizontally: gutter is {gap_x:.1f}px."
                )
            if x_overlap > min(left.width, right.width) * 0.30 and 0.0 <= gap_y < 10.0:
                errors.append(
                    f"{box_role_name(left).title()} '{left.node_id}' and {box_role_name(right)} '{right.node_id}' are too close vertically: gutter is {gap_y:.1f}px."
                )
    return errors


def collect_container_membership_errors(
    boxes: list[NodeBox], containers: dict[str, RectBox], attr_name: str, container_label: str
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    memberships = [box for box in boxes if getattr(box, attr_name)]
    for box in memberships:
        container_id = getattr(box, attr_name)
        container = containers.get(container_id)
        if container is None:
            warnings.append(
                f"{box_role_name(box).title()} '{box.node_id}' references missing {container_label} '{container_id}'; {container_label} containment was not checked."
            )
            continue
        if not container.contains(box, margin=12.0):
            errors.append(
                f"{box_role_name(box).title()} '{box.node_id}' exceeds {container_label} '{container_id}' bounds."
            )

    return errors, warnings


def collect_stage_membership_errors(
    boxes: list[NodeBox], stage_boxes: dict[str, RectBox]
) -> tuple[list[str], list[str]]:
    errors, warnings = collect_container_membership_errors(boxes, stage_boxes, "stage_id", "stage")
    if any(box.stage_id for box in boxes) or len(stage_boxes) != 1:
        return errors, warnings

    stage_id, stage_box = next(iter(stage_boxes.items()))
    for box in boxes:
        if not stage_box.contains(box, margin=12.0):
            errors.append(
                f"{box_role_name(box).title()} '{box.node_id}' exceeds stage '{stage_id}' bounds."
            )
    return errors, warnings


def collect_group_title_collisions(
    boxes: list[NodeBox], group_title_boxes: list[tuple[str, RectBox]]
) -> list[str]:
    errors: list[str] = []
    for box in boxes:
        for group_id, title_box in group_title_boxes:
            if boxes_overlap(box, title_box, clearance=4.0):
                errors.append(
                    f"{box_role_name(box).title().capitalize()} '{box.node_id}' intrudes into the title zone of group '{group_id}'."
                )
    return errors


def collect_edge_label_errors(root: ET.Element, boxes: list[NodeBox]) -> list[str]:
    errors: list[str] = []
    edge_label_boxes = collect_edge_label_boxes(root)
    group_title_boxes = collect_group_title_boxes(root)

    for idx, left in enumerate(edge_label_boxes):
        for right in edge_label_boxes[idx + 1 :]:
            if boxes_overlap(left, right, clearance=6.0):
                errors.append(
                    f"Edge labels '{left.label}' and '{right.label}' are colliding or too close to read cleanly."
                )

    for label_box in edge_label_boxes:
        for box in boxes:
            if boxes_overlap(label_box, box, clearance=8.0):
                errors.append(
                    f"Edge label '{label_box.label}' is colliding with or hugging {box_role_name(box)} '{box.node_id}'."
                )
        for group_id, title_box in group_title_boxes:
            if boxes_overlap(label_box, title_box, clearance=4.0):
                errors.append(
                    f"Edge label '{label_box.label}' overlaps group title area for '{group_id}'."
                )

    for el in root.iter():
        if not is_edge_element(el):
            continue
        endpoints = parse_path_endpoints(el.get("d") or "")
        if endpoints is None:
            continue
        (x1, y1), (x2, y2) = endpoints
        for label_box in edge_label_boxes:
            if point_hits_box(x1, y1, label_box, margin=14.0) or point_hits_box(
                x2, y2, label_box, margin=14.0
            ):
                errors.append(
                    f"Edge label '{label_box.label}' sits too close to an arrow endpoint."
                )

    return errors


def collect_edge_crossings(root: ET.Element, boxes: list[NodeBox]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    warned_unsupported = False

    for el in root.iter():
        if not is_edge_element(el):
            continue

        segments, unsupported = parse_svg_path_segments(el.get("d") or "")
        if unsupported:
            if not warned_unsupported:
                warnings.append(
                    "Some edge paths use unsupported curve commands; node-crossing checks were skipped for those paths."
                )
                warned_unsupported = True
            continue

        for start, end in segments:
            for box in boxes:
                if segment_crosses_rect_interior(start, end, box):
                    errors.append(
                        f"Edge segment crosses {box_role_name(box)} '{box.node_id}' interior: segment "
                        f"({start[0]:.1f},{start[1]:.1f}) -> ({end[0]:.1f},{end[1]:.1f})."
                    )
                    break

    return errors, warnings


def dedupe(messages: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for message in messages:
        if message in seen:
            continue
        seen.add(message)
        ordered.append(message)
    return ordered


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: lint-svg-diagram.py <svg-file>")
        return 2

    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"ERROR: File not found: {path}")
        return 2

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        print(f"ERROR: XML parse failed: {exc}")
        return 1

    root = tree.getroot()
    errors: list[str] = []
    warnings: list[str] = []

    if not root.tag.endswith("svg"):
        errors.append("Root element is not <svg>.")

    ids = collect_ids(root)
    for attr_name, ref in collect_url_refs(root):
        if ref not in ids:
            errors.append(f"Missing referenced id '{ref}' from attribute '{attr_name}'.")

    for marker in collect_markers(root):
        marker_id = marker.get("id", "<unknown>")
        width = parse_float(marker.get("markerWidth"))
        height = parse_float(marker.get("markerHeight"))
        if width > 10 or height > 10:
            warnings.append(
                f"Marker '{marker_id}' is {width}x{height}; large arrowheads often look crowded in report diagrams."
            )

    boxes = collect_nodes(root)
    errors.extend(collect_box_collision_errors(boxes))
    errors.extend(collect_box_clearance_errors(boxes))

    group_boxes = collect_group_boxes(root)
    group_errors, group_warnings = collect_container_membership_errors(
        boxes, group_boxes, "group_id", "group"
    )
    errors.extend(group_errors)
    warnings.extend(group_warnings)

    stage_boxes = collect_stage_boxes(root)
    stage_errors, stage_warnings = collect_stage_membership_errors(boxes, stage_boxes)
    errors.extend(stage_errors)
    warnings.extend(stage_warnings)

    group_title_boxes = collect_group_title_boxes(root)
    errors.extend(collect_group_title_collisions(boxes, group_title_boxes))
    errors.extend(collect_edge_label_errors(root, boxes))

    crossing_errors, crossing_warnings = collect_edge_crossings(root, boxes)
    errors.extend(crossing_errors)
    warnings.extend(crossing_warnings)

    if not boxes:
        warnings.append(
            "No auto-diagram node boxes found. Expected groups with class 'ad-node' and rects with class 'ad-node-box' or 'ad-note-box'."
        )

    warnings = dedupe(warnings)
    errors = dedupe(errors)

    print(f"Linting: {path}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("OK: SVG lint passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
