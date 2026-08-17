# Theme Packs

`theme pack` 是 `auto-diagram` 的可复用视觉资产层。

它服务的是：

- 颜色、字体、间距、线条、卡片 chrome 等视觉令牌
- 汇报气质、技术感、日间/暗夜倾向等风格提示
- 参考图风格在未来任务中的稳定复用

它**不**服务的是：

- diagram family 选择
- layout family 选择
- 节点坐标、骨架、阅读路径
- 用固定模板替代内容驱动的构图

## 什么时候读

- brainstorm 阶段要推荐最适合的内置主题包
- 用户问“有哪些主题包”
- 用户给了自定义风格词，需要判断是命中已有主题包，还是走自由风格生成
- 用户给了参考图，希望本次风格以后还能复用
- `SVG-first` 任务需要把视觉令牌稳定映射到具体 SVG / HTML 壳子

## 先读什么

1. [theme-pack-spec.md](theme-pack-spec.md)
2. 若只需要知道当前可选主题包数量：运行 `python3 scripts/theme/list-theme-packs.py --count`
3. 若需要看全部可选主题包：运行 `python3 scripts/theme/list-theme-packs.py --details`
4. 若已经命中某个主题包，再读对应 pack 说明
5. 若用户确认把参考图风格沉淀为常驻 pack，先读 [promotion-flow.md](promotion-flow.md)
6. 执行时优先运行 `python3 scripts/theme/promote-reference-style.py ...`
7. 若需要更底层控制，再运行 `python3 scripts/theme/create-learned-theme-pack.py ...`
8. 若新增或修改 pack，运行 `python3 scripts/theme/validate-theme-pack.py`

## 当前内置主题包

- [default-dark-architecture.md](packs/default-dark-architecture.md)
- [default-day-blue.md](packs/default-day-blue.md)
- [pine-deep-green.md](packs/pine-deep-green.md)

## 主题策略顺序

- 用户给参考图并明确说“按这个感觉”：优先 `reference-derived`
- 用户自己给风格词或风格句：优先 `custom-generated`
- 用户没有给明确风格，但当前图很适合某个内置 pack：推荐 `builtin-selected`
- 都没有明显信号时：回退到 `builtin-default`

换句话说，`theme pack` 是 style 的可复用捷径，不是 style 的唯一来源。

## Brainstorm 纪律

- 默认只推荐 **1 个最适合的主题包** + **1 句最适合的视觉方向**
- 不要每轮都把所有 pack 全量列给用户
- 每轮如果给了主题包建议，都要顺手提示：
  - `我们现在有 X 个主题包可选；如果你想看全量，我可以再展开`
- 这里的 `X` 默认通过 `python3 scripts/theme/list-theme-packs.py --count` 获取
- 如果用户自己编了风格词，例如“恬静风格”“杂志感”“咨询公司汇报风”，不要强拉回主题包菜单；先按用户意图收束 `visual_style_summary`

## Intake / Spec 纪律

- 即便命中了主题包，`visual_style` 也不能留空
- `visual_style` 仍然要保留一句人类可读的风格总结
- `theme pack` 负责给出稳定视觉底座
- 当前任务的 audience、purpose、diagram family、density、reference cues 仍然可以对主题包做轻量覆盖

## 参考图风格沉淀

- 参考图任务默认先学习风格并完成当次出图
- 不要在 brainstorm 或 intake 阶段就自动把参考图落库成常驻主题包
- 只有当最终大图已经产出，且用户确认这次风格值得复用，才允许继续问：
  - `是否把这次风格抽象为常驻主题包，以后都可以选`
- 如果用户确认保存，再补 1 个事实即可：
  - 主题包名称
- 如果用户不想起名，可以由 skill 给一个短推荐名
- 用户确认后，优先用 `python3 scripts/theme/promote-reference-style.py ...` 走高层 promotion 热路径
- 只有当你需要覆盖默认推断，才直接降级使用 `create-learned-theme-pack.py`
