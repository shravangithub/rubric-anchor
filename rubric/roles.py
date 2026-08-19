"""Role packs.

The third dimension. A requisition is now:

    core 50  +  education 8  +  proof of work 8
             +  one INDUSTRY pack (what kind of company)
             +  one ROLE pack     (what the job actually is)
             ×  one LEVEL profile (see levels.py -- reweights, adds nothing)

Roles are deliberately about *the work*, not the title. A "Senior Manager" at
one company is an IC at another; the level profile handles seniority, the role
pack handles what the person is expected to do.
"""
from __future__ import annotations
from .parameters import Parameter, Kind, How, _p


def _role(prefix: str, family: str,
          rows: list[tuple[str, str, How, float]]) -> list[Parameter]:
    return [_p(f"{prefix}_{k}", label, family, Kind.SCORED, how, w)
            for k, label, how, w in rows]


# ===========================================================================
# ENGINEERING & PRODUCT
# ===========================================================================
BACKEND = _role("be", "backend", [
    ("system_design_depth", "Designed systems, not just features", How.MODEL, .050),
    ("data_modelling", "Schema, consistency and storage choices", How.MODEL, .040),
    ("api_contract_discipline", "Versioning, compatibility, contracts", How.MODEL, .035),
    ("concurrency_and_state", "Concurrency, idempotency, race conditions", How.MODEL, .040),
    ("performance_tuning", "Profiled and improved real bottlenecks", How.MODEL, .035),
    ("testing_discipline", "Tests as a design tool, not an afterthought", How.MODEL, .030),
    ("production_debugging", "Diagnosed live production failures", How.MODEL, .035),
])

FDE = _role("fde", "fde", [
    ("customer_facing_delivery", "Built directly with and for a customer", How.MODEL, .050),
    ("ambiguity_tolerance", "Shipped without a written spec", How.MODEL, .045),
    ("integration_into_client_stack", "Worked inside someone else's system", How.MODEL, .040),
    ("solution_prototyping", "Fast prototypes that survived contact", How.MODEL, .035),
    ("technical_translation", "Turned business need into architecture", How.MODEL, .040),
    ("deployment_in_constrained_env", "Air-gapped, on-prem or regulated deploys", How.MODEL, .030),
    ("post_deploy_ownership", "Stayed with it after go-live", How.MODEL, .030),
])

DEVOPS = _role("dev", "devops", [
    ("pipeline_ownership", "Owned CI/CD end to end", How.MODEL, .045),
    ("infrastructure_as_code", "Declarative, reviewed, versioned infra", How.MODEL, .040),
    ("release_engineering", "Safe, frequent, reversible releases", How.MODEL, .040),
    ("container_orchestration", "Kubernetes or equivalent in production", How.MODEL, .035),
    ("secrets_and_supply_chain", "Secrets, artefact and dependency hygiene", How.MODEL, .030),
    ("environment_parity", "Reproducible environments", How.MODEL, .025),
    ("developer_enablement", "Made other engineers faster", How.MODEL, .035),
])

SRE = _role("sre", "sre", [
    ("slo_ownership", "Defined and defended SLOs", How.MODEL, .050),
    ("incident_command", "Ran incidents, not just attended them", How.MODEL, .045),
    ("observability_engineering", "Built the ability to see failures", How.MODEL, .040),
    ("toil_reduction", "Automated away recurring operational work", How.MODEL, .035),
    ("capacity_and_load", "Load testing, capacity, degradation modes", How.MODEL, .035),
    ("postmortem_quality", "Blameless analysis that changed something", How.MODEL, .030),
    ("chaos_and_resilience", "Deliberately tested failure paths", How.MODEL, .025),
])

