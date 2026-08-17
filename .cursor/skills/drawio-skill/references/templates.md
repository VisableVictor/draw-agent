# Draw.io 常用图表模板

本文件提供各类图表的 XML 模板片段，供生成 .drawio 文件时参考。所有模板均可直接嵌入 `<root>` 节点内使用。

## 配色模板使用说明

以下模板默认使用「经典柔和」配色。使用其他配色模板时，按 color-schemes.md 中的色值表替换对应节点的 `fillColor` 和 `strokeColor` 即可。替换规则：

1. **节点**：根据节点用途（用户/服务/数据/中间件/基础设施/外部系统），查找对应主题的填充色和边框色
2. **连线**：根据连线类型（主流程/异步/异常），查找对应主题的 strokeColor
3. **分组容器**：使用对应主题的分组容器色

常用主题快速替换表：

| 用途 | 经典柔和 fill/stroke | 科技蓝 fill/stroke | 商务暖 fill/stroke | 深色专业 fill/stroke |
|------|---------------------|-------------------|-------------------|---------------------|
| 用户/入口 | #d5e8d4/#82b366 | #e3f2fd/#1565c0 | #fff3e0/#e65100 | #c8e6c9/#2e7d32 |
| 应用/服务 | #dae8fc/#6c8ebf | #bbdefb/#1976d2 | #e3f2fd/#1976d2 | #bbdefb/#0d47a1 |
| 数据存储 | #fff2cc/#d6b656 | #e0f7fa/#00838f | #fce4b8/#c77700 | #ffe0b2/#e65100 |
| 中间件 | #e1d5e7/#9673a6 | #e8eaf6/#3949ab | #f3e5f5/#7b1fa2 | #d1c4e9/#4527a0 |
| 基础设施 | #f5f5f5/#666666 | #eceff1/#546e7a | #efebe9/#5d4037 | #cfd8dc/#37474f |
| 外部系统 | #f8cecc/#b85450 | #fce4ec/#c62828 | #ffebee/#c62828 | #ffcdd2/#b71c1c |
| 主连线 | #333333 | #0d47a1 | #333333 | #212121 |
| 虚线 | #999999 | #78909c | #999999 | #616161 |

## 1. 微服务架构图

三层结构：网关 → 服务集群 → 数据存储。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 用户 -->
<mxCell id="user-1" value="用户/客户端" style="shape=mxgraph.basic.person;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;fontFamily=system-ui;" vertex="1" parent="1">
  <mxGeometry x="460" y="20" width="80" height="60" as="geometry" />
</mxCell>

<!-- API Gateway -->
<mxCell id="gw-1" value="API Gateway" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="420" y="140" width="160" height="60" as="geometry" />
</mxCell>

<!-- 服务分组 -->
<mxCell id="svc-group" value="服务集群" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="260" width="800" height="160" as="geometry" />
</mxCell>

<!-- 微服务节点 -->
<mxCell id="svc-1" value="用户服务" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="svc-group">
  <mxGeometry x="20" y="50" width="140" height="60" as="geometry" />
</mxCell>
<mxCell id="svc-2" value="订单服务" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="svc-group">
  <mxGeometry x="200" y="50" width="140" height="60" as="geometry" />
</mxCell>
<mxCell id="svc-3" value="商品服务" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="svc-group">
  <mxGeometry x="380" y="50" width="140" height="60" as="geometry" />
</mxCell>
<mxCell id="svc-4" value="支付服务" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="svc-group">
  <mxGeometry x="560" y="50" width="140" height="60" as="geometry" />
</mxCell>

<!-- 中间件 -->
<mxCell id="mq-1" value="Kafka" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="420" y="480" width="160" height="60" as="geometry" />
</mxCell>

<!-- 数据层分组 -->
<mxCell id="data-group" value="数据层" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="600" width="800" height="140" as="geometry" />
</mxCell>
<mxCell id="db-1" value="MySQL" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;" vertex="1" parent="data-group">
  <mxGeometry x="60" y="40" width="120" height="80" as="geometry" />
</mxCell>
<mxCell id="db-2" value="Redis" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;" vertex="1" parent="data-group">
  <mxGeometry x="260" y="40" width="120" height="80" as="geometry" />
