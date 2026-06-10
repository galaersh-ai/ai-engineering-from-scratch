const fs = require('fs');
const path = require('path');
const assert = require('assert');

const htmlPath = path.join(__dirname, 'reviewer.html');
const reviewerDataPath = path.join(__dirname, 'reviewer-data.js');
assert.ok(fs.existsSync(htmlPath), 'site/reviewer.html must exist');
assert.ok(fs.existsSync(reviewerDataPath), 'site/reviewer-data.js must exist');

const html = fs.readFileSync(htmlPath, 'utf8');
const reviewerData = fs.readFileSync(reviewerDataPath, 'utf8');

[
  'id="lessonSelect"',
  'id="englishColumn"',
  'id="russianColumn"',
  'id="reviewPanel"',
  'id="exportLesson"',
  'id="exportAll"',
  'function buildReviewExport',
  'targetPath',
  'needs_retranslation',
  'bad_translation',
  'localStorage',
  'reviewer-data.js',
  'function readBundledMarkdown',
  'function normalizeMarkdownSource',
  'numberedLines < 3',
  'data-action="delete"',
  'deletedRuRawIds',
  'function getVisibleBlocks',
  'function markRuBlockDeleted',
  'translate_as_text',
  'data-action="text"'
].forEach((needle) => {
  assert.ok(html.includes(needle), `reviewer.html missing ${needle}`);
});

assert.ok(reviewerData.includes('window.REVIEWER_MARKDOWN'), 'reviewer-data.js must expose window.REVIEWER_MARKDOWN');
assert.ok(reviewerData.includes('phases/00-setup-and-tooling/01-dev-environment'), 'reviewer-data.js must include a known reviewed lesson');
assert.ok(reviewerData.includes('"en"'), 'reviewer-data.js must include English markdown payloads');
assert.ok(reviewerData.includes('"ru"'), 'reviewer-data.js must include Russian markdown payloads');

console.log('reviewer.html smoke test passed');
