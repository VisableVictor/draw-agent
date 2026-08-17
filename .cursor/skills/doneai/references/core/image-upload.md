# 本地图片上传

生图工具的参考图字段只接受可访问的 `http://` / `https://` URL。用户明确要求本地图片或对话附件参与本次生成时，优先用本机 `done-cli` 上传到 Done OSS。素材库 `coverUrl` 和已有线上图片 URL 不需上传。

## 执行流程

1. 只处理用户明确要求参与本次生成的图片；不上传无关附件。
2. 已是 `http://` / `https://` URL 时直接保留。
3. 本地图片先确认路径存在、是普通文件且可读。路径中的空格、括号或中文不得被拆分。
4. 确认 `done-cli` 可用。命令不存在时，先用和 `aone-kit` 相同的内网 registry 安装，安装成功后继续：

   ```bash
   if ! command -v done-cli >/dev/null 2>&1; then
     npm install -g @ali/done-cli --registry=https://registry.anpm.alibaba-inc.com
   fi
   command -v done-cli
   ```

5. 对每个本地文件执行：

   ```bash
   done-cli upload "/absolute/path/to/image.png"
   ```

6. `done-cli upload` 成功时会在标准输出中打印 Done OSS preview URL。只接受命令成功退出且输出中匹配到的最后一个独立 `http://` / `https://` URL；上传日志、版本更新提示和其他文本不得写入参考图字段。
7. 将成功得到的 URL 按用户图片原顺序放入 `referenceImageUrls`；如选中素材库图，再将其 `coverUrl` 追加到最后。
8. 上传后继续按 `routing-and-tools.md` 适配到 `referenceImages` 或 `imageUrls`，不将本地路径直接传给生图工具。

`done-cli` 的新版本提示不是上传失败，不要因此中断流程。不需要在每次上传前单独调用 `done-cli whoami`；`upload` 会自行解析当前用户。

## 格式和数量

- 优先上传生图模型可直接使用的 PNG、JPEG/JPG 或 WebP。
- GIF、SVG、HEIC 等格式只在目标模型明确支持时直接传入；否则先转成 PNG，并保留原图不变。
- 目标模型对参考图数量有限制时，先保留用户明确要求的图，再决定是否追加素材库图。

## 失败处理

1. `done-cli` 安装失败、身份解析失败、文件不存在、上传超时、非零退出，或成功退出但没有可用 URL，都视为上传失败。
2. 明显的瞬时网络或超时错误可对该文件重试 1 次；文件不存在、格式不支持或身份错误不盲目重试。
3. 普通参考图上传失败：跳过该图，告知用户具体文件名和原因，继续按剩余参考图或纯 prompt 生图。
4. 编辑目标、人物/IP 一致性、产品保持或 Logo 保持所必需的图上传失败：不能降级为纯文生图；停止调用生图工具，说明原因并请用户提供可访问的线上 URL。
5. `done-cli` 安装失败时，可使用当前环境已有的等价上传能力；也不可用时再按上述普通参考图/必需图规则处理。

不在用户可见输出中暴露本地绝对路径、工号、认证信息或命令的内部日志。
