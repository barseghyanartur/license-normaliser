"""Dataset comparison tool for licence-normaliser.

Compares SPDX, OpenDefinition, OSI, CreativeCommons, ScanCode, and
curated data files (aliases, prose) for:
  - Dataset sizes
  - Cross-dataset overlaps
  - Licences present in OSI but missing from SPDX
  - Orphan alias targets (don't resolve to REGISTRY entries)
  - REGISTRY entries without curated aliases
  - Most-aliased licence targets
"""

from __future__ import annotations

__all__ = ()

import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "licence_normaliser" / "data"


def load_spdx_ids() -> set[str]:
    with open(DATA_DIR / "spdx" / "spdx.json") as f:
        data = json.load(f)
    return {entry["licenseId"] for entry in data["licenses"]}


def load_od_ids() -> set[str]:
    with open(DATA_DIR / "opendefinition" / "opendefinition.json") as f:
        data = json.load(f)
    return set(data.keys())


def load_osi_ids() -> set[str]:
    with open(DATA_DIR / "osi" / "osi.json") as f:
        data = json.load(f)
    return {entry["spdx_id"].strip() for entry in data if entry.get("spdx_id")}


def load_cc_ids() -> set[str]:
    with open(DATA_DIR / "creativecommons" / "creativecommons.json") as f:
        data = json.load(f)
    return {entry["license_key"] for entry in data}


def load_sc_ids() -> set[str]:
    with open(DATA_DIR / "scancode_licensedb" / "scancode_licensedb.json") as f:
        data = json.load(f)
    return {entry["license_key"] for entry in data}


def load_alias_keys() -> set[str]:
    with open(DATA_DIR / "aliases" / "aliases.json") as f:
        data = json.load(f)
    return {k for k in data if not k.startswith("_")}


def load_alias_targets() -> dict[str, str]:
    with open(DATA_DIR / "aliases" / "aliases.json") as f:
        data = json.load(f)
    return {
        k: v.get("version_key", "") for k, v in data.items() if not k.startswith("_")
    }


def load_prose_targets() -> list[str]:
    """Load all prose pattern strings from aliases.json."""
    with open(DATA_DIR / "aliases" / "aliases.json") as f:
        data = json.load(f)
    patterns: list[str] = []
    for entry in data.values():
        if isinstance(entry, dict) and "patterns" in entry:
            entry_patterns = [p for p in entry["patterns"] if isinstance(p, str) and p]
            patterns.extend(entry_patterns)
    return sorted(patterns)


def load_registry_keys() -> set[str]:
    from licence_normaliser._cache import get_registry_keys

    return get_registry_keys()


def would_resolve(alias_key: str, registry: set[str], aliases: dict[str, str]) -> bool:
    """Simulate _resolve() pipeline for orphan detection.

    1. If already in REGISTRY, covered.
    2. If in ALIASES, get version_key - resolves regardless of registry presence.
    """
    if alias_key in registry:
        return True
    version_key = aliases.get(alias_key, "")
    return bool(version_key)


