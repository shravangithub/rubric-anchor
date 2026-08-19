from rubric.evidence import Claim, verify, anchored, evidence_ratio

SRC = "Led sharding of the settlement store, cut p99 latency 40%."


def test_real_span_is_anchored():
    assert anchored("Led sharding of the settlement store", SRC)


def test_fabricated_span_is_rejected():
    assert not anchored("Led the company-wide migration to Kubernetes", SRC)


def test_whitespace_and_case_do_not_matter():
    assert anchored("led   SHARDING of the settlement store", SRC)


def test_trivially_short_span_is_rejected():
    """Stops a model 'anchoring' a claim to a common word."""
    assert not anchored("the", SRC)
    assert not anchored("cut p99", SRC)


def test_verify_splits_and_explains():
    kept, dropped = verify(
        [Claim("a", 1, "Led sharding of the settlement store"),
         Claim("b", 2, "Managed a team of twelve engineers")], SRC)
    assert [c.parameter for c in kept] == ["a"]
    assert [c.parameter for c in dropped] == ["b"]
    assert dropped[0].reason and not dropped[0].verified


def test_evidence_ratio():
    assert evidence_ratio([], []) == 1.0
    assert evidence_ratio([Claim("a", 1, "x")], [Claim("b", 1, "y")]) == 0.5
