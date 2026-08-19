"""Analyse the LLM shuffle experiment.

    python experiments/shuffle_llm/analyse.py

Re-running the experiment itself requires five independent model instances;
`results.json` records what came back so the analysis is reproducible without
re-spending them.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rubric.audit import analyse, report

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "results.json")))
rankings = [v.split() for v in data["rankings"].values()]

pos = {}
for run in rankings:
    for i, c in enumerate(run):
        pos.setdefault(c, []).append(i + 1)

print(f"{data['experiment']}  ({data['model']})\n")
print(f"{'cand':<6}" + "".join(f"{'r'+str(i+1):>5}" for i in range(len(rankings)))
      + f"{'best':>7}{'worst':>7}{'swing':>7}")
print("-" * 56)
for c in sorted(pos, key=lambda c: sum(pos[c]) / len(pos[c])):
    p = pos[c]
    flag = "  <-- unstable" if max(p) - min(p) >= 4 else ""
    print(f"{c:<6}" + "".join(f"{x:>5}" for x in p)
          + f"{min(p):>7}{max(p):>7}{max(p)-min(p):>7}{flag}")

print("\n\nChurn by where you draw the shortlist line\n")
print(f"{'shortlist':>10}{'settled in':>12}{'UNSETTLED':>11}{'settled out':>13}")
print("-" * 46)
for cut in range(2, 9):
    r = analyse(rankings, shortlist_size=cut)
    print(f"{cut:>10}{len(r.settled_in):>12}{len(r.unsettled):>11}{len(r.settled_out):>13}")

print("\n\nDetail at a shortlist of 5\n")
print(report(analyse(rankings, shortlist_size=5)))
print("\n\nCaveats")
for c in data["caveats"]:
    print(f"  - {c}")
