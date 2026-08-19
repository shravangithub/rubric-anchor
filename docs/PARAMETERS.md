# Parameter reference

Generated with `python -m rubric params`. Regenerate after any change.

| key | family | kind | how | weight | auto-reject |
|---|---|---|---|---|---|
| `work_authorization` | eligibility | gate | code | — | **yes** |
| `location_eligible` | eligibility | gate | code | — | no |
| `notice_period_acceptable` | eligibility | gate | code | — | no |
| `min_total_experience` | eligibility | gate | code | — | no |
| `min_relevant_experience` | eligibility | gate | code | — | no |
| `required_licence` | eligibility | gate | code | — | **yes** |
| `education_minimum` | eligibility | gate | code | — | no |
| `availability_date` | eligibility | gate | code | — | no |
| `total_years_experience` | experience | scored | code | 0.030 | — |
| `relevant_years_experience` | experience | scored | code | 0.045 | — |
| `years_at_target_level` | experience | scored | code | 0.035 | — |
| `longest_tenure` | experience | scored | code | 0.020 | — |
| `average_tenure` | experience | scored | code | 0.020 | — |
| `recency_of_relevant_work` | experience | scored | code | 0.030 | — |
| `employment_continuity` | experience | scored | code | 0.015 | — |
| `progression_velocity` | experience | scored | code | 0.025 | — |
| `core_skill_coverage` | skills | scored | model | 0.060 | — |
| `core_skill_depth` | skills | scored | model | 0.055 | — |
| `secondary_skill_coverage` | skills | scored | model | 0.020 | — |
| `tooling_familiarity` | skills | scored | model | 0.020 | — |
| `technical_breadth` | skills | scored | model | 0.020 | — |
| `hands_on_recency` | skills | scored | model | 0.025 | — |
| `certification_relevance` | skills | scored | model | 0.010 | — |
| `skill_evidence_specificity` | skills | scored | model | 0.030 | — |
| `self_directed_learning` | skills | scored | model | 0.015 | — |
| `skill_claim_verifiability` | skills | scored | code | 0.025 | — |
| `team_size_led` | scope | scored | model | 0.030 | — |
| `resource_scope` | scope | scored | model | 0.025 | — |
| `project_complexity` | scope | scored | model | 0.045 | — |
| `cross_functional_reach` | scope | scored | model | 0.025 | — |
| `outcome_quantification` | scope | scored | model | 0.035 | — |
| `ownership_end_to_end` | scope | scored | model | 0.040 | — |
| `operational_responsibility` | scope | scored | model | 0.020 | — |
| `mentoring_evidence` | scope | scored | model | 0.020 | — |
| `industry_relevance` | domain | scored | model | 0.030 | — |
| `regulated_environment` | domain | scored | model | 0.020 | — |
| `company_stage_fit` | domain | scored | model | 0.020 | — |
| `customer_segment_fit` | domain | scored | model | 0.015 | — |
| `scale_of_systems` | domain | scored | model | 0.030 | — |
| `market_experience` | domain | scored | model | 0.015 | — |
| `promotion_history` | trajectory | scored | model | 0.030 | — |
| `increasing_scope` | trajectory | scored | model | 0.030 | — |
| `role_coherence` | trajectory | scored | model | 0.020 | — |
| `transition_clarity` | trajectory | scored | model | 0.015 | — |
| `level_readiness` | trajectory | scored | model | 0.040 | — |
| `claim_evidence_ratio` | integrity | scored | code | 0.030 | — |
| `unverified_claim_count` | integrity | scored | code | 0.025 | — |
| `internal_consistency` | integrity | scored | code | 0.020 | — |
| `timeline_completeness` | integrity | scored | code | 0.015 | — |
| `inflation_risk` | integrity | scored | code | 0.020 | — |

**50 parameters** — 22 computed in code, 28 model-scored.

Notes on specific parameters:

- **`work_authorization`** — The only gate that auto-rejects by default.
- **`min_total_experience`** — Computed from dates. Never estimated by a model.
- **`required_licence`** — Bona fide only where the licence is a legal precondition.
- **`education_minimum`** — Deliberately NOT bona fide. Degree screens have weak job-performance validity and known adverse impact.
- **`employment_continuity`** — Gaps are neutral by default. Career breaks are common and penalising them has known adverse impact.
- **`skill_claim_verifiability`** — Computed from the evidence index, not judged.
- **`timeline_completeness`** — Measures the document, not the candidate. A sparse CV is a data problem to resolve with the candidate, not a demerit.
