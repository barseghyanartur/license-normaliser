"""Check which downloaded licenses are missing from curated aliases.

Compares all refreshable plugin registries against aliases.json to identify
licenses that have no corresponding curated alias entry.

Usage:
    uv run python scripts/check_missing_aliases.py
    uv run python scripts/check_missing_aliases.py --json
"""

from __future__ import annotations

import contextlib
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "license_normaliser" / "data"
SCRIPTS_DIR = Path(__file__).parent


def load_alias_targets() -> set[str]:
    """Load all version_keys from aliases.json."""
    with open(DATA_DIR / "aliases" / "aliases.json") as f:
        data = json.load(f)
    targets: set[str] = set()
    for meta in data.values():
        if isinstance(meta, dict):
            vk = meta.get("version_key", "")
            if vk:
                targets.add(vk)
    return targets


def load_downloaded_licenses() -> dict[str, set[str]]:
    """Load licenses from all refreshable plugins."""
    from license_normaliser.defaults import get_all_refreshable_plugins

    result: dict[str, set[str]] = {}
    for plugin_cls in get_all_refreshable_plugins():
        # Try to load registry
        data = None
        with contextlib.suppress(Exception):
            data = plugin_cls().load_registry()

        if data:
            result[plugin_cls.__name__] = set(data.keys())

    # Also add OSIParser (checked separately since it might fail on network)
    data = None
    try:
        from license_normaliser.parsers.osi import OSIParser

        data = OSIParser().load_registry()
    except Exception:
        pass

    if data:
        result["OSIParser"] = set(data.keys())

    return result


def check_coverage() -> dict:
    """Check which downloaded licenses have alias entries."""
    alias_targets = load_alias_targets()
    downloaded = load_downloaded_licenses()

    all_downloaded: set[str] = set()
    for licenses in downloaded.values():
        all_downloaded.update(licenses)

    # Categorize
    with_alias = all_downloaded & alias_targets
    without_alias = all_downloaded - alias_targets

    return {
        "total_downloaded": len(all_downloaded),
        "total_alias_targets": len(alias_targets),
        "with_alias": sorted(with_alias),
        "without_alias": sorted(without_alias),
        "coverage_percent": round(len(with_alias) / len(all_downloaded) * 100, 1)
        if all_downloaded
        else 0,
        "by_source": {
            name: {
                "total": len(licenses),
                "with_alias": len(licenses & alias_targets),
                "without_alias": sorted(licenses - alias_targets),
                "coverage": round(
                    len(licenses & alias_targets) / len(licenses) * 100, 1
                )
                if licenses
                else 0,
            }
            for name, licenses in downloaded.items()
        },
    }


def print_report(data: dict) -> None:
    """Print text table report."""
    print("=" * 70)
    print("Coverage Report: Downloaded Licenses vs Curated Aliases")
    print("=" * 70)
    print()
    print(f"Total downloaded licenses: {data['total_downloaded']}")
    print(f"Total curated alias targets: {data['total_alias_targets']}")
    print(f"Coverage: {data['coverage_percent']}%")
    print()

    print("-" * 70)
    print("By Source:")
    print("-" * 70)
    print(f"{'Source':<30} {'Total':>8} {'With':>8} {'Without':>8} {'Coverage':>10}")
    print("-" * 70)

    for source, stats in data["by_source"].items():
        print(
            f"{source:<30} {stats['total']:>8} "
            f"{stats['with_alias']:>8} {len(stats['without_alias']):>8} "
            f"{stats['coverage']:>9.1f}%"
        )

    print()
    print("-" * 70)
    print(f"Licenses WITHOUT alias entry: {len(data['without_alias'])}")
    print("-" * 70)
    # Print in columns
    line = ""
    for lic in data["without_alias"]:
        if len(line) + len(lic) > 66:
            print(line)
            line = ""
        line += lic + ", "
    if line:
        print(line.rstrip(", "))
    print()


def main() -> None:
    json_export = "--json" in sys.argv
    data = check_coverage()

    if json_export:
        print(json.dumps(data, indent=2))
    else:
        print_report(data)


if __name__ == "__main__":
    main()
