#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");
const PptxGenJS = require("pptxgenjs");
const JSZip = require("jszip");
const { XMLParser } = require("fast-xml-parser");
const { ensureSealInSvgText } = require("../svg/finalize-svg.cjs");

const DEFAULT_SLIDE_WIDTH = 13.333;
const DEFAULT_SLIDE_HEIGHT = 7.5;
const PATH_TOKEN_RE = /[A-Za-z]|-?\d*\.?\d+(?:[eE][-+]?\d+)?/g;
const TRANSFORM_TOKEN_RE = /([A-Za-z]+)\s*\(([^)]*)\)/g;
const URL_REF_RE = /^url\(#([^)]+)\)$/i;
const IDENTITY_MATRIX = Object.freeze([1, 0, 0, 1, 0, 0]);
const GEOMETRY_EPSILON = 0.001;
const DEGREES_PER_RADIAN = 180 / Math.PI;
const XML_OPTIONS = {
  ignoreAttributes: false,
  attributeNamePrefix: "",
  preserveOrder: true,
  trimValues: false,
  parseTagValue: false,
  processEntities: true,
};

function usage() {
  console.error("Usage: node scripts/export/export-pptx.cjs <png-or-svg-file> [output-pptx] [--mode raster|editable]");
  console.error("       node scripts/export/export-pptx.cjs --mode editable <svg-file> [output-pptx]");
}

function fail(message, code = 1) {
  console.error(`ERROR: ${message}`);
  process.exit(code);
}

function ensureFile(filePath) {
  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    fail(`File not found: ${filePath}`, 2);
  }
}

function parseArgs(argv) {
  const positional = [];
  let mode = "raster";

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--mode") {
      mode = argv[index + 1] ?? "";
      index += 1;
      continue;
    }
    if (arg === "--editable") {
      mode = "editable";
      continue;
    }
    if (arg === "--raster") {
      mode = "raster";
      continue;
    }
    positional.push(arg);
  }

  if (!["raster", "editable"].includes(mode)) {
    fail(`Unsupported mode: ${mode}`);
  }
  if (positional.length < 1 || positional.length > 2) {
    usage();
    process.exit(2);
  }

  const inputPath = path.resolve(positional[0]);
  const outputPath = path.resolve(
    positional[1] ?? inputPath.replace(path.extname(inputPath), ".pptx"),
  );
  return { mode, inputPath, outputPath };
}

function resolvePngPath(inputPath) {
  const ext = path.extname(inputPath).toLowerCase();
  if (ext === ".png") {
    ensureFile(inputPath);
    return inputPath;
  }

  if (ext === ".svg") {
    ensureFile(inputPath);
    const pngPath = inputPath.slice(0, -4) + ".png";
    ensureFile(pngPath);
    return pngPath;
  }

  fail("Input must be a .png file, or a .svg file with an already exported sibling .png.");
}

function readPngDimensions(filePath) {
  const buffer = fs.readFileSync(filePath);
  if (buffer.length < 24) {
    fail(`PNG is too small to parse: ${filePath}`);
  }

  const signature = buffer.subarray(0, 8);
  const expected = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
  if (!signature.equals(expected)) {
    fail(`Unsupported PNG signature: ${filePath}`);
  }

  const width = buffer.readUInt32BE(16);
  const height = buffer.readUInt32BE(20);
  if (!width || !height) {
    fail(`Failed to read PNG dimensions: ${filePath}`);
  }

  return { width, height };
}

function computeRasterPlacement(imageWidth, imageHeight) {
  const imageAspect = imageWidth / imageHeight;
  const slideAspect = DEFAULT_SLIDE_WIDTH / DEFAULT_SLIDE_HEIGHT;

  if (imageAspect >= slideAspect) {
    const width = DEFAULT_SLIDE_WIDTH;
    const height = width / imageAspect;
    return { x: 0, y: (DEFAULT_SLIDE_HEIGHT - height) / 2, w: width, h: height };
  }

  const height = DEFAULT_SLIDE_HEIGHT;
  const width = height * imageAspect;
  return { x: (DEFAULT_SLIDE_WIDTH - width) / 2, y: 0, w: width, h: height };
}

function parseLength(value, fallback = 0) {
  if (value == null || value === "") {
    return fallback;
  }
  const parsed = Number.parseFloat(String(value).replace("px", "").trim());
  return Number.isFinite(parsed) ? parsed : fallback;
}

