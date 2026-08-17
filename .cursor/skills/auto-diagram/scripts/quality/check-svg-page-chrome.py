#!/usr/bin/env python3
"""Validate page-level title/subtitle/footer chrome in auto-diagram SVGs.

Hard errors:
- page title/subtitle/legend overflow page gutters
- stage/group/node/annotation boxes intrude into header/footer text zones
- edge labels or edge segments enter page chrome forbidden zones

Soft feedback:
- header/footer feel too tight against main content
- top annotation cards visually crowd the title block
- page chrome contrast is likely weak when a solid page background is detectable
"""

from __future__ import annotations

import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from svg_quality_lib import (
    NodeBox,
    RectBox,
    boxes_overlap,
    collect_edge_label_boxes,
    collect_group_boxes,
    collect_nodes,
    collect_stage_boxes,
    classes_of,
    parse_float,
    parse_svg_path_segments,
    segment_crosses_rect_interior,
    text_box_to_rect,
    union_rects,
    viewbox_rect,
)


PAGE_GUTTER_X = 24.0
PAGE_GUTTER_TOP = 16.0
PAGE_GUTTER_BOTTOM = 14.0
HEADER_ZONE_PAD_X = 14.0
HEADER_ZONE_PAD_Y = 10.0
FOOTER_ZONE_PAD_X = 10.0
FOOTER_ZONE_PAD_Y = 8.0
HEADER_TARGET_CLEARANCE = 8.0
FOOTER_TARGET_CLEARANCE = 8.0
MIN_HEADER_CONTENT_GAP = 24.0
MIN_FOOTER_CONTENT_GAP = 18.0
HEADER_ANNOTATION_GAP = 26.0

HEX_COLOR_RE = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
RGB_COLOR_RE = re.compile(
    r"^rgb\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*\)$"
)


