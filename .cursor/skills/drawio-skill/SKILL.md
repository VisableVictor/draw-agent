---
name: drawio-skill
description: >-
  生成可编辑的 .drawio 文件（在 draw.io / diagrams.net 中打开和修改）。
  当用户明确要求 drawio 格式、想要可二次编辑的矢量图、或操作现有 .drawio 文件时使用。
  覆盖泳道图、组织架构图、思维导图、鱼骨图、决策树、四象限图、维恩图、漏斗图等。
  Use when user mentions drawio、draw.io、diagrams.net、.drawio文件、
  转drawio、生成drawio、可编辑的图、泳道图、组织架构图、思维导图、
  鱼骨图、决策树、四象限图、维恩图、漏斗图。
  不用于：纯展示 SVG/PNG、数据图表、海报、照片处理。
alwaysApply: false
globs: ["**/*.drawio"]
---

# Draw.io 绘图技能

根据用户文字描述，生成结构清晰、布局合理、配色专业、可在 draw.io 中编辑的 `.drawio` 文件。覆盖从技术架构到业务流程再到各类示意的图表。

> 若用户需求明显更适合其他工具（如纯文本内联的 Mermaid、信息图海报），可提示存在更合适的技能；但只要用户希望得到可在 draw.io 中自由编辑的矢量图，即使用本技能。

## 工作流程

### 1. 需求确认

先对齐需求再动手，是因为图类型、布局、配色一旦选定会贯穿整张图，返工成本高。信息不完整时主动确认（已明确的项可跳过）：

- **图的类型**：见「支持的图表类型」总览，识别用户意图对应哪一类——这决定后续布局与形状选择
- **核心元素/节点**：需要展示哪些对象（模块、步骤、角色、概念、事件等）
- **关系类型**：调用/数据流/依赖（技术图），或先后/包含/因果/对比（业务与通用图）——决定连线样式
- **标签语言**：中文还是英文
- **布局偏好**：上下分层、左右流向、泳道、放射（思维导图）、树形（组织架构）、时间轴、网格/矩阵
- **配色模板**：经典柔和（默认）、科技蓝、商务暖、深色专业、扁平现代、高对比（完整色值见 references/color-schemes.md）

### 支持的图表类型

按用途分为三大类，选择最贴近用户意图的类型，避免用错布局导致图意表达偏差：

**技术类图表**

| 类型 | 说明 | 推荐布局 |
|------|------|---------|
| 系统/云/微服务架构图 | 分层展示组件与调用关系 | 上下分层 |
| 部署/网络拓扑图 | 展示节点、区域、连接 | 分区+网格 |
| 数据流图（DFD） | 展示数据在系统间流转 | 左右流向 |
| 时序图（Sequence） | 展示对象间按时间的消息交互 | 竖向生命线 |
| ER 图 / 类图 | 展示实体/类及其关系 | 网格+连线 |
| 状态机图 | 展示状态与转移 | 有向图 |

**业务类图表**

| 类型 | 说明 | 推荐布局 |
|------|------|---------|
| 业务流程图 | 展示业务处理步骤与分支 | 左右或上下流向 |
| 泳道图 | 跨角色/部门的流程协作 | 泳道 |
| 组织架构图 | 展示汇报层级 | 树形 |
| 时间线 / 路线图 | 展示里程碑与阶段 | 水平时间轴 |
| 漏斗图 | 展示转化各环节递减 | 竖向递减 |
| 看板 / 泳道板 | 展示任务状态流转 | 列式泳道 |

**通用/思维类图表**

| 类型 | 说明 | 推荐布局 |
|------|------|---------|
| 思维导图 | 中心主题放射展开 | 放射/树形 |
| 四象限图 | 二维维度分类（如重要-紧急） | 十字象限 |
| 鱼骨图（因果图） | 分析问题根因 | 主干+分支 |
| 维恩图 | 展示集合交叠关系 | 交叠圆 |
| 概念关系图 | 展示概念间的自由关系 | 力导向/自由 |
| 亲和图 / 分组图 | 归类整理离散想法 | 分组容器 |

