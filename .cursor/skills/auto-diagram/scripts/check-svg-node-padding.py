#!/usr/bin/env python3
"""Padding checker for auto-diagram SVG text containers.

Uses auto-diagram class conventions and data-pad-* attributes to estimate whether
text stays inside the intended safe area, and whether the placed text block still
has visually balanced breathing room.
"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from svg_quality_lib import (
    classes_of,
    font_size_of,
    has_explicit_wrap,
    line_height_of,
    parse_float,
    text_lines_of,
    visual_units,
)


@dataclass
class ContentLine:
    label: str
    width: float
    height: float
    left: float
    right: float
    top: float
    bottom: float


def baseline_offsets(el: ET.Element, line_height: float, line_count: int) -> list[float]:
    tspans = [child for child in list(el) if child.tag.endswith("tspan")]
    if not tspans:
        return [index * line_height for index in range(line_count)]

    offsets: list[float] = []
    current = 0.0
    first = True
    for child in tspans:
        dy = parse_float(child.get("dy"), 0.0)
        if first:
            current = dy
            first = False
        else:
            current += dy
        offsets.append(current)
    return offsets


def is_body_text(el: ET.Element) -> bool:
    child_classes = classes_of(el)
    return any(
        name in child_classes
        for name in ("ad-node-body", "ad-note-body", "ad-mini-body", "ad-core-body")
    )


def estimate_text_block(el: ET.Element, default_size: float) -> ContentLine:
    size = font_size_of(el, default_size)
    lines = text_lines_of(el)
    if not lines:
        return ContentLine(
            label=el.get("class", "text"),
            width=0.0,
            height=0.0,
            left=0.0,
            right=0.0,
            top=0.0,
            bottom=0.0,
        )
    max_units = max(visual_units(line) for line in lines)
    width = max_units * size
    line_height = line_height_of(el, size)
    offsets = baseline_offsets(el, line_height, len(lines))
    x = parse_float(el.get("x"), 0.0)
    y = parse_float(el.get("y"), 0.0)
    anchor = (el.get("text-anchor") or "").strip()

    if anchor == "middle":
        left = x - width / 2.0
    elif anchor == "end":
        left = x - width
    else:
        left = x

    first_baseline = y + offsets[0]
    last_baseline = y + offsets[-1]
    top = first_baseline - size * 0.9
    bottom = last_baseline + size * 0.2
    return ContentLine(
        label=el.get("class", "text"),
        width=width,
        height=max(0.0, bottom - top),
        left=left,
        right=left + width,
        top=top,
        bottom=bottom,
    )


def is_padding_container(group: ET.Element) -> bool:
    if "ad-node" in classes_of(group):
        return True
    return any(
        group.get(attr) is not None
        for attr in ("data-pad-x", "data-pad-top", "data-pad-bottom")
    )


def is_box_rect(el: ET.Element) -> bool:
    if not el.tag.endswith("rect"):
        return False
    child_classes = classes_of(el)
    return any(name.endswith("box") for name in child_classes)


def is_skippable_text(el: ET.Element) -> bool:
    child_classes = classes_of(el)
    return any(
        skip in child_classes
        for skip in ("ad-index", "ad-ring-label", "ad-chip", "ad-legend")
    )


def default_font_size(text_el: ET.Element) -> float:
    child_classes = classes_of(text_el)
    if "ad-node-title" in child_classes or "ad-note-title" in child_classes:
        return 18.0
    if "ad-mini-title" in child_classes:
        return 14.0
    if "ad-core-title" in child_classes:
        return 28.0
    if "ad-core-body" in child_classes:
        return 15.0
    return 13.0


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check-svg-node-padding.py <svg-file>")
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

    failures: list[str] = []
    inspected = 0

    for group in root.iter():
        if not is_padding_container(group):
            continue

        node_id = group.get("data-node-id") or "unknown"
        pad_x = parse_float(group.get("data-pad-x"), 24.0)
        pad_top = parse_float(group.get("data-pad-top"), 18.0)
        pad_bottom = parse_float(group.get("data-pad-bottom"), 18.0)

        rect = None
        texts: list[ET.Element] = []

        for child in list(group):
            if is_box_rect(child) and rect is None:
                rect = child
            elif child.tag.endswith("text") and not is_skippable_text(child):
                texts.append(child)

        if rect is None:
            continue

        inspected += 1
        box_width = parse_float(rect.get("width"), 0.0)
        box_height = parse_float(rect.get("height"), 0.0)
        box_x = parse_float(rect.get("x"), 0.0)
        box_y = parse_float(rect.get("y"), 0.0)
        usable_width = box_width - pad_x * 2
        usable_height = box_height - pad_top - pad_bottom
        safe_left = box_x + pad_x
        safe_right = box_x + box_width - pad_x
        safe_top = box_y + pad_top
        safe_bottom = box_y + box_height - pad_bottom

        consumed_height = 0.0
        widest = 0.0
        stack_top = float("inf")
        stack_bottom = float("-inf")

        for idx, text_el in enumerate(texts):
            block = estimate_text_block(text_el, default_font_size(text_el))
            consumed_height += block.height
            widest = max(widest, block.width)
            stack_top = min(stack_top, block.top)
            stack_bottom = max(stack_bottom, block.bottom)
            if idx < len(texts) - 1:
                consumed_height += 6.0

            if (
                is_body_text(text_el)
                and not has_explicit_wrap(text_el)
                and block.width > usable_width * 0.82
                and len("".join(text_lines_of(text_el))) >= 18
            ):
                failures.append(
                    f"Node '{node_id}' has a long body line without explicit wrapping: content width ~{block.width:.1f}px approaches usable width {usable_width:.1f}px."
                )
            if block.left < safe_left:
                failures.append(
                    f"Node '{node_id}' places text too far left: text starts at {block.left:.1f}px but safe area starts at {safe_left:.1f}px."
                )
            if block.right > safe_right:
                failures.append(
                    f"Node '{node_id}' places text too far right: text ends at {block.right:.1f}px but safe area ends at {safe_right:.1f}px."
                )
            if block.top < safe_top:
                failures.append(
                    f"Node '{node_id}' places text too high: text top ~{block.top:.1f}px exceeds safe top {safe_top:.1f}px."
                )
            if block.bottom > safe_bottom:
                failures.append(
                    f"Node '{node_id}' places text too low: text bottom ~{block.bottom:.1f}px exceeds safe bottom {safe_bottom:.1f}px."
                )

        if widest > usable_width:
            failures.append(
                f"Node '{node_id}' likely violates horizontal padding: content width ~{widest:.1f}px > usable width {usable_width:.1f}px."
            )
        if consumed_height > usable_height:
            failures.append(
                f"Node '{node_id}' likely violates vertical padding: content height ~{consumed_height:.1f}px > usable height {usable_height:.1f}px."
            )
        if stack_top != float("inf") and stack_bottom != float("-inf"):
            top_clearance = stack_top - safe_top
            bottom_clearance = safe_bottom - stack_bottom
            if top_clearance < 0 or bottom_clearance < 0:
                pass
            elif (
                abs(top_clearance - bottom_clearance) > 10.0
                and min(top_clearance, bottom_clearance) < max(12.0, usable_height * 0.22)
            ):
                failures.append(
                    f"Node '{node_id}' has vertically unbalanced text placement: top clearance ~{top_clearance:.1f}px vs bottom clearance ~{bottom_clearance:.1f}px."
                )

    if inspected == 0:
        print(
            "WARNING: No auto-diagram padding containers found. Expected groups with class 'ad-node' or data-pad-* attributes."
        )
        return 0

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print(f"OK: Padding check passed for {inspected} nodes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
