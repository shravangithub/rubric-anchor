import re

import pytest
from rubric import parameters as P


def test_exactly_fifty():
    assert len(P.ALL) == 50
    assert len(set(p.key for p in P.ALL)) == 50, "duplicate parameter key"


def test_gates_and_scored_split():
    assert len(P.GATES) + len(P.SCORED) == 50
    assert all(p.weight == 0 for p in P.GATES)
    assert all(p.weight > 0 for p in P.SCORED)


def test_only_bona_fide_gates_may_auto_reject():
    auto = [p.key for p in P.GATES if p.bona_fide]
    assert set(auto) == {"work_authorization", "required_licence"}, (
        "widening the auto-reject list is a policy change and must be "
        "deliberate -- update this test with the reason")


def test_education_is_not_bona_fide():
    """Degree screens have weak validity and known adverse impact."""
    assert P.BY_KEY["education_minimum"].bona_fide is False


def test_no_parameter_names_a_protected_attribute():
    """Whole-word matching only: 'average_tenure' legitimately contains 'age'."""
    for p in P.ALL:
        words = set(re.findall(r"[a-z]+", f"{p.key} {p.label} {p.family}".lower()))
        for bad in P.BLOCKED:
            bad_words = set(bad.split("_"))
            assert not bad_words.issubset(words), \
                f"{p.key} touches protected attribute '{bad}'"


def test_computable_things_are_computed_in_code():
    """Dates, counts and ratios must never be delegated to a model."""
    must_be_code = {
        "total_years_experience", "relevant_years_experience", "longest_tenure",
        "average_tenure", "employment_continuity", "claim_evidence_ratio",
        "unverified_claim_count", "skill_claim_verifiability",
        "min_total_experience", "min_relevant_experience",
    }
    for k in must_be_code:
        assert P.BY_KEY[k].how is P.How.CODE, f"{k} must be computed in code"


def test_weights_normalise_to_one():
    w = P.normalised_weights()
    assert abs(sum(w.values()) - 1.0) < 1e-9
    assert len(w) == len(P.SCORED)


def test_family_coverage():
    assert set(P.FAMILIES) == {"eligibility", "experience", "skills", "scope",
                               "domain", "trajectory", "integrity"}
