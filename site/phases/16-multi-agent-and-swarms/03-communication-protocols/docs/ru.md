# Протоколы коммуникации

> Агенты, которые не говорят на одном языке — не команда. Они незнакомцы, кричащие в пустоту.

**Тип:** Практическая работа
**Языки:** TypeScript
**Предварительные требования:** Фаза 14 (Инженерия агента), Урок 16.01 (Почему мультиагентная система)
**Время:** ~120 минут

## Цели обучения

- Реализовать обнаружение и вызов инструментов через MCP, чтобы агенты могли использовать инструменты, предоставляемые внешними серверами
- Построить A2A-карту агента и эндпоинт задач, позволяющий одному агенту делегировать работу другому через HTTP
- Сравнить MCP (доступ к инструментам), A2A (агент-агент), ACP (корпоративный аудит) и ANP (децентрализованное доверие) и объяснить, какой протокол решает какую задачу
- Объединить несколько протоколов в единую систему, где агенты обнаруживают инструменты через MCP и делегируют задачи через A2A

## Проблема

Вы разделили систему на нескольких агентов. Исследователь, программист, ревьюер. Каждый хорош в своём деле. Но теперь нужно, чтобы они реально общались друг с другом.

Первая попытка очевидна: передавать строки. Исследователь возвращает кусок текста, программист парсит его как может. Это работает, пока программист не неправильно интерпретирует исследовательское резюме, или два агента не попадают в взаимную блокировку, ожидая друг друга, или вам не понадобится заставить агентов от разных команд работать вместе. Внезапно «просто передавать строки» перестаёт работать.

Это проблема протоколов коммуникации. Без общего контракта о том, как агенты обмениваются информацией, мультиагентные системы хрупкие, неаудитируемые и не масштабируются за пределы нескольких агентов, написанных лично вами.

Экосистема ИИ ответила четырьмя протоколами, каждый из которых решает свою часть проблемы:

- **MCP** для доступа к инструментам
- **A2A** для сотрудничества между агентами
- **ACP** для корпоративного аудита
- **ANP** для децентрализованной идентификации и доверия

Этот урок идёт глубоко. Вы прочитаете реальные форматы данных из каждого специфицирования, построите рабочие реализации и соедините все четыре протокола в единую систему.

## Концепция

### Ландшафт протоколов

Представьте эти четыре протокола как слои, каждый из которых отвечает на свой вопрос:

```mermaid
block-beta
  columns 1
  block:ANP["ANP — Как агенты доверяют незнакомцам?\nДецентрализованная идентификация (DID), E2EE, мета-протокол"]
  end
  block:A2A["A2A — Как агенты сотрудничают ради целей?\nКарты агентов, жизненный цикл задач, стриминг, переговоры"]
  end
  block:ACP["ACP — Как агенты общаются в аудитируемых системах?\nВыполнение, метаданные траектории, непрерывность сессии"]
  end
  block:MCP["MCP — Как агент использует инструмент?\nОбнаружение инструментов, выполнение, обмен контекстом"]
  end

  style ANP fill:#f3e8ff,stroke:#7c3aed
  style A2A fill:#dbeafe,stroke:#2563eb
  style ACP fill:#fef3c7,stroke:#d97706
  style MCP fill:#d1fae5,stroke:#059669
```

Они не конкуренты. Они решают разные задачи на разных уровнях.

### MCP (напоминание)

MCP подробно рассматривается в Фазе 13. Краткое напоминание: MCP стандартизирует способ подключения LLM к внешним инструментам и источникам данных. Это **клиент-серверный** протокол, в котором агент (клиент) обнаруживает и вызывает инструменты, предоставляемые сервером.

```mermaid
sequenceDiagram
    participant Agent as Агент (клиент)
    participant MCP1 as MCP-сервер<br/>(база данных, API, файлы)

    Agent->>MCP1: list tools
    MCP1-->>Agent: определения инструментов
    Agent->>MCP1: вызов инструмента X
    MCP1-->>Agent: результат
```

MCP — это коммуникация **агент-инструмент**. Он не помогает агентам общаться друг с другом.

### A2A (протокол Agent2Agent)

**Создатель:** Google (теперь под Linux Foundation как `lf.a2a.v1`)
**Версия спецификации:** 1.0.0
**Задача:** Как автономные агенты сотрудничают, ведут переговоры и делегируют задачи друг другу?

A2A — это протокол для **пирингового сотрудничества агентов**. Там, где MCP соединяет агент с инструментами, A2A соединяет агента с другими агентами. Каждый агент публикует **Карту агента** на известном URL, а другие агенты обнаруживают его, ведут переговоры и делегируют задачи.

#### Как работает A2A

```mermaid
sequenceDiagram
    participant Client as Клиентский агент
    participant Remote as Удалённый агент

    Client->>Remote: GET /.well-known/agent-card.json
    Remote-->>Client: Карта агента (навыки, режимы, безопасность)

    Client->>Remote: POST /message:send
    Remote-->>Client: Задача (отправлена/в работе)

    alt Опрос
        Client->>Remote: GET /tasks/{id}
        Remote-->>Client: Статус задачи + артефакты
    else Стриминг
        Client->>Remote: POST /message:stream
        Remote-->>Client: SSE: statusUpdate
        Remote-->>Client: SSE: artifactUpdate
        Remote-->>Client: SSE: completed
    end
```

#### Реальная карта агента

Вот как выглядит реальная A2A-карта агента. Обслуживается по адресу `GET /.well-known/agent-card.json`:

```json
{
  "name": "Research Agent",
  "description": "Searches documentation and summarizes findings",
  "version": "1.0.0",
  "supportedInterfaces": [
    {
      "url": "https://research-agent.example.com/a2a/v1",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0"
    },
    {
      "url": "https://research-agent.example.com/a2a/rest",
      "protocolBinding": "HTTP+JSON",
      "protocolVersion": "1.0"
    }
  ],
  "provider": {
    "organization": "Your Company",
    "url": "https://example.com"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": false
  },
  "defaultInputModes": ["text/plain", "application/json"],
  "defaultOutputModes": ["text/plain", "application/json"],
  "skills": [
    {
      "id": "web-research",
      "name": "Web Research",
      "description": "Searches the web and synthesizes findings",
      "tags": ["research", "search", "summarization"],
      "examples": ["Research the latest changes in React 19"]
    },
    {
      "id": "doc-analysis",
      "name": "Documentation Analysis",
      "description": "Reads and analyzes technical documentation",
      "tags": ["docs", "analysis"],
      "inputModes": ["text/plain", "application/pdf"],
      "outputModes": ["application/json"]
    }
  ],
  "securitySchemes": {
    "bearer": {
      "httpAuthSecurityScheme": {
        "scheme": "Bearer",
        "bearerFormat": "JWT"
      }
    }
  },
  "security": [{ "bearer": [] }]
}
```

