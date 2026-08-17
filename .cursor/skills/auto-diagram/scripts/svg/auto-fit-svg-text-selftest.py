#!/usr/bin/env python3
"""Regression selftest for SVG auto-fit text pass."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
FIXTURES = [
    ROOT_DIR / "assets" / "regression" / "font-fit-overflow.svg",
    ROOT_DIR / "assets" / "regression" / "font-fit-grow-overflow.svg",
]
AUTO_FIT = ROOT_DIR / "scripts" / "svg" / "auto-fit-svg-text.py"
PADDING_CHECK = ROOT_DIR / "scripts" / "quality" / "check-svg-node-padding.py"


def main() -> int:
    for fixture in FIXTURES:
        if not fixture.is_file():
            print(f"ERROR: Fixture not found: {fixture}")
            return 2

    with tempfile.TemporaryDirectory(prefix="auto-diagram-font-fit-") as temp_dir:
        for index, fixture in enumerate(FIXTURES, start=1):
            temp_svg = Path(temp_dir) / f"fixture-{index}.svg"
            shutil.copyfile(fixture, temp_svg)

            subprocess.run([sys.executable, str(AUTO_FIT), str(temp_svg)], check=True)
            subprocess.run([sys.executable, str(PADDING_CHECK), str(temp_svg)], check=True)

    print("OK: auto-fit-svg-text selftest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
