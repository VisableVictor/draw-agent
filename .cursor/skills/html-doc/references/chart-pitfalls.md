# 图表生成避坑指南

> 本文件是 SKILL.md 的参考。当生成的 HTML 中包含 Chart.js 图表、数据可视化元素时，读取此文件避免常见错误。

## Chart.js 容器高度（高危，必须遵守）

这是最常见的致命问题。Chart.js 在 `responsive: true, maintainAspectRatio: false` 模式下，依赖父容器的显式高度来决定 canvas 尺寸。

**规则**：每个 `<canvas>` 外层必须包一个有显式高度的 div：

```html
<div style="position: relative; height: 280px;">
  <canvas id="myChart"></canvas>
</div>
```

**高度参考值**：
- KPI 迷你趋势线：~40px
- 主图表（折线/柱状/饼图）：~240-280px
- 全屏可视化：~400-500px

**Chart.js 配置**：
```javascript
new Chart(ctx, {
  options: {
    responsive: true,
    maintainAspectRatio: false,  // 必须配合父容器固定高度
  }
});
```

**后果**：若父容器无显式高度 → ResizeObserver 死循环 → 图表高度无限增长 → 浏览器卡死

**常见错误写法**：
- 直接给 canvas 写 `height="280"` 属性 ❌ — 这只是初始渲染值，responsive 模式下会被忽略
- 用 Tailwind 的 `h-[280px]` 在 canvas 上 ❌ — Chart.js 不认 Tailwind class
- 父容器只有 `min-height` 没有 `height` ❌ — 不够，必须是确定的 height

## JSON 注入防护

当图表数据从后端或变量注入到 `<script>` 标签中时，数据中可能包含 `</script>` 字符串，导致 HTML 解析提前闭合。

**规则**：所有内联 JSON 数据必须做转义：

```javascript
const data = JSON.parse('json_data'.replace(/<\//g, '<\\/'));
```

或者用 `<script type="application/json">` + `JSON.parse` 的安全模式：

```html
<script id="chart-data" type="application/json">
  {"labels": ["Q1", "Q2"], "values": [120, 340]}
</script>
<script>
  const data = JSON.parse(document.getElementById('chart-data').textContent);
</script>
```

## 图表配色原则

- **从主色衍生调色板**：用主色 + 透明度变化产生序列，不要每条线一种新颜色
  ```javascript
  const colors = [
    'rgba(184, 71, 42, 1)',    // 主色 100%
    'rgba(184, 71, 42, 0.7)',  // 主色 70%
    'rgba(184, 71, 42, 0.4)',  // 主色 40%
    'rgba(201, 169, 97, 0.8)', // 强调色 80%
  ];
  ```
- **饼图/环形图**：用不同色相，但保持相近饱和度
- **柱状图**：单色 + hover 高亮即可，不需要每根柱子不同色
- **折线图**：2-3 条线用不同色相，超过 4 条建议拆分为小多图 (small multiples)

## Chart.js CDN 引入

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
```

如需插件（数据标签、注释等）：
```html
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
```

## 中文标签

Chart.js 默认字体不支持中文，数字旁的中文标签会显示为方块。

**解决**：在 Chart.js 全局配置中指定支持中文的字体：

```javascript
Chart.defaults.font.family = "'Noto Sans SC', 'Inter', sans-serif";
```

## 避坑速查表

| 问题 | 原因 | 解决 |
|------|------|------|
| 图表无限增高 | 父容器无固定高度 | 外包 `<div style="height:Npx">` |
| 中文显示方块 | 未配置中文字体 | `Chart.defaults.font.family` 加中文字体 |
| 数据注入报错 | JSON 含 `</script>` | 转义或用 `type="application/json"` |
| 饼图颜色太接近 | 随机配色 | 预设调色板，保持饱和度一致 |
| 响应式失效 | 同时设了 responsive + maintainAspectRatio | 设 `maintainAspectRatio: false` + 固定高度容器 |
| 图表空白 | canvas 在 hidden 容器中 | 切换显示后调用 `chart.resize()` |
