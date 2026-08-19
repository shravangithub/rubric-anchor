import random
import pytest
from rubric.kg import PeopleGraph, Validity, FairnessMonitor
from rubric.scoring import Result


def seeded_graph(n=200, seed=3):
    random.seed(seed)
    g = PeopleGraph(extractor_version="test-1")
    for i in range(n):
        cid = f"C{i:04d}"
        talent = random.gauss(.55, .18)
        sc = {"be_system_design_depth": max(0, min(100, talent*100+random.gauss(0, 12))),
              "qualification_level":    max(0, min(100, random.gauss(55, 20))),
              "market_experience":      max(0, min(100, random.gauss(50, 25)))}
        d = sc["be_system_design_depth"]*.6 + sc["qualification_level"]*.4
        g.ingest_result(Result(candidate_id=cid, scores=sc, composite=round(d, 2)),
                        "REQ", at="2024-01-01")
        hired = d > 57
        g.record_outcome(cid, "REQ", "hired" if hired else "rejected", at="2024-02-01")
        if hired:
            g.record_performance(cid, rating=max(1, min(5, talent*5+random.gauss(0, .5))),
                                 at="2025-02-01")
    return g


def test_ingest_writes_facts_with_provenance():
    g = PeopleGraph()
    g.ingest_result(Result(candidate_id="C1", scores={"a": 70.0}, composite=70.0),
                    "R1", at="2024-01-01")
    row = g.conn.execute(
        "SELECT extractor, valid_from, recorded_at FROM fact "
        "WHERE predicate='SCORED_a'").fetchone()
    assert all(row), "every fact must carry extractor version and both timestamps"


def test_bitemporal_separates_valid_from_recorded():
    """A fact true in March but learned in June must not appear in an
    as-of-April answer."""
    g = PeopleGraph()
    g.ingest_result(Result(candidate_id="C1", scores={"a": 70.0}, composite=70.0),
                    "R1", at="2024-03-01", recorded_at="2024-06-01")
    assert g.as_of("COMPOSITE", valid_on="2024-04-01", known_on="2024-04-01") == []
    assert g.as_of("COMPOSITE", valid_on="2024-04-01", known_on="2024-07-01")


def test_merge_is_logged_and_moves_facts():
    g = PeopleGraph()
    g.ingest_result(Result(candidate_id="A1", scores={"a": 10.0}, composite=10.0),
                    "R1", at="2024-01-01")
    g.ingest_result(Result(candidate_id="A2", scores={"a": 20.0}, composite=20.0),
                    "R2", at="2024-01-01")
    g.merge("A1", "A2", basis="verified email", at="2024-03-01")
    assert g.person("A2") == "A1"
    assert g.stats()["people"] == 1
    assert g.conn.execute("SELECT basis FROM alias WHERE alias_id='A2'").fetchone()[0]


def test_validity_finds_the_predictive_parameter():
    rep = {v.parameter: v for v in Validity(seeded_graph()).report()}
    assert rep["be_system_design_depth"].verdict == "strong"
    assert rep["be_system_design_depth"].r_performance > 0.3


def test_selection_artefact_is_flagged_not_believed():
    """qualification_level is generated INDEPENDENTLY of talent here. Because
    the process rewards it, restricting to hires manufactures a negative
    correlation. The module must flag that rather than report it as signal."""
    rep = {v.parameter: v for v in Validity(seeded_graph()).report()}
    q = rep["qualification_level"]
    assert q.r_performance is not None and q.r_performance < 0
    assert "SUSPECT" in q.verdict, "a spurious negative must not read as evidence"


def test_drop_one_measures_outcome_change_not_rank_jitter():
    """An earlier version reported ~90% movement for every parameter, which is
    true and useless. This must measure shortlist churn."""
    d = Validity(seeded_graph()).drop_one("market_experience")
    assert set(d) >= {"swapped", "shortlist", "pct_of_shortlist"}
    assert 0 <= d["pct_of_shortlist"] <= 100
    assert d["swapped"] <= d["shortlist"]


def test_explain_attributes_the_score():
    g = PeopleGraph()
    g.ingest_result(Result(candidate_id="C1", composite=60.0,
                           scores={"be_system_design_depth": 80.0,
                                   "market_experience": 20.0}),
                    "R1", at="2024-01-01")
    ex = g.explain("C1", "R1")
    assert ex[0]["parameter"] == "be_system_design_depth"
    assert sum(c["share_pct"] for c in ex) == pytest.approx(100, abs=0.5)


def test_fairness_suppresses_small_groups_and_flags_disparity():
    out = FairnessMonitor.selection_rates({"a": (40, 100), "b": (20, 100), "c": (2, 5)})
    assert "c" in out["suppressed"]
    assert "b" in out["four_fifths_flagged"]
    assert "not a legal finding" in out["note"]


def test_fairness_never_touches_a_protected_attribute():
    """The monitor takes aggregate counts. It has no path to a person."""
    import inspect
    src = inspect.getsource(FairnessMonitor)
    assert "person_id" not in src and "SELECT" not in src
