# Web 原型与仪表盘美学指南

> 本文件是 SKILL.md 场景路由的参考。当用户需要生成着陆页、定价页、仪表盘、看板、线框图、移动 App 等 Web 原型时读取此文件。

## 通用约束

- **响应式优先**：至少处理 `md:` 断点，移动端单栏、桌面端多栏
- **现代 Web 设计语言**：大字号、柔和渐变、充足留白，不要拥挤过时
- **技术栈**：Tailwind CSS (CDN) + Google Fonts，不引入额外框架
- **交互反馈**：所有可点击元素必须有 `hover` / `active` 状态，不能看起来像死的

## 子场景设计思路

### SaaS 着陆页

**触发信号**：用户说"着陆页"、"landing page"、"产品页"、"官网"。

**布局**：
1. **Top nav**：logo + 导航链接 + sign-in + 主 CTA 按钮
2. **Hero**：大标题（text-5xl~6xl）+ 副标题 + 双 CTA（primary / secondary）+ 右侧可视化占位（SVG 插画或 dashboard 截图占位）
3. **Logo wall**：社会认证，一行 5-6 个灰色 logo 占位
4. **Features**：3-6 个特性卡片，每张 icon + 标题 + 描述，网格排列
5. **How it works**：3 步流程，编号 + 图标 + 说明
6. **Pricing**：2-3 档定价卡片，推荐档高亮
7. **FAQ**：`<details>/<summary>` 手风琴折叠
8. **Footer**：多列链接 + 版权 + 社交图标

**设计语言**：现代 SaaS 风——大字号 hero、柔和渐变背景、glassmorphism 卡片（`backdrop-blur` + 半透明底）、滚动入场动画（`IntersectionObserver` 触发 `opacity` + `translateY`）。移动端单栏堆叠，桌面端双栏或网格。

**配色 CSS 变量**：

```css
:root {
  --lp-bg: #FAFBFF;             /* 页面背景 */
  --lp-surface: #FFFFFF;        /* 卡片 / section 背景 */
  --lp-ink: #0F172A;            /* 主文字 */
  --lp-muted: #64748B;          /* 次要文字 */
  --lp-primary: #6366F1;        /* 主 CTA / 链接 */
  --lp-primary-hover: #4F46E5;  /* 主 CTA hover */
  --lp-accent: #A78BFA;         /* 渐变辅助色 */
  --lp-border: #E2E8F0;         /* 分割线 / 边框 */
}
```

---

### 定价页

**触发信号**：用户说"定价页"、"pricing"、"套餐对比"。

**布局**：
1. **Header**：简洁导航 + 页面标题
2. **Monthly / Annual 切换**：toggle 开关，年付显示折扣标签（如 "Save 20%"）
3. **3 档定价卡片**：Free / Pro / Enterprise，中间档 popular 高亮（`border-2` + `shadow-xl` + `scale-105`）
4. **特性对比表**：语义化 `<table>`，每行一个特性，每列一个档位，用 ✓ / – 标记
5. **FAQ**：`<details>/<summary>` 手风琴
6. **底部 CTA**：一句话号召 + 按钮

**设计语言**：推荐档用 `border-2 border-primary` + `shadow-xl` + `scale-105` 突出，CTA 按钮层级清晰（primary 给推荐档、secondary 给其他档、tertiary 给 Enterprise 的 "Contact us"）。价格数字用大字号 + 等宽字体呈现。

**配色 CSS 变量**：

```css
:root {
  --pricing-bg: #F8FAFC;        /* 页面背景 */
  --pricing-card: #FFFFFF;      /* 卡片背景 */
  --pricing-ink: #0F172A;       /* 主文字 */
  --pricing-muted: #94A3B8;     /* 次要文字 / 不适用标记 */
  --pricing-popular: #6366F1;   /* 推荐档边框 / 按钮 */
  --pricing-check: #22C55E;     /* 对比表勾号 */
  --pricing-dash: #CBD5E1;      /* 对比表横线 */
}
```

---

### 仪表盘

**触发信号**：用户说"仪表盘"、"dashboard"、"管理后台"、"数据看板"。

**布局**：
1. **Fixed left sidebar**（`w-64`）：logo + 导航菜单（带 icon + 激活态高亮）+ 底部用户信息（avatar + 名字 + 设置入口）
2. **Top bar**：搜索框 + 通知铃铛（带红点）+ 用户 avatar 下拉
3. **Main content**：
   - KPI cards 网格（3-5 个）：每个含标题 + 大数字 + 趋势指示（↑ 绿 / ↓ 红 + 百分比）
   - 1-2 张主图表（折线 / 柱状 / 区域图，Chart.js）
   - 底部 recent activity 列表（时间 + 事件 + 用户头像）

**设计语言**：侧边栏宽度 `w-64`，暗色（`bg-slate-900`）或白色均可。KPI 卡片要有趋势箭头和百分比变化。图表容器**必须有固定高度**（详见 `chart-pitfalls.md`），否则 Chart.js 会卡死浏览器。

