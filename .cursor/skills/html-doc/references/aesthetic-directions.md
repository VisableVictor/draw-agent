# 美学定调详细参考

> 本文件是 SKILL.md 中 Step 0 的详细参考。核心决策流程在 SKILL.md，此处提供完整的字体代码、配色变量、背景质感选项和自检清单。

## 字体引入

所有方向均从 Google Fonts CDN 引入。在 `<head>` 中加（以方向 A 为例）：

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,800&family=Inter+Tight:wght@400;500;600&display=swap" rel="stylesheet">
```

并通过 CSS 变量绑定：

```css
:root {
  --font-display: 'Fraunces', Georgia, serif;
  --font-body: 'Inter Tight', system-ui, sans-serif;
}
body { font-family: var(--font-body); }
h1, h2, h3 { font-family: var(--font-display); }
```

## 配色 CSS 变量约定

每个方向都以 CSS 变量集中定义，便于整体换皮：

```css
:root {
  --color-bg: #FAF7F2;          /* 页面背景 */
  --color-surface: #FFFFFF;     /* 卡片/表面 */
  --color-ink: #1A1815;         /* 主文字 */
  --color-muted: #6B6760;       /* 次要文字 */
  --color-primary: #B8472A;     /* 主色（如砖红/烫金）*/
  --color-accent: #C9A961;      /* 强调色 */
  --color-line: #E8E2D8;        /* 分割线 */
}
```

所有颜色优先用 `var(--color-xxx)` 而非硬编码 hex 或 Tailwind 默认色，换皮只改这 7 个变量。

## 六套方向完整参数

### A. 编辑杂志风
- **Display**：Fraunces (400/600/800)
- **Body**：Inter Tight (400/500/600)
- **Google Fonts URL**：`family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,800&family=Inter+Tight:wght@400;500;600`
- **主色**：`#B8472A`（砖红）| **强调色**：`#C9A961`（烫金）| **背景**：`#FAF7F2`

### B. 极简瑞士风
- **Display**：Space Grotesk (500/700)
- **Body**：Inter (400/500)
- **Google Fonts URL**：`family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500`
- **主色**：`#1A1A1A`（纯黑）| **强调色**：`#E63946`（瑞士红）| **背景**：`#FAFAFA`
- **CSS 变量**：`--color-primary: #1A1A1A; --color-accent: #E63946; --color-bg: #FAFAFA;`

### C. 自然有机
- **Display**：Bitter (400/600/700)
- **Body**：Source Sans 3 (400/500)
- **Google Fonts URL**：`family=Bitter:wght@400;600;700&family=Source+Sans+3:wght@400;500`
- **主色**：`#2D6A4F`（森林绿）| **强调色**：`#D4A373`（大地棕）| **背景**：`#F5F1EB`
- **CSS 变量**：`--color-primary: #2D6A4F; --color-accent: #D4A373; --color-bg: #F5F1EB;`

### D. 学术严肃
- **Display**：Libre Baskerville (400/700)
- **Body**：Crimson Pro (400/500)
- **Google Fonts URL**：`family=Libre+Baskerville:wght@400;700&family=Crimson+Pro:wght@400;500`
- **主色**：`#1B3A5C`（学院藏蓝）| **强调色**：`#8B6914`（旧金）| **背景**：`#FAF8F4`
- **CSS 变量**：`--color-primary: #1B3A5C; --color-accent: #8B6914; --color-bg: #FAF8F4;`

### E. 科技冷冽
- **Display**：Outfit (600/800)
- **Body**：DM Sans (400/500)
- **Google Fonts URL**：`family=Outfit:wght@600;800&family=DM+Sans:wght@400;500`
- **主色**：`#6366F1`（靛蓝）| **强调色**：`#06B6D4`（青）| **背景**：`#0F172A`（深蓝黑底）
- **CSS 变量**：`--color-primary: #818CF8; --color-accent: #22D3EE; --color-bg: #0F172A; --color-ink: #E2E8F0; --color-surface: #1E293B; --color-muted: #94A3B8; --color-line: #334155;`

### F. 暖色商务
- **Display**：DM Serif Display (400)
- **Body**：Plus Jakarta Sans (400/500/600)
- **Google Fonts URL**：`family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@400;500;600`
- **主色**：`#C2410C`（赤陶橙）| **强调色**：`#CA8A04`（暖金）| **背景**：`#FFFBF5`
- **CSS 变量**：`--color-primary: #C2410C; --color-accent: #CA8A04; --color-bg: #FFFBF5;`

## 背景质感（必加其一）