</mxCell>
<mxCell id="db-3" value="MongoDB" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;" vertex="1" parent="data-group">
  <mxGeometry x="460" y="40" width="120" height="80" as="geometry" />
</mxCell>
<mxCell id="db-4" value="OSS" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=13;" vertex="1" parent="data-group">
  <mxGeometry x="620" y="40" width="120" height="80" as="geometry" />
</mxCell>

<!-- 连线 -->
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="user-1" target="gw-1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="gw-1" target="svc-group" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;strokeColor=#999999;" edge="1" source="svc-group" target="mq-1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="svc-group" target="data-group" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 2. Kubernetes 部署架构图

展示 K8s 集群内的 Pod、Service、Ingress 关系。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 外部流量 -->
<mxCell id="ext-1" value="外部流量" style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="380" y="20" width="160" height="80" as="geometry" />
</mxCell>

<!-- Ingress -->
<mxCell id="ingress-1" value="Ingress Controller" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="370" y="150" width="180" height="50" as="geometry" />
</mxCell>

<!-- K8s Cluster -->
<mxCell id="k8s-cluster" value="Kubernetes Cluster" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=16;fillColor=#f5f5f5;strokeColor=#666666;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="60" y="250" width="800" height="450" as="geometry" />
</mxCell>

<!-- Namespace: production -->
<mxCell id="ns-prod" value="namespace: production" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=0;fontSize=12;fillColor=#ffffff;strokeColor=#6c8ebf;dashed=1;container=1;collapsible=0;fontFamily=monospace;" vertex="1" parent="k8s-cluster">
  <mxGeometry x="20" y="40" width="760" height="180" as="geometry" />
</mxCell>

<!-- Service + Pod -->
<mxCell id="svc-web" value="Service&#xa;web-svc" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="ns-prod">
  <mxGeometry x="20" y="40" width="120" height="50" as="geometry" />
</mxCell>
<mxCell id="pod-web-1" value="Pod: web-1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="ns-prod">
  <mxGeometry x="20" y="110" width="100" height="40" as="geometry" />
</mxCell>
<mxCell id="pod-web-2" value="Pod: web-2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="ns-prod">
  <mxGeometry x="140" y="110" width="100" height="40" as="geometry" />
</mxCell>

<mxCell id="svc-api" value="Service&#xa;api-svc" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="ns-prod">
  <mxGeometry x="300" y="40" width="120" height="50" as="geometry" />
</mxCell>
<mxCell id="pod-api-1" value="Pod: api-1" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="ns-prod">
  <mxGeometry x="280" y="110" width="100" height="40" as="geometry" />
</mxCell>
<mxCell id="pod-api-2" value="Pod: api-2" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="ns-prod">
  <mxGeometry x="400" y="110" width="100" height="40" as="geometry" />
</mxCell>

<!-- 数据库 Service -->
<mxCell id="svc-db" value="StatefulSet&#xa;MySQL" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="ns-prod">
  <mxGeometry x="590" y="40" width="120" height="80" as="geometry" />
</mxCell>

<!-- Monitoring namespace -->
<mxCell id="ns-monitor" value="namespace: monitoring" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=0;fontSize=12;fillColor=#ffffff;strokeColor=#9673a6;dashed=1;container=1;collapsible=0;fontFamily=monospace;" vertex="1" parent="k8s-cluster">
  <mxGeometry x="20" y="250" width="760" height="100" as="geometry" />
</mxCell>
<mxCell id="prom" value="Prometheus" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="ns-monitor">
  <mxGeometry x="40" y="35" width="130" height="45" as="geometry" />
</mxCell>
<mxCell id="grafana" value="Grafana" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="ns-monitor">
  <mxGeometry x="220" y="35" width="130" height="45" as="geometry" />
</mxCell>

<!-- 连线 -->
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="ext-1" target="ingress-1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="ingress-1" target="k8s-cluster" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 3. 业务流程图（左右流向）

从左到右展示业务处理流程。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 起始 -->
<mxCell id="start" value="开始" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="40" y="180" width="80" height="60" as="geometry" />
</mxCell>

<!-- 处理步骤 -->
<mxCell id="step-1" value="提交订单" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="180" y="180" width="140" height="60" as="geometry" />
</mxCell>

