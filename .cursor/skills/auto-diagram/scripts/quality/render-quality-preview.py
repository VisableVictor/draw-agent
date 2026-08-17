#!/usr/bin/env python3
"""Create a per-round preview artifact for quality repair loops.

Usage:
  python3 scripts/quality/render-quality-preview.py <svg-file> --stage hard --round 1

The script snapshots the current SVG and, when rsvg-convert is available, also
renders a PNG preview. It prints a user-facing markdown block so agents can show
either an inline image or artifact links during Q3 effect preview.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a per-round quality preview artifact.")
    parser.add_argument("svg_file", help="Current SVG file to snapshot.")
    parser.add_argument("--stage", required=True, help="Internal quality stage label, e.g. hard or soft.")
    parser.add_argument("--round", required=True, type=int, help="Current quality loop round number.")
    parser.add_argument("--label", default="preview", help="Short label for the snapshot filename.")
    parser.add_argument("--width", default="1600", help="PNG render width passed to rsvg-convert.")
    parser.add_argument("--out-dir", help="Output directory. Defaults to <svg-parent>/quality-preview.")
    return parser.parse_args()


def slug(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-")
    return cleaned or "preview"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def render_png(snapshot_svg: Path, png_path: Path, width: str) -> list[str]:
    warnings: list[str] = []
    materialized_svg = png_path.with_suffix(".raster.svg")
    try:
        node = shutil.which("node")
        if not node:
            return ["WARNING: node not found; PNG preview skipped."]
        materialize_cmd = [
            node,
            str(ROOT / "scripts/svg/materialize-css-vars.cjs"),
            str(snapshot_svg),
            str(materialized_svg),
        ]
        materialize = run(materialize_cmd)
        if materialize.returncode != 0:
            return [
                "WARNING: CSS variable materialization failed; PNG preview skipped.",
                *materialize.stdout.splitlines(),
                *materialize.stderr.splitlines(),
            ]

        rsvg = shutil.which("rsvg-convert")
        if not rsvg:
            return ["WARNING: rsvg-convert not found; PNG preview skipped."]
        convert = run([rsvg, "-w", str(width), str(materialized_svg), "-o", str(png_path)])
        if convert.returncode != 0:
            warnings.extend(
                [
                    "WARNING: PNG preview render failed.",
                    *convert.stdout.splitlines(),
                    *convert.stderr.splitlines(),
                ]
            )
            png_path.unlink(missing_ok=True)
    finally:
        materialized_svg.unlink(missing_ok=True)
    return warnings


def markdown_link(label: str, path: Path) -> str:
    target = str(path)
    if any(char.isspace() for char in target):
        return f"[{label}](<{target}>)"
    return f"[{label}]({target})"


def main() -> int:
    args = parse_args()
    source_svg = Path(args.svg_file).resolve()
    if not source_svg.is_file():
        print(f"ERROR: file not found: {source_svg}")
        return 2
    if source_svg.suffix.lower() != ".svg":
        print(f"ERROR: expected an .svg file: {source_svg}")
        return 2

    out_dir = Path(args.out_dir).resolve() if args.out_dir else source_svg.parent / "quality-preview"
    out_dir.mkdir(parents=True, exist_ok=True)

    suffix = f"{slug(args.stage)}-r{args.round:02d}-{slug(args.label)}"
    snapshot_svg = out_dir / f"{source_svg.stem}.{suffix}.svg"
    png_path = snapshot_svg.with_suffix(".png")
    shutil.copyfile(source_svg, snapshot_svg)

    warnings = render_png(snapshot_svg, png_path, args.width)

    print("质量闸门 Q3/5｜效果预览")
    print(f"SVG: {snapshot_svg}")
    if png_path.exists():
        print(f"PNG: {png_path}")
    for warning in warnings:
        print(warning)

    print("")
    print("User-facing block:")
    print("🖼️ 质量闸门 Q3/5｜效果预览")
    if png_path.exists():
        print(f"![quality preview]({png_path})")
        print(f"- PNG: {markdown_link(png_path.name, png_path)}")
    else:
        print("- PNG: 未生成，使用 SVG 快照链接查看当前效果")
    print(f"- SVG: {markdown_link(snapshot_svg.name, snapshot_svg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
