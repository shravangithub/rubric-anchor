"""Industry packs and extended families.

The core 50 in `parameters.py` are role-agnostic. Real hiring is not: what
counts as evidence of competence differs sharply between a GCC services firm
and a pharma QA team.

Rather than inflate the core, this module adds:

  * two extra CORE families -- education and proof of work -- that apply
    everywhere, and
  * ten INDUSTRY PACKS, one of which is activated per requisition.

A requisition therefore scores on  core + education + proof_of_work + one pack.
Weights renormalise to 1.0 over whatever is active, so activating a pack does
not silently shrink everything else out of proportion.
"""
from __future__ import annotations
from .parameters import Parameter, Kind, How, _p


# ===========================================================================
# EDUCATION -- a real criterion. The discipline is about auto-rejection,
# not about whether it may be scored at all.
# ===========================================================================
EDUCATION = [
    _p("required_credential", "Holds a legally mandated qualification",
       "education", Kind.GATE, How.CODE, bona_fide=True,
       notes="Bona fide ONLY where practising without it is unlawful -- "
             "medicine, law, chartered accountancy, pharmacy QP, structural "
             "engineering sign-off. Set bona_fide=False for everything else."),
    _p("qualification_level", "Highest qualification attained",
       "education", Kind.SCORED, How.CODE, 0.025),
    _p("field_of_study_relevance", "Field of study maps to the work",
       "education", Kind.SCORED, How.MODEL, 0.035),
    _p("academic_performance", "Grades or class where disclosed",
       "education", Kind.SCORED, How.MODEL, 0.020,
       notes="Weight this heavily only for early-career hiring. Predictive "
             "validity decays sharply after roughly three years of work."),
    _p("academic_distinction", "Rank, medal, scholarship, competitive entry",
       "education", Kind.SCORED, How.MODEL, 0.015),
    _p("academic_project_relevance", "Thesis or capstone relevant to the role",
       "education", Kind.SCORED, How.MODEL, 0.020),
    _p("certification_currency", "Certifications still valid, not lapsed",
       "education", Kind.SCORED, How.CODE, 0.015),
    _p("continuing_education_recency", "Recent formal upskilling",
       "education", Kind.SCORED, How.CODE, 0.015),
]
#: Deliberately absent: institution tier / college ranking. It is the single
#: strongest proxy for socio-economic background in most markets and adds
#: little over field-of-study plus demonstrated work. Add it only with a
#: documented validity study.

# ===========================================================================
# PROOF OF WORK -- externally verifiable artefacts. Stronger evidence than
# any self-asserted claim, because a third party can check it.
# ===========================================================================
PROOF_OF_WORK = [
    _p("public_repo_evidence", "Public code repositories attributable to them",
       "proof_of_work", Kind.SCORED, How.MODEL, 0.035),
    _p("contribution_substance", "Substantive commits, not forks or stars",
       "proof_of_work", Kind.SCORED, How.MODEL, 0.035),
    _p("contribution_recency", "Recency of public contribution",
       "proof_of_work", Kind.SCORED, How.CODE, 0.020),
    _p("open_source_maintainership", "Maintains or reviews for a project",
       "proof_of_work", Kind.SCORED, How.MODEL, 0.025),
    _p("publication_record", "Papers, articles or technical writing",
       "proof_of_work", Kind.SCORED, How.MODEL, 0.025),
    _p("patent_record", "Granted or filed patents",
       "proof_of_work", Kind.SCORED, How.MODEL, 0.015),
    _p("portfolio_artifacts", "Shipped work a third party can inspect",
       "proof_of_work", Kind.SCORED, How.MODEL, 0.030),
    _p("competitive_record", "Kaggle, CTF, ICPC, hackathon standing",
       "proof_of_work", Kind.SCORED, How.MODEL, 0.015),
]
#: Fairness note enforced in scoring: ABSENCE of proof of work is NEUTRAL,
#: never a penalty. Employer IP policy, NDAs, caregiving load and unpaid-time
#: inequality all suppress public output independently of ability. Presence is
#: strong positive evidence; absence is no evidence either way.

