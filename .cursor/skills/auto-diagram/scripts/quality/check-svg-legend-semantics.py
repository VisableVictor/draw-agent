#!/usr/bin/env python3
"""Soft-check whether differentiated edge semantics are explained clearly enough."""

from __future__ import annotations

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from svg_quality_lib import classes_of, collect_legend_boxes


PRIMARY_CHANNELS = {"", "none", "primary"}


def style_value(el: ET.Element, key: str) -> str | None:
    style = el.get("style") or ""
    for part in style.split(";"):
        name, _, value = part.partition(":")
        if name.strip() == key:
            cleaned = value.strip()
            return cleaned or None
    return None


def stroke_of(el: ET.Element) -> str | None:
    return (el.get("stroke") or style_value(el, "stroke") or "").strip() or None


def dasharray_of(el: ET.Element) -> str | None:
    return (el.get("stroke-dasharray") or style_value(el, "stroke-dasharray") or "").strip() or None


def is_edge_element(el: ET.Element) -> bool:
    return el.tag.endswith("path") and "ad-edge" in classes_of(el)


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
        print("Usage: check-svg-legend-semantics.py <svg-file>")
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

    channels: set[str] = set()
    differentiated_channels: set[str] = set()
    stroke_colors: set[str] = set()
    dashed_edges = 0
    metadata_missing = 0
    total_edges = 0

    for el in root.iter():
        if not is_edge_element(el):
            continue
        total_edges += 1
        channel = (el.get("data-edge-channel") or "").strip()
        channels.add(channel or "primary")
        if channel in PRIMARY_CHANNELS:
            if not channel:
                metadata_missing += 1
        else:
            differentiated_channels.add(channel)
        stroke = stroke_of(el)
        if stroke:
            stroke_colors.add(stroke)
        if dasharray_of(el):
            dashed_edges += 1

    legend_boxes = collect_legend_boxes(root)
    has_legend = bool(legend_boxes)

    if total_edges >= 4 and len(differentiated_channels) >= 2 and not has_legend:
        warnings.append(
            f"Diagram uses {len(differentiated_channels)} differentiated edge channels but has no page legend to explain them."
        )
    elif total_edges >= 4 and len(stroke_colors) >= 3 and not has_legend:
        warnings.append(
            f"Diagram uses {len(stroke_colors)} distinct edge colors but has no page legend to explain the semantics."
        )

    if differentiated_channels and metadata_missing:
        hints.append(
            f"{metadata_missing} edge(s) still rely on implicit primary semantics while other edges declare data-edge-channel; metadata is inconsistent."
        )

    if dashed_edges >= 2 and not has_legend:
        hints.append(
            "Multiple dashed edges are present without a legend; the viewer may not know what the dash semantics mean."
        )

    if has_legend and not differentiated_channels and len(stroke_colors) <= 1 and dashed_edges == 0:
        hints.append(
            "A page legend is present, but edge semantics are mostly uniform; check whether the footer copy is carrying its weight."
        )

    print(f"Legend Semantics: {path}")
    warnings = dedupe(warnings)
    hints = dedupe(hints)
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    if hints:
        for hint in hints:
            print(f"DESIGN_HINT: {hint}")
    if not warnings and not hints:
        print("OK: Legend semantics checks found no obvious missing explanations.")

    strict_mode = os.getenv("AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING") or os.getenv(
        "AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING"
    )
    if warnings and strict_mode == "1":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
