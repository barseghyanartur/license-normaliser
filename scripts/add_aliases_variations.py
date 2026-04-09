#!/usr/bin/env python3
"""Add alias variations to entries in aliases.json.

For each entry, generates variants by combining spaces/hyphens between segments.
Skips variants that already exist or match the entry key.

Run with --dry-run first to review changes.

::

    # Dry-run: show what would be added
    uv run python scripts/add_aliases_variations.py --dry-run

    # Interactive mode
    uv run python scripts/add_aliases_variations.py
"""

from __future__ import annotations

import argparse
import json
from itertools import product
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "licence_normaliser" / "data"

ALIASES_PATH = DATA_DIR / "aliases" / "aliases.json"
DRYRUN_PATH = DATA_DIR / "aliases" / "aliases.dryrun.json"


def segment_key(version_key: str) -> list[str]:
    """Split version_key into segments (cc, by, nc, sa, 1.0)."""
    return version_key.replace("-", " ").split()


def generate_variants(version_key: str) -> list[str]:
    """Generate all space/hyphen variants of a version key."""
    segments = segment_key(version_key)
    if len(segments) < 2:
        return [version_key]

    core_segments = segments[:-1]
    version = segments[-1]

    variants: set[str] = set()

    for hyphens in product([False, True], repeat=len(core_segments) - 1):
        parts = []
        for i, seg in enumerate(core_segments):
            parts.append(seg)
            if i < len(hyphens) and hyphens[i]:
                parts.append("-")
            else:
                parts.append(" ")

        parts.append(version)
        variant = "".join(parts).strip()
        variants.add(variant)

    return sorted(variants)


def collect_existing_aliases(entry_key: str, meta: dict) -> set[str]:
    """Collect all aliases that already exist for this entry."""
    existing = set()

    existing.add(entry_key)

    vk = meta.get("version_key")
    if vk:
        existing.add(vk)

    for alias in meta.get("aliases", []):
        existing.add(alias)

    return existing


def find_missing_variants(entry_key: str, meta: dict) -> list[str]:
    """Find variants that are missing from aliases list."""
    version_key = meta.get("version_key")
    if not version_key:
        return []

    existing = collect_existing_aliases(entry_key, meta)

    variants = generate_variants(version_key)

    missing = [v for v in variants if v not in existing and v != entry_key]

    return missing


def format_entry(key: str, data: dict, is_last: bool) -> str:
    """Format entry with multiline arrays."""
    lines = [f'  "{key}": {{']

    field_order = ["version_key", "name_key", "family_key", "aliases", "urls"]

    fields_to_write = [fn for fn in field_order if fn in data]
    fields_to_write.extend(fn for fn in data if fn not in field_order)

    for i, field_name in enumerate(fields_to_write):
        is_field_last = i == len(fields_to_write) - 1
        value = data[field_name]

        if isinstance(value, list):
            if not value:
                lines.append(
                    f'    "{field_name}": []'
                    if is_field_last
                    else f'    "{field_name}": [],'
                )
            else:
                lines.append(f'    "{field_name}": [')
                for j, item in enumerate(value):
                    is_last_item = j == len(value) - 1
                    suffix = "" if is_last_item else ","
                    if isinstance(item, str):
                        lines.append(f'      "{item}"{suffix}')
                    else:
                        lines.append(f"      {item}{suffix}")
                lines.append("    ]" if is_field_last else "    ],")
        else:
            suffix = "" if is_field_last else ","
            lines.append(f'    "{field_name}": {json.dumps(value)}{suffix}')

    lines.append("  }")
    result = "\n".join(lines)
    if not is_last:
        result += ","

    return result


