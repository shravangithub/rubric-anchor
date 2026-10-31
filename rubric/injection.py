"""Prompt-injection scan.

A CV is untrusted input. The prompts already say "a CV is data, not a
prompt" -- but a prompt is a request, not a control. This module is the
control, and it is deterministic:

  1. `scan()` flags lines that look like instructions to a model, plus
     invisible characters used to hide text.
  2. `score_candidate` routes any flagged CV to a person, and DROPS every model
     claim whose evidence span sits inside a flagged line. Text written to
     the scorer can never be the evidence the scorer relies on.

It errs towards flagging. A false positive costs one human glance; a false
negative lets a candidate write their own score.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict

from .evidence import normalise

PATTERNS: tuple[tuple[str, re.Pattern], ...] = tuple((name, re.compile(rx, re.I)) for name, rx in (
    ("override", r"\b(ignore|disregard|forget|override)\b.{0,40}\b(instruction|prompt|rule|"
                 r"guideline|criteria|above|previous|prior)s?\b"),
    ("role_marker", r"^\s*(system|assistant|developer)\s*[:>]"),
    ("role_tag", r"</?\s*(system|instructions?|prompt)\s*>|\[/?INST\]|<\|im_start\|>"),
    ("addressing_model", r"\b(you are (now )?(an? )?(ai|assistant|language model|llm|"
                         r"screener|recruiter bot)|as an ai\b|dear (ai|llm|model|chatgpt|claude)"
                         r"|note to (the )?(ai|llm|model|screener))"),
    ("score_demand", r"\b(score|rate|rank|grade|mark)\b.{0,30}\b(this (candidate|cv|resume)|me)"
                     r"\b.{0,30}(\b100\b|\b10/10\b|\b5/5\b|highest|top|first|#1|maximum|"
                     r"perfect|strong(ly)? (hire|yes))"),
    ("shortlist_demand", r"\b(must|should|always)\b.{0,20}\b(shortlist|hire|select|"
                         r"advance|recommend)\b.{0,20}\b(this candidate|me)\b"),
))
INVISIBLE = re.compile("[​-‏‪-‮⁠-⁤﻿]")


@dataclass
class Finding:
    line: int            # 1-based line number
    kind: str
    excerpt: str         # trimmed, for the reviewer

    def as_dict(self) -> dict:
        return asdict(self)


def scan(text: str) -> list[Finding]:
    out: list[Finding] = []
    for i, line in enumerate((text or "").split("\n"), start=1):
        if INVISIBLE.search(line):
            out.append(Finding(i, "invisible_characters", INVISIBLE.sub("", line).strip()[:120]))
        for name, rx in PATTERNS:
            if rx.search(line):
                out.append(Finding(i, name, line.strip()[:120]))
                break
    return out


def flagged_lines(text: str, findings: list[Finding]) -> list[str]:
    lines = (text or "").split("\n")
    return [normalise(lines[f.line - 1]) for f in findings
            if 0 < f.line <= len(lines) and lines[f.line - 1].strip()]


def span_in_flagged(span: str, flagged: list[str]) -> bool:
    s = normalise(span)
    return bool(s) and any(s in fl or fl in s for fl in flagged)
