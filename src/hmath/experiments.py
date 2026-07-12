"""Phase 3 — the three experiments.

RQ2  Is taste learnable?   Gradient-boosted trees predict significance from
     structural features only, evaluated on held-out theorems (5-fold CV).
RQ1  Structure vs. taste.  Feature-family ablation of the RQ2 selector.
RQ3  Do measures converge? Pairwise rank agreement among the Phase-2
     measures, and each measure's agreement with the landmark signal.

Significance targets:
- "mm100": membership in the Formalizing-100-Theorems list (external,
  human-curated landmark signal available for all of T).
- "human": the user's graded 0-3 labels on the Phase-1 sample, if present.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import kendalltau, spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier, \
    HistGradientBoostingRegressor
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

SEED = 0


def _cv_auc(X: np.ndarray, y: np.ndarray) -> dict[str, float]:
    # 72 positives in ~39k rows: balance classes and disable the internal
    # early-stopping split (it can hold almost no positives).
    clf = HistGradientBoostingClassifier(random_state=SEED,
                                         class_weight="balanced",
                                         early_stopping=False, max_iter=150)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    prob = cross_val_predict(clf, X, y, cv=cv, method="predict_proba")[:, 1]
    return {
        "roc_auc": float(roc_auc_score(y, prob)),
        "avg_precision": float(average_precision_score(y, prob)),
        "n_pos": int(y.sum()), "n": len(y),
    }


def rq2_selector(X: np.ndarray, y: np.ndarray,
                 families: dict[str, list[int]],
                 intrinsic: tuple[str, ...]) -> dict:
    cols = sorted(i for f in intrinsic for i in families[f])
    return _cv_auc(X[:, cols], y)


def rq1_ablation(X: np.ndarray, y: np.ndarray,
                 families: dict[str, list[int]],
                 intrinsic: tuple[str, ...]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    # each family alone
    for fam, cols in families.items():
        out[f"only_{fam}"] = _cv_auc(X[:, sorted(cols)], y)
    # intrinsic vs cultural vs everything
    intr = sorted(i for f in intrinsic for i in families[f])
    out["intrinsic_all"] = _cv_auc(X[:, intr], y)
    out["all_features"] = _cv_auc(X, y)
    # leave-one-family-out within intrinsic
    for fam in intrinsic:
        cols = sorted(i for f in intrinsic if f != fam for i in families[f])
        out[f"intrinsic_minus_{fam}"] = _cv_auc(X[:, cols], y)
    return out


def rq3_convergence(measures: dict[str, dict[str, float]],
                    labels: list[str], y_landmark: np.ndarray) -> dict:
    names = sorted(measures)
    vecs = {m: np.array([measures[m][t] for t in labels]) for m in names}
    pairwise = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            rho = spearmanr(vecs[a], vecs[b]).statistic
            tau = kendalltau(vecs[a], vecs[b]).statistic
            pairwise[f"{a}~{b}"] = {"spearman": float(rho),
                                    "kendall": float(tau)}
    vs_landmarks = {}
    for m in names:
        ranks = vecs[m].argsort().argsort() / (len(labels) - 1)
        vs_landmarks[m] = {
            "roc_auc": float(roc_auc_score(y_landmark, vecs[m])),
            "mean_landmark_percentile": float(ranks[y_landmark == 1].mean()),
        }
    return {"pairwise": pairwise, "vs_landmarks": vs_landmarks}


def human_label_experiments(X: np.ndarray, feature_names: list[str],
                            families: dict[str, list[int]],
                            intrinsic: tuple[str, ...],
                            labels: list[str],
                            human: dict[str, int],
                            measures: dict[str, dict[str, float]]) -> dict:
    """RQ1/RQ2/RQ3 readouts against graded human labels on the labeled sample."""
    idx = [i for i, t in enumerate(labels) if t in human]
    Xh = X[idx]
    yh = np.array([human[labels[i]] for i in idx], dtype=float)
    out: dict = {"n_labeled": len(idx),
                 "grade_counts": {g: int((yh == g).sum()) for g in sorted(set(yh))}}

    def loo_spearman(cols: list[int]) -> float:
        # leave-one-out over the small labeled sample
        preds = np.empty(len(idx))
        for k in range(len(idx)):
            mask = np.arange(len(idx)) != k
            reg = HistGradientBoostingRegressor(random_state=SEED,
                                                min_samples_leaf=5)
            reg.fit(Xh[np.ix_(mask, cols)], yh[mask])
            preds[k] = reg.predict(Xh[np.ix_([k], cols)])[0]
        return float(spearmanr(preds, yh).statistic)

    intr = sorted(i for f in intrinsic for i in families[f])
    out["rq2_intrinsic_spearman"] = loo_spearman(intr)
    out["rq1_ablation_spearman"] = {
        f"only_{fam}": loo_spearman(sorted(cols))
        for fam, cols in families.items()}
    out["rq3_measures_vs_human"] = {
        m: {"spearman": float(spearmanr(
                [measures[m][labels[i]] for i in idx], yh).statistic),
            "kendall": float(kendalltau(
                [measures[m][labels[i]] for i in idx], yh).statistic)}
        for m in sorted(measures)}
    return out
