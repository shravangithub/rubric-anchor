"""Counterfactual swap test -- did redaction actually work?

Take one CV, change only something that must not matter (a name, a pronoun,
a gendered club, a career-break line), score both versions, and compare.
If the score moves, something other than the evidence is driving it.

Redaction removes the obvious markers. Proxies survive it. This test is how
you find the proxies -- run it against your live model before you trust it,
and again whenever the model or prompt version changes.

    from rubric.counterfactual import swap_test, replace, PRONOUN_SWAP
    rep = swap_test("C-1", cv, job, extractor, {
        "pronouns": PRONOUN_SWAP,
        "club": replace("Captain, chess club", "Captain, women's chess club"),
    })
    rep.passed, rep.worst
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from typing import Callable

from .scoring import score_candidate

Transform = Callable[[str], str]


def replace(old: str, new: str) -> Transform:
    def f(t: str) -> str:
        return t.replace(old, new)
    f.__name__ = f"replace({old!r}->{new!r})"
    return f


_PAIRS = {"he": "she", "she": "he", "him": "her", "his": "her", "her": "his",
          "himself": "herself", "herself": "himself", "mr": "ms", "ms": "mr"}


def PRONOUN_SWAP(t: str) -> str:
    def f(m):
        w = m.group(0)
        s = _PAIRS[w.lower()]
        return s.capitalize() if w[0].isupper() else s
    return re.sub(r"(?i)\b(" + "|".join(_PAIRS) + r")\b", f, t)


@dataclass
class SwapResult:
    variant: str
    base: float
    swapped: float
    parameter_deltas: dict[str, float] = field(default_factory=dict)

    @property
    def delta(self) -> float:
        return round(self.swapped - self.base, 2)


@dataclass
class SwapReport:
    candidate_id: str
    tolerance: float
    results: list[SwapResult] = field(default_factory=list)

    @property
    def worst(self) -> float:
        return max((abs(r.delta) for r in self.results), default=0.0)

    @property
    def passed(self) -> bool:
        return self.worst <= self.tolerance

    def as_dict(self) -> dict:
        return {"candidate_id": self.candidate_id, "tolerance": self.tolerance,
                "passed": self.passed, "worst_delta": self.worst,
                "variants": [{"variant": r.variant, "base": r.base,
                              "swapped": r.swapped, "delta": r.delta,
                              "moved_parameters": {k: v for k, v in r.parameter_deltas.items() if v}}
                             for r in self.results]}


def swap_test(candidate_id: str, resume: str, job: dict, extractor,
              variants: dict[str, Transform], tolerance: float = 0.0,
              **kw) -> SwapReport:
    base = score_candidate(candidate_id, resume, job, extractor, **kw)
    rep = SwapReport(candidate_id, tolerance)
    for name, fn in variants.items():
        alt = score_candidate(candidate_id, fn(resume), job, extractor, **kw)
        deltas = {k: round(alt.scores.get(k, 0.0) - base.scores.get(k, 0.0), 2)
                  for k in set(base.scores) | set(alt.scores)}
        rep.results.append(SwapResult(name, base.composite, alt.composite, deltas))
    return rep
