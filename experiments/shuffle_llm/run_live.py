"""Re-run the shuffle experiment on a live model, or several.

The August 2026 run used claude-opus-5 (see results.json). Reviewers rightly
ask whether the instability is one vendor's quirk, so this script runs the same
twelve CVs, the same five orders and the same prompt against any model you
name, independently per run (a fresh request each time, temperature 1.0 as
the original "default sampling"), and writes results-<model>.json next to
results.json in the same shape, so analyse.py can read any of them.

    ANTHROPIC_API_KEY=... python experiments/shuffle_llm/run_live.py --provider anthropic --model claude-sonnet-5-5
    ANTHROPIC_API_KEY=... python experiments/shuffle_llm/run_live.py --provider anthropic --model claude-haiku-5-5
    OPENAI_API_KEY=...    python experiments/shuffle_llm/run_live.py --provider openai --model gpt-5-mini
    GEMINI_API_KEY=...    python experiments/shuffle_llm/run_live.py --provider gemini --model gemini-2.5-flash
    python experiments/shuffle_llm/analyse.py --results experiments/shuffle_llm/results-claude-sonnet-5-5.json

Cost: five requests of about 1,500 input tokens each per model.
"""
from __future__ import annotations
import argparse, json, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", ".."))
from cvs import CVS  # noqa: E402

ROLE = """# Hiring task

## Role
Senior Backend Engineer — Payments Platform.
We need someone who has owned a backend system end to end, at real scale, where
correctness matters. 6+ years. Distributed systems depth. Experience in a regulated
or high-consequence environment is valued. You will own the ledger and settlement path.

## Candidates (12)
"""
TAIL = """
## What to return
Rank ALL 12 candidates from strongest to weakest fit for this role.
Return ONLY the candidate letters separated by spaces, best first, on a single
line. No explanation, no other text.
Example format: D A K F ...
"""
ORDERS = json.load(open(os.path.join(HERE, "results.json")))["orders"]


def prompt(order: list[str]) -> str:
    body = "".join(f"\n### Candidate {c}\n{CVS[c]}\n" for c in order)
    return ROLE + body + TAIL


def parse(text: str) -> list[str]:
    letters = re.findall(r"\b[A-L]\b", text.upper())
    seen, out = set(), []
    for x in letters:
        if x not in seen:
            seen.add(x); out.append(x)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", choices=["anthropic", "openai", "gemini"], required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--temperature", type=float, default=1.0)
    args = ap.parse_args(argv)
    from rubric.llm import anthropic_adapter, openai_adapter, gemini_adapter
    if args.provider == "anthropic":
        complete = anthropic_adapter(os.environ["ANTHROPIC_API_KEY"], model=args.model,
                                     max_tokens=200, temperature=args.temperature)
    elif args.provider == "gemini":
        # Gemini 2.5 thinks before it answers and the thinking counts against max_tokens
        complete = gemini_adapter(os.environ["GEMINI_API_KEY"], model=args.model,
                                  max_tokens=4000, temperature=args.temperature)
    else:
        # reasoning models spend tokens before the answer; leave room
        complete = openai_adapter(os.environ["OPENAI_API_KEY"], model=args.model, max_tokens=4000,
                                  temperature=args.temperature, base_url=os.environ.get("OPENAI_BASE_URL"))
    path = os.path.join(HERE, f"results-{args.model}.json")
    # resume: a run that died on a rate limit keeps what it got; rerun fills the gaps
    prev = json.load(open(path)) if os.path.exists(path) else {}
    rankings, raw = dict(prev.get("rankings", {})), dict(prev.get("raw", {}))
    out = {"experiment": "llm-shuffle-stability", "date": date.today().isoformat(),
           "design": "Same twelve CVs, same five orders and prompt as results.json; one fresh request per run.",
           "model": f"{args.model} (temperature {args.temperature})", "orders": ORDERS,
           "rankings": rankings, "raw": raw,
           "caveats": ["Five runs. A sixth could add a swing this one missed.",
                       "Synthetic CVs written to be close in strength; a wide-spread pool would look more stable."]}
    for k, order in ORDERS.items():
        if len(rankings.get(k, "").split()) == 12:
            print(f"run {k}: {rankings[k]}  (kept from an earlier run)")
            continue
        try:
            text = complete(prompt(order.split()))
        except Exception as e:
            print(f"run {k}: FAILED {type(e).__name__}: {str(e)[:100]}", file=sys.stderr)
            json.dump(out, open(path, "w"), indent=2)
            print(f"-> {path} (partial: {sum(1 for v in rankings.values() if len(v.split()) == 12)} of 5 runs)")
            sys.exit(1)
        raw[k] = text.strip()
        r = parse(text)
        if len(r) != 12:
            print(f"run {k}: could not parse 12 letters from: {text.strip()[:120]}", file=sys.stderr)
        rankings[k] = " ".join(r)
        print(f"run {k}: {rankings[k]}")
        json.dump(out, open(path, "w"), indent=2)
    print(f"-> {path}")


if __name__ == "__main__":
    main()
