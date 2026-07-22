> 📝 Перевод: русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../../glossary/GLOSSARY.ru.md)

# Статистика для машинного обучения

> Статистика позволяет понять, действительно ли работает Ваша модель — или ей просто повезло.

**Тип:** Построение
**Язык программирования:** Python
**Предварительные требования:** Фаза 1, Уроки 06 (Вероятность и распределения), 07 (Теорема Байеса)
**Время:** ~120 минут

## Цели обучения

- Вычислять описательную статистику, корреляцию Пирсона/Спирмена и матрицы ковариаций с нуля
- Применять гипотетические тесты (t-тест, хи-квадрат) и правильно интерпретировать p-значения и доверительные интервалы
- Использовать перебор Бутстрепа для построения доверительных интервалов для любого метрики без предположений о распределении
- Различать статистическую значимость от практической значимости с помощью мер эффекта

## Проблема

Вы обучили две модели. Модель A получила 0,87 на тестовом наборе данных. Модель B получила 0,89. Вы выкатываете модель B. Через три недели метрики в продакшене оказываются хуже, чем раньше. Что произошло?

На самом деле модель B не была лучше модели A. Разница в 0,02 оказалась случайным шумом. Либо тестовый набор был слишком маленьким, либо дисперсия слишком высокой, либо совпали оба фактора. Вы приняли случайное колебание за настоящее улучшение.

Такое происходит постоянно. Лидерборды Kaggle меняются из-за шума. Статьи не удаётся воспроизвести. В A/B-тестах объявляют победителя по нескольким сотням наблюдений. Корень проблемы один и тот же: кто-то проигнорировал статистику.

Статистика даёт Вам инструменты, чтобы отличать сигнал от шума. Она помогает понять, реальна ли разница, насколько Вы можете быть в ней уверены и сколько данных нужно собрать, прежде чем доверять результату. Любой ML-пайплайн, любое сравнение моделей и любое экспериментальное исследование опираются на статистику. Без неё Вы просто гадаете.

## Концепция

### Описательная статистика: сводка данных

Перед тем как строить модель, Вам нужно понять, с какими данными Вы работаете. Описательная статистика сжимает набор данных в несколько чисел, которые описывают его форму.

**Меры центральной тенденции** отвечают на вопрос "где находится середина?"

```
Mean:   sum of all values / count
        mu = (1/n) * sum(x_i)

Median: middle value when sorted
        Robust to outliers. If you have [1, 2, 3, 4, 1000], the mean is 202
        but the median is 3.

Mode:   most frequent value
        Useful for categorical data. For continuous data, rarely informative.
```

Среднее — это точка баланса. Медиана — центральное значение. Когда они расходятся, распределение оказывается смещённым. У распределений доходов среднее обычно намного больше медианы: правый хвост формируют миллиардеры. У распределений потерь во время обучения среднее, наоборот, может быть заметно меньше медианы из-за большого числа лёгких примеров.

**Меры разброса** отвечают на вопрос "насколько данные рассеяны?"

```
Variance:   average squared deviation from the mean
            sigma^2 = (1/n) * sum((x_i - mu)^2)

Standard deviation:  square root of variance
                     sigma = sqrt(sigma^2)
                     Same units as the data, so more interpretable.

Range:      max - min
            Sensitive to outliers. Almost never useful alone.

IQR:        Q3 - Q1 (interquartile range)
            The range of the middle 50% of the data.
            Robust to outliers. Used for box plots and outlier detection.
```

**Процентили** делят отсортированные данные на 100 равных частей. Процентиль 25-й (Q1) означает, что 25% значений ниже этой точки. Процентиль 50-й — это медиана. Процентиль 75-й — Q3.

```
For latency monitoring:
  P50 = median latency        (typical user experience)
  P95 = 95th percentile       (bad but not worst case)
  P99 = 99th percentile       (tail latency, often 10x the median)
```

В ML Вас обычно интересуют перцентили задержки инференса, распределения уверенности предсказаний и форма распределения ошибок. Модель с низкой средней ошибкой, но катастрофической P99-ошибкой может оказаться непригодной для критически важных приложений.

**Статистика выборки против статистики популяции.** При вычислении дисперсии по выборке делите на (n-1), а не на n. Это поправка Бесселя. Она компенсирует тот факт, что среднее по выборке не совпадает с истинным средним популяции. Если делить на n, Вы систематически занизите истинную дисперсию. Деление на (n-1) даёт несмещённую оценку.

