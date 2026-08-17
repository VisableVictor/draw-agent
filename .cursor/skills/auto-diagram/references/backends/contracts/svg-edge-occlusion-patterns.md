# SVG Edge Occlusion Patterns

这份文档不是新的后端 contract，而是 `SVG-first` 在遇到复杂长箭头时的补充执行模板。

目标只有一个：

- 当反馈线、控制线、例外线已经把绕线成本拉得过高时，给 backend 一个可直接照着落坐标和层级的 few-shot

## 什么时候该用

优先满足下面三个条件，才考虑 `under-node`：

- 主路径已经清楚，额外长边只是辅助说明，不是观众第一眼要追的主干
- 如果继续靠多次拐弯来避让，会显著拉长线长、压缩留白或制造更多视觉噪音
- 用颜色通道就能把它与主路径、相邻长边肉眼区分开

下面这些情况不要用：

- 主链路主干箭头
- 需要靠标签或大段说明才能看懂的边
- 会穿过标题区、说明卡、摘要卡、edge label 的边
- 只是因为懒得重排布局就想让所有线都走砖块下面

## 默认判断顺序

遇到复杂长边时，backend 默认按这个顺序做决策：

1. 先检查能否通过扩通道、调锚点、减少非必要节点，让线走正常外部通道
2. 再检查能否通过颜色分层，减少“必须几何隔离”的压力
3. 仍然拥挤时，再把最长的一两条辅助边改成 `under-node`
4. 最后重新检查主舞台和分组有没有出现新的空跑带

## 颜色通道建议

推荐把长边通道稳定映射到少量语义颜色，而不是每张图重新发明。

建议优先级：

- `primary`：默认主链边，维持主题包默认边色
- `feedback`：高对比冷色或亮色，强调“回流”
- `control`：与主链明显区分的暖色或高饱和强调色
- `exception`：更警示的强调色，用于异常、告警、补偿
- `sync` / `async`：只有确实要区分同步异步时才加，不要平白增加图例负担

约束：

- 同一张图里，`feedback` / `control` / `exception` 至少要与 `primary` 保持肉眼可辨差异
- 颜色是辅助识别，不是替代几何；锚点进出方向仍要清晰
- 同一语义通道在同一张图里尽量保持一致，不要一会儿蓝一会儿橙

## 绘制顺序

`under-node` 是否看起来合理，核心不只在路径，还在 SVG 绘制顺序。

推荐顺序：

1. 背景、舞台、分组底板
2. `under-node` 长箭头主干
3. 普通箭头
4. 主节点砖块和子砖块
5. 节点文字
6. edge label、说明卡、摘要卡、图例

要点：

- 节点填充层要晚于 `under-node` 边绘制，这样砖块才能把中间那段箭头主干盖住
- `edge label` 仍应独立落在无遮挡通道，不要跟着一起放到砖块下面
- 如果一条 `under-node` 边需要跨多个节点，只允许中间主干被遮挡；起点、终点和转折判断点必须暴露在外部通道
- 如果当前任务尤其依赖质量脚本去检查“是否穿砖”，优先把这类长边写成 `M / L / H / V` 正交段；曲线可以更顺，但会降低现有闸门的可验证性

## Good Pattern

下面这个模式适合“左到右主链路 + 一条跨组反馈线 + 一条控制线”的汇报图：

```xml
<g class="ad-stage" data-stage-id="main-stage">
  <rect class="ad-stage-box" x="64" y="188" width="1480" height="620" rx="28"/>
</g>

<path
  class="ad-edge ad-edge-underlay"
  data-edge-id="feedback-risk-loop"
  data-edge-channel="feedback"
  data-edge-occlusion="under-node"
  d="M1260 650 C1080 650 1040 458 860 458 C720 458 690 650 520 650"
/>

<path
  class="ad-edge"
  data-edge-id="control-dispatch"
  data-edge-channel="control"
  d="M980 356 C1100 356 1160 320 1280 320"
/>

<g class="ad-node" data-node-id="order-intake" data-stage-id="main-stage">
  <rect class="ad-node-box" x="180" y="280" width="250" height="120" rx="18"/>
  <text class="ad-node-title" x="305" y="326" text-anchor="middle">订单接入</text>
</g>

<g class="ad-node" data-node-id="routing" data-stage-id="main-stage">
  <rect class="ad-node-box" x="520" y="280" width="250" height="120" rx="18"/>
  <text class="ad-node-title" x="645" y="326" text-anchor="middle">智能路由</text>
</g>

<g class="ad-node" data-node-id="dispatch" data-stage-id="main-stage">
  <rect class="ad-node-box" x="860" y="280" width="250" height="120" rx="18"/>
  <text class="ad-node-title" x="985" y="326" text-anchor="middle">波次调度</text>
</g>

<g class="ad-node" data-node-id="delivery" data-stage-id="main-stage">
  <rect class="ad-node-box" x="1200" y="280" width="250" height="120" rx="18"/>
  <text class="ad-node-title" x="1325" y="326" text-anchor="middle">履约配送</text>
</g>

<text class="ad-edge-label" x="1030" y="622">风险回流 / 逆向补偿</text>
<text class="ad-edge-label" x="1128" y="300">调度控制</text>
```

为什么这是好模式：

- 主链仍然可以走上方清晰通道，`under-node` 只承担辅助反馈
- 被遮挡的是反馈线中段，而不是锚点和终点
- `feedback` 和 `control` 通过颜色通道区分，避免继续堆拐弯
- 标签都落在外部通道，没有压进节点或标题区

## Bad Pattern

下面这些属于不允许的坏模式：

```xml
<!-- Bad 1: 主链路直接穿砖 -->
<path
  class="ad-edge ad-edge-underlay"
  data-edge-channel="primary"
  data-edge-occlusion="under-node"
  d="M180 340 L1320 340"
/>

<!-- Bad 2: 标签和边一起塞到砖块下面 -->
<text class="ad-edge-label" x="850" y="340">主链路</text>

<!-- Bad 3: 说明卡也压在线上方，试图一起“遮挡” -->
<rect class="ad-note-box" x="760" y="250" width="220" height="120" rx="20"/>
```

为什么不行：

- `primary` 主链不应该靠 `under-node` 穿过一串节点来维持连通
- `ad-edge-label` 绝不允许跟着进入遮挡区
- 说明卡、摘要卡、标题区都不是可遮挡层

## Backend Few-Shot Checklist

当 backend 准备生成复杂长边时，默认逐条自问：

1. 这条边是不是辅助关系，而不是主叙事主干？
2. 如果不用 `under-node`，是否还能通过重排布局解决？
3. 这条边是否已经分配了稳定的 `data-edge-channel`？
4. 这条边是否显式加了 `class="ad-edge ad-edge-underlay"` 和 `data-edge-occlusion="under-node"`？
5. 节点、文字、标签的绘制顺序，是否真的会让“只遮主干、不遮文字”成立？
6. 被遮挡的是否仅为中间长段，而不是整条线都在砖块下失联？
7. 这条边是否会诱发新的右侧/底部大空带，需要回头调整布局？

## 推荐配套质检

- `python3 scripts/quality/lint-svg-diagram.py <svg-file>`
- `python3 scripts/quality/check-layout-rhythm.py <svg-file>`
- 如需对外导出 PNG，再补：
  - `bash scripts/export/export-diagram.sh <svg-file> [png-width]`

## 回归样例

可直接参考：

- `assets/regression/under-node-edge-pattern-good.svg`

如果要新增变体，优先沿用这份样例的图层顺序、数据属性和颜色通道命名。
