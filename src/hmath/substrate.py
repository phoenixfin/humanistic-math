"""Phase 1 — the shared substrate: theorem set T + dependency DAG.

Built from a parsed Metamath database:

- T = all $p assertions with logical typecode "|-" (actual theorems, not
  syntax constructors), canonicalized up to variable renaming and
  deduplicated (first occurrence is canonical; restatements are recorded).
- DAG = edges (theorem -> lemma) restricted to logical assertions, so an edge
  means "used as a logical step in the proof", not "used to build syntax".
- Axioms/definitions ($a with "|-") are kept as DAG roots but are not part
  of T (they have no proofs to measure).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .metamath import Assertion, Database, parse


@dataclass
class Theorem:
    label: str
    index: int                 # database order among substrate nodes
    statement: str
    comment: str
    mm100: int | None
    deps: tuple[str, ...]      # logical deps only (labels), deduplicated
    proof_size: int            # distinct labels referenced by the proof (all kinds)
    n_restatements: int        # other theorems with the same canonical statement
    is_axiom: bool             # True for $a roots (axioms/definitions)


@dataclass
class Substrate:
    theorems: list[Theorem]                # T, database order (proofs only)
    axioms: list[Theorem]                  # DAG roots
    by_label: dict[str, Theorem]

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            for t in self.axioms + self.theorems:
                fh.write(json.dumps({
                    "label": t.label, "index": t.index, "statement": t.statement,
                    "comment": t.comment, "mm100": t.mm100, "deps": list(t.deps),
                    "proof_size": t.proof_size, "n_restatements": t.n_restatements,
                    "is_axiom": t.is_axiom,
                }) + "\n")

    @staticmethod
    def load(path: Path) -> "Substrate":
        theorems, axioms = [], []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                d = json.loads(line)
                t = Theorem(label=d["label"], index=d["index"],
                            statement=d["statement"], comment=d["comment"],
                            mm100=d["mm100"], deps=tuple(d["deps"]),
                            proof_size=d["proof_size"],
                            n_restatements=d["n_restatements"],
                            is_axiom=d["is_axiom"])
                (axioms if t.is_axiom else theorems).append(t)
        s = Substrate(theorems=theorems, axioms=axioms, by_label={})
        s.by_label = {t.label: t for t in s.axioms + s.theorems}
        return s


def build(db: Database) -> Substrate:
    logical = [a for a in db.assertions if a.tokens and a.tokens[0] == "|-"]
    logical_labels = {a.label for a in logical}

    # Dedup up to variable renaming: first statement with a canonical form is
    # canonical; later restatements are dropped from T but counted.
    seen: dict[tuple[str, ...], str] = {}
    restatements: dict[str, int] = {}
    keep: list[Assertion] = []
    for a in logical:
        key = db.canonical(a)
        if a.kind == "p" and key in seen:
            restatements[seen[key]] = restatements.get(seen[key], 0) + 1
            continue
        seen.setdefault(key, a.label)
        keep.append(a)

    kept_labels = {a.label for a in keep}

    # Redirect dependency edges that point at dropped restatements to their
    # canonical representative, so reuse counts aggregate correctly.
    redirect = {a.label: seen[db.canonical(a)] for a in logical
                if a.label not in kept_labels}

    theorems, axioms = [], []
    for i, a in enumerate(keep):
        deps = []
        for d in a.deps:
            if d not in logical_labels:
                continue                       # syntax-construction step
            d = redirect.get(d, d)
            if d != a.label and d not in deps:
                deps.append(d)
        t = Theorem(label=a.label, index=i, statement=a.statement,
                    comment=a.comment, mm100=a.mm100, deps=tuple(deps),
                    proof_size=len(set(a.deps)),
                    n_restatements=restatements.get(a.label, 0),
                    is_axiom=a.kind == "a")
        (axioms if t.is_axiom else theorems).append(t)

    s = Substrate(theorems=theorems, axioms=axioms, by_label={})
    s.by_label = {t.label: t for t in s.axioms + s.theorems}
    return s


def build_from_file(mm_path: str) -> Substrate:
    return build(parse(mm_path))
