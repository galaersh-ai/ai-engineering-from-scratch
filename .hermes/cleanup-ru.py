"""Generic cleanup for translated ru.md — strip model commentary, fix headers."""
import re, sys

RU = sys.argv[1] if len(sys.argv) > 1 else None
if not RU:
    print("Usage: cleanup.py <path/to/docs/ru.md>")
    sys.exit(1)

with open(RU, encoding='utf-8') as f:
    lines = f.readlines()

commentary = [
    r'^Here (is|are)',
    r'^Translation',
    r'^Note:',
    r'^Certainly',
    r'^Of course',
    r'^The (text|passage|original|following)',
    r'^This (text|appears|is)',
    r'^\(?(Here|Note|The text|This)',
    r'^Вот перевод',
    r'^Перевел',
    r'^Для перевода',
    r'^Примечание',
    r'^На русском',
    r'^Это перевод',
    r'^На русский',
    r'^Конечно[,!]?\s*(вот )?(перевод|на русск)',
    r'^Перевод на русский',
    r'^Переведенный текст',
    r'^Если (вам|тебе) (нужно|понадобится)',
    r'^Обратите внимание',
    r'^\(В русском языке',
    r'^Создайте его \(в зависимости',
    r'^Это наиболее подходящий',
    r'^Я перевел',
    r'^Текст переведен',
    r'^Данный текст',
    r'^Представленный',
    r'^\(При переводе',
]

cleaned = []
for line in lines:
    s = line.strip()
    if not s:
        cleaned.append(line)
        continue
    skip = any(re.match(p, s, re.IGNORECASE) for p in commentary)
    if not skip:
        cleaned.append(line)

# Fix common missing headers
header_map = {
    'Проблема': '## Проблема', 'Концепция': '## Концепция',
    'Упражнения': '## Упражнения', 'Ключевые термины': '## Ключевые термины',
    'Ключевые термины:': '## Ключевые термины',
    'Дополнительная литература': '## Дополнительная литература',
    'Дальнейшее чтение': '## Дальнейшее чтение',
    'Где это работает': '## Где это работает',
    'Где это ломается': '## Где это ломается',
    'Отправляем!': '## Отправляем!',
    'Каркасные отображения': '## Каркасные отображения',
    'Список проверки:': '### Список проверки:',
    'Критик vs проверяющий': '### Критик vs проверяющий',
}

fixed = []
for i, line in enumerate(cleaned):
    s = line.rstrip('\n')
    prev_blank = (i == 0 or not cleaned[i-1].strip())
    if s in header_map and prev_blank:
        s = header_map[s]
    fixed.append(s + '\n')

text = ''.join(fixed)
text = re.sub(r'\n{3,}', '\n\n', text)
text = text.strip() + '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
print(f'{len(text)} chars, {text.count(chr(10))+1} lines, {cyr} Cyrillic')
