"""A small, dependency-free knowledge graph.

Everything is a triple with provenance:

    (subject) --[predicate]--> (object)   + evidence, source, timestamp

Stored in SQLite so the repo runs anywhere. Swap in Neo4j by reimplementing
`Graph` -- the rest of the package only uses this interface.

The point of the graph is NOT to screen a candidate. It is to accumulate,
across many requisitions, the record that answers the only question that
really matters: *which of our parameters actually predicted a good hire?*
"""
from __future__ import annotations
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass

SCHEMA = """
CREATE TABLE IF NOT EXISTS node (
  id     TEXT PRIMARY KEY,
  label  TEXT NOT NULL,
  props  TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS edge (
  src        TEXT NOT NULL,
  predicate  TEXT NOT NULL,
  dst        TEXT NOT NULL,
  props      TEXT NOT NULL DEFAULT '{}',
  evidence   TEXT,
  source     TEXT,
  at         TEXT,
  PRIMARY KEY (src, predicate, dst, at)
);
CREATE INDEX IF NOT EXISTS edge_src ON edge(src, predicate);
CREATE INDEX IF NOT EXISTS edge_dst ON edge(dst, predicate);
CREATE INDEX IF NOT EXISTS node_label ON node(label);
"""

#: Causal edges are claims, not observations. They require a human to confirm
#: before any answer may present them as causal.
CAUSAL = {"CAUSED_BY", "PREDICTED"}


@dataclass
class Edge:
    src: str
    predicate: str
    dst: str
    props: dict
    evidence: str | None
    source: str | None
    at: str | None


class Graph:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # -- write -------------------------------------------------------------
    def node(self, id: str, label: str, **props) -> str:
        self.conn.execute(
            "INSERT INTO node(id,label,props) VALUES(?,?,?) "
            "ON CONFLICT(id) DO UPDATE SET label=excluded.label, props=excluded.props",
            (id, label, json.dumps(props, sort_keys=True)))
        return id

    def edge(self, src: str, predicate: str, dst: str, *,
             evidence: str | None = None, source: str | None = None,
             at: str = "", **props) -> None:
        if predicate in CAUSAL and not props.get("human_confirmed"):
            props["human_confirmed"] = False   # stored, but not answerable as causal
        self.conn.execute(
            "INSERT OR REPLACE INTO edge(src,predicate,dst,props,evidence,source,at) "
            "VALUES(?,?,?,?,?,?,?)",
            (src, predicate, dst, json.dumps(props, sort_keys=True),
             evidence, source, at))

    def commit(self) -> None:
        self.conn.commit()

    # -- read --------------------------------------------------------------
    def out(self, src: str, predicate: str | None = None) -> list[Edge]:
        q = "SELECT src,predicate,dst,props,evidence,source,at FROM edge WHERE src=?"
        a = [src]
        if predicate:
            q += " AND predicate=?"; a.append(predicate)
        with closing(self.conn.execute(q, a)) as cur:
            return [Edge(r[0], r[1], r[2], json.loads(r[3]), r[4], r[5], r[6])
                    for r in cur.fetchall()]

    def props(self, id: str) -> dict:
        r = self.conn.execute("SELECT props FROM node WHERE id=?", (id,)).fetchone()
        return json.loads(r[0]) if r else {}

    def count(self) -> tuple[int, int]:
        n = self.conn.execute("SELECT COUNT(*) FROM node").fetchone()[0]
        e = self.conn.execute("SELECT COUNT(*) FROM edge").fetchone()[0]
        return n, e

    # -- the query the whole thing exists for ------------------------------
    def parameter_separation(self, min_group: int = 5) -> list[dict]:
        """For each parameter, the mean score of people who were HIRED vs those
        who were REJECTED, and the gap between them.

        A parameter with a near-zero gap is not distinguishing anyone. It is
        costing candidates time and telling you nothing -- and you cannot see
        that from inside a single requisition.

        `min_group` suppresses any cell below k. Never lower it for people data.
        """
        rows = self.conn.execute("""
            SELECT s.predicate                AS parameter,
                   o.dst                      AS outcome,
                   AVG(json_extract(s.props,'$.score')) AS mean_score,
                   COUNT(DISTINCT s.src)      AS n
            FROM edge s
            JOIN edge o ON o.src = s.src AND o.predicate = 'RESULTED_IN'
            WHERE s.predicate LIKE 'SCORED_%'
            GROUP BY parameter, outcome
        """).fetchall()
        agg: dict[str, dict] = {}
        for param, outcome, mean, n in rows:
            key = param.replace("SCORED_", "")
            agg.setdefault(key, {"parameter": key})
            agg[key][outcome] = None if n < min_group else round(mean or 0, 2)
            agg[key][f"n_{outcome}"] = n
        out = []
        for k, v in agg.items():
            hi, lo = v.get("hired"), v.get("rejected")
            v["separation"] = None if hi is None or lo is None else round(hi - lo, 2)
            out.append(v)
        return sorted(out, key=lambda r: (r["separation"] is None,
                                          abs(r["separation"] or 0)))
