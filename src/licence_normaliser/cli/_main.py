"""licence-normaliser CLI - licence normalisation from the command line."""

import argparse
import sys
from pathlib import Path

from licence_normaliser import __version__, normalise_licence
from licence_normaliser._trace import _should_trace
from licence_normaliser.defaults import get_all_refreshable_plugins
from licence_normaliser.exceptions import (
    LicenceNormalisationError,
    LicenceNotFoundError,
)

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("main",)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="licence-normaliser",
        description="Comprehensive licence normalisation - three-level hierarchy.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    norm = sub.add_parser("normalise", help="Normalise a licence string.")
    norm.add_argument("licence", help="Licence string to normalise.")
    norm.add_argument("--full", action="store_true")
    norm.add_argument("--strict", action="store_true")
    norm.add_argument("--trace", action="store_true", help="Show resolution trace.")

    batch = sub.add_parser("batch", help="Normalise multiple licence strings.")
    batch.add_argument("licences", nargs="+")
    batch.add_argument("--strict", action="store_true")
    batch.add_argument(
        "--trace", action="store_true", help="Show resolution trace for each."
    )

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
        trace = args.trace or _should_trace()
        result = normalise_licence(args.licence, strict=args.strict, trace=trace)
        if trace:
            print(result.explain())
        elif args.full:
            print(f"Key: {result.key}")
            print(f"URL: {result.url or '(none)'}")
            print(f"Licence: {result.licence}")
            print(f"Family: {result.family}")
        else:
            print(result.key)
    except LicenceNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except LicenceNormalisationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def _cmd_batch(args: argparse.Namespace) -> int:
    trace = args.trace or _should_trace()
    if args.strict:
        try:
            for licence_str in args.licences:
                result = normalise_licence(licence_str, strict=True, trace=trace)
                if trace:
                    print(f"{licence_str}:")
                    print(result.explain())
                else:
                    print(f"{licence_str}: {result.key}")
        except LicenceNotFoundError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    else:
        for licence_str in args.licences:
            result = normalise_licence(licence_str, strict=False, trace=trace)
            if trace:
                print(f"{licence_str}:")
                print(result.explain())
            else:
                print(f"{licence_str}: {result.key}")
    return 0


def _cmd_update_data(args: argparse.Namespace) -> int:
    parser_classes = get_all_refreshable_plugins()
    if args.parser_name:
        parser_classes = [
            p for p in parser_classes if getattr(p, "id", None) == args.parser_name
        ]
        if not parser_classes:
            available = [
                getattr(p, "id", p.__name__) for p in get_all_refreshable_plugins()
            ]
            print(
                f"error: unknown parser {args.parser_name!r}. Available: {available}",
                file=sys.stderr,
            )
            return 1

    failed: list[str] = []
    for parser_cls in parser_classes:
        name = getattr(parser_cls, "id", parser_cls.__name__)
        url = parser_cls.url
        target = parser_cls.local_path
        target_path = Path(__file__).parent.parent / target

        # Check skip condition before calling refresh
        if target_path.exists() and not args.force:
            status = "skipped"
            ok = True  # Not a failure, just skipped
        else:
            ok = parser_cls.refresh(args.force)
            if ok:
                status = "fetched"
            else:
                status = "FAILED"
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
