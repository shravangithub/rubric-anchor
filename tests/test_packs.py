import pytest
from datetime import date
from rubric import parameters as P
from rubric import packs
from rubric.scoring import score_candidate
from rubric.extractors import NullExtractor

CV = open("examples/resumes/C-1041.txt").read()
JOB = {"job_family_titles": ["engineer"], "min_total_years": 5,
       "min_relevant_years": 3, "max_notice_days": 60}
TODAY = date(2026, 8, 19)


def test_ten_industry_packs():
    assert len(packs.INDUSTRY_PACKS) == 10
    assert set(packs.INDUSTRY_PACKS) == {
        "services", "product", "saas", "paas", "ecommerce",
        "fintech", "ai", "infra", "cybersec", "pharma"}


def test_no_duplicate_keys_anywhere():
    for ind in packs.INDUSTRY_PACKS:
        keys = [p.key for p in packs.build_rubric(ind)]
        assert len(keys) == len(set(keys)), f"{ind} pack collides with core"


def test_unknown_industry_is_rejected_loudly():
    with pytest.raises(ValueError, match="unknown industry"):
        packs.build_rubric("blockchain-quantum")


def test_education_is_scorable_but_only_credentials_auto_reject():
    """Education may be scored. Only a legally mandated credential may reject."""
    gates = [p for p in packs.EDUCATION if p.kind is P.Kind.GATE]
    assert [g.key for g in gates] == ["required_credential"]
    assert gates[0].bona_fide is True
    assert any(p.key == "field_of_study_relevance" for p in packs.EDUCATION)


def test_institution_tier_is_not_a_parameter():
    """College ranking is the strongest proxy for socio-economic background
    in most markets. Adding it needs a documented validity study."""
    keys = " ".join(p.key for p in packs.build_rubric("product"))
    for banned in ("institution_tier", "college_rank", "university_rank",
                   "school_prestige", "tier_1_college"):
        assert banned not in keys


def test_absence_of_proof_of_work_is_neutral_not_penalised():
    """A candidate with no public repos must not be scored down for it."""
    r = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY)
    assert r.not_applicable, "expected some parameters to be suppressed"
    for k in r.not_applicable:
        assert k in packs.NEUTRAL_IF_ABSENT
        assert k not in r.scores, "suppressed parameters must leave the composite"


def test_every_proof_of_work_param_is_neutral_if_absent():
    for p in packs.PROOF_OF_WORK:
        assert p.key in packs.NEUTRAL_IF_ABSENT


def test_activating_a_pack_changes_what_is_scored():
    base = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY)
    fin = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY,
                          industry="fintech")
    assert len(fin.scores) > len(base.scores)
    assert any(k.startswith("fin_") for k in fin.scores)


def test_industry_scoring_is_still_deterministic():
    a = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY, industry="ai")
    b = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY, industry="ai")
    assert a.composite == b.composite


def test_composite_stays_bounded_with_any_pack():
    for ind in packs.INDUSTRY_PACKS:
        r = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY, industry=ind)
        assert 0.0 <= r.composite <= 100.0, ind


def test_every_pack_parameter_carries_a_weight():
    for ind, ps in packs.INDUSTRY_PACKS.items():
        for p in ps:
            assert p.kind is P.Kind.SCORED and p.weight > 0, f"{ind}:{p.key}"
