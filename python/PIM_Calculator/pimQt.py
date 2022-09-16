#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import logging
import sys
from itertools import cycle

from PySide2 import QtCore, QtWidgets

from PIM_Calculator.pim_calc import PIMCalc

# try to import plotting
plt = None
try:
    import matplotlib

    matplotlib.use("Qt5Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure

    plt.style.use("bmh")
    import numpy as np
    from scipy.interpolate import interp1d
    from scipy.interpolate import splrep as spline
except ImportError:
    print("no plotting.. :/")
    raise


VERSION = "0.2"


# TODO: add slots and signals
class PIMCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=6, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        plt.style.use("bmh")

    def update_figure(self, data, plot_name=""):
        self.axes.cla()
        self.axes.set_title(plot_name)
        self.axes.set_ylabel("Power Normalized")
        self.axes.set_xlabel("Frequency [MHz]")

        # Shapes:
        shape_im = np.array(
            [0.2, 0.4, 0.50, 0.55, 0.58, 0.6, 0.6, 0.6, 0.6, 0.6, 0.58, 0.55, 0.50, 0.4, 0.2]
        )

        shape_crr = np.array([0.2, 0.5, 0.9, 0.99, 1, 1, 1, 1, 1, 1, 1, 0.99, 0.9, 0.5, 0.2])
        # plot RX vs IM
        # if isinstance(data[0], tuple):
        if "RX" in plot_name:
            rx_present = []
            for rx, im_hits, im_src in data:
                # x = np.arange(im_hits[0], im_hits[1])
                x = np.linspace(im_hits[0], im_hits[1], num=15)
                x_cf = im_hits[0] + (im_hits[1] - im_hits[0]) / 2

                # make pseudo PIM shape with edges lower than middle
                y = np.outer(shape_im, np.ones(len(x))).ravel()
                y = y[:: int(len(y) / len(x))]
                x2 = np.linspace(x.min(), x.max(), num=124)
                y = spline(x, y, x2)

                self.axes.plot(x2, y, label="IM Cf={0}".format(x_cf), alpha=0.60, lw="3")

                rx_cf = rx[0] + (rx[1] - rx[0]) / 2
                if rx_cf not in rx_present:
                    # rx = np.arange(rx[0], rx[1])
                    rx = np.linspace(rx[0] - 0.1, rx[1] + 0.1, num=15)

                    # make pseudo PIM shape with edges lower than middle
                    y = np.outer(shape_crr, np.ones(len(rx))).ravel()
                    y = y[:: int(len(y) / len(rx))]
                    rx2 = np.linspace(rx.min(), rx.max(), num=124)
                    y = spline(rx, y, rx2, order=2)

                    self.axes.plot(rx2, y, label="RX Cf={0}".format(rx_cf), alpha=0.8, lw="3")
                    rx_present.append(rx_cf)
                self.axes.legend()
            self.draw()
            return

        # Plot IM items
        # data = [np.arange(x[0], x[1]) for x in data]
        # data = [np.arange(x[0], x[1]) for x in data]
        # y = [np.ones(len(x)) for x in data]
        for pim in data:
            x = np.linspace(pim[0], pim[1], num=15, endpoint=True)
            x_cf = pim[0] + (pim[1] - pim[0]) / 2
            y = np.outer(shape_im, np.ones(len(x))).ravel()
            y = y[:: int(len(y) / len(x))]
            x2 = np.linspace(x.min(), x.max(), num=124)
            y = spline(x, y, x2)

            self.axes.plot(x2, y, label="IM Cf={0}".format(x_cf), alpha=0.60, lw="3")
            """self.axes.bar(x, y,
                          label="Cf={0}".format(x[0]+(x[-1]-x[0])/2),
                          alpha=0.60,
                          lw="3")
            """
            # self.axes.plot(x, y, alpha=0.8, lw="3")
        # self.xticks(a + 0.4, a)
        self.axes.legend()
        self.draw()


class PIMPlot(QtWidgets.QWidget):
    def __init__(self, item):
        QtWidgets.QWidget.__init__(self)


class ScrollMessageBox(QtWidgets.QMessageBox):
    def __init__(self, widgets, *args, **kwargs):
        QtWidgets.QMessageBox.__init__(self, *args, **kwargs)

        scroll = QtWidgets.QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setGeometry(100, 100, 100, 100)
        self.content = QtWidgets.QWidget()
        scroll.setWidget(self.content)
        lay = QtWidgets.QVBoxLayout(self.content)

        if not isinstance(widgets, list):
            widgets = [widgets]

        for item in widgets:
            lay.addWidget(item)

        self.layout().addWidget(scroll, 0, 0, 1, self.layout().columnCount())
        self.setStyleSheet("QScrollArea{min-width:640 px; min-height: 480px}")


# TODO: add slots and signals
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        # super(MainWindow, self).__init__()
        # elements
        self.labels = []
        self.fields = []
        self.chk_box = []
        self.windows = []
        self.initUI()

    def fileQuit(self):
        for wind in self.windows:
            wind.close()
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def initUI(self):
        # MENUS
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("-- PIM Calculator --")

        self.file_menu = QtWidgets.QMenu("&File", self)
        self.file_menu.addAction("&Quit", self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu("&Help", self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction("&About", self.about)

        self.main_widget = QtWidgets.QWidget(self)

        # Go! btn
        self.chk_box.append(QtWidgets.QCheckBox("Plot Results"))
        self.chk_box[-1].setChecked(False)
        self.chk_box.append(QtWidgets.QCheckBox("Plot IM Separately"))
        self.chk_box[-1].setChecked(False)
        self.chk_box.append(QtWidgets.QCheckBox("Show IM source"))
        self.chk_box[-1].setChecked(False)
        calculate_btn = QtWidgets.QPushButton("Calculate", self)
        calculate_btn.setToolTip("<b>Click to calculate</b>")
        calculate_btn.resize(calculate_btn.sizeHint())
        calculate_btn.clicked.connect(self.on_calculate_click)

        # Labels and text forms
        self.labels.append(QtWidgets.QLabel("<b>TX Carriers</b>", self))
        self.labels.append(QtWidgets.QLabel("Frequency [MHz]", self))
        self.labels.append(QtWidgets.QLabel("Bandwidth [MHz]", self))
        self.labels.append(QtWidgets.QLabel("<b>RX Carriers</b>", self))
        self.labels.append(QtWidgets.QLabel("Frequency [MHz]", self))
        self.labels.append(QtWidgets.QLabel("Bandwidth [MHz]", self))

        self.fields.append(QtWidgets.QLineEdit("1980,1940", self))
        self.fields.append(QtWidgets.QLineEdit("5,5", self))
        self.fields.append(QtWidgets.QLineEdit("1900,1880", self))
        self.fields.append(QtWidgets.QLineEdit("5,5", self))

        # Grid
        grid_main = QtWidgets.QGridLayout(self.main_widget)
        grid_main.setSpacing(5)
        grid = QtWidgets.QGridLayout()

        grid_main.addLayout(grid, 0, 0, 1, 4)
        grid.setSpacing(5)

        yPos = 0
        xPos = 0
        # Add labels to grid
        for l in range(0, len(self.labels)):
            if (yPos == 0) or (yPos == 3) or (yPos == 6):
                x = 1
            else:
                x = 0
            grid.addWidget(self.labels[l], l, x)
            yPos += 1
        # Add edit fields
        yPos = 1
        for l in self.fields:
            grid.addWidget(l, yPos, 1)
            if yPos == 2 or yPos == 5:
                yPos += 1
            yPos += 1

        grid.addWidget(calculate_btn, 1, 4)
        grid.addWidget(self.chk_box[0], 2, 4)
        grid.addWidget(self.chk_box[1], 3, 4)
        grid.addWidget(self.chk_box[2], 4, 4)

        self.setGeometry(500, 300, 400, 150)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.show()

    @staticmethod
    def _convert_list(items):
        """ Convert string params into lists """

        if not isinstance(items, str):
            items = str(items)

        if "," in items:
            items = [float(x) for x in items.strip().split(",")]
        else:
            items = [float(items)]

        return items

    def show_results(self, results, plot_results, plot_im, im_data=None, rx_data=None):
        # box = QtWidgets.QMessageBox()
        items = []
        text_obj = QtWidgets.QTextBrowser(self)
        text_obj.setText(results)
        # items.append(text_obj)
        if plt and plot_results:
            if plot_im:
                for im, im_full in im_data:
                    pim_plots = PIMCanvas()
                    pim_plots.update_figure(im_full, plot_name=im)
                    items.append([im, pim_plots])

            for im, im_full in rx_data:
                pim_plots = PIMCanvas()
                # call the plots only if there is something to show
                if len(im_full) > 0:
                    pim_plots.update_figure(im_full, plot_name=im)
                    items.append([im, pim_plots])

            for w in items:
                self.result_window(w[1], item_name=w[0])

        box = ScrollMessageBox(text_obj)
        box.setWindowTitle("PIM Calculator Results")
        result = box.exec_()

    def result_window(self, item, item_name="Results"):
        item.setWindowTitle(item_name)
        item.show()
        self.windows.append(item)

    def on_calculate_click(self):
        """ Method to call on calculate click """

        tx_list = self._convert_list(self.fields[0].text())
        tx_bandwith = self._convert_list(self.fields[1].text())
        rx_list = self._convert_list(self.fields[2].text())
        rx_bandwith = self._convert_list(self.fields[3].text())

        plot_results = self.chk_box[0].isChecked()
        plot_im = self.chk_box[1].isChecked()
        pimc = PIMCalc()

        # get IM results
        text_result, im_result, rx_result = pimc.get_results(
            tx_list, tx_bandwith, rx_list, rx_bandwith
        )

        """
        im_result = pimc.calculate(tx_list, tx_bandwith=tx_size)
        text_result = []
        im_name = cycle(["IM3", "IM5"]).next
        rx_result = []
        for im, im_full in im_result:
            name = im_name()
            pimc.logger.info(48*"=")
            pimc.logger.info(im)
            pimc.logger.info("==== {0}:fmin, fmax ====".format(name))
            pimc.logger.info(im_full)
            pimc.logger.info(48*"=")
            text_result.append(48*"=")
            text_result.append("==== {0} ====".format(name))
            text_result.append(str(im))
            text_result.append("==== {0}:fmin, fmax ====".format(name))
            text_result.append(str(im_full))
            text_result.append(48*"=")
            if rx_list is not None:
                pimc.logger.info("==== RX check ===")
                im_hits = pimc.check_rx(rx_list, im_full, rx_bandwith=rx_size)
                if len(im_hits) > 0:
                    pimc.logger.warning("yey, we've got some {0} PIM".format(name))
                rx_result.append((name, im_hits))
                text_result.append(48*"=")
                pimc.logger.info(48*"=")

        for rx_res in rx_result:
            im_type = rx_res[0]
            pimc.logger.warning("===== {0} =====".format(im_type))
            text_result.append("===== {0} =====".format(im_type))
            for pim in rx_res[1]:
                pimc.logger.warning("{0} is inside: {1}".format(pim[0], pim[1]))
                text_result.append("{0} is inside: {1}".format(pim[0], pim[1]))
        """
        text_result = "\n".join(text_result)
        self.show_results(text_result, plot_results, plot_im, im_data=im_result, rx_data=rx_result)

    def about(self):
        QtWidgets.QMessageBox.about(
            self,
            "About",
            """PIM Calculator
This program is a simple GUI for Passive InterModulation Calculation.
versio={0}
""".format(
                VERSION
            ),
        )


def main():
    # setup logger
    console = logging.StreamHandler()
    console.setLevel("DEBUG")
    logger = logging.getLogger(__name__)
    logger.addHandler(console)
    logger.setLevel("DEBUG")

    # Allow the taking of command line arguements
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet("QMessageBox { messagebox-text-interaction-flags: 5; }")

    main = MainWindow()
    # Ensure the execution stops correctly
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
