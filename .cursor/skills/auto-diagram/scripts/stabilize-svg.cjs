#!/usr/bin/env node

const impl = require("./svg/stabilize-svg.cjs");

if (require.main === module) {
  impl.runCli(process.argv.slice(2), "scripts/stabilize-svg.cjs");
}

module.exports = impl;
