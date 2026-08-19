"""The model seam.

Implement `Extractor` against any provider. The rest of the package never
imports an SDK, so the repo runs and its tests pass with no API key.
"""
from __future__ import annotations
import re
from typing import Protocol
from .evidence import Claim


class Extractor(Protocol):

    # --- role packs ---------------------------------------------------
    ROLE_CUES: dict[str, tuple[str, ...]] = {
      # backend
      "be_system_design_depth":("designed the","architecture","system","sharding"),
      "be_data_modelling":("schema","ledger","double-entry","storage"),
      "be_api_contract_discipline":("api","contract","versioning","rest"),
      "be_concurrency_and_state":("idempotency","exactly-once","concurrency","race"),
      "be_performance_tuning":("latency","throughput","p99","cut "),
      "be_testing_discipline":("wrote tests","test","coverage"),
      "be_production_debugging":("production","incident","debugged","on-call"),
      # fde
      "fde_customer_facing_delivery":("customer","client","onsite"),
      "fde_ambiguity_tolerance":("without a spec","ambiguity","undefined"),
      "fde_integration_into_client_stack":("integration","their stack","embedded"),
      "fde_solution_prototyping":("prototype","poc","pilot"),
      "fde_technical_translation":("business need","requirements","translated"),
      "fde_deployment_in_constrained_env":("on-prem","air-gapped","regulated"),
      "fde_post_deploy_ownership":("go-live","after launch","support"),
      # devops
      "dev_pipeline_ownership":("ci/cd","pipeline","build"),
      "dev_infrastructure_as_code":("terraform","infrastructure as code","iac"),
      "dev_release_engineering":("release","deploy","rollback"),
      "dev_container_orchestration":("kubernetes","container","docker"),
      "dev_secrets_and_supply_chain":("secrets","dependency","artefact"),
      "dev_environment_parity":("environment","reproducible","staging"),
      "dev_developer_enablement":("developer","faster","tooling"),
      # sre
      "sre_slo_ownership":("slo","error budget","availability"),
      "sre_incident_command":("incident command","sev-1","incident"),
      "sre_observability_engineering":("observability","tracing","monitoring"),
      "sre_toil_reduction":("toil","automating","automated"),
      "sre_capacity_and_load":("capacity","load","degradation"),
      "sre_postmortem_quality":("postmortem","blameless"),
      "sre_chaos_and_resilience":("chaos","failover","failure paths"),
      # qa
      "qa_test_strategy_design":("test strategy","strategy for"),
      "qa_automation_coverage":("automated suites","playwright","selenium","coverage"),
      "qa_defect_analysis":("root-caused","root cause","defect"),
      "qa_risk_based_prioritisation":("risk-based","prioritisation","critical paths"),
      "qa_performance_and_load_testing":("performance and load","load testing","peak"),
      "qa_shift_left_practice":("shift-left","earlier in the cycle"),
      "qa_release_gatekeeping":("held releases","release","gate"),
      # product manager
      "pm_problem_framing":("framed the","problem"),
      "pm_prioritisation_rigour":("prioritised","killed","deliberately"),
      "pm_customer_evidence":("user research","customers","interviews"),
      "pm_metric_definition":("as a metric","activation","churn","metric"),
      "pm_cross_functional_influence":("cross-functional","design and engineering"),
      "pm_roadmap_and_tradeoffs":("roadmap","tradeoff","sequenced"),
      "pm_launch_and_adoption":("adoption","after launch","launched"),
      # marketing
      "mkt_positioning_and_messaging":("positioning","messaging"),
      "mkt_channel_ownership":("channel","owned"),
      "mkt_pipeline_contribution":("pipeline","sourced"),
      "mkt_content_and_demand":("content","demand"),
      "mkt_brand_and_category":("brand","category"),
      "mkt_analytics_and_attribution":("attribution","analytics"),
      "mkt_budget_efficiency":("cac","roas","budget"),
      # sales
      "sal_quota_attainment":("quota","attainment","%"),
      "sal_deal_size_and_cycle":("deal size","cycle","lakh","crore"),
      "sal_complex_stakeholder_sale":("multi-stakeholder","committee","enterprise"),
      "sal_pipeline_discipline":("forecast","pipeline"),
      "sal_negotiation_and_close":("negotiation","close","closed"),
      "sal_territory_or_segment":("territory","segment"),
      "sal_methodology_fluency":("meddic","challenger","methodology"),
      # bizdev
      "bd_partnership_origination":("partnership","sourced","originated"),
      "bd_commercial_structuring":("structured","terms","commercial"),
      "bd_new_market_entry":("market entry","new market","geography"),
      "bd_ecosystem_relationships":("ecosystem","relationships"),
      "bd_revenue_attribution":("revenue","attributed"),
      "bd_long_cycle_persistence":("multi-quarter","long cycle"),
      # sdr
      "sdr_meeting_generation":("meetings","booked","target"),
      "sdr_outbound_craft":("outbound","sequences","reply rate"),
      "sdr_qualification_discipline":("qualified out","qualified"),
      "sdr_activity_consistency":("activity","sustained"),
      "sdr_tooling_fluency":("salesforce","outreach","crm"),
      "sdr_coachability_evidence":("after feedback","improved","coach"),
      "sdr_ae_conversion_quality":("converted","conversion"),
      # customer success
      "cs_retention_and_renewal":("retention","renewal"),
      "cs_expansion_revenue":("expansion","grew accounts","upsell"),
      "cs_onboarding_and_time_to_value":("onboarding","time to value"),
      "cs_escalation_handling":("escalation","at-risk","recovered"),
      "cs_product_feedback_loop":("feedback","into product"),
      "cs_account_portfolio_scale":("book","accounts","portfolio"),
      "cs_health_scoring_discipline":("health score","health"),
      # eng leadership
      "engl_org_design_and_scaling":("scaled the engineering org","org","from 18"),
      "engl_technical_strategy":("technical strategy","strategy others"),
      "engl_delivery_predictability":("predictable","delivery"),
      "engl_hiring_and_bar_setting":("hiring bar","hiring"),
      "engl_manager_development":("grew 6 managers","managers"),
      "engl_platform_vs_product_balance":("platform against roadmap","platform"),
      "engl_engineering_cost_ownership":("build and run cost","cost"),
      "engl_exec_and_board_communication":("board","credible with"),
      # exec leadership
      "exec_pnl_ownership":("p and l","p&l","revenue from"),
      "exec_strategy_to_execution":("set strategy","made it happen"),
      "exec_capital_and_fundraising":("raised","series","capital"),
      "exec_board_and_governance":("board and governance","governance"),
      "exec_org_transformation":("org transformation","transformation"),
      "exec_market_and_competitive_read":("read the market","competitors"),
      "exec_crisis_leadership":("crisis","led through"),
      "exec_succession_and_bench":("succession","bench"),
      # gtm leadership
      "gtml_revenue_ownership":("revenue","number"),
      "gtml_gtm_motion_design":("motion","go-to-market"),
      "gtml_team_scaling_and_quota":("quota-carrying","scaled a"),
      "gtml_pricing_and_packaging":("pricing","packaging"),
      "gtml_forecast_credibility":("forecast",),
      "gtml_channel_and_partner_strategy":("channel","partner"),
      "gtml_customer_segment_expansion":("up market","down market","segment"),
      # industry packs (abbreviated -- enough to exercise them)
      "fin_regulatory_exposure":("rbi","pci","compliance","regulat"),
      "fin_ledger_and_reconciliation":("ledger","reconciliation","double-entry"),
      "fin_risk_and_fraud":("fraud","kyc","aml","risk"),
      "fin_money_movement":("money movement","settlement","payments"),
      "fin_audit_traceability":("audit",),
      "fin_financial_accuracy_discipline":("idempotency","exactly-once"),
      "fin_licensing_awareness":("licence","license"),
      "saas_multi_tenancy":("multi-tenant","tenant"),
      "saas_subscription_metrics":("churn","activation","subscription"),
      "saas_integration_surface":("integration","webhook"),
      "saas_sla_and_uptime":("sla","uptime"),
      "saas_self_serve_funnel":("self-serve","funnel"),
      "saas_tenant_data_isolation":("isolation","data isolation"),
    }

    def employment(self, resume: str) -> list[dict]: ...
    def eligibility(self, resume: str) -> dict: ...
    def score_parameter(self, key: str, resume: str, rubric: dict) -> Claim: ...


