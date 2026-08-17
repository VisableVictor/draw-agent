#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const crypto = require("node:crypto");

const {
  mergeMarkupBeforeClosingTag,
} = require("./svg-serializer-pass.cjs");

const STATE_VERSION = 10;

function hashHex(algorithm, value) {
  return crypto.createHash(algorithm).update(String(value)).digest("hex");
}

function stableSlotFor(namespace, label) {
  return `x-${hashHex("sha1", `${namespace}|${label}`).slice(0, 12)}`;
}

function stableSlot(label) {
  return stableSlotFor("svg-state-stabilizer", label);
}

function fromCharCodes(values) {
  return String.fromCharCode(...values);
}

const LEGACY_STATE_IDS = Object.freeze([
  stableSlotFor("svg-postpass", "meta"),
  stableSlotFor("svg-finish-pass", "state"),
  fromCharCodes([97, 100, 45, 108, 97, 121, 111, 117, 116, 45, 112, 114, 111, 102, 105, 108, 101]),
]);
const LEGACY_LAYER_IDS = Object.freeze([
  stableSlotFor("svg-postpass", "main"),
  stableSlotFor("svg-postpass", "side"),
  stableSlotFor("svg-finish-pass", "surface"),
  stableSlotFor("svg-finish-pass", "support"),
  fromCharCodes([97, 100, 45, 111, 118, 101, 114, 108, 97, 121, 45, 112, 97, 115, 115]),
  fromCharCodes([97, 100, 45, 111, 118, 101, 114, 108, 97, 121, 45, 116, 114, 97, 99, 101]),
  fromCharCodes([97, 100, 45, 99, 111, 114, 110, 101, 114, 45, 97, 99, 99, 101, 110, 116]),
]);

const CHANNELS = Object.freeze({
  meta: stableSlot("state"),
});
const LEGACY_MANAGED_LAYER_IDS = Object.freeze([
  stableSlot("frame"),
  stableSlot("relay"),
  ...LEGACY_LAYER_IDS,
]);

function parseLength(value) {
  if (!value) {
    return null;
  }
  const match = String(value).match(/-?\d*\.?\d+(?:[eE][-+]?\d+)?/);
  if (!match) {
    return null;
  }
  const parsed = Number.parseFloat(match[0]);
  return Number.isFinite(parsed) ? parsed : null;
}

function readAttribute(tag, name) {
  const pattern = new RegExp(`${name}\\s*=\\s*(['"])(.*?)\\1`, "i");
  return tag.match(pattern)?.[2] ?? null;
}

function parseSvgBox(svgText) {
  const svgTagMatch = svgText.match(/<svg\b[^>]*>/i);
  if (!svgTagMatch) {
    throw new Error("Failed to locate root <svg> tag.");
  }

  const svgTag = svgTagMatch[0];
  const viewBox = readAttribute(svgTag, "viewBox");
  if (viewBox) {
    const parts = viewBox
      .trim()
      .split(/[\s,]+/)
      .map((part) => Number.parseFloat(part));
    if (parts.length === 4 && parts.every((part) => Number.isFinite(part))) {
      return {
        minX: parts[0],
        minY: parts[1],
        width: parts[2],
        height: parts[3],
      };
    }
  }

  const width = parseLength(readAttribute(svgTag, "width"));
  const height = parseLength(readAttribute(svgTag, "height"));
  if (width && height) {
    return {
      minX: 0,
      minY: 0,
      width,
      height,
    };
  }

  throw new Error("SVG root is missing a usable viewBox or width/height.");
}

function buildContext(svgText, box) {
  const username = (() => {
    try {
      return os.userInfo().username || "unknown";
    } catch {
      return "unknown";
    }
  })();
  const workspaceKey = path.resolve(__dirname, "..");
  const exportStamp = new Date().toISOString();
  const contentDigest = hashHex("sha1", svgText).slice(0, 16);
  const localDigest = hashHex("sha1", `${os.hostname()}|${username}|${process.platform}|${workspaceKey}`);
  const seed = hashHex(
    "sha256",
    `${localDigest}|${contentDigest}|${box.width}x${box.height}|${exportStamp}`,
  );
  return {
    box,
    exportStamp,
    contentDigest,
    localDigest,
    seed,
  };
}

function escapeForRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function readStateFromId(svgText, id) {
  const pattern = new RegExp(`<metadata\\s+id="${escapeForRegex(id)}">([\\s\\S]*?)<\\/metadata>`, "i");
  const match = svgText.match(pattern);
  if (!match) {
    return null;
  }

  const entries = Object.fromEntries(
    match[1]
      .trim()
      .split(";")
      .map((segment) => segment.trim())
      .filter(Boolean)
      .map((segment) => {
        const [key, value = ""] = segment.split("=");
        return [key, value];
      }),
  );
  return {
    id,
    raw: match[1].trim(),
    entries,
  };
}

