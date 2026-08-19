"""The model seam.

Implement `Extractor` against any provider. The rest of the package never
imports an SDK, so the repo runs and its tests pass with no API key.
"""
from __future__ import annotations
import re
from typing import Protocol
from .evidence import Claim


class Extractor(Protocol):
    def employment(self, resume: str) -> list[dict]: ...
    def eligibility(self, resume: str) -> dict: ...
    def score_parameter(self, key: str, resume: str, rubric: dict) -> Claim: ...


class NullExtractor:
    """Deterministic stand-in. Same input -> same output, always.

    It is intentionally simple: it reads dated employment lines, looks for a
    work-authorisation statement, and scores MODEL parameters from keyword
    evidence. Replace it with a real client; keep the contract.
    """

    ROW = re.compile(
        r"(?im)^\s*[-*]?\s*(?P<title>[^|\n]+?)\s*\|\s*(?P<company>[^|\n]+?)\s*\|\s*"
        r"(?P<start>\d{4}-\d{2})\s*(?:to|-|–)\s*(?P<end>\d{4}-\d{2}|present)")

    CUES: dict[str, tuple[str, ...]] = {
        "core_skill_coverage":      ("distributed", "api", "pipeline", "service"),
        "core_skill_depth":         ("sharding", "consensus", "throughput", "latency"),
        "secondary_skill_coverage": ("sql", "kafka", "redis", "docker"),
        "tooling_familiarity":      ("kubernetes", "terraform", "airflow", "git"),
        "technical_breadth":        ("frontend", "data", "infra", "mobile"),
        "hands_on_recency":         ("built", "wrote", "implemented", "shipped"),
        "certification_relevance":  ("certified", "certification"),
        "skill_evidence_specificity": ("%", "reduced", "increased", "cut"),
        "self_directed_learning":   ("learned", "course", "self-taught"),
        "team_size_led":            ("team of", "engineers", "reports"),
        "resource_scope":           ("budget", "headcount", "portfolio"),
        "project_complexity":       ("migration", "rearchitect", "scale", "redesign"),
        "cross_functional_reach":   ("product", "design", "stakeholder", "cross-functional"),
        "outcome_quantification":   ("%", "x faster", "reduced", "saved"),
        "ownership_end_to_end":     ("owned", "led", "end to end", "from scratch"),
        "operational_responsibility": ("on-call", "oncall", "incident", "sre"),
        "mentoring_evidence":       ("mentored", "coached", "onboarded"),
        "industry_relevance":       ("payments", "fintech", "banking", "ledger"),
        "regulated_environment":    ("pci", "kyc", "compliance", "audit"),
        "company_stage_fit":        ("startup", "scale-up", "enterprise"),
        "customer_segment_fit":     ("b2b", "b2c", "enterprise", "consumer"),
        "scale_of_systems":         ("million", "tps", "qps", "petabyte"),
        "market_experience":        ("india", "emea", "apac", "us market"),
        "promotion_history":        ("promoted", "promotion"),
        "increasing_scope":         ("staff", "principal", "lead", "head of"),
        "role_coherence":           ("engineer", "developer", "architect"),
        "transition_clarity":       ("moved to", "transitioned", "joined to"),
        "level_readiness":          ("staff", "principal", "lead", "owned"),
    }

    def employment(self, resume: str) -> list[dict]:
        return [{"title": m.group("title").strip(),
                 "company": m.group("company").strip(),
                 "start": m.group("start"),
                 "end": m.group("end").lower(),
                 "span": m.group(0).strip()}
                for m in self.ROW.finditer(resume)]

    def eligibility(self, resume: str) -> dict:
        out = {}
        m = re.search(r"(?im)^.*work\s*authoris?z?ation.*$", resume)
        if m:
            out["work_authorization"] = {
                "value": not re.search(r"(?i)\b(not|no|requires? sponsorship)\b", m.group(0)),
                "span": m.group(0).strip()}
        m = re.search(r"(?im)^.*notice period.*$", resume)
        if m:
            d = re.search(r"(\d+)\s*(day|week|month)", m.group(0), re.I)
            out["notice_period_days"] = {
                "value": _to_days(d) if d else None, "span": m.group(0).strip()}
        return out

    def score_parameter(self, key: str, resume: str, rubric: dict) -> Claim:
        cues = self.CUES.get(key, ())
        hits, span = [], ""
        for c in cues:
            m = re.search(r"(?im)^.*" + re.escape(c) + r".*$", resume)
            if m:
                hits.append(c)
                span = span or m.group(0).strip()
        score = 0.0 if not cues else min(100.0, 22.0 * len(hits))
        return Claim(parameter=key, value=score, span=span,
                     confidence=0.6 if hits else 0.2)


def _to_days(m) -> int:
    n, unit = int(m.group(1)), m.group(2).lower()
    return n * {"day": 1, "week": 7, "month": 30}[unit]
