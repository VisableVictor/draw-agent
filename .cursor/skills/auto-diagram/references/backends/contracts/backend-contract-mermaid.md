# Mermaid Backend Contract

适用于简单流程图、轻量时序图、状态图、轻量链路图。

## 输出规则

- 必须使用 ` ```mermaid ` fence
- 默认使用 `flowchart` 而不是 `graph`
- 先服从 unified spec，再写 Mermaid 语法

## 适用边界

适合：

- 结构简单
- 节点数量有限
- 关系主轴清晰
- 目标是快速嵌入 Markdown 文档

不适合：

- 汇报级高密大图
- 需要精确控制留白和走线的图
- 关系极多的依赖图

## 关键护栏

- 子图要使用稳定 ID，不要直接引用显示名称
- 容易冲突的特殊字符要转义或改写
- 节点文本过长时，优先简化文案，不要硬塞
- 如果画面变得拥挤，优先拆图，而不是继续堆在一张图里

## Fallback

- 如果只是简单流程但 Mermaid 语法受限，回退到 SVG-first
- 如果关系太密导致线混乱，回退到 Graphviz
- 如果图实际上是正式 UML/BPMN，回退到 PlantUML