纯白底是 AI 套皮重灾区。从下列任选其一加入 `<body>` 或主容器：

1. **Noise grain**：SVG `<filter feTurbulence>` 生成颗粒，`opacity: 0.03~0.05` 叠在背景
2. **几何网格**：`background-image: linear-gradient(...)` 画细网格线
3. **微渐变**：`background: radial-gradient(circle at 20% 0%, ..., transparent)` 在角落晕开主色
4. **装饰线条**：页面边缘加细装饰线（双线、虚线），杂志感
5. **大字水印**：超大字号的英文/年份/数字作为底层装饰

## 顶部美学注释（必写）

生成的 HTML `<!DOCTYPE html>` 之后必须有一段注释，明示本次决策：

```html
<!--
  Aesthetic Direction: A. 编辑杂志风
  Display Font: Fraunces  |  Body Font: Inter Tight
  Primary: #B8472A  |  Accent: #C9A961  |  Bg: #FAF7F2
  Texture: noise grain (opacity 0.04)
-->
```

这段注释是给后续维护者看的，也是给 AI 自己看的——下次回到这份文件能立刻接上设计语境。

## 设计风格建议

### 导航交互
- 使用 `scroll-margin-top` 处理 sticky 导航的锚点偏移
- 可用 CSS `:target` 伪类实现点击导航后的高亮效果
- 纯 CSS 无法实现滚动自动高亮（需要 JS IntersectionObserver）
- 导航链接加 `transition` 实现 hover 平滑过渡

### 内容排版
- 技术文档类页面：`max-w-5xl` 比 `max-w-7xl` 更易读
- 段落间距用 `mb-6` ~ `mb-8`，不要太松
- 引用/重点内容用 `border-l-4` 左边框 + 灰色背景突出
- 表格用 `text-sm`，内容多时可加 `overflow-x-auto`

### 配色补充

配色方案在 Step 0 的 CSS 变量中集中定义。以下是用色原则：
- 主色用法**集中而锐利**（关键数字、CTA、章节标号、标题首字），不要均匀涂在所有卡片头部
- 图表配色从主色 + 强调色衍生，用透明度/明度变化产生序列，避免一条线一种新颜色

### 响应式（用户要求时才加）
- 导航栏：`hidden md:flex` 移动端隐藏，桌面端显示
- 表格：外层包 `overflow-x-auto` 支持横向滚动
- 卡片网格：`grid-cols-1 md:grid-cols-3` 自适应

## Anti-AI-Slop Checklist（生成后自检）

输出 HTML 之前，对照以下清单逐项检查，**任一未达标必须返工**。**定期报告预设模式跳过此自检**（样式已固定，不需要差异化）。

### 视觉差异化（必查）
- [ ] 主色**不是** `#2563EB` 或类似的 Tailwind 默认蓝
- [ ] 没有出现「白底 + 紫色渐变」这种 AI 经典套皮
- [ ] 字体**不是** Inter / Roboto / Arial / system-ui 默认栈，已通过 Google Fonts 引入有性格的配对
- [ ] display 字体和 body 字体**形成对比**（衬线 vs 无衬线 / 字重对比 / 宽窄对比 至少一项）
- [ ] 背景**不是**纯白或纯灰，至少加了一种质感（noise / 几何 / 微渐变 / 装饰线 / 大字水印）

### 结构差异化（必查）
- [ ] 页面中**不超过 1 处**三列等宽卡片网格
- [ ] 至少包含以下一项**版式亮点**：字号 ≥ text-7xl 的元素 / 非对称布局 / 装饰性 SVG / 引文挂边（border-l-4 + 大字号）/ 超出标准网格的元素
- [ ] 标题字号阶梯有戏剧性（h1 和正文 body 至少 4 倍差距）
- [ ] 页面中至少使用 **3 种不同的纵向间距值**（如 mb-4、mb-12、mb-24 同时出现）
- [ ] 组件使用了所选方向对应的变体（见 `template-vue-guide.md` 组件变体表），不是 Tailwind 默认样式

### 工程合规（必查）
- [ ] 顶部 HTML 注释写明本次的 Aesthetic Direction、字体、主色、背景质感
- [ ] 颜色统一走 CSS 变量，不散落 hex 或硬编码 Tailwind 颜色类
- [ ] 中文 `lang="zh-CN"`、CDN 链接稳定
- [ ] 单文件可双击打开，无需本地服务器

### 方向选择合理性（必查）
- [ ] 本次选择的方向与 SKILL.md「快速决策参考」映射表推荐一致；若不一致，有明确理由（如用户指定、主题特殊需求）
