#!/usr/bin/env python3
"""Soft layout-rhythm checks for auto-diagram SVGs.

This script focuses on design quality instead of hard geometry failures.
It reports:
- WARNING: likely quality issues worth fixing before delivery
- DESIGN_HINT: softer composition suggestions

It exits non-zero only for usage / parse failures unless
AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING=1 is set and warnings are found.
"""

from __future__ import annotations

import math
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from svg_quality_lib import (
    NodeBox,
    RectBox,
    collect_group_boxes,
    collect_nodes,
    collect_stage_boxes,
    horizontal_gap,
    vertical_gap,
)


def cluster_positions(values: list[tuple[float, NodeBox]], tolerance: float) -> list[list[NodeBox]]:
    if not values:
        return []

    ordered = sorted(values, key=lambda item: item[0])
    clusters: list[list[NodeBox]] = [[ordered[0][1]]]
    anchors = [ordered[0][0]]
    for pos, node in ordered[1:]:
        if abs(pos - anchors[-1]) <= tolerance:
            clusters[-1].append(node)
            anchors[-1] = sum(item[0] for item in ordered if item[1] in clusters[-1]) / len(
                clusters[-1]
            )
        else:
            clusters.append([node])
            anchors.append(pos)
    return clusters


def build_clusters(nodes: list[NodeBox], axis: str) -> list[list[NodeBox]]:
    explicit_key = "row" if axis == "row" else "col"
    explicit: dict[str, list[NodeBox]] = {}
    implicit: list[NodeBox] = []
    for node in nodes:
        value = getattr(node, explicit_key)
        if value:
            explicit.setdefault(value, []).append(node)
        else:
            implicit.append(node)

    result = list(explicit.values())
    if implicit:
        if axis == "row":
            tolerance = max(
                8.0,
                min(24.0, sum(node.height for node in implicit) / len(implicit) * 0.18),
            )
            values = [(node.center_y, node) for node in implicit]
        else:
            tolerance = max(
                8.0,
                min(24.0, sum(node.width for node in implicit) / len(implicit) * 0.18),
            )
            values = [(node.center_x, node) for node in implicit]
        result.extend(cluster_positions(values, tolerance))
    return [cluster for cluster in result if len(cluster) >= 2]


def core_nodes_of(nodes: list[NodeBox]) -> list[NodeBox]:
    return [node for node in nodes if node.box_kind == "node" and node.role != "annotation"]


def collect_layout_warnings(nodes: list[NodeBox]) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    hints: list[str] = []

    core_nodes = core_nodes_of(nodes)
    if len(core_nodes) < 2:
        return warnings, hints

    row_clusters = build_clusters(core_nodes, "row")
    for row in row_clusters:
        spread = max(node.y for node in row) - min(node.y for node in row)
        if spread > 10.0:
            warnings.append(
                f"Row alignment drift: nodes {[node.node_id for node in row]} differ by {spread:.1f}px on top alignment."
            )

        gaps: list[float] = []
        ordered = sorted(row, key=lambda node: node.x)
        for left, right in zip(ordered, ordered[1:]):
            gaps.append(right.x - left.right)
        if len(gaps) >= 2:
            gap_spread = max(gaps) - min(gaps)
            if gap_spread > 22.0:
                warnings.append(
                    f"Row spacing inconsistency: gaps in row {[node.node_id for node in ordered]} vary by {gap_spread:.1f}px."
                )
            elif gap_spread > 12.0:
                hints.append(
                    f"Row spacing could be tighter: gaps in row {[node.node_id for node in ordered]} vary by {gap_spread:.1f}px."
                )

    col_clusters = build_clusters(core_nodes, "col")
    for col in col_clusters:
        spread = max(node.center_x for node in col) - min(node.center_x for node in col)
        if spread > 10.0:
            warnings.append(
                f"Column alignment drift: nodes {[node.node_id for node in col]} differ by {spread:.1f}px on center alignment."
            )

        gaps: list[float] = []
        ordered = sorted(col, key=lambda node: node.y)
        for top, bottom in zip(ordered, ordered[1:]):
            gaps.append(bottom.y - top.bottom)
        if len(gaps) >= 2:
            gap_spread = max(gaps) - min(gaps)
            if gap_spread > 22.0:
                warnings.append(
                    f"Column spacing inconsistency: gaps in column {[node.node_id for node in ordered]} vary by {gap_spread:.1f}px."
                )
            elif gap_spread > 12.0:
                hints.append(
                    f"Column spacing could be normalized: gaps in column {[node.node_id for node in ordered]} vary by {gap_spread:.1f}px."
                )

    return warnings, hints


def collect_inter_node_clearance_feedback(nodes: list[NodeBox]) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    hints: list[str] = []
    core_nodes = core_nodes_of(nodes)

    for idx, left in enumerate(core_nodes):
        for right in core_nodes[idx + 1 :]:
            x_overlap = min(left.right, right.right) - max(left.x, right.x)
            y_overlap = min(left.bottom, right.bottom) - max(left.y, right.y)
            gap_x = horizontal_gap(left, right)
            gap_y = vertical_gap(left, right)

            if y_overlap > min(left.height, right.height) * 0.28 and 0.0 <= gap_x < 18.0:
                if gap_x < 12.0:
                    warnings.append(
                        f"Nodes '{left.node_id}' and '{right.node_id}' feel horizontally cramped: gutter is only {gap_x:.1f}px."
                    )
                else:
                    hints.append(
                        f"Nodes '{left.node_id}' and '{right.node_id}' are close horizontally: gutter is {gap_x:.1f}px."
                    )

            if x_overlap > min(left.width, right.width) * 0.28 and 0.0 <= gap_y < 18.0:
                if gap_y < 12.0:
                    warnings.append(
                        f"Nodes '{left.node_id}' and '{right.node_id}' feel vertically cramped: gutter is only {gap_y:.1f}px."
                    )
                else:
                    hints.append(
                        f"Nodes '{left.node_id}' and '{right.node_id}' are close vertically: gutter is {gap_y:.1f}px."
                    )

    return warnings, hints


