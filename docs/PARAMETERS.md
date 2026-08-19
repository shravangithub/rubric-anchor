# Parameter reference

Regenerate with `python -m rubric params [--industry X] [--family Y]`.

A requisition scores on: **core 50 + education 8 + proof of work 8 + one
industry pack** — 71 to 73 parameters depending on the pack. 133 are defined
in total; you never run all of them at once.

Weights renormalise to 1.0 over whatever is active, so activating a pack
rescales cleanly rather than quietly shrinking the core.

# Core (role-agnostic)

## ELIGIBILITY

*8 parameters, 8 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `work_authorization` — Authorised to work in the hiring location | gate | code | — | **yes** |
| `location_eligible` — Meets the role's location or onsite requirement | gate | code | — | no |
| `notice_period_acceptable` — Notice period within the stated limit | gate | code | — | no |
| `min_total_experience` — Meets minimum total professional experience | gate | code | — | no |
| `min_relevant_experience` — Meets minimum experience in the job family | gate | code | — | no |
| `required_licence` — Holds a legally required licence or registration | gate | code | — | **yes** |
| `education_minimum` — Meets a stated education requirement | gate | code | — | no |
| `availability_date` — Can start within the required window | gate | code | — | no |

## EXPERIENCE

*8 parameters, 8 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `total_years_experience` — Total professional years | scored | code | 0.030 | — |
| `relevant_years_experience` — Years within the target job family | scored | code | 0.045 | — |
| `years_at_target_level` — Years already operating at the target level | scored | code | 0.035 | — |
| `longest_tenure` — Longest single tenure | scored | code | 0.020 | — |
| `average_tenure` — Average tenure across roles | scored | code | 0.020 | — |
| `recency_of_relevant_work` — How recently the relevant work happened | scored | code | 0.030 | — |
| `employment_continuity` — Proportion of the period in employment | scored | code | 0.015 | — |
| `progression_velocity` — Rate of level progression over time | scored | code | 0.025 | — |

## SKILLS

*10 parameters, 1 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `core_skill_coverage` — How many required core skills are evidenced | scored | model | 0.060 | — |
| `core_skill_depth` — Depth of evidence behind core skills | scored | model | 0.055 | — |
| `secondary_skill_coverage` — Coverage of nice-to-have skills | scored | model | 0.020 | — |
| `tooling_familiarity` — Familiarity with the role's tooling | scored | model | 0.020 | — |
| `technical_breadth` — Range across adjacent technical areas | scored | model | 0.020 | — |
| `hands_on_recency` — Recency of hands-on practice, not oversight | scored | model | 0.025 | — |
| `certification_relevance` — Relevance of certifications held | scored | model | 0.010 | — |
| `skill_evidence_specificity` — Specific claims vs generic assertions | scored | model | 0.030 | — |
| `self_directed_learning` — Evidence of acquiring new capability | scored | model | 0.015 | — |
| `skill_claim_verifiability` — Share of skill claims that carry evidence | scored | code | 0.025 | — |

## SCOPE

*8 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `team_size_led` — Size of team led or coordinated | scored | model | 0.030 | — |
| `resource_scope` — Budget, headcount or system scope owned | scored | model | 0.025 | — |
| `project_complexity` — Complexity of problems taken on | scored | model | 0.045 | — |
| `cross_functional_reach` — Work spanning functions or organisations | scored | model | 0.025 | — |
| `outcome_quantification` — Outcomes stated with measurable results | scored | model | 0.035 | — |
| `ownership_end_to_end` — Owned something from start to finish | scored | model | 0.040 | — |
| `operational_responsibility` — On-call, incident or production duty | scored | model | 0.020 | — |
| `mentoring_evidence` — Developed other people | scored | model | 0.020 | — |

## DOMAIN

