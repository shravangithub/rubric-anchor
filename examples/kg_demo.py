"""Can the graph tell a parameter that predicts from one that merely separates?

We plant ground truth: three parameters genuinely predict later performance,
three drive hiring decisions but predict nothing, and the rest are noise.
Then we see whether `Validity` finds them without being told.

This is a simulation with a KNOWN answer -- that is the point. On real data
you never know the answer, which is exactly why you need the machinery.
"""
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rubric.kg import PeopleGraph, Validity
from rubric.scoring import Result

random.seed(17)
N = 400

TRULY_PREDICTIVE = ["be_system_design_depth", "ownership_end_to_end",
                    "outcome_quantification"]
LOOKS_GOOD_PREDICTS_NOTHING = ["qualification_level", "academic_performance",
                               "certification_relevance"]
NOISE = ["secondary_skill_coverage", "tooling_familiarity", "market_experience",
         "customer_segment_fit", "technical_breadth"]
ALL = TRULY_PREDICTIVE + LOOKS_GOOD_PREDICTS_NOTHING + NOISE

g = PeopleGraph(extractor_version="sim-1.0")

for i in range(N):
    cid = f"C{i:04d}"
    talent = random.gauss(0.55, 0.18)          # hidden. Nobody ever sees this.
    scores = {}
    for p in TRULY_PREDICTIVE:                  # tracks talent, noisily
        scores[p] = max(0, min(100, talent * 100 + random.gauss(0, 14)))
    for p in LOOKS_GOOD_PREDICTS_NOTHING:       # independent of talent
        scores[p] = max(0, min(100, random.gauss(55, 20)))
    for p in NOISE:
        scores[p] = max(0, min(100, random.gauss(50, 25)))

    # The recruiter's decision leans on BOTH the predictive parameters and the
    # credential ones -- which is exactly how a rubric acquires dead weight.
    decision = (sum(scores[p] for p in TRULY_PREDICTIVE) / 3 * 0.6
                + sum(scores[p] for p in LOOKS_GOOD_PREDICTS_NOTHING) / 3 * 0.4)
    r = Result(candidate_id=cid, scores=scores,
               composite=round(decision, 2), role_fit=None)
    g.ingest_result(r, "REQ-SIM", at="2024-01-15", config={"role": "backend"})

    hired = decision > 58
    g.record_outcome(cid, "REQ-SIM", "hired" if hired else "rejected",
                     at="2024-02-01")
    if hired:                                   # only hires get a rating
        g.record_performance(cid, rating=max(1, min(5, talent * 5 + random.gauss(0, .55))),
                             at="2025-02-01")

print(f"Simulated {N} candidates. {g.stats()['outcomes']} outcomes recorded.\n")
print("Ground truth (the graph is NOT told this):")
print(f"  genuinely predictive : {', '.join(TRULY_PREDICTIVE)}")
print(f"  drives hiring, predicts nothing : {', '.join(LOOKS_GOOD_PREDICTS_NOTHING)}")
print(f"  noise : {len(NOISE)} parameters\n")

print(f"{'parameter':<30}{'n':>5}{'r(perf)':>9}{'hired':>8}{'rej':>8}{'sep':>7}  verdict")
print("-" * 92)
for v in Validity(g, min_group=5).report():
    r = "--" if v.r_performance is None else f"{v.r_performance:+.3f}"
    print(f"{v.parameter:<30}{v.n:>5}{r:>9}"
          f"{('--' if v.mean_hired is None else f'{v.mean_hired:.1f}'):>8}"
          f"{('--' if v.mean_rejected is None else f'{v.mean_rejected:.1f}'):>8}"
          f"{('--' if v.separation is None else f'{v.separation:+.1f}'):>7}  {v.verdict}")

print("\n\nCounterfactual -- if we dropped a parameter, who would move?\n")
val = Validity(g)
for p in [TRULY_PREDICTIVE[0], LOOKS_GOOD_PREDICTS_NOTHING[0], NOISE[0]]:
    d = val.drop_one(p)
    print(f"  drop {d['parameter']:<28} -> {d['swapped']:>2} of {d['shortlist']} "
          f"shortlist places change ({d['pct_of_shortlist']}%)")

print("\n\nExplain one decision:\n")
for c in g.explain("C0007", "REQ-SIM", top=5):
    print(f"  {c['parameter']:<30} score {c['score']:>5.1f} x weight {c['weight']:.3f}"
          f"  = {c['share_pct']:>5}% of the score")
