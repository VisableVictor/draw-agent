---
name: auto-diagram
description: >-
  汇报级多引擎图：用 PlantUML、Mermaid、Graphviz 渲染，支持 PPTX 导出和
  主题包复用。适合需要"按参考图风格出图"、汇报演示大图、能力盘点、
  现状-目标态对比、路径图等商业/技术汇报场景。
  Use when user mentions 汇报图、画个大图、能力图、关系图谱、矩阵图、
  总览图、路径图、PPTX导出、PlantUML、Mermaid、Graphviz、BPMN、
  按这个风格出图、主题包、现状到目标态。
  不用于：纯数据图表、办公海报、照片海报、.drawio 文件。
alwaysApply: false
globs: []
---

# Auto Diagram

> 只保留触发、读取顺序、硬规则、资源地图。细则一律按树状结构下钻。

## 读取总顺序

1. **先读** [reading-map.md](references/reading-map.md) — 它定义了完整的按需读取树，按当前任务阶段下钻，不要一次性全读。
2. 读 [interaction-contract.md](references/shared/interaction-contract.md) — 共享交互协议，所有阶段通用。

⛔ 禁止跳过 brainstorm 直接出图。
  ↳ brainstorm 跳过会导致图型选错、受众错位，后期返工成本远高于前期 2 分钟澄清。
⛔ 禁止在 unified spec 形成前直接选后端或写图稿。
  ↳ spec 未锁定就选后端，容易出现表达路径和实际需求不匹配，整张图要推翻重来。
⛔ 禁止跳过草稿图确认直接进入正式渲染（非交互模式除外，详见交互协议）。
  ↳ 草稿确认是最后一次低成本纠错机会；跳过它意味着用正式渲染的时间去赌结构正确。
⛔ 禁止把所有 backend contract、formal pack、few-shot 一次性全部预读。
  ↳ 全量预读浪费大量 token，且无关后端的规则会干扰当前决策。
⛔ 禁止把布局家族当成固定模板照搬。
  ↳ 布局家族是结构启发，不是版式模具；照搬会让每张图看起来都一样，丧失信息层次感。
⛔ 禁止把主题包当成固定版式模板照搬。
  ↳ 主题包提供视觉语言（色板、字号、间距），不决定内容结构；版式应由 spec 驱动。

## 硬规则

- Mandatory Brainstorm Lock 不得跳过
- 共享交互、入口纪律、spec 优先、参考图边界、布局反模板、汇报优先等跨阶段规则，一律以下面 principles 为准
- 静默稳定化、字体栈、重复署名禁令、不注入可见水印和 SVG 受控交付，一律以下面 canonical 文档为准：
  - [svg-contract.md](references/backends/contracts/svg-contract.md)
  - [quality/quality-gates.md](references/quality/quality-gates.md)
  - [quality/batch-repair-loop.md](references/quality/batch-repair-loop.md)
  - [delivery/reporting-output.md](references/delivery/reporting-output.md)
- **stdout 纪律**：质量脚本输出一律用 `--json-out` 写文件，回执只贴 compact summary；禁止在回执中展示 SVG 源码、脚本原始日志或大段 XML。qodercli 有 stdout 上限保护，超限会直接终止会话。详见 [batch-repair-loop.md](references/quality/batch-repair-loop.md) 的"stdout 控制"章节。
- [entry-and-confirmation.md](references/principles/entry-and-confirmation.md)
- [spec-before-render.md](references/principles/spec-before-render.md)
- [reference-boundary.md](references/principles/reference-boundary.md)
- [layout-over-template.md](references/principles/layout-over-template.md)
- [report-grade-output.md](references/principles/report-grade-output.md)

## 退出条件与错误处理

- **迭代上限**：草稿→反馈→重绘最多 3 轮。超过 3 轮仍未通过质量闸门时，停止迭代，输出当前最佳版本并标注未通过项，交由用户决策。
- **渲染失败回退**：首选后端渲染失败时，按 SVG → Mermaid → 纯文本 ASCII 逐级降级交付，确保始终有可交付产物。
- **依赖缺失降级**：rsvg-convert / dot / mmdc / plantuml 不可用时，切换到不依赖该工具的备选后端，并在输出中注明降级原因。
- **质量闸门未通过**：单项检查失败时原地修复并重试（最多 2 次）；仍失败则跳过该项、标注 warning 后继续交付，不阻塞整体流程。
- **用户无响应 / 非交互模式**：brainstorm 或草稿确认阶段用户未回复时，使用合理默认值继续推进。prompt 已预填全部 brainstorm 参数并明确要求"直接出图"时，视为非交互模式——brainstorm 和草稿确认均自动通过，直接进入正式渲染与交付。

## 最小化输出示例

一轮最简交互的关键回执形态，详见 [interaction-example.md](references/shared/interaction-example.md)。

## 资源地图

按需查阅，不要一次性全读。根据当前阶段选择对应资源：

- **开始新任务前**：读 [reading-map.md](references/reading-map.md) 获取完整读取树
- **交互规范不明确时**：读 [interaction-contract.md](references/shared/interaction-contract.md)
- **需要跨阶段原则指导时**：读 [principles/README.md](references/principles/README.md)
- **进入具体阶段时**：读对应阶段 README
  - [flow/brainstorm/README.md](references/flow/brainstorm/README.md)
  - [flow/intake/README.md](references/flow/intake/README.md)
  - [themes/README.md](references/themes/README.md)
  - [routing/README.md](references/routing/README.md)
  - [formal/README.md](references/formal/README.md)
  - [backends/README.md](references/backends/README.md)
  - [quality/README.md](references/quality/README.md)
  - [delivery/README.md](references/delivery/README.md)
- **需要图法包、后端契约、主题定义等细则时**：查阅对应目录
  - `references/formal/packs/*`
  - `references/formal/examples/*`
  - `references/backends/contracts/*`
  - `references/flow/*/*`
  - `references/themes/*`
  - `references/routing/*`
  - `references/quality/*`
  - `references/delivery/*`
- **执行渲染、质检、导出、主题管理时**：调用对应脚本
  - `scripts/stabilize-svg.cjs`
  - `scripts/finalize-svg.cjs`
  - `scripts/render/render-mermaid.sh`
  - `scripts/render/render-graphviz.sh`
  - `scripts/render/render-plantuml.sh`
  - `scripts/quality/run-quality-preflight.py`
  - `scripts/quality/render-quality-preview.py`
  - `scripts/export/export-diagram.sh`
  - `scripts/export/export-pptx.cjs`
  - `scripts/svg/materialize-css-vars.cjs`
  - `scripts/theme/create-learned-theme-pack.py`
  - `scripts/theme/promote-reference-style.py`
  - `scripts/theme/list-theme-packs.py`
  - `scripts/theme/validate-theme-pack.py`
- **查看示例或主题 token 时**：查阅产物目录
  - `assets/examples/*`
  - `assets/generated/*`
  - `assets/themes/*`
