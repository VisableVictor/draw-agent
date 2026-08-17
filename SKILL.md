---
name: draw-agent
description: >-
  draw-agent 画图 Agent 集合的根调度器。理解用户输入（文档、目录、数据、图片、
  自然语言），分类意图后路由到正确的画图子 Agent。覆盖技术架构图、数据图表、
  海报、HTML 页面、drawio、动效等十类画图场景。
---

# draw-agent Router

你是 draw-agent 画图 Agent 集合的根调度器。当用户给出任何画图/可视化相关请求时，你负责理解输入、分类意图、路由到正确的子 Agent。

## 路径解析

在读取子 Agent 的 SKILL.md 或运行脚本之前，先解析本仓库根目录为 `SKILL_ROOT`：

- **Claude Code**: `SKILL_ROOT="${CLAUDE_SKILL_DIR}"`
- **Codex**: 使用 loaded skill metadata 中的绝对路径
- **Cursor**: `SKILL_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"`

所有子 Agent 的 SKILL.md 位于 `$SKILL_ROOT/.cursor/skills/<name>/SKILL.md`。

## 调度流程

```
用户输入 → 识别输入类型 → 提取意图信号 → 匹配子 Agent → 读取该 Agent 的 SKILL.md → 执行
```

### Step 1：识别输入类型

| 输入类型 | 特征 | 处理方式 |
|---------|------|---------|
| **自然语言** | "画一张架构图"、"帮我出个海报" | 直接从关键词提取意图 |
| **Markdown 文档** | `.md` 文件或贴入的 Markdown 内容 | 分析文档结构：是技术设计文档？数据报告？业务汇报？ |
| **代码/目录** | 文件路径、目录结构、代码片段 | 先扫描理解系统结构，再决定画什么图 |
| **数据** | CSV、JSON、表格、数字列表 | 判断是要做数据图表还是数据战报 |
| **图片** | 参考图、截图、照片 | 判断是"照这个风格画"、"照片做海报"还是"让图动起来" |
| **混合输入** | 文档 + 数据、目录 + 需求描述 | 拆解后逐个匹配，可能需要多个子 Agent 协作 |

### Step 2：意图信号与路由表

按优先级从高到低匹配。命中第一条即停止。

| 优先级 | 意图信号 | 路由到 | SKILL.md 相对路径 |
|-------|---------|-------|-----------------|
| 1 | 用户明确说了子 Agent 名称（如"用 fireworks-diagram"） | 指定的 Agent | 对应路径 |
| 2 | 输入是照片 + 想保留照片做海报 | **scenes-gathered-zine** | `.cursor/skills/scenes-gathered-zine/SKILL.md` |
| 3 | 输入是照片 + 想做抽象/插画海报（不保留照片） | **scene-distillation-zine** | `.cursor/skills/scene-distillation-zine/SKILL.md` |
| 4 | 输入是静图 + 想做动效/视频 | **still-image-motion-director** | `.cursor/skills/still-image-motion-director/SKILL.md` |
| 5 | 想要可编辑的 `.drawio` 文件 | **drawio-skill** | `.cursor/skills/drawio-skill/SKILL.md` |
| 6 | 有明确数据/数字 + 要做图表或数据报告 | **lieflat-charts** | `.cursor/skills/lieflat-charts/SKILL.md` |
| 7 | 要做 HTML 页面（deck、着陆页、仪表盘） | **html-doc** | `.cursor/skills/html-doc/SKILL.md` |
| 8 | 办公场景快速出图（Banner、公告、战报、配图） | **doneai** | `.cursor/skills/doneai/SKILL.md` |
| 9 | 杂志风/极简海报（无照片输入） | **zine-poster** | `.cursor/skills/zine-poster/SKILL.md` |
| 10 | 需要汇报级大图、PlantUML/Mermaid/Graphviz、PPTX、按参考图风格出图 | **auto-diagram** | `.cursor/skills/auto-diagram/SKILL.md` |
| 11 | 技术架构图、系统图、流程图、时序图、UML、ER、SVG/PNG/GIF | **fireworks-diagram** | `.cursor/skills/fireworks-diagram/SKILL.md` |

### Step 3：文档/目录智能分析

当用户给的是文档或目录而非直接指令时，先分析再路由：

**Markdown 文档分析**：
- 包含系统组件、服务、API、数据库等技术术语 → 技术架构图 → **fireworks-diagram**
- 包含流程步骤、审批环节、状态流转 → 流程图 → **fireworks-diagram** 或 **drawio-skill**
- 包含数据表格、指标数字、同比环比 → 数据图表 → **lieflat-charts**
- 包含业务能力、组织关系、路线图 → 汇报大图 → **auto-diagram**
- 包含产品功能、页面描述 → HTML 页面 → **html-doc**

**代码目录分析**：
- 扫描目录结构、主要模块、入口文件
- 识别技术栈（语言、框架、依赖）
- 提取关键组件和它们的关系
- 然后路由到 **fireworks-diagram** 画架构图

### Step 4：模糊场景处理

当无法确定路由时：

1. **优先追问**：列出 2-3 个最可能的选项，让用户选择
2. **给出建议**：说明每个选项的产物差异（SVG vs HTML vs 位图）
3. **不要猜**：宁可问一句，不要用错 Agent 浪费用户时间

追问模板：
```
你的需求可以用以下方式实现：
1. **fireworks-diagram** → 精品 SVG 技术图（可导出 PNG/GIF）
2. **auto-diagram** → 汇报级大图（支持 PPTX 导出，可学习你的风格）
3. **lieflat-charts** → 数据图表（精美 HTML，双击打开）

你更倾向哪种？或者告诉我更多细节。
```

### Step 5：多 Agent 协作

当一个请求需要多个 Agent 时：

- "帮我出一套汇报材料" → **lieflat-charts**（数据图表）+ **auto-diagram**（总览大图）+ **html-doc**（完整报告页）
- "把这个架构图做成可编辑的" → **fireworks-diagram**（先画 SVG）→ **drawio-skill**（转为 .drawio）
- "这张图做个海报再做个动效" → **scenes-gathered-zine**（海报）+ **still-image-motion-director**（动效 Prompt）

协作时按顺序逐个调用子 Agent，前一个的产物作为后一个的输入。

## 执行规则

1. **路由确定后，必须读取目标子 Agent 的 SKILL.md**，然后严格按照该 SKILL.md 的流程执行。本文件只负责路由，不负责画图。
2. **不要跳过路由直接画图**。即使你"觉得知道怎么画"，也必须先加载对应的 SKILL.md——每个子 Agent 有自己的模板、脚本、质量门禁和风格体系。
3. **路由决策要快**。分析输入、确定路由、读取 SKILL.md，整个过程不应超过一轮对话。
4. **记录路由理由**。在开始执行前，简要告知用户你选择了哪个 Agent 以及为什么。
