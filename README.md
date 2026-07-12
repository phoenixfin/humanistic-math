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
  (Lean mathlib / Isabelle) as the theorem set.
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

Phase 0 — deciding the derivation source (see ROADMAP). No code yet by design: the
Branch A/B decision determines whether we build a bounded-Peano enumerator or a
mathlib/Isabelle extraction pipeline.