QA = _role("qa", "qa", [
    ("test_strategy_design", "Designed a strategy, not just cases", How.MODEL, .050),
    ("automation_coverage", "Built durable automated suites", How.MODEL, .045),
    ("defect_analysis", "Root-caused rather than logged", How.MODEL, .040),
    ("risk_based_prioritisation", "Tested by risk, not by checklist", How.MODEL, .035),
    ("performance_and_load_testing", "Non-functional testing depth", How.MODEL, .030),
    ("shift_left_practice", "Quality moved earlier in the cycle", How.MODEL, .030),
    ("release_gatekeeping", "Held or released with evidence", How.MODEL, .025),
])

PRODUCT_MGR = _role("pm", "product_manager", [
    ("problem_framing", "Framed the problem before the solution", How.MODEL, .050),
    ("prioritisation_rigour", "Said no with a defensible reason", How.MODEL, .045),
    ("customer_evidence", "Decisions traceable to real users", How.MODEL, .045),
    ("metric_definition", "Chose and defended the right metric", How.MODEL, .040),
    ("cross_functional_influence", "Moved work without authority", How.MODEL, .035),
    ("roadmap_and_tradeoffs", "Sequenced under real constraint", How.MODEL, .030),
    ("launch_and_adoption", "Shipped and drove adoption", How.MODEL, .030),
])

# ===========================================================================
# GO-TO-MARKET & COMMERCIAL
# ===========================================================================
MARKETING = _role("mkt", "marketing", [
    ("positioning_and_messaging", "Sharpened how the product is described", How.MODEL, .045),
    ("channel_ownership", "Owned a channel to a number", How.MODEL, .045),
    ("pipeline_contribution", "Marketing-sourced pipeline attributed", How.MODEL, .050),
    ("content_and_demand", "Content that produced measurable demand", How.MODEL, .035),
    ("brand_and_category", "Built brand or defined a category", How.MODEL, .025),
    ("analytics_and_attribution", "Measured honestly, including failures", How.MODEL, .035),
    ("budget_efficiency", "CAC, ROAS or equivalent discipline", How.MODEL, .030),
])

SALES = _role("sal", "sales", [
    ("quota_attainment", "Consistent attainment against a stated number", How.MODEL, .055),
    ("deal_size_and_cycle", "Deal size and cycle length handled", How.MODEL, .045),
    ("complex_stakeholder_sale", "Multi-stakeholder or committee sales", How.MODEL, .040),
    ("pipeline_discipline", "Forecast accuracy and hygiene", How.MODEL, .035),
    ("negotiation_and_close", "Closed under real commercial pressure", How.MODEL, .035),
    ("territory_or_segment", "Segment and territory relevance", How.MODEL, .025),
    ("methodology_fluency", "MEDDIC, Challenger or similar, applied", How.MODEL, .025),
])

BIZDEV = _role("bd", "business_development", [
    ("partnership_origination", "Sourced partnerships that closed", How.MODEL, .050),
    ("commercial_structuring", "Structured terms, not just intros", How.MODEL, .045),
    ("new_market_entry", "Opened a market, segment or geography", How.MODEL, .045),
    ("ecosystem_relationships", "Durable relationships in the ecosystem", How.MODEL, .035),
    ("revenue_attribution", "Partnership revenue actually attributed", How.MODEL, .040),
    ("long_cycle_persistence", "Carried multi-quarter cycles", How.MODEL, .025),
])

SDR = _role("sdr", "sdr", [
    ("meeting_generation", "Qualified meetings booked against target", How.MODEL, .055),
    ("outbound_craft", "Personalised outbound that got replies", How.MODEL, .045),
    ("qualification_discipline", "Qualified out early and honestly", How.MODEL, .040),
    ("activity_consistency", "Sustained volume without burning lists", How.MODEL, .030),
    ("tooling_fluency", "CRM and sequencing tooling", How.MODEL, .025),
    ("coachability_evidence", "Improved measurably after feedback", How.MODEL, .035),
    ("ae_conversion_quality", "Meetings that converted downstream", How.MODEL, .040),
])