def section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def main() -> None:
    print("Loading datasets...")
    spdx = load_spdx_ids()
    od = load_od_ids()
    osi = load_osi_ids()
    cc = load_cc_ids()
    sc = load_sc_ids()
    alias_keys = load_alias_keys()
    alias_tgt = load_alias_targets()
    prose_tgt = load_prose_targets()
    registry = load_registry_keys()

    # --- 1. Dataset sizes ---
    section("Dataset Sizes")
    print(f"  SPDX licences:          {len(spdx):>6}")
    print(f"  OpenDefinition entries: {len(od):>6}")
    print(f"  OSI-approved (SPDX):   {len(osi):>6}")
    print(f"  CreativeCommons:        {len(cc):>6}")
    print(f"  ScanCode DB entries:   {len(sc):>6}")
    print(f"  Aliases (curated):     {len(alias_keys):>6}")
    print(f"  Prose patterns:        {len(prose_tgt):>6}")
    print(f"  REGISTRY entries:     {len(registry):>6}")

    # --- 2. Overlaps ---
    section("Cross-Dataset Overlaps")

    def pct(sub: int, total: int) -> str:
        return f"{100 * sub / max(total, 1):.1f}%"

    overlaps = [
        ("SPDX n OSI", len(spdx & osi), len(osi), "OSI"),
        ("SPDX n OD", len(spdx & od), len(od), "OD"),
        ("SPDX n CC", len(spdx & cc), len(cc), "CC"),
        ("OSI n OD", len(osi & od), len(od), "OD"),
        ("OSI n CC", len(osi & cc), len(cc), "CC"),
        ("OD  n CC", len(od & cc), len(cc), "CC"),
        ("ScanCode n SPDX", len(sc & spdx), len(sc), "ScanCode"),
        ("ScanCode n OSI", len(sc & osi), len(sc), "ScanCode"),
    ]
    for label, overlap_count, total_count, pct_label in overlaps:
        ratio = pct(overlap_count, total_count)
        print(f"  {label:<17} {overlap_count:>5}  ({ratio} of {pct_label})")

    print(f"\n  Unique to SPDX:  {len(spdx - od - osi - cc - sc):>6}")
    print(f"  Unique to OD:    {len(od - spdx):>6}")
    print(f"  Unique to OSI:   {len(osi - spdx):>6}  (OSI IDs not in SPDX)")
    print(f"  Unique to CC:    {len(cc - spdx - od):>6}")
    print(f"  Unique to ScanCode: {len(sc - spdx - osi - od - cc):>6}")

    # --- 3. OSI licences not in SPDX (reference integrity) ---
    section("OSI Licences Missing from SPDX")
    osi_only = sorted(osi - spdx)
    if osi_only:
        print(f"  {len(osi_only)} OSI-licenced IDs have no SPDX entry:")
        for lid in osi_only[:20]:
            print(f"    {lid}")
        if len(osi_only) > 20:
            print(f"    ... and {len(osi_only) - 20} more")
    else:
        print("  All OSI IDs are present in SPDX.")

    # --- 4. Curated targets not in REGISTRY ---
    section("Curated Targets Missing from REGISTRY")
    orphan_alias = sorted(
        k for k in alias_keys if not would_resolve(k, registry, alias_tgt)
    )
    if orphan_alias:
        print(f"  Alias keys that fail resolution ({len(orphan_alias)}):")
        for k in orphan_alias[:10]:
            print(f"    {k!r}  ->  {alias_tgt.get(k, '')!r}")
        if len(orphan_alias) > 10:
            print(f"    ... and {len(orphan_alias) - 10} more")
    else:
        print("  All alias keys resolve to REGISTRY entries.")
    print(
        "\n  (Note: prose pattern version_keys are often bare name_keys like "
        "'cc-by'; these resolve via the prose pipeline and are not orphans.)"
    )

    # --- 5. REGISTRY entries not covered by curated data ---
    section("REGISTRY Entries Without Curated Mapping")
    covered = set(alias_tgt.values())
    uncovered = sorted(k for k in registry if k not in covered)
    if uncovered:
        print(f"  {len(uncovered)} REGISTRY keys have no curated alias mapping:")
        for k in uncovered[:20]:
            print(f"    {k}")
        if len(uncovered) > 20:
            print(f"    ... and {len(uncovered) - 20} more")
    else:
        print("  All REGISTRY entries have at least one curated mapping.")

    # --- 6. Alias target frequency (which targets have the most aliases) ---
    section("Most-Aliased Licence Targets")
    alias_counts = Counter(alias_tgt.values())
    for target, count in alias_counts.most_common(15):
        print(f"  {target:<30}  alias_count={count}")

    # --- 7. Summary ---
    section("Summary")
    distinct = len(spdx | od | osi | cc | sc)
    orphans = len(orphan_alias)
    print(f"  Distinct licence IDs:          {distinct}")
    print(f"  Curated alias entries:        {len(alias_keys)}")
    print(f"  Orphan curated targets:       {orphans}")
    print(f"  OSI IDs missing SPDX:         {len(osi_only)}")
    covered_count = len(registry) - len(uncovered)
    print(f"  REGISTRY entries covered:       {covered_count}/{len(registry)}")


if __name__ == "__main__":
    main()
