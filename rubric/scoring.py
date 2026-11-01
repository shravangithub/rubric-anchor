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
from .packs import NEUTRAL_IF_ABSENT, build_rubric, INDUSTRY_PACKS
from .roles import ROLE_PACKS
from . import levels as LV
from .evidence import NO_ANSWER, Claim, verify, evidence_ratio
from .guards import assert_no_protected_attributes, assert_single_candidate
from .redact import redact
from .injection import scan, flagged_lines, span_in_flagged
from ._version import __version__

#: Order of severity for `Result.decision`.
DECISIONS = ("proceed", "review", "confirm_reject")


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
    #: Mean score (0-100) across the ROLE pack only. Unlike `composite`, this
    #: IS comparable between different role packs, because it is a mean rather
    #: than a weighted sum over a pack-size-dependent denominator. Use it to
    #: ask "which role does this person fit best"; use `composite` to rank
    #: candidates WITHIN one requisition.
    role_fit: float | None = None
    industry_fit: float | None = None
    #: Facts the CV did not state. Unknown is not a fail: ask, don't reject.
    unknowns: list[str] = field(default_factory=list)
    #: proceed | review | confirm_reject. No path rejects without a person:
    #: even a failed bona-fide gate only PROPOSES the rejection.
    decision: str = "proceed"
    #: Lines that looked like instructions to a model (see injection.py).
    injection: list[dict] = field(default_factory=list)
    #: Redaction counts per category -- never the removed values.
    redaction: dict = field(default_factory=dict)
    #: What produced this result: package, extractor, model, prompt version.
    provenance: dict = field(default_factory=dict)

    def _escalate(self, to: str) -> None:
        if DECISIONS.index(to) > DECISIONS.index(self.decision):
            self.decision = to

    def as_dict(self) -> dict:
        return {"candidate_id": self.candidate_id, "composite": self.composite,
                "gates": self.gates, "scores": self.scores,
                "needs_human": self.needs_human, "reasons": self.reasons,
                "not_applicable": self.not_applicable,
                "role_fit": self.role_fit, "industry_fit": self.industry_fit,
                "decision": self.decision, "unknowns": self.unknowns,
                "injection": self.injection, "redaction": self.redaction,
                "provenance": self.provenance,
                "dropped_claims": [c.as_dict() for c in self.dropped],
                "unanswered": self.unanswered,
                "audit": self.audit}

    @property
    def unanswered(self) -> list[str]:
        """Criteria the model never answered (empty or unparseable reply after retries).
        They score 0, and a result with any is incomplete, not evidence."""
        return [c.parameter for c in self.dropped if c.reason == NO_ANSWER]


def months_between(start: str, end: str, today: date) -> int:
    sy, sm = (int(x) for x in start.split("-"))
    ey, em = (today.year, today.month) if end == "present" else \
             (int(end.split("-")[0]), int(end.split("-")[1]))
    return max(0, (ey - sy) * 12 + (em - sm))


def _cap(v: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, v))


