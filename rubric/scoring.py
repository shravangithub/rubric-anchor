"""Absolute scoring.

Each candidate is scored ALONE against a fixed rubric. Nothing here can see
another candidate -- that is enforced, not merely intended (see guards).
The consequence: a score is stable across batches, orderings and runs, which
is what makes it storable, comparable and auditable later.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date

from . import parameters as P
from .packs import NEUTRAL_IF_ABSENT, build_rubric
from .evidence import Claim, verify, evidence_ratio
from .guards import assert_no_protected_attributes, assert_single_candidate


@dataclass
class Result:
    candidate_id: str
    scores: dict[str, float] = field(default_factory=dict)
    gates: dict[str, bool] = field(default_factory=dict)
    composite: float = 0.0
    kept: list[Claim] = field(default_factory=list)
    dropped: list[Claim] = field(default_factory=list)
    needs_human: bool = False
    reasons: list[str] = field(default_factory=list)
    audit: list[dict] = field(default_factory=list)
    #: Parameters excluded from the composite because absence is not evidence.
    not_applicable: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {"candidate_id": self.candidate_id, "composite": self.composite,
                "gates": self.gates, "scores": self.scores,
                "needs_human": self.needs_human, "reasons": self.reasons,
                "not_applicable": self.not_applicable,
                "dropped_claims": [c.as_dict() for c in self.dropped],
                "audit": self.audit}


def months_between(start: str, end: str, today: date) -> int:
    sy, sm = (int(x) for x in start.split("-"))
    ey, em = (today.year, today.month) if end == "present" else \
             (int(end.split("-")[0]), int(end.split("-")[1]))
    return max(0, (ey - sy) * 12 + (em - sm))


def _cap(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def score_candidate(candidate_id: str, resume: str, job: dict,
                    extractor, today: date | None = None,
                    industry: str | None = None) -> Result:
    """Score ONE candidate against the rubric.

    `industry` activates a pack from `rubric.packs`. Absent it, only the
    role-agnostic core plus education and proof of work are scored.
    """
    assert_single_candidate(resume)
    assert_no_protected_attributes(job, "the job spec")
    today = today or date.today()
    r = Result(candidate_id=candidate_id)

    # ---- extract, then verify every span in CODE ------------------------
    emp = extractor.employment(resume)
    elig = extractor.eligibility(resume)
    raw: list[Claim] = [Claim("employment", e, e["span"], 0.95) for e in emp]
    for k, v in elig.items():
        raw.append(Claim(k, v["value"], v["span"], 0.9))
    kept, dropped = verify(raw, resume)
    r.kept, r.dropped = list(kept), list(dropped)
    r.audit.append({"step": "verify", "kept": len(kept), "dropped": len(dropped)})

    ver_emp = [c.value for c in kept if c.parameter == "employment"]
    ver = {c.parameter: c.value for c in kept if c.parameter != "employment"}

    # ---- gates: CODE only ------------------------------------------------
    total_m = sum(months_between(e["start"], e["end"], today) for e in ver_emp)
    fam = job.get("job_family_titles", [])
    rel_m = sum(months_between(e["start"], e["end"], today) for e in ver_emp
                if any(t.lower() in e["title"].lower() for t in fam))
    r.gates = {
        "work_authorization":     bool(ver.get("work_authorization", False)),
        "location_eligible":      job.get("location_required") is None,
        "notice_period_acceptable": (ver.get("notice_period_days") is None
                                     or ver["notice_period_days"] <= job.get("max_notice_days", 10**6)),
        "min_total_experience":   total_m / 12 >= job.get("min_total_years", 0),
        "min_relevant_experience": rel_m / 12 >= job.get("min_relevant_years", 0),
        "required_licence":       not job.get("required_licence"),
        "education_minimum":      True,
        "availability_date":      True,
    }

    # ---- scored: CODE parameters ----------------------------------------
    yrs, rel = total_m / 12, rel_m / 12
    longest = max((months_between(e["start"], e["end"], today) for e in ver_emp), default=0) / 12
    avg = (total_m / len(ver_emp) / 12) if ver_emp else 0
    recent = any(e["end"] == "present" for e in ver_emp)
    ratio = evidence_ratio(kept, dropped)

    code_scores = {
        "total_years_experience":    _cap(yrs / max(job.get("min_total_years", 5), 1) * 60),
        "relevant_years_experience": _cap(rel / max(job.get("min_relevant_years", 3), 1) * 60),
        "years_at_target_level":     _cap(rel * 12),
        "longest_tenure":            _cap(longest * 20),
        "average_tenure":            _cap(avg * 25),
        "recency_of_relevant_work":  100.0 if recent else 40.0,
        "employment_continuity":     _cap(70 + 30 * ratio),
        "progression_velocity":      _cap(len(ver_emp) * 18),
        "skill_claim_verifiability": _cap(ratio * 100),
        "claim_evidence_ratio":      _cap(ratio * 100),
        "unverified_claim_count":    _cap(100 - 20 * len(dropped)),
        "internal_consistency":      100.0 if ver_emp else 50.0,
        "timeline_completeness":     _cap(len(ver_emp) * 30),
        "inflation_risk":            _cap(100 - 25 * len(dropped)),
    }
    r.scores.update(code_scores)

    # ---- scored: MODEL parameters, each evidence-anchored ----------------
    active = build_rubric(industry)
    active_scored = [p for p in active if p.kind is P.Kind.SCORED]
    model_keys = [p.key for p in active_scored
                  if p.how is P.How.MODEL and p.key not in r.scores]
    mclaims = [extractor.score_parameter(k, resume, job) for k in model_keys]
    mkept, mdropped = verify(mclaims, resume)
    for c in mkept:
        r.scores[c.parameter] = float(c.value)
    for c in mdropped:
        if c.parameter in NEUTRAL_IF_ABSENT:
            # Absence is not evidence. Public repos, patents and academic
            # distinctions are suppressed by employer IP policy, NDAs,
            # caregiving load and unpaid-time inequality -- none of which
            # tell you anything about capability. Drop the parameter from
            # the composite entirely rather than scoring it zero.
            r.not_applicable.append(c.parameter)
        else:
            r.scores[c.parameter] = 0.0    # unevidenced -> contributes nothing
        r.dropped.append(c)
    r.audit.append({"step": "model_scores", "scored": len(mkept),
                    "unevidenced": len(mdropped),
                    "not_applicable": len(r.not_applicable)})

    # ---- composite: arithmetic, in code ---------------------------------
    # Weights renormalise over the parameters actually in play, so activating
    # an industry pack -- or excluding a not-applicable one -- rescales
    # cleanly instead of quietly shrinking everything else.
    weights = {p.key: p.weight for p in active_scored if p.key in r.scores}
    tot = sum(weights.values())
    r.composite = round(sum(r.scores[k] * (weights[k] / tot) for k in weights), 2)
    r.audit.append({"step": "composite", "parameters_used": len(weights),
                    "industry_pack": industry or "none"})

    # ---- policy ----------------------------------------------------------
    failed = [k for k, ok in r.gates.items() if not ok]
    non_auto = [k for k in failed if not P.BY_KEY[k].bona_fide]
    if non_auto:
        r.needs_human = True
        r.reasons.append(
            f"failed non-bona-fide gate(s) {non_auto} - a person must decide")
    elif failed:
        r.reasons.append(f"failed bona-fide gate(s) {failed}")
    if ratio < 0.7:
        r.needs_human = True
        r.reasons.append(f"only {ratio:.0%} of claims carried usable evidence")
    r.audit.append({"step": "policy", "gates_failed": failed,
                    "needs_human": r.needs_human})
    return r
