"""Run-to-run stability -- the noise that isolation does not remove.

Scoring each CV alone removes ORDER and BATCH effects. It does not remove the
model's own sampling noise: the same CV, scored twice by a live model, can
come back a few points apart. The shuffle experiment showed what that does at
a cut-off -- a candidate placed 4th in one run and 11th in another.

So: score each candidate several times (still alone, every time), report a
range rather than a point, and cut the shortlist by BAND, not by rank.

    clear_in     the whole range is at or above the cut-off
    borderline   the range straddles the cut-off -- a person decides
    clear_out    the whole range is below the cut-off

With the deterministic `NullExtractor` the range is a single point. That is
expected; this module earns its keep with a live model.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from statistics import median

from .scoring import score_candidate, Result


@dataclass
class Stability:
    candidate_id: str
    composites: list[float]
    parameter_spread: dict[str, float] = field(default_factory=dict)
    tolerance: float = 2.0
    results: list[Result] = field(default_factory=list, repr=False)

    @property
    def low(self) -> float:
        return min(self.composites)

    @property
    def high(self) -> float:
        return max(self.composites)

    @property
    def median(self) -> float:
        return round(median(self.composites), 2)

    @property
    def spread(self) -> float:
        return round(self.high - self.low, 2)

    @property
    def stable(self) -> bool:
        return self.spread <= self.tolerance

    def band(self, cutoff: float) -> str:
        if self.low >= cutoff:
            return "clear_in"
        if self.high < cutoff:
            return "clear_out"
        return "borderline"

    def as_dict(self) -> dict:
        return {"candidate_id": self.candidate_id, "runs": len(self.composites),
                "composites": self.composites, "low": self.low, "median": self.median,
                "high": self.high, "spread": self.spread, "stable": self.stable,
                "tolerance": self.tolerance,
                "unstable_parameters": {k: v for k, v in self.parameter_spread.items()
                                        if v > self.tolerance}}


def score_repeated(candidate_id: str, resume: str, job: dict, extractor,
                   runs: int = 3, tolerance: float = 2.0, **kw) -> Stability:
    """Score ONE candidate `runs` times. Each run is a fresh, isolated score."""
    if runs < 2:
        raise ValueError("stability needs at least 2 runs")
    results = [score_candidate(candidate_id, resume, job, extractor, **kw)
               for _ in range(runs)]
    keys = set().union(*(r.scores for r in results))
    spread = {}
    for k in sorted(keys):
        vals = [r.scores[k] for r in results if k in r.scores]
        spread[k] = round(max(vals) - min(vals), 2) if vals else 0.0
    return Stability(candidate_id, [r.composite for r in results], spread,
                     tolerance, results)


def bands(stabilities: list[Stability], cutoff: float) -> dict[str, list[str]]:
    """Group candidates by band. Within a band, order by median (in code)."""
    out: dict[str, list[str]] = {"clear_in": [], "borderline": [], "clear_out": []}
    for s in sorted(stabilities, key=lambda s: -s.median):
        out[s.band(cutoff)].append(s.candidate_id)
    return out
