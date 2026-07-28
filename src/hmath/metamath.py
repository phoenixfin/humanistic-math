"""Streaming parser for Metamath databases (set.mm).

Extracts the assertion-level view the project needs: every $a/$p statement with
its label, statement tokens, preceding comment, and — for $p — the labels of
previously-proven assertions referenced by its proof (the dependency edges).
Proof steps are not verified; only the referenced labels are collected.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterator


@dataclass
class Assertion:
    label: str
    kind: str                     # "a" (axiom/definition) or "p" (proven theorem)
    tokens: tuple[str, ...]       # statement math tokens, e.g. ("|-", "(", "ph", "->", "ph", ")")
    comment: str                  # description comment immediately preceding the statement
    deps: tuple[str, ...] = ()    # labels of $a/$p assertions used in the proof (empty for $a)
    index: int = 0                # position in database order

    @property
    def statement(self) -> str:
        return " ".join(self.tokens)

    @property
    def mm100(self) -> int | None:
        """Metamath 100 proof number if this theorem is flagged in its comment."""
        m = re.search(r"Metamath 100 proof #(\d+)", self.comment)
        return int(m.group(1)) if m else None


@dataclass
class Database:
    assertions: list[Assertion]
    variables: set[str]           # all $v tokens (for alpha-canonicalization)
    var_typecode: dict[str, str]  # variable -> its $f-declared typecode (e.g. "wff", "set")

    def canonical(self, a: Assertion) -> tuple[str, ...]:
        """Statement tokens with variables renamed by order of first occurrence."""
        mapping: dict[str, str] = {}
        out = []
        for t in a.tokens:
            if t in self.variables:
                if t not in mapping:
                    mapping[t] = f"#{len(mapping)}"
                out.append(mapping[t])
            else:
                out.append(t)
        return tuple(out)


def _tokens(path: str) -> Iterator[str]:
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            yield from line.split()


def parse(path: str) -> Database:
    """Parse a .mm file into its assertions (database order) and variable set."""
    assertions: list[Assertion] = []
    variables: set[str] = set()
    var_typecode: dict[str, str] = {}
    labels_seen: set[str] = set()          # labels of $a/$p (to filter proof deps)
    comment: list[str] = []                # tokens of the most recent comment
    in_comment = False
    prev = ""                              # previous non-comment token (statement label)
    it = _tokens(path)

    for tok in it:
        if in_comment:
            if tok == "$)":
                in_comment = False
            else:
                comment.append(tok)
            continue
        if tok == "$(":
            in_comment = True
            comment = []
            continue

        if tok in ("$a", "$p"):
            label = prev
            kind = tok[1]
            stmt: list[str] = []
            deps: list[str] = []
            for t in it:
                if t in ("$.", "$="):
                    terminator = t
                    break
                stmt.append(t)
            if terminator == "$=":           # proof follows ($p only)
                first = next(it)
                if first == "(":             # compressed proof: ( label ... ) STEPS $.
                    for t in it:
                        if t == ")":
                            break
                        deps.append(t)
                    for t in it:             # skip compressed step letters
                        if t == "$.":
                            break
                else:                        # uncompressed proof: label sequence
                    if first != "$.":
                        deps.append(first)
                        for t in it:
                            if t == "$.":
                                break
                            deps.append(t)
            good_deps = tuple(d for d in deps if d in labels_seen)
            assertions.append(Assertion(
                label=label,
                kind=kind,
                tokens=tuple(stmt),
                comment=" ".join(comment),
                deps=good_deps,
                index=len(assertions),
            ))
            labels_seen.add(label)
            comment = []
            prev = ""
            continue

        # $c/$v/$f/$e/$d statements and block braces: skip their bodies but
        # remember the last plain token so assertion labels are available.
        if tok in ("$c", "$v", "$f", "$e", "$d"):
            if tok == "$v":
                for t in it:
                    if t == "$.":
                        break
                    variables.add(t)
            elif tok == "$f":
                typecode = next(it)
                varname = next(it)
                var_typecode[varname] = typecode
                for t in it:
                    if t == "$.":
                        break
            else:
                for t in it:
                    if t == "$.":
                        break
            prev = ""
            continue
        if tok in ("${", "$}"):
            prev = ""
            continue
        prev = tok

    return Database(assertions=assertions, variables=variables,
                    var_typecode=var_typecode)