<!-- 判断节点 -->
<mxCell id="decision-1" value="库存充足？" style="rhombus;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="380" y="165" width="120" height="90" as="geometry" />
</mxCell>

<!-- 是 -->
<mxCell id="step-2" value="扣减库存" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="560" y="120" width="140" height="60" as="geometry" />
</mxCell>

<!-- 否 -->
<mxCell id="step-3" value="通知缺货" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="560" y="240" width="140" height="60" as="geometry" />
</mxCell>

<!-- 支付 -->
<mxCell id="step-4" value="发起支付" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="760" y="120" width="140" height="60" as="geometry" />
</mxCell>

<!-- 结束 -->
<mxCell id="end" value="结束" style="ellipse;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="960" y="180" width="80" height="60" as="geometry" />
</mxCell>

<!-- 连线 -->
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="start" target="step-1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="step-1" target="decision-1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e3" value="是" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333;fontSize=11;" edge="1" source="decision-1" target="step-2" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e4" value="否" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333;fontSize=11;" edge="1" source="decision-1" target="step-3" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="step-2" target="step-4" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e6" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="step-4" target="end" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e7" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#999;dashed=1;" edge="1" source="step-3" target="end" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 4. 云架构图（阿里云/AWS 风格）

分层展示云上部署架构。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- CDN/DNS 入口 -->
<mxCell id="cdn" value="CDN / DNS" style="ellipse;shape=cloud;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="380" y="20" width="160" height="80" as="geometry" />
</mxCell>

<!-- 负载均衡 -->
<mxCell id="slb" value="SLB / NLB" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="380" y="150" width="160" height="50" as="geometry" />
</mxCell>

<!-- 计算层 -->
<mxCell id="compute-group" value="计算层" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="260" width="720" height="120" as="geometry" />
</mxCell>
<mxCell id="ecs-1" value="ECS / ACK&#xa;应用集群" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="compute-group">
  <mxGeometry x="30" y="40" width="140" height="60" as="geometry" />
</mxCell>
<mxCell id="ecs-2" value="FC&#xa;函数计算" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="compute-group">
  <mxGeometry x="220" y="40" width="140" height="60" as="geometry" />
</mxCell>
<mxCell id="ecs-3" value="SAE&#xa;应用引擎" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="compute-group">
  <mxGeometry x="410" y="40" width="140" height="60" as="geometry" />
</mxCell>

<!-- 中间件层 -->
<mxCell id="mid-group" value="中间件层" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="430" width="720" height="100" as="geometry" />
</mxCell>
<mxCell id="mq" value="RocketMQ" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="mid-group">
  <mxGeometry x="30" y="40" width="130" height="45" as="geometry" />
</mxCell>
<mxCell id="redis" value="Redis" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="mid-group">
  <mxGeometry x="200" y="40" width="130" height="45" as="geometry" />
</mxCell>
<mxCell id="es" value="Elasticsearch" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="mid-group">
  <mxGeometry x="370" y="40" width="130" height="45" as="geometry" />
</mxCell>

<!-- 数据层 -->
<mxCell id="data-group" value="数据层" style="rounded=0;whiteSpace=wrap;html=1;verticalAlign=top;fontStyle=1;fontSize=14;fillColor=#f5f5f5;strokeColor=#666666;dashed=1;container=1;collapsible=0;" vertex="1" parent="1">
  <mxGeometry x="100" y="580" width="720" height="120" as="geometry" />
</mxCell>
<mxCell id="rds" value="RDS MySQL" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="data-group">
  <mxGeometry x="50" y="30" width="120" height="75" as="geometry" />
</mxCell>
<mxCell id="oss" value="OSS" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="data-group">
  <mxGeometry x="240" y="30" width="120" height="75" as="geometry" />
</mxCell>
<mxCell id="dw" value="MaxCompute" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="data-group">
  <mxGeometry x="430" y="30" width="120" height="75" as="geometry" />
</mxCell>

<!-- 连线 -->
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="cdn" target="slb" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="slb" target="compute-group" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="compute-group" target="mid-group" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="compute-group" target="data-group" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 5. 泳道图模板

按角色划分的跨部门流程。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 泳道：用户 -->
<mxCell id="lane-user" value="用户" style="shape=table;startSize=40;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;fontSize=14;fillColor=#d5e8d4;strokeColor=#82b366;horizontal=0;" vertex="1" parent="1">
  <mxGeometry x="40" y="40" width="800" height="120" as="geometry" />
