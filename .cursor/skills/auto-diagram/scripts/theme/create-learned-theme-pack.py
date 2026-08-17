#!/usr/bin/env python3
"""Create a learned theme pack from a base pack plus metadata and optional overrides.

Usage:
  python3 scripts/theme/create-learned-theme-pack.py \
    --name "静海蓝图" \
    --base-pack default-day-blue \
    --summary "从参考图学习出的安静蓝系汇报风格。" \
    --style-summary "低饱和白底 + 柔和蓝灰 + 留白更大 + 细描边 + 克制箭头" \
    --source-notes "Derived from a user-provided reference image after final diagram delivery." \
    --recommended-for "老板汇报" \
    --default-when "用户想要更安静的蓝系白底风格" \
    --avoid-for "夜景技术舞台"

Optional:
  --id quiet-blue-boardroom
  --token-overrides-file /path/to/overrides.json
  --soft-hints-file /path/to/hints.json
  --preview-file /path/to/preview.png
  --status available
  --dry-run
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = ROOT / "assets" / "themes"
PACK_DOCS_DIR = ROOT / "references" / "themes" / "packs"
VALIDATOR = ROOT / "scripts" / "theme" / "validate-theme-pack.py"
ALLOWED_STATUSES = {"available", "draft"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a learned auto-diagram theme pack.")
    parser.add_argument("--spec-file", help="Optional JSON file containing the learned pack spec.")
    parser.add_argument("--id", help="Theme pack id. Defaults to a slug derived from --name.")
    parser.add_argument("--name", help="Display name for the learned pack.")
    parser.add_argument("--base-pack", help="Base pack id to inherit tokens and defaults from.")
    parser.add_argument("--summary", help="One-sentence summary of the learned pack.")
    parser.add_argument("--style-summary", help="Human-readable style summary seed.")
    parser.add_argument("--source-notes", help="How the pack was learned / why it exists.")
    parser.add_argument("--source-image", help="Optional source image path or label.")
    parser.add_argument("--inspired-by", help="Optional source inspiration label.")
    parser.add_argument("--status", default=None, help="available or draft. Defaults to available.")
    parser.add_argument("--recommended-for", action="append", default=None, help="Repeatable.")
    parser.add_argument("--default-when", action="append", default=None, help="Repeatable.")
    parser.add_argument("--avoid-for", action="append", default=None, help="Repeatable.")
    parser.add_argument("--mood", action="append", default=None, help="Repeatable mood hints.")
    parser.add_argument("--density-bias", help="Override soft_hints.density_bias.")
    parser.add_argument("--annotation-style", help="Override soft_hints.annotation_style.")
    parser.add_argument("--allow-override", action="append", default=None, help="Repeatable soft hint.")
    parser.add_argument("--avoid-hint", action="append", default=None, help="Repeatable soft hint.")
    parser.add_argument("--confidence-notes", help="Optional confidence notes for guessed fields.")
    parser.add_argument("--token-overrides-file", help="JSON file with a partial tokens override object.")
    parser.add_argument("--soft-hints-file", help="JSON file with a partial soft_hints override object.")
    parser.add_argument("--preview-file", help="Optional preview asset to copy into the theme directory.")
    parser.add_argument("--notes-md", help="Optional extra markdown note block appended to the pack doc.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing pack with the same id.")
    parser.add_argument("--dry-run", action="store_true", help="Print the resolved pack payload without writing files.")
    return parser.parse_args()


def load_json_file(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    target = Path(path).expanduser().resolve()
    return json.loads(target.read_text(encoding="utf-8"))


def deep_merge(base: Any, override: Any) -> Any:
    if isinstance(base, dict) and isinstance(override, dict):
        merged = {key: copy.deepcopy(value) for key, value in base.items()}
        for key, value in override.items():
            if key in merged:
                merged[key] = deep_merge(merged[key], value)
            else:
                merged[key] = copy.deepcopy(value)
        return merged
    return copy.deepcopy(override)


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if not slug:
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
        slug = f"theme-{digest}"
    return slug


def load_base_pack(base_pack_id: str) -> dict[str, Any]:
    pack_path = THEMES_DIR / base_pack_id / "theme-pack.json"
    if not pack_path.exists():
        raise FileNotFoundError(f"Base pack not found: {pack_path}")
    return json.loads(pack_path.read_text(encoding="utf-8"))


def coalesce(spec: dict[str, Any], cli_value: Any, key: str, default: Any = None) -> Any:
    return cli_value if cli_value not in (None, []) else spec.get(key, default)


def normalize_list(value: Any, fallback: list[str] | None = None) -> list[str]:
    if value is None:
        return list(fallback or [])
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def render_pack_doc(
    theme: dict[str, Any],
    token_path: Path,
    preview_rel: str | None,
    base_pack_id: str,
    style_summary: str,
    notes_md: str | None,
) -> str:
    recommended = "\n".join(f"- {item}" for item in theme["recommended_for"])
    avoid_for = "\n".join(f"- {item}" for item in theme["avoid_for"])
    default_when = "\n".join(f"- {item}" for item in theme["default_when"])
    preview_line = (
        f"- preview：[{preview_rel}](../../../{preview_rel})\n"
        if preview_rel
        else ""
    )
    notes_block = f"\n## 额外备注\n\n{notes_md.strip()}\n" if notes_md and notes_md.strip() else ""
    return f"""# {theme["display_name"]}

