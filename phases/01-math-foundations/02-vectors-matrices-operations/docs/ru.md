# Векторы, матрицы и операции

> Каждая нейронная сеть — это просто матричное умножение с дополнительными шагами.

**Тип:** Создание
**Языки:** Python, Julia
**Пререквизиты:** Phase 1, Lesson 01 (Интуиция линейной алгебры)
**Время:** ~60 минут

## Цели обучения

- Создать класс Matrix с поэлементными операциями, матричным умножением, транспонированием, определителем и обратной матрицей
- Различать поэлементное умножение и матричное умножение, объяснять, когда применяется каждое
- Реализовать один плотный слой нейронной сети (`relu(W @ x + b)`), используя только созданный с нуля класс Matrix
- Объяснить правила broadcasting и то, как добавление смещения работает во фреймворках нейронных сетей

## Проблема

Вы хотите построить нейронную сеть. Вы читаете код и видите:

```
output = activation(weights @ input + bias)
```

`@` — это матричное умножение. `weights` — матрица. `input` — вектор. Если Вы не знаете, что делают эти операции, эта строка — магия. Если знаете, то это весь прямой проход слоя в трёх операциях.

Каждое изображение, которое обрабатывает Ваша модель, — это матрица значений пикселей. Каждый эмбеддинг слова — вектор. Каждый слой каждой нейронной сети — матричное преобразование. Нельзя строить AI-системы, не владея свободно матричными операциями — так же, как нельзя писать код, не понимая переменных.

Этот урок формирует такое владение с нуля.

## Концепция

### Векторы: упорядоченные списки чисел

Вектор — это список чисел, имеющий направление и величину. В AI векторы представляют точки данных, признаки или параметры.

```
v = [3, 4]        -- a 2D vector
w = [1, 0, -2]    -- a 3D vector
```

Двумерный вектор `[3, 4]` указывает на координаты (3, 4) на плоскости. Его длина (величина) равна 5 (треугольник 3-4-5).

### Матрицы: сетки чисел

Матрица — это двумерная сетка. Строки и столбцы. Матрица m × n имеет m строк и n столбцов.

```
A = | 1  2  3 |     -- 2x3 matrix (2 rows, 3 columns)
    | 4  5  6 |
```

В нейронных сетях весовые матрицы преобразуют входные векторы в выходные. Слой с 784 входами и 128 выходами использует весовую матрицу 128×784.

### Почему размерности важны

У матричного умножения есть строгое правило: `(m × n) @ (n × p) = (m × p)`. Внутренние размерности должны совпадать.

```
(128 x 784) @ (784 x 1) = (128 x 1)
  weights       input       output

Inner dimensions: 784 = 784  -- valid
```

Если Вы получаете ошибку несовпадения размерностей в PyTorch — причина именно в этом.

### Карта операций

| Операция | Что делает | Применение в нейронных сетях |
|----------|-----------|---------------------------|
| Сложение | Поэлементное объединение | Добавление смещения к выходу |
| Умножение на скаляр | Масштабирование каждого элемента | Скорость обучения × градиенты |
| Матричное умножение | Преобразование векторов | Прямой проход слоя |
| Транспонирование | Обмен строк и столбцов | Обратное распространение |
| Определитель | Одночисловая характеристика | Проверка обратимости |
| Обратная матрица | Отмена преобразования | Решение линейных систем |
| Единичная матрица | Матрица «ничего не делать» | Инициализация, остаточные связи |

### Поэлементное умножение vs матричное умножение

Это различие постоянно сбивает с толку новичков.

Поэлементное: умножение соответствующих позиций. Обе матрицы должны быть одинаковой размерности.

```
| 1  2 |   | 5  6 |   | 5  12 |
| 3  4 | * | 7  8 | = | 21 32 |
```

Матричное умножение: скалярные произведения строк и столбцов. Внутренние размерности должны совпадать.

```
| 1  2 |   | 5  6 |   | 1*5+2*7  1*6+2*8 |   | 19  22 |
| 3  4 | @ | 7  8 | = | 3*5+4*7  3*6+4*8 | = | 43  50 |
```

Разные операции, разные результаты, разные правила.

### Broadcasting

Когда Вы добавляете вектор смещения к матрице выходов, размерности не совпадают. Broadcasting растягивает меньший массив до нужного размера.

