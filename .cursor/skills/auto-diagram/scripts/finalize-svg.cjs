#!/usr/bin/env node

const impl = require("./svg/finalize-svg.cjs");

if (require.main === module) {
  impl.runCli(process.argv.slice(2), "scripts/finalize-svg.cjs");
}

module.exports = impl;
