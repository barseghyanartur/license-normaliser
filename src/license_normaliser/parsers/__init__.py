"""license_normaliser.parsers - dynamic parser registry."""

from .alias import AliasParser
from .base import BaseParser
from .creativecommons import CreativeCommonsParser
from .opendefinition import OpenDefinitionParser
from .osi import OSIParser
from .prose import ProseParser
from .publisher import PublisherParser
from .scancode_licensedb import ScanCodeLicenseDBParser
from .spdx import SPDXParser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"
__all__ = ("get_parsers",)


def get_parsers() -> list[BaseParser]:
    return [
        SPDXParser(),
        OpenDefinitionParser(),
        OSIParser(),
        ScanCodeLicenseDBParser(),
        CreativeCommonsParser(),
        ProseParser(),
        AliasParser(),
        PublisherParser(),
    ]
