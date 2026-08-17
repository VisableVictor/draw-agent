# Graphviz Backend Contract

适用于高边密度依赖图、模块关系图、包关系图、调用关系图。

## 输出规则

- 必须使用 ` ```dot ` fence
- 优先使用 `digraph`
- 先服从 unified spec，再写 DOT 语法

## 适用边界

适合：

- 边很多
- 自动布局价值高
- 重点是关系，不是视觉舞台

不适合：

- 讲故事型的大图
- 需要强视觉风格迁移
- 主要目标是汇报审美和舞台感

## 关键护栏

- cluster 名称必须规范
- 节点 ID 要稳定且避免含糊空格
- 属性写法保持明确，避免渲染歧义
- 如果 rank 失控、边过密，先调布局，再决定是否拆图

## Fallback

- 如果关系图需要强视觉表达，回退到 SVG-first
- 如果图其实是正式 UML / BPMN / Network 类型，回退到 PlantUML
- 如果只是简单流程，不要硬用 Graphviz，回退到 Mermaid
