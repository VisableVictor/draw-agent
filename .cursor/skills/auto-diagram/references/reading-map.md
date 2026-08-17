# Auto Diagram Reading Map

## 默认读取顺序

1. [shared/interaction-contract.md](shared/interaction-contract.md)
2. [flow/brainstorm/README.md](flow/brainstorm/README.md)
3. 若 style 需要主题包推荐 / 自定义风格收束 / 参考图风格沉淀，再读 [themes/README.md](themes/README.md)
4. [flow/intake/README.md](flow/intake/README.md)
5. [routing/README.md](routing/README.md)
6. 若命中正式图法，再读 [formal/README.md](formal/README.md)
7. 进入正式渲染前，读 [routing/draft-preview.md](routing/draft-preview.md)
8. 草稿图确认后，再读 [backends/README.md](backends/README.md)
9. 正式图初版完成后，读 [quality/README.md](quality/README.md)
10. 准备交付时，读 [delivery/README.md](delivery/README.md)

## 不要读什么

- 不要跳过 brainstorm 直接 intake 或出图
- 不要在 unified spec 形成前预读全部 backend contract
- 不要把主题包当固定模板，绕过 style 判断或 layout 判断
- 不要跳过草稿图确认直接开始正式 SVG 或重渲染
- 不要把所有 formal pack 和 examples 一次性全读
- 正式图法只有在需求明确命中时才展开
- 质量与交付文件放在后半段，不要在入口阶段把它们塞进 prompt 主体
- SVG metadata 状态稳定化属于内部后处理，不要在前置阶段把它当成独立用户可见步骤；交付图不注入可见水印
- `references/` 根目录下保留的同名旧文件，默认视为 compatibility shim，不是 canonical 正文
