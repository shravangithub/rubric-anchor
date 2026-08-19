"""
The 50 parameters.

Design rules, enforced by tests:
  1. Every parameter is scored on ONE candidate at a time, never against others.
     A score is a property of the person, not of the pile they arrived in.
  2. Every parameter declares HOW it is computed: CODE or MODEL.
     Anything an analyst could do with dates and a written rule is CODE.
  3. Every MODEL parameter must return evidence -- a verbatim span from the
     source document. No span, no score.
  4. A gate may only auto-reject if bona_fide is True. Everything else routes
     to a human.
  5. Protected attributes are not parameters and never will be. See BLOCKED.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class How(str, Enum):
    CODE = "code"      # deterministic, unit-testable, no model involved
    MODEL = "model"    # language model, must return an evidence span


class Kind(str, Enum):
    GATE = "gate"      # pass/fail
    SCORED = "scored"  # 0..100


@dataclass(frozen=True)
class Parameter:
    key: str
    label: str
    family: str
    kind: Kind
    how: How
    weight: float = 0.0          # only meaningful for SCORED
    bona_fide: bool = False      # only meaningful for GATE
    requires_evidence: bool = True
    notes: str = ""

    def __post_init__(self):
        if self.kind is Kind.SCORED and self.weight <= 0:
            raise ValueError(f"{self.key}: scored parameter needs a weight")
        if self.kind is Kind.GATE and self.weight:
            raise ValueError(f"{self.key}: gates must not carry a weight")


#: Attributes that must never become parameters, be inferred, or reach a score.
#: `guards.assert_no_protected_attributes` enforces this at runtime.
BLOCKED = frozenset({
    "age", "date_of_birth", "gender", "sex", "pronouns", "ethnicity", "race",
    "nationality", "national_origin", "religion", "caste", "disability",
    "health", "pregnancy", "marital_status", "parental_status",
    "sexual_orientation", "political_affiliation", "trade_union_membership",
    "photograph", "criminal_record",   # jurisdiction-specific; keep out by default
})


def _p(*a, **k) -> Parameter:
    return Parameter(*a, **k)


# ---------------------------------------------------------------------------
# 1. ELIGIBILITY  -- gates. All CODE. No model gets a vote on these.
# ---------------------------------------------------------------------------
ELIGIBILITY = [
    _p("work_authorization", "Authorised to work in the hiring location",
       "eligibility", Kind.GATE, How.CODE, bona_fide=True,
       notes="The only gate that auto-rejects by default."),
    _p("location_eligible", "Meets the role's location or onsite requirement",
       "eligibility", Kind.GATE, How.CODE, bona_fide=False),
    _p("notice_period_acceptable", "Notice period within the stated limit",
       "eligibility", Kind.GATE, How.CODE, bona_fide=False),
    _p("min_total_experience", "Meets minimum total professional experience",
       "eligibility", Kind.GATE, How.CODE, bona_fide=False,
       notes="Computed from dates. Never estimated by a model."),
    _p("min_relevant_experience", "Meets minimum experience in the job family",
       "eligibility", Kind.GATE, How.CODE, bona_fide=False),
    _p("required_licence", "Holds a legally required licence or registration",
       "eligibility", Kind.GATE, How.CODE, bona_fide=True,
       notes="Bona fide only where the licence is a legal precondition."),
    _p("education_minimum", "Meets a stated education requirement",
       "eligibility", Kind.GATE, How.CODE, bona_fide=False,
       notes="Deliberately NOT bona fide. Degree screens have weak "
             "job-performance validity and known adverse impact."),
    _p("availability_date", "Can start within the required window",
       "eligibility", Kind.GATE, How.CODE, bona_fide=False),
]

# ---------------------------------------------------------------------------
# 2. EXPERIENCE DEPTH -- all CODE, computed from dated employment records
# ---------------------------------------------------------------------------
EXPERIENCE = [
    _p("total_years_experience", "Total professional years",
       "experience", Kind.SCORED, How.CODE, 0.030),
    _p("relevant_years_experience", "Years within the target job family",
       "experience", Kind.SCORED, How.CODE, 0.045),
    _p("years_at_target_level", "Years already operating at the target level",
       "experience", Kind.SCORED, How.CODE, 0.035),
    _p("longest_tenure", "Longest single tenure",
       "experience", Kind.SCORED, How.CODE, 0.020),
    _p("average_tenure", "Average tenure across roles",
       "experience", Kind.SCORED, How.CODE, 0.020),
    _p("recency_of_relevant_work", "How recently the relevant work happened",
       "experience", Kind.SCORED, How.CODE, 0.030),
    _p("employment_continuity", "Proportion of the period in employment",
       "experience", Kind.SCORED, How.CODE, 0.015,
       notes="Gaps are neutral by default. Career breaks are common and "
             "penalising them has known adverse impact."),
    _p("progression_velocity", "Rate of level progression over time",
       "experience", Kind.SCORED, How.CODE, 0.025),
]

# ---------------------------------------------------------------------------
# 3. SKILLS -- MODEL, every one evidence-anchored
# ---------------------------------------------------------------------------
SKILLS = [
    _p("core_skill_coverage", "How many required core skills are evidenced",
       "skills", Kind.SCORED, How.MODEL, 0.060),
    _p("core_skill_depth", "Depth of evidence behind core skills",
       "skills", Kind.SCORED, How.MODEL, 0.055),
    _p("secondary_skill_coverage", "Coverage of nice-to-have skills",
       "skills", Kind.SCORED, How.MODEL, 0.020),
    _p("tooling_familiarity", "Familiarity with the role's tooling",
       "skills", Kind.SCORED, How.MODEL, 0.020),
    _p("technical_breadth", "Range across adjacent technical areas",
       "skills", Kind.SCORED, How.MODEL, 0.020),
    _p("hands_on_recency", "Recency of hands-on practice, not oversight",
       "skills", Kind.SCORED, How.MODEL, 0.025),
    _p("certification_relevance", "Relevance of certifications held",
       "skills", Kind.SCORED, How.MODEL, 0.010),
    _p("skill_evidence_specificity", "Specific claims vs generic assertions",
       "skills", Kind.SCORED, How.MODEL, 0.030),
    _p("self_directed_learning", "Evidence of acquiring new capability",
       "skills", Kind.SCORED, How.MODEL, 0.015),
    _p("skill_claim_verifiability", "Share of skill claims that carry evidence",
       "skills", Kind.SCORED, How.CODE, 0.025,
       notes="Computed from the evidence index, not judged."),
]

# ---------------------------------------------------------------------------
# 4. SCOPE & IMPACT
# ---------------------------------------------------------------------------
SCOPE = [
    _p("team_size_led", "Size of team led or coordinated",
       "scope", Kind.SCORED, How.MODEL, 0.030),
    _p("resource_scope", "Budget, headcount or system scope owned",
       "scope", Kind.SCORED, How.MODEL, 0.025),
    _p("project_complexity", "Complexity of problems taken on",
       "scope", Kind.SCORED, How.MODEL, 0.045),
    _p("cross_functional_reach", "Work spanning functions or organisations",
       "scope", Kind.SCORED, How.MODEL, 0.025),
    _p("outcome_quantification", "Outcomes stated with measurable results",
       "scope", Kind.SCORED, How.MODEL, 0.035),
    _p("ownership_end_to_end", "Owned something from start to finish",
       "scope", Kind.SCORED, How.MODEL, 0.040),
    _p("operational_responsibility", "On-call, incident or production duty",
       "scope", Kind.SCORED, How.MODEL, 0.020),
    _p("mentoring_evidence", "Developed other people",
       "scope", Kind.SCORED, How.MODEL, 0.020),
]

# ---------------------------------------------------------------------------
# 5. DOMAIN CONTEXT
# ---------------------------------------------------------------------------
DOMAIN = [
    _p("industry_relevance", "Relevance of industry background",
       "domain", Kind.SCORED, How.MODEL, 0.030),
    _p("regulated_environment", "Experience under regulatory constraint",
       "domain", Kind.SCORED, How.MODEL, 0.020),
    _p("company_stage_fit", "Fit with the organisation's stage",
       "domain", Kind.SCORED, How.MODEL, 0.020),
    _p("customer_segment_fit", "Experience with the relevant customer type",
       "domain", Kind.SCORED, How.MODEL, 0.015),
    _p("scale_of_systems", "Scale of systems, data or operations handled",
       "domain", Kind.SCORED, How.MODEL, 0.030),
    _p("market_experience", "Experience in the relevant geographic market",
       "domain", Kind.SCORED, How.MODEL, 0.015),
]

# ---------------------------------------------------------------------------
# 6. TRAJECTORY
# ---------------------------------------------------------------------------
TRAJECTORY = [
    _p("promotion_history", "Promotions within an employer",
       "trajectory", Kind.SCORED, How.MODEL, 0.030),
    _p("increasing_scope", "Scope grew role over role",
       "trajectory", Kind.SCORED, How.MODEL, 0.030),
    _p("role_coherence", "Roles form a coherent line of work",
       "trajectory", Kind.SCORED, How.MODEL, 0.020),
    _p("transition_clarity", "Career transitions are explained",
       "trajectory", Kind.SCORED, How.MODEL, 0.015),
    _p("level_readiness", "Readiness for the target level",
       "trajectory", Kind.SCORED, How.MODEL, 0.040),
]

# ---------------------------------------------------------------------------
# 7. INTEGRITY & DATA QUALITY -- CODE. These measure the RECORD, not the person.
# ---------------------------------------------------------------------------
INTEGRITY = [
    _p("claim_evidence_ratio", "Share of claims backed by a verbatim span",
       "integrity", Kind.SCORED, How.CODE, 0.030),
    _p("unverified_claim_count", "Claims dropped for missing evidence",
       "integrity", Kind.SCORED, How.CODE, 0.025),
    _p("internal_consistency", "Dates and titles agree across the document",
       "integrity", Kind.SCORED, How.CODE, 0.020),
    _p("timeline_completeness", "Timeline is reconstructable from the record",
       "integrity", Kind.SCORED, How.CODE, 0.015,
       notes="Measures the document, not the candidate. A sparse CV is a "
             "data problem to resolve with the candidate, not a demerit."),
    _p("inflation_risk", "Language overstates relative to evidence",
       "integrity", Kind.SCORED, How.CODE, 0.020),
]

ALL: list[Parameter] = (ELIGIBILITY + EXPERIENCE + SKILLS + SCOPE
                        + DOMAIN + TRAJECTORY + INTEGRITY)

BY_KEY = {p.key: p for p in ALL}
GATES = [p for p in ALL if p.kind is Kind.GATE]
SCORED = [p for p in ALL if p.kind is Kind.SCORED]
FAMILIES = sorted({p.family for p in ALL})


def total_weight() -> float:
    return round(sum(p.weight for p in SCORED), 6)


def normalised_weights(subset: list[str] | None = None) -> dict[str, float]:
    """Weights renormalised to 1.0 over the parameters actually in play."""
    ps = [p for p in SCORED if subset is None or p.key in subset]
    tot = sum(p.weight for p in ps)
    if tot <= 0:
        raise ValueError("no scored parameters selected")
    return {p.key: p.weight / tot for p in ps}
