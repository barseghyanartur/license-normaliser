"""Compare ScanCode license categories with aliases.json family_keys.

Compares (license_key, category) from scancode_licensedb.json with
(version_key/name_key, family_key) from aliases.json.
Reports:
  - Licenses in ScanCode but missing from aliases
  - Licenses where family_key doesn't match expected family from ScanCode category
"""

from __future__ import annotations

__all__ = ()

import json
from pathlib import Path
from typing import Optional

DATA_DIR = Path(__file__).parent.parent / "src" / "licence_normaliser" / "data"

CATEGORY_TO_FAMILY: dict[str, str] = {
    "Permissive": "osi",
    "Copyleft": "copyleft",
    "Copyleft Limited": "copyleft",
    "Proprietary Free": "publisher-proprietary",
    "Commercial": "publisher-proprietary",
    "Free Restricted": "other-oa",
    "Source-available": "other-oa",
    "Public Domain": "public-domain",
}

SKIP_CATEGORIES = {"CLA", "Patent License", "Unstated License", "Non-Commercial"}


def load_scancode_data() -> dict[str, str]:
    """Load scancode_licensedb.json, return dict[license_key] = category."""
    with open(DATA_DIR / "scancode_licensedb" / "scancode_licensedb.json") as f:
        data = json.load(f)
    return {
        entry["license_key"]: entry["category"]
        for entry in data
        if entry.get("license_key")
    }


def load_aliases_data() -> tuple[dict[str, str], dict[str, str]]:
    """Load aliases.json, return (version_key→family, name_key→family)."""
    with open(DATA_DIR / "aliases" / "aliases.json") as f:
        data = json.load(f)

    version_to_family: dict[str, str] = {}
    name_to_family: dict[str, str] = {}

    for value in data.values():
        if isinstance(value, dict):
            family = value.get("family_key", "")
            version_key = value.get("version_key", "")
            name_key = value.get("name_key", "")

            if version_key and family:
                version_to_family[version_key] = family
            if name_key and family and name_key != version_key:
                name_to_family[name_key] = family

    return version_to_family, name_to_family


def strip_version(key: str) -> str:
    """Strip common version suffixes to get name_key."""
    suffixes = [
        "-1.0",
        "-2.0",
        "-3.0",
        "-4.0",
        "-5.0",
        "-1",
        "-2",
        "-3",
        "-4",
        "-5",
        "-1.1",
        "-2.1",
        "-3.1",
        "-0",
        "-0.1",
        "-0.2",
        "-only",
        "-or-later",
    ]
    for suffix in suffixes:
        if key.endswith(suffix):
            return key[: -len(suffix)]
    return key


def lookup_family(
    license_key: str,
    version_to_family: dict[str, str],
    name_to_family: dict[str, str],
) -> Optional[tuple[str, str]]:
    """Look up family_key for a license_key.

    Returns (family_key, lookup_method) or None if not found.
    """
    key_lower = license_key.lower()

    if key_lower in version_to_family:
        return (version_to_family[key_lower], "version_key")

    if key_lower in name_to_family:
        return (name_to_family[key_lower], "name_key")

    stripped = strip_version(key_lower)
    if stripped in name_to_family:
        return (name_to_family[stripped], "name_key (stripped version)")

    return None


def compare() -> None:
    """Compare ScanCode categories with aliases family_keys."""
    print("Loading data...")
    scancode_data = load_scancode_data()
    version_to_family, name_to_family = load_aliases_data()

    print(f"  ScanCode entries: {len(scancode_data)}")
    print(f"  Aliases version_key→family: {len(version_to_family)}")
    print(f"  Aliases name_key→family: {len(name_to_family)}")

    missing: list[tuple[str, str, str]] = []
    mismatches: list[tuple[str, str, str, str]] = []
    matches: list[str] = []

    for license_key, category in sorted(scancode_data.items()):
        if category in SKIP_CATEGORIES:
            continue

        expected_family = CATEGORY_TO_FAMILY.get(category)
        if expected_family is None:
            continue

        result = lookup_family(license_key, version_to_family, name_to_family)

        if result is None:
            missing.append((license_key, category, expected_family))
        else:
            actual_family, lookup_method = result
            if actual_family == expected_family:
                matches.append(license_key)
            else:
                mismatches.append(
                    (license_key, category, expected_family, actual_family)
                )

    print(f"\n{'=' * 60}")
    print("  Results")
    print(f"{'=' * 60}")
    print(f"  Matches: {len(matches)}")
    print(f"  Missing from aliases: {len(missing)}")
    print(f"  Category/family mismatches: {len(mismatches)}")

    if missing:
        print(f"\n{'=' * 60}")
        print(f"  Missing from aliases ({len(missing)})")
        print(f"{'=' * 60}")
        for license_key, category, expected_family in missing[:50]:
            print(f"    {license_key}")
            print(f"      ScanCode category: {category}")
            print(f"      Expected family: {expected_family}")
        if len(missing) > 50:
            print(f"    ... and {len(missing) - 50} more")

    if mismatches:
        print(f"\n{'=' * 60}")
        print(f"  Category/family mismatches ({len(mismatches)})")
        print(f"{'=' * 60}")
        for license_key, category, expected_family, actual_family in mismatches[:50]:
            print(f"    {license_key}")
            print(f"      ScanCode category: {category}")
            print(f"      Expected family: {expected_family}")
            print(f"      Actual family: {actual_family}")
        if len(mismatches) > 50:
            print(f"    ... and {len(mismatches) - 50} more")


if __name__ == "__main__":
    compare()
