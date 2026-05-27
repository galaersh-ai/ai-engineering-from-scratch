# AI Engineering From Scratch — русский перевод

Русская адаптация репозитория [rohitg00/ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch).

Оригинальный автор: **Rohit Ghumare**  
Лицензия: **MIT** — см. [`LICENSE`](LICENSE).

> Этот репозиторий — перевод и адаптация. Оригинальный проект остаётся источником истины для новых материалов и исправлений.

## Статус перевода

Актуальность относительно оригинала отслеживается в [`UPSTREAM.md`](UPSTREAM.md).

- Последний зафиксированный upstream commit: `32738eee8234d2f58140972d04aff3a00f1e66d7`
- Дата upstream commit: `2026-05-27`
- Сообщение: `chore(readme): sync counts`

## Как будем переводить

1. Переводим материалы постепенно, маленькими PR/commit'ами.
2. Сохраняем структуру оригинала, чтобы было проще сверять изменения.
3. Термины ведём единообразно через [`docs/TRANSLATION_GUIDE.md`](docs/TRANSLATION_GUIDE.md).
4. После синхронизации с оригиналом обновляем [`UPSTREAM.md`](UPSTREAM.md).

## Синхронизация с оригиналом

В репозитории настроен GitHub Actions workflow: `.github/workflows/upstream-watch.yml`.

Он не меняет файлы автоматически. Он проверяет оригинальный репозиторий и создаёт issue, если появились новые commits. Дальше изменения принимаются вручную: посмотреть diff → перевести → обновить `UPSTREAM.md` → закрыть issue.
