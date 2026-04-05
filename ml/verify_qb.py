"""Quick verification of question_bank.json"""
import json
from collections import Counter
from pathlib import Path

qb_path = Path("data/datasets/question_bank.json")
if not qb_path.exists():
    print("ERROR: question_bank.json not found!")
    exit(1)

with open(qb_path, encoding="utf-8") as f:
    data = json.load(f)

print(f"Total questions: {len(data)}")
print()

cats = Counter(q["category"] for q in data)
diffs = Counter(q["difficulty"] for q in data)
sources = Counter(q["source"] for q in data)

print("Categories:")
for cat, count in cats.most_common():
    print(f"  {cat:25s} {count:>5}")

print(f"\nDifficulties:")
for d, count in diffs.most_common():
    print(f"  {d:10s} {count:>5}")

print(f"\nSources:")
for s, count in sources.most_common():
    print(f"  {s:40s} {count:>5}")

with_answers = sum(1 for q in data if q.get("answer", "").strip())
print(f"\nQuestions with answers: {with_answers}/{len(data)} ({100*with_answers//len(data)}%)")

print(f"\nSample questions:")
for i, q in enumerate(data[:3]):
    print(f"  [{i+1}] ({q['category']}/{q['difficulty']}) {q['question'][:120]}")
