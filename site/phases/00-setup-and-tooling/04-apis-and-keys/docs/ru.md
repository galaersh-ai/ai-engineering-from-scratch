     1|# API и ключи
     2|
     3|> Все AI API работают одинаково: отправляете запрос, получаете ответ. Детали меняются, принцип неизменен.
     4|
     5|**Тип:** Сборка
     6|**Языки:** Python, TypeScript
     7|**Требования:** Фаза 0, Урок 01
     8|**Время:** ~30 минут
     9|
    10|## Цели обучения
    11|
    12|- Безопасно хранить API-ключи через переменные окружения и `.env`-файлы
    13|- Сделать вызов LLM API через Anthropic Python SDK и чистый HTTP
    14|- Сравнить форматы запросов/ответов через SDK и HTTP для отладки
    15|- Распознавать и обрабатывать типичные ошибки API: аутентификацию и лимиты запросов
    16|
    17|## Проблема
    18|
    19|Начиная с Фазы 11 Вы будете вызывать LLM API (Anthropic, OpenAI, Google). В Фазах 13–16 — создавать агентов, использующих эти API в циклах. Нужно знать, как работают ключи, как их безопасно хранить и как сделать первый вызов.
    20|
    21|## Концепция
    22|
    23|```mermaid
    24|sequenceDiagram
    25|    participant C as Your Code
    26|    participant S as API Server
    27|    C->>S: HTTP Request (with API key)
    28|    S->>C: HTTP Response (JSON)
    29|```
    30|
    31|У каждого API-вызова есть:
    32|1. Endpoint (URL)
    33|2. API-ключ (аутентификация)
    34|3. Тело запроса (что Вы хотите)
    35|4. Тело ответа (что получаете)
    36|
    37|## Собираем
    38|
    39|### Шаг 1: Безопасное хранение ключей
    40|
    41|Никогда не храни ключи в коде. Используй переменные окружения.
    42|
    43|```bash
    44|export ANTHROPIC_API_KEY="sk-ant-..."
    45|export OPENAI_API_KEY="sk-..."
    46|```
    47|
    48|Или `.env`-файл (добавь его в `.gitignore`):
    49|
    50|```
    51|ANTHROPIC_API_KEY=sk-ant-...
    52|OPENAI_API_KEY=sk-...
    53|```
    54|
    55|### Шаг 2: Первый вызов API (Python)
    56|
    57|```python
    58|import anthropic
    59|
    60|client = anthropic.Anthropic()
    61|
    62|response = client.messages.create(
    63|    model="claude-sonnet-4-20250514",
    64|    max_tokens=256,
    65|    messages=[{"role": "user", "content": "What is a neural network in one sentence?"}]
    66|)
    67|
    68|print(response.content[0].text)
    69|```
    70|
    71|### Шаг 3: Первый вызов API (TypeScript)
    72|
    73|```typescript
    74|import Anthropic from "@anthropic-ai/sdk";
    75|
    76|const client = new Anthropic();
    77|
    78|const response = await client.messages.create({
    79|  model: "claude-sonnet-4-20250514",
    80|  max_tokens: 256,
    81|  messages: [{ role: "user", content: "What is a neural network in one sentence?" }],
    82|});
    83|
    84|console.log(response.content[0].text);
    85|```
    86|
    87|### Шаг 4: Чистый HTTP (без SDK)
    88|
    89|```python
    90|import os
    91|import urllib.request
    92|import json
    93|
    94|url = "https://api.anthropic.com/v1/messages"
    95|headers = {
    96|    "Content-Type": "application/json",
    97|    "x-api-key": os.environ["ANTHROPIC_API_KEY"],
    98|    "anthropic-version": "2023-06-01",
    99|}
   100|body = json.dumps({
   101|    "model": "claude-sonnet-4-20250514",
   102|    "max_tokens": 256,
   103|    "messages": [{"role": "user", "content": "What is a neural network in one sentence?"}],
   104|}).encode()
   105|
   106|req = urllib.request.Request(url, data=body, headers=headers, method="POST")
   107|with urllib.request.urlopen(req) as resp:
   108|    result = json.loads(resp.read())
   109|    print(result["content"][0]["text"])
   110|```
   111|
   112|Именно это SDK делают под капотом. Понимание чистого HTTP помогает при отладке.
   113|
   114|## Используем
   115|
   116|Для этого курса:
   117|
   118|| API | Когда понадобится | Бесплатный уровень |
   119||-----|-------------------|--------------------|
   120|| Anthropic (Claude) | Фазы 11–16 (агенты, инструменты) | $5 кредит при регистрации |
   121|| OpenAI | Фаза 11 (сравнение) | $5 кредит при регистрации |
   122|| Hugging Face | Фазы 4–10 (модели, датасеты) | Бесплатно |
   123|
   124|Не нужно всё сразу. Настраивай, когда потребуется в уроке.
   125|
   126|## Результат
   127|
   128|Этот урок создаёт:
   129|- `outputs/prompt-api-troubleshooter.md` — диагностика типичных ошибок API
   130|
   131|## Упражнения
   132|
   133|1. Получите ключ Anthropic API и сделайте первый вызов
   134|2. Попробуй чистый HTTP и сравни формат ответа с SDK-версией
   135|3. Намеренно используйте неверный ключ и прочитайте сообщение об ошибке
   136|
   137|## Ключевые термины
   138|
   139|| Термин | Что говорят | Что на самом деле |
   140||--------|------------|-------------------|
   141|| API-ключ | «Пароль для API» | Уникальная строка, идентифицирующая аккаунт и авторизующая запросы |
   142|| Rate limit | «Меня троттлят» | Максимум запросов в минуту/час для предотвращения злоупотреблений и честного использования |
   143|| Токен | «Слово» (в контексте API) | Единица биллинга: входные и выходные токены считаются и оплачиваются отдельно |
   144|| Streaming | «Ответы в реальном времени» | Получение ответа слово за словом вместо ожидания полного ответа |
   145|
   146|---
   147|
   148|> 📝 **Перевод:** русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../glossary/GLOSSARY.ru.md)
   149|