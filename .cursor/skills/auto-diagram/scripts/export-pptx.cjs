#!/usr/bin/env node

const impl = require("./export/export-pptx.cjs");

if (require.main === module) {
  impl.main(process.argv.slice(2)).catch((error) => {
    const message = error instanceof Error ? error.message : String(error);
    process.stderr.write(`ERROR: ${message}\n`);
    process.exit(1);
  });
}

module.exports = impl;