</mxCell>

<!-- 泳道：前端 -->
<mxCell id="lane-fe" value="前端" style="shape=table;startSize=40;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;fontSize=14;fillColor=#dae8fc;strokeColor=#6c8ebf;horizontal=0;" vertex="1" parent="1">
  <mxGeometry x="40" y="160" width="800" height="120" as="geometry" />
</mxCell>

<!-- 泳道：后端 -->
<mxCell id="lane-be" value="后端" style="shape=table;startSize=40;container=1;collapsible=0;childLayout=tableLayout;fixedRows=1;rowLines=0;fontStyle=1;fontSize=14;fillColor=#fff2cc;strokeColor=#d6b656;horizontal=0;" vertex="1" parent="1">
  <mxGeometry x="40" y="280" width="800" height="120" as="geometry" />
</mxCell>

<!-- 节点示例（放在各自的泳道内，坐标相对于泳道容器） -->
<mxCell id="u1" value="提交表单" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#82b366;fontSize=12;" vertex="1" parent="lane-user">
  <mxGeometry x="80" y="35" width="120" height="45" as="geometry" />
</mxCell>
<mxCell id="f1" value="表单校验" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="lane-fe">
  <mxGeometry x="260" y="35" width="120" height="45" as="geometry" />
</mxCell>
<mxCell id="b1" value="处理请求" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="lane-be">
  <mxGeometry x="460" y="35" width="120" height="45" as="geometry" />
</mxCell>

<!-- 连线 -->
<mxCell id="e1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333333;" edge="1" source="u1" target="f1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
<mxCell id="e2" value="API 调用" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=#333;fontSize=11;" edge="1" source="f1" target="b1" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 6. 组织架构图（树形）

自上而下展示汇报层级。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 顶层 -->
<mxCell id="ceo" value="总经理" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="420" y="40" width="140" height="50" as="geometry" />
</mxCell>

<!-- 第二层 -->
<mxCell id="vp1" value="技术部" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="200" y="160" width="130" height="45" as="geometry" />
</mxCell>
<mxCell id="vp2" value="产品部" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="425" y="160" width="130" height="45" as="geometry" />
</mxCell>
<mxCell id="vp3" value="运营部" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="650" y="160" width="130" height="45" as="geometry" />
</mxCell>

<!-- 第三层（技术部下属） -->
<mxCell id="t1" value="前端组" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
  <mxGeometry x="130" y="270" width="110" height="40" as="geometry" />
</mxCell>
<mxCell id="t2" value="后端组" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1">
  <mxGeometry x="260" y="270" width="110" height="40" as="geometry" />
</mxCell>

