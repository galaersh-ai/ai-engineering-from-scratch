RU = 'phases/16-multi-agent-and-swarms/13-shared-memory-blackboard/docs/ru.md'
for i, line in enumerate(open(RU, encoding='utf-8'), 1):
    latin = sum(1 for c in line if c.isascii() and c.isalpha())
    cyr = sum(1 for c in line if '\u0410' <= c <= '\u044f' or c in '\u0401\u0451')
    if latin > 30 and cyr < 10 and line.strip() and line.strip()[0] not in '#|-`\n':
        print(f'L{i}: {line.rstrip()[:120]}')
