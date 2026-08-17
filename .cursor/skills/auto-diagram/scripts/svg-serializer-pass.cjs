#!/usr/bin/env node

function findClosingTagIndex(markup, tagName = "svg") {
  const closeToken = `</${tagName}>`;
  const closeIndex = markup.lastIndexOf(closeToken);
  if (closeIndex === -1) {
    throw new Error(`Failed to locate </${tagName}> closing tag.`);
  }
  return closeIndex;
}

function serializeMarkupParts(parts) {
  return parts
    .filter(Boolean)
    .map((part) => String(part))
    .join("");
}

function mergeMarkupBeforeClosingTag(markup, parts, tagName = "svg") {
  const closeIndex = findClosingTagIndex(markup, tagName);
  const payload = serializeMarkupParts(parts);
  return `${markup.slice(0, closeIndex)}${payload}${markup.slice(closeIndex)}`;
}

module.exports = {
  findClosingTagIndex,
  mergeMarkupBeforeClosingTag,
  serializeMarkupParts,
};
