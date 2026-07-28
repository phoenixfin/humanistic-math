# Significance Labeling Guide (Phase 1)

Human ground truth for RQ1–RQ3. You grade a stratified sample of theorems on a
0–3 scale; the experiments compare these grades against intrinsic measures.

## Two tracks: full library vs. the propositional starter

Every script in this pipeline takes an optional `variant` argument:

- **`""` (default)** — the full `set.mm` library: 38,928 theorems. This is the
  real experiment.
- **`"prop"`** — a smaller, real starter substrate: just the
  propositional-calculus theorems inside `set.mm` (1,036 theorems, no
  quantifiers/sets/classes — see `docs/PHASE0_DECISION.md`). Simple enough to
  grade quickly and sanity-check the whole pipeline, but note it has **zero**
  Metamath-100 landmark flags (those are all set-theory/analysis/number-theory
  results), so the mm100-based RQ1/RQ2 experiments auto-skip for this variant
  — only RQ3 (measure convergence) and, once you've labeled it, the
  human-label readouts apply. Good for a fast dry run; not a substitute for
  the full-scale result.

Every command below accepts the variant as its one positional argument, e.g.
`py scripts/run_experiments.py prop`.

## The scale

| Grade | Anchor | Test |
|---|---|---|
| **0** | Mechanical / trivial | Pure bookkeeping: restatement, commuted hypothesis order, inference-form of an axiom. You'd never mention it in a paper. |
| **1** | Minor lemma | Real but local step; exists only to serve one or two nearby proofs. A textbook would inline it. |
| **2** | Named / reusable result | You'd expect a name or a textbook display: a lemma any working mathematician recognizes as a standard tool. |
| **3** | Landmark | A theorem someone might state as a *reason the field matters*: irrationality of √2, infinitude of primes, Cantor's theorem. |

Grade the **statement**, not the proof: "would this deserve attention if I met
it in a book?" — not "was it hard to prove?".

## Workflow (interactive — recommended)

1. Run `py scripts/label_ui.py` (full library, port 8731) or
   `py scripts/label_ui.py 8732 prop` (propositional starter, port 8732 so
   both can run at once) and open the corresponding `http://127.0.0.1:PORT`.
   Grading panel on the left, the human-readable us.metamath.org page for the
   current theorem on the right.
2. Grade with the buttons or keys `0`–`3` (auto-advances); `←`/`→` navigate,
   `n` for notes. Every grade is saved immediately to
   `data/labels/labels_filled.csv` (or `labels_filled_prop.csv`) — stop and
   resume anytime.
3. When the progress bar completes, re-run `py scripts/run_experiments.py`
   (add `prop` for the starter variant) — it detects the filled file and adds
   the human-label readouts (RQ1/RQ2/RQ3 against your grades) to the report.

## Workflow (manual)

Fill the `significance_0_3` column of `data/labels/label_sample.csv` (or
`label_sample_prop.csv`) — integers 0–3, `notes` free-form — and save it as
`data/labels/labels_filled.csv` (or `labels_filled_prop.csv`), then re-run the
experiments script as above.

Design notes (resolving ROADMAP open items, defaults chosen 2026-07-12):
- **Scale**: 0–3 as above.
- **Volume**: 100 theorems, single labeler to start; a second labeler can fill
  a copy of the same CSV later for inter-rater agreement (Cohen's κ) — the
  experiment script accepts `labels_filled_2.csv` for that.
- The sample is stratified on centrality percentiles (plus a slice of
  Metamath-100 landmarks) so all significance levels are represented; this is
  deliberate selection bias toward coverage and is reported as such.
