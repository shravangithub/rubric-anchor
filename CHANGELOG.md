# Changelog

## v0.3.0 — 31 October 2026

Three changes made in response to what was published in the last quarter.

- **Proxy redaction, on by default.** Tan et al. (EMNLP 2026) showed 18 models
  recovering ethnicity from languages spoken and gender from hobbies on CVs with
  every name removed, and that rationale prompting amplified it. `redact()`
  now removes languages-spoken, hobbies/interests, volunteering, co-curricular
  and personal-details sections before the model sees the CV; programming
  languages stay. `score_candidate(redact_proxies=False)` and provenance
  `proxy_redaction` record the choice.
- **Proxy swaps in the eval report.** `counterfactual.PROXY_VARIANTS`
  (pronouns, three language sets, three hobby sets, two volunteering lines, a
  career break) run by default in `evals/run_evals.py`, in pairs.
- **Polish-invariance test.** `rubric.polish.polish_test` has the scoring
  model rewrite the CV in shinier language with no new facts (`fact_leak`
  guards that) and requires the score not to move — the self-preference case
  from arXiv 2509.00462. In the eval report as `polish`.
- **Shuffle experiment, named and repeatable.** The write-up now says which
  model and when (claude-opus-5, 19 August 2026). `experiments/shuffle_llm/run_live.py`
  repeats the identical prompt and orders on any model; `analyse.py --results`
  reads the result.
- **`notice.adverse_explanation`** writes the plain-language adverse-outcome
  explanation Colorado's ADMT Act (1 January 2027) asks for within 30 days,
  naming the person who decided.
- NullExtractor cues match at a word start ("rest" no longer fires on
  "interests").
- Candidate notice mentions that languages, interests and volunteering are not
  shown to the tool.

## Site — 31 October 2026

- New design across all four pages of the project site. The overview opens with
  the shuffle experiment drawn as a chart from `experiments/shuffle_llm/results.json`
  (candidates that crossed the shortlist line in red) under the headline
  "Your shortlist shouldn't depend on upload order."
- One typeface (Archivo; condensed for headlines), a cool grey ground and navy
  text. Red is used only for instability and failed gates; teal for stable
  results and checks done in code.
- One top menu on every page; the tool pages lose the "back to overview" bar.
- The logo now uses the dark-text file on the light background (the old page
  used the white-text file).
- Every page fits a 390px phone screen with no sideways scrolling.
- The overview's Parameters card now says 148 (core plus 12 company types),
  matching the Parameters page; role packs are on the roles page.
- README lists every page of the site; `pyproject.toml` carries the site,
  repository and changelog links.

## Docs — 31 October 2026 (after 0.2.0)

- `docs/PARAMETERS.md` is now generated from code (`scripts/gen_parameters_md.py`)
  and checked by a test. It was stale: it listed 10 industry packs (the code has
  12) and no role packs.
- No page, table or CLI output says "auto-reject" any more; a test keeps it that
  way. Gates read "propose reject — person confirms" or "person decides".
- Project site: new "What's new in 0.2" section, `scan` and eval commands in the
  quick start, and two more honest limits (redaction is not anonymisation; the
  notice is a template, not legal advice).

Tests: 109 → 111.

## 0.2.0 — 31 October 2026

Hardening for live models and for the 2026 rules on automated hiring decisions.

**Changed behaviour**
- **Hold-and-confirm.** A failed bona-fide gate (work authorisation, required
  licence) no longer closes an application. It sets
  `decision = "confirm_reject"` and `needs_human = True`; a person confirms.
- **Unknown is not a fail.** A CV that does not state work authorisation no
  longer fails that gate. The fact is listed in `Result.unknowns`.
- **Redaction on by default.** Emails, phones, profile URLs, gendered pronouns
  and honorifics, and the name line are removed before extraction, and spans
  are verified against the redacted text. `redact_pii=False` turns it off;
  `names=` / `institutions=` remove more.
- **Fix:** the offline `NullExtractor` read "no sponsorship required" as *not*
  authorised. Combined with the old auto-reject, example `C-1041` was silently
  rejected. Regression-tested.

**Added**
- `rubric.injection` — deterministic prompt-injection scan; flagged CVs go to
  a person and claims quoting flagged lines are dropped.
- `rubric.stability` — score each candidate N times (alone), report a range,
  shortlist by band (`clear_in` / `borderline` / `clear_out`).
- `rubric.counterfactual` — swap test (pronouns, names, any replacement) to
  check what redaction missed.
- `rubric.notice` — candidate notice with a human-review route; never
  discloses scores.
- `Result.provenance` — package, extractor, model id, prompt version (hash of
  every prompt template).
- `Result.decision`, `Result.unknowns`, `Result.injection`, `Result.redaction`.
- `python -m rubric scan` and `evals/run_evals.py` (offline or live).
- Default Anthropic model updated to `claude-sonnet-5-5`.

Tests: 87 → 109.
