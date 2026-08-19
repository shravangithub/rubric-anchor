# Shuffle stability, measured on a real model

Everything else in this repo that talks about ranking instability is either
argued or simulated. This is measured.

## Design

Twelve synthetic senior-backend CVs, written to be **close in strength** — the
hard case by construction. Five independent model instances, each shown the
same twelve CVs **in a different order**, each asked to rank all twelve. No
instance could see any other.

```bash
python experiments/shuffle_llm/analyse.py
```

## Result

The extremes were perfectly stable. **A, C and J placed 1st, 2nd and 3rd in all
five runs. L placed 12th every time.**

The middle was not:

| candidate | r1 | r2 | r3 | r4 | r5 | swing |
|---|---|---|---|---|---|---|
| **G** | 6 | 8 | **11** | **4** | 5 | **7 places** |
| **H** | 5 | 5 | 5 | 5 | **9** | 4 places |
| E | 10 | 7 | 10 | 8 | 8 | 3 places |

G was ranked 4th in one run and 11th in another, on an unchanged CV.

H is the more instructive case: it placed 5th in four consecutive runs — enough
to look settled — and 9th in the fifth. **Three runs would have missed it.**

## Churn depends on where you draw the line

| shortlist | unsettled |
|---|---|
| 3 | **0** |
| 4 | 2 |
| 5 | **3 (25% of the pool)** |
| 6 | 3 |

Shortlist three from twelve and this costs you nothing. Shortlist five and a
quarter of the pool is a coin flip.

## Caveats

**Synthetic CVs.** Real resumes were not used. They are identifiable people who
did not consent to being ranked and having the result published.

**Deliberately close in strength.** A pool with clearer separation shows less
churn. This is the hard case on purpose.

**Order is not the only variable.** Separate instances also vary in sampling, so
this measures *total run-to-run instability*, of which input order is one
component. Isolating order alone needs deterministic decoding with only the
sequence changing.

**N=5, one role, one pool.** Directional, not definitive — and the point is the
*shape*, which matches what the simulations predicted: stable at both ends,
unstable exactly at the boundary where the decision gets made.
