# Phase 4 Readout — What the Experiments Say (landmark-signal run, 2026-07-13)

Substrate: 38,928 deduplicated `|-` theorems from Metamath `set.mm`,
639,632 logical dependency edges. Significance signal for this run:
membership in the "Formalizing 100 Theorems" list (72 theorems in T).
Numbers in `reports/results.json`; the human-label rerun (see
`docs/LABELING.md`) will add the graded-significance readouts.

## RQ2 — Is taste learnable? **Largely yes.**

A gradient-boosted selector using *intrinsic features only* (statement
shape, proof shape, DAG position, surprise) identifies landmark theorems on
held-out data at **ROC-AUC 0.859**, average precision 0.051 against a base
rate of 0.0018 (~28× lift). Whatever humans are doing when they crown a
landmark, a large part of it is recoverable from structure alone.

## RQ1 — Structure vs. taste: **structure ≈ culture, and they add.**

| feature family | ROC-AUC |
|---|---|
| proof shape only (size, height, breadth) | **0.854** |
| cultural only (comment length, restatements, position) | 0.839 |
| graph position only | 0.676 |
| statement shape only | 0.655 |
| surprise only | 0.536 |
| all intrinsic | 0.859 |
| everything | **0.921** |

Intrinsic features match the cultural ones; neither subsumes the other
(combining lifts AUC to 0.92). On the roadmap's dichotomy this is the
**mixed** outcome — but with a sharp decomposition (below).

## RQ3 — Do independent measures converge? **Yes — on the *wrong* thing.**

Reuse, centrality, and compression agree strongly with each other
(Spearman 0.81–0.94): there is a robust, convergently-measurable structural
notion of importance. But it **anti-predicts** landmarks (AUC 0.28–0.34;
landmarks sit around the 30th percentile of these rankings). Surprise is
orthogonal to everything (≈0.49 vs landmarks).

## Interpretation

Mathematical significance appears to **decompose into two structural
species**:

1. **Infrastructure significance** — the hub lemmas (`a1i`, `imp`, `id`)
   that reuse, centrality, and compression convergently crown. Fully
   "discovered" in the roadmap's sense: three independent measures agree.
   Humans do not celebrate these theorems; nobody names a lecture hall
   after modus-ponens-with-a-hypothesis.
2. **Summit significance** — what humans call landmarks. These are *not*
   hubs: they are terminal peaks with deep, large proofs and little reuse.
   Crucially, they are still structurally visible — proof depth/size alone
   finds them at AUC 0.85 — so landmark-ness is not arbitrary taste either.

So: *neither* pure "discovered" (the unsupervised measures do not converge
on human landmarks) *nor* pure "invented" (structure alone predicts
landmarks nearly as well as human-authoring traces, and far above chance).
The landmark set looks like a structurally-constrained choice: mathematics
supplies the summits, humans choose which summits to name — and the
residual ~0.06 AUC that cultural features add over intrinsic ones is a
first quantitative estimate of that human residue.

## Caveats

- The landmark signal (Metamath 100) is itself a human-curated list — by
  design (it *is* the taste being probed), but n=72 positives is thin;
  the graded 0–3 human labels on the 100-theorem sample will test whether
  the same decomposition holds off the landmark extreme.
- Dependency edges come from proof label references in one library;
  set.mm's authoring conventions (many micro-lemmas) shape proof-size
  statistics.
- The cultural family is a proxy for authoring signal, not a measurement of
  mathematical culture at large.
