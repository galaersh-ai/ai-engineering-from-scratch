"""Chunked translation via ollama CLI (not API) — more reliable."""
import subprocess, sys, re, time, os

EN = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/en.md"
RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"
MODEL = "qwen2.5:7b"

with open(EN, encoding="utf-8") as f:
    en_text = f.read()

# Split into sections by ## headings
sections = re.split(r'(\n(?=##))', en_text)
# Merge the split markers
merged = []
for s in sections:
    if merged and not s.startswith('\n##'):
        merged[-1] += s
    else:
        merged.append(s)

# Filter empty
sections = [s.strip() for s in merged if s.strip()]
if not sections:
    sections = [en_text]

print(f"Split into {len(sections)} sections, total {len(en_text)} chars", flush=True)

system = "Ты — технический переводчик. Переведи фрагмент учебного Markdown с английского на русский. Сохрани ВСЮ Markdown-разметку. Код-блоки не трогай. Используй «Вы». supervisor→супервайзер. Выдай ТОЛЬКО перевод без пояснений."

ru_parts = []
for i, sec in enumerate(sections):
    prompt = f"{system}\n\nПЕРЕВЕДИ:\n\n{sec}"
    
    # Write prompt to temp file to avoid shell escaping issues
    tmp_in = f"/tmp/chunk-{i}.txt"
    with open(tmp_in, 'w', encoding='utf-8') as f:
        f.write(prompt)
    
    print(f"  [{i+1}/{len(sections)}] {len(sec)} chars...", flush=True, end='')
    start = time.time()
    
    try:
        result = subprocess.run(
            ['ollama', 'run', MODEL],
            input=prompt,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300
        )
        translated = result.stdout.strip()
        elapsed = time.time() - start
        print(f" {elapsed:.0f}s → {len(translated)} chars ✓", flush=True)
        ru_parts.append(translated)
    except subprocess.TimeoutExpired:
        print(f" TIMEOUT — keeping original", flush=True)
        ru_parts.append(sec)
    except Exception as e:
        print(f" ERROR: {e}", flush=True)
        ru_parts.append(sec)

ru_text = '\n\n'.join(ru_parts)

# Ensure trailing newline
if en_text.endswith('\n') and not ru_text.endswith('\n'):
    ru_text += '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(ru_text)

print(f"\nDONE: {len(en_text)}→{len(ru_text)} chars → {RU}", flush=True)
