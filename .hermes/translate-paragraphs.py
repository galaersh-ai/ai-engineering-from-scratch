"""Reusable paragraph-by-paragraph translator via Ollama API, no system prompt."""
import json, urllib.request, time, sys, os, re

EN = sys.argv[1] if len(sys.argv) > 1 else "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/en.md"
RU = EN.replace('/en.md', '/ru.md')

MODEL = "qwen2.5:7b"
URL = "http://localhost:11434/api/generate"

with open(EN, encoding='utf-8') as f:
    en_text = f.read()

# Split by double-newline (paragraphs)
paras = re.split(r'\n\n+', en_text)
paras = [p.strip() for p in paras if p.strip()]

print(f"Source: {len(en_text)} chars, {len(paras)} paragraphs", flush=True)

def is_code_block(para):
    return para.startswith('```') or para.strip().startswith('```')

def translate_chunk(chunk):
    if is_code_block(chunk):
        return chunk, 0
    if len(chunk) < 3:
        return chunk, 0
    
    prompt = f"Translate to Russian:\n\n{chunk}"
    data = json.dumps({
        'model': MODEL,
        'prompt': prompt,
        'stream': False,
        'options': {'temperature': 0.1, 'num_predict': min(len(chunk)*3, 4096)}
    })
    req = urllib.request.Request(URL, data=data.encode(), headers={'Content-Type': 'application/json'})
    
    start = time.time()
    try:
        resp = urllib.request.urlopen(req, timeout=180)
        result = json.loads(resp.read())
        elapsed = time.time() - start
        return result.get('response', '').strip(), elapsed
    except Exception as e:
        elapsed = time.time() - start
        print(f" ERROR: {e}", flush=True)
        return chunk, elapsed  # keep original on error

ru_parts = []
total_cyr = 0

for i, para in enumerate(paras):
    print(f"  [{i+1}/{len(paras)}] {len(para)} chars...", end="", flush=True)
    
    if is_code_block(para):
        print(" code — kept", flush=True)
        ru_parts.append(para)
        continue
    
    translated, elapsed = translate_chunk(para)
    
    if translated and translated != para:
        # Check if it's just echoed English (not real translation)
        cyr_count = sum(1 for c in translated if 'А' <= c <= 'я' or c in 'Ёё')
        if cyr_count > 0 or len(translated) < 20:
            print(f" {elapsed:.0f}s ✓", flush=True)
            ru_parts.append(translated)
            total_cyr += cyr_count
        else:
            print(f" EMPTY/ECHO — kept original", flush=True)
            ru_parts.append(para)
    else:
        print(f" {elapsed:.0f}s — kept original", flush=True)
        ru_parts.append(para)

# Assemble with proper spacing
result = []
for i, p in enumerate(ru_parts):
    if i > 0:
        # Preserve original spacing structure
        # If next piece looks like a new section (starts with #), ensure blank line
        if p.startswith('#'):
            result.append('')
    result.append(p)

final = '\n\n'.join(result)
if not final.endswith('\n'):
    final += '\n'

os.makedirs(os.path.dirname(RU), exist_ok=True)
with open(RU, 'w', encoding='utf-8') as f:
    f.write(final)

print(f"\nDONE: {len(en_text)}→{len(final)} chars, ~{total_cyr} Cyrillic → {RU}", flush=True)