<!-- 连线（树形使用 tree 边样式） -->
<mxCell id="oe1" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;strokeColor=#333333;" edge="1" source="ceo" target="vp1" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="oe2" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;strokeColor=#333333;" edge="1" source="ceo" target="vp2" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="oe3" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;strokeColor=#333333;" edge="1" source="ceo" target="vp3" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="oe4" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;strokeColor=#333333;" edge="1" source="vp1" target="t1" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="oe5" style="edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;exitX=0.5;exitY=1;entryX=0.5;entryY=0;strokeColor=#333333;" edge="1" source="vp1" target="t2" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
```

## 7. 思维导图（放射布局）

中心主题向四周放射展开，一级分支用曲线连接。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 中心主题 -->
<mxCell id="center" value="产品规划" style="ellipse;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=15;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="400" y="260" width="140" height="80" as="geometry" />
</mxCell>

<!-- 一级分支（四个方向） -->
<mxCell id="b1" value="用户研究" style="rounded=1;whiteSpace=wrap;html=1;arcSize=40;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="140" y="120" width="120" height="45" as="geometry" />
</mxCell>
<mxCell id="b2" value="功能设计" style="rounded=1;whiteSpace=wrap;html=1;arcSize=40;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="680" y="120" width="120" height="45" as="geometry" />
</mxCell>
<mxCell id="b3" value="技术方案" style="rounded=1;whiteSpace=wrap;html=1;arcSize=40;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="140" y="430" width="120" height="45" as="geometry" />
</mxCell>
<mxCell id="b4" value="上线运营" style="rounded=1;whiteSpace=wrap;html=1;arcSize=40;fillColor=#f8cecc;strokeColor=#b85450;fontSize=12;" vertex="1" parent="1">
  <mxGeometry x="680" y="430" width="120" height="45" as="geometry" />
</mxCell>

<!-- 二级分支示例 -->
<mxCell id="b1a" value="访谈" style="text;html=1;fillColor=none;strokeColor=none;fontSize=11;fontColor=#82b366;" vertex="1" parent="1">
  <mxGeometry x="60" y="70" width="70" height="20" as="geometry" />
</mxCell>
<mxCell id="b1b" value="问卷" style="text;html=1;fillColor=none;strokeColor=none;fontSize=11;fontColor=#82b366;" vertex="1" parent="1">
  <mxGeometry x="60" y="170" width="70" height="20" as="geometry" />
</mxCell>

<!-- 曲线连接 -->
<mxCell id="me1" style="edgeStyle=none;curved=1;html=1;strokeColor=#82b366;strokeWidth=2;endArrow=none;" edge="1" source="center" target="b1" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="me2" style="edgeStyle=none;curved=1;html=1;strokeColor=#d6b656;strokeWidth=2;endArrow=none;" edge="1" source="center" target="b2" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="me3" style="edgeStyle=none;curved=1;html=1;strokeColor=#9673a6;strokeWidth=2;endArrow=none;" edge="1" source="center" target="b3" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="me4" style="edgeStyle=none;curved=1;html=1;strokeColor=#b85450;strokeWidth=2;endArrow=none;" edge="1" source="center" target="b4" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="me5" style="edgeStyle=none;curved=1;html=1;strokeColor=#82b366;endArrow=none;" edge="1" source="b1" target="b1a" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="me6" style="edgeStyle=none;curved=1;html=1;strokeColor=#82b366;endArrow=none;" edge="1" source="b1" target="b1b" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
```

## 8. 时间线 / 路线图（水平时间轴）

事件卡片沿水平主轴上下交替排列。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 主轴 -->
<mxCell id="axis" style="endArrow=classic;html=1;strokeColor=#6c8ebf;strokeWidth=3;" edge="1" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="60" y="280" as="sourcePoint" />
    <mxPoint x="900" y="280" as="targetPoint" />
  </mxGeometry>
</mxCell>

<!-- 时间点圆点 -->
<mxCell id="p1" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=#6c8ebf;strokeColor=#6c8ebf;" vertex="1" parent="1"><mxGeometry x="155" y="272" width="16" height="16" as="geometry" /></mxCell>
<mxCell id="p2" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=#82b366;strokeColor=#82b366;" vertex="1" parent="1"><mxGeometry x="365" y="272" width="16" height="16" as="geometry" /></mxCell>
<mxCell id="p3" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=#d6b656;strokeColor=#d6b656;" vertex="1" parent="1"><mxGeometry x="575" y="272" width="16" height="16" as="geometry" /></mxCell>
<mxCell id="p4" value="" style="ellipse;whiteSpace=wrap;html=1;fillColor=#9673a6;strokeColor=#9673a6;" vertex="1" parent="1"><mxGeometry x="785" y="272" width="16" height="16" as="geometry" /></mxCell>

<!-- 事件卡片（上下交替） -->
<mxCell id="c1" value="Q1 需求调研&#xa;完成用户访谈" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=11;" vertex="1" parent="1"><mxGeometry x="100" y="150" width="130" height="60" as="geometry" /></mxCell>
<mxCell id="c2" value="Q2 产品设计&#xa;交互与视觉定稿" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=11;" vertex="1" parent="1"><mxGeometry x="310" y="350" width="130" height="60" as="geometry" /></mxCell>
<mxCell id="c3" value="Q3 研发上线&#xa;核心功能发布" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=11;" vertex="1" parent="1"><mxGeometry x="520" y="150" width="130" height="60" as="geometry" /></mxCell>
<mxCell id="c4" value="Q4 迭代运营&#xa;数据复盘优化" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=11;" vertex="1" parent="1"><mxGeometry x="730" y="350" width="130" height="60" as="geometry" /></mxCell>

