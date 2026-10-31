# Parameter reference

Generated from the code by `python scripts/gen_parameters_md.py` — do not edit by hand. A test fails if this file is stale.

A requisition scores on: **core 50 + education 8 + proof of work 8 + one industry pack + one role pack**, reweighted by level. 247 parameters are defined in total (12 industry packs, 14 role packs); you never run all of them at once.

Weights renormalise to 1.0 over whatever is active, so activating a pack rescales cleanly rather than quietly shrinking the core. Level weights are in [`roles-levels.html`](roles-levels.html).

**No gate closes an application on its own.** A failed bona-fide gate proposes a rejection that a person confirms; every other gate routes to a person. A fact the CV does not state is Unknown — asked, never treated as a fail.

# Core (role-agnostic)

## ELIGIBILITY

*8 parameters, 8 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `work_authorization` — Authorised to work in the hiring location | gate | code | — | **propose rejection** — a person confirms |
| `location_eligible` — Meets the role's location or onsite requirement | gate | code | — | person decides |
| `notice_period_acceptable` — Notice period within the stated limit | gate | code | — | person decides |
| `min_total_experience` — Meets minimum total professional experience | gate | code | — | person decides |
| `min_relevant_experience` — Meets minimum experience in the job family | gate | code | — | person decides |
| `required_licence` — Holds a legally required licence or registration | gate | code | — | **propose rejection** — a person confirms |
| `education_minimum` — Meets a stated education requirement | gate | code | — | person decides |
| `availability_date` — Can start within the required window | gate | code | — | person decides |

## EXPERIENCE

*8 parameters, 8 computed in code*

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `industry_relevance` — Relevance of industry background | scored | model | 0.030 | — |
| `regulated_environment` — Experience under regulatory constraint | scored | model | 0.020 | — |
| `company_stage_fit` — Fit with the organisation's stage | scored | model | 0.020 | — |
| `customer_segment_fit` — Experience with the relevant customer type | scored | model | 0.015 | — |
| `scale_of_systems` — Scale of systems, data or operations handled | scored | model | 0.030 | — |
| `market_experience` — Experience in the relevant geographic market | scored | model | 0.015 | — |

## TRAJECTORY

*5 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `promotion_history` — Promotions within an employer | scored | model | 0.030 | — |
| `increasing_scope` — Scope grew role over role | scored | model | 0.030 | — |
| `role_coherence` — Roles form a coherent line of work | scored | model | 0.020 | — |
| `transition_clarity` — Career transitions are explained | scored | model | 0.015 | — |
| `level_readiness` — Readiness for the target level | scored | model | 0.040 | — |

## INTEGRITY

*5 parameters, 5 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `claim_evidence_ratio` — Share of claims backed by a verbatim span | scored | code | 0.030 | — |
| `unverified_claim_count` — Claims dropped for missing evidence | scored | code | 0.025 | — |
| `internal_consistency` — Dates and titles agree across the document | scored | code | 0.020 | — |
| `timeline_completeness` — Timeline is reconstructable from the record | scored | code | 0.015 | — |
| `inflation_risk` — Language overstates relative to evidence | scored | code | 0.020 | — |


# Core extensions (apply to every requisition)

## EDUCATION

Education is a legitimate scored signal. The discipline is about rejection, not about whether it may be scored. Only `required_credential` may propose a rejection, only where practising without the qualification is unlawful, and a person confirms it.

**Deliberately absent: institution tier / college ranking.** It is the strongest single proxy for socio-economic background in most markets and adds little over field-of-study plus demonstrated work. A test asserts it stays out.

