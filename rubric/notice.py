"""Candidate-facing text: notice, review route, and the questions to ask.

Automated-decision rules increasingly require that candidates are told an
automated tool assisted, and that they can ask a person to review the result
(see the Legal note in the README). This module writes that text from a
`Result` without ever disclosing scores, parameters or internal notes.

It is a template, not legal advice. Have whoever owns employment law where
you hire approve the wording before it is sent.
"""
from __future__ import annotations

from .scoring import Result

_ASK = {
    "work_authorization": "Are you authorised to work in the hiring location, "
                          "or would you need sponsorship?",
    "notice_period_days": "What is your notice period?",
}


def questions_for(result: Result) -> list[str]:
    """Plain questions for facts the CV did not state. Unknown is not a fail."""
    return [_ASK.get(k, f"Could you tell us about: {k.replace('_', ' ')}?")
            for k in result.unknowns]


def candidate_notice(result: Result, *, company: str, contact: str,
                     review_days: int = 14) -> str:
    lines = [
        f"Thank you for applying to {company}.",
        "",
        "An automated tool helped us read your application. It checks what your "
        "CV says against the requirements of the role, and every point it uses is "
        "tied to a line of your CV. It does not consider your name, age, gender, "
        "or any other personal characteristic, and it does not compare you with "
        "other applicants.",
        "",
        "A person reviews the result before any decision about your application "
        "is made.",
    ]
    qs = questions_for(result)
    if qs:
        lines += ["", "Your CV did not mention the following. Replying will help "
                      "us assess your application fairly:"]
        lines += [f"  - {q}" for q in qs]
    lines += [
        "",
        f"If you think something has been read incorrectly, or you would like a "
        f"person to review your application again, write to {contact} within "
        f"{review_days} days. You can also send corrected or additional "
        f"information.",
    ]
    return "\n".join(lines)


def adverse_explanation(result: Result, *, company: str, contact: str,
                        decided_by: str, gates_failed: list[str] | None = None,
                        review_days: int = 30) -> str:
    """Plain-language explanation of an adverse outcome, for the candidate.

    Written for the rules that now ask for one (Colorado's ADMT Act from
    1 January 2027: an explanation within 30 days and a route to human
    review; the EU AI Act's transparency duties; the CCPA ADMT rules). It
    names the person who decided, which requirements were not met, and
    how to ask for review. It never discloses scores, weights or other
    applicants. Keep the sent copy with the audit record; some rules ask
    for three years.
    """
    failed = gates_failed if gates_failed is not None else [
        g for g, ok in result.gates.items() if not ok]
    words = {
        "work_authorization": "authorisation to work in the hiring location",
        "location_eligible": "the role's location or onsite requirement",
        "notice_period_acceptable": "the notice period the role can accommodate",
        "min_total_experience": "the minimum years of experience for the role",
        "min_relevant_experience": "the minimum years in this kind of role",
        "required_licence": "a licence the role legally requires",
        "education_minimum": "the minimum qualification for the role",
        "availability_date": "the start date the role needs",
    }
    lines = [
        f"Thank you for applying to {company}.",
        "",
        f"We are not taking your application further for this role. The decision "
        f"was made by {decided_by}, a person, after reviewing what your CV says "
        f"against the role's requirements. An automated tool helped prepare that "
        f"review; it did not make the decision.",
    ]
    if failed:
        lines += ["", "The requirement(s) your application did not show:"]
        lines += [f"  - {words.get(g, g.replace('_', ' '))}" for g in failed]
    else:
        lines += ["", "Your application met the role's stated requirements; other "
                      "applicants showed closer evidence for what the role needs."]
    lines += [
        "",
        f"If you believe something was read incorrectly, or you have information "
        f"that was not in your CV, write to {contact} within {review_days} days and "
        f"a person will review your application again and reply to you.",
    ]
    return "\n".join(lines)