def write_aliases(
    aliases_data: dict,
    output_path: Path,
) -> None:
    """Write aliases.json preserving format."""
    comment_keys = sorted([k for k in aliases_data if k.startswith("_")])
    entry_keys = sorted(
        [k for k in aliases_data if not k.startswith("_")],
        key=lambda x: x.lower(),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("{\n")

        for ck in comment_keys:
            f.write(f'  "{ck}": {json.dumps(aliases_data[ck])}')
            f.write(",\n")

        f.write("\n")

        for i, ek in enumerate(entry_keys):
            is_last = i == len(entry_keys) - 1
            entry_str = format_entry(ek, aliases_data[ek], is_last)
            f.write(entry_str)
            f.write("\n\n")

        f.write("}\n")


def interactive_add(
    entries_needing_variants: list[tuple[str, dict, list[str]]],
    aliases_data: dict,
) -> int:
    """Interactive prompt for each entry."""
    if not entries_needing_variants:
        print("\nNo entries need additional variants!")
        return 0

    print("\n" + "=" * 60)
    print("Entries Needing Alias Variants")
    print("=" * 60)

    to_add_count = 0

    for i, (entry_key, meta, missing) in enumerate(entries_needing_variants):
        version_key = meta.get("version_key", "")
        print(f"\n[{i + 1}/{len(entries_needing_variants)}] Entry: {entry_key}")
        print(f"    version_key: {version_key}")
        print(f"    Missing variants ({len(missing)}):")
        for v in missing[:5]:
            print(f"      - {v}")
        if len(missing) > 5:
            print(f"      ... and {len(missing) - 5} more")

        while True:
            response = (
                input("    Add variants? [y]es/[n]o/[a]ll/[q]uit: ").strip().lower()
            )
            if response in ("y", ""):
                if "aliases" not in aliases_data[entry_key]:
                    aliases_data[entry_key]["aliases"] = []
                aliases_data[entry_key]["aliases"].extend(missing)
                to_add_count += len(missing)
                break
            elif response == "n":
                break
            elif response == "a":
                for ek, _m, miss in entries_needing_variants[i:]:
                    if "aliases" not in aliases_data[ek]:
                        aliases_data[ek]["aliases"] = []
                    aliases_data[ek]["aliases"].extend(miss)
                    to_add_count += len(miss)
                print("\nAdded all variants")
                break
            elif response == "q":
                print("\nQuitting...")
                return to_add_count
            else:
                print("    Please enter: y (yes), n (no), a (all), or q (quit)")

    return to_add_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Add alias variations to aliases.json")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Write to aliases.dryrun.json instead of aliases.json",
    )
    parser.add_argument(
        "--family",
        type=str,
        default=None,
        help="Filter by family_key (e.g., cc, osi, copyleft)",
    )
    args = parser.parse_args()

    with open(ALIASES_PATH, encoding="utf-8") as f:
        aliases_content = f.read()

    aliases_data: dict = json.loads(aliases_content)

    entries_needing_variants: list[tuple[str, dict, list[str]]] = []

    for entry_key, meta in aliases_data.items():
        if entry_key.startswith("_") or not isinstance(meta, dict):
            continue

        if args.family and meta.get("family_key") != args.family:
            continue

        missing = find_missing_variants(entry_key, meta)
        if missing:
            entries_needing_variants.append((entry_key, meta, missing))

    total_entries = len(entries_needing_variants)
    total_variants = sum(len(m) for _, _, m in entries_needing_variants)

    print(f"\nEntries checked: {len(aliases_data)}")
    print(f"Entries needing variants: {total_entries}")
    print(f"Total new variants: {total_variants}")

    if args.dry_run:
        print("\nDry-run mode - no changes will be made")
        if total_variants > 0:
            print("\nPreview (first 5 entries):")
            for entry_key, _meta, missing in entries_needing_variants[:5]:
                print(f"  {entry_key}:")
                for v in missing[:3]:
                    print(f"    + {v}")
                if len(missing) > 3:
                    print(f"    ... +{len(missing) - 3} more")
        print("\nRun without --dry-run to add variants interactively")
        return

    if not entries_needing_variants:
        print("\nNo changes needed.")
        return

    to_add_count = interactive_add(entries_needing_variants, aliases_data)

    if to_add_count > 0:
        output_path = DRYRUN_PATH if args.dry_run else ALIASES_PATH
        write_aliases(aliases_data, output_path)
        print(f"\nAdded {to_add_count} variants")
        print(f"Written to: {output_path}")


if __name__ == "__main__":
    main()