*8 parameters, 4 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `required_credential` — Holds a legally mandated qualification | gate | code | — | **propose rejection** — a person confirms |
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

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `fin_regulatory_exposure` — Worked under RBI, PCI-DSS, SOC2, PSD2 or similar | scored | model | 0.045 | — |
| `fin_ledger_and_reconciliation` — Double-entry ledger, reconciliation, settlement | scored | model | 0.045 | — |
| `fin_risk_and_fraud` — Risk scoring, AML, KYC, fraud systems | scored | model | 0.035 | — |
| `fin_money_movement` — Payment rails, clearing, payouts | scored | model | 0.035 | — |
| `fin_audit_traceability` — Built systems that survive external audit | scored | model | 0.030 | — |
| `fin_financial_accuracy_discipline` — Idempotency, exactly-once, no-loss design | scored | model | 0.035 | — |
| `fin_licensing_awareness` — Understands the licence the product operates under | scored | model | 0.020 | — |

## FRONTIER_AI  (`--industry frontier_ai`)

*8 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `fai_research_publication` — Publications at top-tier venues | scored | model | 0.045 | — |
| `fai_novel_contribution` — Original method, architecture or result | scored | model | 0.050 | — |
| `fai_large_scale_training` — Trained or fine-tuned at significant scale | scored | model | 0.045 | — |
| `fai_distributed_training_systems` — Multi-node parallelism and training infra | scored | model | 0.040 | — |
| `fai_evaluation_design` — Designed evaluations, not merely ran them | scored | model | 0.035 | — |
| `fai_alignment_and_safety` — Safety, interpretability or red-team research | scored | model | 0.040 | — |
| `fai_open_source_impact` — Released models or tools with real adoption | scored | model | 0.030 | — |
| `fai_compute_efficiency` — Got more capability from less compute | scored | model | 0.030 | — |

## GCC  (`--industry gcc`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `gcc_charter_ownership` — Owned a capability charter, not just execution | scored | model | 0.045 | — |
| `gcc_global_stakeholder_management` — Direct counterparts at the global HQ | scored | model | 0.040 | — |
| `gcc_captive_build_out` — Built or scaled a function inside the centre | scored | model | 0.035 | — |
| `gcc_vendor_to_captive_transition` — Moved work from vendor to in-house | scored | model | 0.030 | — |
| `gcc_distributed_timezone_delivery` — Sustained follow-the-sun collaboration | scored | model | 0.025 | — |
| `gcc_centre_talent_scaling` — Hired and grew teams locally | scored | model | 0.025 | — |
| `gcc_value_shift_evidence` — Moved work up from cost arbitrage to ownership | scored | model | 0.030 | — |

## INFRA  (`--industry infra`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `paas_api_design_quality` — Designed APIs others build on | scored | model | 0.045 | — |
| `paas_developer_experience` — SDKs, docs, error surfaces, DX judgement | scored | model | 0.040 | — |
| `paas_backward_compatibility` — Versioning and deprecation discipline | scored | model | 0.035 | — |
| `paas_platform_adoption` — Drove internal or external adoption | scored | model | 0.030 | — |
| `paas_extensibility_design` — Plugin, webhook or extension architecture | scored | model | 0.025 | — |
| `paas_quota_and_abuse` — Rate limiting, quotas, abuse handling | scored | model | 0.020 | — |

## PHARMA  (`--industry pharma`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
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

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `prd_zero_to_one` — Took something from nothing to launched | scored | model | 0.045 | — |
| `prd_user_research_evidence` — Decisions traceable to user evidence | scored | model | 0.035 | — |
| `prd_experimentation_rigour` — A/B tests, cohorts, measured iteration | scored | model | 0.035 | — |
| `prd_metric_ownership` — Owned a product metric, not just delivery | scored | model | 0.040 | — |
| `prd_discovery_to_delivery` — Worked across discovery and delivery | scored | model | 0.025 | — |
| `prd_sunsetting_judgement` — Killed or descoped work deliberately | scored | model | 0.015 | — |

## SAAS  (`--industry saas`)

*6 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `saas_multi_tenancy` — Built for multi-tenant isolation | scored | model | 0.040 | — |
| `saas_subscription_metrics` — Worked against churn, NRR, activation | scored | model | 0.030 | — |
| `saas_integration_surface` — Third-party integrations and webhooks | scored | model | 0.030 | — |
| `saas_sla_and_uptime` — Operated to a contractual uptime commitment | scored | model | 0.030 | — |
| `saas_self_serve_funnel` — Self-serve onboarding or PLG motion | scored | model | 0.025 | — |
| `saas_tenant_data_isolation` — Data isolation and per-tenant compliance | scored | model | 0.030 | — |

