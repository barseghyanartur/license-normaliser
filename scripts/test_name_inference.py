"""Test name inference accuracy against curated aliases.

Compares heuristic name stripping against curated name_key values from
aliases.json to assess how well automatic name extraction works.

Usage:
    uv run python scripts/test_name_inference.py
    uv run python scripts/test_name_inference.py --json
    uv run python scripts/test_name_inference.py --json --incorrect-only
    uv run python scripts/test_name_inference.py --json --details
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from licence_normaliser import LicenceNormaliser

DATA_DIR = Path(__file__).parent.parent / "src" / "licence_normaliser" / "data"
SCRIPTS_DIR = Path(__file__).parent

_normaliser = LicenceNormaliser()


def load_name_mappings() -> dict[str, str]:
    """Load version_key -> name_key mappings from aliases.json."""
    with open(DATA_DIR / "aliases" / "aliases.json") as f:
        data = json.load(f)
    mappings: dict[str, str] = {}
    for meta in data.values():
        if isinstance(meta, dict):
            vk = meta.get("version_key", "")
            nk = meta.get("name_key", "")
            if vk and nk:
                mappings[vk] = nk
    return mappings


def infer_name_heuristic(version_key: str) -> str:
    """Delegate to the core LicenceNormaliser's _infer_name method."""
    return _normaliser._infer_name(version_key)


def categorize_by_family(mappings: dict[str, str]) -> dict[str, dict[str, str]]:
    """Categorize licences by inferred family."""
    categories: dict[str, dict[str, str]] = {
        "cc": {},  # Creative Commons
        "copyleft": {},  # GPL/AGPL/LGPL
        "osi": {},  # OSI-approved
        "other": {},
    }

    for vk, nk in mappings.items():
        if vk.startswith("cc-"):
            categories["cc"][vk] = nk
        elif vk.startswith(("gpl-", "agpl-", "lgpl-")):
            categories["copyleft"][vk] = nk
        elif vk.startswith(
            ("mpl-", "apache-", "bsd-", "mit", "isc", "unlicense", "zlib")
        ):
            categories["osi"][vk] = nk
        else:
            categories["other"][vk] = nk

    return categories


def assess_accuracy() -> dict:
    """Assess name inference accuracy."""
    mappings = load_name_mappings()
    categories = categorize_by_family(mappings)

    results: dict = {
        "total_mappings": len(mappings),
        "by_family": {},
    }

    for family, family_mappings in categories.items():
        correct = 0
        incorrect = 0
        details: list[dict] = []

        for vk, curated_nk in family_mappings.items():
            inferred = infer_name_heuristic(vk)
            is_match = inferred == curated_nk
            if is_match:
                correct += 1
            else:
                incorrect += 1

            details.append(
                {
                    "version_key": vk,
                    "curated_name": curated_nk,
                    "inferred_name": inferred,
                    "match": is_match,
                }
            )

        accuracy = (
            round(correct / len(family_mappings) * 100, 1) if family_mappings else 0
        )

        results["by_family"][family] = {
            "total": len(family_mappings),
            "correct": correct,
            "incorrect": incorrect,
            "accuracy_percent": accuracy,
            "details": details,
        }

    # Overall accuracy
    all_correct = sum(r["correct"] for r in results["by_family"].values())
    all_total = sum(r["total"] for r in results["by_family"].values())
    results["overall_accuracy"] = (
        round(all_correct / all_total * 100, 1) if all_total else 0
    )

    return results


def print_report(data: dict) -> None:
    """Print text table report."""
    print("=" * 70)
    print("Name Inference Accuracy Report")
    print("=" * 70)
    print()
    print(f"Total curated mappings: {data['total_mappings']}")
    print(f"Overall accuracy: {data['overall_accuracy']}%")
    print()

    print("-" * 70)
    print("By Family:")
    print("-" * 70)
    print(
        f"{'Family':<15} {'Total':>8} {'Correct':>8} {'Incorrect':>8} {'Accuracy':>10}"
    )
    print("-" * 70)

    for family, stats in data["by_family"].items():
        print(
            f"{family:<15} {stats['total']:>8} {stats['correct']:>8} "
            f"{stats['incorrect']:>8} {stats['accuracy_percent']:>9.1f}%"
        )

    print()

    # Show some incorrect examples
    for family, stats in data["by_family"].items():
        if stats["incorrect"] > 0:
            print("-" * 70)
            print(f"Incorrect in {family}: {stats['incorrect']} cases")
            print("-" * 70)
            print(
                f"{'Version Key':<30} {'Curated (aliases.json)':<25} "
                f"{'Inferred (heuristic)':<20}"
            )
            print("-" * 70)
            for detail in stats["details"][:10]:
                if not detail["match"]:
                    print(
                        f"{detail['version_key']:<30} "
                        f"{detail['curated_name']:<25} {detail['inferred_name']:<20}"
                    )
            incorrect_count = len([d for d in stats["details"] if not d["match"]])
            if incorrect_count > 10:
                print(f"... and {incorrect_count - 10} more")
            print()


def main() -> None:
    json_export = "--json" in sys.argv
    incorrect_only = "--incorrect-only" in sys.argv
    include_details = "--details" in sys.argv
    data = assess_accuracy()

    if json_export:
        for family in data["by_family"]:
            details = data["by_family"][family].get("details", [])
            if incorrect_only:
                data["by_family"][family]["details"] = [
                    d for d in details if not d["match"]
                ]
            elif not include_details:
                data["by_family"][family].pop("details", None)
        print(json.dumps(data, indent=2))
    else:
        print_report(data)


if __name__ == "__main__":
    main()
