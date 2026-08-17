#!/usr/bin/env python3
"""Auto-fit SVG node text before hard quality checks.

This pass is intentionally conservative:
- Prefer explicit wrapping for long single-line body text
- Then allow small font-size reductions within readable floors
- Re-center the text stack inside the existing safe area

It improves theme-pack / font-switch robustness without silently replacing the
later hard-fail quality gates.
"""

from __future__ import annotations

import importlib.util
import sys
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
QUALITY_DIR = SCRIPT_DIR.parent / "quality"
if str(QUALITY_DIR) not in sys.path:
    sys.path.insert(0, str(QUALITY_DIR))

from svg_quality_lib import (
    RectBox,
    boxes_overlap,
    classes_of,
    collect_edge_label_boxes,
    collect_group_boxes,
    collect_group_title_boxes,
    collect_nodes,
    collect_stage_boxes,
    font_size_of,
    line_height_of,
    parse_float,
    parse_svg_path_segments,
    text_lines_of,
    visual_units,
)  # noqa: E402


def load_padding_module():
    module_path = QUALITY_DIR / "check-svg-node-padding.py"
    spec = importlib.util.spec_from_file_location("check_svg_node_padding", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load padding module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PADDING = load_padding_module()


@dataclass
class FitStats:
    wrapped: int = 0
    shrunk: int = 0
    recentered: int = 0
    grown: int = 0
    touched_containers: int = 0


def usage() -> None:
    print("Usage: auto-fit-svg-text.py <svg-file>")


def svg_ns(tag: str, local_name: str) -> str:
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[0] + "}" + local_name
    return local_name


def viewbox_area(root: ET.Element) -> float:
    values = (root.get("viewBox") or "").strip().split()
    if len(values) != 4:
        return 0.0
    width = parse_float(values[2], 0.0)
    height = parse_float(values[3], 0.0)
    return width * height


def is_large_implicit_container(spec, page_area: float) -> bool:
    if spec.source != "implicit" or page_area <= 0:
        return False
    width = parse_float(spec.rect.get("width"), 0.0)
    height = parse_float(spec.rect.get("height"), 0.0)
    area = width * height
    return area >= page_area * 0.10


def is_body_like(text_el: ET.Element) -> bool:
    child_classes = classes_of(text_el)
    return any(
        name in child_classes
        for name in (
            "ad-node-body",
            "ad-note-body",
            "ad-mini-body",
            "ad-core-body",
        )
    )


def is_title_like(text_el: ET.Element) -> bool:
    child_classes = classes_of(text_el)
    return any(
        name in child_classes
        for name in (
            "ad-node-title",
            "ad-note-title",
            "ad-mini-title",
            "ad-core-title",
        )
    )


def semantic_role(spec, text_el: ET.Element) -> str:
    child_classes = classes_of(text_el)
    if "ad-core-title" in child_classes or is_title_like(text_el):
        return "title"
    if is_body_like(text_el):
        return "body"
    if len(spec.texts) >= 2 and spec.texts[0] is text_el:
        return "title"
    return "body"


def min_font_size(spec, text_el: ET.Element) -> float:
    role = semantic_role(spec, text_el)
    child_classes = classes_of(text_el)
    if "ad-core-title" in child_classes:
        return 22.0
    if role == "title":
        return 16.0
    if role == "body":
        return 12.0
    return 11.0


def should_wrap(spec, text_el: ET.Element) -> bool:
    child_classes = classes_of(text_el)
    blocked = {
        "ad-title",
        "ad-subtitle",
        "ad-group-title",
        "ad-legend",
        "ad-edge-label",
    }
    if any(name in child_classes for name in blocked):
        return False
    return semantic_role(spec, text_el) != "title"


def wrap_line_limit(spec, text_el: ET.Element) -> int:
    if semantic_role(spec, text_el) == "body":
        return 3
    return 2


def split_long_token(token: str, max_units: float) -> list[str]:
    if not token:
        return []
    pieces: list[str] = []
    current = ""
    current_units = 0.0
    for char in token:
        units = visual_units(char)
        if current and current_units + units > max_units:
            pieces.append(current)
            current = char
            current_units = units
        else:
            current += char
            current_units += units
    if current:
        pieces.append(current)
    return pieces


def tokenize_text(text: str) -> list[str]:
    tokens: list[str] = []
    ascii_buffer = ""

    def flush_ascii() -> None:
        nonlocal ascii_buffer
        if ascii_buffer:
            tokens.append(ascii_buffer)
            ascii_buffer = ""

    for char in text:
        if char.isspace():
            flush_ascii()
            if tokens and tokens[-1] != " ":
                tokens.append(" ")
            continue
        if unicodedata.east_asian_width(char) in {"W", "F"}:
            flush_ascii()
            tokens.append(char)
            continue
        if char.isalnum():
            ascii_buffer += char
            continue
        flush_ascii()
        tokens.append(char)

    flush_ascii()
    while tokens and tokens[0] == " ":
        tokens.pop(0)
    while tokens and tokens[-1] == " ":
        tokens.pop()
    return tokens


def wrap_text_content(text: str, max_units: float, max_lines: int) -> list[str]:
    tokens = tokenize_text(text)
    if not tokens:
        return []

    lines: list[str] = []
    current = ""

    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == " ":
            if current and not current.endswith(" "):
                current += " "
            index += 1
            continue

        candidate = token if not current else current + token
        if current and visual_units(candidate.rstrip()) > max_units:
            lines.append(current.rstrip())
            current = ""
            if len(lines) >= max_lines:
                return [text]
            continue

        if not current and visual_units(token) > max_units:
            pieces = split_long_token(token, max_units)
            if len(pieces) > 1:
                tokens = tokens[:index] + pieces + tokens[index + 1 :]
                continue

        current = candidate
        index += 1

    if current.strip():
        lines.append(current.rstrip())

    if not lines or len(lines) > max_lines:
        return [text]
    return lines


def set_text_x(text_el: ET.Element, x: float) -> None:
    text_el.set("x", f"{x:.1f}")
    for child in list(text_el):
        if child.tag.endswith("tspan"):
            child.set("x", f"{x:.1f}")


def rewrite_text_lines(text_el: ET.Element, lines: list[str]) -> None:
    line_height = line_height_of(text_el, font_size_of(text_el, PADDING.default_font_size(text_el)))
    text_el.text = None
    for child in list(text_el):
        text_el.remove(child)

    if not lines:
        return
    if len(lines) == 1:
        text_el.text = lines[0]
        return

    x_value = text_el.get("x") or "0"
    tspan_tag = svg_ns(text_el.tag, "tspan")
    for index, line in enumerate(lines):
        tspan = ET.SubElement(text_el, tspan_tag)
        tspan.set("x", x_value)
        tspan.set("dy", "0" if index == 0 else f"{line_height:.1f}")
        tspan.text = line


def current_text_width(text_el: ET.Element) -> float:
    block = PADDING.estimate_text_block(text_el, PADDING.default_font_size(text_el))
    return block.width


def current_box(spec) -> RectBox:
    rect = spec.rect
    return RectBox(
        node_id=spec.node_id,
        x=parse_float(rect.get("x"), 0.0),
        y=parse_float(rect.get("y"), 0.0),
        width=parse_float(rect.get("width"), 0.0),
        height=parse_float(rect.get("height"), 0.0),
    )


def shrink_text(spec, text_el: ET.Element) -> bool:
    current = font_size_of(text_el, PADDING.default_font_size(text_el))
    floor = min_font_size(spec, text_el)
    if current <= floor:
        return False
    next_size = max(floor, current - 1.0)
    if next_size >= current:
        return False
    text_el.set("font-size", f"{next_size:.1f}")
    lines = text_lines_of(text_el)
    if len(lines) > 1:
        text_el.set("line-height", f"{next_size * 1.35:.1f}")
        rewrite_text_lines(text_el, lines)
    return True


def wrap_text_element(spec, text_el: ET.Element, usable_width: float) -> bool:
    if not should_wrap(spec, text_el):
        return False
    lines = text_lines_of(text_el)
    if not lines:
        return False
    if len(lines) > 1:
        return False

    size = font_size_of(text_el, PADDING.default_font_size(text_el))
    max_units = usable_width / max(size, 1.0)
    if max_units <= 1.0:
        return False

    source_text = lines[0]
    wrapped = wrap_text_content(source_text, max_units * 0.96, wrap_line_limit(spec, text_el))
    if wrapped == lines or len(wrapped) == 1:
        return False
    text_el.set("line-height", f"{size * 1.35:.1f}")
    rewrite_text_lines(text_el, wrapped)
    return True


def is_horizontal_overflow(text_el: ET.Element, spec) -> bool:
    rect = spec.rect
    box_x = parse_float(rect.get("x"), 0.0)
    box_width = parse_float(rect.get("width"), 0.0)
    safe_left = box_x + spec.pad_x
    safe_right = box_x + box_width - spec.pad_x
    block = PADDING.estimate_text_block(text_el, PADDING.default_font_size(text_el))
    return block.left < safe_left - 0.5 or block.right > safe_right + 0.5


def is_edge_element(el: ET.Element) -> bool:
    return el.tag.endswith("path") and "ad-edge" in classes_of(el)


def segment_crosses_rect_interior(start: tuple[float, float], end: tuple[float, float], rect: RectBox) -> bool:
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


def collect_edge_segments(root: ET.Element) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    for el in root.iter():
        if not is_edge_element(el):
            continue
        parsed, unsupported = parse_svg_path_segments(el.get("d") or "")
        if unsupported:
            continue
        segments.extend(parsed)
    return segments


def collect_container_groups(root: ET.Element) -> dict[str, ET.Element]:
    groups: dict[str, ET.Element] = {}
    for group in root.iter():
        if not group.tag.endswith("g"):
            continue
        rect = PADDING.primary_rect_of(group)
        texts = PADDING.content_texts_of(group)
        if rect is None or not texts:
            continue
        if not PADDING.is_padding_container(group) and not PADDING.is_implicit_text_container(group, rect, texts):
            continue
        groups[PADDING.derived_node_id(group, texts)] = group
    return groups


def candidate_box(box: RectBox, width: float, height: float) -> RectBox:
    delta_w = max(0.0, width - box.width)
    delta_h = max(0.0, height - box.height)
    return RectBox(
        node_id=box.node_id,
        x=box.x - delta_w / 2.0,
        y=box.y - delta_h / 2.0,
        width=width,
        height=height,
    )


def grow_target(report) -> tuple[float, float]:
    max_width_delta = max(120.0, report.box_width * 0.35)
    max_height_delta = max(56.0, report.box_height * 0.35)
    width = min(report.recommended_width + 2.0, report.box_width + max_width_delta)
    height = min(report.recommended_height + 2.0, report.box_height + max_height_delta)
    return max(report.box_width, width), max(report.box_height, height)


def resolve_container_boxes(root: ET.Element, spec) -> tuple[dict[str, RectBox], dict[str, RectBox], dict[str, RectBox]]:
    nodes = {node.node_id: RectBox(node.node_id, node.x, node.y, node.width, node.height) for node in collect_nodes(root)}
    groups = collect_group_boxes(root)
    stages = collect_stage_boxes(root)
    return nodes, groups, stages


def would_break_edges(current: RectBox, candidate: RectBox, edge_segments) -> bool:
    for start, end in edge_segments:
        if segment_crosses_rect_interior(start, end, candidate) and not segment_crosses_rect_interior(start, end, current):
            return True
    return False


def safe_to_grow(spec, root: ET.Element, candidate: RectBox) -> bool:
    current = current_box(spec)
    nodes, groups, stages = resolve_container_boxes(root, spec)
    node = next((item for item in collect_nodes(root) if item.node_id == spec.node_id), None)

    if node and node.group_id:
        group_box = groups.get(node.group_id)
        if group_box and not group_box.contains(candidate, margin=12.0):
            return False

    if node and node.stage_id:
        stage_box = stages.get(node.stage_id)
        if stage_box and not stage_box.contains(candidate, margin=12.0):
            return False

    for other_id, other in nodes.items():
        if other_id == spec.node_id:
            continue
        if boxes_overlap(candidate, other, clearance=10.0) and not boxes_overlap(current, other, clearance=10.0):
            return False

    for label_box in collect_edge_label_boxes(root):
        if boxes_overlap(candidate, label_box, clearance=8.0) and not boxes_overlap(current, label_box, clearance=8.0):
            return False

    for _, title_box in collect_group_title_boxes(root):
        if boxes_overlap(candidate, title_box, clearance=4.0) and not boxes_overlap(current, title_box, clearance=4.0):
            return False

    if would_break_edges(current, candidate, collect_edge_segments(root)):
        return False

    return True


def apply_box_growth(spec, group: ET.Element, candidate: RectBox) -> bool:
    rect = spec.rect
    old_x = parse_float(rect.get("x"), 0.0)
    old_y = parse_float(rect.get("y"), 0.0)
    old_w = parse_float(rect.get("width"), 0.0)
    old_h = parse_float(rect.get("height"), 0.0)

    if (
        abs(candidate.x - old_x) < 0.5
        and abs(candidate.y - old_y) < 0.5
        and abs(candidate.width - old_w) < 0.5
        and abs(candidate.height - old_h) < 0.5
    ):
        return False

    rect.set("x", f"{candidate.x:.1f}")
    rect.set("y", f"{candidate.y:.1f}")
    rect.set("width", f"{candidate.width:.1f}")
    rect.set("height", f"{candidate.height:.1f}")

    for child in list(group):
        if child is rect or not child.tag.endswith("rect"):
            continue
        x = parse_float(child.get("x"), 0.0)
        y = parse_float(child.get("y"), 0.0)
        w = parse_float(child.get("width"), 0.0)
        h = parse_float(child.get("height"), 0.0)
        is_top_strip = (
            abs(x - old_x) <= 1.0
            and abs(y - old_y) <= 1.0
            and abs(w - old_w) <= 1.0
            and 0.0 < h < old_h * 0.55
        )
        if is_top_strip:
            child.set("x", f"{candidate.x:.1f}")
            child.set("y", f"{candidate.y:.1f}")
            child.set("width", f"{candidate.width:.1f}")

    return True


def try_safe_grow(spec, root: ET.Element, group_map: dict[str, ET.Element], stats: FitStats) -> bool:
    if spec.source != "explicit":
        return False

    group = group_map.get(spec.node_id)
    if group is None:
        return False

    report = PADDING.inspect_container(spec)
    target_width, target_height = grow_target(report)
    current = current_box(spec)

    candidates: list[RectBox] = []
    if target_width > current.width + 0.5 or target_height > current.height + 0.5:
        candidates.append(candidate_box(current, target_width, target_height))
    if target_width > current.width + 0.5:
        candidates.append(candidate_box(current, target_width, current.height))
    if target_height > current.height + 0.5:
        candidates.append(candidate_box(current, current.width, target_height))

    seen: set[tuple[int, int, int, int]] = set()
    for candidate in candidates:
        signature = (
            round(candidate.x * 10),
            round(candidate.y * 10),
            round(candidate.width * 10),
            round(candidate.height * 10),
        )
        if signature in seen:
            continue
        seen.add(signature)
        if not safe_to_grow(spec, root, candidate):
            continue
        if apply_box_growth(spec, group, candidate):
            stats.grown += 1
            return True

    return False


def recenter_container(spec) -> bool:
    rect = spec.rect
    box_x = parse_float(rect.get("x"), 0.0)
    box_y = parse_float(rect.get("y"), 0.0)
    box_width = parse_float(rect.get("width"), 0.0)
    box_height = parse_float(rect.get("height"), 0.0)
    safe_left = box_x + spec.pad_x
    safe_right = box_x + box_width - spec.pad_x
    safe_top = box_y + spec.pad_top
    safe_bottom = box_y + box_height - spec.pad_bottom
    usable_height = max(0.0, safe_bottom - safe_top)

    changed = False
    blocks = [PADDING.estimate_text_block(text_el, PADDING.default_font_size(text_el)) for text_el in spec.texts]
    gaps: list[float] = []
    for index in range(1, len(blocks)):
        previous = blocks[index - 1]
        current = blocks[index]
        gaps.append(max(6.0, current.top - previous.bottom))

    stack_height = PADDING.stack_height_of(blocks)
    cursor = safe_top + max((usable_height - stack_height) / 2.0, 0.0)

    for index, text_el in enumerate(spec.texts):
        anchor = (text_el.get("text-anchor") or "").strip()
        if anchor == "middle":
            target_x = box_x + box_width / 2.0
        elif anchor == "end":
            target_x = safe_right
        else:
            target_x = safe_left
        if abs(parse_float(text_el.get("x"), target_x) - target_x) > 0.5:
            set_text_x(text_el, target_x)
            changed = True

        size = font_size_of(text_el, PADDING.default_font_size(text_el))
        target_y = cursor + size * 0.9
        if abs(parse_float(text_el.get("y"), target_y) - target_y) > 0.5:
            text_el.set("y", f"{target_y:.1f}")
            changed = True

        lines = text_lines_of(text_el)
        if len(lines) > 1:
            rewrite_text_lines(text_el, lines)

        block = PADDING.estimate_text_block(text_el, PADDING.default_font_size(text_el))
        cursor = block.bottom + (gaps[index] if index < len(gaps) else 0.0)

    return changed


def ordered_texts_for_shrink(spec) -> list[ET.Element]:
    def priority(text_el: ET.Element) -> tuple[int, float]:
        role = semantic_role(spec, text_el)
        if role == "body":
            bucket = 0
        elif role == "title":
            bucket = 1
        else:
            bucket = 2
        return bucket, -current_text_width(text_el)

    return sorted(spec.texts, key=priority)


def fit_container(spec, root: ET.Element, group_map: dict[str, ET.Element], stats: FitStats) -> bool:
    rect = spec.rect
    box_width = parse_float(rect.get("width"), 0.0)
    usable_width = max(0.0, box_width - spec.pad_x * 2.0)
    changed = False

    for text_el in spec.texts:
        if wrap_text_element(spec, text_el, usable_width):
            stats.wrapped += 1
            changed = True

    if changed and recenter_container(spec):
        stats.recentered += 1

    max_rounds = 10
    for _ in range(max_rounds):
        report = PADDING.inspect_container(spec)
        if not report.failures:
            break

        changed_this_round = False
        if recenter_container(spec):
            stats.recentered += 1
            changed = True
            changed_this_round = True
            continue

        for text_el in ordered_texts_for_shrink(spec):
            needs_width_help = is_horizontal_overflow(text_el, spec)
            needs_height_help = report.stack_height > (report.box_height - spec.pad_top - spec.pad_bottom)
            if not needs_width_help and not needs_height_help:
                continue
            if shrink_text(spec, text_el):
                stats.shrunk += 1
                changed = True
                changed_this_round = True
                if wrap_text_element(spec, text_el, usable_width):
                    stats.wrapped += 1
                break

        if not changed_this_round:
            if try_safe_grow(spec, root, group_map, stats):
                changed = True
                changed_this_round = True
            else:
                break

        if recenter_container(spec):
            stats.recentered += 1

    return changed


def register_default_namespace(root: ET.Element) -> None:
    if root.tag.startswith("{") and "}" in root.tag:
        namespace = root.tag[1:].split("}", 1)[0]
        ET.register_namespace("", namespace)


def parse_args(argv: list[str]) -> Path:
    args = argv[1:]
    if len(args) != 1:
        usage()
        raise SystemExit(2)
    return Path(args[0])


def main() -> int:
    path = parse_args(sys.argv)
    if not path.is_file():
        print(f"ERROR: File not found: {path}")
        return 2

    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        print(f"ERROR: XML parse failed: {exc}")
        return 1

    root = tree.getroot()
    page_area = viewbox_area(root)
    containers = PADDING.collect_containers(root)
    stats = FitStats()

    group_map = collect_container_groups(root)
    for spec in containers:
        if is_large_implicit_container(spec, page_area):
            continue
        if fit_container(spec, root, group_map, stats):
            stats.touched_containers += 1

    if stats.touched_containers == 0:
        print(f"Auto-fit: no text adjustments needed for {path}")
        return 0

    register_default_namespace(root)
    tree.write(path, encoding="utf-8", xml_declaration=True)
    print(
        "Auto-fit:"
        f" updated {stats.touched_containers} containers"
        f" (wrapped {stats.wrapped}, shrunk {stats.shrunk}, grown {stats.grown}, re-centered {stats.recentered}) in {path}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