*6 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `industry_relevance` — Relevance of industry background | scored | model | 0.030 | — |
| `regulated_environment` — Experience under regulatory constraint | scored | model | 0.020 | — |
| `company_stage_fit` — Fit with the organisation's stage | scored | model | 0.020 | — |
| `customer_segment_fit` — Experience with the relevant customer type | scored | model | 0.015 | — |
| `scale_of_systems` — Scale of systems, data or operations handled | scored | model | 0.030 | — |
| `market_experience` — Experience in the relevant geographic market | scored | model | 0.015 | — |

## TRAJECTORY

*5 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `promotion_history` — Promotions within an employer | scored | model | 0.030 | — |
| `increasing_scope` — Scope grew role over role | scored | model | 0.030 | — |
| `role_coherence` — Roles form a coherent line of work | scored | model | 0.020 | — |
| `transition_clarity` — Career transitions are explained | scored | model | 0.015 | — |
| `level_readiness` — Readiness for the target level | scored | model | 0.040 | — |

## INTEGRITY

*5 parameters, 5 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `claim_evidence_ratio` — Share of claims backed by a verbatim span | scored | code | 0.030 | — |
| `unverified_claim_count` — Claims dropped for missing evidence | scored | code | 0.025 | — |
| `internal_consistency` — Dates and titles agree across the document | scored | code | 0.020 | — |
| `timeline_completeness` — Timeline is reconstructable from the record | scored | code | 0.015 | — |
| `inflation_risk` — Language overstates relative to evidence | scored | code | 0.020 | — |


# Core extensions (apply to every requisition)

## EDUCATION

Education is a legitimate scored signal. The discipline is about auto-rejection, not about whether it may be scored. Only `required_credential` may close a candidate, and only where practising without the qualification is unlawful.

**Deliberately absent: institution tier / college ranking.** It is the strongest single proxy for socio-economic background in most markets and adds little over field-of-study plus demonstrated work. A test asserts it stays out.

*8 parameters, 4 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `required_credential` — Holds a legally mandated qualification | gate | code | — | **yes** |
| `qualification_level` — Highest qualification attained | scored | code | 0.025 | — |
| `field_of_study_relevance` — Field of study maps to the work | scored | model | 0.035 | — |
| `academic_performance` — Grades or class where disclosed | scored | model | 0.020 | — |
| `academic_distinction` — Rank, medal, scholarship, competitive entry | scored | model | 0.015 | — |
| `academic_project_relevance` — Thesis or capstone relevant to the role | scored | model | 0.020 | — |
| `certification_currency` — Certifications still valid, not lapsed | scored | code | 0.015 | — |
| `continuing_education_recency` — Recent formal upskilling | scored | code | 0.015 | — |

## PROOF OF WORK

Externally verifiable artefacts — stronger evidence than any self-asserted claim, because a third party can check it.

**Absence is neutral, never a penalty.** Employer IP policy, NDAs, caregiving load and unpaid-time inequality all suppress public output independently of ability. When these parameters find no evidence they are dropped from the composite entirely rather than scored zero — see `NEUTRAL_IF_ABSENT` and `Result.not_applicable`.

*8 parameters, 1 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `public_repo_evidence` — Public code repositories attributable to them | scored | model | 0.035 | — |
| `contribution_substance` — Substantive commits, not forks or stars | scored | model | 0.035 | — |
| `contribution_recency` — Recency of public contribution | scored | code | 0.020 | — |
| `open_source_maintainership` — Maintains or reviews for a project | scored | model | 0.025 | — |
| `publication_record` — Papers, articles or technical writing | scored | model | 0.025 | — |
| `patent_record` — Granted or filed patents | scored | model | 0.015 | — |
| `portfolio_artifacts` — Shipped work a third party can inspect | scored | model | 0.030 | — |
| `competitive_record` — Kaggle, CTF, ICPC, hackathon standing | scored | model | 0.015 | — |


# Industry packs — activate exactly one