### 2. 创建或修改 .drawio 文件

**新建图**——按此顺序是为了先定骨架再填细节，避免坐标返工：

1. 分析需求，确定图的类型和布局方式
2. 规划节点位置坐标（基于布局规则）
3. 生成 mxGraphModel XML
4. 检查连线、对齐、命名
5. 写入 `.drawio` 文件

**修改已有图**——须先理解再改，以免破坏用户既有的布局与语义：

1. 读取现有 `.drawio` 文件
2. 解析 XML 结构，理解现有节点和连线
3. 仅修改用户要求的部分，保持原有布局风格
4. 保留语义关系，确保图仍可编辑且结构完整

### 3. 输出文件

仅输出 `.drawio` 文件。用户可在 draw.io 桌面版或 app.diagrams.net 中打开编辑。

## .drawio XML 结构

### 基础骨架

```xml
<mxfile host="app.diagrams.net" type="device">
  <diagram id="diagram-1" name="Page-1">
    <mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1"
      tooltips="1" connect="1" arrows="1" fold="1" page="1"
      pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- 节点和连线放在这里 -->
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

### 节点（Vertex）

```xml
<!-- 矩形节点 -->
<mxCell id="node-1" value="服务名称" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;fontFamily=system-ui;" vertex="1" parent="1">
  <mxGeometry x="100" y="100" width="160" height="60" as="geometry" />
</mxCell>

<!-- 分组容器 -->
<mxCell id="group-1" value="分组名称" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="50" y="50" width="400" height="300" as="geometry" />
</mxCell>
```

### 连线（Edge）

```xml
<!-- 实线箭头 -->
<mxCell id="edge-1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jetSize=auto;html=1;strokeColor=#333333;fontSize=11;" edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- 带标签的连线 -->
<mxCell id="edge-2" value="HTTP/REST" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jetSize=auto;html=1;strokeColor=#333333;fontSize=11;" edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>

<!-- 虚线连线 -->
<mxCell id="edge-3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;dashed=1;strokeColor=#999999;" edge="1" source="node-1" target="node-2" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

各类节点的完整样式串（数据库、云、菱形、人形、六边形、便签、气泡等），见 references/node-styles.md，复制即用。

## 绘图规则

### 布局规范

选对布局能让图的结构一眼可读，用错布局则会误导阅读方向：

| 布局类型 | 适用场景 | 说明 |
|---------|---------|------|
| 上下分层 | 系统架构图、云架构图、组织架构图 | 顶部为入口/根，向下展开 |
| 左右流向 | 业务流程图、数据流图、时间线 | 从左到右表示流程或时间方向 |
| 泳道 | 跨团队/跨角色流程、看板 | 按角色/系统/状态分列或分行 |
| 矩阵/网格 | 微服务架构、组件关系、ER图 | 网格排列，连线表示依赖或关系 |
| 放射（Radial） | 思维导图、概念关系图 | 中心主题居中，分支向四周放射 |
| 树形（Tree） | 组织架构图、分类树、决策树 | 根在上（或左），逐级向下分叉 |
| 时间轴（Timeline） | 里程碑、路线图、发展历程 | 水平主轴 + 上下交替事件卡片 |
| 象限（Quadrant） | 四象限图、优先级矩阵 | 十字分区，元素按坐标落位 |
| 主干分支（Fishbone） | 鱼骨图、因果分析 | 水平主干 + 斜向分支肋骨 |

**各布局坐标要点**：
- 放射：中心节点置于画布中心，子节点均匀分布在圆周（可按角度 `x=cx+r*cos(θ)`, `y=cy+r*sin(θ)` 估算），一级分支用曲线连接。
- 树形：同层节点等间距水平排列，父节点水平居中于子节点组之上；层间距 100-120px。
- 时间轴：一条水平直线作主轴，事件节点交替置于轴上方/下方，用短竖线连接到轴上的时间点。
- 象限：先画十字轴（两条正交直线）并标注四个象限标题，元素以小圆点或标签按语义落在对应象限。
- 鱼骨：一条水平主干指向"问题"（右端方框），主要原因作为斜向分支从主干两侧引出。