```
Population variance: sigma^2 = (1/N) * sum((x_i - mu)^2)
Sample variance:     s^2     = (1/(n-1)) * sum((x_i - x_bar)^2)
```

На практике: если n велико (тысячи образцов), разница незначительна. Если n мал (несколько десятков образцов), это имеет значение.

### Корреляция: как переменные движутся вместе

Корреляция измеряет силу и направление линейной связи между двумя переменными.

**Коэффициент корреляции Пирсона** измеряет линейную ассоциацию:

```
r = sum((x_i - x_bar)(y_i - y_bar)) / (n * s_x * s_y)

r = +1:  perfect positive linear relationship
r = -1:  perfect negative linear relationship
r =  0:  no linear relationship (but there might be a nonlinear one!)

Range: [-1, 1]
```

Пирсон предполагает, что связь линейна и обе переменные приблизительно нормально распределены. Она чувствительна к выбросам. Одна экстремальная точка может утянуть r с 0,1 до 0,9.

**Коэффициент ранговой корреляции Спирмена** измеряет монотонную ассоциацию:

```
1. Replace each value with its rank (1, 2, 3, ...)
2. Compute Pearson correlation on the ranks

Spearman catches any monotonic relationship, not just linear.
If y = x^3, Pearson gives r < 1 but Spearman gives rho = 1.
```

**Когда использовать каждый:**

```
Pearson:    Both variables are continuous and roughly normal.
            You care about the linear relationship specifically.
            No extreme outliers.

Spearman:   Ordinal data (rankings, ratings).
            Data is not normally distributed.
            You suspect a monotonic but not linear relationship.
            Outliers are present.
```

**Золотое правило:** корреляция не означает причинно-следственную связь. Продажи мороженого и смертность от утопления связаны, потому что оба увеличиваются летом. Точность модели и количество параметров связаны, но добавление параметров автоматически не улучшит точность (см.: переобучение).

### Матрица ковариации

Ковариация между двумя переменными измеряет, как они изменяются вместе:

```
Cov(X, Y) = (1/n) * sum((x_i - x_bar)(y_i - y_bar))

Cov(X, Y) > 0:  X and Y tend to increase together
Cov(X, Y) < 0:  when X increases, Y tends to decrease
Cov(X, Y) = 0:  no linear co-movement
```

Для d признаков матрица ковариации C является d x d матрицей, где C[i][j] = Cov(feature_i, feature_j). Диагональные элементы C[i][i] являются дисперсиями каждого признака.

```
C = | Var(x1)      Cov(x1,x2)  Cov(x1,x3) |
    | Cov(x2,x1)  Var(x2)      Cov(x2,x3) |
    | Cov(x3,x1)  Cov(x3,x2)  Var(x3)     |

Properties:
  - Symmetric: C[i][j] = C[j][i]
  - Positive semi-definite: all eigenvalues >= 0
  - Diagonal = variances
  - Off-diagonal = covariances
```

**Связь с PCA.** PCA разлагает матрицу ковариаций на собственные вектора и значения. Собственные векторы являются главными компонентами (направлениями максимальной дисперсии). Собственные значения показывают, какую часть дисперсии захватывает каждая компонента.

**Связь с корреляцией.** Матрица корреляции — это матрица ковариаций стандартизированных переменных (каждой деленной на ее стандартное отклонение). Корреляция нормализует ковариацию, чтобы все значения падали в диапазоне [-1, 1].

### Гипотетические тесты

Гипотетический тест — это фреймворк для принятия решений при неопределенности. Вы начинаете с утверждения, собираете данные и определяете, согласуются ли данные с этим утверждением.

**Установка:**

```
Null hypothesis (H0):        the default assumption, usually "no effect"
Alternative hypothesis (H1): what you are trying to show

Example:
  H0: Model A and Model B have the same accuracy
  H1: Model B has higher accuracy than Model A
```

**P-значение** — это вероятность увидеть данные столь же экстремальные, как те, которые вы наблюдали, предполагая, что H0 истинна. Это НЕ вероятность того, что H0 истинна. Это самое распространенное недоразумение в статистике.

```
p-value = P(data this extreme | H0 is true)

If p-value < alpha (typically 0.05):
    Reject H0. The result is "statistically significant."
If p-value >= alpha:
    Fail to reject H0. You do not have enough evidence.
    This does NOT mean H0 is true.
```

**Доверительные интервалы** предоставляют диапазон вероятных значений для параметра:

