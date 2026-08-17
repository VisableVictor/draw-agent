# Batch Repair Loop

这份文件是质量闸门轮回的唯一真相源。

目标：把“遇到一个关键结构问题就停下修一个”的串行返工，改成“批量检查、批量修复、批量复检”的受控循环，并用稳定的 Q 阶段语言对用户展示。

## 总流程

```text
正式 SVG 初版
  -> Q1 结构闸门
  -> Q2 关键修复
  -> Q3 效果预览
  -> Q1 结构闸门复检，直到关键问题清零
  -> 用户确认是否进入 Q4 视觉打磨
  -> Q5 交付复核
  -> Final Export / Delivery
```

`scripts/export/export-diagram.sh` 只在关键结构问题清零后用于最终导出，不作为修复阶段的首选入口。

## Preflight 脚本

优先使用：

```bash
python3 scripts/quality/run-quality-preflight.py --stage hard <svg-file>
python3 scripts/quality/run-quality-preflight.py --stage soft <svg-file>
python3 scripts/quality/run-quality-preflight.py --stage full <svg-file>
```

行为约定：

- `--stage hard`：内部对应 Q1 结构闸门；执行稳定化、auto-fit、verify，然后批量跑所有 hard gate；任一 hard 脚本失败时不提前中断，继续收集同轮全部关键结构问题。
- `--stage soft`：内部对应 Q4 视觉打磨；执行稳定化、auto-fit、verify，然后批量跑 soft checks；输出可优化项 / 打磨建议汇总。
- `--stage full`：先跑 Q1 结构闸门；关键结构问题清零才继续跑 Q4 视觉打磨。
- 退出码 `0` 表示该 stage 没有待处理发现；退出码 `1` 表示发现关键结构问题或视觉打磨项；退出码 `2` 表示用法、文件或预处理失败。
- 可选 `--json-out <path>` 输出结构化报告；Agent 默认只读 compact stdout，除非需要更稳定解析。

## Q3 效果预览

每一轮关键修复或视觉打磨结束后，Agent 都必须展示当前 SVG 的阶段性效果。展示方式按 harness 能力降级：

1. 支持图片渲染：直接展示 PNG 预览图
2. 支持本地文件链接：展示 SVG / PNG 链接
3. 仅支持纯文本：展示 SVG / PNG 绝对路径

优先使用：

```bash
python3 scripts/quality/render-quality-preview.py <svg-file> --stage hard --round 1 --label after-repair
python3 scripts/quality/render-quality-preview.py <svg-file> --stage soft --round 1 --label after-polish
```

脚本会复制当前 SVG 为轮次快照，并在 `rsvg-convert` 可用时导出 PNG。即使 PNG 生成失败，也必须展示 SVG 快照链接。

用户可见回执固定包含：

```text
🖼️ 质量闸门 Q3/5｜效果预览
- 图片：使用绝对 PNG 路径输出 markdown image
- PNG：使用绝对 PNG 路径输出文件链接
- SVG：使用绝对 SVG 路径输出文件链接
```

如果当前 harness 不能渲染本地图片，保留同一段链接；如果不能渲染链接，改用绝对路径。

## Q1/Q2 结构闸门与关键修复

关键修复最多自动跑 3 轮。

每轮固定顺序：

1. 运行 `python3 scripts/quality/run-quality-preflight.py --stage hard <svg-file>`
2. 如果关键结构问题为 0，进入结构闸门通过确认点
3. 如果存在关键结构问题，Agent 读取同轮汇总报告
4. Agent 一次性批量修复所有关键结构问题，不要只修第一个
5. 运行 `python3 scripts/quality/render-quality-preview.py <svg-file> --stage hard --round <n> --label after-repair`
6. 在 Agent 回执中展示 `🖼️ 质量闸门 Q3/5｜效果预览`，包含 PNG 图或 SVG / PNG 链接
7. 回到第 1 步

如果本轮没有发生修复但要向用户展示阶段结果，也要对当前 SVG 运行 Q3 效果预览。

第 3 轮后如果仍有关键结构问题，必须停下来让用户选择：

```text
🛠️ 质量闸门 Q2/5｜关键修复
状态：已自动修复 3 轮，仍有 X 个关键结构问题
📌 下一步:
[1] 接受当前版本 - 交付 SVG + 关键问题报告，用户自行修复
[2] 继续让 Agent 修复 - 额外再跑一轮批量修复
[0] 暂停 - 先不继续
```

