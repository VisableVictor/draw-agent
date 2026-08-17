# Backend Contracts

后端是 `auto-diagram` 的内部责任。只在 routing 已经锁定表达路径、且草稿图已经被用户确认后，才展开 backend matrix 和对应 contract。

## 先读

- [backend-matrix.md](backend-matrix.md)
- [contracts/README.md](contracts/README.md)

## 只读一个主后端 contract

- `SVG-first`：读 [contracts/svg-contract.md](contracts/svg-contract.md)
- `Mermaid`：读 [contracts/backend-contract-mermaid.md](contracts/backend-contract-mermaid.md)
- `Graphviz`：读 [contracts/backend-contract-graphviz.md](contracts/backend-contract-graphviz.md)
- `PlantUML`：读 [contracts/backend-contract-plantuml.md](contracts/backend-contract-plantuml.md)

## 需要脚本时再读脚本

- `scripts/render/render-mermaid.sh`
- `scripts/render/render-graphviz.sh`
- `scripts/render/render-plantuml.sh`
- `scripts/render/validate-mermaid.sh`
- `scripts/render/validate-graphviz.sh`
- `scripts/render/validate-plantuml.sh`

## 共同行为约束

- 先服从 unified spec，再写具体语法
- 先过草稿图确认，再进入正式后端语法
- 最终渲染必须服从草稿阶段已经锁定的比例，不得在后端阶段偷偷改画幅
- 如果 spec 已锁定主题包，后端负责把 token 落到视觉层，不负责借主题包回改布局骨架
- 主链路、分组和阅读顺序必须可见
- 不得为了复用模板而牺牲主叙事
- `SVG-first` 仍是汇报型大图的主战场，但不是所有图都必须走 SVG
- 任何后端只要产出 `.svg`，交付前都必须按 `svg-contract.md` 静默完成稳定化与受控状态校验
- 不要在 routing 阶段把 `contracts/` 整包预读