Важные моменты:
- **Навыки (Skills)** — это то, что агент умеет делать. У каждого есть ID, теги и поддерживаемые MIME-типы ввода/вывода. Так клиентский агент определяет, может ли удалённый агент обработать его запрос.
- **supportedInterfaces** перечисляет несколько привязок протоколов. Один агент может одновременно говорить на JSON-RPC, REST и gRPC.
- **Безопасность** встроена в карту. Клиент знает, какая аутентификация нужна, до первого запроса.

#### Жизненный цикл задач

Задачи — это основная единица работы в A2A. Они проходят через определённые состояния:

```mermaid
stateDiagram-v2
    [*] --> submitted
    submitted --> working
    working --> input_required: нужна дополнительная информация
    input_required --> working: клиент отправляет данные
    working --> completed: успех
    working --> failed: ошибка
    working --> canceled: клиент отменяет
    submitted --> rejected: агент отклоняет

    completed --> [*]
    failed --> [*]
    canceled --> [*]
    rejected --> [*]

    note right of completed: Терминальные состояния неизменяемы.\nПоследующие задачи создаются\nв том же contextId.
```

Все 8 состояний (спецификация также определяет `UNSPECIFIED` как sentinel, здесь опущен):

| Состояние | Терминальное? | Значение |
|---|---|---|
| `TASK_STATE_SUBMITTED` | Нет | Принято, ещё не обрабатывается |
| `TASK_STATE_WORKING` | Нет | Активно обрабатывается |
| `TASK_STATE_INPUT_REQUIRED` | Нет | Агенту нужна дополнительная информация от клиента |
| `TASK_STATE_AUTH_REQUIRED` | Нет | Требуется аутентификация |
| `TASK_STATE_COMPLETED` | Да | Успешно завершено |
| `TASK_STATE_FAILED` | Да | Завершено с ошибкой |
| `TASK_STATE_CANCELED` | Да | Отменено до завершения |
| `TASK_STATE_REJECTED` | Да | Агент отклонил задачу |

Как только задача достигает терминального состояния, она неизменяема. Никаких дальнейших сообщений. Последующие задачи создаются в том же `contextId`.

#### Формат данных

A2A использует JSON-RPC 2.0. Вот как выглядит реальный обмен сообщениями:

**Клиент отправляет задачу:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "SendMessage",
  "params": {
    "message": {
      "messageId": "msg-001",
      "role": "ROLE_USER",
      "parts": [{ "text": "Research React 19 compiler features" }]
    },
    "configuration": {
      "acceptedOutputModes": ["text/plain", "application/json"],
      "historyLength": 10
    }
  }
}
```

**Агент отвечает задачей:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "task": {
      "id": "task-abc-123",
      "contextId": "ctx-xyz-789",
      "status": {
        "state": "TASK_STATE_COMPLETED",
        "timestamp": "2026-03-27T10:30:00Z"
      },
      "artifacts": [
        {
          "artifactId": "art-001",
          "name": "research-results",
          "parts": [{
            "data": {
              "findings": [
                "React 19 compiler auto-memoizes components",
                "No more manual useMemo/useCallback needed",
                "Compiler runs at build time, not runtime"
              ]
            },
            "mediaType": "application/json"
          }]
        }
      ]
    }
  }
}
```

**Стриминг через SSE:**
```text
POST /message:stream HTTP/1.1
Content-Type: application/json
A2A-Version: 1.0

data: {"task":{"id":"task-123","status":{"state":"TASK_STATE_WORKING"}}}

data: {"statusUpdate":{"taskId":"task-123","status":{"state":"TASK_STATE_WORKING","message":{"role":"ROLE_AGENT","parts":[{"text":"Searching documentation..."}]}}}}

data: {"artifactUpdate":{"taskId":"task-123","artifact":{"artifactId":"art-1","parts":[{"text":"partial findings..."}]},"append":true,"lastChunk":false}}

data: {"statusUpdate":{"taskId":"task-123","status":{"state":"TASK_STATE_COMPLETED"}}}
```

### ACP (протокол коммуникации агентов)

**Создатель:** IBM / BeeAI
**Версия спецификации:** 0.2.0 (OpenAPI 3.1.1)
**Статус:** Сливается с A2A под Linux Foundation
**Задача:** Как агенты общаются с полной аудитируемостью, непрерывностью сессий и отслеживанием траектории?

ACP — это **корпоративный протокол**. В отличие от того, что утверждают многие обзоры, ACP **не** использует JSON-LD. Это простой REST/JSON API, определённый через OpenAPI. То, что делает его особенным — это **TrajectoryMetadata**: каждый ответ агента может нести подробный журнал шагов рассуждений и вызовов инструментов, которые его породили.

```mermaid
sequenceDiagram
    participant Client
    participant ACP as ACP-агент
    participant Audit as Журнал аудита

    Client->>ACP: POST /runs (mode: sync)
    ACP->>ACP: Обработка запроса...
    ACP->>Audit: Логирование траектории:<br/>рассуждения + вызовы инструментов
    ACP-->>Client: Ответ + TrajectoryMetadata
    Note over Audit: Каждый шаг записывается:<br/>tool_name, tool_input,<br/>tool_output, reasoning
```

#### Обнаружение агентов в ACP

ACP определяет четыре метода обнаружения:

```mermaid
graph LR
    A[Обнаружение агентов] --> B["Runtime<br/>GET /agents"]
    A --> C["Open<br/>.well-known/agent.yml"]
    A --> D["Registry<br/>Централизованный каталог"]
    A --> E["Embedded<br/>Метки контейнеров"]

    style B fill:#dbeafe,stroke:#2563eb
    style C fill:#d1fae5,stroke:#059669
    style D fill:#fef3c7,stroke:#d97706
    style E fill:#f3e8ff,stroke:#7c3aed
```

**AgentManifest** проще, чем A2A-карта агента:

```json
{
  "name": "summarizer",
  "description": "Summarizes documents with source citations",
  "input_content_types": ["text/plain", "application/pdf"],
  "output_content_types": ["text/plain", "application/json"],
  "metadata": {
    "tags": ["summarization", "RAG"],
    "framework": "BeeAI",
    "capabilities": [
      {
        "name": "Document Summarization",
        "description": "Condenses long documents into key points"
      }
    ],
    "recommended_models": ["llama3.3:70b-instruct-fp16"],
    "license": "Apache-2.0",
    "programming_language": "Python"
  }
}
```

#### Жизненный цикл выполнения

ACP использует «Выполнения (Runs)» вместо «Задач (Tasks)». Выполнение — это запуск агента в трёх режимах:

| Режим | Поведение |
|---|---|
| `sync` | Блокирующий. Ответ содержит полный результат. |
| `async` | Немедленно возвращает 202. Опрос `GET /runs/{id}` для получения статуса. |
| `stream` | SSE-поток. События генерируются по мере работы агента. |

