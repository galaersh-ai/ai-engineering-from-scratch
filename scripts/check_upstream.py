#!/usr/bin/env python3
"""Check upstream commits for the Russian translation fork.

This script is intentionally read-only. It prints GitHub Actions outputs and a
Markdown report. The workflow uses the report to create/update an issue.
"""
from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

UPSTREAM = "upstream/main"
UPSTREAM_MD = Path("UPSTREAM.md")
REPORT = Path("upstream-report.md")


def run(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def set_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as fh:
            fh.write(f"{name}={value}\n")
    else:
        print(f"{name}={value}")


def main() -> None:
    text = UPSTREAM_MD.read_text(encoding="utf-8")
    match = re.search(r"Last translated upstream commit:\s*`([0-9a-f]{7,40})`", text)
    if not match:
        raise SystemExit("Cannot find last translated upstream commit in UPSTREAM.md")

    last = match.group(1)
    current = run("git", "rev-parse", UPSTREAM)

    if last == current:
        set_output("has_changes", "false")
        set_output("last", last)
        set_output("current", current)
        REPORT.write_text("Upstream is already in sync.\n", encoding="utf-8")
        return

    commits = run("git", "log", "--oneline", f"{last}..{UPSTREAM}")
    files = run("git", "diff", "--name-status", f"{last}..{UPSTREAM}")
    stat = run("git", "diff", "--stat", f"{last}..{UPSTREAM}")

    body = f"""# Upstream changes detected

Original repository has new commits after the last translated upstream commit.

- Last translated: `{last}`
- Current upstream: `{current}`

## Commits

```text
{commits}
```

## Changed files

```text
{files}
```

## Diff stat

```text
{stat}
```

## Manual approve checklist

- [ ] Review diff
- [ ] Decide what to bring into the Russian adaptation
- [ ] Translate changed text
- [ ] Update `UPSTREAM.md` to `{current}`
- [ ] Close this issue

## Local commands

```bash
git fetch upstream
git log {last}..upstream/main --oneline
git diff --stat {last}..upstream/main
git diff {last}..upstream/main
```
"""
    REPORT.write_text(body, encoding="utf-8")
    set_output("has_changes", "true")
    set_output("last", last)
    set_output("current", current)


if __name__ == "__main__":
    main()
