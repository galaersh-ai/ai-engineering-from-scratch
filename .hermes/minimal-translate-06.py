"""Translate en.md paragraph-by-paragraph via Ollama API, NO system prompt."""
import json, urllib.request, time, sys, re, os

EN = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/en.md"
RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"
OLLAMA = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:7b"

with open(EN, encoding="utf-8") as f:
    en_text = f.read()

# Split by double newline
paragraphs = re.split(r'\n\n+', en_text)
print(f"Source: {len(en_text)} chars, {len(paragraphs)} paragraphs", flush=True)

ru_parts = []
for i, para in enumerate(paragraphs):
    stripped = para.strip()
    
    # Code blocks — keep as-is
    if stripped.startswith('```') or stripped.startswith('~~~'):
        ru_parts.append(para)
        print(f"  [{i+1}/{len(paragraphs)}] code — kept", flush=True)
        continue
    
    # Empty/short
    if len(stripped) < 3:
        ru_parts.append(para)
        continue
    
    # MINIMAL prompt — no system, no instructions
    prompt = f"Translate to Russian:\n\n{para}"
    
    print(f"  [{i+1}/{len(paragraphs)}] {len(para)} chars...", flush=True, end='')
    start = time.time()
    
    try:
        data = json.dumps({
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": max(100, len(para)*3), "temperature": 0.1}
        })
        req = urllib.request.Request(OLLAMA, data=data.encode(), headers={"Content-Type": "application/json"})
        resp = urllib.request.urlopen(req, timeout=180)
        result = json.loads(resp.read())
        translated = result.get("response", "").strip()
        
        if translated and translated != para and len(translated) > 5:
            ru_parts.append(translated)
            elapsed = time.time() - start
            print(f" {elapsed:.0f}s ✓", flush=True)
        else:
            ru_parts.append(para)
            print(f" EMPTY/ECHO — kept original", flush=True)
    except Exception as e:
        elapsed = time.time() - start
        ru_parts.append(para)
        print(f" {elapsed:.0f}s ERROR: {e}", flush=True)
    time.sleep(0.25)

# Reconstruct with original separation
ru_text = '\n\n'.join(ru_parts)
if en_text.endswith('\n') and not ru_text.endswith('\n'):
    ru_text += '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(ru_text)

cyr = sum(1 for c in ru_text if 'А' <= c <= 'я' or c in 'Ёё')
print(f"\nDONE: {len(en_text)}→{len(ru_text)} chars, ~{cyr} Cyrillic, saved to {RU}", flush=True)