```mermaid
stateDiagram-v2
    [*] --> created
    created --> in_progress
    in_progress --> completed: успех
    in_progress --> failed: ошибка
    in_progress --> awaiting: нужен ввод
    awaiting --> in_progress: клиент возобновляет
    in_progress --> cancelling: запрос отмены
    cancelling --> cancelled

    completed --> [*]
    failed --> [*]
    cancelled --> [*]
```

#### TrajectoryMetadata (аудит- след)

Это ключевое отличие ACP. Каждая часть сообщения может содержать метаданные, показывающие, что именно делал агент:

```json
{
  "role": "agent/researcher",
  "parts": [
    {
      "content_type": "text/plain",
      "content": "The weather in San Francisco is 72F and sunny.",
      "metadata": {
        "kind": "trajectory",
        "message": "I need to check the weather for this location",
        "tool_name": "weather_api",
        "tool_input": { "location": "San Francisco, CA" },
        "tool_output": { "temperature": 72, "condition": "sunny" }
      }
    }
  ]
}
```

Для регулируемых отраслей это золото. Каждый ответ сопровождается доказуемой цепочкой рассуждений: какие инструменты вызывались, какие входные данные использовались, какие результаты были получены. Никакого чёрного ящика.

ACP также поддерживает **CitationMetadata** для атрибуции источников:

```json
{
  "kind": "citation",
  "start_index": 0,
  "end_index": 47,
  "url": "https://weather.gov/sf",
  "title": "NWS San Francisco Forecast"
}
```

### ANP (протокол сети агентов)

