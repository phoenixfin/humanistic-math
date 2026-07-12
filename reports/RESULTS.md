# Results

Theorem set: **38928** deduplicated theorems; landmark signal: **72** Metamath-100 entries.

## RQ2 — Is taste learnable? (landmark signal)

Gradient-boosted trees on intrinsic features only, 5-fold CV: **ROC-AUC 0.859**, average precision 0.051 (base rate 72/38928).

## RQ1 — Structure vs. taste (feature-family ablation)

| feature set | ROC-AUC | avg. precision |
|---|---|---|
| only_statement | 0.655 | 0.011 |
| only_proof | 0.854 | 0.011 |
| only_graph | 0.676 | 0.010 |
| only_surprise | 0.536 | 0.002 |
| only_cultural | 0.839 | 0.022 |
| intrinsic_all | 0.859 | 0.051 |
| all_features | 0.921 | 0.133 |
| intrinsic_minus_statement | 0.829 | 0.038 |
| intrinsic_minus_proof | 0.716 | 0.037 |
| intrinsic_minus_graph | 0.866 | 0.063 |
| intrinsic_minus_surprise | 0.839 | 0.052 |

## RQ3 — Do independent measures converge?

Pairwise rank agreement (all of T):

| pair | Spearman | Kendall |
|---|---|---|
| centrality~compression | 0.808 | 0.639 |
| centrality~reuse | 0.885 | 0.752 |
| centrality~surprise | -0.142 | -0.097 |
| compression~reuse | 0.939 | 0.822 |
| compression~surprise | -0.133 | -0.092 |
| reuse~surprise | -0.176 | -0.127 |

Each measure vs. the landmark set:

| measure | ROC-AUC | mean landmark percentile |
|---|---|---|
| centrality | 0.283 | 0.305 |
| compression | 0.339 | 0.342 |
| reuse | 0.332 | 0.325 |
| surprise | 0.494 | 0.494 |
