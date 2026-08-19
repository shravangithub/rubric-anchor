import pytest
from datetime import date
from collections import defaultdict
from rubric import parameters as P, packs, roles
from rubric import levels as LV
from rubric.scoring import score_candidate
from rubric.extractors import NullExtractor

CV = open("examples/resumes/C-1041.txt").read()
JOB = {"job_family_titles": ["engineer"], "min_total_years": 5,
       "min_relevant_years": 3, "max_notice_days": 60}
TODAY = date(2026, 8, 19)


def share(level, industry="fintech", role="backend"):
    """Share of the composite by family, at one level."""
    active = [p for p in packs.build_rubric(industry, role)
              if p.kind is P.Kind.SCORED]
    rf = {p.family for p in roles.ROLE_PACKS[role]}
    inf = {p.family for p in packs.INDUSTRY_PACKS[industry]}
    w = {p.key: p.weight * LV.multiplier(level, p.family, rf, inf) for p in active}
    tot = sum(w.values())
    g = defaultdict(float)
    for p in active:
        fam = "role" if p.family in rf else ("industry" if p.family in inf else p.family)
        g[fam] += w[p.key] / tot
    return g


def test_fourteen_role_packs_in_three_groups():
    assert len(roles.ROLE_PACKS) == 14
    grouped = [r for ks in roles.ROLE_GROUPS.values() for r in ks]
    assert sorted(grouped) == sorted(roles.ROLE_PACKS)


def test_nine_levels_in_order():
    assert len(LV.LEVELS) == 9
    assert LV.ORDER == ["entry", "junior", "mid", "senior", "lead",
                        "manager", "director", "vp", "c_level"]


def test_levels_add_no_parameters():
    """A level reweights. It must never change WHAT is scored, or scores at
    different levels would not be comparable."""
    base = {p.key for p in packs.build_rubric("fintech", "backend")}
    for lv in LV.ORDER:
        r = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY,
                            industry="fintech", role="backend", level=lv)
        assert set(r.scores) | set(r.not_applicable) <= base
        assert len(r.scores) == len(
            score_candidate("C", CV, JOB, NullExtractor(), today=TODAY,
                            industry="fintech", role="backend",
                            level="entry").scores)


def test_education_weight_falls_monotonically_with_level():
    vals = [share(lv)["education"] for lv in LV.ORDER]
    assert vals[0] > vals[-1] * 4, "education should dominate at entry"
    # allow the manager step to tick up (a manager is not less credentialled
    # than a staff IC) but the overall trend must be downward
    assert vals[0] > vals[2] > vals[4] >= vals[-1]


def test_scope_weight_rises_monotonically_with_level():
    vals = [share(lv)["scope"] for lv in LV.ORDER]
    assert all(b >= a - 1e-9 for a, b in zip(vals, vals[1:])), \
        "scope must never fall as level rises"
    assert vals[-1] > vals[0] * 4


def test_role_pack_matters_more_at_senior_levels():
    assert share("c_level")["role"] > share("entry")["role"] * 2


def test_proof_of_work_is_an_entry_level_signal():
    """Strongest where there is no track record; near-irrelevant at C-level."""
    assert share("entry")["proof_of_work"] > 0.15
    assert share("c_level")["proof_of_work"] < 0.05


def test_unknown_role_and_level_rejected_loudly():
    with pytest.raises(ValueError, match="unknown role"):
        packs.build_rubric("fintech", "astronaut")
    with pytest.raises(ValueError, match="unknown level"):
        LV.get("emperor")


def test_leadership_role_at_junior_level_warns_not_raises():
    """A questionable pairing is the recruiter's call, not the tool's."""
    r = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY,
                        role="eng_leadership", level="junior")
    assert any("configuration" in x for x in r.reasons)


def test_ic_pack_at_c_level_warns():
    r = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY,
                        role="backend", level="c_level")
    assert any("leadership hire" in x for x in r.reasons)


def test_every_role_level_combination_is_bounded_and_deterministic():
    for role in roles.ROLE_PACKS:
        for lv in ("entry", "mid", "c_level"):
            a = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY,
                                industry="saas", role=role, level=lv)
            b = score_candidate("C", CV, JOB, NullExtractor(), today=TODAY,
                                industry="saas", role=role, level=lv)
            assert a.composite == b.composite, f"{role}/{lv} not deterministic"
            assert 0.0 <= a.composite <= 100.0, f"{role}/{lv} out of range"


def test_no_key_collisions_across_all_three_dimensions():
    for ind in packs.INDUSTRY_PACKS:
        for role in roles.ROLE_PACKS:
            keys = [p.key for p in packs.build_rubric(ind, role)]
            assert len(keys) == len(set(keys)), f"{ind}+{role} collides"
