import pytest
from rubric.audit import analyse, report, orderings

R1 = ["a", "b", "c", "d", "e", "f", "g", "h"]
R2 = ["a", "b", "d", "c", "f", "e", "h", "g"]
R3 = ["a", "c", "b", "f", "d", "g", "e", "h"]


def test_settled_and_unsettled():
    res = analyse([R1, R2, R3], shortlist_size=4)
    assert set(res.settled_in) == {"a", "b", "c"}
    assert "e" in res.unsettled or "f" in res.unsettled
    assert res.settled_in and res.settled_out


def test_refuses_incomplete_runs():
    """A partial pile must never yield a reassuring result."""
    res = analyse([R1, R2[:5]], shortlist_size=4)
    assert res.incomplete
    assert "CANNOT REPORT" in report(res)


def test_needs_two_runs():
    with pytest.raises(ValueError):
        analyse([R1], shortlist_size=4)


def test_orderings_are_reproducible():
    assert orderings(R1, 3, seed=7) == orderings(R1, 3, seed=7)
    assert orderings(R1, 3, seed=7) != orderings(R1, 3, seed=8)


def test_stable_pile_reports_clean():
    res = analyse([R1, R1, R1], shortlist_size=4)
    assert res.unsettled == []
    assert "stable" in report(res)
