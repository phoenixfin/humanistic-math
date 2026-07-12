# Significance Labeling Guide (Phase 1)

Human ground truth for RQ1–RQ3. You grade a stratified sample of theorems on a
0–3 scale; the experiments compare these grades against intrinsic measures.

## The scale

| Grade | Anchor | Test |
|---|---|---|
| **0** | Mechanical / trivial | Pure bookkeeping: restatement, commuted hypothesis order, inference-form of an axiom. You'd never mention it in a paper. |
| **1** | Minor lemma | Real but local step; exists only to serve one or two nearby proofs. A textbook would inline it. |
| **2** | Named / reusable result | You'd expect a name or a textbook display: a lemma any working mathematician recognizes as a standard tool. |
| **3** | Landmark | A theorem someone might state as a *reason the field matters*: irrationality of √2, infinitude of primes, Cantor's theorem. |

Grade the **statement**, not the proof: "would this deserve attention if I met
it in a book?" — not "was it hard to prove?".

## Workflow

1. Open `data/labels/label_sample.csv` (100 theorems, stratified across the
   significance range; column `url` links to the human-readable Metamath page).
2. Fill the `significance_0_3` column (integers 0–3). Use `notes` freely.
3. Save as `data/labels/labels_filled.csv` (same columns).
4. Re-run `py scripts/run_experiments.py` — it detects the filled file and adds
   the human-label readouts (RQ1/RQ2/RQ3 against your grades) to the report.

Design notes (resolving ROADMAP open items, defaults chosen 2026-07-12):
- **Scale**: 0–3 as above.
- **Volume**: 100 theorems, single labeler to start; a second labeler can fill
  a copy of the same CSV later for inter-rater agreement (Cohen's κ) — the
  experiment script accepts `labels_filled_2.csv` for that.
- The sample is stratified on centrality percentiles (plus a slice of
  Metamath-100 landmarks) so all significance levels are represented; this is
  deliberate selection bias toward coverage and is reported as such.
