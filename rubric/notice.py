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
