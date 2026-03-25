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
For each duplicate group the proposed merge is shown and confirmation is
requested before any change is made.  At the prompt:

    y  - apply this merge
    n  - skip this group (leave the file unchanged for it)
    q  - quit immediately, writing only the merges accepted so far

Pass ``--noinput`` to apply all safe merges without prompting (useful in
scripts / CI after you have reviewed the output once).

Per-group rules:

1. If exactly one entry already has an ``aliases`` list  ->  merge the other
   primary key(s) into that entry's ``aliases`` list and remove the now-
   redundant top-level key(s).

2. If *no* entry has an ``aliases`` list  ->  pick the shortest primary key
   as the canonical one (ties broken alphabetically), attach the others as
   ``aliases``, and remove the extra top-level keys.

3. If *more than one* entry has an ``aliases`` list  ->  report a conflict
   with line numbers and skip regardless of ``--noinput``.

Usage
-----
    uv run python scripts/find_alias_duplicates.py

    uv run python scripts/find_alias_duplicates.py --fix

    # apply without prompting
    uv run python scripts/find_alias_duplicates.py --fix --noinput

    # machine-readable report
    uv run python scripts/find_alias_duplicates.py --json

    # fix + JSON summary (implies --noinput)
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
    """Return mapping version_key -> list of {primary_key, line, has_aliases}."""
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


def _plan_merge(vk: str, members: list[dict]) -> dict:
    """Return a merge plan dict.

    Plan keys:
        version_key      - the shared version_key
        canonical_key    - primary key that will survive
        merge_keys       - primary keys to be removed and absorbed
        conflict         - True when the group cannot be auto-merged
        conflict_detail  - list of {primary_key, line} for conflicted entries
    """
    keys_with_aliases = [m for m in members if m["has_aliases"]]

    if len(keys_with_aliases) > 1:
        return {
            "version_key": vk,
            "conflict": True,
            "conflict_detail": [
                {"primary_key": m["primary_key"], "line": m["line"]}
                for m in keys_with_aliases
            ],
        }

    if len(keys_with_aliases) == 1:
        canonical_key = keys_with_aliases[0]["primary_key"]
    else:
        canonical_key = sorted(
            [m["primary_key"] for m in members],
            key=lambda k: (len(k), k),
        )[0]

    merge_keys = [
        m["primary_key"] for m in members if m["primary_key"] != canonical_key
    ]

    return {
        "version_key": vk,
        "conflict": False,
        "canonical_key": canonical_key,
        "merge_keys": merge_keys,
    }


def _apply_plan(data: dict, plan: dict) -> None:
    """Mutate ``data`` in-place according to ``plan``."""
    canonical_key = plan["canonical_key"]
    canonical_meta = data[canonical_key]
    existing_aliases: list[str] = list(canonical_meta.get("aliases", []))

    for other_key in plan["merge_keys"]:
        other_meta = data[other_key]
        if other_key not in existing_aliases and other_key != canonical_key:
            existing_aliases.append(other_key)
        for a in other_meta.get("aliases", []):
            if a not in existing_aliases and a != canonical_key:
                existing_aliases.append(a)
        del data[other_key]

    canonical_meta["aliases"] = existing_aliases


# ---------------------------------------------------------------------------
# Interactive confirmation
# ---------------------------------------------------------------------------


def _describe_plan(plan: dict, lines: list[str]) -> str:
    """Return a human-readable description of a merge plan."""
    vk = plan["version_key"]
    canonical = plan["canonical_key"]
    parts = [
        f"  version_key : {vk!r}",
        f"  keep        : {canonical!r}  (aliases list stays here)",
    ]
    for mk in plan["merge_keys"]:
        line = _line_of_key(mk, lines)
        parts.append(
            f"  merge       : {mk!r}  (line {line})"
            f" -> absorbed into aliases of {canonical!r}"
        )
    return "\n".join(parts)


def _confirm(plan: dict, lines: list[str]) -> str:
    """Prompt the user and return 'y', 'n', or 'q'."""
    print()
    print(_describe_plan(plan, lines))
    while True:
        try:
            answer = input("  Apply this merge? [y/n/q] ").strip().lower()
        except EOFError:
            return "q"
        if answer in ("y", "n", "q"):
            return answer
        print("  Please enter y (yes), n (skip), or q (quit).")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _print_report(
    duplicates: dict[str, list[dict]],
    fixed: list[dict] | None = None,
    skipped: list[str] | None = None,
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
                f"merged {f['merge_keys']}"
            )
        print()

    if skipped:
        print(f"Skipped {len(skipped)} group(s) (user declined):")
        for vk in skipped:
            print(f"  {vk!r}")
        print()

    if conflicts:
        print(f"Conflicts (not fixed) - {len(conflicts)} group(s):")
        for c in conflicts:
            print(f"  {c['version_key']!r}: multiple entries already have aliases:")
            for entry in c["conflict_detail"]:
                print(f"    line {entry['line']:>4}  {entry['primary_key']!r}")
        print()


def _print_json(
    duplicates: dict[str, list[dict]],
    fixed: list[dict] | None = None,
    skipped: list[str] | None = None,
    conflicts: list[dict] | None = None,
) -> None:
    out: dict = {
        "duplicate_count": len(duplicates),
        "duplicates": dict(sorted(duplicates.items())),
    }
    if fixed is not None:
        out["fixed"] = fixed
    if skipped is not None:
        out["skipped"] = skipped
    if conflicts is not None:
        out["conflicts"] = conflicts
    print(json.dumps(out, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Find (and optionally fix) duplicate version_keys in aliases.json."
        )
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Merge duplicate entries into a single canonical entry.",
    )
    parser.add_argument(
        "--noinput",
        action="store_true",
        default=False,
        help=(
            "Apply all safe merges without prompting. "
            "Only meaningful with --fix. Default: False."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON (implies --noinput when used with --fix).",
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

    # --fix path: build a plan for every group
    plans = [_plan_merge(vk, members) for vk, members in sorted(duplicates.items())]

    fixed: list[dict] = []
    skipped: list[str] = []
    conflicts: list[dict] = [p for p in plans if p["conflict"]]
    safe_plans = [p for p in plans if not p["conflict"]]

    # --json implies non-interactive (no prompts mid-JSON output)
    auto_apply = args.noinput or args.json
    aborted = False

    for plan in safe_plans:
        if auto_apply:
            _apply_plan(data, plan)
            fixed.append(plan)
        else:
            answer = _confirm(plan, lines)
            if answer == "y":
                _apply_plan(data, plan)
                fixed.append(plan)
            elif answer == "n":
                skipped.append(plan["version_key"])
            else:  # q
                print("\nAborted. Writing merges accepted so far.")
                aborted = True
                break

    if fixed:
        ALIASES_PATH.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    if args.json:
        _print_json(duplicates, fixed, skipped, conflicts)
    else:
        print()
        _print_report(duplicates, fixed, skipped, conflicts)

    sys.exit(1 if (conflicts or aborted) else 0)


if __name__ == "__main__":
    main()
