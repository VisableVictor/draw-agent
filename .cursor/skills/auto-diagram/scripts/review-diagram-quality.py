#!/usr/bin/env python3
"""Aggregate design-quality checks into internal repair actions.

This script is for the agent, not the user. It turns raw WARNING / DESIGN_HINT
 output into a prioritized internal checklist that can drive a repair loop.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SCRIPT_NAMES = [
    "check-layout-rhythm.py",
    "check-visual-hierarchy.py",
]


def run_script(script_dir: Path, script_name: str, svg_file: Path) -> tuple[list[str], list[str]]:
    cmd = ["python3", str(script_dir / script_name), str(svg_file)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"{script_name} failed")

    warnings: list[str] = []
    hints: list[str] = []
    for line in proc.stdout.splitlines():
        if line.startswith("WARNING: "):
            warnings.append(line[len("WARNING: ") :].strip())
        elif line.startswith("DESIGN_HINT: "):
            hints.append(line[len("DESIGN_HINT: ") :].strip())
    return warnings, hints


def action_for_message(message: str) -> str:
    if "feels cramped" in message:
        return "Increase container gutters by expanding the group box, reducing node widths, or moving edge nodes inward."
    if "close horizontally" in message or "close vertically" in message:
        return "Open up more local breathing room so neighboring nodes do not feel visually crowded even if they do not overlap."
    if "spacing inconsistency" in message or "spacing could be tighter" in message:
        return "Normalize spacing between sibling nodes so repeated gaps use one rhythm value."
    if "alignment drift" in message:
        return "Realign the affected row or column to a shared anchor line instead of leaving optical drift."
    if "imbalance" in message and "padding" in message:
        return "Redistribute nodes inside the group so top/bottom or left/right padding feels more even."
    if "horizontal weight imbalance" in message or "vertical weight imbalance" in message:
        return "Redistribute large nodes or notes so the visual centroid stays closer to the stage center."
    if "density hotspot" in message:
        return "Spread dense content across adjacent zones or split heavy clusters into clearer sub-groups."
    if "primary nodes" in message:
        return "Reduce the number of primary focal points or demote some nodes to secondary/support roles."
    if "Horizontal edge directions are mixed" in message or "Vertical edge directions are mixed" in message:
        return "Clarify one dominant reading direction so the narrative path feels deliberate."
    if "Annotation / note area" in message:
        return "Shrink, soften, or reposition support cards so they do not compete with the main chain."
    if "No data-role metadata" in message:
        return "Annotate nodes with data-role so hierarchy checks can distinguish primary, secondary, support, and annotation roles."
    if "No data-flow-level metadata" in message:
        return "Annotate nodes with data-flow-level so the system can validate core vs branch path emphasis."
    if "No explicit primary node" in message:
        return "Promote one core node or one core band so the viewer immediately sees the main focal point."
    return "Review this issue and adjust layout, emphasis, or spacing so the diagram reads more cleanly."


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: review-diagram-quality.py <svg-file>")
        return 2

    svg_file = Path(sys.argv[1])
    if not svg_file.is_file():
        print(f"ERROR: File not found: {svg_file}")
        return 2

    script_dir = Path(__file__).resolve().parent
    warnings: list[str] = []
    hints: list[str] = []

    for script_name in SCRIPT_NAMES:
        script_warnings, script_hints = run_script(script_dir, script_name, svg_file)
        warnings.extend(script_warnings)
        hints.extend(script_hints)

    print(f"Internal Design Review: {svg_file}")
    if not warnings and not hints:
        print("OK: No soft design issues detected.")
        return 0

    priority = 1
    for message in warnings:
        print(f"INTERNAL_ACTION {priority}: {action_for_message(message)}")
        print(f"  Trigger: {message}")
        priority += 1

    for message in hints:
        print(f"INTERNAL_HINT {priority}: {action_for_message(message)}")
        print(f"  Trigger: {message}")
        priority += 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
