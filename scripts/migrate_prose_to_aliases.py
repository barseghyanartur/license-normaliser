#!/usr/bin/env python3
"""Migrate prose_patterns.json into aliases/aliases.json.

Adds a new 'patterns' array to each matching entry containing regex patterns.

The script:
- Matches by version_key in the entry
- Preserves exact format (2-space indent, blank lines, ordering)
- Adds entries in alphabetical order by version_key
- Is idempotent — running multiple times adds nothing new

::

   # Dry-run: shows summary + writes aliases.dryrun.json
   uv run python scripts/migrate_prose_to_aliases.py --dry-run

   # Real migration: overwrites aliases.json
   uv run python scripts/migrate_prose_to_aliases.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "licence_normaliser" / "data"

ALIASES_PATH = DATA_DIR / "aliases" / "aliases.json"
PROSE_PATH = DATA_DIR / "prose" / "prose_patterns.json"
DRYRUN_PATH = DATA_DIR / "aliases" / "aliases.dryrun.json"


def build_entry_lookup(aliases_data: dict) -> dict[str, str]:
    """Build lookup table from version_key to entry key."""
    version_key_to_entry_key: dict[str, str] = {}

    for entry_key, meta in aliases_data.items():
        if entry_key.startswith("_") or not isinstance(meta, dict):
            continue

        vk = meta.get("version_key")
        if vk:
            version_key_to_entry_key[vk] = entry_key

    return version_key_to_entry_key


def format_entry_with_multiline_arrays(key: str, data: dict, is_last: bool) -> str:
    """Format entry with multiline arrays like the original format."""
    lines = [f'  "{key}": {{']

    field_order = [
        "version_key",
        "name_key",
        "family_key",
        "aliases",
        "justification",
        "urls",
        "patterns",
    ]

    fields_to_write = [fn for fn in field_order if fn in data]
    fields_to_write.extend(fn for fn in data if fn not in field_order)

    for i, field_name in enumerate(fields_to_write):
        is_field_last = i == len(fields_to_write) - 1
        value = data[field_name]

        if isinstance(value, list):
            if not value:
                if not is_field_last:
                    lines.append(f'    "{field_name}": [],')
                else:
                    lines.append(f'    "{field_name}": []')
            else:
                lines.append(f'    "{field_name}": [')
                for j, item in enumerate(value):
                    is_last_item = j == len(value) - 1
                    suffix = "" if is_last_item else ","
                    if isinstance(item, str):
                        lines.append(f"      {json.dumps(item)}{suffix}")
                    else:
                        lines.append(f"      {item}{suffix}")
                if not is_field_last:
                    lines.append("    ],")
                else:
                    lines.append("    ]")
        else:
            suffix = "" if is_field_last else ","
            if isinstance(value, str):
                lines.append(f'    "{field_name}": "{value}"{suffix}')
            elif value is None:
                lines.append(f'    "{field_name}": null{suffix}')
            elif isinstance(value, bool):
                lines.append(
                    f'    "{field_name}": {"true" if value else "false"}{suffix}'
                )
            else:
                lines.append(f'    "{field_name}": {value}{suffix}')

    lines.append("  }")

    result = "\n".join(lines)
    if not is_last:
        result += ","

    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Migrate prose_patterns.json into aliases.json"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write to aliases.dryrun.json instead of aliases.json",
    )
    args = parser.parse_args()

    with open(ALIASES_PATH, encoding="utf-8") as f:
        aliases_content = f.read()

    with open(PROSE_PATH, encoding="utf-8") as f:
        prose_patterns: list[dict] = json.loads(f.read())

    aliases_data: dict = json.loads(aliases_content)

    version_key_to_entry_key = build_entry_lookup(aliases_data)

    patterns_added = 0
    unmatched: list[tuple[str, str]] = []

    for entry in prose_patterns:
        pattern = entry.get("pattern", "")
        version_key = entry.get("version_key", "")

        if not pattern or not version_key:
            continue

        entry_key = version_key_to_entry_key.get(version_key)

        if entry_key is None:
            unmatched.append((pattern, version_key))
            continue

        entry = aliases_data[entry_key]
        if "patterns" not in entry:
            entry["patterns"] = []

        if pattern not in entry["patterns"]:
            entry["patterns"].append(pattern)
            patterns_added += 1

    output_path = DRYRUN_PATH if args.dry_run else ALIASES_PATH

    comment_keys = sorted([k for k in aliases_data if k.startswith("_")])
    entry_keys = sorted(
        [k for k in aliases_data if not k.startswith("_")],
        key=lambda x: x.lower(),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("{\n")

        for ck in comment_keys:
            f.write(f'  "{ck}": {json.dumps(aliases_data[ck])}')
            f.write(",")
            f.write("\n")

        f.write("\n")

        for i, ek in enumerate(entry_keys):
            is_last = i == len(entry_keys) - 1
            entry_str = format_entry_with_multiline_arrays(
                ek, aliases_data[ek], is_last
            )
            f.write(entry_str)
            f.write("\n\n")

        f.write("}\n")

    print("\nMigration summary:")
    print(f"  Patterns added    : {patterns_added}")
    print(f"  Unmatched        : {len(unmatched)}")

    if unmatched:
        print("\nUnmatched patterns (no matching alias entry):")
        for pattern, vk in unmatched[:10]:
            print(f'  pattern="{pattern}" -> version_key="{vk}"')
        if len(unmatched) > 10:
            print(f"  ... and {len(unmatched) - 10} more")

    if args.dry_run:
        print(f"\nDry-run output written to: {output_path}")
        print("Review the file, then run without --dry-run to apply.")
    else:
        print(f"\nMigration completed. Output written to: {output_path}")


if __name__ == "__main__":
    main()