## SERVICES  (`--industry services`)

*7 parameters, 1 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `svc_client_facing_exposure` — Direct client or stakeholder ownership | scored | model | 0.040 | — |
| `svc_multi_engagement_range` — Delivered across several clients or accounts | scored | model | 0.030 | — |
| `svc_delivery_model_fit` — Onsite / offshore / hybrid delivery experience | scored | model | 0.025 | — |
| `svc_billable_utilisation_eq` — Sustained delivery under utilisation targets | scored | model | 0.020 | — |
| `svc_estimation_and_sow` — Scoping, estimation, statement-of-work input | scored | model | 0.025 | — |
| `svc_vendor_certification` — Partner certifications the practice requires | scored | code | 0.020 | — |
| `svc_transition_and_kt` — Ran knowledge transfer or account transition | scored | model | 0.020 | — |


# Role packs — activate exactly one

## BACKEND  (`--role backend`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `be_system_design_depth` — Designed systems, not just features | scored | model | 0.050 | — |
| `be_data_modelling` — Schema, consistency and storage choices | scored | model | 0.040 | — |
| `be_api_contract_discipline` — Versioning, compatibility, contracts | scored | model | 0.035 | — |
| `be_concurrency_and_state` — Concurrency, idempotency, race conditions | scored | model | 0.040 | — |
| `be_performance_tuning` — Profiled and improved real bottlenecks | scored | model | 0.035 | — |
| `be_testing_discipline` — Tests as a design tool, not an afterthought | scored | model | 0.030 | — |
| `be_production_debugging` — Diagnosed live production failures | scored | model | 0.035 | — |

## FDE  (`--role fde`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `fde_customer_facing_delivery` — Built directly with and for a customer | scored | model | 0.050 | — |
| `fde_ambiguity_tolerance` — Shipped without a written spec | scored | model | 0.045 | — |
| `fde_integration_into_client_stack` — Worked inside someone else's system | scored | model | 0.040 | — |
| `fde_solution_prototyping` — Fast prototypes that survived contact | scored | model | 0.035 | — |
| `fde_technical_translation` — Turned business need into architecture | scored | model | 0.040 | — |
| `fde_deployment_in_constrained_env` — Air-gapped, on-prem or regulated deploys | scored | model | 0.030 | — |
| `fde_post_deploy_ownership` — Stayed with it after go-live | scored | model | 0.030 | — |

## DEVOPS  (`--role devops`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `dev_pipeline_ownership` — Owned CI/CD end to end | scored | model | 0.045 | — |
| `dev_infrastructure_as_code` — Declarative, reviewed, versioned infra | scored | model | 0.040 | — |
| `dev_release_engineering` — Safe, frequent, reversible releases | scored | model | 0.040 | — |
| `dev_container_orchestration` — Kubernetes or equivalent in production | scored | model | 0.035 | — |
| `dev_secrets_and_supply_chain` — Secrets, artefact and dependency hygiene | scored | model | 0.030 | — |
| `dev_environment_parity` — Reproducible environments | scored | model | 0.025 | — |
| `dev_developer_enablement` — Made other engineers faster | scored | model | 0.035 | — |

## SRE  (`--role sre`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `sre_slo_ownership` — Defined and defended SLOs | scored | model | 0.050 | — |
| `sre_incident_command` — Ran incidents, not just attended them | scored | model | 0.045 | — |
| `sre_observability_engineering` — Built the ability to see failures | scored | model | 0.040 | — |
| `sre_toil_reduction` — Automated away recurring operational work | scored | model | 0.035 | — |
| `sre_capacity_and_load` — Load testing, capacity, degradation modes | scored | model | 0.035 | — |
| `sre_postmortem_quality` — Blameless analysis that changed something | scored | model | 0.030 | — |
| `sre_chaos_and_resilience` — Deliberately tested failure paths | scored | model | 0.025 | — |

