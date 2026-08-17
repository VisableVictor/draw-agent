# PlantUML Backend Contract

适用于 UML、BPMN、ArchiMate、Cloud、Network、Security 等正式图法模式。

## 输出规则

- 必须使用 ` ```plantuml ` 或 ` ```puml ` fence
- 每张图都必须有 `@startuml` 和 `@enduml`
- 先服从 unified spec，再写具体图法语法

## 适用边界

适合：

- 正式图法
- 行业标准表达
- 需要 stencil / icon / provider assets 的场景

不适合：

- 以视觉舞台感为第一目标的汇报封面图
- 需要极强版式控制的汇报级主图

## 关键护栏

- 先确认图法种类，再写语法，不要混着写
- 图标和 stencil 只用于提升识别度，不要为了炫技堆满
- 线和元素过多时，优先分层或拆图
- 正式图法的关系语义要正确，不要用看起来差不多的箭头糊弄

## 交付说明

使用 PlantUML 时，默认要附一句说明：

- 采用了什么正式图法
- 这张图最值得先看哪一层、哪一条主线

## Fallback

- 如果用户真正想要的是“拿去讲”的总览图，回退或补充 SVG-first
- 如果图非常简单且只想嵌文档，可回退到 Mermaid