**配色 CSS 变量**：

```css
:root {
  --dash-sidebar: #0F172A;      /* 侧边栏背景 */
  --dash-sidebar-ink: #94A3B8;  /* 侧边栏文字 */
  --dash-sidebar-active: #6366F1; /* 激活菜单项 */
  --dash-bg: #F1F5F9;           /* 主区域背景 */
  --dash-card: #FFFFFF;         /* 卡片背景 */
  --dash-ink: #0F172A;          /* 主文字 */
  --dash-muted: #64748B;        /* 次要文字 */
  --dash-up: #22C55E;           /* 上升趋势 */
  --dash-down: #EF4444;         /* 下降趋势 */
}
```

---

### 看板

**触发信号**：用户说"看板"、"kanban"、"任务板"、"sprint board"。

**布局**：
1. **顶部 filter bar**：assignee 筛选 + label 筛选 + 搜索框
2. **4 列**：To do / In progress / In review / Done，横向滚动（`overflow-x-auto`）
3. **卡片**：标题 + labels（彩色 pill）+ due date + avatar + 评论数气泡
4. **可选 swimlanes**：按 assignee 或 priority 横向分行

**设计语言**：视觉上像可拖拽但不需要真 drag 实现。列头用不同颜色标识（如蓝 / 黄 / 紫 / 绿）。卡片有 `hover:shadow-lg` + `cursor-grab` 反馈。Done 列的卡片可加 `opacity-60` 表示已完成。

**配色 CSS 变量**：

```css
:root {
  --kb-bg: #F1F5F9;             /* 看板背景 */
  --kb-col: #E2E8F0;            /* 列背景 */
  --kb-card: #FFFFFF;           /* 卡片背景 */
  --kb-ink: #0F172A;            /* 主文字 */
  --kb-muted: #64748B;          /* 次要文字 */
  --kb-todo: #3B82F6;           /* To do 列头 */
  --kb-progress: #F59E0B;       /* In progress 列头 */
  --kb-review: #8B5CF6;         /* In review 列头 */
  --kb-done: #22C55E;           /* Done 列头 */
}
```

---

### 手绘线框

**触发信号**：用户说"线框"、"wireframe"、"草稿"、"低保真"。

**布局**：
1. **Graph-paper 网格背景**：CSS `linear-gradient` 画细线网格
2. **多 tab labels**：顶部变体标签（"Variant A" / "Variant B"），手写体
3. **Scribbled chart placeholders**：图表用波浪线手绘框 + hatched fills（SVG `<pattern>` 斜线填充）
4. **Sticky-note annotations**：黄色便签（`bg-yellow-100`），旋转 1-2 度（`rotate-1` / `-rotate-2`），带手写批注

**设计语言**：字体用 Caveat / Architects Daughter，不要用 Tailwind 默认字体。不要规整对齐，要有手绘的随意感——元素可以略微歪斜、间距不等。hatched fill 用 SVG `<pattern>` 实现斜线填充，不要用纯色块。

**配色 CSS 变量**：

```css
:root {
  --wf-bg: #FAFAF8;             /* 纸张底色 */
  --wf-grid: #D4D4D4;           /* 网格线 */
  --wf-ink: #1A1A1A;            /* 手绘笔触 */
  --wf-muted: #6B7280;          /* 次要文字 */
  --wf-hatch: #9CA3AF;          /* 斜线填充 */
  --wf-note: #FEF9C3;           /* 便签黄 */
  --wf-accent: #3B82F6;         /* 标注蓝 */
}
```

---

### 移动 App 单屏

**触发信号**：用户说"App 设计"、"移动端"、"iOS"、"手机页面"。

**布局**：
1. **iPhone 15 Pro frame**：纯 CSS 模拟——像素级圆角边框（`rounded-[55px]`）+ `box-shadow` 多层阴影 + dynamic island（顶部居中黑色椭圆）
2. **Status bar**：时间（左侧）+ 电池 / 信号 / WiFi 图标（右侧），用 SVG 内联
3. **App header**：标题 + 头像 + 搜索图标
4. **Main content**：feed / list / detail / form 之一，根据用户需求决定
5. **Bottom tab bar**：4-5 个 tab，icon + label，当前 tab 高亮

**设计语言**：safe-area 留白（顶部 44px, 底部 34px），圆角内容区域。frame 用 CSS `border-radius` + `box-shadow` 模拟，**不用外部设备图片**。整体宽度固定 `w-[393px]`（iPhone 15 Pro 逻辑宽度）。

**配色 CSS 变量**：

```css
:root {
  --app-bg: #F2F2F7;            /* iOS 系统灰背景 */
  --app-card: #FFFFFF;          /* 卡片 / 列表背景 */
  --app-ink: #000000;           /* 主文字 */
  --app-muted: #8E8E93;         /* 次要文字 */
  --app-blue: #007AFF;          /* iOS 蓝 */
  --app-separator: #C6C6C8;     /* 列表分割线 */
  --app-tab-bg: #F8F8F8;        /* 底部 tab bar 背景 */
}
```

