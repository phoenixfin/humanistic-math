"""Phase 1 — draw the stratified labeling sample (deterministic, seed=0).

    py scripts/make_label_sample.py [variant]

Target is min(100, |T|): if the substrate has 100 theorems or fewer (e.g.
the "prop" starter variant), every theorem is included. Otherwise, strata:
- up to 10 Metamath-100 landmarks (anchor the top of the scale)
- the rest split evenly across top centrality decile / middle 25-75% / bottom quartile
"""

import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmath import paths  # noqa: E402
from hmath.substrate import Substrate  # noqa: E402


def main() -> None:
    variant = sys.argv[1] if len(sys.argv) > 1 else ""
    s = Substrate.load(paths.substrate_path(variant))
    scores = json.loads(paths.measures_path(variant).read_text())
    cent = scores["centrality"]

    rng = random.Random(0)
    ranked = sorted(s.theorems, key=lambda t: cent[t.label], reverse=True)
    n = len(ranked)
    landmarks = [t for t in s.theorems if t.mm100 is not None]
    target = min(100, n)

    if n <= target:
        picked = list(s.theorems)
    else:
        picked = rng.sample(landmarks, min(10, len(landmarks)))
        chosen = {t.label for t in picked}
        rest = target - len(picked)
        thirds = [rest // 3] * 3
        thirds[0] += rest - sum(thirds)

        def draw(pool, k):
            pool = [t for t in pool if t.label not in chosen]
            k = min(k, len(pool))
            got = rng.sample(pool, k) if k else []
            chosen.update(t.label for t in got)
            return got

        picked += draw(ranked[: max(n // 10, 1)], thirds[0])
        picked += draw(ranked[n // 4: 3 * n // 4], thirds[1])
        picked += draw(ranked[3 * n // 4:], thirds[2])
    rng.shuffle(picked)

    out = paths.label_sample_path(variant)
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
