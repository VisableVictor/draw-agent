#!/usr/bin/env python3
"""Padding checker for auto-diagram SVG text containers.

Validates both explicit auto-diagram nodes and simple anonymous "rect + text"
chips. It also computes a minimum recommended box size so SVG-first diagrams can
expand bricks before text starts touching the edges.
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

    @property
    def center_x(self) -> float:
        return (self.left + self.right) / 2.0


@dataclass
class ContainerSpec:
    node_id: str
    rect: ET.Element
    texts: list[ET.Element]
    pad_x: float
    pad_top: float
    pad_bottom: float
    source: str


@dataclass
class ContainerReport:
    node_id: str
    source: str
    box_x: float
    box_y: float
    box_width: float
    box_height: float
    pad_x: float
    pad_top: float
    pad_bottom: float
    widest: float
    stack_height: float
    recommended_width: float
    recommended_height: float
    failures: list[str]


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
        for skip in (
            "ad-index",
            "ad-ring-label",
            "ad-chip",
            "ad-legend",
            "ad-edge-label",
            "ad-group-title",
            "ad-title",
            "ad-subtitle",
        )
    )


def default_font_size(text_el: ET.Element) -> float:
    child_classes = classes_of(text_el)
    if "ad-node-title" in child_classes or "ad-note-title" in child_classes:
        return 18.0
    if "ad-note-body" in child_classes:
        return 14.0
    if "ad-mini-title" in child_classes:
        return 14.0
    if "ad-core-title" in child_classes:
        return 28.0
    if "ad-core-body" in child_classes:
        return 15.0
    return 13.0


def primary_rect_of(group: ET.Element) -> ET.Element | None:
    rects = [child for child in list(group) if child.tag.endswith("rect")]
    if not rects:
        return None
    candidates = [child for child in rects if is_box_rect(child)] or rects
    return max(
        candidates,
        key=lambda child: parse_float(child.get("width"), 0.0) * parse_float(child.get("height"), 0.0),
    )


def content_texts_of(group: ET.Element) -> list[ET.Element]:
    return [
        child
        for child in list(group)
        if child.tag.endswith("text") and not is_skippable_text(child)
    ]


def has_title_text(texts: list[ET.Element]) -> bool:
    for text_el in texts:
        child_classes = classes_of(text_el)
        if any(name in child_classes for name in ("ad-node-title", "ad-note-title", "ad-mini-title")):
            return True
    return False


def top_strip_height(group: ET.Element, primary_rect: ET.Element) -> float:
    box_x = parse_float(primary_rect.get("x"), 0.0)
    box_y = parse_float(primary_rect.get("y"), 0.0)
    box_w = parse_float(primary_rect.get("width"), 0.0)
    box_h = parse_float(primary_rect.get("height"), 0.0)
    strip = 0.0
    for child in list(group):
        if child is primary_rect or not child.tag.endswith("rect"):
            continue
        x = parse_float(child.get("x"), 0.0)
        y = parse_float(child.get("y"), 0.0)
        w = parse_float(child.get("width"), 0.0)
        h = parse_float(child.get("height"), 0.0)
        if (
            abs(x - box_x) <= 1.0
            and abs(y - box_y) <= 1.0
            and abs(w - box_w) <= 1.0
            and 0.0 < h < box_h * 0.55
        ):
            strip = max(strip, h)
    return strip


def infer_padding(group: ET.Element, rect: ET.Element, texts: list[ET.Element]) -> tuple[float, float, float, str]:
    explicit = is_padding_container(group)
    if explicit:
        return (
            parse_float(group.get("data-pad-x"), 24.0),
            parse_float(group.get("data-pad-top"), 18.0),
            parse_float(group.get("data-pad-bottom"), 18.0),
            "explicit",
        )

    max_font = max(font_size_of(text_el, default_font_size(text_el)) for text_el in texts)
    pad_x = max(18.0, round(max_font * 1.6))
    pad_y = max(8.0, round(max_font * 0.75))
    if has_title_text(texts):
        pad_x = max(pad_x, 24.0)
        pad_y = max(pad_y, 12.0)
    pad_top = max(pad_y, top_strip_height(group, rect))
    return pad_x, pad_top, pad_y, "implicit"


def derived_node_id(group: ET.Element, texts: list[ET.Element]) -> str:
    explicit = group.get("data-node-id") or group.get("id")
    if explicit:
        return explicit
    for text_el in texts:
        lines = text_lines_of(text_el)
        if lines:
            return lines[0][:48]
    return "unknown"


def is_implicit_text_container(group: ET.Element, rect: ET.Element | None, texts: list[ET.Element]) -> bool:
    if rect is None or not texts:
        return False
    group_classes = classes_of(group)
    if "ad-stage" in group_classes or "ad-group" in group_classes:
        return False
    for child in list(group):
        if not child.tag.endswith("text"):
            continue
        child_classes = classes_of(child)
        if any(name in child_classes for name in ("ad-edge-label", "ad-group-title", "ad-legend")):
            return False
    return True


def collect_containers(root: ET.Element) -> list[ContainerSpec]:
    containers: list[ContainerSpec] = []
    for group in root.iter():
        if not group.tag.endswith("g"):
            continue
        rect = primary_rect_of(group)
        texts = content_texts_of(group)
        if rect is None or not texts:
            continue
        if not is_padding_container(group) and not is_implicit_text_container(group, rect, texts):
            continue
        pad_x, pad_top, pad_bottom, source = infer_padding(group, rect, texts)
        containers.append(
            ContainerSpec(
                node_id=derived_node_id(group, texts),
                rect=rect,
                texts=texts,
                pad_x=pad_x,
                pad_top=pad_top,
                pad_bottom=pad_bottom,
                source=source,
            )
        )
    return containers


def stack_height_of(blocks: list[ContentLine]) -> float:
    if not blocks:
        return 0.0
    total = blocks[0].height
    previous = blocks[0]
    for block in blocks[1:]:
        gap = max(6.0, block.top - previous.bottom)
        total += gap + block.height
        previous = block
    return total


def inspect_container(spec: ContainerSpec) -> ContainerReport:
    rect = spec.rect
    box_width = parse_float(rect.get("width"), 0.0)
    box_height = parse_float(rect.get("height"), 0.0)
    box_x = parse_float(rect.get("x"), 0.0)
    box_y = parse_float(rect.get("y"), 0.0)
    usable_width = box_width - spec.pad_x * 2
    usable_height = box_height - spec.pad_top - spec.pad_bottom
    safe_left = box_x + spec.pad_x
    safe_right = box_x + box_width - spec.pad_x
    safe_top = box_y + spec.pad_top
    safe_bottom = box_y + box_height - spec.pad_bottom

    failures: list[str] = []
    blocks: list[ContentLine] = []

    for text_el in spec.texts:
        block = estimate_text_block(text_el, default_font_size(text_el))
        blocks.append(block)
        if (
            is_body_text(text_el)
            and not has_explicit_wrap(text_el)
            and block.width > usable_width * 0.82
            and len("".join(text_lines_of(text_el))) >= 18
        ):
            failures.append(
                f"Node '{spec.node_id}' has a long body line without explicit wrapping: content width ~{block.width:.1f}px approaches usable width {usable_width:.1f}px."
            )
        if block.left < safe_left:
            failures.append(
                f"Node '{spec.node_id}' places text too far left: text starts at {block.left:.1f}px but safe area starts at {safe_left:.1f}px."
            )
        if block.right > safe_right:
            failures.append(
                f"Node '{spec.node_id}' places text too far right: text ends at {block.right:.1f}px but safe area ends at {safe_right:.1f}px."
            )
        if block.top < safe_top:
            failures.append(
                f"Node '{spec.node_id}' places text too high: text top ~{block.top:.1f}px exceeds safe top {safe_top:.1f}px."
            )
        if block.bottom > safe_bottom:
            failures.append(
                f"Node '{spec.node_id}' places text too low: text bottom ~{block.bottom:.1f}px exceeds safe bottom {safe_bottom:.1f}px."
            )

    widest = max((block.width for block in blocks), default=0.0)
    stack_top = min((block.top for block in blocks), default=0.0)
    stack_bottom = max((block.bottom for block in blocks), default=0.0)
    stack_left = min((block.left for block in blocks), default=0.0)
    stack_right = max((block.right for block in blocks), default=0.0)
    stack_height = stack_height_of(blocks)
    recommended_width = widest + spec.pad_x * 2
    recommended_height = stack_height + spec.pad_top + spec.pad_bottom

    if widest > usable_width:
        failures.append(
            f"Node '{spec.node_id}' likely violates horizontal padding: content width ~{widest:.1f}px > usable width {usable_width:.1f}px."
        )
    if stack_height > usable_height:
        failures.append(
            f"Node '{spec.node_id}' likely violates vertical padding: content height ~{stack_height:.1f}px > usable height {usable_height:.1f}px."
        )

    if blocks:
        top_clearance = stack_top - safe_top
        bottom_clearance = safe_bottom - stack_bottom
        if top_clearance >= 0 and bottom_clearance >= 0:
            if (
                abs(top_clearance - bottom_clearance) > 10.0
                and min(top_clearance, bottom_clearance) < max(12.0, usable_height * 0.22)
            ):
                failures.append(
                    f"Node '{spec.node_id}' has vertically unbalanced text placement: top clearance ~{top_clearance:.1f}px vs bottom clearance ~{bottom_clearance:.1f}px."
                )

        anchors = {(text_el.get("text-anchor") or "").strip() for text_el in spec.texts}
        if anchors == {"middle"}:
            stack_center_x = (stack_left + stack_right) / 2.0
            box_center_x = box_x + box_width / 2.0
            if abs(stack_center_x - box_center_x) > 6.0:
                failures.append(
                    f"Node '{spec.node_id}' has horizontally off-center text: text center ~{stack_center_x:.1f}px vs box center {box_center_x:.1f}px."
                )

    if failures:
        needs_growth = box_width + 0.5 < recommended_width or box_height + 0.5 < recommended_height
        if needs_growth:
            failures.append(
                f"Node '{spec.node_id}' should grow to at least {recommended_width:.1f}x{recommended_height:.1f}px for balanced padding; current box is {box_width:.1f}x{box_height:.1f}px."
            )
        else:
            failures.append(
                f"Node '{spec.node_id}' can keep its current box {box_width:.1f}x{box_height:.1f}px, but text should be re-centered within the existing safe area."
            )

    return ContainerReport(
        node_id=spec.node_id,
        source=spec.source,
        box_x=box_x,
        box_y=box_y,
        box_width=box_width,
        box_height=box_height,
        pad_x=spec.pad_x,
        pad_top=spec.pad_top,
        pad_bottom=spec.pad_bottom,
        widest=widest,
        stack_height=stack_height,
        recommended_width=recommended_width,
        recommended_height=recommended_height,
        failures=failures,
    )


def parse_args(argv: list[str]) -> tuple[Path, bool]:
    recommend = False
    args = argv[1:]
    if args and args[0] == "--recommend":
        recommend = True
        args = args[1:]
    if len(args) != 1:
        print("Usage: check-svg-node-padding.py [--recommend] <svg-file>")
        raise SystemExit(2)
    return Path(args[0]), recommend


def main() -> int:
    path, recommend = parse_args(sys.argv)
    if not path.is_file():
        print(f"ERROR: File not found: {path}")
        return 2

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        print(f"ERROR: XML parse failed: {exc}")
        return 1

    reports = [inspect_container(spec) for spec in collect_containers(root)]

    if not reports:
        print(
            "WARNING: No auto-diagram padding containers found. Expected groups with class 'ad-node', data-pad-* attributes, or simple rect+text chips."
        )
        return 0

    if recommend:
        for report in reports:
            print(
                "RECOMMEND: "
                f"{report.node_id} [{report.source}] current {report.box_width:.1f}x{report.box_height:.1f}px "
                f"-> min {report.recommended_width:.1f}x{report.recommended_height:.1f}px "
                f"(pads x={report.pad_x:.1f}, top={report.pad_top:.1f}, bottom={report.pad_bottom:.1f})."
            )

    failures = [failure for report in reports for failure in report.failures]
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    explicit_count = sum(1 for report in reports if report.source == "explicit")
    implicit_count = len(reports) - explicit_count
    print(
        f"OK: Padding check passed for {len(reports)} containers "
        f"({explicit_count} explicit, {implicit_count} inferred)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
