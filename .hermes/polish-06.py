"""Final polish: add missing rows, translate exercises, fix headers."""
import re

RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"

with open(RU, encoding="utf-8") as f:
    text = f.read()

# Translate exercises
exercises_en = """1. Run `code/main.py` and compare happy vs perturbed. How many levels of manager hand-off does it take before the top output fully diverges from the user's question?
2. Add a third level (top → sub → sub-sub → worker). Measure how often the perturbed path corrects itself vs fully diverges as depth grows.
3. Implement a \"canary\" worker at each sub-manager that is always asked the original user question unchanged. Use the canary answer to detect decomposition drift. How should the manager react when the canary disagrees with the synthesized answer?
4. Read CrewAI's `Process.hierarchical` docs. Identify one concrete guardrail CrewAI applies (step limit, manager_llm constraint) and describe what failure mode it targets.
5. Compare nested LangGraph supervisors to CrewAI hierarchical. Which makes reconciliation loops cheaper to detect?"""

exercises_ru = """1. Запустите `code/main.py` и сравните счастливый сценарий с возмущённым. Сколько уровней передачи между менеджерами требуется, прежде чем итоговый результат полностью расходится с вопросом пользователя?
2. Добавьте третий уровень (верхний → подменеджер → под-подменеджер → работник). Измерьте, как часто возмущённый путь исправляет себя и как часто расходится полностью с ростом глубины.
3. Реализуйте «канареечного» работника на каждом подменеджере, который всегда получает исходный вопрос пользователя без изменений. Используйте ответ канарейки для обнаружения дрейфа декомпозиции. Как должен реагировать менеджер, когда ответ канарейки расходится с синтезированным ответом?
4. Прочитайте документацию CrewAI по `Process.hierarchical`. Найдите одно конкретное ограждение, которое применяет CrewAI (ограничение шагов, ограничение manager_llm), и опишите, на какой режим сбоя оно направлено.
5. Сравните вложенных супервайзеров LangGraph с иерархическим процессом CrewAI. Что делает циклы согласования более дешёвыми для обнаружения?"""

text = text.replace(exercises_en, exercises_ru)

# Fix "## Ключевые термины" — already OK
# Fix "Дополнительная литература" → "## Дополнительная литература"
text = text.replace('\nДополнительная литература\n', '\n## Дополнительная литература\n')

# Fix "Инженерия Anthropic — Система исследования" → "Исследовательская система Anthropic"
text = text.replace(
    '- [Инженерия Anthropic — Система исследования многокорпусной системы]',
    '- [Исследовательская система Anthropic]'
)

# Add missing "Provenance chain" row to Key Terms table
provenance_en = '|| Provenance chain | "Who said what" | Trace from each synthesis back to the leaf outputs that produced it. |'
provenance_ru = '|| Цепочка происхождения | «Кто что сказал» | Отслеживание от каждого синтеза к выходным данным листьев, которые его породили. |'
text = text.replace(provenance_en, provenance_ru)

# Actually the row is missing, not in English. Let me insert it before "## Further Reading" / "## Дополнительная литература"
# Find the position: after last table row, before ## Дополнительная литература
insert_pos = text.find('\n## Дополнительная литература')
if insert_pos > 0:
    # Check if provenance row already exists
    if 'Цепочка происхождения' not in text:
        text = text[:insert_pos] + '\n| Цепочка происхождения | «Кто что сказал» | Отслеживание от каждого синтеза к выходным данным листьев, которые его породили. |\n' + text[insert_pos:]

# Add missing Cemri reference
cemri_missing = '- [Cemri et al. — Why Do Multi-Agent LLM Systems Fail?](https://arxiv.org/abs/2503.13657) — MAST taxonomy; section on coordination failures documents decomposition drift'
if 'Cemri' not in text:
    last_ref = text.rfind('\n- [')
    if last_ref > 0:
        end_of_last = text.find('\n', text.find('\n', last_ref+1))
        if end_of_last < 0:
            end_of_last = len(text)
        cemri_ru = '\n- [Cemri et al. — Почему системы множественных агентов LLM дают сбои?](https://arxiv.org/abs/2503.13657) — таксономия MAST; раздел о сбоях координации документирует дрейф декомпозиции'
        text = text[:end_of_last] + cemri_ru + '\n' + text[end_of_last:]

# Fix "на внутренней узле" → "на внутреннем узле"
text = text.replace('на внутренней узле', 'на внутреннем узле')

# Fix terminology header: add "Степень происхождения" if missing
# Already added provenance chain above

with open(RU, 'w', encoding='utf-8') as f:
    f.write(text)

cyr = sum(1 for c in text if 'А' <= c <= 'я' or c in 'Ёё')
print(f"Final polish: {len(text)} chars, {text.count(chr(10))+1} lines, {cyr} Cyrillic", flush=True)
