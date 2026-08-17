# Deck / 演示稿场景美学指南

> 本文件是 SKILL.md 场景路由的参考。当用户需要生成演示稿、PPT、deck 时读取此文件，获取布局约束、子场景设计思路和字体推荐。

## 通用约束

- **比例**：16:9，容器 `w-[1280px] h-[720px]`（或 1920×1080）
- **交互**：horizontal-swipe 翻页，键盘 `←` / `→` 切换，URL hash 同步当前页码
- **进度指示**：顶部 progress bar（细线，主色填充，宽度随页码比例变化）
- **信息密度**：每页一个核心信息，不堆砌；文字总量控制在每页 80 字以内（deck 不是文档）
- **页码**：底部右下角小字 `当前/总数`
- **切换动效**：页间 `transform: translateX()` + `transition` 平滑过渡，不要生硬跳切

## 子场景设计思路

### 通用 Deck

**触发信号**：用户说"做个 deck"、"做个 PPT"、"做个演示"，无特定风格要求。

**布局**：Cover → N 个 content 页 → 收尾（Thank you / Q&A）。N 由内容量决定，短内容 6-10 页起步，长内容应更多。

**设计语言**：干净极简，不追 magazine 调。纯色或微渐变背景，重点用色块/图标突出。

---

### 技术分享

**触发信号**：用户说"技术分享"、"tech talk"、"内部演讲"、"会议 talk"。

**布局**：Cover（议题 + 讲者 + handle）→ Agenda → 正文页若干（代码块 + 关键观点）→ Demo 页（终端截图/SVG 模拟）→ Q&A

**设计语言**：
- **GitHub-dark 配色**：背景 `#0D1117`，文字 `#C9D1D9`，关键词高亮 `#FF7B72` / `#79C0FF`
- **代码块**：使用 [highlight.js](https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@latest/build/highlight.min.js) CDN，暗色主题（github-dark）
- **等宽数字**：关键数据用 JetBrains Mono 大字号呈现
- **终端模拟**：深色背景 + `$` 前缀 + 绿色输出，模拟真实 terminal

---

### 融资 Pitch

**触发信号**：用户说"pitch"、"融资 deck"、"投资人 deck"、"BP"。

**布局（标准 10 页）**：
1. Cover（Logo + Tagline + Round / $Ask）
2. Problem
3. Solution
4. Why Now
5. Product（截图/SVG 占位）
6. Market Size（TAM / SAM / SOM 三层同心圆或柱状）
7. Traction（柱状图 + 大数字增长指标）
8. Business Model
9. Go-to-Market
10. Team + Ask（$X.XM 大数字）

**设计语言**：浅色底（非纯白，如 `#FAFAF8` 或 `#F8F6F3`）+ 深色 hero 区块（深蓝 `#1E293B` 或藏青），数据用大字号冲击力呈现，traction 用 Chart.js 柱状图。整体克制专业，不过度花哨。注意：不使用「白底 + 紫色渐变」这种 AI 套皮组合。

---

### 产品发布 Keynote

**触发信号**：用户说"产品发布"、"launch deck"、"keynote"。

**布局**：Cover（暗背景 + 大字主题）→ Why we built this（痛点）→ Introducing（产品名 + hero shot）→ Feature Cards（3-6 个）→ Pricing Tiers → CTA / Available Now

**设计语言**：
- 暗 hero + 亮内容页的节奏对比
- 暖色 accent 渐变（橙→桃）
- Feature 用 icon + 一句话卡片，不写长段落

---

### 演讲者模式

**触发信号**：用户说"演讲者模式"、"带备注的 deck"、"提词器"、"presenter mode"。

**布局**：
- 每页正文 + `<aside class="notes">` 存放 150-300 字逐字稿
- 右下角小 toolbar：`T` 切换主题 / `S` 打开 popup teleprompter
- Popup 四张磁吸卡：CURRENT（当前页缩略）/ NEXT（下一页缩略）/ SCRIPT（当前页逐字稿）/ TIMER（计时器）

**设计语言**：
- 默认 tokyo-night 主题（深蓝背景 + 柔和色文字）
- 可内置 3-5 套主题切换（含一套 light）
- 主题通过 CSS 变量切换，不改 HTML 结构

---

