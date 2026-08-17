# Draw.io 样式与布局规范

本文件详细说明 draw.io XML 中的样式属性和布局技巧，供生成高质量图表时参考。

> **配色主题**：本文件中的颜色示例使用「经典柔和」默认主题。使用其他主题时，请参考 color-schemes.md 中的对应色值表进行替换。支持 6 种配色模板：经典柔和、科技蓝、商务暖、深色专业、扁平现代、高对比。

## 1. 样式属性速查

### 通用属性

| 属性 | 说明 | 常用值 |
|------|------|--------|
| `rounded` | 圆角 | 0=直角, 1=圆角 |
| `whiteSpace` | 文本换行 | `wrap` |
| `html` | 启用 HTML 标签 | 1 |
| `fillColor` | 填充颜色 | `#dae8fc` |
| `strokeColor` | 边框颜色 | `#6c8ebf` |
| `strokeWidth` | 边框粗细 | 1, 2, 3 |
| `fontSize` | 字号 | 11-16 |
| `fontStyle` | 字体样式 | 0=普通, 1=粗体, 2=斜体, 3=粗斜体 |
| `fontFamily` | 字体 | `system-ui` |
| `fontColor` | 字体颜色 | `#333333` |
| `dashed` | 虚线 | 0=实线, 1=虚线 |
| `opacity` | 透明度 | 0-100 |
| `shadow` | 阴影 | 0=无, 1=有 |
| `verticalAlign` | 垂直对齐 | `top`, `middle`, `bottom` |
| `align` | 水平对齐 | `left`, `center`, `right` |

### 容器属性

| 属性 | 说明 | 常用值 |
|------|------|--------|
| `container` | 标记为容器 | 1 |
| `collapsible` | 可折叠 | 0=不可折叠, 1=可折叠 |
| `childLayout` | 子元素布局 | `tableLayout` |
| `swimlane` | 泳道模式 | 1 |
| `startSize` | 标题区高度 | 30-50 |
| `horizontal` | 泳道方向 | 0=水平标题(垂直泳道), 1=垂直标题(水平泳道) |

### 连线属性

| 属性 | 说明 | 常用值 |
|------|------|--------|
| `edgeStyle` | 连线样式 | `orthogonalEdgeStyle`, `elbowEdgeStyle`, `entityRelationEdgeStyle` |
| `curved` | 曲线 | 0=直线, 1=曲线 |
| `rounded` | 连线拐角圆滑 | 0=直角, 1=圆角 |
| `orthogonalLoop` | 正交连接 | 1 |
| `jetSize` | 连接点偏移 | `auto` |
| `exitX/exitY` | 出发点位置 | 0-1 (相对坐标) |
| `entryX/entryY` | 到达点位置 | 0-1 (相对坐标) |
| `endArrow` | 箭头类型 | `classic`, `block`, `open`, `diamond`, `none` |
| `startArrow` | 起始箭头 | 同上 |
| `endFill` | 箭头填充 | 0=空心, 1=实心 |

## 2. 坐标与尺寸规范

### 标准节点尺寸

| 节点类型 | 宽度 | 高度 | 说明 |
|---------|------|------|------|
| 标准矩形 | 160 | 60 | 通用服务节点 |
| 小矩形 | 120 | 45 | 子模块、Pod |
| 圆柱体(DB) | 120 | 80 | 数据库 |
| 菱形(决策) | 120 | 90 | 判断节点 |
| 圆形(起止) | 80 | 60 | 流程起点/终点 |
| 云形状 | 160 | 80 | 外部系统/网络 |
| 人形 | 80 | 60 | 用户角色 |

### 间距规范

```
横向间距（同层节点）：40px
纵向间距（层与层）  ：80-100px
容器内边距          ：上 40px，左右 20px，下 20px
容器标题高度        ：30-40px
画布边距            ：最小 40px
```

### 坐标计算示例

五个同层服务节点居中排列（画布宽 1000px，节点宽 140px，间距 40px）：

```
总宽度 = 5 * 140 + 4 * 40 = 860px
起始 x = (1000 - 860) / 2 = 70px

节点1: x=70,   y=300, w=140, h=60
节点2: x=250,  y=300, w=140, h=60
节点3: x=430,  y=300, w=140, h=60
节点4: x=610,  y=300, w=140, h=60
节点5: x=790,  y=300, w=140, h=60
```

## 3. 特殊形状样式

### 数据库（圆柱体）

```
shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;
```

### 文档

```
shape=mxgraph.flowchart.document;whiteSpace=wrap;html=1;
```

### 队列/管道

```
shape=mxgraph.flowchart.delay;whiteSpace=wrap;html=1;
```

### 六边形

```
shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;
```

### 平行四边形

```
shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;size=20;
```

### 注释/便签

```
shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;size=15;fillColor=#ffffcc;strokeColor=#999;
```

## 4. 连线技巧

### 指定连接点

通过 `exitX/exitY` 和 `entryX/entryY` 精确控制连线位置：

```
(0, 0.5) = 左中
(1, 0.5) = 右中
(0.5, 0) = 上中
(0.5, 1) = 下中
```

示例：从节点底部出发，连接到目标节点顶部：

```xml
<mxCell style="edgeStyle=orthogonalEdgeStyle;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" source="a" target="b" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

### 避免交叉

- 调整节点位置使连线不交叉
- 使用 waypoint（中间点）引导连线绕行
- 对于无法避免交叉的情况，使用曲线 `curved=1`

### Waypoint 示例

```xml
<mxCell style="edgeStyle=orthogonalEdgeStyle;" edge="1" source="a" target="b" parent="1">
  <mxGeometry relative="1" as="geometry">
    <Array as="points">
      <mxPoint x="300" y="200" />
      <mxPoint x="300" y="400" />
    </Array>
  </mxGeometry>
</mxCell>
```

## 5. 多页面支持

一个 .drawio 文件可包含多个页面：

```xml
<mxfile host="app.diagrams.net" type="device">
  <diagram id="page-1" name="系统架构">
    <mxGraphModel ...>
      <root>...</root>
    </mxGraphModel>
  </diagram>
  <diagram id="page-2" name="数据流图">
    <mxGraphModel ...>
      <root>...</root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

## 6. 文本格式化

draw.io 支持在节点中使用 HTML 标签（需要 `html=1`）：

```xml
<!-- 多行文本 -->
<mxCell value="标题&lt;br&gt;&lt;font style=&quot;font-size:11px&quot;&gt;副标题&lt;/font&gt;" ... />

<!-- 换行使用 &#xa; -->
<mxCell value="第一行&#xa;第二行" ... />

<!-- 富文本 -->
<mxCell value="&lt;b&gt;粗体&lt;/b&gt;&lt;br&gt;&lt;i&gt;斜体&lt;/i&gt;" ... />
```

## 7. 画布尺寸参考

| 图表复杂度 | 推荐 pageWidth | 推荐 pageHeight |
|-----------|---------------|----------------|
| 简单（5-10 节点） | 1169 | 827 |
| 中等（10-30 节点） | 1169 | 827 |
| 复杂（30+ 节点） | 1600 | 1200 |
| 超大（多层架构） | 2000 | 1500 |

根据实际节点数量和层次深度调整画布尺寸，确保所有内容不超出边界。
