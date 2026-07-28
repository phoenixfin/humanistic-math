"""Central path resolution so scripts can target either the full substrate
or a smaller named variant (e.g. "prop" for the propositional-calculus
slice) without duplicating filenames everywhere."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _suffix(variant: str) -> str:
    return f"_{variant}" if variant else ""


def substrate_path(variant: str = "") -> Path:
    return ROOT / "data" / "derived" / f"substrate{_suffix(variant)}.jsonl"


def measures_path(variant: str = "") -> Path:
    return ROOT / "data" / "derived" / f"measures{_suffix(variant)}.json"


def label_sample_path(variant: str = "") -> Path:
    return ROOT / "data" / "labels" / f"label_sample{_suffix(variant)}.csv"


def labels_filled_path(variant: str = "") -> Path:
    return ROOT / "data" / "labels" / f"labels_filled{_suffix(variant)}.csv"


def results_json_path(variant: str = "") -> Path:
    return ROOT / "reports" / f"results{_suffix(variant)}.json"


def results_md_path(variant: str = "") -> Path:
    return ROOT / "reports" / f"RESULTS{_suffix(variant)}.md"
