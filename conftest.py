"""Pytest fixtures for documentation testing."""

from typing import Any as AnyType

import pytest


@pytest.fixture()
def Any() -> AnyType:  # noqa
    """For to be used in documentation."""
    return AnyType
