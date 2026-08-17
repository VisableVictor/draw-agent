# 数据分离架构

> 当报告包含大量数据时，采用"模板 + 构建脚本"架构，避免将原始数据硬编码到 HTML 中浪费 token。

## 核心思路

```
数据源 (JSON/CSV/API) → 构建脚本 (Node.js) → 自包含 HTML
                              ↑
                     HTML 模板 (带占位符)
```

三个文件各司其职：
- **HTML 模板**：页面结构和样式，含**示例数据**（包在 `<script data-template>` 标签内），构建时整段替换
- **构建脚本**（`build.js`）：读取数据源 → 读取模板 → 标签整段替换 → 输出最终 HTML
- **最终产物**：自包含单文件，数据内联在 `<script>` 中，可直接传播

## 模板中的数据占位

模板用 `<script data-template>` 标签包裹示例数据作为占位（机制详见 `references/template-vue-guide.md`），构建脚本整段替换该标签即可。

`assets/templates/` 中的预置模板都采用此方式：示例数据即契约、独立打开可见渲染、数据量小可手填跳过构建脚本。

## 构建脚本（复制改造）

`assets/scripts/build.js` 是构建脚本的**复制改造模板**，使用方式与 HTML 模板一致：

1. **复制到项目目录**：`cp assets/scripts/build.js my-project/build.js`
2. **改顶部 3 个路径常量**：`TEMPLATE_PATH` / `DATA_PATH` / `OUTPUT_PATH`
3. 需要数据聚合 / 统计 / 跨源合并时，编辑 `transform()` 函数（默认透传，文件里有示例）
4. **跑**：`node build.js`

脚本做的事：读模板 + 读数据 → `transform()` 加工 → 整段替换 `<script data-template>` 标签 → 输出最终 HTML。

内置：
- `</script>` 防污染（`.replace(/<\//g, '<\\/')`）
- 找不到 `<script data-template>` 时报错而非静默失败
- 输出路径上级目录不存在时自动 `mkdir -p`

数据准备：`data.json` 的形状参考模板内 `<script data-template>` 的示例数据（示例数据本身即契约的活文档）。

## 何时使用

| 场景 | 方案 |
|------|------|
| 数据量小（<20 行表格、<5 个图表） | 直接在 HTML 中用 JS 变量管理数据 |
| 数据量大（几十行以上表格、需要统计分析） | 模板 + 构建脚本 |
| 数据会频繁更新 | 模板 + 构建脚本（重跑脚本即可） |

## 好处
- **AI 维护成本低**：模板不含数据，体积小，修改设计时省 token
- **数据更新无需 AI**：`node build.js` 一条命令重新生成
- **最终产物自包含**：单文件 HTML，发给任何人都能直接打开