def dedupe(messages: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for message in messages:
        if message in seen:
            continue
        seen.add(message)
        ordered.append(message)
    return ordered


def style_value(el: ET.Element, key: str) -> str | None:
    style = el.get("style") or ""
    for part in style.split(";"):
        name, _, value = part.partition(":")
        if name.strip() == key:
            cleaned = value.strip()
            return cleaned or None
    return None


def fill_of(el: ET.Element) -> str | None:
    return (el.get("fill") or style_value(el, "fill") or "").strip() or None


def parse_rgb(color: str) -> tuple[int, int, int] | None:
    color = color.strip()
    hex_match = HEX_COLOR_RE.fullmatch(color)
    if hex_match:
        raw = hex_match.group(1)
        if len(raw) == 3:
            raw = "".join(char * 2 for char in raw)
        return (int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16))

    rgb_match = RGB_COLOR_RE.fullmatch(color)
    if rgb_match:
        return tuple(max(0, min(255, int(part))) for part in rgb_match.groups())
    return None


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(value: int) -> float:
        normalized = value / 255.0
        if normalized <= 0.03928:
            return normalized / 12.92
        return ((normalized + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(foreground: tuple[int, int, int], background: tuple[int, int, int]) -> float:
    fg = relative_luminance(foreground)
    bg = relative_luminance(background)
    lighter = max(fg, bg)
    darker = min(fg, bg)
    return (lighter + 0.05) / (darker + 0.05)


def is_edge_element(el: ET.Element) -> bool:
    return el.tag.endswith("path") and "ad-edge" in classes_of(el)


def collect_chrome_text_elements(
    root: ET.Element, class_name: str, default_size: float
) -> list[tuple[ET.Element, RectBox]]:
    from svg_quality_lib import text_bbox

    results: list[tuple[ET.Element, RectBox]] = []
    index = 0
    for el in root.iter():
        if not el.tag.endswith("text"):
            continue
        if class_name not in classes_of(el):
            continue
        bbox = text_bbox(el, default_size)
        if bbox is None:
            continue
        results.append((el, text_box_to_rect(bbox, f"{class_name}-{index}")))
        index += 1
    return results


def page_background_color(root: ET.Element, viewbox: RectBox) -> tuple[int, int, int] | None:
    candidates: list[tuple[int, tuple[int, int, int]]] = []
    index = 0
    for el in root.iter():
        if not el.tag.endswith("rect"):
            continue
        x = parse_float(el.get("x"))
        y = parse_float(el.get("y"))
        width = parse_float(el.get("width"))
        height = parse_float(el.get("height"))
        if (
            abs(x - viewbox.x) > 1.0
            or abs(y - viewbox.y) > 1.0
            or abs(width - viewbox.width) > 1.0
            or abs(height - viewbox.height) > 1.0
        ):
            index += 1
            continue
        fill = fill_of(el)
        if not fill:
            index += 1
            continue
        rgb = parse_rgb(fill)
        if rgb is not None:
            candidates.append((index, rgb))
        index += 1
    if not candidates:
        return None
    return candidates[0][1]


def chrome_overflow_errors(
    entries: list[tuple[str, RectBox]], viewbox: RectBox
) -> list[str]:
    errors: list[str] = []
    for label, box in entries:
        if box.x < viewbox.x + PAGE_GUTTER_X:
            errors.append(
                f"{label} exceeds the left page gutter: left edge is {box.x:.1f}px."
            )
        if box.right > viewbox.right - PAGE_GUTTER_X:
            errors.append(
                f"{label} exceeds the right page gutter: right edge is {box.right:.1f}px."
            )
        if "legend" not in label and box.y < viewbox.y + PAGE_GUTTER_TOP:
            errors.append(f"{label} sits too close to the top page edge: top is {box.y:.1f}px.")
        if "legend" in label and box.bottom > viewbox.bottom - PAGE_GUTTER_BOTTOM:
            errors.append(
                f"{label} exceeds the bottom page gutter: bottom edge is {box.bottom:.1f}px."
            )
    return errors


def collect_zone_intrusions(
    zone: RectBox,
    zone_name: str,
    targets: list[tuple[str, RectBox]],
    clearance: float,
) -> list[str]:
    errors: list[str] = []
    for target_kind, target_box in targets:
        if boxes_overlap(zone, target_box, clearance=clearance):
            errors.append(
                f"{target_kind.title()} '{target_box.node_id}' intrudes into the {zone_name}."
            )
    return errors


def collect_edge_intrusions(root: ET.Element, zone: RectBox, zone_name: str) -> tuple[list[str], list[str]]:
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
                    f"Some edge paths use unsupported curve commands; {zone_name} edge-intrusion checks were skipped for those paths."
                )
                warned_unsupported = True
            continue
        for start, end in segments:
            if segment_crosses_rect_interior(start, end, zone, inset=2.0):
                errors.append(
                    f"Edge segment enters the {zone_name}: segment ({start[0]:.1f},{start[1]:.1f}) -> ({end[0]:.1f},{end[1]:.1f})."
                )
                break
    return errors, warnings


def collect_zone_gap_feedback(
    zone: RectBox,
    zone_name: str,
    content_boxes: list[RectBox],
    minimum_gap: float,
) -> list[str]:
    if not content_boxes:
        return []

    if zone_name == "header zone":
        lower_boxes = [box for box in content_boxes if box.y >= zone.bottom]
        if not lower_boxes:
            return []
        gap = min(box.y for box in lower_boxes) - zone.bottom
        if gap < minimum_gap:
            return [
                f"{zone_name.title()} is tight against main content: only {gap:.1f}px of vertical breathing room."
            ]
        return []

    upper_boxes = [box for box in content_boxes if box.bottom <= zone.y]
    if not upper_boxes:
        return []
    gap = zone.y - max(box.bottom for box in upper_boxes)
    if gap < minimum_gap:
        return [
            f"{zone_name.title()} is tight against main content: only {gap:.1f}px of vertical breathing room."
        ]
    return []


def collect_header_annotation_feedback(
    header_zone: RectBox, nodes: list[NodeBox], title_zone: RectBox | None
) -> list[str]:
    hints: list[str] = []
    header_annotations = [
        node
        for node in nodes
        if node.box_kind == "annotation" and node.y < header_zone.bottom + HEADER_ANNOTATION_GAP
    ]
    if not header_annotations or title_zone is None:
        return hints

    annotation_area = sum(node.area for node in header_annotations)
    title_area = max(1.0, title_zone.area)
    if annotation_area > title_area * 1.1:
        hints.append(
            f"Top annotation chrome is visually heavy ({annotation_area / title_area:.2f}x of title block area); it may compete with the page title."
        )

    side_candidates = [node.x - title_zone.right for node in header_annotations if node.x >= title_zone.right]
    if side_candidates and min(side_candidates) < 36.0:
        hints.append(
            f"Top annotation chrome crowds the title block horizontally: only {min(side_candidates):.1f}px of side breathing room."
        )
    return hints


def collect_chrome_contrast_hints(
    viewbox: RectBox,
    background_rgb: tuple[int, int, int] | None,
    chrome_entries: list[tuple[str, ET.Element]],
) -> list[str]:
    if background_rgb is None:
        return []

    hints: list[str] = []
    thresholds = {
        "title": 3.8,
        "subtitle": 3.0,
        "legend": 3.0,
    }
    for label, el in chrome_entries:
        fill = fill_of(el)
        if not fill:
            continue
        rgb = parse_rgb(fill)
        if rgb is None:
            continue
        ratio = contrast_ratio(rgb, background_rgb)
        key = "legend" if "legend" in label else "subtitle" if "subtitle" in label else "title"
        if ratio < thresholds[key]:
            hints.append(
                f"{label} may have weak contrast against the page background (ratio {ratio:.2f})."
            )
    return hints


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check-svg-page-chrome.py <svg-file>")
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

    errors: list[str] = []
    warnings: list[str] = []
    hints: list[str] = []

    viewbox = viewbox_rect(root)
    if viewbox is None:
        print(f"ERROR: {path} is missing a valid viewBox; page chrome checks require one.")
        return 1

    title_entries = collect_chrome_text_elements(root, "ad-title", 16.0)
    subtitle_entries = collect_chrome_text_elements(root, "ad-subtitle", 14.0)
    legend_entries = collect_chrome_text_elements(root, "ad-legend", 12.0)

    title_boxes = [entry[1] for entry in title_entries]
    subtitle_boxes = [entry[1] for entry in subtitle_entries]
    legend_boxes = [entry[1] for entry in legend_entries]

    if not title_boxes:
        warnings.append("No page title detected; report-grade diagrams usually need an ad-title.")

    chrome_boxes = (
        [(f"page title '{box.node_id}'", box) for box in title_boxes]
        + [(f"page subtitle '{box.node_id}'", box) for box in subtitle_boxes]
        + [(f"page legend '{box.node_id}'", box) for box in legend_boxes]
    )
    errors.extend(chrome_overflow_errors(chrome_boxes, viewbox))

    header_zone = union_rects(title_boxes + subtitle_boxes, "page-header-zone", HEADER_ZONE_PAD_X, HEADER_ZONE_PAD_Y)
    title_zone = union_rects(title_boxes, "page-title-zone", 8.0, 6.0)
    footer_zone = union_rects(legend_boxes, "page-footer-zone", FOOTER_ZONE_PAD_X, FOOTER_ZONE_PAD_Y)

    target_boxes: list[tuple[str, RectBox]] = []
    target_boxes.extend(("node" if node.box_kind == "node" else "annotation", node) for node in collect_nodes(root))
    target_boxes.extend(("group", box) for box in collect_group_boxes(root).values())
    target_boxes.extend(("stage", box) for box in collect_stage_boxes(root).values())

    if header_zone is not None:
        errors.extend(
            collect_zone_intrusions(header_zone, "header zone", target_boxes, HEADER_TARGET_CLEARANCE)
        )
        edge_errors, edge_warnings = collect_edge_intrusions(root, header_zone, "header zone")
        errors.extend(edge_errors)
        warnings.extend(edge_warnings)
        for label_box in collect_edge_label_boxes(root):
            if boxes_overlap(header_zone, label_box, clearance=6.0):
                errors.append(
                    f"Edge label '{label_box.label}' intrudes into the header zone."
                )

    if footer_zone is not None:
        errors.extend(
            collect_zone_intrusions(footer_zone, "footer zone", target_boxes, FOOTER_TARGET_CLEARANCE)
        )
        edge_errors, edge_warnings = collect_edge_intrusions(root, footer_zone, "footer zone")
        errors.extend(edge_errors)
        warnings.extend(edge_warnings)
        for label_box in collect_edge_label_boxes(root):
            if boxes_overlap(footer_zone, label_box, clearance=6.0):
                errors.append(
                    f"Edge label '{label_box.label}' intrudes into the footer zone."
                )

    content_boxes = [box for _, box in target_boxes]
    if header_zone is not None:
        warnings.extend(
            collect_zone_gap_feedback(header_zone, "header zone", content_boxes, MIN_HEADER_CONTENT_GAP)
        )
        hints.extend(collect_header_annotation_feedback(header_zone, collect_nodes(root), title_zone))
        if header_zone.height > viewbox.height * 0.22:
            hints.append(
                f"Header zone uses {header_zone.height / viewbox.height * 100:.0f}% of page height; consider tightening chrome so the canvas serves the main diagram."
            )

    if footer_zone is not None:
        warnings.extend(
            collect_zone_gap_feedback(footer_zone, "footer zone", content_boxes, MIN_FOOTER_CONTENT_GAP)
        )

    background_rgb = page_background_color(root, viewbox)
    hints.extend(
        collect_chrome_contrast_hints(
            viewbox,
            background_rgb,
            [(f"page title '{el.get('class', 'ad-title')}'", el) for el, _ in title_entries]
            + [(f"page subtitle '{el.get('class', 'ad-subtitle')}'", el) for el, _ in subtitle_entries]
            + [(f"page legend '{el.get('class', 'ad-legend')}'", el) for el, _ in legend_entries],
        )
    )

    errors = dedupe(errors)
    warnings = dedupe(warnings)
    hints = dedupe(hints)

    print(f"Page Chrome: {path}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    if hints:
        for hint in hints:
            print(f"DESIGN_HINT: {hint}")
    if not errors and not warnings and not hints:
        print("OK: Page chrome checks found no obvious header/footer collisions or spacing issues.")

    strict_mode = os.getenv("AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING") or os.getenv(
        "AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING"
    )
    if warnings and strict_mode == "1":
        return 1
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
