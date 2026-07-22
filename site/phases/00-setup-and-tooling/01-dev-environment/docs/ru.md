     1|# Окружение разработчика
     2|
     3|> Инструменты формируют мышление. Настройте их один раз — настройте правильно.
     4|
     5|**Тип:** Сборка
     6|**Языки:** Python, Node.js, Rust
     7|**Требования:** Нет
     8|**Время:** ~45 минут
     9|
    10|## Цели обучения
    11|
    12|- Установить Python 3.11+, Node.js 20+ и Rust-тулчейны с нуля
    13|- Настроить виртуальные окружения и пакетные менеджеры для воспроизводимых сборок
    14|- Проверить доступ к GPU через CUDA/MPS и запустить тестовую тензорную операцию
    15|- Понять четырёхуровневый стек: система, пакеты, рантаймы, AI-библиотеки
    16|
    17|## Проблема
    18|
    19|Вы собираетесь изучать AI-инжиниринг в 200+ уроках на Python, TypeScript, Rust и Julia. Если Ваше окружение сломано, каждый урок превращается в борьбу с инструментами вместо обучения.
    20|
    21|Большинство пропускает настройку окружения. А потом тратит часы на отладку ошибок импорта, конфликтов версий и отсутствующих CUDA-драйверов. Мы сделаем это один раз и правильно.
    22|
    23|## Концепция
    24|
    25|Окружение AI-разработчика состоит из четырёх уровней:
    26|
    27|```mermaid
    28|graph TD
    29|    A["4. AI/ML Libraries\nPyTorch, JAX, transformers, etc."] --> B["3. Language Runtimes\nPython 3.11+, Node 20+, Rust, Julia"]
    30|    B --> C["2. Package Managers\nuv, pnpm, cargo, juliaup"]
    31|    C --> D["1. System Foundation\nOS, shell, git, editor, GPU drivers"]
    32|```
    33|
    34|Устанавливаем снизу вверх. Каждый уровень зависит от предыдущего.
    35|
    36|## Собираем
    37|
    38|### Шаг 1: Системный фундамент
    39|
    40|Проверь систему и установи базовые инструменты.
    41|
    42|```bash
    43|# macOS
    44|xcode-select --install
    45|brew install git curl wget
    46|
    47|# Ubuntu/Debian
    48|sudo apt update && sudo apt install -y build-essential git curl wget
    49|
    50|# Windows (use WSL2)
    51|wsl --install -d Ubuntu-24.04
    52|```
    53|
    54|### Шаг 2: Python с uv
    55|
    56|Мы используем `uv` — он в 10–100 раз быстрее pip и автоматически управляет виртуальными окружениями.
    57|
    58|```bash
    59|curl -LsSf https://astral.sh/uv/install.sh | sh
    60|
    61|uv python install 3.12
    62|
    63|uv venv
    64|source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    65|
    66|uv pip install numpy matplotlib jupyter
    67|```
    68|
    69|Проверка:
    70|
    71|```python
    72|import sys
    73|print(f"Python {sys.version}")
    74|
    75|import numpy as np
    76|print(f"NumPy {np.__version__}")
    77|a = np.array([1, 2, 3])
    78|print(f"Vector: {a}, dot product with itself: {np.dot(a, a)}")
    79|```
    80|
    81|### Шаг 3: Node.js с pnpm
    82|
    83|Для уроков на TypeScript (агенты, MCP-серверы, веб-приложения).
    84|
    85|```bash
    86|curl -fsSL https://fnm.vercel.app/install | bash
    87|fnm install 22
    88|fnm use 22
    89|
    90|npm install -g pnpm
    91|
    92|node -e "console.log('Node', process.version)"
    93|```
    94|
    95|### Шаг 4: Rust
    96|
    97|Для уроков, критичных к производительности (инференс, системы).
    98|
    99|```bash
   100|curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   101|
   102|rustc --version
   103|cargo --version
   104|```
   105|
   106|### Шаг 5: Julia (опционально)
   107|
   108|Для уроков с интенсивной математикой, где Julia особенно хороша.
   109|
   110|```bash
   111|curl -fsSL https://install.julialang.org | sh
   112|
   113|julia -e 'println("Julia ", VERSION)'
   114|```
   115|
   116|### Шаг 6: Настройка GPU (если есть)
   117|
   118|```bash
   119|# NVIDIA
   120|nvidia-smi
   121|
   122|# Install PyTorch with CUDA
   123|uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   124|```
   125|
   126|```python
   127|import torch
   128|print(f"CUDA available: {torch.cuda.is_available()}")
   129|if torch.cuda.is_available():
   130|    print(f"GPU: {torch.cuda.get_device_name(0)}")
   131|```
   132|
   133|Нет GPU? Не проблема. Большинство уроков работает на CPU. Для уроков с интенсивным обучением используйте Google Colab или облачные GPU.
   134|
   135|### Шаг 7: Проверка всего
   136|
   137|Запусти проверочный скрипт:
   138|
   139|```bash
   140|python phases/00-setup-and-tooling/01-dev-environment/code/verify.py
   141|```
   142|
   143|## Используем
   144|
   145|Твоё окружение готово для каждого урока этого курса. Вот что и где понадобится:
   146|
   147|| Язык | Используется в | Пакетный менеджер |
   148||------|---------------|-------------------|
   149|| Python | Фазы 1–12 (ML, DL, NLP, CV, Audio, LLM) | uv |
   150|| TypeScript | Фазы 13–17 (инструменты, агенты, рои, инфраструктура) | pnpm |
   151|| Rust | Фазы 12, 15–17 (производительные системы) | cargo |
   152|| Julia | Фаза 1 (математические основы) | Pkg |
   153|
   154|## В продакшен
   155|
   156|Этот урок создаёт проверочный скрипт, который кто угодно может запустить для проверки своей настройки.
   157|
   158|См. `outputs/prompt-env-check.md` — промпт, помогающий AI-ассистентам диагностировать проблемы окружения.
   159|
   160|## Упражнения
   161|
   162|1. Запусти проверочный скрипт и исправь все ошибки
   163|2. Создай Python-виртуальное окружение для этого курса и установи PyTorch
   164|3. Напиши «hello world» на всех четырёх языках и запусти каждый
   165|
   166|---
   167|
   168|> 📝 **Перевод:** русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../glossary/GLOSSARY.ru.md)
   169|