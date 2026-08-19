"""Knowledge graph engineering for hiring.

`graph.py` is the store. This is the engineering on top of it -- the part that
turns a pile of scores into something that can answer questions no single
requisition can.

Four capabilities, in the order they become useful:

  1. INGEST      every scored candidate becomes triples with provenance
  2. RESOLVE     one person, one node, across requisitions and spellings
  3. VALIDATE    which parameters actually predicted a good hire
  4. DEFEND      reconstruct what the system believed on any past date

The fourth is the one people underestimate. An employment decision is
challenged months or years later, by which time your weights have changed,
your model has changed, and the candidate is asking about a run you can no
longer reproduce. Bi-temporal storage is how you answer.

Design notes
------------
* **Bi-temporal.** Every fact carries `valid_from` (when it was true in the
  world) and `recorded_at` (when we learned it). Those differ constantly --
  a promotion effective in March recorded in June -- and conflating them is
  how audit answers become wrong.
* **Append-only.** Nothing is updated in place. Corrections supersede.
* **Provenance on every edge.** Source document, extractor version, and the
  evidence span.
* **No protected attributes, ever.** Fairness monitoring takes externally
  supplied aggregate counts and never joins back to a person. See
  `FairnessMonitor`.
"""
from __future__ import annotations

import json
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field

from .graph import Graph
from .guards import assert_no_protected_attributes


