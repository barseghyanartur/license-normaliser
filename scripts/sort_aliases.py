#!/usr/bin/env python3
"""Sort aliases.json keys alphabetically.

Comment keys (starting with '_') are preserved at the top in their original
order. All other entries are sorted case-insensitively.

Usage:
    uv run python scripts/sort_aliases.py
    uv run python scripts/sort_aliases.py --check
    # exit 1 if file is not already sorted
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ALIASES_PATH = (
    Path(__file__).parent.parent
    / "src"
    / "license_normaliser"
    / "data"
    / "aliases"
    / "aliases.json"
)


def sort_aliases(data: dict) -> dict:
    """Return a new dict with comment keys first, then entries sorted A-Z."""
    comments = {k: v for k, v in data.items() if k.startswith("_")}
    entries = {k: v for k, v in data.items() if not k.startswith("_")}
    sorted_entries = dict(sorted(entries.items(), key=lambda kv: kv[0].lower()))
    return {**comments, **sorted_entries}


def main() -> None:
    parser = argparse.ArgumentParser(description="Sort aliases.json alphabetically.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check only — exit 1 if the file is not already sorted.",
    )
    args = parser.parse_args()

    raw = ALIASES_PATH.read_text(encoding="utf-8")
    data: dict = json.loads(raw)

    sorted_data = sort_aliases(data)
    sorted_text = json.dumps(sorted_data, indent=2, ensure_ascii=False) + "\n"

    if args.check:
        if raw == sorted_text:
            print("aliases.json is already sorted.")
            sys.exit(0)
        else:
            # Show which keys are out of order
            original_keys = [k for k in data if not k.startswith("_")]
            sorted_keys = [k for k in sorted_data if not k.startswith("_")]
            for i, (orig, expected) in enumerate(
                zip(original_keys, sorted_keys, strict=False)
            ):
                if orig != expected:
                    print(
                        f"First out-of-order key at position {i}: {orig!r} "
                        f"(expected {expected!r})"
                    )
                    break
            print("aliases.json is NOT sorted. Run without --check to fix.")
            sys.exit(1)

    ALIASES_PATH.write_text(sorted_text, encoding="utf-8")
    print(
        f"Sorted "
        f"{len(sorted_data) - len([k for k in data if k.startswith('_')])} "
        f"entries in {ALIASES_PATH}"
    )


if __name__ == "__main__":
    main()
