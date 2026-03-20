"""Base parser interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseParser(ABC):
    """All data parsers must implement this."""

    @abstractmethod
    def parse(self) -> list[tuple[str, dict[str, Any]]]:
        """Return (license_key, metadata_dict) for every entry."""
        ...
