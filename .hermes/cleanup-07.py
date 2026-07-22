"""Deep cleanup of lesson 07 ru.md."""
import re

RU = "phases/16-multi-agent-and-swarms/07-society-of-mind-debate/docs/ru.md"
EN = "phases/16-multi-agent-and-swarms/07-society-of-mind-debate/docs/en.md"

with open(RU, encoding='utf-8') as f:
    ru_lines = f.readlines()

with open(EN, encoding='utf-8') as f:
    en_lines = f.readlines()

# Strategy: remove lines that are model commentary (not corresponding to any en line)
# Model commentary patterns
commentary = [
    r'^Here is the translation',
    r'^Translation:',
    r'^Certainly[!.]?\s*(here is|the following)',
    r"^The (text|passage|original) (is|appears|reads).*",
    r'^This (appears to be |is )?(a translation|an? .*document)',
    r"^\(?(Here|Note|The text|This text).*(?:English|translate|original)",
    r'^Я перевел',
    r'^Вот перевод',
    r'^Перевел текст',
    r'^Текст переведен',
    r'^Оригинальный текст',
    r'^Данный текст',
    r'^Представленный (текст|документ|урок)',
]

# Identify en headers to align 
en_headers = set()
for line in en_lines:
    s = line.strip()
    if s.startswith('#'):
        en_headers.add(s)

cleaned = []
skip_next = False

for i, line in enumerate(ru_lines):
    s = line.strip()
    
    # Skip commentary lines
    if not s:
        cleaned.append(line)
        continue
    
    # Check if this is a standalone commentary line
    is_commentary = False
    for pat in commentary:
        if re.match(pat, s, re.IGNORECASE):
            is_commentary = True
            break
    
    if is_commentary:
        # Skip this line and the next if it's the continuation
        skip_next = True
        continue
    
    if skip_next:
        skip_next = False
        # If the next line is blank, skip it too
        if not s:
            continue
    
    cleaned.append(line)

# Fix missing ## headers
fixed = []
for i, line in enumerate(cleaned):
    s = line.rstrip('\n')
    
    # If this line looks like a section title without #, and the corresponding en line has #
    if s and not s.startswith('#') and not s.startswith('|') and not s.startswith('-') and not s.startswith('`') and not s.startswith('*') and len(s) < 80:
        # Check if this might be a header
        # Look at previous line — if blank, likely a header
        prev_blank = (i == 0 or not cleaned[i-1].strip())
        # Look at next non-blank line
        next_nonblank = None
        for j in range(i+1, min(i+5, len(cleaned))):
            if cleaned[j].strip():
                next_nonblank = cleaned[j].strip()
                break
        if prev_blank and next_nonblank:
            # Simple heuristic: if the line has Title Case or is a known section name
            words = s.split()
            if len(words) <= 8:
                # Common section names
                section_map = {
                    'Проблема': '## Проблема',
                    'Концепция': '## Концепция',
                    'Форма': '### Форма',
                    'Упражнения': '## Упражнения',
                    'Ключевые термины': '## Ключевые термины',
                    'Дополнительная литература': '## Дополнительная литература',
                    'Где это работает': '## Где это работает',
                    'Где это ломается': '## Где это ломается',
                    'The shape': '### Форма',
                    'Problem': '## Проблема',
                    'Concept': '## Концепция',
                }
                if s in section_map:
                    s = section_map[s]
    
    fixed.append(s + '\n')

text = ''.join(fixed)

# Remove multiple blank lines
text = re.sub(r'\n{3,}', '\n\n', text)

# Remove trailing blank lines
text = text.rstrip() + '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
print(f"{len(text)} chars, {text.count(chr(10))+1} lines, {cyr} Cyrillic")
