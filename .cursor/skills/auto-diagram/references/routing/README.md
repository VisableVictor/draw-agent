# Routing Phase

这一阶段负责先定“表达路径”，再给草稿图确认最终画面，最后才进入“渲染后端”。

## 先读什么

1. [../principles/layout-over-template.md](../principles/layout-over-template.md)
2. [../backends/backend-matrix.md](../backends/backend-matrix.md)
3. 若需要正式图法判断，再转 [../formal/README.md](../formal/README.md)
4. 选定表达路径后，再读 [layout-and-rendering.md](layout-and-rendering.md)
5. 在正式渲染前，固定读 [draft-preview.md](draft-preview.md)

## 这一阶段要完成什么

- 先判断是否需要正式图法
- 再判断是否要走两张图策略
- 再判断布局骨架和阅读路径
- 先给草稿图确认最终画面和导出比例
- 最后才确定具体后端

## 不要做什么

- 不要把 layout family 当成现成模板
- 不要为了“看起来高级”强上不适配的骨架
- 不要在高边密度关系图上硬用 SVG 手工绕线
- 不要在草稿图确认前提前进入正式 SVG 精修或其他重渲染
- 不要在 routing 阶段把所有后端 contract 一次性全读
