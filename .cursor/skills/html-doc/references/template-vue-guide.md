# 模板与 Vue 3 参考

> 模板基础结构、Vue 3 CDN 运行时、组件设计变体、图表生成规范。用于"复制改造"模式或需要复杂交互的报告。

## 模板基础结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<!--
  Aesthetic Direction: X. 方向名称
  Display Font: xxx  |  Body Font: xxx
  Primary: #xxx  |  Accent: #xxx  |  Bg: #xxx
  Texture: xxx
-->
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>报告标题</title>
    <!-- Google Fonts（按所选方向替换） -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
    <!-- Tailwind + Chart.js + Vue 3 -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
    <script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
    <style>
        :root {
            --font-display: 'DisplayFont', serif;
            --font-body: 'BodyFont', system-ui, sans-serif;
            --color-bg: #FAF7F2;
            --color-surface: #FFFFFF;
            --color-ink: #1A1815;
            --color-muted: #6B6760;
            --color-primary: #B8472A;
            --color-accent: #C9A961;
            --color-line: #E8E2D8;
        }
        html { scroll-behavior: smooth; }
        body {
            font-family: var(--font-body);
            line-height: 1.8;
            background: var(--color-bg);
            color: var(--color-ink);
        }
        h1, h2, h3 { font-family: var(--font-display); }
    </style>
</head>
<body class="min-h-screen">
    <!-- 内容区域 -->
</body>
</html>
```

**关键约定：**
- `lang="zh-CN"` 确保中文排版正确
- Tailwind CDN 支持任意 class
- Chart.js 按需引入（无图表时可省略）
- 所有样式内联，不依赖外部 CSS 文件

## Vue 3 运行时

`assets/templates/` 中的预置模板**全部基于 Vue 3 CDN 渲染**，不是可选项。

### CDN 引入

```html
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
```

### 最小骨架

```html
<style>[v-cloak]{display:none}</style>

<!-- 数据注入点：构建脚本会整段替换这个 <script data-template> 标签 -->
<script data-template>
    const D = {
        meta: { hero: { title: '示例报告标题', subtitle: '副标题' } },
        kpis: [
            { label: '示例指标 A', value: '128' },
            { label: '示例指标 B', value: '￥3.2M' }
        ],
        chart: { labels: ['1月','2月','3月','4月','5月','6月'], seriesLabel: '示例序列', data: [10, 24, 38, 52, 47, 61] }
    };
</script>

<div id="app" v-cloak>
    <h1>{{ D.meta.hero.title }}</h1>
    <div v-for="kpi in D.kpis" :key="kpi.label">
        <span>{{ kpi.value }}</span>
    </div>
</div>

