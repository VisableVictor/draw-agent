# Intake Phase

这一阶段负责把 brainstorm 结果压缩成可执行规格，并按需补齐缺口。

## 先读什么

1. [../../principles/spec-before-render.md](../../principles/spec-before-render.md)
2. [../../principles/reference-boundary.md](../../principles/reference-boundary.md)
3. [intake-and-classification.md](intake-and-classification.md)
4. 若信息不完整但方向明确，再读 [domain-completion.md](domain-completion.md)
5. 若用户提供参考图，再读 [reference-image-mode.md](reference-image-mode.md)
6. 若 style 已命中主题包或要准备风格沉淀，再读 [../../themes/README.md](../../themes/README.md)
7. 在开始任何后端语法前，固定读 [unified-diagram-spec.md](unified-diagram-spec.md)

## 这一阶段要完成什么

- 把原始输入和 brainstorm 结果压成 `Diagram Brief`
- 明确哪些是用户明确给出，哪些是领域补全，哪些是推断
- 如果图型还没锁定，给 2-4 个候选并推荐一个
- 如果风格已经明显命中某个主题包或参考图学习路径，也要一并锁清主题策略
- 如果有参考图，只提炼风格和骨架适配，不盲抄原内容
- 在进入 routing 前，形成统一 spec

## 不要做什么

- 不要把 intake 重新做成第二轮 brainstorm
- 不要先选后端，再倒推 spec
- 不要把参考图的文字和结构直接抄进新图
