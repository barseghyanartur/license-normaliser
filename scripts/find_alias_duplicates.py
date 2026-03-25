#!/usr/bin/env python3
"""Find (and optionally fix) duplicate version_key entries in aliases.json.

A "duplicate" is two or more top-level primary keys that share the same
version_key.  In that situation the extra keys are redundant because they
could live in the ``aliases`` list of a single canonical entry.

Detection
---------
Groups every primary key by its ``version_key`` and reports groups with
more than one member.

Fix strategy (``--fix``)
------------------------
For each duplicate group:

1. If exactly one entry already has an ``aliases`` list  →  merge the other
   primary key(s) into that entry's ``aliases`` list and remove the now-
   redundant top-level key(s).

2. If *no* entry has an ``aliases`` list  →  pick the shortest primary key
   as the canonical one (ties broken alphabetically), attach the others as
   ``aliases``, and remove the extra top-level keys.

3. If *more than one* entry has an ``aliases`` list  →  report a conflict
   with line numbers and leave the file untouched (for that group).

Usage
-----
    uv run python scripts/find_alias_duplicates.py

    uv run python scripts/find_alias_duplicates.py --fix

    # machine-readable report
    uv run python scripts/find_alias_duplicates.py --json

    # fix + JSON summary
    uv run python scripts/find_alias_duplicates.py --fix --json
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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _line_of_key(key: str, lines: list[str]) -> int:
    """Return the 1-based line number where ``key`` appears as a JSON key."""
    needle = f'"{key}"'
    for i, line in enumerate(lines, start=1):
        if needle in line:
            return i
    return -1


def _find_duplicates(data: dict, lines: list[str]) -> dict[str, list[dict]]:
    """
    Return mapping version_key -> list of {primary_key, line, has_aliases}.
    """
    groups: dict[str, list[dict]] = {}
    for primary_key, meta in data.items():
        if primary_key.startswith("_"):
            continue
        if not isinstance(meta, dict):
            continue
        vk = meta.get("version_key", "")
        if not vk:
            continue
        groups.setdefault(vk, []).append(
            {
                "primary_key": primary_key,
                "line": _line_of_key(primary_key, lines),
                "has_aliases": bool(meta.get("aliases")),
            }
        )
    return {vk: members for vk, members in groups.items() if len(members) > 1}


# ---------------------------------------------------------------------------
# Fix logic
# ---------------------------------------------------------------------------


def _apply_fix(
    data: dict, duplicates: dict[str, list[dict]]
) -> tuple[dict, list[dict], list[dict]]:
    """Return (updated_data, fixed_groups, conflicted_groups).

    fixed_groups     – list of {version_key, canonical_key, merged_keys}
    conflicted_groups – list of {version_key, keys_with_aliases}
    """
    fixed: list[dict] = []
    conflicts: list[dict] = []

    for vk, members in duplicates.items():
        keys_with_aliases = [m for m in members if m["has_aliases"]]

        if len(keys_with_aliases) > 1:
            conflicts.append(
                {
                    "version_key": vk,
                    "keys_with_aliases": [
                        {"primary_key": m["primary_key"], "line": m["line"]}
                        for m in keys_with_aliases
                    ],
                }
            )
            continue

        # Determine canonical entry
        if len(keys_with_aliases) == 1:
            canonical_key = keys_with_aliases[0]["primary_key"]
        else:
            # No aliases anywhere – pick shortest key, ties broken alpha
            canonical_key = sorted(
                [m["primary_key"] for m in members],
                key=lambda k: (len(k), k),
            )[0]

        others = [
            m["primary_key"] for m in members if m["primary_key"] != canonical_key
        ]

        # Merge others into canonical aliases list
        canonical_meta = data[canonical_key]
        existing_aliases: list[str] = list(canonical_meta.get("aliases", []))
        for other_key in others:
            other_meta = data[other_key]
            # The other primary key itself becomes an alias
            if other_key not in existing_aliases and other_key != canonical_key:
                existing_aliases.append(other_key)
            # Carry over any aliases the other entry already had
            for a in other_meta.get("aliases", []):
                if a not in existing_aliases and a != canonical_key:
                    existing_aliases.append(a)
            del data[other_key]

        canonical_meta["aliases"] = existing_aliases
        fixed.append(
            {
                "version_key": vk,
                "canonical_key": canonical_key,
                "merged_keys": others,
            }
        )

    return data, fixed, conflicts


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _print_report(
    duplicates: dict[str, list[dict]],
    fixed: list[dict] | None = None,
    conflicts: list[dict] | None = None,
) -> None:
    if not duplicates:
        print("No duplicate version_keys found.")
        return

    print(f"Found {len(duplicates)} duplicate version_key group(s):\n")
    for vk, members in sorted(duplicates.items()):
        print(f"  version_key: {vk!r}")
        for m in members:
            alias_flag = "  [has aliases]" if m["has_aliases"] else ""
            print(f"    line {m['line']:>4}  {m['primary_key']!r}{alias_flag}")
        print()

    if fixed:
        print(f"Fixed {len(fixed)} group(s):")
        for f in fixed:
            print(
                f"  {f['version_key']!r}: kept {f['canonical_key']!r}, "
                f"merged {f['merged_keys']}"
            )
        print()

    if conflicts:
        print(f"Conflicts (not fixed) – {len(conflicts)} group(s):")
        for c in conflicts:
            print(f"  {c['version_key']!r}: multiple entries already have aliases:")
            for entry in c["keys_with_aliases"]:
                print(f"    line {entry['line']:>4}  {entry['primary_key']!r}")
        print()


def _print_json(
    duplicates: dict[str, list[dict]],
    fixed: list[dict] | None = None,
    conflicts: list[dict] | None = None,
) -> None:
    out = {
        "duplicate_count": len(duplicates),
        "duplicates": dict(sorted(duplicates.items())),
    }
    if fixed is not None:
        out["fixed"] = fixed
    if conflicts is not None:
        out["conflicts"] = conflicts
    print(json.dumps(out, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find (and optionally fix) duplicate version_keys in aliases.json."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help=(
            "Merge duplicate entries into a single canonical entry with "
            "an aliases list."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    args = parser.parse_args()

    content = ALIASES_PATH.read_text(encoding="utf-8")
    data: dict = json.loads(content)
    lines = content.splitlines()

    duplicates = _find_duplicates(data, lines)

    if not args.fix:
        if args.json:
            _print_json(duplicates)
        else:
            _print_report(duplicates)
        sys.exit(1 if duplicates else 0)

    # --fix path
    data, fixed, conflicts = _apply_fix(data, duplicates)

    if fixed:
        ALIASES_PATH.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        _print_json(duplicates, fixed, conflicts)
    else:
        _print_report(duplicates, fixed, conflicts)

    sys.exit(1 if conflicts else 0)


if __name__ == "__main__":
    main()
