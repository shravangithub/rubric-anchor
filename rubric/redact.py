"""Redaction -- what the model never sees.

Runs BEFORE extraction, and the redacted text is also the text every span is
verified against, so a quote can never smuggle a redacted value back in.

What is removed by default:
  * email addresses, phone numbers, profile / portfolio URLs
  * gendered pronouns and honorifics (he, she, his, her, Mr, Ms, ...)
  * a name line at the top of the CV ("Name: ..." or a bare 2-4 word name)
  * any names or institutions the caller passes in

  * (proxies=True, default) the sections that leak demographics without
    naming them: languages spoken, hobbies and interests, volunteering,
    co-curricular activities, "personal details". Tan et al. (EMNLP 2026)
    showed 18 models recovering ethnicity from spoken languages and gender
    from hobbies on CVs that had every name removed, so these go to the
    human reviewer, never to the model. Programming-language lines are kept.

What redaction CANNOT remove: proxies that live inside the work history.
"Captain, women's chess club" under a job, a career-break year, a home town.
Those are why `counterfactual.swap_test` exists -- redaction is the first
control, the swap test is how you find out whether it was enough.

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

# ---- proxy sections ------------------------------------------------------
# A heading line (optionally with a colon and inline values) that opens a
# section the model should not see. The section runs to the next blank line
# or the next heading-looking line.
PROXY_HEAD = re.compile(
    r"(?im)^\s*(?:#+\s*)?(?P<kind>"
    r"languages?(?:\s+(?:spoken|known))?|spoken\s+languages?|linguistic\s+skills?|"
    r"hobbies(?:\s*(?:&|and)\s*interests)?|interests(?:\s*(?:&|and)\s*hobbies)?|personal\s+interests|"
    r"volunteer(?:ing|\s+work|\s+experience)?|community\s+(?:work|service|involvement)|social\s+work|"
    r"extra-?curricular(?:\s+activities)?|co-?curricular(?:\s+activities)?|activities(?:\s*(?:&|and)\s*interests)?|"
    r"personal\s+(?:details|information|profile)|about\s+me|other\s+(?:interests|activities)"
    r")\s*[:\-–—]?\s*(?P<rest>.*)$")
_PROG = re.compile(r"(?i)\b(python|java|javascript|typescript|go|golang|rust|c\+\+|c#|\bc\b|ruby|php|scala|kotlin|swift|"
                   r"sql|html|css|bash|shell|r|matlab|perl|haskell|elixir|erlang|clojure|dart|objective-c|solidity|"
                   r"cobol|fortran|vba|lua|groovy|julia|assembly)\b")
_HUMAN = re.compile(r"(?i)\b(english|hindi|telugu|tamil|kannada|malayalam|marathi|bengali|gujarati|punjabi|odia|urdu|"
                    r"assamese|konkani|sanskrit|nepali|sinhala|mandarin|chinese|cantonese|malay|bahasa|tagalog|filipino|"
                    r"thai|vietnamese|japanese|korean|arabic|hebrew|persian|farsi|turkish|french|german|spanish|"
                    r"portuguese|italian|dutch|russian|polish|ukrainian|swedish|norwegian|danish|finnish|greek|"
                    r"swahili|zulu|xhosa|afrikaans|amharic|yoruba|hausa|igbo|native|fluent|mother\s+tongue|bilingual)\b")
_HEADING_LIKE = re.compile(r"^\s*(?:#+\s*)?[A-Z][A-Za-z &/]{1,40}:?\s*$")


def _proxy_sections(text: str, rep: RedactionReport) -> str:
    """Replace proxy sections with a marker that names the kind, never the content."""
    lines = text.split("\n")
    out, i = [], 0
    while i < len(lines):
        m = PROXY_HEAD.match(lines[i])
        if not m:
            out.append(lines[i]); i += 1
            continue
        kind = re.sub(r"\s+", " ", m.group("kind").lower())
        rest = m.group("rest") or ""
        is_lang = kind.startswith(("lang", "spoken", "linguistic"))
        # "Languages: Python, Go" is a skills line and stays. "Languages: Hindi, Telugu" does not.
        if is_lang and rest and _PROG.search(rest) and not _HUMAN.search(rest):
            out.append(lines[i]); i += 1
            continue
        label = ("languages" if is_lang else
                 "volunteering" if kind.startswith(("volunteer", "community", "social")) else
                 "personal" if kind.startswith(("personal", "about")) else "interests")
        out.append(f"[{label.upper()} SECTION REDACTED]")
        rep.add("proxy_" + label, 1)
        i += 1
        if rest.strip():
            continue  # inline values were on the heading line; nothing more to swallow
        # swallow the section body: until a blank line or the next heading-like line
        while i < len(lines) and lines[i].strip() and not _HEADING_LIKE.match(lines[i]) and not PROXY_HEAD.match(lines[i]):
            i += 1
    return "\n".join(out)


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
           institutions: tuple[str, ...] | list[str] = (),
           proxies: bool = True) -> tuple[str, RedactionReport]:
    """Return (redacted_text, report). Deterministic: same input, same output.

    `proxies` removes the sections that leak demographics without naming
    them (languages spoken, hobbies, volunteering, personal details). Keep
    it on. Turn it off only to measure what it was doing.
    """
    rep = RedactionReport()
    t = text or ""
    if proxies:
        t = _proxy_sections(t, rep)
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
