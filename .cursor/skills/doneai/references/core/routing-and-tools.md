# 模型路由与工具适配

先选模型，再把标准请求转换成具体工具参数。尺寸也是工具参数的一部分：工具要 `width/height` 就选宽高，工具要 `aspectRatio` 就选比例。

## 用户指定模型优先

先归一化用户原句：转小写，去掉空格、连字符、下划线。

| 命中别名 | 锁定模型 |
|----------|----------|
| `image2` / `gptimage` / `gptimage2` / `gpt-image-2` / `GPT-Image-2` | `gpt_image_2` |
| `nano2` / `gemininano` / `gemininano2` / `gemini` | `gemini_nano_2` |
| `seedream` / `即梦` / `seedreamv45` | `seedream_v4_5` |

锁定后，场景只能影响内容、尺寸和 prompt，不能改模型。

## 默认路由

| 条件 | 默认模型 |
|------|----------|
| 用户指定 Seedream / 即梦 | `seedream_v4_5` |
| 图片编辑目标 + 未指定模型 | `gpt_image_2` |
| 未指定模型 + 信息图类 | `gpt_image_2` |
| 未指定模型 + 通用图片 | `seedream_v4_5` |
| 未指定模型 + 常规办公图 | `seedream_v4_5` |
| 用户指定 Nano 2 / Gemini | `gemini_nano_2` |
| 用户指定 Image 2 / GPT-Image-2 | `gpt_image_2` |

## 默认工具

| 模型 | 工具 | 擅长 | 尺寸字段 | 参考图字段 |
|------|------|------|----------|------------|
| `seedream_v4_5` | <tool provider="aone">d.one::liblib_seedream_v4_5</tool> | 通用图片、海报、Banner、战报、公告、社媒图 | `generateParams.width` / `height` | `generateParams.referenceImages` |
| `gpt_image_2` | <tool provider="aone">d.one::gpt_image_2_generate</tool> | 信息图、图解、流程图、文字密集视觉 | `aspectRatio` | `imageUrls` |
| `gemini_nano_2` | <tool provider="aone">d.one::gemini_nano_2_image_create</tool> | 用户明确指定时的任意轻量出图 | `aspectRatio` + `imageSize` | `imageUrls` |

参考图先归入标准请求的 `referenceImageUrls`，只放可访问的 `http://` / `https://` URL。

本地图片不得直接写入工具参数；用户明确要求参与本次生成时，先按 `image-upload.md` 使用 `done-cli upload` 得到 URL。

只有用户明确要求参与本次生成的图片，才作为用户图进入 `referenceImageUrls`。普通上传但未被用户要求使用的图片不进入该字段。

顺序：用户明确使用的上传图 / 用户图片 URL 在前；素材库图如有，追加到最后。

不同模型按工具字段适配：

| 模型 | 参考图字段 |
|------|------------|
| `seedream_v4_5` | `generateParams.referenceImages = referenceImageUrls` |
| `gpt_image_2` | `imageUrls = referenceImageUrls` |
| `gemini_nano_2` | `imageUrls = referenceImageUrls` |

## 标准请求

主流程先形成内部标准请求，只用于选择工具和填参数；它不是 MCP 工具参数，不要直接传给工具。最终输出仍按 `SKILL.md` 展示完整 Prompt。

```json
{
  "model": "seedream_v4_5",
  "prompt": "<完整 prompt>",
  "referenceImageUrls": ["https://..."],
  "targetRatio": "16:9",
  "sizeIntent": "banner",
  "count": 1,
  "skillName": "doneai"
}
```

## 用途到比例

处理顺序：

1. 用户明确给尺寸、比例、平台或用途时优先。
2. 用户没给时，取场景文件的默认比例。
3. 先形成 `targetRatio` 和 `sizeIntent`，再适配具体工具字段。
4. 工具要 `aspectRatio`：传最接近的比例。
5. 工具要 `width/height`：选最接近目标比例的合法宽高。
6. 无法精确匹配时，输出里说明展示裁切方向。

同一个 `sizeIntent` 有多个平台变体时，先用默认 `targetRatio`；只有命中触发条件时才切换。

