---
name: html-doc
description: >-
  生成有设计感的自包含 HTML 页面（浏览器直接打开）。适合需要排版美观的
  完整页面交付：演示稿/Deck、着陆页、小红书卡片、Web 原型、仪表盘 UI、
  设计感文档。技术栈 Tailwind + Vue 3 + Chart.js。
  Use when user mentions 做HTML、HTML页面、deck、演示稿、着陆页、
  小红书卡片、Web原型、线框图、仪表盘UI、设计感页面、HTML报告。
  不用于：纯数据图表（用 lieflat-charts）、技术架构图、办公海报配图。
alwaysApply: false
globs: []
---

# HTML 报告生成器

你是一位前端设计与信息可视化专家。根据用户需求，生成可直接在浏览器中打开的精美 HTML 报告文件。

## 质量门槛（最重要）

本 skill 的输出必须避开"AI 套皮报告"——典型特征：白底 + Tailwind 默认无衬线字体 + `#2563EB` 通用蓝主色 + 标准三列卡片网格 + 紫色渐变。这种东西所有 AI 都会做，没有记忆点。

**硬性规则：**
- **每次生成前必须执行 Step 0 美学定调**，不得跳过。**例外：定期报告预设模式（日报/周报/月报）跳过 Step 0，使用固定样式**
- **禁止默认 `#2563EB` 蓝**作为兜底主色，除非用户主动要求"专业商务"且选择了「学术严肃」或「暖色商务」方向
- **禁止以 system-ui / sans-serif 作为主字体**，必须从 Google Fonts 引入有辨识度的字体配对（fallback 链中可保留 system-ui 作为兜底）
- **禁止纯白背景 + 无装饰**，必须至少加一种背景质感（noise grain / 几何图案 / 微渐变 / 装饰线条 / 大字水印 之一）
- 生成后必须执行末尾的 **Anti-AI-Slop Checklist** 自检（定期报告预设模式跳过）

## 何时触发

**主动触发场景：**
- 用户提到"生成报告"、"做 HTML 页面"、"转网页"、"Markdown 转 HTML"
- 用户提到"工作汇报"、"数据报告"、"分析文档"、"总结报告"
- 用户提供 Markdown 内容并要求美化或转为可视化格式
- 用户描述了一个报告需求（如"帮我做一个 Q1 销售报告"）
- 用户提到需要展示数据、图表、指标卡片等可视化内容

**输入识别（自动判断，无需主动询问用户属于哪种）：**
- 用户已贴出 Markdown / 文本 / 大纲 → 直接进入 Step 1 分支 A 解析
- 用户仅描述需求或主题 → 进入 Step 1 分支 B 收集信息后生成内容
- 混合情况（部分内容 + 部分需求）→ 已有部分按 A 解析，缺失部分按 B 补齐

**不应触发（交给其他 skill）：**
- 纯数据分析任务（不涉及 HTML 产出）
- 生成图表图片而非 HTML 页面
- 纯 Markdown / 文档写作（不涉及视觉设计）
- React / Vue 组件开发（这是项目代码，不是单文件 HTML）

## 场景路由

根据用户意图，在 Step 2 之前读取对应的美学指南：

| 用户信号 | 场景类别 | 读取文件 |
|---------|---------|---------|
| "做 deck"、"PPT"、"演示稿"、"技术分享"、"pitch"、"keynote" | Deck/演示稿 | `references/scenario-decks.md` |
| "小红书卡片"、"推特卡"、"社交卡片"、"轮播图" | 社交卡片 | `references/scenario-social-cards.md` |
| "海报"、"朋友圈图"、"营销图"、"杂志风" | 海报 | `references/scenario-posters.md` |
| "着陆页"、"定价页"、"仪表盘"、"看板"、"App 原型"、"线框图" | Web 原型 | `references/scenario-web-prototypes.md` |
| "报告"、"汇报"、"数据可视化"、"文档" | 报告（原有） | 走原有流程 |

**路由规则**：
- 如果匹配到非报告场景 → 读取对应 `scenario-*.md` 获取布局约束和字体推荐 → 结合 Step 0 美学定调生成
- 如果匹配到报告场景 → 走原有逻辑不变
- 图表密集场景额外读取 `references/chart-pitfalls.md`
- 小红书图文 deck 同时参考 `scenario-decks.md` 和 `scenario-social-cards.md`

