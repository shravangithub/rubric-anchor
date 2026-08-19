import pytest
from datetime import date
from rubric import score_candidate, NullExtractor, parameters as P
from rubric.guards import ProtectedAttributeError, ComparativeScoringError
from rubric.scoring import months_between

CV = """Work authorization: Authorized to work in India.
Notice period: 30 days.
- Staff Engineer | Nimbus Payments | 2021-03 to present
  Owned the ledger service. Led sharding of the settlement store, cut p99 latency 40%.
  On-call lead for the PCI-scoped payments path. Mentored 4 engineers.
- Backend Engineer | Corvid Labs | 2017-06 to 2021-02
  Built distributed job scheduler. Improved throughput 3x.
"""
JOB = {"job_family_titles": ["engineer"], "min_total_years": 5,
       "min_relevant_years": 3, "max_notice_days": 60}
TODAY = date(2026, 8, 19)


def score(cv=CV, job=JOB, cid="C-1"):
    return score_candidate(cid, cv, job, NullExtractor(), today=TODAY)


def test_deterministic():
    """Same input, same output. This is the whole product."""
    a, b = score(), score()
    assert a.composite == b.composite
    assert a.scores == b.scores


def test_score_is_independent_of_other_candidates():
    """A candidate's score must not move when the pile changes.

    This is the property that comparative ranking cannot offer, and the reason
    scores from this system can be stored and compared months apart.
    """
    alone = score().composite
    for _ in range(5):
        score("Unrelated other candidate | Somewhere | 2019-01 to 2020-01")
    assert score().composite == alone


def test_all_scored_parameters_get_a_value():
    r = score()
    assert set(r.scores) == {p.key for p in P.SCORED}


def test_composite_is_bounded():
    r = score()
    assert 0.0 <= r.composite <= 100.0


def test_unevidenced_claims_score_zero_not_average():
    r = score()
    for c in r.dropped:
        if c.parameter in r.scores:
            assert r.scores[c.parameter] == 0.0


def test_years_are_computed_not_guessed():
    assert months_between("2021-03", "present", TODAY) == 65
    assert months_between("2017-06", "2021-02", TODAY) == 44


def test_failing_a_non_bona_fide_gate_routes_to_a_human():
    """The machine narrows the pool. A person makes the adverse decision."""
    r = score(job={**JOB, "min_total_years": 40})
    assert r.gates["min_total_experience"] is False
    assert r.needs_human is True
    assert "person must decide" in " ".join(r.reasons)


def test_missing_work_authorisation_is_the_one_auto_reject():
    r = score(cv=CV.replace("Authorized to work in India.",
                            "Not authorized; requires sponsorship."))
    assert r.gates["work_authorization"] is False
    assert r.needs_human is False          # bona fide -> may close without a human


def test_protected_attribute_in_job_spec_raises():
    with pytest.raises(ProtectedAttributeError):
        score(job={**JOB, "preferred_gender": "male"})


def test_scorer_refuses_a_pile():
    with pytest.raises(ComparativeScoringError):
        score_candidate("X", ["cv one", "cv two"], JOB, NullExtractor())