class NullExtractor:
    """Deterministic stand-in. Same input -> same output, always.

    It is intentionally simple: it reads dated employment lines, looks for a
    work-authorisation statement, and scores MODEL parameters from keyword
    evidence. Replace it with a real client; keep the contract.
    """

    ROW = re.compile(
        r"(?im)^\s*[-*]?\s*(?P<title>[^|\n]+?)\s*\|\s*(?P<company>[^|\n]+?)\s*\|\s*"
        r"(?P<start>\d{4}-\d{2})\s*(?:to|-|–)\s*(?P<end>\d{4}-\d{2}|present)")

    CUES: dict[str, tuple[str, ...]] = {
        "core_skill_coverage":      ("distributed", "api", "pipeline", "service"),
        "core_skill_depth":         ("sharding", "consensus", "throughput", "latency"),
        "secondary_skill_coverage": ("sql", "kafka", "redis", "docker"),
        "tooling_familiarity":      ("kubernetes", "terraform", "airflow", "git"),
        "technical_breadth":        ("frontend", "data", "infra", "mobile"),
        "hands_on_recency":         ("built", "wrote", "implemented", "shipped"),
        "certification_relevance":  ("certified", "certification"),
        "skill_evidence_specificity": ("%", "reduced", "increased", "cut"),
        "self_directed_learning":   ("learned", "course", "self-taught"),
        "team_size_led":            ("team of", "engineers", "reports"),
        "resource_scope":           ("budget", "headcount", "portfolio"),
        "project_complexity":       ("migration", "rearchitect", "scale", "redesign"),
        "cross_functional_reach":   ("product", "design", "stakeholder", "cross-functional"),
        "outcome_quantification":   ("%", "x faster", "reduced", "saved"),
        "ownership_end_to_end":     ("owned", "led", "end to end", "from scratch"),
        "operational_responsibility": ("on-call", "oncall", "incident", "sre"),
        "mentoring_evidence":       ("mentored", "coached", "onboarded"),
        "industry_relevance":       ("payments", "fintech", "banking", "ledger"),
        "regulated_environment":    ("pci", "kyc", "compliance", "audit"),
        "company_stage_fit":        ("startup", "scale-up", "enterprise"),
        "customer_segment_fit":     ("b2b", "b2c", "enterprise", "consumer"),
        "scale_of_systems":         ("million", "tps", "qps", "petabyte"),
        "market_experience":        ("india", "emea", "apac", "us market"),
        "promotion_history":        ("promoted", "promotion"),
        "increasing_scope":         ("staff", "principal", "lead", "head of"),
        "role_coherence":           ("engineer", "developer", "architect"),
        "transition_clarity":       ("moved to", "transitioned", "joined to"),
        "level_readiness":          ("staff", "principal", "lead", "owned"),
    }


    # --- role packs ---------------------------------------------------
    ROLE_CUES: dict[str, tuple[str, ...]] = {
      # backend
      "be_system_design_depth":("designed the","architecture","system","sharding"),
      "be_data_modelling":("schema","ledger","double-entry","storage"),
      "be_api_contract_discipline":("api","contract","versioning","rest"),
      "be_concurrency_and_state":("idempotency","exactly-once","concurrency","race"),
      "be_performance_tuning":("latency","throughput","p99","cut "),
      "be_testing_discipline":("wrote tests","test","coverage"),
      "be_production_debugging":("production","incident","debugged","on-call"),
      # fde
      "fde_customer_facing_delivery":("customer","client","onsite"),
      "fde_ambiguity_tolerance":("without a spec","ambiguity","undefined"),
      "fde_integration_into_client_stack":("integration","their stack","embedded"),
      "fde_solution_prototyping":("prototype","poc","pilot"),
      "fde_technical_translation":("business need","requirements","translated"),
      "fde_deployment_in_constrained_env":("on-prem","air-gapped","regulated"),
      "fde_post_deploy_ownership":("go-live","after launch","support"),
      # devops
      "dev_pipeline_ownership":("ci/cd","pipeline","build"),
      "dev_infrastructure_as_code":("terraform","infrastructure as code","iac"),
      "dev_release_engineering":("release","deploy","rollback"),
      "dev_container_orchestration":("kubernetes","container","docker"),
      "dev_secrets_and_supply_chain":("secrets","dependency","artefact"),
      "dev_environment_parity":("environment","reproducible","staging"),
      "dev_developer_enablement":("developer","faster","tooling"),
      # sre
      "sre_slo_ownership":("slo","error budget","availability"),
      "sre_incident_command":("incident command","sev-1","incident"),
      "sre_observability_engineering":("observability","tracing","monitoring"),
      "sre_toil_reduction":("toil","automating","automated"),
      "sre_capacity_and_load":("capacity","load","degradation"),
      "sre_postmortem_quality":("postmortem","blameless"),
      "sre_chaos_and_resilience":("chaos","failover","failure paths"),
      # qa
      "qa_test_strategy_design":("test strategy","strategy for"),
      "qa_automation_coverage":("automated suites","playwright","selenium","coverage"),
      "qa_defect_analysis":("root-caused","root cause","defect"),
      "qa_risk_based_prioritisation":("risk-based","prioritisation","critical paths"),
      "qa_performance_and_load_testing":("performance and load","load testing","peak"),
      "qa_shift_left_practice":("shift-left","earlier in the cycle"),
      "qa_release_gatekeeping":("held releases","release","gate"),
      # product manager
      "pm_problem_framing":("framed the","problem"),
      "pm_prioritisation_rigour":("prioritised","killed","deliberately"),
      "pm_customer_evidence":("user research","customers","interviews"),
      "pm_metric_definition":("as a metric","activation","churn","metric"),
      "pm_cross_functional_influence":("cross-functional","design and engineering"),
      "pm_roadmap_and_tradeoffs":("roadmap","tradeoff","sequenced"),
      "pm_launch_and_adoption":("adoption","after launch","launched"),
      # marketing
      "mkt_positioning_and_messaging":("positioning","messaging"),
      "mkt_channel_ownership":("channel","owned"),
      "mkt_pipeline_contribution":("pipeline","sourced"),
      "mkt_content_and_demand":("content","demand"),
      "mkt_brand_and_category":("brand","category"),
      "mkt_analytics_and_attribution":("attribution","analytics"),
      "mkt_budget_efficiency":("cac","roas","budget"),
      # sales
      "sal_quota_attainment":("quota","attainment","%"),
      "sal_deal_size_and_cycle":("deal size","cycle","lakh","crore"),
      "sal_complex_stakeholder_sale":("multi-stakeholder","committee","enterprise"),
      "sal_pipeline_discipline":("forecast","pipeline"),
      "sal_negotiation_and_close":("negotiation","close","closed"),
      "sal_territory_or_segment":("territory","segment"),
      "sal_methodology_fluency":("meddic","challenger","methodology"),
      # bizdev
      "bd_partnership_origination":("partnership","sourced","originated"),
      "bd_commercial_structuring":("structured","terms","commercial"),
      "bd_new_market_entry":("market entry","new market","geography"),
      "bd_ecosystem_relationships":("ecosystem","relationships"),
      "bd_revenue_attribution":("revenue","attributed"),
      "bd_long_cycle_persistence":("multi-quarter","long cycle"),
      # sdr
      "sdr_meeting_generation":("meetings","booked","target"),
      "sdr_outbound_craft":("outbound","sequences","reply rate"),
      "sdr_qualification_discipline":("qualified out","qualified"),
      "sdr_activity_consistency":("activity","sustained"),
      "sdr_tooling_fluency":("salesforce","outreach","crm"),
      "sdr_coachability_evidence":("after feedback","improved","coach"),
      "sdr_ae_conversion_quality":("converted","conversion"),
      # customer success
      "cs_retention_and_renewal":("retention","renewal"),
      "cs_expansion_revenue":("expansion","grew accounts","upsell"),
      "cs_onboarding_and_time_to_value":("onboarding","time to value"),
      "cs_escalation_handling":("escalation","at-risk","recovered"),
      "cs_product_feedback_loop":("feedback","into product"),
      "cs_account_portfolio_scale":("book","accounts","portfolio"),
      "cs_health_scoring_discipline":("health score","health"),
      # eng leadership
      "engl_org_design_and_scaling":("scaled the engineering org","org","from 18"),
      "engl_technical_strategy":("technical strategy","strategy others"),
      "engl_delivery_predictability":("predictable","delivery"),
      "engl_hiring_and_bar_setting":("hiring bar","hiring"),
      "engl_manager_development":("grew 6 managers","managers"),
      "engl_platform_vs_product_balance":("platform against roadmap","platform"),
      "engl_engineering_cost_ownership":("build and run cost","cost"),
      "engl_exec_and_board_communication":("board","credible with"),
      # exec leadership
      "exec_pnl_ownership":("p and l","p&l","revenue from"),
      "exec_strategy_to_execution":("set strategy","made it happen"),
      "exec_capital_and_fundraising":("raised","series","capital"),
      "exec_board_and_governance":("board and governance","governance"),
      "exec_org_transformation":("org transformation","transformation"),
      "exec_market_and_competitive_read":("read the market","competitors"),
      "exec_crisis_leadership":("crisis","led through"),
      "exec_succession_and_bench":("succession","bench"),
      # gtm leadership
      "gtml_revenue_ownership":("revenue","number"),
      "gtml_gtm_motion_design":("motion","go-to-market"),
      "gtml_team_scaling_and_quota":("quota-carrying","scaled a"),
      "gtml_pricing_and_packaging":("pricing","packaging"),
      "gtml_forecast_credibility":("forecast",),
      "gtml_channel_and_partner_strategy":("channel","partner"),
      "gtml_customer_segment_expansion":("up market","down market","segment"),
      # industry packs (abbreviated -- enough to exercise them)
      "fin_regulatory_exposure":("rbi","pci","compliance","regulat"),
      "fin_ledger_and_reconciliation":("ledger","reconciliation","double-entry"),
      "fin_risk_and_fraud":("fraud","kyc","aml","risk"),
      "fin_money_movement":("money movement","settlement","payments"),
      "fin_audit_traceability":("audit",),
      "fin_financial_accuracy_discipline":("idempotency","exactly-once"),
      "fin_licensing_awareness":("licence","license"),
      "saas_multi_tenancy":("multi-tenant","tenant"),
      "saas_subscription_metrics":("churn","activation","subscription"),
      "saas_integration_surface":("integration","webhook"),
      "saas_sla_and_uptime":("sla","uptime"),
      "saas_self_serve_funnel":("self-serve","funnel"),
      "saas_tenant_data_isolation":("isolation","data isolation"),
    }

    def employment(self, resume: str) -> list[dict]:
        return [{"title": m.group("title").strip(),
                 "company": m.group("company").strip(),
                 "start": m.group("start"),
                 "end": m.group("end").lower(),
                 "span": m.group(0).strip()}
                for m in self.ROW.finditer(resume)]

    def eligibility(self, resume: str) -> dict:
        out = {}
        m = re.search(r"(?im)^.*work\s*authoris?z?ation.*$", resume)
        if m:
            out["work_authorization"] = {
                "value": not re.search(r"(?i)\b(not|no|requires? sponsorship)\b", m.group(0)),
                "span": m.group(0).strip()}
        m = re.search(r"(?im)^.*notice period.*$", resume)
        if m:
            d = re.search(r"(\d+)\s*(day|week|month)", m.group(0), re.I)
            out["notice_period_days"] = {
                "value": _to_days(d) if d else None, "span": m.group(0).strip()}
        return out

    def score_parameter(self, key: str, resume: str, rubric: dict) -> Claim:
        cues = self.CUES.get(key) or self.ROLE_CUES.get(key, ())
        hits, span = [], ""
        for c in cues:
            m = re.search(r"(?im)^.*" + re.escape(c) + r".*$", resume)
            if m:
                hits.append(c)
                span = span or m.group(0).strip()
        score = 0.0 if not cues else min(100.0, 22.0 * len(hits))
        return Claim(parameter=key, value=score, span=span,
                     confidence=0.6 if hits else 0.2)


def _to_days(m) -> int:
    n, unit = int(m.group(1)), m.group(2).lower()
    return n * {"day": 1, "week": 7, "month": 30}[unit]
