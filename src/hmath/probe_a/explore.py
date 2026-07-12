"""Theory exploration: enumerate -> filter numerically -> prove in rounds."""

from __future__ import annotations

import itertools
import random
import time
from dataclasses import dataclass, field

from .prover import Proof, Theory, normalize, prove
from .terms import (Equation, ONE, OPS, S, Term, X, Y, Z, ZERO, add,
                    canonical_eq, mul, pw, term_key)

AXIOMS: list[tuple[str, Equation]] = [
    ("add_zero", Equation(add(X, ZERO), X)),
    ("add_succ", Equation(add(X, S(Y)), S(add(X, Y)))),
    ("mul_zero", Equation(mul(X, ZERO), ZERO)),
    ("mul_succ", Equation(mul(X, S(Y)), add(mul(X, Y), X))),
    ("pow_zero", Equation(pw(X, ZERO), ONE)),
    ("pow_succ", Equation(pw(X, S(Y)), mul(pw(X, Y), X))),
]


@dataclass
class Config:
    max_term_size: int = 7
    n_tests: int = 14
    test_values: tuple[int, ...] = (0, 1, 2, 3)
    confirm_tests: int = 24
    max_rounds: int = 12
    time_budget_s: float = 300.0
    seed: int = 0


@dataclass
class Result:
    proven: list[tuple[str, Equation, Proof]] = field(default_factory=list)
    n_terms: int = 0
    n_candidates: int = 0
    rounds: int = 0
    wall_s: float = 0.0


def enumerate_terms(max_size: int) -> list[Term]:
    by_size: dict[int, list[Term]] = {1: [ZERO, X, Y, Z]}
    for n in range(2, max_size + 1):
        out = [S(t) for t in by_size[n - 1]]
        for k in range(1, n - 1):
            for a, b in itertools.product(by_size[k], by_size[n - 1 - k]):
                out.extend(Term(op, (a, b)) for op in OPS)
        by_size[n] = out
    return [t for ts in by_size.values() for t in ts]


def fingerprint(t: Term, envs: list[dict[str, int]]) -> tuple[int, ...] | None:
    try:
        return tuple(t.eval(env) for env in envs)
    except OverflowError:
        return None


def candidates(cfg: Config, theory: Theory) -> tuple[list[Equation], int]:
    rng = random.Random(cfg.seed)
    envs = [{v: rng.choice(cfg.test_values) for v in "xyz"}
            for _ in range(cfg.n_tests)]
    confirm = [{v: rng.randint(0, 6) for v in "xyz"}
               for _ in range(cfg.confirm_tests)]

    terms = enumerate_terms(cfg.max_term_size)
    n_terms = len(terms)
    # Keep only axiom-normal forms: reducible terms yield derivable equations.
    terms = [t for t in terms if normalize(t, theory, set()) == t]

    groups: dict[tuple[int, ...], list[Term]] = {}
    for t in terms:
        fp = fingerprint(t, envs)
        if fp is not None:
            groups.setdefault(fp, []).append(t)

    seen: set[Equation] = set()
    out: list[Equation] = []
    for group in groups.values():
        if len(group) < 2:
            continue
        rep = min(group, key=term_key)
        for t in group:
            if t is rep or t.vars() != rep.vars():
                continue
            try:
                if any(t.eval(e) != rep.eval(e) for e in confirm):
                    continue
            except OverflowError:
                continue
            eq = canonical_eq(Equation(t, rep))
            if eq in seen or eq.lhs == eq.rhs:
                continue
            seen.add(eq)
            out.append(eq)
    out.sort(key=lambda e: (e.lhs.size + e.rhs.size, repr(e)))
    return out, n_terms


def explore(cfg: Config) -> Result:
    t0 = time.time()
    theory = Theory(list(AXIOMS))
    res = Result()
    cands, res.n_terms = candidates(cfg, theory)
    res.n_candidates = len(cands)
    pending = list(cands)

    for rnd in range(1, cfg.max_rounds + 1):
        res.rounds = rnd
        progress = False
        still: list[Equation] = []
        for i, eq in enumerate(pending):
            if time.time() - t0 > cfg.time_budget_s:
                still.extend(pending[i:])
                break
            # Already derivable? Skip without naming it a lemma.
            if normalize(eq.lhs, theory, set()) == \
                    normalize(eq.rhs, theory, set()):
                progress = True
                continue
            proof = prove(eq, theory)
            if proof is None:
                still.append(eq)
                continue
            name = f"lemma_{len(res.proven):03d}"
            theory.add(name, eq)
            res.proven.append((name, eq, proof))
            progress = True
        pending = still
        if not progress or not pending or time.time() - t0 > cfg.time_budget_s:
            break

    res.wall_s = time.time() - t0
    return res
