# Results

Theorem set: **1036** deduplicated theorems; landmark signal: **0** Metamath-100 entries.

## RQ1/RQ2 — landmark-signal experiments skipped

only 0 Metamath-100 landmarks in this substrate — too few for the 5-fold CV selector/ablation; skipped. Rely on human labels instead.

## RQ3 — Do independent measures converge?

Pairwise rank agreement (all of T):

| pair | Spearman | Kendall |
|---|---|---|
| centrality~compression | 0.908 | 0.796 |
| centrality~reuse | 0.984 | 0.923 |
| centrality~surprise | -0.122 | -0.088 |
| compression~reuse | 0.927 | 0.860 |
| compression~surprise | -0.084 | -0.059 |
| reuse~surprise | -0.124 | -0.093 |

## Human-label readouts

Labeled sample: 100 theorems, grade counts {0: 51, 1: 28, 2: 19, 3: 2}.

RQ2 (intrinsic features -> grade, leave-one-out): Spearman **0.510**

RQ1 ablation (Spearman by family):

- only_statement: 0.430
- only_proof: 0.063
- only_graph: 0.338
- only_surprise: -0.155
- only_cultural: 0.458

RQ3 measures vs. human grades:

- centrality: Spearman 0.371, Kendall 0.313
- compression: Spearman 0.384, Kendall 0.310
- reuse: Spearman 0.398, Kendall 0.333
- surprise: Spearman -0.084, Kendall -0.063