### 间距与对齐

统一间距与对齐能显著提升图的专业观感，杂乱的坐标会让图显得草率：

- 同层级节点间横向间距：40px
- 层与层之间纵向间距：80-100px
- 节点默认尺寸：160x60（可按内容调整）
- 分组容器内边距：上方留 40px（放标题），左右各留 20px
- 同层级元素必须严格对齐

### 节点命名

- 简洁明了，优先使用用户指定的语言
- 避免过长文本，超过 6-8 个字考虑换行（`whiteSpace=wrap`），因为过长文本会撑破节点或溢出
- 技术图保留英文术语（如 API Gateway、Redis、Kafka）；业务与通用图使用自然、口语化的短语（如"提交申请""客户下单"）
- 概念/思维类节点可用名词短语，流程类节点用"动词+宾语"以体现动作

### 连线原则

连线承载图的逻辑关系，混乱的连线会让整张图失去可读性：

- 连线必须明确 source 和 target
- 结构化图（架构/流程/时序）用 `orthogonalEdgeStyle` 保持线条整齐
- 思维导图、概念图等自由布局可用 `curved=1` 曲线，更柔和自然
- 避免连线交叉，必要时调整节点位置
- 关键关系用实线，可选/抽象/弱关系用虚线，以区分主次
- 连线标签简短：技术图用 "HTTP"、"gRPC"；业务图用 "是/否"、"通过/驳回"、"包含" 等

## 配色方案

配色的目的是用颜色传达语义（层级、状态、角色），而非装饰。共提供 6 套专业主题（经典柔和/科技蓝/商务暖/深色专业/扁平现代/高对比），以及分层架构、业务流程、泳道等分图类型的配色建议和连线配色规则。

**快速选择**：用户未指定时默认「经典柔和」；"科技/云/微服务"→科技蓝；"汇报/演示/商务"→商务暖或深色专业；"设计/产品"→扁平现代。

完整色值表、分图类型配色、连线配色与特殊标记规则，见 references/color-schemes.md。

## 分层架构布局参考（技术架构图）

对于复杂系统架构，按以下层次自上而下组织，符合读者对系统栈的心智模型：

1. **入口层**（y=0~100）：用户、客户端、CDN、DNS
2. **网关层**（y=150~250）：API Gateway、负载均衡、WAF
3. **应用层**（y=300~400）：BFF、Web 应用、移动端服务
4. **服务层**（y=450~600）：微服务、业务逻辑
5. **中间件层**（y=650~750）：消息队列、缓存、搜索引擎
6. **数据层**（y=800~900）：数据库、对象存储、数据仓库
7. **基础设施层**（y=950~1050）：K8s、云服务、监控

如果用户未指定具体层次，根据实际需求选择合适的层数，不必全部包含。

## 附加资源（references/）

需要具体色值、样式串或整图范例时，按需加载以下文件（路径相对于本 SKILL.md 所在目录）：

```bash
DRAWIO_SKILL_ROOT="$(dirname "$(realpath "$0")")"
# 或在 Cursor 中使用绝对路径:
# /Users/victor/IdeaProjects/draw-agent/.cursor/skills/drawio-skill/references/
```

- **references/color-schemes.md**：6 套配色主题完整色值、分图类型配色建议、连线配色与特殊标记
- **references/node-styles.md**：各类节点的 draw.io 样式串速查（复制即用）
- **references/templates.md**：各类图表的完整 XML 模板（架构/流程/泳道/组织架构/思维导图/时间线/四象限/鱼骨图/时序图/ER图）
- **references/style-guide.md**：样式属性、坐标尺寸、连线技巧、多页面、文本格式化等详细规范

## 输出要求

1. 使用 Write 工具生成 `.drawio` 文件
2. 文件名应简洁有意义、反映图表内容（如 `order-flow.drawio`、`team-org-chart.drawio`、`product-roadmap.drawio`），便于用户日后检索
3. 输出后告知用户可用 draw.io 桌面版或 app.diagrams.net 打开编辑
4. 对图的内容做简要说明：图表类型、包含哪些核心元素、关键关系或结构
