"""license-normaliser CLI — license normalisation from the command line."""

import argparse
import sys

from license_normaliser import __version__, normalise_license

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("main",)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="license-normaliser",
        description="Comprehensive license normalisation — three-level hierarchy.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_version()}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # Normalise command
    norm = sub.add_parser("normalise", help="Normalise a license string.")
    norm.add_argument(
        "license",
        help="License string to normalise (token, URL, or prose).",
    )
    norm.add_argument(
        "--full",
        action="store_true",
        help="Show full details (key, URL, license name, family).",
    )

    # Batch normalise command
    batch = sub.add_parser("batch", help="Normalise multiple license strings.")
    batch.add_argument(
        "licenses",
        nargs="+",
        help="License strings to normalise.",
    )

    return parser


def _version() -> str:
    return __version__


def _cmd_normalise(args: argparse.Namespace) -> int:
    try:
        result = normalise_license(args.license)
        if args.full:
            print(f"Key: {result.key}")
            print(f"URL: {result.url or '(none)'}")
            print(f"License: {result.license}")
            print(f"Family: {result.family}")
        else:
            print(result.key)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def _cmd_batch(args: argparse.Namespace) -> int:
    try:
        for license_str in args.licenses:
            result = normalise_license(license_str)
            print(f"{license_str}: {result.key}")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    if args.command == "normalise":
        sys.exit(_cmd_normalise(args))
    elif args.command == "batch":
        sys.exit(_cmd_batch(args))
    else:
        parser.print_help()
        sys.exit(1)
