"""Regression tests against the sample CVs.

These exist because a cross-role test initially returned 0/9: every CV
"fitted" business_development best. Two causes, both now fixed and locked
down here.
"""
import glob, os
import pytest
from datetime import date
from rubric.scoring import score_candidate
from rubric.extractors import NullExtractor
from rubric.roles import ROLE_PACKS

TODAY = date(2026, 8, 19)
JOB = {"job_family_titles": ["engineer", "sre", "qa", "manager", "director",
                             "executive", "product", "account", "sdr"],
       "min_total_years": 0, "min_relevant_years": 0, "max_notice_days": 200}
EXPECT = {"E01": "backend", "S02": "backend", "S03": "sre",
          "S04": "product_manager", "S05": "sdr", "S06": "sales",
          "S07": "eng_leadership", "S08": "exec_leadership", "S09": "qa"}
LEVEL = {"E01": "entry", "S02": "senior", "S03": "senior", "S04": "senior",
         "S05": "entry", "S06": "mid", "S07": "director", "S08": "c_level",
         "S09": "mid", "S10": "mid"}


def cvs():
    return sorted(glob.glob("examples/sample_cvs/*.txt"))


def fit_profile(cv, level):
    out = {}
    for role in ROLE_PACKS:
        r = score_candidate("X", cv, JOB, NullExtractor(), today=TODAY,
                            industry="saas", role=role, level=level)
        out[role] = r.role_fit or 0.0
    return out


@pytest.mark.parametrize("path", cvs())
def test_each_cv_fits_its_intended_role_best(path):
    key = os.path.basename(path)[:4].split("_")[0]
    if key not in EXPECT:
        pytest.skip("control CV")
    fit = fit_profile(open(path).read(), LEVEL[key])
    best = max(fit, key=fit.get)
    assert best == EXPECT[key], f"{key}: best fit was {best} ({fit[best]:.1f})"


def test_control_cv_fits_nothing():
    """An office administrator CV must not 'fit' an engineering role."""
    fit = fit_profile(open("examples/sample_cvs/S10_weak_control.txt").read(), "mid")
    assert max(fit.values()) < 10.0


def test_every_role_parameter_has_an_extractor_cue():
    """The original 0/9 failure was partly this: the mock scored every role
    parameter zero, so the ranking measured pack size instead of fit."""
    n = NullExtractor()
    missing = [p.key for pack in ROLE_PACKS.values() for p in pack
               if p.key not in n.ROLE_CUES and p.key not in n.CUES]
    assert not missing, f"no cue for: {missing}"


def test_composite_is_not_comparable_across_packs():
    """Documented limitation, asserted so it stays documented.

    A larger pack has more parameters in the denominator, so composites shift
    with pack size. Compare candidates WITHIN one requisition; use role_fit to
    compare across packs.
    """
    cv = open("examples/sample_cvs/S02_senior_backend_fintech.txt").read()
    small = score_candidate("X", cv, JOB, NullExtractor(), today=TODAY,
                            role="business_development", level="senior")
    large = score_candidate("X", cv, JOB, NullExtractor(), today=TODAY,
                            role="eng_leadership", level="senior")
    assert small.composite != large.composite
    # but role_fit correctly says this is a backend CV, not either of those
    be = score_candidate("X", cv, JOB, NullExtractor(), today=TODAY,
                         role="backend", level="senior")
    assert be.role_fit > small.role_fit and be.role_fit > large.role_fit


def test_within_requisition_ranking_is_sensible():
    """The production case: one role, many candidates, ranked."""
    scored = []
    for path in cvs():
        key = os.path.basename(path)[:4].split("_")[0]
        r = score_candidate(os.path.basename(path)[:-4], open(path).read(), JOB,
                            NullExtractor(), today=TODAY, industry="fintech",
                            role="backend", level="senior")
        scored.append((r.composite, r.candidate_id))
    scored.sort(reverse=True)
    top = scored[0][1]
    bottom = scored[-1][1]
    assert "backend" in top or "sre" in top, f"unexpected top: {top}"
    assert "weak_control" in bottom, f"unexpected bottom: {bottom}"
