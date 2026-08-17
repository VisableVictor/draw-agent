# Cloud Example: Kubernetes Platform

适用于：

- 云平台部署图
- K8s 架构
- 请求入口到服务与数据的主链路

```plantuml
@startuml
title SaaS Platform on Kubernetes

mxgraph.kubernetes.ing "Ingress" as ing
mxgraph.kubernetes.svc "API Service" as svc
mxgraph.kubernetes.deploy "Order Deployment" as deploy
mxgraph.kubernetes.pod "Order Pod" as pod
mxgraph.aws4.rds "Postgres" as rds
mxgraph.aws4.elasticache "Redis" as redis

ing --> svc
svc --> deploy
deploy --> pod
pod --> rds
pod --> redis
@enduml
```

要点：

- 图标帮助识别，但不要图标堆满
- 适合讲部署关系，不适合讲复杂业务叙事