# ===========================================================================
# INDUSTRY PACKS
# ===========================================================================
def _pack(prefix: str, family: str,
          rows: list[tuple[str, str, How, float]]) -> list[Parameter]:
    """`prefix` keeps keys short and collision-free; `family` is what a human
    filters on (`--family fintech`, not `--family fin`)."""
    return [_p(f"{prefix}_{k}", label, family, Kind.SCORED, how, w)
            for k, label, how, w in rows]

#: IT services / consulting: delivering TO a client. For a captive centre
#: owning its own charter, use the `gcc` pack instead -- the dynamics differ.
SERVICES = _pack("svc", "services", [
    ("client_facing_exposure", "Direct client or stakeholder ownership", How.MODEL, .040),
    ("multi_engagement_range", "Delivered across several clients or accounts", How.MODEL, .030),
    ("delivery_model_fit", "Onsite / offshore / hybrid delivery experience", How.MODEL, .025),
    ("billable_utilisation_eq", "Sustained delivery under utilisation targets", How.MODEL, .020),
    ("estimation_and_sow", "Scoping, estimation, statement-of-work input", How.MODEL, .025),
    ("vendor_certification", "Partner certifications the practice requires", How.CODE, .020),
    ("transition_and_kt", "Ran knowledge transfer or account transition", How.MODEL, .020),
])

PRODUCT = _pack("prd", "product", [
    ("zero_to_one", "Took something from nothing to launched", How.MODEL, .045),
    ("user_research_evidence", "Decisions traceable to user evidence", How.MODEL, .035),
    ("experimentation_rigour", "A/B tests, cohorts, measured iteration", How.MODEL, .035),
    ("metric_ownership", "Owned a product metric, not just delivery", How.MODEL, .040),
    ("discovery_to_delivery", "Worked across discovery and delivery", How.MODEL, .025),
    ("sunsetting_judgement", "Killed or descoped work deliberately", How.MODEL, .015),
])

SAAS = _pack("saas", "saas", [
    ("multi_tenancy", "Built for multi-tenant isolation", How.MODEL, .040),
    ("subscription_metrics", "Worked against churn, NRR, activation", How.MODEL, .030),
    ("integration_surface", "Third-party integrations and webhooks", How.MODEL, .030),
    ("sla_and_uptime", "Operated to a contractual uptime commitment", How.MODEL, .030),
    ("self_serve_funnel", "Self-serve onboarding or PLG motion", How.MODEL, .025),
    ("tenant_data_isolation", "Data isolation and per-tenant compliance", How.MODEL, .030),
])

PAAS = _pack("paas", "paas", [
    ("api_design_quality", "Designed APIs others build on", How.MODEL, .045),
    ("developer_experience", "SDKs, docs, error surfaces, DX judgement", How.MODEL, .040),
    ("backward_compatibility", "Versioning and deprecation discipline", How.MODEL, .035),
    ("platform_adoption", "Drove internal or external adoption", How.MODEL, .030),
    ("extensibility_design", "Plugin, webhook or extension architecture", How.MODEL, .025),
    ("quota_and_abuse", "Rate limiting, quotas, abuse handling", How.MODEL, .020),
])

ECOMMERCE = _pack("ecom", "ecommerce", [
    ("catalog_scale", "Catalogue size and complexity handled", How.MODEL, .030),
    ("peak_event_readiness", "Sale-event or peak-load experience", How.MODEL, .040),
    ("payments_and_checkout", "Checkout, payments, failure recovery", How.MODEL, .035),
    ("fulfilment_logistics", "Inventory, warehousing, last-mile systems", How.MODEL, .030),
    ("conversion_optimisation", "Measured conversion or basket impact", How.MODEL, .030),
    ("marketplace_dynamics", "Seller-side or two-sided marketplace work", How.MODEL, .025),
    ("returns_and_fraud", "Returns, chargebacks, transaction fraud", How.MODEL, .020),
])