```
| 1  2  3 |   +   [10, 20, 30]
| 4  5  6 |

Broadcasting stretches the vector across rows:

| 1  2  3 |   | 10  20  30 |   | 11  22  33 |
| 4  5  6 | + | 10  20  30 | = | 14  25  36 |
```

Каждый современный фреймворк делает это автоматически. Понимание механизма избавляет от путаницы, когда размерности кажутся неправильными, но код работает.

## Создаём

### Шаг 1: Класс Vector

```python
class Vector:
    def __init__(self, data):
        self.data = list(data)
        self.size = len(self.data)

    def __repr__(self):
        return f"Vector({self.data})"

    def __add__(self, other):
        return Vector([a + b for a, b in zip(self.data, other.data)])

    def __sub__(self, other):
        return Vector([a - b for a, b in zip(self.data, other.data)])

    def __mul__(self, scalar):
        return Vector([x * scalar for x in self.data])

    def dot(self, other):
        return sum(a * b for a, b in zip(self.data, other.data))

    def magnitude(self):
        return sum(x ** 2 for x in self.data) ** 0.5
```

### Шаг 2: Класс Matrix с основными операциями

```python
class Matrix:
    def __init__(self, data):
        self.data = [list(row) for row in data]
        self.rows = len(self.data)
        self.cols = len(self.data[0])
        self.shape = (self.rows, self.cols)

    def __repr__(self):
        rows_str = "\n  ".join(str(row) for row in self.data)
        return f"Matrix({self.shape}):\n  {rows_str}"

    def __add__(self, other):
        return Matrix([
            [self.data[i][j] + other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def __sub__(self, other):
        return Matrix([
            [self.data[i][j] - other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def scalar_multiply(self, scalar):
        return Matrix([
            [self.data[i][j] * scalar for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def element_wise_multiply(self, other):
        return Matrix([
            [self.data[i][j] * other.data[i][j] for j in range(self.cols)]
            for i in range(self.rows)
        ])

    def matmul(self, other):
        return Matrix([
            [
                sum(self.data[i][k] * other.data[k][j] for k in range(self.cols))
                for j in range(other.cols)
            ]
            for i in range(self.rows)
        ])

    def transpose(self):
        return Matrix([
            [self.data[j][i] for j in range(self.rows)]
            for i in range(self.cols)
        ])

    def determinant(self):
        if self.shape == (1, 1):
            return self.data[0][0]
        if self.shape == (2, 2):
            return self.data[0][0] * self.data[1][1] - self.data[0][1] * self.data[1][0]
        det = 0
        for j in range(self.cols):
            minor = Matrix([
                [self.data[i][k] for k in range(self.cols) if k != j]
                for i in range(1, self.rows)
            ])
            det += ((-1) ** j) * self.data[0][j] * minor.determinant()
        return det

    def inverse_2x2(self):
        det = self.determinant()
        if det == 0:
            raise ValueError("Matrix is singular, no inverse exists")
        return Matrix([
            [self.data[1][1] / det, -self.data[0][1] / det],
            [-self.data[1][0] / det, self.data[0][0] / det]
        ])

    @staticmethod
    def identity(n):
        return Matrix([
            [1 if i == j else 0 for j in range(n)]
            for i in range(n)
        ])
```

### Шаг 3: Смотрим в действии

```python
A = Matrix([[1, 2], [3, 4]])
B = Matrix([[5, 6], [7, 8]])

print("A + B =", (A + B).data)
print("A @ B =", A.matmul(B).data)
print("A^T =", A.transpose().data)
print("det(A) =", A.determinant())
print("A^-1 =", A.inverse_2x2().data)

I = Matrix.identity(2)
print("A @ A^-1 =", A.matmul(A.inverse_2x2()).data)
```

### Шаг 4: Связь с нейронными сетями

```python
import random

inputs = Matrix([[0.5], [0.8], [0.2]])
weights = Matrix([
    [random.uniform(-1, 1) for _ in range(3)]
    for _ in range(2)
])
bias = Matrix([[0.1], [0.1]])

def relu_matrix(m):
    return Matrix([[max(0, val) for val in row] for row in m.data])

pre_activation = weights.matmul(inputs) + bias
output = relu_matrix(pre_activation)

print(f"Input shape: {inputs.shape}")
print(f"Weight shape: {weights.shape}")
print(f"Output shape: {output.shape}")
print(f"Output: {output.data}")
```

