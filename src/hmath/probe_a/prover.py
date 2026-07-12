"""Ordered rewriting + one-variable structural induction.

Every known equation is usable in both directions, but an instance is only
applied when it strictly decreases a lexicographic path order (LPO) with
total precedence  ^ > * > + > S > variables/constants > 0.  Under this order
all six defining Peano axioms orient left-to-right, and commutativity-like
equations act as argument-sorting rules (classic ordered rewriting), so
rewriting terminates; a global step cap backstops it regardless.

Variable names are compared as constants — that loses stability under
substitution (irrelevant here: we only ever rewrite concrete goal terms) but
makes the order total, so every equation instance is usable in exactly the
decreasing direction.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .terms import Equation, S, Term, ZERO

_PREC = {"^": (9,), "*": (8,), "+": (7,), "S": (6,), "0": (0,)}


def _prec(t: Term) -> tuple:
    if t.op == "var":
        return (1, t.name)
    return _PREC.get(t.op, (1, t.op))     # frozen constants rank with vars


def lpo_gt(s: Term, t: Term) -> bool:
    """s > t in the lexicographic path order."""
    if s == t:
        return False
    if any(a == t or lpo_gt(a, t) for a in s.args):        # subterm case
        return True
    ps, pt = _prec(s), _prec(t)
    if ps > pt:
        return all(lpo_gt(s, b) for b in t.args)
    if ps == pt and len(s.args) == len(t.args) and s.args:
        for a, b in zip(s.args, t.args):                    # lex on args
            if a == b:
                continue
            return lpo_gt(a, b) and all(lpo_gt(s, x) for x in t.args)
    return False


def decreases(frm: Term, to: Term) -> bool:
    return lpo_gt(frm, to)


@dataclass
class Theory:
    equations: list[tuple[str, Equation]] = field(default_factory=list)

    def add(self, name: str, eq: Equation) -> None:
        self.equations.append((name, eq))


@dataclass
class Proof:
    method: str                  # "rewrite" or "induction on <v>"
    used: set[str]               # names of axioms/lemmas applied


def match(pattern: Term, term: Term, sub: dict[str, Term]) -> bool:
    if pattern.op == "var":
        bound = sub.get(pattern.name)
        if bound is None:
            sub[pattern.name] = term
            return True
        return bound == term
    if pattern.op != term.op or len(pattern.args) != len(term.args):
        return False
    return all(match(p, t, sub) for p, t in zip(pattern.args, term.args))


def _rewrite_here(t: Term, theory: Theory, used: set[str]) -> Term | None:
    for name, eq in theory.equations:
        for lhs, rhs in ((eq.lhs, eq.rhs), (eq.rhs, eq.lhs)):
            sub: dict[str, Term] = {}
            if match(lhs, t, sub) and lhs.vars() >= rhs.vars():
                out = rhs.subst(sub)
                if decreases(t, out):
                    used.add(name)
                    return out
    return None


def _rewrite_step(t: Term, theory: Theory, used: set[str]) -> Term | None:
    here = _rewrite_here(t, theory, used)
    if here is not None:
        return here
    for i, a in enumerate(t.args):
        na = _rewrite_step(a, theory, used)
        if na is not None:
            args = list(t.args)
            args[i] = na
            return Term(t.op, tuple(args), t.name)
    return None


def normalize(t: Term, theory: Theory, used: set[str],
              cap: int = 400) -> Term:
    for _ in range(cap):
        nt = _rewrite_step(t, theory, used)
        if nt is None:
            return t
        t = nt
    return t


def _rewrites(t: Term, theory: Theory) -> list[tuple[Term, str]]:
    """All single-step decreasing rewrites of t, at any position."""
    out: list[tuple[Term, str]] = []
    for name, eq in theory.equations:
        for lhs, rhs in ((eq.lhs, eq.rhs), (eq.rhs, eq.lhs)):
            sub: dict[str, Term] = {}
            if match(lhs, t, sub) and lhs.vars() >= rhs.vars():
                nt = rhs.subst(sub)
                if decreases(t, nt):
                    out.append((nt, name))
    for i, a in enumerate(t.args):
        for na, name in _rewrites(a, theory):
            args = list(t.args)
            args[i] = na
            out.append((Term(t.op, tuple(args), t.name), name))
    return out


def _reach(t: Term, theory: Theory, cap: int) -> dict[Term, set[str]]:
    """Terms reachable from t by decreasing rewrites -> rules used en route."""
    seen: dict[Term, set[str]] = {t: set()}
    frontier = [t]
    while frontier and len(seen) < cap:
        cur = frontier.pop()
        for nt, name in _rewrites(cur, theory):
            if nt not in seen:
                seen[nt] = seen[cur] | {name}
                frontier.append(nt)
    return seen


def joinable(eq: Equation, theory: Theory, used: set[str],
             cap: int = 150) -> bool:
    # Cheap deterministic pass first; ordered rewriting is not confluent, so
    # fall back to a bounded search over all decreasing rewrite sequences.
    u: set[str] = set()
    if normalize(eq.lhs, theory, u) == normalize(eq.rhs, theory, u):
        used |= u
        return True
    left = _reach(eq.lhs, theory, cap)
    right = _reach(eq.rhs, theory, cap)
    common = set(left) & set(right)
    if not common:
        return False
    w = min(common, key=lambda x: len(left[x]) + len(right[x]))
    used |= left[w] | right[w]
    return True


def prove(eq: Equation, theory: Theory) -> Proof | None:
    used: set[str] = set()
    if joinable(eq, theory, used):
        return Proof("rewrite", used)

    for v in sorted(eq.vars()):
        used = set()
        base = eq.subst({v: ZERO})
        if not joinable(base, theory, used):
            continue
        # Freeze the induction variable as the constant "c": the hypothesis
        # holds for c only (other variables stay universally quantified),
        # and the step goal is the equation at S(c).
        c = Term("c")
        step_theory = Theory(theory.equations + [("IH", eq.subst({v: c}))])
        step = eq.subst({v: S(c)})
        if joinable(step, step_theory, used):
            used.discard("IH")
            return Proof(f"induction on {v}", used)
    return None
