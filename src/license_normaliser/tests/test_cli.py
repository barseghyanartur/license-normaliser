"""Tests for license_normaliser CLI - includes new --strict flag."""

from unittest.mock import patch

import pytest

from license_normaliser.cli._main import main

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestNormaliseCommand:
    def test_normalise_mit(self, capsys):
        with patch("sys.argv", ["license-normaliser", "normalise", "MIT"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert capsys.readouterr().out.strip() == "mit"

    def test_normalise_full(self, capsys):
        with patch(
            "sys.argv", ["license-normaliser", "normalise", "--full", "CC BY 4.0"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Key: cc-by-4.0" in out
        assert "License: cc-by" in out
        assert "Family: cc" in out

    def test_normalise_cc_url(self, capsys):
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
        assert capsys.readouterr().out.strip() == "cc-by-4.0"

    def test_normalise_unknown(self, capsys):
        with patch(
            "sys.argv", ["license-normaliser", "normalise", "totally-unknown-xyz"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert "totally-unknown-xyz" in capsys.readouterr().out

    def test_normalise_strict_known(self, capsys):
        with patch("sys.argv", ["license-normaliser", "normalise", "--strict", "MIT"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert capsys.readouterr().out.strip() == "mit"

    def test_normalise_strict_unknown_exits_1(self, capsys):
        with patch(
            "sys.argv",
            ["license-normaliser", "normalise", "--strict", "totally-unknown-xyz-9999"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        assert capsys.readouterr().err  # error message on stderr


class TestBatchCommand:
    def test_batch_basic(self, capsys):
        with patch(
            "sys.argv",
            ["license-normaliser", "batch", "MIT", "Apache-2.0", "CC BY 4.0"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "MIT: mit" in out
        assert "Apache-2.0: apache-2.0" in out
        assert "CC BY 4.0: cc-by-4.0" in out

    def test_batch_strict_all_known(self, capsys):
        with patch(
            "sys.argv", ["license-normaliser", "batch", "--strict", "MIT", "GPL-3.0"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_batch_strict_with_unknown_exits_1(self, capsys):
        with patch(
            "sys.argv",
            ["license-normaliser", "batch", "--strict", "MIT", "no-such-license-xyz"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1


class TestVersionFlag:
    def test_version_flag(self, capsys):
        with patch("sys.argv", ["license-normaliser", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert "license-normaliser" in capsys.readouterr().out
