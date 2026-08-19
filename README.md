# TalentRubric Rank

**Absolute, evidence-anchored resume scoring. 247 parameters, ~80 active per role.**

A candidate's score is a property of *that candidate* — not of the batch they
arrived in, the order the files were uploaded, or the day you ran it.

```bash
pip install -e .
python -m rubric params --industry fintech --role backend
python -m rubric score --job examples/job.json --cvs examples/resumes \
       --industry fintech --role backend --level senior
python -m rubric audit --rankings examples/rankings.json --shortlist 4
```

No API key. No external services. The runtime dependency list is empty — the
package uses only the Python standard library, so it runs anywhere and its
tests prove its behaviour rather than mocking a vendor.

---

## The problem this exists for

Most AI screening **ranks** candidates against each other. That makes the output
for any one person a function of three things: their CV, who else happened to be
in the batch, and what order they were read in. Two of those have nothing to do
with the candidate.

So a rank cannot be stored, compared across requisitions, or reused next week.
It evaporates when the pile changes. And when a rejected candidate asks why,
there is no per-person record to point at — because the architecture has no
slot for one.

Run the audit on any existing tool and you can measure this yourself:

```
Runs: 3   Shortlist: 4
Settled in  : 3
UNSETTLED   : 2

These candidates changed sides between runs:
  C-1045           placed [5, 4, 3]
  C-1042           placed [4, 5, 6]

Their CVs did not change. Only the order did.
```

## What this does instead

Each CV is scored **alone** against a fixed rubric, and the ranking is produced
afterwards by sorting numbers. Nothing is compared, so nothing depends on the
pile.

```python
from datetime import date
from rubric import score_candidate, NullExtractor

result = score_candidate("C-1041", open("cv.txt").read(), job,
                         NullExtractor(), today=date(2026, 8, 19))

result.composite        # 48.91  -- same value in January and in June
result.gates            # pass/fail, all computed in code
result.dropped          # claims deleted for missing evidence, with reasons
result.needs_human      # and why
```

## The five rules, all enforced by tests

**1. One candidate at a time.** Handing a scorer a list raises
`ComparativeScoringError`. `test_score_is_independent_of_other_candidates`
scores a candidate, runs five other candidates through, scores again, and
asserts the number did not move.

**2. Anything computable is computed in code.** 22 of the 50 parameters never
touch a model — years of experience, tenure, ratios, thresholds. "Roughly seven
years" does not survive an audit; `months_between()` does.

**3. Every model claim carries a verbatim span.** The span is checked against
the source by substring comparison, in code. No span, no score — the parameter
contributes zero rather than an average. This turns hallucination from a fuzzy
problem into a string comparison.

**4. Only bona-fide gates may auto-reject.** Exactly two of the eight gates
qualify: work authorisation and a legally required licence. Everything else —
including `education_minimum`, deliberately — routes to a person. *The machine
narrows the pool; a human makes the adverse decision.*

**5. Protected attributes raise, they do not warn.** `BLOCKED` lists them and
`assert_no_protected_attributes` refuses any payload whose keys name one. A
compliance control that can be ignored is not a control.

## The parameters

A requisition scores on **core 50 + education 8 + proof of work 8 + one
industry pack + one role pack**, reweighted by **level**. 247 are defined;
roughly 80 run on any given requisition. 1,512 possible configurations.

**Level reweights — it never adds parameters.** If seniority added parameters,
an entry candidate would be measured on a different instrument from a director
and the two scores would not be comparable. Every level scores the same things
and weights them differently, so 62 at entry and 62 at director both mean "met
the bar for the level" — and the difference between them is inspectable.

| | entry | mid | c-level |
|---|---|---|---|
| education | 16.9% | 6.3% | 3.1% |
| proof of work | 21.2% | 10.7% | 2.6% |
| skills | 19.3% | 16.3% | 3.0% |
| scope | 3.8% | 11.7% | 20.5% |
| role pack | 11.2% | 14.2% | 24.9% |

**Roles** (`--role`), 14 across three groups:
`backend` `fde` `devops` `sre` `qa` `product_manager` ·
`marketing` `sales` `business_development` `sdr` `customer_success` ·
`eng_leadership` `exec_leadership` `gtm_leadership`

**Levels** (`--level`), 9: `entry` `junior` `mid` `senior` `lead` `manager`
`director` `vp` `c_level`

Pair a leadership pack with a junior level and the system *warns rather than
blocks* — odd pairings are sometimes correct (a founding engineer, a technical
CEO), and that is the recruiter's call, not the tool's.

See [`docs/roles-levels.html`](docs/roles-levels.html) and
[`docs/company-types.html`](docs/company-types.html) — both generated from the
code, so they cannot drift.

