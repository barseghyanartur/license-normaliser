#!/usr/bin/env python3
"""Apply alias additions to aliases.json.

Run from the repo root:
    uv run python scripts/apply_aliases_patch.py

What this does
--------------
1. Adds an ``"aliases"`` list to existing CC version-free entries so that
   the hyphenated forms (e.g. ``"cc-by-nc"``) resolve without needing a
   separate top-level key.
2. Adds new top-level entries for GPL shorthand keys that currently fall
   through to the unknown fallback (``gpl-2``, ``gpl-3``, ``gpl-v2``,
   ``gpl-v3``, ``agpl-3``, ``lgpl-3``).
"""

from __future__ import annotations

import json
from pathlib import Path

ALIASES_PATH = (
    Path(__file__).parent.parent
    / "src"
    / "license_normaliser"
    / "data"
    / "aliases"
    / "aliases.json"
)


def main() -> None:
    data: dict = json.loads(ALIASES_PATH.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # 1. CC version-free entries – add explicit aliases arrays
    # ------------------------------------------------------------------
    cc_aliases: dict[str, list[str]] = {
        # primary key -> extra alias keys to add
        "cc by-nc": ["cc-by-nc", "cc by nc", "cc-by nc"],
        "cc by-nd": ["cc-by-nd", "cc by nd", "cc-by nd"],
        "cc by-nc-sa": ["cc-by-nc-sa", "cc by nc-sa", "cc by nc sa", "cc-by nc-sa"],
        "cc by-nc-nd": ["cc-by-nc-nd", "cc by nc-nd", "cc by nc nd", "cc-by nc-nd"],
        "cc by-sa": ["cc-by-sa", "cc by sa", "cc-by sa"],
        "cc by": ["cc-by", "cc by"],  # cc-by already has its own entry but unify
    }

    for primary_key, extra_keys in cc_aliases.items():
        if primary_key not in data:
            print(f"  WARNING: primary key {primary_key!r} not found, skipping")
            continue
        existing = data[primary_key].get("aliases", [])
        merged = list(
            dict.fromkeys(existing + extra_keys)
        )  # deduplicate, preserve order
        data[primary_key]["aliases"] = merged
        print(f"  Updated aliases for {primary_key!r}: {merged}")

    # ------------------------------------------------------------------
    # 2. GPL shorthand entries (new top-level keys)
    # ------------------------------------------------------------------
    gpl_entries: dict[str, dict] = {
        "gpl-2": {
            "version_key": "gpl-2.0",
            "name_key": "gpl-2",
            "family_key": "copyleft",
            "aliases": ["gpl-v2", "gpl 2"],
        },
        "gpl-3": {
            "version_key": "gpl-3.0",
            "name_key": "gpl-3",
            "family_key": "copyleft",
            "aliases": ["gpl-v3", "gpl v3 only", "gpl 3"],
        },
        "agpl-3": {
            "version_key": "agpl-3.0",
            "name_key": "agpl-3",
            "family_key": "copyleft",
            "aliases": ["agpl-v3", "agpl 3"],
        },
        "lgpl-3": {
            "version_key": "lgpl-3.0",
            "name_key": "lgpl-3",
            "family_key": "copyleft",
            "aliases": ["lgpl-v3", "lgpl 3"],
        },
        "lgpl-2": {
            "version_key": "lgpl-2.1",
            "name_key": "lgpl-2.1",
            "family_key": "copyleft",
            "aliases": ["lgpl-v2", "lgpl 2", "lgpl-2.1-only", "lgpl-2.1-or-later"],
        },
    }

    for key, meta in gpl_entries.items():
        if key in data:
            print(f"  Skipping {key!r} – already present")
            continue
        data[key] = meta
        print(f"  Added new entry {key!r} -> {meta['version_key']}")

    # ------------------------------------------------------------------
    # Write back preserving formatting
    # ------------------------------------------------------------------
    ALIASES_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote updated aliases.json to {ALIASES_PATH}")


if __name__ == "__main__":
    main()
