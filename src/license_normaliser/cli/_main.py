"""license-normaliser CLI - license normalisation from the command line."""

import argparse
import sys
from pathlib import Path

from license_normaliser import __version__, normalise_license
from license_normaliser._exceptions import LicenseNormalisationError
from license_normaliser.exceptions import LicenseNotFoundError
from license_normaliser.parsers import get_parsers

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
        "update-data", help="Fetch fresh data from all registered parsers."
    )
    update.add_argument(
        "--parser",
        dest="parser_name",
        metavar="NAME",
        help="Refresh only the named parser (e.g. spdx, opendefinition, osi). "
        "Without this flag, all parsers are refreshed.",
    )
    update.add_argument(
        "--force",
        action="store_true",
        help="Overwrite even if the local file already exists.",
    )

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
    parsers = get_parsers()
    if args.parser_name:
        parsers = [p for p in parsers if p.__class__.__name__ == args.parser_name]
        if not parsers:
            print(
                f"error: unknown parser {args.parser_name!r}. "
                f"Available: {[p.__class__.__name__ for p in get_parsers()]}",
                file=sys.stderr,
            )
            return 1

    failed: list[str] = []
    for parser_cls in parsers:
        name = parser_cls.__class__.__name__
        url = parser_cls.url
        target = parser_cls.local_path
        target_path = Path(__file__).parent.parent / target
        ok = parser_cls.refresh(args.force)
        if target_path.exists() and not args.force:
            status = "skipped"
        elif ok:
            status = "fetched"
        else:
            status = "FAILED"
        if not ok:
            failed.append(name)
        print(f"  {status}: {name} ({url}) -> {target}")

    if failed:
        print(f"error: failed to refresh: {', '.join(failed)}", file=sys.stderr)
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
