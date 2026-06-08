#!/usr/bin/env bash
set -u

REPO=/c/Projects/AI_Project/ai-engineering-from-scratch
PYTHON=/c/Users/Galina/AppData/Roaming/uv/python/cpython-3.11.15-windows-x86_64-none/python.exe
STATE_WIN='C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/translation-batch-state.json'
mkdir -p "$REPO/.hermes"
STARTED_AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

L14_NAME='14-norms-and-distances'
L15_NAME='15-statistics-for-ml'
L16_NAME='16-sampling-methods'

L14_STATUS='pending'
L15_STATUS='pending'
L16_STATUS='pending'

L14_NOTIFY='false'
L15_NOTIFY='false'
L16_NOTIFY='false'

L14_LOG='C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/translation-14.log'
L15_LOG='C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/translation-15.log'
L16_LOG='C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/translation-16.log'

L14_DONE='C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/translation-14.done'
L15_DONE='C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/translation-15.done'
L16_DONE='C:/Projects/AI_Project/ai-engineering-from-scratch/.hermes/translation-16.done'

L14_RU='C:/Projects/AI_Project/ai-engineering-from-scratch/phases/01-math-foundations/14-norms-and-distances/docs/ru.md'
L15_RU='C:/Projects/AI_Project/ai-engineering-from-scratch/phases/01-math-foundations/15-statistics-for-ml/docs/ru.md'
L16_RU='C:/Projects/AI_Project/ai-engineering-from-scratch/phases/01-math-foundations/16-sampling-methods/docs/ru.md'

write_state() {
  export STARTED_AT STATE_WIN
  export MODE="$1" CURRENT_NAME="$2" CURRENT_STEP="$3" CURRENT_LOG="$4" CURRENT_RU="$5" CURRENT_DONE="$6" CURRENT_NEXT="$7" CURRENT_COMPLETION_SENT="$8"
  export L14_NAME L15_NAME L16_NAME
  export L14_STATUS L15_STATUS L16_STATUS
  export L14_NOTIFY L15_NOTIFY L16_NOTIFY
  export L14_LOG L15_LOG L16_LOG
  export L14_DONE L15_DONE L16_DONE
  export L14_RU L15_RU L16_RU
  "$PYTHON" - <<'PY'
import json, os
from pathlib import Path
state = {
  'mode': os.environ['MODE'],
  'started_at': os.environ['STARTED_AT'],
  'current_lesson': {
    'name': os.environ['CURRENT_NAME'],
    'step': os.environ['CURRENT_STEP'],
    'log_path': os.environ['CURRENT_LOG'],
    'ru_path': os.environ['CURRENT_RU'],
    'done_path': os.environ['CURRENT_DONE'],
    'next_chapter_if_any': os.environ['CURRENT_NEXT'],
    'completion_notification_sent': os.environ['CURRENT_COMPLETION_SENT'].lower() == 'true',
  },
  'chapters': [
    {
      'name': os.environ['L14_NAME'],
      'status': os.environ['L14_STATUS'],
      'notification_sent': os.environ['L14_NOTIFY'].lower() == 'true',
      'log_path': os.environ['L14_LOG'],
      'ru_path': os.environ['L14_RU'],
      'done_path': os.environ['L14_DONE'],
    },
    {
      'name': os.environ['L15_NAME'],
      'status': os.environ['L15_STATUS'],
      'notification_sent': os.environ['L15_NOTIFY'].lower() == 'true',
      'log_path': os.environ['L15_LOG'],
      'ru_path': os.environ['L15_RU'],
      'done_path': os.environ['L15_DONE'],
    },
    {
      'name': os.environ['L16_NAME'],
      'status': os.environ['L16_STATUS'],
      'notification_sent': os.environ['L16_NOTIFY'].lower() == 'true',
      'log_path': os.environ['L16_LOG'],
      'ru_path': os.environ['L16_RU'],
      'done_path': os.environ['L16_DONE'],
    },
  ],
}
Path(os.environ['STATE_WIN']).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding='utf-8')
PY
}

