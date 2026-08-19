"""TalentRubric Rank -- absolute, evidence-anchored resume scoring.

    from rubric import score_candidate, NullExtractor, Graph, parameters

Principles, all enforced by tests in tests/:
  * 50 parameters, each scored on ONE candidate in isolation
  * anything computable is computed in code, never by a model
  * every model claim carries a verbatim span, checked by substring
  * only bona-fide gates may auto-reject; everything else goes to a human
  * protected attributes raise, they do not warn
"""
from .parameters import ALL, GATES, SCORED, FAMILIES, BY_KEY, BLOCKED, Parameter
from .scoring import score_candidate, Result
from .extractors import NullExtractor, Extractor
from .evidence import Claim, verify, anchored
from .graph import Graph
from .audit import orderings, analyse, report, AuditResult
from .guards import ProtectedAttributeError, ComparativeScoringError

__version__ = "0.1.0"
__all__ = ["ALL","GATES","SCORED","FAMILIES","BY_KEY","BLOCKED","Parameter",
           "score_candidate","Result","NullExtractor","Extractor","Claim",
           "verify","anchored","Graph","orderings","analyse","report",
           "AuditResult","ProtectedAttributeError","ComparativeScoringError"]
