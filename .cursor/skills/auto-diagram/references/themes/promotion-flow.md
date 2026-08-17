# Theme Promotion Flow

这条路径只在下面条件同时成立时使用：

- 当前任务来自参考图学习
- 最终大图已经完成交付
- 用户明确选择：`沉淀为主题包`

目标是把“一次性参考图风格”稳定升级成未来可复用的 `learned theme pack`。

## 先读什么

1. [theme-pack-spec.md](theme-pack-spec.md)
2. [../delivery/reporting-output.md](../delivery/reporting-output.md)
3. 若只需要直接执行，优先用 `python3 scripts/theme/promote-reference-style.py ...`
4. 若需要更底层控制，再读 `python3 scripts/theme/create-learned-theme-pack.py --help`

## 标准执行顺序

### Step 1：确认仍然满足沉淀前提

只有下面三条都满足，才继续：

- 本次风格来自 `reference-derived`
- 当前最终图已经交付完成
- 这次风格在未来大概率值得复用

如果只是参考图借风格，但这次结果不够稳定、不够典型，默认不要沉淀。

### Step 2：收 1 个事实

默认只补一个事实：

- 主题包名称

如果用户不想起名，可以由 skill 推荐一个短名。

## 推荐命名方式

- `主情绪 + 色系/材质 + 用途`
- 例如：`静海蓝图`、`夜幕架构`、`清朗汇报蓝`

### Step 3：先判 base pack

判断顺序：

- 画面明显白底 / 日间 / 蓝灰 / 汇报感更强：
  - 优先 `default-day-blue`
- 画面明显暗夜 / 深色 / 技术舞台 / 架构感更强：
  - 优先 `default-dark-architecture`
- 如果两者都不像，仍然选择更接近的一个作为 base，再用 learned pack override 补差异

不要因为“像得不够完全”就从零造整份 token。

### Step 4：收束 style summary

把这次风格压成一句：

`背景基调 + 主强调色 + 组件质感 + 信息密度 + 连线气质`

示例：

- `白底蓝灰基调 + 低饱和浅蓝强调 + 轻卡片 + 中低密信息 + 克制箭头`
- `石板暗夜底 + 青绿语义描边 + 稳定卡片 + 中密分层 + 小箭头`

这句话既服务 learned pack，也服务后续复用时的快速理解。

### Step 5：整理 promotion metadata

最小 metadata：

- `name`
- `style_summary`
- `base_pack`
- `summary`
- `source_notes`
- `reference_image` 或来源说明
- `recommended_for`
- `default_when`
- `avoid_for`
- `preview_file` 或可自动选择的 artifact candidates

推荐默认生成逻辑：

- `summary`：一句话说明这个 learned pack 是什么风格、基于哪个 base pack 派生
- `recommended_for`：优先从 audience / purpose / diagram family 抽
- `default_when`：优先写“后续仍想延续这次参考图气质”这类未来复用条件
- `avoid_for`：写“哪些图不适合它”

### Step 6：优先走高层 promote 脚本

推荐命令：

```bash
python3 scripts/theme/promote-reference-style.py \
  --name "静海蓝图" \
  --style-summary "白底蓝灰 + 更安静留白 + 细描边 + 克制箭头" \
  --reference-image "/path/to/reference.png" \
  --artifact-candidate "/path/to/final.png" \
  --artifact-candidate "/path/to/final.svg" \
  --audience "老板/评审" \
  --purpose "汇报" \
  --diagram-family "架构图"
```

这个高层脚本会：

- 自动推断最合适的 base pack
- 自动补 summary / recommended_for / default_when / avoid_for 的默认值
- 自动从交付产物中优先挑选 `PNG > SVG > HTML` 作为 preview
- 内部再调用 `create-learned-theme-pack.py`
- 最后自动做 validator 检查

### Step 7：标准回执

执行成功后，默认回：

```text
🧩 主题包沉淀
- 名称：...
- 基于：...
- 风格摘要：...
- 预览：...

✅ 当前产出
- 新主题包：...
- 当前主题包总数：...

🧠 后续如何用
- 下次你可以直接说“用这个主题包风格”
- 如果内容相近，我在 brainstorm 阶段也可能主动推荐它
```

## 不要做什么

- 不要在交付前就提前落 learned pack
- 不要让用户一次性填写一大堆 pack 字段
- 不要把 learned pack 做成一次性 prompt 存档
- 不要把主题包当模板，反向去改布局骨架
- 不要因为 preview 缺失就阻塞整条链；能从已有产物自动挑 preview 时优先自动挑
