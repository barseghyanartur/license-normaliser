"""Dataset comparison tool for license-normaliser.

Compares SPDX, OpenDefinition, OSI, CreativeCommons, ScanCode, and
curated data files (aliases, url_map, prose, publishers) for:
  - Dataset sizes
  - Cross-dataset overlaps
  - Licenses present in OSI but missing from SPDX
  - Orphan alias/URL targets (don't resolve to REGISTRY entries)
  - REGISTRY entries without curated aliases
  - Most-aliased license targets
"""

from __future__ import annotations

__all__ = ()

import json
from collections import Counter
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "src" / "license_normaliser" / "data"


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


def load_url_keys() -> set[str]:
    with open(DATA_DIR / "urls" / "url_map.json") as f:
        data = json.load(f)
    return {k for k in data if not k.startswith("_")}


def load_url_targets() -> dict[str, str]:
    with open(DATA_DIR / "urls" / "url_map.json") as f:
        data = json.load(f)
    return {
        k: v.get("version_key", "") for k, v in data.items() if not k.startswith("_")
    }


def load_prose_targets() -> list[str]:
    with open(DATA_DIR / "prose" / "prose_patterns.json") as f:
        data = json.load(f)
    return [entry.get("version_key", "") for entry in data]


def load_pub_urls() -> set[str]:
    with open(DATA_DIR / "publishers" / "publishers.json") as f:
        data = json.load(f)
    return set(data.get("urls", {}).keys())


def load_pub_aliases() -> dict[str, str]:
    with open(DATA_DIR / "publishers" / "publishers.json") as f:
        data = json.load(f)
    return dict(data.get("shorthand_aliases", {}))


def load_registry_keys() -> set[str]:
    from license_normaliser._cache import get_registry_keys

    return get_registry_keys()


def load_merged_aliases() -> dict[str, str]:
    """Simulate merged ALIASES: alias_key -> version_key from all curated sources."""
    merged: dict[str, str] = {}
    merged.update(load_alias_targets())
    merged.update(load_pub_aliases())
    for k, v in load_url_targets().items():
        if k not in merged:
            merged[k] = v
    return merged