<script>
const { createApp, ref, computed, onMounted } = Vue;
createApp({
    setup() {
        const chartCanvas = ref(null);
        const hasChart = computed(() => D.chart && D.chart.data && D.chart.data.length > 0);
        onMounted(() => {
            if (hasChart.value && chartCanvas.value) {
                new Chart(chartCanvas.value, { /* ... */ });
            }
        });
        return { D, chartCanvas, hasChart };
    }
}).mount('#app');
</script>
```

### 为什么用 `<script data-template>` 整段替换

- **模板态可调试**：独立打开模板就能看到真实渲染效果，无需先跑构建脚本
- **示例数据即契约**：字段名、类型、缺省值、多形态单元都在数据里直观可见
- **省掉 IIFE 兜底**：不需要 `(function(){ const raw = ... })()` 这种间接
- **不会误伤同名字符串**：标签整段替换比 `replace("__INJECT_DATA__", ...)` 更安全

### 三条硬规则

1. **必须 `v-cloak`**：避免渲染前的 `{{ }}` 字面量闪入
2. **数据全走 D**：所有图表 / 表格 / 数字从 `D.xxx` 读取，不写死
3. **动态颜色不要在 JS 里拼接 class 名**（如 `:class="text-${color}-500"`，Tailwind JIT 不扫 JS 字符串）。两种解法：① `:style="{ color: D.meta.primaryColor }"` inline style；② 用 Tailwind CDN 的 `tailwind.config.theme.extend.colors.primary = D.meta.primaryColor` 注入后再用 `bg-primary` / `text-primary` 类

### 进阶模式

- 折叠面板、移动端菜单、复选框组、`<transition>` 动画等模式：见 `references/vue3-patterns.md`
- Element Plus 组件库集成：见 `references/element-plus.md`

## 组件设计参考

`assets/components/` 目录中的组件文件是**风格参考**，展示每类组件的典型结构。实际生成时需按所选 Aesthetic Direction 应用对应变体，不是直接复制。

组件类型：
- **kpi-card**：展示关键数字，多个卡片用 grid 排列
- **data-table**：结构化数据，带表头高亮、斑马纹、悬停效果
- **chart-container**：趋势/占比/对比分析，使用 `<canvas>` + Chart.js
- **timeline**：项目进展、里程碑、发展历程
- **pros-cons**：方案对比、优劣分析、决策依据
- **navbar**：顶部导航，带 logo 和锚点链接
- **hero-banner**：标题 + 副标题 + 日期/作者
- **footer**：版权信息 + 生成时间

### 组件的 Aesthetic 变体

同一组件在不同 Aesthetic Direction 下应**显著不同**，避免所有报告长一个样：

| 组件 | A. 编辑杂志风 | B. 极简瑞士风 | C. 数据驾驶舱 | D. 学术严肃 | E. 科技冷冽 | F. 暖色商务 |
|------|------|------|------|------|------|------|
| **kpi-card** | 大数字衬线 + 无边框 + 仅左侧色条 | 巨大数字占满 + 仅细线分割 | 暗底 + 等宽霓虹数字 + glow | 衬线小卡 + 数字带刻度线 | 玻璃态 + glow 边缘 | 圆角卡 + 暖色阴影 |
| **data-table** | 无边框 + 大行距 + 衬线表头 | 极细线 + 全大写表头 | 暗底 + 等宽数字 + 细分割 | 单线表头 + 引文式行距 | 半透明背景 + 细线 | 圆角 + 暖灰斑马纹 |
| **chart-container** | 单色衬线标签 + 极简网格 | 单色 + 隐藏网格 + 大留白 | 霓虹色 + 暗底 + 细网格 | 灰阶 + 衬线轴标签 | 渐变线 + glow | 暖色调 + 柔和填充 |
| **hero-banner** | 巨型衬线 + 不对称副标 | 全大写小字 + 巨数字 | 数据流装饰 + 暗底 | 居中衬线 + 副标分隔线 | grid 背景 + glow 标题 | 衬线 + 暖色块装饰 |
| **timeline** | 衬线年份 + 长引线 | 极细竖线 + 大间距 | 等宽时间戳 + 节点 glow | 衬线 + 学术编号 | grid 节点 + 冷蓝连线 | 圆角节点 + 暖色填充 |
| **navbar** | 衬线 logo + 大间距链接 | 全大写 + 极细字重 | 暗底 + 单色高亮 | 衬线 + 居中布局 | 玻璃态 + glow hover | 暖色 + 圆角 hover |
| **pros-cons** | 双栏衬线 + 大引号装饰 | 极细中线 + 全大写标签 | 暗底双卡 + 绿/红 glow | 编号列表 + 衬线对比 | 玻璃双卡 + 冷暖 glow | 圆角双卡 + 暖色填充 |
| **footer** | 衬线小字 + 装饰线分隔 | 极细全大写 + 居左 | 等宽时间戳 + 单线 | 衬线居中 + 脚注线 | 单色细字 + glow 线 | 暖灰背景 + 圆角 |

**关键规则**：选定方向后，**所有组件统一应用该方向的变体**，不要混搭。

## 图表生成规范

使用 Chart.js 时遵循以下模式：

1. **集中管理数据**：在 `<script>` 中用变量定义所有图表数据
2. **按需初始化**：只在页面中存在 `<canvas>` 时初始化对应图表
3. **中文标签**：图例、标题、tooltip 使用中文
4. **配色协调**：使用协调的配色方案
5. **响应式（可选）**：用户要求适配移动端时，图表容器设置 `max-width` 确保正常显示

**常用图表类型选择：**
- 趋势变化 → 折线图 (line)
- 占比分布 → 饼图/环形图 (pie/doughnut)
- 对比分析 → 柱状图 (bar)
- 多维评估 → 雷达图 (radar)
- 进度展示 → 仪表盘 (doughnut, 配合旋转角度)
