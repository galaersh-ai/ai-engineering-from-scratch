"""Aggressive cleanup of ru.md artifacts."""
import re

RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"

with open(RU, encoding="utf-8") as f:
    text = f.read()

lines = text.split('\n')
cleaned = []
for line in lines:
    s = line.strip()
    # Skip ANY line that's translator meta-commentary
    if re.match(r'^\(?Translation', s, re.I):
        continue
    if re.match(r'^Конечно[,!]', s):
        continue
    if re.match(r'^Вот перевод', s):
        continue
    # Skip "Here is the translation" patterns
    if re.match(r'^Here is', s, re.I) and 'translat' in s.lower():
        continue
    cleaned.append(line)

text = '\n'.join(cleaned)

# Terminology fixes
text = text.replace('Хищерархическая', 'Иерархическая')
text = text.replace('хищерархическая', 'иерархическая')
text = text.replace('Хирархические', 'Иерархические')
text = text.replace('хирархические', 'иерархические')
text = text.replace('супервайзера', 'супервайзера')  # already correct
text = text.replace('Супервайзера', 'Супервайзера')

# Fix missing ## in headers (Концепция → ## Концепция)
# "Концепция" on its own line
text = re.sub(r'^Концепция$', '## Концепция', text, flags=re.M)

# Fix "### The shape" → "### Форма"
text = text.replace('### The shape', '### Форма')

# Fix "Где оно сияет" → "Где это работает"
text = text.replace('Где оно сияет', '## Где это работает')

# Remove multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text)

# Ensure trailing newline
if not text.endswith('\n'):
    text += '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
print(f"Cleaned v2: {len(text)} chars, {text.count(chr(10))+1} lines, {cyr} Cyrillic", flush=True)