**Создатель:** Open-source сообщество (основано GaoWei Chang)
**Репозиторий:** [github.com/agent-network-protocol/AgentNetworkProtocol](https://github.com/agent-network-protocol/AgentNetworkProtocol)
**Задача:** Как агенты из разных организаций доверяют друг другу без центрального органа?

ANP — это **протокол децентрализованной идентификации**. Он строит доверие с помощью W3C Decentralized Identifiers (DID) и сквозного шифрования. В отличие от A2A, где вы обнаруживаете агентов через известные эндпоинты, ANP позволяет агентам криптографически доказывать свою личность.

ANP имеет три уровня:

```mermaid
graph TB
    subgraph Layer3["Уровень 3: Протокол приложения"]
        AD[Документы описания агентов]
        DISC[Эндпоинты обнаружения]
    end
    subgraph Layer2["Уровень 2: Мета-протокол"]
        NEG[Переговоры протоколов на основе ИИ]
        CODE[Динамическая генерация кода]
    end
    subgraph Layer1["Уровень 1: Идентификация и безопасная коммуникация"]
        DID["did:wba (W3C DID)"]
        HPKE[HPKE E2EE - RFC 9180]
        SIG[Проверка подписей]
    end

    Layer3 --> Layer2
    Layer2 --> Layer1

    style Layer1 fill:#d1fae5,stroke:#059669
    style Layer2 fill:#dbeafe,stroke:#2563eb
    style Layer3 fill:#f3e8ff,stroke:#7c3aed
```

#### DID-документы (реальная структура)

ANP использует собственный метод DID под названием `did:wba` (Web-Based Agent). DID `did:wba:example.com:user:alice` резолвится в `https://example.com/user/alice/did.json`:

```json
{
  "@context": [
    "https://www.w3.org/ns/did/v1",
    "https://w3id.org/security/suites/jws-2020/v1",
    "https://w3id.org/security/suites/secp256k1-2019/v1"
  ],
  "id": "did:wba:example.com:user:alice",
  "verificationMethod": [
    {
      "id": "did:wba:example.com:user:alice#key-1",
      "type": "EcdsaSecp256k1VerificationKey2019",
      "controller": "did:wba:example.com:user:alice",
      "publicKeyJwk": {
        "crv": "secp256k1",
        "x": "NtngWpJUr-rlNNbs0u-Aa8e16OwSJu6UiFf0Rdo1oJ4",
        "y": "qN1jKupJlFsPFc1UkWinqljv4YE0mq_Ickwnjgasvmo",
        "kty": "EC"
      }
    },
    {
      "id": "did:wba:example.com:user:alice#key-x25519-1",
      "type": "X25519KeyAgreementKey2019",
      "controller": "did:wba:example.com:user:alice",
      "publicKeyMultibase": "z9hFgmPVfmBZwRvFEyniQDBkz9LmV7gDEqytWyGZLmDXE"
    }
  ],
  "authentication": [
    "did:wba:example.com:user:alice#key-1"
  ],
  "keyAgreement": [
    "did:wba:example.com:user:alice#key-x25519-1"
  ],
  "humanAuthorization": [
    "did:wba:example.com:user:alice#key-1"
  ],
  "service": [
    {
      "id": "did:wba:example.com:user:alice#agent-description",
      "type": "AgentDescription",
      "serviceEndpoint": "https://example.com/agents/alice/ad.json"
    }
  ]
}
```

Важные моменты:
- **Разделение ключей**строго обеспечивается. Ключи подписи (secp256k1) отделены от ключей шифрования (X25519).
- **`humanAuthorization`** — уникальная особенность ANP. Эти ключи требуют явного одобрения человека (биометрия, пароль, HSM) перед использованием. Операции с высоким риском, مثل переводы средств, проходят через этот путь.
- Ключи **`keyAgreement`** используются для сквозного шифрования HPKE (RFC 9180).
- Раздел **service** ссылается на документ описания агента.

#### Как работает доверие в ANP

ANP **не** использует сеть доверия или граф рекомендаций. Доверие двустороннее и проверяется при каждом взаимодействии:

```mermaid
sequenceDiagram
    participant A as Агент A
    participant Domain as Домен агента A
    participant B as Агент B

    A->>B: HTTP-запрос + DID + подпись
    B->>Domain: Получение DID-документа (HTTPS)
    Domain-->>B: DID-документ + открытый ключ
    B->>B: Проверка подписи открытым ключом
    B-->>A: Выдача токена доступа
    A->>B: Последующие запросы используют токен
    Note over A,B: Доверие = проверка домена TLS<br/>+ проверка подписи DID<br/>+ принцип минимального доверия
```

Доверие исходит из трёх источников:
1. **TLS на уровне домена** проверяет хост DID-документа
2. **Криптографические подписи DID** проверяют личность агента
3. **Принцип минимального доверия** предоставляет только минимальные разрешения

Нет распространения доверия на основе сплетен или расчёта PageRank. Вы проверяете каждого агента напрямую через его DID.

#### Переговоры мета-протокола

Это самая новаторская особенность ANP. Когда два агента из разных экосистем встречаются, им не нужны заранее согласованные форматы данных. Они ведут переговоры на естественном языке:

```json
{
  "action": "protocolNegotiation",
  "sequenceId": 0,
  "candidateProtocols": "I can communicate using:\n1. JSON-RPC with hotel booking schema\n2. REST with OpenAPI 3.1 spec\n3. Natural language over HTTP",
  "modificationSummary": "Initial proposal",
  "status": "negotiating"
}
```

```mermaid
sequenceDiagram
    participant A as Агент A
    participant B as Агент B

    A->>B: protocolNegotiation (candidateProtocols)
    B->>A: protocolNegotiation (контрпредложение)
    A->>B: protocolNegotiation (принято)
    Note over A,B: Агенты динамически генерируют код<br/>для обработки agreed формата.<n>Макс. 10 раундов, затем тайм-аут.
```

Агенты обмениваются сообщениями (максимум 10 раундов), пока не договорятся о формате, а затем динамически генерируют код для его обработки. Значения статуса: `negotiating`, `rejected`, `accepted`, `timeout`.

Это означает, что два агента, которые никогда раньше не виделись, могут договориться о способе коммуникации без предварительного определения общего формата.

### Сравнение (исправленное)

| | MCP | A2A | ACP | ANP |
|---|---|---|---|---|
| **Создатель** | Anthropic | Google / Linux Foundation | IBM / BeeAI | Сообщество |
| **Формат спецификации** | JSON-RPC | JSON-RPC / REST / gRPC | OpenAPI 3.1 (REST) | JSON-RPC |
| **Основное применение** | Агент к инструменту | Агент к агенту | Агент к агенту | Агент к агенту |
| **Обнаружение** | Список инструментов | `/.well-known/agent-card.json` | `GET /agents`, `/.well-known/agent.yml` | `/.well-known/agent-descriptions`, эндпоинты DID-сервисов |
| **Идентификация** | Неявная (локальная) | Схемы безопасности (OAuth, mTLS) | Уровень сервера | W3C DID (`did:wba`) с E2EE |
| **Аудит-след** | Н/Д | Базовый (история задач) | TrajectoryMetadata (вызовы инструментов, рассуждения) | Не определён формально |
| **Автомат состояний** | Н/Д | 9 состояний задач | 7 состояний выполнения | Н/Д |
| **Стриминг** | Н/Д | SSE | SSE | Транспорт-независимый |
| **Уникальная особенность** | Схемы инструментов | Карты агентов + навыки | Аудит-след траектории | Переговоры мета-протокола |
| **Лучше всего для** | Инструменты и данные | Динамическое сотрудничество | Регулируемые отрасли | Кросс-организационное доверие |
| **Статус** | Стабильный | Стабильный (v1.0) | Сливается с A2A | Активная разработка |

### Как они работают вместе

Эти протоколы не взаимоисключающие. Реалистичная корпоративная система использует несколько:

```mermaid
graph TB
    subgraph org["Ваша организация"]
        RA[Исследовательский агент] <-->|A2A| CA[Кодирующий агент]
        RA -->|MCP| SS[Сервер поиска]
        CA -->|MCP| GS[Сервер GitHub]
        AUDIT["Все ответы агентов несут<br/>ACP TrajectoryMetadata"]
    end

    subgraph ext["Внешние (проверенные DID через ANP)"]
        EA[Внешний агент]
        PA[Партнёрский агент]
    end

    RA <-->|ANP + A2A| EA
    CA <-->|ANP + A2A| PA

    style org fill:#f8fafc,stroke:#334155
    style ext fill:#fef2f2,stroke:#991b1b
    style AUDIT fill:#fef3c7,stroke:#d97706
```

- **MCP** соединяет каждого агента с его инструментами
- **A2A** обеспечивает сотрудничество между агентами (внутренними и внешними)
- **ACP** оборачивает ответы в метаданные траектории для аудитируемости
- **ANP** обеспечивает проверку идентификации для агентов, которыми вы не управляете

## Реализуем

### Шаг 1: Основные типы сообщений

Каждая мультиагентная система начинается с формата сообщений. Мы определяем типы, которые соответствуют тому, что используют реальные протоколы:

```typescript
import crypto from "node:crypto";

type MessageRole = "user" | "agent";

type MessagePart =
  | { kind: "text"; text: string }
  | { kind: "data"; data: unknown; mediaType: string }
  | { kind: "file"; name: string; url: string; mediaType: string };

type TrajectoryEntry = {
  reasoning: string;
  toolName?: string;
  toolInput?: unknown;
  toolOutput?: unknown;
  timestamp: number;
};

type AgentMessage = {
  id: string;
  role: MessageRole;
  parts: MessagePart[];
  trajectory?: TrajectoryEntry[];
  replyTo?: string;
  timestamp: number;
};

function createMessage(
  role: MessageRole,
  parts: MessagePart[],
  replyTo?: string
): AgentMessage {
  return {
    id: crypto.randomUUID(),
    role,
    parts,
    replyTo,
    timestamp: Date.now(),
  };
}

function textMessage(role: MessageRole, text: string): AgentMessage {
  return createMessage(role, [{ kind: "text", text }]);
}
```

Обратите внимание: `MessagePart` — мультимодальный (текст, структурированные данные, файлы), точно как в реальных спецификациях A2A и ACP. `TrajectoryEntry` фиксирует цепочку рассуждений, соответствуя TrajectoryMetadata из ACP.

### Шаг 2: Карта агента A2A и реестр

Постройте обнаружение агентов, соответствующее реальной спецификации A2A:

```typescript
type Skill = {
  id: string;
  name: string;
  description: string;
  tags: string[];
  inputModes: string[];
  outputModes: string[];
};

type AgentCard = {
  name: string;
  description: string;
  version: string;
  url: string;
  capabilities: {
    streaming: boolean;
    pushNotifications: boolean;
  };
  defaultInputModes: string[];
  defaultOutputModes: string[];
  skills: Skill[];
};

class AgentRegistry {
  private cards: Map<string, AgentCard> = new Map();

  register(card: AgentCard) {
    this.cards.set(card.name, card);
  }

  discoverBySkillTag(tag: string): AgentCard[] {
    return [...this.cards.values()].filter((card) =>
      card.skills.some((skill) => skill.tags.includes(tag))
    );
  }

  discoverByInputMode(mimeType: string): AgentCard[] {
    return [...this.cards.values()].filter(
      (card) =>
        card.defaultInputModes.includes(mimeType) ||
        card.skills.some((skill) => skill.inputModes.includes(mimeType))
    );
  }

  resolve(name: string): AgentCard | undefined {
    return this.cards.get(name);
  }

  listAll(): AgentCard[] {
    return [...this.cards.values()];
  }
}
```

Это значительно богаче простого отображения «имя-возможность». Вы можете обнаруживать агентов по тегам навыков, по MIME-типам ввода или по имени — точно как поддерживает реальная спецификация A2A.

### Шаг 3: Жизненный цикл задач A2A

Постройте полный автомат состояний задач:

```typescript
type TaskState =
  | "submitted"
  | "working"
  | "input-required"
  | "auth-required"
  | "completed"
  | "failed"
  | "canceled"
  | "rejected";

const TERMINAL_STATES: TaskState[] = [
  "completed",
  "failed",
  "canceled",
  "rejected",
];

type TaskStatus = {
  state: TaskState;
  message?: AgentMessage;
  timestamp: number;
};

type Artifact = {
  id: string;
  name: string;
  parts: MessagePart[];
};

type Task = {
  id: string;
  contextId: string;
  status: TaskStatus;
  artifacts: Artifact[];
  history: AgentMessage[];
};

type TaskEvent =
  | { kind: "statusUpdate"; taskId: string; status: TaskStatus }
  | {
      kind: "artifactUpdate";
      taskId: string;
      artifact: Artifact;
      append: boolean;
      lastChunk: boolean;
    };

type TaskHandler = (
  task: Task,
  message: AgentMessage
) => AsyncGenerator<TaskEvent>;

class TaskManager {
  private tasks: Map<string, Task> = new Map();
  private handlers: Map<string, TaskHandler> = new Map();
  private listeners: Map<string, ((event: TaskEvent) => void)[]> = new Map();

  registerHandler(agentName: string, handler: TaskHandler) {
    this.handlers.set(agentName, handler);
  }

  subscribe(taskId: string, listener: (event: TaskEvent) => void) {
    const existing = this.listeners.get(taskId) ?? [];
    existing.push(listener);
    this.listeners.set(taskId, existing);
  }

  async sendMessage(
    agentName: string,
    message: AgentMessage,
    contextId?: string
  ): Promise<Task> {
    const handler = this.handlers.get(agentName);
    if (!handler) {
      const task = this.createTask(contextId);
      task.status = {
        state: "rejected",
        timestamp: Date.now(),
        message: textMessage("agent", `No handler for ${agentName}`),
      };
      return task;
    }

    const task = this.createTask(contextId);
    task.history.push(message);
    task.status = { state: "submitted", timestamp: Date.now() };

    this.processTask(task, handler, message).catch((err) => {
      task.status = {
        state: "failed",
        timestamp: Date.now(),
        message: textMessage("agent", String(err)),
      };
    });
    return task;
  }

  getTask(taskId: string): Task | undefined {
    return this.tasks.get(taskId);
  }

  cancelTask(taskId: string): boolean {
    const task = this.tasks.get(taskId);
    if (!task || TERMINAL_STATES.includes(task.status.state)) return false;
    task.status = { state: "canceled", timestamp: Date.now() };
    this.emit(taskId, {
      kind: "statusUpdate",
      taskId,
      status: task.status,
    });
    return true;
  }

  private createTask(contextId?: string): Task {
    const task: Task = {
      id: crypto.randomUUID(),
      contextId: contextId ?? crypto.randomUUID(),
      status: { state: "submitted", timestamp: Date.now() },
      artifacts: [],
      history: [],
    };
    this.tasks.set(task.id, task);
    return task;
  }

  private async processTask(
    task: Task,
    handler: TaskHandler,
    message: AgentMessage
  ) {
    task.status = { state: "working", timestamp: Date.now() };
    this.emit(task.id, {
      kind: "statusUpdate",
      taskId: task.id,
      status: task.status,
    });

    try {
      for await (const event of handler(task, message)) {
        if (TERMINAL_STATES.includes(task.status.state)) break;

        if (event.kind === "statusUpdate") {
          task.status = event.status;
        }
        if (event.kind === "artifactUpdate") {
          const existing = task.artifacts.find(
            (a) => a.id === event.artifact.id
          );
          if (existing && event.append) {
            existing.parts.push(...event.artifact.parts);
          } else {
            task.artifacts.push(event.artifact);
          }
        }
        this.emit(task.id, event);
      }
    } catch (err) {
      task.status = {
        state: "failed",
        timestamp: Date.now(),
        message: textMessage("agent", String(err)),
      };
      this.emit(task.id, {
        kind: "statusUpdate",
        taskId: task.id,
        status: task.status,
      });
    }
  }

  private emit(taskId: string, event: TaskEvent) {
    for (const listener of this.listeners.get(taskId) ?? []) {
      listener(event);
    }
  }
}
```

Это реализация реального жизненного цикла задач A2A: submitted, working, input-required, терминальные состояния. Обработчики — асинхронные генераторы, которые порождают события (обновления статуса и фрагменты артефактов), соответствующие модели стриминга SSE.

### Шаг 4: Аудит-след в стиле ACP

Оберните коммуникацию отслеживанием траектории:

```typescript
type AuditEntry = {
  runId: string;
  agentName: string;
  input: AgentMessage[];
  output: AgentMessage[];
  trajectory: TrajectoryEntry[];
  status: "created" | "in-progress" | "completed" | "failed" | "awaiting";
  startedAt: number;
  completedAt?: number;
  sessionId?: string;
};

class AuditableRunner {
  private log: AuditEntry[] = [];
  private handlers: Map<
    string,
    (input: AgentMessage[]) => Promise<{
      output: AgentMessage[];
      trajectory: TrajectoryEntry[];
    }>
  > = new Map();

  registerAgent(
    name: string,
    handler: (input: AgentMessage[]) => Promise<{
      output: AgentMessage[];
      trajectory: TrajectoryEntry[];
    }>
  ) {
    this.handlers.set(name, handler);
  }

  async run(
    agentName: string,
    input: AgentMessage[],
    sessionId?: string
  ): Promise<AuditEntry> {
    const entry: AuditEntry = {
      runId: crypto.randomUUID(),
      agentName,
      input: structuredClone(input),
      output: [],
      trajectory: [],
      status: "created",
      startedAt: Date.now(),
      sessionId,
    };
    this.log.push(entry);

    const handler = this.handlers.get(agentName);
    if (!handler) {
      entry.status = "failed";
      return entry;
    }

    entry.status = "in-progress";
    try {
      const result = await handler(input);
      entry.output = structuredClone(result.output);
      entry.trajectory = structuredClone(result.trajectory);
      entry.status = "completed";
      entry.completedAt = Date.now();
    } catch (err) {
      entry.status = "failed";
      entry.trajectory.push({
        reasoning: `Error: ${String(err)}`,
        timestamp: Date.now(),
      });
      entry.completedAt = Date.now();
    }
    return entry;
  }

  getFullAuditLog(): AuditEntry[] {
    return structuredClone(this.log);
  }

  getAuditLogForAgent(agentName: string): AuditEntry[] {
    return structuredClone(
      this.log.filter((e) => e.agentName === agentName)
    );
  }

  getAuditLogForSession(sessionId: string): AuditEntry[] {
    return structuredClone(
      this.log.filter((e) => e.sessionId === sessionId)
    );
  }

  getTrajectoryForRun(runId: string): TrajectoryEntry[] {
    const entry = this.log.find((e) => e.runId === runId);
    return entry ? structuredClone(entry.trajectory) : [];
  }
}
```

Каждый запуск агента генерирует полную запись аудита: что поступило, что вышло и полная траектория вызовов инструментов и шагов рассуждений между ними. Вы можете запрашивать по агенту, по сессии или по отдельному запуску.

### Шаг 5: Проверка идентификации в стиле ANP

Постройте идентификацию и проверку на основе DID:

```typescript
type VerificationMethod = {
  id: string;
  type: string;
  controller: string;
  publicKeyDer: string;
};

type DIDDocument = {
  id: string;
  verificationMethod: VerificationMethod[];
  authentication: string[];
  keyAgreement: string[];
  humanAuthorization: string[];
  service: { id: string; type: string; serviceEndpoint: string }[];
};

type AgentIdentity = {
  did: string;
  document: DIDDocument;
  privateKey: crypto.KeyObject;
  publicKey: crypto.KeyObject;
};

class IdentityRegistry {
  private documents: Map<string, DIDDocument> = new Map();

  publish(doc: DIDDocument) {
    this.documents.set(doc.id, doc);
  }

  resolve(did: string): DIDDocument | undefined {
    return this.documents.get(did);
  }

  verify(did: string, signature: string, payload: string): boolean {
    const doc = this.documents.get(did);
    if (!doc) return false;

    const authKeyIds = doc.authentication;
    const authKeys = doc.verificationMethod.filter((vm) =>
      authKeyIds.includes(vm.id)
    );

    for (const key of authKeys) {
      const publicKey = crypto.createPublicKey({
        key: Buffer.from(key.publicKeyDer, "base64"),
        format: "der",
        type: "spki",
      });
      const isValid = crypto.verify(
        null,
        Buffer.from(payload),
        publicKey,
        Buffer.from(signature, "hex")
      );
      if (isValid) return true;
    }
    return false;
  }

  requiresHumanAuth(did: string, operationKeyId: string): boolean {
    const doc = this.documents.get(did);
    if (!doc) return false;
    return doc.humanAuthorization.includes(operationKeyId);
  }
}

function createIdentity(domain: string, agentName: string): AgentIdentity {
  const did = `did:wba:${domain}:agent:${agentName}`;
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");

  const publicKeyDer = publicKey
    .export({ format: "der", type: "spki" })
    .toString("base64");

  const keyId = `${did}#key-1`;
  const encKeyId = `${did}#key-x25519-1`;

  const document: DIDDocument = {
    id: did,
    verificationMethod: [
      {
        id: keyId,
        type: "Ed25519VerificationKey2020",
        controller: did,
        publicKeyDer,
      },
      {
        id: encKeyId,
        type: "X25519KeyAgreementKey2019",
        controller: did,
        publicKeyDer,
      },
    ],
    authentication: [keyId],
    keyAgreement: [encKeyId],
    humanAuthorization: [keyId],
    service: [
      {
        id: `${did}#agent-description`,
        type: "AgentDescription",
        serviceEndpoint: `https://${domain}/agents/${agentName}/ad.json`,
      },
    ],
  };

  return { did, document, privateKey, publicKey };
}

