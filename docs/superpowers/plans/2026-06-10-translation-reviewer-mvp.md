# Translation Reviewer MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use $superpower-subagents (recommended) or $superpower-executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking via update_plan.

**Goal:** Build `site/reviewer.html`, a static side-by-side EN/RU translation review workspace with local saved review state and JSON export.

**Architecture:** Keep the MVP self-contained in one static HTML file so the existing `lesson.html` remains untouched. Reuse `site/data.js`, `site/style.css`, and the same lesson path convention. Add one lightweight Node smoke test that validates the static page contract.

**Tech Stack:** Static HTML, vanilla JavaScript, existing CSS variables/styles, browser `localStorage`, browser Blob download API, Node.js smoke test.

---

### Task 1: Add Static Page Contract Test

**Files:**
- Create: `site/reviewer.test.js`

- [ ] **Step 1: Write the failing smoke test**

Create `site/reviewer.test.js` with assertions that `site/reviewer.html` exists and contains the key MVP hooks:

```javascript
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const htmlPath = path.join(__dirname, 'reviewer.html');
assert.ok(fs.existsSync(htmlPath), 'site/reviewer.html must exist');

const html = fs.readFileSync(htmlPath, 'utf8');

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
  'localStorage'
].forEach((needle) => {
  assert.ok(html.includes(needle), `reviewer.html missing ${needle}`);
});

console.log('reviewer.html smoke test passed');
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node site/reviewer.test.js`

Expected: FAIL with `site/reviewer.html must exist`.

### Task 2: Create Reviewer Page

**Files:**
- Create: `site/reviewer.html`

- [ ] **Step 1: Add the static HTML shell**

Create `site/reviewer.html` with the shared fonts, `style.css`, `progress.js`, `data.js`, and `header.js`. Add header navigation, desktop lesson sidebar, mobile lesson selector, EN/RU columns, review panel, issue summary, and export buttons.

- [ ] **Step 2: Add markdown rendering and lesson loading**

Implement simple markdown rendering locally in the page:

- headings `#`, `##`, `###`
- fenced code blocks
- blockquotes
- unordered and ordered list lines
- paragraphs

Fetch `../<lessonPath>/docs/en.md` and `../<lessonPath>/docs/ru.md`, render both columns, and assign review ids `p-0001`, `p-0002`, etc. Pair blocks by index and show a mismatch warning if counts differ.

- [ ] **Step 3: Add review state**

Store state in `localStorage` under `aifs:translation-review:v1`. Each lesson path maps to paragraph review records. On selection, update the panel fields. On flag/comment/edit changes, save immediately.

- [ ] **Step 4: Add export behavior**

Implement `buildReviewExport(lessonPath)` so exported JSON includes:

- `schemaVersion`
- `lessonPath`
- `source.en`
- `source.ru`
- `targetPath`
- `exportedAt`
- `paragraphs`

`Export lesson` downloads `<lesson-slug>.review.<timestamp>.json`. `Export all pending` downloads `translation-review-export.<timestamp>.json`.

- [ ] **Step 5: Add synchronized scroll**

Synchronize the EN/RU column scroll positions in both directions with a guard flag to avoid feedback loops.

### Task 3: Verify And Polish

**Files:**
- Verify: `site/reviewer.html`
- Verify: `site/reviewer.test.js`

- [ ] **Step 1: Run smoke test**

Run: `node site/reviewer.test.js`

Expected: PASS and output `reviewer.html smoke test passed`.

- [ ] **Step 2: Run local static server**

Run: `python -m http.server 8000`

Expected: server starts from repository root.

- [ ] **Step 3: Browser verification**

Open `http://localhost:8000/site/reviewer.html?path=phases/14-agent-engineering/01-the-agent-loop` and verify:

- EN/RU columns render.
- Selecting a paragraph highlights both sides.
- Flags and comments persist after reload.
- `Export lesson` downloads timestamped JSON with `targetPath`.
- `Export all pending` includes reviewed lesson data.

- [ ] **Step 4: Check git diff**

Run: `git diff -- site/reviewer.html site/reviewer.test.js`

Expected: diff only contains reviewer MVP files.
