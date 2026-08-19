"""Evidence anchoring.

A model-produced claim is only admissible if the span it cites appears
verbatim in the source document. That check is a substring comparison and is
done here, in code -- never by a model.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict


@dataclass
class Claim:
    parameter: str
    value: object
    span: str                 # must appear verbatim in the source
    confidence: float = 1.0
    verified: bool = False
    reason: str = ""

    def as_dict(self) -> dict:
        return asdict(self)


_WS = re.compile(r"\s+")


def normalise(text: str) -> str:
    """Whitespace and case are not meaningful; everything else is."""
    return _WS.sub(" ", text or "").strip().lower()


def anchored(span: str, source: str, min_chars: int = 12) -> bool:
    """Is this span really in the document?

    `min_chars` stops a model from 'anchoring' a claim to the word 'and'.
    """
    s = normalise(span)
    if len(s) < min_chars:
        return False
    return s in normalise(source)


def verify(claims: list[Claim], source: str) -> tuple[list[Claim], list[Claim]]:
    """Split claims into (kept, dropped). Dropped claims are never silently lost
    -- callers are expected to write them to the audit record."""
    kept, dropped = [], []
    for c in claims:
        if anchored(c.span, source):
            c.verified, c.reason = True, "span found in source"
            kept.append(c)
        else:
            c.verified = False
            c.reason = ("span too short to be meaningful"
                        if len(normalise(c.span)) < 12
                        else "span does not appear in the source document")
            dropped.append(c)
    return kept, dropped


def evidence_ratio(kept: list[Claim], dropped: list[Claim]) -> float:
    total = len(kept) + len(dropped)
    return 1.0 if total == 0 else len(kept) / total
