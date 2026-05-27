# Upstream tracking

Оригинальный репозиторий: https://github.com/rohitg00/ai-engineering-from-scratch

## Последняя синхронизация перевода

- Upstream branch: `main`
- Last translated upstream commit: `32738eee8234d2f58140972d04aff3a00f1e66d7`
- Commit date: `2026-05-27`
- Commit message: `chore(readme): sync counts`

## Правило

Этот файл обновляется только после того, как изменения из оригинального репозитория просмотрены и русская версия вручную приведена в актуальное состояние.

## Проверка вручную

```bash
git fetch upstream
LAST=$(grep 'Last translated upstream commit:' UPSTREAM.md | sed 's/.*`\(.*\)`.*/\1/')
git log "$LAST..upstream/main" --oneline
git diff --stat "$LAST..upstream/main"
```

## Обновление после ручного перевода

```bash
NEW=$(git rev-parse upstream/main)
# затем обновить этот файл: commit, date, message
```
