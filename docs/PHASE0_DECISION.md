# Phase 0 Decision — Derivation Source

**Decision: Branch B — import an existing library, instantiated with Metamath
`set.mm`.** Branch A is kept as a working artifact (`src/hmath/probe_a/`) for
a possible controlled-substrate complement, but it is not the project's
theorem source.

## Probe A — self-enumerate a bounded Peano fragment

A QuickSpec-style theory explorer over quantifier-free equational Peano
(0, S, +, ·, ^): enumerate terms, numerically filter candidate equations,
prove survivors by LPO-ordered rewriting plus one-variable structural
induction, feed proven lemmas back as rewrite rules.

- Runs (size-cap 7, i.e. 60,460 terms, 5,197 surviving candidate equations):
  **5 min budget → 121 equations proven, 4/17 named identities reached**
  (add_zero_left, succ_add, add_assoc, one_mul); **20 min budget → 136
  proven, still 4/17**, without completing even one exploration round.
  Compute scales badly: every proven lemma enlarges the rewrite theory, so
  each later proof attempt gets more expensive (~superlinear in theory
  size).
- The deeper constraint is **expressiveness**: the
  recognizably-named theorems reachable in an equational fragment top out at
  ~17 non-axiom identities (commutativity/associativity/distributivity and
  the power laws) + 6 defining axioms — under the roadmap's ≥ 30–50
  criterion *by construction*. Landmarks like the division algorithm,
  infinitude of primes, or unique factorization need inequalities,
  divisibility, and quantifiers — each a major prover investment (the
  predecessor project's central lesson).

**Verdict: fails the Phase 0 criterion.**

## Probe B — import an existing library

Lean mathlib and Isabelle/AFP both require a heavy toolchain (hours of
build; extraction engineering) to expose theorem-level dependency edges.
**Metamath `set.mm`** delivers the same scientific object — a large,
human-curated theorem library with exact per-proof dependency edges — as a
single 49 MB text file:

- Parses in **1.5 s** (`src/hmath/metamath.py`): 50,461 assertions,
  47,463 proven theorems, 1.5 M proof-reference edges.
- After restricting to logical (`|-`) statements and deduplicating up to
  variable renaming: **38,928 theorems, 639,632 logical dependency edges**.
- Contains an in-file external landmark signal: 72 theorems in T flagged as
  entries of the "Formalizing 100 Theorems" list ("Metamath 100"), spanning
  √2 ∉ ℚ, Cantor, infinitude of primes, etc. — usable ground truth for
  RQ1–RQ3 *before* (and alongside) our own graded labels.

**Verdict: passes with headroom.**

## The confound, addressed

The roadmap flags Branch B's risk: dependency edges reflect *library
authoring choices*, entangling structure with taste. Mitigations now built
in:

1. The RQ1 ablation explicitly separates a **cultural** feature family
   (comment length, restatement count, database position) from intrinsic
   families (statement shape, proof shape, graph position, surprise) — so
   "authoring signal" is measured, not ignored.
2. Landmark markers ("Metamath 100" mentions) are stripped from any text
   shown to models or labelers.
3. Probe A's enumerator remains available to regenerate a small
   *authoring-free* substrate as a robustness check later.
4. A second real (not self-enumerated) starter substrate is available:
   `variant="prop"` filters `set.mm` down to its propositional-calculus
   theorems only (no quantifiers/sets/classes) — 1,036 theorems, 20 axiom
   roots, 2,976 dependency edges. Same real proofs and dependency edges as
   the full library, just a smaller and simpler slice; useful for fast
   pipeline iteration and quick manual labeling, though it carries **zero**
   Metamath-100 landmark flags (see `docs/LABELING.md`).

## Roadmap open items resolved

- **Derivation source** → Branch B via Metamath `set.mm` (this document).
- **Significance scale** → 0–3, anchors in `docs/LABELING.md`.
- **Label volume & labelers** → 100 theorems, single labeler first,
  second-labeler workflow reserved (`labels_filled_2.csv`).
- **Intrinsic measures shortlist** → reuse, PageRank centrality, MDL-style
  compression, bigram surprise (exact definitions in
  `src/hmath/measures.py`).
