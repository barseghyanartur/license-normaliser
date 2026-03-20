"""license_normaliser.parsers - dynamic parser registry."""

from .base import BaseParser
from .opendefinition import OpenDefinitionParser
from .scancode_licensedb import ScanCodeLicenseDBParser
from .spdx import SPDXParser

__all__ = ("get_parsers",)


def get_parsers() -> list[BaseParser]:
    return [
        SPDXParser(),
        OpenDefinitionParser(),
        ScanCodeLicenseDBParser(),
    ]
