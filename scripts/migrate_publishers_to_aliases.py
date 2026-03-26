#!/usr/bin/env python3
"""Migrate publishers.json (urls + shorthand_aliases) into aliases/aliases.json.

Adds:
  - URLs to the "urls" array
  - Shorthand aliases to the "aliases" array

Run AFTER the url_map migration (or on the already-merged file).

::

    # Dry-run: shows summary + writes aliases.dryrun.json
    uv run python scripts/migrate_publishers_to_aliases.py --dry-run

    # Real migration: overwrites aliases.json
    uv run python scripts/migrate_publishers_to_aliases.py

"""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "licence_normaliser" / "data"

ALIASES_PATH = DATA_DIR / "aliases" / "aliases.json"
PUBLISHERS_PATH = DATA_DIR / "publishers" / "publishers.json"
OUTPUT_PATH = DATA_DIR / "aliases" / "aliases.merged.json"


def normalise_url(url: str) -> str:
    """Normalise URL exactly as _normaliser.py does at runtime."""
    key = url.strip().lower().rstrip("/")
    if key.startswith("http://"):
        key = "https://" + key[7:]
    return key


def main() -> None:
    # Load aliases (preserve _comment keys and original ordering)
    with open(ALIASES_PATH, encoding="utf-8") as f:
        aliases_content = f.read()
    aliases_data: dict = json.loads(aliases_content)

    # Load publishers
    with open(PUBLISHERS_PATH, encoding="utf-8") as f:
        publishers: dict = json.loads(f.read())

    # Build reverse lookup: version_key → entry
    version_to_entry: dict[str, dict] = {}
    for key, meta in aliases_data.items():
        if key.startswith("_") or not isinstance(meta, dict):
            continue
        vk = meta.get("version_key")
        if vk:
            version_to_entry[vk] = meta

    urls_added = 0
    aliases_added = 0
    new_entries_created = 0

    # 1. Process URLs
    for raw_url, meta in publishers.get("urls", {}).items():
        if not isinstance(meta, dict):
            continue
        vk = meta.get("version_key")
        if not vk:
            continue

        entry = version_to_entry.get(vk)
        if entry is None:
            # Create minimal entry
            entry = {
                "version_key": vk,
                "name_key": meta.get("name_key", vk),
                "family_key": meta.get("family_key", "unknown"),
                "aliases": [],
                "urls": [],
            }
            aliases_data[vk] = entry
            version_to_entry[vk] = entry
            new_entries_created += 1
            print(f"Created new alias entry for {vk}")

        if "urls" not in entry or not isinstance(entry["urls"], list):
            entry["urls"] = []

        norm_url = normalise_url(raw_url)
        if norm_url not in entry["urls"]:
            entry["urls"].append(norm_url)
            urls_added += 1

    # 2. Process shorthand_aliases
    for alias_key, vk in publishers.get("shorthand_aliases", {}).items():
        if not isinstance(alias_key, str) or not isinstance(vk, str):
            continue

        entry = version_to_entry.get(vk)
        if entry is None:
            # Should be extremely rare after url_map migration
            entry = {
                "version_key": vk,
                "name_key": vk,
                "family_key": "unknown",
                "aliases": [],
                "urls": [],
            }
            aliases_data[vk] = entry
            version_to_entry[vk] = entry
            new_entries_created += 1
            print(f"Created new alias entry for {vk} (from shorthand)")

        if "aliases" not in entry or not isinstance(entry["aliases"], list):
            entry["aliases"] = []

        if alias_key not in entry["aliases"] and alias_key != vk:
            entry["aliases"].append(alias_key)
            aliases_added += 1

    # Write merged file
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(aliases_data, f, indent=2, ensure_ascii=False)

    print("\nPublishers migration completed successfully!")
    print(f"   URLs added          : {urls_added}")
    print(f"   Shorthand aliases added : {aliases_added}")
    print(f"   New entries created : {new_entries_created}")
    print(f"   Output written to   : {OUTPUT_PATH}")
    print("\nNext steps:")
    print("1. Review aliases.merged.json")
    print("2. If happy, replace aliases.json with it")
    print("3. Delete (or deprecate) data/publishers/ and data/urls/")
    print("4. Update compare_datasets.py, tests, and parsers accordingly")


if __name__ == "__main__":
    main()
