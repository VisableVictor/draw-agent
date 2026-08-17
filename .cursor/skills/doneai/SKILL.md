---
name: doneai
description: >-
  办公/运营场景快速出图：活动海报、数据战报、内部公告、社媒配图、
  运营 Banner、信息图、知识卡片。适合需要快速交付的日常办公配图。
  Use when user mentions 活动海报、Banner、数据战报、内部公告、社媒配图、
  做一张配图、广告位、横幅、战报、通知、放假通知、朋友圈配图、
  信息图、图解、知识卡片、运营物料、快速出图。
  不用于：技术架构图、杂志风艺术海报（用 zine-poster）、数据图表（用 lieflat-charts）。
alwaysApply: false
globs: []
---

# DoneAI

用于出图：通用图片、活动海报、数据战报、内部公告、社媒配图、运营 Banner 和信息图。抓住用途、素材、尺寸和模型偏好，产出可调用的 prompt 与参数，并轮询到结果。

```
用户意图 → 场景/素材 → Prompt 或素材轻提示 → 模型参数 → 工具调用 → 轮询验收
```

## 读取顺序

执行生图：

1. `references/core/workflow.md`：总流程、意图、素材库、输入图和人物一致性内置规则。
2. 有本地图片需参与生成时读 `references/core/image-upload.md`：用 `done-cli` 上传并取可访问 URL。
3. `references/core/scenes.md`：场景触发词、关键信息和场景文件入口。
4. 对应 `references/scenes/*.md`：场景业务内容、默认尺寸和 Prompt 模块。
5. `references/core/routing-and-tools.md`：模型别名、路由规则、工具参数、尺寸/比例字段。
6. `references/core/polling-and-errors.md`：异步轮询、失败重试、超时处理。

维护或新增场景：

- 新建或复制一个 `references/scenes/*.md`。
- 在 `references/core/scenes.md` 登记触发词和关键信息。
- 不在场景文件里写具体工具调用字段。

维护或新增模型：

- 改 `references/core/routing-and-tools.md`。
- 必要时更新本文件的默认选择。

## 执行准则

1. **用户指定模型优先**：用户明确指定模型时优先使用指定模型。
2. **场景文件管内容和比例意图**：场景文件决定业务内容、版式、默认 `sizeIntent` / `targetRatio` 和 Prompt 模块；模型选择看 `routing-and-tools.md`。
3. **工具文件管尺寸参数**：用户尺寸/平台要求优先；工具要 `width/height` 或 `aspectRatio` 时，在 `routing-and-tools.md` 里转换。
4. **图片按意图参与**：只有用户明确要求使用的图片、或已选中的素材库图，才进入 `referenceImageUrls`；普通上传但未指向本次生成的图片，不自动触发图改图；素材历史 prompt 里提到的输入图不是本次用户必须提供的图片。
5. **不补业务事实**：用户没给的时间、地点、部门、数据、人物身份、品牌承诺不能擅自补。
6. **必须传 `skillName: "doneai"`**：所有生图工具调用都带上该字段。
7. **异步任务轮询到终态**：每个 `generateUuid` 必须轮询到 `generateStatus` 为 5 或 6。
8. **JSON 字符串转义**：prompt 写进工具参数时，英文双引号按 `routing-and-tools.md` 处理。
9. **aone-kit 缺失先安装**：需要调用工具但本机没有 `aone-kit` 时，先按 `routing-and-tools.md` 安装，再继续调用。
10. **执行优先**：不能只复述 DoneAI 流程；必须把素材库、输入图、尺寸和模型选择落到标准请求和真实工具参数里。
11. **素材库异常不阻断**：素材库不可用、查不到或字段异常时跳过素材库，继续按用户需求生图。
12. **本地图片优先走 `done-cli`**：用户明确要求本地图片参与生成时，必须先按 `image-upload.md` 执行 `done-cli upload`，成功后再将 URL 写入参考图字段。
13. **done-cli 缺失先安装**：需要上传本地图但本机没有 `done-cli` 时，先按 `image-upload.md` 安装 `@ali/done-cli`，再继续上传。

## 默认选择

| 用户输入 | 处理 |
|----------|----------|
| 明确说 `image2` / `gpt-image-2`，且属于 DoneAI 范围 | 用 Image 2 |
| 明确说 `nano2` / `Gemini`，且属于 DoneAI 范围 | 用 Nano 2 |
| 图片编辑 / 改已有图 | 默认 Image 2 |
| 信息图 / 图解 / 流程图 / 对比图 / 知识卡片 | 默认 Image 2 |
| 活动海报 / 战报 / 公告 / 社媒配图 / Banner | 默认 Seedream V4.5 |
| 通用图片 / 小猫 / 风景 / 头像 / 壁纸 | 默认 Seedream V4.5 |
| 素材库返回素材 | agent 判断是否有可用参考图；有则选最合适的一张 `coverUrl` 追加到输入图最后，prompt 保持用户输入 + 参考图角色 |
| 基于某张图修改 / 让上传 IP 做动作 | 用户明确使用的图按顺序传入；动作和修改要求写进 prompt |
| 用户上传多张图 | 只传用户明确要求参与本次生成的图；多张都被明确使用时按上传顺序传入 |
| 上传图 / 本地参考图 | 需要参与生成时优先用 `done-cli upload` 转成线上 URL；无法上传时，普通参考图可跳过，编辑目标必须要求 URL |
| 查询状态 / 保存素材库 | 不生新图，只做查询或保存 |

## 输出格式

````markdown
## 生图结果

**场景**：{场景名称}
**尺寸**：{实际工具参数；如需裁切，注明目标展示尺寸}
**模型**：{Seedream V4.5 / GPT-Image-2 / Gemini Nano 2 / 未来模型名}

### 生成说明

- **场景判断**：{1句话}
- **模型选择**：{用户指定 / 默认路由 / 能力适配，1句话}
- **尺寸处理**：{用户指定 / 场景默认 / 最接近适配，1句话}
- **素材库参考**：{未使用 / 已使用素材库参考图}
- **参考图处理**：{未使用 / 用户指定图片已传入 / 素材库图已追加到最后}

### 图片

![图片](图片URL)

- **视觉方向**：{一句话说明画面方向}
- **Prompt 摘要**：{核心描述，1句话}
- **适用场景**：{如：首页主视觉 / 活动预热 / 社媒传播 / 汇报配图}

### 完整 Prompt

```text
{实际传给工具的完整 prompt 参数全文，禁止省略；如使用素材库参考图，必须包含"参考图列表最后一张为素材库参考图"}
```
````

默认不展示 `generateUuid` / `recordId`，除非用户要求查询、保存或排障。

工具清单和参数见 `references/core/routing-and-tools.md`。