CUSTOMER_SUCCESS = _role("cs", "customer_success", [
    ("retention_and_renewal", "Owned renewal or gross retention", How.MODEL, .055),
    ("expansion_revenue", "Grew accounts, not just kept them", How.MODEL, .045),
    ("onboarding_and_time_to_value", "Shortened time to first value", How.MODEL, .040),
    ("escalation_handling", "Recovered at-risk accounts", How.MODEL, .040),
    ("product_feedback_loop", "Fed the field back into product", How.MODEL, .025),
    ("account_portfolio_scale", "Book size and account complexity", How.MODEL, .030),
    ("health_scoring_discipline", "Systematic account health practice", How.MODEL, .025),
])

# ===========================================================================
# LEADERSHIP -- pair with a senior LEVEL profile (director / vp / c_level)
# ===========================================================================
ENG_LEADERSHIP = _role("engl", "eng_leadership", [
    ("org_design_and_scaling", "Designed and scaled an engineering org", How.MODEL, .055),
    ("technical_strategy", "Set direction others could execute against", How.MODEL, .055),
    ("delivery_predictability", "Made delivery predictable at scale", How.MODEL, .045),
    ("hiring_and_bar_setting", "Built the hiring bar and held it", How.MODEL, .040),
    ("manager_development", "Grew managers, not only engineers", How.MODEL, .040),
    ("platform_vs_product_balance", "Balanced platform against roadmap", How.MODEL, .030),
    ("engineering_cost_ownership", "Owned build and run cost", How.MODEL, .030),
    ("exec_and_board_communication", "Credible with the board and peers", How.MODEL, .035),
])

EXEC_LEADERSHIP = _role("exec", "exec_leadership", [
    ("pnl_ownership", "Owned a profit and loss line", How.MODEL, .060),
    ("strategy_to_execution", "Set strategy and made it happen", How.MODEL, .055),
    ("capital_and_fundraising", "Raised or allocated capital", How.MODEL, .040),
    ("board_and_governance", "Operated with a board and governance", How.MODEL, .040),
    ("org_transformation", "Led a genuine change, not a reorg deck", How.MODEL, .045),
    ("market_and_competitive_read", "Read the market ahead of others", How.MODEL, .035),
    ("crisis_leadership", "Led through a real crisis", How.MODEL, .040),
    ("succession_and_bench", "Built a bench behind them", How.MODEL, .025),
])

GTM_LEADERSHIP = _role("gtml", "gtm_leadership", [
    ("revenue_ownership", "Carried a company-level revenue number", How.MODEL, .060),
    ("gtm_motion_design", "Designed the motion, not just ran it", How.MODEL, .050),
    ("team_scaling_and_quota", "Scaled a quota-carrying team", How.MODEL, .045),
    ("pricing_and_packaging", "Owned pricing and packaging decisions", How.MODEL, .040),
    ("forecast_credibility", "Forecasts the board could rely on", How.MODEL, .040),
    ("channel_and_partner_strategy", "Built channel or partner-led growth", How.MODEL, .030),
    ("customer_segment_expansion", "Moved the company up or down market", How.MODEL, .035),
])

ROLE_PACKS: dict[str, list[Parameter]] = {
    "backend": BACKEND, "fde": FDE, "devops": DEVOPS, "sre": SRE, "qa": QA,
    "product_manager": PRODUCT_MGR,
    "marketing": MARKETING, "sales": SALES,
    "business_development": BIZDEV, "sdr": SDR,
    "customer_success": CUSTOMER_SUCCESS,
    "eng_leadership": ENG_LEADERSHIP, "exec_leadership": EXEC_LEADERSHIP,
    "gtm_leadership": GTM_LEADERSHIP,
}

ROLE_GROUPS = {
    "Engineering & Product": ["backend", "fde", "devops", "sre", "qa", "product_manager"],
    "Go-to-market": ["marketing", "sales", "business_development", "sdr", "customer_success"],
    "Leadership": ["eng_leadership", "exec_leadership", "gtm_leadership"],
}
