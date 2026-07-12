"""Phase 1 — draw the stratified labeling sample (deterministic, seed=0).

Strata (target 100):
- 10 Metamath-100 landmarks (anchor the top of the scale)
- 30 from the top centrality decile
- 30 from the middle (25th-75th percentile)
- 30 from the bottom quartile
"""

import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmath.substrate import Substrate  # noqa: E402


def main() -> None:
    s = Substrate.load(ROOT / "data" / "derived" / "substrate.jsonl")
    scores = json.loads((ROOT / "data" / "derived" / "measures.json").read_text())
    cent = scores["centrality"]

    rng = random.Random(0)
    ranked = sorted(s.theorems, key=lambda t: cent[t.label], reverse=True)
    n = len(ranked)
    landmarks = [t for t in s.theorems if t.mm100 is not None]

    picked = rng.sample(landmarks, 10)
    chosen = {t.label for t in picked}

    def draw(pool, k):
        pool = [t for t in pool if t.label not in chosen]
        got = rng.sample(pool, k)
        chosen.update(t.label for t in got)
        return got

    picked += draw(ranked[: n // 10], 30)
    picked += draw(ranked[n // 4: 3 * n // 4], 30)
    picked += draw(ranked[3 * n // 4:], 30)
    rng.shuffle(picked)

    out = ROOT / "data" / "labels" / "label_sample.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["label", "statement", "description", "url",
                    "significance_0_3", "notes"])
        for t in picked:
            # Strip Metamath-100 mentions so the labeler is not primed.
            desc = re.sub(r"[^.]*Metamath 100[^.]*\.", "", t.comment)[:400]
            w.writerow([t.label, t.statement, desc,
                        f"https://us.metamath.org/mpeuni/{t.label}.html", "", ""])
    print(f"wrote {out.relative_to(ROOT)} ({len(picked)} theorems)")


if __name__ == "__main__":
    main()
