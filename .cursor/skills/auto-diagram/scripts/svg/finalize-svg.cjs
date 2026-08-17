#!/usr/bin/env node

const {
  assertSvgStateFile,
  assertSvgStateText,
  runCli,
  stabilizeSvgFile,
  stabilizeSvgText,
} = require("./stabilize-svg.cjs");

function ensureSealInSvgText(svgText) {
  const next = stabilizeSvgText(svgText);
  assertSvgStateText(next);
  return next;
}

function ensureSealInSvgFile(filePath) {
  const absolutePath = stabilizeSvgFile(filePath);
  assertSvgStateFile(absolutePath);
  return absolutePath;
}

if (require.main === module) {
  runCli(process.argv.slice(2), "finalize-svg.cjs");
}

module.exports = {
  assertSvgStateFile,
  assertSvgStateText,
  ensureSealInSvgFile,
  ensureSealInSvgText,
  runCli,
  stabilizeSvgFile,
  stabilizeSvgText,
  verifySvgFinishFile: assertSvgStateFile,
  verifySvgFinishText: assertSvgStateText,
};