function parsePercent(value) {
  if (value == null || value === "") {
    return null;
  }
  const text = String(value).trim();
  if (text.endsWith("%")) {
    return parseLength(text.slice(0, -1), 0) / 100;
  }
  const numeric = parseLength(text, 1);
  return numeric > 1 ? numeric / 100 : numeric;
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function parseViewBox(raw) {
  const parts = String(raw || "")
    .trim()
    .split(/[\s,]+/)
    .map((value) => Number.parseFloat(value));
  if (parts.length !== 4 || parts.some((value) => !Number.isFinite(value))) {
    fail("SVG root is missing a valid viewBox.");
  }
  return { minX: parts[0], minY: parts[1], width: parts[2], height: parts[3] };
}

function getElementName(entry) {
  return Object.keys(entry).find((key) => key !== ":@" && key !== "#text") ?? null;
}

function toElement(entry) {
  const name = getElementName(entry);
  if (!name) {
    return null;
  }
  return {
    name,
    attrs: entry[":@"] || {},
    children: entry[name] || [],
  };
}

function collectText(nodes) {
  let text = "";
  for (const node of nodes || []) {
    if (Object.prototype.hasOwnProperty.call(node, "#text")) {
      text += node["#text"];
    }
    const element = toElement(node);
    if (element) {
      text += collectText(element.children);
    }
  }
  return text;
}

function splitClasses(value) {
  return String(value || "")
    .trim()
    .split(/\s+/)
    .filter(Boolean);
}

function parseDeclarations(body) {
  const declarations = {};
  for (const part of String(body).split(";")) {
    const [rawKey, ...rest] = part.split(":");
    if (!rawKey || rest.length === 0) {
      continue;
    }
    declarations[rawKey.trim()] = rest.join(":").trim();
  }
  return declarations;
}

function parseCssClassRules(cssText) {
  const rules = new Map();
  const ruleRe = /([^{}]+)\{([^{}]+)\}/g;
  let match;
  while ((match = ruleRe.exec(cssText))) {
    const selectors = match[1]
      .split(",")
      .map((selector) => selector.trim())
      .filter(Boolean);
    const declarations = parseDeclarations(match[2]);
    for (const selector of selectors) {
      if (!selector.startsWith(".")) {
        continue;
      }
      const className = selector.slice(1);
      rules.set(className, { ...(rules.get(className) || {}), ...declarations });
    }
  }
  return rules;
}

function parseFontShorthand(value) {
  const text = String(value || "").trim();
  if (!text) {
    return {};
  }

  const sizeMatch = text.match(/(\d*\.?\d+)px/);
  const size = sizeMatch ? Number.parseFloat(sizeMatch[1]) : null;
  const weightMatch = text.match(/\b(100|200|300|400|500|600|700|800|900|bold)\b/i);
  const italic = /\bitalic\b/i.test(text);

  let family = null;
  if (sizeMatch) {
    const familyPart = text.slice(sizeMatch.index + sizeMatch[0].length).trim();
    if (familyPart) {
      family = familyPart;
    }
  }

  return {
    size,
    weight: weightMatch ? weightMatch[1] : null,
    italic,
    family,
  };
}

function parseFontFamilies(value) {
  return String(value || "")
    .split(",")
    .map((part) => part.trim().replace(/^['"]|['"]$/g, ""))
    .filter(Boolean);
}

function containsCjk(text) {
  return /[\u3000-\u9fff\uf900-\ufaff]/.test(String(text || ""));
}

function containsMixedScripts(text) {
  return containsCjk(text) && /[A-Za-z]/.test(String(text || ""));
}

function isGenericFamily(family) {
  return /^(sans-serif|serif|monospace|system-ui|ui-sans-serif|ui-serif)$/i.test(String(family || ""));
}

function isCjkFriendlyFamily(family) {
  return /(pingfang|hiragino|heiti|songti|simhei|simsun|microsoft yahei|source han|noto sans cjk|noto sans sc|wenquanyi|arial unicode|sarasa|lxgw)/i.test(
    String(family || ""),
  );
}

function isPortableLatinFamily(family) {
  return /(arial|aptos|calibri|segoe ui|tahoma|verdana|trebuchet|helvetica|noto sans|liberation sans)/i.test(
    String(family || ""),
  );
}

function isPortableCjkFamily(family) {
  return /(noto sans cjk|noto sans sc|source han|microsoft yahei|pingfang sc|hiragino sans gb|dengxian|heiti|simhei|simsun|wenquanyi|sarasa|arial unicode)/i.test(
    String(family || ""),
  );
}

function portabilityPriority(family, hasCjk) {
  const text = String(family || "").toLowerCase();
  if (hasCjk) {
    if (/pingfang sc|pingfang|hiragino sans gb/.test(text)) {
      return 30;
    }
    if (/microsoft yahei|dengxian/.test(text)) {
      return 24;
    }
    if (/noto sans cjk|noto sans sc|source han/.test(text)) {
      return 20;
    }
    if (/simhei|simsun|sarasa|wenquanyi|arial unicode/.test(text)) {
      return 16;
    }
    return 0;
  }
  if (/arial|aptos|calibri|segoe ui/.test(text)) {
    return 18;
  }
  if (/noto sans|liberation sans|verdana|tahoma|trebuchet/.test(text)) {
    return 12;
  }
  if (/helvetica/.test(text)) {
    return 6;
  }
  return 0;
}

function isDesignerOnlyFamily(family) {
  return /(avenir|helvetica neue|sf pro|san francisco|futura|gotham|frutiger)/i.test(String(family || ""));
}

function pickExportFontFamily(families, text) {
  const cleaned = families.filter((family) => !isGenericFamily(family));
  const hasCjk = containsCjk(text);
  const hasMixedScripts = containsMixedScripts(text);
  const preferredPortableCjk = cleaned.find((family) => /(pingfang sc|pingfang|microsoft yahei|hiragino sans gb|noto sans cjk|noto sans sc|source han|dengxian)/i.test(family));
  const scored = cleaned
    .map((family, index) => {
      let score = 0;
      if (hasCjk && isCjkFriendlyFamily(family)) {
        score += 50;
      }
      if (hasCjk && isPortableCjkFamily(family)) {
        score += 35;
      }
      if (!hasCjk && isPortableLatinFamily(family)) {
        score += 30;
      }
      score += portabilityPriority(family, hasCjk);
      if (hasMixedScripts && isPortableLatinFamily(family) && isCjkFriendlyFamily(family)) {
        score += 10;
      }
      if (isDesignerOnlyFamily(family) && cleaned.length > 1) {
        score -= 15;
      }
      score -= index;
      return { family, score };
    })
    .sort((left, right) => right.score - left.score);

  if (hasCjk) {
    if (preferredPortableCjk) {
      return preferredPortableCjk;
    }
    const explicitCjk = scored.find((entry) => isCjkFriendlyFamily(entry.family))?.family;
    if (explicitCjk) {
      return explicitCjk;
    }
    if (process.platform === "darwin") {
      return "PingFang SC";
    }
    if (process.platform === "win32") {
      return "Microsoft YaHei";
    }
    return "Noto Sans SC";
  }

  const explicitLatin = scored.find((entry) => isPortableLatinFamily(entry.family))?.family;
  if (explicitLatin) {
    return explicitLatin;
  }

  return scored[0]?.family || "Arial";
}

function resolveFont(style, text) {
  const shorthand = parseFontShorthand(style.font);
  const size = parseLength(style["font-size"], shorthand.size ?? 16);
  const weight = String(style["font-weight"] ?? shorthand.weight ?? "").toLowerCase();
  const families = [
    ...parseFontFamilies(style["font-family"]),
    ...parseFontFamilies(shorthand.family),
  ];
  const family = pickExportFontFamily(families, text);
  return {
    sizePx: size,
    families,
    family,
    bold: weight === "bold" || parseLength(weight, 0) >= 600,
    italic: shorthand.italic || String(style["font-style"] || "").toLowerCase() === "italic",
    lang: containsCjk(text) ? "zh-CN" : "en-US",
  };
}

function hexFromRgb(r, g, b) {
  return [r, g, b]
    .map((value) => clamp(Math.round(value), 0, 255).toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();
}

function averageHexColors(colors) {
  if (!colors.length) {
    return null;
  }
  const totals = colors.reduce(
    (sum, color) => {
      sum.r += Number.parseInt(color.slice(0, 2), 16);
      sum.g += Number.parseInt(color.slice(2, 4), 16);
      sum.b += Number.parseInt(color.slice(4, 6), 16);
      return sum;
    },
    { r: 0, g: 0, b: 0 },
  );
  return hexFromRgb(totals.r / colors.length, totals.g / colors.length, totals.b / colors.length);
}

function parseColorValue(value, defs) {
  const raw = String(value || "").trim();
  if (!raw || raw === "none") {
    return null;
  }

  const urlMatch = raw.match(URL_REF_RE);
  if (urlMatch) {
    const gradientColor = defs.gradientColors.get(urlMatch[1]);
    return gradientColor ? { color: gradientColor, alpha: 1 } : null;
  }

  const hexMatch = raw.match(/^#?([0-9a-f]{3}|[0-9a-f]{6})$/i);
  if (hexMatch) {
    let hex = hexMatch[1].toUpperCase();
    if (hex.length === 3) {
      hex = hex
        .split("")
        .map((part) => part + part)
        .join("");
    }
    return { color: hex, alpha: 1 };
  }

  const rgbMatch = raw.match(/^rgba?\(([^)]+)\)$/i);
  if (rgbMatch) {
    const parts = rgbMatch[1].split(",").map((part) => part.trim());
    if (parts.length >= 3) {
      const [r, g, b] = parts.slice(0, 3).map((part) => parseLength(part, 0));
      const alpha = parts[3] == null ? 1 : parsePercent(parts[3]) ?? 1;
      return { color: hexFromRgb(r, g, b), alpha: clamp(alpha, 0, 1) };
    }
  }

  const namedColors = {
    black: "000000",
    white: "FFFFFF",
    gray: "808080",
    grey: "808080",
  };
  const named = namedColors[raw.toLowerCase()];
  return named ? { color: named, alpha: 1 } : null;
}

function resolvePaint(rawValue, styleOpacity, defs) {
  const parsed = parseColorValue(rawValue, defs);
  if (!parsed) {
    return null;
  }
  const opacity = clamp(parsed.alpha * (styleOpacity ?? 1), 0, 1);
  return {
    color: parsed.color,
    transparency: clamp(Math.round((1 - opacity) * 100), 0, 100),
  };
}

function resolveStyle(attrs, defs) {
  const style = {};
  for (const className of splitClasses(attrs.class)) {
    Object.assign(style, defs.classStyles.get(className) || {});
  }
  Object.assign(style, parseDeclarations(attrs.style || ""));

  const directAttrs = [
    "fill",
    "stroke",
    "stroke-width",
    "stroke-dasharray",
    "stroke-linecap",
    "stroke-linejoin",
    "stroke-miterlimit",
    "opacity",
    "fill-opacity",
    "stroke-opacity",
    "font",
    "font-size",
    "font-weight",
    "font-style",
    "font-family",
    "letter-spacing",
    "text-anchor",
    "marker-end",
    "marker-start",
    "marker-mid",
  ];
  for (const attrName of directAttrs) {
    if (attrs[attrName] != null) {
      style[attrName] = attrs[attrName];
    }
  }
  return style;
}

function inferArrowTypeFromName(value) {
  const text = String(value || "");
  if (/diamond/i.test(text)) {
    return "diamond";
  }
  if (/(oval|circle|dot)/i.test(text)) {
    return "oval";
  }
  if (/stealth/i.test(text)) {
    return "stealth";
  }
  if (/triangle/i.test(text)) {
    return "triangle";
  }
  if (/arrow/i.test(text)) {
    return "arrow";
  }
  return null;
}

function countPathVertices(d) {
  const tokens = String(d || "").match(PATH_TOKEN_RE) || [];
  let index = 0;
  let command = null;
  let vertices = 0;
  while (index < tokens.length) {
    const token = tokens[index];
    if (/^[A-Za-z]$/.test(token)) {
      command = token;
      index += 1;
      continue;
    }
    if (!command) {
      break;
    }
    if ("MmLlTt".includes(command) && index + 1 < tokens.length) {
      index += 2;
      vertices += 1;
      continue;
    }
    if ("HhVv".includes(command) && index < tokens.length) {
      index += 1;
      vertices += 1;
      continue;
    }
    if ("Cc".includes(command) && index + 5 < tokens.length) {
      index += 6;
      vertices += 1;
      continue;
    }
    if ("SsQq".includes(command) && index + 3 < tokens.length) {
      index += 4;
      vertices += 1;
      continue;
    }
    if ("Aa".includes(command) && index + 6 < tokens.length) {
      index += 7;
      vertices += 1;
      continue;
    }
    break;
  }
  return vertices;
}

function inferMarkerArrowType(markerElement) {
  for (const child of markerElement.children) {
    const element = toElement(child);
    if (!element) {
      continue;
    }
    if (element.name === "circle" || element.name === "ellipse") {
      return "oval";
    }
    if (element.name === "polygon" || element.name === "polyline") {
      const points = String(element.attrs.points || "")
        .trim()
        .split(/\s+/)
        .filter(Boolean);
      if (points.length === 4) {
        return "diamond";
      }
      if (points.length === 3) {
        return "triangle";
      }
    }
    if (element.name === "path") {
      const vertices = countPathVertices(element.attrs.d);
      if (vertices === 4) {
        return "diamond";
      }
      if (vertices === 3) {
        return "triangle";
      }
    }
  }

  const candidates = [
    markerElement.attrs.id,
    markerElement.attrs.class,
    ...markerElement.children.map((child) => {
      const element = toElement(child);
      return element ? `${element.name} ${element.attrs.class || ""} ${element.attrs.id || ""}` : "";
    }),
  ].filter(Boolean);

  const namedMatch = candidates.map(inferArrowTypeFromName).find(Boolean);
  if (namedMatch) {
    return namedMatch;
  }

  return "triangle";
}

function extractDefs(root) {
  const classStyles = new Map();
  const gradientColors = new Map();
  const markers = new Map();

  function visit(nodes) {
    for (const node of nodes || []) {
      const element = toElement(node);
      if (!element) {
        continue;
      }

      if (element.name === "style") {
        const cssText = collectText(element.children);
        for (const [className, declarations] of parseCssClassRules(cssText)) {
          classStyles.set(className, declarations);
        }
        continue;
      }

      if (element.name === "linearGradient" || element.name === "radialGradient") {
        const id = element.attrs.id;
        const stopColors = [];
        for (const stopNode of element.children) {
          const stop = toElement(stopNode);
          if (!stop || stop.name !== "stop") {
            continue;
          }
          const stopStyle = { ...parseDeclarations(stop.attrs.style || "") };
          if (stop.attrs["stop-color"]) {
            stopStyle["stop-color"] = stop.attrs["stop-color"];
          }
          const color = parseColorValue(stopStyle["stop-color"], { gradientColors: new Map() });
          if (color) {
            stopColors.push(color.color);
          }
        }
        if (id && stopColors.length) {
          gradientColors.set(id, averageHexColors(stopColors));
        }
        continue;
      }

      if (element.name === "marker") {
        if (element.attrs.id) {
          markers.set(element.attrs.id, { arrowType: inferMarkerArrowType(element) });
        }
        continue;
      }

      visit(element.children);
    }
  }

  for (const child of root.children) {
    const element = toElement(child);
    if (element?.name === "defs") {
      visit(element.children);
    }
  }

  return { classStyles, gradientColors, markers };
}

function toVisualUnits(text) {
  let total = 0;
  for (const char of text) {
    if (/\s/.test(char)) {
      total += 0.35;
    } else if (/[\u3000-\u9fff\uf900-\ufaff]/.test(char)) {
      total += 1.0;
    } else if (/[A-Z]/.test(char)) {
      total += 0.68;
    } else {
      total += 0.58;
    }
  }
  return total;
}

function parseLetterSpacingPx(rawValue, fontSizePx) {
  const text = String(rawValue || "").trim();
  if (!text) {
    return 0;
  }
  if (text.endsWith("em")) {
    return parseLength(text.slice(0, -2), 0) * fontSizePx;
  }
  return parseLength(text, 0);
}

function extractTextLines(textElement) {
  const tspanLines = [];
  const tspans = [];
  for (const child of textElement.children) {
    const element = toElement(child);
    if (element?.name === "tspan") {
      tspans.push(element);
      const text = collectText(element.children).replace(/\s+/g, " ").trim();
      if (text) {
        tspanLines.push(text);
      }
    }
  }
  if (tspanLines.length) {
    return { lines: tspanLines, tspans };
  }

  const fullText = collectText(textElement.children).replace(/\s+/g, " ").trim();
  if (!fullText) {
    return { lines: [], tspans: [] };
  }
  return { lines: fullText.split(/\n+/).map((part) => part.trim()).filter(Boolean), tspans: [] };
}

function extractLineHeightPx(fontSizePx, tspans) {
  const dyValues = tspans
    .map((tspan) => parseLength(tspan.attrs.dy, 0))
    .filter((value) => value > 0);
  if (!dyValues.length) {
    return fontSizePx * 1.35;
  }
  return dyValues.reduce((sum, value) => sum + value, 0) / dyValues.length;
}

function multiplyMatrices(left, right) {
  return [
    (left[0] * right[0]) + (left[2] * right[1]),
    (left[1] * right[0]) + (left[3] * right[1]),
    (left[0] * right[2]) + (left[2] * right[3]),
    (left[1] * right[2]) + (left[3] * right[3]),
    (left[0] * right[4]) + (left[2] * right[5]) + left[4],
    (left[1] * right[4]) + (left[3] * right[5]) + left[5],
  ];
}

function applyMatrix(matrix, x, y) {
  return {
    x: (matrix[0] * x) + (matrix[2] * y) + matrix[4],
    y: (matrix[1] * x) + (matrix[3] * y) + matrix[5],
  };
}

function applyLinearMatrix(matrix, dx, dy) {
  return {
    x: (matrix[0] * dx) + (matrix[2] * dy),
    y: (matrix[1] * dx) + (matrix[3] * dy),
  };
}

function parseTransformArgs(text) {
  return String(text || "")
    .trim()
    .split(/[\s,]+/)
    .filter(Boolean)
    .map((part) => Number.parseFloat(part));
}

function parseTransform(value) {
  const text = String(value || "").trim();
  if (!text) {
    return IDENTITY_MATRIX;
  }

  let matrix = IDENTITY_MATRIX;
  let match;
  while ((match = TRANSFORM_TOKEN_RE.exec(text))) {
    const transformName = match[1].toLowerCase();
    const args = parseTransformArgs(match[2]);
    let local = IDENTITY_MATRIX;

    switch (transformName) {
      case "matrix":
        if (args.length >= 6) {
          local = [args[0], args[1], args[2], args[3], args[4], args[5]];
        }
        break;
      case "translate":
        local = [1, 0, 0, 1, args[0] ?? 0, args[1] ?? 0];
        break;
      case "scale":
        local = [args[0] ?? 1, 0, 0, args[1] ?? args[0] ?? 1, 0, 0];
        break;
      case "rotate": {
        const angle = ((args[0] ?? 0) * Math.PI) / 180;
        const cos = Math.cos(angle);
        const sin = Math.sin(angle);
        const cx = args[1] ?? 0;
        const cy = args[2] ?? 0;
        local = multiplyMatrices(
          [1, 0, 0, 1, cx, cy],
          multiplyMatrices([cos, sin, -sin, cos, 0, 0], [1, 0, 0, 1, -cx, -cy]),
        );
        break;
      }
      case "skewx": {
        const angle = ((args[0] ?? 0) * Math.PI) / 180;
        local = [1, 0, Math.tan(angle), 1, 0, 0];
        break;
      }
      case "skewy": {
        const angle = ((args[0] ?? 0) * Math.PI) / 180;
        local = [1, Math.tan(angle), 0, 1, 0, 0];
        break;
      }
      default:
        local = IDENTITY_MATRIX;
        break;
    }

    matrix = multiplyMatrices(local, matrix);
  }

  TRANSFORM_TOKEN_RE.lastIndex = 0;
  return matrix;
}

function vectorLength(vector) {
  return Math.hypot(vector.x, vector.y);
}

function averageMatrixScale(matrix) {
  return (vectorLength(applyLinearMatrix(matrix, 1, 0)) + vectorLength(applyLinearMatrix(matrix, 0, 1))) / 2;
}

function isOrthogonalMatrix(matrix) {
  const xAxis = applyLinearMatrix(matrix, 1, 0);
  const yAxis = applyLinearMatrix(matrix, 0, 1);
  const dot = (xAxis.x * yAxis.x) + (xAxis.y * yAxis.y);
  const lengths = Math.max(vectorLength(xAxis) * vectorLength(yAxis), 1);
  return Math.abs(dot) <= lengths * 0.0001;
}

function transformBox(matrix, x, y, width, height) {
  const topLeft = applyMatrix(matrix, x, y);
  const topRight = applyMatrix(matrix, x + width, y);
  const bottomRight = applyMatrix(matrix, x + width, y + height);
  const bottomLeft = applyMatrix(matrix, x, y + height);
  const points = [topLeft, topRight, bottomRight, bottomLeft];
  if (!isOrthogonalMatrix(matrix)) {
    return null;
  }

  const xAxis = { x: topRight.x - topLeft.x, y: topRight.y - topLeft.y };
  const yAxis = { x: bottomLeft.x - topLeft.x, y: bottomLeft.y - topLeft.y };
  const transformedWidth = Math.max(GEOMETRY_EPSILON, vectorLength(xAxis));
  const transformedHeight = Math.max(GEOMETRY_EPSILON, vectorLength(yAxis));
  const center = applyMatrix(matrix, x + (width / 2), y + (height / 2));

  return {
    points,
    x: center.x - (transformedWidth / 2),
    y: center.y - (transformedHeight / 2),
    width: transformedWidth,
    height: transformedHeight,
    rotate: Number((Math.atan2(xAxis.y, xAxis.x) * DEGREES_PER_RADIAN).toFixed(3)),
  };
}

function matricesRoughlyEqual(left, right) {
  return left.every((value, index) => Math.abs(value - right[index]) < 0.0001);
}

function buildRectPolygon(x, y, width, height) {
  return [
    { x, y },
    { x: x + width, y },
    { x: x + width, y: y + height },
    { x, y: y + height },
  ];
}

function computePolygonBounds(points) {
  const bounds = points.reduce(
    (current, point) => ({
      minX: Math.min(current.minX, point.x),
      minY: Math.min(current.minY, point.y),
      maxX: Math.max(current.maxX, point.x),
      maxY: Math.max(current.maxY, point.y),
    }),
    { minX: Number.POSITIVE_INFINITY, minY: Number.POSITIVE_INFINITY, maxX: Number.NEGATIVE_INFINITY, maxY: Number.NEGATIVE_INFINITY },
  );

  if (!Number.isFinite(bounds.minX) || !Number.isFinite(bounds.minY)) {
    return null;
  }

  return {
    x: bounds.minX,
    y: bounds.minY,
    width: Math.max(0, bounds.maxX - bounds.minX),
    height: Math.max(0, bounds.maxY - bounds.minY),
    maxX: bounds.maxX,
    maxY: bounds.maxY,
  };
}

function polygonArea(points) {
  if (!points.length) {
    return 0;
  }
  let area = 0;
  for (let index = 0; index < points.length; index += 1) {
    const current = points[index];
    const next = points[(index + 1) % points.length];
    area += (current.x * next.y) - (next.x * current.y);
  }
  return Math.abs(area / 2);
}

function pointInPolygon(points, x, y) {
  let inside = false;
  for (let left = 0, right = points.length - 1; left < points.length; right = left, left += 1) {
    const current = points[left];
    const previous = points[right];
    const intersects = (
      (current.y > y) !== (previous.y > y)
      && x < (((previous.x - current.x) * (y - current.y)) / ((previous.y - current.y) || GEOMETRY_EPSILON)) + current.x
    );
    if (intersects) {
      inside = !inside;
    }
  }
  return inside;
}

function buildRectContext(attrs, groupStack, matrix) {
  const x = parseLength(attrs.x);
  const y = parseLength(attrs.y);
  const width = parseLength(attrs.width);
  const height = parseLength(attrs.height);
  const localPolygon = buildRectPolygon(x, y, width, height);
  const globalPolygon = localPolygon.map((point) => applyMatrix(matrix, point.x, point.y));
  return {
    x,
    y,
    width,
    height,
    area: Math.max(width * height, polygonArea(globalPolygon)),
    groupStack: [...groupStack],
    matrix,
    localPolygon,
    globalPolygon,
    globalBounds: computePolygonBounds(globalPolygon),
  };
}

function containsPoint(rect, x, y) {
  return pointInPolygon(rect.globalPolygon, x, y);
}

function nearestPadding(groupStack, key, fallback) {
  for (let index = groupStack.length - 1; index >= 0; index -= 1) {
    const value = groupStack[index][key];
    if (value != null) {
      return value;
    }
  }
  return fallback;
}

function findContainingRect(rects, x, y) {
  const containing = rects.filter((rect) => containsPoint(rect, x, y));
  containing.sort((left, right) => left.area - right.area);
  return containing[0] ?? null;
}

function currentNodeContext(groupStack) {
  for (let index = groupStack.length - 1; index >= 0; index -= 1) {
    if (groupStack[index].nodeId) {
      return groupStack[index];
    }
  }
  return null;
}

function buildObjectName(tagName, attrs, groupStack) {
  const current = groupStack[groupStack.length - 1] || {};
  const parts = [
    tagName,
    attrs["data-node-id"],
    attrs["data-group-id"],
    current.nodeId,
    current.groupId,
    splitClasses(attrs.class)[0],
  ].filter(Boolean);
  return parts.join(" ");
}

function createGroupContext(attrs) {
  return {
    nodeId: attrs["data-node-id"] || null,
    groupId: attrs["data-group-id"] || null,
    stageId: attrs["data-stage-id"] || null,
    padX: attrs["data-pad-x"] != null ? parseLength(attrs["data-pad-x"]) : null,
    padTop: attrs["data-pad-top"] != null ? parseLength(attrs["data-pad-top"]) : null,
    padBottom: attrs["data-pad-bottom"] != null ? parseLength(attrs["data-pad-bottom"]) : null,
  };
}

function reflectPoint(point, pivot) {
  return {
    x: (2 * pivot.x) - point.x,
    y: (2 * pivot.y) - point.y,
  };
}

function angleBetweenVectors(from, to) {
  const cross = (from.x * to.y) - (from.y * to.x);
  const dot = (from.x * to.x) + (from.y * to.y);
  return Math.atan2(cross, dot);
}

function arcToCubicSegments(startX, startY, rx, ry, rotation, largeArcFlag, sweepFlag, endX, endY) {
  if (!rx || !ry) {
    return [{ x1: startX, y1: startY, x2: endX, y2: endY, x: endX, y: endY }];
  }

  let radiusX = Math.abs(rx);
  let radiusY = Math.abs(ry);
  const phi = (rotation * Math.PI) / 180;
  const cosPhi = Math.cos(phi);
  const sinPhi = Math.sin(phi);
  const dx = (startX - endX) / 2;
  const dy = (startY - endY) / 2;
  const x1p = (cosPhi * dx) + (sinPhi * dy);
  const y1p = (-sinPhi * dx) + (cosPhi * dy);

  const radiusCheck = ((x1p ** 2) / (radiusX ** 2)) + ((y1p ** 2) / (radiusY ** 2));
  if (radiusCheck > 1) {
    const scale = Math.sqrt(radiusCheck);
    radiusX *= scale;
    radiusY *= scale;
  }

  const sign = largeArcFlag === sweepFlag ? -1 : 1;
  const numerator = ((radiusX ** 2) * (radiusY ** 2))
    - ((radiusX ** 2) * (y1p ** 2))
    - ((radiusY ** 2) * (x1p ** 2));
  const denominator = ((radiusX ** 2) * (y1p ** 2)) + ((radiusY ** 2) * (x1p ** 2));
  const factor = sign * Math.sqrt(Math.max(0, numerator / (denominator || 1)));
  const cxp = factor * ((radiusX * y1p) / radiusY);
  const cyp = factor * (-(radiusY * x1p) / radiusX);
  const centerX = (cosPhi * cxp) - (sinPhi * cyp) + ((startX + endX) / 2);
  const centerY = (sinPhi * cxp) + (cosPhi * cyp) + ((startY + endY) / 2);

  const startVector = { x: (x1p - cxp) / radiusX, y: (y1p - cyp) / radiusY };
  const endVector = { x: (-x1p - cxp) / radiusX, y: (-y1p - cyp) / radiusY };
  let startAngle = angleBetweenVectors({ x: 1, y: 0 }, startVector);
  let sweepAngle = angleBetweenVectors(startVector, endVector);
  if (!sweepFlag && sweepAngle > 0) {
    sweepAngle -= Math.PI * 2;
  } else if (sweepFlag && sweepAngle < 0) {
    sweepAngle += Math.PI * 2;
  }

  const segmentCount = Math.max(1, Math.ceil(Math.abs(sweepAngle) / (Math.PI / 2)));
  const anglePerSegment = sweepAngle / segmentCount;
  const segments = [];

  for (let index = 0; index < segmentCount; index += 1) {
    const theta1 = startAngle + (index * anglePerSegment);
    const theta2 = theta1 + anglePerSegment;
    const alpha = (4 / 3) * Math.tan((theta2 - theta1) / 4);
    const cosTheta1 = Math.cos(theta1);
    const sinTheta1 = Math.sin(theta1);
    const cosTheta2 = Math.cos(theta2);
    const sinTheta2 = Math.sin(theta2);

    const p1 = { x: radiusX * cosTheta1, y: radiusY * sinTheta1 };
    const p2 = { x: radiusX * (cosTheta1 - (alpha * sinTheta1)), y: radiusY * (sinTheta1 + (alpha * cosTheta1)) };
    const p3 = { x: radiusX * (cosTheta2 + (alpha * sinTheta2)), y: radiusY * (sinTheta2 - (alpha * cosTheta2)) };
    const p4 = { x: radiusX * cosTheta2, y: radiusY * sinTheta2 };

    const transform = (point) => ({
      x: (cosPhi * point.x) - (sinPhi * point.y) + centerX,
      y: (sinPhi * point.x) + (cosPhi * point.y) + centerY,
    });

    const cp1 = transform(p2);
    const cp2 = transform(p3);
    const end = transform(p4);
    segments.push({ x1: cp1.x, y1: cp1.y, x2: cp2.x, y2: cp2.y, x: end.x, y: end.y });
  }

  return segments;
}

function parsePathCommands(d) {
  const tokens = String(d || "").match(PATH_TOKEN_RE) || [];
  let index = 0;
  let command = null;
  let cursor = { x: 0, y: 0 };
  let startPoint = { x: 0, y: 0 };
  let lastCubicControl = null;
  let lastQuadraticControl = null;
  const points = [];
  let unsupported = false;

  const hasNumber = () => index < tokens.length && !/^[A-Za-z]$/.test(tokens[index]);
  const nextNumber = () => {
    const token = tokens[index];
    index += 1;
    return Number.parseFloat(token);
  };
  const toAbsolutePoint = (x, y, relative) => ({
    x: relative ? cursor.x + x : x,
    y: relative ? cursor.y + y : y,
  });

  while (index < tokens.length) {
    if (/^[A-Za-z]$/.test(tokens[index])) {
      command = tokens[index];
      index += 1;
    }
    if (!command) {
      break;
    }

    const relative = command === command.toLowerCase();
    switch (command.toUpperCase()) {
      case "M": {
        let isFirst = true;
        while (hasNumber()) {
          const x = nextNumber();
          const y = nextNumber();
          if (!Number.isFinite(x) || !Number.isFinite(y)) {
            unsupported = true;
            break;
          }
          const target = toAbsolutePoint(x, y, relative);
          cursor = target;
          if (isFirst) {
            startPoint = target;
            points.push({ x: target.x, y: target.y, moveTo: true });
            isFirst = false;
          } else {
            points.push({ x: target.x, y: target.y });
          }
        }
        lastCubicControl = null;
        lastQuadraticControl = null;
        break;
      }
      case "L":
        while (hasNumber()) {
          const target = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          if (!Number.isFinite(target.x) || !Number.isFinite(target.y)) {
            unsupported = true;
            break;
          }
          points.push({ x: target.x, y: target.y });
          cursor = target;
        }
        lastCubicControl = null;
        lastQuadraticControl = null;
        break;
      case "H":
        while (hasNumber()) {
          const x = nextNumber();
          const target = { x: relative ? cursor.x + x : x, y: cursor.y };
          points.push({ x: target.x, y: target.y });
          cursor = target;
        }
        lastCubicControl = null;
        lastQuadraticControl = null;
        break;
      case "V":
        while (hasNumber()) {
          const y = nextNumber();
          const target = { x: cursor.x, y: relative ? cursor.y + y : y };
          points.push({ x: target.x, y: target.y });
          cursor = target;
        }
        lastCubicControl = null;
        lastQuadraticControl = null;
        break;
      case "C":
        while (hasNumber()) {
          const cp1 = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          const cp2 = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          const target = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          points.push({
            x: target.x,
            y: target.y,
            curve: { type: "cubic", x1: cp1.x, y1: cp1.y, x2: cp2.x, y2: cp2.y },
          });
          cursor = target;
          lastCubicControl = cp2;
          lastQuadraticControl = null;
        }
        break;
      case "S":
        while (hasNumber()) {
          const cp1 = lastCubicControl ? reflectPoint(lastCubicControl, cursor) : { ...cursor };
          const cp2 = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          const target = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          points.push({
            x: target.x,
            y: target.y,
            curve: { type: "cubic", x1: cp1.x, y1: cp1.y, x2: cp2.x, y2: cp2.y },
          });
          cursor = target;
          lastCubicControl = cp2;
          lastQuadraticControl = null;
        }
        break;
      case "Q":
        while (hasNumber()) {
          const cp = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          const target = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          points.push({
            x: target.x,
            y: target.y,
            curve: { type: "quadratic", x1: cp.x, y1: cp.y },
          });
          cursor = target;
          lastQuadraticControl = cp;
          lastCubicControl = null;
        }
        break;
      case "T":
        while (hasNumber()) {
          const cp = lastQuadraticControl ? reflectPoint(lastQuadraticControl, cursor) : { ...cursor };
          const target = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          points.push({
            x: target.x,
            y: target.y,
            curve: { type: "quadratic", x1: cp.x, y1: cp.y },
          });
          cursor = target;
          lastQuadraticControl = cp;
          lastCubicControl = null;
        }
        break;
      case "A":
        while (hasNumber()) {
          const rx = nextNumber();
          const ry = nextNumber();
          const rotation = nextNumber();
          const largeArcFlag = nextNumber();
          const sweepFlag = nextNumber();
          const target = toAbsolutePoint(nextNumber(), nextNumber(), relative);
          const segments = arcToCubicSegments(
            cursor.x,
            cursor.y,
            rx,
            ry,
            rotation,
            largeArcFlag,
            sweepFlag,
            target.x,
            target.y,
          );
          for (const segment of segments) {
            points.push({
              x: segment.x,
              y: segment.y,
              curve: { type: "cubic", x1: segment.x1, y1: segment.y1, x2: segment.x2, y2: segment.y2 },
            });
            cursor = { x: segment.x, y: segment.y };
          }
          lastCubicControl = segments.at(-1) ? { x: segments.at(-1).x2, y: segments.at(-1).y2 } : null;
          lastQuadraticControl = null;
        }
        break;
      case "Z":
        points.push({ close: true });
        cursor = { ...startPoint };
        lastCubicControl = null;
        lastQuadraticControl = null;
        break;
      default:
        unsupported = true;
        index += 1;
        break;
    }
  }

  return { points, unsupported };
}

function buildRoundedRectPath(x, y, width, height, rx, ry) {
  const radiusX = clamp(rx || ry || 0, 0, width / 2);
  const radiusY = clamp(ry || rx || 0, 0, height / 2);
  if (!(radiusX > 0) && !(radiusY > 0)) {
    return [
      { x, y, moveTo: true },
      { x: x + width, y },
      { x: x + width, y: y + height },
      { x, y: y + height },
      { close: true },
    ];
  }

  const kappa = 0.5522847498307936;
  const offsetX = radiusX * kappa;
  const offsetY = radiusY * kappa;
  return [
    { x: x + radiusX, y, moveTo: true },
    { x: x + width - radiusX, y },
    {
      x: x + width,
      y: y + radiusY,
      curve: {
        type: "cubic",
        x1: x + width - radiusX + offsetX,
        y1: y,
        x2: x + width,
        y2: y + radiusY - offsetY,
      },
    },
    { x: x + width, y: y + height - radiusY },
    {
      x: x + width - radiusX,
      y: y + height,
      curve: {
        type: "cubic",
        x1: x + width,
        y1: y + height - radiusY + offsetY,
        x2: x + width - radiusX + offsetX,
        y2: y + height,
      },
    },
    { x: x + radiusX, y: y + height },
    {
      x,
      y: y + height - radiusY,
      curve: {
        type: "cubic",
        x1: x + radiusX - offsetX,
        y1: y + height,
        x2: x,
        y2: y + height - radiusY + offsetY,
      },
    },
    { x, y: y + radiusY },
    {
      x: x + radiusX,
      y,
      curve: {
        type: "cubic",
        x1: x,
        y1: y + radiusY - offsetY,
        x2: x + radiusX - offsetX,
        y2: y,
      },
    },
    { close: true },
  ];
}

function transformGeometryPoints(points, matrix) {
  return points.map((point) => {
    if (point.close) {
      return { close: true };
    }
    const transformed = applyMatrix(matrix, point.x, point.y);
    if (!point.curve) {
      return {
        x: transformed.x,
        y: transformed.y,
        moveTo: point.moveTo,
      };
    }

    if (point.curve.type === "quadratic") {
      const control = applyMatrix(matrix, point.curve.x1, point.curve.y1);
      return {
        x: transformed.x,
        y: transformed.y,
        moveTo: point.moveTo,
        curve: { type: "quadratic", x1: control.x, y1: control.y },
      };
    }

    const control1 = applyMatrix(matrix, point.curve.x1, point.curve.y1);
    const control2 = applyMatrix(matrix, point.curve.x2, point.curve.y2);
    return {
      x: transformed.x,
      y: transformed.y,
      moveTo: point.moveTo,
      curve: { type: "cubic", x1: control1.x, y1: control1.y, x2: control2.x, y2: control2.y },
    };
  });
}

function collectPointSamples(points) {
  return points.flatMap((point) => {
    if (point.close) {
      return [];
    }
    if (point.curve?.type === "quadratic") {
      return [
        { x: point.curve.x1, y: point.curve.y1 },
        { x: point.x, y: point.y },
      ];
    }
    if (point.curve?.type === "cubic") {
      return [
        { x: point.curve.x1, y: point.curve.y1 },
        { x: point.curve.x2, y: point.curve.y2 },
        { x: point.x, y: point.y },
      ];
    }
    return [{ x: point.x, y: point.y }];
  });
}

function mapDashArrayToPptDash(rawValue, strokeWidth = 1) {
  const values = String(rawValue || "")
    .split(/[\s,]+/)
    .map((part) => Number.parseFloat(part))
    .filter((part) => Number.isFinite(part) && part > 0);

  if (!values.length) {
    return undefined;
  }

  const normalized = values.length % 2 === 1 ? [...values, ...values] : values;
  const [firstOn = 0, firstOff = 0, secondOn = 0] = normalized;
  const width = Math.max(strokeWidth, 0.1);
  const onRatio = firstOn / width;
  const offRatio = firstOff / width;
  const hasDot = secondOn > 0 && secondOn <= width * 1.5;

  if (normalized.length <= 2) {
    if (onRatio <= 1.5 && offRatio <= 2) {
      return "sysDot";
    }
    if (onRatio >= 4) {
      return "lgDash";
    }
    if (onRatio >= 2.2) {
      return "sysDash";
    }
    return "dash";
  }

  if (normalized.length <= 4) {
    return onRatio >= 4 || hasDot ? "lgDashDot" : "dashDot";
  }

  return onRatio >= 4 ? "lgDashDotDot" : "dashDot";
}

function mapLineCap(value) {
  const text = String(value || "").toLowerCase();
  if (text === "round") {
    return "round";
  }
  if (text === "square") {
    return "square";
  }
  return "flat";
}

function mapLineJoin(value) {
  const text = String(value || "").toLowerCase();
  if (text === "round") {
    return "round";
  }
  if (text === "bevel") {
    return "bevel";
  }
  return "miter";
}

function resolveMarkerArrowType(rawValue, defs, fallback = null) {
  const raw = String(rawValue || "").trim();
  if (!raw || raw === "none") {
    return fallback;
  }
  const urlMatch = raw.match(URL_REF_RE);
  if (urlMatch) {
    return defs.markers.get(urlMatch[1])?.arrowType || inferArrowTypeFromName(urlMatch[1]) || fallback;
  }
  return inferArrowTypeFromName(raw) || fallback;
}

function buildLineXmlTweak(style, uid) {
  return {
    uid,
    cap: mapLineCap(style["stroke-linecap"]),
    join: mapLineJoin(style["stroke-linejoin"]),
    miterLimit: Math.round(parseLength(style["stroke-miterlimit"], 8) * 100000),
  };
}

function exportRasterPptx(inputPath, outputPath) {
  const pngPath = resolvePngPath(inputPath);
  const { width, height } = readPngDimensions(pngPath);
  const placement = computeRasterPlacement(width, height);

  const pptx = new PptxGenJS();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "auto-diagram";
  pptx.company = "auto-diagram";
  pptx.subject = "Diagram export";
  pptx.title = path.basename(outputPath, ".pptx");
  pptx.lang = "zh-CN";

  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };
  slide.addImage({
    path: pngPath,
    x: placement.x,
    y: placement.y,
    w: placement.w,
    h: placement.h,
  });

  return pptx.writeFile({ fileName: outputPath });
}

async function exportEditablePptx(inputPath, outputPath) {
  if (path.extname(inputPath).toLowerCase() !== ".svg") {
    fail("Editable mode currently only supports .svg input from the auto-diagram SVG pipeline.");
  }
  ensureFile(inputPath);

  const xml = ensureSealInSvgText(fs.readFileSync(inputPath, "utf8"));
  const parsed = new XMLParser(XML_OPTIONS).parse(xml);
  const rootEntry = parsed.find((entry) => getElementName(entry) === "svg");
  const root = toElement(rootEntry || {});
  if (!root || root.name !== "svg") {
    fail("Failed to parse SVG root.");
  }

  const viewBox = parseViewBox(root.attrs.viewBox);
  const slideWidth = DEFAULT_SLIDE_WIDTH;
  const slideHeight = Number((slideWidth * (viewBox.height / viewBox.width)).toFixed(4));
  const scaleX = slideWidth / viewBox.width;
  const scaleY = slideHeight / viewBox.height;
  const toInX = (value) => Number(((value - viewBox.minX) * scaleX).toFixed(4));
  const toInY = (value) => Number(((value - viewBox.minY) * scaleY).toFixed(4));
  const toInLenX = (value) => Number((value * scaleX).toFixed(4));
  const toInLenY = (value) => Number((value * scaleY).toFixed(4));
  const svgToPtX = (value) => Number((value * scaleX * 72).toFixed(2));
  const svgToPtY = (value) => Number((value * scaleY * 72).toFixed(2));
  const svgToPt = (value) => Number((value * ((scaleX + scaleY) / 2) * 72).toFixed(2));

  const defs = extractDefs(root);
  const pptx = new PptxGenJS();
  const layoutName = "AUTO_DIAGRAM_EDITABLE";
  pptx.defineLayout({ name: layoutName, width: slideWidth, height: slideHeight });
  pptx.layout = layoutName;
  pptx.author = "auto-diagram";
  pptx.company = "auto-diagram";
  pptx.subject = "Editable diagram export";
  pptx.title = path.basename(outputPath, ".pptx");
  pptx.lang = "zh-CN";

  const slide = pptx.addSlide();
  slide.background = { color: "FFFFFF" };

  const stats = {
    shapes: 0,
    texts: 0,
    lines: 0,
    skippedPaths: 0,
  };
  const lineXmlTweaks = [];
  let objectSequence = 0;

  function nextObjectMeta(tagName, attrs, groupStack) {
    const uid = `${tagName}-${(objectSequence += 1)}`;
    const baseName = buildObjectName(tagName, attrs, groupStack) || tagName;
    return {
      uid,
      name: `${baseName} ad-uid:${uid}`,
    };
  }

  function toRelativeGeometryPoints(points, bounds) {
    return points.map((point) => {
      if (point.close) {
        return { close: true };
      }

      const relativePoint = {
        x: toInLenX(point.x - bounds.x),
        y: toInLenY(point.y - bounds.y),
      };
      if (point.moveTo) {
        relativePoint.moveTo = true;
      }
      if (!point.curve) {
        return relativePoint;
      }
      if (point.curve.type === "quadratic") {
        return {
          ...relativePoint,
          curve: {
            type: "quadratic",
            x1: toInLenX(point.curve.x1 - bounds.x),
            y1: toInLenY(point.curve.y1 - bounds.y),
          },
        };
      }
      return {
        ...relativePoint,
        curve: {
          type: "cubic",
          x1: toInLenX(point.curve.x1 - bounds.x),
          y1: toInLenY(point.curve.y1 - bounds.y),
          x2: toInLenX(point.curve.x2 - bounds.x),
          y2: toInLenY(point.curve.y2 - bounds.y),
        },
      };
    });
  }

  function normalizeGeometryBounds(points) {
    const samples = collectPointSamples(points);
    const bounds = computePolygonBounds(samples);
    if (!bounds) {
      return null;
    }

    let { x, y, width, height } = bounds;
    if (width < GEOMETRY_EPSILON) {
      x -= GEOMETRY_EPSILON / 2;
      width = GEOMETRY_EPSILON;
    }
    if (height < GEOMETRY_EPSILON) {
      y -= GEOMETRY_EPSILON / 2;
      height = GEOMETRY_EPSILON;
    }
    return { x, y, width, height };
  }

  function addCustomGeometry(points, options) {
    const bounds = normalizeGeometryBounds(points);
    if (!bounds) {
      return false;
    }

    slide.addShape("custGeom", {
      x: toInX(bounds.x),
      y: toInY(bounds.y),
      w: Math.max(0.001, toInLenX(bounds.width)),
      h: Math.max(0.001, toInLenY(bounds.height)),
      points: toRelativeGeometryPoints(points, bounds),
      ...options,
    });
    return true;
  }

  function createLineOptions(style, matrix, fallbackEndArrow = null) {
    const opacity = parsePercent(style.opacity) ?? 1;
    const stroke = resolvePaint(
      style.stroke,
      opacity * (parsePercent(style["stroke-opacity"]) ?? 1),
      defs,
    );
    if (!stroke) {
      return { type: "none" };
    }

    const localStrokeWidth = parseLength(style["stroke-width"], 1);
    return {
      color: stroke.color,
      transparency: stroke.transparency,
      width: Math.max(0.5, svgToPt(localStrokeWidth * averageMatrixScale(matrix))),
      dashType: mapDashArrayToPptDash(style["stroke-dasharray"], localStrokeWidth),
      beginArrowType: resolveMarkerArrowType(style["marker-start"], defs) || undefined,
      endArrowType: resolveMarkerArrowType(style["marker-end"], defs, fallbackEndArrow) || undefined,
    };
  }

  function pushLineXmlTweak(style, uid, lineOptions) {
    if (lineOptions.type === "none") {
      return;
    }
    lineXmlTweaks.push(buildLineXmlTweak(style, uid));
  }

  function renderRect(element, context) {
    const elementMatrix = context.transformMatrix;
    const style = resolveStyle(element.attrs, defs);
    const opacity = parsePercent(style.opacity) ?? 1;
    const fill = resolvePaint(style.fill, opacity * (parsePercent(style["fill-opacity"]) ?? 1), defs);
    const line = createLineOptions(style, elementMatrix);

    const x = parseLength(element.attrs.x);
    const y = parseLength(element.attrs.y);
    const width = parseLength(element.attrs.width);
    const height = parseLength(element.attrs.height);
    const rx = parseLength(element.attrs.rx);
    const ry = parseLength(element.attrs.ry);
    if (!(width > 0) || !(height > 0)) {
      return null;
    }

    const objectMeta = nextObjectMeta("rect", element.attrs, context.groupStack);
    const fillOptions = fill || { type: "none" };
    if (matricesRoughlyEqual(elementMatrix, IDENTITY_MATRIX)) {
      const maxRadius = Math.max(rx, ry);
      slide.addShape(maxRadius > 0 ? "roundRect" : "rect", {
        x: toInX(x),
        y: toInY(y),
        w: Math.max(0.001, toInLenX(width)),
        h: Math.max(0.001, toInLenY(height)),
        rectRadius: maxRadius > 0 ? Number((maxRadius / Math.max(Math.min(width, height), 1)).toFixed(4)) : 0,
        fill: fillOptions,
        line,
        objectName: objectMeta.name,
      });
    } else {
      const geometry = transformGeometryPoints(buildRoundedRectPath(x, y, width, height, rx, ry), elementMatrix);
      addCustomGeometry(geometry, {
        fill: fillOptions,
        line,
        objectName: objectMeta.name,
      });
    }

    pushLineXmlTweak(style, objectMeta.uid, line);
    stats.shapes += 1;
    return buildRectContext(element.attrs, context.groupStack, elementMatrix);
  }

  function renderText(element, context, availableRects) {
    const { lines, tspans } = extractTextLines(element);
    if (!lines.length) {
      return;
    }

    const elementMatrix = context.transformMatrix;
    const style = resolveStyle(element.attrs, defs);
    const font = resolveFont(style, lines.join(" "));
    const letterSpacingPx = parseLetterSpacingPx(style["letter-spacing"], font.sizePx);
    const textOpacity = parsePercent(style.opacity) ?? 1;
    const fill = resolvePaint(style.fill, textOpacity * (parsePercent(style["fill-opacity"]) ?? 1), defs)
      || { color: "17344A", transparency: 0 };
    const anchor = String(style["text-anchor"] || element.attrs["text-anchor"] || "start").trim();
    const baseX = parseLength(element.attrs.x);
    const baseY = parseLength(element.attrs.y);
    const lineHeightPx = extractLineHeightPx(font.sizePx, tspans);
    const lineSpacingMultiple = lines.length > 1
      ? Number((Math.max(1.05, lineHeightPx / Math.max(font.sizePx, 0.1))).toFixed(3))
      : undefined;
    const estimatedWidthPx = (
      Math.max(
        ...lines.map((lineText) => (toVisualUnits(lineText) * font.sizePx) + (Math.max(lineText.length - 1, 0) * letterSpacingPx)),
      ) * 1.08
    ) + Math.max(6, font.sizePx * 0.25);
    const estimatedHeightPx = (font.sizePx * 1.25) + (Math.max(lines.length - 1, 0) * lineHeightPx) + (font.sizePx * 0.2);

    let x = baseX;
    let y = baseY - (font.sizePx * 0.92);
    let width = estimatedWidthPx;
    let wrap = false;
    const align = anchor === "middle" ? "center" : anchor === "end" ? "right" : "left";

    const nodeContext = currentNodeContext(context.groupStack);
    if (nodeContext) {
      const globalBase = applyMatrix(elementMatrix, baseX, baseY);
      const container = findContainingRect(availableRects, globalBase.x, globalBase.y);
      if (container && matricesRoughlyEqual(container.matrix, elementMatrix)) {
        const padX = nearestPadding([nodeContext], "padX", 18);
        width = Math.max(24, container.width - (padX * 2));
        x = container.x + padX;
        wrap = true;
      }
    } else if (anchor === "middle") {
      x = baseX - (estimatedWidthPx / 2);
    } else if (anchor === "end") {
      x = baseX - estimatedWidthPx;
    }

    const placement = transformBox(elementMatrix, x, y, width, estimatedHeightPx);
    let pptPlacement;
    if (placement) {
      pptPlacement = {
        x: toInX(placement.x),
        y: toInY(placement.y),
        w: Math.max(0.05, toInLenX(placement.width)),
        h: Math.max(0.05, toInLenY(placement.height)),
        rotate: placement.rotate,
      };
    } else {
      const corners = buildRectPolygon(x, y, width, estimatedHeightPx).map((point) => applyMatrix(elementMatrix, point.x, point.y));
      const bounds = computePolygonBounds(corners);
      pptPlacement = {
        x: toInX(bounds.x),
        y: toInY(bounds.y),
        w: Math.max(0.05, toInLenX(bounds.width)),
        h: Math.max(0.05, toInLenY(bounds.height)),
      };
    }

    const xScale = vectorLength(applyLinearMatrix(elementMatrix, 1, 0));
    const yScale = vectorLength(applyLinearMatrix(elementMatrix, 0, 1));
    const textRuns = lines.length > 1
      ? lines.map((lineText, index) => ({
        text: lineText,
        options: { softBreakBefore: index > 0 },
      }))
      : lines[0];
    const objectMeta = nextObjectMeta("text", element.attrs, context.groupStack);

    slide.addText(textRuns, {
      ...pptPlacement,
      align,
      valign: "top",
      margin: 0,
      wrap,
      fit: wrap ? "shrink" : "none",
      fontFace: font.family,
      fontSize: Math.max(6, svgToPtY(font.sizePx * yScale)),
      bold: font.bold,
      italic: font.italic,
      lang: font.lang,
      color: fill.color,
      transparency: fill.transparency,
      charSpacing: letterSpacingPx > 0 ? svgToPtX(letterSpacingPx * xScale) : undefined,
      lineSpacingMultiple,
      paraSpaceBefore: 0,
      paraSpaceAfter: 0,
      fill: { type: "none" },
      line: { type: "none" },
      objectName: objectMeta.name,
    });
    stats.texts += 1;
  }

  function renderPath(element, context) {
    const elementMatrix = context.transformMatrix;
    const style = resolveStyle(element.attrs, defs);
    const opacity = parsePercent(style.opacity) ?? 1;
    const fill = resolvePaint(style.fill, opacity * (parsePercent(style["fill-opacity"]) ?? 1), defs);
    const line = createLineOptions(
      style,
      elementMatrix,
      splitClasses(element.attrs.class).includes("ad-edge") ? "triangle" : null,
    );
    const { points, unsupported } = parsePathCommands(element.attrs.d);
    if (!points.length) {
      return;
    }
    if (unsupported) {
      stats.skippedPaths += 1;
    }

    const transformedPoints = transformGeometryPoints(points, elementMatrix);
    const objectMeta = nextObjectMeta("path", element.attrs, context.groupStack);
    addCustomGeometry(transformedPoints, {
      fill: fill || { type: "none" },
      line,
      objectName: objectMeta.name,
    });
    pushLineXmlTweak(style, objectMeta.uid, line);
    stats.lines += 1;
  }

  function walk(nodes, context) {
    const siblingRects = [];

    for (const node of nodes || []) {
      const element = toElement(node);
      if (!element) {
        continue;
      }
      if (element.name === "defs") {
        continue;
      }

      const nextAvailableRects = [...context.availableRects, ...siblingRects];
      const elementMatrix = multiplyMatrices(context.transformMatrix, parseTransform(element.attrs.transform));
      if (element.name === "g") {
        walk(element.children, {
          groupStack: [...context.groupStack, createGroupContext(element.attrs)],
          availableRects: nextAvailableRects,
          transformMatrix: elementMatrix,
        });
        continue;
      }

      if (element.name === "rect") {
        const rectContext = renderRect(element, {
          ...context,
          transformMatrix: elementMatrix,
        });
        if (rectContext) {
          siblingRects.push(rectContext);
        }
        continue;
      }

      if (element.name === "text") {
        renderText(element, {
          ...context,
          transformMatrix: elementMatrix,
        }, nextAvailableRects);
        continue;
      }

      if (element.name === "path") {
        renderPath(element, {
          ...context,
          transformMatrix: elementMatrix,
        });
        continue;
      }

      if (element.children?.length) {
        walk(element.children, {
          groupStack: context.groupStack,
          availableRects: nextAvailableRects,
          transformMatrix: elementMatrix,
        });
      }
    }
  }

  function patchSlideLineXml(xmlText) {
    return lineXmlTweaks.reduce((currentXml, tweak) => currentXml.replace(
      new RegExp(
        `(<p:sp[\\s\\S]*?<p:cNvPr[^>]*name="[^"]*ad-uid:${tweak.uid}[^"]*"[^>]*>[\\s\\S]*?<a:ln\\b)([^>]*)(>)([\\s\\S]*?)(</a:ln>)`,
      ),
      (_match, open, attrs, closeStart, body, closeEnd) => {
        let nextAttrs = attrs;
        if (tweak.cap && !/\bcap=/.test(nextAttrs)) {
          nextAttrs += ` cap="${tweak.cap}"`;
        }
        let nextBody = body
          .replace(/<a:round\/>/g, "")
          .replace(/<a:bevel\/>/g, "")
          .replace(/<a:miter[^>]*\/>/g, "");
        if (tweak.join === "round") {
          nextBody += "<a:round/>";
        } else if (tweak.join === "bevel") {
          nextBody += "<a:bevel/>";
        } else {
          nextBody += `<a:miter lim="${tweak.miterLimit}"/>`;
        }
        return `${open}${nextAttrs}${closeStart}${nextBody}${closeEnd}`;
      },
    ), xmlText);
  }

  walk(root.children, {
    groupStack: [],
    availableRects: [],
    transformMatrix: parseTransform(root.attrs.transform),
  });

  let outputBuffer = Buffer.from(await pptx.write({ outputType: "nodebuffer" }));
  if (lineXmlTweaks.length) {
    const zip = await JSZip.loadAsync(outputBuffer);
    const slideEntry = zip.file("ppt/slides/slide1.xml");
    if (slideEntry) {
      const slideXml = await slideEntry.async("string");
      zip.file("ppt/slides/slide1.xml", patchSlideLineXml(slideXml));
      outputBuffer = await zip.generateAsync({ type: "nodebuffer" });
    }
  }
  fs.writeFileSync(outputPath, outputBuffer);
  console.log(
    `Exported editable PPTX: ${outputPath} (shapes=${stats.shapes}, texts=${stats.texts}, lines=${stats.lines}, skippedPaths=${stats.skippedPaths})`,
  );
}

async function main(argv = process.argv.slice(2)) {
  const { mode, inputPath, outputPath } = parseArgs(argv);
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  if (mode === "editable") {
    await exportEditablePptx(inputPath, outputPath);
    return;
  }

  await exportRasterPptx(inputPath, outputPath);
  console.log(`Exported: ${outputPath}`);
}

if (require.main === module) {
  main().catch((error) => {
    fail(error instanceof Error ? error.message : String(error));
  });
}

module.exports = {
  exportEditablePptx,
  exportRasterPptx,
  main,
};