<!-- 卡片到时间点的连线 -->
<mxCell id="l1" style="html=1;strokeColor=#6c8ebf;dashed=1;endArrow=none;" edge="1" source="c1" target="p1" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="l2" style="html=1;strokeColor=#82b366;dashed=1;endArrow=none;" edge="1" source="c2" target="p2" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="l3" style="html=1;strokeColor=#d6b656;dashed=1;endArrow=none;" edge="1" source="c3" target="p3" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
<mxCell id="l4" style="html=1;strokeColor=#9673a6;dashed=1;endArrow=none;" edge="1" source="c4" target="p4" parent="1"><mxGeometry relative="1" as="geometry" /></mxCell>
```

## 9. 四象限图（优先级矩阵）

以十字轴划分四个象限，元素按语义落位。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 四象限背景 -->
<mxCell id="q1" value="" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;opacity=40;" vertex="1" parent="1"><mxGeometry x="440" y="80" width="360" height="230" as="geometry" /></mxCell>
<mxCell id="q2" value="" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;opacity=40;" vertex="1" parent="1"><mxGeometry x="80" y="80" width="360" height="230" as="geometry" /></mxCell>
<mxCell id="q3" value="" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;opacity=40;" vertex="1" parent="1"><mxGeometry x="80" y="310" width="360" height="230" as="geometry" /></mxCell>
<mxCell id="q4" value="" style="rounded=0;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;opacity=40;" vertex="1" parent="1"><mxGeometry x="440" y="310" width="360" height="230" as="geometry" /></mxCell>

<!-- 象限标题 -->
<mxCell id="qt1" value="重要 &amp; 紧急&#xa;立即做" style="text;html=1;fontSize=13;fontStyle=1;fontColor=#2e7d32;align=center;" vertex="1" parent="1"><mxGeometry x="540" y="90" width="160" height="40" as="geometry" /></mxCell>
<mxCell id="qt2" value="重要 &amp; 不紧急&#xa;计划做" style="text;html=1;fontSize=13;fontStyle=1;fontColor=#c77700;align=center;" vertex="1" parent="1"><mxGeometry x="180" y="90" width="160" height="40" as="geometry" /></mxCell>
<mxCell id="qt3" value="不重要 &amp; 不紧急&#xa;不做" style="text;html=1;fontSize=13;fontStyle=1;fontColor=#b85450;align=center;" vertex="1" parent="1"><mxGeometry x="180" y="490" width="160" height="40" as="geometry" /></mxCell>
<mxCell id="qt4" value="不重要 &amp; 紧急&#xa;委托做" style="text;html=1;fontSize=13;fontStyle=1;fontColor=#1976d2;align=center;" vertex="1" parent="1"><mxGeometry x="540" y="490" width="160" height="40" as="geometry" /></mxCell>

<!-- 坐标轴 -->
<mxCell id="ax" style="endArrow=classic;html=1;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="80" y="310" as="sourcePoint" /><mxPoint x="820" y="310" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="ay" style="endArrow=classic;html=1;strokeColor=#333333;strokeWidth=2;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="440" y="540" as="sourcePoint" /><mxPoint x="440" y="60" as="targetPoint" /></mxGeometry></mxCell>

<!-- 轴标签 -->
<mxCell id="axl" value="紧急程度 →" style="text;html=1;fontSize=11;fontColor=#666666;" vertex="1" parent="1"><mxGeometry x="720" y="315" width="90" height="20" as="geometry" /></mxCell>
<mxCell id="ayl" value="↑ 重要程度" style="text;html=1;fontSize=11;fontColor=#666666;" vertex="1" parent="1"><mxGeometry x="450" y="60" width="90" height="20" as="geometry" /></mxCell>

<!-- 示例条目 -->
<mxCell id="i1" value="线上故障" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#2e7d32;fontSize=11;" vertex="1" parent="1"><mxGeometry x="560" y="160" width="100" height="35" as="geometry" /></mxCell>
<mxCell id="i2" value="能力建设" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#c77700;fontSize=11;" vertex="1" parent="1"><mxGeometry x="200" y="160" width="100" height="35" as="geometry" /></mxCell>
```

## 10. 鱼骨图（因果分析图）

