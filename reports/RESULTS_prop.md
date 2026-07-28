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