function signPayload(identity: AgentIdentity, payload: string): string {
  return crypto
    .sign(null, Buffer.from(payload), identity.privateKey)
    .toString("hex");
}
```

Это зеркало реальной модели идентификации ANP: агенты имеют DID-документы с отдельными ключами аутентификации, согласования ключей и авторизации человека. `IdentityRegistry` имитирует резолвинг DID (в продакшене это были бы HTTP-запросы к домену агента).

### Шаг 6: Протокольный шлюз

Соедините все четыре протокола в единую систему:

```mermaid
graph LR
    REQ[Входящий запрос] --> ANP_V{ANP: Проверка DID}
    ANP_V -->|Валидный| A2A_D{A2A: Обнаружение агента}
    ANP_V -->|Невалидный| REJECT[Отклонить]
    A2A_D -->|Найден| ACP_A[ACP: Аудит выполнения]
    A2A_D -->|Не найден| REJECT
    ACP_A --> A2A_T[A2A: Создание задачи]
    A2A_T --> RESULT[Задача + запись аудита]

    style ANP_V fill:#d1fae5,stroke:#059669
    style A2A_D fill:#dbeafe,stroke:#2563eb
    style ACP_A fill:#fef3c7,stroke:#d97706
    style A2A_T fill:#dbeafe,stroke:#2563eb