水平主干指向"问题"，主要原因作为斜向肋骨引出。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 问题（头部） -->
<mxCell id="head" value="转化率下降" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#f8cecc;strokeColor=#b85450;fontSize=13;fontStyle=1;" vertex="1" parent="1">
  <mxGeometry x="800" y="255" width="140" height="60" as="geometry" />
</mxCell>

<!-- 主干 -->
<mxCell id="spine" style="endArrow=classic;html=1;strokeColor=#333333;strokeWidth=3;" edge="1" target="head" parent="1">
  <mxGeometry relative="1" as="geometry">
    <mxPoint x="80" y="285" as="sourcePoint" />
  </mxGeometry>
</mxCell>

<!-- 上侧主因 -->
<mxCell id="c1" value="产品因素" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1"><mxGeometry x="200" y="80" width="110" height="40" as="geometry" /></mxCell>
<mxCell id="c2" value="价格因素" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;" vertex="1" parent="1"><mxGeometry x="480" y="80" width="110" height="40" as="geometry" /></mxCell>

<!-- 下侧主因 -->
<mxCell id="c3" value="渠道因素" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1"><mxGeometry x="200" y="450" width="110" height="40" as="geometry" /></mxCell>
<mxCell id="c4" value="服务因素" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;" vertex="1" parent="1"><mxGeometry x="480" y="450" width="110" height="40" as="geometry" /></mxCell>

<!-- 肋骨（斜向连到主干） -->
<mxCell id="r1" style="html=1;endArrow=classic;strokeColor=#6c8ebf;" edge="1" source="c1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="330" y="285" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="r2" style="html=1;endArrow=classic;strokeColor=#6c8ebf;" edge="1" source="c2" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="610" y="285" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="r3" style="html=1;endArrow=classic;strokeColor=#82b366;" edge="1" source="c3" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="330" y="285" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="r4" style="html=1;endArrow=classic;strokeColor=#82b366;" edge="1" source="c4" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="610" y="285" as="targetPoint" /></mxGeometry></mxCell>
```

## 11. 时序图（Sequence Diagram）

展示对象间按时间顺序的消息交互。使用垂直生命线 + 水平消息箭头。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 参与者头部 -->
<mxCell id="a1" value="用户" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#d5e8d4;strokeColor=#82b366;fontSize=12;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="80" y="40" width="100" height="40" as="geometry" /></mxCell>
<mxCell id="a2" value="前端" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#dae8fc;strokeColor=#6c8ebf;fontSize=12;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="300" y="40" width="100" height="40" as="geometry" /></mxCell>
<mxCell id="a3" value="后端" style="rounded=1;whiteSpace=wrap;html=1;fillColor=#fff2cc;strokeColor=#d6b656;fontSize=12;fontStyle=1;" vertex="1" parent="1"><mxGeometry x="520" y="40" width="100" height="40" as="geometry" /></mxCell>
<mxCell id="a4" value="数据库" style="shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=10;fillColor=#e1d5e7;strokeColor=#9673a6;fontSize=12;" vertex="1" parent="1"><mxGeometry x="740" y="35" width="90" height="50" as="geometry" /></mxCell>

<!-- 生命线（虚线） -->
<mxCell id="ll1" style="html=1;endArrow=none;dashed=1;strokeColor=#999999;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="130" y="80" as="sourcePoint" /><mxPoint x="130" y="500" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="ll2" style="html=1;endArrow=none;dashed=1;strokeColor=#999999;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="350" y="80" as="sourcePoint" /><mxPoint x="350" y="500" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="ll3" style="html=1;endArrow=none;dashed=1;strokeColor=#999999;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="570" y="80" as="sourcePoint" /><mxPoint x="570" y="500" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="ll4" style="html=1;endArrow=none;dashed=1;strokeColor=#999999;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="785" y="85" as="sourcePoint" /><mxPoint x="785" y="500" as="targetPoint" /></mxGeometry></mxCell>

<!-- 消息（水平箭头，从上到下） -->
<mxCell id="m1" value="点击提交" style="html=1;endArrow=classic;strokeColor=#333333;fontSize=11;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="130" y="130" as="sourcePoint" /><mxPoint x="350" y="130" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="m2" value="POST /api/order" style="html=1;endArrow=classic;strokeColor=#333333;fontSize=11;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="350" y="190" as="sourcePoint" /><mxPoint x="570" y="190" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="m3" value="INSERT 订单" style="html=1;endArrow=classic;strokeColor=#333333;fontSize=11;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="570" y="250" as="sourcePoint" /><mxPoint x="785" y="250" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="m4" value="返回结果" style="html=1;endArrow=open;dashed=1;strokeColor=#999999;fontSize=11;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="785" y="310" as="sourcePoint" /><mxPoint x="570" y="310" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="m5" value="200 OK" style="html=1;endArrow=open;dashed=1;strokeColor=#999999;fontSize=11;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="570" y="370" as="sourcePoint" /><mxPoint x="350" y="370" as="targetPoint" /></mxGeometry></mxCell>
<mxCell id="m6" value="提示成功" style="html=1;endArrow=open;dashed=1;strokeColor=#999999;fontSize=11;" edge="1" parent="1"><mxGeometry relative="1" as="geometry"><mxPoint x="350" y="430" as="sourcePoint" /><mxPoint x="130" y="430" as="targetPoint" /></mxGeometry></mxCell>
```

