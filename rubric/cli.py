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
    rows = build_rubric(args.industry, getattr(args, "role", None))
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
        from .roles import ROLE_PACKS
        print(f"--industry: {', '.join(sorted(INDUSTRY_PACKS))}")
        print(f"--role    : {', '.join(sorted(ROLE_PACKS))}")


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
                            industry=args.industry or job.get("industry"),
                            role=args.role or job.get("role"),
                            level=args.level or job.get("level", "mid"))
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


def _validate(args):
    from .kg import PeopleGraph, Validity
    g = PeopleGraph(args.db)
    st = g.stats()
    print(f"people {st['people']} | requisitions {st['requisitions']} | "
          f"outcomes {st['outcomes']} | facts {st['facts']}\n")
    rows = Validity(g, args.min_group).report()
    if not rows:
        sys.exit("no scored facts in this graph yet")
    print(f"{'parameter':<30}{'n':>5}{'r(perf)':>9}{'sep':>7}  verdict")
    print("-" * 82)
    for v in rows:
        r = "--" if v.r_performance is None else f"{v.r_performance:+.3f}"
        sep = "--" if v.separation is None else f"{v.separation:+.1f}"
        print(f"{v.parameter:<30}{v.n:>5}{r:>9}{sep:>7}  {v.verdict}")
    print("\nSelection bias applies: performance data exists only for hires. "
          "Trust strong positives; treat weak negatives as artefacts.")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rubric")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("params", help="list the 50 parameters")
    a.add_argument("--family")
    a.add_argument("--industry")
    a.add_argument("--role")
    a.set_defaults(fn=_params)

    b = sub.add_parser("score", help="score a folder of CVs")
    b.add_argument("--job", required=True)
    b.add_argument("--cvs", required=True)
    b.add_argument("--json", help="write the full audit record here")
    b.add_argument("--today", help="YYYY-MM-DD, for reproducible date maths")
    b.add_argument("--industry", help="what kind of company")
    b.add_argument("--role", help="what the job is")
    b.add_argument("--level", help="seniority: entry..c_level (reweights)")
    b.set_defaults(fn=_score)

    c = sub.add_parser("audit", help="shuffle audit on an existing tool")
    c.add_argument("--rankings", required=True, help="JSON: list of ranked id lists")
    c.add_argument("--shortlist", type=int, required=True)
    c.set_defaults(fn=_audit)

    d = sub.add_parser("validate", help="which parameters actually predicted?")
    d.add_argument("--db", required=True, help="path to the people graph")
    d.add_argument("--min-group", type=int, default=5)
    d.set_defaults(fn=_validate)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