```

```typescript
class ProtocolGateway {
  private registry: AgentRegistry;
  private taskManager: TaskManager;
  private auditRunner: AuditableRunner;
  private identityRegistry: IdentityRegistry;

  constructor(
    registry: AgentRegistry,
    taskManager: TaskManager,
    auditRunner: AuditableRunner,
    identityRegistry: IdentityRegistry
  ) {
    this.registry = registry;
    this.taskManager = taskManager;
    this.auditRunner = auditRunner;
    this.identityRegistry = identityRegistry;
  }

  async delegateTask(
    fromDid: string,
    signature: string,
    targetAgent: string,
    message: AgentMessage,
    sessionId?: string
  ): Promise<{ task: Task; audit: AuditEntry } | { error: string }> {
    if (!this.identityRegistry.verify(fromDid, signature, message.id)) {
      return { error: "Identity verification failed" };
    }

    const card = this.registry.resolve(targetAgent);
    if (!card) {
      return { error: `Agent ${targetAgent} not found in registry` };
    }

    const audit = await this.auditRunner.run(
      targetAgent,
      [message],
      sessionId
    );
    const task = await this.taskManager.sendMessage(targetAgent, message);

    return { task, audit };
  }

  discoverAndDelegate(
    fromDid: string,
    signature: string,
    skillTag: string,
    message: AgentMessage
  ): Promise<{ task: Task; audit: AuditEntry } | { error: string }> {
    const candidates = this.registry.discoverBySkillTag(skillTag);
    if (candidates.length === 0) {
      return Promise.resolve({
        error: `No agents found with skill tag: ${skillTag}`,
      });
    }
    return this.delegateTask(
      fromDid,
      signature,
      candidates[0].name,
      message
    );
  }
}
```

Шлюз делает четыре вещи за один вызов:
1. **ANP**: Проверяет личность вызывающего через подпись DID
2. **A2A**: Обнаруживает целевого агента и проверяет возможности
3. **ACP**: Оборачивает выполнение в аудит-след с траекторией
4. **A2A**: Создаёт задачу с полным отслеживанием жизненного цикла

### Шаг 7: Соединяем всё вместе

```typescript
async function protocolDemo() {
  const registry = new AgentRegistry();
  registry.register({
    name: "researcher",
    description: "Searches and summarizes findings",
    version: "1.0.0",
    url: "https://researcher.local/a2a/v1",
    capabilities: { streaming: true, pushNotifications: false },
    defaultInputModes: ["text/plain"],
    defaultOutputModes: ["text/plain", "application/json"],
    skills: [
      {
        id: "web-research",
        name: "Web Research",
        description: "Searches the web",
        tags: ["research", "search", "summarization"],
        inputModes: ["text/plain"],
        outputModes: ["application/json"],
      },
    ],
  });
  registry.register({
    name: "coder",
    description: "Writes code from specs",
    version: "1.0.0",
    url: "https://coder.local/a2a/v1",
    capabilities: { streaming: false, pushNotifications: false },
    defaultInputModes: ["text/plain", "application/json"],
    defaultOutputModes: ["text/plain"],
    skills: [
      {
        id: "code-gen",
        name: "Code Generation",
        description: "Generates code",
        tags: ["coding", "generation"],
        inputModes: ["text/plain", "application/json"],
        outputModes: ["text/plain"],
      },
    ],
  });

  const taskManager = new TaskManager();
  const auditRunner = new AuditableRunner();

  const researchTrajectory: TrajectoryEntry[] = [];

  taskManager.registerHandler(
    "researcher",
    async function* (task, message) {
      yield {
        kind: "statusUpdate" as const,
        taskId: task.id,
        status: { state: "working" as const, timestamp: Date.now() },
      };

      researchTrajectory.push({
        reasoning: "Searching for React 19 documentation",
        toolName: "web_search",
        toolInput: { query: "React 19 compiler features" },
        toolOutput: {
          results: ["react.dev/blog/react-19", "github.com/react/react"],
        },
        timestamp: Date.now(),
      });

      researchTrajectory.push({
        reasoning: "Extracting key findings from search results",
        toolName: "doc_analysis",
        toolInput: { url: "react.dev/blog/react-19" },
        toolOutput: {
          summary:
            "React 19 compiler auto-memoizes, no manual useMemo needed",
        },
        timestamp: Date.now(),
      });

      yield {
        kind: "artifactUpdate" as const,
        taskId: task.id,
        artifact: {
          id: crypto.randomUUID(),
          name: "research-results",
          parts: [
            {
              kind: "data" as const,
              data: {
                findings: [
                  "React 19 compiler auto-memoizes components",
                  "No more manual useMemo/useCallback needed",
                  "Compiler runs at build time, not runtime",
                ],
                sources: ["react.dev/blog/react-19"],
              },
              mediaType: "application/json",
            },
          ],
        },
        append: false,
        lastChunk: true,
      };

      yield {
        kind: "statusUpdate" as const,
        taskId: task.id,
        status: { state: "completed" as const, timestamp: Date.now() },
      };
    }
  );

  auditRunner.registerAgent("researcher", async () => ({
    output: [
      textMessage("agent", "React 19 compiler auto-memoizes components"),
    ],
    trajectory: researchTrajectory,
  }));

  const identityRegistry = new IdentityRegistry();

  const coderIdentity = createIdentity("coder.local", "coder");
  const researcherIdentity = createIdentity("researcher.local", "researcher");

  identityRegistry.publish(coderIdentity.document);
  identityRegistry.publish(researcherIdentity.document);

  const gateway = new ProtocolGateway(
    registry,
    taskManager,
    auditRunner,
    identityRegistry
  );

  console.log("=== Protocol Demo ===\n");

  console.log("1. Agent Discovery (A2A)");
  const researchAgents = registry.discoverBySkillTag("research");
  console.log(
    `   Found ${researchAgents.length} agent(s):`,
    researchAgents.map((a) => a.name)
  );

  console.log("\n2. Identity Verification (ANP)");
  const message = textMessage("user", "Research React 19 compiler features");
  const signature = signPayload(coderIdentity, message.id);
  const verified = identityRegistry.verify(
    coderIdentity.did,
    signature,
    message.id
  );
  console.log(`   Coder DID: ${coderIdentity.did}`);
  console.log(`   Signature verified: ${verified}`);

  console.log("\n3. Task Delegation (A2A + ACP + ANP)");
  const result = await gateway.delegateTask(
    coderIdentity.did,
    signature,
    "researcher",
    message,
    "session-001"
  );

  if ("error" in result) {
    console.log(`   Error: ${result.error}`);
    return;
  }

  console.log(`   Task ID: ${result.task.id}`);
  console.log(`   Task state: ${result.task.status.state}`);
  console.log(`   Artifacts: ${result.task.artifacts.length}`);

  console.log("\n4. Audit Trail (ACP)");
  console.log(`   Run ID: ${result.audit.runId}`);
  console.log(`   Status: ${result.audit.status}`);
  console.log(`   Trajectory steps: ${result.audit.trajectory.length}`);
  for (const step of result.audit.trajectory) {
    console.log(`     - ${step.reasoning}`);
    if (step.toolName) {
      console.log(`       Tool: ${step.toolName}`);
    }
  }

  console.log("\n5. Full Audit Log");
  const fullLog = auditRunner.getFullAuditLog();
  console.log(`   Total runs: ${fullLog.length}`);
  for (const entry of fullLog) {
    const duration = entry.completedAt
      ? `${entry.completedAt - entry.startedAt}ms`
      : "in-progress";
    console.log(`   ${entry.agentName}: ${entry.status} (${duration})`);
  }
}

