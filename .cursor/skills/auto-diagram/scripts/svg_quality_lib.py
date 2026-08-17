#!/usr/bin/env python3
"""Shared SVG geometry and extraction helpers for auto-diagram quality checks."""

from __future__ import annotations

from typing import Protocol
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass

PATH_TOKEN_RE = re.compile(r"[A-Za-z]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")
URL_REF_RE = re.compile(r"url\(#([^)]+)\)")


class BoxLike(Protocol):
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float: ...

    @property
    def bottom(self) -> float: ...


@dataclass
class RectBox:
    node_id: str
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    @property
    def center_x(self) -> float:
        return self.x + self.width / 2.0

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2.0

    @property
    def area(self) -> float:
        return self.width * self.height

    def overlaps(self, other: "RectBox") -> bool:
        return not (
            self.right <= other.x
            or other.right <= self.x
            or self.bottom <= other.y
            or other.bottom <= self.y
        )

    def contains(self, other: "RectBox", margin: float = 0.0) -> bool:
        return (
            other.x >= self.x + margin
            and other.y >= self.y + margin
            and other.right <= self.right - margin
            and other.bottom <= self.bottom - margin
        )

    def contains_point(self, x: float, y: float, margin: float = 0.0) -> bool:
        return (
            self.x + margin <= x <= self.right - margin
            and self.y + margin <= y <= self.bottom - margin
        )

    def inset(self, margin: float) -> "RectBox":
        return RectBox(
            node_id=self.node_id,
            x=self.x + margin,
            y=self.y + margin,
            width=max(0.0, self.width - margin * 2),
            height=max(0.0, self.height - margin * 2),
        )


@dataclass
class NodeBox(RectBox):
    group_id: str | None = None
    stage_id: str | None = None
    role: str | None = None
    row: str | None = None
    col: str | None = None
    flow_level: str | None = None
    box_kind: str = "node"


@dataclass
class TextBox:
    label: str
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height

    def overlaps_rect(self, rect: RectBox) -> bool:
        return not (
            self.right <= rect.x
            or rect.right <= self.x
            or self.bottom <= rect.y
            or rect.bottom <= self.y
        )

    def overlaps_text(self, other: "TextBox") -> bool:
        return not (
            self.right <= other.x
            or other.right <= self.x
            or self.bottom <= other.y
            or other.bottom <= self.y
        )


def boxes_overlap(left: BoxLike, right: BoxLike, clearance: float = 0.0) -> bool:
    return not (
        left.right + clearance <= right.x
        or right.right + clearance <= left.x
        or left.bottom + clearance <= right.y
        or right.bottom + clearance <= left.y
    )


def horizontal_gap(left: BoxLike, right: BoxLike) -> float:
    if left.right <= right.x:
        return right.x - left.right
    if right.right <= left.x:
        return left.x - right.right
    return -min(left.right - right.x, right.right - left.x)


def vertical_gap(left: BoxLike, right: BoxLike) -> float:
    if left.bottom <= right.y:
        return right.y - left.bottom
    if right.bottom <= left.y:
        return left.y - right.bottom
    return -min(left.bottom - right.y, right.bottom - left.y)


def point_hits_box(x: float, y: float, box: BoxLike, margin: float = 0.0) -> bool:
    return (
        box.x - margin <= x <= box.right + margin
        and box.y - margin <= y <= box.bottom + margin
    )


def classes_of(el: ET.Element) -> set[str]:
    return set((el.get("class") or "").split())


