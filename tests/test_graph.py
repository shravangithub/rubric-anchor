from rubric.graph import Graph


def test_triples_carry_provenance():
    g = Graph()
    g.node("c1", "Candidate"); g.node("p1", "Parameter", key="core_skill_depth")
    g.edge("c1", "SCORED_core_skill_depth", "p1", score=72,
           evidence="Led sharding of the settlement store",
           source="cv.txt", at="2026-08-19")
    g.commit()
    e = g.out("c1")[0]
    assert e.evidence and e.source and e.at
    assert e.props["score"] == 72


def test_causal_edges_are_unconfirmed_by_default():
    """A model may propose a cause. It may not assert one."""
    g = Graph()
    g.node("o1", "Outcome"); g.node("o2", "Outcome")
    g.edge("o1", "CAUSED_BY", "o2", evidence="exit interview")
    assert g.out("o1")[0].props["human_confirmed"] is False


def test_parameter_separation_suppresses_small_groups():
    g = Graph()
    for i in range(3):                     # below k=5
        cid = f"c{i}"
        g.node(cid, "Candidate")
        g.edge(cid, "SCORED_core_skill_depth", "p", score=80, at=str(i))
        g.edge(cid, "RESULTED_IN", "hired", at=str(i))
    g.commit()
    rows = g.parameter_separation(min_group=5)
    assert rows and rows[0]["hired"] is None, "small cells must be suppressed"
