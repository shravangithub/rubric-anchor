# Changelog

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
