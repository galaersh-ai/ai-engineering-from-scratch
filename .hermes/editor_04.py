"""Editor stage: raw-socket Ollama call — no urllib timeout"""
import json, socket, time, re

RU_PATH = "C:/Projects/AI_Project/ai-engineering-from-scratch/phases/16-multi-agent-and-swarms/04-primitive-model/docs/ru.md"
OLLAMA_HOST = "localhost"
OLLAMA_PORT = 11434
MODEL = "qwen2.5:14b"

with open(RU_PATH, encoding="utf-8") as f:
    ru_text = f.read()

# Extract code blocks to restore them after editing
code_blocks = re.findall(r'```[\s\S]*?```', ru_text)

editor_prompt = f"""Ты — русский литературный редактор учебного материала по программированию.

Задача: отполируй текст. Сделай предложения естественными для русского уха. Убирай кальки с английского. Сохраняй «Вы» (с заглавной) + глаголы мн.ч. НЕ меняй заголовки, структуру, таблицы. НЕ трогай КОДОВЫЕ БЛОКИ (```...```). НЕ меняй термины: передача управления, оркестратор, общее состояние, примитив, агент.

Отдай ПОЛНЫЙ исправленный текст.

ТЕКСТ:
{ru_text}
"""

body = json.dumps({"model": MODEL, "prompt": editor_prompt, "stream": False, "options": {"num_predict": 16384}})
request = (
    f"POST /api/generate HTTP/1.1\r\n"
    f"Host: {OLLAMA_HOST}:{OLLAMA_PORT}\r\n"
    f"Content-Type: application/json\r\n"
    f"Content-Length: {len(body)}\r\n"
    f"Connection: close\r\n\r\n"
    f"{body}"
)

start = time.time()
sock = socket.create_connection((OLLAMA_HOST, OLLAMA_PORT), timeout=30)
sock.sendall(request.encode())
sock.settimeout(None)  # no read timeout

response = b""
while True:
    try:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk
    except:
        break
sock.close()

# Split headers and body
header_end = response.find(b"\r\n\r\n")
raw_body = response[header_end + 4:] if header_end >= 0 else response

# Handle chunked encoding
def decode_chunked(data):
    result = b""
    while data:
        crlf = data.find(b"\r\n")
        if crlf < 0:
            break
        try:
            size = int(data[:crlf].split(b";")[0], 16)
        except ValueError:
            break
        data = data[crlf + 2:]
        if size == 0:
            break
        result += data[:size]
        data = data[size + 2:]
    return result

decoded = decode_chunked(raw_body)
try:
    result = json.loads(decoded)
    edited = result.get("response", "")
except json.JSONDecodeError:
    # try direct JSON parse
    result = json.loads(raw_body)
    edited = result.get("response", "")

elapsed = time.time() - start

# Strip preamble if model echoed prompt
if "ТЕКСТ:" in edited:
    edited = edited.split("ТЕКСТ:")[-1].strip()

# Restore original code blocks
orig_iter = iter(code_blocks)
edited = re.sub(r'```[\s\S]*?```', lambda _: next(orig_iter, '```\n```'), edited)

with open(RU_PATH, "w", encoding="utf-8") as f:
    f.write(edited)

print(f"EDITOR done in {elapsed:.0f}s ({elapsed/60:.1f} min)")
print(f"Edited chars: {len(edited)}")
print(f"Code blocks restored: {len(code_blocks)}")
print("---END---")
