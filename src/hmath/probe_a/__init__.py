"""Probe A: self-enumeration of a bounded quantifier-free equational Peano fragment.

Feasibility probe for ROADMAP Phase 0 / Branch A.  A small theory-exploration
prover (QuickSpec/Hipster-style): enumerate candidate equations over 0, S, +, *, ^,
filter them numerically, prove survivors by ordered rewriting + one-variable
structural induction, and feed proven lemmas back as rewrite rules in rounds.
"""

from .terms import Term, Equation, ZERO, ONE, X, Y, Z, S, add, mul, pw, canonical_eq
from .prover import Theory, Proof, prove
from .explore import Config, AXIOMS, explore

__all__ = [
    "Term", "Equation", "ZERO", "ONE", "X", "Y", "Z", "S", "add", "mul", "pw",
    "canonical_eq", "Theory", "Proof", "prove", "Config", "AXIOMS", "explore",
]
