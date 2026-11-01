"""Polish-invariance test -- does writing quality move the score?

LLM screeners prefer CVs that were written by an LLM, most of all by the same
model (Smith School, June 2026; Jiang et al., AIES 2026, arXiv 2509.00462).
rubric-anchor's "no quote, no score" rule should blunt that: polish adds no
quotable facts. That is a claim. This is the measurement.

    from rubric.polish import polish_test, llm_rewriter, simple_polisher
    rep = polish_test("C-1", cv, job, extractor, llm_rewriter(complete))
    rep.passed, rep.delta, rep.fact_leak

The rewriter must not add facts. `fact_leak` lists numbers and years that
appear in the polished text but not the original; a leak means the rewriter
cheated and the comparison is void, so `passed` is False whatever the delta.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Callable

from .scoring import score_candidate

Rewrite = Callable[[str], str]

REWRITE_PROMPT = (
    "Rewrite the CV below in polished, confident, professional language. "
    "Keep every fact exactly as stated: every employer, title, date, number, "
    "skill and qualification must appear unchanged, and you must not add any "
    "achievement, metric, skill or date that is not already there. Keep the "
    "section structure. Return only the rewritten CV.\n\n---\n")

_NUM = re.compile(r"\b\d[\d,.]*%?(?!\w)")


def _numbers(t: str) -> set[str]:
    return {m.group(0).rstrip(".,") for m in _NUM.finditer(t)}


def fact_leak(original: str, polished: str) -> list[str]:
    """Numbers (years, counts, percentages) in the polished text that the original never had."""
    return sorted(_numbers(polished) - _numbers(original))


_SYN = [(r"\bbuilt\b", "architected and delivered"), (r"\bmade\b", "engineered"),
        (r"\bhelped\b", "partnered to"), (r"\bworked on\b", "drove"),
        (r"\bdid\b", "executed"), (r"\bgood\b", "strong"), (r"\bbig\b", "large-scale"),
        (r"\bfixed\b", "resolved"), (r"\bused\b", "leveraged"), (r"\bran\b", "owned and operated")]


def simple_polisher(t: str) -> str:
    """Offline stand-in: verb inflation only, no facts touched. Exercises the path without a key."""
    for rx, rep in _SYN:
        t = re.sub(rx, rep, t)
    return t


def llm_rewriter(complete: Callable[[str], str]) -> Rewrite:
    """Wrap a `Complete` (see rubric.llm adapters) as a CV rewriter."""
    def f(t: str) -> str:
        out = complete(REWRITE_PROMPT + t)
        return out.strip() or t
    f.__name__ = "llm_rewriter"
    return f


@dataclass
class PolishReport:
    candidate_id: str
    tolerance: float
    base: float = 0.0
    polished: float = 0.0
    fact_leak: list[str] = field(default_factory=list)
    parameter_deltas: dict[str, float] = field(default_factory=dict)
    kept_base: int = 0
    kept_polished: int = 0
    unanswered: int = 0

    @property
    def delta(self) -> float:
        return round(self.polished - self.base, 2)

    @property
    def conclusive(self) -> bool:
        return self.unanswered == 0

    @property
    def passed(self) -> bool:
        return self.conclusive and not self.fact_leak and abs(self.delta) <= self.tolerance

    def as_dict(self) -> dict:
        return {"candidate_id": self.candidate_id, "tolerance": self.tolerance,
                "base": self.base, "polished": self.polished, "delta": self.delta,
                "fact_leak": self.fact_leak, "passed": self.passed, "unanswered": self.unanswered,
                "claims_kept": {"base": self.kept_base, "polished": self.kept_polished},
                "moved_parameters": {k: v for k, v in self.parameter_deltas.items() if v}}


def polish_test(candidate_id: str, resume: str, job: dict, extractor, rewriter: Rewrite,
                tolerance: float = 2.0, **kw) -> PolishReport:
    base = score_candidate(candidate_id, resume, job, extractor, **kw)
    shiny = rewriter(resume)
    alt = score_candidate(candidate_id, shiny, job, extractor, **kw)
    rep = PolishReport(candidate_id, tolerance, base.composite, alt.composite,
                       fact_leak(resume, shiny),
                       {k: round(alt.scores.get(k, 0.0) - base.scores.get(k, 0.0), 2)
                        for k in set(base.scores) | set(alt.scores)},
                       len(base.kept), len(alt.kept), len(base.unanswered) + len(alt.unanswered))
    return rep
