     1|# Настройка GPU и облака
     2|
     3|> Обучаться на CPU — нормально для учёбы. Обучать по-настоящему — нужен GPU.
     4|
     5|**Тип:** Сборка
     6|**Языки:** Python
     7|**Требования:** Фаза 0, Урок 01
     8|**Время:** ~45 минут
     9|
    10|## Цели обучения
    11|
    12|- Проверить доступность локального GPU через `nvidia-smi` и CUDA API в PyTorch
    13|- Настроить Google Colab с бесплатным T4 GPU для облачных экспериментов
    14|- Сравнить скорость умножения матриц на CPU и GPU, измерить ускорение
    15|- Оценить максимальный размер модели, помещающейся в VRAM, по правилу fp16
    16|
    17|## Проблема
    18|
    19|Большинство уроков фаз 1–3 работают на CPU. Но когда дойдёте до обучения CNN, трансформеров или LLM (фазы 4+), понадобится ускорение GPU. То, что на CPU занимает 8 часов, на GPU — 10 минут.
    20|
    21|У тебя три варианта: локальный GPU, облачный GPU или Google Colab (бесплатно).
    22|
    23|## Концепция
    24|
    25|```
    26|Your options:
    27|
    28|1. Local NVIDIA GPU
    29|   Cost: $0 (you already have it)
    30|   Setup: Install CUDA + cuDNN
    31|   Best for: Regular use, large datasets
    32|
    33|2. Google Colab (free tier)
    34|   Cost: $0
    35|   Setup: None
    36|   Best for: Quick experiments, no GPU at home
    37|
    38|3. Cloud GPU (Lambda, RunPod, Vast.ai)
    39|   Cost: $0.20-2.00/hr
    40|   Setup: SSH + install
    41|   Best for: Serious training, large models
    42|```
    43|
    44|## Собираем
    45|
    46|### Вариант 1: Локальный NVIDIA GPU
    47|
    48|Проверь, есть ли он:
    49|
    50|```bash
    51|nvidia-smi
    52|```
    53|
    54|Установи PyTorch с CUDA:
    55|
    56|```python
    57|import torch
    58|
    59|print(f"CUDA available: {torch.cuda.is_available()}")
    60|print(f"CUDA version: {torch.version.cuda}")
    61|if torch.cuda.is_available():
    62|    print(f"GPU: {torch.cuda.get_device_name(0)}")
    63|    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    64|```
    65|
    66|### Вариант 2: Google Colab
    67|
    68|1. Перейди на [colab.research.google.com](https://colab.research.google.com)
    69|2. Runtime > Change runtime type > T4 GPU
    70|3. Запусти `!nvidia-smi` для проверки
    71|
    72|Загружай ноутбуки курса напрямую в Colab.
    73|
    74|### Вариант 3: Облачный GPU
    75|
    76|Для Lambda Labs, RunPod или Vast.ai:
    77|
    78|```bash
    79|ssh user@your-gpu-instance
    80|
    81|pip install torch torchvision torchaudio
    82|python -c "import torch; print(torch.cuda.get_device_name(0))"
    83|```
    84|
    85|### Нет GPU? Не проблема.
    86|
    87|Большинство уроков работает на CPU. Те, которым нужен GPU, скажут об этом и предложат ссылки на Colab.
    88|
    89|```python
    90|device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    91|print(f"Using: {device}")
    92|```
    93|
    94|## Собираем: бенчмарк GPU vs CPU
    95|
    96|```python
    97|import torch
    98|import time
    99|
   100|size = 5000
   101|
   102|a_cpu = torch.randn(size, size)
   103|b_cpu = torch.randn(size, size)
   104|
   105|start = time.time()
   106|c_cpu = a_cpu @ b_cpu
   107|cpu_time = time.time() - start
   108|print(f"CPU: {cpu_time:.3f}s")
   109|
   110|if torch.cuda.is_available():
   111|    a_gpu = a_cpu.to("cuda")
   112|    b_gpu = b_cpu.to("cuda")
   113|
   114|    torch.cuda.synchronize()
   115|    start = time.time()
   116|    c_gpu = a_gpu @ b_gpu
   117|    torch.cuda.synchronize()
   118|    gpu_time = time.time() - start
   119|    print(f"GPU: {gpu_time:.3f}s")
   120|    print(f"Speedup: {cpu_time / gpu_time:.0f}x")
   121|```
   122|
   123|## Упражнения
   124|
   125|1. Запусти бенчмарк выше и сравни время CPU и GPU
   126|2. Если нет GPU, запусти в Google Colab и сравни
   127|3. Проверь объём видеопамяти и оцени максимальный размер модели (правило: 2 байта на параметр для fp16)
   128|
   129|## Ключевые термины
   130|
   131|| Термин | Что говорят | Что на самом деле |
   132||--------|------------|-------------------|
   133|| CUDA | «Программирование GPU» | Параллельная вычислительная платформа NVIDIA для запуска кода на GPU |
   134|| VRAM | «Память GPU» | Видеопамять на GPU, отдельная от системной RAM. Ограничивает размер модели. |
   135|| fp16 | «Половинная точность» | 16-битные числа с плавающей точкой, вдвое меньше памяти, чем fp32, с минимальной потерей точности |
   136|| Tensor Core | «Быстрое матричное железо» | Специализированные ядра GPU для умножения матриц, в 4–8 раз быстрее обычных |
   137|
   138|---
   139|
   140|> 📝 **Перевод:** русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../glossary/GLOSSARY.ru.md)
   141|