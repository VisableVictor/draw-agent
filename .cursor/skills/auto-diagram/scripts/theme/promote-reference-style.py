#!/usr/bin/env python3
"""Promote a delivered reference-derived style into a reusable learned theme pack.

Usage:
  python3 scripts/theme/promote-reference-style.py \
    --name "静海蓝图" \
    --style-summary "白底蓝灰 + 更安静留白 + 细描边 + 克制箭头" \
    --reference-image "/path/to/reference.png" \
    --artifact-candidate "/path/to/final.png" \
    --audience "老板/评审" \
    --purpose "汇报" \
    --diagram-family "架构图"

This script chooses a base pack when possible, prepares sensible defaults,
copies a preview asset when available, delegates the final file creation to
`create-learned-theme-pack.py`, and then validates the result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CREATE_SCRIPT = ROOT / "scripts" / "theme" / "create-learned-theme-pack.py"
LIST_SCRIPT = ROOT / "scripts" / "theme" / "list-theme-packs.py"

DEFAULT_DAY_PACK = "default-day-blue"
DEFAULT_DARK_PACK = "default-dark-architecture"

DAY_KEYWORDS = [
    "白底",
    "日间",
    "日光",
    "蓝",
    "浅蓝",
    "清淡",
    "清朗",
    "明亮",
    "温和",
    "安静",
    "恬静",
    "老板",
    "评审",
    "客户",
    "汇报",
    "咨询",
    "day",
    "light",
    "blue",
    "clean",
    "quiet",
    "calm",
    "boardroom",
    "paper",
]

DARK_KEYWORDS = [
    "深色",
    "暗夜",
    "夜景",
    "夜",
    "石板",
    "石墨",
    "工业",
    "技术",
    "赛博",
    "霓虹",
    "架构",
    "平台",
    "云",
    "网络",
    "安全",
    "微服务",
    "dark",
    "night",
    "slate",
    "graphite",
    "industrial",
    "technical",
    "cyber",
    "platform",
    "cloud",
    "security",
    "network",
]

PREVIEW_PRIORITY = {
    ".png": 0,
    ".jpg": 1,
    ".jpeg": 1,
    ".svg": 2,
    ".html": 3,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a reference-derived style into a learned theme pack.")
    parser.add_argument("--spec-file", help="Optional JSON file containing the promotion spec.")
    parser.add_argument("--name", help="Display name for the learned theme pack.")
    parser.add_argument("--id", help="Optional theme pack id.")
    parser.add_argument("--style-summary", help="Human-readable style summary.")
    parser.add_argument("--base-pack", default=None, help="Base pack id, or omit to auto-infer.")
    parser.add_argument("--summary", help="One-sentence learned pack summary.")
    parser.add_argument("--source-notes", help="How this pack was learned.")
    parser.add_argument("--reference-image", help="Optional reference image path or label.")
    parser.add_argument("--artifact-candidate", action="append", default=None, help="Repeatable delivered artifact path; best preview is auto-selected.")
    parser.add_argument("--preview-file", help="Explicit preview file path. Overrides artifact auto-selection.")
    parser.add_argument("--audience", help="Primary audience, used to infer defaults.")
    parser.add_argument("--purpose", help="Purpose, used to infer defaults.")
    parser.add_argument("--diagram-family", help="Diagram family, used to infer defaults.")
    parser.add_argument("--density", help="Optional density hint.")
    parser.add_argument("--recommended-for", action="append", default=None, help="Repeatable.")
    parser.add_argument("--default-when", action="append", default=None, help="Repeatable.")
    parser.add_argument("--avoid-for", action="append", default=None, help="Repeatable.")
    parser.add_argument("--mood", action="append", default=None, help="Repeatable mood hints.")
    parser.add_argument("--annotation-style", help="Optional annotation style override.")
    parser.add_argument("--density-bias", help="Optional density_bias override.")
    parser.add_argument("--allow-override", action="append", default=None, help="Repeatable soft hint override.")
    parser.add_argument("--avoid-hint", action="append", default=None, help="Repeatable soft hint avoid item.")
    parser.add_argument("--confidence-notes", help="Optional confidence notes.")
    parser.add_argument("--inspired-by", help="Optional inspiration label.")
    parser.add_argument("--token-overrides-file", help="Optional token overrides JSON file.")
    parser.add_argument("--soft-hints-file", help="Optional soft_hints overrides JSON file.")
    parser.add_argument("--notes-md", help="Optional extra markdown notes for the pack doc.")
    parser.add_argument("--status", default=None, help="available or draft. Defaults to available.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing pack if needed.")
    parser.add_argument("--dry-run", action="store_true", help="Show the derived decision and delegated command without writing files.")
    return parser.parse_args()


def load_spec(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    target = Path(path).expanduser().resolve()
    return json.loads(target.read_text(encoding="utf-8"))


def coalesce(spec: dict[str, Any], cli_value: Any, key: str, default: Any = None) -> Any:
    return cli_value if cli_value not in (None, []) else spec.get(key, default)


def normalize_list(value: Any, fallback: list[str] | None = None) -> list[str]:
    if value is None:
        return list(fallback or [])
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower())
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    if not slug:
        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
        slug = f"theme-{digest}"
    return slug


def resolve_existing_path(raw_path: str) -> Path:
    candidate = Path(raw_path).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()
    repo_candidate = (ROOT / candidate).resolve()
    if repo_candidate.exists():
        return repo_candidate
    return candidate.resolve()


def choose_preview(explicit_preview: str | None, artifact_candidates: list[str]) -> Path | None:
    if explicit_preview:
        preview = resolve_existing_path(explicit_preview)
        if not preview.exists():
            raise FileNotFoundError(f"Preview file not found: {preview}")
        return preview

    resolved = []
    for raw in artifact_candidates:
        path = resolve_existing_path(raw)
        if path.exists():
            resolved.append(path)
    if not resolved:
        return None

    resolved.sort(key=lambda item: (PREVIEW_PRIORITY.get(item.suffix.lower(), 99), item.name))
    return resolved[0]


def score_keywords(texts: list[str], keywords: list[str]) -> int:
    haystack = " ".join(filter(None, texts)).lower()
    return sum(haystack.count(keyword.lower()) for keyword in keywords)


def infer_base_pack(
    explicit_base_pack: str | None,
    style_summary: str,
    audience: str | None,
    purpose: str | None,
    diagram_family: str | None,
) -> tuple[str, str]:
    if explicit_base_pack:
        return explicit_base_pack, "由调用方显式指定。"

    texts = [style_summary, audience or "", purpose or "", diagram_family or ""]
    day_score = score_keywords(texts, DAY_KEYWORDS)
    dark_score = score_keywords(texts, DARK_KEYWORDS)

    if day_score > dark_score:
        return DEFAULT_DAY_PACK, f"根据更偏白底 / 汇报 / 日间的线索自动判断（day={day_score}, dark={dark_score}）。"
    if dark_score > day_score:
        return DEFAULT_DARK_PACK, f"根据更偏深色 / 技术 / 架构的线索自动判断（dark={dark_score}, day={day_score}）。"

    tie_hint = "自动判断出现平分后的兜底决策。"
    if any(token in (audience or "") for token in ["老板", "评审", "客户"]) or any(
        token in (purpose or "") for token in ["汇报", "评审", "说服"]
    ):
        return DEFAULT_DAY_PACK, f"{tie_hint} audience / purpose 更偏白底汇报场景。"
    if any(token in (diagram_family or "") for token in ["架构", "云", "网络", "安全", "平台"]):
        return DEFAULT_DARK_PACK, f"{tie_hint} diagram family 更偏深色技术结构展示。"
    return DEFAULT_DAY_PACK, f"{tie_hint} 没有更强信号时默认回到日间蓝图。"


def infer_summary(name: str, style_summary: str, base_pack: str) -> str:
    return f"从参考图学习出的「{name}」风格，基于 {base_pack} 做稳定复用，核心气质为：{style_summary}。"


def infer_source_notes(reference_image: str | None) -> str:
    if reference_image:
        return f"在最终大图交付后，由参考图风格沉淀生成。参考来源：{reference_image}"
    return "在最终大图交付后，由本次参考图学习得到的风格沉淀生成。"


def unique_non_empty(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        clean = item.strip()
        if not clean or clean in seen:
            continue
        seen.add(clean)
        result.append(clean)
    return result


def infer_recommended_for(audience: str | None, purpose: str | None, diagram_family: str | None, base_pack: str) -> list[str]:
    items: list[str] = []
    if diagram_family:
        items.append(diagram_family)
    if purpose:
        items.append(f"{purpose}场景")
    if audience:
        items.append(f"{audience}阅读")
    if not items:
        items.append("参考图风格延续任务")
    if base_pack == DEFAULT_DAY_PACK:
        items.append("白底汇报图")
    else:
        items.append("深色技术架构图")
    return unique_non_empty(items)


def infer_default_when(style_summary: str, base_pack: str, audience: str | None, purpose: str | None) -> list[str]:
    items = ["后续仍想沿用这次参考图的视觉气质"]
    if audience or purpose:
        label = " / ".join(filter(None, [audience, purpose]))
        items.append(f"面向 {label} 的图面仍希望保持同一气质")
    if base_pack == DEFAULT_DAY_PACK:
        items.append("更适合白底、日间或蓝灰汇报环境")
    else:
        items.append("更适合深色、技术舞台或系统结构展示")
    if style_summary:
        items.append(f"需要延续这条风格主轴：{style_summary}")
    return unique_non_empty(items)


def infer_avoid_for(base_pack: str) -> list[str]:
    items = ["需要与当前风格相反的明暗基调"]
    if base_pack == DEFAULT_DAY_PACK:
        items.append("需要强夜景技术氛围或暗夜舞台的图")
    else:
        items.append("需要白底咨询汇报感或日间轻画面的图")
    return items


def infer_mood(base_pack: str, style_summary: str, explicit_moods: list[str] | None) -> list[str]:
    if explicit_moods:
        return unique_non_empty(explicit_moods)
    items = ["reference-derived"]
    if base_pack == DEFAULT_DAY_PACK:
        items.extend(["daylight", "clean"])
        if any(token in style_summary for token in ["安静", "恬静", "柔和", "清淡"]):
            items.append("calm")
    else:
        items.extend(["dark", "technical"])
        if any(token in style_summary for token in ["工业", "石墨", "石板"]):
            items.append("industrial")
    return unique_non_empty(items)


def build_command(args: argparse.Namespace, theme_name: str, theme_id: str, base_pack: str, base_reason: str, preview: Path | None) -> list[str]:
    spec = load_spec(args.spec_file)
    style_summary = str(coalesce(spec, args.style_summary, "style_summary", "")).strip()
    audience = coalesce(spec, args.audience, "audience")
    purpose = coalesce(spec, args.purpose, "purpose")
    diagram_family = coalesce(spec, args.diagram_family, "diagram_family")
    summary = coalesce(spec, args.summary, "summary") or infer_summary(theme_name, style_summary, base_pack)
    source_notes = coalesce(spec, args.source_notes, "source_notes") or infer_source_notes(coalesce(spec, args.reference_image, "reference_image"))
    recommended_for = normalize_list(
        coalesce(spec, args.recommended_for, "recommended_for"),
        infer_recommended_for(audience, purpose, diagram_family, base_pack),
    )
    default_when = normalize_list(
        coalesce(spec, args.default_when, "default_when"),
        infer_default_when(style_summary, base_pack, audience, purpose),
    )
    avoid_for = normalize_list(
        coalesce(spec, args.avoid_for, "avoid_for"),
        infer_avoid_for(base_pack),
    )
    mood = infer_mood(base_pack, style_summary, normalize_list(coalesce(spec, args.mood, "mood")))

    cmd = [
        sys.executable,
        str(CREATE_SCRIPT),
        "--name",
        theme_name,
        "--id",
        theme_id,
        "--base-pack",
        base_pack,
        "--summary",
        str(summary),
        "--style-summary",
        style_summary,
        "--source-notes",
        str(source_notes),
    ]
    status = coalesce(spec, args.status, "status")
    if status:
        cmd.extend(["--status", str(status)])
    reference_image = coalesce(spec, args.reference_image, "reference_image")
    if reference_image:
        cmd.extend(["--source-image", str(reference_image)])
    inspired_by = coalesce(spec, args.inspired_by, "inspired_by")
    if inspired_by:
        cmd.extend(["--inspired-by", str(inspired_by)])
    confidence_notes = coalesce(spec, args.confidence_notes, "confidence_notes")
    if confidence_notes:
        cmd.extend(["--confidence-notes", str(confidence_notes)])
    annotation_style = coalesce(spec, args.annotation_style, "annotation_style")
    if annotation_style:
        cmd.extend(["--annotation-style", str(annotation_style)])
    density_bias = coalesce(spec, args.density_bias, "density_bias")
    if density_bias:
        cmd.extend(["--density-bias", str(density_bias)])
    notes_md = coalesce(spec, args.notes_md, "notes_md")
    if notes_md:
        cmd.extend(["--notes-md", str(notes_md)])
    token_overrides = coalesce(spec, args.token_overrides_file, "token_overrides_file")
    if token_overrides:
        cmd.extend(["--token-overrides-file", str(token_overrides)])
    hints_file = coalesce(spec, args.soft_hints_file, "soft_hints_file")
    if hints_file:
        cmd.extend(["--soft-hints-file", str(hints_file)])
    if preview:
        cmd.extend(["--preview-file", str(preview)])
    if args.force:
        cmd.append("--force")
    for item in recommended_for:
        cmd.extend(["--recommended-for", item])
    for item in default_when:
        cmd.extend(["--default-when", item])
    for item in avoid_for:
        cmd.extend(["--avoid-for", item])
    for item in mood:
        cmd.extend(["--mood", item])
    for item in normalize_list(coalesce(spec, args.allow_override, "allowed_overrides")):
        cmd.extend(["--allow-override", item])
    for item in normalize_list(coalesce(spec, args.avoid_hint, "avoid_hints")):
        cmd.extend(["--avoid-hint", item])
    if args.dry_run:
        cmd.append("--dry-run")
    return cmd


def format_receipt(
    theme_name: str,
    theme_id: str,
    base_pack: str,
    base_reason: str,
    style_summary: str,
    preview: Path | None,
    theme_count: str,
) -> str:
    lines = [
        "🧩 主题包沉淀",
        f"- 名称：{theme_name}",
        f"- ID：{theme_id}",
        f"- 基于：{base_pack}",
        f"- 判断依据：{base_reason}",
        f"- 风格摘要：{style_summary}",
    ]
    if preview:
        lines.append(f"- 预览：{preview}")

    lines.extend(
        [
            "",
            "✅ 当前产出",
            f"- 新主题包：{theme_id}",
            f"- 当前主题包总数：{theme_count}",
            "",
            "🧠 后续如何用",
            f"- 下次你可以直接说“用‘{theme_name}’这个主题包风格”",
            "- 如果内容相近，我在 brainstorm 阶段也可能主动推荐它",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    spec = load_spec(args.spec_file)

    theme_name = coalesce(spec, args.name, "name")
    if not theme_name or not str(theme_name).strip():
        raise ValueError("Missing required value: --name")
    theme_name = str(theme_name).strip()
    theme_id = str(coalesce(spec, args.id, "id", theme_name)).strip()
    theme_id = slugify(theme_id)

    style_summary = coalesce(spec, args.style_summary, "style_summary")
    if not style_summary or not str(style_summary).strip():
        raise ValueError("Missing required value: --style-summary")
    style_summary = str(style_summary).strip()

    audience = coalesce(spec, args.audience, "audience")
    purpose = coalesce(spec, args.purpose, "purpose")
    diagram_family = coalesce(spec, args.diagram_family, "diagram_family")
    preview = choose_preview(
        coalesce(spec, args.preview_file, "preview_file"),
        normalize_list(coalesce(spec, args.artifact_candidate, "artifact_candidates")),
    )
    base_pack, base_reason = infer_base_pack(
        coalesce(spec, args.base_pack, "base_pack"),
        style_summary,
        audience,
        purpose,
        diagram_family,
    )

    cmd = build_command(args, theme_name, theme_id, base_pack, base_reason, preview)

    if args.dry_run:
        payload = {
            "name": theme_name,
            "id": theme_id,
            "base_pack": base_pack,
            "base_pack_reason": base_reason,
            "style_summary": style_summary,
            "preview_file": str(preview) if preview else None,
            "delegated_command": cmd,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stdout.strip() or proc.stderr.strip() or "theme promotion failed")

    count_proc = subprocess.run(
        [sys.executable, str(LIST_SCRIPT), "--count", "--include-draft"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    theme_count = count_proc.stdout.strip() if count_proc.returncode == 0 else "unknown"

    print(proc.stdout.strip())
    print()
    print(format_receipt(theme_name, theme_id, base_pack, base_reason, style_summary, preview, theme_count))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