Это один плотный слой: `output = relu(W @ x + b)`. Каждый плотный слой в каждой нейронной сети делает именно это.

## Используем

NumPy делает всё вышеперечисленное в меньшем количестве строк и на порядки быстрее.

```python
import numpy as np

A = np.array([[1, 2], [3, 4]])
B = np.array([[5, 6], [7, 8]])

print("A + B =\n", A + B)
print("A * B (element-wise) =\n", A * B)
print("A @ B (matrix multiply) =\n", A @ B)
print("A^T =\n", A.T)
print("det(A) =", np.linalg.det(A))
print("A^-1 =\n", np.linalg.inv(A))
print("I =\n", np.eye(2))

inputs = np.random.randn(3, 1)
weights = np.random.randn(2, 3)
bias = np.array([[0.1], [0.1]])
output = np.maximum(0, weights @ inputs + bias)

print(f"\nNeural network layer: {weights.shape} @ {inputs.shape} = {output.shape}")
print(f"Output:\n{output}")
```

Оператор `@` в Python вызывает `__matmul__`. NumPy реализует его с помощью оптимизированных BLAS-процедур, написанных на C и Fortran. Та же математика, в 100 раз быстрее.

Broadcasting в NumPy:

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])
bias = np.array([10, 20, 30])
print(matrix + bias)
```

NumPy автоматически растягивает одномерный bias на обе строки. Именно так работает добавление смещения в каждом фреймворке нейронных сетей.

## Результат

Этот урок создаёт промпт для обучения матричным операциям через геометрическую интуицию. См. `outputs/prompt-matrix-operations.md`.

Класс Matrix, построенный здесь, — фундамент для мини-фреймворка нейронных сетей, который мы создадим в Phase 3, Lesson 10.

## Упражнения

1. **Проверьте обратную матрицу.** Умножьте `A @ A.inverse_2x2()` и убедитесь, что получается единичная матрица. Попробуйте с тремя разными матрицами 2×2. Что происходит, когда определитель равен нулю?

2. **Реализуйте обратную матрицу 3×3.** Расширьте класс Matrix для вычисления обратных матриц 3×3 методом присоединённой матрицы. Проверьте результат с помощью `np.linalg.inv` из NumPy.

3. **Постройте двухслойную сеть.** Используя только свой класс Matrix (без NumPy), создайте двухслойную нейронную сеть: вход (3) → скрытый (4) → выход (2). Инициализируйте случайные веса, выполните прямой проход и проверьте, что все размерности корректны.

## Ключевые термины

| Термин | Что говорят | Что это на самом деле |
|--------|------------|---------------------|
| Вектор | «Стрелка» | Упорядоченный список чисел. В AI: точка в многомерном пространстве. |
| Матрица | «Таблица чисел» | Линейное преобразование. Отображает векторы из одного пространства в другое. |
| Матричное умножение | «Просто перемножьте числа» | Скалярные произведения каждой строки первой матрицы и каждого столбца второй. Порядок важен. |
| Транспонирование | «Переверните» | Обмен строк и столбцов. Превращает матрицу m × n в n × m. Критически важно при обратном распространении. |
| Определитель | «Какое-то число из матрицы» | Показывает, насколько матрица масштабирует площадь (2D) или объём (3D). Ноль означает, что преобразование схлопывает измерение. |
| Обратная матрица | «Отмена матрицы» | Матрица, обращающая преобразование. Существует только когда определитель не равен нулю. |
| Единичная матрица | «Скучная матрица» | Матричный эквивалент умножения на 1. Используется в остаточных связях (ResNet). |
| Broadcasting | «Магическое исправление размерностей» | Растягивание меньшего массива до размеров большего путём повторения вдоль недостающих размерностей. |
| Поэлементное | «Обычное умножение» | Умножение соответствующих позиций. Оба массива должны иметь одинаковую размерность (или быть broadcastable). |

## Дополнительные материалы

- [3Blue1Brown: Суть линейной алгебры](https://www.3blue1brown.com/topics/linear-algebra) — визуальная интуиция для каждой рассмотренной здесь операции
- [Документация NumPy по broadcasting](https://numpy.org/doc/stable/user/basics.broadcasting.html) — точные правила, которым следует NumPy
- [Stanford CS229, обзор линейной алгебры](http://cs229.stanford.edu/section/cs229-linalg.pdf) — краткий справочник по линейной алгебре для ML
