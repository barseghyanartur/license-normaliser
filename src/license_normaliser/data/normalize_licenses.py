#!/usr/bin/env python3
"""Normalize licenses from data sources and produce a summary."""

import json
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from license_normaliser import normalise_licenses

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def process_opendefinition(data: dict) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for entry in data.values():
        if not isinstance(entry, dict):
            continue
        results.append((entry.get("id", ""), entry.get("url", "")))
    return results


def process_spdx(data: dict) -> list[tuple[str, str]]:
    results: list[tuple[str, str]] = []
    for entry in data.get("licenses", []):
        if not isinstance(entry, dict):
            continue
        license_id = entry.get("licenseId", "")
        urls = entry.get("seeAlso", [])
        results.append((license_id, urls[0] if urls else ""))
    return results


def normalize_batch(items: list[tuple[str, str]], source: str) -> dict:
    successes = 0
    failures = 0
    errors: list[str] = []

    license_ids = [lid for lid, _ in items if lid]
    batch_results = normalise_licenses(license_ids)

    for (lid, url), result in zip(items, batch_results, strict=False):
        if result.family.key != "unknown":
            successes += 1
            logger.debug("Normalized %s -> %s", lid, result.key)
        else:
            failures += 1
            errors.append(f"[{source}] {lid}: family=unknown, url={url}")
            logger.warning("Failed to normalize: %s (url=%s)", lid, url)

    return {
        "source": source,
        "total": len(items),
        "successes": successes,
        "failures": failures,
        "errors": errors,
    }


def main():
    data_dir = Path(__file__).parent

    summary: list[dict] = []

    od_path = data_dir / "opendefinition" / "opendefinition_licenses_all.json"
    logger.info("Processing %s", od_path.name)
    od_data = load_json(od_path)
    od_items = process_opendefinition(od_data)
    result = normalize_batch(od_items, str(od_path))
    summary.append(result)
    logger.info(
        "  %s: %d/%d normalized",
        od_path.name,
        result["successes"],
        result["total"],
    )

    spdx_path = data_dir / "spdx" / "spdx-licenses.json"
    logger.info("Processing %s", spdx_path.name)
    spdx_data = load_json(spdx_path)
    spdx_items = process_spdx(spdx_data)
    result = normalize_batch(spdx_items, str(spdx_path))
    summary.append(result)
    logger.info(
        "  %s: %d/%d normalized",
        spdx_path.name,
        result["successes"],
        result["total"],
    )

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_items = sum(r["total"] for r in summary)
    total_successes = sum(r["successes"] for r in summary)
    total_failures = sum(r["failures"] for r in summary)

    for r in summary:
        print(f"\n{r['source']}:")
        print(f"  Total:     {r['total']}")
        print(f"  Successes: {r['successes']}")
        print(f"  Failures:  {r['failures']}")
        if r["errors"]:
            print("  Errors:")
            for err in r["errors"][:10]:
                print(f"    {err}")
            if len(r["errors"]) > 10:
                print(f"    ... and {len(r['errors']) - 10} more")

    print(
        f"\nOverall: {total_successes}/{total_items} normalized "
        f"({total_failures} failures)"
    )


if __name__ == "__main__":
    main()
