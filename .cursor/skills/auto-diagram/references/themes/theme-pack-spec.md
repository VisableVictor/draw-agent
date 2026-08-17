# Theme Pack Spec

`theme pack` 的目标是把“可稳定复用的视觉底座”结构化，但不要把图生成过程绑死。

## 定位

`theme pack` 是：

- style layer 的结构化资产
- 视觉令牌和轻量风格提示的组合
- `auto-diagram` 在 brainstorm / intake / render / delivery 间共享的视觉真相源

`theme pack` 不是：

- layout template
- diagram family
- 画布比例
- 节点坐标
- 一次性 prompt prose 的原样存档

## 文件落位

- 结构化 token：`assets/themes/<id>/theme-pack.json`
- 人类可读说明：`references/themes/packs/<id>.md`
- 可选预览：`assets/themes/<id>/preview.svg|png|html`

## 顶层字段

推荐字段：

- `id`
- `display_name`
- `kind`
  - `builtin`
  - `learned`
- `status`
  - `default`
  - `available`
  - `draft`
- `summary`
- `source`
- `preview_asset`（可选）
- `recommended_for`
- `default_when`
- `avoid_for`
- `tokens`
- `soft_hints`

## `source` 字段

至少包含：

- `origin`
  - `built-in`
  - `reference-derived`
  - `manual`
- `notes`

可选包含：

- `inspired_by`
- `reference_image`
- `confidence_notes`

## `tokens` 字段

`tokens` 里优先保留那些可脚本化、可稳定映射到 SVG / HTML / PPTX 的内容。

至少包含这些分组：

- `background`
- `semantic_roles`
- `typography`
- `spacing`
- `shape`
- `lines`
- `chrome`

### `background`

推荐包含：

- `page`
- `surface`
- `canvas`
- `grid`
- `stage_fill`
- `stage_stroke`
- `title`
- `subtitle`
- `text_primary`
- `text_secondary`
- `edge`
- `edge_label`

### `semantic_roles`

推荐至少覆盖这些语义角色：

- `frontend`
- `backend`
- `database`
- `cloud`
- `security`
- `external`
- `message_bus`

每个角色建议包含：

- `fill`
- `stroke`
- `text`

### `typography`

推荐包含：

- `families`
- `title`
- `subtitle`
- `group_title`
- `node_title`
- `node_body`
- `note_title`
- `note_body`
- `edge_label`
- `legend`

每个文字层级建议保留：

- `size`
- `weight`
- `letter_spacing_em`

### `spacing`

推荐包含：

- `diagram_padding`
- `stage_padding`
- `group_padding`
- `component_min_gap_y`
- `legend_gap_y`
- `card_gap`
- `node_pad_x`
- `node_pad_top`
- `node_pad_bottom`

### `shape`

推荐包含：

- `node_radius`
- `group_radius`
- `stage_radius`
- `card_radius`

### `lines`

推荐包含：

- `stroke_width`
- `boundary_dash`
- `security_dash`
- `auth_dash`
- `arrow_marker_width`
- `arrow_marker_height`
- `arrow_color`
- `edge_label_backplate`

### `chrome`

这是指页面舞台和外围壳子，不是布局骨架。

推荐包含：

- `html_shell`
- `header_pulse`
- `summary_cards`
- `footer`
- `grid_background`
- `opaque_node_mask`

## `soft_hints` 字段

这里放那些值得复用、但不应该硬编码成几何规则的内容。

推荐包含：

- `mood`
- `density_bias`
- `annotation_style`
- `style_summary_seed`
- `allowed_overrides`
- `avoid`

## 生成纪律

- 命中主题包时，优先应用 `tokens`
- 同时保留一条人类可读的 `visual_style` 摘要，说明当前任务到底要呈现什么感觉
- 允许当前任务覆盖部分 token，例如：
  - 更暖或更冷的强调色
  - 更轻或更重的 note card
  - 减少或取消 summary cards
- 但不要为了局部覆盖，把整个 pack 重写成一次性风格

## 与现有流程的关系

- brainstorm：负责推荐是否命中某个主题包
- intake：负责把主题策略写进 unified spec
- routing：负责先锁布局，再决定视觉层如何落 pack
- backends：负责把 token 映射到 SVG / HTML / PPTX
- delivery：负责在需要时询问是否将参考图学习结果提升为常驻主题包
- promotion flow：负责在用户确认后，把参考图学习结果落成可复用 learned pack

## Learned Pack 纪律

- `learned` pack 默认来自参考图学习结果
- 先完成一次真实出图，再决定是否沉淀
- 不确定的视觉信息，优先放进 `soft_hints` 或 `source.confidence_notes`
- 只把足够稳定、足够可复用的内容写进 `tokens`
- 如果某些字段只能靠猜，不要伪装成精确 token
- 推荐用 `python3 scripts/theme/create-learned-theme-pack.py ...` 从最接近的 base pack 派生 learned pack，而不是从零手抄整份 token
- learned pack 默认至少要同时落：
  - `assets/themes/<id>/theme-pack.json`
  - `references/themes/packs/<id>.md`
- 如果有可复用的风格预览，也可以附带：
  - `assets/themes/<id>/preview.svg|png|html`