```
95% confidence interval for the mean:
    x_bar +/- z * (s / sqrt(n))

where z = 1.96 for 95% confidence

Interpretation: if you repeated this experiment many times, 95% of the
computed intervals would contain the true mean. It does NOT mean there
is a 95% probability the true mean is in this specific interval.
```

Ширина доверительного интервала говорит вам об точности. Широкие интервалы указывают на высокую неопределенность. Узкие интервалы указывают на то, что ваша оценка точна (но не обязательно верна, если ваши данные смещены).

### Т-тест

Т-тест сравнивает средние значения. Существует несколько вариантов.

**Односемпловый t-тест:** отличается ли популяционное среднее от предполагаемого значения?

```
t = (x_bar - mu_0) / (s / sqrt(n))

degrees of freedom = n - 1
```

**Двухсемпловый t-тест (независимый):** отличаются ли средние двух групп?

```
t = (x_bar_1 - x_bar_2) / sqrt(s1^2/n1 + s2^2/n2)

This is Welch's t-test, which does not assume equal variances.
Always use Welch's unless you have a specific reason for equal variances.
```

**Связанный t-тест:** когда измерения приходят парами (одна и та же модель оценивается на одних и тех же данных разбиений):

```
Compute d_i = x_i - y_i for each pair
Then run a one-sample t-test on the d_i values against mu_0 = 0
```

В ML связанный t-тест часто используется: вы запускаете обе модели на одних и тех же 10 разбиениях кросс-валидации и сравниваете их оценки парами.

### Тест хи-квадрат

Тест хи-квадрат проверяет, соответствуют ли наблюдаемые частоты ожидаемым. Полезен для категориальных данных.

```
chi^2 = sum((observed - expected)^2 / expected)

Example: does a language model's output distribution match the
training distribution across categories?

Category    Observed   Expected
Positive       120        100
Negative        80        100
chi^2 = (120-100)^2/100 + (80-100)^2/100 = 4 + 4 = 8

With 1 degree of freedom, chi^2 = 8 gives p < 0.005.
The difference is significant.
```

### A/B тестирование для ML моделей

A/B тестирование в ML не то же самое, что веб-тестирование. Сравнение моделей имеет специфические проблемы:

```
1. Same test set:    Both models must be evaluated on identical data.
                     Different test sets make comparison meaningless.

2. Multiple metrics: Accuracy alone is not enough. You need precision,
                     recall, F1, latency, and fairness metrics.

3. Variance:         Use cross-validation or bootstrap to estimate
                     the variance of each metric, not just point estimates.

4. Data leakage:     If the test set was used during model selection,
                     your comparison is biased. Hold out a final test set.
```

**Процедура:**

```
1. Define your metric and significance level (alpha = 0.05)
2. Run both models on the same k-fold cross-validation splits
3. Collect paired scores: [(a1, b1), (a2, b2), ..., (ak, bk)]
4. Compute differences: d_i = b_i - a_i
5. Run a paired t-test on the differences
6. Check: is the mean difference significantly different from 0?
7. Compute a confidence interval for the mean difference
8. Compute effect size (Cohen's d) to judge practical significance
```

### Статистическая значимость против практической значимости

Результат может быть статистически значимым, но практически несущественным. При достаточно большом объёме данных даже незначительная разница становится статистически значимой.

```
Example:
  Model A accuracy: 0.9234
  Model B accuracy: 0.9237
  n = 1,000,000 test samples
  p-value = 0.001

Statistically significant? Yes.
Practically significant? A 0.03% improvement is not worth the
engineering cost of deploying a new model.
```

**Величина эффекта** количественно описывает размер разницы, независимо от объема выборки:

```
Cohen's d = (mean_1 - mean_2) / pooled_std

d = 0.2:  small effect
d = 0.5:  medium effect
d = 0.8:  large effect
```

Всегда сообщайте как p-значение, так и величину эффекта. P-значение говорит вам, реальна ли разница. Величина эффекта говорит вам, имеет ли она значение.

### Проблема множественных сравнений

Когда вы проверяете много гипотез, некоторые из них будут "статистически значимыми" случайно. Если вы проверите 20 вещей при alpha = 0,05, вы ожидаете одно ложное положительное значение даже когда ничего не реально.

```
P(at least one false positive) = 1 - (1 - alpha)^m

m = 20 tests, alpha = 0.05:
P(false positive) = 1 - 0.95^20 = 0.64

You have a 64% chance of at least one false positive.
```

