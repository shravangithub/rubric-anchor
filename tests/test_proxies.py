"""Proxy redaction, proxy swap variants, polish invariance, adverse explanation (Oct 2026)."""
from datetime import date

from rubric import NullExtractor, score_candidate
from rubric.redact import redact
from rubric.counterfactual import swap_test, PROXY_VARIANTS
from rubric.polish import polish_test, simple_polisher, fact_leak
from rubric.notice import adverse_explanation

CV = """Priya Example
Work authorization: Authorized to work in India.
Experience
- Senior Engineer | Quill SaaS | 2022-01 to present
  Built the billing engine. Owned the api contract and versioning.

Skills
Languages: Python, Go, SQL

Languages spoken: Hindi, Telugu, English (fluent)

Hobbies & Interests
- Carnatic music, temple volunteering, cricket
- Cooking

Volunteering: Teach for India, weekends.

Education
B.Tech CS, 2016
"""
JOB = {"job_family_titles": ["engineer"], "min_total_years": 0, "min_relevant_years": 0}


def test_proxy_sections_never_reach_the_model():
    t, rep = redact(CV)
    assert "Hindi" not in t and "Carnatic" not in t and "Teach for India" not in t and "Cooking" not in t
    assert "[LANGUAGES SECTION REDACTED]" in t and "[INTERESTS SECTION REDACTED]" in t
    assert "[VOLUNTEERING SECTION REDACTED]" in t
    assert rep.counts["proxy_languages"] == 1 and rep.counts["proxy_interests"] == 1
    assert rep.counts["proxy_volunteering"] == 1


def test_programming_languages_are_kept():
    t, _ = redact(CV)
    assert "Languages: Python, Go, SQL" in t


def test_mixed_language_line_is_redacted():
    t, _ = redact("Languages: Python, Hindi, English\n")
    assert "Hindi" not in t


def test_proxy_redaction_can_be_measured_off():
    t, rep = redact(CV, proxies=False)
    assert "Hindi" in t and not any(k.startswith("proxy_") for k in rep.counts)
    r = score_candidate("c", CV, JOB, NullExtractor(), today=date(2026, 10, 31), role="backend")
    assert r.provenance["proxy_redaction"] is True
    r2 = score_candidate("c", CV, JOB, NullExtractor(), today=date(2026, 10, 31), role="backend",
                         redact_proxies=False)
    assert r2.provenance["proxy_redaction"] is False


def test_proxy_variants_do_not_move_the_offline_score():
    rep = swap_test("c", CV, JOB, NullExtractor(), PROXY_VARIANTS, tolerance=0.0,
                    today=date(2026, 10, 31), role="backend")
    assert rep.passed, rep.as_dict()
    assert {"lang_a", "hobby_b", "volunteer_a", "career_break"} <= {r.variant for r in rep.results}


def test_cue_matching_starts_at_a_word():
    # "rest" must not fire on "interests": the marker text is not evidence
    r = score_candidate("c", "Engineer | X | 2020-01 to present\nInterests: chess\n", JOB,
                        NullExtractor(), today=date(2026, 10, 31), role="backend")
    assert r.scores.get("be_api_contract_discipline", 0.0) == 0.0


def test_polish_without_new_facts_passes_and_a_leak_fails():
    rep = polish_test("c", CV, JOB, NullExtractor(), simple_polisher, tolerance=2.0,
                      today=date(2026, 10, 31), role="backend")
    assert rep.passed and not rep.fact_leak
    assert fact_leak("Led a team.", "Led a team of 12 for 3 years.") == ["12", "3"]
    cheat = polish_test("c", CV, JOB, NullExtractor(), lambda t: t + "\nCut latency 40%.\n",
                        tolerance=100.0, today=date(2026, 10, 31), role="backend")
    assert not cheat.passed and cheat.fact_leak == ["40%"]


def test_adverse_explanation_names_a_person_and_no_scores():
    r = score_candidate("c", CV, {"job_family_titles": ["engineer"], "min_total_years": 10,
                                  "min_relevant_years": 0}, NullExtractor(),
                        today=date(2026, 10, 31), role="backend")
    txt = adverse_explanation(r, company="Acme", contact="jobs@acme.example", decided_by="R. Rao")
    assert "R. Rao, a person" in txt and "minimum years of experience" in txt
    assert "30 days" in txt and "%" not in txt and "score" not in txt.lower()
