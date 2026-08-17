# Cloud Domain Pack

适用于 AWS、Azure、GCP、Alibaba Cloud、Kubernetes 等云架构图。

## 进入信号

- 用户要求云厂商图标
- 需求里出现 VPC、Subnet、LB、API Gateway、Lambda、RDS、K8s 等对象
- 需要更专业的云基础设施表达

## 表达原则

- 优先表现边界、入口、核心服务、数据与网络关系
- Provider icons 用来增强识别，不要把图做成图标海
- 云架构图既可以是正式部署图，也可以是高层总览图，先分清目标

## 常见主轴

- 请求流主轴
- 控制面 / 数据面
- 公网入口到私网服务链路
- 跨区域 / 跨账号 / 跨 VPC 拓扑

## 默认建议

- 技术评审：优先正式云图
- 管理汇报：优先 `SVG 总览图`，必要时补 provider 图版
