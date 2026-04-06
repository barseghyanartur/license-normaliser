#!/usr/bin/env python3
"""Documentation validator tool for licence-normaliser.

Validates that documentation matches the source code ground truth.
Can also auto-fix issues where possible.

Usage:
    documentation-validator              # Check all documentation
    documentation-validator --fix        # Auto-fix issues
    documentation-validator --json       # Output JSON report
    documentation-validator -v           # Verbose output
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


# =============================================================================
# Data Classes
# =============================================================================


@dataclass
class Mismatch:
    """Represents a single documentation mismatch."""

    check: str
    type: str
    message: str
    document: str
    severity: str = "error"  # error, warning, info
    fixable: bool = False
    suggestion: str | None = None


@dataclass
class CheckResult:
    """Result of a documentation check."""

    check_name: str
    passed: bool
    mismatches: list[Mismatch] = field(default_factory=list)


# =============================================================================
# AST Extractors - Extract ground truth from source code
# =============================================================================


class SourceExtractor:
    """Extracts ground truth from Python source files using AST."""

    def __init__(self, src_dir: Path):
        self.src_dir = src_dir

    def extract_public_api(self) -> set[str]:
        """Extract __all__ tuple from __init__.py."""
        init_file = self.src_dir / "__init__.py"
        if not init_file.exists():
            return set()

        tree = ast.parse(init_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if (
                        isinstance(target, ast.Name)
                        and target.id == "__all__"
                        and isinstance(node.value, ast.Tuple)
                    ):
                        return {
                            elt.value
                            for elt in node.value.elts
                            if isinstance(elt, ast.Constant)
                        }
        return set()

    def extract_exceptions(self) -> set[str]:
        """Extract exception class names from exceptions.py."""
        exc_file = self.src_dir / "exceptions.py"
        if not exc_file.exists():
            return set()

        tree = ast.parse(exc_file.read_text())
        exceptions = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Check if it inherits from Exception
                for base in node.bases:
                    if (
                        isinstance(base, ast.Name)
                        and base.id == "Exception"
                        or isinstance(base, ast.Attribute)
                        and base.attr.endswith("Error")
                        or isinstance(base, ast.Name)
                        and base.id.endswith("Error")
                    ):
                        exceptions.add(node.name)
        return exceptions

    def extract_cli_commands(self) -> set[str]:
        """Extract CLI subcommand names from cli/_main.py."""
        cli_file = self.src_dir / "cli" / "_main.py"
        if not cli_file.exists():
            return set()

        tree = ast.parse(cli_file.read_text())
        commands = set()
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_parser"
            ):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        commands.add(arg.value)
        return commands

    def extract_parser_classes(self) -> dict[str, dict[str, Any]]:
        """Extract parser class info from parsers/ directory."""
        parsers_dir = self.src_dir / "parsers"
        if not parsers_dir.exists():
            return {}

        parsers = {}
        for file in parsers_dir.glob("*.py"):
            if file.name == "__init__.py":
                continue

            tree = ast.parse(file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    bases = []
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            bases.append(base.id)
                        elif isinstance(base, ast.Attribute):
                            bases.append(base.attr)

                    # Check if it's a plugin class
                    if any("Plugin" in b for b in bases):
                        plugins = [b for b in bases if "Plugin" in b]
                        parsers[node.name] = {
                            "file": f"parsers/{file.name}",
                            "plugins": plugins,
                            "all_bases": bases,
                        }
        return parsers

    def extract_model_classes(self) -> set[str]:
        """Extract model class names from _models.py."""
        models_file = self.src_dir / "_models.py"
        if not models_file.exists():
            return set()

        tree = ast.parse(models_file.read_text())
        classes = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Look for dataclass-like patterns
                for decorator in node.decorator_list:
                    is_dataclass = (
                        isinstance(decorator, ast.Name) and decorator.id == "dataclass"
                    )
                    is_dataclass_call = (
                        isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Name)
                        and decorator.func.id == "dataclass"
                    )
                    if is_dataclass or is_dataclass_call:
                        classes.add(node.name)
        return classes


# =============================================================================
# Documentation Parsers - Extract references from docs
# =============================================================================


class RSTParser:
    """Parse RST documentation files."""

    CODE_BLOCK_PATTERN = re.compile(
        r"\.\.\s+code-block::\s*(\w+)\s*(?::name:\s*(\S+))?",
        re.MULTILINE | re.IGNORECASE,
    )

    FILE_REF_PATTERN = re.compile(r"`?(src/licence_normaliser/[^`\s>]+)`?")

    TABLE_ROW_PATTERN = re.compile(
        r"^\|\s*([^|]+)\|\s*([^|]+)\|\s*([^|]+)\|", re.MULTILINE
    )

    def __init__(self, content: str):
        self.content = content

    def extract_file_references(self) -> set[str]:
        """Extract file path references."""
        refs = set()
        for match in self.FILE_REF_PATTERN.finditer(self.content):
            ref = match.group(1)
            # Clean up RST formatting
            ref = ref.rstrip("_")
            refs.add(ref)
        return refs

    def extract_code_blocks(self) -> list[dict[str, Any]]:
        """Extract code blocks with their names."""
        return [
            {
                "language": match.group(1),
                "name": match.group(2),
                "position": match.start(),
            }
            for match in self.CODE_BLOCK_PATTERN.finditer(self.content)
        ]

    def extract_table_rows(self) -> list[list[str]]:
        """Extract table rows."""
        return [
            [match.group(1).strip(), match.group(2).strip()]
            for match in self.TABLE_ROW_PATTERN.finditer(self.content)
        ]

    def extract_class_references(self) -> set[str]:
        """Extract class name references (PascalCase words)."""
        # Look for class names in backticks or plain text
        pattern = re.compile(r"`?([A-Z][a-zA-Z]+(?:[A-Z][a-zA-Z]+)*)`?")
        return {m.group(1) for m in pattern.finditer(self.content)}


class MarkdownParser:
    """Parse Markdown documentation files."""

    CODE_BLOCK_PATTERN = re.compile(
        r"```(\w+)?\s*name=(\S+)", re.MULTILINE | re.IGNORECASE
    )

    FILE_REF_PATTERN = re.compile(r"`?(src/licence_normaliser/[^`\s>]+)`?")

    TABLE_PATTERN = re.compile(
        r"^\|([^\n]+)\|\n\|[-:|\s]+\|\n((?:\|[^\n]+\|\n)*)", re.MULTILINE
    )

    def __init__(self, content: str):
        self.content = content

    def extract_file_references(self) -> set[str]:
        """Extract file path references."""
        refs = set()
        for match in self.FILE_REF_PATTERN.finditer(self.content):
            ref = match.group(1)
            refs.add(ref)
        return refs

    def extract_code_blocks(self) -> list[dict[str, Any]]:
        """Extract code blocks with their names."""
        return [
            {
                "language": match.group(1),
                "name": match.group(2),
                "position": match.start(),
            }
            for match in self.CODE_BLOCK_PATTERN.finditer(self.content)
        ]

    def extract_table_rows(self) -> list[list[str]]:
        """Extract markdown table rows."""
        rows = []
        tables = self.TABLE_PATTERN.findall(self.content)
        for table in tables:
            # Parse row content
            row_text = table[1]
            for line in row_text.strip().split("\n"):
                if line.startswith("|") and line.endswith("|"):
                    cells = [c.strip() for c in line[1:-1].split("|")]
                    rows.append(cells)
        return rows


# =============================================================================
# Validator Checks
# =============================================================================


class DocumentationValidator:
    """Main documentation validator checker."""

    def __init__(self, project_root: Path, verbose: bool = False):
        self.project_root = project_root
        self.src_dir = project_root / "src" / "licence_normaliser"
        self.verbose = verbose
        self.extractor = SourceExtractor(self.src_dir)

        # Ground truth from source code
        self.actual_api: set[str] = set()
        self.actual_exceptions: set[str] = set()
        self.actual_parsers: dict[str, dict[str, Any]] = {}
        self.actual_cli_commands: set[str] = set()
        self.actual_models: set[str] = set()

    def load_ground_truth(self) -> None:
        """Load ground truth from source code."""
        if self.verbose:
            print("Loading ground truth from source code...")

        self.actual_api = self.extractor.extract_public_api()
        self.actual_exceptions = self.extractor.extract_exceptions()
        self.actual_parsers = self.extractor.extract_parser_classes()
        self.actual_cli_commands = self.extractor.extract_cli_commands()
        self.actual_models = self.extractor.extract_model_classes()

        if self.verbose:
            print(f"  Public API: {self.actual_api}")
            print(f"  Exceptions: {self.actual_exceptions}")
            print(f"  Parsers: {set(self.actual_parsers.keys())}")
            print(f"  CLI commands: {self.actual_cli_commands}")
            print(f"  Models: {self.actual_models}")

    def check_file_paths(self, doc_name: str, content: str) -> list[Mismatch]:
        """Check that referenced file paths exist."""
        mismatches = []

        # Choose parser based on file extension
        if doc_name.endswith(".rst"):
            parser = RSTParser(content)
        else:
            parser = MarkdownParser(content)

        refs = parser.extract_file_references()

        for ref in refs:
            # Clean up the reference
            ref = ref.strip()
            if ref.endswith("`"):
                ref = ref[:-1]

            full_path = self.project_root / ref
            if not full_path.exists():
                mismatches.append(
                    Mismatch(
                        check="file_paths",
                        type="missing_file",
                        message=f"Referenced file does not exist: {ref}",
                        document=doc_name,
                        severity="error",
                        fixable=False,
                    )
                )

        return mismatches

    def check_code_blocks(self, doc_name: str, content: str) -> list[Mismatch]:
        """Check code blocks have proper name attributes."""
        if doc_name.endswith(".rst"):
            parser = RSTParser(content)
        else:
            parser = MarkdownParser(content)

        blocks = parser.extract_code_blocks()

        return [
            Mismatch(
                check="code_blocks",
                type="missing_name",
                message="Python code block missing :name: attribute",
                document=doc_name,
                severity="warning",
                fixable=False,
            )
            for block in blocks
            if block["language"] == "python" and not block["name"]
        ]

    def check_agents_md(self, content: str) -> list[Mismatch]:
        """Check AGENTS.md specific content."""
        mismatches: list[Mismatch] = []

        # Look for parser classes mentioned in tables
        parser_pattern = re.compile(r"`?(\w+Parser)`?")
        mentioned_parsers = {
            match.group(1) for match in parser_pattern.finditer(content)
        }

        # Find parsers not documented
        mismatches.extend(
            Mismatch(
                check="agents_md",
                type="undocumented_parser",
                message=f"Parser {parser_name} not found in AGENTS.md",
                document="AGENTS.md",
                severity="warning",
                fixable=False,
            )
            for parser_name in self.actual_parsers
            if parser_name not in mentioned_parsers
        )

        # Check public API exports are documented
        mismatches.extend(
            Mismatch(
                check="agents_md",
                type="undocumented_api",
                message=f"API export '{export}' not documented in AGENTS.md",
                document="AGENTS.md",
                severity="info",
                fixable=False,
            )
            for export in self.actual_api
            if export not in content
        )

        return mismatches

    def check_architecture_rst(self, content: str) -> list[Mismatch]:
        """Check ARCHITECTURE.rst specific content."""
        # Check all parsers are in plugin interfaces table
        parser_pattern = re.compile(r"`?(\w+Parser)`?")
        mentioned_parsers = {
            match.group(1) for match in parser_pattern.finditer(content)
        }

        return [
            Mismatch(
                check="architecture_rst",
                type="undocumented_parser",
                message=f"Parser {parser_name} not found in ARCHITECTURE.rst",
                document="ARCHITECTURE.rst",
                severity="warning",
                fixable=False,
            )
            for parser_name in self.actual_parsers
            if parser_name not in mentioned_parsers
        ]

    def check_readme_rst(self, content: str) -> list[Mismatch]:
        """Check README.rst specific content."""
        mismatches: list[Mismatch] = []

        # Check CLI commands are documented
        mismatches.extend(
            Mismatch(
                check="readme_rst",
                type="undocumented_cli",
                message=f"CLI command '{cmd}' not documented in README.rst",
                document="README.rst",
                severity="error",
                fixable=False,
            )
            for cmd in self.actual_cli_commands
            if cmd not in content
        )

        # Check public API is documented
        mismatches.extend(
            Mismatch(
                check="readme_rst",
                type="undocumented_api",
                message=f"API export '{export}' not documented in README.rst",
                document="README.rst",
                severity="info",
                fixable=False,
            )
            for export in self.actual_api
            if not export.startswith("_")
            and export not in content
            and export.lower() not in content.lower()
        )

        return mismatches

    def run_all_checks(self) -> list[CheckResult]:
        """Run all documentation checks."""
        results = []

        self.load_ground_truth()

        # Define documentation files to check
        doc_files = {
            "README.rst": self.project_root / "README.rst",
            "AGENTS.md": self.project_root / "AGENTS.md",
            "ARCHITECTURE.rst": self.project_root / "ARCHITECTURE.rst",
            "CONTRIBUTING.rst": self.project_root / "CONTRIBUTING.rst",
            "DATA_README.rst": self.project_root
            / "src"
            / "licence_normaliser"
            / "data"
            / "README.rst",
        }

        for doc_name, doc_path in doc_files.items():
            if not doc_path.exists():
                if self.verbose:
                    print(f"Skipping {doc_name}: file not found")
                continue

            if self.verbose:
                print(f"Checking {doc_name}...")

            content = doc_path.read_text()
            mismatches = []

            # Generic checks
            mismatches.extend(self.check_file_paths(doc_name, content))
            mismatches.extend(self.check_code_blocks(doc_name, content))

            # Document-specific checks
            if doc_name == "AGENTS.md":
                mismatches.extend(self.check_agents_md(content))
            elif doc_name == "ARCHITECTURE.rst":
                mismatches.extend(self.check_architecture_rst(content))
            elif doc_name == "README.rst":
                mismatches.extend(self.check_readme_rst(content))

            results.append(
                CheckResult(
                    check_name=doc_name,
                    passed=len([m for m in mismatches if m.severity == "error"]) == 0,
                    mismatches=mismatches,
                )
            )

        return results


# =============================================================================
# Reporting
# =============================================================================


class Reporter:
    """Handles output formatting for check results."""

    def __init__(self, results: list[CheckResult], verbose: bool = False):
        self.results = results
        self.verbose = verbose

    def console_report(self) -> int:
        """Print console report and return exit code."""
        total_errors = 0
        total_warnings = 0

        for result in self.results:
            if not result.mismatches and not self.verbose:
                continue

            print(f"\n{'=' * 60}")
            print(f"📄 {result.check_name}")
            print("=" * 60)

            if not result.mismatches:
                print("  ✓ No issues found")
                continue

            for mismatch in result.mismatches:
                icon = (
                    "🔴"
                    if mismatch.severity == "error"
                    else "🟡"
                    if mismatch.severity == "warning"
                    else "🔵"
                )
                print(f"  {icon} [{mismatch.type}] {mismatch.message}")

                if mismatch.severity == "error":
                    total_errors += 1
                elif mismatch.severity == "warning":
                    total_warnings += 1

        print(f"\n{'=' * 60}")
        print(f"Summary: {total_errors} errors, {total_warnings} warnings")
        print("=" * 60)

        return 1 if total_errors > 0 else 0

    def json_report(self) -> str:
        """Generate JSON report."""
        return json.dumps(
            [
                {
                    "document": result.check_name,
                    "passed": result.passed,
                    "mismatches": [
                        {
                            "check": m.check,
                            "type": m.type,
                            "message": m.message,
                            "severity": m.severity,
                            "fixable": m.fixable,
                        }
                        for m in result.mismatches
                    ],
                }
                for result in self.results
            ],
            indent=2,
        )


# =============================================================================
# Main Entry Point
# =============================================================================


def main() -> int:
    """Main entry point for documentation-validator."""
    parser = argparse.ArgumentParser(
        prog="documentation-validator",
        description="Validate documentation against source code ground truth.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  documentation-validator              # Check all documentation
  documentation-validator --fix        # Auto-fix issues where possible
  documentation-validator --json       # Output JSON report for CI
  documentation-validator -v           # Verbose output
        """,
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues where possible (not yet implemented)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON report",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root directory (default: current working directory)",
    )

    args = parser.parse_args()

    # Determine project root
    project_root = args.project_root or Path.cwd()
    project_root = project_root.resolve()

    if args.verbose:
        print(f"Project root: {project_root}")

    # Run checks
    validator = DocumentationValidator(project_root, verbose=args.verbose)
    results = validator.run_all_checks()

    # Generate report
    reporter = Reporter(results, verbose=args.verbose)

    if args.json:
        print(reporter.json_report())
        # Return 1 if any document failed
        return 1 if any(not r.passed for r in results) else 0
    else:
        return reporter.console_report()


if __name__ == "__main__":
    sys.exit(main())
