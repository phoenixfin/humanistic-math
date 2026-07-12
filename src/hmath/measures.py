"""Phase 2 — intrinsic significance measures (deterministic, no learning).

Each measure maps every theorem in T to a score where HIGHER = more
significant, yielding a ranking over T. Definitions:

- reuse(t)        = number of distinct theorems whose proof uses t.
- centrality(t)   = PageRank of t in the dependency digraph (edge u -> v when
                    u's proof uses v), i.e. hub-ness under recursive reuse.
- compression(t)  = uses(t) * (|proof(t)| - 1) - |proof(t)| : the corpus-size
                    saving from stating t once instead of inlining its proof
                    at every use site (an MDL-style contribution proxy, with
                    |proof| = distinct logical lemmas referenced).
- surprise(t)     = mean per-token negative log2-likelihood of t's statement
                    under a Laplace-smoothed bigram model fit on the
                    statements of all theorems appearing BEFORE t in database
                    order (deviation from what prior theorems predict).
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict

import networkx as nx

from .substrate import Substrate


def reuse(s: Substrate) -> dict[str, float]:
    counts: dict[str, float] = defaultdict(float)
    for t in s.theorems:
        for d in t.deps:
            counts[d] += 1.0
    return {t.label: counts.get(t.label, 0.0) for t in s.theorems}


def centrality(s: Substrate) -> dict[str, float]:
    g = nx.DiGraph()
    g.add_nodes_from(t.label for t in s.theorems)
    g.add_edges_from((t.label, d) for t in s.theorems for d in t.deps)
    pr = nx.pagerank(g, alpha=0.85)
    return {t.label: pr.get(t.label, 0.0) for t in s.theorems}


def compression(s: Substrate) -> dict[str, float]:
    uses = reuse(s)
    return {t.label: uses[t.label] * (len(t.deps) - 1) - len(t.deps)
            for t in s.theorems}


def surprise(s: Substrate) -> dict[str, float]:
    bigrams: Counter[tuple[str, str]] = Counter()
    unigrams: Counter[str] = Counter()
    vocab: set[str] = set()
    scores: dict[str, float] = {}
    for t in sorted(s.theorems, key=lambda t: t.index):
        toks = t.statement.split()
        v = len(vocab) + 1
        nll = 0.0
        for prev, cur in zip(["<s>"] + toks, toks + ["</s>"]):
            p = (bigrams[(prev, cur)] + 1) / (unigrams[prev] + v)
            nll -= math.log2(p)
        scores[t.label] = nll / (len(toks) + 1)
        for prev, cur in zip(["<s>"] + toks, toks + ["</s>"]):
            bigrams[(prev, cur)] += 1
            unigrams[prev] += 1
        vocab.update(toks)
    return scores


ALL = {
    "reuse": reuse,
    "centrality": centrality,
    "compression": compression,
    "surprise": surprise,
}


def compute_all(s: Substrate) -> dict[str, dict[str, float]]:
    return {name: fn(s) for name, fn in ALL.items()}
