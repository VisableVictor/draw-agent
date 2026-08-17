#!/usr/bin/env node

const fs = require("node:fs");
const path = require("node:path");

function usage() {
  console.error("Usage: node scripts/svg/materialize-css-vars.cjs <input-svg> [output-svg]");
}

function collectCustomProperties(cssText) {
  const vars = new Map();
  const pattern = /(--[\w-]+)\s*:\s*([^;]+);/g;
  let match = pattern.exec(cssText);
  while (match) {
    vars.set(match[1].trim(), match[2].trim());
    match = pattern.exec(cssText);
  }
  return vars;
}

function resolveValue(value, vars, stack = []) {
  return value.replace(/var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)/g, (_, name, fallback = "") => {
    if (stack.includes(name)) {
      return fallback ? resolveValue(fallback.trim(), vars, stack) : "";
    }
    if (vars.has(name)) {
      return resolveValue(vars.get(name), vars, [...stack, name]);
    }
    return fallback ? resolveValue(fallback.trim(), vars, stack) : "";
  });
}

function materializeStyleBlock(styleText) {
  const vars = collectCustomProperties(styleText);
  if (!vars.size || !styleText.includes("var(")) {
    return styleText;
  }

  const resolvedVars = new Map();
  for (const [name, value] of vars.entries()) {
    resolvedVars.set(name, resolveValue(value, vars));
  }

  return styleText.replace(/var\(\s*(--[\w-]+)\s*(?:,\s*([^)]+))?\)/g, (_, name, fallback = "") => {
    if (resolvedVars.has(name)) {
      return resolvedVars.get(name);
    }
    return fallback ? fallback.trim() : "";
  });
}

function materializeSvgCssVars(svgText) {
  return svgText.replace(/<style\b([^>]*)>([\s\S]*?)<\/style>/gi, (full, attrs, cssText) => {
    const nextCss = materializeStyleBlock(cssText);
    return `<style${attrs}>${nextCss}</style>`;
  });
}

function materializeSvgFile(inputPath, outputPath) {
  const absoluteInput = path.resolve(inputPath);
  const absoluteOutput = path.resolve(outputPath || inputPath);
  const source = fs.readFileSync(absoluteInput, "utf8");
  const next = materializeSvgCssVars(source);
  fs.writeFileSync(absoluteOutput, next, "utf8");
  return absoluteOutput;
}

function runCli(args = process.argv.slice(2)) {
  const inputPath = args[0];
  const outputPath = args[1];
  if (!inputPath) {
    usage();
    process.exit(2);
  }

  try {
    const absoluteOutput = materializeSvgFile(inputPath, outputPath);
    console.log(`Materialized CSS vars: ${absoluteOutput}`);
  } catch (error) {
    console.error(`ERROR: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

if (require.main === module) {
  runCli();
}

module.exports = {
  collectCustomProperties,
  materializeStyleBlock,
  materializeSvgCssVars,
  materializeSvgFile,
  resolveValue,
  runCli,
};