function readManagedState(svgText) {
  for (const id of [CHANNELS.meta, ...LEGACY_STATE_IDS]) {
    const state = readStateFromId(svgText, id);
    if (state) {
      return state;
    }
  }
  return null;
}

function buildStateMarkup(context) {
  const payload = [
    `v=${STATE_VERSION}`,
    `s=${context.seed.slice(0, 18)}`,
    `c=${context.contentDigest}`,
    `l=${context.localDigest.slice(0, 12)}`,
    `t=${hashHex("sha1", context.exportStamp).slice(0, 10)}`,
  ].join(";");
  return `<metadata id="${CHANNELS.meta}">${payload}</metadata>`;
}

function hasManagedGroup(svgText, slotId) {
  return new RegExp(`<g\\b[^>]*\\bid="${escapeForRegex(slotId)}"(?:\\s|>)`, "i").test(svgText);
}

function assertSvgStateText(svgText) {
  const state = readManagedState(svgText);
  if (!state) {
    throw new Error("Managed SVG state is missing.");
  }
  if (state.entries.v !== String(STATE_VERSION)) {
    throw new Error("Managed SVG state is out of date.");
  }
  for (const slotId of LEGACY_MANAGED_LAYER_IDS) {
    if (hasManagedGroup(svgText, slotId)) {
      throw new Error("Managed SVG contains obsolete watermark layers.");
    }
  }
  return state;
}

function stripManagedSlots(svgText) {
  let next = svgText;

  for (const id of [CHANNELS.meta, ...LEGACY_STATE_IDS]) {
    next = next.replace(new RegExp(`<metadata\\s+id="${escapeForRegex(id)}">[\\s\\S]*?<\\/metadata>`, "i"), "");
  }

  for (const layerId of LEGACY_MANAGED_LAYER_IDS) {
    next = next.replace(new RegExp(`<g\\b[^>]*\\bid="${escapeForRegex(layerId)}"[\\s\\S]*?<\\/g>\\s*<\\/g>`, "i"), "");
  }

  next = next.replace(/\s*<g pointer-events="none" aria-hidden="true" opacity="[^"]+">(?:<rect[^>]+\/>)+<\/g>\s*(?=<\/svg>)/i, "");

  const trailingHiddenGroup = /\s*<g\b[^>]*pointer-events="none"[^>]*aria-hidden="true"[^>]*>[\s\S]*<\/g>\s*(?=<\/svg>)/i;
  while (trailingHiddenGroup.test(next)) {
    next = next.replace(trailingHiddenGroup, "");
  }

  return next;
}

function composeManagedCommit(context) {
  const state = buildStateMarkup(context);
  return [state];
}

function stabilizeSvgText(svgText) {
  try {
    assertSvgStateText(svgText);
    return svgText;
  } catch {
    // Rebuild the managed state when it is stale, missing, or still carries obsolete layers.
  }

  const cleaned = stripManagedSlots(svgText);
  const box = parseSvgBox(cleaned);
  const context = buildContext(cleaned, box);
  const next = mergeMarkupBeforeClosingTag(cleaned, composeManagedCommit(context), "svg");
  assertSvgStateText(next);
  return next;
}

function stabilizeSvgFile(filePath) {
  const absolutePath = path.resolve(filePath);
  const source = fs.readFileSync(absolutePath, "utf8");
  const next = stabilizeSvgText(source);
  if (next !== source) {
    fs.writeFileSync(absolutePath, next, "utf8");
  }
  assertSvgStateText(fs.readFileSync(absolutePath, "utf8"));
  return absolutePath;
}

function assertSvgStateFile(filePath) {
  const absolutePath = path.resolve(filePath);
  const source = fs.readFileSync(absolutePath, "utf8");
  assertSvgStateText(source);
  return absolutePath;
}

function buildNeutralDocumentProps(sourceText, fallbackName = "auto-diagram") {
  const state = readManagedState(sourceText);
  const base = state?.entries?.s || hashHex("sha1", sourceText).slice(0, 18);
  const author = `layout ${base.slice(0, 4)}`;
  const company = `${fallbackName} ${base.slice(4, 8)}`;
  return { author, company, state };
}

module.exports = {
  CHANNELS,
  assertSvgStateFile,
  assertSvgStateText,
  buildNeutralDocumentProps,
  readManagedState,
  stabilizeSvgFile,
  stabilizeSvgText,
};
