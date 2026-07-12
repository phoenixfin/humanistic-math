"""Terms and equations of the bounded quantifier-free Peano fragment.

Language: constant 0, successor S, binary + * ^, variables x y z.
"""

from __future__ import annotations

from dataclasses import dataclass

OPS = ("+", "*", "^")


@dataclass(frozen=True, slots=True)
class Term:
    op: str                      # "0", "var", "S", or one of OPS
    args: tuple["Term", ...] = ()
    name: str = ""               # variable name when op == "var"

    def __repr__(self) -> str:
        if self.op == "var":
            return self.name
        if self.op == "S":
            return f"S({self.args[0]!r})"
        if not self.args:            # "0" and frozen induction constants
            return self.op
        return f"({self.args[0]!r} {self.op} {self.args[1]!r})"

    @property
    def size(self) -> int:
        return 1 + sum(a.size for a in self.args)

    def vars(self) -> frozenset[str]:
        if self.op == "var":
            return frozenset((self.name,))
        return frozenset().union(*(a.vars() for a in self.args)) \
            if self.args else frozenset()

    def subst(self, mapping: dict[str, "Term"]) -> "Term":
        if self.op == "var":
            return mapping.get(self.name, self)
        if not self.args:
            return self
        return Term(self.op, tuple(a.subst(mapping) for a in self.args))

    def eval(self, env: dict[str, int], cap: int = 10**60) -> int:
        if self.op == "0":
            return 0
        if self.op == "var":
            return env[self.name]
        if self.op == "S":
            return self.args[0].eval(env, cap) + 1
        a, b = (x.eval(env, cap) for x in self.args)
        if self.op == "+":
            v = a + b
        elif self.op == "*":
            v = a * b
        else:
            if b * max(a.bit_length(), 1) > 200:      # would exceed any cap
                raise OverflowError
            v = a ** b
        if v > cap:
            raise OverflowError
        return v


ZERO = Term("0")
X, Y, Z = (Term("var", name=n) for n in "xyz")


def S(t: Term) -> Term:
    return Term("S", (t,))


def add(a: Term, b: Term) -> Term:
    return Term("+", (a, b))


def mul(a: Term, b: Term) -> Term:
    return Term("*", (a, b))


def pw(a: Term, b: Term) -> Term:
    return Term("^", (a, b))


ONE = S(ZERO)


@dataclass(frozen=True, slots=True)
class Equation:
    lhs: Term
    rhs: Term

    def __repr__(self) -> str:
        return f"{self.lhs!r} = {self.rhs!r}"

    def vars(self) -> frozenset[str]:
        return self.lhs.vars() | self.rhs.vars()

    def subst(self, mapping: dict[str, Term]) -> "Equation":
        return Equation(self.lhs.subst(mapping), self.rhs.subst(mapping))


def _rename(t: Term, mapping: dict[str, str]) -> Term:
    if t.op == "var":
        if t.name not in mapping:
            mapping[t.name] = f"v{len(mapping)}"
        return Term("var", name=mapping[t.name])
    if not t.args:
        return t
    return Term(t.op, tuple(_rename(a, mapping) for a in t.args))


def term_key(t: Term) -> tuple[int, str]:
    return (t.size, repr(t))


def canonical_eq(eq: Equation) -> Equation:
    """Normalize an equation up to variable renaming and symmetry of '='."""
    best = None
    for lhs, rhs in ((eq.lhs, eq.rhs), (eq.rhs, eq.lhs)):
        m: dict[str, str] = {}
        c = Equation(_rename(lhs, m), _rename(rhs, m))
        k = (term_key(c.lhs), term_key(c.rhs))
        if best is None or k < best[0]:
            best = (k, c)
    return best[1]
