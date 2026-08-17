# Draw.io 常用节点样式速查

本文件收录各类节点的 draw.io 样式串，可直接复制到 mxCell 的 `style` 属性中。以下示例以「经典柔和」为默认主题；使用其他主题时，替换对应的 `fillColor` 和 `strokeColor` 即可（色值见 [color-schemes.md](color-schemes.md)）。

```
# 圆角矩形（通用服务）
# 经典柔和:
rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;
# 科技蓝:
rounded=1;whiteSpace=wrap;html=1;fillColor=#bbdefb;strokeColor=#1976d2;fontSize=13;
# 深色专业:
rounded=1;whiteSpace=wrap;html=1;fillColor=#bbdefb;strokeColor=#0d47a1;fontSize=13;

# 数据库
shape=mxgraph.flowchart.database;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;

# 圆柱体（数据存储）
# 经典柔和:
shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;
# 科技蓝:
shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#e0f7fa;strokeColor=#00838f;fontSize=13;
# 深色专业:
shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#ffe0b2;strokeColor=#e65100;fontSize=13;

# 云形状
# 经典柔和:
ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=13;
# 科技蓝:
ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#eceff1;strokeColor=#546e7a;fontSize=13;

# 菱形（决策）
rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;

# 人形图标（用户）
# 经典柔和:
shape=mxgraph.basic.person;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;
# 科技蓝:
shape=mxgraph.basic.person;fillColor=#e3f2fd;strokeColor=#1565c0;fontSize=13;

# 文档形状
shape=mxgraph.flowchart.document;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;

# 六边形（微服务）
# 经典柔和:
shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;
# 科技蓝:
shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=1;fixedSize=1;fillColor=#bbdefb;strokeColor=#1976d2;fontSize=13;

# 椭圆/圆（流程起止、思维导图中心主题）
ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;

# 圆角卡片（任务、想法、看板卡片）
rounded=1;whiteSpace=wrap;html=1;arcSize=20;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;

# 便签/贴纸（亲和图、批注）
shape=note;whiteSpace=wrap;html=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;

# 标注气泡（说明、旁注）
shape=callout;whiteSpace=wrap;html=1;perimeter=calloutPerimeter;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;

# 平行四边形（输入/输出）
shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=1;fixedSize=1;size=20;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;

# 纯文本标签（标题、象限名、时间点）
text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;fontSize=12;fontColor=#333333;

# 圆点（思维导图叶节点、象限散点）
ellipse;whiteSpace=wrap;html=1;fillColor=#6c8ebf;strokeColor=#6c8ebf;fontSize=1;
```
