"""Phase 2 — compute all intrinsic measures and persist score tables."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmath import paths  # noqa: E402
from hmath.measures import compute_all  # noqa: E402
from hmath.substrate import Substrate  # noqa: E402


def main() -> None:
    variant = sys.argv[1] if len(sys.argv) > 1 else ""
    s = Substrate.load(paths.substrate_path(variant))
    scores = {}
    for name in ("reuse", "centrality", "compression", "surprise"):
        from hmath.measures import ALL
        t0 = time.time()
        scores[name] = ALL[name](s)
        print(f"{name:12s} computed in {time.time() - t0:.1f}s")

    out = paths.measures_path(variant)
    out.write_text(json.dumps(scores), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")

    # Top-10 per measure, as a sanity readout.
    for name, sc in scores.items():
        top = sorted(sc, key=sc.get, reverse=True)[:10]
        print(f"\ntop {name}: {', '.join(top)}")


if __name__ == "__main__":
    main()
