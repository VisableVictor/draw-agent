# Design Quality System

`auto-diagram` 的质检分三层，不再只看“有没有硬错误”。

注意：

- 这套系统默认是 **内部驱动**，不是用户交付物
- 用户默认不应该看到原始 `WARNING` / `DESIGN_HINT` / 评分明细
- skill 应该把这些结果转成下一轮修图动作，再把更好的最终图交给用户

## Layer 1: Q1 结构闸门

由这些脚本负责：

- `check-svg-attribution.py`
- `lint-svg-diagram.py`
- `check-svg-edge-clearance.py`
- `check-svg-node-padding.py`
- `check-svg-page-chrome.py`

特点：

- 几何或结构错误
- 命中后直接阻断交付

典型问题：

- 节点重叠
- 穿砖
- 贴边滑线
- 分组越界
- 主舞台越界
- 显式或推断母容器下的子砖块越界
- 页面标题、副标题、footer legend 被节点、说明卡、分组、主舞台或箭头侵入
- 页面标题、副标题、footer legend 超出页面 gutter
- 边标签压标题区
- 文字溢出 padding
- 伪水印、重复品牌署名，或手工写出的 `auto-diagram 生成`
- 匿名 `rect + text` chip 因尺寸不足导致的贴边、越界或失衡

## Layer 2: Q4 视觉打磨

由这些脚本负责：

- `check-svg-page-chrome.py`
- `check-layout-rhythm.py`
- `check-visual-hierarchy.py`
- `check-svg-legend-semantics.py`
- `review-diagram-quality.py`

特点：

- 不一定阻断交付
- 但属于设计质量已经下降，建议优先修

典型问题：

- 行列不齐
- 间距体系明显不一致
- 某个分组过挤
- 某个分组或舞台一侧出现明显空白带，说明内容没有把母容器吃满
- 主舞台相对整个 SVG 外沿明显偏置，导致页面一侧出现过大的 outer page band
- 整张图的内容包络相对 viewBox 吃满度不足，边缘视觉平衡失衡
- 页面 header / footer 与主图主体过近，导致 chrome 像被挤压
- 视觉重心明显偏移
- 主次层级扁平
- 主阅读路径方向混乱
  默认以主链和中性通道为主，不把反馈回流、控制线、例外线直接当成主阅读方向

## Layer 3: Design Hint

由 soft-check 脚本输出的 `DESIGN_HINT` 承担。

特点：

- 更偏设计优化建议
- 不代表图一定错误
- 但通常代表“可以做得更像专业图”

典型问题：

- 视觉重量太均匀
- 没有清楚的 primary 节点
- 注释卡存在喧宾夺主风险
- 顶部摘要卡比标题块更抢眼，header chrome 权重失衡
- 某个区域是密度热点
- 复杂反馈线本可以靠颜色分层解决，却仍然被过度绕线
- 多种边通道和线型已经存在，但 legend 解释仍然不足

## 推荐处理原则

- `ERROR`：必须修
- `WARNING`：默认应修；如果有意为之，需能说明理由
- `DESIGN_HINT`：默认看一遍，优先修那些会影响汇报效果的项

## 内部化原则

- Q4 视觉打磨检查的主要用途不是“给用户看分数”
- 而是驱动 skill 做下一轮布局、间距、层级、强调修正
- 默认用 `run-quality-preflight.py --stage soft` 批量收集同轮 `WARNING` / `DESIGN_HINT`
- 如需把视觉打磨项转成更细的内部修图动作，再按需使用 `review-diagram-quality.py`
- 默认目标是：最多 3 轮 Q4 视觉打磨；优先清掉 `WARNING`，再视时间收敛关键 `DESIGN_HINT`

## 环境开关

默认情况下：

- `ERROR` 阻断交付
- `WARNING` 和 `DESIGN_HINT` 只输出，不阻断

如果希望让 soft warning 也阻断，可设置：

```bash
AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING=1
# legacy alias 也兼容：
AUTO_DIAGRAM_FAIL_ON_DESIGN_WARNING=1
```