用户选择 `[2]` 时，只额外执行一轮关键修复；如果仍未清零，再次回到同一菜单。

## Q1 结构闸门通过确认点

关键结构问题清零后，不要默认直接进入 Q4 视觉打磨。先给用户选择：

```text
🚦 质量闸门 Q1/5｜结构闸门通过
状态：关键结构问题已清零，当前版本可以安全导出
📌 下一步:
[1] 进入 Q4 视觉打磨 - 继续优化层级、留白和汇报可读性
[2] 接受当前版本 - 直接导出 SVG / PNG
[0] 暂停 - 先不继续
```

非交互模式下默认选择 `[1]`，继续进入 Q4 视觉打磨。

## Q4 视觉打磨

视觉打磨也必须批量执行，最多自动跑 3 轮。

每轮固定顺序：

1. 运行 `python3 scripts/quality/run-quality-preflight.py --stage soft <svg-file>`
2. 如果可优化项 / 打磨建议为 0，进入 Q5 交付复核
3. 如果存在视觉打磨项，Agent 读取同轮汇总报告
4. Agent 一次性批量打磨关键视觉问题，不要逐条修完逐条重跑
5. 运行 `python3 scripts/quality/render-quality-preview.py <svg-file> --stage soft --round <n> --label after-polish`
6. 在 Agent 回执中展示 `🖼️ 质量闸门 Q3/5｜效果预览`，包含 PNG 图或 SVG / PNG 链接
7. 运行 `python3 scripts/quality/run-quality-preflight.py --stage hard <svg-file>` 作为 Q5 交付复核
8. 如果 Q5 交付复核发现关键结构问题，立即回到 Q2 关键修复
9. 如果 Q5 交付复核通过，回到第 1 步

如果本轮没有发生打磨但要向用户展示阶段结果，也要对当前 SVG 运行 Q3 效果预览。

第 3 轮后如果仍有可优化项 / 打磨建议，必须停下来让用户选择：

```text
🎨 质量闸门 Q4/5｜视觉打磨
状态：已自动打磨 3 轮，当前仍有 X 个可优化项 / 打磨建议
📌 下一步:
[1] 接受当前版本 - 直接导出交付
[2] 继续让 Agent 打磨 - 额外再跑一轮视觉打磨
[0] 暂停 - 先不继续
```

用户选择 `[2]` 时，只额外执行一轮视觉打磨；如果仍未清零，再次回到同一菜单。

## Q5 交付复核与最终导出

进入最终导出前必须满足：

- 最近一次 Q1 结构闸门已通过
- 如果执行过 Q4 视觉打磨，最近一次视觉修改后已经跑过 Q5 交付复核且通过
- 用户选择接受当前版本，或 Q4 视觉打磨已清零

最终导出使用：

```bash
scripts/export/export-diagram.sh <svg-file> [png-width]
```

如果最终导出阶段又出现关键结构问题，回到 Q2 关键修复，而不是在 export 日志里逐项临时修补。

## Agent 纪律

- 每轮只消费 compact report；不要把多个脚本的完整原始日志全部塞进用户回执。
- 每轮向用户展示阶段性 SVG / PNG 产物；不要只展示计数和菜单。
- 对用户只汇报数量、阶段和选择点；不要直接抛原始 warning / hint。
- 批量修复时先处理几何和结构，再处理视觉打磨。
- Q4 视觉打磨不追求无限清空所有 design hint；3 轮后必须交还选择权。
- 不要在关键结构问题未清零时导出 PNG 做最终交付。

## stdout 控制（防 stdout-guard）

qodercli 对单会话 stdout 有上限保护，超限会直接终止进程。质量闸门阶段必须严格控制输出量：

- 运行 preflight / 质量脚本时，**始终**用 `--json-out` 把报告写到文件，不要依赖 stdout 解析。
- Agent 回执中只展示 compact summary（错误数、关键问题列表），**禁止**贴脚本原始 stdout/stderr。
- 不要在回执中重复展示 SVG 源码或大段 XML；只展示文件路径或图片。
- 多轮修复时，每轮回执控制在 10 行以内；不要把历史轮次的报告累积到当前回执。
- 非交互模式下，Q1/Q4 菜单自动跳过时不要打印菜单文本，只输出一行状态（如 "Q1 passed, entering Q4"）。
