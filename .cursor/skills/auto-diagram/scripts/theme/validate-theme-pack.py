#!/usr/bin/env python3
"""Validate auto-diagram theme pack JSON files.

Usage:
  python3 scripts/theme/validate-theme-pack.py
  python3 scripts/theme/validate-theme-pack.py assets/themes/default-dark-architecture/theme-pack.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = ROOT / "assets" / "themes"
PACK_DOCS_DIR = ROOT / "references" / "themes" / "packs"
ALLOWED_KINDS = {"builtin", "learned"}
ALLOWED_STATUSES = {"default", "available", "draft"}
REQUIRED_TOP_LEVEL = [
    "id",
    "display_name",
    "kind",
    "status",
    "summary",
    "source",
    "recommended_for",
    "default_when",
    "avoid_for",
    "tokens",
    "soft_hints",
]
REQUIRED_TOKEN_SECTIONS = [
    "background",
    "semantic_roles",
    "typography",
    "spacing",
    "shape",
    "lines",
    "chrome",
]
REQUIRED_SEMANTIC_ROLES = [
    "frontend",
    "backend",
    "database",
    "cloud",
    "security",
    "external",
    "message_bus",
]
REQUIRED_TYPE_STYLES = [
    "title",
    "subtitle",
    "group_title",
    "node_title",
    "node_body",
    "note_title",
    "note_body",
    "edge_label",
    "legend",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate auto-diagram theme packs.")
    parser.add_argument("paths", nargs="*", help="Optional theme-pack.json paths.")
    return parser.parse_args()


def iter_targets(paths: list[str]) -> list[Path]:
    if paths:
        return [Path(path).resolve() for path in paths]
    return sorted(THEMES_DIR.glob("*/theme-pack.json"))


def require_keys(obj: dict, keys: list[str], context: str, errors: list[str]) -> None:
    for key in keys:
        if key not in obj:
            errors.append(f"{context}: missing key '{key}'")


def validate_role(role_name: str, role_data: dict, errors: list[str]) -> None:
    require_keys(role_data, ["fill", "stroke", "text"], f"semantic_roles.{role_name}", errors)


def validate_typography(style_name: str, style_data: dict, errors: list[str]) -> None:
    require_keys(style_data, ["size", "weight", "letter_spacing_em"], f"typography.{style_name}", errors)


def validate_theme(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - defensive
        return [f"{path}: invalid JSON ({exc})"]

    require_keys(data, REQUIRED_TOP_LEVEL, str(path), errors)
    if errors:
        return errors

    if data["kind"] not in ALLOWED_KINDS:
        errors.append(f"{path}: kind must be one of {sorted(ALLOWED_KINDS)}")
    if data["status"] not in ALLOWED_STATUSES:
        errors.append(f"{path}: status must be one of {sorted(ALLOWED_STATUSES)}")
    if path.parent.name != data["id"]:
        errors.append(f"{path}: parent directory '{path.parent.name}' must match id '{data['id']}'")

    if not isinstance(data["recommended_for"], list):
        errors.append(f"{path}: recommended_for must be a list")
    if not isinstance(data["default_when"], list):
        errors.append(f"{path}: default_when must be a list")
    if not isinstance(data["avoid_for"], list):
        errors.append(f"{path}: avoid_for must be a list")

    source = data["source"]
    if not isinstance(source, dict):
        errors.append(f"{path}: source must be an object")
    else:
        require_keys(source, ["origin", "notes"], "source", errors)

    pack_doc = PACK_DOCS_DIR / f"{data['id']}.md"
    if not pack_doc.exists():
        errors.append(f"{path}: missing pack doc '{pack_doc.relative_to(ROOT)}'")

    preview_asset = data.get("preview_asset")
    if preview_asset:
        preview_path = ROOT / preview_asset
        if not preview_path.exists():
            errors.append(f"{path}: preview_asset not found at '{preview_asset}'")

    tokens = data["tokens"]
    if not isinstance(tokens, dict):
        errors.append(f"{path}: tokens must be an object")
        return errors

    require_keys(tokens, REQUIRED_TOKEN_SECTIONS, "tokens", errors)

    background = tokens.get("background", {})
    require_keys(
        background,
        [
            "page",
            "surface",
            "canvas",
            "grid",
            "stage_fill",
            "stage_stroke",
            "title",
            "subtitle",
            "text_primary",
            "text_secondary",
            "edge",
            "edge_label",
        ],
        "tokens.background",
        errors,
    )

    semantic_roles = tokens.get("semantic_roles", {})
    for role_name in REQUIRED_SEMANTIC_ROLES:
        if role_name not in semantic_roles:
            errors.append(f"tokens.semantic_roles: missing role '{role_name}'")
            continue
        validate_role(role_name, semantic_roles[role_name], errors)

    typography = tokens.get("typography", {})
    if "families" not in typography or not isinstance(typography.get("families"), list):
        errors.append("tokens.typography: missing list key 'families'")
    for style_name in REQUIRED_TYPE_STYLES:
        if style_name not in typography:
            errors.append(f"tokens.typography: missing style '{style_name}'")
            continue
        validate_typography(style_name, typography[style_name], errors)

    require_keys(
        tokens.get("spacing", {}),
        [
            "diagram_padding",
            "stage_padding",
            "group_padding",
            "component_min_gap_y",
            "legend_gap_y",
            "card_gap",
            "node_pad_x",
            "node_pad_top",
            "node_pad_bottom",
        ],
        "tokens.spacing",
        errors,
    )
    require_keys(
        tokens.get("shape", {}),
        ["node_radius", "group_radius", "stage_radius", "card_radius"],
        "tokens.shape",
        errors,
    )
    require_keys(
        tokens.get("lines", {}),
        [
            "stroke_width",
            "boundary_dash",
            "security_dash",
            "auth_dash",
            "arrow_marker_width",
            "arrow_marker_height",
            "arrow_color",
            "edge_label_backplate",
        ],
        "tokens.lines",
        errors,
    )
    require_keys(
        tokens.get("chrome", {}),
        [
            "html_shell",
            "header_pulse",
            "summary_cards",
            "footer",
            "grid_background",
            "opaque_node_mask",
        ],
        "tokens.chrome",
        errors,
    )

    soft_hints = data.get("soft_hints", {})
    require_keys(
        soft_hints,
        ["mood", "density_bias", "annotation_style", "style_summary_seed", "allowed_overrides", "avoid"],
        "soft_hints",
        errors,
    )
    return errors


def main() -> int:
    args = parse_args()
    targets = iter_targets(args.paths)
    if not targets:
        print("No theme packs found.")
        return 1

    all_errors: list[str] = []
    for target in targets:
        errors = validate_theme(target)
        if errors:
            all_errors.extend(errors)
        else:
            print(f"OK: {target.relative_to(ROOT)}")

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
