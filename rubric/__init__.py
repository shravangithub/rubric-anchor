"""TalentRubric Rank -- absolute, evidence-anchored resume scoring.

    from rubric import score_candidate, NullExtractor, Graph, parameters

Principles, all enforced by tests in tests/:
  * 50 parameters, each scored on ONE candidate in isolation
  * anything computable is computed in code, never by a model
  * every model claim carries a verbatim span, checked by substring
  * only bona-fide gates may PROPOSE a rejection, and a person confirms it
  * unknown is not a fail: a fact the CV does not state is asked, not assumed
  * the model sees redacted text; claims quoting suspected injection are dropped
  * protected attributes raise, they do not warn
"""
from .parameters import ALL, GATES, SCORED, FAMILIES, BY_KEY, BLOCKED, Parameter
from .scoring import score_candidate, Result
from .extractors import NullExtractor, Extractor
from .evidence import Claim, verify, anchored
from .graph import Graph
from .audit import orderings, analyse, report, AuditResult
from .guards import ProtectedAttributeError, ComparativeScoringError
from .redact import redact
from .injection import scan
from .stability import score_repeated, bands, Stability
from .counterfactual import swap_test, replace, PRONOUN_SWAP
from .notice import candidate_notice, questions_for
from ._version import __version__
__all__ = ["ALL","GATES","SCORED","FAMILIES","BY_KEY","BLOCKED","Parameter",
           "score_candidate","Result","NullExtractor","Extractor","Claim",
           "verify","anchored","Graph","orderings","analyse","report",
           "AuditResult","ProtectedAttributeError","ComparativeScoringError",
           "redact","scan","score_repeated","bands","Stability","swap_test",
           "replace","PRONOUN_SWAP","candidate_notice","questions_for",
           "__version__"]
