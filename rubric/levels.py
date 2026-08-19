"""Experience levels.

A level does NOT add parameters. It changes how much each family counts.

That distinction matters. If seniority added parameters, an entry-level
candidate would be scored on a different instrument from a senior one, and the
two scores would not be comparable. Instead every level scores the same things
and weights them differently -- so a 62 at entry and a 62 at director both mean
"met the bar for the level", and you can still see WHY they differ.

The progression encoded here:
  * education and proof of work carry most weight at entry, and decay steeply.
    Academic performance has real predictive validity for a first job and very
    little after roughly three years of work.
  * scope, trajectory and the role pack rise steadily.
  * technical skill DEPTH fades for executives -- not because it stops
    mattering, but because it stops being the thing you are hiring for.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Level:
    key: str
    label: str
    typical_years: str
    #: family -> multiplier applied to raw weights before renormalisation
    multipliers: dict[str, float] = field(default_factory=dict)
    note: str = ""


_D = 1.0   # families not listed keep their raw weight

LEVELS: dict[str, Level] = {
 "entry": Level("entry", "Entry / Graduate", "0–1 yrs", {
    "education": 2.2, "proof_of_work": 2.0, "skills": 1.3, "integrity": 1.2,
    "experience": 0.4, "scope": 0.3, "domain": 0.6, "trajectory": 0.4,
    "role": 0.8, "industry": 0.7},
    "There is no track record yet, so the evidence that exists -- what they "
    "studied and what they have built -- carries the load."),

 "junior": Level("junior", "Junior", "1–3 yrs", {
    "education": 1.6, "proof_of_work": 1.5, "skills": 1.3,
    "experience": 0.6, "scope": 0.5, "domain": 0.8, "trajectory": 0.6,
    "role": 0.9, "industry": 0.8}),

 "mid": Level("mid", "Mid-level", "3–6 yrs", {
    "education": 0.9, "proof_of_work": 1.1, "skills": 1.2,
    "experience": 1.0, "scope": 1.0, "trajectory": 1.0,
    "role": 1.1, "industry": 1.0},
    "The crossover point. Demonstrated work now outweighs credentials."),

 "senior": Level("senior", "Senior", "6–10 yrs", {
    "education": 0.6, "proof_of_work": 1.0, "skills": 1.1,
    "experience": 1.1, "scope": 1.3, "trajectory": 1.1,
    "role": 1.3, "industry": 1.1}),

 "lead": Level("lead", "Staff / Principal / Lead", "8–15 yrs", {
    "education": 0.5, "proof_of_work": 1.0, "skills": 1.0,
    "experience": 1.1, "scope": 1.5, "domain": 1.2, "trajectory": 1.3,
    "role": 1.4, "industry": 1.2},
    "Individual contributor, but scope is now the differentiator."),

 "manager": Level("manager", "Manager", "6–12 yrs", {
    "education": 0.5, "proof_of_work": 0.7, "skills": 0.7,
    "experience": 1.0, "scope": 1.6, "trajectory": 1.4,
    "role": 1.5, "industry": 1.2},
    "The first level where people outcomes count more than personal output."),

 "director": Level("director", "Director / Head of", "10–18 yrs", {
    "education": 0.5, "proof_of_work": 0.5, "skills": 0.5,
    "experience": 1.0, "scope": 1.8, "domain": 1.3, "trajectory": 1.5,
    "role": 1.7, "industry": 1.3}),

 "vp": Level("vp", "VP", "12–20 yrs", {
    "education": 0.5, "proof_of_work": 0.4, "skills": 0.35,
    "experience": 0.9, "scope": 1.9, "domain": 1.4, "trajectory": 1.6,
    "role": 1.9, "industry": 1.4}),

 "c_level": Level("c_level", "C-level (CEO / CTO / COO)", "15+ yrs", {
    "education": 0.5, "proof_of_work": 0.3, "skills": 0.25,
    "experience": 0.8, "scope": 2.0, "domain": 1.5, "trajectory": 1.7,
    "role": 2.2, "industry": 1.5},
    "Hire for judgement, scope and track record. Technical depth still "
    "matters for a CTO -- but it is table stakes, not the differentiator."),
}

ORDER = ["entry", "junior", "mid", "senior", "lead",
         "manager", "director", "vp", "c_level"]

#: Role packs that only make sense from these levels upward.
LEADERSHIP_ROLES = {"eng_leadership", "exec_leadership", "gtm_leadership"}
LEADERSHIP_MIN_LEVEL = {"manager", "director", "vp", "c_level"}


def get(level: str) -> Level:
    if level not in LEVELS:
        raise ValueError(f"unknown level '{level}'. "
                         f"Available: {', '.join(ORDER)}")
    return LEVELS[level]


def multiplier(level: str, family: str, role_families: set[str],
               industry_families: set[str]) -> float:
    """Resolve the multiplier for one family at one level."""
    lv = get(level)
    if family in role_families:
        return lv.multipliers.get("role", _D)
    if family in industry_families:
        return lv.multipliers.get("industry", _D)
    return lv.multipliers.get(family, _D)


def check_role_level(role: str | None, level: str) -> str | None:
    """Warn -- not raise -- when a pairing looks wrong. The recruiter decides."""
    if role in LEADERSHIP_ROLES and level not in LEADERSHIP_MIN_LEVEL:
        return (f"role '{role}' is a leadership pack but the level is "
                f"'{level}'. Leadership parameters expect manager and above; "
                f"most candidates will score near zero on them.")
    if role not in LEADERSHIP_ROLES and level in {"vp", "c_level"} and role:
        return (f"level '{level}' with an individual-contributor pack "
                f"('{role}'). If this is a leadership hire, use one of: "
                f"{', '.join(sorted(LEADERSHIP_ROLES))}.")
    return None
