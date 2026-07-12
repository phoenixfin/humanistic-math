# Humanistic Mathematics — Roadmap

Fresh design around one pipeline: **enumerate → label → measure → select → converge**.
RL is not part of the core; generation is enumeration/search, and the science lives in
selection.

---

## Phase 0 — Derivation Source Decision (fork)

The whole project reads from a **theorem set `T`** plus a **dependency DAG** (node =
theorem, edge = "used as a lemma in the proof of"). How we obtain these forks the plan.

### Branch A — Self-enumerate a bounded Peano fragment
Generate `T` ourselves by forward-saturating a restricted system (e.g. quantifier-free
or bounded-quantifier Peano, with a controlled induction schema).

- **Unlocks:** full control over axioms, proof objects, and the dependency edges (we
  know exactly why each theorem was derived).
- **Cost/risk:** enumeration may be intractable at useful depth; induction-schema
  handling is the hard part; landmarks may stay thin if the fragment is too weak.

### Branch B — Import an existing library
Use Lean `mathlib` or Isabelle as the theorem set + dependency graph.

- **Unlocks:** real, rich, human-curated theorems and a real dependency graph *for
  free*; sidesteps the prover bottleneck entirely.
- **Cost/risk:** dependency edges reflect *library structure* (human authoring choices),
  which subtly entangles "structure" with "taste" — a confound to control for in RQ1;
  parsing/extraction engineering.

### Decision criteria
- Can Branch A reach ≥ ~30–50 recognizably-named theorems at feasible compute?
- Does Branch B's dependency graph expose enough intrinsic structure independent of
  human authoring order?
- **Deliverable of Phase 0:** a small feasibility probe on each branch, then commit.

---

## Phase 1 — Shared Substrate

Built regardless of branch.

- **Theorem set `T`** — canonicalized, deduplicated (alpha/structural equivalence).
- **Dependency DAG** — the raw material all experiments read.
- **Significance labels** — human ground truth.
  - Draft scale (0–3): `0` mechanical/trivial · `1` minor lemma · `2` named/reusable
    result · `3` landmark. *(anchors tunable)*
  - Target: ~50–100 labeled theorems. *(volume open)*
  - Single vs. multiple labelers (for inter-rater agreement). *(open)*

---

## Phase 2 — Intrinsic Measures (deterministic, no learning)

Unsupervised significance scorers over `T` / the DAG:

- **Compression / MDL** — does the theorem shorten future proofs?
- **Centrality** — DAG hub-ness (e.g. PageRank on dependencies).
- **Reuse frequency** — how often invoked as a lemma across the set.
- **Surprise** — deviation from what prior theorems predict. *(exact defs TBD)*

Each yields a ranking over `T`. Python, standard graph/compression libs.

---

## Phase 3 — The Three Experiments

- **RQ2 — Is taste learnable?**
  Selector predicts human-significance from **structural features only**, evaluated on
  **held-out** theorems (AUC / rank correlation). Model: TF MLP or gradient-boosted trees.
- **RQ1 — Structure vs. taste.**
  Feature-family ablation on the RQ2 selector. Intrinsic-only features predictive →
  discovered; only human-fitted features work → invented.
- **RQ3 — Do independent measures converge?**
  Mutual agreement among Phase-2 rankings, and their agreement with human labels
  (Kendall-τ / Spearman).

---

## Phase 4 — Readout & Interpretation

Map outcomes to the philosophical claim:

- Intrinsic measures agree with each other **and** with human landmarks → strong
  **discovered** signal (landmarks forced by structure).
- Only supervised, human-fitted features predict significance → **invented** signal
  (landmarks reflect us).
- Mixed → a decomposition of *which* aspects of significance are structural vs. cultural.

---

## Carried-Forward Open Items

All resolved 2026-07-13 (details in [docs/PHASE0_DECISION.md](docs/PHASE0_DECISION.md)):

- **[RESOLVED] Derivation source** — Branch B via Metamath `set.mm` (mathlib/
  Isabelle need a heavy toolchain; set.mm gives the same theorem-set + exact
  dependency DAG as one parseable file, plus in-file landmark flags).
- **[RESOLVED] Significance scale** — 0–3, anchors in [docs/LABELING.md](docs/LABELING.md).
- **[RESOLVED] Label volume & labelers** — 100 theorems, single labeler first;
  second-labeler CSV workflow reserved for inter-rater agreement.
- **[RESOLVED] Intrinsic measures shortlist** — reuse, PageRank centrality,
  MDL-style compression, bigram surprise (`src/hmath/measures.py`).
- **[OPEN] Human labels** — `data/labels/label_sample.csv` awaits grading;
  experiments re-run automatically once `labels_filled.csv` exists.

---

## Notes on Scope

- **No RL in the core.** If used later, it is a downstream consumer guided by the
  selector, never the object under test.
- **Not bound to v3/v4 code.** Reuse `formula.py`/graph utilities only if convenient.
- Full "rebuild mathematics" remains out of scope; the target is a bounded fragment plus
  a sharp selection experiment.
