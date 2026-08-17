# Delivery Phase

这一阶段负责“图 + 讲法 + 导出分叉”。

## 先读什么

1. [../principles/report-grade-output.md](../principles/report-grade-output.md)
2. [reporting-output.md](reporting-output.md)
3. 如需稳定交付骨架，再读 [delivery-templates.md](delivery-templates.md)
4. 若用户确认要把参考图风格沉淀为常驻主题包，再读 [../themes/promotion-flow.md](../themes/promotion-flow.md)

## 这一阶段要完成什么

- 返回 `✅ 当前产出`
- 明确当前图片的比例和画布尺寸
- 说明当前风格来自内置主题包、自定义风格，还是参考图学习
- 确认最近一次 Q1 结构闸门已通过；如果 Q4 视觉打磨修改过 SVG，确认最近一次 Q5 交付复核已通过
- 给一句主结论和推荐阅读路径
- 在需要时补 30 秒讲法、密度分档建议、追问准备
- 只有当图片产物已存在后，才处理 PPTX 分叉
- 如果当前风格来自参考图学习且值得复用，询问是否沉淀为常驻主题包
- 如果交付链还没完成 SVG 稳定化与受控状态校验，在内部静默补齐，不单独向用户播报脚本过程

## PPTX 纪律

- 用户一开始明确要求 `pptx`，可以直接导出
- 用户没明确要求时，必须先给一次明确选择
- 任何 `pptx` 导出都必须发生在 Q1 结构闸门通过之后
- 稳定图片版优先；只有用户明确要“可编辑 PPT”时，才走 editable 模式
- 只对本 skill 产出的受控 SVG 承诺可编辑导出
- 受控 SVG 默认意味着已经执行 `scripts/stabilize-svg.cjs` 或 `scripts/finalize-svg.cjs`
- “沉淀为主题包”只在参考图学习任务里出现，不要对普通内置主题包任务重复追问