def collect_group_padding_feedback(
    nodes: list[NodeBox], groups: dict[str, RectBox]
) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    hints: list[str] = []
    by_group: dict[str, list[NodeBox]] = {}
    for node in nodes:
        if node.group_id:
            by_group.setdefault(node.group_id, []).append(node)

    for group_id, group_nodes in by_group.items():
        group = groups.get(group_id)
        if group is None or not group_nodes:
            continue

        left = min(node.x for node in group_nodes) - group.x
        right = group.right - max(node.right for node in group_nodes)
        top = min(node.y for node in group_nodes) - group.y
        bottom = group.bottom - max(node.bottom for node in group_nodes)
        min_gutter = min(left, right, top, bottom)

        if min_gutter < 18.0:
            warnings.append(
                f"Group '{group_id}' feels cramped: minimum inner gutter is {min_gutter:.1f}px."
            )

        if abs(left - right) > 36.0:
            hints.append(
                f"Group '{group_id}' has left/right imbalance ({left:.1f}px vs {right:.1f}px padding)."
            )
        if abs(top - bottom) > 42.0:
            hints.append(
                f"Group '{group_id}' has top/bottom imbalance ({top:.1f}px vs {bottom:.1f}px padding)."
            )

    return warnings, hints


def collect_stage_balance_feedback(
    nodes: list[NodeBox], stages: dict[str, RectBox]
) -> tuple[list[str], list[str]]:
    warnings: list[str] = []
    hints: list[str] = []
    by_stage: dict[str, list[NodeBox]] = {}
    for node in nodes:
        if node.stage_id:
            by_stage.setdefault(node.stage_id, []).append(node)

    if not by_stage and len(stages) == 1:
        stage_id = next(iter(stages))
        by_stage[stage_id] = nodes

    for stage_id, stage_nodes in by_stage.items():
        stage = stages.get(stage_id)
        if stage is None or not stage_nodes:
            continue

        total_area = sum(node.area for node in stage_nodes)
        if total_area <= 0:
            continue

        centroid_x = sum(node.center_x * node.area for node in stage_nodes) / total_area
        centroid_y = sum(node.center_y * node.area for node in stage_nodes) / total_area
        dx = abs(centroid_x - stage.center_x)
        dy = abs(centroid_y - stage.center_y)

        if dx > stage.width * 0.14:
            warnings.append(
                f"Stage '{stage_id}' has horizontal weight imbalance: visual centroid shifts {dx:.1f}px from center."
            )
        elif dx > stage.width * 0.09:
            hints.append(
                f"Stage '{stage_id}' leans horizontally by {dx:.1f}px; consider redistributing node weight."
            )

        if dy > stage.height * 0.16:
            warnings.append(
                f"Stage '{stage_id}' has vertical weight imbalance: visual centroid shifts {dy:.1f}px from center."
            )
        elif dy > stage.height * 0.10:
            hints.append(
                f"Stage '{stage_id}' leans vertically by {dy:.1f}px; consider reducing top/bottom density skew."
            )

        quadrants = [0.0, 0.0, 0.0, 0.0]
        for node in stage_nodes:
            idx = 0
            if node.center_x >= stage.center_x:
                idx += 1
            if node.center_y >= stage.center_y:
                idx += 2
            quadrants[idx] += node.area
        non_zero = [value for value in quadrants if value > 0]
        if len(non_zero) >= 2:
            hotspot_ratio = max(non_zero) / min(non_zero)
            if hotspot_ratio > 3.2:
                hints.append(
                    f"Stage '{stage_id}' has a density hotspot: busiest quadrant is {hotspot_ratio:.1f}x heavier than the lightest occupied quadrant."
                )

    return warnings, hints


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: check-layout-rhythm.py <svg-file>")
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

    nodes = collect_nodes(root)
    groups = collect_group_boxes(root)
    stages = collect_stage_boxes(root)

    warnings: list[str] = []
    hints: list[str] = []

    layout_warnings, layout_hints = collect_layout_warnings(nodes)
    warnings.extend(layout_warnings)
    hints.extend(layout_hints)

    clearance_warnings, clearance_hints = collect_inter_node_clearance_feedback(nodes)
    warnings.extend(clearance_warnings)
    hints.extend(clearance_hints)

    group_warnings, group_hints = collect_group_padding_feedback(nodes, groups)
    warnings.extend(group_warnings)
    hints.extend(group_hints)

    stage_warnings, stage_hints = collect_stage_balance_feedback(nodes, stages)
    warnings.extend(stage_warnings)
    hints.extend(stage_hints)

    print(f"Layout Rhythm: {path}")
    if warnings:
        for warning in warnings:
            print(f"WARNING: {warning}")
    if hints:
        for hint in hints:
            print(f"DESIGN_HINT: {hint}")
    if not warnings and not hints:
        print("OK: Layout rhythm checks found no obvious spacing or balance issues.")

    strict_mode = os.getenv("AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING") or os.getenv(
        "AUTO" + "_" + "DIAGRAM" + "_FAIL_ON_DESIGN_WARNING"
    )
    if warnings and strict_mode == "1":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
