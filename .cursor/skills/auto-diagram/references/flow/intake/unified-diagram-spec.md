# Unified Diagram Spec

所有后端都必须先吃同一份中间语义规格。

目标不是让某个后端直接决定图长什么样，而是先把“表达任务”固定下来，再决定由谁渲染。

对外回执时，建议用 `🧱 Unified Spec 摘要` 作为阶段标题。

## 最小规格

至少要形成下面这份内部规格：

```text
title:
audience:
purpose:
core_message:
diagram_family:
formal_notation_required:
layout_preference:
visual_style:
theme_strategy:
theme_pack_ref:
style_source:
density:
aspect_ratio:
aspect_ratio_source:
canvas_size_hint:
render_strategy:
must_show:
must_not_show:
nodes:
edges:
groups:
annotations:
legend:
assumptions:
```

## 字段说明

- `title`：图的标题，最好能体现结论而不只是主题
- `audience`：主要读者是谁
- `purpose`：汇报、说服、对齐、讲结构、讲流程、指导执行等
- `core_message`：对方只能记住一句话时希望记住的内容
- `diagram_family`：架构图、流程图、能力图、矩阵图、关系图、路线图、问题归因图等
- `formal_notation_required`：是否需要 UML、BPMN、ArchiMate、Cloud、Network、Security 等正式图法
- `layout_preference`：适合的骨架家族
- `visual_style`：商务、科技、极简、氛围感、参考图学习结果等；即使命中主题包，也要保留一句当前任务自己的风格总结
- `theme_strategy`：`builtin-default`、`builtin-selected`、`reference-derived`、`custom-generated` 中的哪一种
- `theme_pack_ref`：若命中主题包，写 pack id；否则留空
- `style_source`：风格主要来自用户描述、参考图、主题包，还是几者混合
- `density`：低、中、高，或老板版、评审版、执行版
- `aspect_ratio`：最终导出的目标比例，如 `16:9`、`4:3`、`1:1`、`9:16`
- `aspect_ratio_source`：来自默认值、skill 推荐，还是用户锁定
- `canvas_size_hint`：推荐导出尺寸，如 `1920x1080`
- `render_strategy`：计划使用的后端
- `must_show`：必须出现的模块、边、说明
- `must_not_show`：不能出现、必须弱化、必须移出主图的内容
- `nodes / edges / groups / annotations / legend`：图的基础语义元素
- `assumptions`：哪些是用户已确认，哪些是领域补全，哪些是你的推断

## 汇报级补充规格

如果是汇报级大图、复杂技术架构图、现状到目标态图，还必须补充：

```text
zones:
  title_zone:
  footer_zone:
  lane_label_zone:
  node_zone:
  annotation_zone:
layout_guardrails:
  min_header_content_gap:
  min_footer_content_gap:
  min_node_gap:
  min_stage_fill_ratio:
  max_child_outer_slack:
  forbidden_line_areas:
  edge_differentiation:
  underlay_edge_policy:
  legend_semantics:
  max_label_lines:
```

## 规格纪律

- 先固定 spec，再写任何具体语法
- spec 里的 `core_message` 必须驱动取舍
- `must_not_show` 不能留空思考
- `theme pack` 只负责视觉层，不能代替 diagram family、layout family 或比例判断
- 即使命中主题包，也允许在当前任务里做少量 style override；但 override 不能大到把 pack 变成一次性模板
- 如果用户已经指定比例，spec 必须保留该比例，不得在正式渲染前静默改掉
- 如果用户没有指定比例，必须在草稿图阶段先形成比例建议，再把确认后的比例写回 spec
- `min_stage_fill_ratio` 和 `max_child_outer_slack` 用来约束“画布有没有被吃满”，以及子区域是否离母区域边缘太远
- `min_header_content_gap` / `min_footer_content_gap` 用来约束页面 chrome 与主图主体之间的垂直呼吸感
- `edge_differentiation` 用来声明复杂边是优先靠几何分流，还是允许用颜色分层辅助识别
- `underlay_edge_policy` 只约束箭头；如果允许 `under-node`，必须显式写明只允许箭头主干被节点遮挡，其他元素不享有此例外
- `legend_semantics` 用来声明当图里存在多通道边色、虚实线或角色配色时，legend 应该解释到什么粒度
- 如果正式图法与汇报效果冲突，要在 spec 中明确处理策略
- 如果需要两张图，也要在 spec 中先承认“一张总览图 + 一张正式图”这样的组合方案