## QA  (`--role qa`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `qa_test_strategy_design` — Designed a strategy, not just cases | scored | model | 0.050 | — |
| `qa_automation_coverage` — Built durable automated suites | scored | model | 0.045 | — |
| `qa_defect_analysis` — Root-caused rather than logged | scored | model | 0.040 | — |
| `qa_risk_based_prioritisation` — Tested by risk, not by checklist | scored | model | 0.035 | — |
| `qa_performance_and_load_testing` — Non-functional testing depth | scored | model | 0.030 | — |
| `qa_shift_left_practice` — Quality moved earlier in the cycle | scored | model | 0.030 | — |
| `qa_release_gatekeeping` — Held or released with evidence | scored | model | 0.025 | — |

## PRODUCT_MANAGER  (`--role product_manager`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `pm_problem_framing` — Framed the problem before the solution | scored | model | 0.050 | — |
| `pm_prioritisation_rigour` — Said no with a defensible reason | scored | model | 0.045 | — |
| `pm_customer_evidence` — Decisions traceable to real users | scored | model | 0.045 | — |
| `pm_metric_definition` — Chose and defended the right metric | scored | model | 0.040 | — |
| `pm_cross_functional_influence` — Moved work without authority | scored | model | 0.035 | — |
| `pm_roadmap_and_tradeoffs` — Sequenced under real constraint | scored | model | 0.030 | — |
| `pm_launch_and_adoption` — Shipped and drove adoption | scored | model | 0.030 | — |

## MARKETING  (`--role marketing`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `mkt_positioning_and_messaging` — Sharpened how the product is described | scored | model | 0.045 | — |
| `mkt_channel_ownership` — Owned a channel to a number | scored | model | 0.045 | — |
| `mkt_pipeline_contribution` — Marketing-sourced pipeline attributed | scored | model | 0.050 | — |
| `mkt_content_and_demand` — Content that produced measurable demand | scored | model | 0.035 | — |
| `mkt_brand_and_category` — Built brand or defined a category | scored | model | 0.025 | — |
| `mkt_analytics_and_attribution` — Measured honestly, including failures | scored | model | 0.035 | — |
| `mkt_budget_efficiency` — CAC, ROAS or equivalent discipline | scored | model | 0.030 | — |

## SALES  (`--role sales`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `sal_quota_attainment` — Consistent attainment against a stated number | scored | model | 0.055 | — |
| `sal_deal_size_and_cycle` — Deal size and cycle length handled | scored | model | 0.045 | — |
| `sal_complex_stakeholder_sale` — Multi-stakeholder or committee sales | scored | model | 0.040 | — |
| `sal_pipeline_discipline` — Forecast accuracy and hygiene | scored | model | 0.035 | — |
| `sal_negotiation_and_close` — Closed under real commercial pressure | scored | model | 0.035 | — |
| `sal_territory_or_segment` — Segment and territory relevance | scored | model | 0.025 | — |
| `sal_methodology_fluency` — MEDDIC, Challenger or similar, applied | scored | model | 0.025 | — |

## BUSINESS_DEVELOPMENT  (`--role business_development`)

*6 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `bd_partnership_origination` — Sourced partnerships that closed | scored | model | 0.050 | — |
| `bd_commercial_structuring` — Structured terms, not just intros | scored | model | 0.045 | — |
| `bd_new_market_entry` — Opened a market, segment or geography | scored | model | 0.045 | — |
| `bd_ecosystem_relationships` — Durable relationships in the ecosystem | scored | model | 0.035 | — |
| `bd_revenue_attribution` — Partnership revenue actually attributed | scored | model | 0.040 | — |
| `bd_long_cycle_persistence` — Carried multi-quarter cycles | scored | model | 0.025 | — |