prepend_note() {
  "$PYTHON" - "$1" <<'PY'
import sys
from pathlib import Path
p = Path(sys.argv[1])
text = p.read_text(encoding='utf-8')
note = '> 📝 Перевод: русская адаптация. [Оригинал](en.md) | Глоссарий: [GLOSSARY.ru.md](../../../../glossary/GLOSSARY.ru.md)\n\n'
if not text.startswith(note):
    p.write_text(note + text, encoding='utf-8')
PY
}

notification_sent_for() {
  local lesson_name="$1"
  export STATE_WIN LESSON_NAME="$lesson_name"
  "$PYTHON" - <<'PY'
import json, os, sys
from pathlib import Path
state = json.loads(Path(os.environ['STATE_WIN']).read_text(encoding='utf-8'))
lesson = os.environ['LESSON_NAME']
for chapter in state.get('chapters', []):
    if chapter.get('name') == lesson:
        print('true' if chapter.get('notification_sent') else 'false')
        raise SystemExit(0)
print('false')
PY
}

wait_for_notification() {
  local lesson_name="$1"
  local next_name="$2"
  local log_path="$3"
  local ru_path="$4"
  local done_path="$5"

  write_state running "$lesson_name" awaiting_completion_notification "$log_path" "$ru_path" "$done_path" "$next_name" false
  while true; do
    local sent
    sent="$(notification_sent_for "$lesson_name")"
    if [ "$sent" = "true" ]; then
      return 0
    fi
    sleep 30
  done
}

run_one() {
  local lesson_name="$1"
  local en_path="$2"
  local ru_path="$3"
  local log_path="$4"
  local done_path="$5"
  local chapter_var="$6"
  local notify_var="$7"
  local next_name="$8"

  rm -f "$log_path" "$done_path"
  write_state running "$lesson_name" translating "$log_path" "$ru_path" "$done_path" "$next_name" false

  if "$PYTHON" "$REPO/translate_lesson.py" "$en_path" "$ru_path" > "$log_path" 2>&1; then
    prepend_note "$ru_path"
    printf 'exit_code=0 finished_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$done_path"
    eval "$chapter_var='done'"
    eval "$notify_var='false'"
    wait_for_notification "$lesson_name" "$next_name" "$log_path" "$ru_path" "$done_path"
    eval "$notify_var='true'"
    return 0
  else
    local code=$?
    printf 'exit_code=%s finished_at=%s\n' "$code" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$done_path"
    eval "$chapter_var='failed'"
    write_state failed "$lesson_name" failed "$log_path" "$ru_path" "$done_path" "$next_name" false
    return "$code"
  fi
}

run_one "$L14_NAME" \
  "$REPO/phases/01-math-foundations/14-norms-and-distances/docs/en.md" \
  "$REPO/phases/01-math-foundations/14-norms-and-distances/docs/ru.md" \
  "$REPO/.hermes/translation-14.log" \
  "$REPO/.hermes/translation-14.done" \
  L14_STATUS \
  L14_NOTIFY \
  "$L15_NAME" || exit $?

run_one "$L15_NAME" \
  "$REPO/phases/01-math-foundations/15-statistics-for-ml/docs/en.md" \
  "$REPO/phases/01-math-foundations/15-statistics-for-ml/docs/ru.md" \
  "$REPO/.hermes/translation-15.log" \
  "$REPO/.hermes/translation-15.done" \
  L15_STATUS \
  L15_NOTIFY \
  "$L16_NAME" || exit $?

run_one "$L16_NAME" \
  "$REPO/phases/01-math-foundations/16-sampling-methods/docs/en.md" \
  "$REPO/phases/01-math-foundations/16-sampling-methods/docs/ru.md" \
  "$REPO/.hermes/translation-16.log" \
  "$REPO/.hermes/translation-16.done" \
  L16_STATUS \
  L16_NOTIFY \
  "none" || exit $?

write_state completed "$L16_NAME" completed "$L16_LOG" "$L16_RU" "$L16_DONE" none true
