"""Phase 3 — run RQ1-RQ3 and write reports/results*.json + reports/RESULTS*.md.

    py scripts/run_experiments.py [variant]

Runs against the Metamath-100 landmark signal always; adds human-label
readouts when the variant's labels_filled csv exists (see docs/LABELING.md).
"""

import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmath import experiments, features, paths  # noqa: E402
from hmath.substrate import Substrate  # noqa: E402


def load_human_labels(path: Path) -> dict[str, int]:
    labels: dict[str, int] = {}
    with open(path, encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            v = row.get("significance_0_3", "").strip()
            if v:
                labels[row["label"]] = int(v)
    return labels


def main() -> None:
    variant = sys.argv[1] if len(sys.argv) > 1 else ""
    t0 = time.time()
    s = Substrate.load(paths.substrate_path(variant))
    measures = json.loads(paths.measures_path(variant).read_text())
    X, names, families, labels = features.compute(s, measures)
    y = np.array([1 if t.mm100 is not None else 0 for t in s.theorems])
    n_landmarks = int(y.sum())

    results = {
        "substrate": {"n_theorems": len(labels),
                      "n_landmarks_mm100": n_landmarks},
        "rq3_convergence": experiments.rq3_convergence(measures, labels, y),
    }
    # 5-fold stratified CV needs a handful of positives per fold; a small
    # substrate (e.g. the propositional slice) may have too few mm100 flags.
    if n_landmarks >= 5:
        results["rq2_selector_mm100"] = experiments.rq2_selector(
            X, y, families, features.INTRINSIC)
        results["rq1_ablation_mm100"] = experiments.rq1_ablation(
            X, y, families, features.INTRINSIC)
    else:
        results["mm100_note"] = (
            f"only {n_landmarks} Metamath-100 landmarks in this substrate — "
            "too few for the 5-fold CV selector/ablation; skipped. Rely on "
            "human labels instead.")

    filled = paths.labels_filled_path(variant)
    if filled.exists():
        human = load_human_labels(filled)
        results["human_labels"] = experiments.human_label_experiments(
            X, names, families, features.INTRINSIC, labels, human, measures)

    out_json = paths.results_json_path(variant)
    out_json.parent.mkdir(exist_ok=True)
    out_json.write_text(json.dumps(results, indent=2), encoding="utf-8")
    out_md = paths.results_md_path(variant)
    write_markdown(results, out_md)
    print(json.dumps(results, indent=2))
    print(f"\ndone in {time.time() - t0:.1f}s -> {out_json.relative_to(ROOT)}, "
          f"{out_md.relative_to(ROOT)}")


def write_markdown(r: dict, path: Path) -> None:
    L = ["# Results", ""]
    sub = r["substrate"]
    L += [f"Theorem set: **{sub['n_theorems']}** deduplicated theorems; "
          f"landmark signal: **{sub['n_landmarks_mm100']}** Metamath-100 "
          f"entries.", ""]

    if "mm100_note" in r:
        L += ["## RQ1/RQ2 — landmark-signal experiments skipped", "",
              r["mm100_note"], ""]
    else:
        q2 = r["rq2_selector_mm100"]
        L += ["## RQ2 — Is taste learnable? (landmark signal)", "",
              f"Gradient-boosted trees on intrinsic features only, 5-fold "
              f"CV: **ROC-AUC {q2['roc_auc']:.3f}**, average precision "
              f"{q2['avg_precision']:.3f} "
              f"(base rate {q2['n_pos']}/{q2['n']}).", ""]

        L += ["## RQ1 — Structure vs. taste (feature-family ablation)", "",
              "| feature set | ROC-AUC | avg. precision |", "|---|---|---|"]
        for k, v in r["rq1_ablation_mm100"].items():
            L.append(f"| {k} | {v['roc_auc']:.3f} | {v['avg_precision']:.3f} |")
        L.append("")

    q3 = r["rq3_convergence"]
    L += ["## RQ3 — Do independent measures converge?", "",
          "Pairwise rank agreement (all of T):", "",
          "| pair | Spearman | Kendall |", "|---|---|---|"]
    for k, v in q3["pairwise"].items():
        L.append(f"| {k} | {v['spearman']:.3f} | {v['kendall']:.3f} |")
    if "vs_landmarks" in q3:
        L += ["", "Each measure vs. the landmark set:", "",
              "| measure | ROC-AUC | mean landmark percentile |",
              "|---|---|---|"]
        for k, v in q3["vs_landmarks"].items():
            L.append(f"| {k} | {v['roc_auc']:.3f} | "
                     f"{v['mean_landmark_percentile']:.3f} |")
    L.append("")

    if "human_labels" in r:
        h = r["human_labels"]
        L += ["## Human-label readouts", "",
              f"Labeled sample: {h['n_labeled']} theorems, grade counts "
              f"{h['grade_counts']}.", "",
              f"RQ2 (intrinsic features -> grade, leave-one-out): Spearman "
              f"**{h['rq2_intrinsic_spearman']:.3f}**", "",
              "RQ1 ablation (Spearman by family):", ""]
        for k, v in h["rq1_ablation_spearman"].items():
            L.append(f"- {k}: {v:.3f}")
        L += ["", "RQ3 measures vs. human grades:", ""]
        for k, v in h["rq3_measures_vs_human"].items():
            L.append(f"- {k}: Spearman {v['spearman']:.3f}, "
                     f"Kendall {v['kendall']:.3f}")
        L.append("")

    path.write_text("\n".join(L), encoding="utf-8")


if __name__ == "__main__":
    main()