## SDR  (`--role sdr`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `sdr_meeting_generation` — Qualified meetings booked against target | scored | model | 0.055 | — |
| `sdr_outbound_craft` — Personalised outbound that got replies | scored | model | 0.045 | — |
| `sdr_qualification_discipline` — Qualified out early and honestly | scored | model | 0.040 | — |
| `sdr_activity_consistency` — Sustained volume without burning lists | scored | model | 0.030 | — |
| `sdr_tooling_fluency` — CRM and sequencing tooling | scored | model | 0.025 | — |
| `sdr_coachability_evidence` — Improved measurably after feedback | scored | model | 0.035 | — |
| `sdr_ae_conversion_quality` — Meetings that converted downstream | scored | model | 0.040 | — |

## CUSTOMER_SUCCESS  (`--role customer_success`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `cs_retention_and_renewal` — Owned renewal or gross retention | scored | model | 0.055 | — |
| `cs_expansion_revenue` — Grew accounts, not just kept them | scored | model | 0.045 | — |
| `cs_onboarding_and_time_to_value` — Shortened time to first value | scored | model | 0.040 | — |
| `cs_escalation_handling` — Recovered at-risk accounts | scored | model | 0.040 | — |
| `cs_product_feedback_loop` — Fed the field back into product | scored | model | 0.025 | — |
| `cs_account_portfolio_scale` — Book size and account complexity | scored | model | 0.030 | — |
| `cs_health_scoring_discipline` — Systematic account health practice | scored | model | 0.025 | — |

## ENG_LEADERSHIP  (`--role eng_leadership`)

*8 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `engl_org_design_and_scaling` — Designed and scaled an engineering org | scored | model | 0.055 | — |
| `engl_technical_strategy` — Set direction others could execute against | scored | model | 0.055 | — |
| `engl_delivery_predictability` — Made delivery predictable at scale | scored | model | 0.045 | — |
| `engl_hiring_and_bar_setting` — Built the hiring bar and held it | scored | model | 0.040 | — |
| `engl_manager_development` — Grew managers, not only engineers | scored | model | 0.040 | — |
| `engl_platform_vs_product_balance` — Balanced platform against roadmap | scored | model | 0.030 | — |
| `engl_engineering_cost_ownership` — Owned build and run cost | scored | model | 0.030 | — |
| `engl_exec_and_board_communication` — Credible with the board and peers | scored | model | 0.035 | — |

## EXEC_LEADERSHIP  (`--role exec_leadership`)

*8 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `exec_pnl_ownership` — Owned a profit and loss line | scored | model | 0.060 | — |
| `exec_strategy_to_execution` — Set strategy and made it happen | scored | model | 0.055 | — |
| `exec_capital_and_fundraising` — Raised or allocated capital | scored | model | 0.040 | — |
| `exec_board_and_governance` — Operated with a board and governance | scored | model | 0.040 | — |
| `exec_org_transformation` — Led a genuine change, not a reorg deck | scored | model | 0.045 | — |
| `exec_market_and_competitive_read` — Read the market ahead of others | scored | model | 0.035 | — |
| `exec_crisis_leadership` — Led through a real crisis | scored | model | 0.040 | — |
| `exec_succession_and_bench` — Built a bench behind them | scored | model | 0.025 | — |

## GTM_LEADERSHIP  (`--role gtm_leadership`)

*7 parameters, 0 computed in code*

| key | kind | how | weight | if the gate fails |
|---|---|---|---|---|
| `gtml_revenue_ownership` — Carried a company-level revenue number | scored | model | 0.060 | — |
| `gtml_gtm_motion_design` — Designed the motion, not just ran it | scored | model | 0.050 | — |
| `gtml_team_scaling_and_quota` — Scaled a quota-carrying team | scored | model | 0.045 | — |
| `gtml_pricing_and_packaging` — Owned pricing and packaging decisions | scored | model | 0.040 | — |
| `gtml_forecast_credibility` — Forecasts the board could rely on | scored | model | 0.040 | — |
| `gtml_channel_and_partner_strategy` — Built channel or partner-led growth | scored | model | 0.030 | — |
| `gtml_customer_segment_expansion` — Moved the company up or down market | scored | model | 0.035 | — |
