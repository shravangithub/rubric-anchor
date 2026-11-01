"""Compare shuffle results across models.

    python experiments/shuffle_llm/compare.py            # every results*.json here
    python experiments/shuffle_llm/compare.py --md       # as a Markdown table

Per model: how many of the twelve moved 4+ places, the biggest swing, how many
were unsettled at a shortlist of 3 and of 5, and whether the top 3 and the
bottom 1 held. The point is the shape, not the exact numbers.
"""
import glob, json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from rubric.audit import analyse

HERE = os.path.dirname(os.path.abspath(__file__))


def summarise(path):
    d = json.load(open(path))
    runs = [v.split() for v in d["rankings"].values() if len(v.split()) == 12]
    if len(runs) < 2:
        return {"model": d["model"], "date": d.get("date", ""), "runs": len(runs), "bad": True}
    pos = {}
    for run in runs:
        for i, c in enumerate(run):
            pos.setdefault(c, []).append(i + 1)
    swings = {c: max(p) - min(p) for c, p in pos.items()}
    top3 = [c for c, p in pos.items() if max(p) <= 3]
    return {"model": d["model"], "date": d.get("date", ""), "runs": len(runs),
            "moved4": sum(1 for s in swings.values() if s >= 4),
            "max_swing": max(swings.values()), "max_who": max(swings, key=swings.get),
            "unsettled3": len(analyse(runs, 3).unsettled), "unsettled5": len(analyse(runs, 5).unsettled),
            "top3_held": len(top3), "bottom_held": any(min(p) == 12 for p in pos.values()), "bad": False}


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    files = sorted(glob.glob(os.path.join(HERE, "results*.json")))
    rows = [summarise(f) for f in files]
    if "--md" in argv:
        print("| model | date | runs | moved 4+ places | biggest swing | unsettled at 3 | unsettled at 5 | top 3 held | last held |")
        print("|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            if r["bad"]:
                print(f"| {r['model']} | {r['date']} | {r['runs']} | (fewer than two complete runs) | | | | | |"); continue
            print(f"| {r['model']} | {r['date']} | {r['runs']} | {r['moved4']} of 12 | {r['max_swing']} places ({r['max_who']}) | "
                  f"{r['unsettled3']} | {r['unsettled5']} | {r['top3_held']} of 3 | {'yes' if r['bottom_held'] else 'no'} |")
    else:
        for r in rows:
            print(json.dumps(r))


if __name__ == "__main__":
    main()
