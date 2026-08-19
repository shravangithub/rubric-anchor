"""The shuffle audit.

Use this on a system you CANNOT change -- an existing vendor -- to measure
whether its shortlist is repeatable. It is a diagnostic, not part of scoring.

Note the asymmetry: if you rank comparatively you need this test. If you score
absolutely (see scoring.py) there is nothing to shuffle, because no candidate's
result depends on any other candidate.
"""
from __future__ import annotations
import random
from dataclasses import dataclass, field


@dataclass
class AuditResult:
    shortlist_size: int
    runs: int
    settled_in: list[str] = field(default_factory=list)
    unsettled: list[str] = field(default_factory=list)
    settled_out: list[str] = field(default_factory=list)
    positions: dict[str, list[int]] = field(default_factory=dict)
    incomplete: list[str] = field(default_factory=list)

    @property
    def stability(self) -> float:
        n = len(self.settled_in) + len(self.unsettled)
        return 1.0 if n == 0 else len(self.settled_in) / self.shortlist_size

    def as_dict(self) -> dict:
        return {"shortlist_size": self.shortlist_size, "runs": self.runs,
                "unsettled_count": len(self.unsettled),
                "stability": round(self.stability, 3),
                "settled_in": self.settled_in, "unsettled": self.unsettled,
                "settled_out": self.settled_out, "positions": self.positions,
                "incomplete": self.incomplete}


def orderings(ids: list[str], runs: int = 3, seed: int = 0) -> list[list[str]]:
    """Deterministic shuffles, so an audit can be reproduced exactly."""
    out = []
    for i in range(runs):
        rng = random.Random(f"{seed}:{i}")
        x = list(ids)
        rng.shuffle(x)
        out.append(x)
    return out


def analyse(rankings: list[list[str]], shortlist_size: int) -> AuditResult:
    """`rankings` are ranked candidate ids, best first, one list per run."""
    if len(rankings) < 2:
        raise ValueError("need at least 2 runs to detect movement")
    pos: dict[str, list[int]] = {}
    for run in rankings:
        for i, cid in enumerate(run):
            pos.setdefault(cid, []).append(i + 1)

    res = AuditResult(shortlist_size=shortlist_size, runs=len(rankings))
    for cid, ps in pos.items():
        if len(ps) != len(rankings):
            # Refuse to judge anyone who is not in every run. A partial pile
            # would otherwise produce a falsely reassuring result.
            res.incomplete.append(cid)
            continue
        res.positions[cid] = ps
        if max(ps) <= shortlist_size:
            res.settled_in.append(cid)
        elif min(ps) > shortlist_size:
            res.settled_out.append(cid)
        else:
            res.unsettled.append(cid)
    res.unsettled.sort(key=lambda c: min(res.positions[c]))
    return res


def report(res: AuditResult) -> str:
    if res.incomplete:
        return ("CANNOT REPORT: these candidates are missing from at least one "
                f"run: {', '.join(res.incomplete)}. Every run must cover the "
                "same pile, or the result is meaningless.")
    lines = [
        f"Runs: {res.runs}   Shortlist: {res.shortlist_size}",
        f"Settled in  : {len(res.settled_in)}",
        f"UNSETTLED   : {len(res.unsettled)}",
        f"Settled out : {len(res.settled_out)}",
        "",
    ]
    if res.unsettled:
        lines.append("These candidates changed sides between runs:")
        for c in res.unsettled:
            lines.append(f"  {c:<16} placed {res.positions[c]}")
        lines.append("")
        lines.append("Their CVs did not change. Only the order did.")
    else:
        lines.append("Nothing crossed the line. This pile is stable.")
    return "\n".join(lines)
