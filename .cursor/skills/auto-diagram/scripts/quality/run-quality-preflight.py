#!/usr/bin/env python3
"""Run auto-diagram quality checks in collect-all preflight mode.

Usage:
  python3 scripts/quality/run-quality-preflight.py [--stage hard|soft|full] <svg-file>

This script orchestrates existing checks. It does not replace their geometry
logic; it keeps running peer checks after one failure so the agent can repair
all findings in one batch.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


@dataclass
class CheckResult:
    name: str
    kind: str
    returncode: int
    errors: list[str]
    warnings: list[str]
    hints: list[str]
    output: list[str]

    @property
    def failed(self) -> bool:
        return self.returncode != 0 or bool(self.errors)


PREPARE_STEPS = [
    ("stabilize-svg.cjs", ["node", str(ROOT / "scripts/svg/stabilize-svg.cjs")]),
    ("auto-fit-svg-text.py", ["python3", "-B", str(ROOT / "scripts/svg/auto-fit-svg-text.py")]),
    ("stabilize-svg.cjs", ["node", str(ROOT / "scripts/svg/stabilize-svg.cjs")]),
    ("stabilize-svg.cjs --verify", ["node", str(ROOT / "scripts/svg/stabilize-svg.cjs"), "--verify"]),
]

HARD_CHECKS = [
    ("check-svg-attribution.py", ["python3", "-B", str(ROOT / "scripts/quality/check-svg-attribution.py")]),
    ("lint-svg-diagram.py", ["python3", "-B", str(ROOT / "scripts/quality/lint-svg-diagram.py")]),
    ("check-svg-edge-clearance.py", ["python3", "-B", str(ROOT / "scripts/quality/check-svg-edge-clearance.py")]),
    ("check-svg-node-padding.py", ["python3", "-B", str(ROOT / "scripts/quality/check-svg-node-padding.py")]),
    ("check-svg-page-chrome.py", ["python3", "-B", str(ROOT / "scripts/quality/check-svg-page-chrome.py")]),
]

SOFT_CHECKS = [
    ("check-svg-page-chrome.py", ["python3", "-B", str(ROOT / "scripts/quality/check-svg-page-chrome.py")]),
    ("check-layout-rhythm.py", ["python3", "-B", str(ROOT / "scripts/quality/check-layout-rhythm.py")]),
    ("check-visual-hierarchy.py", ["python3", "-B", str(ROOT / "scripts/quality/check-visual-hierarchy.py")]),
    ("check-svg-legend-semantics.py", ["python3", "-B", str(ROOT / "scripts/quality/check-svg-legend-semantics.py")]),
]

USER_STAGE_LABELS = {
    "hard": "Q1/5｜结构闸门",
    "soft": "Q4/5｜视觉打磨",
    "full": "Q1-Q5｜全量质量闸门",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run collect-all auto-diagram quality preflight checks.")
    parser.add_argument("svg_file", help="SVG file to check. Prepare steps may update this file in place.")
    parser.add_argument(
        "--stage",
        choices=("hard", "soft", "full"),
        default="hard",
        help="Check stage to run. full runs hard first and soft only if hard is clean.",
    )
    parser.add_argument("--json-out", help="Optional path for a machine-readable report.")
    parser.add_argument("--skip-prepare", action="store_true", help="Skip stabilize/auto-fit/verify prepare steps.")
    return parser.parse_args()


def merged_env() -> dict[str, str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def run_command(name: str, kind: str, cmd: list[str], svg_file: Path) -> CheckResult:
    full_cmd = [*cmd, str(svg_file)]
    try:
        proc = subprocess.run(full_cmd, cwd=ROOT, capture_output=True, text=True, env=merged_env())
        returncode = proc.returncode
        raw_output = [*proc.stdout.splitlines(), *proc.stderr.splitlines()]
    except FileNotFoundError as exc:
        returncode = 127
        raw_output = [f"ERROR: {exc}"]

    errors: list[str] = []
    warnings: list[str] = []
    hints: list[str] = []
    for line in raw_output:
        stripped = line.strip()
        if stripped.startswith("ERROR:"):
            errors.append(stripped)
        elif stripped.startswith("WARNING:"):
            warnings.append(stripped)
        elif stripped.startswith("DESIGN_HINT:"):
            hints.append(stripped)

    if returncode != 0 and not errors:
        errors.append(f"ERROR: {name} exited with status {returncode}.")

    return CheckResult(
        name=name,
        kind=kind,
        returncode=returncode,
        errors=dedupe(errors),
        warnings=dedupe(warnings),
        hints=dedupe(hints),
        output=raw_output,
    )


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def run_prepare(svg_file: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    for name, cmd in PREPARE_STEPS:
        result = run_command(name, "prepare", cmd, svg_file)
        results.append(result)
        if result.failed:
            break
    return results


def run_checks(stage: str, svg_file: Path) -> list[CheckResult]:
    checks = HARD_CHECKS if stage == "hard" else SOFT_CHECKS
    return [run_command(name, stage, cmd, svg_file) for name, cmd in checks]


def count_errors(results: list[CheckResult]) -> int:
    return sum(len(result.errors) for result in results)


def count_warnings(results: list[CheckResult]) -> int:
    return sum(len(result.warnings) for result in results)


def count_hints(results: list[CheckResult]) -> int:
    return sum(len(result.hints) for result in results)


def print_group(title: str, results: list[CheckResult], attr: str) -> None:
    printed = False
    for result in results:
        messages = getattr(result, attr)
        if not messages:
            continue
        if not printed:
            print(title)
            printed = True
        print(f"[{result.name}]")
        for message in messages:
            print(f"- {message}")


def emit_report(svg_file: Path, requested_stage: str, results: list[CheckResult], hard_clean: bool) -> None:
    hard_results = [result for result in results if result.kind == "hard"]
    soft_results = [result for result in results if result.kind == "soft"]
    prepare_results = [result for result in results if result.kind == "prepare"]

    print(f"质量闸门: {svg_file}")
    print(f"阶段: {requested_stage} ({USER_STAGE_LABELS[requested_stage]})")
    print(
        "Summary: "
        f"prepare_errors={count_errors(prepare_results)} "
        f"hard_errors={count_errors(hard_results)} "
        f"stage_errors={count_errors(results)} "
        f"warnings={count_warnings(hard_results + soft_results)} "
        f"hints={count_hints(hard_results + soft_results)}"
    )
    print_group("ERRORS", results, "errors")
    print_group("WARNINGS", hard_results + soft_results, "warnings")
    print_group("DESIGN HINTS", hard_results + soft_results, "hints")

    if requested_stage == "hard":
        if hard_clean:
            print("下一步: Q1 结构闸门已通过；除非是非交互模式，否则先询问用户是否进入 Q4 视觉打磨。")
        else:
            print("下一步: 进入 Q2 关键修复，然后重跑 Q1 结构闸门。")
    elif requested_stage == "soft":
        if count_warnings(soft_results) or count_hints(soft_results):
            print("下一步: 继续 Q4 视觉打磨，然后运行 Q5 交付复核。")
        else:
            print("下一步: Q4 视觉打磨已清零，进入 Q5 交付复核和最终导出。")
    elif requested_stage == "full":
        if not hard_clean:
            print("下一步: Q1 发现关键结构问题，已跳过 Q4；先进入 Q2 关键修复。")
        elif count_warnings(soft_results) or count_hints(soft_results):
            print("下一步: 继续 Q4 视觉打磨，然后运行 Q5 交付复核。")
        else:
            print("下一步: Q1 / Q4 已清零，进入 Q5 交付复核和最终导出。")


def write_json_report(path: Path, svg_file: Path, stage: str, results: list[CheckResult], hard_clean: bool) -> None:
    payload = {
        "svg_file": str(svg_file),
        "stage": stage,
        "user_stage_label": USER_STAGE_LABELS[stage],
        "hard_clean": hard_clean,
        "summary": {
            "prepare_errors": count_errors([result for result in results if result.kind == "prepare"]),
            "hard_errors": count_errors([result for result in results if result.kind == "hard"]),
            "stage_errors": count_errors(results),
            "warnings": count_warnings(results),
            "hints": count_hints(results),
        },
        "results": [asdict(result) for result in results],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    svg_file = Path(args.svg_file).resolve()
    if not svg_file.is_file():
        print(f"ERROR: file not found: {svg_file}")
        return 2

    results: list[CheckResult] = []
    if not args.skip_prepare:
        results.extend(run_prepare(svg_file))
        prepare_failed = any(result.failed for result in results if result.kind == "prepare")
        if prepare_failed:
            emit_report(svg_file, args.stage, results, hard_clean=False)
            if args.json_out:
                write_json_report(Path(args.json_out), svg_file, args.stage, results, hard_clean=False)
            return 2

    hard_clean = True
    if args.stage in ("hard", "full"):
        hard_results = run_checks("hard", svg_file)
        results.extend(hard_results)
        hard_clean = not any(result.failed for result in hard_results)

    if args.stage == "soft" or (args.stage == "full" and hard_clean):
        results.extend(run_checks("soft", svg_file))

    emit_report(svg_file, args.stage, results, hard_clean=hard_clean)
    if args.json_out:
        write_json_report(Path(args.json_out), svg_file, args.stage, results, hard_clean=hard_clean)

    if args.stage == "hard":
        return 0 if hard_clean else 1
    if args.stage == "soft":
        return 0 if count_errors(results) == 0 and count_warnings(results) == 0 and count_hints(results) == 0 else 1
    if not hard_clean:
        return 1
    return 0 if count_errors(results) == 0 and count_warnings(results) == 0 and count_hints(results) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
