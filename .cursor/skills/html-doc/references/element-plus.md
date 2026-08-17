# Element Plus CDN 集成参考

当页面需要更丰富的 UI 组件（卡片、折叠面板、进度条、对话框、表单控件）时，可引入 Element Plus。

## 引入方式

```html
<!-- 在 head 中引入 -->
<link rel="stylesheet" href="https://unpkg.com/element-plus/dist/index.css">
<script src="https://unpkg.com/element-plus"></script>

<!-- 在 Vue 应用注册 -->
<script>
const app = createApp({ setup() { /* ... */ } });
app.use(ElementPlus);
app.mount('#app');
</script>
```

## 常用组件替换

| 原生实现 | Element Plus 组件 |
|---------|------------------|
| 自定义卡片 | `<el-card>` |
| 原生 checkbox | `<el-checkbox>` |
| 自定义进度条 | `<el-progress>` |
| 手动折叠面板 | `<el-collapse>` + `<el-collapse-item>` |
| 手动对话框 | `<el-dialog>` |
| 手动提示框 | `<el-alert>` |
| 手动标签页 | `<el-tabs>` + `<el-tab-pane>` |

## 使用场景建议

- 适合需要多个同类型组件的场景（如多个卡片、多个表单）
- 组件自带交互和动画，减少手动编写代码
- CDN 引入会增加约 300KB 文件体积，仅在必要时使用
- 简单的单页文档不需要引入组件库

## 样式覆盖

Element Plus 默认样式可能与 Tailwind 风格不一致，建议添加自定义 CSS 覆盖：

```css
.el-card { border: 1px solid #e5e7eb; box-shadow: none; }
.el-checkbox__label { color: #374151 !important; }
.el-collapse { border: none; }
```

## 注意事项

- Element Plus 与 Vue 3 配合使用，不支持纯 HTML 页面
- 使用 CDN 版本时，全局变量为 `ElementPlus`
- 组件的 props 使用 kebab-case（如 `stroke-width`），在 Vue 模板中也可用 camelCase（如 `strokeWidth`）
