# 图表示例

此目录用于存放 README 中展示的示例图片。

## 如何添加示例图片

### 1. 导出 PNG 格式

将你生成的图表导出为 PNG 格式：

```bash
rsvg-convert -w 1920 -h 1080 your-chart.svg -o architecture-demo.png
```

### 2. 命名规范

建议使用清晰的命名：

- `architecture-demo.png` - 架构图示例
- `flowchart-demo.png` - 流程图示例
- `capability-matrix.png` - 能力矩阵示例
- `comparison-demo.png` - 对比图示例
- `network-topology.png` - 网络拓扑示例

### 3. 图片要求

- **格式**：PNG（推荐）或 JPG
- **分辨率**：1920x1080（16:9）或更高
- **大小**：建议 < 500KB（便于 GitHub 加载）
- **内容**：选择最能展示项目能力的图表

### 4. 更新 README

在 README.md 的"生成示例"部分添加对应的图片引用：

```markdown
示例名称图片路径: PATH_TO_EXAMPLE_PNG

*示例描述*
```

## 当前案例

| 文件名 | 类型 | 说明 |
|--------|------|------|
| llm-wiki-workflow.png | 知识架构图 | LLM Wiki 知识管理工作流 - 先把知识编译进 Wiki，再持续维护 |

## 如何添加新案例

当你生成了满意的图表后：

1. **导出 PNG 格式**（推荐使用浅色主题包）：
   ```bash
   rsvg-convert -w 1920 -h 1080 your-chart.svg -o your-case-name.png
   ```

2. **复制到示例目录**：
   ```bash
   cp your-case-name.png assets/generated/examples/
   ```

3. **更新 README**：
   在 README.md 的"真实案例"部分添加：
   ```markdown
   ### 案例标题
   
   案例图片路径: PATH_TO_CASE_PNG
   
   *案例描述*
   ```

4. **提交并推送**：
   ```bash
   git add assets/generated/examples/your-case-name.png
   git commit -m "docs: 添加 [案例名称] 示例"
   git push origin main
   ```
