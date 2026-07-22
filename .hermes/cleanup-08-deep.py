"""Deep clean lesson 08: strip all model commentary, fix headers."""
import re

RU = 'phases/16-multi-agent-and-swarms/08-role-specialization/docs/ru.md'

with open(RU, encoding='utf-8') as f:
    lines = f.readlines()

# Patterns for lines that are model commentary (not translation)
commentary = [
    # English
    r'^Here (is|are)',
    r'^Translation',
    r'^Note:',
    r'^Certainly',
    r'^Of course',
    r'^The (text|passage|original|following)',
    r'^This (text|appears|is)',
    r'^\(?(Here|Note|The text|This)',
    # Russian - explicit commentary
    r'^Вот перевод',
    r'^Перевел(и|а)?\s',
    r'^Для перевода',
    r'^Примечание:',
    r'^На русском( языке)?\s',
    r'^Это перевод',
    r'^На русский( язык)?\s',
    r'^Конечно[,!]?\s*(вот )?(перевод|на русск)',
    r'^Перевод на русский',
    r'^Переведенный текст',
    r'^Если (вам|тебе) (нужно|понадобится)',
    r'^Обратите внимание',
    r'^\(В русском языке\s',
    r'^Создайте его \(в зависимости',
    r'^Это наиболее подходящий',
    r'^Я перевел',
    r'^Текст переведен',
    r'^Данный текст',
    r'^Представленный',
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

# Fix headers
fixed = []
for i, line in enumerate(cleaned):
    s = line.rstrip('\n')
    # Heuristic: standalone short line, preceded by blank, not code/table/link — likely a section header
    prev_blank = (i == 0 or not cleaned[i-1].strip())
    if prev_blank and s and len(s) < 80 and not s.startswith('#') and not s.startswith('|') and not s.startswith('-') and not s.startswith('`') and not s.startswith('*') and 'http' not in s:
        if s.count(' ') <= 6 and '/' not in s and '\\' not in s:
            # If it looks like a section title, add ##
            known = {
                'Проблема': '## Проблема', 'Концепция': '## Концепция',
                'Упражнения': '## Упражнения', 'Ключевые термины': '## Ключевые термины',
                'Дополнительная литература': '## Дополнительная литература',
                'Дальнейшее чтение': '## Дальнейшее чтение',
                'Где это работает': '## Где это работает',
                'Где это ломается': '## Где это ломается',
                'Отправляем!': '## Отправляем!',
                'Используйте Его': '## Используйте Его',
                'Запустить:': '### Запустить:',
                'Каркасные отображения': '## Каркасные отображения',
                'Список проверки:': '### Список проверки:',
                'Критик vs проверяющий': '### Критик vs проверяющий',
            }
            if s in known:
                s = known[s]
            elif s[0].isupper() and s[-1] not in '.!?,:;':
                # Likely a header — but be conservative, only if < 6 words
                pass  # Skip auto-detection, too aggressive
    
    fixed.append(s + '\n')

text = ''.join(fixed)

# Fix the title
text = text.replace('# Специализация роля —', '# Специализация ролей —')

# Clean whitespace
text = re.sub(r'\n{3,}', '\n\n', text)
text = text.strip() + '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
print(f'{len(text)} chars, {text.count(chr(10))+1} lines, {cyr} Cyrillic')
