"""Redaction -- what the model never sees.

Runs BEFORE extraction, and the redacted text is also the text every span is
verified against, so a quote can never smuggle a redacted value back in.

What is removed by default:
  * email addresses, phone numbers, profile / portfolio URLs
  * gendered pronouns and honorifics (he, she, his, her, Mr, Ms, ...)
  * a name line at the top of the CV ("Name: ..." or a bare 2-4 word name)
  * any names or institutions the caller passes in

What redaction CANNOT remove: proxies. "Captain, women's chess club", a
career-break year, a home town. Those are why `counterfactual.swap_test`
exists -- redaction is the first control, the swap test is how you find out
whether it was enough.

The report records counts per category, never the removed values.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+|\b(?:linkedin|github|gitlab|behance|"
                 r"dribbble|medium|x|twitter)\.com/\S+")
PHONE = re.compile(r"(?<![\w-])(?:\+\d{1,3}[\s-]?)?(?:\(?\d{2,5}\)?[\s-]?){2,4}\d{3,5}(?![\w-])")
PRONOUN = re.compile(r"(?i)\b(he|she|him|her|his|hers|himself|herself|mr|mrs|ms|miss)\b\.?")
NAME_LINE = re.compile(r"(?im)^\s*(?:full\s+)?name\s*[:\-]\s*.+$")
BARE_NAME = re.compile(r"^\s*[A-Z][a-zA-Z.'-]+(?:\s+[A-Z][a-zA-Z.'-]*){1,3}\s*$")

# A date range like 2017-06 to 2021-02 must never be mistaken for a phone number.
_DATEISH = re.compile(r"^\d{4}[-/]\d{2}$|^\d{4}$")


@dataclass
class RedactionReport:
    counts: dict[str, int] = field(default_factory=dict)

    def add(self, kind: str, n: int) -> None:
        if n:
            self.counts[kind] = self.counts.get(kind, 0) + n

    @property
    def total(self) -> int:
        return sum(self.counts.values())

    def as_dict(self) -> dict:
        return {"counts": dict(self.counts), "total": self.total}


def _sub(rx: re.Pattern, repl: str, text: str, rep: RedactionReport, kind: str) -> str:
    out, n = rx.subn(repl, text)
    rep.add(kind, n)
    return out


def _phones(text: str, rep: RedactionReport) -> str:
    def f(m):
        s = m.group(0)
        digits = re.sub(r"\D", "", s)
        if len(digits) < 8 or _DATEISH.match(s.strip()):
            return s
        rep.add("phone", 1)
        return "[PHONE]"
    return PHONE.sub(f, text)


def redact(text: str, names: tuple[str, ...] | list[str] = (),
           institutions: tuple[str, ...] | list[str] = ()) -> tuple[str, RedactionReport]:
    """Return (redacted_text, report). Deterministic: same input, same output."""
    rep = RedactionReport()
    t = text or ""
    t = _sub(EMAIL, "[EMAIL]", t, rep, "email")
    t = _sub(URL, "[URL]", t, rep, "url")
    t = _phones(t, rep)
    t = _sub(NAME_LINE, "Name: [NAME]", t, rep, "name")

    # A bare name as the first non-empty line: 2-4 capitalised words, nothing else.
    lines = t.split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        if BARE_NAME.match(line) and not re.search(r"[:|\d]", line):
            lines[i] = "[NAME]"
            rep.add("name", 1)
        break
    t = "\n".join(lines)

    for n in sorted({x.strip() for x in names if x and x.strip()}, key=len, reverse=True):
        t = _sub(re.compile(r"(?i)\b" + re.escape(n) + r"\b"), "[NAME]", t, rep, "name")
        for part in n.split():
            if len(part) >= 3:
                t = _sub(re.compile(r"\b" + re.escape(part) + r"\b"), "[NAME]", t, rep, "name")
    for inst in sorted({x.strip() for x in institutions if x and x.strip()}, key=len, reverse=True):
        t = _sub(re.compile(r"(?i)\b" + re.escape(inst) + r"\b"), "[INSTITUTION]", t, rep,
                 "institution")
    t = _sub(PRONOUN, "[PRONOUN]", t, rep, "pronoun")
    return t, rep