## 使用模式

### 模式一：单次生成（默认）

AI 直接生成完整 HTML 文件交付，单文件自包含。适用：一次性报告、临时产出、无后续维护。工作流走 Step 0 美学定调 + Step 1-4。

### 模式二：复制改造（工程化）

适用：报告需多次更新、数据频繁变化、大数据量场景（百行表格 / 多图表）。工作流：
1. `cp assets/templates/<某个模板>.html <项目>/your-template.html`
2. `cp assets/scripts/build.js <项目>/build.js`
3. 先做 Step 0 美学定调 → 改造模板样式/布局/数据
4. 改 build.js 顶部 3 个路径常量
5. 准备 data.json → `node build.js` → 输出最终 HTML

### 模式三：定期报告预设

适用：日报 / 周报 / 月报等周期性报告。需要**跨期视觉一致**，**跳过 Step 0 美学定调**，使用固定蓝色调样式。详见 `references/periodic-report-preset.md`。

**触发信号**：用户说"日报"、"周报"、"月报"、"每日简报"、"weekly report"、"monthly report"，或由 orchestrator 触发。

### 如何选择

| 信号 | 模式 |
|------|------|
| "做一份" + 没说后续维护 | 单次生成 |
| "持续维护 / 每周每月更新" | 复制改造 |
| 数据百行以上 / 多图表 | 复制改造 |
| 日报/周报/月报 | 定期报告预设 |
| 只要看一次结果 | 单次生成 |

## Step 0：美学定调（强制前置步骤）

**定期报告预设模式跳过此步骤。**

生成 HTML 之前必须先做美学定调。为本次报告决定：
1. **Aesthetic Direction**：从 6 套预设中选 1 套（或基于用户偏好定制）
2. **字体配对**：display + body 字体
3. **配色方案**：主色 + 辅助色 + 强调色 + 中性梯度

**快速决策参考**（用户未指定方向时，按主题匹配）：

| 主题关键词 | 推荐方向 | 理由 |
|-----------|---------|------|
| 金融/法律/学术/政策 | D. 学术严肃 | 权威感、正式感 |
| 消费品/生活方式/餐饮 | F. 暖色商务 | 温度、亲和力 |
| 科技/SaaS/创业 | E. 科技冷冽 | 科技感、前沿感 |
| 环保/农业/健康/公益 | C. 自然有机 | 自然感、生命力 |
| 时尚/艺术/文化 | A. 编辑杂志风 | 视觉张力、个性 |
| 工业/建筑/极简 | B. 极简瑞士风 | 克制、精确 |
| 无明确倾向 | 主动推荐 A | 视觉冲击力最强 |

详细预设表、字体代码、配色变量、背景质感选项 → 见 `references/aesthetic-directions.md`。用户没说偏好时按上表推荐，不要默认走"商务蓝"。

## 工作流程

### Step 1：理解输入

- **分支 A**（用户已提供内容）：分析语义结构，识别数据密集区域和可图表化数据。内容完整则直接进入 Step 2
- **分支 B**（用户仅描述需求）：收集主题/受众/数据/风格偏好，生成内容结构

### Step 2：模板选型 + 组件映射

**分支 A：报告/文档场景**（走原有流程）

推荐模板（参考 `assets/templates/`）：
- **base-report.html**：通用分析报告、技术文档
- **dashboard.html**：数据密集型、KPI 看板
- **presentation.html**：视觉优先、汇报演示

组件映射：标题→hero-banner / 数字→kpi-card / 表格→data-table / 时间→timeline / 对比→pros-cons / 图表→chart-container

组件变体表 → 见 `references/template-vue-guide.md`

**分支 B：非报告场景**（Deck / 社交卡片 / 海报 / Web 原型）

1. 根据场景路由表读取对应的 `references/scenario-*.md`
2. 按场景指南中的布局约束和字体推荐构建页面结构
3. 不使用 `assets/templates/` 的报告模板，按场景指南从零搭建
4. 图表密集场景额外读取 `references/chart-pitfalls.md`
5. 美学定调（Step 0）仍然执行（背景质感、配色变量），但**字体配对完全采用场景指南推荐**（场景指南的字体是为该产出形态专门选择的，优先级高于 6 套通用预设）

