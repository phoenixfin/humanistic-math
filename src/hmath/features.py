"""Phase 3 — per-theorem features, grouped into families for the RQ1 ablation.

Families:
- statement : intrinsic properties of the statement text alone.
- proof     : local properties of the proof object.
- graph     : global position in the dependency DAG (includes the Phase-2
              graph measures).
- surprise  : the Phase-2 novelty measure (statement vs. prior corpus).
- cultural  : human-authoring traces that are NOT mathematical structure —
              comment length, restatement count, position in the library.
              (Metamath-100 mentions are stripped from comments first, since
              they are the RQ2 target.)

"Intrinsic" = statement + proof + graph + surprise.
"""

from __future__ import annotations

import re

import numpy as np

from .substrate import Substrate

QUANTIFIERS = {"A.", "E.", "E!", "E*"}


def clean_comment(comment: str) -> str:
    return re.sub(r"[^.]*Metamath 100[^.]*\.", "", comment)


def heights(s: Substrate) -> dict[str, int]:
    h: dict[str, int] = {a.label: 0 for a in s.axioms}
    for t in s.theorems:  # deps always precede, so one pass suffices
        h[t.label] = 1 + max((h.get(d, 0) for d in t.deps), default=0)
    return h


def compute(s: Substrate, measures: dict[str, dict[str, float]]
            ) -> tuple[np.ndarray, list[str], dict[str, list[int]], list[str]]:
    """Returns (X, feature_names, family -> column indices, theorem labels)."""
    ht = heights(s)
    n_t = len(s.theorems)

    names: list[str] = []
    families: dict[str, list[int]] = {}
    columns: list[list[float]] = []

    def add(family: str, name: str, values: list[float]) -> None:
        families.setdefault(family, []).append(len(names))
        names.append(name)
        columns.append(values)

    toks = [t.statement.split() for t in s.theorems]
    add("statement", "stmt_len", [float(len(tk)) for tk in toks])
    add("statement", "stmt_distinct", [float(len(set(tk))) for tk in toks])
    add("statement", "stmt_distinct_ratio",
        [len(set(tk)) / len(tk) for tk in toks])
    add("statement", "stmt_quantifiers",
        [float(sum(x in QUANTIFIERS for x in tk)) for tk in toks])
    for sym in ("->", "<->", "=", "e.", "C_", "(", ","):
        add("statement", f"stmt_n_{sym}",
            [float(tk.count(sym)) for tk in toks])

    add("proof", "n_deps", [float(len(t.deps)) for t in s.theorems])
    add("proof", "proof_size", [float(t.proof_size) for t in s.theorems])
    add("proof", "height", [float(ht[t.label]) for t in s.theorems])

    for m in ("reuse", "centrality", "compression"):
        add("graph", m, [measures[m][t.label] for t in s.theorems])
    add("surprise", "surprise", [measures["surprise"][t.label]
                                 for t in s.theorems])

    add("cultural", "comment_words",
        [float(len(clean_comment(t.comment).split())) for t in s.theorems])
    add("cultural", "n_restatements",
        [float(t.n_restatements) for t in s.theorems])
    add("cultural", "position", [t.index / n_t for t in s.theorems])

    X = np.array(columns, dtype=float).T
    return X, names, families, [t.label for t in s.theorems]


INTRINSIC = ("statement", "proof", "graph", "surprise")
