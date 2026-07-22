"""Deep cleanup: remove Chinese text, commentary lines, fix untranslated sections."""
import re

RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"

with open(RU, encoding="utf-8") as f:
    text = f.read()

lines = text.split('\n')
cleaned = []
for line in lines:
    s = line.strip()
    
    # Skip lines with Chinese characters
    if re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', s):
        continue
    
    # Skip model commentary
    if any([re.match(p, s) for p in [
        r'^Перевод на русский',
        r'^Если вам нужно',
        r'^Для перевода',
        r'^Это перевод',
        r'^Это наиболее',
        r'^Это выражение',
        r'^В данном случае',
        r'^\(?Translation',
        r'^Конечно[,!]',
    ]]):
        continue
    
    cleaned.append(line)

text = '\n'.join(cleaned)

# Fix terminology
text = text.replace('Хищерархический', 'Иерархический')
text = text.replace('хищерархический', 'иерархический')

# Fix missing headers
text = text.replace('Где это ломается', '## Где это ломается')
text = text.replace('Ключевые термины:', '## Ключевые термины')
text = text.replace('Отправить его', '## Отправка')
text = text.replace('Используйте Его', '## Используйте Его')

# Fix exercises header
text = text.replace('## Упражнения', '## Упражнения\n')

# Clean up multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text)

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
print(f"Deep cleaned: {len(text)} chars, {text.count(chr(10))+1} lines, {cyr} Cyrillic", flush=True)
