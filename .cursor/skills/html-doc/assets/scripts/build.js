#!/usr/bin/env node
/**
 * html-doc 构建脚本（复制改造模板）
 * --------------------------------------------------------------
 * 用法：
 *   1. 把本脚本复制到你的项目目录：cp build.js my-project/build.js
 *   2. 改下方 3 个路径常量为你的实际路径
 *   3. 如需数据聚合 / 统计 / 跨源合并，编辑 transform() 函数
 *   4. 运行：node build.js
 *
 * 工作机制：
 *   读模板 + 读数据 → transform() 加工 → 整段替换模板内
 *   <script data-template>...</script> 标签为真实数据 → 输出最终 HTML
 */

const fs = require('fs');
const path = require('path');

// ======== 改这 3 个（全部是你项目里的文件，不是 skill 里的） ========
const TEMPLATE_PATH = './your-template.html';   // 你改造好的模板（从 assets/templates/ 复制 + 改造来）
const DATA_PATH     = './your-data.json';       // 你的数据源
const OUTPUT_PATH   = './your-output.html';     // 最终产物
// ======================================================

/**
 * 数据加工钩子：默认透传。
 * 需要做聚合 / 统计 / 多源合并时，在这里改。
 *
 * 示例（取消注释并按需改造）：
 *   return {
 *       ...rawData,
 *       meta: { ...rawData.meta, generatedAt: new Date().toISOString() },
 *       kpis: rawData.records.map(r => ({ label: r.name, value: r.total })),
 *       chart: { data: rawData.records.map(r => r.total) }
 *   };
 */
function transform(rawData) {
    return rawData;
}

// ======== 以下一般无需修改 ========

const template = fs.readFileSync(TEMPLATE_PATH, 'utf8');
const rawData = JSON.parse(fs.readFileSync(DATA_PATH, 'utf8'));
const data = transform(rawData);

// 序列化 + 防 </script> 污染
const jsonStr = JSON.stringify(data).replace(/<\//g, '<\\/');
const realScript = `<script>const D = ${jsonStr};</script>`;

// 整段替换 <script data-template>...</script>
//   - [\s\S]*? 非贪婪，避免吃到下一个 </script>
//   - [^>]* 容忍标签上的任意属性
const TAG_RE = /<script\s+data-template[^>]*>[\s\S]*?<\/script>/;

if (!TAG_RE.test(template)) {
    console.error(`✗ 模板中未找到 <script data-template> 标签: ${TEMPLATE_PATH}`);
    console.error('  请确认模板内是否保留了数据注入点。');
    process.exit(1);
}

fs.mkdirSync(path.dirname(path.resolve(OUTPUT_PATH)), { recursive: true });
fs.writeFileSync(OUTPUT_PATH, template.replace(TAG_RE, realScript));

const sizeKB = (fs.statSync(OUTPUT_PATH).size / 1024).toFixed(1);
console.log(`✓ 已生成 ${OUTPUT_PATH} (${sizeKB} KB)`);