protocolDemo().catch((err) => {
  console.error("Protocol demo failed:", err);
  process.exitCode = 1;
});
```

## Что ломается

Протоколы решают Happy path. Вот что ломается в продакшене:

**Дрейф схемы.** Агент A публикует Карту агента с `application/json` на выходе. Но JSON-схема меняется между версиями. Агент B парсит старый формат и получает мусор. Исправление: версионируйте свои навыки и схемы вывода. Спецификация A2A поддерживает `version` на Картах агентов именно для этого.

**Нарушение автомата состояний.** Обработчик агента порождает событие `completed`, а затем пытается породить ещё артефакты. Задача неизменяема. Ваш код молча отбрасывает обновления или выбрасывает исключение. Исправление: проверяйте терминальное состояние перед порождением. `TaskManager` выше обеспечивает это через `break` после терминальных состояний.

**Сбои разрешения доверия.** Агент A пытается проверить DID агента B, но домен агента B недоступен. DID-документ не может быть получен. Вы делаете fail open (принимаете непроверенных агентов) или fail closed (отклоняете всё)? ANP рекомендует fail closed с принципом минимального доверия.

**Раздувание траектории.** Логирование траектории ACP мощное, но дорогое. Сложный агент, делающий 200 вызовов инструментов за запуск, генерирует огромные записи аудита. Исправление: логируйте траекторию с настраиваемым уровнем детализации. Записывайте имена инструментов и ввод/вывод для compliance, пропускайте шаги рассуждений для нерегулируемых нагрузок.

**Громовой отар обнаружения.** 50 агентов одновременно запрашивают `GET /agents` при запуске. Исправление: кэшируйте Карты агентов с TTL, рассинхронизируйте интервалы обнаружения или используйте push-регистрацию вместо опроса.

## Применение

### Реальные реализации

**A2A** — самая зрелая. [Официальная спецификация](https://github.com/google/A2A) от Google — open-source под Linux Foundation. SDK для Python и TypeScript. Если вашим агентам нужно динамическое обнаружение и сотрудничество, начните с этого.

**ACP** сливается с A2A. [Проект BeeAI от IBM](https://github.com/i-am-bee/acp) создал ACP как REST-first альтернативу, но концепция метаданных траектории поглощается экосистемой A2A. Используйте паттерны ACP (логирование траектории, жизненный цикл выполнения), даже если используете A2A как транспорт.

**ANP** — самая экспериментальная. [Репозиторий сообщества](https://github.com/agent-network-protocol/AgentNetworkProtocol) имеет Python SDK (AgentConnect). Концепция переговоров мета-протокола действительно новаторская. Стоит наблюдать за кросс-организационными развёртываниями агентов.

**MCP** уже рассматривается в Фазе 13. Если вы хотите, чтобы агенты использовали инструменты, MCP — стандарт.

### Выбор правильного протокола

```mermaid
graph TD
    START{Агентам нужно<br/>использовать инструменты?}
    START -->|Да| MCP_R[Используйте MCP]
    START -->|Нет| TALK{Агентам нужно<br/>общаться друг с другом?}
    TALK -->|Нет| NONE[Вам не нужен<br/>протокол]
    TALK -->|Да| AUDIT{Нужны аудит-следы<br/>для compliance?}
    AUDIT -->|Да| ACP_R[A2A + ACP<br/>паттерны траектории]
    AUDIT -->|Нет| ORG{Все агенты<br/>внутри вашей организации?}
    ORG -->|Да| A2A_R[A2A<br/>Карты агентов + Задачи]
    ORG -->|Нет| INFRA{Общая<br/>инфраструктура?}
    INFRA -->|Да| BROKER[A2A + брокер сообщений]
    INFRA -->|Нет| ANP_R[ANP + A2A<br/>проверка DID]

    style MCP_R fill:#d1fae5,stroke:#059669
    style A2A_R fill:#dbeafe,stroke:#2563eb
    style ACP_R fill:#fef3c7,stroke:#d97706
    style ANP_R fill:#f3e8ff,stroke:#7c3aed
    style BROKER fill:#e0e7ff,stroke:#4338ca
