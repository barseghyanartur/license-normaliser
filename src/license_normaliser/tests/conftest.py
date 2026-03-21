"""Shared fixtures for license_normaliser tests."""

import pytest

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


@pytest.fixture()
def mit_raw() -> str:
    return "MIT"


@pytest.fixture()
def cc_by_nc_nd_4_raw() -> str:
    return "CC BY-NC-ND 4.0"


@pytest.fixture()
def batch_raw() -> list[str]:
    return ["MIT", "Apache-2.0", "CC BY 4.0"]
