import re
RU = 'phases/16-multi-agent-and-swarms/08-role-specialization/docs/ru.md'

with open(RU, encoding='utf-8') as f:
    ru_lines = f.readlines()

commentary = [
    r'^Here (is|are)',
    r'^Translation|^Note:',
    r'^Certainly|^Of course',
    r'^The (text|passage|original|following)',
    r'^This (is|appears|text|translation)',
    r'^\(?(Here|Note|The text|This)',
    r'^Вот перевод|^Перевел',
    r'^Для перевода|^Примечание',
    r'^На русском|^Это перевод',
    r'^На русский',
    r'^Конечно[,!]?\s*(вот )?(перевод|на русск)',
    r'^Перевод на русский',
    r'^Переведенный текст',
]

cleaned = []
for line in ru_lines:
    s = line.strip()
    skip = any(re.match(p, s, re.I) for p in commentary)
    if not skip:
        cleaned.append(line)

section_map = {
    'Проблема': '## Проблема', 'Концепция': '## Концепция',
    'Упражнения': '## Упражнения', 'Ключевые термины': '## Ключевые термины',
    'Ключевые термины:': '## Ключевые термины',
    'Дополнительная литература': '## Дополнительная литература',
    'Дальнейшее чтение': '## Дальнейшее чтение',
    'Где это работает': '## Где это работает',
    'Где это ломается': '## Где это ломается',
}

fixed = []
for i, line in enumerate(cleaned):
    s = line.rstrip('\n')
    prev_blank = (i == 0 or not cleaned[i-1].strip())
    if s in section_map and prev_blank:
        s = section_map[s]
    fixed.append(s + '\n')

text = ''.join(fixed)
text = re.sub(r'\n{3,}', '\n\n', text)
text = text.strip() + '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
lines = text.count('\n') + 1
print(f'{len(text)} chars, {lines} lines, {cyr} Cyrillic')
