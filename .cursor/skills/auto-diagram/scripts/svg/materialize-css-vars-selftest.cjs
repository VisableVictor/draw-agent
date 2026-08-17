#!/usr/bin/env node

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const {
  materializeSvgCssVars,
  materializeSvgFile,
} = require("./materialize-css-vars.cjs");

const fixturePath = path.resolve(
  __dirname,
  "../../assets/regression/font-shorthand-css-var.svg",
);

function runSelftest() {
  const source = fs.readFileSync(fixturePath, "utf8");
  assert.match(
    source,
    /font:\s*700 36px var\(--font-stack\);/,
    "fixture should preserve the original shorthand + CSS var repro",
  );

  const materialized = materializeSvgCssVars(source);
  assert.match(
    materialized,
    /font:\s*700 36px "SFMono-Regular", "IBM Plex Mono", monospace;/,
    "font shorthand should be rewritten with an explicit font family",
  );
  assert.doesNotMatch(
    materialized,
    /font:\s*700 36px var\(--font-stack\);/,
    "materialized SVG must not keep the raster-unsafe font shorthand token",
  );
  assert.doesNotMatch(
    materialized,
    /fill:\s*var\(--title-color\);/,
    "nested color tokens should also be resolved in the raster copy",
  );

  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "auto-diagram-css-vars-"));
  const outputPath = path.join(tempDir, "materialized.svg");
  materializeSvgFile(fixturePath, outputPath);

  const written = fs.readFileSync(outputPath, "utf8");
  assert.equal(
    written,
    materialized,
    "file-based materialization should match the in-memory transform",
  );

  fs.rmSync(tempDir, { recursive: true, force: true });
  console.log("OK: materialize-css-vars selftest passed.");
}

if (require.main === module) {
  try {
    runSelftest();
  } catch (error) {
    console.error(`ERROR: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

module.exports = { runSelftest };
