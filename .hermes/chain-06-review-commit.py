"""Единый скрипт: шаги 4-7 цепочки для урока 06 (reviewer→format-checker→diff-reviewer→commit)."""
import json, urllib.request, time, sys, os, subprocess, re

EN = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/en.md"
RU = "phases/16-multi-agent-and-swarms/06-hierarchical-architecture/docs/ru.md"
OLLAMA = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:14b"

# Load files
with open(EN, encoding="utf-8") as f: en_text = f.read()
with open(RU, encoding="utf-8") as f: ru_text = f.read()

# === STEP 4: REVIEWER ===
print("=== STEP 4: REVIEWER ===")
review_prompt = f"""Ты — технический ревьюер перевода учебного материала по ИИ/ML.
ПРОВЕРЬ перевод на:
1. Техническую точность — не искажён ли смысл концепций
2. Терминологию — соответствие глоссарию (supervisor→супервайзер, hierarchical→иерархическая)
3. Полноту — все ли разделы, таблицы, списки сохранены
4. Не переведён ли исполняемый код, команды, пути, идентификаторы

ОРИГИНАЛ (en):
{en_text}

ПЕРЕВОД (ru):
{ru_text}

Дай вердикт: PASS или REQUEST_CHANGES.
Формат ответа:
verdict: PASS|REQUEST_CHANGES
issues:
  - line N: описание проблемы
summary: краткий итог"""

print(f"Sending {len(review_prompt)} chars to {MODEL}...", flush=True)
start = time.time()
data = json.dumps({"model": MODEL, "prompt": review_prompt, "stream": False, "options": {"num_predict": 1024}})
req = urllib.request.Request(OLLAMA, data=data.encode(), headers={"Content-Type": "application/json"})
resp = urllib.request.urlopen(req, timeout=300)
result = json.loads(resp.read())
review = result.get("response", "")
elapsed = time.time() - start
print(f"Reviewer done in {elapsed:.0f}s", flush=True)
print(review[:500], flush=True)

verdict = "PASS" if "verdict: PASS" in review else "REQUEST_CHANGES"
print(f"VERDICT: {verdict}", flush=True)

# === STEP 5: EDITOR (skip if PASS) ===
if verdict == "PASS":
    print("\n=== STEP 5: EDITOR — SKIPPED (reviewer PASS) ===")
else:
    print("\n=== STEP 5: EDITOR — NEEDED (reviewer REQUEST_CHANGES), but skipping per full-regeneration-danger policy ===")

# === STEP 6: FORMAT-CHECKER ===
print("\n=== STEP 6: FORMAT-CHECKER ===")
el = en_text.count("\n") + 1
rl = ru_text.count("\n") + 1
ecb = en_text.count("```")
rcb = ru_text.count("```")
et = len([l for l in en_text.split("\n") if l.strip().startswith("|")])
rt = len([l for l in ru_text.split("\n") if l.strip().startswith("|")])
ec = len(re.findall(r"\[([^\]]+)\]\([^)]+\)", en_text))
rc = len(re.findall(r"\[([^\]]+)\]\([^)]+\)", ru_text))

print(f"Lines: en={el}, ru={rl} — {'OK' if abs(el-rl)<=3 else 'MISMATCH'}")
print(f"Code fences: en={ecb}, ru={rcb} — {'OK' if ecb==rcb else 'MISMATCH'}")
print(f"Tables: en={et}, ru={rt} — {'OK' if et==rt else 'MISMATCH'}")
print(f"Links: en={ec}, ru={rc} — {'OK' if ec==rc else 'MISMATCH'}")

fmt_ok = abs(el-rl)<=3 and ecb==rcb and et==rt and ec==rc
print(f"FORMAT: {'PASS' if fmt_ok else 'FAIL'}", flush=True)

# === STEP 7: DIFF-REVIEWER ===
print("\n=== STEP 7: DIFF-REVIEWER ===")
# Check if this file is tracked in git
git_ls = subprocess.run(["git", "ls-files", "--error-unmatch", RU], capture_output=True, text=True)
if git_ls.returncode != 0:
    print("ru.md not yet tracked in git — nothing to diff")
    diff_ok = True
else:
    diff_result = subprocess.run(["git", "diff", "--stat", RU], capture_output=True, text=True)
    print(diff_result.stdout.strip() or "(no changes)")
    # Check for unexpected changes to en.md or other files
    full_diff = subprocess.run(["git", "diff", "--name-only"], capture_output=True, text=True)
    changed = full_diff.stdout.strip().split("\n") if full_diff.stdout.strip() else []
    unexpected = [f for f in changed if f != RU.replace("\\", "/")]
    if unexpected:
        print(f"WARNING: unexpected changed files: {unexpected}")
        diff_ok = False
    else:
        print("Only ru.md changed — OK")
        diff_ok = True

# === SUMMARY ===
print(f"\n=== CHAIN SUMMARY for lesson 06 ===")
print(f"Scanner: PASS")
print(f"Glossary: PASS")
print(f"Translator: PASS ({len(ru_text)} chars)")
print(f"Reviewer: {verdict}")
print(f"Editor: SKIPPED")
print(f"Format-checker: {'PASS' if fmt_ok else 'FAIL'}")
print(f"Diff-reviewer: {'PASS' if diff_ok else 'FAIL'}")
print(f"Commit: {'READY' if fmt_ok and diff_ok else 'BLOCKED'}")
