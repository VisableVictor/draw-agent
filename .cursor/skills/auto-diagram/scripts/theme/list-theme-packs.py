#!/usr/bin/env python3
"""List available auto-diagram theme packs.

Usage:
  python3 scripts/theme/list-theme-packs.py
  python3 scripts/theme/list-theme-packs.py --count
  python3 scripts/theme/list-theme-packs.py --details
  python3 scripts/theme/list-theme-packs.py --json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = ROOT / "assets" / "themes"
VISIBLE_STATUSES = {"default", "available"}


def load_theme(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    data["_path"] = str(path.relative_to(ROOT))
    return data


def sort_key(theme: dict) -> tuple[int, str, str]:
    status_rank = 0 if theme.get("status") == "default" else 1
    kind_rank = 0 if theme.get("kind") == "builtin" else 1
    return (status_rank, kind_rank, theme.get("display_name", theme.get("id", "")))


def collect_themes(include_draft: bool) -> list[dict]:
    themes: list[dict] = []
    if not THEMES_DIR.exists():
        return themes
    for pack_file in sorted(THEMES_DIR.glob("*/theme-pack.json")):
        theme = load_theme(pack_file)
        if include_draft or theme.get("status") in VISIBLE_STATUSES:
            themes.append(theme)
    return sorted(themes, key=sort_key)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="List available auto-diagram theme packs.")
    parser.add_argument("--count", action="store_true", help="Print only the visible theme pack count.")
    parser.add_argument("--details", action="store_true", help="Print one theme pack per line with details.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    parser.add_argument("--include-draft", action="store_true", help="Include draft theme packs.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    themes = collect_themes(args.include_draft)

    if args.count:
        print(len(themes))
        return 0

    if args.json:
        print(json.dumps(themes, ensure_ascii=False, indent=2))
        return 0

    if args.details:
        for theme in themes:
            print(
                f"{theme['id']}\t{theme['display_name']}\t"
                f"{theme['kind']}/{theme['status']}\t{theme.get('summary', '')}"
            )
        return 0

    print(f"{len(themes)} theme packs available")
    for theme in themes:
        print(f"- {theme['display_name']} ({theme['id']}): {theme.get('summary', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
