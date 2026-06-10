# Translation Reviewer MVP Design

## Summary

Build a separate static review screen for comparing English and Russian lesson markdown side by side. The goal is to let a reviewer move through the existing lesson catalog, mark problematic Russian paragraphs, add comments, and export review data without changing `lesson.html` or writing directly back to `ru.md`.

## Chosen Approach

Create `site/reviewer.html` as a standalone static page that reuses the current site's data and visual language. It loads lesson metadata from `site/data.js`, resolves the current lesson from `?path=phases/.../...`, fetches the lesson markdown from:

- `../<lesson-path>/docs/en.md`
- `../<lesson-path>/docs/ru.md`

The page stores working review state in `localStorage` keyed by lesson path. Export downloads JSON files from the browser rather than writing directly to `outputs/review`, because a static HTML page cannot safely write files into the repository.

## Export Model

The primary export is one timestamped file per lesson:

```text
01-the-agent-loop.review.2026-06-10T191530.json
```

Each exported JSON includes a stable intended destination:

```json
{
  "targetPath": "outputs/review/14-agent-engineering/01-the-agent-loop.review.json"
}
```

This avoids accidental browser-level overwrites when a reviewer exports one chapter, moves to another, and later exports again before processing downloaded files. The MVP also includes `Export all pending`, which downloads a single JSON containing all review records currently stored in `localStorage`.

## Reviewer UI

The first screen is the usable review workspace, not a landing page:

- Fixed site header matching the current static site style.
- Desktop lesson sidebar using the same catalog data as the current lesson page.
- Mobile top lesson selector that uses the same lesson list when the sidebar would not fit.
- Two synchronized reading columns:
  - left: English
  - right: Russian
- A review panel for the selected Russian paragraph.
- A compact issue summary listing paragraphs with flags or comments.

On narrow screens, the two columns stack or switch into a single-column review flow while keeping the selected paragraph and actions reachable.

## Paragraph Model

The MVP treats block-level rendered markdown content as reviewable paragraphs when they are text-bearing blocks such as paragraphs, list items, blockquotes, and headings. Each reviewable block receives an index-based id:

```text
p-0001
p-0002
p-0003
```

English and Russian blocks are paired by index. This is intentionally simple for MVP and supports the current expected lesson structure. If counts differ, the UI still renders all blocks and shows a mismatch warning.

## Review Actions

For each Russian paragraph, the reviewer can:

- Select the paragraph.
- Toggle `bad_translation`.
- Toggle `needs_retranslation`.
- Add or edit a comment.
- Optionally edit the Russian paragraph locally in the browser for review context.

The edited Russian text is saved in review JSON only. The MVP does not write changes back to `ru.md`.

## Data Shape

Each lesson review export uses this shape:

```json
{
  "schemaVersion": 1,
  "lessonPath": "phases/14-agent-engineering/01-the-agent-loop",
  "source": {
    "en": "phases/14-agent-engineering/01-the-agent-loop/docs/en.md",
    "ru": "phases/14-agent-engineering/01-the-agent-loop/docs/ru.md"
  },
  "targetPath": "outputs/review/14-agent-engineering/01-the-agent-loop.review.json",
  "exportedAt": "2026-06-10T19:15:30.000Z",
  "paragraphs": [
    {
      "id": "p-0001",
      "index": 1,
      "enText": "...",
      "ruText": "...",
      "editedRuText": "...",
      "flags": {
        "bad_translation": true,
        "needs_retranslation": false
      },
      "comment": "..."
    }
  ]
}
```

Only paragraphs with flags, comments, or edited text need to be exported.

## Error Handling

- If `en.md` or `ru.md` cannot be loaded, show a readable error in that column.
- If no lesson path is provided, select the first readable lesson from the catalog.
- If markdown block counts differ, keep the page usable and show a warning with both counts.
- If `localStorage` is unavailable, keep the current in-memory session working and warn that refreshes will lose data.

## Testing And Verification

Manual verification is enough for this MVP because the site has no existing automated browser test harness. Verify:

- `reviewer.html` loads from the static site.
- A lesson can be selected from the catalog.
- English and Russian markdown render in separate columns.
- Paragraph selection highlights the paired blocks.
- Synchronized scroll works in both directions without feedback loops.
- Flags and comments persist after navigating away and returning.
- `Export lesson` downloads timestamped JSON with the expected `targetPath`.
- `Export all pending` includes multiple reviewed lessons.

## Deferred Work

- Direct write-back to `outputs/review/*.json`.
- Direct write-back or patch generation for `ru.md`.
- Server-side merge flow.
- Smarter paragraph alignment beyond index pairing.
