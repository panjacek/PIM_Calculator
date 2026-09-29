from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

import PIM_Calculator.pimQt as pim_qt
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
        assert len(window.chk_box) == 2
        assert window.chk_box[0].isChecked() is False
        assert window.chk_box[1].isChecked() is False

        # check file menus
        assert window.file_menu is not None

    def test_MainWindow_closeEvent(
        self, qtbot: Any, main_window: MainWindow, mocker: MockerFixture, xvfb: Any
    ) -> None:
        qtbot.addWidget(main_window)
        file_quit: MagicMock = mocker.patch.object(main_window, "fileQuit")
        main_window.closeEvent(pim_qt.QtGui.QCloseEvent())
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
            cast(MagicMock, wind.close).assert_called_once_with()
        exit.assert_called_once_with()


@pytest.fixture
def real_window(qtbot: Any, xvfb: Any) -> MainWindow:
    window = MainWindow()
    qtbot.addWidget(window)
    window.fields[0].setText("2152,1932")
    window.fields[1].setText("5,5")
    window.fields[2].setText("1752,1900")
    window.fields[3].setText("5,5")
    return window


class TestCalculateClick:
    def test_valid_input(
        self, real_window: MainWindow, mocker: MockerFixture
    ) -> None:
        show = mocker.patch.object(real_window, "show_results")
        real_window.on_calculate_click()

        show.assert_called_once()
        text_out = show.call_args.args[0]
        assert "RX check" in text_out
        im_data = show.call_args.kwargs["im_data"]
        assert [name for name, _rows in im_data] == ["IM3", "IM5"]
        assert all(len(rows) > 0 for _name, rows in im_data)

    def test_garbage_input(
        self, real_window: MainWindow, mocker: MockerFixture
    ) -> None:
        real_window.fields[0].setText("garbage")
        warning = mocker.patch.object(pim_qt.QtWidgets.QMessageBox, "warning")
        show = mocker.patch.object(real_window, "show_results")

        real_window.on_calculate_click()

        warning.assert_called_once()
        show.assert_not_called()

    def test_plot_results_toggle(
        self, real_window: MainWindow, mocker: MockerFixture
    ) -> None:
        show = mocker.patch.object(real_window, "show_results")
        box = real_window.chk_box[0]

        box.setChecked(True)
        real_window.on_calculate_click()
        assert show.call_args.args[1] is True

        box.setChecked(False)
        real_window.on_calculate_click()
        assert show.call_args.args[1] is False

    def test_plot_im_separately_toggle(
        self, real_window: MainWindow, mocker: MockerFixture
    ) -> None:
        show = mocker.patch.object(real_window, "show_results")
        box = real_window.chk_box[1]

        box.setChecked(True)
        real_window.on_calculate_click()
        assert show.call_args.args[2] is True

        box.setChecked(False)
        real_window.on_calculate_click()
        assert show.call_args.args[2] is False
