# 定期报告预设

> 日报 / 周报 / 月报等周期性报告的固定样式规范。跳过 Step 0 美学定调，使用固定蓝色调。

## 触发信号

用户说"日报"、"周报"、"月报"、"每日简报"、"weekly report"、"monthly report"，或由 orchestrator 触发。

## 技术栈

- Tailwind CSS（CDN）+ Google Fonts（Noto Serif SC + Inter）

```html
<script src="https://cdn.tailwindcss.com"></script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Serif+SC:wght@400;600;700&display=swap" rel="stylesheet">
```

## Tailwind 主题配置

```js
tailwind.config = {
  theme: {
    extend: {
      colors: {
        surface: '#FAFAFA',
        'surface-alt': '#F3F4F6',
        border: '#E5E7EB',
        'text-primary': '#111827',
        'text-secondary': '#374151',
        'text-muted': '#9CA3AF',
        accent: '#2563EB',
        'accent-light': '#EFF6FF',
        warm: '#D97706',
        'warm-light': '#FFFBEB',
        success: '#059669',
        'success-light': '#ECFDF5',
        purple: '#7C3AED',
        'purple-light': '#F5F3FF',
        rose: '#E11D48',
        'rose-light': '#FFF1F2',
      },
      fontFamily: {
        display: ['"Noto Serif SC"', 'Georgia', 'serif'],
        body: ['Inter', 'system-ui', 'sans-serif'],
      },
    }
  }
}
```

## 布局

- 主容器：`max-w-5xl mx-auto px-5 py-10 sm:px-8 sm:py-14`
- 段落行宽约束：`max-w-xl`
- 标题用 `font-display`，正文用 `font-body`

## 全局 CSS

```css
body { font-family: 'Inter', system-ui, sans-serif; background: #FAFAFA; color: #111827; }
h1, h2, h3 { font-family: 'Noto Serif SC', Georgia, serif; }
.card { background: #fff; border: 1px solid #E5E7EB; border-radius: 10px; }
.source-link {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; border-radius: 8px; font-size: 0.85rem; font-weight: 500;
  transition: all 0.15s ease; text-decoration: none;
}
.source-link:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.06); }
.copy-btn { transition: all 0.15s ease; }
.copy-btn:hover { background-color: #EFF6FF; color: #2563EB; border-color: #2563EB; }
.copy-btn.copied { background-color: #10B981; color: white; border-color: #10B981; }
@media print { body { background: white; } }
```

## 交互模式：复制按钮

报告中的"汇报摘要"区域常带复制按钮，供用户直接粘贴到 IM/邮件。标准实现：

```html
<button id="copySummary" class="copy-btn px-3 py-1.5 text-xs font-body border border-border rounded text-text-secondary flex items-center gap-1.5">
  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
  </svg>
  复制
</button>
```

```js
(function(){
  var btn = document.getElementById('copySummary');
  if (!btn) return;
  var original = btn.innerHTML;
  btn.addEventListener('click', function(){
    var text = document.getElementById('summaryText').innerText;
    navigator.clipboard.writeText(text).then(function(){
      btn.classList.add('copied');
      btn.innerHTML = '<span>已复制</span>';
      setTimeout(function(){ btn.classList.remove('copied'); btn.innerHTML = original; }, 2000);
    });
  });
})();
```

要点：用 `innerHTML` 保存/恢复原始内容（含 SVG 图标），不要用 `innerText` 覆盖。

## 交互模式：时间线导航

多期报告之间跳转，用紧凑的 pill 按钮排列：

```html
<div class="flex flex-wrap gap-1.5">
  <a href="../2026-06-23/index.html" class="px-2.5 py-1 text-xs font-body rounded border border-border text-text-muted hover:border-accent hover:text-accent transition-colors">06-23</a>
  <span class="px-2.5 py-1 text-xs font-body rounded bg-accent text-white font-semibold">06-24</span>
  <a href="../2026-06-25/index.html" class="px-2.5 py-1 text-xs font-body rounded border border-border text-text-muted hover:border-accent hover:text-accent transition-colors">06-25</a>
</div>
```

当前期用 `<span>` + `bg-accent text-white`，其他期用 `<a>` + hover 变色。

## 禁止项

- 禁止暖色调类名（`text-ink`、`bg-surface`、`border-line`、`card-shadow`）
- 禁止 Instrument Serif / Manrope 字体
- 禁止 `max-w-3xl`（768px 偏窄）或 `max-w-4xl`（896px）作为主容器宽度
- 禁止在 `<style>` 中重复定义已在 tailwind.config 中的颜色
- 禁止走 Step 0 美学定调（风格已固定）
