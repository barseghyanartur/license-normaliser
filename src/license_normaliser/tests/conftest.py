"""
Pytest fixtures for documentation testing and general testing.
"""

import pytest

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


@pytest.fixture()
def simple_license():
    """A simple license string for testing."""
    return "MIT"


@pytest.fixture()
def cc_by_nc_nd_license():
    """A CC BY-NC-ND 4.0 license string."""
    return "CC BY-NC-ND 4.0"


@pytest.fixture()
def multiple_licenses():
    """Multiple license strings for batch testing."""
    return ["MIT", "Apache-2.0", "CC BY 4.0"]
