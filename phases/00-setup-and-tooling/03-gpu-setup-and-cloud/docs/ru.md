# Настройка GPU и облака

> Обучаться на CPU — нормально для учёбы. Обучать по-настоящему — нужен GPU.

**Тип:** Сборка
**Языки:** Python
**Требования:** Фаза 0, Урок 01
**Время:** ~45 минут

## Цели обучения

- Проверить доступность локального GPU через `nvidia-smi` и CUDA API в PyTorch
- Настроить Google Colab с бесплатным T4 GPU для облачных экспериментов
- Сравнить скорость умножения матриц на CPU и GPU, измерить ускорение
- Оценить максимальный размер модели, помещающейся в VRAM, по правилу fp16

## Проблема

Большинство уроков фаз 1–3 работают на CPU. Но когда дойдёшь до обучения CNN, трансформеров или LLM (фазы 4+), понадобится ускорение GPU. То, что на CPU занимает 8 часов, на GPU — 10 минут.

У тебя три варианта: локальный GPU, облачный GPU или Google Colab (бесплатно).

## Концепция

```
Your options:

1. Local NVIDIA GPU
   Cost: $0 (you already have it)
   Setup: Install CUDA + cuDNN
   Best for: Regular use, large datasets

2. Google Colab (free tier)
   Cost: $0
   Setup: None
   Best for: Quick experiments, no GPU at home

3. Cloud GPU (Lambda, RunPod, Vast.ai)
   Cost: $0.20-2.00/hr
   Setup: SSH + install
   Best for: Serious training, large models
```

## Собираем

### Вариант 1: Локальный NVIDIA GPU

Проверь, есть ли он:

```bash
nvidia-smi
```

Установи PyTorch с CUDA:

```python
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
```

### Вариант 2: Google Colab

1. Перейди на [colab.research.google.com](https://colab.research.google.com)
2. Runtime > Change runtime type > T4 GPU
3. Запусти `!nvidia-smi` для проверки

Загружай ноутбуки курса напрямую в Colab.

### Вариант 3: Облачный GPU

Для Lambda Labs, RunPod или Vast.ai:

```bash
ssh user@your-gpu-instance

pip install torch torchvision torchaudio
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Нет GPU? Не проблема.

Большинство уроков работает на CPU. Те, которым нужен GPU, скажут об этом и предложат ссылки на Colab.

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using: {device}")
```

## Собираем: бенчмарк GPU vs CPU

```python
import torch
import time

size = 5000

a_cpu = torch.randn(size, size)
b_cpu = torch.randn(size, size)

start = time.time()
c_cpu = a_cpu @ b_cpu
cpu_time = time.time() - start
print(f"CPU: {cpu_time:.3f}s")

if torch.cuda.is_available():
    a_gpu = a_cpu.to("cuda")
    b_gpu = b_cpu.to("cuda")

    torch.cuda.synchronize()
    start = time.time()
    c_gpu = a_gpu @ b_gpu
    torch.cuda.synchronize()
    gpu_time = time.time() - start
    print(f"GPU: {gpu_time:.3f}s")
    print(f"Speedup: {cpu_time / gpu_time:.0f}x")
```

## Упражнения

1. Запусти бенчмарк выше и сравни время CPU и GPU
2. Если нет GPU, запусти в Google Colab и сравни
3. Проверь объём видеопамяти и оцени максимальный размер модели (правило: 2 байта на параметр для fp16)

## Ключевые термины

| Термин | Что говорят | Что на самом деле |
|--------|------------|-------------------|
| CUDA | «Программирование GPU» | Параллельная вычислительная платформа NVIDIA для запуска кода на GPU |
| VRAM | «Память GPU» | Видеопамять на GPU, отдельная от системной RAM. Ограничивает размер модели. |
| fp16 | «Половинная точность» | 16-битные числа с плавающей точкой, вдвое меньше памяти, чем fp32, с минимальной потерей точности |
| Tensor Core | «Быстрое матричное железо» | Специализированные ядра GPU для умножения матриц, в 4–8 раз быстрее обычных |

---

> 📝 **Перевод:** русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../glossary/GLOSSARY.ru.md)
