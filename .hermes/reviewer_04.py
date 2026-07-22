"""Reviewer stage: technical accuracy check via Ollama qwen2.5:14b"""
import json, urllib.request, time, sys

EN_PATH = "C:/Projects/AI_Project/ai-engineering-from-scratch/phases/16-multi-agent-and-swarms/04-primitive-model/docs/en.md"
RU_PATH = "C:/Projects/AI_Project/ai-engineering-from-scratch/phases/16-multi-agent-and-swarms/04-primitive-model/docs/ru.md"
OLLAMA = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:14b"

with open(EN_PATH, encoding="utf-8") as f:
    en_text = f.read()
with open(RU_PATH, encoding="utf-8") as f:
    ru_text = f.read()

review_prompt = f"""Ты — технический ревьюер перевода учебного материала по многоагентным системам.

ПРОВЕРЬ перевод на:
1. Техническую точность — не искажён ли смысл концепций (агент, handoff, shared state, orchestrator)
2. Терминологию — соответствие глоссарию (handoff→передача управления, orchestrator→оркестратор, shared state→общее состояние, primitive model→модель примитивов)
3. Полноту — все ли разделы, таблицы, списки сохранены
4. Не переведён ли исполняемый код, команды, пути

ОРИГИНАЛ (en):
{en_text}

ПЕРЕВОД (ru):
{ru_text}

Дай вердикт: PASS или REQUEST_CHANGES.
Если REQUEST_CHANGES — перечисли конкретные проблемы с номерами строк.
Если PASS — напиши только "verdict: PASS".

Формат ответа:
verdict: PASS|REQUEST_CHANGES
issues:
  - line N: описание проблемы
summary: краткий итог
"""

start = time.time()
data = json.dumps({"model": MODEL, "prompt": review_prompt, "stream": False, "options": {"num_predict": 2048}})
req = urllib.request.Request(OLLAMA, data=data.encode(), headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req, timeout=600)
result = json.loads(resp.read())
elapsed = time.time() - start

review = result.get("response", "")
print(f"REVIEWER done in {elapsed:.0f}s ({elapsed/60:.1f} min)")
print("---")
print(review)
print("---END---")

# Save review
with open("C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/review-phase16-04.txt", "w", encoding="utf-8") as f:
    f.write(review)
