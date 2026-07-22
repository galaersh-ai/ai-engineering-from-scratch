"""Translate en.md chunk-by-chunk via ollama run CLI, write incrementally."""
import subprocess, sys, re, time, os

EN = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/en.md"
RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"
MODEL = "qwen2.5:7b"

with open(EN, encoding="utf-8") as f:
    en_text = f.read()

print(f"Source: {len(en_text)} chars, {en_text.count(chr(10))+1} lines", flush=True)

# Simple split: by double newline (paragraphs)
paragraphs = re.split(r'\n\n+', en_text)
print(f"Split into {len(paragraphs)} paragraphs", flush=True)

system = "Ты — технический переводчик. Переведи на русский язык, сохранив Markdown-разметку. Код-блоки не трогай. supervisor→супервайзер. Выдай ТОЛЬКО перевод."

ru_lines = []
for i, para in enumerate(paragraphs):
    # Skip code blocks
    if para.strip().startswith('```'):
        ru_lines.append(para)
        print(f"  [{i+1}/{len(paragraphs)}] code block — kept", flush=True)
        continue

    # Skip very short/empty
    if len(para.strip()) < 5:
        ru_lines.append(para)
        continue

    prompt = f"{system}\n\nПереведи этот текст на русский язык:\n\n{para}"
    prompt_bytes = prompt.encode('utf-8')
    print(f"  [{i+1}/{len(paragraphs)}] {len(para)} chars ({len(prompt_bytes)} bytes prompt)...", flush=True, end='')
    
    start = time.time()
    try:
        result = subprocess.run(
            ['ollama', 'run', MODEL],
            input=prompt.encode('utf-8'),
            capture_output=True,
            timeout=120
        )
        elapsed = time.time() - start
        stdout = result.stdout.decode('utf-8', errors='replace').strip()
        stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
        
        if stderr:
            print(f" STDERR: {stderr[:100]}", flush=True)
        
        if stdout:
            # Remove spinner chars (braille patterns)
            clean = re.sub(r'[\u2800-\u28FF]+', '', stdout).strip()
            if clean:
                ru_lines.append(clean)
                print(f" {elapsed:.0f}s ✓ ({len(clean)} chars)", flush=True)
            else:
                ru_lines.append(para)  # fallback to original
                print(f" {elapsed:.0f}s ⚠ empty output, kept original", flush=True)
        else:
            ru_lines.append(para)
            print(f" {elapsed:.0f}s ⚠ no stdout, kept original (ret={result.returncode})", flush=True)
            
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start
        ru_lines.append(para)
        print(f" {elapsed:.0f}s TIMEOUT ⚠", flush=True)
    except Exception as e:
        elapsed = time.time() - start
        ru_lines.append(para)
        print(f" {elapsed:.0f}s ERROR: {e} ⚠", flush=True)

# Join
ru_text = '\n\n'.join(ru_lines)
if en_text.endswith('\n') and not ru_text.endswith('\n'):
    ru_text += '\n'

with open(RU, 'w', encoding='utf-8') as f:
    f.write(ru_text)

cyr_lines = sum(1 for c in ru_text if 'А' <= c <= 'я' or c in 'Ёё')
cyr_count = sum(1 for c in ru_text if 'А' <= c <= 'я' or c in 'Ёё')
print(f"\nDONE: {len(en_text)}→{len(ru_text)} chars, {cyr_count} Cyrillic chars → {RU}", flush=True)
