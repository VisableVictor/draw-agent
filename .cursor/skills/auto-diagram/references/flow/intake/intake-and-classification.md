# Intake And Classification

先把用户的原始输入和 brainstorm 结果一起压缩成一份最小 diagram brief。

注意：

- intake 发生在 Mandatory Brainstorm Lock 之后
- 这里不是重新问一遍需求，而是把已确认内容压缩成可执行规格
- 如果 brainstorm 还没锁定核心信息，不能跳过直接 intake

交互格式统一遵守 `references/shared/interaction-contract.md`。

## 最小回执

- `📦 Diagram Brief`
- `audience`: 这张图主要给谁看
- `purpose`: 这张图是用来汇报、说服、对齐、讲结构还是指导执行
- `goal`: 这张图想解释、说服、汇报进展、争取资源，还是讲清结构
- `core_message`: 只能记住一句话时，希望对方记住什么
- `known_content`: 用户已经明确给出的模块、层、流程、依赖、风险
- `unknowns`: 当前还缺什么
- `style_source`: 当前风格主要来自用户描述、主题包、参考图，还是混合来源
- `theme_strategy`: `builtin-default` / `builtin-selected` / `reference-derived` / `custom-generated`
- `theme_pack_ref`: 若已命中主题包，则写 pack id；否则留空
- `density`: 低 / 中 / 高
- `formal_notation_required`: 是否需要正式图法
- `candidate_types`: 2-4 个候选图型
- `⚠️ 假设 / 风险`: 哪些内容还属于推断

## 图型分类

常见图型：

- 技术架构图
- 流程图 / 责任流转图
- 能力地图 / 平台地图
- 矩阵图 / 对比图
- 关系图 / 依赖图
- 组织图
- 路线图 / 现状到目标态图
- 问题归因图

## 推荐候选的方式

当图型不明确时，不要让用户重新大段描述。按下面方式给建议：

1. 推荐一个你认为最合适的图型，并说明理由
2. 再给 1-3 个备选图型，说明它们适合什么前提

如果需要用户拍板，优先用菜单：

```text
📍 当前: Diagram Brief 已整理完成
📌 下一步:
[1] 确认推荐图型 - 直接进入草稿图阶段
[2] 切换备选图型 - 按另一个表达骨架重组内容
[3] 补充内容 - 再补充会影响节点和分组的信息
[0] 暂停 - 先不继续
```

如果已经明确需要正式图法，还要同步判断：

- 是不是应该进入 `PlantUML` 正式图法模式
- 是否还需要额外补一张汇报型总览图

## 向上汇报默认偏好

如果用户没有明确指出别的目标，默认优先：

- 讲清主链路
- 讲清分层结构
- 讲清从问题到方案的映射
- 讲清现状、目标态与路径

避免默认走复杂自由连线。
