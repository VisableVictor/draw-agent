#!/usr/bin/env python3
"""Validate auto-diagram structure after latest capability alignment and stabilization hardening."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC_FILES = [ROOT / "SKILL.md", *sorted((ROOT / "references").rglob("*.md"))]
TEXT_EXTENSIONS = {".md", ".yaml", ".yml", ".json", ".py", ".cjs", ".js", ".sh"}
LINK_RE = re.compile(r"\]\(([^)#]+)")
LEGACY_NAME = "auto-" + "graph"
JUNK_NAMES = {".DS_Store", "__pycache__"}
REQUIRED_PATHS = [
    ROOT / "SKILL.md",
    ROOT / "agents" / "openai.yaml",
    ROOT / "references" / "reading-map.md",
    ROOT / "references" / "shared" / "interaction-contract.md",
    ROOT / "references" / "flow" / "brainstorm" / "README.md",
    ROOT / "references" / "flow" / "brainstorm" / "brainstorm-mode.md",
    ROOT / "references" / "flow" / "intake" / "README.md",
    ROOT / "references" / "flow" / "intake" / "intake-and-classification.md",
    ROOT / "references" / "flow" / "intake" / "reference-image-mode.md",
    ROOT / "references" / "flow" / "intake" / "unified-diagram-spec.md",
    ROOT / "references" / "routing" / "README.md",
    ROOT / "references" / "routing" / "draft-preview.md",
    ROOT / "references" / "routing" / "layout-and-rendering.md",
    ROOT / "references" / "backends" / "README.md",
    ROOT / "references" / "backends" / "backend-matrix.md",
    ROOT / "references" / "backends" / "contracts" / "svg-contract.md",
    ROOT / "references" / "backends" / "contracts" / "svg-edge-occlusion-patterns.md",
    ROOT / "references" / "formal" / "README.md",
    ROOT / "references" / "quality" / "README.md",
    ROOT / "references" / "quality" / "batch-repair-loop.md",
    ROOT / "references" / "quality" / "quality-gates.md",
    ROOT / "references" / "quality" / "design-quality-system.md",
    ROOT / "references" / "delivery" / "README.md",
    ROOT / "references" / "delivery" / "reporting-output.md",
    ROOT / "references" / "delivery" / "delivery-templates.md",
    ROOT / "references" / "themes" / "README.md",
    ROOT / "references" / "themes" / "theme-pack-spec.md",
    ROOT / "references" / "themes" / "promotion-flow.md",
    ROOT / "references" / "themes" / "packs" / "default-dark-architecture.md",
    ROOT / "references" / "themes" / "packs" / "default-day-blue.md",
    ROOT / "references" / "themes" / "packs" / "pine-deep-green.md",
    ROOT / "references" / "svg-contract.md",
    ROOT / "scripts" / "finalize-svg.cjs",
    ROOT / "scripts" / "stabilize-svg.cjs",
    ROOT / "scripts" / "check-svg-attribution.py",
    ROOT / "scripts" / "export" / "export-diagram.sh",
    ROOT / "scripts" / "export" / "export-pptx.cjs",
    ROOT / "scripts" / "quality" / "check-svg-attribution.py",
    ROOT / "scripts" / "quality" / "check-svg-page-chrome.py",
    ROOT / "scripts" / "quality" / "check-svg-legend-semantics.py",
    ROOT / "scripts" / "quality" / "run-quality-preflight.py",
    ROOT / "scripts" / "quality" / "render-quality-preview.py",
    ROOT / "scripts" / "svg" / "stabilize-svg.cjs",
    ROOT / "scripts" / "svg" / "finalize-svg.cjs",
    ROOT / "scripts" / "svg" / "auto-fit-svg-text.py",
    ROOT / "scripts" / "svg" / "auto-fit-svg-text-selftest.py",
    ROOT / "scripts" / "svg" / "materialize-css-vars.cjs",
    ROOT / "scripts" / "svg" / "materialize-css-vars-selftest.cjs",
    ROOT / "scripts" / "theme" / "list-theme-packs.py",
    ROOT / "scripts" / "theme" / "validate-theme-pack.py",
    ROOT / "scripts" / "theme" / "create-learned-theme-pack.py",
    ROOT / "scripts" / "theme" / "promote-reference-style.py",
    ROOT / "scripts" / "svg-state-stabilizer.cjs",
    ROOT / "scripts" / "svg-serializer-pass.cjs",
    ROOT / "scripts" / "internal" / "check-skill-structure.py",
    ROOT / "assets" / "themes" / "default-dark-architecture" / "theme-pack.json",
    ROOT / "assets" / "themes" / "default-day-blue" / "theme-pack.json",
    ROOT / "assets" / "themes" / "pine-deep-green" / "theme-pack.json",
    ROOT / "assets" / "themes" / "pine-deep-green" / "preview.png",
    ROOT / "assets" / "regression" / "font-fit-grow-overflow.svg",
    ROOT / "assets" / "regression" / "font-fit-overflow.svg",
    ROOT / "assets" / "regression" / "legend-semantics-missing.svg",
    ROOT / "assets" / "regression" / "page-chrome-guard-good.svg",
    ROOT / "assets" / "regression" / "page-chrome-overlap-bad.svg",
    ROOT / "assets" / "regression" / "under-node-edge-pattern-good.svg",
]
REQUIRED_RULE_HINTS = {
    ROOT / "agents" / "openai.yaml": [
        "visibly match the chosen aspect ratio",
        "default 16:9 drafts clearly widescreen",
        "PingFang SC",
        "must not inject or draw any watermark",
        "silently",
    ],
    ROOT / "SKILL.md": [
        "themes/README.md",
        "主题包",
        "静默稳定化",
        "不注入可见水印",
        "batch-repair-loop.md",
        "render-quality-preview.py",
    ],
    ROOT / "references" / "reading-map.md": [
        "themes/README.md",
        "主题包",
        "固定模板",
    ],
    ROOT / "references" / "principles" / "spec-before-render.md": [
        "草稿图必须用自身外形表达当前比例",
        "16:9",
    ],
    ROOT / "references" / "principles" / "layout-over-template.md": [
        "under-node",
        "颜色分层",
        "画布吃满",
    ],
    ROOT / "references" / "themes" / "README.md": [
        "scripts/theme/list-theme-packs.py --count",
        "scripts/theme/promote-reference-style.py",
        "visual_style",
        "主题包",
        "pine-deep-green.md",
    ],
    ROOT / "references" / "flow" / "brainstorm" / "brainstorm-mode.md": [
        "theme_strategy",
        "scripts/theme/list-theme-packs.py --count",
        "最适合的主题包",
    ],
    ROOT / "references" / "flow" / "intake" / "intake-and-classification.md": [
        "style_source",
        "theme_pack_ref",
        "theme_strategy",
    ],
    ROOT / "references" / "svg-contract.md": [
        "scripts/stabilize-svg.cjs",
        "scripts/svg/materialize-css-vars.cjs",
        "title_zone",
        "footer_zone",
        "ad-edge-underlay",
        "data-edge-occlusion",
        "under-node",
        "auto-fit-svg-text.py",
        "PingFang SC",
        "Microsoft YaHei",
        "静默完成",
        "不注入可见水印",
    ],
    ROOT / "references" / "backends" / "contracts" / "README.md": [
        "svg-edge-occlusion-patterns.md",
        "SVG 补充模式",
    ],
    ROOT / "references" / "backends" / "contracts" / "svg-contract.md": [
        "scripts/stabilize-svg.cjs",
        "ad-edge-underlay",
        "data-edge-occlusion",
        "under-node",
        "PingFang SC",
        "Microsoft YaHei",
        "静默完成",
        "不注入可见水印",
    ],
    ROOT / "references" / "shared" / "interaction-contract.md": [
        "现在执行稳定化脚本",
        "scripts/stabilize-svg.cjs",
        "静默完成",
        "🖼️ 草稿图",
        "📐 比例建议",
        "🧭 路由命中",
        "草稿外形必须和当前比例一致",
        "不注入可见水印",
        "质量闸门 Q1/5｜结构闸门",
        "质量闸门 Q4/5｜视觉打磨",
        "质量闸门 Q5/5｜交付复核",
        "run-quality-preflight.py",
        "render-quality-preview.py",
        "效果预览",
    ],
    ROOT / "references" / "routing" / "draft-preview.md": [
        "16:9",
        "1920x1080",
        "草稿外形与比例一致性",
        "先保比例感，再保主结构，再保正文细节",
        "确认草稿图 - 进入正式渲染",
        "用户没有明确确认前",
    ],
    ROOT / "references" / "routing" / "layout-and-rendering.md": [
        "画布有没有被有效吃满",
        "颜色分层",
        "under-node",
        "草稿图里的低保真线框本身就要体现当前画幅",
    ],
    ROOT / "references" / "delivery" / "reporting-output.md": [
        "受控 SVG",
        "静默稳定化",
        "scripts/stabilize-svg.cjs",
        "导出比例 / 画布尺寸",
        "主题来源",
        "沉淀为主题包",
        "不注入可见水印",
    ],
    ROOT / "references" / "quality" / "quality-gates.md": [
        "check-svg-attribution.py",
        "check-svg-page-chrome.py",
        "check-svg-legend-semantics.py",
        "run-quality-preflight.py",
        "render-quality-preview.py",
        "伪水印",
        "PingFang SC",
        "Microsoft YaHei",
        "母容器",
        "under-node",
        "不允许水印",
    ],
    ROOT / "references" / "quality" / "README.md": [
        "check-svg-attribution.py",
        "check-svg-page-chrome.py",
        "check-svg-legend-semantics.py",
        "run-quality-preflight.py",
        "render-quality-preview.py",
        "batch-repair-loop.md",
        "伪水印",
    ],
    ROOT / "references" / "quality" / "batch-repair-loop.md": [
        "Q1 结构闸门",
        "Q2 关键修复",
        "Q4 视觉打磨",
        "Q5 交付复核",
        "3 轮",
        "run-quality-preflight.py",
        "render-quality-preview.py",
        "效果预览",
    ],
    ROOT / "references" / "quality" / "design-quality-system.md": [
        "check-svg-attribution.py",
        "run-quality-preflight.py",
        "AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING",
        "AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING",
        "footer legend",
    ],
    ROOT / "references" / "flow" / "intake" / "unified-diagram-spec.md": [
        "title_zone",
        "footer_zone",
        "min_stage_fill_ratio",
        "max_child_outer_slack",
        "underlay_edge_policy",
        "legend_semantics",
    ],
    ROOT / "scripts" / "export" / "export-diagram.sh": [
        "auto-fit-svg-text.py",
        "check-svg-attribution.py",
        "check-svg-page-chrome.py",
        "check-svg-legend-semantics.py",
    ],
    ROOT / "package.json": [
        "check:text-fit",
        "auto-fit-svg-text.py",
        "check-svg-page-chrome.py",
        "check-svg-legend-semantics.py",
        "run-quality-preflight.py",
        "render-quality-preview.py",
    ],
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def check_links() -> list[str]:
    failures: list[str] = []
    for doc in DOC_FILES:
        text = read_text(doc)
        for target in LINK_RE.findall(text):
            if "://" in target or target.startswith("mailto:"):
                continue
            resolved = (doc.parent / target).resolve()
            if not resolved.exists():
                failures.append(f"Missing link target: {doc.relative_to(ROOT)} -> {target}")
    return failures


def check_required_paths() -> list[str]:
    failures: list[str] = []
    for path in REQUIRED_PATHS:
        if not path.exists():
            failures.append(f"Missing required path: {path.relative_to(ROOT)}")
    return failures


def iter_text_files() -> list[Path]:
    files: list[Path] = []
    for root_name in ("SKILL.md", "agents", "references", "scripts", "package.json", "package-lock.json"):
        candidate = ROOT / root_name
        if candidate.is_file():
            files.append(candidate)
            continue
        if candidate.is_dir():
            for path in candidate.rglob("*"):
                if path.is_file() and path.suffix in TEXT_EXTENSIONS:
                    files.append(path)
    return sorted(set(files))


def check_legacy_name_refs() -> list[str]:
    failures: list[str] = []
    for path in iter_text_files():
        text = read_text(path)
        if LEGACY_NAME in text:
            failures.append(f"Legacy skill name still present: {path.relative_to(ROOT)}")
    return failures


def check_required_rule_hints() -> list[str]:
    failures: list[str] = []
    for path, markers in REQUIRED_RULE_HINTS.items():
        if not path.exists():
            continue
        text = read_text(path)
        missing = [marker for marker in markers if marker not in text]
        if missing:
            failures.append(
                f"Missing expected capability markers in {path.relative_to(ROOT)}: {', '.join(missing)}"
            )
    return failures


def check_junk_files() -> list[str]:
    failures: list[str] = []
    for path in ROOT.rglob("*"):
        if path.name in JUNK_NAMES:
            failures.append(f"Junk artifact should be removed: {path.relative_to(ROOT)}")
    return failures


def main() -> int:
    failures = [
        *check_links(),
        *check_required_paths(),
        *check_legacy_name_refs(),
        *check_required_rule_hints(),
        *check_junk_files(),
    ]
    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        return 1

    print("OK: auto-diagram structure, latest capability sync, and metadata-only stabilization pipeline are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
