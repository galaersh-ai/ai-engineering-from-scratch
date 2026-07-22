"""Clean up ru.md artifacts from minimal translation."""
import re

RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"

with open(RU, encoding="utf-8") as f:
    text = f.read()

# Remove lines with model artifacts
lines = text.split('\n')
cleaned = []
for line in lines:
    s = line.strip()
    # Skip translator commentary
    if s.startswith('(Translation note:') or s.startswith('(Translation'):
        continue
    # Skip "Конечно! Вот перевод..." / "Конечно, вот перевод..."
    if re.match(r'^Конечно[,!]\s*(вот\s+)?перевод', s):
        continue
    cleaned.append(line)

text = '\n'.join(cleaned)

# Fix Хищерархическая → Иерархическая
text = text.replace('Хищерархическая', 'Иерархическая')
text = text.replace('хищерархическая', 'иерархическая')
text = text.replace('Хирархические', 'Иерархические')
text = text.replace('хирархические', 'иерархические')

# Remove multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text)

# Ensure trailing newline matches original
if not text.endswith('\n'):
    text += '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
print(f"Cleaned: {len(text)} chars, {text.count(chr(10))+1} lines, {cyr} Cyrillic", flush=True)
