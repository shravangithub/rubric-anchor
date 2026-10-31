"""Regenerate docs/PARAMETERS.md from the code, so the reference cannot drift.

    python scripts/gen_parameters_md.py            # write the file
    python scripts/gen_parameters_md.py --check    # exit 1 if it is stale

`tests/test_docs.py` runs the check.
"""
from __future__ import annotations
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from rubric import parameters as P                                   # noqa: E402
from rubric.packs import EDUCATION, PROOF_OF_WORK, INDUSTRY_PACKS     # noqa: E402
from rubric.roles import ROLE_PACKS                                   # noqa: E402

OUT = os.path.join(ROOT, "docs", "PARAMETERS.md")

EDU_NOTE = (
    "Education is a legitimate scored signal. The discipline is about rejection, "
    "not about whether it may be scored. Only `required_credential` may propose a "
    "rejection, only where practising without the qualification is unlawful, and a "
    "person confirms it.\n\n"
    "**Deliberately absent: institution tier / college ranking.** It is the strongest "
    "single proxy for socio-economic background in most markets and adds little over "
    "field-of-study plus demonstrated work. A test asserts it stays out.")
POW_NOTE = (
    "Externally verifiable artefacts — stronger evidence than any self-asserted "
    "claim, because a third party can check it.\n\n"
    "**Absence is neutral, never a penalty.** Employer IP policy, NDAs, caregiving "
    "load and unpaid-time inequality all suppress public output independently of "
    "ability. When these parameters find no evidence they are dropped from the "
    "composite entirely rather than scored zero — see `NEUTRAL_IF_ABSENT` and "
    "`Result.not_applicable`.")


def on_fail(p) -> str:
    if p.kind is not P.Kind.GATE:
        return "—"
    return "**propose rejection** — a person confirms" if p.bona_fide else "person decides"


def table(params) -> str:
    rows = ["| key | kind | how | weight | if the gate fails |", "|---|---|---|---|---|"]
    for p in params:
        w = f"{p.weight:.3f}" if p.kind is P.Kind.SCORED else "—"
        rows.append(f"| `{p.key}` — {p.label} | {p.kind.value} | {p.how.value} | {w} | {on_fail(p)} |")
    return "\n".join(rows)


def block(title: str, params, note: str = "") -> str:
    code = sum(1 for p in params if p.how is P.How.CODE)
    parts = [f"## {title}", ""]
    if note:
        parts += [note, ""]
    parts += [f"*{len(params)} parameters, {code} computed in code*", "", table(params), ""]
    return "\n".join(parts)


def render() -> str:
    total = (len(P.ALL) + len(EDUCATION) + len(PROOF_OF_WORK)
             + sum(map(len, INDUSTRY_PACKS.values())) + sum(map(len, ROLE_PACKS.values())))
    out = [
        "# Parameter reference", "",
        "Generated from the code by `python scripts/gen_parameters_md.py` — do not edit "
        "by hand. A test fails if this file is stale.", "",
        f"A requisition scores on: **core {len(P.ALL)} + education {len(EDUCATION)} + "
        f"proof of work {len(PROOF_OF_WORK)} + one industry pack + one role pack**, "
        f"reweighted by level. {total} parameters are defined in total "
        f"({len(INDUSTRY_PACKS)} industry packs, {len(ROLE_PACKS)} role packs); "
        "you never run all of them at once.", "",
        "Weights renormalise to 1.0 over whatever is active, so activating a pack "
        "rescales cleanly rather than quietly shrinking the core. Level weights are in "
        "[`roles-levels.html`](roles-levels.html).", "",
        "**No gate closes an application on its own.** A failed bona-fide gate proposes "
        "a rejection that a person confirms; every other gate routes to a person. A fact "
        "the CV does not state is Unknown — asked, never treated as a fail.", "",
        "# Core (role-agnostic)", "",
    ]
    for fam in dict.fromkeys(p.family for p in P.ALL):   # code order
        out.append(block(fam.upper(), [p for p in P.ALL if p.family == fam]))
    out += ["", "# Core extensions (apply to every requisition)", "",
            block("EDUCATION", EDUCATION, EDU_NOTE),
            block("PROOF OF WORK", PROOF_OF_WORK, POW_NOTE),
            "", "# Industry packs — activate exactly one", ""]
    for k in sorted(INDUSTRY_PACKS):
        out.append(block(f"{k.upper()}  (`--industry {k}`)", INDUSTRY_PACKS[k]))
    out += ["", "# Role packs — activate exactly one", ""]
    for k in ROLE_PACKS:
        out.append(block(f"{k.upper()}  (`--role {k}`)", ROLE_PACKS[k]))
    return "\n".join(out).rstrip() + "\n"


if __name__ == "__main__":
    text = render()
    if "--check" in sys.argv:
        cur = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
        if cur != text:
            sys.exit("docs/PARAMETERS.md is stale: run python scripts/gen_parameters_md.py")
        print("docs/PARAMETERS.md is current")
    else:
        open(OUT, "w", encoding="utf-8").write(text)
        print(f"wrote {OUT}")