### Step 3：数据提取与图表生成（按需）

识别可图表化数据 → Chart.js 配置 → 嵌入 `<canvas>` 初始化。大数据量走数据分离架构（见下方）。

### Step 4：组装 + 注入美学层 + 自检 + 输出

- 注入 Step 0 决定的美学层（Google Fonts、CSS 变量、背景质感、顶部注释）
- 注入组件和内容
- 对照 **Anti-AI-Slop Checklist** 逐项自检（定期报告预设模式跳过）
- 输出完整 HTML，简要说明选了哪个方向、字体、主色

## 输出质量要求

### 必须满足
1. **自包含**：单个 HTML 文件，双击即可打开
2. **中文排版**：正确的行高、字间距
3. **语义化**：`<header>`, `<main>`, `<section>` 等
4. **CDN 可用**：cdn.tailwindcss.com, cdn.jsdelivr.net

### 用户要求时才加
1. 响应式、暗色模式、打印友好

### 禁止
1. 不用构建工具（PostCSS/Webpack）
2. 不引入需本地服务器的功能
3. 不用过时 CSS（float 布局）
4. 图表数据不硬编码散落

### 关键避坑
1. **JSON 注入防 `</script>` 污染**：`.replace(/<\//g, '<\\/')`
2. **暗色方向 Tailwind 类名失效**：必须用 `var(--color-xxx)`
3. **自包含**：不引用外部 CSS 文件

## 详细参考文件

| 参考文件 | 内容 |
|---------|------|
| `references/INDEX.md` | **Reference 注册表** — 所有 reference 文件的索引，含何时读取、核心内容、关键约束、路由决策树。新增 reference 时必须在此注册 |
| `references/aesthetic-directions.md` | 6 套美学方向预设详情、字体/配色代码、背景质感、设计风格建议、Anti-AI-Slop Checklist |
| `references/periodic-report-preset.md` | 定期报告（日报/周报/月报）固定样式、Tailwind 配置、交互模式（复制按钮、时间线导航） |
| `references/template-vue-guide.md` | 模板基础结构、Vue 3 CDN 运行时、组件设计变体表、图表生成规范 |
| `references/data-architecture.md` | 数据分离架构（大数据量报告的模板+构建脚本方案） |
| `references/vue3-patterns.md` | Vue 3 交互模式（折叠面板、transition 动画等） |
| `references/element-plus.md` | Element Plus 组件库集成 |
| `references/scenario-decks.md` | Deck/演示稿场景的布局约束、7 个子场景设计思路（通用/技术分享/pitch/产品发布/演讲者模式/小红书图文/架构蓝图）、字体推荐、交互代码片段 |
| `references/scenario-social-cards.md` | 社交卡片（小红书/Twitter 金句/三联轮播）的尺寸规范、配色原则、排版约束、字体推荐 |
| `references/scenario-posters.md` | 海报（营销海报/杂志风海报）的比例规范、SVG 装饰技巧、背景质感速查、字体推荐 |
| `references/scenario-web-prototypes.md` | Web 原型（SaaS 着陆页/定价页/仪表盘/看板/手绘线框/移动 App）的布局范式、交互片段、字体推荐 |
| `references/chart-pitfalls.md` | Chart.js 容器高度（ResizeObserver 死循环）、JSON 注入防护、图表配色原则、中文标签配置 |

## 定期报告模式（日报/周报/月报）

使用此模式时，先读取 `references/periodic-report-preset.md`，严格按照其中的 Tailwind 配置、字体、布局、交互模式生成。不走 Step 0 美学定调，不做 Anti-AI-Slop 自检。

## 大数据量报告

数据量大时采用"模板 + 构建脚本"数据分离架构。详见 `references/data-architecture.md`。

## 迭代与修改

1. 定位需修改部分
2. 输出修改后的**完整 HTML**（不只输出片段）
3. 说明修改了哪些内容

## Anti-AI-Slop Checklist

详见 `references/aesthetic-directions.md`。定期报告预设模式跳过此自检。
