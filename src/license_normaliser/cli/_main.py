"""license-normaliser CLI - license normalisation from the command line."""

import argparse
import sys
from pathlib import Path

import httpx

from license_normaliser import __version__, normalise_license
from license_normaliser._exceptions import LicenseNormalisationError
from license_normaliser.exceptions import LicenseNotFoundError

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("main",)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="license-normaliser",
        description="Comprehensive license normalisation - three-level hierarchy.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    norm = sub.add_parser("normalise", help="Normalise a license string.")
    norm.add_argument("license", help="License string to normalise.")
    norm.add_argument("--full", action="store_true")
    norm.add_argument("--strict", action="store_true")

    batch = sub.add_parser("batch", help="Normalise multiple license strings.")
    batch.add_argument("licenses", nargs="+")
    batch.add_argument("--strict", action="store_true")

    update = sub.add_parser(
        "update-data", help="Fetch fresh SPDX + OpenDefinition data."
    )
    update.add_argument(
        "--data-dir",
        default="src/license_normaliser/data",
        help="Target directory",
    )
    update.add_argument("--force", action="store_true", help="Overwrite existing files")

    return parser


def _cmd_normalise(args: argparse.Namespace) -> int:
    try:
        result = normalise_license(args.license, strict=args.strict)
        if args.full:
            print(f"Key: {result.key}")
            print(f"URL: {result.url or '(none)'}")
            print(f"License: {result.license}")
            print(f"Family: {result.family}")
        else:
            print(result.key)
    except LicenseNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except LicenseNormalisationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def _cmd_batch(args: argparse.Namespace) -> int:
    if args.strict:
        try:
            for license_str in args.licenses:
                result = normalise_license(license_str, strict=True)
                print(f"{license_str}: {result.key}")
        except LicenseNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    else:
        for license_str in args.licenses:
            result = normalise_license(license_str, strict=False)
            print(f"{license_str}: {result.key}")
    return 0


def _cmd_update_data(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).resolve()
    data_dir.mkdir(parents=True, exist_ok=True)

    sources = {
        "spdx/spdx-licenses.json": (
            "https://raw.githubusercontent.com/spdx/license-list-data/main/json/licenses.json"
        ),
        "opendefinition/opendefinition_licenses_all.json": (
            "https://licenses.opendefinition.org/licenses/groups/all.json"
        ),
    }

    for relative_path, url in sources.items():
        target = data_dir / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and not args.force:
            print(f"Skipping {relative_path} (use --force to overwrite)")
            continue

        print(f"Fetching {url} -> {target}")
        try:
            r = httpx.get(url, follow_redirects=True, timeout=30)
            r.raise_for_status()
            target.write_text(r.text, encoding="utf-8")
            print(f"Saved {relative_path}")
        except Exception as exc:
            print(f"Failed to fetch {relative_path}: {exc}", file=sys.stderr)
            return 1
    print("Data sources updated successfully.")
    return 0


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "normalise":
        sys.exit(_cmd_normalise(args))
    elif args.command == "batch":
        sys.exit(_cmd_batch(args))
    elif args.command == "update-data":
        sys.exit(_cmd_update_data(args))
    else:
        parser.print_help()
        sys.exit(1)