| Core family | Count | In code |
|---|---|---|
| eligibility | 8 (all gates) | 8 |
| experience | 8 | 8 |
| skills | 10 | 1 |
| scope | 8 | 0 |
| domain | 6 | 0 |
| trajectory | 5 | 0 |
| integrity | 5 | 5 |
| **education** | **8** | **3** |
| **proof of work** | **8** | **1** |

**Industry packs** (`--industry`), one active at a time:
`services` · `product` · `saas` · `paas` · `ecommerce` · `fintech` · `ai` ·
`infra` · `cybersec` · `pharma` — 6 to 7 parameters each, covering what
actually counts as evidence in that context: ledger and reconciliation for
fintech, GxP and audit-inspection readiness for pharma, evaluation rigour and
model risk for AI, peak-event readiness for ecommerce.

Weights renormalise to 1.0 over whatever is active, so activating a pack
rescales cleanly instead of quietly shrinking the core. Full table in
[`docs/PARAMETERS.md`](docs/PARAMETERS.md).

### Two rules inside these families worth knowing

**Education is scored, not used to silently reject.** Field of study, academic
performance, distinctions and project relevance all carry weight. Only
`required_credential` may auto-reject, and only where practising without the
qualification is unlawful — medicine, law, chartered accountancy, pharmacy QP.
`academic_performance` carries a note: weight it for early-career hiring, since
its predictive validity decays sharply after about three years of work.

**Institution tier is deliberately not a parameter.** College ranking is the
strongest single proxy for socio-economic background in most markets and adds
little over field-of-study plus demonstrated work. A test asserts it stays out.
Add it only with a documented validity study.

**Absence of proof of work is neutral, never a penalty.** Employer IP policy,
NDAs, caregiving load and unpaid-time inequality all suppress public output
independently of ability. When these parameters find no evidence they are
dropped from the composite entirely rather than scored zero — they appear in
`Result.not_applicable`, and nothing vanishes silently.

## The knowledge graph

`rubric.Graph` stores everything as triples with provenance —
`(subject) --[predicate]--> (object)` plus evidence, source and timestamp — in
SQLite, so the repo runs with no database to install.

Its purpose is **not** to screen anyone. It is to accumulate, across many
requisitions, the record that answers the question no single requisition can:

```python
graph.parameter_separation(min_group=5)
# → for each parameter, mean score of people who were hired vs rejected,
#   and the gap between them. Cells below k are suppressed.
```

Read that list from the bottom. A parameter with near-zero separation is not
distinguishing anyone — it is costing candidates time and telling you nothing.
You cannot see that from inside one requisition, and a system that ranks
comparatively cannot see it at all, because its output was never durable enough
to join to an outcome.

Causal edges (`CAUSED_BY`, `PREDICTED`) are stored with
`human_confirmed=False` by default. A model may propose a cause; it may not
assert one.

## Going live

Replace `NullExtractor` with a real client implementing three methods —
`employment`, `eligibility`, `score_parameter`. Everything else stays. The
package never imports a provider SDK, which is why the test suite runs offline
and why you are not locked to a vendor.

```python
class MyExtractor:
    def employment(self, resume: str) -> list[dict]: ...
    def eligibility(self, resume: str) -> dict: ...
    def score_parameter(self, key, resume, rubric) -> Claim: ...
```

Keep the contract: `score_parameter` must return a `Claim` whose `span` is
copied verbatim from the resume. A paraphrased span fails verification and the
parameter scores zero — which is the intended behaviour, not a bug.

## What this does not do

**It does not make your shortlist better at predicting talent.** It makes it
repeatable and explainable. Those are different claims, and only the second one
is honest.

**It does not validate your rubric.** A perfectly built system applying criteria
that do not predict job performance will apply them consistently to everyone.
`parameter_separation()` is where you start checking — but it needs a few
hundred hires and a couple of years before it says anything.

**It catches noise, not bias.** The audit finds candidates a system is *unsure*
about. A system that is *confidently wrong* about a whole group will look
perfectly settled. Only outcome tracking finds that.

**The default weights are a starting point, not a validated instrument.** They
encode plausible relative importance for a senior individual-contributor
engineering role. Reweight them for your context, and record who approved the
change and when.

## Legal note

Automated employment decisions are regulated, and the regulation is moving.
Nothing here is legal advice. Decide before your first run — with whoever owns
employment law and data protection where you operate — which criteria may
auto-reject, how long records are kept, and whether re-using old applications
for a new role is permitted in your jurisdiction.

## Tests

```bash
pip install -e ".[dev]" && pytest -q
```

57 tests. They are the specification: if you change a rule, a test should fail
and you should have to write down why.

Some of them exist to stop a well-meaning future change: `test_institution_tier_is_not_a_parameter`,
`test_absence_of_proof_of_work_is_neutral_not_penalised`, and
`test_education_is_scorable_but_only_credentials_auto_reject`.

## License

MIT. See `LICENSE`.