## AI  (`--industry ai`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `ai_model_lifecycle` — Train, evaluate, deploy, monitor, retrain | scored | model | 0.045 | — |
| `ai_evaluation_rigour` — Held-out sets, baselines, honest metrics | scored | model | 0.045 | — |
| `ai_data_pipeline_ownership` — Owned data collection, labelling, quality | scored | model | 0.035 | — |
| `ai_production_inference` — Served models under latency and cost constraint | scored | model | 0.035 | — |
| `ai_domain_specialisation` — Depth in NLP, CV, RL, speech, recsys or similar | scored | model | 0.035 | — |
| `ai_research_translation` — Turned papers into working systems | scored | model | 0.025 | — |
| `ai_model_risk_and_safety` — Bias testing, red-teaming, failure analysis | scored | model | 0.030 | — |

## CYBERSEC  (`--industry cybersec`)

*7 parameters, 1 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `sec_threat_modelling` — Structured threat modelling of real systems | scored | model | 0.040 | — |
| `sec_incident_response` — Led or ran security incident response | scored | model | 0.045 | — |
| `sec_offensive_capability` — Pentest, red team, vulnerability research | scored | model | 0.035 | — |
| `sec_defensive_engineering` — Detection engineering, SIEM, hardening | scored | model | 0.035 | — |
| `sec_compliance_frameworks` — ISO 27001, SOC2, NIST, DPDP implementation | scored | model | 0.030 | — |
| `sec_security_certification` — OSCP, CISSP, CISM, GIAC and similar | scored | code | 0.025 | — |
| `sec_secure_sdlc` — Embedded security into the delivery lifecycle | scored | model | 0.025 | — |

## ECOMMERCE  (`--industry ecommerce`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `ecom_catalog_scale` — Catalogue size and complexity handled | scored | model | 0.030 | — |
| `ecom_peak_event_readiness` — Sale-event or peak-load experience | scored | model | 0.040 | — |
| `ecom_payments_and_checkout` — Checkout, payments, failure recovery | scored | model | 0.035 | — |
| `ecom_fulfilment_logistics` — Inventory, warehousing, last-mile systems | scored | model | 0.030 | — |
| `ecom_conversion_optimisation` — Measured conversion or basket impact | scored | model | 0.030 | — |
| `ecom_marketplace_dynamics` — Seller-side or two-sided marketplace work | scored | model | 0.025 | — |
| `ecom_returns_and_fraud` — Returns, chargebacks, transaction fraud | scored | model | 0.020 | — |

## FINTECH  (`--industry fintech`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `fin_regulatory_exposure` — Worked under RBI, PCI-DSS, SOC2, PSD2 or similar | scored | model | 0.045 | — |
| `fin_ledger_and_reconciliation` — Double-entry ledger, reconciliation, settlement | scored | model | 0.045 | — |
| `fin_risk_and_fraud` — Risk scoring, AML, KYC, fraud systems | scored | model | 0.035 | — |
| `fin_money_movement` — Payment rails, clearing, payouts | scored | model | 0.035 | — |
| `fin_audit_traceability` — Built systems that survive external audit | scored | model | 0.030 | — |
| `fin_financial_accuracy_discipline` — Idempotency, exactly-once, no-loss design | scored | model | 0.035 | — |
| `fin_licensing_awareness` — Understands the licence the product operates under | scored | model | 0.020 | — |

## INFRA  (`--industry infra`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `infra_reliability_engineering` — SLOs, error budgets, blameless postmortems | scored | model | 0.045 | — |
| `infra_capacity_and_cost` — Capacity planning and cost optimisation | scored | model | 0.035 | — |
| `infra_networking_depth` — Networking, load balancing, edge | scored | model | 0.030 | — |
| `infra_systems_internals` — OS, kernel, storage or database internals | scored | model | 0.035 | — |
| `infra_automation_and_iac` — Infrastructure as code, self-healing systems | scored | model | 0.030 | — |
| `infra_migration_at_scale` — Ran a large migration without an outage | scored | model | 0.035 | — |
| `infra_multi_region_dr` — Multi-region, failover, disaster recovery | scored | model | 0.025 | — |