---

## 字体推荐

| 子场景 | Display Font | Body Font | Google Fonts 引入 |
|-------|-------------|-----------|-------------------|
| SaaS 着陆页 | Plus Jakarta Sans (600/700) | Inter (400/500) | `family=Plus+Jakarta+Sans:wght@600;700&family=Inter:wght@400;500` |
| 定价页 | Plus Jakarta Sans (600/700) | Inter (400/500) | 同 SaaS 着陆页 |
| 仪表盘 | Inter (400/500/600) | JetBrains Mono (500)（数字） | `family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500` |
| 看板 | Inter (400/500/600) | Inter (400/500) | `family=Inter:wght@400;500;600` |
| 手绘线框 | Caveat (400/700) | Architects Daughter (400) | `family=Caveat:wght@400;700&family=Architects+Daughter` |
| 移动 App | Inter (400/500/600) | Noto Sans SC (400/500) | `family=Inter:wght@400;500;600&family=Noto+Sans+SC:wght@400;500` |

## 交互代码片段

### FAQ 手风琴（details/summary）

```html
<section class="max-w-3xl mx-auto space-y-3">
  <details class="group rounded-xl border border-[var(--lp-border)] p-5">
    <summary class="flex cursor-pointer items-center justify-between font-semibold text-[var(--lp-ink)]">
      <span>问题一：如何开始使用？</span>
      <span class="transition-transform group-open:rotate-180">▾</span>
    </summary>
    <p class="mt-3 text-[var(--lp-muted)] leading-relaxed">
      注册后即可免费使用基础功能，无需信用卡。
    </p>
  </details>
  <details class="group rounded-xl border border-[var(--lp-border)] p-5">
    <summary class="flex cursor-pointer items-center justify-between font-semibold text-[var(--lp-ink)]">
      <span>问题二：支持哪些付款方式？</span>
      <span class="transition-transform group-open:rotate-180">▾</span>
    </summary>
    <p class="mt-3 text-[var(--lp-muted)] leading-relaxed">
      支持信用卡、PayPal 及银行转账，年付享 8 折优惠。
    </p>
  </details>
</section>
```

### Monthly / Annual 切换

```html
<div class="flex items-center justify-center gap-3 mb-8">
  <span id="label-monthly" class="font-medium text-[var(--pricing-ink)]">Monthly</span>
  <button id="billing-toggle" onclick="toggleBilling()"
    class="relative w-14 h-7 rounded-full bg-[var(--pricing-popular)] transition-colors">
    <span id="toggle-dot"
      class="absolute top-0.5 left-0.5 w-6 h-6 rounded-full bg-white shadow transition-transform"></span>
  </button>
  <span id="label-annual" class="font-medium text-[var(--pricing-muted)]">
    Annual <span class="text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full ml-1">-20%</span>
  </span>
</div>
```

```javascript
let isAnnual = false;
const prices = { monthly: [0, 29, 99], annual: [0, 23, 79] };

function toggleBilling() {
  isAnnual = !isAnnual;
  const dot = document.getElementById('toggle-dot');
  dot.style.transform = isAnnual ? 'translateX(28px)' : 'translateX(0)';

  document.getElementById('label-monthly')
    .className = 'font-medium ' + (isAnnual ? 'text-[var(--pricing-muted)]' : 'text-[var(--pricing-ink)]');
  document.getElementById('label-annual')
    .className = 'font-medium ' + (isAnnual ? 'text-[var(--pricing-ink)]' : 'text-[var(--pricing-muted)]');

  // 更新价格显示（假设价格元素有 data-tier 属性）
  const set = isAnnual ? prices.annual : prices.monthly;
  document.querySelectorAll('[data-tier]').forEach((el, i) => {
    el.textContent = set[i] === 0 ? 'Free' : '$' + set[i];
  });
}
```

## 避坑

- **着陆页不要跳过 mobile 断点**——超过 50% 的流量来自手机，移动端不处理就是半成品
- **仪表盘的图表容器必须有固定高度**（详见 `chart-pitfalls.md`），否则 Chart.js 会卡死浏览器
- **定价页的对比表不要用 div 模拟 table**——语义化用 `<table>` 更可靠，浏览器自动处理对齐和响应式
- **线框图不要用 Tailwind 默认字体**——手绘风的灵魂就是手写体，默认 Inter 一秒破功
- **移动 App frame 不要引用外部设备图片**——外部链接会失效，用纯 CSS `border-radius` + `box-shadow` 模拟更可靠
- **glassmorphism 不要过度**：`backdrop-blur` 值控制在 8-16px，太高会糊成一片，太低看不出毛玻璃效果
- **看板列不要少于 3 列**——两列看板没有视觉意义，至少 To do / In progress / Done 三列
- **仪表盘侧边栏图标不要省略**——纯文字的侧边栏导航辨识度差，icon + label 组合是标配