## 12. ER 图（实体关系图）

展示数据实体及其字段与关系。

```xml
<mxCell id="0" />
<mxCell id="1" parent="0" />

<!-- 实体：用户 -->
<mxCell id="ent-user" value="用户 (User)" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=30;fillColor=#dae8fc;strokeColor=#6c8ebf;horizontalStack=0;resizeParent=1;resizeParentMax=0;collapsible=0;marginBottom=0;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="120" y="80" width="200" height="120" as="geometry" />
</mxCell>
<mxCell id="uf1" value="id (PK)" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;" vertex="1" parent="ent-user"><mxGeometry y="30" width="200" height="30" as="geometry" /></mxCell>
<mxCell id="uf2" value="name" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;" vertex="1" parent="ent-user"><mxGeometry y="60" width="200" height="30" as="geometry" /></mxCell>
<mxCell id="uf3" value="email" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;" vertex="1" parent="ent-user"><mxGeometry y="90" width="200" height="30" as="geometry" /></mxCell>

<!-- 实体：订单 -->
<mxCell id="ent-order" value="订单 (Order)" style="swimlane;fontStyle=1;align=center;verticalAlign=top;childLayout=stackLayout;horizontal=1;startSize=30;fillColor=#fff2cc;strokeColor=#d6b656;horizontalStack=0;resizeParent=1;resizeParentMax=0;collapsible=0;marginBottom=0;fontSize=13;" vertex="1" parent="1">
  <mxGeometry x="560" y="80" width="200" height="150" as="geometry" />
</mxCell>
<mxCell id="of1" value="id (PK)" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;" vertex="1" parent="ent-order"><mxGeometry y="30" width="200" height="30" as="geometry" /></mxCell>
<mxCell id="of2" value="user_id (FK)" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;" vertex="1" parent="ent-order"><mxGeometry y="60" width="200" height="30" as="geometry" /></mxCell>
<mxCell id="of3" value="amount" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;" vertex="1" parent="ent-order"><mxGeometry y="90" width="200" height="30" as="geometry" /></mxCell>
<mxCell id="of4" value="created_at" style="text;html=1;align=left;verticalAlign=middle;spacingLeft=8;fontSize=12;" vertex="1" parent="ent-order"><mxGeometry y="120" width="200" height="30" as="geometry" /></mxCell>

<!-- 关系（1:N） -->
<mxCell id="rel" value="1 : N" style="edgeStyle=entityRelationEdgeStyle;fontSize=11;html=1;endArrow=ERmany;startArrow=ERone;strokeColor=#333333;" edge="1" source="ent-user" target="ent-order" parent="1">
  <mxGeometry relative="1" as="geometry" />
</mxCell>
```

## 使用说明

以上模板覆盖技术类（架构、部署、云、时序、ER）与业务/通用类（流程、泳道、组织架构、思维导图、时间线、象限、鱼骨）图表，提供坐标、样式、分组的参考范例。生成实际图表时：

1. 根据用户需求选择最接近的模板类型（技术图或业务/通用图）
2. 调整节点数量、名称和位置坐标
3. 修改连线关系与层级结构以匹配实际内容
4. 保持颜色方案一致性（参照 color-schemes.md 中的配色表）
5. 根据内容多少调整容器和画布尺寸
