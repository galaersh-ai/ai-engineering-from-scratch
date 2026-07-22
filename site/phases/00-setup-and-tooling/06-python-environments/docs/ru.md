     1|# Python-окружения
     2|
     3|> Ад зависимостей реален. Виртуальные окружения — лекарство.
     4|
     5|**Тип:** Сборка
     6|**Языки:** Shell
     7|**Требования:** Фаза 0, Урок 01
     8|**Время:** ~30 минут
     9|
    10|## Цели обучения
    11|
    12|- Создавать изолированные виртуальные окружения с помощью `uv`, `venv` или `conda`
    13|- Писать `pyproject.toml` с опциональными группами зависимостей и генерировать lock-файлы для воспроизводимости
    14|- Диагностировать и исправлять типичные проблемы: глобальные установки, смешивание pip/conda, несовместимость версий CUDA
    15|- Реализовать стратегию отдельных окружений для каждой фазы при конфликтующих зависимостях
    16|
    17|## Проблема
    18|
    19|Вы устанавливаете PyTorch 2.4 для проекта по файнтюнингу. На следующей неделе другому проекту нужен PyTorch 2.1, потому что его CUDA-сборка зафиксирована. Обновляете глобально — первый проект ломается. Откатываете — ломается второй.
    20|
    21|Это ад зависимостей. В AI/ML он происходит постоянно, потому что:
    22|
    23|- PyTorch, JAX и TensorFlow поставляют собственные CUDA-привязки
    24|- Библиотеки моделей фиксируют конкретные версии фреймворков
    25|- Глобальный `pip install` перезаписывает то, что было раньше
    26|- Сборки под CUDA 11.8 не работают с драйверами CUDA 12.x (и наоборот)
    27|
    28|Решение: каждый проект получает собственное изолированное окружение со своими пакетами.
    29|
    30|## Концепция
    31|
    32|```mermaid
    33|graph TD
    34|    subgraph without["Without virtual environments"]
    35|        SP[System Python] --> T24["torch 2.4.0 (CUDA 12.4)\nProject A needs this"]
    36|        SP --> T21["torch 2.1.0 (CUDA 11.8)\nProject B needs this"]
    37|        SP --> CONFLICT["CONFLICT: only one\ntorch version can exist"]
    38|    end
    39|
    40|    subgraph with["With virtual environments"]
    41|        PA["Project A (.venv/)"] --> PA1["torch 2.4.0 (CUDA 12.4)"]
    42|        PA --> PA2["transformers 4.44"]
    43|        PB["Project B (.venv/)"] --> PB1["torch 2.1.0 (CUDA 11.8)"]
    44|        PB --> PB2["diffusers 0.28"]
    45|    end
    46|```
    47|
    48|## Собираем
    49|
    50|### Вариант 1: uv venv (рекомендуется)
    51|
    52|`uv` — самый быстрый пакетный менеджер Python (в 10–100 раз быстрее pip). Управляет виртуальными окружениями, версиями Python и разрешением зависимостей в одном инструменте.
    53|
    54|```bash
    55|curl -LsSf https://astral.sh/uv/install.sh | sh
    56|
    57|uv python install 3.12
    58|
    59|cd your-project
    60|uv venv
    61|source .venv/bin/activate
    62|```
    63|
    64|Установка пакетов:
    65|
    66|```bash
    67|uv pip install torch numpy
    68|```
    69|
    70|Создание проекта с `pyproject.toml` одной командой:
    71|
    72|```bash
    73|uv init my-ai-project
    74|cd my-ai-project
    75|uv add torch numpy matplotlib
    76|```
    77|
    78|### Вариант 2: venv (встроенный)
    79|
    80|Если не можете установить `uv`, Python поставляется с `venv`:
    81|
    82|```bash
    83|python3 -m venv .venv
    84|source .venv/bin/activate  # Linux/macOS
    85|.venv\Scripts\activate     # Windows
    86|
    87|pip install torch numpy
    88|```
    89|
    90|Медленнее, чем `uv`, но работает везде, где установлен Python.
    91|
    92|### Вариант 3: conda (когда нужно)
    93|
    94|Conda управляет не-Python-зависимостями: CUDA toolkit, cuDNN, C-библиотеками. Используй, когда:
    95|
    96|- Нужна конкретная версия CUDA toolkit без системной установки
    97|- Работаешь на общем кластере, где нельзя ставить системные пакеты
    98|- Инструкция библиотеки говорит «используйте conda»
    99|
   100|```bash
   101|# Install miniconda (not the full Anaconda)
   102|curl -LsSf https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda.sh
   103|bash miniconda.sh -b
   104|
   105|conda create -n myproject python=3.12
   106|conda activate myproject
   107|
   108|conda install pytorch torchvision torchaudio pytorch-cuda=12.4 -c pytorch -c nvidia
   109|```
   110|
   111|Одно правило: если используете conda для окружения, используйте conda для всех пакетов в нём. Смешивание `pip install` в conda-окружении вызывает конфликты, которые больно отлаживать.
   112|
   113|### Для этого курса: стратегия отдельных окружений
   114|
   115|Можно создать одно окружение на весь курс. Не делайте этого. Разным фазам нужны разные (иногда конфликтующие) зависимости.
   116|
   117|Стратегия:
   118|
   119|```
   120|ai-engineering-from-scratch/
   121|├── .venv/                    <-- shared lightweight env for phases 0-3
   122|├── phases/
   123|│   ├── 04-neural-networks/
   124|│   │   └── .venv/            <-- PyTorch env
   125|│   ├── 05-cnns/
   126|│   │   └── .venv/            <-- same PyTorch env (symlink or shared)
   127|│   ├── 08-transformers/
   128|│   │   └── .venv/            <-- might need different transformer versions
   129|│   └── 11-llm-apis/
   130|│       └── .venv/            <-- API SDKs, no torch needed
   131|```
   132|
   133|Скрипт `code/env_setup.sh` создаёт базовое окружение для курса.
   134|
   135|## Основы pyproject.toml
   136|
   137|В каждом проекте на Python должен быть `pyproject.toml`. Он заменяет `setup.py`, `setup.cfg` и `requirements.txt` одним файлом.
   138|
   139|```toml
   140|[project]
   141|name = "ai-engineering-from-scratch"
   142|version = "0.1.0"
   143|requires-python = ">=3.11"
   144|dependencies = [
   145|    "numpy>=1.26",
   146|    "matplotlib>=3.8",
   147|    "jupyter>=1.0",
   148|    "scikit-learn>=1.4",
   149|]
   150|
   151|[project.optional-dependencies]
   152|torch = ["torch>=2.3", "torchvision>=0.18"]
   153|llm = ["anthropic>=0.39", "openai>=1.50"]
   154|```
   155|
   156|Установка:
   157|
   158|```bash
   159|uv pip install -e ".[torch]"    # base + PyTorch
   160|uv pip install -e ".[llm]"     # base + LLM SDKs
   161|uv pip install -e ".[torch,llm]" # everything
   162|```
   163|
   164|## Lock-файлы
   165|
   166|Lock-файл фиксирует каждую зависимость (включая транзитивные) до точной версии. Это гарантирует воспроизводимость: кто бы ни устанавливал из lock-файла, получает точно те же пакеты.
   167|
   168|```bash
   169|# uv generates uv.lock automatically when using uv add
   170|uv add numpy
   171|
   172|# pip-tools approach
   173|uv pip compile pyproject.toml -o requirements.lock
   174|uv pip install -r requirements.lock
   175|```
   176|
   177|Коммить lock-файл в git. Когда кто-то клонирует репо, он устанавливает из lock-файла и получает идентичные версии.
   178|
   179|## Типичные ошибки
   180|
   181|### 1. Глобальная установка
   182|
   183|```bash
   184|pip install torch  # BAD: installs to system Python
   185|
   186|source .venv/bin/activate
   187|pip install torch  # GOOD: installs to virtual environment
   188|```
   189|
   190|Проверь, куда идут пакеты:
   191|
   192|```bash
   193|which python       # should show .venv/bin/python, not /usr/bin/python
   194|which pip           # should show .venv/bin/pip
   195|```
   196|
   197|### 2. Смешивание pip и conda
   198|
   199|```bash
   200|conda create -n myenv python=3.12
   201|conda activate myenv
   202|conda install pytorch -c pytorch
   203|pip install some-other-package   # BAD: can break conda's dependency tracking
   204|conda install some-other-package # GOOD: let conda manage everything
   205|```
   206|
   207|Если вынужден использовать pip внутри conda (некоторые пакеты есть только в pip), сначала установи все conda-пакеты, затем pip-пакеты в последнюю очередь.
   208|
   209|### 3. Забыл активировать
   210|
   211|```bash
   212|python train.py           # uses system Python, missing packages
   213|source .venv/bin/activate
   214|python train.py           # uses project Python, packages found
   215|```
   216|
   217|В приглашении командной строки должно отображаться имя окружения:
   218|
   219|```
   220|(.venv) $ python train.py
   221|```
   222|
   223|### 4. Коммит .venv в git
   224|
   225|```bash
   226|echo ".venv/" >> .gitignore
   227|```
   228|
   229|Виртуальные окружения весят 200 MB–2 GB. Они локальные, не переносятся между машинами. Коммить `pyproject.toml` и lock-файл вместо этого.
   230|
   231|### 5. Несовместимость версий CUDA
   232|
   233|```bash
   234|nvidia-smi                # shows driver CUDA version (e.g., 12.4)
   235|python -c "import torch; print(torch.version.cuda)"  # shows PyTorch CUDA version
   236|
   237|# These must be compatible.
   238|# PyTorch CUDA version must be <= driver CUDA version.
   239|```
   240|
   241|## Используем
   242|
   243|Запусти скрипт настройки для создания окружения курса:
   244|
   245|```bash
   246|bash phases/00-setup-and-tooling/06-python-environments/code/env_setup.sh
   247|```
   248|
   249|Он создаёт `.venv` в корне репозитория с основными зависимостями и проверкой.
   250|
   251|## Упражнения
   252|
   253|1. Запусти `env_setup.sh` и убедись, что все проверки пройдены
   254|2. Создай второе виртуальное окружение, установи в него другую версию numpy и убедись, что окружения изолированы
   255|3. Напиши `pyproject.toml` для проекта, которому нужны и PyTorch, и Anthropic SDK
   256|4. Намеренно установите пакет глобально (без активации venv), посмотрите, куда он попал, затем удалите
   257|
   258|## Ключевые термины
   259|
   260|| Термин | Что говорят | Что на самом деле |
   261||--------|------------|-------------------|
   262|| Виртуальное окружение | «venv» | Изолированная директория с интерпретатором Python и пакетами, отдельно от системного Python |
   263|| Lock-файл | «Зафиксированные зависимости» | Файл со списком каждого пакета и его точной версии, гарантирующий идентичную установку на разных машинах |
   264|| pyproject.toml | «Новый setup.py» | Стандартный файл конфигурации проекта Python, заменяющий setup.py/setup.cfg/requirements.txt |
   265|| Транзитивная зависимость | «Зависимость зависимости» | Пакет B зависит от C; если устанавливаете A, зависящий от B, то C — транзитивная зависимость A |
   266|| Несовместимость CUDA | «Мой GPU не работает» | PyTorch скомпилирован под другую версию CUDA, чем поддерживает драйвер GPU |
   267|
   268|---
   269|
   270|> 📝 **Перевод:** русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../glossary/GLOSSARY.ru.md)
   271|