## PAAS  (`--industry paas`)

*6 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `paas_api_design_quality` — Designed APIs others build on | scored | model | 0.045 | — |
| `paas_developer_experience` — SDKs, docs, error surfaces, DX judgement | scored | model | 0.040 | — |
| `paas_backward_compatibility` — Versioning and deprecation discipline | scored | model | 0.035 | — |
| `paas_platform_adoption` — Drove internal or external adoption | scored | model | 0.030 | — |
| `paas_extensibility_design` — Plugin, webhook or extension architecture | scored | model | 0.025 | — |
| `paas_quota_and_abuse` — Rate limiting, quotas, abuse handling | scored | model | 0.020 | — |

## PHARMA  (`--industry pharma`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `pha_gxp_experience` — Worked in a GxP-regulated environment | scored | model | 0.050 | — |
| `pha_regulatory_submissions` — Contributed to regulatory filings | scored | model | 0.040 | — |
| `pha_validation_and_qualification` — CSV, IQ/OQ/PQ, equipment qualification | scored | model | 0.035 | — |
| `pha_quality_management_system` — Deviations, CAPA, change control | scored | model | 0.035 | — |
| `pha_clinical_or_trial_exposure` — Clinical trial or study experience | scored | model | 0.030 | — |
| `pha_audit_inspection_readiness` — Faced FDA, EMA, CDSCO or client audit | scored | model | 0.035 | — |
| `pha_documentation_discipline` — ALCOA+ data integrity practice | scored | model | 0.025 | — |

## PRODUCT  (`--industry product`)

*6 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `prd_zero_to_one` — Took something from nothing to launched | scored | model | 0.045 | — |
| `prd_user_research_evidence` — Decisions traceable to user evidence | scored | model | 0.035 | — |
| `prd_experimentation_rigour` — A/B tests, cohorts, measured iteration | scored | model | 0.035 | — |
| `prd_metric_ownership` — Owned a product metric, not just delivery | scored | model | 0.040 | — |
| `prd_discovery_to_delivery` — Worked across discovery and delivery | scored | model | 0.025 | — |
| `prd_sunsetting_judgement` — Killed or descoped work deliberately | scored | model | 0.015 | — |

## SAAS  (`--industry saas`)

*6 parameters, 0 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `saas_multi_tenancy` — Built for multi-tenant isolation | scored | model | 0.040 | — |
| `saas_subscription_metrics` — Worked against churn, NRR, activation | scored | model | 0.030 | — |
| `saas_integration_surface` — Third-party integrations and webhooks | scored | model | 0.030 | — |
| `saas_sla_and_uptime` — Operated to a contractual uptime commitment | scored | model | 0.030 | — |
| `saas_self_serve_funnel` — Self-serve onboarding or PLG motion | scored | model | 0.025 | — |
| `saas_tenant_data_isolation` — Data isolation and per-tenant compliance | scored | model | 0.030 | — |

## SERVICES  (`--industry services`)

*7 parameters, 1 computed in code*

| key | kind | how | weight | auto-reject |
|---|---|---|---|---|
| `svc_client_facing_exposure` — Direct client or stakeholder ownership | scored | model | 0.040 | — |
| `svc_multi_engagement_range` — Delivered across several clients or accounts | scored | model | 0.030 | — |
| `svc_delivery_model_fit` — Onsite / offshore / hybrid delivery experience | scored | model | 0.025 | — |
| `svc_billable_utilisation_eq` — Sustained delivery under utilisation targets | scored | model | 0.020 | — |
| `svc_estimation_and_sow` — Scoping, estimation, statement-of-work input | scored | model | 0.025 | — |
| `svc_vendor_certification` — Partner certifications the practice requires | scored | code | 0.020 | — |
| `svc_transition_and_kt` — Ran knowledge transfer or account transition | scored | model | 0.020 | — |


---

**133 parameters defined** across 19 families. 73 active on a fintech requisition.