FINTECH = _pack("fin", "fintech", [
    ("regulatory_exposure", "Worked under RBI, PCI-DSS, SOC2, PSD2 or similar", How.MODEL, .045),
    ("ledger_and_reconciliation", "Double-entry ledger, reconciliation, settlement", How.MODEL, .045),
    ("risk_and_fraud", "Risk scoring, AML, KYC, fraud systems", How.MODEL, .035),
    ("money_movement", "Payment rails, clearing, payouts", How.MODEL, .035),
    ("audit_traceability", "Built systems that survive external audit", How.MODEL, .030),
    ("financial_accuracy_discipline", "Idempotency, exactly-once, no-loss design", How.MODEL, .035),
    ("licensing_awareness", "Understands the licence the product operates under", How.MODEL, .020),
])

#: Applied AI/ML: shipping models into a product. For a research lab pushing
#: the frontier, use `frontier_ai` -- different evidence entirely.
AI_ML = _pack("ai", "ai", [
    ("model_lifecycle", "Train, evaluate, deploy, monitor, retrain", How.MODEL, .045),
    ("evaluation_rigour", "Held-out sets, baselines, honest metrics", How.MODEL, .045),
    ("data_pipeline_ownership", "Owned data collection, labelling, quality", How.MODEL, .035),
    ("production_inference", "Served models under latency and cost constraint", How.MODEL, .035),
    ("domain_specialisation", "Depth in NLP, CV, RL, speech, recsys or similar", How.MODEL, .035),
    ("research_translation", "Turned papers into working systems", How.MODEL, .025),
    ("model_risk_and_safety", "Bias testing, red-teaming, failure analysis", How.MODEL, .030),
])

INFRA = _pack("infra", "infra", [
    ("reliability_engineering", "SLOs, error budgets, blameless postmortems", How.MODEL, .045),
    ("capacity_and_cost", "Capacity planning and cost optimisation", How.MODEL, .035),
    ("networking_depth", "Networking, load balancing, edge", How.MODEL, .030),
    ("systems_internals", "OS, kernel, storage or database internals", How.MODEL, .035),
    ("automation_and_iac", "Infrastructure as code, self-healing systems", How.MODEL, .030),
    ("migration_at_scale", "Ran a large migration without an outage", How.MODEL, .035),
    ("multi_region_dr", "Multi-region, failover, disaster recovery", How.MODEL, .025),
])

CYBERSEC = _pack("sec", "cybersec", [
    ("threat_modelling", "Structured threat modelling of real systems", How.MODEL, .040),
    ("incident_response", "Led or ran security incident response", How.MODEL, .045),
    ("offensive_capability", "Pentest, red team, vulnerability research", How.MODEL, .035),
    ("defensive_engineering", "Detection engineering, SIEM, hardening", How.MODEL, .035),
    ("compliance_frameworks", "ISO 27001, SOC2, NIST, DPDP implementation", How.MODEL, .030),
    ("security_certification", "OSCP, CISSP, CISM, GIAC and similar", How.CODE, .025),
    ("secure_sdlc", "Embedded security into the delivery lifecycle", How.MODEL, .025),
])

PHARMA = _pack("pha", "pharma", [
    ("gxp_experience", "Worked in a GxP-regulated environment", How.MODEL, .050),
    ("regulatory_submissions", "Contributed to regulatory filings", How.MODEL, .040),
    ("validation_and_qualification", "CSV, IQ/OQ/PQ, equipment qualification", How.MODEL, .035),
    ("quality_management_system", "Deviations, CAPA, change control", How.MODEL, .035),
    ("clinical_or_trial_exposure", "Clinical trial or study experience", How.MODEL, .030),
    ("audit_inspection_readiness", "Faced FDA, EMA, CDSCO or client audit", How.MODEL, .035),
    ("documentation_discipline", "ALCOA+ data integrity practice", How.MODEL, .025),
])