| `sizeIntent` | 典型用途 | 默认 `targetRatio` | 切换条件 |
|--------------|----------|--------------------|----------|
| `square` | 通用图片、动物、物体、普通社媒 | `1:1` | 无 |
| `avatar` | 头像、图标感形象、个人资料图 | `1:1` | 无 |
| `social_portrait` | 小红书、朋友圈竖图、竖版金句卡 | `3:4` | 用户明确 `4:5`、Instagram 竖图、移动端广告卡片时用 `4:5` |
| `story_vertical` | 手机壁纸、Story、短视频封面竖图 | `9:16` | 无 |
| `poster_vertical` | 活动海报、通知海报、竖版传播海报 | `9:16` | 无 |
| `poster_compact` | 海报感但不想太长、图文卡片 | `4:5` | 用户明确小红书/朋友圈竖图时用 `3:4` |
| `infographic_standard` | 标准信息图、流程图、总结图 | `3:4` | 无 |
| `infographic_long` | 长流程、多步骤清单、长图 | `9:16` | 步骤很多、内容很长、用户说长图时用 `1:2` |
| `knowledge_card` | 知识卡片、单页要点卡 | `1:1` | 用户要求手机端竖版阅读时用 `4:5` |
| `matrix_diagram` | 对比图、象限图、矩阵 | `4:3` | 用户说 PPT/投屏/横版展示时用 `16:9` |
| `architecture_wide` | 架构图、层级图、系统关系图 | `16:9` | 层级横向很多时用 `2:1` |
| `presentation` | PPT、投屏、周会汇报、邮件头图 | `16:9` | 无 |
| `dashboard` | 数据战报、仪表盘、周报配图 | `16:9` | 用户说群内同步/朋友圈时用 `1:1` |
| `web_hero` | 网页头图、活动页 Hero、超宽顶部视觉 | `21:9` | 无 |
| `banner` | 后台 Banner、钉钉工作台、内部广告位 | `2:1` | 用户说邮件头图/PPT 横图时用 `16:9` |
| `narrow_banner` | 窄条 Banner、横幅广告位 | `21:9` | 用户给广告位接近 2:1 时用 `2:1` |
| `desktop_wallpaper` | 桌面壁纸、横向风景图 | `16:9` | 无 |
| `product_showcase` | 产品图、物体展示、主视觉素材 | `1:1` | 海报展示、电商竖图、移动端首屏时用 `4:5` |
| `edit_keep_ratio` | 图片编辑并尽量贴近原图比例 | `1:1` | 有明确原图比例时切换到最接近比例 |

## 比例到工具参数

| `targetRatio` | Seedream V4.5 `width`/`height` | Image 2 `aspectRatio` | Nano 2 `aspectRatio` |
|---------------|---------------------------------|-----------------------|----------------------|
| `1:1` | `2048` / `2048` | `1:1` | `1:1` |
| `3:4` | `1728` / `2304` | `3:4` | `3:4` |
| `4:5` | `1840` / `2300` | `4:5` | `4:5` |
| `9:16` | `1440` / `2560` | `9:16` | `9:16` |
| `16:9` | `2560` / `1440` | `16:9` | `16:9` |
| `4:3` | `2304` / `1728` | `4:3` | `4:3` |
| `3:2` | `2496` / `1664` | `3:2` | `3:2` |
| `2:3` | `1664` / `2496` | `2:3` | `2:3` |
| `2:1` | `2896` / `1448` | `2:1` | `2:1` |
| `21:9` | `3024` / `1296` | `21:9` | `21:9` |
| `1:2` | `1448` / `2896` | `1:2` | `1:2` |
| `9:21` | `1296` / `3024` | `9:21` | `9:21` |
| `5:4` | `2300` / `1840` | `5:4` | `5:4` |

### seedream_v4_5

Seedream 使用 `generateParams.width` + `generateParams.height`：

`width` 和 `height` 必须同时传；只传一个不生效。

默认使用上表的 2K 档尺寸，面积尽量不低于 `3,686,400`，且不超过 `16,777,216`。

