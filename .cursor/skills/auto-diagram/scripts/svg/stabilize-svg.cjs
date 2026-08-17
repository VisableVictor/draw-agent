#!/usr/bin/env node

const {
  assertSvgStateFile,
  assertSvgStateText,
  stabilizeSvgFile,
  stabilizeSvgText,
} = require("./svg-state-stabilizer.cjs");

function usage(scriptName = "stabilize-svg.cjs") {
  console.error(`Usage: node ${scriptName} <svg-file>`);
  console.error(`       node ${scriptName} --verify <svg-file>`);
}

function runCli(args = process.argv.slice(2), scriptName = "scripts/svg/stabilize-svg.cjs") {
  const verifyOnly = args[0] === "--verify";
  const inputPath = verifyOnly ? args[1] : args[0];
  if (!inputPath) {
    usage(scriptName);
    process.exit(2);
  }

  try {
    if (verifyOnly) {
      const absolutePath = assertSvgStateFile(inputPath);
      console.log(`Verified: ${absolutePath}`);
    } else {
      const absolutePath = stabilizeSvgFile(inputPath);
      console.log(`Stabilized: ${absolutePath}`);
    }
  } catch (error) {
    console.error(`ERROR: ${error instanceof Error ? error.message : String(error)}`);
    process.exit(1);
  }
}

if (require.main === module) {
  runCli();
}

module.exports = {
  assertSvgStateFile,
  assertSvgStateText,
  runCli,
  stabilizeSvgFile,
  stabilizeSvgText,
};