# ===========================================================================
# 1. INGEST
# ===========================================================================
class PeopleGraph(Graph):
    """A bi-temporal, provenance-carrying store of hiring facts."""

    def __init__(self, path: str = ":memory:", extractor_version: str = "null-0.1"):
        super().__init__(path)
        self.extractor_version = extractor_version
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS fact (
          person_id   TEXT NOT NULL,
          req_id      TEXT,
          predicate   TEXT NOT NULL,
          value_num   REAL,
          value_txt   TEXT,
          evidence    TEXT,
          source      TEXT,
          extractor   TEXT,
          valid_from  TEXT NOT NULL,
          recorded_at TEXT NOT NULL,
          superseded  INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS fact_person ON fact(person_id, predicate);
        CREATE INDEX IF NOT EXISTS fact_req ON fact(req_id, predicate);
        CREATE INDEX IF NOT EXISTS fact_time ON fact(valid_from, recorded_at);
        CREATE TABLE IF NOT EXISTS alias (
          alias_id  TEXT PRIMARY KEY,
          person_id TEXT NOT NULL,
          basis     TEXT,
          at        TEXT
        );
        """)
        self.conn.commit()

    # -- writing ----------------------------------------------------------
    def ingest_result(self, result, req_id: str, *, at: str,
                      recorded_at: str | None = None,
                      config: dict | None = None) -> str:
        """Write one scored candidate into the graph.

        `at` is when the assessment was valid; `recorded_at` when it was
        written. They differ when you backfill.
        """
        rec = recorded_at or at
        pid = self.person(result.candidate_id)
        self.node(pid, "Person")
        self.node(req_id, "Requisition", **(config or {}))
        self.edge(pid, "APPLIED_TO", req_id, at=at, source=result.candidate_id)

        rows = []
        for key, score in result.scores.items():
            span = next((c.span for c in result.kept if c.parameter == key), None)
            rows.append((pid, req_id, f"SCORED_{key}", float(score), None,
                         span, result.candidate_id, self.extractor_version,
                         at, rec, 0))
        rows.append((pid, req_id, "COMPOSITE", float(result.composite), None,
                     None, result.candidate_id, self.extractor_version, at, rec, 0))
        if result.role_fit is not None:
            rows.append((pid, req_id, "ROLE_FIT", float(result.role_fit), None,
                         None, result.candidate_id, self.extractor_version,
                         at, rec, 0))
        for k in result.not_applicable:
            rows.append((pid, req_id, f"NOT_APPLICABLE_{k}", None, "absent",
                         None, result.candidate_id, self.extractor_version,
                         at, rec, 0))
        for c in result.dropped:
            rows.append((pid, req_id, f"DROPPED_{c.parameter}", None, c.reason,
                         c.span, result.candidate_id, self.extractor_version,
                         at, rec, 0))
        self.conn.executemany(
            "INSERT INTO fact(person_id,req_id,predicate,value_num,value_txt,"
            "evidence,source,extractor,valid_from,recorded_at,superseded) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?)", rows)
        self.commit()
        return pid

    def record_outcome(self, candidate_id: str, req_id: str, kind: str, *,
                       at: str, recorded_at: str | None = None,
                       note: str = "") -> None:
        """hired / rejected / withdrew / declined_offer / regretted_attrition /
        promoted / left_voluntarily ..."""
        pid = self.person(candidate_id)
        self.conn.execute(
            "INSERT INTO fact(person_id,req_id,predicate,value_txt,source,"
            "extractor,valid_from,recorded_at,superseded) "
            "VALUES(?,?,?,?,?,?,?,?,0)",
            (pid, req_id, "OUTCOME", kind, note, self.extractor_version,
             at, recorded_at or at))
        self.edge(pid, "RESULTED_IN", kind, at=at)
        self.commit()

    def record_performance(self, candidate_id: str, *, rating: float,
                           at: str, scale_max: float = 5.0) -> None:
        """The other end of the loop. Without this, nothing can be validated."""
        pid = self.person(candidate_id)
        self.conn.execute(
            "INSERT INTO fact(person_id,predicate,value_num,valid_from,"
            "recorded_at,extractor,superseded) VALUES(?,?,?,?,?,?,0)",
            (pid, "PERFORMANCE", float(rating) / scale_max, at, at,
             self.extractor_version))
        self.commit()

    # -- identity ---------------------------------------------------------
    def person(self, alias_id: str) -> str:
        r = self.conn.execute("SELECT person_id FROM alias WHERE alias_id=?",
                              (alias_id,)).fetchone()
        return r[0] if r else alias_id

    def merge(self, keep: str, absorb: str, basis: str, at: str) -> None:
        """Collapse a duplicate. Logged, and therefore reversible.

        Deterministic keys only -- employee ID, verified email, ATS ID.
        Similar names are never sufficient evidence, and this method does not
        try to guess. Fuzzy candidates go to a human queue instead.
        """
        if keep == absorb:
            return
        self.conn.execute(
            "INSERT OR REPLACE INTO alias(alias_id,person_id,basis,at) "
            "VALUES(?,?,?,?)", (absorb, keep, basis, at))
        self.conn.execute("UPDATE fact SET person_id=? WHERE person_id=?",
                          (keep, absorb))
        self.commit()

    # -- reading ----------------------------------------------------------
    def as_of(self, predicate: str, *, valid_on: str, known_on: str
              ) -> list[tuple]:
        """What did we believe about this predicate on `known_on`, about the
        world as it stood on `valid_on`?

        This is the query that answers a challenge. Using current state to
        explain a past decision produces an answer that is confidently wrong.
        """
        return self.conn.execute(
            "SELECT person_id, req_id, value_num, value_txt, evidence "
            "FROM fact WHERE predicate=? AND valid_from<=? AND recorded_at<=? "
            "AND superseded=0", (predicate, valid_on, known_on)).fetchall()

    def explain(self, candidate_id: str, req_id: str, top: int = 8) -> list[dict]:
        """Which parameters drove this person's score, largest first.

        Contribution = score x normalised weight, recovered from what was
        actually stored rather than recomputed from today's config.
        """
        pid = self.person(candidate_id)
        rows = self.conn.execute(
            "SELECT predicate, value_num, evidence FROM fact "
            "WHERE person_id=? AND req_id=? AND predicate LIKE 'SCORED_%' "
            "AND superseded=0", (pid, req_id)).fetchall()
        if not rows:
            return []
        from . import parameters as P
        from .packs import EDUCATION, PROOF_OF_WORK, INDUSTRY_PACKS
        from .roles import ROLE_PACKS
        wmap = {p.key: p.weight for p in P.ALL}
        for grp in (EDUCATION, PROOF_OF_WORK,
                    *INDUSTRY_PACKS.values(), *ROLE_PACKS.values()):
            wmap.update({p.key: p.weight for p in grp})
        contrib = []
        for pred, val, ev in rows:
            k = pred[len("SCORED_"):]
            w = wmap.get(k, 0.0)
            contrib.append({"parameter": k, "score": val, "weight": w,
                            "contribution": (val or 0) * w, "evidence": ev})
        tot = sum(c["contribution"] for c in contrib) or 1.0
        for c in contrib:
            c["share_pct"] = round(c["contribution"] / tot * 100, 2)
        return sorted(contrib, key=lambda c: -c["contribution"])[:top]

    def stats(self) -> dict:
        q = lambda s: self.conn.execute(s).fetchone()[0]
        return {"people": q("SELECT COUNT(DISTINCT person_id) FROM fact"),
                "requisitions": q("SELECT COUNT(DISTINCT req_id) FROM fact"),
                "facts": q("SELECT COUNT(*) FROM fact"),
                "outcomes": q("SELECT COUNT(*) FROM fact WHERE predicate='OUTCOME'"),
                "merges": q("SELECT COUNT(*) FROM alias")}


# ===========================================================================
# 3. VALIDATE -- the payoff
# ===========================================================================
def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 3:
        return None
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a - mx) ** 2 for a in xs))
    dy = math.sqrt(sum((b - my) ** 2 for b in ys))
    return None if dx == 0 or dy == 0 else round(num / (dx * dy), 3)


@dataclass
class ParameterVerdict:
    parameter: str
    n: int
    r_performance: float | None      # correlation with later performance
    mean_hired: float | None
    mean_rejected: float | None
    separation: float | None
    verdict: str


class Validity:
    """Does this parameter predict anything?

    Two independent questions, and they are not the same:
      * SEPARATION -- did it distinguish the people you hired from those you
        rejected? (measures your PROCESS, and is circular by construction)
      * CORRELATION with later performance -- did it predict who was good?
        (measures the PARAMETER, and is the one that matters)

    A parameter can separate strongly and predict nothing. That is the most
    important failure this module exists to surface: it means the parameter is
    driving your decisions without earning it.

    SELECTION BIAS -- read this before trusting a correlation
    ---------------------------------------------------------
    Performance ratings exist only for people you HIRED. That is a selected
    sample, and correlating within it is biased in a specific, predictable
    direction: among hires, a weak score on one criterion must have been
    offset by a strong score on another, or they would not have been hired at
    all. This manufactures SPURIOUS NEGATIVE correlations between criteria
    that are genuinely independent. (Collider stratification, sometimes called
    Berkson's paradox.)

    Practical reading rules:
      * A strong POSITIVE r is trustworthy -- selection works against it, so
        it survived a headwind.
      * A weak NEGATIVE r on a criterion your process leans on is very likely
        an artefact, NOT evidence the criterion is harmful. `report()` flags
        these rather than scoring them.
      * The bias cannot be removed without performance data on people you did
        not hire, which you will never have. Correcting for it properly means
        a selection model (Heckman-type), which is beyond this module.

    Treat this as a screening tool that tells you where to look, never as a
    validity study.
    """

    def __init__(self, g: PeopleGraph, min_group: int = 5):
        self.g, self.k = g, min_group

    def _series(self) -> tuple[dict, dict, dict]:
        scores = defaultdict(dict)
        for pid, pred, val in self.g.conn.execute(
                "SELECT person_id, predicate, value_num FROM fact "
                "WHERE predicate LIKE 'SCORED_%' AND superseded=0"):
            scores[pred[len("SCORED_"):]][pid] = val
        outcome = {r[0]: r[1] for r in self.g.conn.execute(
            "SELECT person_id, value_txt FROM fact WHERE predicate='OUTCOME' "
            "AND superseded=0")}
        perf = {r[0]: r[1] for r in self.g.conn.execute(
            "SELECT person_id, value_num FROM fact WHERE predicate='PERFORMANCE' "
            "AND superseded=0")}
        return scores, outcome, perf

    def report(self) -> list[ParameterVerdict]:
        scores, outcome, perf = self._series()
        out = []
        for param, by_person in scores.items():
            hired = [v for p, v in by_person.items() if outcome.get(p) == "hired"]
            rej = [v for p, v in by_person.items() if outcome.get(p) == "rejected"]
            paired = [(v, perf[p]) for p, v in by_person.items() if p in perf]
            r = _pearson([a for a, _ in paired], [b for _, b in paired])
            mh = round(statistics.fmean(hired), 2) if len(hired) >= self.k else None
            mr = round(statistics.fmean(rej), 2) if len(rej) >= self.k else None
            sep = round(mh - mr, 2) if mh is not None and mr is not None else None

            # Negative r on a criterion the process rewards is the classic
            # selection artefact -- do not read it as "harmful".
            suspect = (r is not None and r < 0 and sep is not None and sep > 3)
            if r is None:
                v = "no outcome data yet"
            elif suspect:
                v = "SUSPECT -- likely selection artefact, not signal"
            elif abs(r) < 0.05:
                v = ("DROP -- separates but does not predict"
                     if sep and abs(sep) > 5 else "DROP -- no signal")
            elif r < 0:
                v = "negative -- investigate before acting"
            elif r < 0.15:
                v = "weak"
            elif r < 0.3:
                v = "useful"
            else:
                v = "strong"
            out.append(ParameterVerdict(param, len(paired), r, mh, mr, sep, v))
        return sorted(out, key=lambda x: (x.r_performance is None,
                                          -abs(x.r_performance or 0)))

    def drop_one(self, parameter: str, shortlist_pct: float = 0.15) -> dict:
        """Counterfactual: if this parameter had not existed, who would have
        got a DIFFERENT OUTCOME?

        Measured as churn across the shortlist boundary, not as any change in
        rank. Removing any weight nudges almost every rank slightly -- an
        earlier version of this method reported ~90% movement for every
        parameter, which is true and completely useless. What a hiring manager
        needs to know is whether anyone's answer would have changed.
        """
        scores, _, _ = self._series()
        if parameter not in scores:
            raise ValueError(f"no stored scores for '{parameter}'")
        comps = {r[0]: r[1] for r in self.g.conn.execute(
            "SELECT person_id, value_num FROM fact WHERE predicate='COMPOSITE' "
            "AND superseded=0")}
        from . import parameters as P
        from .packs import EDUCATION, PROOF_OF_WORK, INDUSTRY_PACKS
        from .roles import ROLE_PACKS
        wmap = {p.key: p.weight for p in P.ALL}
        for grp in (EDUCATION, PROOF_OF_WORK, *INDUSTRY_PACKS.values(),
                    *ROLE_PACKS.values()):
            wmap.update({p.key: p.weight for p in grp})
        w = wmap.get(parameter, 0.0)
        n = len(comps)
        cut = max(1, int(round(n * shortlist_pct)))
        before = set(sorted(comps, key=lambda p: -comps[p])[:cut])
        adj = {p: comps[p] - scores[parameter].get(p, 0) * w for p in comps}
        after = set(sorted(adj, key=lambda p: -adj[p])[:cut])
        churn = len(before - after)
        return {"parameter": parameter, "weight": w, "people": n,
                "shortlist": cut, "swapped": churn,
                "pct_of_shortlist": round(churn / cut * 100, 1)}


# ===========================================================================
# 4. FAIRNESS -- aggregate only, never joined back to a person
# ===========================================================================
class FairnessMonitor:
    """Adverse-impact monitoring without ever storing a protected attribute.

    The graph holds no such attribute and never will. This class accepts
    aggregate counts assembled elsewhere -- typically from voluntary,
    separately-stored self-identification -- and returns selection rates and
    the four-fifths ratio. It has no access to and cannot request per-person
    data, which is the point.
    """

    @staticmethod
    def selection_rates(counts: dict[str, tuple[int, int]],
                        min_group: int = 30) -> dict:
        """counts: group -> (selected, total). Groups below `min_group` are
        suppressed rather than reported -- small-cell rates are noise, and
        publishing them is a re-identification risk."""
        assert_no_protected_attributes({"counts": {}}, "fairness monitoring")
        rates, suppressed = {}, []
        for g, (sel, tot) in counts.items():
            if tot < min_group:
                suppressed.append(g)
                continue
            rates[g] = round(sel / tot, 4) if tot else 0.0
        if len(rates) < 2:
            return {"rates": rates, "suppressed": suppressed,
                    "four_fifths": None,
                    "note": "need at least two groups above the minimum size"}
        best = max(rates.values())
        ratios = {g: (round(r / best, 3) if best else None) for g, r in rates.items()}
        flagged = [g for g, v in ratios.items() if v is not None and v < 0.8]
        return {"rates": rates, "ratios": ratios, "suppressed": suppressed,
                "four_fifths_flagged": flagged,
                "note": ("The four-fifths rule is a screening heuristic, not a "
                         "legal finding. A flag means investigate, and a pass "
                         "does not mean compliant.")}