**Коррекция Бонферрони:** разделите alpha на количество тестов.

```
Adjusted alpha = alpha / m = 0.05 / 20 = 0.0025

Only reject H0 if p-value < 0.0025.
Conservative but simple. Works when tests are independent.
```

В ML это важно, когда вы сравниваете модель по нескольким метрикам, проверяете много конфигураций гиперпараметров или оцениваете на нескольких наборах данных.

### Методы бутстрепа

Бутстреп оценивает распределение выборки статистики пересэмплением ваших данных с заменой. Не требуется предположений о базовом распределении.

**Алгоритм:**

```
1. You have n data points
2. Draw n samples WITH replacement (some points appear multiple times,
   some not at all)
3. Compute your statistic on this bootstrap sample
4. Repeat B times (typically B = 1000 to 10000)
5. The distribution of bootstrap statistics approximates the
   sampling distribution
```

**Доверительный интервал бутстрепа (метод процентилей):**

```
Sort the B bootstrap statistics
95% CI = [2.5th percentile, 97.5th percentile]
```

**Почему бутстреп важен для ML:**

```
- Test set accuracy is a point estimate. Bootstrap gives you
  confidence intervals.
- You cannot assume metric distributions are normal (especially
  for AUC, F1, precision at k).
- Bootstrap works for ANY statistic: median, ratio of two means,
  difference in AUC between two models.
- No closed-form formula needed.
```

**Бутстреп для сравнения моделей:**

```
1. You have predictions from Model A and Model B on the same test set
2. For each bootstrap iteration:
   a. Resample test indices with replacement
   b. Compute metric_A and metric_B on the resampled set
   c. Store diff = metric_B - metric_A
3. 95% CI for the difference:
   [2.5th percentile of diffs, 97.5th percentile of diffs]
4. If the CI does not contain 0, the difference is significant
```

Это более надежно, чем связанный t-тест, потому что он делает никаких предположений о распределении.

### Параметрические и непараметрические тесты

**Параметрические тесты** предполагают конкретное распределение (обычно нормальное):

```
t-test:         assumes normally distributed data (or large n by CLT)
ANOVA:          assumes normality and equal variances
Pearson r:      assumes bivariate normality
```

**Непараметрические тесты** не делают никаких предположений о распределении:

```
Mann-Whitney U:     compares two groups (replaces independent t-test)
Wilcoxon signed-rank: compares paired data (replaces paired t-test)
Spearman rho:       correlation on ranks (replaces Pearson)
Kruskal-Wallis:     compares multiple groups (replaces ANOVA)
```

**Когда использовать непараметрические тесты:**

```
- Small sample size (n < 30) and data is clearly non-normal
- Ordinal data (ratings, rankings)
- Heavy outliers you cannot remove
- Skewed distributions
```

**Когда использовать параметрические тесты:**

```
- Large sample size (CLT makes the test statistic approximately normal)
- Data is roughly symmetric without extreme outliers
- More statistical power (better at detecting real differences)
```

В экспериментах ML у Вас обычно малый n (5 или 10 разбиений кросс-валидации), поэтому непараметрические тесты, такие как Wilcoxon signed-rank, часто подходят лучше, чем t-тест.

### Центральная предельная теорема: практические последствия

ЦПТ утверждает, что распределение выборочных средних приближается к нормальному распределению по мере увеличения n, независимо от базового распределения популяции.

```
If X_1, X_2, ..., X_n are iid with mean mu and variance sigma^2:

    X_bar ~ Normal(mu, sigma^2 / n)    as n -> infinity

Works for n >= 30 in most cases.
For highly skewed distributions, you might need n >= 100.
```

**Почему это важно для ML:**

```
1. Justifies confidence intervals and t-tests on aggregated metrics
2. Explains why averaging over cross-validation folds gives stable
   estimates even when individual folds vary wildly
3. Mini-batch gradient descent works because the average gradient
   over a batch approximates the true gradient (CLT in action)
4. Ensemble methods: averaging predictions from many models gives
   more stable output than any single model
```

**Что ЦПТ не делает:**

```
- Does NOT make your data normal. It makes the MEAN of samples normal.
- Does NOT work for heavy-tailed distributions with infinite variance
  (Cauchy distribution).
- Does NOT apply to dependent data (time series without correction).
```

### Общие статистические ошибки в статьях по ML

1. **Тестирование на обучающем наборе данных.** Гарантирует переобучение. Всегда оставляйте данные, которые модель никогда не видела во время обучения.

