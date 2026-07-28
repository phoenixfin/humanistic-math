# Humanistic Mathematics

An empirical probe of an old philosophical question: **is mathematics discovered or
invented?** Concretely — is the *significance* of a theorem a structural property of
mathematics itself, or a reflection of human taste?

## The experiment

One pipeline: **enumerate → label → measure → select → converge.**

Take a theorem set with its dependency graph, have humans grade theorem significance,
compute purely *intrinsic* significance measures (compression, centrality, reuse,
surprise), and ask three questions:

- **RQ1 — Structure vs. taste.** Do intrinsic measures predict which theorems humans
  call significant?
- **RQ2 — Is taste learnable?** Can a model predict human significance from structural
  features alone, on held-out theorems?
- **RQ3 — Do independent measures converge?** Do different unsupervised rankings agree
  with each other and with human landmarks?

If intrinsic measures converge on the human landmarks, significance is *in the math*
(discovered). If only human-fitted features work, it's *in us* (invented).

## Documents

- [ROADMAP.md](ROADMAP.md) — the phased plan, starting with the Phase 0 fork:
  self-enumerate a bounded Peano fragment vs. import an existing library
  as the theorem set.
- [docs/PHASE0_DECISION.md](docs/PHASE0_DECISION.md) — the fork's resolution:
  Branch B, instantiated with Metamath `set.mm`.
- [docs/LABELING.md](docs/LABELING.md) — the 0–3 significance scale and the
  human-labeling workflow.
- [reports/READOUT.md](reports/READOUT.md) — Phase 4 interpretation of the
  first full experimental run.
- [docs/BACKGROUND.md](docs/BACKGROUND.md) — how this project emerged from its
  predecessor, and the findings that shaped its design.

## Lineage

This project succeeds [math-rl](https://github.com/phoenixfin/math-rl), which tried to
*generate* mathematics with reinforcement learning over a Hilbert-style propositional
system. Its central finding: a forward-chaining oracle derived 4,743 true theorems, of
which humans would call almost none interesting — and reward shaping could not bootstrap
multi-step proof discovery at all. The lesson is this project's premise: **what makes
math *math* is a selection function, not the derivation.** Generation is now plain
enumeration/search; the science lives in selection. RL is not part of the core.

## Status

Phases 0–4 executed end-to-end (2026-07-13) against an interim landmark signal
(the "Formalizing 100 Theorems" flags inside `set.mm`):

- **Phase 0** — both probes run; **Branch B chosen** (Metamath `set.mm`:
  38,928 deduped theorems, ~640k dependency edges, parsed in seconds). The
  Branch A enumerator lives on in `src/hmath/probe_a/` as a possible
  authoring-free robustness substrate.
- **Phases 1–3** — substrate, four intrinsic measures, and all three RQ
  experiments implemented and run (`reports/RESULTS.md`).
- **Headline so far** — significance splits in two: unsupervised measures
  *converge* on hub/infrastructure lemmas (discovered, but not what humans
  celebrate), while human landmarks are summit theorems that intrinsic
  proof-shape features still predict at AUC ~0.86 (`reports/READOUT.md`).

**Next human step:** grade the sample interactively — run
`py scripts/label_ui.py` and open http://127.0.0.1:8731 — or by hand per
[docs/LABELING.md](docs/LABELING.md); either way it writes
`data/labels/labels_filled.csv`, then re-run `py scripts/run_experiments.py`.

A smaller **starter track** is also available for fast iteration and
labeling practice: pass `prop` to any script to work against just the
propositional-calculus slice of `set.mm` (1,036 real theorems, no
quantifiers/sets/classes) instead of the full 38,928 — e.g.
`py scripts/label_ui.py 8732 prop`. See
[docs/PHASE0_DECISION.md](docs/PHASE0_DECISION.md) for how it's carved out
and [docs/LABELING.md](docs/LABELING.md) for the two-track workflow.

To reproduce from scratch: download `set.mm` to `data/raw/`, then run
`scripts/build_substrate.py [variant]`, `scripts/run_measures.py [variant]`,
`scripts/run_experiments.py [variant]` (Python ≥ 3.12,
`pip install -r requirements.txt`), where `variant` is empty for the full
library or `prop` for the starter slice.