def parse_float(value: str | None, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def font_size_of(el: ET.Element, default: float) -> float:
    direct = el.get("font-size")
    if direct:
        return parse_float(direct.replace("px", ""), default)
    style = el.get("style") or ""
    for part in style.split(";"):
        if "font-size" in part:
            _, _, value = part.partition(":")
            return parse_float(value.strip().replace("px", ""), default)
    return default


def line_height_of(el: ET.Element, font_size: float) -> float:
    direct = el.get("line-height")
    if direct:
        return parse_float(direct.replace("px", ""), font_size * 1.35)
    style = el.get("style") or ""
    for part in style.split(";"):
        if "line-height" in part:
            _, _, value = part.partition(":")
            cleaned = value.strip().replace("px", "")
            if cleaned.endswith("%"):
                return font_size * parse_float(cleaned[:-1], 135.0) / 100.0
            return parse_float(cleaned, font_size * 1.35)
    return font_size * 1.35


def visual_units(text: str) -> float:
    total = 0.0
    for ch in text:
        if ch.isspace():
            total += 0.35
        elif unicodedata.east_asian_width(ch) in {"W", "F"}:
            total += 1.0
        elif ch.isupper():
            total += 0.68
        else:
            total += 0.58
    return total


def text_lines_of(el: ET.Element) -> list[str]:
    tspan_lines = []
    for child in list(el):
        if child.tag.endswith("tspan"):
            text = "".join(child.itertext()).strip()
            if text:
                tspan_lines.append(text)
    if tspan_lines:
        return tspan_lines

    text = "".join(el.itertext()).strip()
    if not text:
        return []
    lines = [line.strip() for line in re.split(r"\n+", text) if line.strip()]
    return lines or [text]


def has_explicit_wrap(el: ET.Element) -> bool:
    if any(child.tag.endswith("tspan") for child in list(el)):
        return True
    return "\n" in "".join(el.itertext())


def text_bbox(el: ET.Element, default_size: float) -> TextBox | None:
    lines = text_lines_of(el)
    if not lines:
        return None
    size = font_size_of(el, default_size)
    width = max(visual_units(line) for line in lines) * size
    height = len(lines) * line_height_of(el, size)
    x = parse_float(el.get("x"))
    y = parse_float(el.get("y"))
    anchor = (el.get("text-anchor") or "").strip()
    if anchor == "middle":
        left = x - width / 2.0
    elif anchor == "end":
        left = x - width
    else:
        left = x
    top = y - size * 0.9
    return TextBox(label=" / ".join(lines), x=left, y=top, width=width, height=height)


def collect_ids(root: ET.Element) -> set[str]:
    ids: set[str] = set()
    for el in root.iter():
        el_id = el.get("id")
        if el_id:
            ids.add(el_id)
    return ids


def collect_url_refs(root: ET.Element) -> list[tuple[str, str]]:
    refs: list[tuple[str, str]] = []
    for el in root.iter():
        for attr_name, attr_value in el.attrib.items():
            match = URL_REF_RE.search(attr_value)
            if match:
                refs.append((attr_name, match.group(1)))
    return refs


def collect_markers(root: ET.Element) -> list[ET.Element]:
    return [el for el in root.iter() if el.tag.endswith("marker")]


def _collect_box(
    group: ET.Element,
    node_id: str,
    allowed_classes: tuple[str, ...],
) -> tuple[ET.Element | None, str]:
    rect = None
    box_kind = "node"
    for child in list(group):
        if not child.tag.endswith("rect"):
            continue
        child_classes = classes_of(child)
        if any(cls in child_classes for cls in allowed_classes):
            rect = child
            if "ad-note-box" in child_classes:
                box_kind = "annotation"
            break
    return rect, box_kind


def infer_container_id(box: RectBox, containers: dict[str, RectBox]) -> str | None:
    candidates = [
        container
        for container in containers.values()
        if container.contains_point(box.center_x, box.center_y)
    ]
    if not candidates:
        return None
    # Prefer the smallest enclosing container so local nesting wins over outer wrappers.
    return min(candidates, key=lambda item: item.area).node_id


def collect_nodes(root: ET.Element, include_annotations: bool = True) -> list[NodeBox]:
    allowed_classes = ("ad-node-box", "ad-note-box") if include_annotations else ("ad-node-box",)
    group_boxes = collect_group_boxes(root)
    stage_boxes = collect_stage_boxes(root)
    nodes: list[NodeBox] = []
    for group in root.iter():
        if "ad-node" not in classes_of(group):
            continue
        node_id = group.get("data-node-id") or "unknown"
        rect, box_kind = _collect_box(group, node_id, allowed_classes)
        if rect is None:
            continue
        node = NodeBox(
            node_id=node_id,
            x=parse_float(rect.get("x")),
            y=parse_float(rect.get("y")),
            width=parse_float(rect.get("width")),
            height=parse_float(rect.get("height")),
            group_id=group.get("data-group-id"),
            stage_id=group.get("data-stage-id"),
            role=group.get("data-role"),
            row=group.get("data-row"),
            col=group.get("data-col"),
            flow_level=group.get("data-flow-level"),
            box_kind=box_kind,
        )
        if node.group_id is None:
            node.group_id = infer_container_id(node, group_boxes)
        if node.stage_id is None:
            node.stage_id = infer_container_id(node, stage_boxes)
        nodes.append(node)
    return nodes


def collect_group_boxes(root: ET.Element) -> dict[str, RectBox]:
    groups: dict[str, RectBox] = {}
    for group in root.iter():
        if "ad-group" not in classes_of(group):
            continue
        group_id = group.get("data-group-id")
        if not group_id:
            continue
        for child in list(group):
            if child.tag.endswith("rect") and "ad-group-box" in classes_of(child):
                groups[group_id] = RectBox(
                    node_id=group_id,
                    x=parse_float(child.get("x")),
                    y=parse_float(child.get("y")),
                    width=parse_float(child.get("width")),
                    height=parse_float(child.get("height")),
                )
                break
    return groups


def collect_stage_boxes(root: ET.Element) -> dict[str, RectBox]:
    stages: dict[str, RectBox] = {}
    for group in root.iter():
        group_classes = classes_of(group)
        if "ad-stage" not in group_classes and group.get("data-stage-id") is None:
            continue
        stage_id = group.get("data-stage-id")
        if not stage_id:
            continue
        for child in list(group):
            if child.tag.endswith("rect") and "ad-stage-box" in classes_of(child):
                stages[stage_id] = RectBox(
                    node_id=stage_id,
                    x=parse_float(child.get("x")),
                    y=parse_float(child.get("y")),
                    width=parse_float(child.get("width")),
                    height=parse_float(child.get("height")),
                )
                break
    if stages:
        return stages
    for el in root.iter():
        if not el.tag.endswith("rect"):
            continue
        if "ad-stage-box" not in classes_of(el):
            continue
        stage_id = el.get("id")
        if not stage_id:
            continue
        stages[stage_id] = RectBox(
            node_id=stage_id,
            x=parse_float(el.get("x")),
            y=parse_float(el.get("y")),
            width=parse_float(el.get("width")),
            height=parse_float(el.get("height")),
        )
    return stages


def collect_group_title_boxes(root: ET.Element) -> list[tuple[str, RectBox]]:
    titles: list[tuple[str, RectBox]] = []
    for group in root.iter():
        if "ad-group" not in classes_of(group):
            continue
        group_id = group.get("data-group-id") or "unknown-group"
        for child in list(group):
            if child.tag.endswith("text") and "ad-group-title" in classes_of(child):
                bbox = text_bbox(child, 13.0)
                if bbox is None:
                    continue
                titles.append(
                    (
                        group_id,
                        RectBox(
                            node_id=group_id,
                            x=bbox.x - 6.0,
                            y=bbox.y - 4.0,
                            width=bbox.width + 12.0,
                            height=bbox.height + 8.0,
                        ),
                    )
                )
    return titles


def collect_edge_label_boxes(root: ET.Element) -> list[TextBox]:
    labels: list[TextBox] = []
    for el in root.iter():
        if not el.tag.endswith("text"):
            continue
        if "ad-edge-label" not in classes_of(el):
            continue
        bbox = text_bbox(el, 12.0)
        if bbox is not None:
            labels.append(bbox)
    return labels


def parse_svg_path_segments(
    path_d: str,
) -> tuple[list[tuple[tuple[float, float], tuple[float, float]]], bool]:
    tokens = PATH_TOKEN_RE.findall(path_d)
    idx = 0
    current = (0.0, 0.0)
    start_point = (0.0, 0.0)
    last_command = ""
    segments: list[tuple[tuple[float, float], tuple[float, float]]] = []
    unsupported = False

    def next_number() -> float:
        nonlocal idx
        value = float(tokens[idx])
        idx += 1
        return value

    while idx < len(tokens):
        token = tokens[idx]
        if re.fullmatch(r"[A-Za-z]", token):
            idx += 1
            command = token
            last_command = command
        else:
            if not last_command:
                break
            command = last_command

        absolute = command.isupper()
        cmd = command.upper()

        if cmd == "M":
            x = next_number()
            y = next_number()
            current = (x, y) if absolute else (current[0] + x, current[1] + y)
            start_point = current
            while idx < len(tokens) and not re.fullmatch(r"[A-Za-z]", tokens[idx]):
                x = next_number()
                y = next_number()
                target = (x, y) if absolute else (current[0] + x, current[1] + y)
                segments.append((current, target))
                current = target
        elif cmd == "L":
            while idx < len(tokens) and not re.fullmatch(r"[A-Za-z]", tokens[idx]):
                x = next_number()
                y = next_number()
                target = (x, y) if absolute else (current[0] + x, current[1] + y)
                segments.append((current, target))
                current = target
        elif cmd == "H":
            while idx < len(tokens) and not re.fullmatch(r"[A-Za-z]", tokens[idx]):
                x = next_number()
                target = (x, current[1]) if absolute else (current[0] + x, current[1])
                segments.append((current, target))
                current = target
        elif cmd == "V":
            while idx < len(tokens) and not re.fullmatch(r"[A-Za-z]", tokens[idx]):
                y = next_number()
                target = (current[0], y) if absolute else (current[0], current[1] + y)
                segments.append((current, target))
                current = target
        elif cmd == "Z":
            segments.append((current, start_point))
            current = start_point
        else:
            unsupported = True
            break

    return segments, unsupported


def parse_path_endpoints(path_d: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
    segments, unsupported = parse_svg_path_segments(path_d)
    if unsupported or not segments:
        return None
    return segments[0][0], segments[-1][1]