2. **Отсутствие доверительных интервалов.** Сообщение одной точной численности без неопределенности делает результаты непроверяемыми и невоспроизводимыми.

3. **Игнорирование множественных сравнений.** Тестирование 50 конфигураций и сообщение о лучшей из них без корректировки увеличивает ложные положительные значения.

4. **Смешивание статистической и практической значимости.** P-значение 0,001 на улучшение точности в 0,01% не имеет значения.

5. **Использование точности на наборе данных с дисбалансом классов.** Точность 99% на наборе данных со 99% отрицательного класса означает, что модель ничего не уловила. Используйте точность, полноту, F1 или AUC.

6. **Выбор метрик по вкусу.** Сообщение только той метрики, где ваша модель выигрывает. Честная оценка отчетливо сообщает все релевантные метрики.

7. **Утечка информации между разбиениями обучающего и тестового наборов данных.** Нормализация до разделения или использование будущих данных для предсказания прошлого.

8. **Малый тестовый набор без оценок дисперсии.** Оценивание на 100 образцах и утверждение, что 2% улучшение — шум, а не сигнал.

9. **Предположение независимости при наличии зависимостей в данных.** Изображения медицинских исследований одного пациента, несколько предложений из одного документа. Замеры внутри группы коррелированы.

10. **P-хакинг.** Попытка различных тестов, подмножеств или критериев исключения до тех пор, пока не получите p < 0,05. Результат — следствие поиска.

## Строительство

Вы реализуете:

1. **Описательную статистику с нуля** (среднее значение, медиана, мода, стандартное отклонение, процентили, IQR)
2. **Функции корреляции** (Пирсон и Спирмен, с матрицей ковариации)
3. **Гипотетические тесты** (односемпловый t-тест, двухсемпловый t-тест, хи-квадратный тест)
4. **Доверительные интервалы бутстрепа** (для любой статистики, без предположений)
5. **Симулятор A/B тестирования** (генерация данных, тестирование, проверка на ошибки I и II типа)
6. **Демонстрация статистической и практической значимости** (показывающая что большие n делают все "статистически значимым")

Все с нуля, используя только `math` и `random`. Без numpy или scipy.

## Основные термины

| Термин | Определение |
|---|---|
| Среднее значение | Сумма всех значений деленная на количество. Чувствительна к выбросам. |
| Медиана | Серединное значение отсортированных данных. Устойчива к выбросам. |
| Стандартное отклонение | Квадратный корень из дисперсии. Измеряет разброс в исходных единицах. |
| Процентиль | Значение, ниже которого находится указанная процентная часть данных. |
| IQR (Interquartile Range) | Интерквартильный диапазон. Q3 минус Q1. Разброс средних 50%. |
| Корреляция Пирсона | Измеряет линейную ассоциацию между двумя переменными. Диапазон [-1, 1]. |
| Корреляция Спирмена | Измеряет монотонную ассоциацию с использованием рангов. |
| Матрица ковариации | Матрица парных ковариаций между всеми признаками. |
| Нулевая гипотеза | Базовое предположение о том, что нет эффекта или различий. |
| P-значение | Вероятность увидеть данные столь же экстремальные, если нулевая гипотеза истинна. |
| Доверительный интервал | Диапазон вероятных значений для параметра при заданном уровне уверенности. |
| T-тест | Проверяет, существенно ли различаются средние значения. Использует t-распределение. |
| Тест хи-квадрат | Проверяет, отличаются ли наблюдаемые частоты от ожидаемых. |
| Величина эффекта | Размер разницы, независимо от объема выборки. Cohen's d часто используется. |
| Коррекция Бонферрони | Делит порог значимости на количество тестов для контроля ложных положительных результатов. |
| Бутстреп | Пересэмплирование с заменой для оценки распределений выборок. |
| Ошибка I типа | Ложное положительное значение. Отклонение H0, когда она истинна. |
| Ошибка II типа | Ложное отрицательное значение. Не отвержение H0, когда она ложна. |
| Статическая мощность | Вероятность правильно отвергнуть ложную H0. Мощность = 1 минус уровень ошибки II типа. |
| Центральная предельная теорема | Выборочные средние сходятся к нормальному распределению по мере увеличения объема выборки. |
| Параметрический тест | Предполагает конкретное распределение данных (обычно нормальное). |
| Непараметрический тест | Не делает предположений о распределении. Работает на рангах или знаках. |