def score_candidate(candidate_id: str, resume: str, job: dict,
                    extractor, today: date | None = None,
                    industry: str | None = None,
                    role: str | None = None,
                    level: str = "mid",
                    redact_pii: bool = True,
                    names: tuple[str, ...] | list[str] = (),
                    institutions: tuple[str, ...] | list[str] = (),
                    redact_proxies: bool = True) -> Result:
    """Score ONE candidate against the rubric.

    `industry`  what kind of company  -> adds a pack
    `role`      what the job is       -> adds a pack
    `level`     seniority             -> REWEIGHTS, adds nothing

    Same instrument at every level, weighted differently -- so a 62 at entry
    and a 62 at director both mean "met the bar for the level", and the
    difference between them is inspectable rather than hidden.

    `redact_pii`  on by default. The model sees -- and every span is verified
                  against -- the redacted text. Pass `names` / `institutions`
                  to remove those too.
    `redact_proxies`  on by default: languages spoken, hobbies, volunteering
                  and personal-details sections never reach the model either.
    """
    assert_single_candidate(resume)
    assert_no_protected_attributes(job, "the job spec")
    today = today or date.today()
    r = Result(candidate_id=candidate_id)
    r.provenance = {
        "package": __version__,
        "extractor": type(extractor).__name__,
        "model": getattr(extractor, "model_id", None),
        "prompt_version": getattr(extractor, "prompt_version", None),
        "redaction": redact_pii,
        "proxy_redaction": redact_pii and redact_proxies,
        "industry": industry, "role": role, "level": level,
        "today": today.isoformat(),
    }

    # ---- untrusted input: scan, then redact ------------------------------
    findings = scan(resume)
    if redact_pii:
        resume, rep = redact(resume, names, institutions, proxies=redact_proxies)
        r.redaction = rep.as_dict()
    flagged = flagged_lines(resume, findings)
    r.injection = [f.as_dict() for f in findings]
    if findings:
        r.audit.append({"step": "injection_scan", "findings": len(findings)})

    def _quarantine(kept_claims):
        """Text written TO the scorer can never be evidence FOR the scorer."""
        ok = []
        for c in kept_claims:
            if flagged and span_in_flagged(c.span, flagged):
                c.verified = False
                c.reason = "span is inside text flagged as a possible prompt injection"
                r.dropped.append(c)
            else:
                ok.append(c)
        return ok

    # ---- extract, then verify every span in CODE ------------------------
    emp = extractor.employment(resume)
    elig = extractor.eligibility(resume)
    raw: list[Claim] = [Claim("employment", e, e["span"], 0.95) for e in emp]
    for k, v in elig.items():
        raw.append(Claim(k, v["value"], v["span"], 0.9))
    kept, dropped = verify(raw, resume)
    r.dropped = list(dropped)
    kept = _quarantine(kept)
    dropped = list(r.dropped)
    r.kept = list(kept)
    r.audit.append({"step": "verify", "kept": len(kept), "dropped": len(dropped)})

    ver_emp = [c.value for c in kept if c.parameter == "employment"]
    ver = {c.parameter: c.value for c in kept if c.parameter != "employment"}

    # ---- gates: CODE only ------------------------------------------------
    total_m = sum(months_between(e["start"], e["end"], today) for e in ver_emp)
    fam = job.get("job_family_titles", [])
    rel_m = sum(months_between(e["start"], e["end"], today) for e in ver_emp
                if any(t.lower() in e["title"].lower() for t in fam))
    # Unknown is not a fail. A CV that does not mention work authorisation
    # has not said "no" -- ask the candidate (see notice.questions_for).
    for k in ("work_authorization", "notice_period_days"):
        if ver.get(k) is None:
            r.unknowns.append(k)
    if "work_authorization" in r.unknowns:
        r.reasons.append("work authorisation not stated in the CV - ask, don't reject")
    r.gates = {
        "work_authorization":     (True if ver.get("work_authorization") is None
                                   else bool(ver["work_authorization"])),
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
    warn = LV.check_role_level(role, level)
    if warn:
        r.reasons.append("configuration: " + warn)
        r.audit.append({"step": "config_warning", "detail": warn})
    active = build_rubric(industry, role)
    active_scored = [p for p in active if p.kind is P.Kind.SCORED]
    model_keys = [p.key for p in active_scored
                  if p.how is P.How.MODEL and p.key not in r.scores]
    if hasattr(extractor, "score_parameters"):
        mclaims = extractor.score_parameters(model_keys, resume, job)
    else:
        mclaims = [extractor.score_parameter(k, resume, job) for k in model_keys]
    mkept, mdropped = verify(mclaims, resume)
    _na = [c.parameter for c in mdropped if c.reason == NO_ANSWER]
    if _na:
        r.audit.append({"step": "unanswered", "criteria": _na})
        r.reasons.append(f"the model gave no answer for {len(_na)} criteria - score incomplete, rerun before relying on it")
    before = len(r.dropped)
    mkept = _quarantine(mkept)
    for c in r.dropped[before:]:
        mdropped.append(c)
        r.dropped.remove(c)
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
    role_fams = {p.family for p in ROLE_PACKS.get((role or "").lower(), [])}
    ind_fams = {p.family for p in INDUSTRY_PACKS.get((industry or "").lower(), [])}
    weights = {}
    for p in active_scored:
        if p.key in r.scores:
            weights[p.key] = p.weight * LV.multiplier(
                level, p.family, role_fams, ind_fams)
    tot = sum(weights.values())
    r.composite = round(sum(r.scores[k] * (weights[k] / tot) for k in weights), 2)
    r.audit.append({"step": "composite", "parameters_used": len(weights),
                    "industry_pack": industry or "none",
                    "role_pack": role or "none", "level": level})

    # ---- pack fit: comparable ACROSS packs, unlike the composite ---------
    def _mean(keys):
        vals = [r.scores[k] for k in keys if k in r.scores]
        return round(sum(vals) / len(vals), 2) if vals else None
    if role:
        r.role_fit = _mean([p.key for p in ROLE_PACKS[role.lower()]])
    if industry:
        r.industry_fit = _mean([p.key for p in INDUSTRY_PACKS[industry.lower()]])

    # ---- policy ----------------------------------------------------------
    failed = [k for k, ok in r.gates.items() if not ok]
    non_auto = [k for k in failed if not P.BY_KEY[k].bona_fide]
    bona = [k for k in failed if k not in non_auto]
    if non_auto:
        r.needs_human = True
        r._escalate("review")
        r.reasons.append(
            f"failed non-bona-fide gate(s) {non_auto} - a person must decide")
    if bona:
        # Hold-and-confirm. A bona-fide gate may PROPOSE a rejection, but a
        # person confirms it before anything reaches the candidate.
        r.needs_human = True
        r._escalate("confirm_reject")
        r.reasons.append(f"failed bona-fide gate(s) {bona} - rejection proposed; "
                         f"a person confirms before anything is sent")
    if ratio < 0.7:
        r.needs_human = True
        r._escalate("review")
        r.reasons.append(f"only {ratio:.0%} of claims carried usable evidence")
    if findings:
        r.needs_human = True
        r._escalate("review")
        lines_ = sorted({f.line for f in findings})
        r.reasons.append(f"possible prompt-injection text on line(s) {lines_} - "
                         f"a person checks before these scores are trusted")
    r.audit.append({"step": "policy", "gates_failed": failed,
                    "needs_human": r.needs_human, "decision": r.decision})
    return r
