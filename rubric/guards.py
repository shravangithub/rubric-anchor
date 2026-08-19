"""Runtime guards. These raise rather than warn -- a compliance control that
can be ignored is not a control."""
from __future__ import annotations
import re
from .parameters import BLOCKED


class ProtectedAttributeError(RuntimeError):
    """Raised when a protected attribute reaches a scoring path."""


class ComparativeScoringError(RuntimeError):
    """Raised when a scorer is handed more than one candidate."""


_WORD = re.compile(r"[a-z_]+")


def assert_no_protected_attributes(payload: dict, where: str = "") -> None:
    """Refuse any structure whose keys name a protected attribute."""
    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                kk = "_".join(_WORD.findall(str(k).lower()))
                for bad in BLOCKED:
                    if bad == kk or kk.endswith("_" + bad) or kk.startswith(bad + "_"):
                        raise ProtectedAttributeError(
                            f"protected attribute '{k}' reached {where or 'scoring'} "
                            f"at {path or '<root>'}. Remove it upstream; it must never "
                            f"be extracted, stored, or scored.")
                walk(v, f"{path}.{k}")
        elif isinstance(o, (list, tuple)):
            for i, v in enumerate(o):
                walk(v, f"{path}[{i}]")
    walk(payload)


def assert_single_candidate(candidates) -> None:
    """A scorer must never see the pile. Absolute scoring or nothing."""
    n = 1 if isinstance(candidates, (str, dict)) else len(candidates)
    if n != 1:
        raise ComparativeScoringError(
            f"a scorer was handed {n} candidates. Every parameter in this "
            f"system is scored on ONE candidate in isolation -- that is what "
            f"makes the score a property of the person rather than of the batch.")
