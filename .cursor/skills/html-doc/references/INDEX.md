# References 索引

> AI 快速查阅用。读取此文件即可定位应该打开哪个 reference，无需逐一打开确认。
> 新增 reference 文件时，必须在此注册。

## 美学体系

| 文件 | 何时读取 | 核心内容 | 关键约束 |
|------|---------|---------|---------|
| `aesthetic-directions.md` | **每次生成必读**（定期报告预设除外） | 6 套美学方向预设（编辑杂志/学术严肃/暖色商务/赛博霓虹/自然有机/极简瑞士）、字体引入代码、CSS 变量模板、背景质感 5 选项、Anti-AI-Slop Checklist | 禁止 `#2563EB` 默认蓝；禁止 Tailwind 默认字体栈；禁止纯白无装饰 |
| `periodic-report-preset.md` | 仅日报/周报/月报场景 | 固定蓝色调样式、Tailwind 配置、复制按钮交互、时间线导航、跨期视觉一致 | 跳过 Step 0 美学定调；跳过 Anti-AI-Slop 自检 |

## 报告/文档专用

| 文件 | 何时读取 | 核心内容 | 关键约束 |
|------|---------|---------|---------|
| `template-vue-guide.md` | 报告场景 Step 2 模板选型时 | 3 个模板的 HTML 结构、Vue 3 CDN 运行时、组件设计变体表（hero-banner/kpi-card/data-table/timeline 等）、图表生成规范 | 组件必须与模板的 CSS 变量体系对齐 |
| `data-architecture.md` | 大数据量报告（百行表格/多图表） | 模板 + 构建脚本的数据分离架构、build.js 路径常量、data.json 格式 | 仅复制改造模式使用 |
| `vue3-patterns.md` | 需要 Vue 3 交互时 | 折叠面板、transition 动画、响应式状态管理 | 通过 CDN 引入 Vue 3 运行时 |
| `element-plus.md` | 用户明确要求 Element Plus 组件时 | Element Plus CDN 全量集成（~300KB）、常用组件替换表、样式覆盖方案 | CDN 为全量加载，仅在组件需求较多时引入 |

## 场景美学指南

| 文件 | 何时读取 | 子场景覆盖 | 关键约束 |
|------|---------|-----------|---------|
| `scenario-decks.md` | 用户要 deck/PPT/演示/技术分享/pitch | 通用 deck、技术分享（GitHub-dark）、融资 pitch（10 页）、产品发布 keynote、演讲者模式（带备注+提词器）、小红书图文 deck（3:4）、架构蓝图（图纸风） | 16:9 swipe + 键盘导航 + progress bar；每页 ≤80 字 |
| `scenario-social-cards.md` | 用户要小红书卡片/推特卡/社交轮播 | 小红书图文卡片（1080×1440）、Twitter/X 金句卡（1600×900）、三联社交轮播（1080×1080×3） | 固定像素尺寸；字号大（手机看）；每张一观点 |
| `scenario-posters.md` | 用户要海报/朋友圈图/杂志风长图 | 营销海报（9:16 竖版渐变）、杂志风海报（editorial 长图） | SVG 装饰代替 img；营销海报禁白底；杂志风必用 serif |
| `scenario-web-prototypes.md` | 用户要着陆页/定价页/仪表盘/看板/线框/App | SaaS 着陆页、定价页（三档对比）、管理后台仪表盘、看板（4 列）、手绘线框（Caveat 字体）、移动 App 单屏（iPhone frame） | 响应式必须处理 md: 断点；仪表盘图表容器需固定高度 |

## 通用避坑

| 文件 | 何时读取 | 核心内容 | 关键约束 |
|------|---------|---------|---------|
| `chart-pitfalls.md` | **任何包含 Chart.js 图表的场景** | 容器高度规则（ResizeObserver 死循环）、JSON 注入防护、图表配色原则、中文标签配置、避坑速查表 | canvas 外层必须有 `<div style="height:Npx">`；不要用 `height=` 属性当布局 |

## 路由决策树

```
用户请求
├── 日报/周报/月报？ → periodic-report-preset.md（跳过 Step 0）
├── 报告/文档？
│   ├── 大数据量？ → data-architecture.md
│   ├── 需要 Vue 交互？ → vue3-patterns.md
│   ├── 需要 Element Plus？ → element-plus.md
│   └── Step 2 选型 → template-vue-guide.md
├── Deck/PPT/演示？ → scenario-decks.md
├── 社交卡片/小红书/Twitter？ → scenario-social-cards.md
├── 海报/朋友圈图？ → scenario-posters.md
├── 着陆页/仪表盘/看板/线框/App？ → scenario-web-prototypes.md
└── 包含图表？ → 额外读取 chart-pitfalls.md
```
