# We asked the same AI to rank the same 12 CVs five times. One candidate moved seven places.

Everything written about AI screening instability is either argued or simulated.
This is measured.

## The test

Twelve CVs for one senior backend role, written to be genuinely close in
strength — twelve plausible candidates, not a CEO next to an intern. Five
independent instances of one model — claude-opus-5, default sampling, run on
19 August 2026. Each was shown the same
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

## Across models

The run above is claude-opus-5 on 19 August 2026. On 1 November 2026 the
identical prompt and orders were run on gpt-5-mini (default reasoning,
temperature 1.0) via `run_live.py`:

| model | date | runs | moved 4+ places | biggest swing | unsettled at 3 | unsettled at 5 | top 3 held | last held |
|---|---|---|---|---|---|---|---|---|
| claude-opus-5 | 2026-08-19 | 5 | 2 of 12 | 7 places (G) | 0 | 3 | 3 of 3 | yes |
| gpt-5-mini | 2026-11-01 | 5 | 1 of 12 | 4 places (E) | 0 | 2 | 3 of 3 | no |

Same shape on both: the extremes hold, the middle moves, and the movement sits
at the shortlist cut (0 unsettled at a shortlist of 3, 2–3 at 5). gpt-5-mini
moved less — it reasons before answering — but it still moved: E was 7th in
two runs and 11th in another.

The larger finding is between the models, not within them:

| candidate | Opus, 5 runs | gpt-5-mini, 5 runs |
|---|---|---|
| A | 1, 1, 1, 1, 1 | 2, 2, 2, 1, 1 |
| C | 2, 2, 2, 2, 2 | 1, 1, 1, 2, 2 |
| **G** | **6, 8, 11, 4, 5** | **3, 3, 3, 3, 3** |
| J | 3, 3, 3, 3, 3 | 4, 4, 4, 5, 4 |
| L | 12, 12, 12, 12, 12 | 12, 12, 12, 11, 12 |

G — the engineering lead with the bank-modernisation record — is the candidate
Opus could not place (4th to 11th) and the candidate gpt-5-mini is sure about
(3rd, five times out of five). One Gemini 2.5 Flash run, before that key's
daily quota closed, also put G 3rd. Whether G is shortlisted at all is decided
by which model the recruiter happened to be using. Nothing about G changed.

That is the argument for scoring against a fixed rubric with evidence spans,
in a form the shuffle alone could not make: a comparative ranker is unstable
*within* a model and inconsistent *between* models, and both faults land on
the same person — the one whose profile does not match the template.

Results files for other models are welcome as pull requests
(`run_live.py --provider ... --model ...`; `compare.py --md` builds the table).

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
