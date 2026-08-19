"""Command line interface.

    python -m rubric params                     list the 50 parameters
    python -m rubric score --job J --cvs DIR    score a folder of CVs
    python -m rubric audit --rankings FILE      run the shuffle audit
"""
from __future__ import annotations
import argparse, glob, json, os, sys
from datetime import date

from . import parameters as P
from .scoring import score_candidate
from .extractors import NullExtractor
from .audit import analyse, report


def _params(args):
    from .packs import build_rubric, INDUSTRY_PACKS
    rows = build_rubric(args.industry)
    rows = [p for p in rows if not args.family or p.family == args.family]
    print(f"{'key':<30}{'family':<13}{'kind':<8}{'how':<7}{'weight':>8}  auto-reject")
    print("-" * 82)
    for p in rows:
        w = f"{p.weight:.3f}" if p.kind is P.Kind.SCORED else "-"
        ar = ("YES" if p.bona_fide else "no") if p.kind is P.Kind.GATE else ""
        print(f"{p.key:<30}{p.family:<13}{p.kind.value:<8}{p.how.value:<7}{w:>8}  {ar}")
    print(f"\n{len(rows)} parameters   "
          f"({sum(1 for p in rows if p.how is P.How.CODE)} computed in code)")
    if not args.industry:
        from .packs import INDUSTRY_PACKS
        print(f"add --industry to include a pack: "
              f"{', '.join(sorted(INDUSTRY_PACKS))}")


def _score(args):
    job = json.load(open(args.job))
    files = sorted(glob.glob(os.path.join(args.cvs, "*.txt")))
    if not files:
        sys.exit(f"no .txt CVs found in {args.cvs}")
    out = []
    for f in files:
        cid = os.path.splitext(os.path.basename(f))[0]
        r = score_candidate(cid, open(f).read(), job, NullExtractor(),
                            today=date.fromisoformat(args.today) if args.today else None,
                            industry=args.industry or job.get("industry"))
        out.append(r)
    out.sort(key=lambda r: -r.composite)          # sorting numbers, in code
    print(f"{'candidate':<18}{'score':>8}   status")
    print("-" * 60)
    for r in out:
        st = "REVIEW - " + r.reasons[0] if r.needs_human else "scored"
        print(f"{r.candidate_id:<18}{r.composite:>8.2f}   {st}")
    if args.json:
        json.dump([r.as_dict() for r in out], open(args.json, "w"), indent=2)
        print(f"\nfull audit record written to {args.json}")


def _audit(args):
    rankings = json.load(open(args.rankings))
    print(report(analyse(rankings, args.shortlist)))


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rubric")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("params", help="list the 50 parameters")
    a.add_argument("--family")
    a.add_argument("--industry")
    a.set_defaults(fn=_params)

    b = sub.add_parser("score", help="score a folder of CVs")
    b.add_argument("--job", required=True)
    b.add_argument("--cvs", required=True)
    b.add_argument("--json", help="write the full audit record here")
    b.add_argument("--today", help="YYYY-MM-DD, for reproducible date maths")
    b.add_argument("--industry", help="activate an industry pack")
    b.set_defaults(fn=_score)

    c = sub.add_parser("audit", help="shuffle audit on an existing tool")
    c.add_argument("--rankings", required=True, help="JSON: list of ranked id lists")
    c.add_argument("--shortlist", type=int, required=True)
    c.set_defaults(fn=_audit)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
