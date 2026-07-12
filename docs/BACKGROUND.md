# Math-RL → Humanistic Mathematics — Project Summary

## 1. The Core Idea

Build an intelligent agent that **rebuilds mathematics from scratch** — starting from
axioms and constructing theorems via logical rules, like assembling from primitives.

The deeper motivation is **philosophical**, made empirical:

> Is the *significance* of a theorem a property of mathematics itself, or a property
> of us? Is mathematics **discovered** (its landmarks forced by structure) or
> **invented** (its landmarks a reflection of human taste)?

This reframes the engineering goal. The point is not to build a machine that proves
everything — that is effectively AGI-complete. The point is to run **sharp, small
experiments** that test whether mathematical "importance" is structural or humanistic.

---

## 2. Research Questions

The three questions are one question, sliced three ways:

- **RQ1 — Structure vs. taste.** Do purely *intrinsic* measures (compression,
  connectivity, reuse) predict which theorems humans call significant? If yes →
  significance is discovered. If only human-fitted features work → invented.
- **RQ2 — Is taste learnable?** Can a model predict human-significance from structural
  features alone, on held-out theorems, above chance? Learnable → taste is structured,
  not arbitrary.
- **RQ3 — Do independent measures converge?** Do different unsupervised significance
  rankings agree with each other *and* with human landmarks? Convergence → the
  landmarks are in the math.

Unifying logic:

```
Intrinsic measures ──agree with each other?──────────────→ RQ3
        │
        └──predict human labels?──→ RQ1 (which features) + RQ2 (can we learn it)
```

One enumerated theorem space, one human-label set, three readouts.

---

## 3. What We Built (v1 → v4)

A propositional-logic system evolved across four iterations:

- **v1–v2** — Graph-traversal RL. Agent selected from a **predefined** list of theorem
  nodes (propositional logic, plus draft Peano & ZFC graphs). Streamlit rating UI +
  reward-model scaffold + local-training / cloud-UI split.
- **v3** — **Generative** redesign. Agent constructs formulas from scratch via axiom
  schemas (A1, A2, A3) + Modus Ponens, with a substitution pool of recent formulas.
  Formula algebra with alpha-equivalence checkpoint matching.
- **v4** — **Term-construction** redesign after a critical diagnosis (below). Added
  `NEG`/`IMP` term-building actions, deterministic state, reward shaping, and
  demonstration warm-start (DQfD-style imitation).

Supporting infrastructure built along the way: Streamlit human-rating interface,
reward model (learns from ratings), path/proof exporter, deployment split
(UI on Streamlit Cloud, training local), proof-construction + deduction-theorem
machinery, and an automated forward-saturation prover.

---

## 4. What We Learned (the important part)

**The central finding — a reachability ceiling, not a tuning problem.**
An env-faithful forward-chaining oracle (stronger than the DQN) was run to fixpoint.
It derived **4,743 distinct theorems** but saturated at **exactly 1 of 7** human
checkpoints. The other six were unreachable *in principle* under v3's design, because
axiom schemas could only be instantiated with already-proven formulas, MP could not
discharge atomic premises, and a size filter discarded the intermediate lemmas every
real proof needs. **Lesson: test the ceiling with a strong search before blaming the
learner.**

**This finding is itself a philosophical result.** Of ~4,743 derivable truths, only a
tiny curated subset are "interesting" to humans. So what makes math *math* is largely
a **selection function**, not the derivation. The interesting science is in selection,
not generation.

**RL is the wrong hammer for generation.** A measured ablation (140 episodes, no demos,
boosted shaping) discovered only the 1-step theorem, never multi-step ones. Reward
shaping cannot bootstrap multi-step proof discovery in a large term-construction action
space. Demonstrations were essential; real autonomous discovery needs **search-based**
exploration (MCTS / best-first), not shaping.

**v4 results (after term construction + demos):** all 7 theorems reachable in
principle; agent reliably reproduces 3 (Weakening, Identity, Ex Falso) via imitation.
The 3 "classical" theorems (Double Negation, Contrapositive, Peirce) all reduce to a
single base lemma (**Clavius**, `(¬p→p)→p`), whose Hilbert proof needs intermediate
terms far larger than the goal — intractable for forward search.

**Engineering lessons banked:** deterministic structural state (never hash with a
salt-randomized `hash()` across sessions); don't flood the checkpoint signal with flat
novelty rewards; UTF-8-safe logging for `→`/`¬`; save the *best* agent snapshot, not the
degraded final one.

---

## 5. Decisions Made

- **Formal system → Peano Arithmetic.** Propositional logic's landmarks are too thin to
  test a "humanistic" hypothesis meaningfully; Peano is where genuinely interesting
  theorems live (commutativity, division algorithm, infinitude of primes).
- **Human labels → graded significance depth** (not binary checkpoints), so the selector
  has real signal to learn and be evaluated against.
- **RL is demoted.** Generation becomes enumeration / search; the learned model lives in
  *selection*. The former RL agent, if used at all, is a downstream consumer guided by
  the selector — not the object under test.
- **Fresh start permitted.** The new project is not bound to the v3/v4 codebase; it may
  be rebuilt from scratch around the enumerate → label → select → converge pipeline.

---

## 6. Constraints & Realities

- **Full "rebuild mathematics" is out of scope** — it is AGI-complete. The tractable
  target is a specific, bounded fragment plus a sharp selection experiment.
- **Peano + term-construction is expensive.** Peano needs an **induction schema** (over
  formulas, not just MP), and real theorems need substantial lemmas. Full first-order
  enumeration-to-fixpoint is likely **intractable** at useful depth.
- **Compute is modest** (local training; Streamlit Cloud has no persistent FS and can't
  train). Any design must fit this.
- **Labeling is human-bottlenecked** — the significance scale must stay feasible to apply
  by hand to ~50–100 theorems.

---

## 7. Open Items (to resolve before/into the roadmap)

- **[OPEN] Peano derivation source.** Self-enumerate a **bounded / quantifier-free
  fragment**, or **import an existing library** (Lean `mathlib` / Isabelle) as the
  theorem set + dependency graph? Importing sidesteps the prover bottleneck entirely and
  gives a real dependency DAG for free — strongly worth considering, since the science is
  in selection, not derivation.
- **[OPEN] Significance scale.** Draft (0–3): 0 mechanical/trivial · 1 minor lemma ·
  2 named/reusable result · 3 landmark. Granularity and anchors not yet finalized.
- **[OPEN] Label volume.** Target count and who labels (single labeler vs. several, for
  inter-rater agreement) undecided.
- **[OPEN] Intrinsic measures shortlist.** Candidates: MDL/compression contribution,
  dependency-graph centrality (e.g. PageRank), lemma-reuse frequency, proof-surprise.
  Final set and exact definitions TBD.

---

## 8. Current Asset Inventory (v4, reference only)

Not binding on the new project, but available to reuse:

- `formula.py` — formula algebra, alpha-equivalence, subformulas, size/depth caps.
- `env.py` — term-construction Hilbert environment (propositional).
- `proofs.py` / `demos.py` / `prover.py` — proof construction, deduction theorem,
  demo replay, forward-saturation prover.
- `agent.py` — DQfD demo buffer + large-margin imitation loss.
- `train.py` — warm-start, best-checkpoint restore, UTF-8-safe logging.
- Streamlit rating UI + reward model + local/cloud deployment split.
