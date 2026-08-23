from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from PIM_Calculator.pimQt import MainWindow


@pytest.fixture
def main_window(qtbot: Any, mocker: MockerFixture, xvfb: Any) -> MainWindow:
    ui_mock: MagicMock = mocker.patch("PIM_Calculator.pimQt.MainWindow.initUI")
    main_window = MainWindow()
    main_window.ui_mock = ui_mock
    return main_window


class TestpimQt:
    def test_MainWindow_init(
        self, qtbot: Any, main_window: MainWindow, xvfb: Any
    ) -> None:
        qtbot.addWidget(main_window)
        init_ui_mock = cast(MagicMock, main_window.initUI)
        init_ui_mock.assert_called_once_with()

    def test_MainWindow_initUI(
        self, qtbot: Any, mocker: MockerFixture, xvfb: Any
    ) -> None:
        window = MainWindow()
        qtbot.addWidget(window)

        assert len(window.labels) == 6
        assert len(window.fields) == 4

        # check boxes
        assert len(window.chk_box) == 3
        assert window.chk_box[0].isChecked() is False
        assert window.chk_box[1].isChecked() is False

        # check file menus
        assert window.file_menu is not None

    def test_MainWindow_closeEvent(
        self, qtbot: Any, main_window: MainWindow, mocker: MockerFixture, xvfb: Any
    ) -> None:
        qtbot.addWidget(main_window)
        file_quit: MagicMock = mocker.patch.object(main_window, "fileQuit")
        main_window.closeEvent("XX")
        file_quit.assert_called_once_with()

    def test_MainWindow_fileQuit(
        self, qtbot: Any, main_window: MainWindow, mocker: MockerFixture, xvfb: Any
    ) -> None:
        qtbot.addWidget(main_window)
        exit: MagicMock = mocker.patch.object(main_window, "close")
        wind1_mock = mocker.Mock()
        wind2_mock = mocker.Mock()
        main_window.windows = [wind1_mock, wind2_mock]
        mocker.patch.object(wind1_mock, "close")
        mocker.patch.object(wind2_mock, "close")
        main_window.fileQuit()

        for wind in main_window.windows:
            wind.close.assert_called_once_with()
        exit.assert_called_once_with()