### 小红书图文 Deck

**触发信号**：用户说"小红书图文"、"小红书帖子"、"IG carousel"。

**注意**：此场景比例不是 16:9，而是 **3:4（1080×1440）**，更接近社交卡片。建议同时参考 `scenario-social-cards.md` 中的小红书卡片约束，两者使用统一尺寸。

**布局**：Cover + N 个 content 页 + 收尾 CTA。N 由内容量决定，短内容 7 页起步，平台限制单帖 ≤ 18 图。

**设计语言**：
- 暖色 pastel 背景（奶白 / 浅杏 / 淡粉）
- 虚线 sticker 卡片风格
- 底部页码 dots
- 大字号、圆角元素、大量留白

---

### 架构蓝图

**触发信号**：用户说"架构 deck"、"蓝图"、"系统架构演示"、"blueprint"。

**布局**：以图为主，文字为辅。每页一个核心架构图 + 右侧 insight callout。

**设计语言**：
- **奶油纸底** `#F0EAE0` + **蓝图网格** 48px 间距 mask
- **锈红 accent** `#B5392A` 用于 callout / 高亮节点
- Playfair serif 大字标题，工程印刷感
- SVG 虚线连线 + 箭头表示数据流 / 依赖关系
- Pipeline 步骤盒（其中一个可抬高表示当前阶段）
- **零渐变零软阴影**，保持图纸感

---

## 字体推荐

| 子场景 | Display Font | Body Font | Google Fonts 引入 |
|-------|-------------|-----------|-------------------|
| 通用 Deck | Plus Jakarta Sans (600/700) | Inter (400/500) | `family=Plus+Jakarta+Sans:wght@600;700&family=Inter:wght@400;500` |
| 技术分享 | JetBrains Mono (500/700) | Inter (400/500) | `family=JetBrains+Mono:wght@500;700&family=Inter:wght@400;500` |
| 融资 Pitch | DM Serif Display (400) | Plus Jakarta Sans (400/500/600) | `family=DM+Serif+Display&family=Plus+Jakarta+Sans:wght@400;500;600` |
| 产品发布 | Space Grotesk (600/700) | Inter Tight (400/500) | `family=Space+Grotesk:wght@600;700&family=Inter+Tight:wght@400;500` |
| 演讲者模式 | JetBrains Mono (500) | Inter (400/500) | 同技术分享 |
| 小红书图文 | ZCOOL KuaiLe (400) | Noto Sans SC (400/500/700) | `family=ZCOOL+KuaiLe&family=Noto+Sans+SC:wght@400;500;700` |
| 架构蓝图 | Playfair Display (700/900) | IBM Plex Sans (400/500) | `family=Playfair+Display:wght@700;900&family=IBM+Plex+Sans:wght@400;500` |

## 交互代码片段

### 键盘翻页 + hash 同步

```javascript
const slides = document.querySelectorAll('.slide');
let current = 0;
function goTo(i) {
  slides[current].classList.remove('active');
  current = Math.max(0, Math.min(i, slides.length - 1));
  slides[current].classList.add('active');
  location.hash = current + 1;
  updateProgress();
}
document.addEventListener('keydown', e => {
  if (e.key === 'ArrowRight') goTo(current + 1);
  if (e.key === 'ArrowLeft') goTo(current - 1);
});
// 初始页从 hash 读取
if (location.hash) goTo(parseInt(location.hash.slice(1)) - 1);
```

### Progress bar

```html
<div id="progress" class="fixed top-0 left-0 h-1 bg-[var(--color-primary)] transition-all duration-300 z-50"></div>
```
```javascript
function updateProgress() {
  const pct = ((current + 1) / slides.length) * 100;
  document.getElementById('progress').style.width = pct + '%';
}
```

## 避坑

- 每页文字不超过 80 字（deck 不是文档，讲者应该讲故事而不是念幻灯片）
- 代码块必须有语法高亮，不要纯文本粘贴
- 图表容器必须有固定高度（详见 `chart-pitfalls.md`）
- 不要用 `overflow: scroll` 让单页内容滚动——deck 的每一页应该是固定视口
- Pitch deck 的 Market Size 不要用饼图，用 TAM/SAM/SOM 同心圆或嵌套矩形更专业
