     1|# Docker для AI
     2|
     3|> Контейнеры делают фразу «на моей машине работает» пережитком прошлого.
     4|
     5|**Тип:** Сборка
     6|**Языки:** Docker
     7|**Требования:** Фаза 0, Уроки 01 и 03
     8|**Время:** ~60 минут
     9|
    10|## Цели обучения
    11|
    12|- Собрать Docker-образ с поддержкой GPU, CUDA, PyTorch и AI-библиотеками из Dockerfile
    13|- Монтировать директории хоста как тома для сохранения моделей, датасетов и кода между пересборками
    14|- Настроить NVIDIA Container Toolkit для доступа к GPU внутри контейнеров
    15|- Оркестрировать мультисервисные AI-приложения (инференс-сервер + векторная БД) через Docker Compose
    16|
    17|## Проблема
    18|
    19|Ты обучил модель на ноутбуке с PyTorch 2.3, CUDA 12.4 и Python 3.12. У коллеги PyTorch 2.1, CUDA 11.8 и Python 3.10. Твоя модель падает на его машине. Dockerfile работает на обеих.
    20|
    21|AI-проекты — это кошмар зависимостей. Типичный стек включает Python, PyTorch, CUDA-драйверы, cuDNN, системные C-библиотеки и специализированные пакеты вроде flash-attn, требующие точных версий компилятора. Docker упаковывает всё это в единый образ, работающий идентично везде.
    22|
    23|## Концепция
    24|
    25|Docker оборачивает Ваш код, рантайм, библиотеки и системные инструменты в изолированную единицу — контейнер. Можно думать о нём как о легковесной виртуальной машине, только он разделяет ядро ОС хоста вместо запуска собственного, поэтому стартует за секунды, а не минуты.
    26|
    27|```mermaid
    28|graph TD
    29|    subgraph without["Without Docker"]
    30|        A1["Your machine<br/>Python 3.12<br/>CUDA 12.4<br/>PyTorch 2.3"] -->|crashes| X1["???"]
    31|        A2["Their machine<br/>Python 3.10<br/>CUDA 11.8<br/>PyTorch 2.1"] -->|crashes| X2["???"]
    32|        A3["Server<br/>Python 3.11<br/>CUDA 12.1<br/>PyTorch 2.2"] -->|crashes| X3["???"]
    33|    end
    34|
    35|    subgraph with_docker["With Docker — Same image everywhere"]
    36|        B1["Your machine<br/>Python 3.12 | CUDA 12.4<br/>PyTorch 2.3 | Your code"]
    37|        B2["Their machine<br/>Python 3.12 | CUDA 12.4<br/>PyTorch 2.3 | Your code"]
    38|        B3["Server<br/>Python 3.12 | CUDA 12.4<br/>PyTorch 2.3 | Your code"]
    39|    end
    40|```
    41|
    42|### Почему AI-проектам Docker нужен больше, чем остальным
    43|
    44|1. **GPU-драйверы хрупкие.** Код под CUDA 12.4 не работает на CUDA 11.8. Docker изолирует CUDA toolkit внутри контейнера, разделяя драйвер GPU хоста через NVIDIA Container Toolkit.
    45|
    46|2. **Веса моделей огромные.** Модель на 7B параметров — это 14 GB в fp16. Перекачивать при каждой пересборке не вариант. Тома Docker позволяют примонтировать директорию моделей с хоста.
    47|
    48|3. **Мультисервисные архитектуры — норма.** Реальное AI-приложение — не просто Python-скрипт. Это инференс-сервер, векторная БД для RAG, возможно, веб-фронтенд. Docker Compose оркестрирует всё одной командой.
    49|
    50|### Ключевой словарь
    51|
    52|| Термин | Значение |
    53||--------|----------|
    54|| Образ (Image) | Шаблон только для чтения. Твой рецепт. Собирается из Dockerfile. |
    55|| Контейнер (Container) | Запущенный экземпляр образа. Твоя кухня. |
    56|| Dockerfile | Инструкции по сборке образа. Слой за слоем. |
    57|| Том (Volume) | Постоянное хранилище, переживающее перезапуски контейнера. |
    58|| docker-compose | Инструмент для описания мультиконтейнерных приложений в YAML. |
    59|
    60|### Распространённые паттерны контейнеров в AI
    61|
    62|```
    63|Dev Container
    64|  Full toolkit. Editor support. Jupyter. Debugging tools.
    65|  Used during development and experimentation.
    66|
    67|Training Container
    68|  Minimal. Just the training script and dependencies.
    69|  Runs on GPU clusters. No editor, no Jupyter.
    70|
    71|Inference Container
    72|  Optimized for serving. Small image. Fast cold start.
    73|  Runs behind a load balancer in production.
    74|```
    75|
    76|## Собираем
    77|
    78|### Шаг 1: Установка Docker
    79|
    80|```bash
    81|# macOS
    82|brew install --cask docker
    83|open /Applications/Docker.app
    84|
    85|# Ubuntu
    86|curl -fsSL https://get.docker.com | sh
    87|sudo usermod -aG docker $USER
    88|# Log out and back in for group change to take effect
    89|```
    90|
    91|Проверка:
    92|
    93|```bash
    94|docker --version
    95|docker run hello-world
    96|```
    97|
    98|### Шаг 2: Установка NVIDIA Container Toolkit (Linux с NVIDIA GPU)
    99|
   100|Позволяет Docker-контейнерам получать доступ к GPU. Пользователи macOS и Windows (WSL2) могут пропустить — Docker Desktop обрабатывает проброс GPU иначе.
   101|
   102|```bash
   103|distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   104|curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
   105|curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
   106|    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
   107|    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
   108|
   109|sudo apt-get update
   110|sudo apt-get install -y nvidia-container-toolkit
   111|sudo nvidia-ctk runtime configure --runtime=docker
   112|sudo systemctl restart docker
   113|```
   114|
   115|Проверка доступа к GPU внутри контейнера:
   116|
   117|```bash
   118|docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi
   119|```
   120|
   121|Если видите информацию о GPU — toolkit работает.
   122|
   123|### Шаг 3: Понимание базовых образов
   124|
   125|Правильный выбор базового образа экономит часы отладки.
   126|
   127|```
   128|nvidia/cuda:12.4.1-devel-ubuntu22.04
   129|  Full CUDA toolkit. Compilers included.
   130|  Use for: building packages that need nvcc (flash-attn, bitsandbytes)
   131|  Size: ~4 GB
   132|
   133|nvidia/cuda:12.4.1-runtime-ubuntu22.04
   134|  CUDA runtime only. No compilers.
   135|  Use for: running pre-built code
   136|  Size: ~1.5 GB
   137|
   138|pytorch/pytorch:2.3.1-cuda12.4-cudnn9-runtime
   139|  PyTorch pre-installed on top of CUDA.
   140|  Use for: skipping the PyTorch install step
   141|  Size: ~6 GB
   142|
   143|python:3.12-slim
   144|  No CUDA. CPU only.
   145|  Use for: inference on CPU, lightweight tools
   146|  Size: ~150 MB
   147|```
   148|
   149|### Шаг 4: Написание Dockerfile для AI-разработки
   150|
   151|Вот Dockerfile из `code/Dockerfile`. Разберём его:
   152|
   153|```dockerfile
   154|FROM nvidia/cuda:12.4.1-devel-ubuntu22.04
   155|
   156|ENV DEBIAN_FRONTEND=noninteractive
   157|ENV PYTHONUNBUFFERED=1
   158|
   159|RUN apt-get update && apt-get install -y --no-install-recommends \
   160|    python3.12 \
   161|    python3.12-venv \
   162|    python3.12-dev \
   163|    python3-pip \
   164|    git \
   165|    curl \
   166|    build-essential \
   167|    && rm -rf /var/lib/apt/lists/*
   168|
   169|RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1
   170|
   171|RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel
   172|
   173|RUN python -m pip install --no-cache-dir \
   174|    torch==2.3.1 \
   175|    torchvision==0.18.1 \
   176|    torchaudio==2.3.1 \
   177|    --index-url https://download.pytorch.org/whl/cu124
   178|
   179|RUN python -m pip install --no-cache-dir \
   180|    numpy \
   181|    pandas \
   182|    scikit-learn \
   183|    matplotlib \
   184|    jupyter \
   185|    transformers \
   186|    datasets \
   187|    accelerate \
   188|    safetensors
   189|
   190|WORKDIR /workspace
   191|
   192|VOLUME ["/workspace", "/models"]
   193|
   194|EXPOSE 8888
   195|
   196|CMD ["python"]
   197|```
   198|
   199|Сборка:
   200|
   201|```bash
   202|docker build -t ai-dev -f phases/00-setup-and-tooling/07-docker-for-ai/code/Dockerfile .
   203|```
   204|
   205|Первый раз занимает время (загрузка базового образа CUDA + PyTorch). Последующие сборки используют кешированные слои.
   206|
   207|Запуск:
   208|
   209|```bash
   210|docker run --rm -it --gpus all \
   211|    -v $(pwd):/workspace \
   212|    -v ~/models:/models \
   213|    ai-dev python -c "import torch; print(f'PyTorch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"
   214|```
   215|
   216|Запуск Jupyter внутри контейнера:
   217|
   218|```bash
   219|docker run --rm -it --gpus all \
   220|    -v $(pwd):/workspace \
   221|    -v ~/models:/models \
   222|    -p 8888:8888 \
   223|    ai-dev jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
   224|```
   225|
   226|### Шаг 5: Монтирование томов для данных и моделей
   227|
   228|Монтирование томов критично для AI-работы. Без них Ваши 14 GB загрузок моделей исчезают при остановке контейнера.
   229|
   230|```bash
   231|# Mount your code
   232|-v $(pwd):/workspace
   233|
   234|# Mount a shared models directory
   235|-v ~/models:/models
   236|
   237|# Mount datasets
   238|-v ~/datasets:/data
   239|```
   240|
   241|В скрипте обучения загружай из примонтированного пути:
   242|
   243|```python
   244|from transformers import AutoModel
   245|
   246|model = AutoModel.from_pretrained("/models/llama-7b")
   247|```
   248|
   249|Модель живёт на файловой системе хоста. Пересобирай контейнер сколько угодно без повторных загрузок.
   250|
   251|### Шаг 6: Docker Compose для мультисервисных AI-приложений
   252|
   253|Реальному RAG-приложению нужны инференс-сервер и векторная БД. Docker Compose запускает оба одной командой.
   254|
   255|См. `code/docker-compose.yml`:
   256|
   257|```yaml
   258|services:
   259|  ai-dev:
   260|    build:
   261|      context: .
   262|      dockerfile: Dockerfile
   263|    deploy:
   264|      resources:
   265|        reservations:
   266|          devices:
   267|            - driver: nvidia
   268|              count: all
   269|              capabilities: [gpu]
   270|    volumes:
   271|      - ../../../:/workspace
   272|      - ~/models:/models
   273|      - ~/datasets:/data
   274|    ports:
   275|      - "8888:8888"
   276|    stdin_open: true
   277|    tty: true
   278|    command: jupyter notebook --ip=0.0.0.0 --port=8888 --no-browser --allow-root
   279|
   280|  qdrant:
   281|    image: qdrant/qdrant:v1.12.5
   282|    ports:
   283|      - "6333:6333"
   284|      - "6334:6334"
   285|    volumes:
   286|      - qdrant_data:/qdrant/storage
   287|
   288|volumes:
   289|  qdrant_data:
   290|```
   291|
   292|Запуск всего:
   293|
   294|```bash
   295|cd phases/00-setup-and-tooling/07-docker-for-ai/code
   296|docker compose up -d
   297|```
   298|
   299|Теперь AI-контейнер разработки может обращаться к векторной БД по адресу `http://qdrant:6333` по имени сервиса. Docker Compose автоматически создаёт общую сеть.
   300|
   301|Проверка соединения из AI-контейнера:
   302|
   303|```python
   304|from qdrant_client import QdrantClient
   305|
   306|client = QdrantClient(host="qdrant", port=6333)
   307|print(client.get_collections())
   308|```
   309|
   310|Остановка всего:
   311|
   312|```bash
   313|docker compose down
   314|```
   315|
   316|Добавь `-v` для удаления также тома qdrant:
   317|
   318|```bash
   319|docker compose down -v
   320|```
   321|
   322|### Шаг 7: Полезные команды Docker для AI
   323|
   324|```bash
   325|# List running containers
   326|docker ps
   327|
   328|# List all images and their sizes
   329|docker images
   330|
   331|# Remove unused images (reclaim disk space)
   332|docker system prune -a
   333|
   334|# Check GPU usage inside a running container
   335|docker exec -it <container_id> nvidia-smi
   336|
   337|# Copy a file from container to host
   338|docker cp <container_id>:/workspace/results.csv ./results.csv
   339|
   340|# View container logs
   341|docker logs -f <container_id>
   342|```
   343|
   344|## Используем
   345|
   346|Теперь у тебя есть воспроизводимое окружение AI-разработки. Для всего курса:
   347|
   348|- Используй `docker compose up` для запуска окружения разработки и векторной БД вместе
   349|- Монтируй код, модели и данные как тома — ничего не теряется между пересборками
   350|- Когда урок требует новый Python-пакет — добавь в Dockerfile и пересобери
   351|- Делись Dockerfile с коллегами. У них будет точно такое же окружение.
   352|
   353|### Нет GPU?
   354|
   355|Убери флаг `--gpus all` и блок NVIDIA deploy. Контейнер всё ещё работает для CPU-уроков. PyTorch автоматически определяет отсутствие CUDA и переключается на CPU.
   356|
   357|## Упражнения
   358|
   359|1. Собери Dockerfile и запусти `python -c "import torch; print(torch.__version__)"` внутри контейнера
   360|2. Запустите docker-compose стек и проверьте, что Qdrant доступен из AI-контейнера по `http://qdrant:6333/collections`
   361|3. Добавь `flask` в Dockerfile, пересобери и запусти простой API-сервер на порту 5000. Пробрось порт через `-p 5000:5000`
   362|4. Измерь размер образа через `docker images`. Попробуй сменить базовый образ с `devel` на `runtime` и сравни размеры
   363|
   364|## Ключевые термины
   365|
   366|| Термин | Что говорят | Что на самом деле |
   367||--------|------------|-------------------|
   368|| Контейнер | «Легковесная VM» | Изолированный процесс на ядре хоста, с собственной файловой системой и сетью |
   369|| Слой образа | «Закешированный шаг» | Каждая инструкция Dockerfile создаёт слой. Неизменённые слои кешируются — пересборки быстрые. |
   370|| NVIDIA Container Toolkit | «GPU в Docker» | Рантайм-хук, пробрасывающий GPU хоста в контейнеры через флаг `--gpus` |
   371|| Монтирование тома | «Общая папка» | Директория хоста, отображённая в контейнер. Изменения сохраняются после остановки контейнера. |
   372|| Базовый образ | «Отправная точка» | Образ в `FROM`, поверх которого строится Dockerfile. Определяет, что предустановлено. |
   373|
   374|---
   375|
   376|> 📝 **Перевод:** русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../glossary/GLOSSARY.ru.md)
   377|