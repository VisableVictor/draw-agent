# Quality Phase

这层负责“没过就不交付”的质量闸门和 post-check 自修复。

## 先读什么

1. [../principles/report-grade-output.md](../principles/report-grade-output.md)
2. [quality-gates.md](quality-gates.md)
3. [batch-repair-loop.md](batch-repair-loop.md)
4. 如需更完整的分层设计规则，再读 [design-quality-system.md](design-quality-system.md)

## 这一阶段要完成什么

- 先用 `scripts/quality/run-quality-preflight.py --stage hard <svg-file>` 批量跑 Q1 结构闸门，不要遇到第一个关键结构问题就停
- Agent 基于同轮结构闸门汇总报告进入 Q2 关键修复，最多自动跑 3 轮；第 3 轮仍未清零时按交互协议让用户选择是否接受当前版本或继续
- 每轮 Q2 关键修复后，用 `scripts/quality/render-quality-preview.py` 生成并展示 `🖼️ 质量闸门 Q3/5｜效果预览`
- Q1 结构闸门通过后，先让用户选择是否进入 Q4 视觉打磨，或直接导出当前版本
- Q4 视觉打磨用 `scripts/quality/run-quality-preflight.py --stage soft <svg-file>` 批量跑可优化项 / 打磨建议，不要逐条打磨逐条重跑
- Q4 视觉打磨最多自动跑 3 轮；每轮视觉修改后必须跑一次 Q5 交付复核
- 每轮 Q4 视觉打磨后，也必须生成并展示阶段性 SVG / PNG 预览
- 看画布是否被合理填满，是否存在某一侧异常大的空白带，或子区域离母区域边缘过远
- 看页面标题、副标题、页脚 legend 是否被主图内容、箭头或说明卡侵入
- 判断复杂长箭头是否应该改成更高辨识度的颜色分层，而不是一味靠拐弯规避
- Q1 结构闸门通过并完成用户选择后，再导出 PNG 做肉眼检查
- 如果最终导出阶段又出现结构性错误，回到 Q2 关键修复，而不是在 export 日志里逐项临时修补

## 常用脚本

- `scripts/quality/check-svg-attribution.py`
- `scripts/quality/lint-svg-diagram.py`
- `scripts/quality/check-svg-edge-clearance.py`
- `scripts/quality/check-svg-node-padding.py`
- `scripts/quality/check-svg-page-chrome.py`
- `scripts/quality/check-layout-rhythm.py`
- `scripts/quality/check-visual-hierarchy.py`
- `scripts/quality/check-svg-legend-semantics.py`
- `scripts/quality/review-diagram-quality.py`
- `scripts/quality/run-quality-preflight.py`
- `scripts/quality/render-quality-preview.py`
- `scripts/export/export-diagram.sh`

## 不要做什么

- 不要把原始 warning 直接甩给用户当结果
- 不要在结构性错误仍存在时直接交付
- 不要在关键结构问题未清零时跑完整 final export 当作交付入口
- 不要让 Q4 视觉打磨无限追求清空所有 design hint；3 轮后必须交还选择权
- 不要只给脚本计数而不展示本轮 SVG / PNG 产物；用户可见回执必须使用 Q 阶段名
- 不要让主图里出现伪水印、重复品牌署名，或 `auto-diagram 生成` 这类手工 attribution
- 不要为了通过连通性，允许箭头压字、穿说明卡、或沿边框长距离滑行
- 不要把页面标题、副标题、footer legend 当成可被牺牲的装饰层
- 只有显式标记为 `under-node` 的箭头主干，才允许在节点下层被砖块局部遮挡；文字、标签、说明卡和其他元素不得享有这个例外