## 基本信息

- `id`: `{theme["id"]}`
- `display_name`: `{theme["display_name"]}`
- `kind`: `{theme["kind"]}`
- `status`: `{theme["status"]}`
- `base_pack`: `{base_pack_id}`
- token 文件：[{token_path.relative_to(ROOT)}](../../../{token_path.relative_to(ROOT).as_posix()})
{preview_line}
## 风格摘要

`{style_summary}`

## 来源

- `origin`: `{theme["source"]["origin"]}`
- `notes`: {theme["source"]["notes"]}

## 适合什么

{recommended}

## 默认推荐场景

{default_when}

## 不适合什么

{avoid_for}

## 说明

- 这是一个 learned pack，来自参考图风格沉淀
- 它继承自 `{base_pack_id}`，并叠加了本次任务特有的风格偏移
- 当前 pack 仍然遵守 `auto-diagram` 的 spec-first 和 layout-first 原则，不替代布局判断
{notes_block}"""


def validate_required(value: Any, label: str) -> str:
    if value is None or not str(value).strip():
        raise ValueError(f"Missing required value: {label}")
    return str(value).strip()


def main() -> int:
    args = parse_args()
    spec = load_json_file(args.spec_file)

    display_name = validate_required(coalesce(spec, args.name, "name"), "--name")
    theme_id = coalesce(spec, args.id, "id")
    if theme_id:
        theme_id = slugify(str(theme_id))
    else:
        theme_id = slugify(display_name)

    base_pack_id = validate_required(coalesce(spec, args.base_pack, "base_pack"), "--base-pack")
    summary = validate_required(coalesce(spec, args.summary, "summary"), "--summary")
    style_summary = validate_required(coalesce(spec, args.style_summary, "style_summary"), "--style-summary")
    source_notes = validate_required(coalesce(spec, args.source_notes, "source_notes"), "--source-notes")
    status = coalesce(spec, args.status, "status", "available")
    if status not in ALLOWED_STATUSES:
        raise ValueError(f"--status must be one of {sorted(ALLOWED_STATUSES)}")

    base_pack = load_base_pack(base_pack_id)
    token_overrides = load_json_file(coalesce(spec, args.token_overrides_file, "token_overrides_file"))
    hints_overrides = load_json_file(coalesce(spec, args.soft_hints_file, "soft_hints_file"))

    recommended_for = normalize_list(
        coalesce(spec, args.recommended_for, "recommended_for"),
        base_pack.get("recommended_for", []),
    )
    default_when = normalize_list(
        coalesce(spec, args.default_when, "default_when"),
        base_pack.get("default_when", []),
    )
    avoid_for = normalize_list(
        coalesce(spec, args.avoid_for, "avoid_for"),
        base_pack.get("avoid_for", []),
    )

    theme_tokens = deep_merge(base_pack["tokens"], token_overrides)
    soft_hints = deep_merge(base_pack.get("soft_hints", {}), hints_overrides)

    mood = normalize_list(coalesce(spec, args.mood, "mood"), soft_hints.get("mood", []))
    allowed_overrides = normalize_list(
        coalesce(spec, args.allow_override, "allowed_overrides"),
        soft_hints.get("allowed_overrides", []),
    )
    avoid_hints = normalize_list(
        coalesce(spec, args.avoid_hint, "avoid_hints"),
        soft_hints.get("avoid", []),
    )

    soft_hints["mood"] = mood
    soft_hints["density_bias"] = coalesce(spec, args.density_bias, "density_bias", soft_hints.get("density_bias"))
    soft_hints["annotation_style"] = coalesce(
        spec,
        args.annotation_style,
        "annotation_style",
        soft_hints.get("annotation_style"),
    )
    soft_hints["style_summary_seed"] = style_summary
    soft_hints["allowed_overrides"] = allowed_overrides
    soft_hints["avoid"] = avoid_hints

    theme_dir = THEMES_DIR / theme_id
    theme_path = theme_dir / "theme-pack.json"
    doc_path = PACK_DOCS_DIR / f"{theme_id}.md"
    preview_file = coalesce(spec, args.preview_file, "preview_file")
    preview_rel: str | None = None

    if (theme_dir.exists() or doc_path.exists()) and not args.force:
        raise FileExistsError(f"Theme pack '{theme_id}' already exists. Use --force to overwrite.")

    theme: dict[str, Any] = {
        "id": theme_id,
        "display_name": display_name,
        "kind": "learned",
        "status": status,
        "summary": summary,
        "source": {
            "origin": "reference-derived",
            "notes": source_notes,
        },
        "recommended_for": recommended_for,
        "default_when": default_when,
        "avoid_for": avoid_for,
        "tokens": theme_tokens,
        "soft_hints": soft_hints,
    }

    inspired_by = coalesce(spec, args.inspired_by, "inspired_by")
    if inspired_by:
        theme["source"]["inspired_by"] = inspired_by

    source_image = coalesce(spec, args.source_image, "source_image")
    if source_image:
        theme["source"]["reference_image"] = source_image

    confidence_notes = coalesce(spec, args.confidence_notes, "confidence_notes")
    if confidence_notes:
        theme["source"]["confidence_notes"] = confidence_notes

    if preview_file:
        preview_src = Path(str(preview_file)).expanduser().resolve()
        preview_name = f"preview{preview_src.suffix.lower()}"
        preview_rel = f"assets/themes/{theme_id}/{preview_name}"
        theme["preview_asset"] = preview_rel

    if args.dry_run:
        print(json.dumps(theme, ensure_ascii=False, indent=2))
        return 0

    theme_dir.mkdir(parents=True, exist_ok=True)
    PACK_DOCS_DIR.mkdir(parents=True, exist_ok=True)

    if preview_file:
        preview_dest = ROOT / theme["preview_asset"]
        shutil.copy2(preview_src, preview_dest)

    theme_path.write_text(json.dumps(theme, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    doc_path.write_text(
        render_pack_doc(theme, theme_path, preview_rel, base_pack_id, style_summary, coalesce(spec, args.notes_md, "notes_md")),
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), str(theme_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.strip() or proc.stderr.strip() or "validation failed")

    print(f"Created learned theme pack: {theme_id}")
    print(f"- JSON: {theme_path.relative_to(ROOT)}")
    print(f"- Doc: {doc_path.relative_to(ROOT)}")
    if preview_rel:
        print(f"- Preview: {preview_rel}")
    print("Validation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