GCC = _pack("gcc", "gcc", [
    ("charter_ownership", "Owned a capability charter, not just execution", How.MODEL, .045),
    ("global_stakeholder_management", "Direct counterparts at the global HQ", How.MODEL, .040),
    ("captive_build_out", "Built or scaled a function inside the centre", How.MODEL, .035),
    ("vendor_to_captive_transition", "Moved work from vendor to in-house", How.MODEL, .030),
    ("distributed_timezone_delivery", "Sustained follow-the-sun collaboration", How.MODEL, .025),
    ("centre_talent_scaling", "Hired and grew teams locally", How.MODEL, .025),
    ("value_shift_evidence", "Moved work up from cost arbitrage to ownership", How.MODEL, .030),
])

FRONTIER_AI = _pack("fai", "frontier_ai", [
    ("research_publication", "Publications at top-tier venues", How.MODEL, .045),
    ("novel_contribution", "Original method, architecture or result", How.MODEL, .050),
    ("large_scale_training", "Trained or fine-tuned at significant scale", How.MODEL, .045),
    ("distributed_training_systems", "Multi-node parallelism and training infra", How.MODEL, .040),
    ("evaluation_design", "Designed evaluations, not merely ran them", How.MODEL, .035),
    ("alignment_and_safety", "Safety, interpretability or red-team research", How.MODEL, .040),
    ("open_source_impact", "Released models or tools with real adoption", How.MODEL, .030),
    ("compute_efficiency", "Got more capability from less compute", How.MODEL, .030),
])

INDUSTRY_PACKS: dict[str, list[Parameter]] = {
    "services":   SERVICES,
    "gcc":        GCC,
    "product":    PRODUCT,
    "saas":       SAAS,
    "paas":       PAAS,
    "ecommerce":  ECOMMERCE,
    "fintech":    FINTECH,
    "ai":         AI_ML,
    "frontier_ai": FRONTIER_AI,
    "infra":      INFRA,
    "cybersec":   CYBERSEC,
    "pharma":     PHARMA,
}

CORE_EXTENSIONS = EDUCATION + PROOF_OF_WORK

#: Parameters whose ABSENCE must never reduce a score. Presence is evidence;
#: absence is silence. Enforced by `scoring.apply_neutral_absence`.
NEUTRAL_IF_ABSENT = frozenset(p.key for p in PROOF_OF_WORK) | {
    "academic_distinction", "academic_performance", "patent_record",
    "continuing_education_recency",
}


def build_rubric(industry: str | None = None,
                 role: str | None = None,
                 include_education: bool = True,
                 include_proof_of_work: bool = True) -> list[Parameter]:
    """The active parameter set for one requisition.

    core + education + proof of work + one industry pack + one role pack.
    Level does not appear here -- it reweights, it does not add. See levels.py.
    """
    from .parameters import ALL as CORE
    from .roles import ROLE_PACKS
    out = list(CORE)
    if include_education:
        out += EDUCATION
    if include_proof_of_work:
        out += PROOF_OF_WORK
    if industry:
        key = industry.lower()
        if key not in INDUSTRY_PACKS:
            raise ValueError(
                f"unknown industry '{industry}'. "
                f"Available: {', '.join(sorted(INDUSTRY_PACKS))}")
        out += INDUSTRY_PACKS[key]
    if role:
        rkey = role.lower()
        if rkey not in ROLE_PACKS:
            raise ValueError(
                f"unknown role '{role}'. "
                f"Available: {', '.join(sorted(ROLE_PACKS))}")
        out += ROLE_PACKS[rkey]
    keys = [p.key for p in out]
    if len(keys) != len(set(keys)):
        dupes = {k for k in keys if keys.count(k) > 1}
        raise ValueError(f"duplicate parameter keys across packs: {dupes}")
    return out
