# We asked the same AI to rank the same 12 CVs five times. One candidate moved seven places.

Everything written about AI screening instability is either argued or simulated.
This is measured.

## The test

Twelve CVs for one senior backend role, written to be genuinely close in
strength — twelve plausible candidates, not a CEO next to an intern. Five
independent instances of a current frontier model. Each was shown the same
twelve CVs **in a different order** and asked to rank all twelve. No instance
could see any other.

Nothing about any candidate changed between runs. Only the sequence.

## The result

**The extremes never moved.** Three candidates placed 1st, 2nd and 3rd in all
five runs. One placed 12th every time. The obvious calls were obvious.

**The middle came apart.**

| candidate | run 1 | run 2 | run 3 | run 4 | run 5 | swing |
|---|---|---|---|---|---|---|
| **G** | 6 | 8 | **11** | **4** | 5 | **7 places** |
| **H** | 5 | 5 | 5 | 5 | **9** | 4 places |
| E | 10 | 7 | 10 | 8 | 8 | 3 places |

G was ranked **4th in one run and 11th in another** on an unchanged CV.

H is the one I keep coming back to. It placed 5th in four consecutive runs —
more than enough to conclude it was settled — and 9th in the fifth. **A
three-run test would have missed it entirely.**

## It depends entirely on where you draw the line

| shortlist size | candidates that changed sides |
|---|---|
| 3 | **0** |
| 4 | 2 |
| 5 | **3 — a quarter of the pool** |
| 6 | 3 |

Shortlist three from twelve and this costs you nothing. Shortlist five and a
quarter of your pool is decided by something other than their CV.

That is the practical finding: **instability doesn't spread evenly. It
concentrates exactly at the cut line — which is the only place decisions
actually get made.**

## Four things this is not

**The CVs are synthetic.** I did not use real resumes. Those are identifiable
people who never consented to being ranked and having the result published.
The CVs are invented; the ranker is real, and it is the ranker's stability
being measured.

**They were written to be close on purpose.** A pool with clearer separation
shows less movement. This is the hard case by construction, not a typical one.

**Order was not the only variable.** Separate model instances also vary in
sampling. So this measures *total run-to-run instability*, of which input order
is one component. Isolating order alone needs deterministic decoding with only
the sequence changing.

**Five runs, one role, twelve candidates.** Directional, not definitive.

## Why publish it anyway

Because the *shape* is the point, and the shape is unambiguous: stable at both
ends, unstable at the boundary. That is what every simulation of this predicts,
and now there is a measurement behind it.

And because it is testable. Take a requisition you have already closed. Run
your screening three times with the CVs shuffled. Count how many names cross
your shortlist line.

If it comes back zero, your setup is steady and you can ignore all of this —
which is a genuinely useful thing to learn in twenty minutes.

If it comes back at three, those were three people whose outcome came down to
what order the files were in.

---

*Method, data and analysis script:
[experiments/shuffle_llm](https://github.com/YOURORG/rubric-anchor/tree/main/experiments/shuffle_llm)*