def would_resolve(alias_key: str, registry: set[str], aliases: dict[str, str]) -> bool:
    """Simulate _resolve() pipeline for orphan detection.

    1. If already in REGISTRY, covered.
    2. If in ALIASES, get version_key and check if that's in REGISTRY.
    """
    if alias_key in registry:
        return True
    version_key = aliases.get(alias_key, "")
    return bool(version_key and version_key in registry)


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
    url_keys = load_url_keys()
    url_tgt = load_url_targets()
    prose_tgt = load_prose_targets()
    pub_urls = load_pub_urls()
    pub_aliases = load_pub_aliases()
    registry = load_registry_keys()
    merged_aliases = load_merged_aliases()

    # --- 1. Dataset sizes ---
    section("Dataset Sizes")
    print(f"  SPDX licenses:          {len(spdx):>6}")
    print(f"  OpenDefinition entries: {len(od):>6}")
    print(f"  OSI-approved (SPDX):   {len(osi):>6}")
    print(f"  CreativeCommons:        {len(cc):>6}")
    print(f"  ScanCode DB entries:   {len(sc):>6}")
    print(f"  Aliases (curated):     {len(alias_keys):>6}")
    print(f"  URL mappings (curated): {len(url_keys):>6}")
    print(f"  Prose patterns:        {len(prose_tgt):>6}")
    print(f"  Publisher URLs:        {len(pub_urls):>6}")
    print(f"  Publisher aliases:     {len(pub_aliases):>6}")
    print(f"  REGISTRY entries:     {len(registry):>6}")

    # --- 2. Overlaps ---
    section("Cross-Dataset Overlaps")

    # SPDX overlaps
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

    # Unique content
    print(f"\n  Unique to SPDX:  {len(spdx - od - osi - cc - sc):>6}")
    print(f"  Unique to OD:    {len(od - spdx):>6}")
    print(f"  Unique to OSI:   {len(osi - spdx):>6}  (OSI IDs not in SPDX)")
    print(f"  Unique to CC:    {len(cc - spdx - od):>6}")
    print(f"  Unique to ScanCode: {len(sc - spdx - osi - od - cc):>6}")

    # --- 3. OSI licenses not in SPDX (reference integrity) ---
    section("OSI Licenses Missing from SPDX")
    osi_only = sorted(osi - spdx)
    if osi_only:
        print(f"  {len(osi_only)} OSI-licensed IDs have no SPDX entry:")
        for lid in osi_only[:20]:
            print(f"    {lid}")
        if len(osi_only) > 20:
            print(f"    ... and {len(osi_only) - 20} more")
    else:
        print("  All OSI IDs are present in SPDX.")

    # --- 4. Curated targets not in REGISTRY ---
    section("Curated Targets Missing from REGISTRY")
    orphan_alias = sorted(
        k for k in alias_keys if not would_resolve(k, registry, merged_aliases)
    )
    orphan_url = sorted(
        k for k in url_keys if not would_resolve(k, registry, merged_aliases)
    )
    orphan_pub = sorted(
        k for k in pub_aliases if not would_resolve(k, registry, merged_aliases)
    )
    if orphan_alias:
        print(f"  Alias keys that fail resolution ({len(orphan_alias)}):")
        for k in orphan_alias[:10]:
            print(f"    {k!r}  ->  {alias_tgt.get(k, '')!r}")
        if len(orphan_alias) > 10:
            print(f"    ... and {len(orphan_alias) - 10} more")
    else:
        print("  All alias keys resolve to REGISTRY entries.")
    if orphan_url:
        print(f"\n  URL keys that fail resolution ({len(orphan_url)}):")
        for k in orphan_url[:10]:
            print(f"    {k[:60]!r}  ->  {url_tgt.get(k, '')!r}")
        if len(orphan_url) > 10:
            print(f"    ... and {len(orphan_url) - 10} more")
    if orphan_pub:
        print(f"\n  Publisher aliases that fail resolution ({len(orphan_pub)}):")
        for k in orphan_pub[:10]:
            print(f"    {k!r}  ->  {pub_aliases[k]!r}")
        if len(orphan_pub) > 10:
            print(f"    ... and {len(orphan_pub) - 10} more")
    print(
        "\n  (Note: prose pattern version_keys are often bare name_keys like "
        "'cc-by'; these resolve via the prose pipeline and are not orphans.)"
    )

    # --- 5. REGISTRY entries not covered by curated data ---
    section("REGISTRY Entries Without Curated Mapping")
    covered = (
        set(alias_tgt.values()) | set(url_tgt.values()) | set(pub_aliases.values())
    )
    uncovered = sorted(k for k in registry if k not in covered)
    if uncovered:
        print(f"  {len(uncovered)} REGISTRY keys have no curated alias/URL mapping:")
        for k in uncovered[:20]:
            print(f"    {k}")
        if len(uncovered) > 20:
            print(f"    ... and {len(uncovered) - 20} more")
    else:
        print("  All REGISTRY entries have at least one curated mapping.")

    # --- 6. Duplicate alias keys (same key -> different targets) ---
    section("Duplicate Keys in Alias / URL Data Files")
    # Check if any key maps to different targets across aliases + url_map
    # (keys are unique within each file, so cross-file check)
    cross_keys = alias_keys & url_keys
    if cross_keys:
        print(f"  Keys in both aliases.json AND url_map.json ({len(cross_keys)}):")
        for k in sorted(cross_keys):
            print(f"    {k!r}: aliases={alias_tgt[k]!r}, url_map={url_tgt[k]!r}")

    # --- 7. Alias target frequency (which targets have the most aliases) ---
    section("Most-Aliased License Targets")
    alias_counts = Counter(alias_tgt.values())
    url_counts = Counter(url_tgt.values())
    pub_counts = Counter(pub_aliases.values())
    combined = alias_counts + url_counts + pub_counts
    for target, count in combined.most_common(15):
        parts = []
        if alias_counts[target]:
            parts.append(f"alias={alias_counts[target]}")
        if url_counts[target]:
            parts.append(f"url={url_counts[target]}")
        if pub_counts[target]:
            parts.append(f"pub={pub_counts[target]}")
        print(f"  {target:<30}  total={count:<4}  ({', '.join(parts)})")

    # --- 8. Summary ---
    section("Summary")
    distinct = len(spdx | od | osi | cc | sc)
    orphans = len(orphan_alias) + len(orphan_url) + len(orphan_pub)
    print(f"  Distinct license IDs:          {distinct}")
    print(f"  Curated alias entries:        {len(alias_keys)}")
    print(f"  Curated URL mappings:         {len(url_keys)}")
    print(f"  Orphan curated targets:       {orphans}")
    print(f"  OSI IDs missing SPDX:         {len(osi_only)}")
    covered_count = len(registry) - len(uncovered)
    print(f"  REGISTRY entries covered:       {covered_count}/{len(registry)}")


if __name__ == "__main__":
    main()
