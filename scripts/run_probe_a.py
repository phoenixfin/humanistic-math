"""Phase 0 / Probe A — bounded Peano self-enumeration feasibility.

Answers the ROADMAP Phase 0 question: can Branch A reach ~30-50
recognizably-named theorems at feasible compute?
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from hmath.probe_a import (AXIOMS, Config, Equation, ONE, S, X, Y, Z, ZERO,  # noqa: E402
                           add, canonical_eq, explore, mul, pw)

NAMED = {
    "add_zero_left": Equation(add(ZERO, X), X),
    "succ_add": Equation(add(S(X), Y), S(add(X, Y))),
    "add_comm": Equation(add(X, Y), add(Y, X)),
    "add_assoc": Equation(add(add(X, Y), Z), add(X, add(Y, Z))),
    "zero_mul": Equation(mul(ZERO, X), ZERO),
    "succ_mul": Equation(mul(S(X), Y), add(mul(X, Y), Y)),
    "mul_one": Equation(mul(X, ONE), X),
    "one_mul": Equation(mul(ONE, X), X),
    "mul_comm": Equation(mul(X, Y), mul(Y, X)),
    "mul_assoc": Equation(mul(mul(X, Y), Z), mul(X, mul(Y, Z))),
    "distrib_left": Equation(mul(X, add(Y, Z)), add(mul(X, Y), mul(X, Z))),
    "distrib_right": Equation(mul(add(X, Y), Z), add(mul(X, Z), mul(Y, Z))),
    "pow_one": Equation(pw(X, ONE), X),
    "one_pow": Equation(pw(ONE, X), ONE),
    "pow_add": Equation(pw(X, add(Y, Z)), mul(pw(X, Y), pw(X, Z))),
    "pow_mul": Equation(pw(pw(X, Y), Z), pw(X, mul(Y, Z))),
    "mul_pow": Equation(pw(mul(X, Y), Z), mul(pw(X, Z), pw(Y, Z))),
}


def main() -> None:
    cfg = Config()
    if len(sys.argv) > 1:                 # optional wall-clock budget override
        cfg.time_budget_s = float(sys.argv[1])
    res = explore(cfg)

    named_index = {repr(canonical_eq(eq)): name for name, eq in NAMED.items()}
    reached = {}
    for name, eq, proof in res.proven:
        hit = named_index.get(repr(canonical_eq(eq)))
        if hit:
            reached[hit] = {"as": name, "statement": repr(eq),
                            "method": proof.method}

    report = {
        "config": {"max_term_size": cfg.max_term_size,
                   "time_budget_s": cfg.time_budget_s,
                   "max_rounds": cfg.max_rounds},
        "n_terms_enumerated": res.n_terms,
        "n_candidates": res.n_candidates,
        "rounds": res.rounds,
        "wall_seconds": round(res.wall_s, 1),
        "n_proven": len(res.proven),
        "named_targets": len(NAMED),
        "named_reached": len(reached),
        "named_detail": reached,
        "named_missed": sorted(set(NAMED) - set(reached)),
        "proven": [{"name": n, "statement": repr(e), "method": p.method,
                    "used": sorted(p.used)} for n, e, p in res.proven],
    }
    out = ROOT / "data" / "derived" / "probe_a_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"terms {res.n_terms} | candidates {res.n_candidates} | "
          f"rounds {res.rounds} | proven {len(res.proven)} | "
          f"{res.wall_s:.0f}s")
    print(f"named identities reached: {len(reached)}/{len(NAMED)} "
          f"(+{len(AXIOMS)} axioms)")
    for k, v in sorted(reached.items()):
        print(f"  [x] {k:14s} {v['statement']}  ({v['method']})")
    for k in report["named_missed"]:
        print(f"  [ ] {k}")
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
