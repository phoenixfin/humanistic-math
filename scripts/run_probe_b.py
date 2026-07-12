"""Phase 0 / Probe B — can we import an existing library as theorem set + DAG?

Parses data/raw/set.mm (Metamath) and reports the scale and quality of the
theorem set and dependency DAG we get, plus availability of an external
landmark signal (the "Metamath 100" list markers).
"""

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmath.metamath import parse  # noqa: E402


def main() -> None:
    t0 = time.time()
    assertions = parse(str(ROOT / "data" / "raw" / "set.mm")).assertions
    parse_s = time.time() - t0

    axioms = [a for a in assertions if a.kind == "a"]
    theorems = [a for a in assertions if a.kind == "p"]
    edges = sum(len(set(a.deps)) for a in theorems)
    mm100 = [a for a in theorems if a.mm100 is not None]
    use_count = Counter(d for a in theorems for d in set(a.deps))

    dup_statements = Counter(a.tokens for a in theorems)
    n_dup = sum(c - 1 for c in dup_statements.values() if c > 1)

    report = {
        "parse_seconds": round(parse_s, 1),
        "assertions": len(assertions),
        "axioms_and_definitions": len(axioms),
        "theorems": len(theorems),
        "unique_dependency_edges": edges,
        "duplicate_statements": n_dup,
        "mm100_flagged": len(mm100),
        "mm100_distinct_entries": len({a.mm100 for a in mm100}),
        "top_reused": use_count.most_common(15),
        "mm100_examples": [
            {"label": a.label, "n": a.mm100, "statement": a.statement[:100]}
            for a in sorted(mm100, key=lambda a: a.mm100)[:10]
        ],
    }
    out = ROOT / "data" / "derived" / "probe_b_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"parsed {len(assertions)} assertions in {parse_s:.1f}s")
    print(f"  axioms/definitions: {len(axioms)}")
    print(f"  proven theorems:    {len(theorems)}")
    print(f"  dependency edges:   {edges}")
    print(f"  duplicate stmts:    {n_dup}")
    print(f"  Metamath-100 flags: {len(mm100)} theorems, "
          f"{len({a.mm100 for a in mm100})} distinct list entries")
    print(f"  most-reused: {use_count.most_common(5)}")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
