# Как синхронизировать русский форк с оригиналом

## Автоматический контроль

GitHub Actions workflow `.github/workflows/upstream-watch.yml` запускается ежедневно и вручную через **Actions → Check upstream changes → Run workflow**.

Если upstream ушёл вперёд, workflow создаст issue с:

- последним переведённым commit;
- текущим upstream commit;
- списком новых commits;
- списком изменённых файлов;
- командами для локальной проверки.

Workflow ничего не мержит и не переводит сам.

## Ручной approve-процесс

1. Открыть issue с label `upstream-sync`.
2. Посмотреть diff:

```bash
git fetch upstream
LAST=<commit из UPSTREAM.md>
git diff "$LAST..upstream/main"
```

3. Решить, что переносим:
   - документацию — переводим;
   - код — обычно переносим как есть;
   - спорные изменения — отдельным PR.
4. Сделать commit с переводом.
5. Обновить `UPSTREAM.md` на новый upstream commit.
6. Закрыть issue.

## Почему не автомерж

После перевода файлы будут отличаться от оригинала, поэтому автоматический merge upstream → русский fork быстро начнёт создавать конфликты или ломать перевод. Безопаснее: автоматическое обнаружение, ручное принятие.
