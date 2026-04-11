"""Tests for licence_normaliser CLI - includes new --strict flag."""

from unittest.mock import patch

import pytest

from licence_normaliser.cli._main import main
from licence_normaliser.parsers.spdx import SPDXParser

__author__ = "Artur Barseghyan <artur.barseghyan@gmail.com>"
__copyright__ = "2026 Artur Barseghyan"
__license__ = "MIT"


class TestNormaliseCommand:
    def test_normalise_mit(self, capsys) -> None:
        with patch("sys.argv", ["licence-normaliser", "normalise", "MIT"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert capsys.readouterr().out.strip() == "mit"

    def test_normalise_full(self, capsys) -> None:
        with patch(
            "sys.argv", ["licence-normaliser", "normalise", "--full", "CC BY 4.0"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Key: cc-by-4.0" in out
        assert "Licence: cc-by" in out
        assert "Family: cc" in out

    def test_normalise_cc_url(self, capsys) -> None:
        with patch(
            "sys.argv",
            [
                "licence-normaliser",
                "normalise",
                "http://creativecommons.org/licenses/by/4.0/",
            ],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert capsys.readouterr().out.strip() == "cc-by-4.0"

    def test_normalise_unknown(self, capsys) -> None:
        with patch(
            "sys.argv", ["licence-normaliser", "normalise", "totally-unknown-xyz"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert "totally-unknown-xyz" in capsys.readouterr().out

    def test_normalise_strict_known(self, capsys) -> None:
        with patch("sys.argv", ["licence-normaliser", "normalise", "--strict", "MIT"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert capsys.readouterr().out.strip() == "mit"

    def test_normalise_strict_unknown_exits_1(self, capsys) -> None:
        with patch(
            "sys.argv",
            ["licence-normaliser", "normalise", "--strict", "totally-unknown-xyz-9999"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        assert capsys.readouterr().err  # error message on stderr

    def test_normalise_with_trace_flag(self, capsys) -> None:
        with patch("sys.argv", ["licence-normaliser", "normalise", "--trace", "MIT"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Input:" in out
        assert "[✓]" in out

    def test_normalise_env_var_trace(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "1")
        with patch("sys.argv", ["licence-normaliser", "normalise", "MIT"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Input:" in out


class TestBatchCommand:
    def test_batch_basic(self, capsys) -> None:
        with patch(
            "sys.argv",
            ["licence-normaliser", "batch", "MIT", "Apache-2.0", "CC BY 4.0"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "MIT: mit" in out
        assert "Apache-2.0: apache-2.0" in out
        assert "CC BY 4.0: cc-by-4.0" in out

    def test_batch_strict_all_known(self, capsys) -> None:
        with patch(
            "sys.argv", ["licence-normaliser", "batch", "--strict", "MIT", "GPL-3.0"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_batch_strict_with_unknown_exits_1(self, capsys):
        with patch(
            "sys.argv",
            ["licence-normaliser", "batch", "--strict", "MIT", "no-such-license-xyz"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_batch_with_trace_flag(self, capsys) -> None:
        with patch(
            "sys.argv",
            ["licence-normaliser", "batch", "--trace", "MIT", "Apache-2.0"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "MIT:" in out
        assert "Input:" in out or "[✓]" in out
        assert "Apache-2.0:" in out

    def test_batch_env_var_trace(self, capsys, monkeypatch) -> None:
        monkeypatch.setenv("ENABLE_LICENCE_NORMALISER_TRACE", "1")
        with patch(
            "sys.argv",
            ["licence-normaliser", "batch", "MIT", "Apache-2.0"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        out = capsys.readouterr().out
        assert "Input:" in out


class TestVersionFlag:
    def test_version_flag(self, capsys) -> None:
        with patch("sys.argv", ["licence-normaliser", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
        assert "licence-normaliser" in capsys.readouterr().out


class TestUpdateDataCommand:
    @patch("licence_normaliser.cli._main.get_all_refreshable_plugins")
    @patch("licence_normaliser.cli._main.main")
    def test_update_data_all_parsers(self, mock_main, mock_get_plugins, capsys) -> None:
        mock_get_plugins.return_value = []
        with patch("sys.argv", ["licence-normaliser", "update-data"]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    @patch("licence_normaliser.parsers.spdx.SPDXParser.refresh")
    @patch("licence_normaliser.cli._main.get_all_refreshable_plugins")
    def test_update_data_specific_parser(
        self,
        mock_get_plugins,
        mock_refresh,
        capsys,
    ) -> None:
        mock_get_plugins.return_value = [SPDXParser]
        mock_refresh.return_value = True
        with patch(
            "sys.argv", ["licence-normaliser", "update-data", "--parser", "spdx"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_update_data_unknown_parser_error(self, capsys):
        with patch(
            "sys.argv", ["licence-normaliser", "update-data", "--parser", "nonexistent"]
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "unknown parser" in err
        assert "nonexistent" in err

    @patch("licence_normaliser.parsers.spdx.SPDXParser.refresh")
    @patch("licence_normaliser.cli._main.get_all_refreshable_plugins")
    def test_update_data_failure_handling(
        self,
        mock_get_plugins,
        mock_refresh,
        capsys,
    ) -> None:
        mock_get_plugins.return_value = [SPDXParser]
        mock_refresh.return_value = False
        with patch(
            "sys.argv",
            ["licence-normaliser", "update-data", "--parser", "spdx", "--force"],
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1
        err = capsys.readouterr().err
        assert "failed" in err
