"""Phase 1 — build and persist the substrate (T + DAG) from data/raw/set.mm."""

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmath.substrate import build_from_file  # noqa: E402


def main() -> None:
    t0 = time.time()
    s = build_from_file(str(ROOT / "data" / "raw" / "set.mm"))
    out = ROOT / "data" / "derived" / "substrate.jsonl"
    s.save(out)

    n_edges = sum(len(t.deps) for t in s.theorems)
    n_mm100 = sum(1 for t in s.theorems if t.mm100 is not None)
    print(f"substrate built in {time.time() - t0:.1f}s")
    print(f"  |T| (theorems, deduped):   {len(s.theorems)}")
    print(f"  axiom/definition roots:    {len(s.axioms)}")
    print(f"  logical dependency edges:  {n_edges}")
    print(f"  mm100 landmarks in T:      {n_mm100}")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
