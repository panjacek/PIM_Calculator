import pytest
from PIM_Calculator.pimQt import QPlainTextEditLogger, ScrollMessageBox, MainWindow
from PySide2 import QtWidgets, QtCore
import logging


@pytest.fixture
def main_window(mocker, qtbot):
    mocker.patch("PIM_Calculator.pimQt.MainWindow.initUI")
    return MainWindow()


class TestpimQt(object):
    def test_MainWindow_init(self, qtbot, main_window):
        main_window.initUI.assert_called_once_with()

    def test_MainWindow_initUI(self, qtbot, mocker):
        window = MainWindow()
        window.show()
        qtbot.addWidget(window)

        assert len(window.labels) == 6
        assert len(window.fields) == 4
        
        # check boxes
        assert len(window.chk_box) == 3
        assert window.chk_box[0].isChecked() is False
        assert window.chk_box[1].isChecked() is False

        # check file menus
        assert window.file_menu is not None
        assert window.size() == QtCore.QSize(400, 191)


    def test_MainWindow_closeEvent(self, qtbot, main_window, mocker):
        file_quit = mocker.patch.object(main_window, "fileQuit")
        main_window.closeEvent("XX")
        file_quit.assert_called_once_with()

    def test_MainWindow_fileQuit(self, qtbot, main_window, mocker):
        exit = mocker.patch.object(main_window, "close")
        wind1_mock = mocker.Mock()
        wind2_mock = mocker.Mock()
        main_window.windows = [
                    wind1_mock,
                    wind2_mock
                ]
        mocker.patch.object(wind1_mock, "close")
        mocker.patch.object(wind2_mock, "close")
        main_window.fileQuit()
        
        for wind in main_window.windows:
            wind.close.assert_called_once_with()
        exit.assert_called_once_with()