```

## Результат

Этот урок даёт:
- `code/main.ts` -- полная реализация всех четырёх паттернов протоколов
- `outputs/prompt-protocol-selector.md` -- промпт, помогающий выбрать протоколы для вашей системы

## Упражнения

1. **Многошаговое делегирование задач.** Расширьте `TaskManager` так, чтобы обработчик агента мог делегировать подзадачи другим агентам. Исследователь получает задачу, делегирует подзадачи «поиск» и «резюмирование» двум специализированным агентам, ждёт завершения обоих, затем объединяет результаты в собственные артефакты.

2. **Стриминговый аудит-след.** Измените `AuditableRunner` для поддержки режима стриминга. Вместо ожидания полного результата порождайте обновления `AuditEntry` в реальном времени по мере добавления записей траектории. Используйте асинхронный генератор, создающий снимки аудита.

3. **Ротация DID.** Добавьте ротацию ключей в `IdentityRegistry`. Агент должен иметь возможность опубликовать новый DID-документ с обновлёнными ключами, сохраняя ссылку `previousDid`. Проверяющие должны принимать подписи как от текущего, так и от предыдущего ключа в течение льготного периода.

4. **Переговоры протоколов.** Реализуйте концепцию мета-протокола ANP. Два агента обмениваются сообщениями `protocolNegotiation` с кандидатными форматами (например, «Я говорю на JSON-RPC» vs «Я предпочитаю REST»). После максимум 3 раундов они соглашаются на формат или происходит тайм-аут. Согласованный формат определяет, какой `TaskManager` или `AuditableRunner` они используют.

5. **Ограниченный по скорости обнаружения.** Добавьте обёртку `RateLimitedRegistry`, которая кэширует запросы Карт агентов с настраиваемым TTL и ограничивает запросы обнаружения на агента в секунду. Смоделируйте громовую отару из 100 агентов, обнаруживающих друг друга при запуске, и измерьте разницу.

## Ключевые термины

| Термин | Что говорят | Что это на самом деле |
|------|----------------|----------------------|
| MCP | «Протокол для ИИ-инструментов» | Клиент-серверный протокол для обнаружения и использования инструментов агентами. Агент-инструмент, не агент-агент. |
| A2A | «Протокол агентов от Google» | Пиринговый протокол для сотрудничества агентов под Linux Foundation. Обнаружение через Карты агентов, 9-состояний жизненный цикл задач, стриминг через SSE. Поддерживает привязки JSON-RPC, REST и gRPC. |
| ACP | «Корпоративный обмен сообщениями агентов» | REST API от IBM/BeeAI для запусков агентов с TrajectoryMetadata: каждый ответ несёт полную цепочку рассуждений и вызовов инструментов. Сливается с A2A. |
| ANP | «Децентрализованная идентификация агентов» | Протокол сообщества, использующий `did:wba` (DID) для криптографической идентификации, HPKE для E2EE и ИИ-управляемые переговоры мета-протокола для агентов, которые никогда не виделись. |
| Карта агента | «Визитная карточка агента» | JSON-документ по адресу `/.well-known/agent-card.json`, описывающий навыки, поддерживаемые MIME-типы, схемы безопасности и привязки протоколов. |
| DID | «Децентрализованный ID» | Стандарт W3C для криптографически проверяемых идентификаций, размещённых на собственном домене агента. ANP использует метод `did:wba`. |
| TrajectoryMetadata | «Аудит-квитанция» | Механизм ACP для прикрепления шагов рассуждений, вызовов инструментов и их вводов/выводов к каждому ответу агента. |
| Мета-протокол | «Агенты ведут переговоры о том, как общаться» | Подход ANP, при котором агенты используют естественный язык для динамического согласования форматов данных, а затем генерируют код для их обработки. |
| Задача | «Единица работы» | Состоящий объект A2A, отслеживающий работу от отправки до завершения. Неизменяемый после терминального состояния. |

## Дополнительные материалы

- [Спецификация Google A2A](https://github.com/google/A2A) -- официальная спецификация и SDK (v1.0.0, Linux Foundation)
- [Спецификация IBM/BeeAI ACP](https://github.com/i-am-bee/acp) -- спецификация OpenAPI 3.1 для запусков агентов и метаданных траектории
- [Agent Network Protocol](https://github.com/agent-network-protocol/AgentNetworkProtocol) -- идентификация на основе DID, E2EE, переговоры мета-протокола
- [Документация Model Context Protocol](https://modelcontextprotocol.io/) -- спецификация MCP от Anthropic (рассматривается в Фазе 13)
- [W3C Decentralized Identifiers](https://www.w3.org/TR/did-core/) -- стандарт идентификации, лежащий в основе ANP
- [RFC 9180 (HPKE)](https://www.rfc-editor.org/rfc/rfc9180) -- схема шифрования, используемая ANP для E2EE