自定义尺寸按用户指定优先，但必须校验 `width × height`：

- 小于后端最小面积 `1,048,576`：按原比例等比放大到合法范围。
- 大于最大面积 `16,777,216`：按原比例等比缩小到合法范围。
- 介于 `1,048,576` 和 `3,686,400`：用户明确指定时可传；用户未指定时用上表推荐尺寸。

如果用户给的是展示尺寸，例如 `1920×1080`，选择最接近的合法生图参数，并在输出里说明展示时裁切。

### gpt_image_2

Image 2 使用 `aspectRatio`：

`"1:1"` / `"3:2"` / `"2:3"` / `"16:9"` / `"9:16"` / `"4:3"` / `"3:4"` / `"21:9"` / `"9:21"` / `"2:1"` / `"1:2"` / `"5:4"` / `"4:5"`

图片编辑按参考图或场景选择最接近的明确比例，无法判断时用 `"1:1"`。

### gemini_nano_2

Nano 2 使用 `aspectRatio` + `imageSize`。`aspectRatio` 按目标比例选择；DoneAI 默认 `imageSize: "2K"`。

## 工具参数

以下 JSON 是实际工具参数示例；执行时必须使用这些真实字段。

### gpt_image_2

```json
{
  "prompt": "...",
  "imageUrls": ["https://图1用户指定图片", "https://图2用户指定图片", "https://图3素材库参考图"],
  "aspectRatio": "3:4",
  "n": 1,
  "skillName": "doneai"
}
```

无参考图时省略 `imageUrls`。

### gemini_nano_2

```json
{
  "prompt": "...",
  "imageUrls": ["https://图1用户指定图片", "https://图2用户指定图片", "https://图3素材库参考图"],
  "aspectRatio": "3:4",
  "imageSize": "2K",
  "shouldUseGoogleSearch": false,
  "skillName": "doneai"
}
```

无参考图时省略 `imageUrls`。默认 `shouldUseGoogleSearch: false`。

### seedream_v4_5

```json
{
  "prompt": "...",
  "generateParams": {
    "width": 1536,
    "height": 2048,
    "imgCount": 1,
    "referenceImages": ["https://图1用户指定图片", "https://图2用户指定图片", "https://图3素材库参考图"]
  },
  "skillName": "doneai"
}
```

无参考图时省略 `referenceImages`。

## 辅助工具

| 用途 | 工具 | 参数 |
|------|------|------|
| 上传本地图片 | `done-cli upload` | 本地图片绝对路径；详见 `image-upload.md` |
| 素材库参考 | <tool provider="aone">d.one::get_user_library_materials</tool> | `{}` |
| 查询生图状态 | <tool provider="aone">d.one::liblib_get_generate_status</tool> | `generateUuid` |
| 查询生图记录 | <tool provider="aone">d.one::get_generate_record_id</tool> | `generateUuid` |
| 保存素材库 | <tool provider="aone">d.one::add_prompt_to_library</tool> | `recordId`；`libraryId` 可省略 |

## JSON 转义

prompt 中包含英文双引号时，嵌入 `aone-kit` JSON 字符串写成 `\\\"`：

- `标题\\\"千问模型分享会\\\"` 正确
- `标题\"千问模型分享会\"` 错误
- `标题"千问模型分享会"` 错误

## 失败切换

- 用户指定模型失败：不能静默换模型，说明失败并询问是否改用其他模型。
- 默认模型失败：同模型简化 prompt 重试 1 次；仍失败再按场景考虑切换或告知用户。

## 调用方式

本地图片上传使用：

```bash
done-cli upload "/absolute/path/to/image.png"
```

`done-cli` 命令不可用时，先安装：

```bash
npm install -g @ali/done-cli --registry=https://registry.anpm.alibaba-inc.com
```

生图和素材工具调用使用：

```bash
aone-kit call-tool <tool-id> '<json args>'
```

`aone-kit` 命令不可用时，先安装：

```bash
npm install -g @ali/aone-kit --registry=https://registry.anpm.alibaba-inc.com
```

安装完成后继续调用工具。
