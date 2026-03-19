"""Tests for license_normaliser CLI."""

from unittest.mock import patch

import pytest

from license_normaliser.cli._main import main

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestNormaliseCommand:
    """Tests for the normalise command."""

    def test_normalise_basic(self, capsys):
        """Basic normalisation works."""
        with patch("sys.argv", ["license-normaliser", "normalise", "MIT"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert captured.out.strip() == "mit"

    def test_normalise_full(self, capsys):
        """Normalise with full details."""
        with patch(
            "sys.argv", ["license-normaliser", "normalise", "--full", "CC BY 4.0"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "Key: cc-by-4.0" in captured.out
        assert "License: cc-by" in captured.out
        assert "Family: cc" in captured.out

    def test_normalise_cc_url(self, capsys):
        """Normalise a Creative Commons URL."""
        with patch(
            "sys.argv",
            [
                "license-normaliser",
                "normalise",
                "http://creativecommons.org/licenses/by/4.0/",
            ],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert captured.out.strip() == "cc-by-4.0"


class TestBatchCommand:
    """Tests for the batch command."""

    def test_batch_basic(self, capsys):
        """Batch normalisation works."""
        with patch(
            "sys.argv",
            [
                "license-normaliser",
                "batch",
                "MIT",
                "Apache-2.0",
                "CC BY 4.0",
            ],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "MIT: mit" in captured.out
        assert "Apache-2.0: apache-2.0" in captured.out
        assert "CC BY 4.0: cc-by-4.0" in captured.out


class TestVersionFlag:
    """Tests for --version flag."""

    def test_version_flag(self, capsys):
        """--version flag displays version."""
        with patch("sys.argv", ["license-normaliser", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

        captured = capsys.readouterr()
        assert "license-normaliser" in captured.out
