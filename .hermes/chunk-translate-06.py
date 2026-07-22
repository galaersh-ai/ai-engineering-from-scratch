"""Chunked translation: translates en.md paragraph by paragraph."""
import json, urllib.request, time, sys, re, os

EN = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/en.md"
RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"
OLLAMA = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

with open(EN, encoding="utf-8") as f:
    en_text = f.read()

# Split into chunks: preserve code blocks intact, everything else by empty line
chunks = []
current = []
in_code = False

for line in en_text.split('\n'):
    if line.startswith('```'):
        if in_code:
            current.append(line)
            chunks.append('\n'.join(current))
            current = []
            in_code = False
        else:
            if current:
                chunks.append('\n'.join(current))
                current = []
            current.append(line)
            in_code = True
    elif in_code:
        current.append(line)
    elif line.strip() == '':
        if current:
            chunks.append('\n'.join(current))
            current = []
        current.append(line)
    else:
        current.append(line)

if current:
    chunks.append('\n'.join(current))

# Merge very small chunks (single empty lines) with neighbors
merged = []
for ch in chunks:
    if ch.strip() == '' and merged:
        merged[-1] = merged[-1] + '\n' + ch
    elif len(ch.strip()) < 10 and merged and not merged[-1].startswith('```'):
        merged[-1] = merged[-1] + '\n' + ch
    else:
        merged.append(ch)

chunks = merged
print(f"Split into {len(chunks)} chunks, total {len(en_text)} chars", flush=True)

system = "Ты — технический переводчик. Переведи фрагмент учебного Markdown с английского на русский. Сохрани Markdown-разметку. Код-блоки не трогай. Используй «Вы». Выдай ТОЛЬКО перевод."

ru_parts = []
for i, ch in enumerate(chunks):
    if ch.startswith('```'):
        ru_parts.append(ch)
        print(f"  [{i+1}/{len(chunks)}] CODE BLOCK — kept as-is", flush=True)
        continue

    ch_stripped = ch.strip()
    if not ch_stripped or len(ch_stripped) < 3:
        ru_parts.append(ch)
        print(f"  [{i+1}/{len(chunks)}] empty/short — kept", flush=True)
        continue

    # Small request
    data = json.dumps({
        "model": MODEL,
        "system": system,
        "prompt": ch,
        "stream": False,
        "options": {"num_predict": max(256, len(ch)*2), "temperature": 0.1}
    })
    try:
        req = urllib.request.Request(OLLAMA, data=data.encode(), headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=120)
        result = json.loads(resp.read())
        translated = result.get("response", ch)
        ru_parts.append(translated)
        print(f"  [{i+1}/{len(chunks)}] {len(ch)}→{len(translated)} chars ✓", flush=True)
    except Exception as e:
        print(f"  [{i+1}/{len(chunks)}] ERROR: {e} — keeping original", flush=True)
        ru_parts.append(ch)

    time.sleep(0.5)  # brief pause between requests

ru_text = '\n'.join(ru_parts)
with open(RU, 'w', encoding='utf-8') as f:
    f.write(ru_text)

print(f"\nDONE: {len(en_text)}→{len(ru_text)} chars, saved to {RU}", flush=True)
