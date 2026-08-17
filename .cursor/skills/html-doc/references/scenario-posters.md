# 海报美学指南

> 本文件是 SKILL.md 场景路由的参考。当用户需要生成营销海报、杂志风海报等竖版视觉产出时读取此文件。

## 通用约束

- **竖版为主**：海报通常是竖版长图或 9:16 比例，适合手机浏览和朋友圈分享
- **视觉冲击力优先**：海报不是文档，第一眼要抓人，字号要大、对比要强
- **SVG 装饰**：用 SVG 做装饰性元素（圆 / 三角 / 波浪 / 噪点纹理），不要用 img 标签加载外部图片
- **截图友好**：整张海报在一个可视区域内，不需要滚动（除非是杂志风长图）

## 子场景设计思路

### 营销海报（9:16 竖版）

**触发信号**：用户说"海报"、"朋友圈图"、"营销图"、"分享图"、"活动海报"。

**尺寸**：`w-[1080px] h-[1920px] mx-auto`（9:16 竖版，朋友圈 / 小红书通用）。

**布局（从上到下）**：
1. **上部 30%**：留白 + 一个大 emoji 或抽象 SVG 几何图形（圆 / 三角 / 波浪线）
2. **中部主标题**：占视觉中心，`text-7xl~8xl font-black`，一句话副标题 `text-2xl`
3. **下部信息区**：3-5 条核心要点，每条用 icon + 短句（不超过 15 字）
4. **底部**：品牌 logo + 二维码占位（用 SVG 方框 + "扫码" 文字代替真实二维码）

**设计语言**：
- **全屏渐变 / mesh 背景**：大胆色彩，不要保守
  - 推荐渐变方向：`from-violet-600 via-fuchsia-500 to-indigo-600`
  - 或暖色方向：`from-orange-500 via-rose-500 to-pink-600`
  - mesh 效果：用多个 `radial-gradient` 叠加，模拟 mesh gradient
- **文字颜色**：主标题白色，副标题 `rgba(255,255,255,0.85)`，高亮用对比色
- **SVG 装饰**：
  - 噪点纹理：`<filter><feTurbulence>` 叠加在渐变背景上
  - 几何图形：半透明圆 / 三角散落在大标题周围
  - 波浪分割线：用 SVG path 做 section 分割

**配色 CSS 变量**：

```css
:root {
  --poster-bg-1: #7C3AED;      /* 渐变起点 */
  --poster-bg-2: #DB2777;      /* 渐变中点 */
  --poster-bg-3: #4F46E5;      /* 渐变终点 */
  --poster-ink: #FFFFFF;        /* 主文字 */
  --poster-muted: rgba(255,255,255,0.8);
  --poster-accent: #FDE68A;     /* 高亮色（黄色系对比） */
}
```

---

### 杂志风海报（竖版长图）

**触发信号**：用户说"杂志风"、"editorial 海报"、"报纸风"、"manifesto"、"长图海报"。

**尺寸**：`w-[800px] mx-auto`，高度自适应（长图可滚动，但建议控制在 3 屏以内）。

**布局（从上到下）**：
1. **Dateline 顶栏**：publication 名 / 日期 / issue 编号，小字等宽体，像报纸头版
2. **Oversized headline**：超大 serif 标题（text-6xl~8xl），可含 ~~strike-through~~ 词 + *斜体* accent 词
3. **Lead paragraph**：首段字号略大（text-lg），首字母 drop cap（下沉 3 行）
4. **双栏正文**：`columns-2 gap-8`，正文 text-base
5. **编号 sections**（6 个左右）：每个含小标题 + 1-2 段 + pull-quote（大字号引用，`border-l-4` 左边框）
6. **底部**：署名 + 小 ornament（❧ / ◆ / ✦ 等装饰符号）

**设计语言**：
- **纸感**：暖灰 cream 背景 `#F5F0E8` + 细 dot pattern（`background-image: radial-gradient(#000 0.5px, transparent 0.5px); background-size: 12px 12px; opacity: 0.03`）
- **纯黑文字** `#1A1A1A`，不用灰色
- **装饰线**：section 之间用细实线或双线分割
- **零渐变零阴影**：保持印刷品感，不要 web 化

**配色 CSS 变量**：

```css
:root {
  --poster-bg: #F5F0E8;         /* cream 纸底 */
  --poster-ink: #1A1A1A;        /* 正文黑 */
  --poster-muted: #6B6560;      /* 次要文字 */
  --poster-accent: #B5392A;     /* 锈红 accent（标题首字 / 装饰线） */
  --poster-line: #D4CFC7;       /* 分割线 */
}
```

---

## 字体推荐

| 子场景 | Display Font | Body Font | Google Fonts 引入 |
|-------|-------------|-----------|-------------------|
| 营销海报 | Montserrat (800/900) | Poppins (400/500) | `family=Montserrat:wght@800;900&family=Poppins:wght@400;500` |
| 杂志风海报 | Playfair Display (700/900) | IBM Plex Serif (400/500) | `family=Playfair+Display:wght@700;900&family=IBM+Plex+Serif:wght@400;500` |

## 背景质感速查

海报对背景质感要求比报告更高，以下是推荐选项：

| 质感 | 适用场景 | CSS 实现 |
|------|---------|---------|
| Mesh gradient | 营销海报 | 多个 `radial-gradient` 叠加 |
| Noise grain | 通用 | SVG `<filter feTurbulence>` opacity 0.03~0.05 |
| Dot pattern | 杂志风 | `radial-gradient` + `background-size` |
| 几何散落 | 营销海报 | SVG `<circle>` / `<polygon>` 半透明 |
| 波浪曲线 | 营销海报底部 | SVG `<path>` 贝塞尔曲线 |

## 避坑

- **营销海报不要用白底**：白底海报没有视觉冲击力，渐变或深色底是基本要求
- **杂志风海报不要用无衬线字体做标题**：editorial 的灵魂就是 serif 大标题
- **不要用 img 加载外部图片做装饰**：外部链接会失效，用 SVG 内联或 emoji
- **二维码用 SVG 占位**：不要放真实二维码（用户场景可能变化），用方框 + 文字标注代替
- **杂志风的 drop cap 不要超过 3 行**：太大影响阅读节奏
- **竖版海报注意底部安全区**：底部 10% 可能被手机系统导航栏遮挡，重要信息不要放太靠下
